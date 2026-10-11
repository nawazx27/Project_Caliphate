/* Version 84 (2026-10-11, Nawaz: "just keep Pakistan, Afghanistan and Turkmenistan with modern borders as whole and remove everything
   from that side for now").
   V2 (CALIPH.x) on its north-east side is now Iran, Turkmenistan, Afghanistan and Pakistan, each whole by today's borders, and nothing
   beyond them: the traced Greater Khorasan's strip in Tajikistan and sliver in Uzbekistan, and its Caspian water (Versions 82–83), come
   out; Turkmenistan's Khwārazm (Dashoguz) and the Amu Darya's right bank go back in. V5, V6 and V7 are unchanged.
   Run: node tools/v2_three_whole.js */
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
const IRN = country('364'), TKM = country('795'), AFG = country('004'), PAK = country('586');
const KEEP = R3mp(pc.union(IRN, TKM, AFG, PAK));
/* the Khorasan outline's parts beyond those four lands: Tajikistan, Uzbekistan and the Caspian */
const BEYOND = R3mp(pc.difference(R3mp([[KH]]), KEEP));
const before = C.x.km2;
let X = R3mp(pc.difference(R3mp(C.x.polys), BEYOND));
X = R3mp(pc.union(X, TKM, AFG, PAK));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
C.x.states = C.x.states.filter(s => !['762_K', '860_K', 'CAS_K', '795'].includes(s.id));
C.x.states.push({id:'795', n:'Turkmenistan', km2:area(TKM), pct:100});
C.x.states.sort((a, b) => b.km2 - a.km2);
delete C.x.khorasanCaspian; delete C.x.khorasanOnly;
C.x.threeWhole = 'Version 84: Turkmenistan, Afghanistan and Pakistan whole, nothing beyond them (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '| removed beyond', area(BEYOND), '| Turkmenistan', area(TKM));
