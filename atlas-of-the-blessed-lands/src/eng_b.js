/* ================= v4 engine, part B: projection, scaffold, regions ================= */
const proj = d3.geoMercator().fitSize([1000,1000], {type:"MultiPoint", coordinates:[[27,9],[61,41]]});
const P = ll => proj(ll);
const gp = d3.geoPath(proj);
/* the map sheet: everything the base map covers */
const SHEET = {w:-30, s:-36.5, e:104, n:60};   /* the Atlantic to Burma, the Cape of Good Hope to the Baltic: v35 added the south so the whole of Africa sits inside the Natural borders outline */
const SHEET_NW = () => P([SHEET.w, SHEET.n]), SHEET_SE = () => P([SHEET.e, SHEET.s]);
const lineD = pts => "M" + pts.map(p=>P(p).map(v=>v.toFixed(2)).join(",")).join("L");
const ringD = pts => lineD(pts) + "Z";
const runsRing = runs => { const out=[]; runs.forEach((r,i)=>r.p.forEach((pt,j)=>{ if(i>0&&j===0) return; out.push(pt); })); return out; };
const circleRing = (c, km) => d3.geoCircle().center(c).radius(km/111.32).precision(4)().coordinates[0];

/* The base map (coasts, borders, rivers, lakes, deserts) is projected once, arc by arc, and then drawn as flat lines.
   Drawing it straight from longitude and latitude projected every shared border twice and ran the globe-curve and
   clipping steps on every point; the lines that come out are the same. */
const geoP = (()=>{ const t = geo.transform, sx = t ? t.scale[0] : 1, sy = t ? t.scale[1] : 1, tx = t ? t.translate[0] : 0, ty = t ? t.translate[1] : 0;
  return {type:'Topology', objects:geo.objects, arcs:geo.arcs.map(arc=>{ let x = 0, y = 0;
    return arc.map(p=>{ if(t){ x += p[0]; y += p[1]; } else { x = p[0]; y = p[1]; } return proj([x*sx + tx, y*sy + ty]); }); })}; })();
const gpP = d3.geoPath();   /* for shapes already projected */
const countries = topojson.feature(geoP, geoP.objects.countries);
const land = topojson.merge(geoP, geoP.objects.countries.geometries);
const arabLand = topojson.merge(geoP, geoP.objects.countries.geometries.filter(g=>ARAB_IDS.includes(String(g.id))));
const borders = topojson.mesh(geoP, geoP.objects.countries, (a,b)=>a!==b);
const lakes = topojson.feature(geoP, geoP.objects.lakes);
const rivers = topojson.feature(geoP, geoP.objects.rivers);
const deserts = topojson.feature(geoP, geoP.objects.deserts);
const disputed = topojson.feature(geoP, geoP.objects.disputed);
const LAND_D = gpP(land);
document.getElementById('landP').setAttribute('d', LAND_D);
const landLo = topojson.merge(geoLo, geoLo.objects.countries.geometries);
const bordersLo = topojson.mesh(geoLo, geoLo.objects.countries, (a,b)=>a!==b);

/* ---------------- main map scaffold ---------------- */
const svg = d3.select('#map');
const wrapEl = document.getElementById('mapwrap');
const sdefs = svg.append('defs');
/* the main map has its own copy of the land outline (landMP), so it can be swapped for coarser copies while zoomed out;
   the detail maps keep using the full one (landP) */
