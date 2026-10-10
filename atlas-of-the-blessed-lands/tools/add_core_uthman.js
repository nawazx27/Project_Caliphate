/* Version 52 (2026-10-10, Nawaz's request with a map of the caliphate under ʿUthmān, dark and light green: "Make sure all these lands are
   included in the complete caliphate"). The map was lined up with the base map (flat projection fitted to the land/sea pattern: lon = 25 +
   (x − 558.5)·0.0654, lat = 22 + (411 − y)·0.0584°; known points within ~0.7°) and every green pixel tested against the Complete outline.
   Green outside it, and how it is added here (all of it Nawaz's map, traced approximately; see notes.md, Version 52):
   - northern Algeria and northern Morocco: whole provinces (Natural Earth admin-1) that the green covers at least half of; plus the coastal
     provinces between them and the sea (the map's coast is a little off there) and Morocco's Oriental, which joins the two; plus everything
     north of the green band's southern edge as the map draws it (so the green parts of the other provinces are in too);
   - eastern Sicily: Enna, Catania, Messina, Caltanissetta (52–89% green);
   - the south-east coast of Spain (no Spanish provinces in the data): the map's inland edge, down to the coast;
   - Dagestan's Caspian coast north of Derbent to 44°N: a strip 0.8° wide along the real coast (the map draws the Caspian 2–3° too far west);
   - a strip of southern Uzbekistan by the Amu Darya: the map's northern edge, down to the border.
   Joins: Complete; To Iraq gets the western lands (not Dagestan or Uzbekistan); V2 and Maximum, which hold Complete, get what they lacked.
   Run once: node tools/add_core_uthman.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreUthman){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const mpOf = id => asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry);
const closed = pts => { const o = pts.slice(); if(o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1]) o.push(o[0]); return o; };
const inside = (mp, pt) => mp.some(p => d3.polygonContains(p[0], pt) && !p.slice(1).some(h => d3.polygonContains(h, pt)));
const prov = (a3, names) => names.flatMap(n => { const f = A1.filter(f => f.properties.adm0_a3 === a3 && f.properties.name === n); if(!f.length) throw new Error('no province ' + a3 + ' ' + n); return f.flatMap(x => asMp(x.geometry)); });
const cut = (shape, id) => R3mp(pc.intersection(R3mp(shape), R3mp(mpOf(id))));

const DZA = ['Boumerdès','Sétif','Bordj Bou Arréridj','Bouira','Tissemsilt','Aïn Defla','Sidi Bel Abbès','Médéa','Batna','Khenchela','Guelma','Constantine','Mila',
  'Oum el Bouaghi','Blida','Relizane','Mascara',"M'Sila",'Souk Ahras','Tizi Ouzou','Saïda','Tiaret','Béjaïa','Tipaza','Tébessa','Chlef','Mostaganem','Biskra','Tlemcen',
  'El Tarf','Jijel','Skikda',  /* at least half green */  'Aïn Témouchent','Oran','Alger','Annaba'  /* coastal, between the green and the sea */];
const MAR = ['Taza - Al Hoceima - Taounate','Rabat - Salé - Zemmour - Zaer','Chaouia - Ouardigha','Tanger - Tétouan','Gharb - Chrarda - Béni Hssen','Doukkala - Abda',
  'Fès - Boulemane','Grand Casablanca',  /* at least half green */  'Oriental'  /* 41%: joins Morocco's part to Algeria's */];
const SICILY = ['Enna','Catania','Messina','Caltanissetta'];
/* inland edges read from the map (lon, lat) */
const SPAIN_EDGE = [[-3.95,37.02],[-3.65,37.08],[-3.55,37.14],[-3.35,37.14],[-3.25,37.2],[-3.15,37.25],[-2.95,37.25],[-2.85,37.31],[-2.75,37.31],[-2.65,37.37],[-2.45,37.37],
  [-2.35,37.43],[-2.25,37.43],[-2.15,37.49],[-1.95,37.49],[-1.85,37.55],[-1.75,37.6],[-0.85,37.6]];
const UZB_EDGE = [[64.05,38.95],[64.35,38.83],[64.55,38.71],[64.75,38.66],[64.85,38.6],[65.05,38.54],[65.2,38.54],[65.25,38.25],[65.45,38.07],[65.55,38.01],[65.7,38.01],
  [65.75,37.78],[65.9,37.78],[65.95,38.19],[66.15,38.13],[66.25,38.07],[66.45,38.01],[67.1,38.01],[67.15,37.9],[67.25,37.55],[67.5,37.52],[67.65,37.43],[67.75,37.2],[67.9,37.14]];
