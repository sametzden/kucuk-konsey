"""KAP bildirim sayfasından okunabilir metin çıkarır.

KAP bildirimleri XBRL formudur: metin, taksonomi alanlarının (oda_ExplanationTextBlock gibi)
içindeki `text-block-value` kutularında durur. Sitenin görsel tasarımına değil bu veri yapısına
bağlanıyoruz; tasarım değişse de form yapısı daha kalıcıdır.
"""

from bs4 import BeautifulSoup


class BildirimOkunamadi(Exception):
    """Sayfa geldi ama beklenen yapı yok. Sessizce boş dönmek yerine bağırırız."""


def _temizle(metin: str) -> str:
    # &nbsp; ve satır kırıklarıyla dolu metni tek boşluklu hâle getirir.
    return " ".join(metin.split())


def bildirim_metni(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for etiket in soup(["script", "style"]):
        etiket.decompose()

    ozet_el = soup.select_one("div.disclosureSummary")
    ozet = _temizle(ozet_el.get_text(" ")) if ozet_el else ""

    # Sadece Türkçe içerik: KAP her alanı content-tr ve content-en olarak iki dilde basar.
    bloklar = [
        _temizle(el.get_text(" "))
        for el in soup.select(".content-tr .text-block-value")
    ]
    bloklar = [b for b in bloklar if b]

    if not bloklar and not ozet:
        raise BildirimOkunamadi(
            "Ne özet ne metin bulundu. KAP sayfa yapısı değişmiş olabilir."
        )

    sonuc = {"ozet": ozet, "metin": "\n\n".join(bloklar)}
    if not bloklar:
        # Özet var ama metin yok: finansal rapor, faaliyet raporu gibi içeriği ekte ya da
        # tabloda olan bildirimler. Boş metni "içerik yok" diye okunmaya bırakmıyoruz.
        sonuc["uyari"] = (
            "Metin alanı yok. İçerik büyük ihtimalle ekte (PDF) veya tablolarda; "
            "bu araç onları okumaz. Rakamlar için borsa MCP'nin bilanço araçlarını kullan."
        )
    return sonuc
