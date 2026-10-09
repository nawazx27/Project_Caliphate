// v10 base map: the Greater Middle East sheet, 18°W–78°E and 5°S–46°N.
// Full detail inside the atlas core (19°–64°E, 4°S–44.5°N); lighter simplification outside it, where the map is
// only ever seen at small scale. Also writes landlo.json, a much simpler land outline for decorative strokes.
const fs = require('fs');
const tc = require('topojson-client'), ts = require('topojson-server'), tsimp = require('topojson-simplify');
const pc = require('polygon-clipping');
const old = JSON.parse(fs.readFileSync('geo_old.json','utf8'));
const cur = JSON.parse(fs.readFileSync('geo2_v6.json','utf8'));
const fc = JSON.parse(fs.readFileSync('ne_10m_admin_0_countries.geojson','utf8'));
const LK = JSON.parse(fs.readFileSync('lakes.geojson','utf8'));
const RV = JSON.parse(fs.readFileSync('rivers.geojson','utf8'));
const SH = {w:-30, s:-36.5, e:104, n:60};   /* v12: widened so the Greater Caliphate's historical lands sit inside the sheet with room around them; v13: south edge 12.5°S so all three Comoros islands are drawn (Mayotte, from 12.6°S, stays outside) */
const CORE = {w:17, s:-6, e:66, n:46};      // full detail here (a little wider than the old sheet)
const REGION = [[[SH.w,SH.s],[SH.e,SH.s],[SH.e,SH.n],[SH.w,SH.n],[SH.w,SH.s]]];
const round = x => Math.round(x*1e4)/1e4;
const polysOf = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const bbox = g => { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; const add=c=>{ if(typeof c[0]==='number'){x0=Math.min(x0,c[0]);x1=Math.max(x1,c[0]);y0=Math.min(y0,c[1]);y1=Math.max(y1,c[1]);} else c.forEach(add); }; add(g.coordinates); return [x0,y0,x1,y1]; };
const hits = b => b[2] > SH.w && b[0] < SH.e && b[3] > SH.s && b[1] < SH.n;
function ringArea(r){ let a = 0; for(let i=0;i<r.length-1;i++) a += r[i][0]*r[i+1][1] - r[i+1][0]*r[i][1]; return Math.abs(a/2); }
function clipToRegion(g, minArea){
  const out = pc.intersection(polysOf(g), REGION).filter(p=>ringArea(p[0]) > (minArea||0));
  if(!out.length) return null;
  /* polygon-clipping returns counter-clockwise outer rings; d3's spherical paths need clockwise */
  const rr = out.map(p=>p.map(r=>r.map(c=>[round(c[0]), round(c[1])]).reverse()));
  return rr.length === 1 ? {type:'Polygon', coordinates:rr[0]} : {type:'MultiPolygon', coordinates:rr};
}
const NAMES = {PSX:'Palestine',SDS:'South Sudan',CYN:'N. Cyprus',CNM:'Cyprus U.N. Buffer Zone',WSB:'Akrotiri',ESB:'Dhekelia',BRT:'Bir Tawil',SOL:'Somaliland',COD:'DR Congo',CAF:'Central African Rep.',TUR:'Türkiye',SAH:'Western Sahara'};
const countries = {type:'FeatureCollection', features: fc.features.filter(f=>f.geometry && hits(bbox(f.geometry))).map(f=>{
  const geometry = clipToRegion(f.geometry, 0.0006); if(!geometry) return null;
  const a3 = f.properties.ADM0_A3, n3 = f.properties.ISO_N3;
  return {type:'Feature', id: n3 && n3 !== '-99' ? n3 : a3, properties:{n: NAMES[a3] || f.properties.NAME}, geometry};
}).filter(Boolean)};
console.log('countries', countries.features.length);