const landMP = sdefs.append('path').attr('id','landMP').attr('d', LAND_D);
sdefs.append('clipPath').attr('id','landclip').append('use').attr('href','#landMP');
sdefs.append('path').attr('id','landLoP').attr('d', gp(landLo));
sdefs.append('clipPath').attr('id','arabclip').append('path').attr('d', gpP(arabLand));
svg.append('rect').attr('width','100%').attr('height','100%').attr('fill','var(--sea)');
const world = svg.append('g');
/* engraved water lines: a thin ring of darker water at three distances from every coast, outermost first */
/* they follow a simplified coastline (much cheaper to stroke) and are drawn only at the smaller scales */
const gWL = world.append('g').attr('class','wlg');
[[20,'w2'],[9,'w1']].forEach(([w,c])=>{
  gWL.append('use').attr('href','#landLoP').attr('class','wl '+c).style('stroke-width', w+'px');
  gWL.append('use').attr('href','#landLoP').attr('class','wlm').style('stroke-width', (w-1.3)+'px');
});
gWL.append('use').attr('href','#landLoP').attr('class','coastglow g1');
world.append('use').attr('href','#landMP').attr('class','land');
const r0 = SHEET_NW(), r1 = SHEET_SE();   /* relief covers the whole sheet, in Mercator rows */
const gRelief = world.append('g').attr('data-layer','relief');
/* the relief image's edges fade to neutral grey (no effect under the overlay blend), so it meets the flat land beyond 8°N and 26°E without a seam */
/* no clip: the relief's sea is neutral grey, which the overlay blend leaves unchanged, and a clip on this many points is costly to paint */
const RELIEF_W = r1[0]-r0[0], RELIEF_PX = 2680;   /* the relief picture is 2680 pixels wide and covers the whole sheet */
const reliefImg = gRelief.append('image').attr('class','relief').attr('href', RELIEF).attr('x', r0[0]).attr('y', r0[1]).attr('width', r1[0]-r0[0]).attr('height', r1[1]-r0[1]).attr('preserveAspectRatio','none');
world.append('g').attr('data-layer','desert').selectAll('path').data(deserts.features).join('path').attr('class','desert').attr('d', gpP);
const gCountries = world.append('g').attr('data-layer','modern');
gCountries.selectAll('path').data(countries.features).join('path').attr('class','country').attr('d', gpP)
  .on('click', (e,d)=>{ e.stopPropagation(); showInfo('modern', d.properties.n); markSel(null); openSheet('infocard'); })
  .append('title').text(d=>d.properties.n);
world.append('g').selectAll('path').data(rivers.features).join('path').attr('class','river').attr('d', gpP);
const gLava = world.append('g').attr('data-layer','lava');
LAVA.forEach(l=>gLava.append('path').attr('class','lavaf').attr('data-sel','lava').attr('d', ringD(l.p)).on('click', e=>{ e.stopPropagation(); select('lava'); }).append('title').text(l.n+' (approximate)'));
const gFill = world.append('g').attr('clip-path','url(#landclip)');
world.append('g').selectAll('path').data(lakes.features).join('path').attr('class','lake').attr('d', gpP);
const gGrat = world.append('g').attr('data-layer','graticule').style('pointer-events','none');
const gratPath = gGrat.append('path').attr('class','grat');
/* borders: a simplified line at small scales, the full line close in (swapped in render) */
const BORD = {full: gpP(borders), lo: gp(bordersLo), cur: null, els: null};
{ const gb = world.append('g').attr('data-layer','modern'); BORD.els = [gb.append('path').attr('class','mborder-halo'), gb.append('path').attr('class','mborder')]; }
/* Close in, the browser pays for a long dashed line along its whole length, even the part far off screen: the border
   mesh alone took seconds per frame at the scale of the ḥarams. So above zoom 4 the borders and the outlines are
   redrawn as just the stretch near the view (see render). Lines are projected once and clipped as straight segments. */
const projLines = lines => lines.map(r=>{ const a = new Float64Array(r.length*2); r.forEach((c,i)=>{ const p = P(c); a[2*i]=p[0]; a[2*i+1]=p[1]; }); return a; });
function clipD(lines, x0, y0, x1, y1){
  let out = ''; const f = v => v.toFixed(3);
  const code = (x,y)=> (x<x0?1:x>x1?2:0) | (y<y0?4:y>y1?8:0);
  for(const a of lines){
    let pen = false;
    for(let i=0; i+3<a.length; i+=2){
      const ax=a[i], ay=a[i+1], bx=a[i+2], by=a[i+3], ca=code(ax,ay), cb=code(bx,by);
      if(ca & cb){ pen = false; continue; }
      if(!(ca|cb)){ if(!pen){ out += 'M'+f(ax)+','+f(ay); pen = true; } out += 'L'+f(bx)+','+f(by); continue; }
      const dx=bx-ax, dy=by-ay; let t0=0, t1=1, ok=true;
      for(const [pp,q] of [[-dx,ax-x0],[dx,x1-ax],[-dy,ay-y0],[dy,y1-ay]]){
        if(pp===0){ if(q<0){ ok=false; break; } continue; }
        const r = q/pp; if(pp<0){ if(r>t1){ ok=false; break; } if(r>t0) t0=r; } else { if(r<t0){ ok=false; break; } if(r<t1) t1=r; }
      }
      if(!ok){ pen = false; continue; }
      if(t0>0 || !pen) out += 'M'+f(ax+t0*dx)+','+f(ay+t0*dy);
      out += 'L'+f(ax+t1*dx)+','+f(ay+t1*dy);
      pen = t1 === 1;
    }
  }
  return out;
}
/* Very close in (al-Aqṣā, the ḥarams) every other path is cut to the area near the view as well: the browser otherwise
   walks every vertex of the coast, the regions and the land clip on every frame, at coordinates hundreds of thousands
   of pixels wide. Paths are read back from their own d strings (M, L and Z only); anything else is left alone. */
