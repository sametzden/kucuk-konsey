// Veri katmanı: ajanların yazdığı kuzgun markdown dosyasını okur, arayüzün ihtiyacı olanı çıkarır.
// React'ten bağımsız; ileride başka bir ekran da aynı fonksiyonları kullanabilir.

export type Soz = { sembol: string; bugun: string; catisma: string; cozecek: string; dikkat?: string }
export type Muhur = { sembol: string; tarih: string; baslik: string; kap?: string; url?: string }
export type Kuzgun = { tarih: string; soz: Soz[]; muhurler: Muhur[]; hisseler: string[] }

// import.meta.glob: Vite, derleme anında bu kalıba uyan bütün dosyaları metin (?raw) olarak paketler.
const dosyalar = import.meta.glob('../../kuzgunlar/*.md', { query: '?raw', import: 'default', eager: true }) as Record<string, string>

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
    sonuc.push({ sembol: parcalar[i], bugun: alan('Bugün'), catisma: alan('Çatışma'), cozecek: alan('Çözecek veri'), dikkat: alan('Dikkat') || undefined })
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

export function sonKuzgun(): Kuzgun | null {
  const yol = Object.keys(dosyalar).sort().at(-1) // dosya adları YYYY-MM-DD.md, alfabetik = kronolojik
  if (!yol) return null
  const metin = dosyalar[yol]
  const hisseler = [...metin.matchAll(/^## ([A-Z]{4,6})$/gm)].map((m) => m[1])
  return { tarih: yol.match(/(\d{4}-\d{2}-\d{2})/)![1], soz: sozuAyikla(metin), muhurler: muhurleriAyikla(metin, hisseler), hisseler }
}