// lakes and rivers: the existing set, plus the large ones of the wider sheet
const oldLakes = tc.feature(old, old.objects.lakes).features;
const prevGeo = JSON.parse(fs.readFileSync('geo2_v9.json','utf8'));
const prevLakes = tc.feature(prevGeo, prevGeo.objects.lakes).features;
const prevRivers = tc.feature(prevGeo, prevGeo.objects.rivers).features;
const LAKES_OUT = new Set(['Lake Chad','South Aral Sea','North Aral Sea','Lake Balkhash','Issyk-Kul','Lake Zaysan','Alakol','Tengiz Köli','Lake Volta','Lake Malawi','Lake Rukwa','Lake Bangweulu','Lake Peipus','Rybinsk Reservoir','Kremenchuk Reservoir','Tsimlyansk Reservoir','Volgograd Reservoir','Saratov Reservoir','Lake Balaton','Lake Geneva','Lago di Garda','Bosten Hu','Nam Co','Qinghai Hu','Kapchagay Reservoir','Lake Tanganyika']);
const LAKES_REDO = new Set(['Lake Tanganyika']);   /* held clipped at the old sheet edge: take them whole */
const prevLakesK = prevLakes.filter(f=>!LAKES_REDO.has(f.properties.n));
const haveL = new Set(prevLakesK.map(f=>f.properties.n));
const outLakes = LK.features.filter(f=>f.geometry && LAKES_OUT.has(f.properties.name) && !haveL.has(f.properties.name))
  .map(f=>({type:'Feature', properties:{n:f.properties.name}, geometry: clipToRegion(f.geometry, 0.002)})).filter(f=>f.geometry);
const lakes = {type:'FeatureCollection', features: prevLakesK.concat(outLakes)};
console.log('lakes', lakes.features.length, '+', outLakes.map(f=>f.properties.n).join(', '));
const RIVERS_NEW = ['Dnipro','Dniester','Southern Bug','Prut','Tisa','Sava','Morava','Olt','Mures','Evros','Donets','Desna','Pripyat','Kama','Oka','Ob','Tejo','Duero','Ebro','Guadalquivir','Guadiana','Rhône','Po','Loire','Seine','Rhine','Elbe','Oder','Vistula','Salween','Yamuna','Chambal','Son','Gandak','Krishna','Cauvery','Tapi','Lualaba','Rufiji','Yangtze','Mekong','Zambezi','Limpopo','Orange','Kasai','Cuanza','Cunene','Okavango'];
const RIVERS_OUT = new Set([...RIVERS_NEW, 'Niger','Sénégal','Benue','Indus','Ganges','Danube','Volga','Syr  Darya','Ural','Irtysh','Tobol','Ishim','Sutlej','Chenab','Jhelum','Brahmaputra','Tarim','Gambia','Don','Kuban','Narmada','Volta','Ubangi','Congo']);
const linesOf = g => g.type === 'LineString' ? [g.coordinates] : g.coordinates;
const inSheet = c => c[0] > SH.w && c[0] < SH.e && c[1] > SH.s && c[1] < SH.n;
const outsideOld = c => !(c[0] > 19 && c[0] < 64 && c[1] > -4 && c[1] < 44.5);
const cut = (ls, keep) => { const parts = []; let p = []; for(const c of ls){ if(keep(c)) p.push([round(c[0]),round(c[1])]); else { if(p.length > 1) parts.push(p); p = []; } } if(p.length > 1) parts.push(p); return parts; };
const NEWR = new Set(RIVERS_NEW);
const outRivers = RV.features.filter(f=>f.geometry && RIVERS_OUT.has(f.properties.name)).map(f=>{
  const parts = linesOf(f.geometry).flatMap(ls=>cut(ls, c=>inSheet(c) && (f.properties.name==='Syr  Darya' || NEWR.has(f.properties.name) ? true : outsideOld(c))));
  return parts.length ? {type:'Feature', properties:{n:f.properties.name}, geometry:{type:'MultiLineString', coordinates:parts}} : null; }).filter(Boolean);
