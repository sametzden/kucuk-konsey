import { useState } from 'react'
import { AJANLAR, type Ajan } from './ajanlar'
import { sonKuzgun, type Kuzgun } from './kuzgun'
import './App.css'

// Veriyi bir kez, bileşenlerin dışında okuyoruz: dosya derleme anında paketlendi, değişmiyor.
const kuzgun = sonKuzgun()

export default function App() {
  // useState: bileşenin hatırladığı değer. [şimdiki değer, değiştiren fonksiyon].
  const [seciliAjan, setSeciliAjan] = useState<string>('tyrion')
  const [seciliHisse, setSeciliHisse] = useState<string | null>(null)

  const muhurSayisi = (sembol: string) => kuzgun?.muhurler.filter((m) => m.sembol === sembol).length ?? 0

  return (
    <div className="kale">
      <header className="ust">
        <h1>Küçük Konsey</h1>
        <span className="piksel soluk">Kızıl Kale · kuzgun {kuzgun?.tarih ?? 'yok'}</span>
        <span className="rozet-altin piksel">Konsey ({AJANLAR.filter((a) => !a.yolda).length})</span>
      </header>

      <main className="govde">
        <Sahne seciliAjan={seciliAjan} onAjanSec={setSeciliAjan}>
          {kuzgun?.hisseler.map((s, i) => (
            <button
              key={s}
              className={'hane piksel' + (seciliHisse === s ? ' secili' : '')}
              style={{ left: `${36 + (i % 3) * 11}%`, top: `${54 + Math.floor(i / 3) * 7}%` }}
              onClick={() => setSeciliHisse(seciliHisse === s ? null : s)}
            >
              {s}
              {muhurSayisi(s) > 0 && <Muhur sayi={muhurSayisi(s)} />}
            </button>
          ))}
        </Sahne>
        <KralinMasasi kuzgun={kuzgun} seciliHisse={seciliHisse} />
      </main>
    </div>
  )
}

// Props: bir bileşene dışarıdan verilen girdiler. Sahne, hangi ajanın seçili olduğunu bilmez; ona söylenir.
function Sahne(props: { seciliAjan: string; onAjanSec: (id: string) => void; children: React.ReactNode }) {
  const ajan = AJANLAR.find((a) => a.id === props.seciliAjan)!
  return (
    <section className="sahne" aria-label="Konsey odası">
      <img className="oda" src="/assets/oda.png" alt="" />
      <div className="mum-isigi" />
      <div className="kuzgun-ucus" aria-hidden="true"><div className="kuzgun" /></div>
      {props.children}
      {/* y'ye göre sırala: önde duran (y'si büyük) sonra çizilir, arkadakinin önüne geçer */}
      {[...AJANLAR].sort((a, b) => a.y - b.y).map((a) => (
        <AjanFigur key={a.id} ajan={a} secili={a.id === props.seciliAjan} onClick={() => props.onAjanSec(a.id)} />
      ))}
      <aside className="ajan-karti">
        <div className="kart-baslik"><b>{ajan.ad}</b> <span>{ajan.unvan}</span></div>
        <p>{ajan.gorev}</p>
        {ajan.yolda && <p className="piksel soluk">Henüz yolda · {ajan.yolda}</p>}
      </aside>
    </section>
  )
}

function AjanFigur({ ajan, secili, onClick }: { ajan: Ajan; secili: boolean; onClick: () => void }) {
  return (
    <button
      className={'ajan' + (secili ? ' secili' : '') + (ajan.yolda ? ' yolda' : '')}
      style={{ left: `${ajan.x}%`, top: `${ajan.y}%`, height: `${ajan.boy}%`, animationDelay: `${(ajan.x % 7) * 0.3}s` }}
      onClick={onClick}
      aria-label={`${ajan.ad}, ${ajan.unvan}`}
      aria-pressed={secili}
    >
      <img src={`/assets/${ajan.id}.png`} alt="" draggable={false} />
      <span className="isim piksel">{ajan.ad}</span>
    </button>
  )
}

function KralinMasasi({ kuzgun, seciliHisse }: { kuzgun: Kuzgun | null; seciliHisse: string | null }) {
  if (!kuzgun) return <aside className="masa"><h2>Kralın Masası</h2><p>Henüz kuzgun yok.</p></aside>
  const filtre = <T extends { sembol: string }>(l: T[]) => (seciliHisse ? l.filter((x) => x.sembol === seciliHisse) : l)
  return (
    <aside className="masa">
      <div className="masa-baslik">
        <span className="mum" aria-hidden="true" />
        <img src="/assets/parca/taht.png" alt="" className="taht" />
        <h2>Kralın Masası</h2>
        <span className="mum" aria-hidden="true" />
      </div>
      <p className="piksel soluk">{seciliHisse ? `${seciliHisse} hanesi · tümü için haneye tekrar tıkla` : 'Bütün haneler'}</p>

      <h3><img src="/assets/parca/parsomen.png" alt="" className="ikon" /> Tyrion'un sözü</h3>
      {filtre(kuzgun.soz).map((s) => (
        <article key={s.sembol} className="parsomen">
          <div className="piksel altin">{s.sembol}</div>
          {s.bugun && <p><b>Bugün:</b> {s.bugun}</p>}
          <p>{s.catisma}</p>
          {s.cozecek && <p className="soluk"><b>Neyi izle:</b> {s.cozecek}</p>}
          {s.dikkat && <p className="uyari"><b>Dikkat:</b> {s.dikkat}</p>}
        </article>
      ))}

      <h3><img src="/assets/parca/muhur-kirmizi.png" alt="" className="ikon" /> Kırmızı mühürler</h3>
      {filtre(kuzgun.muhurler).map((m) => (
        <div key={m.sembol + m.baslik} className="muhur-satir">
          <img src="/assets/parca/muhur-kirmizi.png" alt="" className="ikon kucuk" />
          <span className="piksel soluk">{m.tarih}</span>
          <span><b>{m.sembol}</b> · {m.baslik}</span>
          {m.url && <a href={m.url} target="_blank" rel="noreferrer" className="piksel">{m.kap}</a>}
        </div>
      ))}
    </aside>
  )
}

// Kırmızı mum mühür, üstünde önemli olay sayısı
function Muhur({ sayi }: { sayi: number }) {
  return (
    <span className="muhur" aria-label={`${sayi} önemli olay`}>
      <img src="/assets/parca/muhur-kirmizi.png" alt="" />
      <b>{sayi}</b>
    </span>
  )
}
