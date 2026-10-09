const fs=require('fs');
const tc=require('topojson-client'), ts=require('topojson-server'), tsimp=require('topojson-simplify');
const old=JSON.parse(fs.readFileSync('geo_old.json','utf8'));
const fc=JSON.parse(fs.readFileSync('ne_10m_admin_0_countries.geojson','utf8'));
const dis=JSON.parse(fs.readFileSync('ne_10m_admin_0_disputed_areas.geojson','utf8'));
const KEEP=new Set('CYP ISR PSX LBN ETH SDS SOM SYR SOL OMN ARE GEO AZE TUR ARM LBY GRC SDN DJI ERI IRQ IRN QAT SAU BGR KWT TKM JOR EGY YEM CYN CNM WSB ESB BRT BHR PAK AFG'.split(' '));

const BB=[24,5,64,43.5];
function clipRing(ring){ // Sutherland-Hodgman against rectangle
  let out=ring.slice(0,-1);
  const edges=[[0,BB[0],1],[0,BB[2],-1],[1,BB[1],1],[1,BB[3],-1]];
  for(const [ax,v,sg] of edges){
    const inp=out; out=[]; if(!inp.length) break;
    const inside=p=>sg*(p[ax]-v)>=0;
    for(let i=0;i<inp.length;i++){ const a=inp[i], b=inp[(i+1)%inp.length]; const ia=inside(a), ib=inside(b);
      const inter=()=>{const t=(v-a[ax])/(b[ax]-a[ax]); const o=ax===0?[v,a[1]+t*(b[1]-a[1])]:[a[0]+t*(b[0]-a[0]),v]; return o;};
      if(ia&&ib) out.push(b); else if(ia&&!ib) out.push(inter()); else if(!ia&&ib){ out.push(inter()); out.push(b);} }
  }
  if(out.length<3) return null; out.push(out[0]); return out; }
function clipGeom(g){ const polys=(g.type==='Polygon'?[g.coordinates]:g.coordinates).map(p=>{ const rs=p.map(clipRing).filter(Boolean); return rs.length?rs:null;}).filter(Boolean); if(!polys.length) return null; return polys.length===1?{type:'Polygon',coordinates:polys[0]}:{type:'MultiPolygon',coordinates:polys}; }
const round=(x)=>Math.round(x*1e4)/1e4;
function rg(g){ if(g.type==='Polygon') return {type:'Polygon',coordinates:g.coordinates.map(r=>r.map(c=>[round(c[0]),round(c[1])]))}; return {type:'MultiPolygon',coordinates:g.coordinates.map(p=>p.map(r=>r.map(c=>[round(c[0]),round(c[1])])))}; }
// drop tiny polygons far from region (islands) to save bytes
function area(r){let a=0;for(let i=0,n=r.length;i<n-1;i++)a+=r[i][0]*r[i+1][1]-r[i+1][0]*r[i][1];return Math.abs(a/2);}
function prune(g,min){ if(g.type==='Polygon') return g; const ps=g.coordinates.filter(p=>area(p[0])>min); return ps.length===1?{type:'Polygon',coordinates:ps[0]}:{type:'MultiPolygon',coordinates:ps}; }
const countries={type:'FeatureCollection',features:fc.features.filter(f=>KEEP.has(f.properties.ADM0_A3)).map(f=>({type:'Feature',id:f.properties.ISO_N3&&f.properties.ISO_N3!=='-99'?f.properties.ISO_N3:f.properties.ADM0_A3,properties:{n:({PSX:'Palestine',SDS:'South Sudan',CYN:'N. Cyprus',CNM:'Cyprus U.N. Buffer Zone',WSB:'Akrotiri',ESB:'Dhekelia',BRT:'Bir Tawil',SOL:'Somaliland'})[f.properties.ADM0_A3]||f.properties.NAME},geometry:prune(rg(clipGeom(f.geometry)),0.0004)}))};
console.log('countries',countries.features.length);
const WANT=new Set(['Golan Heights','Shebaa farms',"Hala'ib Triangle",'East Jerusalem']);
const disputed={type:'FeatureCollection',features:dis.features.filter(f=>WANT.has(f.properties.NAME_EN)).map(f=>({type:'Feature',properties:{n:f.properties.NAME_EN,note:f.properties.NOTE_BRK},geometry:rg(f.geometry)}))};
console.log('disputed',disputed.features.map(f=>f.properties.n));
const dec=o=>tc.feature(old,old.objects[o]);
const lakes=dec('lakes'), rivers=dec('rivers'), deserts=dec('deserts');
let topo=ts.topology({countries,disputed,lakes,rivers,deserts},1e5);
topo=tsimp.presimplify(topo, tsimp.sphericalTriangleArea);
const w=tsimp.quantile(topo,0.0);
topo=tsimp.simplify(topo,+process.argv[2]||2e-10);
// quantize again to 1e5 handled by topology; stringify with limited precision
topo.arcs=topo.arcs.map(a=>a.map(p=>[p[0],p[1]]));
topo=tc.quantize(topo,+process.argv[3]||6e4);
const out=JSON.stringify(topo);
fs.writeFileSync('geo2.json',out);
console.log('geo2 bytes',out.length);

