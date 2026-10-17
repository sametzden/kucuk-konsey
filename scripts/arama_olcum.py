"""Arama ölçümü: aynı sorularda kelime araması ve embedding modellerini yarıştırır.

Sorular bilerek belgenin kendi kelimeleriyle yazılmadı ("temettü" → başlıkta "Kar Payı"):
anlamsal aramanın var olma sebebi tam bu durum. Bir soru "bulundu" sayılır, eğer beklenen
başlık kalıbına uyan bir belge ilk 5 sonuçta varsa (isabet@5).

Veritabanına yazmaz: her model vektörleri bellekte üretir, sonuç tabloda karşılaştırılır.

Kullanım:
    uv run python -m scripts.arama_olcum           # kayıtlı yöntemler: kelime, anlam, hibrit
    uv run python -m scripts.arama_olcum --hepsi   # + embedding modelleri yarışı (dakikalar)
"""

import re
import sys
import time

import numpy as np

from arama import anlam, hibrit, kelime
from toplayici.db import baglan

ILK = 5

# (soru, beklenen başlık kalıbı: regex, büyük/küçük harf duyarsız)
SORULAR = [
    ("temettü", r"kar payı"),
    ("hisse geri alımı", r"payların geri alınması"),
    ("şirket yeni müşteriyle sözleşme imzaladı", r"yeni iş ilişkisi"),
    ("kredi notu", r"kredi derecelendirme"),
    ("merkez bankası faiz politikası", r"tcmb|fed|merkez bankası"),
    ("personel azaltımı", r"işgücü|işten çıkar"),
    ("yurt dışına meyve sebze satışı", r"meyve|tarım ürünleri"),
    ("enerji arzı ve savaş riski", r"hürmüz|rafineri|petrol arz"),
]

# Her model kendi ön ekleriyle eğitildi: e5 "query:/passage:" ister, bge-m3 ön eksiz çalışır.
MODELLER = {
    "intfloat/multilingual-e5-small": ("query: ", "passage: "),
    "intfloat/multilingual-e5-base": ("query: ", "passage: "),
    "BAAI/bge-m3": ("", ""),
}


def isabet(basliklar: list[str], kalip: str) -> bool:
    return any(re.search(kalip, b, re.I) for b in basliklar[:ILK])


def main():
    db = baglan()
    belgeler = db.execute("SELECT id, baslik, ozet, metin FROM belgeler ORDER BY id").fetchall()
    basliklar = [b["baslik"] for b in belgeler]
    metinler = ["\n".join(p for p in (b["baslik"], b["ozet"], b["metin"]) if p) for b in belgeler]

    # Soru setinin kendisini denetle: beklenen belge veritabanında hiç yoksa ölçüm anlamsız.
    for soru, kalip in SORULAR:
        n = sum(bool(re.search(kalip, b, re.I)) for b in basliklar)
        assert n, f"'{soru}' için veritabanında beklenen belge yok ({kalip})"

    # Kayıtlı yöntemler: projenin gerçekte kullandığı arama fonksiyonları (anlam = veritabanındaki vektörler).
    sonuclar = {
        ad: [isabet([s["baslik"] for s in fonk(db, soru, limit=ILK)], kalip) for soru, kalip in SORULAR]
        for ad, fonk in [("FTS5 (kelime)", kelime.ara), ("anlam (kayıtlı)", anlam.ara), ("hibrit (RRF)", hibrit.ara)]
    }
    if "--hepsi" not in sys.argv:   # model yarışı birkaç dakika sürer, yalnız istenince
        tablo(sonuclar)
        return

    from sentence_transformers import SentenceTransformer

    for ad, (sorgu_eki, belge_eki) in MODELLER.items():
        model = SentenceTransformer(ad)
        model.max_seq_length = 512   # bge-m3 varsayılanı 8192; belgelerimiz kısa, bellek boşa gitmesin
        t = time.perf_counter()
        B = model.encode([belge_eki + m for m in metinler], batch_size=16, normalize_embeddings=True)
        S = model.encode([sorgu_eki + s for s, _ in SORULAR], normalize_embeddings=True)
        sure = time.perf_counter() - t
        puanlar = S @ B.T                         # (soru × belge) benzerlik matrisi, tek çarpım
        sira = np.argsort(-puanlar, axis=1)[:, :ILK]
        sonuclar[f"{ad.split('/')[1]} ({sure:.0f} sn)"] = [
            isabet([basliklar[j] for j in sira[i]], kalip) for i, (_, kalip) in enumerate(SORULAR)
        ]
        del model

    tablo(sonuclar)


def tablo(sonuclar: dict[str, list[bool]]):
    """Satır = soru, sütun = yöntem."""
    adlar = list(sonuclar)
    print(f"{'soru':42}" + "".join(f"{a[:22]:>24}" for a in adlar))
    for i, (soru, _) in enumerate(SORULAR):
        print(f"{soru[:40]:42}" + "".join(f"{'✓' if sonuclar[a][i] else '·':>24}" for a in adlar))
    print(f"{'isabet@5':42}" + "".join(f"{sum(sonuclar[a]):>21}/{len(SORULAR)}" for a in adlar))


if __name__ == "__main__":
    main()
