/* Version 76 (2026-10-11, Nawaz: "The border of Mawarāʾ al-Nahr should look like this", with the same pictures; asked, he chose
   "Red line + Shāsh and Isbījāb" and to keep the Ustyurt plateau and western Turkmenistan).
   V3 (CALIPH.x, the Complete outline), Central Asia:
   - Uzbekistan and Turkmenistan stay whole (the Ustyurt plateau and the Caspian side of Turkmenistan are outside every red outline, kept);
   - Tajikistan, Kyrgyzstan and Kazakhstan only inside the red Mawarāʾ al-Nahr line of reference/mawarannahr_khwarazm_khorasan.jpg
     (tools/data/mawarannahr_trace2.json), so eastern Kyrgyzstan (Issyk-Kul, Naryn), the Pamirs and the Kazakh steppe come out;
   - plus Shāsh (Uzbekistan's Tashkent region, inside Uzbekistan anyway) and the land around Isbījāb (Sayram) and Ṭarāz named on
     reference/transoxiana_places.webp: the hull of 50 km around Isbījāb and Ṭarāz and 30 km around Tashkent, in Kazakhstan.
   Thin slivers left between the red line and land already inside (the Panj and Syr Darya banks) are filled.
   Run: node tools/v3_mawarannahr_redline.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const T2 = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/mawarannahr_trace2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const UZB = country('860'), TJK = country('762'), KGZ = country('417'), KAZ = country('398');
const CA = R3mp(pc.union(UZB, TJK, KGZ, KAZ));
const RED = R3mp([[T2.mawarannahr_img2]]);
/* Isbījāb and Ṭarāz: the convex hull of small discs round them and Tashkent */
const disc = (c, km) => d3.geoCircle().center(c).radius(km/111.32).precision(5)().coordinates[0];
const pts = [...disc([69.76, 42.30], 50), ...disc([71.37, 42.90], 50), ...disc([69.28, 41.31], 30)];
const hull = d3.polygonHull(pts); hull.push(hull[0]);
const ISB = R3mp([[hull.reverse()]]);
const OTHER = R3mp(pc.intersection(R3mp(pc.union(TJK, KGZ, KAZ)), R3mp(pc.union(RED, ISB))));
const base = R3mp(pc.difference(R3mp(C.x.polys), CA));
let X = R3mp(pc.union(base, UZB, OTHER));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
/* slivers: small pieces of Tajikistan/Kyrgyzstan/Kazakhstan outside, nearly surrounded by V3 */
const out = R3mp(pc.difference(R3mp(pc.union(TJK, KGZ, KAZ)), X));
const near = q => X.some(xp => [[0.03,0],[-0.03,0],[0,0.03],[0,-0.03]].some(([dx,dy]) => d3.polygonContains(xp[0], [q[0]+dx, q[1]+dy])));
const wedge = out.filter(p => ringSr(p[0])*KM < 6000 && p[0].filter(near).length / p[0].length > 0.8);
if(wedge.length) X = R3mp(pc.union(X, wedge));
X = X.filter(p => ringSr(p[0])*KM >= 1);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
const before = C.x.km2; C.x.polys = X; C.x.km2 = area(X);
const tj = kmIn(TJK), kg = kmIn(KGZ), kz = kmIn(KAZ);
C.x.states = C.x.states.filter(s => !['860','762','417','398_T','762_T','417_T','860_T','398_S'].includes(s.id));
C.x.states.push({id:'860', n:'Uzbekistan', km2:area(UZB), pct:100},
  {id:'762_T', n:'Tajikistan: Mawarāʾ al-Nahr as drawn on the author’s map (without the eastern Pamirs)', km2:tj, pct:Math.round(1000*tj/area(TJK))/10},
  {id:'417_T', n:'Kyrgyzstan: Mawarāʾ al-Nahr as drawn on the author’s map (Farghāna and the west; without Issyk-Kul and Naryn)', km2:kg, pct:Math.round(1000*kg/area(KGZ))/10},
  {id:'398_T', n:'Kazakhstan: Mawarāʾ al-Nahr as drawn on the author’s map, with the land round Isbījāb and Ṭarāz', km2:kz, pct:Math.round(1000*kz/area(KAZ))/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.transoxTraced = 'Version 76: Mawarāʾ al-Nahr as the red line of the author’s map, with Shāsh and Isbījāb; Uzbekistan and Turkmenistan whole (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V3', before, '->', C.x.km2, '| TJK', tj, 'KGZ', kg, 'KAZ', kz, '| wedges', wedge.length, Math.round(wedge.reduce((t,p)=>t+ringSr(p[0])*KM,0)), '| V2', C.xw.km2, 'V4', C.me2.km2);
