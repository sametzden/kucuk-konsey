"""V2 özet biçimi bekçisi; finansal doğruluk veya kaynak doğrulayıcısı değildir."""
import re
import sys
from pathlib import Path

KELIME_SINIRI = 400  # 23.09: 220 telgraf diline itiyordu, Samet 400 dedi
FIELDS = ("Bugün", "Neden önemli", "Fırsat", "Risk", "Neyi izle")

def kontrol(text):
    errors = []
    m = re.search(r"^## Tyrion'un sözü\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return ["Tyrion özeti yok"]
    summary = m[1]
    if len(summary.split()) > KELIME_SINIRI:
        errors.append(f"Özet {KELIME_SINIRI} kelimeyi aşıyor")
    cards = re.split(r"^\*\*([A-Z]{4,6})\*\*\s*$", summary, flags=re.M)[1:]
    if not cards or len(cards) // 2 > 5:
        errors.append("Bir ila beş hisse kartı gerekli")
    for symbol, body in zip(cards[::2], cards[1::2]):
        for field in FIELDS:
            values = re.findall(r"^- \*\*" + field + r":\*\*\s*([^\n]+)", body, re.M)
            if len(values) != 1 or not values[0].strip():
                errors.append(f"{symbol}: {field} alanı tek ve dolu olmalı")
            elif field == "Neyi izle":
                plain = re.sub(r"\[[^\]]+\]\([^)]+\)", "", values[0])
                if re.search(r"\d|%", plain):
                    errors.append(f"{symbol}: teknik eşik/dönem özette yeniden yazılamaz; iddiaya bağlan")
    return errors

if __name__ == "__main__":
    errors = kontrol(Path(sys.argv[1]).read_text())
    print("\n".join(errors) if errors else "V2 özet kontrolü geçti")
    sys.exit(bool(errors))
