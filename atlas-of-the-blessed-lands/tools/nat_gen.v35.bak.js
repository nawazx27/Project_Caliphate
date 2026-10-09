/* Natural borders of Dār al-Amān, Version 35 (your design, 2026-10-07) -> src/nat.json
   Every edge is a sea, a desert or a major mountain crest. Africa is wholly inside: the closed loop runs offshore round the
   continent (and round Madagascar, Zanzibar, the Comoros, the Canaries and Cape Verde), and the land inside it is cut out, so
   the coast itself is the border. In the north-east the line leaves the Caspian at the Garabogaz Gulf and runs over the Ustyurt
   and Kyzylkum deserts to the Nurata and Turkestan ranges, then along the Alay, Trans-Alay, Pamir (Sarykol), Hindu Kush and
   Safed Koh crests (the Tajikistan–Kyrgyzstan, Tajikistan–China, Afghanistan–China and Afghanistan–Pakistan borders, where they
   run on the crest), the Sulaiman and Kirthar ranges, to the sea at Cape Monze. The Red Sea is joined as an inner sea, closed at
   Bāb al-Mandab; the Persian Gulf is open coast. The Libya alternate keeps its Version 34 southern route.
   Run: node --stack-size=30000 tools/nat_gen.js   (about 1 minute)                                                  */
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

/* ---------- the line, clockwise from Cape Agulhas (Version 35) ----------
   Every edge is a sea, a desert or a major mountain crest. Africa is wholly inside: the line goes offshore round the continent and
   the land inside it is cut out, so the coast itself is the border. In the north-east the line leaves the Caspian at the Garabogaz
   Gulf, crosses the Ustyurt and Kyzylkum deserts, then follows the Nurata, Turkestan, Alai, Trans-Alai, Pamir and Hindu Kush crests,
   the Safed Koh, Sulaiman and Kirthar ranges to the sea at Cape Monze. */
