/* Version 49 (2026-10-09, Nawaz's request: "add all the lands of greater turkey to the complete caliphate"; asked which map, he chose
   "the Ottoman Empire at its height"). Adds to the Complete outline (CALIPH.x) the Ottoman lands it did not hold yet:
   - Europe and the Black Sea, traced exactly as the Greater Caliphate's "once ruled" lands are (same provinces as HIST in caliph_gen.js):
     the Balkans, Slavonia/Lika/Dalmatia, Ottoman Hungary, southern and eastern Slovakia, Romania and Moldova, Crimea/Yedisan/Podolia,
     Kuban/Taman/Azov and Derbent;
   - Algeria's Ottoman part (the Regency of Algiers): the V2 province units ruled directly by it or tributary to it (from v2_history.json).
   Left out as late or brief, not the empire at its height: Tibesti and Borkou (1908–13), Kashgar (vassal 1873–77), Otranto (1480–81).
   The version to Iraq's border (CALIPH.xw) gets the same lands except Kuban and Derbent (it leaves out the Caucasus).
   V2 and Maximum are "Complete plus more", so they take the new lands too; the Greater Caliphate already holds them (only flags change).
   Run once: node tools/add_core_ottoman.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreOttoman){ console.log('already added'); process.exit(0); }

const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const areaP = p => area([p]);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const G = geo.objects.countries.geometries;
const mpOf = id => asMp(topojson.feature(geo, G.find(g => String(g.id) === id)).geometry);
const geomOf = ids => ids.flatMap(mpOf);
const closed = pts => { const o = pts.slice(); if(o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1]) o.push(o[0]); return o; };
/* the same helpers as caliph_gen.js, so the pieces come out as they are drawn in the Greater Caliphate */
function rdp(pts, eps){ if(pts.length < 4) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length-1] = 1; const st = [[0, pts.length-1]];
  while(st.length){ const [a,b] = st.pop(); let md = 0, mi = -1; const [x1,y1] = pts[a], [x2,y2] = pts[b]; const dx = x2-x1, dy = y2-y1, L = Math.hypot(dx,dy) || 1e-12;
    for(let i=a+1;i<b;i++){ const d = Math.abs(dy*pts[i][0] - dx*pts[i][1] + x2*y1 - y2*x1) / L; if(d > md){ md = d; mi = i; } }
    if(md > eps){ keep[mi] = 1; st.push([a,mi],[mi,b]); } }
  return pts.filter((_,i)=>keep[i]); }
const rdpRing = (rg, eps) => { let k = 0, md = -1; rg.forEach((p,i)=>{ const d = Math.hypot(p[0]-rg[0][0], p[1]-rg[0][1]); if(d > md){ md = d; k = i; } });
  const a = rdp(rg.slice(0, k+1), eps), b = rdp(rg.slice(k), eps); return a.concat(b.slice(1)); };
const simp = (PP, eps) => PP.map(poly=>poly.map(rg=>rdpRing(rg, eps)).filter(rg=>rg.length >= 4)).filter(poly=>poly.length && poly[0].length >= 4);
const r4 = x => Math.round(x*1e4)/1e4;
const clean4 = PP => PP.map(poly=>poly.map(rg=>{ const o = []; for(const [x,y] of rg){ const q = [r4(x), r4(y)]; const l = o[o.length-1]; if(!l || l[0]!==q[0] || l[1]!==q[1]) o.push(q); } if(o.length && (o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1])) o.push(o[0]); return o; }).filter(rg=>rg.length >= 4)).filter(poly=>poly.length);
const prov = (a3, names) => names.flatMap(n => { const fs_ = A1.filter(f=>f.properties.adm0_a3===a3 && f.properties.name===n); if(!fs_.length) throw new Error('no province '+a3+' '+n); return fs_.flatMap(f=>asMp(f.geometry)); });
const provExcept = (a3, names) => A1.filter(f=>f.properties.adm0_a3===a3 && !names.includes(f.properties.name)).flatMap(f=>asMp(f.geometry));
const largestOnly = PP => { let best = null, ba = -1; for(const p of PP){ const a = areaP(p); if(a > ba){ ba = a; best = p; } } return best ? [best] : []; };
const box = pts => [[closed(pts)]];