/* the southern edge of the green band across the Maghrib, read from the map: the green parts of provinces less than half green are taken too */
const MAGHRIB_EDGE = [[-9.1,31.88],[-8.9,31.82],[-8.7,31.88],[-8.5,31.93],[-8.3,32.05],[-8.1,32.05],[-7.9,32.11],[-7.7,32.17],[-7.5,32.23],[-7.3,32.29],[-7.1,32.34],[-6.9,32.4],[-6.7,32.46],[-6.5,32.52],[-6.3,32.58],[-6.1,32.64],[-5.9,32.75],[-5.7,32.75],[-5.5,32.81],[-5.3,32.87],[-5.1,32.93],[-4.9,32.99],[-4.7,33.05],[-4.5,33.1],[-4.3,33.16],[-4.1,33.22],[-3.9,33.28],[-3.7,33.34],[-3.5,33.4],[-3.3,33.45],[-3.1,33.51],[-2.9,33.57],[-2.7,33.57],[-2.5,33.63],[-2.3,33.69],[-2.1,33.75],[-1.9,33.8],[-1.7,33.86],[-1.5,33.92],[-1.1,34.04],[-0.9,34.04],[-0.7,34.1],[-0.5,34.16],[-0.3,34.21],[-0.1,34.27],[0.1,34.27],[0.3,34.27],[0.5,34.33],[0.7,34.39],[0.9,34.39],[1.1,34.45],[1.3,34.51],[1.5,34.51],[1.7,34.56],[1.9,34.56],[2.1,34.62],[2.3,34.62],[2.5,34.62],[2.7,34.62],[2.9,34.62],[3.1,34.62],[3.3,34.62],[3.5,34.62],[3.7,34.62],[3.9,34.62],[4.1,34.56],[4.3,34.51],[4.5,34.51],[4.7,34.45],[4.9,34.39],[5.1,34.33],[5.3,34.27],[5.5,34.16],[5.7,34.16],[5.9,34.04],[6.1,33.92],[6.3,33.8],[6.5,33.69],[6.7,33.63],[6.9,33.51],[7.1,33.4],[7.3,33.28],[7.5,33.16],[7.7,33.05],[7.9,32.87],[8.1,32.87],[8.3,33.05],[8.5,32.87],[8.7,32.7],[8.9,32.34],[9.1,32.17]];
const BAND = [[closed([[-9.6, MAGHRIB_EDGE[0][1]]].concat(MAGHRIB_EDGE, [[9.2, MAGHRIB_EDGE[MAGHRIB_EDGE.length-1][1]], [9.2, 38.5], [-9.6, 38.5]]))]];
const SPAIN = cut([[closed(SPAIN_EDGE.concat([[-0.85,36.0],[-3.95,36.0]]))]], '724');
const UZBS = cut([[closed(UZB_EDGE.concat([[67.9,36.5],[64.05,36.5]]))]], '860');
/* Dagestan's coast: from the Derbent corridor (42.6°N) to 44°N, 0.8° inland from the real coast */
const RU = mpOf('643');
const coastLon = lat => { let last = null; for(let lon = 45; lon <= 50; lon += 0.01) if(inside(RU, [lon, lat])) last = lon; return last; };
const STRIP = []; for(let lat = 42.4; lat <= 44.0001; lat += 0.1) STRIP.push([R3(coastLon(lat) - 0.8), R3(lat)]);
const DAG = cut([[closed(STRIP.concat([[50.0,44.0],[50.0,42.4]]))]], '643');

const PIECES = {
  '012': {n:'Algeria: the north', mp:R3mp(pc.union(cut(prov('DZA', DZA), '012'), cut(BAND, '012'))), west:true},
  '504': {n:'Morocco: the north', mp:R3mp(pc.union(cut(prov('MAR', MAR), '504'), cut(BAND, '504'))), west:true},
  '724': {n:'Spain: the south-east coast', mp:SPAIN, west:true},
  '380': {n:'Italy: eastern Sicily', mp:cut(prov('ITA', SICILY), '380'), west:true},
  '643': {n:'Russia: the Dagestan coast north of Derbent', mp:DAG},
  '860': {n:'Uzbekistan: the south, by the Amu Darya', mp:UZBS}};
for(const [id, p] of Object.entries(PIECES)){ p.km2 = area(p.mp); console.log(id, p.n.padEnd(46), p.km2, 'km²'); }
const NE = JSON.parse(fs.readFileSync(path.join(ROOT, 'ne_10m_admin_0_countries.geojson'))).features;
const fullKm = id => { const f = NE.find(f => f.properties.ISO_N3 === id); return f ? area(asMp(f.geometry)) : area(mpOf(id)); };
const pctOf = (id, km) => Math.max(0.1, Math.round(1000 * km / fullKm(id)) / 10);