const B = {
  rus_geo: border('643', '268'), rus_aze: border('643', '031'),
  tjk_kgz: border('762', '417'), kaz_tkm: border('398', '795'), tjk_chn: border('762', '156'), afg_chn: border('004', '156'), afg_pak: border('004', '586'),
  uga_ken: border('800', '404'), uga_cod: border('800', '180'), ssd_cod: border('728', '180'), ssd_caf: border('728', '140')
};
const S = [];
const MAIN = [], ALT = [];
/* the coast vertex nearest to a point: waypoints given as 'on the coast' are snapped to the real shore */
const coastVerts = []; land.forEach(p => p.forEach(r => r.forEach(q => coastVerts.push(q))));
const coastNear = p => { let bd = Infinity, bp = null; for(const q of coastVerts){ const d = Math.hypot(q[0]-p[0], q[1]-p[1]); if(d < bd){ bd = d; bp = q; } } return bp; };
const dist = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1]);
/* West: the Atlantic and the Mediterranean, offshore (the coast is the border) */
const seaAtl = [[-20.0,18.3],[-18.2,19.0],[-18.4,21.0],[-18.6,23.0],[-18.6,25.0],[-19.2,27.0],[-19.2,29.6],[-15.5,30.8]];   /* Mauritania and Western Sahara, west of the Canaries */
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
/* across the Caspian (water) to the Turkmen shore at the Garabogaz Gulf */
const caspian = [[48.65,42.2],[50.3,41.9],[51.8,41.5],[52.6,41.3]];
const garabogaz = coastNear([53.0,41.3]);
/* ---- the north-east and east: deserts, then crests (waypoints [lon, lat]) ---- */
const kazTkm = B.kaz_tkm;
const ustyurt = [garabogaz, kazTkm[nearest(kazTkm, [55.43,41.29])], kazTkm[0], [57.0,42.3]];   /* the southern escarpment of the Ustyurt: over the Garabogaz Gulf, below the Kazakh tip of the plateau (the Kazakhstan–Turkmenistan border), then north-east */
const muynak = [[57.0,42.3], [59.0,43.8]];                                /* the south shore of the Aral Sea at Muynak */
const kyzylkum = [[59.0,43.8], [62.3,42.3]];
const nurata = [[62.3,42.3], [65.7,40.6]];
const tjkKgzAll = B.tjk_kgz;
const iTk = nearest(tjkKgzAll, [69.6,39.57]);
const turkestan = [[65.7,40.6], [68.0,39.6], tjkKgzAll[iTk]];             /* the Turkestan Range; the Jizzakh Gap is crossed at 68°E; joins the Tajikistan–Kyrgyzstan border, which runs on the Alay crest */
const alai = tjkKgzAll.slice(iTk);                                        /* Alay and Trans-Alay crest: Lenin Peak is on it, to the China corner */
const tjkChn = B.tjk_chn.slice().reverse();                              /* from the Kyrgyz corner down the Sarykol range on the Tajikistan–China border */
const afgChn = B.afg_chn.slice().reverse();                              /* Afghanistan–China, ending at the Wakhjir Pass */
const wakhjir = afgChn[afgChn.length-1];
const khyber = B.afg_pak[nearest(B.afg_pak, [71.09,34.09])];
const tirich = B.afg_pak[nearest(B.afg_pak, [71.85,36.25])];
const hinduKush = part(B.afg_pak, wakhjir, tirich);                       /* Wakhan, Baroghil Pass and the Hindu Kush crest to Tirich Mir */
const safed = part(B.afg_pak, tirich, khyber);                            /* down the Chitral, Bajaur and Safed Koh ridge to the Khyber Pass */
const kurram = part(B.afg_pak, khyber, [70.15,33.53]);                    /* the Safed Koh crest, west of the Kurram */
const sulaiman = [kurram[kurram.length-1],[70.10,32.80],[70.05,32.20],[70.0,31.6],[69.75,30.6],[69.5,29.5]];   /* the Sulaiman Range, by Takht-e-Sulaiman */
const kirthar = [[69.5,29.5],[67.2,27.0],[67.15,26.0],[67.1,25.5]];
const monze = coastNear([66.7,24.8]);
const kirtharSea = kirthar.concat([[66.85,25.1], monze]);                 /* the Kirthar Range to the sea at Cape Monze */
/* Arabian Sea, offshore: Makran, Oman and Socotra (inside) to Cape Guardafui */
const seaArab = [[65.4,24.1],[62.5,23.0],[60.6,21.5],[59.0,19.5],[57.5,16.5],[56.0,14.0],[55.5,12.4],[54.0,11.3],[52.0,11.3]];
/* The Somali and Kenyan coast, offshore, from Cape Guardafui down to the mouth of the Tana */
const seaSom = [[52.0,11.3],[52.3,10.4],[51.7,9.3],[51.0,8.0],[50.3,7.0],[49.6,6.0],[48.9,5.0],[48.0,4.0],[47.0,3.0],[46.1,2.0],[44.8,1.0],[43.4,0.0],[42.3,-1.0],[41.8,-2.0],[41.2,-2.75],[40.85,-2.75]];
/* East Africa, Mozambique and South Africa, offshore, then round the Cape and up the Atlantic side to Dakar (all west coast points are south to north) */
const seaEAf = [[41.0,-3.8],[41.0,-5.5],[41.0,-8.5],[47.5,-9.9],[51.5,-10.7],[52.6,-14.0],[52.4,-18.5],[50.8,-23.0],[48.0,-26.0],[44.0,-26.8],[34.5,-27.0],[32.3,-30.2],[30.4,-32.4],[28.4,-34.0],[25.5,-35.2],[22.5,-35.6],[20.0,-35.8],[17.7,-35.2]];
const seaWAf = [[16.3,-34.0],[15.5,-32.2],[14.7,-29.5],[13.7,-26.8],[12.9,-23.5],[11.5,-19.5],[11.0,-17.0],[11.0,-14.0],[11.0,-11.5],[10.5,-8.5],[10.5,-6.0],[9.6,-3.6],[7.8,-1.6],[7.8,0.8],[7.9,2.2],[7.9,3.6],[6.0,3.6],[3.0,5.0],[-0.5,4.0],[-2.3,3.9],[-5.0,4.3],[-7.8,3.5],[-11.5,5.2],[-14.5,8.5],[-17.5,9.5],[-17.8,11.5],[-26.3,13.4],[-26.3,17.8]];
/* islands that are part of the continent's offshore world and inside the line, whatever their distance from the coast: [lon, lat] points inside each */
const ISLES = [['Bioko',[8.7,3.5]],['Socotra',[53.95,12.55]],['Abd al-Kuri',[52.2,12.2]],
  ['Canary Islands',[-16.6,28.3]],['Canary Islands',[-15.6,27.95]],['Canary Islands',[-14.0,28.4]],['Canary Islands',[-13.6,29.0]],['Canary Islands',[-17.85,28.7]],['Canary Islands',[-17.1,28.1]],['Canary Islands',[-18.0,27.75]],
  ['Cape Verde',[-23.6,15.05]],['Cape Verde',[-25.2,17.05]],['Cape Verde',[-24.95,16.85]],['Cape Verde',[-24.3,16.6]],['Cape Verde',[-22.9,16.7]],['Cape Verde',[-22.8,16.1]],['Cape Verde',[-23.2,15.2]],['Cape Verde',[-24.4,14.95]],['Cape Verde',[-24.7,14.85]],
  ['Zanzibar',[39.3,-6.15]],['Pemba',[39.75,-5.2]],['Mafia',[39.78,-7.9]],
  ['Grande Comore',[43.3,-11.65]],['Mohéli',[43.7,-12.3]],['Anjouan',[44.45,-12.2]],['Mayotte',[45.15,-12.8]],
  ['Nosy Be',[48.25,-13.3]],['Sainte-Marie',[49.9,-16.9]]];
