# Küçük Konsey arayüzü

Üretim kullanımı (repo kökünden):

```sh
npm --prefix web run build
python3 scripts/web_server.py
```

http://127.0.0.1:8765 adresini aç. Sunucu sadece yerel bilgisayarda dinler; repo dosyalarını
statik olarak sunmaz, yalnız web/dist ve son rapor API'sini sunar. Yeni kuzgun dosyası her
istekte diskten okunur. Arayüz sayfa açılınca ve sekmeye dönülünce raporu yeniden sorar; rapor için yeniden derleme gerekmez.
Sunucu hata verirse son okunabilen rapor hata mesajıyla korunur.

Geliştirme: veri sunucusu açıkken başka terminalde `npm --prefix web run dev`.
Vite /api isteklerini yerel veri sunucusuna aktarır. `vite preview` tek başına API sağlamaz.

Sahnede ya da masadaki sekmelerde bir ajana tıklanınca masada o ajanın kuzgundaki bölümü görünür
(eşleme `src/ajanlar.ts` → `bolum`): Tyrion → Tyrion'un sözü, Varys → Gündem, Serçeparmak → Piyasa,
Ateş/Buz → Tartışma altındaki kendi başlıkları, Samwell → Samwell. Bölüm yoksa "bölüm yok" yazılır.