/* the Ottoman pieces, copied from HIST in caliph_gen.js */
const OTT = [
  {id:'balkans', within:['100','008','807','KOS','688','499','070'], shape:()=>geomOf(['100','008','807','KOS','688','499','070'])},
  {id:'croatia', within:['191'], shape:()=>{
     const inland = prov('HRV',['Osjecko-Baranjska','Vukovarsko-Srijemska','Brodsko-Posavska','Viroviticko-Podravska','Bjelovarsko-bilogorska','Licko-Senjska']);
     const coast = ['Šibensko-Kninska','Splitsko-Dalmatinska','Zadarska','Dubrovacko-Neretvanska'].flatMap(n=>largestOnly(prov('HRV',[n])));
     return inland.concat(coast); }},
  {id:'hungary', within:['348'], shape:()=>provExcept('HUN',['Gyor-Moson-Sopron','Sopron','Gyôr','Vas','Szombathely'])},
  {id:'slovakia', within:['703'], shape:()=>prov('SVK',['Nitriansky','Banskobystrický','Košický','Prešov'])},
  {id:'romania', within:['642','498'], shape:()=>geomOf(['642','498'])},
  {id:'ukraine', within:['804','643'], shape:()=>prov('UKR',['Odessa','Mykolayiv','Kherson','Zaporizhzhya','Kirovohrad','Vinnytsya',"Khmel'nyts'kyy",'Chernivtsi',"Ternopil'",'Cherkasy']).concat(prov('RUS',['Crimea','Sevastopol']))},
  {id:'kuban', caucasus:true, within:['643'], shape:()=>prov('RUS',['Krasnodar']).concat(box([[39.0,46.9],[39.75,46.9],[39.75,47.35],[39.0,47.35]]))},
  {id:'derbent', caucasus:true, within:['643'], shape:()=>box([[48.2,41.2],[48.75,41.85],[48.35,42.6],[47.9,43.0],[47.2,42.6],[47.4,41.9],[47.9,41.5]])}
];
const parts = {};
for(const h of OTT){
  let cut = pc.intersection(h.shape(), geomOf(h.within));
  cut = clean4(simp(clean4(cut), 0.003)).filter(p=>areaP(p) > 20).map(poly=>[poly[0]].concat(poly.slice(1).filter(x=>areaP([x]) > 50)));
  parts[h.id] = cut; console.log('ottoman', h.id.padEnd(9), area(cut), 'km²');
}
/* Algeria under the Regency of Algiers: the V2 units ruled directly by the Ottomans or tributary to them */
const DZA_UNITS = C.v2.units.filter(u => u.a3 === 'DZA' && (u.cat === 'direct' || u.cat === 'tributary') && /Ottoman|Algiers/.test((u.who||'') + ' ' + (u.dates||'')));
console.log('Algeria units:', DZA_UNITS.map(u => u.label.split(' (')[0] + ' ' + u.km2).join('; '));
parts.algeria = clean4(pc.intersection(clean4(pc.union(...DZA_UNITS.map(u => clean4(u.polys)))), mpOf('012')));
console.log('ottoman algeria  ', area(parts.algeria), 'km²');

const ADD_ALL = clean4(pc.union(...Object.values(parts)));
const ADD_W = clean4(pc.union(...OTT.filter(h => !h.caucasus).map(h => parts[h.id]), parts.algeria));

/* union into an outline, then fill the new hairline gaps; holes that were there before stay */
function grow(V, add, label){
  const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = pc.union(R3mp(V.polys), R3mp(add)).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  let filled = 0, fk = 0;
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
    const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
    if(!old && a < 5000){ filled++; fk += a; return false; } return true; })]);
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  console.log(label.padEnd(9), '+', gain, 'km² ->', V.km2, '| gaps filled', filled, Math.round(fk), 'km²');
  return gain;
}

/* rows for the states table: the added part of each state, against its full Natural Earth area */
const NE = JSON.parse(fs.readFileSync(path.join(ROOT, 'ne_10m_admin_0_countries.geojson'))).features;
const fullKm = id => { const f = NE.find(f => (f.properties.ISO_N3 !== '-99' ? f.properties.ISO_N3 : f.properties.ADM0_A3) === id || f.properties.ADM0_A3 === id); return f ? area(asMp(f.geometry)) : null; };
const ROWS = [
  {id:'100', n:'Bulgaria'}, {id:'008', n:'Albania'}, {id:'807', n:'North Macedonia'}, {id:'KOS', n:'Kosovo'}, {id:'688', n:'Serbia'},
  {id:'499', n:'Montenegro'}, {id:'070', n:'Bosnia and Herz.'}, {id:'642', n:'Romania'}, {id:'498', n:'Moldova'},
  {id:'191', n:'Croatia: Slavonia, Lika and Dalmatia'}, {id:'348', n:'Hungary: all but the far west'}, {id:'703', n:'Slovakia: the south and east'},
  {id:'804', n:'Ukraine: Yedisan, Podolia and the south'}, {id:'643', n:'Russia: Kuban, Azov and Derbent', caucasus:true},
  {id:'012', n:'Algeria: the Ottoman north (Regency of Algiers)'}];
