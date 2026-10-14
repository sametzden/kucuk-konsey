---
name: konsey
description: Küçük Konsey'i toplar. Varsayılan gündem turu; arşivdeki son günlerin KAP bildirimleri, haberleri ve BIST 30 fiyatları üzerinden Varys → Serçeparmak → Ateş/Buz → Tyrion → Samwell akışını çalıştırır. "/konsey derin <SEMBOL>" tek hisse için eski derin analiz akışını çalıştırır. Sadece Samet /konsey dediğinde çalışır.
disable-model-invocation: true
---

# Konseyi topla

Sen ana oturumsun: ajanları **sabit sırayla** çağırır, Ateş/Buz çıktısını kuzguna taşırsın.
**Kendin tez, sayı ya da yorum üretmezsin.** Akıştaki tek seçim Varys'ın tema seçimidir; sen sırayı
değiştirmezsin, adım atlamazsın (aşağıda yazılı durumlar hariç).

Bugünün tarihi `YYYY-MM-DD` biçiminde tarih olarak kullanılır; Samet başka bir tarih verdiyse onu kullan.

**Mod:** `/konsey` → gündem turu. `/konsey derin <SEMBOL>` → derin tur. Her ajan çağrısının ilk
satırı `Mod: gündem` ya da `Mod: derin <SEMBOL>` olur.

## Gündem turu

### 0. Ön kontrol

- `mcp__arsiv__*` araçları listende var mı? Yoksa **dur**: "arsiv MCP bağlı değil; `.mcp.json`'u
  kontrol edip bu klasörde oturumu yeniden aç."
- **Veri taze mi?** `son_belgeler(gun=1)` boş dönüyorsa toplayıcı çalışmamış olabilir. Dur ve söyle:
  "Son 24 saatte belge yok. `journalctl --user -u konsey-toplayici -n 30` ile toplayıcıya bak."
- **Gün (N):** `kuzgunlar/` altında `mod: gundem` olan en son kuzgunun tarihinden bugüne geçen gün.
  En az 1, en fazla 7. Hiç yoksa 3.
- `kuzgunlar/<tarih>.md` zaten varsa dur ve Samet'e sor: üstüne mi eklenecek, iptal mi?

### 1. Varys, sonra Serçeparmak (sırayla)

İkisi de kuzguna yazar; aynı anda çalışırlarsa birbirinin yazdığını ezebilirler. Bu yüzden **sırayla**:

1. `varys`: `Mod: gündem · Tarih: <tarih> · Gün: <N>`
2. `serceparmak`: `Mod: gündem · Tarih: <tarih> · Gün: <N>`

Varys "öne çıkan gelişme yok" dediyse ya da tartışmaya tema seçmediyse 2. adımı atla, 3. adıma geç.

### 2. Ateş ve Buz (paralel)

Bir `ates` ve bir `buz` çağrısını **aynı anda** başlat. Girdi yalnızca:
`Mod: gündem · Tarih: <tarih>`. Başka bağlam, ipucu ya da diğer ajanın çıktısını **verme**;
bağımsızlıkları buna bağlı.

İkisi dönünce kuzgunun sonuna `## Tartışma` bölümü aç; altına önce Ateş'in, sonra Buz'un çıktısını
**olduğu gibi** yapıştır: tek harf düzeltme, kısaltma, biçim değişikliği yok. Bir ajan tez kurmadığını
söylediyse o cümle de olduğu gibi girer.

### 3. Tyrion, sonra Samwell (sırayla)

1. `tyrion`: `Mod: gündem · Tarih: <tarih>`
2. `samwell`: `Mod: gündem · Tarih: <tarih>`

### 4. Yayın öncesi kontrol

`python scripts/brief_kontrol.py kuzgunlar/<tarih>.md` çalıştır. Hata varsa tur başarılı sayılmaz;
Tyrion'u hata listesiyle bir kez daha çağır, kendi bölümünü düzeltsin.

### 5. Samet'e dönüş

Kısa tablo: N · Varys tarama/açılan belge/tema sayısı ve tartışmaya giden temalar · Serçeparmak öne
çıkan hisse ve eşleşme sayısı · Ateş ve Buz tez sayısı · Tyrion Dikkat sayısı · yeni iddia sayısı ·
günün kavramı · **derin bakma önerisi.** Altına **bir ajanın durduğu, hata verdiği ya da boş döndüğü
her adım** (sessiz geçme).

Tyrion bir hisse önerdiyse sonuna şu soruyu ekle: "Derin tur başlatayım mı? (`/konsey derin <SEMBOL>`)".
Derin turu **sen başlatmazsın**; karar Samet'in.

## Derin tur: `/konsey derin <SEMBOL>`

Tek hisse için eski akış. Dosya: `kuzgunlar/<tarih>-derin-<SEMBOL>.md` (günün gündem kuzgununa
dokunulmaz). Her çağrının girdisi: `Mod: derin <SEMBOL> · Tarih: <tarih> · Dosya: <dosya>`.

0. **Ön kontrol:** `mcp__borsa__*` ve `mcp__kap__*` araçları var mı? Yoksa dur: "borsa/kap MCP bağlı
   değil." Dosya zaten varsa Samet'e sor.
1. `varys`, sonra `serceparmak` (sırayla). Serçeparmak hiçbir sayı toplayamadıysa dur ve nedenini söyle.
2. `ates` ve `buz` aynı anda, yalnız yukarıdaki girdiyle. Dönünce çıktıları `## <SEMBOL>` bölümünün
   sonuna, önce Ateş sonra Buz, olduğu gibi ekle.
3. `tyrion`, sonra `samwell` (sırayla).
4. Dönüş: Varys bildirim sayısı · Serçeparmak kalem/okunamayan · Ateş ve Buz tez · Tyrion Dikkat ·
   yeni iddia · günün kavramı · duran ya da hata veren her adım.

## Her iki turda

`hisar/kurallar.md` bütün ajanlara uygulanır. Samwell dersini Tyrion özetinin içine eklemez.
