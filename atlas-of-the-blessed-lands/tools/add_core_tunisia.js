/* Version 48 (2026-10-09, Nawaz's request): Tunisia, whole, joins the Complete outline (CALIPH.x) and, since it lies west of Iraq,
   the version to Iraq's border (CALIPH.xw), as Libya and Greece did. The other versions keep their land; Tunisia now counts as core
   in Greater, V2 and Maximum. Tunisia lies wholly inside the natural ring. Run once: node tools/add_core_tunisia.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreTunisia){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const mpOf = id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); const f = topojson.feature(geo, g).geometry; return f.type === 'Polygon' ? [f.coordinates] : f.coordinates; };
const TUN = {id:'788', n:'Tunisia'};

/* union, then fill the hairline gaps left where the simplified edge (Libya) meets Tunisia's border; holes that were there before stay */
function addTo(V){
  const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = pc.union(R3mp(V.polys), R3mp(mpOf(TUN.id))).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  let filled = 0, filledKm = 0;
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
    const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
    if(!old && a < 5000){ filled++; filledKm += a; return false; } return true; })]);
  const gain = area(X) - before;
  V.polys = X; V.km2 += gain;
  V.states.push({id:TUN.id, n:TUN.n, km2:area(mpOf(TUN.id)), pct:100});
  V.states.sort((a, b) => b.km2 - a.km2);
  return `+ ${gain} km² -> ${V.km2} | ${V.states.length} states | gaps filled ${filled} (${Math.round(filledKm)} km²)`;
}
console.log('Complete:', addTo(C.x));
console.log('To Iraq:', addTo(C.xw));

/* the other versions: same land, Tunisia is core now */
for(const k of ['g', 'v2', 'm']) C[k].states.forEach(s => { if(String(s.id) === TUN.id){ s.core = true; if(k === 'm') delete s.add; if(k === 'g'){ s.afr = false; s.hist = false; } } });
/* regional cards of the Greater Caliphate: Tunisia leaves the Maghrib card for the core card with Libya and Greece */
const R = C.g.regions, mg = R.find(r => r.id === 'maghrib'), mh = R.find(r => r.id === 'misrheld');
const tun = mg.states.find(s => s.n === 'Tunisia');
mg.ids = mg.ids.filter(id => id !== TUN.id); mg.states = mg.states.filter(s => s !== tun); mg.km2 -= tun.km2;
mg.en = 'North Africa (Libya and Tunisia are now in the core)';
mh.n = 'Ifrīqiya · Barqah · Ṭarābulus · al-Yūnān'; mh.ar = 'إفريقية وبرقة وطرابلس واليونان';
mh.en = 'all of Tunisia, Libya and Greece, with northern Uganda (Equatoria) · added at your request';
mh.ids = [TUN.id].concat(mh.ids); mh.states = [tun].concat(mh.states); mh.km2 += tun.km2;
mh.b = [[7.5,0.0],[33.5,42.0]];
C.coreTunisia = 'Version 48: Tunisia in the complete version and the version to Iraq’s border';
fs.writeFileSync(F, JSON.stringify(C));
console.log('written');
