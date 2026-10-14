"""Üç toplayıcıyı sırayla çalıştırır. Zamanlayıcının çağırdığı tek komut budur.

Çalıştır: uv run python -m toplayici

Sıra bilinçli: haber önce (en hızlı, RSS penceresi kısa), fiyat sonra, KAP en son
(en yavaş, engellenirse tur ortasında durabilir; diğerlerini beklemeye almasın).
"""

import sys
import time
import traceback
from datetime import datetime

from toplayici import fiyat, haber, kap
from toplayici.db import baglan


def main() -> int:
    db = baglan()
    basarisiz = []
    print(f"=== toplayıcı · {datetime.now():%Y-%m-%d %H:%M}")

    for ad, modul in (("haber", haber), ("fiyat", fiyat), ("kap", kap)):
        baslangic = time.time()
        try:
            rapor = modul.topla(db)
        except Exception:
            # Bir toplayıcı tamamen çökerse (ör. borsapy endeks listesini veremedi)
            # diğerleri yine çalışır; hata ayrıntısıyla günlüğe düşer.
            basarisiz.append(ad)
            print(f"[{ad}] ÇÖKTÜ\n{traceback.format_exc()}")
            continue
        print(f"[{ad}] {time.time() - baslangic:.0f} sn · {rapor}")

    # Çıkış kodu zamanlayıcıya durumu söyler: 0 başarılı, 1 en az biri çöktü.
    # KAP'ın tur ortasında durması çöküş değil, rapordaki "durdu" alanında görünür.
    return 1 if basarisiz else 0


if __name__ == "__main__":
    sys.exit(main())
