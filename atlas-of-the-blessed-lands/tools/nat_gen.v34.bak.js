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
const albert = lakeF.find(f => f.properties.n === 'Lake Albert');
if(!albert) throw new Error('no Lake Albert');
const albertMP = albert.geometry.type === 'Polygon' ? [albert.geometry.coordinates] : albert.geometry.coordinates;
const landNoVic = pc.difference(land, victoriaMP, albertMP);   /* the line runs down Lake Albert and along Lake Victoria's shore: both lakes are water, not territory */
/* European Turkey (Thrace) is cut off at the straits */
const tur = topojson.feature(geo, byId('792')).geometry;
const turPolys = tur.type === 'Polygon' ? [tur.coordinates] : tur.coordinates;
const thrace = turPolys.filter(p => { const xs = p[0].map(q => q[0]), ys = p[0].map(q => q[1]); return Math.min(...ys) > 40.0 && Math.max(...xs) < 29.4 && Math.max(...xs) - Math.min(...xs) > 1; });
console.log('Thrace pieces', thrace.length);

/* ---------- the line, clockwise from the Atlantic at the mouth of the Senegal ---------- */
const B = {
  rus_geo: border('643', '268'), rus_aze: border('643', '031'), irn_tkm: border('364', '795'), irn_afg: border('364', '004'), irn_pak: border('364', '586'),
  uga_ken: border('800', '404'), uga_cod: border('800', '180'), ssd_cod: border('728', '180'), ssd_caf: border('728', '140'),
  caf_sdn: border('140', '729'), caf_cmr: border('140', '120'), mau_sen: border('478', '686')
};
const S = [];   /* segments: {k: kind, p: points, n: name} ; kind 'sea' is never drawn */
const seg = (k, n, p) => S.push({k, n, p});
const MAIN = [], ALT = [];
/* rivers from Natural Earth (rivers.geojson), picked by name and joined end to end */
const RIV = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features;
const riverLines = name => RIV.filter(f => f.properties.name === name).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const dist = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1]);
const findLine = (lines, a, b, tol = 0.03) => { for(const l of lines){ const s = l[0], e = l[l.length-1];
  if(dist(s, a) < tol && dist(e, b) < tol) return l.slice(); if(dist(s, b) < tol && dist(e, a) < tol) return l.slice().reverse(); }
  throw new Error('no river line ' + a + ' ' + b); };
