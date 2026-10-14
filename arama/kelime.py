"""Kelime araması: FTS5 dizininde BM25 ile sıralı sonuç.

Kullanım:
    from arama.kelime import ara
    ara(db, "ihracat rekor", gun=3, tur="haber")
"""

import re
import sqlite3
from datetime import datetime, timedelta, timezone

OZET_SINIRI = 300  # karakter: sonuç listesi kısa kalsın, tam metin ayrıca istenir
EN_FAZLA = 50
KISA_KELIME = 3     # bundan kısa kelimeye * eklenmez: "ab*" yüzlerce alakasız kelimeyi yakalar

# Başlık 10, özet 5, metin 1: kelime başlıkta geçiyorsa belge büyük ihtimalle o konuda.
AGIRLIK = "10.0, 5.0, 1.0"


def fts_sorgusu(metin: str) -> str:
    """Serbest metni güvenli bir FTS5 sorgusuna çevirir.

    'İhracat rekoru, ASELS!' → '"ihracat"* OR "rekoru"* OR "asels"*'

    Kelimeleri tırnağa alıyoruz: FTS5'in kendi sorgu dili var (AND, NOT, NEAR, "metin:" gibi).
    Kullanıcının ya da ajanın yazdığı metin o dilin komutu olarak çalışmasın, hep düz kelime olsun.
    """
    # Python'da "İ".lower() tek harf değil, "i" + birleşik nokta (U+0307) iki karakter verir;
    # \w o noktayı harf saymaz ve "İhracat"ı "i" + "hracat" diye böler. Önce elle çeviriyoruz.
    metin = metin.replace("İ", "i").replace("I", "i").replace("ı", "i")  # dizindeki ı→i'nin aynısı
    kelimeler = re.findall(r"\w+", metin.lower())     # noktalama ve operatörler düşer
    parcalar = [
        f'"{k}"*' if len(k) >= KISA_KELIME else f'"{k}"'
        for k in kelimeler
    ]
    # OR: kelimelerden biri geçen her belge aday; BM25 daha çok kelime tutanı zaten öne alır.
    return " OR ".join(parcalar)


def ara(
    db: sqlite3.Connection,
    sorgu: str,
    *,
    gun: int | None = None,
    tur: str | None = None,
    sembol: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Belgelerde kelime araması yapar, en alakalıdan başlayarak döner.

    Args:
        sorgu: serbest metin, ör. "temettü ödemesi"
        gun: yalnız son N günün belgeleri
        tur: "kap" ya da "haber"
        sembol: yalnız bu hissenin KAP bildirimleri, ör. "ASELS"
        limit: kaç sonuç (en fazla 50)
    """
    fts = fts_sorgusu(sorgu)
    if not fts:
        return []

    kosullar, parametreler = ["belgeler_fts MATCH ?"], [fts]
    if gun is not None:
        sinir = datetime.now(timezone.utc) - timedelta(days=gun)
        # Zamanları hep aynı biçimde (YYYY-MM-DDTHH:MM:SSZ) yazdığımız için metin
        # karşılaştırması tarih karşılaştırmasıyla aynı sonucu verir.
        kosullar.append("b.yayin_zamani >= ?")
        parametreler.append(sinir.strftime("%Y-%m-%dT%H:%M:%SZ"))
    if tur is not None:
        kosullar.append("b.tur = ?")
        parametreler.append(tur)
    if sembol is not None:
        kosullar.append("b.sembol = ?")
        parametreler.append(sembol.upper())
    parametreler.append(max(1, min(limit, EN_FAZLA)))

    satirlar = db.execute(
        f"""SELECT b.id, b.tur, b.kaynak, b.sembol, b.baslik, b.ozet, b.url, b.yayin_zamani,
                   bm25(belgeler_fts, {AGIRLIK}) AS puan
            FROM belgeler_fts JOIN belgeler b ON b.id = belgeler_fts.rowid
            WHERE {" AND ".join(kosullar)}
            ORDER BY puan
            LIMIT ?""",
        parametreler,
    ).fetchall()

    return [
        {
            **dict(s),
            "ozet": (s["ozet"] or "")[:OZET_SINIRI] or None,
            "puan": round(-s["puan"], 2),  # SQLite'ta küçük = iyi; dışarıya büyük = iyi diye veriyoruz
        }
        for s in satirlar
    ]
