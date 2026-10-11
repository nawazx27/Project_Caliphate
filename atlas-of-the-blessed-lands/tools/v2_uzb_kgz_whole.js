/* Version 88 (2026-10-11, Nawaz: "Add entire modern Uzbekistan and Kyrgyzstan to v2").
   V2 (CALIPH.x) takes Uzbekistan and Kyrgyzstan whole by today's borders, on top of Greater Khurāsān at its widest (Version 87);
   the parts of Kazakhstan and China from the Khurāsān maps stay. Run: node tools/v2_uzb_kgz_whole.js */
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
const UZB = country('860'), KGZ = country('417');
const before = C.x.km2;
let X = R3mp(pc.union(R3mp(C.x.polys), UZB, KGZ));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
C.x.states = C.x.states.filter(s => !['860', '860_K', '417', '417_K'].includes(s.id));
C.x.states.push({id:'860', n:'Uzbekistan', km2:area(UZB), pct:100}, {id:'417', n:'Kyrgyzstan', km2:area(KGZ), pct:100});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.uzbKgzWhole = 'Version 88: Uzbekistan and Kyrgyzstan whole (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '(+', C.x.km2 - before, ') | Uzbekistan', area(UZB), 'Kyrgyzstan', area(KGZ), '| V3', C.xw.km2, 'V4', C.me2.km2);
