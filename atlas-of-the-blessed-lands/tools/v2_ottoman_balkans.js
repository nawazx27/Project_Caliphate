/* Version 96 (2026-10-12, Nawaz: "include greater turkey"; asked which, he chose the Ottoman Balkans, in V2 and V2N).
   Adds to V2 (CALIPH.x) and V2N (CALIPH.xn), each whole by today's borders as the base map draws them: Bulgaria, North Macedonia,
   Albania, Kosovo, Serbia, Montenegro, Bosnia and Herzegovina, Romania and Moldova (with Transnistria), and Crimea with Sevastopol
   (admin1_used.geojson; the base map follows Natural Earth in drawing it under Russia, which annexed it from Ukraine in 2014).
   Run: node tools/v2_ottoman_balkans.js */
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
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const G = {}; geo.objects.countries.geometries.forEach(g => { G[String(g.id)] = g; });
const country = id => R3mp(asMp(topojson.feature(geo, G[id]).geometry));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const prov = (c, n) => R3mp(asMp(A1.find(f => f.properties.adm0_a3 === c && f.properties.name === n).geometry));
/* Crimea: the two provinces, and the base map's own coast of the peninsula (Russia's shape round the peninsula, less Krasnodar
   province across the Kerch Strait), so no sliver between the province lines and the drawn coast is lost */
const CRIMEA0 = R3mp(pc.union(prov('RUS', 'Crimea'), prov('RUS', 'Sevastopol')));
const CBOX = [[[[32.3, 44.2], [36.7, 44.2], [36.7, 45.6], [35.1, 45.6], [34.6, 46.0], [33.95, 46.2], [33.5, 46.2], [32.3, 46.0], [32.3, 44.2]]]];
const CRIMEA = R3mp(pc.union(CRIMEA0, R3mp(pc.difference(pc.intersection(country('643'), CBOX), prov('RUS', 'Krasnodar')))));
const WHOLE = [['100', 'Bulgaria'], ['807', 'North Macedonia'], ['008', 'Albania'], ['KOS', 'Kosovo'], ['688', 'Serbia'], ['499', 'Montenegro'],
  ['070', 'Bosnia and Herzegovina'], ['642', 'Romania'], ['498', 'Moldova (with Transnistria)']];
const LANDS = WHOLE.map(([id, n]) => ({id, n, mp: country(id)}));
LANDS.push({id:'643_C', n:'Crimea and Sevastopol (annexed by Russia from Ukraine in 2014; most states recognise it as Ukraine’s)', mp: CRIMEA});
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  for (const L of LANDS) X = R3mp(pc.union(X, L.mp));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  for (const L of LANDS) { V.states = V.states.filter(s => s.id !== L.id); V.states.push({id:L.id, n:L.n, km2:area(L.mp), pct:100}); }
  V.states.sort((a, b) => b.km2 - a.km2);
  V.ottomanBalkans = 'Version 96: the Ottoman Balkans (Rumelia with the vassal Wallachia, Moldavia and Crimea), whole by today’s borders (Nawaz)';
  const miss = LANDS.reduce((t, L) => { try { return t + area(R3mp(pc.difference(L.mp, X))); } catch (e) { return t; } }, 0);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') still missing', miss);
}
console.log(LANDS.map(L => L.id + ' ' + area(L.mp)).join(' | '), '| Crimea provinces only', area(CRIMEA0), '| V3', C.xw.km2, 'V4', C.me2.km2);
fs.writeFileSync(F, JSON.stringify(C));