function parseD(d){
  if(!d || /[^MLZ0-9.,\-\se]/.test(d)) return null;
  const rings = []; let cur = null; const re = /([MLZ])([^MLZ]*)/g; let m;
  while((m = re.exec(d))){
    if(m[1] === 'Z'){ if(cur) cur.z = true; continue; }
    if(m[1] === 'M'){ cur = {p:[], z:false}; rings.push(cur); }
    if(!cur) return null;
    const nums = m[2].split(/[ ,]+/); for(const v of nums) if(v !== '') cur.p.push(+v);
  }
  return rings.map(r=>{ const a = Float64Array.from(r.p); let x0=Infinity, y0=Infinity, x1=-Infinity, y1=-Infinity;
    for(let i=0;i<a.length;i+=2){ const x=a[i], y=a[i+1]; if(x<x0) x0=x; if(x>x1) x1=x; if(y<y0) y0=y; if(y>y1) y1=y; }
    return {a, z:r.z, bb:[x0,y0,x1,y1]}; });
}
function clipRing(a, x0, y0, x1, y1){   /* Sutherland–Hodgman against the box */
  let pts = Array.from(a);
  const n0 = pts.length; if(n0 >= 4 && pts[0] === pts[n0-2] && pts[1] === pts[n0-1]) pts.length = n0 - 2;
  for(const [ax, val, sg] of [[0,x0,1],[0,x1,-1],[1,y0,1],[1,y1,-1]]){
    const n = pts.length/2; if(!n) break; const out = [];
    const inside = (x,y)=> sg*((ax ? y : x) - val) >= 0;
    for(let i=0;i<n;i++){
      const cx = pts[2*i], cy = pts[2*i+1], j = (i+n-1)%n, px = pts[2*j], py = pts[2*j+1];
      const ci = inside(cx,cy), pi = inside(px,py);
      if(ci !== pi){ const t = ((ax ? py : px) - val)/((ax ? py - cy : px - cx) || 1e-12); out.push(px + t*(cx-px), py + t*(cy-py)); }
      if(ci) out.push(cx, cy);
    }
    pts = out;
  }
  return pts;
}
function clipPathD(rings, x0, y0, x1, y1){
  const f = v => v.toFixed(3); let out = '';
  for(const r of rings){
    const b = r.bb;
    if(b[2] < x0 || b[0] > x1 || b[3] < y0 || b[1] > y1) continue;   /* wholly outside */
    if(b[0] >= x0 && b[2] <= x1 && b[1] >= y0 && b[3] <= y1){   /* wholly inside: as drawn */
      out += 'M' + f(r.a[0]) + ',' + f(r.a[1]); for(let i=2;i<r.a.length;i+=2) out += 'L' + f(r.a[i]) + ',' + f(r.a[i+1]); if(r.z) out += 'Z'; continue; }
    if(r.z){ const p = clipRing(r.a, x0, y0, x1, y1); if(p.length < 6) continue;
      out += 'M' + f(p[0]) + ',' + f(p[1]); for(let i=2;i<p.length;i+=2) out += 'L' + f(p[i]) + ',' + f(p[i+1]); out += 'Z'; }
    else out += clipD([r.a], x0, y0, x1, y1);
  }
  return out;
}
/* Level of detail. The land outline has about 52,000 points, far more than the screen can show when zoomed out, and
   the browser walks every one of them each time the map is redrawn (as the fill, the stroke and the clip for every
   region). So coarser copies are drawn at small scales; each keeps the shape to within about a third of a pixel at the
   largest scale it is used at. Douglas-Peucker on every ring; a ring smaller than the tolerance disappears. */
