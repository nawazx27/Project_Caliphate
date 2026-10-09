/* Natural borders of Dār al-Amān (your design, 2026-10-07) -> src/nat.json
   The line is assembled from: country borders that follow a crest, river or watershed (Russia–Georgia/Azerbaijan on the
   Greater Caucasus, Iran–Turkmenistan on the Atrek and Kopet Dag, Uganda–Kenya, Uganda/South Sudan–DR Congo and South
   Sudan–Central African Republic on the Nile–Congo watershed); the edges of named ranges in Natural Earth's geography
   regions (the Ogo range, the Ethiopian Highlands, Jebel Marra, Ennedi, Tibesti, Ahaggar); and hand-placed waypoints
   elsewhere. Where the line meets the sea the coast itself is the border: the territory is the land inside the line,
   and the Red Sea and the Gulf (with the Gulf of Oman) are joined to it as inner seas, closed at Bāb al-Mandab and at
   the mouth of the Gulf of Oman. Run: node tools/nat_gen.js   (about 20 s)                                           */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const REG = JSON.parse(fs.readFileSync(path.join(ROOT, 'regions.geojson'))).features;
const R3 = v => Math.round(v*1000)/1000;

/* ---------- helpers ---------- */
const C = geo.objects.countries.geometries;
const byId = id => C.find(g => String(g.id) === id);
const border = (a, b) => {   /* the shared border of two countries, stitched into one ordered line */
  const m = topojson.mesh(geo, geo.objects.countries, (x, y) => (String(x.id) === a && String(y.id) === b) || (String(x.id) === b && String(y.id) === a));
  const lines = m.coordinates.map(l => l.slice());
  if(!lines.length) throw new Error('no border ' + a + '-' + b);
  const D = (p, q) => Math.hypot(p[0]-q[0], p[1]-q[1]);
  let out = lines.shift();
  while(lines.length){
    let best = null;
    lines.forEach((l, i) => { const s0 = out[0], e0 = out[out.length-1], ls = l[0], le = l[l.length-1];
      [[D(e0, ls), 'end', l], [D(e0, le), 'end', l.slice().reverse()], [D(s0, le), 'start', l], [D(s0, ls), 'start', l.slice().reverse()]]
        .forEach(([d, side, ll]) => { if(!best || d < best.d) best = {d, side, ll, i}; }); });
    lines.splice(best.i, 1);
    out = best.side === 'end' ? out.concat(best.ll) : best.ll.concat(out);
  }
  return out;
};
const nearest = (line, p) => { let bi = 0, bd = Infinity; line.forEach((q, i) => { const d = Math.hypot(q[0]-p[0], (q[1]-p[1])); if(d < bd){ bd = d; bi = i; } }); return bi; };
const part = (line, from, to) => { const i = nearest(line, from), j = nearest(line, to); return i <= j ? line.slice(i, j+1) : line.slice(j, i+1).reverse(); };
const regRing = name => { const f = REG.find(f => f.properties.NAME === name); if(!f) throw new Error('no region ' + name);
  const g = f.geometry; return g.type === 'Polygon' ? g.coordinates[0] : g.coordinates.reduce((a, p) => p[0].length > a.length ? p[0] : a, []); };
const ringPart = (ring, from, to) => {   /* walk a closed ring forward from the vertex nearest 'from' to the one nearest 'to' */
  const r = ring.slice(0, -1), i = nearest(r, from), j = nearest(r, to), out = [];
  for(let k = i; ; k = (k+1) % r.length){ out.push(r[k]); if(k === j) break; }
  return out;
};
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * 6371.0088**2);
const ptIn = (p, ring) => { let c = false; for(let i = 0, j = ring.length-1; i < ring.length; j = i++){ const a = ring[i], b = ring[j];
  if(((a[1] > p[1]) !== (b[1] > p[1])) && (p[0] < (b[0]-a[0]) * (p[1]-a[1]) / (b[1]-a[1]) + a[0])) c = !c; } return c; };
const inPoly = (p, poly) => ptIn(p, poly[0]) && !poly.slice(1).some(h => ptIn(p, h));
const inMP = (p, mp) => mp.some(poly => inPoly(p, poly));
const segDist = (p, a, b) => { const dx = b[0]-a[0], dy = b[1]-a[1], L = dx*dx + dy*dy; let t = L ? ((p[0]-a[0])*dx + (p[1]-a[1])*dy) / L : 0; t = Math.max(0, Math.min(1, t));
  return Math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy); };
