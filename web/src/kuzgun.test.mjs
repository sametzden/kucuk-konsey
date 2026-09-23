import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { ayikla } from './kuzgun.ts'

test('v2 gerçek raporu beş kart ve kaynaklı mühürlerle okur', () => {
  const text = readFileSync(new URL('../../kuzgunlar/2026-09-23.md', import.meta.url), 'utf8')
  const result = ayikla('2026-09-23', text)
  assert.equal(result.soz.length, 5)
  assert.ok(result.soz.every(s => s.neden && s.firsat && s.risk && s.cozecek))
  assert.ok(result.muhurler.some(m => m.kap === 'KAP 1666885' && m.url?.startsWith('https://')))
})
test('eski biçimde çatışma ve çözecek veri korunur', () => {
  const result = ayikla('2026-09-22', "## Tyrion'un sözü\n\n**ASELS**\n- **Bugün:** Olay\n- **Çatışma:** İki okuma\n- **Çözecek veri:** Nakit\n## ASELS\n")
  assert.equal(result.soz[0].catisma, 'İki okuma')
  assert.equal(result.soz[0].cozecek, 'Nakit')
})
test('yarım rapor sahte özet üretmez', () => {
  assert.deepEqual(ayikla('2026-09-23', '## ASELS\nToplanıyor').soz, [])
})
test('Dünya satırı hisse kartlarından ayrı okunur', () => {
  const result = ayikla('2026-09-24', "## Tyrion'un sözü\n\n**Dünya:** Fed faizi sabit tuttu.\n\n**ASELS**\n- **Bugün:** Olay\n## ASELS\n")
  assert.equal(result.dunya, 'Fed faizi sabit tuttu.')
  assert.equal(result.soz.length, 1)
})