function grow(V, ids, label){
  const add = pc.union(...ids.map(id => PIECES[id].mp));
  const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = pc.union(R3mp(V.polys), add).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  let filled = 0, fk = 0;
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
    const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
    if(!old && a < 5000){ filled++; fk += a; return false; } return true; })]);
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  console.log(label.padEnd(9), '+', gain, 'km² ->', V.km2, '| gaps filled', filled, Math.round(fk), 'km²');
}
/* a state partly in the core: its row keeps the rest, the core part gets its own row (counted once) */
function splitRow(V, id, km, label, pick){
  const r = V.states.find(pick || (s => String(s.id) === id && !s.dup)); if(!r) return;
  const whole = r.pct, all = r.km2; r.km2 = Math.max(0, all - km); r.pct = Math.max(1, Math.round(whole * r.km2 / all));
  const c = V.states.find(s => s.id === id + '_C');
  if(c){ c.km2 += km; c.n = label; } else V.states.push({id:id + '_C', n:label, km2:km, pct:pctOf(id, km), core:true, dup:true});
}
const ALL = Object.keys(PIECES), WEST = ALL.filter(id => PIECES[id].west);

/* Complete and To Iraq */
grow(C.x, ALL, 'Complete'); grow(C.xw, WEST, 'To Iraq');
for(const [V, ids] of [[C.x, ALL], [C.xw, WEST]]){
  for(const id of ids){ const p = PIECES[id];
    if(id === '643'){ const r = V.states.find(s => s.id === '643'); r.km2 += p.km2; r.n = 'Russia: Derbent, the Samur valley and the Dagestan coast'; continue; }
    V.states.push({id, n:p.n, km2:p.km2, pct:pctOf(id, p.km2)}); }
  V.states.sort((a, b) => b.km2 - a.km2); }
/* V2 holds Algeria, Morocco, Spain and Uzbekistan whole: it gains eastern Sicily and the Dagestan coast; the core parts get their own rows */
grow(C.v2, ['380', '643'], 'V2');
for(const id of ['012','504','724','860']) splitRow(C.v2, id, PIECES[id].km2, PIECES[id].n + ' (in the complete version)');
C.v2.states.push({id:'380_C', n:'Italy: eastern Sicily (in the complete version)', km2:PIECES['380'].km2, pct:pctOf('380', PIECES['380'].km2), core:true, dup:true});
{ const r = C.v2.states.find(s => s.id === '643_C'); r.km2 += PIECES['643'].km2; r.n = 'Russia: Derbent, the Samur valley and the Dagestan coast'; }
/* Maximum holds Algeria, Morocco, Uzbekistan and Dagestan: it gains the Spanish coast and eastern Sicily, as core rows */
grow(C.m, ['724', '380'], 'Max');
for(const id of ['724', '380']) C.m.states.push({id:id + '_C', n:PIECES[id].n + ' (in the complete version)', km2:PIECES[id].km2, pct:pctOf(id, PIECES[id].km2), core:true});
/* Greater: same land; the core parts get their own rows */
splitRow(C.g, '012', PIECES['012'].km2, 'Algeria: the north (in the complete version)', s => s.id === '012');
splitRow(C.g, '504', PIECES['504'].km2, 'Morocco: the north (in the complete version)');
splitRow(C.g, '724', PIECES['724'].km2, 'Spain: the south-east coast (in the complete version)');
splitRow(C.g, '380', PIECES['380'].km2, 'Italy: eastern Sicily (in the complete version)', s => s.id === '380');
splitRow(C.g, '860', PIECES['860'].km2, 'Uzbekistan: the south (in the complete version)');
splitRow(C.g, '643', PIECES['643'].km2, 'Russia: Derbent and the Dagestan coast (in the complete version)', s => s.id === '643_J');
C.g.states.sort((a, b) => b.km2 - a.km2);
const R = C.g.regions;
R.find(r => r.id === 'maghrib').en = 'North Africa (Libya, Tunisia and the north of Algeria and Morocco are now in the core)';
R.find(r => r.id === 'andalus').en = 'Spain, Portugal and Gibraltar (the south-east coast of Spain is now in the core)';
R.find(r => r.id === 'siqilliyah').en = 'Sicily, southern Italy, Sardinia and Malta (eastern Sicily is now in the core)';
R.find(r => r.id === 'centralasia').en = 'Central Asia (Turkmenistan and a strip of southern Uzbekistan are now in the core)';
C.coreUthman = 'Version 52: the lands on Nawaz’s map of the caliphate under ʿUthmān';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Complete', C.x.km2, C.x.states.length, '| To Iraq', C.xw.km2, C.xw.states.length, '| V2', C.v2.km2, '| Max', C.m.km2);
