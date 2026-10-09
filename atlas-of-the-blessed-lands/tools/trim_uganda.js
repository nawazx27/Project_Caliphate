/* Version 38 (2026-10-07, Nawaz's choice): the complete outline (and V2 and the Greater Caliphate, which contain it) is trimmed back to the
   Victoria Nile between Murchison Falls and Lake Albert, so that the whole of it lies inside the natural ring. The piece removed lay south of
   the river (southern Murchison Falls park, by Buliisa) and was bounded there only by administrative lines.
   Run once: node tools/trim_uganda.js   (it refuses to run twice) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const DONE = !!C.trimUganda; if(DONE) console.log('already trimmed');
const RIV = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features;
const vn = RIV.filter(f => f.properties.name === 'Victoria Nile' && f.properties.featurecla === 'River').flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates)
  .find(l => Math.abs(l[0][0] - 31.366) < 0.01);   /* the last reach, Lake Kyoga to Lake Albert, starting at the lake */
const reach = vn.filter(p => p[0] <= 31.85);
/* everything south of the river from the Uganda–DR Congo line in the lake east to 31.85°E, down to 1.5°N */
const cut = [[30.70,2.173],[31.267,2.173],[31.33,2.19]].concat(reach, [[31.85, reach[reach.length-1][1]],[31.85,1.5],[30.70,1.5],[30.70,2.173]]);
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * 6371.0088**2);
const R3 = v => Math.round(v*1000)/1000;
if(!DONE) for(const k of ['x','v2','g']){
  const o = C[k]; const before = area(o.polys);
  const after = pc.difference(o.polys, [[cut]]).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  const removed = before - area(after);
  o.polys = after; o.km2 -= removed;
  const u = o.states.find(s => s.id === '800'); if(u){ const tot = u.km2 / (u.pct/100); u.km2 -= removed; u.pct = Math.round(100*u.km2/ (241550)); }
  console.log(k, 'removed', removed, 'km²; Uganda now', u && u.km2, u && u.pct + '%');
}
if(!DONE) C.trimUganda = 'Version 38: trimmed back to the Victoria Nile below Murchison Falls';
if(!DONE) fs.writeFileSync(F, JSON.stringify(C));
/* Second step (also Version 38): the complete outline is clipped to the natural ring itself, removing slivers of a few km² where the two
   were drawn from slightly different border lines. Needs the ring: NAT_DEBUG=<dir> node tools/nat_gen.js first, then
   RING=<dir>/terr_main.json node tools/trim_uganda.js */
if(process.env.RING){
  const C2 = JSON.parse(fs.readFileSync(F)); if(C2.clipRing){ console.log('already clipped'); process.exit(0); }
  const loop = JSON.parse(fs.readFileSync(process.env.RING)).loop;
  const before = area(C2.x.polys); const after = pc.intersection(C2.x.polys, [[loop]]).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  console.log('clipped to the ring:', before - area(after), 'km²'); C2.x.polys = after; C2.x.km2 -= (before - area(after)); C2.clipRing = true;
  fs.writeFileSync(F, JSON.stringify(C2));
}
