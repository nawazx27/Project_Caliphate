/* Version 70 (2026-10-11, Nawaz: "The v4 should include the river nile (encompassing it end to end)"; asked how far upstream, he chose
   Uganda, Rwanda, Burundi, Kenya and Tanzania, all whole, so that the White Nile from its farthest headstream (the Kagera, in Rwanda
   and Burundi) and Lake Victoria lie inside; and the same lands for V3, V5, V6 and V7, so that each larger version still holds V4).
   The Blue Nile (Ethiopia) and the rest of the river (South Sudan, Sudan, Egypt) were already inside. Run once: node tools/add_nile_lands.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.nileLands){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const LANDS = [['800','Uganda'], ['834','Tanzania'], ['404','Kenya'], ['108','Burundi'], ['646','Rwanda']];
const shape = {}, km = {};
LANDS.forEach(([id]) => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); if(!g) throw new Error('no country ' + id); shape[id] = R3mp(asMp(topojson.feature(geo, g).geometry)); km[id] = area(shape[id]); });
const NEW = LANDS.map(([id]) => shape[id]);
const report = [];
for(const k of ['x', 'xw', 'x3', 'v2', 'g']){
  const V = C[k], before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = R3mp(pc.union(R3mp(V.polys), ...NEW));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]);
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  const extra = k === 'v2' ? {core:true} : k === 'g' ? {core:true, afr:false, hist:false} : {};
  V.states = V.states.filter(s => !LANDS.some(([id]) => s.id === id));
  LANDS.forEach(([id, n]) => V.states.push({id, n, km2:km[id], pct:100, ...extra}));
  V.states.sort((a, b) => (k === 'v2' || k === 'g' ? (b.core === true) - (a.core === true) : 0) || b.km2 - a.km2);
  report.push(`${k} +${gain} -> ${V.km2}`);
}
/* the regional index (Greater Caliphate data): Uganda leaves the Libya-Tunisia-Greece card; the five lands get a core card of their own */
const R = C.g.regions, mh = R.find(r => r.id === 'misrheld');
mh.en = 'all of Tunisia, Libya and Greece'; mh.ids = mh.ids.filter(id => id !== '800'); mh.states = mh.states.filter(s => !/Uganda/.test(s.n)); mh.km2 = mh.states.reduce((t, s) => t + s.km2, 0);
const nb = d3.geoBounds({type:'FeatureCollection', features: NEW.map(mp => ({type:'Feature', geometry:{type:'MultiPolygon', coordinates:mp}}))});
R.splice(R.indexOf(mh) + 1, 0, {id:'nilesrc', n:'The Nile’s sources', ar:'منابع النيل', en:'all of Uganda, Kenya, Tanzania, Rwanda and Burundi, round Lake Victoria: added so the whole Nile lies inside', b:[[R3(nb[0][0]), R3(nb[0][1])], [R3(nb[1][0]), R3(nb[1][1])]], ids: LANDS.map(([id]) => id), states: LANDS.map(([id, n]) => ({n, km2:km[id], pct:100})), km2: LANDS.reduce((t, [id]) => t + km[id], 0)});
C.nileLands = 'Version 70: Uganda, Rwanda, Burundi, Kenya and Tanzania, whole, in V3, V4, V5, V6 and V7, so the whole Nile and Lake Victoria lie inside (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log(report.join(' | ')); console.log('lands', JSON.stringify(km));
