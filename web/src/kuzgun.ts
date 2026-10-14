// Veri katmanı: ajanların yazdığı kuzgun markdown dosyasını okur, arayüzün ihtiyacı olanı çıkarır.
// React'ten bağımsız; ileride başka bir ekran da aynı fonksiyonları kullanabilir.

export type Kuzgun = { tarih: string; mod: string; metin: string }

export function ayikla(tarih: string, ham: string): Kuzgun {
  // Frontmatter (--- ... ---) gövdeden ayrılır; içindeki "mod:" satırı turun türünü söyler.
  const on = ham.match(/^---\n([\s\S]*?)\n---\n?/)
  const mod = on?.[1].match(/^mod:\s*(\S+)/m)?.[1] ?? ''
  return { tarih, mod, metin: on ? ham.slice(on[0].length) : ham }
}

function altBolum(metin: string, seviye: string, baslik: string): string {
  // "<seviye> <baslik>" satırı ile aynı ya da daha üst seviyedeki bir sonraki başlık arasındaki gövde
  const satirlar = metin.split('\n')
  const bas = satirlar.findIndex((s) => s.trim() === `${seviye} ${baslik}`)
  if (bas < 0) return ''
  const ust = new RegExp(`^#{1,${seviye.length}} `)
  const son = satirlar.findIndex((s, i) => i > bas && ust.test(s))
  return satirlar.slice(bas + 1, son < 0 ? undefined : son).join('\n').trim()
}

// yol: "Gündem" ya da "Tartışma/Ateş" (## bölüm, isteğe bağlı ### alt bölüm). Yoksa boş metin.
export function bolum(kuzgun: Kuzgun, yol: string): string {
  const [ana, alt] = yol.split('/')
  const govde = altBolum(kuzgun.metin, '##', ana)
  return alt ? altBolum(govde, '###', alt) : govde
}

export async function sonKuzgun(signal?: AbortSignal): Promise<Kuzgun | null> {
  const response = await fetch('/api/kuzgun', { cache: 'no-store', signal })
  if (!response.ok) throw new Error('Rapor okunamadı. Yerel veri sunucusunu kontrol et.')
  const data: unknown = await response.json()
  if (data === null) return null
  if (typeof data !== 'object' || !('tarih' in data) || !('metin' in data) ||
      typeof data.tarih !== 'string' || typeof data.metin !== 'string') {
    throw new Error('Rapor yanıtı beklenen biçimde değil.')
  }
  return ayikla(data.tarih, data.metin)
}