/* ---------------- derived polygons ---------------- */
const RV=rivers.features;
const bb=f=>{const cs=[];(function w(a){if(typeof a[0]==='number')cs.push(a);else a.forEach(w)})(f.geometry.coordinates);return {cs,x0:Math.min(...cs.map(c=>c[0])),x1:Math.max(...cs.map(c=>c[0])),y0:Math.min(...cs.map(c=>c[1])),y1:Math.max(...cs.map(c=>c[1]))}};
const find=(x0,x1,y0,y1,t=0.15)=>RV.map(f=>({f,b:bb(f)})).filter(o=>Math.abs(o.b.x0-x0)<t&&Math.abs(o.b.x1-x1)<t&&Math.abs(o.b.y0-y0)<t&&Math.abs(o.b.y1-y1)<t)[0];
const lines=o=>o.f.geometry.type==='LineString'?[o.f.geometry.coordinates]:o.f.geometry.coordinates;
function chain(parts){ // greedy join of line parts into one polyline
  parts=parts.map(p=>p.slice()); let cur=parts.shift(); 
  while(parts.length){ let best=-1,bd=1e9,rev=false,atEnd=true;
    parts.forEach((p,i)=>{ const ends=[[p[0],false,true],[p[p.length-1],true,true],[p[0],false,false],[p[p.length-1],true,false]];
      for(const [pt,r,ae] of ends){ const c=ae?cur[cur.length-1]:cur[0]; const d=Math.hypot(pt[0]-c[0],pt[1]-c[1]); if(d<bd){bd=d;best=i;rev=r;atEnd=ae;} } });
    let p=parts.splice(best,1)[0]; if(atEnd){ if(rev)p.reverse(); cur=cur.concat(p);} else { if(!rev)p.reverse(); cur=p.concat(cur);} }
  return cur; }
const dicle=find(39.2,42.4,37.1,38.5), tigL=find(42.4,47.5,31.0,37.1), eMid=find(38.0,41.0,34.4,36.8), eLow=find(41.0,47.5,30.9,34.5), eUp=find(37.8,41.5,36.8,40.2), nile=find(30.3,34.0,15.6,30.1), shatt=find(47.5,48.5,30.0,31.0);
console.log('found',!!dicle,!!tigL,!!eMid,!!eLow,!!eUp,!!nile,!!shatt);
const E_mid=chain(lines(eMid)), E_low=chain(lines(eLow)), E_up=chain(lines(eUp)), T_up=chain(lines(dicle)), T_low=chain(lines(tigL)), NILE=chain(lines(nile));
const orient=(p,first)=>{ // make polyline start nearest to point first
  const d0=Math.hypot(p[0][0]-first[0],p[0][1]-first[1]), d1=Math.hypot(p[p.length-1][0]-first[0],p[p.length-1][1]-first[1]); return d1<d0?p.slice().reverse():p; };
