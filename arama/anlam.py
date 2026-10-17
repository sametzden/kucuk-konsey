"""Anlamsal arama: belgeleri embedding vektörüne çevirip anlamca yakın olanları bulur.

Kelime araması (kelime.py) yalnız yazılan kelimeyi bulur: "temettü" arayan, içinde sadece
"kâr payı" geçen bildirimi kaçırır. Embedding modeli metni, anlamını temsil eden 768 sayılık bir
vektöre çevirir; anlamca yakın metinlerin vektörleri de birbirine yakın düşer.

İki iş: vektörleri üretip saklamak (ilk seferde hepsini, sonra yalnız yeni belgeleri) ve aramak.

Kullanım:
    uv run python -m arama.anlam      # eksik vektörleri doldurur
    from arama.anlam import ara
    ara(db, "temettü ödemesi", tur="kap")
"""

import sqlite3

import numpy as np

from arama.kelime import EN_FAZLA, OZET_SINIRI, filtreler

# 15 Eki ölçümü (scripts/arama_olcum.py, isabet@5): e5-small 4/8, e5-base 6/8, bge-m3 4/8.
# En büyük model (bge-m3, 568M) kazanmadı; orta boy e5-base hem daha isabetli hem 2 kat hızlı.
MODEL_ADI = "intfloat/multilingual-e5-base"   # Türkçe dahil ~100 dil, 278M parametre, 768 boyut
# Model 512 token'dan sonrasını görmez, sessizce keser. Belgelerin ortalaması ~350 karakter, en uzun
# KAP metni ~3.800; Türkçede token başına 3-4 karakter düşer, yani yalnız birkaç bildirimin sonu kesilir.
PARTI = 32  # modele tek seferde verilen belge sayısı: GPU belleği (4 GB) ile hız arasında denge

_model = None


def model():
    """Modeli ilk çağrıda yükler, sonra aynısını verir: yükleme saniyeler sürer, her aramada olmasın."""
    global _model
    if _model is None:
        # Ağır import (PyTorch'u da yükler): yalnız kelime araması yapan süreç bunu hiç ödemesin.
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_ADI)
    return _model


def belge_metni(satir: sqlite3.Row) -> str:
    """Bir belgenin modele gidecek metni: başlık + özet + tam metin."""
    parcalar = [satir["baslik"], satir["ozet"], satir["metin"]]
    # e5 modelleri ön ek ister: belgeye "passage: ", soruya "query: ". Model böyle eğitildi;
    # ön eki unutmak hata vermez, sadece sonuçları sessizce kötüleştirir.
    return "passage: " + "\n".join(p for p in parcalar if p)


def eksikleri_doldur(db: sqlite3.Connection, parti: int = PARTI) -> int:
    """Vektörü olmayan (ya da başka modelle üretilmiş) belgeleri vektöre çevirir. Kaç belge işlendiğini döner."""
    # LEFT JOIN + IS NULL: "belgeler'de olup bu modelle belgeler_vektor'de olmayan" satırlar.
    satirlar = db.execute(
        """SELECT b.id, b.baslik, b.ozet, b.metin
           FROM belgeler b
           LEFT JOIN belgeler_vektor v ON v.belge_id = b.id AND v.model = ?
           WHERE v.belge_id IS NULL
           ORDER BY b.id""",
        (MODEL_ADI,),
    ).fetchall()
    if not satirlar:
        return 0

    vektorler = model().encode(
        [belge_metni(s) for s in satirlar],
        batch_size=parti,
        # Boyu 1'e eşitlenmiş vektörlerde kosinüs benzerliği = iç çarpım: aramada tek matris çarpımı yeter.
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=len(satirlar) > 100,
    )

    # INSERT OR REPLACE: belge_id birincil anahtar, eski modelin satırı varsa yenisiyle değişir.
    db.executemany(
        "INSERT OR REPLACE INTO belgeler_vektor (belge_id, model, vektor) VALUES (?, ?, ?)",
        [(s["id"], MODEL_ADI, v.astype(np.float32).tobytes()) for s, v in zip(satirlar, vektorler)],
    )
    db.commit()
    return len(satirlar)


def sorgu_vektoru(sorgu: str) -> np.ndarray:
    """Soruyu belgelerle aynı uzaya çevirir. Ön ek bu sefer "query: "."""
    return model().encode("query: " + sorgu, normalize_embeddings=True, convert_to_numpy=True,
                          show_progress_bar=False)  # tek cümle: ilerleme çubuğu sadece gürültü


def ara(
    db: sqlite3.Connection,
    sorgu: str,
    *,
    gun: int | None = None,
    tur: str | None = None,
    sembol: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Belgelerde anlamsal arama yapar, anlamca en yakından başlayarak döner.

    Parametreler ve dönüş biçimi kelime.ara ile aynı: ajan iki aramayı birbirinin yerine kullanabilir.
    puan: kosinüs benzerliği. e5'te alakasız belgeler bile ~0.7 alır, anlamlı olan mutlak değer değil sıra.
    """
    if not sorgu.strip():
        return []

    kosullar, parametreler = filtreler(gun=gun, tur=tur, sembol=sembol)
    kosullar.insert(0, "v.model = ?")
    parametreler.insert(0, MODEL_ADI)

    # Süzgeçten geçen her belgenin vektörünü çekiyoruz: ~1.300 belge × 3 KB ≈ 4 MB, milisaniyeler.
    satirlar = db.execute(
        f"""SELECT b.id, b.tur, b.kaynak, b.sembol, b.baslik, b.ozet, b.url, b.yayin_zamani, v.vektor
            FROM belgeler b JOIN belgeler_vektor v ON v.belge_id = b.id
            WHERE {" AND ".join(kosullar)}""",
        parametreler,
    ).fetchall()
    if not satirlar:
        return []

    # Baytları geri sayıya çevirip alt alta diz: (belge sayısı × 768) boyutunda bir matris.
    matris = np.frombuffer(b"".join(s["vektor"] for s in satirlar), dtype=np.float32)
    matris = matris.reshape(len(satirlar), -1)
    # Vektörler normalize: matris @ sorgu = her belgenin soruyla kosinüs benzerliği, tek çarpımda.
    puanlar = matris @ sorgu_vektoru(sorgu)

    limit = max(1, min(limit, EN_FAZLA))
    en_iyiler = np.argsort(-puanlar)[:limit]   # argsort küçükten büyüğe sıralar, eksiyle ters çeviriyoruz

    sonuc = []
    for i in en_iyiler:
        s = satirlar[i]
        sonuc.append({
            **{k: s[k] for k in s.keys() if k != "vektor"},
            "ozet": (s["ozet"] or "")[:OZET_SINIRI] or None,
            "puan": round(float(puanlar[i]), 3),
        })
    return sonuc


if __name__ == "__main__":
    from toplayici.db import baglan

    n = eksikleri_doldur(baglan())
    print(f"{n} belge vektöre çevrildi ({MODEL_ADI})")
