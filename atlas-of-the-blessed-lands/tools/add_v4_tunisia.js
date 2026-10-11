/* Version 69 (2026-10-11, Nawaz's request: "Add Tunisia to V4"). V4 (the Complete outline, CALIPH.x; it ended at Libya's western
   border) takes in Tunisia, whole, from the base map's own country. Run once: node tools/add_v4_tunisia.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.x.tunisia){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const TUN = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '788')).geometry));
const before = area(C.x.polys), oldHoles = C.x.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = R3mp(pc.union(R3mp(C.x.polys), TUN));
/* keep the outline's own holes; drop slivers left where Tunisia's and Libya's borders do not quite meet */
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]);
const gain = area(X) - before; C.x.polys = X; C.x.km2 += gain;
const row = C.x3.states.find(s => s.id === '788'); C.x.states.push({...row}); C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.tunisia = 'Version 69: Tunisia, whole, in V4 (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V4 +', gain, 'km² ->', C.x.km2, '| states', C.x.states.length, '| V3', C.xw.km2, 'V5', C.x3.km2);