const onLine = (p, line, eps) => { for(let i = 0; i+1 < line.length; i++) if(segDist(p, line[i], line[i+1]) < eps) return true; return false; };
function rdp(pts, eps){ if(pts.length < 3) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length-1] = 1; const st = [[0, pts.length-1]];
  while(st.length){ const [i, j] = st.pop(); let md = -1, mi = -1; for(let k = i+1; k < j; k++){ const d = segDist(pts[k], pts[i], pts[j]); if(d > md){ md = d; mi = k; } }
    if(md > eps){ keep[mi] = 1; st.push([i, mi], [mi, j]); } }
  return pts.filter((_, i) => keep[i]); }

/* ---------- the base land ---------- */
const land = topojson.merge(geo, geo.objects.countries.geometries).coordinates;
const lakeF = topojson.feature(geo, geo.objects.lakes).features;
const victoria = lakeF.find(f => /Victoria/.test(JSON.stringify(f.properties)));
if(!victoria) throw new Error('no Lake Victoria');
const victoriaMP = victoria.geometry.type === 'Polygon' ? [victoria.geometry.coordinates] : victoria.geometry.coordinates;
const landNoVic = pc.difference(land, victoriaMP);
/* European Turkey (Thrace) is cut off at the straits */
const tur = topojson.feature(geo, byId('792')).geometry;
const turPolys = tur.type === 'Polygon' ? [tur.coordinates] : tur.coordinates;
const thrace = turPolys.filter(p => { const xs = p[0].map(q => q[0]), ys = p[0].map(q => q[1]); return Math.min(...ys) > 40.0 && Math.max(...xs) < 29.4 && Math.max(...xs) - Math.min(...xs) > 1; });
console.log('Thrace pieces', thrace.length);

/* ---------- the line, clockwise from the Atlantic at the mouth of the Draa ---------- */
const B = {
  rus_geo: border('643', '268'), rus_aze: border('643', '031'), irn_tkm: border('364', '795'), uga_ken: border('800', '404'),
  uga_cod: border('800', '180'), ssd_cod: border('728', '180'), ssd_caf: border('728', '140')
};
const S = [];   /* segments: {k: kind, p: points, n: name} ; kind 'sea' is never drawn */
const seg = (k, n, p) => S.push({k, n, p});
const MAIN = [], ALT = [];
/* West: the Atlantic and the Mediterranean, offshore (the coast is the border) */
const seaWest = [[-11.6,28.95],[-13.2,30.6],[-10.6,33.6],[-7.0,35.62],[-5.6,35.97],[-4.0,36.05],[-2.0,36.25],[0.5,36.75],[3.5,37.15],[6.5,37.45],[8.8,37.66],[10.6,37.6],[11.6,37.25],[12.2,36.3],[13.0,35.3],[15.5,34.5],[18.6,33.9]];
const seaEast = [[20.0,33.9],[24.0,34.35],[27.0,35.2],[25.3,37.0],[25.3,38.6],[25.5,39.6],[26.05,40.2],
  /* through European Turkey, which is then cut away whole at the straits */
  [26.62,40.62],[27.5,41.2],[28.4,41.45],[29.0,41.95],
  /* the Black Sea, to the Caucasus near Anapa */
  [31.0,42.7],[34.0,43.5],[36.3,44.3],[36.95,44.62]];
