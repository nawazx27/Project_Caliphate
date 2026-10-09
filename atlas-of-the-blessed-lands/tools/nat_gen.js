/* Natural borders of Dār al-Amān, Version 37 (your design, 2026-10-07) -> src/nat.json
   One closed ring of natural features, clockwise from the Adriatic, drawn round the whole of your Complete outline:
     1 Balkans      Rijeka, over Risnjak to the Kupa spring; the Kupa to Sisak; the Sava to Belgrade; the Danube (Chilia arm) to the Black Sea
     2 Caucasus     across the Black Sea to Anapa; the main crest of the Greater Caucasus to Bazardüzü, then the Samur to the Caspian
     3 Caspian      across the Caspian to the Garabogaz; the Ustyurt escarpment to the historic west shore of the Aral; the historic shore to the Amu Darya delta
     4 Central Asia the Amu Darya upstream, the Panj and the Pamir River to Zorkul, and the crest to the Pamir knot
     5 Himalaya     the rim of the Indus basin: the Karakoram crest, round the Indus and Sutlej headwaters by Kailash, the Sutlej–Ganges divide to the Yamuna's source
     6 India        the Yamuna down to the Chambal; the Chambal up to its source; over the Malwa Plateau to the Mahi's source; the Mahi to the Gulf of Khambhat
     7 Seas         the Arabian Sea, the Gulf of Aden, the Somali and Kenyan coast to the Tana mouth
     8 East Africa  the Tana up past Mount Kenya to its source on the Aberdares; the Aberdare crest; the Naivasha–Nakuru divide across the Rift
                    over Eburru; the Mau crest to Mau Summit; the Nyando down to the Winam Gulf; the lakeshore to Jinja;
                    the Victoria Nile through Lake Kyoga to Lake Albert
     9 Central Afr. the Nile–Congo divide to the Mbomou's source; the Mbomou and Ubangi to the Congo; the Congo to the Sangha; the Sangha and Mambéré
                    up to the Yadé Massif; along the Adamawa Plateau to the Benue's source
    10 West Africa  the Benue to Lokoja; the Niger upstream to its source; over the Fouta Djallon to the Senegal's source; the Senegal to the sea
    11 Seas         the Atlantic north to Gibraltar, the Mediterranean and the Adriatic back to Rijeka
   Where a river of the ring is also a national border, the border line of the base map is used, so the states table has no slivers.
   Islands follow the median-line rule: an island nearer to a shore inside the ring is inside (largest first; a decided island of 5,000 km² or more
   counts as a shore for smaller ones near it); the islands you named are fixed as you named them.
   Data: coasts, lakes and borders from the base map (Natural Earth 10m); rivers from Natural Earth 10m rivers_lake_centerlines, the Kupa from
   rivers_europe, the historic Aral shore from lakes_historic (tools/data). HydroSHEDS could not be reached from the build machine, so the
   two watersheds are the borders defined on them where there are such borders (DR Congo–Uganda, DR Congo–South Sudan; China–Pakistan and
   the Siachen crest on the Karakoram) and otherwise traced by hand, like the escarpments and ranges.
   Run: node --stack-size=30000 tools/nat_gen.js   (about 1–2 minutes)                                                                */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const R3 = v => Math.round(v*1000)/1000;
const DEBUG = process.env.NAT_DEBUG;

/* ---------- helpers ---------- */
const C = geo.objects.countries.geometries;
const dist = (a, b) => Math.hypot(a[0]-b[0], a[1]-b[1]);
const border = (a, b) => {   /* the shared border of two countries, stitched into one ordered line */
  const m = topojson.mesh(geo, geo.objects.countries, (x, y) => (String(x.id) === a && String(y.id) === b) || (String(x.id) === b && String(y.id) === a));
  const lines = m.coordinates.map(l => l.slice());
  if(!lines.length) throw new Error('no border ' + a + '-' + b);
  let out = lines.shift();
  while(lines.length){
    let best = null;
    lines.forEach((l, i) => { const s0 = out[0], e0 = out[out.length-1], ls = l[0], le = l[l.length-1];
      [[dist(e0, ls), 'end', l], [dist(e0, le), 'end', l.slice().reverse()], [dist(s0, le), 'start', l], [dist(s0, ls), 'start', l.slice().reverse()]]
        .forEach(([d, side, ll]) => { if(!best || d < best.d) best = {d, side, ll, i}; }); });
    lines.splice(best.i, 1);
    out = best.side === 'end' ? out.concat(best.ll) : best.ll.concat(out);
  }
  return out;
};
const nearest = (line, p) => { let bi = 0, bd = Infinity; line.forEach((q, i) => { const d = dist(q, p); if(d < bd){ bd = d; bi = i; } }); return bi; };
const part = (line, from, to) => { const i = nearest(line, from), j = nearest(line, to); return i <= j ? line.slice(i, j+1) : line.slice(j, i+1).reverse(); };
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
const len = l => l.reduce((t, p, i) => i ? t + dist(p, l[i-1]) : 0, 0);

/* ---------- rivers: Natural Earth lines, stitched into one path between two points ---------- */
const RIV = JSON.parse(fs.readFileSync(path.join(ROOT, 'rivers.geojson'))).features
  .concat(JSON.parse(fs.readFileSync(path.join(__dirname, 'data/ne_10m_rivers_europe_kupa.geojson'))).features);