/* West: the Atlantic and the Mediterranean, offshore (the coast is the border) */
const seaAtl = [[-17.2,16.0],[-18.0,17.2],[-18.2,19.0],[-18.4,21.0],[-18.6,23.0],[-18.6,25.0],[-19.2,27.0],[-19.2,29.6],[-15.5,30.8]];   /* Mauritania and Western Sahara, west of the Canaries */
const seaWest = [[-13.2,30.6],[-10.6,33.6],[-7.0,35.62],[-5.6,35.97],[-4.0,36.05],[-2.0,36.25],[0.5,36.75],[3.5,37.15],[6.5,37.45],[8.8,37.66],[10.6,37.6],[11.6,37.25],[12.2,36.3],[13.0,35.3],[15.5,34.5],[18.6,33.9]];
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
/* Iran's east edge: the Kopet Dag, the Hari River (Tejen) south from Sarakhs, the Sistan basin, the Baluchistan desert edge */
const tkmAll = part(B.irn_tkm, [53.9,37.32], B.irn_tkm[B.irn_tkm.length-1]);
const iSarakhs = nearest(tkmAll, [61.12,36.52]);
const atrekKopet = tkmAll.slice(0, iSarakhs+1);
const hariA = tkmAll.slice(iSarakhs);                                         /* Sarakhs to the Iran–Afghanistan–Turkmenistan corner */
const iIslam = nearest(B.irn_afg, [61.07,34.62]);                              /* where the Hari turns west to Herat (Islam Qala) */
const hariB = B.irn_afg.slice(0, iIslam+1);
const sistan = B.irn_afg.slice(iIslam);
const baluch = B.irn_pak.slice();
const seaArab = [[61.75,24.9],[61.0,22.5],[59.0,18.5],[56.0,15.0],[53.3,13.15],[51.75,12.1],[51.6,11.95]];
/* The Somali and Kenyan coast, offshore, from Cape Guardafui down to the mouth of the Tana */
const seaSom = [[52.0,11.3],[52.3,10.4],[51.7,9.3],[51.0,8.0],[50.3,7.0],[49.6,6.0],[48.9,5.0],[48.0,4.0],[47.0,3.0],[46.1,2.0],[44.8,1.0],[43.4,0.0],[42.3,-1.0],[41.8,-2.0],[41.2,-2.75],[40.85,-2.75]];
/* ---- the southern edge of Africa, in your order (west to east) ---- */
const mauSenPart = B.mau_sen.slice(nearest(B.mau_sen, [-16.5,16.0]));            /* the Senegal River, as the Mauritania–Senegal border */
const SEN = riverLines('Sénégal');
const senRiver = findLine(SEN, [-16.542,15.806], [-13.09,15.497]).concat(findLine(SEN, [-13.083,15.492], [-10.851,13.814]));
const senUp = senRiver.slice(nearest(senRiver, B.mau_sen[B.mau_sen.length-1]));   /* above the Mauritania–Mali corner: the river itself, to the Bafing */
const senegal = mauSenPart.concat(senUp);
const bafing = findLine(riverLines('Bafing'), [-10.851,13.814], [-12.088,10.59]);   /* Bafoulabé to its source in the Fouta Djallon */
const NG = riverLines('Niger');
const n7 = findLine(NG, [-9.38,11.0], [-3.98,15.28]), debo = findLine(NG, [-3.98,15.28], [-4.3,15.51]), n5 = findLine(NG, [-4.3,15.51], [-3.22,16.4]),
  n0 = findLine(NG, [-3.22,16.4], [4.66,10.61]), kainji = findLine(NG, [4.66,10.61], [4.63,9.86]), n9 = findLine(NG, [4.63,9.86], [5.5,5.14]);
