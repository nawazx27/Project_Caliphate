/* Version 139 (2026-10-14, Nawaz: Greater Khurāsān "according to all classical sources and geographers to widest and maximum", Central
   Asia cut back to it). In V2 and V2-B, all land in Kazakhstan (with Baikonur), Uzbekistan, Kyrgyzstan, Tajikistan and China is replaced
   by tools/data/khorasan_classical.geojson (tools/khorasan_classical.py); rows of those countries recounted. Pakistan, Afghanistan and
   Turkmenistan stay whole. Run: node tools/v2_khorasan_classical.js   (or "rows" to only recount) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const IDS = [['860', 'Uzbekistan'], ['762', 'Tajikistan'], ['417', 'Kyrgyzstan'], ['398', 'Kazakhstan'], ['156', 'China'], ['KAB', 'Baikonur (Kazakh land leased to Russia)']];
const CG = Object.fromEntries(IDS.map(([id]) => [id, country(id)]));
const CA = R3mp(pc.union(...Object.values(CG)));
const NEW = R3mp(asMp(JSON.parse(fs.readFileSync(path.join(__dirname, 'data/khorasan_classical.geojson'))).features[0].geometry));
const NAME = {
  '860': 'Uzbekistan: Greater Khurāsān, Transoxiana and Khwārazm at their widest classical extent',
  '417': 'Kyrgyzstan: Farghāna, Osh, the Talas valley, and the Chu valley and Issyk-Kul (Nawākath, Barskhān)',
  '398': 'Kazakhstan: Isbījāb’s district (Shymkent, Turkistan, Otrār, Ṭarāz) and the lower Syr Darya (Qyzylorda region: Jand, Yanghikant)',
  '156': 'China: the Kashgar oasis to the Taklamakan’s edge (Kashgar and Kizilsu prefectures) and the Pamir edges',
  'KAB': 'Baikonur (Kazakh land leased to Russia), in the Qyzylorda region' };
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  if (process.argv[2] !== 'rows') {
    X = R3mp(pc.union(R3mp(pc.difference(X, CA)), NEW));
    X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
    V.polys = X; V.km2 = area(X);
  }
  V.states = V.states.filter(s => !/^(860|762|417|398|156|KAB)(_|$)/.test(String(s.id)));
  for (const [id, nm] of IDS) {
    const a = area(CG[id]), i = area(R3mp(pc.intersection(X, CG[id])));
    if (i < 1) continue;
    const pct = Math.round(1000*i/a)/10;
    V.states.push(pct >= 99.5 ? {id, n: nm, km2: a, pct: 100} : {id: id + '_K', n: NAME[id] || nm, km2: i, pct});
  }
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ')', V.states.filter(s => /^(860|762|417|398|156|KAB)/.test(s.id)).map(s => s.id + ' ' + s.km2 + ' ' + s.pct + '%').join(', '));
}
fs.writeFileSync(F, JSON.stringify(C));