const linesOf = names => RIV.filter(f => names.includes(f.properties.name)).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates).map(l => l.map(p => [p[0], p[1]]));
/* shortest path along the named rivers from the point nearest 'a' to the point nearest 'b' (the lines are split there, and joined where their ends meet) */
function river(names, a, b){
  let lines = linesOf(Array.isArray(names) ? names : [names]);
  if(!lines.length) throw new Error('no river ' + names);
  const cut = (lines, p) => { let bl = -1, bi = -1, bd = Infinity; lines.forEach((l, li) => l.forEach((q, i) => { const d = dist(q, p); if(d < bd){ bd = d; bl = li; bi = i; } }));
    const l = lines[bl], out = lines.filter((_, i) => i !== bl); if(bi > 0) out.push(l.slice(0, bi+1)); if(bi < l.length-1) out.push(l.slice(bi)); return {lines: out, node: l[bi], d: bd}; };
  const ca = cut(lines, a); const cb = cut(ca.lines, b); lines = cb.lines;
  if(ca.d > 0.05 || cb.d > 0.05) console.log('  note: river', names, 'ends snapped by', ca.d.toFixed(3), cb.d.toFixed(3));
  const key = p => p[0].toFixed(3) + ',' + p[1].toFixed(3);
  const nodes = new Map(); const node = p => { const k = key(p); if(!nodes.has(k)) nodes.set(k, {p, e:[]}); return nodes.get(k); };
  lines.forEach(l => { const s = node(l[0]), e = node(l[l.length-1]), L = len(l); s.e.push({to:e, l, L}); e.e.push({to:s, l:l.slice().reverse(), L}); });
  /* join ends that almost meet (the base data has small gaps where a river leaves a lake) */
  const all = [...nodes.values()];
  all.forEach(n => all.forEach(m => { if(n !== m && dist(n.p, m.p) < 0.07 && !n.e.some(e => e.to === m)){ const L = dist(n.p, m.p); n.e.push({to:m, l:[n.p, m.p], L}); } }));
  const A = node(ca.node), B = node(cb.node);
  const D = new Map([[A, 0]]), prev = new Map(), done = new Set();
  while(true){ let u = null, ud = Infinity; for(const [n, d] of D) if(!done.has(n) && d < ud){ ud = d; u = n; }
    if(!u) throw new Error('no river path ' + names); if(u === B) break; done.add(u);
    for(const e of u.e){ const nd = ud + e.L; if(nd < (D.has(e.to) ? D.get(e.to) : Infinity)){ D.set(e.to, nd); prev.set(e.to, {from:u, l:e.l}); } } }
  const segs = []; for(let n = B; n !== A; n = prev.get(n).from) segs.unshift(prev.get(n).l);
  return segs.reduce((o, l) => o.concat(o.length ? l.slice(1) : l), []);
}

/* ---------- the base land: the mainland of Afro-Eurasia and the islands ---------- */
const landAll = topojson.merge(geo, geo.objects.countries.geometries).coordinates;
const lakeF = topojson.feature(geo, geo.objects.lakes).features;
const lakeMP = re => { const f = lakeF.find(f => re.test(JSON.stringify(f.properties))); if(!f) throw new Error('no lake ' + re); return f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates; };
const victoriaMP = lakeMP(/Victoria/), albertMP = lakeMP(/Albert/);
const land = pc.difference(landAll, victoriaMP, albertMP);   /* the ring runs along Lake Victoria's shore and across the tip of Lake Albert: their water is not land */
const sizes = land.map(p => area([p]));
const mainIdx = sizes.indexOf(Math.max(...sizes));
const mainland = [land[mainIdx]];
const islandsAll = land.filter((_, i) => i !== mainIdx).map((p, i) => ({p, a: sizes[i >= mainIdx ? i+1 : i]}));
console.log('mainland', sizes[mainIdx], 'km²; islands', islandsAll.length);
const coastVerts = []; mainland[0].forEach(r => r.forEach(q => coastVerts.push(q)));
const coastNear = p => { let bd = Infinity, bp = null; for(const q of coastVerts){ const d = dist(q, p); if(d < bd){ bd = d; bp = q; } } return bp; };

/* ---------- borders used ---------- */
const B = {
  hrv_svn: border('191','705'), hrv_bih: border('191','070'), srb_rou: border('688','642'), bgr_rou: border('100','642'), rou_ukr: border('642','804'),
  rus_geo: border('643','268'), rus_aze: border('643','031'), kaz_tkm: border('398','795'),
  afg_uzb: border('004','860'), afg_tjk: border('004','762'), afg_chn: border('004','156'), chn_pak: border('156','586'), chn_kas: border('156','KAS'), chn_ind: border('156','356'),
  uga_cod: border('800','180'), ssd_cod: border('728','180'), caf_cod: border('140','180'), cog_cod: border('178','180'),
  sen_mrt: border('686','478'), gin_sle: border('324','694')
};
const from = (line, p) => line.slice(nearest(line, p));
const upto = (line, p) => line.slice(0, nearest(line, p)+1);
const rev = l => l.slice().reverse();

