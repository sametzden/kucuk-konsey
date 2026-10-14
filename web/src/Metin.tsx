import type { ReactNode } from 'react'

// Kuzgunun kullandığı kadar markdown: ### başlık, liste, numaralı liste, tablo, kalın, italik, bağlantı, [[wikilink]].
// HTML çalıştırmaz; yalnız HTTP(S) bağlantıları tıklanır. Her dolu satır kendi paragrafıdır
// (ajanlar "**Etiket:** ..." satırlarını boş satırsız alt alta yazıyor).
const SATIR_ICI = /(\[\[[^\]]+\]\]|\[[^\]]+\]\(https?:\/\/[^\s)]+\)|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|🔴)/g

export function Metin({ text }: { text: string }): ReactNode {
  return text.split(SATIR_ICI).map((part, i) => {
    const link = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/)
    if (link) return <a key={i} href={link[2]} target="_blank" rel="noreferrer">{link[1]}</a>
    if (/^\[\[.+\]\]$/.test(part)) return <span key={i} className="wikilink">{part.slice(2, -2)}</span>
    if (/^\*\*.+\*\*$/.test(part)) return <b key={i}><Metin text={part.slice(2, -2)} /></b>
    if (/^\*.+\*$/.test(part)) return <i key={i}>{part.slice(1, -1)}</i>
    if (part === '🔴') return <img key={i} src="/assets/parca/muhur-kirmizi.png" alt="önemli" className="ikon kucuk" />
    return part
  })
}

const hucreler = (satir: string) => satir.trim().replace(/^\||\|$/g, '').split('|').map((h) => h.trim())

export function Markdown({ text }: { text: string }) {
  const satirlar = text.split('\n')
  const bloklar: ReactNode[] = []
  for (let i = 0; i < satirlar.length; ) {
    const s = satirlar[i]
    // Aynı türden ardışık satırları topla (liste, tablo)
    const topla = (re: RegExp) => { const l: string[] = []; while (i < satirlar.length && re.test(satirlar[i])) l.push(satirlar[i++]); return l }
    if (!s.trim()) { i++; continue }
    if (/^#{3,6} /.test(s)) { bloklar.push(<h4 key={i}><Metin text={s.replace(/^#+ /, '')} /></h4>); i++; continue }
    if (/^\s*\|/.test(s)) {
      const [bas, , ...govde] = topla(/^\s*\|/).map(hucreler)
      bloklar.push(
        <div key={i} className="tablo-kap"><table>
          <thead><tr>{bas.map((h, j) => <th key={j}><Metin text={h} /></th>)}</tr></thead>
          <tbody>{govde.map((r, k) => <tr key={k}>{r.map((h, j) => <td key={j}><Metin text={h} /></td>)}</tr>)}</tbody>
        </table></div>,
      )
      continue
    }
    if (/^\s*[-*] /.test(s)) {
      bloklar.push(<ul key={i}>{topla(/^\s*[-*] /).map((l, k) => <li key={k}><Metin text={l.replace(/^\s*[-*] /, '')} /></li>)}</ul>)
      continue
    }
    if (/^\d+\. /.test(s)) {
      bloklar.push(<ol key={i}>{topla(/^\d+\. /).map((l, k) => <li key={k}><Metin text={l.replace(/^\d+\. /, '')} /></li>)}</ol>)
      continue
    }
    bloklar.push(<p key={i}><Metin text={s} /></p>)
    i++
  }
  return <div className="md">{bloklar}</div>
}