function simplifyD(d, eps){
  const rings = parseD(d); if(!rings) return d;
  let out = ''; const f = v => v.toFixed(2), e2 = eps*eps;
  for(const r of rings){
    const a = r.a, n = a.length/2, b = r.bb; if(n < 3 || Math.max(b[2]-b[0], b[3]-b[1]) < eps) continue;
    const keep = new Uint8Array(n); keep[0] = keep[n-1] = 1; const st = [0, n-1];
    while(st.length){
      const j = st.pop(), i = st.pop(); if(j - i < 2) continue;
      const ax = a[2*i], ay = a[2*i+1], dx = a[2*j]-ax, dy = a[2*j+1]-ay, L2 = dx*dx + dy*dy; let md = -1, mi = -1;
      for(let k = i+1; k < j; k++){ const px = a[2*k]-ax, py = a[2*k+1]-ay; let d2;
        if(L2 === 0) d2 = px*px + py*py; else { let t = (px*dx + py*dy)/L2; t = t < 0 ? 0 : t > 1 ? 1 : t; const qx = px - t*dx, qy = py - t*dy; d2 = qx*qx + qy*qy; }
        if(d2 > md){ md = d2; mi = k; } }
      if(md > e2){ keep[mi] = 1; st.push(i, mi, mi, j); }
    }
    let s = '', c = 0; for(let i = 0; i < n; i++) if(keep[i]){ s += (c ? 'L' : 'M') + f(a[2*i]) + ',' + f(a[2*i+1]); c++; }
    if(c >= (r.z ? 3 : 2)) out += s + (r.z ? 'Z' : '');
  }
  return out;
}
/* used below k 0.6, below k 1.5, and from there on; each coarse copy is made the first time it is needed, and the
   other one a moment after the page has settled, so opening the page does not wait for both */
const LAND_EPS = [0.8, 0.3], LAND_LODC = [null, null, LAND_D];
const landLOD = lv => LAND_LODC[lv] || (LAND_LODC[lv] = simplifyD(LAND_D, LAND_EPS[lv]));
const whenIdle = f => (window.requestIdleCallback ? requestIdleCallback(f, {timeout:4000}) : setTimeout(f, 1500));
let landLv = 2, VIEW_SET = false;   /* VIEW_SET: the opening view is in place, so the right coarse coastline can be chosen */
const CLIPS = [];   /* {els, lines(), full(), key()}: strokes swapped for their clipped stretch close in */
CLIPS.push({els: BORD.els, key: ()=> T.k < 2.2 ? 'lo' : 'full', full: ()=> BORD[T.k < 2.2 ? 'lo' : 'full'],
  lines: ()=> BORD.pl || (BORD.pl = borders.coordinates.map(r=>Float64Array.from(r.flat())))});   /* already projected */
const gDisp = world.append('g').attr('data-layer','disputed');
disputed.features.forEach(f=>gDisp.append('path').attr('class','dispfill').attr('d', gpP(f)).on('click', e=>{ e.stopPropagation(); showInfo('modern', f.properties.n); markSel(null); openSheet('infocard'); }).append('title').text(f.properties.n+' · '+f.properties.note));
const gEdges = world.append('g');
const gRoutes = world.append('g');
const gTop = world.append('g');
/* the edge of the map sheet: beyond the area the base map covers, show the page, not empty sea */
const gSheet = world.append('g').attr('class','sheetedge');
{ const outer = ringD([[-40,80],[130,80],[130,-60],[-40,-60]]);
  const inner = ringD([[SHEET.w,SHEET.s],[SHEET.w,SHEET.n],[SHEET.e,SHEET.n],[SHEET.e,SHEET.s]]);
  gSheet.append('path').attr('class','offsheet').attr('d', outer + inner).attr('fill-rule','evenodd'); }
const layerG = (parent, id) => parent.append('g').attr('data-layer', id);

