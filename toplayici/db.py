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
"""


def baglan(yol: Path = DB_YOLU) -> sqlite3.Connection:
    yol.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(yol)
    db.row_factory = sqlite3.Row          # satırlara sütun adıyla erişim: satir["baslik"]
    db.execute("PRAGMA journal_mode=WAL")  # toplayıcı yazarken ajanlar okuyabilsin
    db.executescript(SEMA)                 # IF NOT EXISTS: her bağlantıda güvenle çalışır
    return db
