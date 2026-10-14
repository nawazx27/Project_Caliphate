/* Version 138 (2026-10-14, Nawaz: "Add entire modern Pakistan, Afghanistan, Uzbekistan, Kazakhstan, Turkmenistan, Tajikistan, Kyrgyzstan
   to v2 and v2b and even at the thing that you said was left outside"). Each of the seven is taken whole by today's borders (geo2;
   Kazakhstan with Baikonur) into V2 and V2-B, rows set to the whole country; and tools/data/kashgar_and_shore.geojson
   (tools/kashgar_and_shore.py: the Kashgar and Kizilsu prefectures of China and the last Caspian-shore slivers) is added.
   Run: node tools/v2_ca_countries_whole.js */
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
const LIST = [['586', 'Pakistan'], ['004', 'Afghanistan'], ['860', 'Uzbekistan'], ['398', 'Kazakhstan'], ['795', 'Turkmenistan'], ['762', 'Tajikistan'], ['417', 'Kyrgyzstan'], ['KAB', 'Baikonur (Kazakh land leased to Russia)']];
const G = LIST.map(([id]) => country(id));
const EXTRA = R3mp(asMp(JSON.parse(fs.readFileSync(path.join(__dirname, 'data/kashgar_and_shore.geojson'))).features[0].geometry));
const CN = country('156');
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const g of [...G, EXTRA]) for (const poly of g) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => !/^(586|004|860|398|795|762|417|KAB|156)(_|$)/.test(String(s.id)));
  LIST.forEach(([id, n], i) => V.states.push({id, n, km2: area(G[i]), pct: 100}));
  const cn = area(R3mp(pc.intersection(X, CN)));
  V.states.push({id: '156_K', n: 'China: the Kashgar and Kizilsu prefectures (the Kashgar oasis to the Taklamakan’s edge, Tashkurgan) and the edges the author’s region maps cross', km2: cn, pct: Math.round(1000*cn/area(CN))/10});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed', fail, 'China', cn);
}
fs.writeFileSync(F, JSON.stringify(C));
