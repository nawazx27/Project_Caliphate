/* Version 85 (2026-10-11, Nawaz: "Include greater khorasan without deducting any land and find out the actual size of it and implement";
   his answer: the strict sense, to the Oxus).
   Research (search summaries; see notes.md): in the strict sense Khurāsān ran to the Amu Darya (Oxus), from the edge of the Dasht-e Kavir
   (with Gurgān and Qūmis on the border with the Jibāl) to the Hindu Kush and the Pamirs, in four quarters round Nīshāpūr, Marw, Harāt and
   Balkh; the looser usage took in most of Transoxiana too (Encyclopaedia Iranica, "Khorasan"; Wikipedia, "Greater Khorasan"/"Khorasan").
   V2 keeps Iran, Turkmenistan, Afghanistan and Pakistan whole (Version 84) and adds the whole traced Greater Khorasan outline of the
   author's map (tools/data/transoxiana_trace.json, 'khorasan', about 1.16 million km²) with nothing cut: its strip in Tajikistan
   (Badakhshan, by the Panj), its sliver in Uzbekistan and its south-east Caspian water. Run: node tools/v2_khorasan_strict.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KH = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/transoxiana_trace.json'))).khorasan;
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const T = R3mp([[KH]]);
const byC = {}; for (const [id, nm] of [['364', 'Iran'], ['795', 'Turkmenistan'], ['004', 'Afghanistan'], ['762', 'Tajikistan'], ['860', 'Uzbekistan'], ['586', 'Pakistan']])
  byC[nm] = area(R3mp(pc.intersection(T, country(id))));
const land = Object.values(byC).reduce((a, b) => a + b, 0);
const before = C.x.km2;
let X = R3mp(pc.union(R3mp(C.x.polys), T));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
const tjk = byC.Tajikistan, uzb = byC.Uzbekistan, water = area(T) - land;
C.x.states = C.x.states.filter(s => !['762_K', '860_K', 'CAS_K'].includes(s.id));
C.x.states.push({id:'762_K', n:'Tajikistan: the strip of Greater Khurāsān in Badakhshan, by the Panj, as the author’s map draws it', km2:tjk, pct:Math.round(1000*tjk/area(country('762')))/10});
C.x.states.push({id:'860_K', n:'Uzbekistan: the edge of Greater Khurāsān as the author’s map draws it', km2:uzb, pct:Math.round(1000*uzb/area(country('860')))/10});
C.x.states.push({id:'CAS_K', n:'Caspian Sea: the Khurāsān shore (Gorgan Bay and the Turkmen coast), as the author’s Khurāsān map draws it (water)', km2:water, pct:null});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.khorasanStrict = 'Version 85: Greater Khurāsān in the strict sense, whole as traced, on top of Iran, Turkmenistan, Afghanistan and Pakistan (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Khurasan traced', area(T), 'land', land, JSON.stringify(byC), 'water', water, '| V2', before, '->', C.x.km2, '| outside V2', area(R3mp(pc.difference(T, X))));
