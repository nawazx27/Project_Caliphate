/* Version 103 (2026-10-12, Nawaz, with the silk-flag map again: "include all the lands in the image in v2 light shaded, the dark
   shaded everything associated with greater turkey ... i want that in v2"). The old map under the flag colours, besides the lands
   already in V2: Romania (yellow), Serbia of 1913 (green, which held Kosovo and North Macedonia), and, at the very top edge under
   the "Sébastopol" label, the southern tip of Crimea (yellow). Each is added whole to V2 (CALIPH.x) and V2N (CALIPH.xn): Romania,
   Serbia, Kosovo, North Macedonia (row 807_G, a sliver, becomes 807), and the Crimean peninsula (the base map draws it inside
   Russia, as its own piece; only that piece is taken, not Russia; row CRI as in V7). Run: node tools/v2_silk_map_lands.js */
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
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const crimea = country('643').filter(poly => d3.geoContains({type:'Polygon', coordinates:poly}, [34.1, 44.95]));
if (crimea.length !== 1) throw new Error('Crimea piece not found: ' + crimea.length);
const ADD = [
  {id:'642', n:'Romania', mp:country('642')},
  {id:'688', n:'Serbia', mp:country('688')},
  {id:'807', n:'North Macedonia', mp:country('807')},
  {id:'KOS', n:'Kosovo', mp:country('KOS')},
  {id:'CRI', n:'Crimea (annexed by Russia in 2014; recognised internationally as Ukraine)', mp:crimea},
];
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  for (const a of ADD) for (const poly of a.mp) {
    try { X = R3mp(pc.union(X, [poly])); }
    catch (e) { console.log(k, a.n, 'union failed for one piece:', e.message); }
  }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  const ids = new Set(ADD.map(a => a.id).concat(['807_G']));
  V.states = V.states.filter(s => !ids.has(s.id));
  for (const a of ADD) V.states.push({id:a.id, n:a.n, km2:area(a.mp), pct:100});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ')');
  for (const a of ADD) { let miss; try { miss = area(R3mp(pc.difference(a.mp, X))); } catch (e) { miss = 'check failed'; } console.log('  ', a.n.split(' (')[0], area(a.mp), 'km2, still missing', miss); }
}
fs.writeFileSync(F, JSON.stringify(C));
