"""BIST 30 şirketlerinin KAP bildirimlerini toplayıp veritabanına yazar.

Çalıştır: uv run python -m toplayici.kap
"""

import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import borsapy as bp
import httpx

from kap.metin import BildirimOkunamadi, bildirim_metni
from toplayici import ENDEKS
from toplayici.db import baglan

KAP_URL = "https://www.kap.org.tr/tr/Bildirim/{id}"
ISTANBUL = ZoneInfo("Europe/Istanbul")
BEKLEME = 2.0  # saniye: istekler arası nezaket aralığı (0,5 ile ~80 istekte 429 yedik)
DENEME = 3     # 429 ya da kopan bağlantıda kaç kez yeniden denenir

# Metni indirmeye değmeyen rutin türler: başlık yeterli, KAP'a istek atmayız.
RUTIN = (
    "SPK İşlem Yasağı",
    "Pay Bazında Devre Kesici",
    "Borsada İşlem Gören Tipe Dönüşüm",
    "Pay Dışında Sermaye Piyasası Aracı İşlemlerine İlişkin Bildirim",
)


class KapReddetti(Exception):
    """KAP art arda reddetti. Tur durur; kalanlar sonraki çalıştırmada toplanır."""


def _utc(kap_tarihi: str) -> str:
    """'12.10.2026 14:58:37' (İstanbul saati) → '2026-10-12T11:58:37Z'"""
    yerel = datetime.strptime(kap_tarihi, "%d.%m.%Y %H:%M:%S").replace(tzinfo=ISTANBUL)
    return yerel.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _retry_after(yanit: httpx.Response) -> float:
    try:
        return float(yanit.headers.get("Retry-After", 0))
    except ValueError:  # tarih biçiminde de gelebilir; o zaman kendi süremizi kullanırız
        return 0


def _getir(istemci: httpx.Client, url: str) -> httpx.Response:
    """429 ya da kopan bağlantıda üstel bekleyerek dener (4, 8, 16 sn). Olmazsa KapReddetti."""
    for deneme in range(DENEME):
        try:
            yanit = istemci.get(url)
        except httpx.TransportError:  # "Server disconnected": sunucu bizi kesiyor olabilir
            yanit = None
        if yanit is not None and yanit.status_code != 429:
            yanit.raise_for_status()  # 404 gibi başka hatalar: o bildirime özgü, yukarı fırlar
            return yanit
        sunucunun_istedigi = _retry_after(yanit) if yanit is not None else 0
        time.sleep(max(sunucunun_istedigi, BEKLEME * 2 ** (deneme + 1)))
    raise KapReddetti(url)


def _icerik(istemci: httpx.Client, bildirim_id: str) -> dict:
    """Bildirimin özetini ve metnini getirir. Ağ hatası yukarı fırlar, okunamayan sayfa boş döner."""
    yanit = _getir(istemci, KAP_URL.format(id=bildirim_id))
    try:
        return bildirim_metni(yanit.text)
    except BildirimOkunamadi:
        # Sayfa geldi ama metin yapısı tanıdık değil (SPK işlem yasağı gibi türler).
        # Başlık yine de değerli, belgeyi metinsiz kaydediyoruz.
        return {"ozet": None, "metin": None, "okunamadi": True}


def topla(db, semboller: list[str] | None = None) -> dict:
    semboller = semboller or bp.Index(ENDEKS).component_symbols
    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rapor = {"sembol": len(semboller), "yeni": 0, "okunamadi": 0, "rutin": 0, "hata": [], "durdu": None}

    with httpx.Client(timeout=30, follow_redirects=True) as istemci:
        for sembol in semboller:
            try:
                liste = bp.Ticker(sembol).news
            except Exception as e:
                rapor["hata"].append(f"{sembol} listesi: {e}")
                continue
            if liste is None or liste.empty:
                rapor["hata"].append(f"{sembol} listesi boş geldi")
                continue

            for satir in liste.itertuples():
                bildirim_id = satir.URL.rstrip("/").rsplit("/", 1)[-1]

                # Zaten varsa KAP'a hiç gitme: asıl pahalı iş metni indirmek.
                if db.execute(
                    "SELECT 1 FROM belgeler WHERE kaynak = 'KAP' AND dis_id = ?", (bildirim_id,)
                ).fetchone():
                    continue

                if satir.Title.startswith(RUTIN):
                    icerik = {"ozet": None, "metin": None}
                    rapor["rutin"] += 1
                else:
                    try:
                        icerik = _icerik(istemci, bildirim_id)
                    except KapReddetti as e:
                        # Devre kesici: reddeden sunucuya istek yağdırmaya devam etmiyoruz.
                        db.commit()
                        rapor["durdu"] = f"{sembol} hissesinde KAP reddetti ({e}); tur durdu"
                        return rapor
                    except httpx.HTTPError as e:
                        # Kaydetmiyoruz: kaydetseydik UNIQUE yüzünden bir daha hiç denenmezdi.
                        rapor["hata"].append(f"{sembol} {bildirim_id}: {e}")
                        continue
                    finally:
                        time.sleep(BEKLEME)

                db.execute(
                    """INSERT OR IGNORE INTO belgeler
                       (tur, kaynak, dis_id, url, baslik, ozet, metin, sembol, dil,
                        yayin_zamani, toplanma_zamani)
                       VALUES ('kap', 'KAP', ?, ?, ?, ?, ?, ?, 'tr', ?, ?)""",
                    (bildirim_id, satir.URL, satir.Title, icerik["ozet"], icerik["metin"],
                     sembol, _utc(satir.Date), simdi),
                )
                rapor["yeni"] += 1
                rapor["okunamadi"] += icerik.get("okunamadi", False)

            db.commit()  # her hisseden sonra: yarıda kesilirse biten hisseler kaybolmaz

    return rapor


if __name__ == "__main__":
    baslangic = time.time()
    rapor = topla(baglan())
    print(f"{rapor['sembol']} hisse · {rapor['yeni']} yeni bildirim "
          f"({rapor['rutin']} rutin, {rapor['okunamadi']} okunamadı) · {time.time() - baslangic:.0f} sn")
    if rapor["durdu"]:
        print("DURDU", rapor["durdu"])
    for satir in rapor["hata"]:
        print("HATA", satir)
