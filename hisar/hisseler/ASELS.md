---
sembol: ASELS
sirket: Aselsan Elektronik Sanayi ve Ticaret A.Ş.
sektor: Savunma elektroniği
eklendi: 2026-09-21
izleme: aktif
---
# ASELS — Aselsan

Savunma elektroniği üreticisi: haberleşme, radar, elektronik harp, optik ve silah sistemleri.
Geliri ağırlıklı olarak Savunma Sanayii Başkanlığı ve TSK ile imzalanan uzun vadeli
sözleşmelerden gelir; sözleşmelerin önemli kısmı döviz cinsindendir.

## Ne izliyoruz

- **Yeni sözleşme bildirimleri** — tutar, para birimi ve teslim yılı. Tek tek küçük görünse de
  bakiyeyi büyüten şey bunlar.
- **Bakiye sipariş (backlog)** — imzalanmış ama henüz teslim edilmemiş işlerin toplamı; şirketin
  önümüzdeki yıllara taşıdığı garantili iş yükü.
- **Kur etkisi** — sözleşmeler dövizli, maliyetin bir kısmı TL. Kur hareketi kârı iki yönden etkiler.
- **Alacaklar ve tahsilat** — kamuya satış yapan şirkette ciro büyürken nakit gecikebilir.

### Kalem karşılıkları

Araçlardaki gerçek kalem adları (22.09.2026'da `get_financial_statements` çıktısından doğrulandı).
Serçeparmak bunları arayacak:

| İzlediğimiz | Tablo | Kalem adı |
| --- | --- | --- |
| Tahsilat | `cashflow` | `İşletme Faaliyetlerinden Kaynaklanan Net Nakit` · `Serbest Nakit Akım` |
| Alacaklar | `balance` | `Ticari Alacaklar` |
| Ciro (tahsilatla karşılaştırmak için) | `income` | `Satış Gelirleri` |
| Kur etkisi | `cashflow` | `Parasal net yabancı para varlık/(yükümlülük) pozisyonu` · `Net YPP (Hedge Dahil)` |
| Döviz geliri payı | `cashflow` | `Yurtiçi Satışlar` · `Yurtdışı Satışlar` |
| Yeni sözleşmeler | — | Borsa araçlarında yok; KAP bildirimi, **Varys'ın işi** |
| Bakiye sipariş (backlog) | — | Bu araçların hiçbirinde yok. Faaliyet raporundan elle okunur |

`income` ve `cashflow` kalemleri **yıl başından itibaren birikimlidir** (2026Q2 = ilk 6 ay);
`balance` kalemleri dönem sonu bakiyesidir. Tek çeyrek isteniyorsa fark alınır.
ASELS'te gelirin yaklaşık yarısı Q4'te yazılıyor — teslimatlar yıl sonunda yığılıyor (2023-2025'te üç kez).

## Açık tezler

_(tarihli iddialar; Bran Birim 4'te gerçekleşeni kontrol edecek)_

- [[ASELS-ates-2026Q3-satis-gelirleri]] · ates · kontrol 2026Q3
- [[ASELS-ates-2026Q3-yurtdisi-satislar]] · ates · kontrol 2026Q3
- [[ASELS-ates-2026Q3-yurtdisi-satis-payi]] · ates · kontrol 2026Q3
- [[ASELS-buz-2026Q3-ticari-alacaklar]] · buz · kontrol 2026Q3
- [[ASELS-buz-2026Q3-serbest-nakit-akim]] · buz · kontrol 2026Q3

## Önemli bildirimler

- 18.09.2026 · Güdüm Sistemleri Üretim Merkezi devreye alındı, 56 milyon ABD Doları ([KAP 1665180](https://www.kap.org.tr/tr/Bildirim/1665180))
- 04.08.2026 · 30 Haziran 2026 Finansal Tabloları bildirimi ([KAP 1643141](https://www.kap.org.tr/tr/Bildirim/1643141)) — metin içeriği bu araçla okunamadı

## Görülen bildirimler

- 1665180 (18.09.2026, Özel Durum Açıklaması (Genel))
- 1663667 (16.09.2026, Pay Bazında Devre Kesici Bildirimi)
- 1643570 (05.08.2026, Özel Durum Açıklaması (Genel))
- 1643144 (04.08.2026, Katılım Finansı İlkeleri Bilgi Formu)
- 1643143 (04.08.2026, Şirket Genel Bilgi Formu)
- 1643142 (04.08.2026, Sorumluluk Beyanı (Konsolide))
- 1643141 (04.08.2026, Finansal Rapor)
- 1643140 (04.08.2026, Faaliyet Raporu (Konsolide))
- 1639448 (30.07.2026, Pay Bazında Devre Kesici Bildirimi)
- 1637005 (27.07.2026, Pay Bazında Devre Kesici Bildirimi)
