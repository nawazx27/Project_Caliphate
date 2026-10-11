/* Version 74 (2026-10-11, Nawaz: "Transoxiana borders should look like this in the v3", with a map of Khwārazm, Transoxiana and
   Khorasan drawn as red dashed outlines; kept as reference/transoxiana_khwarazm_khorasan.webp).
   The outlines were traced from the map: the map was registered to the base map by matching its coasts and borders (median error
   about 3 px, roughly 4 km), and the two dashed outlines were filled and turned into longitude/latitude rings (tools/data/transoxiana_trace.json).
   V3's Central Asia is rebuilt: Uzbekistan, Tajikistan, Kyrgyzstan and the southern Kazakhstan strip come out, and in go
   Transoxiana and Khwārazm as traced (on land). Turkmenistan and Afghanistan stay whole, as before. Thin strips left between a traced
   line and land already inside (the Amu Darya bank at Termez, for example) are filled, so the drawn line's small errors leave no gaps.
   SHASH=1 also keeps Shāsh (Uzbekistan's Tashkent region and city) and the Isbījāb strip (Kazakhstan's Turkistan and Zhambyl regions).
   Usage: node tools/v3_transoxiana_traced.js [--dry] ; SHASH=1 node tools/v3_transoxiana_traced.js [--dry] */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const TR = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/transoxiana_trace.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const DRY = process.argv.includes('--dry'), SHASH = process.env.SHASH === '1';
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const prov = (a3, n) => A1.filter(f => f.properties.adm0_a3 === a3 && f.properties.name === n).map(f => R3mp(asMp(f.geometry)));
const UZB = country('860'), TJK = country('762'), KGZ = country('417'), KAZ = country('398');
const CA = R3mp(pc.union(UZB, TJK, KGZ, KAZ));                       /* the lands the traced outlines may take from */
/* 'merged' is Transoxiana and Khwārazm traced as one shape, so no seam is left between the two dashed outlines */
const TRACED = R3mp(pc.intersection(R3mp([[TR.merged]]), CA));
let ADD = TRACED;
if(SHASH){ const shash = R3mp(pc.intersection(R3mp(pc.union(...prov('UZB', 'Tashkent'))), UZB));
  const isb = R3mp(pc.intersection(R3mp(pc.union(...prov('KAZ', 'South Kazakhstan'), ...prov('KAZ', 'Zhambyl'))), KAZ));
  ADD = R3mp(pc.union(ADD, shash, isb)); }
/* V3 without its Central Asian additions, then with the traced lands */
let base = R3mp(pc.difference(R3mp(C.x.polys), CA));
let X = R3mp(pc.union(base, ADD));
/* fill gaps: interior rings (holes) up to 20,000 km² that lie inside the Central Asian lands are slivers between a drawn line and a border */
let filled = 0;
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM; const c = d3.polygonCentroid(r);
  const ca = CA.some(q => d3.polygonContains(q[0], c)); if(ca && a < 20000){ filled += a; return false; } return true; })]);
/* and thin pieces of Central Asian land outside the traced lines but wedged against land already inside (the Amu Darya bank) */
const outside = R3mp(pc.difference(CA, X));
let wedge = [];
outside.forEach(p => { const a = ringSr(p[0])*KM; if(a > 8000) return;
  /* a wedge: most of its edge is shared with V3 after the union (measure by buffering-free test: sample its ring and count points on V3's edge) */
  const pts = p[0]; let near = 0;
  for(const q of pts){ const inX = X.some(xp => d3.polygonContains(xp[0], [q[0]+0.02, q[1]]) || d3.polygonContains(xp[0], [q[0]-0.02, q[1]]) || d3.polygonContains(xp[0], [q[0], q[1]+0.02]) || d3.polygonContains(xp[0], [q[0], q[1]-0.02])); if(inX) near++; }
  if(near / pts.length > 0.85) wedge.push(p); });
if(wedge.length) X = R3mp(pc.union(X, wedge));
X = X.filter(p => ringSr(p[0])*KM >= 1);
const before = C.x.km2, after = area(X);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
console.log(SHASH ? 'with Shash and Isbijab' : 'traced only', '| V3', before, '->', after, '| filled holes', Math.round(filled), 'wedges', wedge.length, Math.round(wedge.reduce((t, p) => t + ringSr(p[0])*KM, 0)));
console.log('  Uzbekistan', kmIn(UZB), 'of', area(UZB), '| Tajikistan', kmIn(TJK), 'of', area(TJK), '| Kyrgyzstan', kmIn(KGZ), 'of', area(KGZ), '| Kazakhstan', kmIn(KAZ), 'of', area(KAZ));
if(DRY) process.exit(0);
C.x.polys = X; C.x.km2 = after;
const rowOf = (id, n, mp, tot) => { const k = kmIn(mp); return k > 0 ? {id, n, km2:k, pct:Math.round(1000*k/tot)/10} : null; };
C.x.states = C.x.states.filter(s => !['860','762','417','398_S'].includes(s.id));
[rowOf('860_T', 'Uzbekistan: Transoxiana and Khwārazm' + (SHASH ? ', with Shāsh (Tashkent)' : '') + ', as traced', UZB, area(UZB)),
 rowOf('762_T', 'Tajikistan: Transoxiana, as traced (without the Pamirs)', TJK, area(TJK)),
 rowOf('417_T', 'Kyrgyzstan: Farghāna, as traced', KGZ, area(KGZ)),
 rowOf('398_T', 'Kazakhstan: ' + (SHASH ? 'Isbījāb (the Turkistan and Zhambyl regions) and the Khwārazm shore, as traced' : 'the Khwārazm shore of the Aral, as traced'), KAZ, area(KAZ))].filter(Boolean).forEach(r => C.x.states.push(r));
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.transoxTraced = 'Version 74: Transoxiana and Khwārazm traced from Nawaz\'s map' + (SHASH ? ', with Shāsh and Isbījāb' : '');
fs.writeFileSync(F, JSON.stringify(C));
console.log('written');
