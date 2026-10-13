/* Version 106 (2026-10-12, Nawaz): keep every settlement that V2's / V2N's own lines cut in two whole, inside.
   Adds the outer parts listed in tools/data/split_settlements.geojson (made by tools/split_settlements.py) to CALIPH.x and
   CALIPH.xn, piece by piece, and updates the rows of the partly included countries (km² and share).
   Run: node tools/v2_whole_settlements.js [additions.geojson] */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = JSON.parse(fs.readFileSync(process.argv[2] || path.join(__dirname, 'data/split_settlements.geojson')));   // a later pass may give its own file
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
for (const k of ['x', 'xn', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), n = 0, fail = 0;
  for (const f of ADD.features.filter(f => f.properties.v === k)) {
    for (const poly of R3mp(asMp(f.geometry))) {
      try { X = R3mp(pc.union(X, [poly])); n++; } catch (e) { fail++; }
    }
  }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);   // small holes left between added pieces are filled, as in the other tools
  V.polys = X; V.km2 = area(X);
  // rows of the partly included countries: share now inside
  for (const s of V.states) {
    const m = /^(\d{3})_[A-Z]$/.exec(s.id); if (!m || !['860','417','398','156','356','191','688','705','642','380','643'].includes(m[1])) continue;
    try { const cg = country(m[1]); const inside = area(R3mp(pc.intersection(cg, X))); s.km2 = inside; s.pct = Math.round(1000*inside/area(cg))/10; } catch (e) {}
  }
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') pieces added', n, 'failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