const niger = [].concat(n7.slice(nearest(n7, [-8.0,12.64])), debo.slice(1), n5.slice(1), n0.slice(1), kainji.slice(1), n9.slice(1, nearest(n9, [6.75,7.80])+1));
const crossing = [bafing[bafing.length-1], [-12.0,10.33], [-11.3,10.25], niger[0]];   /* straight lines by hand: nothing in the base data joins the two rivers */
const benueLow = riverLines('Benue')[0].slice().reverse();                     /* from the Niger at Lokoja up to Numan */
const benueMid = [[12.20,9.40],[12.45,9.31],[12.80,9.34],[13.10,9.33],[13.40,9.30]];   /* Numan to Garoua: not in the base data, placed by hand */
const benueUp = [[13.66,9.06],[13.88,8.70],[14.02,8.30],[13.95,7.95],[13.70,7.65],[13.50,7.30],[13.45,7.12]];   /* Garoua up to the Benue's source: by hand */
const adamawa = [[13.45,7.12],[13.829,7.515],[14.252,7.665],[14.781,7.736],B.caf_cmr[B.caf_cmr.length-1]];       /* south edge of the Mbang range (Adamawa Plateau), to the corner of Cameroon, Chad and the CAR */
const carDivide = part(B.caf_cmr, B.caf_cmr[B.caf_cmr.length-1], [14.78,6.36]).concat([[15.40,6.05],[16.40,5.95],[17.40,5.92],[18.30,5.95],[19.20,6.15],[20.00,6.40],[20.90,6.70],[21.60,7.45],[22.20,8.40],[22.90,9.10],[23.458,9.147]]);   /* the CAR–Cameroon border, then by hand */
const carSudan = part(B.caf_sdn, [23.458,9.147], B.caf_sdn[B.caf_sdn.length-1]);                              /* the CAR–Sudan border down to the three-country corner */
const congoNile = [].concat(B.ssd_caf.slice().reverse(), B.ssd_cod.slice().reverse());                      /* from (24.17,8.69) to the Uganda corner */
const ugaCodAll = B.uga_cod;                                                                                 /* Uganda–DR Congo, which runs down the middle of Lake Albert */
const albertS = ugaCodAll[nearest(ugaCodAll, [30.53,1.15])];
const ugaCod = ugaCodAll.slice(0, nearest(ugaCodAll, [30.53,1.15])+1);
const albertKatonga = [albertS, [30.60,0.70], [30.65,0.22]];                                               /* by hand */
const katonga = [[30.65,0.22],[31.00,0.22],[31.20,0.17],[31.40,0.11]];       /* by hand: the river is not in the base data */
const katongaLake = [[31.40,0.11],[31.62,-0.25],[31.95,-0.45]];   /* the river's last stretch would cut off about 1,200 km² the old outline held, so the line keeps to the old diagonal to the shore */
const lakeVic = [[31.95,-0.45],[32.0,-0.95],[33.0,-0.99],[33.904,-1.003]];                                 /* in the water; the shore is the line */
const ugaKenAll = B.uga_ken;
const elgonI = nearest(ugaKenAll, [34.55,1.12]);
const ugaKen = ugaKenAll.slice(0, elgonI+1);
const elgonTurkana = [ugaKenAll[elgonI],[35.00,1.15],[35.50,1.20],[35.62,1.60],[35.90,2.00],[36.25,2.25],[36.558,2.395]];  /* by hand */
const ndoto = [[36.558,2.395],[36.80,2.00],[37.10,1.40],[37.30,1.05],[37.45,0.55],[37.50,0.20]];                       /* by hand */
const TA = riverLines('Tana');
const tanaLow = findLine(TA, [37.811,-0.799], [40.513,-2.525]);
const tana = tanaLow.slice(nearest(tanaLow, [38.573,-0.024]));   /* from its northern bend to Kipini */
const toTana = [[37.50,0.20],[38.00,0.10],tana[0]];                                                          /* by hand */
/* the Libya alternate: from the Sudan corner north along Darfur, Ennedi's east side and the Libyan Desert to the Gulf of Sirte */
const marra = [[24.1,10.6],[24.0,11.8],[23.87,12.53],[23.50,13.41],[23.88,14.42],[23.9,15.3]];   /* along the west foot of Jebel Marra */
const ennediS0 = ringPart(regRing('Ennedi Plat.'), [23.75,16.19], [20.99,18.05])[0];
const ennediNE = ringPart(regRing('Ennedi Plat.'), [24.26,17.74], [23.75,16.19]).reverse().slice(1);   /* the plateau's east side */
const libyan = [[24.3,19.6],[24.95,21.9],[25.55,22.8],[25.65,23.9],[25.2,25.0],[24.95,26.4],[24.85,27.8],[24.55,29.65],[23.2,29.5],[21.6,29.4],[20.2,29.75],[19.3,30.15],[18.85,30.3]];
const seaSirte = [[18.6,31.4]];

