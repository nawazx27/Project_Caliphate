/* Version 115 (2026-10-13, Nawaz: "Ykw, just give it v5 borders"; his choice: V5's border, keeping Russia's Black Sea coast;
   V2, V2-B and V2N). Takes out of each version Russia in the Caucasus except the Black Sea coast ('drop' in
   tools/data/caucasus_v5.geojson, made by tools/caucasus_v5.py) and adds V5's Russian land there ('add', piece by piece).
   Rows: 643_GC and 643_DC (Version 114) go; 643_C is the Black Sea coast, 643_D is V5's Dagestan block.
   Run: node tools/v2_caucasus_v5.js        (or with "rows" to only recount the two rows after whole-town passes) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const D = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/caucasus_v5.geojson'))).features;
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const box = (w, s, e, n) => [[[[w, s], [e, s], [e, n], [w, n], [w, s]]]];
const RU = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '643')).geometry));
const ruIn = (X, b) => { try { return area(pc.intersection(pc.intersection(RU, b), X)); } catch (e) { return null; } };
const rowsOnly = process.argv[2] === 'rows';
for (const k of ['x', 'xb', 'xn']) {
  if (!C[k]) continue;   // V2N (xn) was merged into V2 in Version 118
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  if (!rowsOnly) {
    for (const poly of R3mp(asMp(D.find(f => f.properties.role === 'drop').geometry))) { try { X = R3mp(pc.difference(X, [poly])); } catch (e) { fail++; } }
    for (const poly of R3mp(asMp(D.find(f => f.properties.role === 'add').geometry))) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
    X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
    V.polys = X; V.km2 = area(X);
  }
  V.states = V.states.filter(s => !['643_GC', '643_DC', '643_C', '643_D'].includes(s.id));
  V.states.push({id: '643_C', n: 'Russia: the Black Sea coast from Anapa to Sochi, on the southern side of the Caucasus crest', km2: ruIn(X, box(36, 42.5, 42, 46)), pct: null});
  V.states.push({id: '643_D', n: 'Russia: Derbent, the Samur valley and the Dagestan coast (V5’s border)', km2: ruIn(X, box(44, 40, 50, 46)), pct: null});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ') failed', fail, V.states.filter(s => s.id.startsWith('643')).map(s => s.id + ' ' + s.km2).join(', '));
}
fs.writeFileSync(F, JSON.stringify(C));
