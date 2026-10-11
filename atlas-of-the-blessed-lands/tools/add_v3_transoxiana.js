/* Version 72 (2026-10-11, Nawaz, with two screenshots: the frontier fortresses (thughūr and ribāṭ: Ashkelon, Alexandria, Tarsus,
   Qazvin) and Transoxiana and Greater Khurasan (Bukhara, Samarkand, Fergana): "Include these as well in the v3"). The four towns,
   Turkmenistan, Afghanistan and Iran's Khurasan were already in V3 (CALIPH.x, the Complete outline); Transoxiana is added as
   Uzbekistan, Tajikistan and Kyrgyzstan, whole (the Fergana valley is shared by all three). Run once: node tools/add_v3_transoxiana.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.x.transoxiana){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const IDS = ['860','762','417'];   /* Uzbekistan, Tajikistan, Kyrgyzstan */
const NEW = IDS.map(id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry)));
const V = C.x, before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = R3mp(pc.union(R3mp(V.polys), ...NEW));
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]);
const gain = area(X) - before; V.polys = X; V.km2 += gain;
IDS.forEach(id => { const s = C.x3.states.find(s => s.id === id); if(!s) throw new Error('no row ' + id); V.states.push({...s}); });
V.states.sort((a, b) => b.km2 - a.km2);
V.transoxiana = 'Version 72: Uzbekistan, Tajikistan and Kyrgyzstan, whole, in V3 (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V3 +', gain, '->', V.km2, '| rows', V.states.length, '| V2', C.xw.km2, 'V4', C.me2.km2);
