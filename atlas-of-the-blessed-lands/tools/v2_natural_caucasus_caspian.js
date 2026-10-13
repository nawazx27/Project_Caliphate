/* Version 109 (2026-10-13, Nawaz: "Make this place follow its natural border"; his choices: the Caucasus and the Caspian shore;
   out to the crest, keeping Georgia and Azerbaijan whole; in V2, V2-B and V2N).
   - Adds the Russian land on the southern side of the Greater Caucasus watershed (tools/data/caucasus_south_of_crest.geojson, from
     tools/caucasus_crest.py): the Black Sea coast from Anapa to Sochi and thin strips along the crest. Row 643_C.
   - Takes out the Caspian water (tools/data/caspian_water_in_v2.geojson, from tools/caspian_shore.py), so the outline follows the shore.
     Row CAS_K goes.
   Run: node tools/v2_natural_caucasus_caspian.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/caucasus_south_of_crest.geojson')));
const WAT = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/caspian_water_in_v2.geojson')));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const RU = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '643')).geometry));
for (const k of ['x', 'xb', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fa = 0, fw = 0, added = 0;
  for (const f of ADD.features) for (const poly of R3mp(asMp(f.geometry))) {
    try { X = R3mp(pc.union(X, [poly])); added += area([poly]); } catch (e) { fa++; }
  }
  const afterAdd = area(X);
  for (const f of WAT.features.filter(f => f.properties.v === k)) for (const poly of R3mp(asMp(f.geometry))) {
    try { X = R3mp(pc.difference(X, [poly])); } catch (e) { fw++; }
  }
  X = X.filter(p => ringSr(p[0])*KM >= 0.5);   // specks left along the shore
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => s.id !== 'CAS_K' && s.id !== '643_C');
  V.states.push({id:'643_C', n:'Russia: the southern side of the Greater Caucasus (the Black Sea coast from Anapa to Sochi, with thin strips along the crest)', km2: Math.round(added), pct: Math.round(1000*added/area(RU))/10});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '-> +crest', afterAdd, '-> -Caspian water', V.km2, '| failed add', fa, 'failed water', fw);
}
fs.writeFileSync(F, JSON.stringify(C));
