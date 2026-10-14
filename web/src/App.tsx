import { useEffect, useState } from 'react'
import { AJANLAR, type Ajan } from './ajanlar'
import { bolum, sonKuzgun, type Kuzgun } from './kuzgun'
import './App.css'
import { Markdown } from './Metin'

const MOD_ADI: Record<string, string> = { gundem: 'gündem turu', derin: 'derin tur' }

export default function App() {
  const [kuzgun, setKuzgun] = useState<Kuzgun | null>(null)
  const [hata, setHata] = useState('')
  const [yukleniyor, setYukleniyor] = useState(true)
  useEffect(() => {
    let controller: AbortController | undefined
    const yenile = async () => {
      controller?.abort()
      controller = new AbortController()
      const signal = controller.signal
      try {
        const result = await sonKuzgun(signal)
        if (!signal.aborted) { setKuzgun(result); setHata('') }
      } catch (error) {
        if (!signal.aborted) setHata(error instanceof Error ? error.message : 'Rapor okunamadı')
      } finally { if (!signal.aborted) setYukleniyor(false) }
    }
    // Konsey günde bir kez toplanır; sürekli sormak yerine sayfa açılınca ve sekmeye dönülünce sor.
    void yenile()
    const gorundu = () => { if (document.visibilityState === 'visible') void yenile() }
    document.addEventListener('visibilitychange', gorundu)
    return () => { document.removeEventListener('visibilitychange', gorundu); controller?.abort() }
  }, [])
  // useState: bileşenin hatırladığı değer. [şimdiki değer, değiştiren fonksiyon].
  const [seciliAjan, setSeciliAjan] = useState<string>('tyrion')
  const ajan = AJANLAR.find((a) => a.id === seciliAjan)!

  return (
    <div className="kale">
      <header className="ust">
        <h1>Küçük Konsey</h1>
        <span className="piksel soluk">
          Kızıl Kale · kuzgun {kuzgun?.tarih ?? 'yok'}{kuzgun?.mod && ` · ${MOD_ADI[kuzgun.mod] ?? kuzgun.mod}`}
        </span>
        <span className="rozet-altin piksel">Konsey ({AJANLAR.length})</span>
      </header>

      {yukleniyor && <p role="status">Kuzgun okunuyor…</p>}
      {hata && <p role="alert">{hata} {kuzgun ? 'Son okunabilen rapor gösteriliyor.' : ''}</p>}
      <main className="govde">
        <Sahne ajan={ajan} onAjanSec={setSeciliAjan} />
        <KralinMasasi kuzgun={kuzgun} ajan={ajan} onAjanSec={setSeciliAjan} />
      </main>
    </div>
  )
}

// Props: bir bileşene dışarıdan verilen girdiler. Sahne, hangi ajanın seçili olduğunu bilmez; ona söylenir.
function Sahne(props: { ajan: Ajan; onAjanSec: (id: string) => void }) {
  return (
    <section className="sahne" aria-label="Konsey odası">
      <img className="oda" src="/assets/oda.png" alt="" />
      <div className="mum-isigi" />
      <div className="kuzgun-ucus" aria-hidden="true"><div className="kuzgun" /></div>
      {/* y'ye göre sırala: önde duran (y'si büyük) sonra çizilir, arkadakinin önüne geçer */}
      {[...AJANLAR].sort((a, b) => a.y - b.y).map((a) => (
        <AjanFigur key={a.id} ajan={a} secili={a.id === props.ajan.id} onClick={() => props.onAjanSec(a.id)} />
      ))}
      <aside className="ajan-karti">
        <div className="kart-baslik"><b>{props.ajan.ad}</b> <span>{props.ajan.unvan}</span></div>
        <p>{props.ajan.gorev}</p>
      </aside>
    </section>
  )
}

function AjanFigur({ ajan, secili, onClick }: { ajan: Ajan; secili: boolean; onClick: () => void }) {
  return (
    <button
      className={'ajan' + (secili ? ' secili' : '')}
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

// Masada seçili ajanın kuzgundaki bölümü durur. Ajan sahnede ya da masadaki sekmelerden seçilir.
function KralinMasasi({ kuzgun, ajan, onAjanSec }: { kuzgun: Kuzgun | null; ajan: Ajan; onAjanSec: (id: string) => void }) {
  const metin = kuzgun ? bolum(kuzgun, ajan.bolum) : ''
  return (
    <aside className="masa">
      <div className="masa-baslik">
        <span className="mum" aria-hidden="true" />
        <img src="/assets/parca/taht.png" alt="" className="taht" />
        <h2>Kralın Masası</h2>
        <span className="mum" aria-hidden="true" />
      </div>
      <nav className="sekmeler" aria-label="Ajan bölümleri">
        {AJANLAR.map((a) => (
          <button key={a.id} className={'sekme piksel' + (a.id === ajan.id ? ' secili' : '')} aria-pressed={a.id === ajan.id} onClick={() => onAjanSec(a.id)}>
            {a.ad}
          </button>
        ))}
      </nav>
      <h3><img src="/assets/parca/parsomen.png" alt="" className="ikon" /> {ajan.bolum.replace('/', ' · ')}</h3>
      {!kuzgun && <p>Henüz kuzgun yok.</p>}
      {kuzgun && (metin
        ? <article className="parsomen"><Markdown text={metin} /></article>
        : <p role="status" className="soluk">Bu kuzgunda “{ajan.bolum.replace('/', ' · ')}” bölümü yok.</p>)}
    </aside>
  )
}