/* the segments, west to east along the south, then up the east side: [kind, name, points] */
const SOUTH = [
  ['river',    'Senegal River', [seaAtl[0]].concat(senegal)],
  ['river',    'Bafing', bafing],
  ['weak',     'Bafing to Bamako crossing', crossing],
  ['river',    'Niger River', niger],
  ['river',    'Benue River', [niger[niger.length-1]].concat(benueLow, benueMid, benueUp)],
  ['mountain', 'Adamawa Plateau', adamawa],
  ['weak',     'Chari–Congo watershed (Central African Republic)', carDivide.concat(carSudan)],
  ['mountain', 'Congo–Nile Divide', congoNile.concat(ugaCod)],
  ['weak',     'Lake Albert to the Katonga', albertKatonga],
  ['river',    'Katonga River', katonga],
  ['weak',     'Katonga to Lake Victoria', katongaLake],
  ['lake',     'Lake Victoria', lakeVic],
  ['river',    'Uganda–Kenya border (Lake Victoria to Mount Elgon)', ugaKen],
  ['weak',     'Mount Elgon to Lake Turkana (Kerio and Suguta valleys)', elgonTurkana],
  ['weak',     'Ndoto and Mathews ranges to Mount Kenya', ndoto],
  ['weak',     'Mount Kenya to the Tana', toTana],
  ['river',    'Tana River', tana.concat([seaSom[seaSom.length-1]])]
];
const FRONT = [   /* land segments with their kind, in order (the drawn border) */
  ['mountain', 'Greater Caucasus', [seaEast[seaEast.length-1]].concat(caucasusW, geoCrest, azeCrest)],
  ['fort', 'Derbent (Bāb al-Abwāb)', [azeCrest[azeCrest.length-1]].concat(derbent, [caspian[0]])],
  ['river', 'Atrek valley', [caspian[caspian.length-1]].concat(atrekKopet.filter(p => p[0] < 55.6))],
  ['mountain', 'Kopet Dag', atrekKopet.filter(p => p[0] >= 55.5)],
  ['river', 'Hari River', hariA.concat(hariB)],
  ['valley', 'Sistan basin', sistan],
  ['desert', 'Baluchistan desert edge', baluch],
  ['mouth', 'mouth of the Gulf of Oman', [baluch[baluch.length-1], seaArab[0]]]
].concat(SOUTH);
const ALTFRONT = [
  ['weak', 'Darfur and Jebel Marra', [B.ssd_caf[B.ssd_caf.length-1]].concat(marra, [ennediS0])],
  ['desert', 'Libyan Desert: Gilf Kebir, the Great Sand Sea and the Calanscio', [ennediS0].concat(ennediNE, libyan, seaSirte)]];
/* closed loops (the same orientation both times: west coast north, then east, then back west along the south) */
const southLoop = idx => [].concat(...SOUTH.slice(idx).reverse().map(s => s[2].slice().reverse()));
const eastLoop = [].concat(seaEast, caucasusW, geoCrest, azeCrest, derbent, caspian, atrekKopet, hariA, hariB, sistan, baluch, seaArab, seaSom);
const loopMain = [].concat(seaAtl, seaWest, eastLoop, southLoop(0));
const iCN = SOUTH.findIndex(s => s[1] === 'Congo–Nile Divide');
const loopAlt = [].concat(seaEast, caucasusW, geoCrest, azeCrest, derbent, caspian, atrekKopet, hariA, hariB, sistan, baluch, seaArab, seaSom, southLoop(iCN), marra, [ennediS0], ennediNE, libyan, seaSirte);
const close = l => { const a = l[0], b = l[l.length-1]; return (a[0] === b[0] && a[1] === b[1]) ? l : l.concat([a]); };

/* ---------- inner seas: water inside the line, cut off from the open sea at two mouths ---------- */
const MOUTHS = [
  {n:'Bāb al-Mandab', p:[[43.62,12.82],[43.47,12.66],[43.33,12.47],[43.22,12.35]]},
  {n:'mouth of the Gulf of Oman', p:[[62.3,25.4],[61.75,25.07],[59.80,22.52],[59.70,22.40]]}
];
MOUTHS.forEach(m => [m.p[0], m.p[m.p.length-1]].forEach(q => { if(!inMP(q, landNoVic)) console.log('WARNING mouth end not on land', m.n, q); }));
/* ---------- checks on the hand-drawn line ---------- */
const CMP = C.map(g => { const f = topojson.feature(geo, g).geometry; return [String(g.id), g.properties.n, f.type === 'Polygon' ? [f.coordinates] : f.coordinates]; });
const countryName = p => { const c = CMP.find(([id, n, mp]) => inMP(p, mp)); return c ? c[1] : '(sea)'; };
[['sea Atlantic', seaAtl], ['sea west', seaWest], ['sea east', seaEast], ['sea Arabian', seaArab], ['sea Somali', seaSom], ['lake Victoria path', lakeVic.slice(1, -1)]].forEach(([n, pts]) => {
  const bad = pts.filter(q => inMP(q, n.startsWith('lake') ? landNoVic : land)); if(bad.length) console.log('WARNING', n, 'points on land:', JSON.stringify(bad)); });