const caucasusW = [[37.55,44.83],[37.95,44.68],[38.35,44.48],[38.85,44.30],[39.30,44.10],[39.75,43.95],[40.15,43.78]];
const geoCrest = part(B.rus_geo, [40.45,43.58], B.rus_geo[nearest(B.rus_geo, [46.6,41.85])]);
const azeCrest = part(B.rus_aze, [46.6,41.85], [47.75,41.33]);
const derbent = [[47.85,41.70],[47.95,41.98],[48.30,42.075]];
const caspian = [[48.65,42.2],[50.3,41.8],[51.8,40.6],[52.4,39.2],[52.9,38.0],[53.6,37.45]];
const atrekKopet = part(B.irn_tkm, [53.9,37.32], [58.0,38.0]);
const khorasan = [[57.9,37.6],[57.0,36.7],[56.1,35.6]];
const deserts = [[55.2,34.5],[55.0,34.0],[55.9,33.2],[57.2,32.3],[58.3,31.6],[59.0,31.0],[59.25,30.0],[59.15,28.9]];
const makran = [[59.0,28.3],[59.7,27.3],[60.4,26.5],[61.05,25.75],[61.55,25.3]];
const seaArab = [[61.75,24.9],[61.0,22.5],[59.0,18.5],[56.0,15.0],[53.3,13.15],[51.75,12.1],[51.6,11.95]];
const ogo = ringPart(regRing('Ogo Mts.'), [51.19,11.60], [44.55,9.88]);
const ethH = ringPart(regRing('ETHIOPIAN HIGHLANDS'), [43.18,9.43], [38.29,4.10]);
const rift = [[37.3,4.35],[36.05,4.5],[35.3,4.6],[34.4,4.25]];
const ugaKen = (() => { const l = part(B.uga_ken, [34.0,4.2], [34.0,0.1]); return l; })();
const lake = [[33.9,-0.35],[32.6,-0.5],[31.95,-0.4]];
const weakA = [[31.62,-0.25],[31.2,0.5],[30.75,1.15]];
const ugaCod = part(B.uga_cod, [30.55,1.5], [30.86,3.49]);
const ssdCod = part(B.ssd_cod, [30.86,3.49], B.ssd_cod[nearest(B.ssd_cod, [27.4,5.1])]);
const ssdCaf = (() => { const s = B.ssd_caf, a = nearest(s, [27.4,5.1]); const b = a < s.length/2 ? s.length-1 : 0; return a <= b ? s.slice(a, b+1) : s.slice(b, a+1).reverse(); })();
const marra = [[24.1,10.6],[24.0,11.8],[23.87,12.53],[23.50,13.41],[23.88,14.42],[23.9,15.3]];   /* along the west foot of Jebel Marra */
const ennediS = ringPart(regRing('Ennedi Plat.'), [23.75,16.19], [20.99,18.05]);
const tibesti = [[19.9,19.2]].concat(ringPart(regRing('TIBESTI MTS.'), [19.31,19.87], [15.68,22.23]));
const toAhaggar = [[13.9,22.6],[11.9,23.4]];
const ahaggar = ringPart(regRing('AHAGGAR MTS.'), [8.90,23.25], [1.07,24.85]);
const toDraa = [[0.2,25.8],[-1.4,26.8],[-3.0,27.5],[-4.4,28.1],[-5.8,29.7]];
const draa = [[-6.6,29.3],[-7.6,29.0],[-8.6,28.75],[-9.6,28.55],[-10.5,28.55],[-11.05,28.65]];
/* the Libya alternate: from Ennedi north along the Libyan Desert to the Gulf of Sirte */
const ennediNE = ringPart(regRing('Ennedi Plat.'), [24.26,17.74], [23.75,16.19]).reverse().slice(1);   /* the plateau's east side */   /* east side, north to the plateau's corner */
const libyan = [[24.3,19.6],[24.95,21.9],[25.55,22.8],[25.65,23.9],[25.2,25.0],[24.95,26.4],[24.85,27.8],[24.55,29.65],[23.2,29.5],[21.6,29.4],[20.2,29.75],[19.3,30.15],[18.85,30.3]];
const seaSirte = [[18.6,31.4]];