function region(id, runs, colorVar, infoKey, title, parent){
  const fg = layerG(parent||gFill, id), eg = layerG(gEdges, id);
  fg.append('path').attr('class','rfill').attr('data-sel', infoKey).attr('d', ringD(runsRing(runs)))
    .style('fill', `var(${colorVar})`).on('click', e=>{ e.stopPropagation(); select(infoKey); }).append('title').text(title);
  runs.forEach(r=>{ if(r.c==='sea') return; eg.append('path').attr('class','edge c-'+r.c).attr('d', lineD(r.p)).style('stroke', `var(${colorVar})`); });
  return eg;
}
function coreEdge(id, core, outer, colorVar, hatch, infoKey, title){
  const cores = Array.isArray(core[0]) ? core : [core];
  const fg = layerG(gFill, id), eg = layerG(gEdges, id);
  const coreD = cores.map(c=>ringD(runsRing(c))).join('');
  fg.append('path').attr('class','hfill').attr('data-sel', infoKey).attr('d', ringD(runsRing(outer)) + coreD).attr('fill', `url(#${hatch})`)
    .on('click', e=>{ e.stopPropagation(); select(infoKey); }).append('title').text(title+' (included by some sources)');
  fg.append('path').attr('class','rfill').attr('data-sel', infoKey).attr('d', coreD).style('fill', `var(${colorVar})`)
    .on('click', e=>{ e.stopPropagation(); select(infoKey); }).append('title').text(title+' (included by every major source)');
  [outer].concat(cores).forEach((rs,i)=>rs.forEach(r=>{ if(r.c==='sea') return; eg.append('path').attr('class','edge c-'+(i===0?'uncertain':r.c)).attr('d', lineD(r.p)).style('stroke', `var(${colorVar})`).style('stroke-width', i===0?2:1.6); }));
}
region('jazirah', JAZIRAH, '--jaz', 'jazirah', 'Jazīrat al-ʿArab');
region('yemen', YEMEN, '--yemen', 'yemen', 'al-Yaman');
region('najd', NAJD, '--najd', 'najd', 'Najd (rough indication)');
region('bahrayn', BAHRAYN, '--bahr', 'bahrayn', 'al-Baḥrayn (rough indication)');
const gArab = gFill.append('g').attr('clip-path','url(#arabclip)');
region('tihamah', TIHAMAH, '--tiham', 'tihamah', 'Tihāmah (rough indication)', gArab);
region('rum', RUM, '--rum', 'rum', 'Bilād al-Rūm');
region('upper', UPPER, '--upper', 'upper', 'al-Jazīrah (Upper Mesopotamia)');
region('iraq', IRAQ, '--iraq', 'iraq', 'al-ʿIrāq and the Sawād');
coreEdge('misr', [MISR_CORE, DELTA], MISR_OUTER, '--misr', 'h-misr', 'misr', 'Miṣr');
coreEdge('sham', SHAM_CORE, SHAM_OUTER, '--sham', 'h-sham', 'sham', 'Bilād al-Shām');
const gAj = layerG(gFill, 'ajnad');
AJNAD.forEach(j=>{
  INFO['jund_'+j.id] = {title:j.name, ar:j.ar, src:["early","classical"], cert:"uncertain", body:j.body + `<p class="fine">Borders between the ajnād are schematic.</p>`, refs:INFO.ajnad.refs};
  gAj.append('path').attr('class','jund').attr('data-sel','jund_'+j.id).attr('d', ringD(j.ring)).style('fill',`var(${j.col})`).style('stroke',`var(${j.col})`)
    .on('click', e=>{ e.stopPropagation(); select('jund_'+j.id); }).append('title').text(j.name);
});
coreEdge('hijaz', HIJAZ_CORE, HIJAZ_OUTER, '--hijaz', 'h-hijaz', 'hijaz', 'al-Ḥijāz');
coreEdge('filastin', FIL_CORE, FIL_OUTER, '--fil', 'h-fil', 'filastin', 'Jund Filasṭīn');
layerG(gFill, 'filastin').append('path').attr('class','urd').attr('data-sel','filastin').attr('d', ringD(runsRing(URDUNN))).on('click', e=>{ e.stopPropagation(); select('filastin'); }).append('title').text('Jund al-Urdunn');
const gMuq = layerG(gFill, 'muq');
const gFiqh = layerG(gTop, 'hijazfiqh');
FIQH.forEach(f=>gFiqh.append('path').attr('class','circ').attr('data-sel','hijazfiqh').attr('d', ringD(circleRing(f.c,f.km))).on('click', e=>{ e.stopPropagation(); select('hijazfiqh'); }).append('title').text(f.n+' (district, illustrative size)'));
const CX = {};   /* elements of the user's outline, swapped by the version switch */
/* Dār al-Amān's natural line (your design; tools/nat_gen.js): one ring of coasts, rivers, cliffs, crests and watersheds round the whole
   Complete outline. Its territory is also a version of the outline: each polygon's ring is its coast and natural-boundary segments joined in order. */