/* ================= the ring, clockwise from the Adriatic: [kind, name, points] ================= */
const RING = [];
const add = (k, n, pts) => RING.push([k, n, pts]);
/* 1. Balkans */
const rijeka = coastNear([14.44,45.325]);
add('shed', 'Rječina and the Adriatic–Black Sea watershed by Risnjak to the Kupa spring (by hand)', [rijeka, [14.45,45.36], [14.47,45.40], [14.50,45.43], [14.61,45.44], [14.69,45.49]]);   /* up the Rječina valley to the divide, over Risnjak to the spring */
const kupaB = part(B.hrv_svn, [14.72,45.51], [15.36,45.66]);   /* the Kupa where it is the Croatia–Slovenia border */
add('river', 'Kupa', [[14.69,45.49]].concat(kupaB));
const kupaLow = river('Kupa', [15.55,45.49], [16.37,45.47]);    /* Karlovac to Sisak */
add('river', 'Kupa', [kupaB[kupaB.length-1], [15.42,45.635], [15.48,45.60], [15.53,45.53]].concat(kupaLow));   /* Ozalj to Karlovac by hand: not in the base data */
const sisak = kupaLow[kupaLow.length-1];
const savaHB = part(B.hrv_bih, [16.93,45.27], [19.016,44.865]);     /* the Sava where it is the Croatia–Bosnia border, from the Una to the Drina corner */
add('river', 'Sava', river('Sava', sisak, savaHB[0]).concat(savaHB.slice(1)));
const belgrade = [20.455,44.840];
add('river', 'Sava', river('Sava', savaHB[savaHB.length-1], belgrade));
const danSR = part(B.srb_rou, [21.37,44.80], [22.692,44.228]);
const danBR = part(B.bgr_rou, [22.692,44.228], [27.27,44.125]);
const danRU = part(B.rou_ukr, [28.200,45.462], [29.659,45.216]);   /* from the Prut mouth down the Chilia arm to the sea */
add('river', 'Danube', river('Danube', belgrade, danSR[0]).concat(danSR.slice(1), danBR.slice(1), river('Danube', danBR[danBR.length-1], danRU[0]).slice(1), danRU.slice(1)));
const danMouth = danRU[danRU.length-1];
/* 2. the Black Sea and the Caucasus */
add('sea', 'Black Sea', [danMouth, [29.95,45.10], [31.2,44.25], [33.6,43.7], [36.3,44.3], [36.95,44.62]]);
const geoCrest = from(B.rus_geo.slice().reverse(), [40.45,43.58]);   /* rus_geo runs from the Azerbaijan corner to the Psou mouth */
add('crest', 'Greater Caucasus', [coastNear([37.36,44.82]), [37.55,44.83],[37.95,44.68],[38.35,44.48],[38.85,44.30],[39.30,44.10],[39.75,43.95],[40.15,43.78]].concat(geoCrest));
const geoEnd = B.rus_geo[0];
add('crest', 'Greater Caucasus and the Samur', B.rus_aze.slice().reverse());   /* the crest to Bazardüzü, then the Samur to the Caspian */
const samurMouth = B.rus_aze[0];
/* 3. the Caspian, the Ustyurt and the historic Aral shore */
const kazTkm = B.kaz_tkm.slice().reverse();   /* from the Caspian at the Garabogaz to the Uzbekistan corner */
add('sea', 'Caspian Sea', [samurMouth, [49.3,41.95], [50.6,41.95], [51.8,41.85], kazTkm[0]]);
add('scarp', 'Ustyurt escarpment', kazTkm);
const ARAL = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/ne_10m_lakes_historic_aral.geojson'))).features[0].geometry.coordinates[0];
const aralSW = ARAL[nearest(ARAL, [58.30,43.72])];
add('scarp', 'Ustyurt escarpment', [kazTkm[kazTkm.length-1], [56.5,41.33], [56.82,41.45], [56.85,41.85], [57.0,42.15], [57.35,42.35], [57.6,42.42], [58.1,42.75], [58.5,43.05], [58.35,43.45], aralSW]);
/* the Amu Darya meets the historic shore where its line first enters the old sea */
const amuAll = river('Amu  Darya', [59.541,44.148], [66.52,37.364]);   /* delta to the Afghanistan corner (downstream to upstream) */
let ja = 0; while(ja < amuAll.length && ptIn(amuAll[ja], ARAL)) ja++;
const amuJ = amuAll[ja];
const iJ = nearest(ARAL, amuJ), iS = nearest(ARAL, aralSW);
const arcA = []; for(let k = iS; ; k = (k+1) % (ARAL.length-1)){ arcA.push(ARAL[k]); if(k === iJ) break; }
const arcB = []; for(let k = iS; ; k = (k-1+ARAL.length-1) % (ARAL.length-1)){ arcB.push(ARAL[k]); if(k === iJ) break; }
const shore = (arcA.reduce((s, p) => s + p[1], 0)/arcA.length < arcB.reduce((s, p) => s + p[1], 0)/arcB.length) ? arcA : arcB;   /* the southern arc */
add('shore', 'Aral Sea, historic shore', shore.concat([amuJ]));
/* 4. Central Asia */
add('river', 'Amu Darya', amuAll.slice(ja));
const afgUzb = part(B.afg_uzb, [66.520,37.364], [67.781,37.188]);
add('river', 'Amu Darya', afgUzb);
const afgTjk = part(B.afg_tjk, [67.781,37.188], [74.893,37.231]);
const zorkul = nearest(afgTjk, [73.70,37.42]);
add('river', 'Amu Darya, Panj and Pamir River', afgTjk.slice(0, zorkul+1));
add('crest', 'Pamir knot', afgTjk.slice(zorkul).concat(part(B.afg_chn, [74.893,37.231], [74.542,37.022]).slice(1)));
/* 5. the rim of the Indus basin */
add('shed', 'Karakoram crest', part(B.chn_pak, [74.542,37.022], [76.777,35.646]).concat(part(B.chn_kas, [76.777,35.646], [77.800,35.496]).slice(1)));
const lipulekh = [80.996,30.197];
add('shed', 'Indus basin rim (Ladakh and western Tibet, by hand)', [[77.800,35.496],[78.05,35.35],[78.30,35.15],[78.55,34.95],[78.85,34.75],[79.10,34.55],[79.45,34.40],[79.30,34.15],[78.95,34.05],[78.60,34.05],[78.45,33.85],[78.55,33.55],[78.85,33.38],[79.20,33.18],[79.55,33.02],[80.00,32.98],[80.50,32.85],[81.10,32.72],[81.50,32.35],[81.55,32.0],[81.75,31.65],[81.95,31.15],[81.85,30.75],[81.55,30.52],[81.25,30.50],[81.05,30.58],[80.88,30.64],[80.82,30.50],[80.92,30.33],[80.944,30.270]]);   /* north of the Indus (Senge Zangbo) and round its source; east of Manasarovar; west round the head of the Karnali to Lipulekh */
const sgB = part(B.chn_ind, [80.944,30.270], [78.76,31.40]);   /* the Sutlej–Ganges divide where it is the India–China border (Uttarakhand) */
add('shed', 'Sutlej–Ganges divide', sgB);
const chambalMouth = [79.245,26.502];
const yamuna = river('Yamuna', [78.340,30.915], chambalMouth), yamSrc = yamuna[0];
add('shed', 'Sutlej–Ganges divide to the Yamuna source (by hand)', [sgB[sgB.length-1], [78.58,31.30], [78.37,31.21], [78.45,31.08], [78.46,31.01], yamSrc]);
/* 6. India */
add('river', 'Yamuna', yamuna);
const chambal = river('Chambal', yamuna[yamuna.length-1], [75.667,22.473]), mahi = river('Mahi', [74.973,22.730], [72.907,22.279]);
const chambalSrc = chambal[chambal.length-1], mahiSrc = mahi[0], mahiMouth = mahi[mahi.length-1];
add('river', 'Chambal', chambal);
add('crest', 'Malwa Plateau', [chambalSrc, [75.50,22.49], [75.30,22.53], [75.12,22.62], mahiSrc]);   /* along the top of the Vindhya scarp */
add('river', 'Mahi', mahi);
/* 7. the seas: the Gulf of Khambhat, the Arabian Sea, Socotra (inside), the Gulf of Aden, the Somali and Kenyan coast */
const tanaMouth = [40.513,-2.525];
add('sea', 'Arabian Sea', [mahiMouth, [72.90,22.255], [72.83,22.245], [72.6,22.235], [72.45,22.12], [72.40,22.0], [72.38,21.6], [72.40,21.0], [72.2,20.4], [70.0,19.3], [66.0,17.0], [60.0,13.6], [55.5,11.6], [53.3,11.3], [52.0,11.3],
  [52.3,10.4],[51.7,9.3],[51.0,8.0],[50.3,7.0],[49.6,6.0],[48.9,5.0],[48.0,4.0],[47.0,3.0],[46.1,2.0],[44.8,1.0],[43.4,0.0],[42.3,-1.0],[41.8,-2.0],[41.2,-2.75],[40.7,-2.68], tanaMouth]);
