---
title: Westeros arayüzü: asset prompt'ları
created: 2026-09-23
---
# Asset prompt'ları

Hepsini **aynı araçta, aynı sohbette** üret. Stil tutarlılığı ancak böyle korunur.
Sıra önemli: önce **1. stil referansı**, sonra her şeyi o görsele referans vererek üret.

## Araç seçimi

| Araç | Neden | Not |
| --- | --- | --- |
| **ChatGPT (görsel üretimi)** ⭐ | Prompt'a sadık, referans görsel yüklenebiliyor, şeffaf arka plan isteyince veriyor | Aynı sohbette devam et, önceki görseli referans göster |
| Gemini (görsel modeli) | Karakter tutarlılığı ve "şunu değiştir" düzenlemelerinde güçlü | ChatGPT beğenilmezse alternatif |
| Midjourney | En estetik sonuç, `--sref` ile stil kilitleme | Ücretli; şeffaf arka plan için ayrı temizlik gerekir |
| **Piskel** (ücretsiz, tarayıcıda) | Üretilen görseldeki bozuk pikselleri elle düzeltme, sprite boyutuna indirme | piskelapp.com |
| remove.bg / araç içi | Arka planı şeffaf yapma | Karakterlerde gerekli |

**Kural:** Karakterler dizideki oyuncuların yüzlerine benzemesin, HBO görseli kullanılmasın. Rolü çağrıştıran
**özgün** karakterler. (Kişisel proje ama sonradan paylaşılırsa önemli.)

## Ortak stil bloğu

Her prompt'un başına bunu ekle:

```
16-bit pixel art, SNES-era RPG style, top-down 3/4 view, warm candlelit palette
(deep browns, crimson, antique gold, stone grey, night blue), crisp hard-edged pixels,
no anti-aliasing, no blur, no text, no letters, no watermark. Original characters,
not resembling any real actor.
```

## 1. Stil referansı (ilk bu)

```
[stil bloğu] A medieval royal small council chamber inside a red stone castle.
A long wooden table in the center with a painted map of a fantasy continent on its surface.
Tall arched windows at the back showing a night sky, red and gold banners on the walls,
candles on the table corners casting warm light. Empty chairs around the table.
Wide shot, 16:9, 1920x1080.
```

Beğendiğin sonucu kaydet: `tasarim/assets/oda.png`. Bu hem arka plan hem stil referansı.

## 2. Karakter dizisi (tek görselde, tutarlılık için)

```
[stil bloğu] Character lineup sheet, 8 characters standing side by side, same scale,
same pixel density as the reference image, plain transparent background, full body, front 3/4 view:
1) a bald, plump spymaster in flowing purple silk robes, hands clasped, calm smile
2) a slim, sly treasurer with short dark hair and a small pointed beard, grey-green doublet,
   a small silver mockingbird pin
3) a short nobleman with messy blond hair, dark red doublet, a golden hand-shaped brooch, holding a wine cup
4) a young, round-faced scholar in grey robes with a chain of metal links, holding a thick book
5) a warrior with fiery red-orange hair and an ember-colored cloak, confident stance
6) a pale warrior with white-blue hair, a steel-blue fur cloak, frost on the shoulders, calm cold look
7) a young man in a wooden wheelchair wearing a dark green cloak, a black raven on his shoulder
8) an old grey-bearded maester in dark robes with a long chain, holding a rolled letter with a red wax seal
```

Sıra = Varys · Serçeparmak · Tyrion · Samwell · Ateş · Buz · Bran · **Haberci (yeni üye, 8)**.
Dizi beğenilince her karakteri tek tek iste ("make character 3 alone, same style, transparent background,
512x512"), dosya adı: `tasarim/assets/karakter-<ad>.png`.

## 3. Küçük parçalar

```
[stil bloğu] Sprite sheet on transparent background, same style as the reference:
a black raven flying (4 animation frames in a row), a lit candle (3 flame frames),
a red wax seal, a gold wax seal, a rolled parchment scroll, a small iron throne-like chair.
```

Dosya: `tasarim/assets/parcalar.png`. Kuzgun = ajan çalışırken üstünde döner; kırmızı mühür = önemli olay.

## Teslim

Hepsini `tasarim/assets/` klasörüne koy. Boyut/kesim/şeffaflık işini ben yaparım; beğenmediğin bir karakter
olursa sadece o karakterin prompt'unu tekrar çalıştırmak yeter.
