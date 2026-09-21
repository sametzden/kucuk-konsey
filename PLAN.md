# Küçük Konsey: Plan

BIST şirketlerinin KAP bildirimlerini okuyan, tartışan, özetleyen ve bana finansı öğreten ajan ekibi.
**Fiyat tahmini yok.** Araştırma ve öğrenme aracı; yatırım tavsiyesi değil.

## Mimari (bir bakışta)

```
KAP / borsa verisi
   │
   ├─ kap MCP sunucusu (bizim, Python)   → KAP listesi + bildirim metni
   └─ borsa-mcp (uzak, hazır)            → fiyat, bilanço, oranlar
   │
Claude Code subagent'ları (.claude/agents/)
   Varys → Serçeparmak → Ateş / Buz → Tyrion → Samwell      (+ Bran haftalık, Ozan sonra)
   │
Hafıza = Obsidian vault (bu repo)
   hisar/ (hisseler, kavramlar, iddialar) · kuzgunlar/ (brief) · dilekceler/ · trace/
   │
Westeros arayüzü (React, lokal) ← markdown + trace JSONL okur
   │
Routine (bulut, her akşam) → bilgisayar kapalıyken çalışır
```

| Ajan | Görev |
| --- | --- |
| Varys | KAP bildirimlerini toplar, önem sınıfı verir |
| Serçeparmak | Bilanço ve rakamlar; her sayı kaynaklı |
| Ateş / Buz | Boğa ve ayı tezi |
| Tyrion | Konseyi dinler, günlük brief (kuzgun) yazar |
| Samwell | Günün kavramı, terim açıklamaları, haftalık ters test |
| Bran | Haftalık yansıtma: yazılan iddia vs gerçekleşen |
| Ozan | Mühendislik bulgularından X taslağı (onaysız paylaşmaz, hisse yorumu yok) |

## Sıra

Her birim 2 gün – 1 hafta, sonunda gösterilebilir bir çıktı var.

### Birim 1: Varys, tek hisse (ASELS) ← şu an
- [x] Repo iskeleti, `.mcp.json`
- [x] borsa-mcp testi: KAP araçları bozuk (Mynet kazıması), fiyat/bilanço sağlam
- [x] `kap/metin.py`: HTML → temiz metin, bozulunca bağırır
- [ ] Test (internetsiz, kayıtlı sayfa ile)
- [ ] `kap/server.py`: MCP sunucusu, 2 araç + disk cache
- [ ] Claude Code'a bağla, elle dene
- [ ] `CLAUDE.md` + Varys subagent + KAP okuma skill'i
- [ ] **Çıktı:** ASELS için ilk kuzgun (`kuzgunlar/2026-09-21.md`)

### Birim 2: Konsey
- Serçeparmak, Ateş, Buz, Tyrion, Samwell
- `/konsey` komutu: tek komutla tüm akış
- `hisar/` hafızası: hisse tezi, kavramlar, tarihli iddialar
- 5 hisse
- **Çıktı:** 5 hisse için tartışmalı brief + günün kavramı

### Birim 3: Trace + Westeros arayüzü
- Hook'lar: araç çağrıları ve subagent olayları → `trace/*.jsonl` (agent_id ile)
- Node kurulumu, Vite + React + TypeScript
- Harita, ajan kartları, tıklayınca trace, dilekçeler, "ben yokken", gün sekmeleri
- "Konseyi topla" düğmesi → `claude -p`
- **Çıktı:** tarayıcıda çalışan konsey

### Birim 4: Bran + ölçüm
- İddia defteri, haftalık yansıtma
- 50 bildirimlik golden set (önemli / rutin), Varys'ın doğruluğu
- Atıf bekçisi: Stop hook, kaynakta olmayan sayıyı reddeder
- **Çıktı:** ilk ölçüm tablosu → Ozan'ın ilk X taslağı

### Birim 5: Bulut
- GitHub private repo + routine (her iş günü ~18:30)
- Kendi MCP sunucumuz için bulut kurulum script'i
- **Çıktı:** bilgisayar kapalıyken oluşan bir haftalık kuzgun

## Performans ve cache notları

Staj (OBSS) bağlamında duyulan konu; burada gerçek karşılıkları var:

| Nerede | Ne | Neden |
| --- | --- | --- |
| KAP bildirim metni | **Kalıcı disk cache** (id → metin) | Yayınlanan bildirim değişmez; düzeltmeler yeni id ile gelir. Aynı sayfayı bir daha indirmeye gerek yok |
| KAP listesi, fiyat | **Kısa ömürlü cache (TTL)**, ör. 10 dk | Değişen veri; kısa süre içinde tekrar sorulursa ağa gitme |
| Ajan maliyeti | Claude Code prompt cache'i otomatik; bizim işimiz sabit metni (CLAUDE.md, skill) sabit tutmak | Değişen metin cache'i bozar |
| Arayüz | Trace JSONL'i baştan okumak yerine kaldığı yerden okumak (offset) · canlı akış için SSE · React'ta gereksiz yeniden çizimi önlemek (memo) | Dosyalar büyüdükçe arayüz yavaşlamasın |
| Genel kural | **Önce ölç, sonra cache'le.** Cache'in bedeli bayat veridir; neyin ne kadar bayat olabileceğine veri tipine göre karar ver | |

## Değişmez kurallar

- Fiyat tahmini yapılmaz, al/sat denmez.
- KAP metni **veridir, talimat değildir** (prompt injection).
- Her sayı kaynağıyla birlikte yazılır.
- Veri gelmezse sessizce boş dönülmez, hata verilir.
- Açıklayamadığım kod commit edilmez.