const CRI = prov('RUS', ['Crimea', 'Sevastopol']);
function rowsFor(add, skipCaucasus){
  const out = [];
  for(const r of ROWS){
    if(skipCaucasus && r.caucasus) continue;
    let mp = R3mp(mpOf(r.id)); if(r.id === '643') mp = pc.difference(mp, CRI);
    const km2 = area(pc.intersection(mp, add)); if(km2 < 50) continue;
    const full = r.id === 'KOS' ? area(mpOf('KOS')) : (fullKm(r.id) || area(mpOf(r.id)));
    out.push({id:r.id, n:r.n, km2, pct:Math.min(100, Math.max(1, Math.round(100*km2/full))), ottoman:true});
  }
  const ck = area(pc.intersection(R3mp(CRI), add)); if(ck > 50) out.push({id:'CRI', n:'Crimea (annexed by Russia in 2014; recognised internationally as Ukraine)', km2:ck, pct:100, ottoman:true});
  return out;
}

/* Complete and To Iraq */
grow(C.x, ADD_ALL, 'Complete'); C.x.states.push(...rowsFor(ADD_ALL, false)); C.x.states.sort((a,b) => b.km2 - a.km2);
grow(C.xw, ADD_W, 'To Iraq'); C.xw.states.push(...rowsFor(ADD_W, true)); C.xw.states.sort((a,b) => b.km2 - a.km2);
const coreRows = rowsFor(ADD_ALL, false), coreById = Object.fromEntries(coreRows.map(r => [r.id, r]));

/* V2 and Maximum: Complete plus more, so they take the new lands; new rows count as core */
for(const k of ['v2', 'm']){
  grow(C[k], ADD_ALL, k);
  const have = new Set(C[k].states.map(s => String(s.id)));
  coreRows.forEach(r => { if(!have.has(r.id)) C[k].states.push({...r, core:true}); });
  C[k].states.sort((a,b) => (k === 'v2' ? (b.core === true) - (a.core === true) : 0) || b.km2 - a.km2);
}
/* V2: Algeria is now part core: its row keeps the rest, and the core part gets its own row (counted once) */
{ const a = C.v2.states.find(s => s.id === '012'), c = coreById['012'];
  if(a && c){ a.km2 -= c.km2; a.n = 'Algeria: the south (the Sahara beyond the Regency)'; C.v2.states.push({id:'012_C', n:'Algeria: the Ottoman north (in the complete version)', km2:c.km2, pct:c.pct, core:true, dup:true}); } }

/* Greater Caliphate: same land; the Ottoman rows become core */
const HIST_IDS = new Set(['100','008','807','KOS','688','499','070','191','348','703','642','498','804','643','CRI']);
C.g.states.forEach(s => { if(HIST_IDS.has(String(s.id))){ s.core = true; s.hist = false; s.ottoman = true; } });
{ const a = C.g.states.find(s => String(s.id) === '012'), c = coreById['012'];
  if(a && c){ a.km2 -= c.km2; a.n = 'Algeria: the south'; C.g.states.push({id:'012_C', n:'Algeria: the Ottoman north (in the complete version)', km2:c.km2, pct:c.pct, core:true, dup:true}); } }
C.g.states.sort((a,b) => b.km2 - a.km2);
const R = C.g.regions;
const toCore = (id, en) => { const r = R.find(r => r.id === id); delete r.hist; r.en = en; r.ottoman = true; };
toCore('rumeli', 'the Ottoman Balkans · added to the complete version at your request (Greece is in the core too)');
toCore('danube', 'Ottoman Hungary, Slovakia’s south and east, Romania and Moldova · added to the complete version at your request');
toCore('qirim', 'Crimea, Yedisan and Podolia, the Kuban and Derbent · added to the complete version at your request');
R.find(r => r.id === 'maghrib').en = 'North Africa (Libya, Tunisia and Algeria’s Ottoman north are now in the core)';
/* the three cards move up with the other core cards */
const moved = ['rumeli','danube','qirim'].map(id => R.splice(R.findIndex(r => r.id === id), 1)[0]);
R.splice(R.findIndex(r => r.id === 'khurasan') + 1, 0, ...moved);

C.coreOttoman = 'Version 49: the Ottoman Empire at its height in the complete version';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Complete', C.x.km2, C.x.states.length, 'states | To Iraq', C.xw.km2, C.xw.states.length, '| V2', C.v2.km2, '| Max', C.m.km2);
console.log('rows:', coreRows.map(r => r.n + ' ' + r.km2 + ' (' + r.pct + '%)').join('; '));
