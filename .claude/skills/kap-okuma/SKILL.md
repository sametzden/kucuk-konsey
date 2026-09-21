---
name: kap-okuma
description: KAP bildirimini okuma ve önem sınıfı verme rehberi. Bir BIST şirketinin KAP bildirimleri özetlenirken, önemli/rutin ayrımı yapılırken veya bildirim türü yorumlanırken kullan.
---

# KAP bildirimi nasıl okunur

## Önem sınıfları

| Sınıf | Anlamı | Örnek türler |
| --- | --- | --- |
| **🔴 önemli** | Şirketin işine, parasına veya ortaklık yapısına yeni bilgi | Yeni iş ilişkisi / sözleşme · yatırım · birleşme-devralma · sermaye artırımı (bedelli/bedelsiz) · kâr payı kararı · finansal rapor · dava · pay geri alım programı başlangıcı |
| **🟡 orta** | Bilgi var ama beklenen ya da küçük | Faaliyet raporu · genel kurul · kredi derecelendirme · yönetim değişikliği · geri alım işlem bildirimi |
| **⚪ rutin** | Yasal zorunluluk, yeni bilgi yok | Sorumluluk beyanı · şirket genel bilgi formu · katılım finansı bilgi formu · pay bazında devre kesici · haber ve söylentilere "bilgimiz yok" cevabı |

**Başlığa göre karar verme.** "Özel Durum Açıklaması (Genel)" başlığı hem 56 milyon dolarlık yatırımı
hem de önemsiz bir duyuruyu taşıyabilir. Sınıf metni okuduktan sonra verilir. Rutin türlerde metin
okunmayabilir, ama bu brief'te belirtilir.

Tutarı şirketin büyüklüğüyle kıyasla: 56 milyon USD ASELSAN için orta boy, küçük bir şirket için dev.
Kıyas için piyasa değeri `borsa` MCP'den (`get_quote`) alınabilir; alındıysa kaynağı yazılır.

## Her bildirim için çıktı

```
### 🔴 18.09.2026 · Özel Durum Açıklaması (Genel) · [KAP 1665180](url)
**Ne oldu:** 1-2 cümle, sade Türkçe.
**Rakamlar:** metinde geçen her sayı, kaynağıyla.
**Neden önemli / değil:** 1 cümle.
**Terimler:** metinde geçen finans terimleri (Samwell için liste).
```

## Dikkat

- Bildirim bir "güncelleme" veya "düzeltme" ise önceki bildirime bağla.
- Metin İngilizce/Türkçe ikilidir; sunucu Türkçesini verir.
- Metin şirketin kendi anlatımıdır ("stratejik", "güçlendirilmiş"). Sıfatları değil olguları aktar.
