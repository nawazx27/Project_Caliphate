/* Version 77 (2026-10-11, Nawaz: "Include entire modern Tajikistan and Kyrgyzstan in v2"). The Complete outline (CALIPH.x) takes in
   Tajikistan and Kyrgyzstan whole (the eastern Pamirs, Bishkek, Issyk-Kul and Naryn back in). Mawarāʾ al-Nahr in Kazakhstan stays as the
   red line of his map with the land round Isbījāb and Ṭarāz (Version 76). Run: node tools/v2_tjk_kgz_whole.js */
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
const TJK = country('762'), KGZ = country('417');
let X = R3mp(pc.union(R3mp(C.x.polys), TJK, KGZ));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
const before = C.x.km2; C.x.polys = X; C.x.km2 = area(X);
C.x.states = C.x.states.filter(s => !['762_T','417_T','762','417'].includes(s.id));
C.x.states.push({id:'762', n:'Tajikistan', km2:area(TJK), pct:100}, {id:'417', n:'Kyrgyzstan', km2:area(KGZ), pct:100});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.tjkKgzWhole = 'Version 77: Tajikistan and Kyrgyzstan whole (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Complete', before, '->', C.x.km2, '| to Iraq', C.xw.km2, '| V4', C.me2.km2, '| holes', X.reduce((t, p) => t + p.length - 1, 0));