/* the Libya alternate (kept from Version 34, not redrawn): from the Sudan corner north along Darfur, Ennedi's east side and the Libyan Desert to the Gulf of Sirte */
const congoNile = [].concat(B.ssd_caf.slice().reverse(), B.ssd_cod.slice().reverse());                      /* from (24.17,8.69) to the Uganda corner */
const ugaCodAll = B.uga_cod;                                                                                 /* Uganda–DR Congo, which runs down the middle of Lake Albert */
const albertS = ugaCodAll[nearest(ugaCodAll, [30.53,1.15])];
const ugaCod = ugaCodAll.slice(0, nearest(ugaCodAll, [30.53,1.15])+1);
const albertKatonga = [albertS, [30.60,0.70], [30.65,0.22]];                                               /* by hand */
const katonga = [[30.65,0.22],[31.00,0.22],[31.20,0.17],[31.40,0.11]];       /* by hand: the river is not in the base data */
const katongaLake = [[31.40,0.11],[31.62,-0.25],[31.95,-0.45]];
const lakeVic = [[31.95,-0.45],[32.0,-0.95],[33.0,-0.99],[33.904,-1.003]];                                 /* in the water; the shore is the line */
const ugaKenAll = B.uga_ken;
const elgonI = nearest(ugaKenAll, [34.55,1.12]);
const ugaKen = ugaKenAll.slice(0, elgonI+1);
const elgonTurkana = [ugaKenAll[elgonI],[35.00,1.15],[35.50,1.20],[35.62,1.60],[35.90,2.00],[36.25,2.25],[36.558,2.395]];  /* by hand */
const ndoto = [[36.558,2.395],[36.80,2.00],[37.10,1.40],[37.30,1.05],[37.45,0.55],[37.50,0.20]];                       /* by hand */
const RIV = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features;
const riverLines = name => RIV.filter(f => f.properties.name === name).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const findLine = (lines, a, b, tol = 0.03) => { for(const l of lines){ const s = l[0], e = l[l.length-1];
  if(dist(s, a) < tol && dist(e, b) < tol) return l.slice(); if(dist(s, b) < tol && dist(e, a) < tol) return l.slice().reverse(); }
  throw new Error('no river line ' + a + ' ' + b); };
const TA = riverLines('Tana');
const tanaLow = findLine(TA, [37.811,-0.799], [40.513,-2.525]);
const tana = tanaLow.slice(nearest(tanaLow, [38.573,-0.024]));   /* from its northern bend to Kipini */
const toTana = [[37.50,0.20],[38.00,0.10],tana[0]];                                                          /* by hand */
const marra = [[24.1,10.6],[24.0,11.8],[23.87,12.53],[23.50,13.41],[23.88,14.42],[23.9,15.3]];   /* along the west foot of Jebel Marra */
const ennediS0 = ringPart(regRing('Ennedi Plat.'), [23.75,16.19], [20.99,18.05])[0];
const ennediNE = ringPart(regRing('Ennedi Plat.'), [24.26,17.74], [23.75,16.19]).reverse().slice(1);   /* the plateau's east side */
const libyan = [[24.3,19.6],[24.95,21.9],[25.55,22.8],[25.65,23.9],[25.2,25.0],[24.95,26.4],[24.85,27.8],[24.55,29.65],[23.2,29.5],[21.6,29.4],[20.2,29.75],[19.3,30.15],[18.85,30.3]];
const seaSirte = [[18.6,31.4]];

