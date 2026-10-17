"""Toplayıcının veritabanı: KAP bildirimleri, haberler ve fiyatlar tek SQLite dosyasında.

Neden SQLite: tek kullanıcı, tek yazan süreç (toplayıcı), haftada birkaç okuma. Sunucu yok,
yedek = dosyayı kopyalamak. Eşzamanlı yazan çoğalırsa ya da vektör araması aynı yerde
gerekirse Postgres (+ pgvector) sıradaki adım.
"""

import sqlite3
from pathlib import Path

DB_YOLU = Path(__file__).resolve().parent.parent / "veri" / "konsey.db"

SEMA = """
-- KAP bildirimi de haber de bir "belge": RAG ikisini aynı yerden arayacak.
CREATE TABLE IF NOT EXISTS belgeler (
    id              INTEGER PRIMARY KEY,
    tur             TEXT NOT NULL CHECK (tur IN ('kap', 'haber')),
    kaynak          TEXT NOT NULL,   -- 'KAP', 'Bloomberg HT', 'CNBC' ...
    dis_id          TEXT NOT NULL,   -- KAP bildirim no ya da haberin linki
    url             TEXT NOT NULL,
    baslik          TEXT NOT NULL,
    ozet            TEXT,            -- KAP özet satırı ya da RSS açıklaması
    metin           TEXT,            -- tam metin: KAP'ta var, haberde şimdilik yok
    sembol          TEXT,            -- KAP: şirket kodu. Haber: boş, etiketi ajan koyacak
    dil             TEXT NOT NULL CHECK (dil IN ('tr', 'en')),
    yayin_zamani    TEXT NOT NULL,   -- ISO 8601, UTC
    toplanma_zamani TEXT NOT NULL,   -- ISO 8601, UTC
    UNIQUE (kaynak, dis_id)          -- aynı belge iki kez girmez
);
CREATE INDEX IF NOT EXISTS ix_belgeler_yayin  ON belgeler (yayin_zamani);
CREATE INDEX IF NOT EXISTS ix_belgeler_sembol ON belgeler (sembol, yayin_zamani);

-- Günlük kapanış. Değişim yüzdesi saklanmaz, ardışık iki kapanıştan hesaplanır.
CREATE TABLE IF NOT EXISTS fiyatlar (
    sembol  TEXT NOT NULL,
    tarih   TEXT NOT NULL,           -- YYYY-MM-DD
    kapanis REAL NOT NULL,
    hacim   REAL,
    PRIMARY KEY (sembol, tarih)
);

-- Tam metin arama dizini (FTS5). Metni ikinci kez saklamaz (content=''), sadece hangi kelime
-- hangi belgede geçiyor onu tutar; rowid = belgeler.id. Sıralama BM25 ile.
-- remove_diacritics 2: ş→s, ç→c, ğ→g, İ→i ("sirket" yazan "şirket"i bulur).
CREATE VIRTUAL TABLE IF NOT EXISTS belgeler_fts USING fts5(
    baslik, ozet, metin,
    content = '', contentless_delete = 1,
    tokenize = 'unicode61 remove_diacritics 2'
);

-- Tetikleyiciler: belgeler'e yazılan her satır dizine de kendiliğinden yazılır, unutmak mümkün değil.
-- replace('ı','i'): dizin "I"yı "i"ye çeviriyor ama "ı"ya dokunmuyor; "IŞIK" ile "ışık" ancak
-- ikisi de "isik" olunca buluşur. Sorgu tarafında aynı çeviriyi arama kodu yapar.
CREATE TRIGGER IF NOT EXISTS belgeler_fts_ekle AFTER INSERT ON belgeler BEGIN
    INSERT INTO belgeler_fts (rowid, baslik, ozet, metin) VALUES (
        new.id,
        replace(new.baslik, 'ı', 'i'),
        replace(coalesce(new.ozet, ''), 'ı', 'i'),
        replace(coalesce(new.metin, ''), 'ı', 'i'));
END;
CREATE TRIGGER IF NOT EXISTS belgeler_fts_sil AFTER DELETE ON belgeler BEGIN
    DELETE FROM belgeler_fts WHERE rowid = old.id;
END;

-- Anlamsal arama vektörleri (arama/anlam.py doldurur). 384 float32 = 1.536 bayt, BLOB olarak.
-- model sütunu: başka bir modelin vektörü başka bir "dil"dir, karşılaştırılamaz; model değişince
-- satır eskimiş sayılır ve yeniden üretilir.
-- Ekleme tetikleyicisi yok: SQL modeli çalıştıramaz, vektörü Python üretir. Silme ise SQL'de kalır.
CREATE TABLE IF NOT EXISTS belgeler_vektor (
    belge_id INTEGER PRIMARY KEY,   -- = belgeler.id
    model    TEXT NOT NULL,
    vektor   BLOB NOT NULL
);
CREATE TRIGGER IF NOT EXISTS belgeler_vektor_sil AFTER DELETE ON belgeler BEGIN
    DELETE FROM belgeler_vektor WHERE belge_id = old.id;
END;
"""

# Tetikleyiciler yalnız yeni satırları görür. Dizin ilk kez kurulduğunda eski satırları bir kez doldurur.
DIZINI_DOLDUR = """
INSERT INTO belgeler_fts (rowid, baslik, ozet, metin)
SELECT id, replace(baslik, 'ı', 'i'), replace(coalesce(ozet, ''), 'ı', 'i'),
       replace(coalesce(metin, ''), 'ı', 'i')
FROM belgeler
"""


def baglan(yol: Path = DB_YOLU) -> sqlite3.Connection:
    yol.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(yol)
    db.row_factory = sqlite3.Row          # satırlara sütun adıyla erişim: satir["baslik"]
    db.execute("PRAGMA journal_mode=WAL")  # toplayıcı yazarken ajanlar okuyabilsin
    dizin_yoktu = db.execute(
        "SELECT 1 FROM sqlite_master WHERE name = 'belgeler_fts'").fetchone() is None
    db.executescript(SEMA)                 # IF NOT EXISTS: her bağlantıda güvenle çalışır
    if dizin_yoktu:
        db.execute(DIZINI_DOLDUR)
        db.commit()
    return db
