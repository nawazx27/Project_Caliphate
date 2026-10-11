/* Version 83 (2026-10-11, Nawaz: "remove transoxiana and leave greater khorasan in from v2"; his answers: remove Khwārazm too, keep the
   rest of Turkmenistan).
   V2 (the Complete outline, CALIPH.x) drops Mawarāʾ al-Nahr and Khwārazm:
   - Uzbekistan, Tajikistan, Kyrgyzstan and the Kazakh part (Versions 72–80), and the strip in China (Version 80);
   - in Turkmenistan, the parts inside the traced Khwārazm and Transoxiana outlines (Dashoguz, and the Amu Darya's right bank).
   It keeps Greater Khorasan whole as the author's map draws it (tools/data/transoxiana_trace.json, 'khorasan'), with the bits of it that
   lie in Tajikistan and Uzbekistan south of the river and its Caspian water, and the rest of Turkmenistan (Karakum, the Caspian side).
   Run: node tools/v2_khorasan_only.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const D = n => JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data', n + '.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const T1 = D('transoxiana_trace'), T2 = D('mawarannahr_trace2'), T3 = D('transoxiana_locator_trace');
const KHOR = R3mp([[T1.khorasan]]);
const TKM = country('795'), UZB = country('860'), TJK = country('762'), KGZ = country('417'), KAZ = country('398'), CHN = country('156');
/* Turkmenistan's share of the traced Transoxiana and Khwārazm outlines */
const BEYOND = R3mp(pc.union(...[T1.khwarazm, T1.transoxiana, T1.merged, T2.mawarannahr_img2, T3.transoxiana_locator].map(t => R3mp([[t]]))));
const TKM_OUT = R3mp(pc.intersection(TKM, BEYOND));
const CUT = R3mp(pc.union(UZB, TJK, KGZ, KAZ, R3mp(pc.intersection(CHN, R3mp(C.x.polys))), TKM_OUT));
const before = C.x.km2;
let X = R3mp(pc.difference(R3mp(C.x.polys), CUT));
X = R3mp(pc.union(X, KHOR));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
const tkm = kmIn(TKM), tjk = kmIn(TJK), uzb = kmIn(UZB), tkmAll = area(TKM);
C.x.states = C.x.states.filter(s => !['860', '762', '417', '398_T', '156_T', '795'].includes(s.id));
C.x.states.push({id:'795', n:'Turkmenistan: all but Khwārazm (Dashoguz) and the Amu Darya’s right bank', km2:tkm, pct:Math.round(1000*tkm/tkmAll)/10});
if (tjk) C.x.states.push({id:'762_K', n:'Tajikistan: the strip of Greater Khorasan as the author’s map draws it, by the Panj', km2:tjk, pct:Math.round(1000*tjk/area(TJK))/10});
if (uzb) C.x.states.push({id:'860_K', n:'Uzbekistan: the edge of Greater Khorasan as the author’s map draws it', km2:uzb, pct:Math.round(1000*uzb/area(UZB))/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
['transoxTraced', 'tjkKgzWhole', 'locator', 'syrdarya', 'everything'].forEach(k => delete C.x[k]);
C.x.khorasanOnly = 'Version 83: Transoxiana and Khwārazm removed, Greater Khorasan kept (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '| Turkmenistan', tkm, 'of', tkmAll, '(cut', area(TKM_OUT), ') | Tajikistan', tjk, '| Uzbekistan', uzb,
  '| Khorasan outside V2', area(R3mp(pc.difference(KHOR, X))), '| KAZ/KGZ left', kmIn(KAZ), kmIn(KGZ), '| China', kmIn(CHN));
