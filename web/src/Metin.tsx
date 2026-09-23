// HTML çalıştırmadan yalnız HTTP(S) Markdown bağlantılarını gösterir.
export function Metin({ text }: { text: string }) {
  return <>{text.split(/(\[[^\]]+\]\(https?:\/\/[^\s)]+\))/g).map((part, i) => {
    const match = part.match(/^\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)$/)
    return match ? <a key={i} href={match[2]} target="_blank" rel="noreferrer">{match[1]}</a> : part
  })}</>
}
