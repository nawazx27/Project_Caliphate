/* Version 68 (2026-10-11, Nawaz's request: "Add Western Sahara, Morocco, Algeria, Tunisia, Afghanistan and Pakistan to a new version
   which is building upon V1"). The new version (internal key me2) is V1 with those six lands, each whole, from the base map's own
   countries (Morocco there includes the part of Western Sahara it holds; the rest of Western Sahara is its own shape). It is
   about 13.3 million km², between V1 and the old V2, so by Nawaz's rule (numbered by size) it becomes V2 and the larger versions move up one.
   Run after tools/add_v1_middle_east.js: node tools/add_v2_maghrib_afpak.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const ADD = ['504','732','012','788','004','586'];   /* Morocco (with the part of Western Sahara it holds), the rest of Western Sahara, Algeria, Tunisia, Afghanistan, Pakistan */
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const geoms = ADD.map(id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); if(!g) throw new Error('no country ' + id); return R3mp(asMp(topojson.feature(geo, g).geometry)); });
let X = R3mp(pc.union(R3mp(C.me.polys), ...geoms));
X = X.filter(p => ringSr(p[0])*KM >= 1).map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 50)]);
/* the table rows are the ones the other versions use: Algeria, Tunisia, Afghanistan and Pakistan from V5 (old Complete V3);
   Morocco and the two parts of Western Sahara from V6 (old Complete V2), which split them the same way */
const row = (list, id) => { const s = list.find(s => s.id === id); if(!s) throw new Error('no row ' + id); const {core, hs, ...r} = s; return r; };
const states = C.me.states.map(s => ({...s})).concat(['012','788','004','586'].map(id => row(C.x3.states, id)), ['504','504_W','732'].map(id => row(C.v2.states, id)))
  .map(s => s.id === '732' ? {...s, n:'Western Sahara, the rest'} : s).sort((a, b) => b.km2 - a.km2);
C.me2 = {polys: X, km2: area(X), states, ref:'Version 68: V1 with Morocco, Western Sahara, Algeria, Tunisia, Afghanistan and Pakistan, whole (Nawaz)'};
fs.writeFileSync(F, JSON.stringify(C));
console.log('new V2', C.me2.km2, 'km² (rows', states.reduce((t, s) => t + s.km2, 0), ') states', states.length, '| pieces', X.length, 'holes', X.reduce((t, p) => t + p.length - 1, 0), '| old V2 (west)', C.xw.km2);
