/* Version 46 (2026-10-09, Nawaz's request): Turkmenistan, Afghanistan and Pakistan, whole, join the Complete outline (CALIPH.x).
   Pakistan is taken as the base map draws it, with Azad Kashmir and Gilgit-Baltistan (the Siachen Glacier, 'KAS', stays out), as in Maximum.
   The other versions keep their land; only their notes change: the three now count as core in Greater, V2 and Maximum.
   Not in the To-Iraq version (it stops at Iraq's eastern border). Not clipped to the natural ring: a strip of Turkmenistan on the
   Amu Darya's right bank (about 17,500 km²) lies outside it. Run once: node tools/add_core_east.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreEast){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const mpOf = id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); const f = topojson.feature(geo, g).geometry; return f.type === 'Polygon' ? [f.coordinates] : f.coordinates; };
const ADD = [{id:'795', n:'Turkmenistan'}, {id:'004', n:'Afghanistan'}, {id:'586', n:'Pakistan', flag:'with Azad Kashmir and Gilgit-Baltistan'}];

/* the outline: union, then fill the hairline gaps left where the simplified core edge (Iran) meets the new countries' borders */
const holesBefore = C.x.polys.reduce((t, p) => t + p.length - 1, 0), before = area(C.x.polys);
let X = pc.union(R3mp(C.x.polys), ...ADD.map(a => R3mp(mpOf(a.id)))).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const oldHoles = C.x.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let filled = 0, filledKm = 0;
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
  const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
  if(!old && a < 5000){ filled++; filledKm += a; return false; } return true; })]);
const gain = area(X) - before;
C.x.polys = X; C.x.km2 += gain;
ADD.forEach(a => C.x.states.push({id:a.id, n:a.n, km2:area(mpOf(a.id)), pct:100, ...(a.flag ? {flag:a.flag} : {})}));
C.x.states.sort((a, b) => b.km2 - a.km2);
console.log('Complete: +', gain, 'km² ->', C.x.km2, '|', C.x.states.length, 'states | holes before', holesBefore, 'after', X.reduce((t, p) => t + p.length - 1, 0), '| new gaps filled', filled, Math.round(filledKm), 'km²');

/* the other versions: same land, but the three are core now */
const ids = new Set(ADD.map(a => a.id));
for(const k of ['g', 'v2', 'm']) C[k].states.forEach(s => { if(ids.has(String(s.id))){ s.core = true; if(k === 'm') delete s.add; } });
C.g.states.forEach(s => { if(ids.has(String(s.id))){ s.afr = false; s.hist = false; } });
/* regional cards of the Greater Caliphate: Afghanistan and Pakistan, with Turkmenistan, become a core card; Central Asia keeps the rest */
const R = C.g.regions, ca = R.find(r => r.id === 'centralasia'), kh = R.find(r => r.id === 'khurasan');
const tkm = ca.states.find(s => s.n === 'Turkmenistan');
ca.ids = ca.ids.filter(id => id !== '795'); ca.states = ca.states.filter(s => s !== tkm); ca.km2 -= tkm.km2;
ca.en = 'Central Asia (Turkmenistan is now in the core)';
delete kh.ring; kh.n = 'Khurāsān · Khwārazm · al-Sind'; kh.ar = 'خراسان وخوارزم والسند';
kh.en = 'Turkmenistan, Afghanistan and Pakistan · added at your request';
kh.ids = ['795'].concat(kh.ids); kh.states = [tkm].concat(kh.states); kh.km2 += tkm.km2;
kh.b = [[52.4,23.5],[77.9,42.8]];
R.splice(R.indexOf(kh), 1); R.splice(R.indexOf(R.find(r => r.id === 'qabq')) + 1, 0, kh);   /* after the other core cards */
C.coreEast = 'Version 46: Turkmenistan, Afghanistan and Pakistan in the complete version';
fs.writeFileSync(F, JSON.stringify(C));
console.log('written');