const NAT = JSON.parse(document.getElementById('nat').textContent);
const NB_ALT = false;   /* the Libya variant was removed with the old line (Version 37) */
let NAT_BUILT = false;
let CLEAN = false;   /* "Clean map": while an outline is showing, the key, the outline's captions and markers, the scale, the compass and the coordinates are hidden */
let INTL_OFF = false;   /* the internal lines come on with the natural borders unless you switch them off there */
const inNat = () => !!layerOn.caliphx && XV === 'nat';   /* the natural-borders version is showing */
const XK = () => XV;   /* the key of the drawn version */
['main'].forEach(v=>{ const by = {}; NAT[v].lines.forEach(l=>{ const a = by[l.r] || (by[l.r] = []); for(let i = a.length ? 1 : 0; i < l.p.length; i++) a.push(l.p[i]); }); NAT[v].polys = Object.values(by).map(r=>[r]); });
const NAT_B = [[-18.5,-3.5],[83.0,46.5]];   /* the whole ring, from Saint-Louis to Kailash and from the Danube to the Tana, with a margin */
/* thought experiment: one outline around every best land (my synthesis) */
{
  const d = CALIPH.polys.map(poly=>poly.map(rg=>ringD(rg)).join('')).join('');
  sdefs.append('clipPath').attr('id','caliphclip').append('path').attr('d', d);
  const g = layerG(gEdges, 'caliph');
  const open = e=>{ e.stopPropagation(); select('caliph'); };
  const cb = g.append('g').attr('clip-path','url(#caliphclip)').append('path').attr('class','caliph-band').attr('data-sel','caliph').attr('d', d).on('click', open);
  cb.append('title').text('One outline around every best land (my synthesis)');
  const cl = g.append('g').attr('clip-path','url(#landclip)').append('path').attr('class','caliph-line').attr('d', d);
  let bl = null; CLIPS.push({els:[cb, cl], key:()=>'', full:()=>d, lines:()=> bl || (bl = projLines(CALIPH.polys.flat()))});
  /* the user's expanded outline: their specification, not from the sources; two versions share one set of elements */
  const dOf = o => o.polys.map(poly=>poly.map(rg=>ringD(rg)).join('')).join('');
  /* each version's path is built the first time it is shown, not all seven at startup */
  const dx = dOf(CALIPH.x); CX.d = {full:dx};
  const lazyD = (k, f) => Object.defineProperty(CX.d, k, {configurable:true, enumerable:true, get(){ const v = f(); Object.defineProperty(CX.d, k, {value:v, enumerable:true}); return v; }});
  lazyD('west', ()=>dOf(CALIPH.xw)); lazyD('gme', ()=>dOf(CALIPH.g)); lazyD('v2', ()=>dOf(CALIPH.v2)); lazyD('nat', ()=>dOf(NAT.main)); lazyD('natp', ()=>dOf(NAT.pol)); lazyD('v3', ()=>dOf(CALIPH.x3));
  CX.clip = sdefs.append('clipPath').attr('id','caliphxclip').append('path').attr('d', dx);
  const gx = layerG(gEdges, 'caliphx');
  const openx = e=>{ e.stopPropagation(); select('caliphx'); };
  CX.band = gx.append('g').attr('clip-path','url(#caliphxclip)').append('path').attr('class','caliphx-band').attr('data-sel','caliphx').attr('d', dx).on('click', openx);
  CX.band.append('title').text('Your outline (your specification, not from the sources)');
  CX.line = gx.append('g').attr('clip-path','url(#landclip)').append('path').attr('class','caliphx-line').attr('d', dx);
  gEdges.node().insertBefore(gx.node(), g.node());
  const xl = {}, src = {full:CALIPH.x, west:CALIPH.xw, gme:CALIPH.g, v2:CALIPH.v2};
  src.nat = NAT.main; src.natp = NAT.pol; src.v3 = CALIPH.x3;
  /* in the natural-borders version the band runs only along the land stretches of the ring: a wide clipped band along every coast
     inside the ring (the Red Sea, the Gulf, the Aegean) made zooming there several times slower, and the coast has its own line */
  const natLand = NAT.main.lines.filter(l=>l.k !== 'coast').map(l=>l.p);
  lazyD('natband', ()=>natLand.map(p=>lineD(p)).join(''));
  const BK = () => XK() === 'nat' ? 'natband' : XK();
  CLIPS.push({els:[CX.band], key:BK, full:()=>CX.d[BK()], lines:()=> xl[BK()] || (xl[BK()] = BK() === 'natband' ? projLines(natLand) : projLines(src[XK()].polys.flat()))});
  CLIPS.push({els:[CX.line], key:()=>XK(), full:()=>CX.d[XK()], lines:()=> xl[XK()] || (xl[XK()] = projLines(src[XK()].polys.flat()))});
  /* the Greater Caliphate is drawn by the same elements in the core's colour (see setXV), so it reads as one territory */
  /* a faint wash over the land inside your outline, under every other colour */
  const gw = layerG(gFill, 'caliphx'); gFill.node().insertBefore(gw.node(), gFill.node().firstChild);
  CX.wash = gw.append('path').attr('class','caliphx-wash').attr('d', dx);
  /* Complete Caliphate V2: the province history shading is not drawn since Version 41 (Nawaz: V2 in the same neutral colour as Complete and Greater);
     the history stays in the notes, and the page carries only each province's box (see build.js), so the layer is no longer built (Version 47) */
}
/* ---------- Dār al-Amān: natural borders and internal lines (your design, 2026-10-07; see tools/nat_gen.js) ----------
   (no wide halo or glow strokes under these lines: on a long line they doubled the cost of every redraw)
   Overlays you switch on over any version of the outline. Every land stretch of the ring (river, crest, watershed, escarpment,
   lake shore) is drawn the same, as one natural boundary; where the ring runs at sea, the coast is drawn. */
