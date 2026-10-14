"""Tyrion özetinin biçim bekçisi (gündem ve derin); finansal doğruluk veya kaynak doğrulayıcısı değildir."""
import re
import sys
from pathlib import Path

KELIME_SINIRI = 400  # 23.09: 220 telgraf diline itiyordu, Samet 400 dedi
FIELDS = ("Bugün", "Neden önemli", "Fırsat", "Risk", "Neyi izle")
GUNDEM_ALANLARI = ("Haftanın hikâyesi", "İyi gidebilecekler", "Kötüye gidebilecekler", "Piyasa",
                   "Neyi izle", "Derin bakmaya değer")


def _sayi_var(metin):
    """Bağlantıları çıkarıp rakam ya da yüzde arar: Neyi izle'de eşik yazılmaz."""
    return re.search(r"\d|%", re.sub(r"\[[^\]]+\]\([^)]+\)", "", metin))


def kontrol(text):
    m = re.search(r"^## Tyrion'un sözü\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return ["Tyrion özeti yok"]
    summary = m[1]
    errors = []
    if len(summary.split()) > KELIME_SINIRI:
        errors.append(f"Özet {KELIME_SINIRI} kelimeyi aşıyor")
    if re.search(r"^mod:\s*gundem\s*$", text, re.M):
        return errors + _gundem(summary)
    return errors + _derin(summary)


def _gundem(summary):
    errors = []
    for alan in GUNDEM_ALANLARI:
        # "Haftanın başı:" ilk turun kabul edilen biçimi
        desen = r"Haftanın (?:hikâyesi|başı)" if alan == "Haftanın hikâyesi" else re.escape(alan)
        degerler = re.findall(r"^\*\*(?:" + desen + r"):\*\*\s*(.+)$", summary, re.M)
        if len(degerler) != 1 or not degerler[0].strip():
            errors.append(f"{alan} satırı tek ve dolu olmalı")
    blok = re.search(r"^\*\*Önemli olanlar\*\*\s*\n(.*?)(?=^\*\*[^*\n]+:\*\*|\Z)", summary, re.M | re.S)
    if not blok:
        errors.append("Önemli olanlar listesi yok")
    else:
        maddeler = re.split(r"^\d+\.\s", blok[1], flags=re.M)[1:]
        if not 3 <= len(maddeler) <= 5:
            errors.append(f"Önemli olanlar 3-5 madde olmalı ({len(maddeler)} var)")
        for i, madde in enumerate(maddeler, 1):
            if "**Neden önemli:**" not in madde:
                errors.append(f"Önemli olanlar {i}. madde: Neden önemli yok")
    izle = re.search(r"^\*\*Neyi izle:\*\*\s*(.+)$", summary, re.M)
    if izle and _sayi_var(izle[1]):
        errors.append("Neyi izle: teknik eşik/sayı özette yazılamaz; iddiaya bağlan")
    return errors


def _derin(summary):
    errors = []
    cards = re.split(r"^\*\*([A-Z]{4,6})\*\*\s*$", summary, flags=re.M)[1:]
    if not cards or len(cards) // 2 > 5:
        errors.append("Bir ila beş hisse kartı gerekli")
    for symbol, body in zip(cards[::2], cards[1::2]):
        for field in FIELDS:
            values = re.findall(r"^- \*\*" + field + r":\*\*\s*([^\n]+)", body, re.M)
            if len(values) != 1 or not values[0].strip():
                errors.append(f"{symbol}: {field} alanı tek ve dolu olmalı")
            elif field == "Neyi izle":
                if _sayi_var(values[0]):
                    errors.append(f"{symbol}: teknik eşik/dönem özette yeniden yazılamaz; iddiaya bağlan")
    return errors

if __name__ == "__main__":
    errors = kontrol(Path(sys.argv[1]).read_text())
    print("\n".join(errors) if errors else "Özet kontrolü geçti")
    sys.exit(bool(errors))
