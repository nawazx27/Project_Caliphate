/* Version 136 (2026-10-14, Nawaz, of the widest Greater Khurāsān: "Add it in v2b as well"). V2-B (CALIPH.xb) takes V2's land in
   Kazakhstan (with Baikonur), Uzbekistan, Kyrgyzstan, Tajikistan and China exactly (with its whole towns and filled gaps), and V2's rows
   for those countries. Run: node tools/v2b_khorasan_from_v2.js */
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
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const CA = R3mp(pc.union(...['860', '762', '417', '398', '156', 'KAB'].map(country)));
const before = C.xb.km2;
let X = R3mp(pc.difference(R3mp(C.xb.polys), CA));
X = R3mp(pc.union(X, R3mp(pc.intersection(R3mp(C.x.polys), CA))));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
C.xb.polys = X; C.xb.km2 = area(X);
const re = /^(860|762|417|398|156|KAB)(_|$)/;
C.xb.states = C.xb.states.filter(s => !re.test(String(s.id))).concat(C.x.states.filter(s => re.test(String(s.id))).map(s => ({...s})));
C.xb.states.sort((a, b) => b.km2 - a.km2);
fs.writeFileSync(F, JSON.stringify(C));
console.log('xb', before, '->', C.xb.km2, '(', C.xb.km2 - before, ')');
