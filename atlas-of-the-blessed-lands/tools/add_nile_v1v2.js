/* Version 71 (2026-10-11, Nawaz, with a hadith: "Sayḥān, Jayḥān, the Euphrates and the Nile are all among the rivers of Paradise"
   (Muslim 2839): "Include these rivers end to end"). Sayḥān and Jayḥān (Seyhan and Ceyhan, in Türkiye) and the Euphrates (Türkiye,
   Syria, Iraq) were already wholly inside every version, and the Nile inside V3–V7 (Version 70). V1 and V2 held only the Egyptian Nile:
   they take in Sudan, Bir Tawil, South Sudan, Ethiopia (the Blue Nile) and the five lands of the White Nile's sources (Uganda, Kenya,
   Tanzania, Rwanda, Burundi), all whole, as in V4. Nawaz chose to renumber by size afterwards. Run once: node tools/add_nile_v1v2.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.me.nile){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const IDS = ['729','BRT','728','231','800','834','404','108','646'];
const NEW = IDS.map(id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); if(!g) throw new Error('no country ' + id); return R3mp(asMp(topojson.feature(geo, g).geometry)); });
/* the table rows as V4 has them (Sudan, South Sudan, Ethiopia, Bir Tawil from V5, which lists them the same way) */
const rows = IDS.map(id => { const s = C.x.states.find(s => s.id === id) || C.x3.states.find(s => s.id === id); if(!s) throw new Error('no row ' + id); return {...s}; });
const report = [];
for(const k of ['me', 'me2']){
  const V = C[k], before = area(V.polys);
  let X = R3mp(pc.union(R3mp(V.polys), ...NEW));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);   /* V1 and V2 had no holes of their own: drop slivers only */
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  V.states = V.states.concat(rows.map(r => ({...r}))).sort((a, b) => b.km2 - a.km2);
  V.nile = 'Version 71: the whole Nile (Sudan, Bir Tawil, South Sudan, Ethiopia, Uganda, Kenya, Tanzania, Rwanda, Burundi) (Nawaz)';
  report.push(`${k} +${gain} -> ${V.km2} (${V.states.length} rows, holes ${X.reduce((t, p) => t + p.length - 1, 0)})`);
}
fs.writeFileSync(F, JSON.stringify(C));
console.log(report.join(' | '), '| V3(west)', C.xw.km2, 'V4(full)', C.x.km2, 'V5(x3)', C.x3.km2);
