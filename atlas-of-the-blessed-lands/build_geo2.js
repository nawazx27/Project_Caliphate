// v7 base map: same sources as build_geo.js, extended south to 4°S and west to 19°E below 33.2°N,
// so Sudan, South Sudan, Ethiopia, Somalia and their neighbours are complete.
const fs = require('fs');
const tc = require('topojson-client'), ts = require('topojson-server'), tsimp = require('topojson-simplify');
const pc = require('polygon-clipping');
const old = JSON.parse(fs.readFileSync('geo_old.json','utf8'));
const cur = JSON.parse(fs.readFileSync('geo2_v6.json','utf8'));
const fc = JSON.parse(fs.readFileSync('ne_10m_admin_0_countries.geojson','utf8'));
const LK = JSON.parse(fs.readFileSync('lakes.geojson','utf8'));
const RV = JSON.parse(fs.readFileSync('rivers.geojson','utf8'));
const KEEP = new Set(('CYP ISR PSX LBN ETH SDS SOM SYR SOL OMN ARE GEO AZE TUR ARM LBY GRC SDN DJI ERI IRQ IRN QAT SAU BGR KWT TKM JOR EGY YEM CYN CNM WSB ESB BRT BHR PAK AFG '+
  'TCD CAF COD KEN UGA RWA BDI TZA ALB MKD SRB KOS MNE BIH RUS ROU UKR UZB KAZ').trim().split(/\s+/));
const REGION = [[[19,-4],[64,-4],[64,44.5],[19,44.5],[19,-4]]];
const round = x => Math.round(x*1e4)/1e4;
const polysOf = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
function ringArea(r){ let a = 0; for(let i=0;i<r.length-1;i++) a += r[i][0]*r[i+1][1] - r[i+1][0]*r[i][1]; return Math.abs(a/2); }
function clipToRegion(g, minArea){
  const out = pc.intersection(polysOf(g), REGION).filter(p=>ringArea(p[0]) > (minArea||0));
  if(!out.length) return null;
  /* polygon-clipping returns counter-clockwise outer rings; d3's spherical paths need clockwise, so reverse every ring */
  const rr = out.map(p=>p.map(r=>r.map(c=>[round(c[0]), round(c[1])]).reverse()));
  return rr.length === 1 ? {type:'Polygon', coordinates:rr[0]} : {type:'MultiPolygon', coordinates:rr};
}
const NAMES = {PSX:'Palestine',SDS:'South Sudan',CYN:'N. Cyprus',CNM:'Cyprus U.N. Buffer Zone',WSB:'Akrotiri',ESB:'Dhekelia',BRT:'Bir Tawil',SOL:'Somaliland',COD:'DR Congo',CAF:'Central African Rep.',TUR:'Türkiye'};
const countries = {type:'FeatureCollection', features: fc.features.filter(f=>KEEP.has(f.properties.ADM0_A3)).map(f=>{
  const geometry = clipToRegion(f.geometry, 0.0004); if(!geometry) return null;
  const a3 = f.properties.ADM0_A3, n3 = f.properties.ISO_N3;
  return {type:'Feature', id: n3 && n3 !== '-99' ? n3 : a3, properties:{n: NAMES[a3] || f.properties.NAME}, geometry};
}).filter(Boolean)};
console.log('countries', countries.features.length);

// lakes: the earlier set plus the big lakes of the new southern strip
const oldLakes = tc.feature(old, old.objects.lakes);
const oldNames = new Set(oldLakes.features.map(f=>f.properties.n));
const bbox = g => { let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9; const add=c=>{ if(typeof c[0]==='number'){x0=Math.min(x0,c[0]);x1=Math.max(x1,c[0]);y0=Math.min(y0,c[1]);y1=Math.max(y1,c[1]);} else c.forEach(add); }; add(g.coordinates); return [x0,y0,x1,y1]; };
const newLakes = LK.features.filter(f=>f.geometry && f.properties.name && f.properties.scalerank <= 5 && !oldNames.has(f.properties.name)).filter(f=>{ const b = bbox(f.geometry); return (b[3] < 9.5 && b[2] > 19 && b[1] < 9.5 && b[3] > -4) || (b[2] > 44 && b[0] < 64 && b[1] < 44.5 && b[3] > 25 && ['Lake Sevan','Sarygamysh Köli'].includes(f.properties.name)); })
  .map(f=>({type:'Feature', properties:{n:f.properties.name}, geometry: clipToRegion(f.geometry, 0.002)})).filter(f=>f.geometry);
console.log('new lakes', newLakes.map(f=>f.properties.n).join(', '));
const lakes = {type:'FeatureCollection', features: oldLakes.features.concat(newLakes)};

// rivers: the earlier set plus the Nile system, Jubba and Shabeelle south of the old edge (9.34°N)
const WANT_E = new Set(['Kura','Aras','Karkheh','Atrek','Helmand','Harirud','Amu  Darya','Kuban']);
const WANT_R = new Set(['Bahr el Jebel','El Bahr el Abyad','Albert Nile','Victoria Nile','Sobat','Jubba','Shabeelle','Shebele','Omo','Kagera','Bahr el  Zeraf']);
const linesOf = g => g.type === 'LineString' ? [g.coordinates] : g.coordinates;
const cutSouth = ls => { const parts = []; let curp = []; for(const c of ls){ if(c[1] < 9.34 && c[0] > 19 && c[1] > -4){ curp.push([round(c[0]),round(c[1])]); } else { if(curp.length > 1) parts.push(curp); curp = []; } } if(curp.length > 1) parts.push(curp); return parts; };
const newRivers = RV.features.filter(f=>f.geometry && WANT_R.has(f.properties.name)).map(f=>{ const parts = linesOf(f.geometry).flatMap(cutSouth); return parts.length ? {type:'Feature', properties:{n:f.properties.name}, geometry:{type:'MultiLineString', coordinates:parts}} : null; }).filter(Boolean);
const cutBox = ls => { const parts = []; let curp = []; for(const c of ls){ if(c[0] > 19 && c[0] < 64 && c[1] > -4 && c[1] < 44.5){ curp.push([round(c[0]),round(c[1])]); } else { if(curp.length > 1) parts.push(curp); curp = []; } } if(curp.length > 1) parts.push(curp); return parts; };
const eastRivers = RV.features.filter(f=>f.geometry && WANT_E.has(f.properties.name)).map(f=>{ const parts = linesOf(f.geometry).flatMap(cutBox); return parts.length ? {type:'Feature', properties:{n:f.properties.name}, geometry:{type:'MultiLineString', coordinates:parts}} : null; }).filter(Boolean);
newRivers.push(...eastRivers);
console.log('new rivers', newRivers.map(f=>f.properties.n).join(', '));
const rivers = {type:'FeatureCollection', features: tc.feature(old, old.objects.rivers).features.concat(newRivers)};
const deserts = tc.feature(old, old.objects.deserts);
const disputed = tc.feature(cur, cur.objects.disputed);

let topo = ts.topology({countries, disputed, lakes, rivers, deserts}, 1e5);
topo = tsimp.presimplify(topo, tsimp.sphericalTriangleArea);
topo = tsimp.simplify(topo, +process.argv[2] || 2e-10);
topo.arcs = topo.arcs.map(a=>a.map(p=>[p[0],p[1]]));
topo = tc.quantize(topo, +process.argv[3] || 8e4);
const out = JSON.stringify(topo);
fs.writeFileSync('geo2.json', out);
console.log('geo2 bytes', out.length, 'bbox', JSON.stringify(topo.bbox));
