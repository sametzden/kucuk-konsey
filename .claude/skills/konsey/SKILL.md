---
name: konsey
description: Küçük Konsey'i toplar. İzlenen bütün hisseler için Varys → Serçeparmak → Ateş/Buz → Tyrion → Samwell akışını çalıştırır ve günün kuzgununu üretir. Sadece Samet /konsey dediğinde çalışır.
disable-model-invocation: true
---

# Konseyi topla

Sen ana oturumsun: ajanları sırayla çağırır, Ateş/Buz çıktısını kuzguna taşırsın. **Kendin tez,
sayı ya da yorum üretmezsin.** Bugünün tarihi `YYYY-MM-DD` biçiminde tarih olarak kullanılır;
Samet başka bir tarih verdiyse onu kullan.

## 0. Ön kontrol

- `mcp__borsa__*` ve `mcp__kap__*` araçları listende var mı? Yoksa **dur**: "borsa/kap MCP bağlı değil.
  `.mcp.json`'u kontrol edip oturumu yeniden aç (lokal borsa uyandırma istemez; uzak sunucuya
  dönüldüyse `./scripts/uyandir.sh && claude`)." Araçsız konsey toplanmaz.
- `hisar/hisseler/*.md` dosyalarını tara, frontmatter'ında `izleme: aktif` olanları al. Liste başka
  hiçbir yerden gelmez.
- `kuzgunlar/<tarih>.md` zaten varsa dur ve Samet'e sor: üstüne mi eklenecek, iptal mi?

## 1. Varys, sonra Serçeparmak (sırayla)

İkisi de kuzguna yazar; aynı anda çalışırlarsa birbirinin yazdığını ezebilirler. Bu yüzden **sırayla**:

1. `varys` ajanı: bütün aktif hisseler + gündem taraması, tek çağrı.
2. `serceparmak` ajanı: bütün aktif hisseler, tek çağrı.

Serçeparmak hiçbir sayı toplayamadıysa dur ve nedenini Samet'e söyle; tezsiz, sayısız konsey olmaz.

## 2. Ateş ve Buz (paralel)

Serçeparmak tablosu olan **her hisse için** bir `ates` ve bir `buz` çağrısı yap, **hepsini aynı anda**
başlat. Her çağrının girdisi yalnızca: `Tarih: <tarih> · Sembol: <SEMBOL>`. Ajanlara başka bağlam,
ipucu ya da diğer ajanın çıktısını **verme**; bağımsızlıkları buna bağlı.

Hepsi dönünce her çıktıyı ilgili `## <SEMBOL>` bölümünün **sonuna**, önce Ateş sonra Buz olacak
şekilde ekle. **Çıktıyı olduğu gibi yapıştır:** tek harf düzeltme, kısaltma, biçim değişikliği yok.
Bir ajan tez kurmadığını söylediyse ("Serçeparmak tablosu yok" gibi) o cümle de olduğu gibi girer.

## 3. Tyrion, sonra Samwell (sırayla)

1. `tyrion` ajanı: `Tarih: <tarih>`.
2. `samwell` ajanı: `Tarih: <tarih>`.

## 4. Samet'e dönüş

Kısa tablo: Varys gündem madde sayısı · hisse başına Varys bildirim sayısı · Serçeparmak kalem/okunamayan sayısı · Ateş ve Buz
tez sayısı · Tyrion Dikkat sayısı. Altına: yeni iddia sayısı, günün kavramı, ve **bir ajanın durduğu,
hata verdiği ya da boş döndüğü her adım** (sessiz geçme).

## Yayın öncesi kontrol

Ana oturum `python scripts/brief_kontrol.py kuzgunlar/<tarih>.md` çalıştırır.
Hata varsa tur başarılı sayılmaz; Tyrion kendi bölümünü düzeltir. `hisar/kurallar.md`
bütün ajanlara uygulanır. Samwell dersini Tyrion özetinin içine eklemez.
