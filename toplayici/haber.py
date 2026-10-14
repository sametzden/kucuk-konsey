"""Sabit haber kaynaklarının RSS beslemelerini okuyup veritabanına yazar.

RSS: sitenin "son yayınladıklarım" listesini makinenin okuyacağı XML olarak sunduğu dosya.
Arşiv değil, son N haberi tutar; bu yüzden toplayıcı düzenli çalışır (12 saatte bir).

Çalıştır: uv run python -m toplayici.haber
"""

import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx
from bs4 import BeautifulSoup

from toplayici.db import baglan

# (ad, besleme adresi, dil). Kaynak eklemek/çıkarmak için yalnız bu listeyi düzenle.
KAYNAKLAR = [
    ("AA", "https://www.aa.com.tr/tr/rss/default?cat=ekonomi", "tr"),
    ("Bloomberg HT", "https://www.bloomberght.com/rss", "tr"),
    ("TRT Haber", "https://www.trthaber.com/ekonomi_articles.rss", "tr"),
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html", "en"),
    ("BBC", "https://feeds.bbci.co.uk/news/business/rss.xml", "en"),
    ("FT", "https://www.ft.com/markets?format=rss", "en"),
]
# Kim olduğumuzu dürüstçe söyleyen bir tanıtım. Tarayıcı taklidi yapmıyoruz.
USER_AGENT = "KucukKonsey/0.1 (kisisel arastirma araci)"
OZET_SINIRI = 1000  # karakter: özet alanına tam makale koyan kaynaklara karşı


def _temiz(html: str | None) -> str | None:
    """RSS açıklamasındaki HTML'i (TRT <img> koyuyor) düz metne çevirir."""
    if not html:
        return None
    metin = " ".join(BeautifulSoup(html, "html.parser").get_text(" ").split())
    return metin[:OZET_SINIRI] or None


def _utc(rss_tarihi: str) -> str:
    """'Wed, 14 Oct 2026 14:08:00 +0300' → '2026-10-14T11:08:00Z'"""
    an = parsedate_to_datetime(rss_tarihi)
    if an.tzinfo is None:  # saat dilimi yazmayan kaynak: UTC varsayıyoruz
        an = an.replace(tzinfo=timezone.utc)
    return an.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ogeler(xml: bytes) -> list[dict]:
    """RSS 2.0 dosyasından haberleri çıkarır. Başlığı, linki ya da tarihi olmayanı atlar."""
    sonuc = []
    for item in ET.fromstring(xml).iter("item"):
        baslik = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        tarih = item.findtext("pubDate")
        if not (baslik and link and tarih):
            continue
        sonuc.append({
            # guid: kaynağın habere verdiği kalıcı kimlik. Yoksa link.
            "dis_id": (item.findtext("guid") or link).strip(),
            "url": link,
            "baslik": baslik,
            "ozet": _temiz(item.findtext("description")),
            "yayin_zamani": _utc(tarih),
        })
    return sonuc


def topla(db) -> dict:
    simdi = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rapor = {"kaynak": {}, "hata": []}

    with httpx.Client(timeout=30, follow_redirects=True,
                      headers={"User-Agent": USER_AGENT}) as istemci:
        for ad, adres, dil in KAYNAKLAR:
            try:
                yanit = istemci.get(adres)
                yanit.raise_for_status()
                ogeler = _ogeler(yanit.content)
            except (httpx.HTTPError, ET.ParseError, ValueError) as e:
                # Bir kaynak bozuksa diğerleri yine toplanır.
                rapor["hata"].append(f"{ad}: {e}")
                continue

            yeni = 0
            for o in ogeler:
                imlec = db.execute(
                    """INSERT OR IGNORE INTO belgeler
                       (tur, kaynak, dis_id, url, baslik, ozet, dil, yayin_zamani, toplanma_zamani)
                       VALUES ('haber', ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (ad, o["dis_id"], o["url"], o["baslik"], o["ozet"], dil, o["yayin_zamani"], simdi),
                )
                yeni += imlec.rowcount  # 1: eklendi, 0: zaten vardı
            db.commit()
            rapor["kaynak"][ad] = f"{yeni} yeni / {len(ogeler)}"

    return rapor


if __name__ == "__main__":
    baslangic = time.time()
    rapor = topla(baglan())
    for ad, durum in rapor["kaynak"].items():
        print(f"{ad}: {durum}")
    for satir in rapor["hata"]:
        print("HATA", satir)
    print(f"{time.time() - baslangic:.1f} sn")
