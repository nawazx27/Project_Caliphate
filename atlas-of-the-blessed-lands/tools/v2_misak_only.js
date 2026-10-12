/* Version 105 (2026-10-12, Nawaz, with the Wikipedia Misak-ı Millî map and its six decisions: "Ykw, just do this greater turkey").
   Greater Turkey is now the Misak-ı Millî map alone: the red core, 1 Western Thrace, 2 the Dodecanese, 3 Kars, Ardahan and Batumi,
   4 the Aleppo vilayet, 5 the Mosul vilayet, 6 the Zor sanjak and 7 Cyprus, all inside V2 already (checked in Version 99). The lands
   that only the silk-flag map had brought in (Versions 97 and 102) come out of V2 (CALIPH.x) and V2N (CALIPH.xn): Bulgaria (row 100)
   and the sliver of North Macedonia by Dojran (row 807_G). Run: node tools/v2_misak_only.js */
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
const OUT = [...country('100'), ...country('807')];
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  for (const poly of OUT) X = R3mp(pc.difference(X, [poly]));
  X = X.filter(p => ringSr(p[0])*KM >= 1);   // drop slivers under 1 km² left along the cut
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => s.id !== '100' && s.id !== '100_G' && s.id !== '807_G');
  let left = 0; try { left = area(R3mp(pc.intersection(X, OUT))); } catch (e) { left = -1; }
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ') Bulgaria/N. Macedonia left inside', left);
}
fs.writeFileSync(F, JSON.stringify(C));
