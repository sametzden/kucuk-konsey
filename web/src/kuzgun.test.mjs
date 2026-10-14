import { test } from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { ayikla, bolum } from './kuzgun.ts'
import { AJANLAR } from './ajanlar.ts'

const gercek = () => ayikla('2026-10-14', readFileSync(new URL('../../kuzgunlar/2026-10-14.md', import.meta.url), 'utf8'))

test('frontmatter gövdeden ayrılır, mod okunur', () => {
  const k = gercek()
  assert.equal(k.mod, 'gundem')
  assert.ok(k.metin.startsWith('# Kuzgun'))
})
test('gerçek gündem raporunda her ajanın bölümü dolu', () => {
  const k = gercek()
  for (const a of AJANLAR) assert.ok(bolum(k, a.bolum), `${a.ad} bölümü boş`)
})
test('Ateş ve Buz birbirinin metnini almaz', () => {
  const k = gercek()
  assert.ok(!bolum(k, 'Tartışma/Ateş').includes('Şüpheli içerik'))
  assert.ok(bolum(k, 'Tartışma/Buz').includes('Şüpheli içerik'))
})
test('bölüm, içindeki ### başlıklarla bölünmez; sonraki ## başlıkta biter', () => {
  const k = ayikla('2026-10-15', '## Gündem\n### Tema\n- satır\n## Piyasa\ntablo\n')
  assert.equal(bolum(k, 'Gündem'), '### Tema\n- satır')
  assert.equal(bolum(k, 'Piyasa'), 'tablo')
})
test('olmayan bölüm boş döner, sahte içerik üretmez', () => {
  const k = ayikla('2026-10-15', '## Gündem\nToplanıyor')
  assert.equal(bolum(k, "Tyrion'un sözü"), '')
  assert.equal(bolum(k, 'Tartışma/Ateş'), '')
  assert.equal(k.mod, '')
})
