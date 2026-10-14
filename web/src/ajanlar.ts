// Konsey üyeleri. x/y: sahnede ayak noktasının yeri (resmin yüzdesi). boy: resim yüksekliğinin yüzdesi.
// bolum: kuzgunda bu ajanın yazdığı yer ("## başlık" ya da "## başlık/### alt başlık").
export type Ajan = { id: string; ad: string; unvan: string; gorev: string; bolum: string; x: number; y: number; boy: number }

export const AJANLAR: Ajan[] = [
  { id: 'tyrion', ad: 'Tyrion', unvan: "Kral'ın Eli", gorev: 'Kuzgunu okur, olayları önem sırasına koyar: haftanın hikâyesi, neden önemli, neyi izle, derin bakmaya değer.', bolum: "Tyrion'un sözü", x: 50, y: 50, boy: 14.5 },
  { id: 'varys', ad: 'Varys', unvan: 'Fısıltılar Ustası', gorev: 'Arşivdeki KAP bildirimlerini ve haberleri tarar, gürültüyü ayıklar, tartışmaya gidecek temaları seçer.', bolum: 'Gündem', x: 59.2, y: 50, boy: 17 },
  { id: 'serceparmak', ad: 'Serçeparmak', unvan: 'Gümüş Sayman', gorev: 'BIST 30 fiyat hareketlerini çıkarır, temalarla ve arşivle eşleştirir. Yorum yapmaz, neden-sonuç kurmaz.', bolum: 'Piyasa', x: 40.8, y: 50, boy: 17 },
  { id: 'ates', ad: 'Ateş', unvan: 'Boğa sesi', gorev: 'Seçilen temaların hangi şirketin işine iyi gelebileceğini arar. Buz’u göremez; her tezi yanlışlanabilir.', bolum: 'Tartışma/Ateş', x: 18, y: 64, boy: 19 },
  { id: 'buz', ad: 'Buz', unvan: 'Ayı sesi', gorev: 'Seçilen temaların hangi şirketin işine zarar verebileceğini arar. Ateş’i göremez; mekanizma yazar.', bolum: 'Tartışma/Buz', x: 82, y: 64, boy: 19 },
  { id: 'samwell', ad: 'Samwell', unvan: 'Hisar kâtibi', gorev: 'Günün tartışmasından bir kavram seçer, gerçek veriyle anlatır; açıklanmadan geçen terimleri toplar.', bolum: 'Samwell', x: 15.5, y: 80, boy: 19 },
]