const FRONT = [   /* land segments with their kind, in order (the drawn border) */
  ['mountain', 'Greater Caucasus', [seaEast[seaEast.length-1]].concat(caucasusW, geoCrest, azeCrest)],
  ['fort', 'Derbent (Bāb al-Abwāb)', [azeCrest[azeCrest.length-1]].concat(derbent, [caspian[0]])],
  ['river', 'Atrek valley', [caspian[caspian.length-1]].concat(atrekKopet.filter(p => p[0] < 55.6))],
  ['mountain', 'Kopet Dag', atrekKopet.filter(p => p[0] >= 55.5)],
  ['mountain', 'Khorasan hills', [atrekKopet[atrekKopet.length-1]].concat(khorasan)],
  ['desert', 'Dasht-e Kavir and Dasht-e Lut', [khorasan[khorasan.length-1]].concat(deserts)],
  ['mountain', 'Makran', [deserts[deserts.length-1]].concat(makran, [seaArab[0]])],
  ['mountain', 'Ogo range (northern Somali highlands)', [seaArab[seaArab.length-1]].concat(ogo)],
  ['mountain', 'Ethiopian Highlands', [ogo[ogo.length-1], [43.8,9.6]].concat(ethH)],
  ['valley', 'Rift Valley (Lake Turkana)', [ethH[ethH.length-1]].concat(rift)],
  ['mountain', 'Uganda escarpment and Mount Elgon', [rift[rift.length-1]].concat(ugaKen, [lake[0]])],
  ['weak', 'Nile–Congo watershed', [lake[lake.length-1]].concat(weakA, ugaCod, ssdCod, ssdCaf)],
  ['weak', 'Darfur and Jebel Marra', [ssdCaf[ssdCaf.length-1]].concat(marra, [ennediS[0]])],
  ['mountain', 'Ennedi', ennediS],
  ['desert', 'Borkou and Tibesti', [ennediS[ennediS.length-1]].concat(tibesti)],
  ['desert', 'Djado and Tassili', [tibesti[tibesti.length-1]].concat(toAhaggar, [ahaggar[0]])],
  ['mountain', 'Ahaggar', ahaggar],
  ['desert', 'Erg Chech and Erg Iguidi', [ahaggar[ahaggar.length-1]].concat(toDraa)],
  ['river', 'Wadi Draa', [toDraa[toDraa.length-1]].concat(draa, [seaWest[0]])]
];
const ALTFRONT = [['desert', 'Libyan Desert: Gilf Kebir, the Great Sand Sea and the Calanscio', [ennediS[0]].concat(ennediNE, libyan, seaSirte)]];
/* closed loops */
const loopMain = [].concat(seaWest, seaEast, caucasusW, geoCrest, azeCrest, derbent, caspian, atrekKopet, khorasan, deserts, makran, seaArab, ogo, [[43.8,9.6]], ethH, rift, ugaKen, lake, weakA, ugaCod, ssdCod, ssdCaf, marra, ennediS, tibesti, toAhaggar, ahaggar, toDraa, draa);
const iE = loopMain.findIndex(p => p === ennediS[0]);
const loopAlt = [].concat(seaEast, caucasusW, geoCrest, azeCrest, derbent, caspian, atrekKopet, khorasan, deserts, makran, seaArab, ogo, [[43.8,9.6]], ethH, rift, ugaKen, lake, weakA, ugaCod, ssdCod, ssdCaf, marra, ennediS.slice(0,1), ennediNE, libyan, seaSirte);
const close = l => { const a = l[0], b = l[l.length-1]; return (a[0] === b[0] && a[1] === b[1]) ? l : l.concat([a]); };

/* ---------- inner seas: water inside the line, cut off from the open sea at two mouths ---------- */
const MOUTHS = [
  {n:'Bāb al-Mandab', p:[[43.62,12.82],[43.47,12.66],[43.33,12.47],[43.22,12.35]]},
  {n:'mouth of the Gulf of Oman', p:[[62.3,25.4],[61.75,25.07],[59.80,22.52],[59.70,22.40]]}
];
MOUTHS.forEach(m => [m.p[0], m.p[m.p.length-1]].forEach(q => { if(!inMP(q, landNoVic)) console.log('WARNING mouth end not on land', m.n, q); }));
console.log('ssdCaf ends', ssdCaf[0], ssdCaf[ssdCaf.length-1], 'ugaKen', ugaKen[0], ugaKen[ugaKen.length-1], 'geoCrest', geoCrest[0], geoCrest[geoCrest.length-1], 'atrek', atrekKopet[0], atrekKopet[atrekKopet.length-1]);
[['libya landfall',[18.85,30.3]],['caucasus start',[37.55,44.83]],['ogo start',[51.19,11.60]],['weak start',[31.62,-0.25]],['draa end',[-11.05,28.65]],['derbent',[48.30,42.075]]].forEach(([n,q]) => console.log(n, inMP(q, land) ? 'on land' : 'NOT on land'));
const buffer = (line, w) => line.slice(0, -1).map((a, i) => { const b = line[i+1], dx = b[0]-a[0], dy = b[1]-a[1], L = Math.hypot(dx, dy), nx = -dy/L*w, ny = dx/L*w;
  return [[[a[0]+nx, a[1]+ny], [b[0]+nx, b[1]+ny], [b[0]-nx, b[1]-ny], [a[0]-nx, a[1]-ny], [a[0]+nx, a[1]+ny]]]; });
