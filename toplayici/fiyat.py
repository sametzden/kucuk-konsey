"""BIST 30'un günlük kapanışlarını borsapy'den çekip veritabanına yazar.

Çalıştır: uv run python -m toplayici.fiyat
"""

import math
import time

import borsapy as bp

from toplayici import ENDEKS
from toplayici.db import baglan

# Her çalıştırmada son 1 ay: bilgisayar birkaç gün kapalı kalsa da eksik günler kendiliğinden dolar.
# borsapy hisseleri tek tek çeker (~2 sn/hisse, tur ~1 dk). Günde 2 tur için paralelleştirmeye değmez.
DONEM = "1mo"


def topla(db, semboller: list[str] | None = None) -> dict:
    semboller = semboller or bp.Index(ENDEKS).component_symbols
    df = bp.download(semboller, period=DONEM, group_by="ticker", progress=False)
    rapor = {"sembol": len(semboller), "satir": 0, "eksik": []}

    for sembol in semboller:
        # Tek hissede borsapy düz sütun döner, çokluda (hisse, alan) çiftli sütun.
        if len(semboller) == 1:
            tablo = df
        elif sembol in df.columns.get_level_values(0):
            tablo = df[sembol]
        else:
            rapor["eksik"].append(sembol)
            continue

        for zaman, satir in tablo.iterrows():
            if math.isnan(satir["Close"]):  # işleme kapalı gün ya da eksik veri
                continue
            hacim = None if math.isnan(satir["Volume"]) else float(satir["Volume"])
            # Haberden farklı olarak bugünün satırı değişir: seans açıkken "Close" anlık fiyattır.
            # Bu yüzden IGNORE değil UPSERT: varsa üstüne yaz, akşamki tur gerçek kapanışı koyar.
            db.execute(
                """INSERT INTO fiyatlar (sembol, tarih, kapanis, hacim) VALUES (?, ?, ?, ?)
                   ON CONFLICT (sembol, tarih)
                   DO UPDATE SET kapanis = excluded.kapanis, hacim = excluded.hacim""",
                # Tarih borsanın kendi takvim günü (İstanbul). Zaman damgası değil, gün.
                (sembol, zaman.strftime("%Y-%m-%d"), float(satir["Close"]), hacim),
            )
            rapor["satir"] += 1

    db.commit()
    return rapor


if __name__ == "__main__":
    baslangic = time.time()
    rapor = topla(baglan())
    print(f"{rapor['sembol']} hisse · {rapor['satir']} satır yazıldı · {time.time() - baslangic:.1f} sn")
    if rapor["eksik"]:
        print("EKSİK", ", ".join(rapor["eksik"]))
