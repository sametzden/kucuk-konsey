from scripts.brief_kontrol import kontrol
from scripts.web_server import latest

def card(watch="Tahsilatı izle."):
    return "## Tyrion'un sözü\n\n**ASELS**\n" + "\n".join(
        f"- **{field}:** {watch if field == 'Neyi izle' else 'Veri yetersiz.'}"
        for field in ("Bugün", "Neden önemli", "Fırsat", "Risk", "Neyi izle")) + "\n## ASELS\n"

def test_summary_accepts_plain_watch():
    assert kontrol(card()) == []

def test_summary_rejects_rewritten_threshold():
    assert any("eşik" in e for e in kontrol(card("Oran 5 puan düşerse.")))

def test_summary_rejects_missing_fields():
    assert kontrol(card().replace("- **Risk:** Veri yetersiz.", ""))

def test_latest_reads_new_files_without_restart(tmp_path):
    folder = tmp_path / "kuzgunlar"
    folder.mkdir()
    assert latest(tmp_path) is None
    (folder / "2026-09-22.md").write_text("eski")
    assert latest(tmp_path)["metin"] == "eski"
    (folder / "2026-09-23.md").write_text("yeni")
    (folder / "notlar.md").write_text("rapor değil")
    assert latest(tmp_path)["metin"] == "yeni"
    (folder / "2026-09-23.md").write_text("güncellendi")
    assert latest(tmp_path)["metin"] == "güncellendi"

def test_summary_word_limit():
    long = card().replace("Veri yetersiz.", " ".join(["kelime"] * 90))
    assert kontrol(long) == []  # ~360 kelime: yeni sınırın içinde
    assert any("kelimeyi aşıyor" in e for e in kontrol(card().replace("Veri yetersiz.", " ".join(["kelime"] * 110))))


def gundem(maddeler=3, izle="TCMB'nin bir sonraki kararını izle.", neden=True):
    liste = "\n".join(
        f"{i}. **Olay {i}:** Bir şey oldu." + (" **Neden önemli:** Bankaları etkiler." if neden else "")
        for i in range(1, maddeler + 1))
    return ("---\ntarih: 2026-10-15\nmod: gundem\n---\n# Kuzgun\n\n## Tyrion'un sözü\n\n"
            "**Haftanın başı:** Hafta faiz beklentisiyle açıldı.\n\n**Önemli olanlar**\n" + liste + "\n\n"
            "**İyi gidebilecekler:** Veri yetersiz.\n**Kötüye gidebilecekler:** Veri yetersiz.\n"
            "**Piyasa:** Bankalar öne çıktı.\n**Neyi izle:** " + izle + "\n"
            "**Derin bakmaya değer:** Bu hafta yok.\n\n## Gündem\n")

def test_gundem_gecerli():
    assert kontrol(gundem()) == []

def test_gundem_madde_sayisi():
    assert any("3-5 madde" in e for e in kontrol(gundem(maddeler=2)))
    assert any("3-5 madde" in e for e in kontrol(gundem(maddeler=6)))

def test_gundem_neden_onemli_zorunlu():
    assert any("Neden önemli yok" in e for e in kontrol(gundem(neden=False)))

def test_gundem_neyi_izle_sayisiz():
    assert any("eşik" in e for e in kontrol(gundem(izle="Faiz %40'ı geçerse.")))

def test_gundem_eksik_alan():
    assert any("Derin bakmaya değer" in e for e in kontrol(gundem().replace("**Derin bakmaya değer:** Bu hafta yok.\n", "")))
