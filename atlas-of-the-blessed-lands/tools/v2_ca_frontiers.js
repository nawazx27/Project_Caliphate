/* Version 116 (2026-10-13, Nawaz: defensible frontiers for V2, V2-B and V2N in Central Asia, Khurasan and the Punjab).
   Adds the pieces of tools/data/central_asia_frontiers.geojson (made by tools/ca_frontiers.py) to each version, piece by piece:
   V2N's frontiers (for V2 and V2-B), the land between the Amu Darya, the Aral and the Syr Darya, and Kazakhstan's land to the Chu.
   Then V2 and V2-B take V2N's names for the rows it had, and the rows of the partly included countries are recounted.
   Run: node tools/v2_ca_frontiers.js   (with "rows" to only recount the rows after the whole-town passes) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/central_asia_frontiers.geojson'))).features;
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const NAMES = {
  '860_K': 'Uzbekistan: Greater Khurāsān as the author’s maps draw it, with all the land between the Amu Darya and the Syr Darya (the Kyzylkum, Nukus and Karakalpakstan east of the Amu)',
  '417_K': 'Kyrgyzstan: the Fergana valley to its mountain crests (Batken, Osh and Jalal-Abad regions), the Talas valley (Version 117, a gap filled) and the Khurāsān maps’ edge',
  '156_K': 'China: the part of Greater Khurāsān as the author’s maps draw it (the widest of them), with the Tashkurgan pocket (Version 117, a gap filled)',
  '398_K': 'Kazakhstan: the Mangystau region and the Qyzylorda region (since Version 127, by whole districts up to the author’s line from the Caspian to the Syr Darya, with the Aral district; cut back in Version 130 to his border line from the Caspian to east of the Aral), the Turkistan region to the Karatau range and the Moyynkum and Kyzylkum sands, and the Zhambyl region south of the Chu (Taraz)',
};
const N = Object.fromEntries((C.xn || C.x).states.map(s => [s.id, s]));   // xn (V2N) was merged into V2 in Version 118
const rowsOnly = process.argv[2] === 'rows';
for (const k of ['x', 'xb', 'xn']) {
  if (!C[k]) continue;
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), n = 0, fail = 0;
  if (!rowsOnly) for (const f of ADD) {
    if (k === 'xn' && f.properties.role === 'v2n') continue;
    for (const poly of R3mp(asMp(f.geometry))) { try { X = R3mp(pc.union(X, [poly])); n++; } catch (e) { fail++; } }
  }
  if (!rowsOnly) { X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]); V.polys = X; V.km2 = area(X); }
  // Baikonur (Kazakh land leased to Russia): the town and the lease south of the Syr Darya, inside since the river line
  { const kab = country('KAB'); let inside = 0; try { inside = area(R3mp(pc.intersection(kab, X))); } catch (e) {}
    V.states = V.states.filter(s => s.id !== 'KAB_S');
    if (inside > 0) V.states.push({id: 'KAB_S', n: 'Baikonur (Kazakh land leased to Russia): the town and the lease south of the Syr Darya', km2: inside, pct: Math.round(1000*inside/area(kab))/10}); }
  for (const id of ['417_K', '398_K', '156_K', '356_P', '860_K']) {
    if (id === '860_K' && V.states.some(s => s.id === '860')) continue;   // Version 126: Uzbekistan whole
    let s = V.states.find(s => s.id === id);
    if (!s) { s = {...N[id]}; V.states.push(s); }
    s.n = NAMES[id] || N[id].n;
    const cg = country(id.slice(0, 3));
    try { const inside = area(R3mp(pc.intersection(cg, X))); s.km2 = inside; s.pct = Math.round(1000*inside/area(cg))/10; } catch (e) { console.log(k, id, 'recount failed'); }
  }
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') pieces', n, 'failed', fail, V.states.filter(s => /^(417|398|156|356|860)_/.test(s.id)).map(s => s.id + ' ' + s.km2 + ' ' + s.pct + '%').join(', '));
}
fs.writeFileSync(F, JSON.stringify(C));
