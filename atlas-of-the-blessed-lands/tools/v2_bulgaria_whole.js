/* Version 102 (2026-10-12, Nawaz, with the flag map again and a close-up of its Balkan part: "Look at ... the shaded regions you
   left, Bulgaria. Check whether if all the lands included in this image, even the shaded parts and the dark colored parts are
   included in the V2"). The old map under the flag shades the whole of Bulgaria (pink); his standing rule is that every shaded
   region of a map he sends goes in whole. So Bulgaria, whole, is added to V2 (CALIPH.x) and V2N (CALIPH.xn); row 100_G becomes 100.
   Run: node tools/v2_bulgaria_whole.js */
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
const BGR = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '100')).geometry));
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  for (const poly of BGR) X = R3mp(pc.union(X, [poly]));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => s.id !== '100_G' && s.id !== '100');
  V.states.push({id:'100', n:'Bulgaria', km2:area(BGR), pct:100});
  V.states.sort((a, b) => b.km2 - a.km2);
  let miss = 0; try { miss = area(R3mp(pc.difference(BGR, X))); } catch (e) { miss = -1; }
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') Bulgaria still missing', miss);
}
fs.writeFileSync(F, JSON.stringify(C));
