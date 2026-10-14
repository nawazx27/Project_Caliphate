/* Version 125 (2026-10-14, Nawaz: the line across the North Caucasus should have the shape of real borders, not be straight; his choice:
   district borders). In V2 and V2-B, Russia's land in the Caucasus is replaced by tools/data/caucasus_districts.geojson (made by
   tools/caucasus_districts.py: Version 123's Black Sea strip and Dagestan block, plus the districts mostly south of Version 124's line).
   Row 643_N is recounted. Run: node tools/v2_caucasus_districts.js   (or "rows" to only recount after whole-town passes) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const NEW = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/caucasus_districts.geojson'))).features[0];
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const RUc = pc.intersection(R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '643')).geometry)), [[[[35, 40], [50, 40], [50, 48], [35, 48], [35, 40]]]]);
const rowsOnly = process.argv[2] === 'rows';
for (const k of ['x', 'xb']) {
  if (!C[k]) continue;
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  if (!rowsOnly) {
    for (const poly of RUc) { try { X = R3mp(pc.difference(X, [poly])); } catch (e) { fail++; } }
    for (const poly of R3mp(asMp(NEW.geometry))) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
    X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
    V.polys = X; V.km2 = area(X);
  }
  let ru = null; try { ru = area(pc.intersection(RUc, X)); } catch (e) {}
  V.states = V.states.filter(s => !['643_C', '643_D', '643_N'].includes(s.id));
  V.states.push({id: '643_N', n: 'Russia: the North Caucasus to the district borders along a line from Anapa to the Kizlyar Bay (with the Black Sea coast and V5’s Dagestan block)', km2: ru, pct: null});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ') failed', fail, '643_N', ru);
}
fs.writeFileSync(F, JSON.stringify(C));