/* 8. East Africa */
/* the Tana upstream past Mount Kenya to its source on the Aberdares; then natural features only, placed by hand (not in the base data) */
const tanaUp = river('Tana', tanaMouth, [36.704,-0.350]);
add('river', 'Tana', tanaUp);
add('crest', 'Aberdare crest (by hand)', [tanaUp[tanaUp.length-1], [36.68,-0.30], [36.60,-0.24]]);
add('shed', 'Naivasha–Nakuru divide over Eburru (by hand)', [[36.60,-0.24], [36.42,-0.24], [36.28,-0.33], [36.22,-0.47], [36.24,-0.63], [36.10,-0.62], [35.95,-0.55]]);
add('crest', 'Mau crest to Mau Summit (by hand)', [[35.95,-0.55], [35.86,-0.42], [35.78,-0.30], [35.70,-0.17]]);
const winamHead = coastNear([34.86,-0.27]);
add('river', 'Nyando to the Winam Gulf (by hand, past Muhoroni and Ahero)', [[35.70,-0.17], [35.55,-0.13], [35.38,-0.13], [35.20,-0.16], [35.05,-0.17], [34.93,-0.18], winamHead]);
const jinja = [33.187,0.428];
add('lake', 'Lake Victoria', [winamHead, [34.825,-0.272], [34.80,-0.25], [34.62,-0.22], [34.45,-0.26], [34.40,-0.33], [34.35,-0.38], [34.30,-0.405], [34.26,-0.40], [34.20,-0.37], [34.10,-0.32], [33.95,-0.12], [33.70,0.05], [33.45,0.18], [33.27,0.33], jinja]);
const vn = river('Victoria Nile', jinja, [31.366,2.193]);
add('river', 'Victoria Nile and Lake Kyoga', vn);
const ugaCod = B.uga_cod;   /* from the South Sudan corner (30.84,3.49) down the Lake Albert line */
const albertN = nearest(ugaCod, [31.267,2.173]);
add('lake', 'Lake Albert', [vn[vn.length-1], [31.33,2.19], ugaCod[albertN]]);
/* 9. Central Africa */
add('shed', 'Nile–Congo divide', ugaCod.slice(0, albertN+1).reverse().concat(B.ssd_cod.slice(1)));
add('river', 'Mbomou and Ubangi', B.caf_cod.slice().reverse());
const sanghaMouth = [16.849,-1.251];
const cogCod = upto(B.cog_cod, sanghaMouth);
add('river', 'Ubangi and Congo', cogCod);
const nola = [16.06,3.52];
const sangha = river(['Sangha','Kadéï'], cogCod[cogCod.length-1], nola);
add('river', 'Sangha', sangha);
const mambereSrc = [14.78,6.15];
add('river', 'Mambéré (by hand: not in the base data)', [sangha[sangha.length-1], [16.00,3.85], [15.95,4.40], [15.88,4.94], [15.62,5.25], [15.30,5.55], [14.98,5.85], mambereSrc]);
const lokoja = [6.767,7.786];
const benue = river(['Bénoué','Benue'], [13.524,7.777], lokoja), benueSrc = benue[0];
add('crest', 'Yadé Massif and Adamawa Plateau', [mambereSrc, [14.88,6.45], [14.80,6.85], [14.45,6.95], [14.10,7.05], [13.75,7.25], [13.45,7.40], [13.40,7.62], benueSrc]);   /* north of the heads of the Lom and the Djérem, south of the Vina */
/* 10. West Africa */
add('river', 'Benue', benue);
const niger = river('Niger', benue[benue.length-1], [-10.732,9.090]), nigerSrc = niger[niger.length-1];
add('river', 'Niger', niger);
const senMrt0 = B.sen_mrt.slice().reverse();
const senegal = river(['Bafing','Sénégal'], [-12.088,10.590], senMrt0[0]), bafingSrc = senegal[0];
add('crest', 'Fouta Djallon', part(B.gin_sle, nigerSrc, [-11.20,9.98]).concat([[-11.55,10.12], [-11.95,10.30], [-12.15,10.45], bafingSrc]));   /* the Guinea–Sierra Leone border, on the Niger's watershed, then over the highland */
const senMrt = B.sen_mrt.slice().reverse();   /* from the Mali corner down the Senegal to its mouth */
add('river', 'Senegal', senegal.concat(senMrt.slice(1)));
const senMouth = senMrt[senMrt.length-1];
/* 11. the Atlantic and the Mediterranean, back to Rijeka */
add('sea', 'Atlantic and Mediterranean', [senMouth, [-16.75,15.95], [-17.2,16.6], [-17.4,18.2], [-17.5,20.0], [-17.6,21.0], [-17.9,23.0], [-17.0,24.5], [-15.5,26.0], [-13.6,27.6], [-13.0,28.7], [-10.6,30.6], [-10.6,33.6],
  [-7.0,35.62], [-5.6,35.97], [-4.0,36.05], [-2.0,36.25], [0.5,36.75], [3.5,37.15], [6.5,37.45], [8.8,37.66], [10.6,37.6], [11.4,37.15], [12.2,36.3], [13.4,35.6], [15.6,35.4],
  [17.5,37.2], [18.8,39.2], [18.95,40.25], [18.4,41.1], [17.2,42.0], [16.0,42.8], [14.9,43.55], [14.1,44.35], [14.05,44.75], [14.25,45.05], [14.38,45.25], rijeka]);

