"""Hibrit arama: kelime araması (FTS5) ile anlamsal aramayı tek listede birleştirir.

İkisi farklı soruları kaçırıyor (scripts/arama_olcum.py): kelime araması "personel azaltımı"nı bulmuyor
(belgede "işgücü" yazıyor), anlamsal arama "enerji arzı ve savaş riski"ni. Ölçüm 17 Eki, 1266 belge:
kelime 5/8, anlam 6/8, hibrit 6/8. Hibrit kelimenin bulduğu son soruyu kaybetti: o belge kelimede 1.,
anlamda 16. sıradaydı; RRF iki listede orta sıradaki belgeleri tek listede birinci olana tercih eder.

Sorun: iki aramanın puanları aynı ölçekte değil. BM25 0 ile 30 arası gezer, kosinüs 0.7 ile 0.9
arası. Toplanamazlar. Çözüm puanı değil sırayı kullanmak: RRF (Reciprocal Rank Fusion).
Her belge, girdiği her listeden 1 / (K + sıra) puan alır; iki listede birden üst sıradaysa öne geçer.

Kullanım:
    from arama.hibrit import ara
    ara(db, "temettü ödemesi", tur="kap")
"""

import sqlite3

from arama import anlam, kelime

# RRF'nin sabiti. Literatürdeki varsayılan 60 (Cormack ve ark., 2009). Büyük K sıralar arasındaki
# farkı yumuşatır: 1. ile 5. sıra arasında uçurum olmaz, iki listede orta sırada olan belge de yükselir.
K = 60
# Her aramadan kaç aday alınacağı, istenen sonucun katı olarak. Kelime aramasının 15. sıraya koyduğu
# belge anlamsalda 1. ise birleşimde öne çıkabilmeli; bunun için listelerin sonuçtan uzun olması gerek.
ADAY_KATI = 3


def ara(
    db: sqlite3.Connection,
    sorgu: str,
    *,
    gun: int | None = None,
    tur: str | None = None,
    sembol: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Kelime ve anlamsal aramayı RRF ile birleştirir. İmza ve dönüş kelime.ara ile aynı.

    puan: RRF puanı (iki listede de 1. olan belge 2/61 ≈ 0.033 alır). Mutlak değeri anlamsız, sıra önemli.
    Her sonuçta ayrıca "kaynak_sira": {"kelime": 3, "anlam": 1} gibi, hangi listede kaçıncı olduğu.
    """
    limit = max(1, min(limit, kelime.EN_FAZLA))
    aday = min(limit * ADAY_KATI, kelime.EN_FAZLA)
    suzgec = dict(gun=gun, tur=tur, sembol=sembol, limit=aday)

    listeler = {
        "kelime": kelime.ara(db, sorgu, **suzgec),
        "anlam": anlam.ara(db, sorgu, **suzgec),
    }

    puan: dict[int, float] = {}
    belge: dict[int, dict] = {}
    sira: dict[int, dict] = {}
    for ad, sonuclar in listeler.items():
        for i, s in enumerate(sonuclar, start=1):   # sıra 1'den başlar: 1. sıra 1/61 alır
            puan[s["id"]] = puan.get(s["id"], 0.0) + 1 / (K + i)
            belge.setdefault(s["id"], s)          # iki listede de varsa belge bilgisi aynı, ilkini tut
            sira.setdefault(s["id"], {})[ad] = i

    en_iyiler = sorted(puan, key=puan.get, reverse=True)[:limit]
    return [
        {**belge[i], "puan": round(puan[i], 4), "kaynak_sira": sira[i]}
        for i in en_iyiler
    ]
