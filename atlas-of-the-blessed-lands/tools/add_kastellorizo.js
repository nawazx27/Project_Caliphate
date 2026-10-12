/* Version 100: adds Kastellorizo (Megisti), Ro, Strongyli and the Psomi islet (tools/data/kastellorizo.geojson, from
   tools/kastellorizo.py) to every version that holds Greece whole, and stores them as CALIPH.extraLand so the page draws them as land
   (the base map, Natural Earth, has no land there). Run: node tools/add_kastellorizo.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM;
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const K = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/kastellorizo.geojson'))).features;
/* the islands at 0.001° (about 100 m); Psomi, about 60 m across, is kept as a 0.002° square round its point so it is not rounded away */
const isles = R3mp(pc.union(...K.map(f => f.properties.name === 'Psomi' ? [[[[29.608, 36.153], [29.610, 36.153], [29.610, 36.155], [29.608, 36.155], [29.608, 36.153]]]] : R3mp(asMp(f.geometry)))));
C.extraLand = {n:'Kastellorizo (Megisti), Ro, Strongyli and Psomi, traced (tools/kastellorizo.py)', polys:isles, km2:Math.round(area(isles)*100)/100};
for (const k of ['me', 'x', 'xn', 'xw', 'me2', 'x3', 'v2', 'g']) {
  const V = C[k]; if (!V || !V.states.some(s => s.id === '300' && s.pct >= 99.5)) continue;
  const before = V.km2;
  V.polys = R3mp(pc.union(R3mp(V.polys), isles)); V.km2 = Math.round(area(V.polys));
  V.states = V.states.filter(s => s.id !== '300_K');
  V.states.push({id:'300_K', n:'Greece: Kastellorizo (Megisti), Ro, Strongyli and Psomi (not drawn by the base map; traced)', km2:Math.round(area(isles)), pct:100});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2);
}
console.log('islands', C.extraLand.km2, 'km²');
fs.writeFileSync(F, JSON.stringify(C));
