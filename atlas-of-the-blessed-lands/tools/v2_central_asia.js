/* Version 75 (2026-10-11, Nawaz, with five pictures of Transoxiana/Mawarāʾ al-Nahr, Khwārazm and Greater Khurasan: "In v2 include all of
   modern Uzbekistan, Tajikistan, Kyrgyzstan, and build upon them Mawara'an-Nahr everything included in these images").
   V2 (CALIPH.x, the Complete outline): its Central Asia becomes all of Uzbekistan, Tajikistan and Kyrgyzstan, whole, plus every part of
   Mawarāʾ al-Nahr and Khwārazm that the pictures draw beyond them:
   - the dashed outlines of reference/transoxiana_khwarazm_khorasan.webp (tools/data/transoxiana_trace.json, Version 74);
   - the solid Mawarāʾ al-Nahr outline of reference/mawarannahr_khwarazm_khorasan.jpg (tools/data/mawarannahr_trace2.json; that frame
     was registered to the base map by the Caspian, Aral, Kara-Bogaz-Gol and Issyk-Kul shores, median error about 1.2 px, ~8 km);
   - Shāsh and Isbījāb, named on reference/transoxiana_places.webp (Uzbekistan's Tashkent region; Kazakhstan's Turkistan and Zhambyl regions).
   Khwārazm on the second frame lies inside Uzbekistan and Turkmenistan (checked by its corners), both whole in V2. Kashgar, at the edge of
   the places map, is not part of Mawarāʾ al-Nahr and is not added. Run: node tools/v2_central_asia.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const T1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/transoxiana_trace.json')));
const T2 = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/mawarannahr_trace2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const prov = (a3, n) => A1.filter(f => f.properties.adm0_a3 === a3 && f.properties.name === n).map(f => R3mp(asMp(f.geometry)));
const UZB = country('860'), TJK = country('762'), KGZ = country('417'), KAZ = country('398');
const CA = R3mp(pc.union(UZB, TJK, KGZ, KAZ));
const KAZPART = R3mp(pc.union(
  pc.intersection(R3mp([[T1.merged]]), KAZ),
  pc.intersection(R3mp([[T2.mawarannahr_img2]]), KAZ),
  pc.intersection(R3mp(pc.union(...prov('KAZ', 'South Kazakhstan'), ...prov('KAZ', 'Zhambyl'))), KAZ))).filter(p => ringSr(p[0])*KM >= 20);
const base = R3mp(pc.difference(R3mp(C.x.polys), CA));
let X = R3mp(pc.union(base, UZB, TJK, KGZ, KAZPART));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
const kazKm = area(R3mp(pc.intersection(X, KAZ)));
const before = C.x.km2; C.x.polys = X; C.x.km2 = area(X);
C.x.states = C.x.states.filter(s => !['860_T','762_T','417_T','398_T','860','762','417','398_S'].includes(s.id));
const row = (id, n, mp) => ({id, n, km2:area(mp), pct:100});
C.x.states.push(row('860', 'Uzbekistan', UZB), row('762', 'Tajikistan', TJK), row('417', 'Kyrgyzstan', KGZ),
  {id:'398_T', n:'Kazakhstan: Isbījāb (the Turkistan and Zhambyl regions) and the Mawarāʾ al-Nahr and Khwārazm edges of the author’s maps', km2:kazKm, pct:Math.round(1000*kazKm/area(KAZ))/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.transoxTraced = 'Version 75: all of Uzbekistan, Tajikistan and Kyrgyzstan, with Mawarāʾ al-Nahr and Khwārazm as drawn on the author’s maps (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '| Kazakhstan part', kazKm, '| V3', C.xw.km2, 'V4', C.me2.km2, '| holes', X.reduce((t, p) => t + p.length - 1, 0));