function build(loop, name){
  const hand = [close(loop)];
  let terrLand = pc.intersection(landNoVic, [hand]);
  terrLand = pc.difference(terrLand, thrace);
  /* keep the mainland, uncut islands of the countries inside within ~60 km of it, and Cyprus */
  const big = terrLand.filter(p => area([p]) > 20000);
  const mainArea = area(big);
  const handOn = p => onLine(p, hand[0], 1e-7);
  const inside = new Set();
  C.forEach(g => { const f = topojson.feature(geo, g).geometry; const mp = f.type === 'Polygon' ? [f.coordinates] : f.coordinates; let a = 0;
    try { a = area(pc.intersection(mp, big)); } catch(e){ a = 0; } if(a > 1000) inside.add(String(g.id)); });
  const countryOf = p => { for(const g of C){ const f = topojson.feature(geo, g).geometry; const mp = f.type === 'Polygon' ? [f.coordinates] : f.coordinates; if(inMP(p, mp)) return String(g.id); } return null; };
  const mainPts = []; big.forEach(p => p[0].forEach((q, i) => { if(i % 3 === 0) mainPts.push(q); }));
  const islands = terrLand.filter(p => !big.includes(p)).filter(p => {
    if(p[0].some(handOn)) return false;   /* cut pieces, not islands */
    const c = d3.polygonCentroid(p[0]), id = countryOf(p[0][0]) || countryOf(c);
    if(['196','CYN','CNM','048'].includes(id)) return true;   /* Cyprus, and Bahrain (an island nation wholly inside the Gulf) */
    if(!inside.has(id)) return false;
    let md = Infinity; for(const q of mainPts){ const d = Math.hypot(q[0]-c[0], q[1]-c[1]); if(d < md) md = d; }
    return md < 0.6; });
  terrLand = big.concat(islands);
  /* water inside the line; the parts closed off at the two mouths are the inner seas */
  let water = pc.difference([hand], landNoVic);
  MOUTHS.forEach(m => { water = pc.difference(water, buffer(m.p, 0.0004)); });
  const SEEDS = [[38.5,20.0],[51.0,27.0]];   /* a point in the Red Sea and one in the Gulf */
  const inner = water.filter(p => SEEDS.some(q => inPoly(q, p)));
  console.log(name, 'inner seas', inner.length, inner.map(p => area([p])));
  const full = pc.union(terrLand, inner, ...MOUTHS.map(m => buffer(m.p, 0.0004)).flat().map(r => [r]));
  /* the border: outer rings only, split by kind */
  const fronts = name === 'alt' ? FRONT.filter(f => !['Ennedi','Borkou and Tibesti','Djado and Tassili','Ahaggar','Erg Chech and Erg Iguidi','Wadi Draa'].includes(f[1])).concat(ALTFRONT) : FRONT;
  const kindOf = (a, b) => { const m = [(a[0]+b[0])/2, (a[1]+b[1])/2];
    for(const f of fronts) if(onLine(m, f[2], 2e-6)) return [f[0], f[1]];
    for(const mo of MOUTHS) if(onLine(m, mo.p, 0.003)) return ['mouth', mo.n];
    if(onLine(m, hand[0], 2e-6)) return ['mouth', 'mouth of the Gulf of Oman'];   /* the short stretch of the line across Gwatar Bay */
    return ['coast', null]; };
  const lines = []; let ri = 0;
  full.forEach(poly => { if(area([poly]) < 250) return;   /* tiny islands: no outline */
    const r = poly[0]; let cur = null; ri++;
    for(let i = 0; i+1 < r.length; i++){
      const [k, n] = kindOf(r[i], r[i+1]);
      if(!cur || cur.k !== k || cur.n !== n){ if(cur) lines.push(cur); cur = {k, n, r:ri, p:[r[i]]}; }
      cur.p.push(r[i+1]);
    }
    if(cur) lines.push(cur);
  });
  /* merge a run split at the ring's start; simplify; round */
  const out = lines.map(l => ({k:l.k, n:l.n, r:l.r, p: rdp(l.p, l.k === 'coast' ? 0.004 : 0.002).map(q => [R3(q[0]), R3(q[1])])})).filter(l => l.p.length > 1);
  const km2 = area(terrLand), withSeas = area(full);
  /* the states inside, with the area and the share of each (Cyprus is one row; the base map splits it in three) */
  const acc = new Map();
  C.forEach(g => { const f = topojson.feature(geo, g).geometry; const mp = f.type === 'Polygon' ? [f.coordinates] : f.coordinates;
    let a = 0; try { a = area(pc.intersection(mp, terrLand)); } catch(e){}
    const t = area(mp); let id = String(g.id), n = g.properties.n;
    if(['196','CYN','CNM'].includes(id)){ id = 'CYP'; n = 'Cyprus (the whole island)'; }   /* the same id as in the outlines */
    if(n === 'Bir Tawil') n = 'Bir Tawil (unclaimed)';
    const o = acc.get(id) || {id, n, a:0, t:0}; o.a += a; o.t += t; acc.set(id, o); });
  const states = [...acc.values()].filter(o => o.a > 300).map(o => { const p = 100*o.a/o.t; return {id:o.id, n:o.n, km2:o.a, pct: p < 1 ? Math.round(p*10)/10 : Math.round(p), ...(o.id === '643' ? {flag:'a strip of the Black Sea coast'} : {})}; })
    .sort((a, b) => b.km2 - a.km2);
  const shares = states;
  return {km2, lines: out, states};
}
const main = build(loopMain, 'main'), alt = build(loopAlt, 'alt');

