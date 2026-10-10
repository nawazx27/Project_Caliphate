/* Version 51 (2026-10-10, Nawaz's brief "Missing Rashidun Caliphate Territories", and "make sure all the lands that were ruled at the time
   of the Rashidun Caliphate are included" in the Complete outline). Checked first against the outline (see notes.md): of the Rashidun-held
   places tested, only Derbent was outside; Cyprus was inside but its coast was simplified; Arwad is not in the base map (too small).
   - Cyprus: the base map's exact island (Cyprus, N. Cyprus, the U.N. buffer zone, Dhekelia, Akrotiri) is unioned into every version that
     holds it (Complete, To Iraq, Greater, V2, Maximum), so the whole island is shaded to the coast.
   - Derbent (Bāb al-Abwāb): the same traced area the Greater Caliphate uses (caliph_gen.js, HIST 'derbent'), cut to Russia, joins Complete
     and V2 (Greater and Maximum hold it already; To Iraq leaves out the Caucasus).
   - Arwad: a marker in the page (eng_c.js), since there is no island shape to shade.
   Run once: node tools/add_core_rashidun.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreRashidun){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const mpOf = id => asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry);
const closed = pts => { const o = pts.slice(); if(o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1]) o.push(o[0]); return o; };

const CYPRUS = R3mp(pc.union(...['196','CYN','CNM','ESB','WSB'].map(mpOf)));
/* the Derbent area as caliph_gen.js draws it for the Greater Caliphate (north edge 47.2,42.6 – 47.9,43.0), widened south-west down to the
   Russia–Azerbaijan border so the strip of southern Dagestan between them (the Samur valley) is not left as a gap: one corridor along the coast.
   The widening is my drawing, not from the sources. */
const DERBENT = R3mp(pc.intersection([[closed([[48.75,41.85],[48.35,42.6],[47.9,43.0],[47.2,42.6],[46.55,41.95],[46.5,41.0],[48.9,41.0]])]], mpOf('643')));
const derbentKm = area(DERBENT);

function grow(V, add, label){
  const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = pc.union(R3mp(V.polys), add).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  let filled = 0, fk = 0;
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
    const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
    if(!old && a < 5000){ filled++; fk += a; return false; } return true; })]);
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  console.log(label.padEnd(9), '+', gain, 'km² ->', V.km2, '| gaps filled', filled, Math.round(fk), 'km²');
}
for(const k of ['x', 'xw', 'g', 'v2', 'm']) grow(C[k], CYPRUS, k + ' Cyprus');
grow(C.x, DERBENT, 'x Derbent'); grow(C.v2, DERBENT, 'v2 Derbent');
const row = {id:'643', n:'Russia: Derbent (Bāb al-Abwāb) and the Samur valley', km2:derbentKm, pct:0.1};
C.x.states.push({...row}); C.x.states.sort((a,b) => b.km2 - a.km2);
C.v2.states.push({...row, id:'643_C', core:true, dup:true});
/* Greater: Derbent is part of its Russia row (Kuban, Azov, Derbent): the core part gets its own row, counted once */
{ const ru = C.g.states.find(s => String(s.id) === '643');
  ru.km2 -= derbentKm; ru.n = 'Russia (Kuban, Azov)'; C.g.states.push({id:'643_C', n:'Russia: Derbent (in the complete version)', km2:derbentKm, pct:0.1, core:true, dup:true});
  C.g.states.sort((a,b) => b.km2 - a.km2);
  const q = C.g.regions.find(r => r.id === 'qirim'); q.en = 'southern Ukraine, Crimea and the Kuban (Derbent is now in the core)';
  const qr = q.states.find(s => /^Russia/.test(s.n)); if(qr){ qr.km2 -= derbentKm; qr.n = 'Russia (Kuban, Azov)'; q.km2 -= derbentKm; } }
/* Maximum holds all of Dagestan already; its table counts Russia among the lands added in part, so nothing changes there */
const inside = (mp, pt) => mp.some(p => d3.polygonContains(p[0], pt) && !p.slice(1).some(h => d3.polygonContains(h, pt)));
console.log('Derbent', derbentKm, 'km² | inside Maximum already:', inside(C.m.polys, [48.29, 42.06]), '| inside Greater already:', inside(C.g.polys, [48.29, 42.06]));
C.coreRashidun = 'Version 51: Derbent and the exact island of Cyprus in the complete version (Rashidun lands)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Complete', C.x.km2, C.x.states.length, 'states');
