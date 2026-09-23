// Konsey üyeleri. x/y: sahnede ayak noktasının yeri (resmin yüzdesi). boy: resim yüksekliğinin yüzdesi.
export type Ajan = { id: string; ad: string; unvan: string; gorev: string; x: number; y: number; boy: number; yolda?: string }

export const AJANLAR: Ajan[] = [
  { id: 'serceparmak', ad: 'Serçeparmak', unvan: 'Gümüş Sayman', gorev: 'Sayıları toplar, yorum yapmaz. Her sayının dönemi ve kaynağı yazılı.', x: 40.8, y: 50, boy: 17 },
  { id: 'tyrion', ad: 'Tyrion', unvan: "Kral'ın Eli", gorev: 'Konseyi dinler, son sözü söyler: ne oldu, fırsat ne, kötüye nereden gidebilir.', x: 50, y: 50, boy: 14.5 },
  { id: 'varys', ad: 'Varys', unvan: 'Fısıltılar Ustası', gorev: 'KAP bildirimlerini ve önemli haberleri toplar. Okuyamadığını uydurmaz.', x: 59.2, y: 50, boy: 17 },
  { id: 'ates', ad: 'Ateş', unvan: 'Boğa sesi', gorev: 'Aynı sayılarda iyiye gidişi arar. Buz’u göremez; her tezi yanlışlanabilir.', x: 18, y: 64, boy: 19 },
  { id: 'samwell', ad: 'Samwell', unvan: 'Hisar kâtibi', gorev: 'Günün kavramını gerçek veriyle, iki okumayla anlatır.', x: 15.5, y: 80, boy: 19 },
  { id: 'buz', ad: 'Buz', unvan: 'Ayı sesi', gorev: 'Aynı sayılarda riski arar. Ateş’i göremez; genel risk değil mekanizma yazar.', x: 82, y: 64, boy: 19 },
  { id: 'bran', ad: 'Bran', unvan: 'Üç Gözlü Kuzgun', gorev: 'Yazılan iddiaları gerçekleşenle karşılaştıracak.', x: 84, y: 81, boy: 18, yolda: 'Birim 4' },
]
