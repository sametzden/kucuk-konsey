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