/* ---------- the far east, shown with the Greater Caliphate: Hindu Kush, the Indus and the Thar ---------- */
const riv = topojson.feature(geo, geo.objects.rivers).features;
const indusAll = riv.filter(f => (f.properties.n || '') === 'Indus').flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const indusLine = indusAll.reduce((a, l) => l.length > a.length ? l : a, []);
const indus = part(indusLine, [72.9,34.9], [70.4,28.95]);
const kopetE = part(B.irn_tkm, [58.0,38.0], B.irn_tkm[nearest(B.irn_tkm, [61.1,36.6])]);
const far = kopetE.concat([[61.5,35.4],[63.0,35.3],[64.5,35.5],[66.0,35.6],[67.5,35.4],[69.0,35.45],[70.4,35.9],[71.8,36.25],[72.7,36.0],[73.0,35.5]], indus, [[70.9,28.0],[71.0,26.8],[70.6,25.6],[70.0,24.25],[68.75,23.75]]);

/* ---------- barrier zones ---------- */
const zones = [
  {n:'Gilf Kebir and the Great Sand Sea', r:[[25.3,22.55],[26.6,22.6],[26.85,23.6],[26.4,24.3],[26.9,25.3],[27.15,26.6],[26.6,28.0],[25.7,29.3],[24.7,29.5],[24.6,27.7],[24.8,25.9],[25.1,24.3],[25.3,22.55]]},
  {n:'the Sudd', r: regRing('SUDD')}
].map(z => ({n:z.n, r: rdp(z.r, 0.01).map(q => [R3(q[0]), R3(q[1])])}));

/* ---------- internal lines ---------- */
const taurus = [[29.6,36.9],[30.4,37.15],[31.3,37.2],[32.3,37.05],[33.4,37.05],[34.4,37.3],[35.2,37.7],[36.2,37.95],[37.3,38.1],[38.4,38.35],[39.6,38.4],[40.8,38.3],[41.9,38.15],[42.9,37.85],[43.8,37.5],[44.5,37.35]];
const redsea = [[32.55,29.9],[33.0,29.1],[33.7,28.1],[34.3,27.5],[35.1,26.3],[36.0,24.8],[36.9,23.2],[37.8,21.6],[38.6,20.0],[39.5,18.4],[40.5,16.6],[41.6,15.0],[42.4,13.8],[43.3,12.7]];
const RIVN = {Nile:['Nile','El Bahr el Abyad','Bahr el Jebel','Albert Nile','Victoria Nile','Rosetta Branch','Damietta Branch','Blue Nile','Abay','Bahr el Azraq'], Tigris:['Tigris','Dicle'], Euphrates:['Euphrates','Firat','Al Furat','Shatt al Arab']};
/* the base map has no Blue Nile, so it is taken from the full Natural Earth rivers */
const blue = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features.filter(f => ['Abay','El Bahr el Azraq'].includes(f.properties.name))
  .flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const rivers = Object.entries(RIVN).map(([n, names]) => ({n, p: riv.filter(f => names.includes(f.properties.n)).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates)
  .concat(n === 'Nile' ? blue : []).map(l => rdp(l, 0.003).map(q => [R3(q[0]), R3(q[1])]))}));
console.log('rivers', rivers.map(r => r.n + ':' + r.p.length + ' lines/' + r.p.reduce((t, l) => t + l.length, 0) + ' pts').join(' '), 'names seen', [...new Set(riv.map(f => f.properties.n))].filter(n => /Nil|Abay|Azraq|Atbara/.test(n)).join(','));

const out = {main, alt, far: rdp(far, 0.003).map(q => [R3(q[0]), R3(q[1])]), zones, intl:{taurus, redsea, rivers}};
fs.writeFileSync(path.join(ROOT, 'src/nat.json'), JSON.stringify(out));
console.log('wrote src/nat.json', JSON.stringify(out).length, 'bytes');