/* ---------- the loop, and checks ---------- */
const dd = l => l.filter((p, i) => !i || p[0] !== l[i-1][0] || p[1] !== l[i-1][1]);
const gaps = []; RING.forEach(([k, n, pts], i) => { const nx = RING[(i+1) % RING.length][2]; const g = dist(pts[pts.length-1], nx[0]); if(g > 0.02) gaps.push(n + ' -> ' + RING[(i+1) % RING.length][1] + ' gap ' + g.toFixed(3)); });
if(gaps.length) console.log('JOINS with a gap (joined straight):', gaps.join(' | '));
const loop = dd([].concat(...RING.map(s => s[2])));
const close = l => { const a = l[0], b = l[l.length-1]; return (a[0] === b[0] && a[1] === b[1]) ? l : l.concat([a]); };
const segHit = (p1, p2, p3, p4) => { const d = (p2[0]-p1[0])*(p4[1]-p3[1]) - (p2[1]-p1[1])*(p4[0]-p3[0]); if(Math.abs(d) < 1e-14) return false;
  const t = ((p3[0]-p1[0])*(p4[1]-p3[1]) - (p3[1]-p1[1])*(p4[0]-p3[0])) / d, u = ((p3[0]-p1[0])*(p2[1]-p1[1]) - (p3[1]-p1[1])*(p2[0]-p1[0])) / d;
  return t > 1e-9 && t < 1-1e-9 && u > 1e-9 && u < 1-1e-9; };
{ let c = 0; const L = close(loop); const bb = L.slice(0, -1).map((a, i) => { const b = L[i+1]; return [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])]; });
  for(let i = 0; i < bb.length; i++) for(let j = i+2; j < bb.length; j++){ if(i === 0 && j === bb.length-1) continue; const A = bb[i], Bx = bb[j]; if(A[2] < Bx[0] || Bx[2] < A[0] || A[3] < Bx[1] || Bx[3] < A[1]) continue;
    if(segHit(L[i], L[i+1], L[j], L[j+1])){ c++; if(c < 10) console.log('SELF-INTERSECTION near', JSON.stringify(L[i]), JSON.stringify(L[j])); } }
  console.log('loop:', L.length, 'points,', c, 'self-intersections'); }
