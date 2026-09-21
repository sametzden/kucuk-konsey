from pathlib import Path

import pytest

from kap.metin import BildirimOkunamadi, bildirim_metni

FIXTURE = Path(__file__).parent / "fixtures" / "asels_1665180.html"


def test_asels_yatirim_bildirimi_okunur():
    sonuc = bildirim_metni(FIXTURE.read_text())

    assert sonuc["ozet"] == "Devreye Alınan Yatırımımız Hakkında"
    assert "56 milyon ABD Doları" in sonuc["metin"]
    # İngilizce kopya karışmamalı, script içindeki kaçışlı kopya da.
    assert "ASELSAN continues" not in sonuc["metin"]
    assert "\\u003c" not in sonuc["metin"]


def test_yapi_yoksa_bagirir():
    # Sayfa yapısı değişirse boş sonuç değil hata bekliyoruz.
    with pytest.raises(BildirimOkunamadi):
        bildirim_metni("<html><body><p>tasarım değişti</p></body></html>")


def test_finansal_rapor_metinsiz_ama_uyarili():
    sonuc = bildirim_metni((FIXTURE.parent / "asels_1643141_finansal.html").read_text())

    assert sonuc["ozet"] == "30 Haziran 2026 Finansal Tabloları"
    assert sonuc["metin"] == ""
    assert "uyari" in sonuc
