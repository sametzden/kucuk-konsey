# Sanayi çekirdek kalemleri

THYAO dahil banka dışı şirketler için başlangıç seti. Her kalemi dönen tabloda tam adıyla
bul; ad/tanım doğrulanmıyorsa benzer kalemi otomatik ikame etme. Kaynak, dönem, para birimi,
ölçek ve akım/bakiye bilgisini kaydet. Aynı dönemin geçen yılını da getir.

| Kalem | Tür | Kullanım |
| --- | --- | --- |
| Satış Gelirleri | Akım | Satış tutarı; hacim değildir |
| Brüt Kâr | Akım | Satış maliyeti sonrası kalan tutar |
| Ticari Alacaklar | Bakiye | Henüz tahsil edilmemiş satışlar |
| İşletme Faaliyetlerinden Kaynaklanan Net Nakit | Akım | Faaliyetlerin net nakdi; yalnız tahsilat değildir |
| Yatırım Harcamaları | Akım | Kaynaktaki işaret ve kapsam korunur |
| Serbest Nakit Akım | Akım | Sağlayıcı tanımı doğrulanır; yoksa kendiliğinden türetilmez |

Tablo konumu isimden tahmin edilmez; balance/income/cashflow birlikte taranır.
THYAO trafik/doluluk/birim gelir ve TUPRS rafineri marjı/kapasite kullanımı bu setin yerine
geçmez; ayrı operasyonel veri ihtiyaçlarıdır. Varys KAP ekine erişemiyorsa “ek okunamadı”
yazar, finansal kalemler yine toplanır. Brüt kâr rafineri marjı veya birim gelir diye sunulmaz.