const crossesLand = (a, b) => { const n = Math.ceil(dist(a, b) / 0.02); for(let i = 1; i < n; i++){ const q = [a[0]+(b[0]-a[0])*i/n, a[1]+(b[1]-a[1])*i/n]; if(inMP(q, mainland)) return q; } return null; };
RING.filter(s => s[0] === 'sea' || s[0] === 'lake').forEach(([k, n, pts]) => { for(let i = 0; i+1 < pts.length; i++){ const q = crossesLand(pts[i], pts[i+1]); if(q) console.log('WARNING', n, 'leg crosses the mainland between', JSON.stringify(pts[i]), JSON.stringify(pts[i+1]), 'at', JSON.stringify(q.map(R3))); } });

/* ---------- the territory ---------- */
const hand = [close(loop)];
let terrMain = pc.intersection(mainland, [hand]);
const mainIn = terrMain.filter(p => area([p]) > 20000);
const cutBits = terrMain.filter(p => area([p]) <= 20000);
console.log('mainland pieces inside:', mainIn.length, mainIn.map(p => area([p])), 'small cut pieces dropped:', cutBits.length, cutBits.map(p => area([p])).sort((a, b) => b - a).slice(0, 8));
const mainOut = pc.difference(mainland, mainIn);
/* the median-line rule for islands */
const sample = (mp, step) => { const out = []; mp.forEach(p => p.forEach(r => r.forEach((q, i) => { if(i % step === 0) out.push(q); }))); return out; };
const IN_SH = sample(mainIn, 2), OUT_SH = sample(mainOut, 2);
const grid = pts => { const g = new Map(); pts.forEach(q => { const k = Math.floor(q[0]) + ',' + Math.floor(q[1]); if(!g.has(k)) g.set(k, []); g.get(k).push(q); }); return g; };
const kmd = (a, b) => { const la = (a[1]+b[1])/2 * Math.PI/180; return Math.hypot((a[0]-b[0]) * Math.cos(la), a[1]-b[1]) * 111.2; };
const nearestIn = (g, p, maxR = 25) => { let best = Infinity; const x0 = Math.floor(p[0]), y0 = Math.floor(p[1]);
  for(let r = 0; r <= maxR; r++){ for(let dx = -r; dx <= r; dx++) for(let dy = -r; dy <= r; dy++){ if(Math.max(Math.abs(dx), Math.abs(dy)) !== r) continue; const c = g.get((x0+dx) + ',' + (y0+dy)); if(c) c.forEach(q => { const d = kmd(p, q); if(d < best) best = d; }); }
    if(best < (r - 1) * 50) break; }
  return best; };
const gIn = grid(IN_SH), gOut = grid(OUT_SH);
/* the islands you named; each by a point on it */
const NAMED = {in: [['Crete',[24.9,35.25]],['Rhodes',[28.0,36.25]],['Kos',[27.15,36.85]],['Karpathos',[27.15,35.6]],['Kalymnos',[26.98,36.98]],['Leros',[26.84,37.15]],['Patmos',[26.55,37.32]],['Symi',[27.84,36.59]],['Tilos',[27.38,36.44]],['Nisyros',[27.17,36.59]],['Kasos',[26.92,35.39]],
    ['Cyprus',[33.0,35.0]],['Pantelleria',[11.98,36.79]],['Lampedusa',[12.6,35.51]],['Bahrain',[50.55,26.05]],['Socotra',[53.95,12.55]],['Dahlak',[40.1,15.75]],['Farasan',[41.9,16.75]]],
  out: [['Sicily',[14.2,37.5]],['Malta',[14.43,35.88]],['Gozo',[14.25,36.05]],['Sardinia',[9.0,40.0]],['Corsica',[9.1,42.1]],['Mallorca',[2.95,39.6]],['Menorca',[4.1,39.95]],['Ibiza',[1.4,38.98]],['Formentera',[1.45,38.7]]]};
