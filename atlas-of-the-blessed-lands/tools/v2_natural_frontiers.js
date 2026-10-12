/* Version 92 (2026-10-12, Nawaz: "Strengthen the borders around v2 by making them optimal"; he chose natural frontiers, and all three
   of the stretches offered). Where V2's edge crossed open land, it is moved out to the nearest strong natural barrier (my synthesis;
   land is only added):
   - Punjab: today's Pakistan–India border crosses the open plain; the new line follows the Beas and then the Sutlej (river lines from
     rivers.geojson, Natural Earth), with the Ravi and the Shivalik foothills (Madhopur to the Beas) on the north: India's land west of
     the Beas–Sutlej (Amritsar, Tarn Taran, Gurdaspur);
   - Fergana: Kyrgyzstan's Osh and Jalal-Abad regions whole (admin1_used.geojson), so the edge runs on the Chatkal, Fergana and Alay ranges;
   - southern Kazakhstan: the Turkistan region (South Kazakhstan in admin1_used.geojson) whole, to the Karatau range and the Moyynkum
     and Kyzylkum sands.
   Run: node tools/v2_natural_frontiers.js */
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
const RIV = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features;
const riv = n => RIV.filter(f => f.properties.name === n).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
/* Punjab: Madhopur on the Ravi → the Beas where it leaves the hills → down the Beas → the Sutlej below the confluence → back up the Ravi */
const beas = riv('Beas').find(l => l[0][0] > 75.9 && l[0][0] < 75.95), sut = riv('Sutlej').find(l => l.length > 300), ravi = riv('Ravi').find(l => l[0][0] > 76.8);
const sutD = sut.filter(p => p[0] <= 75.0 && p[0] >= 73.6), raviU = ravi.filter(p => p[0] <= 75.62);
const ring = [[75.6, 32.37], [75.93, 31.96], ...beas, ...sutD, [73.5, sutD[sutD.length - 1][1]], [73.5, 31.5], ...raviU.slice().reverse(), [75.6, 32.37]];
const IND = country('356');
const PUNJAB = R3mp(pc.intersection(R3mp([[ring]]), IND));
/* provinces taken whole */
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const prov = (c, n) => R3mp(asMp(A1.find(f => f.properties.adm0_a3 === c && f.properties.name === n).geometry));
const FERGANA = R3mp(pc.union(prov('KGZ', 'Osh'), prov('KGZ', 'Jalal-Abad')));
const TURKISTAN = prov('KAZ', 'South Kazakhstan');
const before = C.x.km2, X0 = R3mp(C.x.polys);
const gain = mp => area(R3mp(pc.difference(mp, X0)));
const g = {punjab:gain(PUNJAB), fergana:gain(FERGANA), turkistan:gain(TURKISTAN)};
let X = R3mp(pc.union(X0, PUNJAB, FERGANA, TURKISTAN));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
const KGZ = country('417'), KAZ = country('398');
const upd = (id, n, c) => { const i = kmIn(c), a = area(c); C.x.states = C.x.states.filter(s => s.id !== id); C.x.states.push({id, n, km2:i, pct:Math.round(1000*i/a)/10}); };
upd('417_K', 'Kyrgyzstan: the Fergana valley to its mountain crests (Batken, Osh and Jalal-Abad regions) and the Khurāsān maps’ edge', KGZ);
upd('398_K', 'Kazakhstan: the Turkistan region, to the Karatau range and the Moyynkum and Kyzylkum sands, with the Khurāsān maps’ edge', KAZ);
const pj = kmIn(IND);
C.x.states = C.x.states.filter(s => s.id !== '356_P');
C.x.states.push({id:'356_P', n:'India: Punjab west of the Beas and Sutlej (Amritsar, Tarn Taran, Gurdaspur)', km2:pj, pct:Math.round(10000*pj/area(IND))/100});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.naturalFrontiers = 'Version 92: the Punjab, Fergana and Turkistan frontiers moved out to natural barriers (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '(+', C.x.km2 - before, ')', JSON.stringify(g), '| India in V2', pj, '| V3', C.xw.km2);