/* the land segments of the new line, in order, with their kind: this is what the drawn border is made of */
const NE = [
  ['fort',     'Derbent (Bāb al-Abwāb)', [azeCrest[azeCrest.length-1]].concat(derbent, [caspian[0]])],
  ['desert',   'Ustyurt escarpment', ustyurt],
  ['desert',   'Aral Sea south shore (Muynak)', muynak],
  ['desert',   'Kyzylkum desert', kyzylkum],
  ['mountain', 'Nurata Range', nurata],
  ['mountain', 'Turkestan Range (Jizzakh Gap crossed)', turkestan],
  ['mountain', 'Alay and Trans-Alay crest (Lenin Peak)', alai],
  ['mountain', 'Pamir crest (Sarykol Range)', tjkChn],
  ['mountain', 'Wakhjir Pass', afgChn],
  ['mountain', 'Hindu Kush: Wakhan, Baroghil Pass to Tirich Mir', hinduKush],
  ['mountain', 'Safed Koh crest to the Khyber Pass', safed],
  ['mountain', 'Safed Koh crest (Khyber to the Kurram)', kurram],
  ['mountain', 'Sulaiman Range', sulaiman],
  ['mountain', 'Kirthar Range to Cape Monze', kirtharSea]
];
const FRONT = [['mountain', 'Greater Caucasus', [seaEast[seaEast.length-1]].concat(caucasusW, geoCrest, azeCrest)]].concat(NE);
/* the Libya alternate keeps the old Africa route (Version 34): Tana, Lake Victoria and the Congo–Nile divide, with its weaker stretches */
const SOUTH = [
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
const ALTFRONT = [
  ['weak', 'Darfur and Jebel Marra', [B.ssd_caf[B.ssd_caf.length-1]].concat(marra, [ennediS0])],
  ['desert', 'Libyan Desert: Gilf Kebir, the Great Sand Sea and the Calanscio', [ennediS0].concat(ennediNE, libyan, seaSirte)]];
/* closed loops (clockwise: west coast north, then east, then back west along the south) */
const neLoop = [].concat(caspian, ustyurt, muynak, kyzylkum, nurata, turkestan, alai, tjkChn, afgChn, hinduKush, safed, kurram, sulaiman, kirtharSea);
const eastLoop = [].concat(seaEast, caucasusW, geoCrest, azeCrest, derbent, neLoop, seaArab, seaSom);
const dd = l => l.filter((p, i) => !i || p[0] !== l[i-1][0] || p[1] !== l[i-1][1]);
const loopMain = dd([].concat(seaWAf, seaAtl, seaWest, eastLoop, seaEAf));
const southLoop = [].concat(...SOUTH.slice().reverse().map(s => s[2].slice().reverse()));
const loopAlt = dd([].concat(seaEast, caucasusW, geoCrest, azeCrest, derbent, neLoop, seaArab, seaSom, southLoop, marra, [ennediS0], ennediNE, libyan, seaSirte));
const close = l => { const a = l[0], b = l[l.length-1]; return (a[0] === b[0] && a[1] === b[1]) ? l : l.concat([a]); };

/* ---------- inner sea: the Red Sea, inside the line and cut off from the Gulf of Aden at Bāb al-Mandab (the Persian Gulf is now open coast) ---------- */
const MOUTHS = [
  {n:'Bāb al-Mandab', p:[[43.62,12.82],[43.47,12.66],[43.33,12.47],[43.22,12.35]]}
];
MOUTHS.forEach(m => [m.p[0], m.p[m.p.length-1]].forEach(q => { if(!inMP(q, landNoVic)) console.log('WARNING mouth end not on land', m.n, q); }));
/* ---------- checks on the hand-drawn line ---------- */
const CMP = C.map(g => { const f = topojson.feature(geo, g).geometry; return [String(g.id), g.properties.n, f.type === 'Polygon' ? [f.coordinates] : f.coordinates]; });
const countryName = p => { const c = CMP.find(([id, n, mp]) => inMP(p, mp)); return c ? c[1] : '(sea)'; };
[['sea Atlantic', seaAtl], ['sea west', seaWest], ['sea east', seaEast], ['sea Arabian', seaArab], ['sea Somali', seaSom], ['sea East Africa', seaEAf], ['sea West Africa', seaWAf], ['sea Caspian', caspian], ['lake Victoria path', lakeVic.slice(1, -1)]].forEach(([n, pts]) => {
  const bad = pts.filter(q => inMP(q, n.startsWith('lake') ? landNoVic : land)); if(bad.length) console.log('WARNING', n, 'points on land:', JSON.stringify(bad)); });
/* the sea legs must not cross land between their waypoints either */
const crossesLand = (a, b) => { const n = Math.ceil(dist(a, b) / 0.04); for(let i = 1; i < n; i++){ const q = [a[0]+(b[0]-a[0])*i/n, a[1]+(b[1]-a[1])*i/n]; if(inMP(q, land)) return q; } return null; };
[['West Africa', [seaEAf[seaEAf.length-1]].concat(seaWAf, [seaAtl[0]])], ['Atlantic', seaAtl], ['west', seaWest], ['east', seaEast], ['Caspian', caspian.concat([garabogaz])], ['Arabian', [monze].concat(seaArab)], ['Somali', seaSom], ['East Africa', [seaSom[seaSom.length-1]].concat(seaEAf)]].forEach(([n, pts]) => {
  for(let i = 0; i+1 < pts.length; i++){ const q = crossesLand(pts[i], pts[i+1]); if(q && !(n === 'Caspian' && i+2 === pts.length) && !(n === 'Arabian' && i === 0)) console.log('WARNING sea leg', n, 'crosses land between', JSON.stringify(pts[i]), JSON.stringify(pts[i+1]), 'at', JSON.stringify(q)); } });
ISLES.forEach(([n, q]) => { if(!inMP(q, land)) console.log('WARNING island point not on land', n, JSON.stringify(q)); });
[['Nile-Congo and the rest of the Libya alternate', SOUTH]].forEach(([_, SS]) => SS.forEach(([k, n, pts]) => { const names = {}; pts.forEach((q, i) => { if(i % 4 === 0 || i === pts.length-1){ const c = countryName(q); names[c] = (names[c] || 0) + 1; } });
  console.log(('  ' + k).padEnd(10), n.padEnd(58), pts.length + ' pts', JSON.stringify(names)); }));
NE.forEach(([k, n, pts]) => { const names = {}; pts.forEach((q, i) => { if(i % 4 === 0 || i === pts.length-1){ const c = countryName(q); names[c] = (names[c] || 0) + 1; } });
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
    if(ISLES.some(([n, q]) => inPoly(q, p))) return true;      /* Socotra, the Canary Islands, Cape Verde, Zanzibar, Pemba, Mafia, the Comoros and the other named islands */
    if(!inside.has(id)) return false;
    let md = Infinity; for(const q of mainPts){ const d = Math.hypot(q[0]-c[0], q[1]-c[1]); if(d < md) md = d; }
    return md < 0.6; });
  terrLand = big.concat(islands);
  /* water inside the line; the parts closed off at the two mouths are the inner seas */
  let water = pc.difference([hand], landNoVic);
  MOUTHS.forEach(m => { water = pc.difference(water, buffer(m.p, 0.0004)); });
  const SEEDS = [[38.5,20.0]];   /* a point in the Red Sea */
  const inner = water.filter(p => SEEDS.some(q => inPoly(q, p)));
  console.log(name, 'inner seas', inner.length, inner.map(p => area([p])));
  const full = pc.union(terrLand, inner, ...MOUTHS.map(m => buffer(m.p, 0.0004)).flat().map(r => [r]));
  /* the border: outer rings only, split by kind */
  const fronts = name === 'alt' ? FRONT.concat(SOUTH, ALTFRONT) : FRONT;
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
  const states = [...acc.values()].filter(o => o.a > 300).map(o => { const p = 100*o.a/o.t; return {id:o.id, n:o.n, km2:o.a, pct: p < 1 ? Math.round(p*10)/10 : Math.round(p), ...(o.id === '643' ? {flag:'a strip of the Black Sea coast'} : o.id === '732' ? {flag:'status internationally disputed'} : o.id === '724' ? {flag:'the Canary Islands, Ceuta and Melilla only'} : o.id === '250' || o.id === 'FRA' ? {flag:'Mayotte only'} : {})}; })
    .sort((a, b) => b.km2 - a.km2);
  const shares = states;
  return {km2, lines: out, states};
}
const main = build(loopMain, 'main'), alt = build(loopAlt, 'alt');

/* ---------- the far east, shown with the Greater Caliphate: from Tirich Mir across the Indus and the Thar ---------- */
const riv = topojson.feature(geo, geo.objects.rivers).features;
const indusAll = riv.filter(f => (f.properties.n || '') === 'Indus').flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const indusLine = indusAll.reduce((a, l) => l.length > a.length ? l : a, []);
const indus = part(indusLine, [72.9,34.9], [70.4,28.95]);
const far = [tirich].concat([[72.7,36.0],[73.0,35.5]], indus, [[70.9,28.0],[71.0,26.8],[70.6,25.6],[70.0,24.25],[68.75,23.75]]);   /* from Tirich Mir, on the new line, east to the Indus and the Thar */

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
