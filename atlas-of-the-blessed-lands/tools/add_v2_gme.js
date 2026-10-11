/* Version 73, second step: V2 is "V5 stopping at Iraq's eastern border", so it takes Western Sahara (the part Morocco holds and
   the rest) and Mauritania, whole, as V5 does (tools/add_v3_kaz_v5_gme.js). Run after that: node tools/add_v2_gme.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const tc = require(path.join(ROOT, 'node_modules/topojson-client')), pc = require(path.join(ROOT, 'node_modules/polygon-clipping')), d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json'))); const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.xw.gme){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2; const rs = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, p) => t + rs(p[0]) - p.slice(1).reduce((h, r) => h + rs(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000, R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(tc.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const V = C.xw, before = area(V.polys), oh = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = R3mp(pc.union(R3mp(V.polys), ...['504', '732', '478'].map(country)));
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oh.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || rs(r)*KM >= 5000; })]).filter(p => rs(p[0])*KM >= 1);
const gain = area(X) - before; V.polys = X; V.km2 += gain;
['504_W', '732', '478'].forEach(id => V.states.push({...C.x3.states.find(s => s.id === id)}));
V.states.sort((a, b) => b.km2 - a.km2); V.gme = 'Version 73: Western Sahara (both parts) and Mauritania, whole, as in V5';
fs.writeFileSync(F, JSON.stringify(C)); console.log('V2 +', gain, '->', V.km2);