/* drawn the first time either overlay is switched on (see applyLayers), so opening the page does not pay for them */
function buildNat(){ if(NAT_BUILT) return; NAT_BUILT = true;
  const openN = e=>{ e.stopPropagation(); select('natb'); }, openI = e=>{ e.stopPropagation(); select('intl'); };
  const clipPathEl = (g, cls, lines) => { const d = lines.map(p=>lineD(p)).join(''); const el = g.append('path').attr('class', cls).attr('d', d);
    let pl = null; CLIPS.push({els:[el], key:()=>'', full:()=>d, lines:()=> pl || (pl = projLines(lines))}); return el; };
  const gN = world.append('g').attr('data-layer','natbAny');
  { const g = layerG(gN, 'natbMain'), by = {coast:[], solid:[]};
    NAT.main.lines.forEach(l=>by[l.k === 'coast' ? 'coast' : 'solid'].push(l.p));   /* every land stretch is the one natural-boundary line; the Balkan piece is a ring of its own, so the kind decides, not the ring */
    /* the coasts are not drawn again: the map's own coastline is the edge there, and a second line along every coast inside the ring
       (the Red Sea, the Gulf, the Aegean islands) made zooming several times slower */
    clipPathEl(g, 'nat-solid', by.solid);
    const hit = clipPathEl(g, 'route-hit nat-hit', by.solid).style('pointer-events','stroke').on('click', openN);
    hit.append('title').text('The natural ring of Dār al-Amān · your design'); }
  /* internal lines: the Taurus divide, the three rivers, the Red Sea as the axis */
  const gI = world.insert('g', ()=>gN.node()).attr('data-layer','intlAny');   /* under the ring, which runs along the Victoria Nile */
  NAT.intl.rivers.forEach(r=>{ clipPathEl(gI, 'intl-river', r.p).append('title').text(`${r.n} · a core waterway`);
    clipPathEl(gI, 'route-hit', r.p).style('pointer-events','stroke').on('click', openI).append('title').text(`${r.n} · a core waterway`); });
  clipPathEl(gI, 'intl-taurus', [NAT.intl.taurus]);
  clipPathEl(gI, 'route-hit', [NAT.intl.taurus]).style('pointer-events','stroke').on('click', openI).append('title').text('Taurus Mountains: the Anatolia · Levant · Mesopotamia divide');
  clipPathEl(gI, 'intl-axis', [NAT.intl.redsea]);
  clipPathEl(gI, 'route-hit', [NAT.intl.redsea]).style('pointer-events','stroke').on('click', openI).append('title').text('The Red Sea: the central axis joining the African and Arabian halves');
}
const gHaram = layerG(gTop, 'haram');
gHaram.append('path').attr('class','haramfill').attr('data-sel','makkah').attr('d', ringD(MAKKAH_HARAM)).on('click', e=>{ e.stopPropagation(); select('makkah'); }).append('title').text('Ḥaram of Makkah (approximate outline)');
gHaram.append('path').attr('class','haramfill').attr('data-sel','madinah').attr('d', ringD(MADINAH_HARAM)).on('click', e=>{ e.stopPropagation(); select('madinah'); }).append('title').text('Ḥaram of Madinah (approximate outline)');
layerG(gTop, 'aqsa').append('path').attr('class','aqsa').attr('data-sel','aqsa').attr('d', ringD(AQSA_ENCL)).on('click', e=>{ e.stopPropagation(); select('aqsa'); }).append('title').text('Enclosure of al-Masjid al-Aqṣā (approximate)');
/* al-Aḥqāf: three reports, three rings */
const gSaba = layerG(gTop, 'saba');
AHQAF.forEach(a=>gSaba.append('path').attr('class','ring3').attr('data-sel','ahqaf').attr('d', ringD(circleRing(a.c, a.km))).on('click', e=>{ e.stopPropagation(); select('ahqaf'); }).append('title').text(`al-Aḥqāf: ${a.n} says ${a.s} (illustrative size)`));
/* ʿAmuq plain, loosely */
const gEsch = layerG(gTop, 'eschat');
gEsch.append('path').attr('class','ring3 esc').attr('data-sel','eg_amaq').attr('d', ringD(circleRing([36.32,36.38], 24))).on('click', e=>{ e.stopPropagation(); select('eg_amaq'); }).append('title').text('al-Aʿmāq (the ʿAmuq plain, loosely)');
/* al-Isrāʾ line (schematic) */
const gLinks = layerG(gTop, 'links');
gLinks.append('path').attr('class','isra').attr('d', gp({type:"LineString", coordinates:[QIBLA.makkah, QIBLA.aqsa]})).attr('data-sel','isra').style('pointer-events','none');
gLinks.append('path').attr('class','route-hit').attr('d', gp({type:"LineString", coordinates:[QIBLA.makkah, QIBLA.aqsa]})).style('pointer-events','stroke').on('click', e=>{ e.stopPropagation(); select('isra'); }).append('title').text('al-Isrāʾ (schematic)');
Object.values(ROUTES).forEach(r=>{
  const g = layerG(gRoutes, r.cls);
  g.append('path').attr('class','route '+r.cls).attr('data-sel', r.info).attr('d', lineD(r.pts));
  g.append('path').attr('class','route-hit').attr('d', lineD(r.pts)).style('pointer-events','stroke').on('click', e=>{ e.stopPropagation(); select(r.info); }).append('title').text(r.name+' (approximate)');
});
{ const g = layerG(gRoutes, 'trade');
  g.append('path').attr('class','route trade saba-r').attr('data-sel','saba').attr('d', lineD(SABA_ROUTE));
  g.append('path').attr('class','route-hit').attr('d', lineD(SABA_ROUTE)).style('pointer-events','stroke').on('click', e=>{ e.stopPropagation(); select('saba'); }).append('title').text('Road from Maʾrib toward al-Shām (approximate)'); }

