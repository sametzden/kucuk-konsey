// Veri katmanı: ajanların yazdığı kuzgun markdown dosyasını okur, arayüzün ihtiyacı olanı çıkarır.
// React'ten bağımsız; ileride başka bir ekran da aynı fonksiyonları kullanabilir.

export type Soz = { sembol: string; bugun: string; catisma: string; cozecek: string; dikkat?: string; neden?: string; firsat?: string; risk?: string }
export type Muhur = { sembol: string; tarih: string; baslik: string; kap?: string; url?: string }
export type Kuzgun = { tarih: string; soz: Soz[]; muhurler: Muhur[]; hisseler: string[]; metin: string; dunya?: string }

function bolum(metin: string, baslik: string): string {
  // "## <baslik>" ile bir sonraki "## " arasındaki metin
  const bas = metin.indexOf(`## ${baslik}`)
  if (bas < 0) return ''
  const son = metin.indexOf('\n## ', bas + 3)
  return metin.slice(bas, son < 0 ? undefined : son)
}

function sozuAyikla(metin: string): Soz[] {
  const blok = bolum(metin, "Tyrion'un sözü")
  const parcalar = blok.split(/\n\*\*([A-Z]{4,6})\*\*\n/).slice(1) // [sembol, içerik, sembol, içerik, ...]
  const sonuc: Soz[] = []
  for (let i = 0; i < parcalar.length; i += 2) {
    const alan = (ad: string) => parcalar[i + 1].match(new RegExp(`\\*\\*${ad}:\\*\\*\\s*(.+)`))?.[1]?.trim() ?? ''
    sonuc.push({ sembol: parcalar[i], bugun: alan('Bugün'), catisma: alan('Çatışma'), cozecek: alan('Neyi izle') || alan('Çözecek veri'), dikkat: alan('Dikkat') || undefined, neden: alan('Neden önemli'), firsat: alan('Fırsat'), risk: alan('Risk') })
  }
  return sonuc
}

function muhurleriAyikla(metin: string, hisseler: string[]): Muhur[] {
  // Varys'ın kırmızı işaretli (🔴) bildirimleri: "### 🔴 23.09.2026 · Başlık · [KAP 123](url)"
  return hisseler.flatMap((sembol) =>
    [...bolum(metin, sembol).matchAll(/^### 🔴 (\S+) · (.+?)(?: · \[(KAP \d+)\]\((\S+)\))?$/gm)].map((m) => ({
      sembol, tarih: m[1].slice(0, 5), baslik: m[2].replace(/ · \[.*$/, ''), kap: m[3], url: m[4],
    })),
  )
}

export function ayikla(tarih: string, metin: string): Kuzgun {
  const hisseler = [...metin.matchAll(/^## ([A-Z]{4,6})$/gm)].map((m) => m[1])
  // Tyrion'un sözündeki, hisse kartlarından önce gelen tek "**Dünya:**" satırı (Varys'ın Gündem'inden)
  const dunya = bolum(metin, "Tyrion'un sözü").match(/^\*\*Dünya:\*\*\s*(.+)$/m)?.[1]?.trim()
  return { tarih, metin, soz: sozuAyikla(metin), muhurler: muhurleriAyikla(metin, hisseler), hisseler, dunya }
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