const named = new Map(); for(const side of ['in', 'out']) NAMED[side].forEach(([n, q]) => { const isl = islandsAll.find(o => inPoly(q, o.p)); if(!isl) console.log('WARNING named island not found', n); else named.set(isl, {side, n}); });
const order = islandsAll.slice().sort((a, b) => b.a - a.a);
const decided = []; const conflicts = []; const notable = [];
order.forEach(o => {
  const c = d3.polygonCentroid(o.p[0]); const ring = o.p[0]; const step = Math.max(1, Math.floor(ring.length / 40));
  const pts = ring.filter((_, i) => i % step === 0);
  let dIn = Infinity, dOut = Infinity;
  for(const q of pts){ dIn = Math.min(dIn, nearestIn(gIn, q)); dOut = Math.min(dOut, nearestIn(gOut, q)); }
  /* islands already decided count as shores too */
  const bx = [Math.min(...pts.map(q => q[0])), Math.min(...pts.map(q => q[1])), Math.max(...pts.map(q => q[0])), Math.max(...pts.map(q => q[1]))];
  for(const d of decided){ if(d.b[0] > bx[2] + 12 || bx[0] > d.b[2] + 12 || d.b[1] > bx[3] + 12 || bx[1] > d.b[3] + 12) continue; let m = Infinity; for(const q of pts) for(const r of d.pts) m = Math.min(m, kmd(q, r)); if(d.inside) dIn = Math.min(dIn, m); else dOut = Math.min(dOut, m); }
  let inside = dIn < dOut;
  const nm = named.get(o);
  if(nm){ const want = nm.side === 'in'; if(want !== inside) conflicts.push(`${nm.n}: by the rule ${inside ? 'inside' : 'outside'} (${Math.round(dIn)} km to an inside shore, ${Math.round(dOut)} km to an outside one); set ${nm.side} as you named it`); inside = want; }
  if(o.a > 400 && dIn < 900) notable.push(`${inside ? 'IN ' : 'out'} ${String(o.a).padStart(7)} km² at ${R3(c[0])},${R3(c[1])}  in ${Math.round(dIn)} / out ${Math.round(dOut)} km${nm ? ' (' + nm.n + ')' : ''}`);
  o.inside = inside; if(o.a >= 5000){   /* large islands, once decided, count as shores for the smaller ones near them (Madagascar for the Seychelles, Sicily for Malta) */ const st = Math.max(1, Math.floor(ring.length / 24)); const dp = ring.filter((_, i) => i % st === 0); decided.push({c, pts: dp, inside, b: [Math.min(...ring.map(q => q[0])), Math.min(...ring.map(q => q[1])), Math.max(...ring.map(q => q[0])), Math.max(...ring.map(q => q[1]))]}); }
});
if(conflicts.length) console.log('named islands where the rule disagrees:\n  ' + conflicts.join('\n  '));
console.log('islands over 400 km² near the ring:\n  ' + notable.join('\n  '));
const islIn = order.filter(o => o.inside).map(o => o.p);
const terr = mainIn.concat(islIn);
const km2 = area(terr);
console.log('territory', km2, 'km²;', islIn.length, 'islands inside');
if(DEBUG) fs.writeFileSync(path.join(DEBUG, 'terr_main.json'), JSON.stringify({terr, loop: hand[0], ring: RING}));

/* ---------- is the whole Complete outline inside? ---------- */
{ const CAL = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/caliph.json'))).x.polys;
  const outside = pc.difference(CAL, hand);   /* against the ring itself, so differences in the drawing of the coast do not count */
  const bits = outside.map(p => ({a: area([p]), c: d3.polygonCentroid(p[0]).map(R3)})).filter(b => b.a > 0).sort((a, b) => b.a - a.a);
  console.log('Complete outline outside the ring:', bits.reduce((t, b) => t + b.a, 0), 'km² in', bits.length, 'pieces; largest', JSON.stringify(bits.slice(0, 12))); }

/* ---------- the border lines, by kind ---------- */
const lakeRings = [[victoriaMP, 'Lake Victoria'], [albertMP, 'Lake Albert']].map(([mp, n]) => [n, mp.flatMap(poly => poly)]);
const unknown = [];
const kindOf = (a, b) => { const m = [(a[0]+b[0])/2, (a[1]+b[1])/2];
  for(const [k, n, pts] of RING) if(k !== 'sea' && k !== 'lake' && onLine(m, pts, 2e-6)) return [k, n];
  for(const [n, rings] of lakeRings) if(rings.some(r => onLine(m, r, 2e-6))) return ['lake', n];
  if(onLine(m, hand[0], 2e-6)){   /* a short straight join between two segments: it takes the kind of the nearer one */
    let best = null, bd = Infinity; RING.forEach(([k, n, pts]) => { if(k === 'sea') return; [pts[0], pts[pts.length-1]].forEach(q => { const d = dist(q, m); if(d < bd){ bd = d; best = [k === 'lake' ? 'lake' : k, n]; } }); });
    if(best && bd < 0.3) return best; unknown.push(R3(m[0]) + ',' + R3(m[1])); }
  return ['coast', null]; };
const lines = []; let ri = 0;
terr.forEach(poly => { if(area([poly]) < 250) return;   /* tiny islands: no outline */
  const r = poly[0]; let cur = null; ri++;
  for(let i = 0; i+1 < r.length; i++){
    const [k, n] = kindOf(r[i], r[i+1]);
    if(!cur || cur.k !== k || cur.n !== n){ if(cur) lines.push(cur); cur = {k, n, r:ri, p:[r[i]]}; }
    cur.p.push(r[i+1]);
  }
  if(cur) lines.push(cur);
});
if(unknown.length) console.log('edges on the ring that no segment claims:', unknown.length, unknown.slice(0, 12).join(' '));
const out = lines.map(l => ({k:l.k, n:l.n, r:l.r, p: rdp(l.p, l.k === 'coast' ? 0.004 : 0.006).map(q => [R3(q[0]), R3(q[1])])})).filter(l => l.p.length > 1);
{ const by = {}; out.forEach(l => { const key = l.k + ' · ' + (l.n || ''); by[key] = (by[key] || 0) + l.p.length; }); console.log('line points by kind:', JSON.stringify(by)); }

/* ---------- the states inside, with the area and the share of each ---------- */
const FLAGS = {'643':'the Black Sea coast south of the Caucasus crest', '732':'status internationally disputed', '724':'Ceuta, Melilla and the Canary Islands', '380':'Lampedusa and Pantelleria',
  '620':'Madeira', '156':'the upper Indus and Sutlej in western Tibet', 'KAS':'disputed between India and Pakistan'};
