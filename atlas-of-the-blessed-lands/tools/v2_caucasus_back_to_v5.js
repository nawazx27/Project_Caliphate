/* Version 127 (2026-10-14, Nawaz, with a screenshot of V5's Caucasus: "And make the current one go back to the one in v5"). In V2 and
   V2-B, all of Russia's land in the Caucasus (geo2's Russia within 35–50 E, 40–48 N) is replaced by V5's (CALIPH.x3): Georgia's and
   Azerbaijan's borders and V5's Dagestan block. Versions 114–126's Russian additions (the Black Sea coast, the district line, Taman) go.
   Run: node tools/v2_caucasus_back_to_v5.js   (or "rows" to only recount) */
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
const RUc = R3mp(pc.intersection(R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '643')).geometry)), [[[[35, 40], [50, 40], [50, 48], [35, 48], [35, 40]]]]));
const V5ru = R3mp(pc.intersection(RUc, R3mp(C.x3.polys)));
console.log('V5 Russia in the Caucasus', area(V5ru));
const rowsOnly = process.argv[2] === 'rows';
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  if (!rowsOnly) {
    for (const poly of RUc) { try { X = R3mp(pc.difference(X, [poly])); } catch (e) { fail++; } }
    for (const poly of V5ru) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
    X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
    V.polys = X; V.km2 = area(X);
  }
  let ru = null; try { ru = area(pc.intersection(RUc, X)); } catch (e) {}
  V.states = V.states.filter(s => !['643_C', '643_D', '643_N'].includes(s.id));
  V.states.push({id: '643_D', n: 'Russia: V5’s Dagestan block (Derbent, Bāb al-Abwāb)', km2: ru, pct: null});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ') failed', fail, '643_D', ru);
}
fs.writeFileSync(F, JSON.stringify(C));
