/* Version 107 (2026-10-13, Nawaz): the whole Balkan Peninsula, as Wikipedia's map draws it (OpenStreetMap relation 4016746),
   into V2 (CALIPH.x) and V2N (CALIPH.xn). Adds the pieces of tools/data/balkans_v2.geojson (made by tools/balkans.py) piece by
   piece and writes the rows: whole countries 100%, the others as "<id>_B" with the share inside.
   Run: node tools/v2_balkans.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/balkans_v2.geojson')));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const NAME = {'191':'Croatia: the part in the Balkan Peninsula (south of the Sava and Kupa, with Istria, Dalmatia and all the Adriatic islands)',
  '688':'Serbia: the part in the Balkan Peninsula (south of the Sava and Danube)', '705':'Slovenia: the part in the Balkan Peninsula (the south-west, with the coast)',
  '642':'Romania: Dobruja (the part in the Balkan Peninsula)', '380':'Italy: Trieste and its coast (the part in the Balkan Peninsula as the map draws it)'};
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const f of ADD.features) for (const poly of R3mp(asMp(f.geometry))) {
    try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; }
  }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  for (const f of ADD.features) {
    const id = f.properties.id;
    V.states = V.states.filter(s => s.id !== id && s.id !== id + '_B' && s.id !== id + '_G');
    if (f.properties.whole) V.states.push({id, n: f.properties.n === 'Bosnia and Herz.' ? 'Bosnia and Herzegovina' : f.properties.n, km2: area(country(id)), pct: 100});
    else { const cg = country(id); const ins = area(R3mp(asMp(f.geometry)));   // the piece is exactly the part inside
           V.states.push({id: id + '_B', n: NAME[id], km2: ins, pct: Math.round(1000*ins/area(cg))/10}); }
  }
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed pieces', fail);
  console.log('  ', V.states.filter(s => ADD.features.some(f => s.id.split('_')[0] === f.properties.id)).map(s => s.id + ' ' + s.km2 + ' ' + s.pct + '%').join(' | '));
}
fs.writeFileSync(F, JSON.stringify(C));