/* the rivers new to the v12 sheet are only ever seen at small scale: thin them first */
function rdpL(pts, eps){ if(pts.length < 3) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length-1] = 1; const st = [[0, pts.length-1]];
  while(st.length){ const [a,b] = st.pop(); let md = 0, mi = -1; const [x1,y1] = pts[a], [x2,y2] = pts[b]; const dx = x2-x1, dy = y2-y1, L = Math.hypot(dx,dy) || 1e-12;
    for(let i=a+1;i<b;i++){ const d = Math.abs(dy*pts[i][0] - dx*pts[i][1] + x2*y1 - y2*x1) / L; if(d > md){ md = d; mi = i; } }
    if(md > eps){ keep[mi] = 1; st.push([a,mi],[mi,b]); } }
  return pts.filter((_,i)=>keep[i]); }
outRivers.forEach(f=>{ if(NEWR.has(f.properties.n)) f.geometry.coordinates = f.geometry.coordinates.map(l=>rdpL(l, 0.015)).filter(l=>l.length > 1); });
const rivers = {type:'FeatureCollection', features: prevRivers.concat(outRivers)};
console.log('rivers', rivers.features.length, '+', outRivers.map(f=>f.properties.n).join(', '));
const deserts = tc.feature(old, old.objects.deserts);
const disputed = tc.feature(cur, cur.objects.disputed);

let topo = ts.topology({countries, disputed, lakes, rivers, deserts}, 1e5);
topo = tsimp.presimplify(topo, tsimp.sphericalTriangleArea);
const T_CORE = +process.argv[2] || 2e-10, T_OUT = +process.argv[3] || 3e-9, T_MID = +process.argv[7] || 3e-9;
topo.arcs = topo.arcs.map(a=>{
  let sx = 0, sy = 0; a.forEach(p=>{ sx += p[0]; sy += p[1]; }); const cx = sx/a.length, cy = sy/a.length;
  const inCore = cx > CORE.w && cx < CORE.e && cy > CORE.s && cy < CORE.n;
  /* the Greater Middle East ring (Maghrib, Central Asia, Afghanistan and Pakistan) gets a middle tier of detail */
  const inMid = (cx > -18 && cx < 17 && cy > 14 && cy < 38) || (cx > 46 && cx < 88 && cy > 23 && cy < 56)
    /* v12: the Greater Caliphate's historical lands: southern Europe, the Sokoto lands, India, Kashgaria */
    || (cx > -10 && cx < 45 && cy > 34 && cy < 50) || (cx > -2 && cx < 24 && cy > 0 && cy < 24) || (cx > 66 && cx < 93 && cy > 6 && cy < 32) || (cx > 73 && cx < 91 && cy > 35 && cy < 44)
    /* v35: the whole of Africa is inside the Natural borders outline, so its southern coasts get the middle tier too */
    || (cx > -20 && cx < 52 && cy > -36.5 && cy < -6);
  const thr = inCore ? T_CORE : inMid ? T_MID : T_OUT;
  return a.filter(p=>p[2] >= thr).map(p=>[p[0],p[1]]);
});
topo = tc.quantize(topo, +process.argv[4] || 1.2e5);
const out = JSON.stringify(topo);
fs.writeFileSync('geo2.json', out);
console.log('geo2 bytes', out.length, 'bbox', JSON.stringify(topo.bbox));

// a simple land outline for the coast decorations (water lines, glow): ~1–2 km generalisation
const g2 = JSON.parse(out);
// countries again (not just merged land), so the simple file can also give simplified borders
let lt = ts.topology({countries: tc.feature(g2, g2.objects.countries)}, 1e5);
lt = tsimp.presimplify(lt, tsimp.sphericalTriangleArea);
lt = tsimp.simplify(lt, +process.argv[5] || 6e-9);
lt = tsimp.filter(lt, tsimp.filterWeight(lt, +process.argv[6] || 4e-7, tsimp.sphericalRingArea));
lt.arcs = lt.arcs.map(a=>a.map(p=>[p[0],p[1]]));
lt = tc.quantize(lt, 4e4);
const lo = JSON.stringify(lt);
fs.writeFileSync('landlo.json', lo);
const cntPts = t => t.arcs.reduce((s,a)=>s+a.length,0);
console.log('landlo bytes', lo.length, 'points', cntPts(lt), 'vs full arcs points', cntPts(g2));