const acc = new Map();
C.forEach(g => { const f = topojson.feature(geo, g).geometry; const mp = f.type === 'Polygon' ? [f.coordinates] : f.coordinates;
  let a = 0; try { a = area(pc.intersection(mp, terr)); } catch(e){}
  const t = area(mp); let id = String(g.id), n = g.properties.n;
  if(['196','CYN','CNM'].includes(id)){ id = 'CYP'; n = 'Cyprus (the whole island)'; }
  if(n === 'Bir Tawil') n = 'Bir Tawil (unclaimed)';
  const o = acc.get(id) || {id, n, a:0, t:0}; o.a += a; o.t += t; acc.set(id, o); });
console.log('small pieces of states (not listed unless named below):', [...acc.values()].filter(o => o.a > 0 && o.a <= 300).map(o => o.n + ' ' + o.a + ' km²').join(', '));
const states = [...acc.values()].filter(o => o.a > 50).map(o => { const p = 100*o.a/o.t; return {id:o.id, n:o.n, km2:o.a, pct: p < 1 ? Math.max(0.1, Math.round(p*10)/10) : p > 99 && p < 99.5 ? 99 : Math.round(p), ...(FLAGS[o.id] ? {flag: FLAGS[o.id]} : {})}; })
  .sort((a, b) => b.km2 - a.km2);
console.log('states', states.length + ':', states.map(s => s.n + ' ' + s.pct + '%').join(', '));
const main = {km2, lines: out, states};

/* ---------- Natural + political (Version 40, Nawaz's choice): the same ring, but every state it cuts is taken whole or left out whole, so every edge
   is a present-day international border or a coast. Majority rule: a state comes in whole if more than half of it is inside the ring; every state
   in the Complete outline comes in whole too (Uganda, 48% inside the ring). In Kashmir the base map's de facto lines are used. ---------- */
const polStates = (() => {
  const CALX = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/caliph.json'))).x.states.map(s => s.id);
  const ids = new Set(states.filter(s => s.pct > 50).map(s => s.id).concat(CALX));
  const geoms = C.filter(g => { const id = String(g.id); return ids.has(id) || (ids.has('CYP') && ['196','CYN','CNM'].includes(id)); });
  const merged = topojson.merge(geo, geoms).coordinates;
  const landP = pc.difference(merged, victoriaMP, albertMP);
  const km2p = area(landP);
  const polys = merged.filter(p => area([p]) >= 250).map(p => [p[0]].concat(p.slice(1).filter(h => area([h]) > 5000))).map(p => p.map(r => rdp(r, 0.008).map(q => [R3(q[0]), R3(q[1])])));
  const FL = {'732':'status internationally disputed', 'KAS':'disputed between India and Pakistan', 'ESB':'British sovereign base area', 'WSB':'British sovereign base area', 'BRT':'claimed by neither Egypt nor Sudan'};
  const st = [...acc.values()].filter(o => ids.has(o.id)).map(o => ({id:o.id, n:o.n, km2:o.t, pct:100, ...(FL[o.id] ? {flag:FL[o.id]} : {})})).sort((a, b) => b.km2 - a.km2);
  const added = st.filter(s => { const n = states.find(x => x.id === s.id); return n && n.pct < 100; }).map(s => s.n + ' (' + states.find(x => x.id === s.id).pct + '% in the ring)');
  const dropped = states.filter(s => !ids.has(s.id)).map(s => s.n + ' ' + s.pct + '%');
  console.log('natural + political:', km2p, 'km² in', st.length, 'states; taken whole:', added.join(', '), '| left out:', dropped.join(', '));
  return {km2: km2p, polys, states: st, taken: added.length, left: dropped};
})();

/* ---------- internal lines (unchanged) ---------- */
const riv = topojson.feature(geo, geo.objects.rivers).features;
const taurus = [[29.6,36.9],[30.4,37.15],[31.3,37.2],[32.3,37.05],[33.4,37.05],[34.4,37.3],[35.2,37.7],[36.2,37.95],[37.3,38.1],[38.4,38.35],[39.6,38.4],[40.8,38.3],[41.9,38.15],[42.9,37.85],[43.8,37.5],[44.5,37.35]];
const redsea = [[32.55,29.9],[33.0,29.1],[33.7,28.1],[34.3,27.5],[35.1,26.3],[36.0,24.8],[36.9,23.2],[37.8,21.6],[38.6,20.0],[39.5,18.4],[40.5,16.6],[41.6,15.0],[42.4,13.8],[43.3,12.7]];
const RIVN = {Nile:['Nile','El Bahr el Abyad','Bahr el Jebel','Albert Nile','Victoria Nile','Rosetta Branch','Damietta Branch','Blue Nile','Abay','Bahr el Azraq'], Tigris:['Tigris','Dicle'], Euphrates:['Euphrates','Firat','Al Furat','Shatt al Arab']};
const blue = RIV.filter(f => ['Abay','El Bahr el Azraq'].includes(f.properties.name)).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates);
const rivers = Object.entries(RIVN).map(([n, names]) => ({n, p: riv.filter(f => names.includes(f.properties.n)).flatMap(f => f.geometry.type === 'LineString' ? [f.geometry.coordinates] : f.geometry.coordinates)
  .concat(n === 'Nile' ? blue : []).map(l => rdp(l, 0.003).map(q => [R3(q[0]), R3(q[1])]))}));

const outJ = {main, pol: polStates, intl:{taurus, redsea, rivers}};
fs.writeFileSync(path.join(ROOT, 'src/nat.json'), JSON.stringify(outJ));
console.log('wrote src/nat.json', JSON.stringify(outJ).length, 'bytes');