SOUTH.forEach(([k, n, pts]) => { const names = {}; pts.forEach((q, i) => { if(i % 4 === 0 || i === pts.length-1){ const c = countryName(q); names[c] = (names[c] || 0) + 1; } });
  console.log(('  ' + k).padEnd(10), n.padEnd(58), pts.length + ' pts', JSON.stringify(names)); });
const segHit = (p1, p2, p3, p4) => { const d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0]); if(Math.abs(d) < 1e-14) return false;
  const t = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d, u = ((p3[0]-p1[0])*(p2[1]-p1[1]) - (p3[1]-p1[1])*(p2[0]-p1[0])) / d;
  return t > 1e-9 && t < 1-1e-9 && u > 1e-9 && u < 1-1e-9; };
const selfX = (loop, nm) => { let c = 0; const L = close(loop); for(let i = 0; i+1 < L.length; i++) for(let j = i+2; j+1 < L.length; j++){ if(i === 0 && j+1 === L.length-1) continue;
  if(segHit(L[i], L[i+1], L[j], L[j+1])){ c++; if(c < 8) console.log('SELF-INTERSECTION in', nm, 'near', JSON.stringify(L[i]), JSON.stringify(L[j])); } } console.log(nm, 'loop:', L.length, 'points,', c, 'self-intersections'); };
selfX(loopMain, 'main'); selfX(loopAlt, 'alt');
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
  const westOnly = SOUTH.slice(0, iCN).map(s => s[1]);
  const fronts = name === 'alt' ? FRONT.filter(f => !westOnly.includes(f[1])).concat(ALTFRONT) : FRONT;
  const lakeRings = [[victoriaMP, 'Lake Victoria'], [albertMP, 'Lake Albert']].map(([mp, n]) => [n, mp.flatMap(poly => poly)]);
  const unknown = [];
  const kindOf = (a, b) => { const m = [(a[0]+b[0])/2, (a[1]+b[1])/2];
    for(const f of fronts) if(onLine(m, f[2], 2e-6)) return [f[0], f[1]];
    for(const mo of MOUTHS) if(onLine(m, mo.p, 0.003)) return ['mouth', mo.n];
    for(const [n, rings] of lakeRings) if(rings.some(r => onLine(m, r, 2e-6))) return ['lake', n];
    if(onLine(m, hand[0], 2e-6)) unknown.push(R3(m[0]) + ',' + R3(m[1]));
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
  if(unknown.length) console.log(name, 'edges on the hand line that no segment claims:', unknown.length, unknown.slice(0, 12).join(' '));
  if(process.env.NAT_DEBUG) fs.writeFileSync(path.join(process.env.NAT_DEBUG, 'terr_' + name + '.json'), JSON.stringify({terr: terrLand, loop: hand[0]}));
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
  const states = [...acc.values()].filter(o => o.a > 300).map(o => { const p = 100*o.a/o.t; return {id:o.id, n:o.n, km2:o.a, pct: p < 1 ? Math.round(p*10)/10 : Math.round(p), ...(o.id === '643' ? {flag:'a strip of the Black Sea coast'} : o.id === '732' ? {flag:'status internationally disputed'} : {})}; })
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
const far = [B.irn_tkm[B.irn_tkm.length-1]].concat([[61.5,35.4],[63.0,35.3],[64.5,35.5],[66.0,35.6],[67.5,35.4],[69.0,35.45],[70.4,35.9],[71.8,36.25],[72.7,36.0],[73.0,35.5]], indus, [[70.9,28.0],[71.0,26.8],[70.6,25.6],[70.0,24.25],[68.75,23.75]]);

/* ---------- barrier zones ----------
   The Sudd is no longer a zone: the line now runs on the watershed far to the south-west and the Sudd lies well inside.
   The Gilf Kebir zone is drawn only with the Libya variant, whose line runs past it. */
const zones = [
  {n:'Gilf Kebir and the Great Sand Sea', r:[[25.3,22.55],[26.6,22.6],[26.85,23.6],[26.4,24.3],[26.9,25.3],[27.15,26.6],[26.6,28.0],[25.7,29.3],[24.7,29.5],[24.6,27.7],[24.8,25.9],[25.1,24.3],[25.3,22.55]]}
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