/* muqaddasah views */
let muqView = "tabari";
const muqLabels = [];
function drawMuq(){
  gMuq.selectAll('*').remove(); muqLabels.length = 0;
  const add = (d, cls, title) => gMuq.append('path').attr('class','muqfill '+(cls||'')).attr('data-sel','muq').attr('d', d).on('click', e=>{ e.stopPropagation(); select('muq'); }).append('title').text(title);
  if(muqView==="tabari"){ add(ringD(runsRing(SHAM_OUTER)),'partial',"al-Ṭabarī: somewhere between the Euphrates and al-ʿArīsh"); muqLabels.push(["somewhere between the Euphrates and al-ʿArīsh (al-Ṭabarī)",37.4,31.4,0]); }
  if(muqView==="qatadah"){ add(ringD(runsRing(SHAM_CORE)),'','al-Arḍ al-Muqaddasah: al-Shām (Qatādah)'); muqLabels.push(["al-Shām (Qatādah)",36.6,32.6,0]); }
  if(muqView==="kalbi"){ add(ringD(runsRing(FIL_CORE)),'','Filasṭīn (al-Kalbī)'); add(ringD(runsRing(URDUNN)),'partial','part of al-Urdunn (al-Kalbī); which part is not specified'); add(ringD(circleRing([36.29,33.51],30)),'','Dimashq (al-Kalbī); city or district not specified'); muqLabels.push(["Filasṭīn",34.85,31.2,0],["part of al-Urdunn",35.7,32.75,1.4],["Dimashq",36.3,33.15,1.4]); }
  if(muqView==="dahhak"){ add(ringD(circleRing([35.235,31.777],7)),'','Īliyāʾ and Bayt al-Maqdis (al-Ḍaḥḥāk)'); muqLabels.push(["Īliyāʾ · Bayt al-Maqdis",35.31,31.70,6]); }
  if(muqView==="ikrimah"){ add(ringD(circleRing([35.444,31.857],7)),'','Arīḥāʾ (ʿIkrimah, al-Suddī)'); muqLabels.push(["Arīḥāʾ (Jericho)",35.52,31.80,6]); }
  if(muqView==="mujahid"){ muqLabels.push(["Mujāhid's view is not drawn: the report does not say which mountain",35.3,30.4,1.2]); }
  buildOverlay(); applyLayers();
}
