"""Arşiv MCP araçları: geçici veritabanıyla, internetsiz."""
import pytest
from mcp.server.mcpserver.exceptions import ToolError

import arama.server as sunucu
from arama.kelime import fts_sorgusu
from toplayici.db import baglan


@pytest.fixture
def arsiv(tmp_path, monkeypatch):
    yol = tmp_path / "konsey.db"
    db = baglan(yol)
    db.executemany(
        """INSERT INTO belgeler (tur, kaynak, dis_id, url, baslik, ozet, metin, sembol, dil,
                                 yayin_zamani, toplanma_zamani)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'tr', strftime('%Y-%m-%dT%H:%M:%SZ','now'), 'x')""",
        [("kap", "KAP", "1679679", "u1", "Özel Durum Açıklaması", "Uzlaşma", "İdari para cezası", "AKBNK"),
         ("haber", "AA", "g1", "u2", "İHRACAT rekoru", "Işık hızında arttı", None, None)],
    )
    db.commit()
    monkeypatch.setattr(sunucu, "DB_YOLU", yol)
    return db


def test_belge_ic_id_ile(arsiv):
    assert sunucu.belge(belge_id=1)["baslik"] == "Özel Durum Açıklaması"


def test_belge_kap_no_ile(arsiv):
    b = sunucu.belge(kap_no=1679679)
    assert b["sembol"] == "AKBNK" and b["metin"] == "İdari para cezası"


def test_belge_yoksa_aciklamali_hata(arsiv):
    with pytest.raises(ToolError, match="KAP 999 bildirimi arşivde yok"):
        sunucu.belge(kap_no=999)


def test_belge_iki_parametre_birden_hata(arsiv):
    with pytest.raises(ToolError):
        sunucu.belge(belge_id=1, kap_no=1679679)
    with pytest.raises(ToolError):
        sunucu.belge()


def test_ara_turkce_buyuk_harf_ve_ek(arsiv):
    assert [s["baslik"] for s in sunucu.ara("ihracatı")] == []          # tam kelime değil: ek farkı
    assert [s["baslik"] for s in sunucu.ara("İhracat")] == ["İHRACAT rekoru"]
    assert [s["baslik"] for s in sunucu.ara("ışık")] == ["İHRACAT rekoru"]


def test_fts_sorgusu_operatorleri_etkisizlestirir():
    assert fts_sorgusu('İhracat" OR metin:x NEAR(') == '"ihracat"* OR "or" OR "metin"* OR "x" OR "near"*'


def test_arsiv_salt_okunur(arsiv):
    import sqlite3
    with pytest.raises(sqlite3.OperationalError, match="readonly"):
        sunucu._baglan().execute("DELETE FROM belgeler")