const nearestIdx=(p,pt)=>{let bi=0,bd=1e9;p.forEach((q,i)=>{const d=Math.hypot(q[0]-pt[0],q[1]-pt[1]);if(d<bd){bd=d;bi=i;}});return bi;};
const sub=(p,a,b)=>{const i=nearestIdx(p,a),j=nearestIdx(p,b);return i<=j?p.slice(i,j+1):p.slice(j,i+1).reverse();};
const r3=p=>p.map(c=>[+c[0].toFixed(3),+c[1].toFixed(3)]);
const thin=(p,step)=>p.filter((_,i)=>i%step===0||i===p.length-1);
const E_all=chain([...lines(eMid),...lines(eLow)]); const Eo=orient(E_all,[38.03,36.83]);
const T_all=chain([...lines(dicle),...lines(tigL)]); 
// Upper Euphrates trunk: Samsat (38.5,37.5) -> Jarabulus
const Eu=orient(E_up,[38.0,36.8]);
const HIT=[42.83,33.64], TIKRIT=[43.68,34.6], DIYAR=[40.23,37.95], SAMSAT=[38.5,37.55], JARAB=[38.03,36.83], QURNA=[47.43,31.0];
const To=orient(T_all,[39.4,38.4]); // starts upstream
// Jazirah
const jW=thin(sub(Eo,JARAB,HIT),2), jE=thin(sub(To,DIYAR,TIKRIT),2).reverse(); // Tikrit->Diyarbakir
const jNW=thin(sub(Eu,SAMSAT,JARAB),1);
const UPPER=[
 {c:'approx',p:r3([...jW])},
 {c:'uncertain',p:r3([HIT,TIKRIT])},
 {c:'approx',p:r3(jE)},
 {c:'uncertain',p:r3([DIYAR,[39.6,37.98],SAMSAT])},
 {c:'approx',p:r3(jNW)}
];
// Iraq (Sawad): offset margins
const offs=(p,dx)=>p.map(c=>[c[0]+dx,c[1]]);
const eI=thin(sub(Eo,HIT,QURNA),2), tI=thin(sub(To,TIKRIT,QURNA),2);
const IRAQ=[
 {c:'uncertain',p:r3([[HIT[0]-0.35,HIT[1]+0.05],[TIKRIT[0]+0.2,TIKRIT[1]+0.1]])},
 {c:'uncertain',p:r3([[TIKRIT[0]+0.2,TIKRIT[1]+0.1],...tI.slice(1).map(c=>[Math.min(c[0]+(c[1]>32.8?0.45:0.3),c[1]<31.2?47.75:99),c[1]])])},
 {c:'sea',p:r3([[47.75,30.8],[48.5,30.05],[48.9,29.8],[47.5,30.1]])},
 {c:'uncertain',p:r3([[47.5,30.1],[47.05,30.8],...eI.slice().reverse().map(c=>[c[0]-0.35,c[1]]),[HIT[0]-0.35,HIT[1]+0.05]])}
];
// Misr core: Nile ribbon Aswan..Cairo(30.0) + Delta
let N=NILE.filter(c=>c[1]>=24.0&&c[1]<=30.0); N=orient(N,[32.9,24.1]); N=thin(N,3);
const off=(p,d)=>p.map((c,i)=>{const a=p[Math.max(0,i-1)],b=p[Math.min(p.length-1,i+1)];let dx=(b[0]-a[0])*Math.cos(c[1]*Math.PI/180),dy=b[1]-a[1];const L=Math.hypot(dx,dy)||1;const nx=-dy/L,ny=dx/L;return [c[0]+nx*d/Math.cos(c[1]*Math.PI/180),c[1]+ny*d];});
const ribbon=[...off(N,0.1),...off(N,-0.1).reverse()];
const MISR_CORE=[ {c:'approx',p:r3([...ribbon,ribbon[0]])} ];
const DELTA=[ {c:'sea',p:r3([[31.2,30.0],[30.6,30.4],[30.0,31.0]])},{c:'sea',p:r3([[30.0,31.0],[30.4,31.75],[31.1,31.95],[31.8,31.85],[32.4,31.6]])},{c:'approx',p:r3([[32.4,31.6],[32.3,30.9],[31.9,30.3],[31.2,30.0]])} ];
fs.writeFileSync('src/generated.json',JSON.stringify({UPPER,IRAQ,MISR_CORE,DELTA}));
console.log('generated', JSON.stringify({UPPER:UPPER.map(r=>r.p.length),IRAQ:IRAQ.map(r=>r.p.length),MISR:MISR_CORE[0].p.length}));
console.log('Nile ribbon sample', JSON.stringify(N.slice(0,3)), N.length);
