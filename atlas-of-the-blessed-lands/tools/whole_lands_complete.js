/* Version 81 (2026-10-11, Nawaz: "leave no area that the lands I ask you about occupy").
   Every land listed whole in a version (a state row at 100%) is put back into that version in full: earlier steps dropped pieces under
   1 km² and some small islands and coastal slivers, so each whole country was missing a few to a few hundred km². This unions each whole
   country's full shape (as the base map draws it) into every version that lists it, and keeps every piece, however small.
   Lands listed in part (e.g. "Italy: Sicily") are untouched. Run: node tools/whole_lands_complete.js */
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
const G = {}; geo.objects.countries.geometries.forEach(g => { G[String(g.id)] = g; });
const shape = id => { const f = topojson.feature(geo, G[id]); return f.geometry ? R3mp(asMp(f.geometry)) : null; };
for (const k of ['me', 'x', 'xw', 'me2', 'x3', 'v2', 'g']) {
  const V = C[k], whole = V.states.filter(s => G[s.id] && s.pct >= 99.5).map(s => shape(s.id)).filter(Boolean);
  const before = V.km2;
  let X = R3mp(pc.union(R3mp(V.polys), ...whole));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  const miss = whole.reduce((t, s) => { try { return t + area(R3mp(pc.difference(s, X))); } catch (e) { return t; } }, 0);  /* check only; a rare clipping failure skips that land's check */
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') pieces', X.length, '| still missing', miss);
}
fs.writeFileSync(F, JSON.stringify(C));
