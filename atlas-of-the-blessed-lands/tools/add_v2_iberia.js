/* Version 42 (2026-10-07, Nawaz's request): Complete V2 also takes in Spain and Portugal (whole) and the islands of Corsica and Sardinia.
   Run once: node tools/add_v2_iberia.js   (it refuses to run twice) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.v2.iberia){ console.log('already added'); process.exit(0); }
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * 6371.0088**2);
const R3 = v => Math.round(v*1000)/1000;
const mpOf = id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); const f = topojson.feature(geo, g).geometry; return f.type === 'Polygon' ? [f.coordinates] : f.coordinates; };
const inBox = (p, b) => p[0].every(q => q[0] >= b[0] && q[0] <= b[2] && q[1] >= b[1] && q[1] <= b[3]);
const spain = mpOf('724'), portugal = mpOf('620');
const corsica = mpOf('FRA').filter(p => inBox(p, [8.4, 41.3, 9.7, 43.1]));
const sardinia = mpOf('380').filter(p => inBox(p, [8.0, 38.8, 10.0, 41.35]));
const add = [['724','Spain',spain,'with the Balearics, the Canary Islands, Ceuta and Melilla'],['620','Portugal',portugal,'with Madeira and the Azores'],['FRA','France',corsica,'Corsica only'],['380','Italy',sardinia,'Sardinia and its islets only']];
const before = area(C.v2.polys);
C.v2.polys = pc.union(C.v2.polys, ...add.map(a => a[2])).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const gain = area(C.v2.polys) - before;
C.v2.km2 += gain;
const tot = id => area(mpOf(id));
add.forEach(([id, n, mp, flag]) => { const a = area(mp); C.v2.states.push({id, n, km2:a, pct: Math.max(1, Math.round(100*a/tot(id))), core:false, flag, iberia:true}); console.log(n, a, 'km²'); });
C.v2.states.sort((a, b) => (b.core === true) - (a.core === true) || b.km2 - a.km2);
const GK = ' (From general knowledge; not checked against the sources used for the other lands.)';
C.v2.countries.push(
  {a3:'ESP', n:'Spain', summary:'Al-Andalus. Conquered from 711 and ruled by governors of the Umayyad caliphate until 750; then the Umayyad emirate of Córdoba (from 756), which became a caliphate in its own right in 929 and lasted to 1031. After the taifa kingdoms, the Almoravids (who recognised the Abbasid caliph) and the Almohads (a caliphate) ruled the south and centre into the 13th century; the Nasrid kingdom of Granada lasted until 1492. The far north (Asturias, the Basque country, the Pyrenees) was held briefly or not at all.' + GK},
  {a3:'PRT', n:'Portugal', summary:'The west of al-Andalus (Gharb al-Andalus). The south and centre were held from 711–716 under the Umayyads and then Córdoba, the taifas, the Almoravids and the Almohads, until Lisbon fell in 1147 and the Algarve in 1249; the far north was held only briefly. Madeira and the Azores were uninhabited until the Portuguese.' + GK},
  {a3:'COR', n:'Corsica (France)', summary:'Raided repeatedly by Muslim fleets from the 8th to the 10th century; as far as I know no caliphate held it for any length of time.' + GK},
  {a3:'SAR', n:'Sardinia (Italy)', summary:'Raided from the early 8th century; Mujahid, ruler of the taifa of Dénia (not a caliphate), occupied part of the south briefly in 1015–16 before being driven out. No lasting caliphal rule.' + GK});
C.v2.iberia = 'Version 42: Spain and Portugal whole, Corsica and Sardinia';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2 gained', gain, 'km²; now', C.v2.km2);
