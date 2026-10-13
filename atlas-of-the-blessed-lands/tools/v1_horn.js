/* Version 110 (2026-10-13, Nawaz: "Add Eritrea, somaliland and Somalia to v1").
   Adds Eritrea (232), Somaliland (SOL) and Somalia (706), each whole, to V1 (CALIPH.me) and to V4 (CALIPH.me2), which is V1 with
   six more lands. Version 111 (Nawaz: "Sure", to adding Djibouti): Djibouti (262) too, so the Horn has no gap.
   Run: node tools/v1_horn.js (it can be run again; the rows are replaced) */
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
const ADD = [['232', 'Eritrea'], ['SOL', 'Somaliland'], ['706', 'Somalia'], ['262', 'Djibouti']];
for (const k of ['me', 'me2']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const [id] of ADD) for (const poly of country(id)) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  for (const [id, n] of ADD) { V.states = V.states.filter(s => s.id !== id); V.states.push({id, n, km2: area(country(id)), pct: 100}); }
  V.states.sort((a, b) => b.km2 - a.km2);
  let miss = 0; for (const [id] of ADD) { try { miss += area(R3mp(pc.difference(country(id), X))); } catch (e) { miss = -1; } }
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed', fail, 'still missing', miss, 'km2;', V.states.length, 'rows');
}
fs.writeFileSync(F, JSON.stringify(C));
