// Build the "one outline around every best land" envelope (my synthesis) and the share of each modern state inside it.
const fs = require('fs');
const pc = require('polygon-clipping');
const topo = require('topojson-client');
const d3 = require('d3');
const D = require('./tools/data_mod.js');      // atlas data, built by tools/make_data_mod.js
const g = require('./geo2.json');
const fc = topo.feature(g, g.objects.countries);
const byId = id => fc.features.find(f => f.id === id);
const geomOf = ids => ids.map(id => { const f = byId(id); if(!f) throw new Error('no country '+id); return f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates; }).flat();

const ring = runs => { const out = []; runs.forEach((r,i)=>r.p.forEach((pt,j)=>{ if(i>0 && j===0) return; out.push(pt); })); if(out[0][0]!==out[out.length-1][0] || out[0][1]!==out[out.length-1][1]) out.push(out[0]); return out; };
const closed = pts => { const o = pts.slice(); if(o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1]) o.push(o[0]); return o; };

// Sinai, generous at sea (cut to Egypt below): Port Said, al-ʿArīsh, Rafaḥ, Ṭābā, Rās Muḥammad, Suez, Ismailia
const SINAI = closed([[32.25,31.40],[34.27,31.40],[34.92,29.48],[34.30,27.60],[32.50,29.90],[32.25,30.60]]);

const ARAB = ['682','887','512'];
const LEVANT = ['760','422','376','275','400','792','368','682','818'];
const pieces = [
  {n:'al-Shām (with every edge some sources include)', rings:[ring(D.SHAM_OUTER)], allow:LEVANT},
  {n:'Filasṭīn', rings:[ring(D.FIL_OUTER)], allow:LEVANT},
  {n:'al-Ḥijāz (with its contested edges)', rings:[ring(D.HIJAZ_OUTER)], allow:['682','400']},
  {n:'Tihāmah', rings:[ring(D.TIHAMAH)], allow:ARAB},
  {n:'al-Yaman', rings:[ring(D.YEMEN)], allow:ARAB},
  {n:'Sinai', rings:[SINAI], allow:['818']},
  {n:'Miṣr: the Nile valley', rings:[ring(D.MISR_CORE)], allow:['818']},
  {n:'Miṣr: the Delta', rings:[ring(D.DELTA)], allow:['818']},
  {n:'Miṣr: Cairo, joining valley and Delta', rings:[closed([[30.95,29.80],[31.55,29.80],[31.55,30.30],[30.95,30.30]])], allow:['818']}
];
let parts = [];
for(const p of pieces){
  const allowed = geomOf(p.allow);
  const cut = pc.intersection([p.rings], allowed);
  if(!cut.length) console.warn('empty piece', p.n);
  parts.push(cut);
}
let U = parts.reduce((a,b)=> a ? pc.union(a,b) : b, null);
// drop slivers smaller than ~300 km²
const area = poly => { let a = d3.geoArea({type:'Polygon', coordinates:poly}); if(a > 2*Math.PI) a = 4*Math.PI - a; return a * 6371.0088**2; };
U = U.filter(poly => area(poly) > 300);
const total = U.reduce((s,poly)=>s+area(poly), 0);

/* ---------- the user's expanded outline (their specification, not from the sources) ---------- */
const tg = require('topojson-client');
const RV = tg.feature(g, g.objects.rivers).features;
const bbOf = f => { const cs=[]; (function w(a){ if(typeof a[0]==='number') cs.push(a); else a.forEach(w); })(f.geometry.coordinates); return {cs, x0:Math.min(...cs.map(c=>c[0])), x1:Math.max(...cs.map(c=>c[0])), y0:Math.min(...cs.map(c=>c[1])), y1:Math.max(...cs.map(c=>c[1]))}; };
const findR = (x0,x1,y0,y1,t=0.2) => RV.map(f=>({f,b:bbOf(f)})).filter(o=>Math.abs(o.b.x0-x0)<t && Math.abs(o.b.x1-x1)<t && Math.abs(o.b.y0-y0)<t && Math.abs(o.b.y1-y1)<t)[0];
const eLow = findR(41.0,47.5,30.9,34.5);
if(!eLow) throw new Error('lower Euphrates not found');
let E = (eLow.f.geometry.type==='LineString' ? [eLow.f.geometry.coordinates] : eLow.f.geometry.coordinates).flat();
E = E.filter(c=>c[0] >= 40.9);
// order upstream (north-west) to downstream (south-east)
E.sort((a,b)=>(a[0]-a[1]) - (b[0]-b[1]));
const westOfEuphrates = closed([[40.9,34.75], ...E, [47.43,31.0],[47.8,30.5],[48.55,29.95],[48.7,28.4],[38.4,28.4],[38.4,34.75]]);
const expPieces = [
  {n:'Arabian Peninsula', ids:['682','887','512','784','634','048','414']},
  {n:'Greater Syria', ids:['760','422','400','376','275']},
  {n:'Egypt, Sudan, South Sudan and the Horn', ids:['818','729','728','706','SOL','231','232','262','BRT']}
];
let X = U;
for(const p of expPieces) X = pc.union(X, geomOf(p.ids));
X = pc.union(X, pc.intersection([ring(D.SHAM_OUTER)], geomOf(['792','368'])));       // Bilād al-Shām's belt in Turkey and its desert to the Euphrates
X = pc.union(X, pc.intersection([westOfEuphrates], geomOf(['368'])));                 // Greater Israel's widest reading: Iraq west of the Euphrates
X = pc.union(X, geomOf(['368']));                                                       // all of Iraq (user's request)
X = pc.union(X, geomOf(['792']));                                                       // all of Türkiye, East Thrace and Istanbul included (user's request)
X = pc.union(X, geomOf(['196','CYN','CNM','WSB','ESB']));
/* Greater Iraq, both readings the user chose: Khuzestan (al-Ahwāz) and ʿIrāq al-ʿAjam (the Jibāl),
   the latter approximated by twelve modern Iranian provinces. Iran's outer borders come from the country shape;
   only the inner edges come from the provinces. */
let XW = X;   /* the 'to Iraq's border' version: everything up to here, nothing in Iran or the Caucasus */
const IRP = JSON.parse(fs.readFileSync('iran_admin1.geojson','utf8')).features;
const JIBAL = ['Kermanshah','Hamadan','Lorestan','Markazi','Qom','Tehran','Alborz','Qazvin','Zanjan','Esfahan','Kordestan','Ilam','Chahar Mahall and Bakhtiari'];
const KHUZ = ['Khuzestan'];
const keepNames = new Set(JIBAL.concat(KHUZ));
const pgeom = f => f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
let GI = geomOf(['364']);
for(const f of IRP.filter(f=>!keepNames.has(f.properties.name))) GI = pc.difference(GI, pgeom(f));
GI = GI.filter(poly => area(poly) > 1500);
const jibalKm = Math.round(pc.intersection(GI, ...IRP.filter(f=>JIBAL.includes(f.properties.name)).map(pgeom).reduce((a,b)=>pc.union(a,b))).reduce((t,p)=>t+area(p),0));
const khuzKm = Math.round(pc.intersection(GI, pgeom(IRP.find(f=>f.properties.name==='Khuzestan'))).reduce((t,p)=>t+area(p),0));
console.log('Greater Iraq parts', GI.length, 'Jibal km2', jibalKm, 'Khuzestan km2', khuzKm);
X = pc.union(X, GI);
X = pc.union(X, geomOf(['364','268','051','031']));                                     // all of Iran, Georgia, Armenia and Azerbaijan (user's final request)
/* Lands Egypt once held that the outline did not yet contain (Nawaz's request, 2026-10-07, from a list of lands held by Egypt
   in ancient, Ptolemaic and Muhammad ʿAlī times): Cyrenaica (eastern Libya, with the Libyan borderlands by Egypt), northern
   Uganda (Equatoria), Crete, the Aegean islands, and the Morea (the Peloponnese, with western Greece and Missolonghi).
   The rest of that list (Egypt, Sinai, Sudan with Darfur, South Sudan, the Eritrean and Somali coasts, Harar, the Levant,
   the Hejaz, Cilicia and Adana, Cyprus) was already inside. Added to both versions. */
const A1E = JSON.parse(fs.readFileSync('admin1_used.geojson','utf8')).features;
const provE = (a3, names) => names.flatMap(n=>{ const f = A1E.filter(x=>x.properties.adm0_a3===a3 && x.properties.name===n); if(!f.length) throw new Error('no province '+a3+' '+n); return f.flatMap(x=>x.geometry.type==='Polygon' ? [x.geometry.coordinates] : x.geometry.coordinates); });
const EGYPT_HELD = [
  /* later the same day Nawaz asked for all of Libya and all of Greece, not only Cyrenaica, Crete, the islands and the Morea */
  {n:'Libya, all of it', shape:()=>geomOf(['434']), within:['434']},
  {n:'northern Uganda (Equatoria)', shape:()=>provE('UGA',['Arua','Koboko','Yumbe','Moyo','Adjumani','Maracha','Zombo','Nebbi','Amuru','Nwoya','Gulu','Kitgum','Lamwo','Pader','Agago','Buliisa']), within:['800']},
  {n:'Greece, all of it', shape:()=>geomOf(['300']), within:['300']}
];
let EH = null;
for(const e of EGYPT_HELD){ let c = pc.intersection(e.shape(), geomOf(e.within)); c = c.filter(poly=>area(poly) > 30); console.log('Egypt-held', e.n, Math.round(c.reduce((t,p)=>t+area(p),0)), 'km2'); EH = EH ? pc.union(EH, c) : c; }
X = pc.union(X, EH); XW = pc.union(XW, EH);
// close any hairline gaps left between province and country edges
X = X.map(poly => [poly[0]].concat(poly.slice(1).filter(h => area([h]) > 500)));
X = X.filter(poly => area(poly) > 40);
const totalX = X.reduce((s,poly)=>s+area(poly), 0);
XW = XW.map(poly => [poly[0]].concat(poly.slice(1).filter(h => area([h]) > 500))).filter(poly => area(poly) > 40);
const totalXW = XW.reduce((s,poly)=>s+area(poly), 0);

// share of each modern state inside the outline
const states = [];
for(const f of fc.features){
  const geom = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
  const inter = pc.intersection(U, geom);
  if(!inter.length) continue;
  const ai = inter.reduce((s,poly)=>s+area(poly), 0);
  if(ai < 150) continue;
  const as = geom.reduce((s,poly)=>s+area(poly), 0);
  states.push({id:f.id, n:f.properties.n, km2:Math.round(ai), pct:Math.round(100*ai/as)});
}
states.sort((a,b)=>b.km2-a.km2);
states.forEach(s=>{ if(String(s.id)==='792') s.n = 'Türkiye'; });
// simplify for the page (Ramer–Douglas–Peucker in degrees); the outline is a thought experiment, not a survey line
function rdp(pts, eps){ if(pts.length < 4) return pts; const keep = new Uint8Array(pts.length); keep[0] = keep[pts.length-1] = 1; const st = [[0, pts.length-1]];
  while(st.length){ const [a,b] = st.pop(); let md = 0, mi = -1; const [x1,y1] = pts[a], [x2,y2] = pts[b]; const dx = x2-x1, dy = y2-y1, L = Math.hypot(dx,dy) || 1e-12;
    for(let i=a+1;i<b;i++){ const d = Math.abs(dy*pts[i][0] - dx*pts[i][1] + x2*y1 - y2*x1) / L; if(d > md){ md = d; mi = i; } }
    if(md > eps){ keep[mi] = 1; st.push([a,mi],[mi,b]); } }
  return pts.filter((_,i)=>keep[i]); }
const rdpRing = (rg, eps) => { // closed ring: split at the point farthest from the start, simplify both halves
  let k = 0, md = -1; rg.forEach((p,i)=>{ const d = Math.hypot(p[0]-rg[0][0], p[1]-rg[0][1]); if(d > md){ md = d; k = i; } });
  const a = rdp(rg.slice(0, k+1), eps), b = rdp(rg.slice(k), eps); return a.concat(b.slice(1)); };
const simp = (PP, eps) => PP.map(poly=>poly.map(rg=>rdpRing(rg, eps)).filter(rg=>rg.length >= 4)).filter(poly=>poly.length && poly[0].length >= 4);
// round coordinates for the page
const r3 = x => Math.round(x*1000)/1000;
const statesIn = PP => { const st = [];
  for(const f of fc.features){
    const geom = f.geometry.type === 'Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates;
    let inter; try { inter = pc.intersection(PP, geom); } catch(e){ inter = pc.intersection(PP, clean4(geom)); } if(!inter.length) continue;
    const ai = inter.reduce((s,poly)=>s+area(poly), 0); if(ai < 150) continue;
    const as = geom.reduce((s,poly)=>s+area(poly), 0);
    st.push({id:f.id, n:String(f.id)==='792' ? 'Türkiye' : f.properties.n, km2:Math.round(ai), pct:Math.round(100*ai/as)});
  }
  return st.sort((a,b)=>b.km2-a.km2); };
function tidyStates(PP){
  let st = statesIn(PP);
  const CY = new Set(['196','CYN','CNM','WSB','ESB']);
  const cy = st.filter(x=>CY.has(String(x.id)));
  const cyKm = Math.round(pc.intersection(PP, geomOf(['196','CYN','CNM','WSB','ESB'])).reduce((t,poly)=>t+area(poly),0));
  st = st.filter(x=>!CY.has(String(x.id)));
  if(cy.length) st.push({id:'CYP', n:'Cyprus (the whole island)', km2:cyKm, pct:100});
  st.forEach(x=>{ if(x.id==='BRT') x.n = 'Bir Tawil (unclaimed)'; if(String(x.id)==='792') x.n = 'Türkiye'; });
  return st.sort((a,b)=>b.km2-a.km2);
}
const statesX = tidyStates(X), statesXW = tidyStates(XW);
const out = {polys: simp(U, 0.004).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)]))), km2:Math.round(total), states,
  gi:{jibalKm, khuzKm}, x:{polys: simp(X, 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)]))), km2:Math.round(totalX), states:statesX},
  xw:{polys: simp(XW, 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)]))), km2:Math.round(totalXW), states:statesXW}};
/* ---------- lands once ruled by caliphates, outside the core and the Greater Middle East (user's request, 2026-10-06) ----------
   Only the parts that were ruled: whole countries where the whole was ruled, provinces (Natural Earth admin-1) or a traced
   area elsewhere. Researched from the dynasty and province histories cited in the page; edges are approximate. */
const A1 = JSON.parse(fs.readFileSync(fs.existsSync('admin1_used.geojson') ? 'admin1_used.geojson' : 'admin1.geojson','utf8')).features;
const polysOf = geom => geom.type === 'Polygon' ? [geom.coordinates] : geom.coordinates;
const prov = (a3, names) => { const out = []; for(const n of names){ const fs_ = A1.filter(f=>f.properties.adm0_a3===a3 && f.properties.name===n); if(!fs_.length) throw new Error('no province '+a3+' '+n); fs_.forEach(f=>out.push(...polysOf(f.geometry))); } return out; };
const provExcept = (a3, names) => A1.filter(f=>f.properties.adm0_a3===a3 && !names.includes(f.properties.name)).flatMap(f=>polysOf(f.geometry));
const largestOnly = PP => { let best = null, ba = -1; for(const p of PP){ const a = area(p); if(a > ba){ ba = a; best = p; } } return best ? [best] : []; };
const box = pts => [[closed(pts)]];
const HIST = [
  {id:'andalus', n:'Iberia under the caliphs', sub:'Umayyad, Córdoba, Almohad · 711–1230s', within:['724','620'], shape:()=>geomOf(['724','620'])},
  {id:'septimania', n:'Septimania (Arbūnah)', sub:'Umayyad · 719–759; the Rhône to 737', within:['FRA'], shape:()=>prov('FRA',['Pyrénées-Orientales','Aude','Hérault','Gard','Vaucluse','Bouches-du-Rhône'])},
  {id:'fraxinetum', n:'Fraxinetum', sub:'tied to Córdoba · c. 887–972', within:['FRA'], shape:()=>prov('FRA',['Var'])},
  {id:'sicily', n:'Ṣiqilliyah', sub:'Aghlabid, Fatimid, Kalbid · 827–1091', within:['380'], shape:()=>prov('ITA',['Trapani','Messina','Palermo','Agrigento','Caltanissetta','Ragusa','Siracusa','Catania','Enna']).filter(p=>{ const c = d3.geoCentroid({type:'Polygon',coordinates:p}); return !(c[1] < 35.95 && c[0] > 12.3); })},
  {id:'south_italy', n:'Bari, Taranto and Calabria', sub:'Aghlabid-era emirates · 840s–880s', within:['380'], shape:()=>prov('ITA',['Foggia','Barletta-Andria Trani','Bari','Brindisi','Lecce','Taranto','Matera','Potenza','Cosenza','Crotene','Catanzaro','Reggio Calabria','Vibo Valentia'])},
  {id:'sardinia', n:'Sardinia’s south', sub:'Mujāhid of Dénia · 1015–16', within:['380'], shape:()=>prov('ITA',['Cagliari','Medio Campidano','Carbonia-Iglesias'])},
  {id:'malta', n:'Mālṭah', sub:'Aghlabid to Kalbid · 870–1091', within:['470'], shape:()=>geomOf(['470'])},
  {id:'greece', n:'Greece and the islands', sub:'Crete emirate 827–961 · Ottoman to 1912', within:['300'], shape:()=>geomOf(['300'])},
  {id:'balkans', n:'al-Rūmīlī', sub:'Ottoman · to 1878–1912', within:['100','008','807','KOS','688','499','070'], shape:()=>geomOf(['100','008','807','KOS','688','499','070'])},
  {id:'croatia', n:'Slavonia, Lika and Dalmatia', sub:'Ottoman to 1699 · Dubrovnik tributary to 1808', within:['191'], shape:()=>{
     const inland = prov('HRV',['Osjecko-Baranjska','Vukovarsko-Srijemska','Brodsko-Posavska','Viroviticko-Podravska','Bjelovarsko-bilogorska','Licko-Senjska']);
     const coast = ['Šibensko-Kninska','Splitsko-Dalmatinska','Zadarska','Dubrovacko-Neretvanska'].flatMap(n=>largestOnly(prov('HRV',[n])));
     return inland.concat(coast); }},
  {id:'hungary', n:'Budin', sub:'Ottoman Hungary · 1541–1699', within:['348'], shape:()=>provExcept('HUN',['Gyor-Moson-Sopron','Sopron','Gyôr','Vas','Szombathely'])},
  {id:'slovakia', n:'Uyvar and Upper Hungary', sub:'Ottoman and vassal · 1663–85', within:['703'], shape:()=>prov('SVK',['Nitriansky','Banskobystrický','Košický','Prešov'])},
  {id:'romania', n:'Eflak, Boğdan, Erdel', sub:'Ottoman vassals and provinces · to 1878', within:['642','498'], shape:()=>geomOf(['642','498'])},
  {id:'ukraine', n:'Crimea, Yedisan and Podolia', sub:'Crimean Khanate and Ottoman · 1475–1792', within:['804','643'], shape:()=>prov('UKR',['Odessa','Mykolayiv','Kherson','Zaporizhzhya','Kirovohrad','Vinnytsya',"Khmel'nyts'kyy",'Chernivtsi',"Ternopil'",'Cherkasy']).concat(prov('RUS',['Crimea','Sevastopol']))},
  {id:'kuban', n:'Kuban, Taman and Azov', sub:'Ottoman and Crimean · to 1774–83', within:['643'], shape:()=>prov('RUS',['Krasnodar']).concat(box([[39.0,46.9],[39.75,46.9],[39.75,47.35],[39.0,47.35]]))},
  {id:'derbent', n:'Bāb al-Abwāb (Derbent)', sub:'Umayyad, Abbasid · Ottoman 1578–c. 1607', within:['643'], shape:()=>box([[48.2,41.2],[48.75,41.85],[48.35,42.6],[47.9,43.0],[47.2,42.6],[47.4,41.9],[47.9,41.5]])},
  {id:'sokoto', n:'Sokoto Caliphate', sub:'1804–1903', within:['566','562','854','120','148','140'], shape:()=>prov('NGA',['Sokoto','Kebbi','Zamfara','Katsina','Kano','Jigawa','Kaduna','Bauchi','Gombe','Adamawa','Taraba','Niger','Kwara','Nassarawa','Yobe'])
      .concat(box([[0.95,13.0],[1.4,12.65],[2.2,12.3],[3.1,12.0],[3.65,12.5],[3.6,13.3],[2.9,13.6],[2.0,13.55],[1.3,13.4]]))
      .concat(prov('BFA',['Séno','Yagha']))
      .concat(prov('CMR',['Adamaoua','Nord','Extrême-Nord']))
      .concat(prov('TCD',['Mayo-Kebbi Ouest']))
      .concat(box([[14.3,7.45],[14.9,7.25],[15.3,6.75],[15.4,6.15],[15.05,5.7],[14.5,5.55],[14.3,5.6]]))},
  {id:'tibesti', n:'Tibesti and Borkou', sub:'Ottoman garrisons · 1908–13', within:['148'], shape:()=>prov('TCD',['Tibesti','Borkou'])},
  {id:'equatoria', n:'Equatoria', sub:'Egypt under the Ottomans · 1870s–1889', within:['800'], shape:()=>prov('UGA',['Arua','Koboko','Yumbe','Moyo','Adjumani','Maracha','Zombo','Nebbi','Amuru','Nwoya','Gulu','Kitgum','Lamwo','Pader','Agago','Buliisa'])},
  {id:'hind', n:'Delhi Sultanate', sub:'invested by the Abbasid caliph 1229 · height c. 1335', within:['356'], shape:()=>prov('IND',['Punjab','Haryana','Delhi','Chandigarh','Uttar Pradesh','Bihar','West Bengal','Rajasthan','Gujarat','Madhya Pradesh','Maharashtra','Telangana','Andhra Pradesh','Karnataka','Tamil Nadu','Dadra and Nagar Haveli and Daman and Diu'])},
  {id:'bengal', n:'Bangālah', sub:'Delhi Sultanate · from 1227', within:['050'], shape:()=>pc.difference(prov('BGD',['Chittagong','Sylhet','Dhaka','Rangpur','Rajshahi','Khulna','Barisal']), [[closed([[91.85,20.5],[93,20.5],[93,23.3],[91.85,23.3]])]])},
  {id:'kashgar', n:'Kāshghar', sub:'Karakhanids c. 1000 · Ottoman vassal 1873–77', within:['156'], shape:()=>box([[73.5,39.0],[74.5,37.0],[78.5,35.5],[84,36.2],[88.5,37.5],[90.5,39.5],[90,42.6],[88,43.6],[84,42.5],[80.5,42.2],[76,41],[73.5,40.0]])}
];
/* round to 1e-4° and drop repeated points, so the clipping library does not trip over near-coincident edges */
const r4 = x => Math.round(x*1e4)/1e4;
const clean4 = PP => PP.map(poly=>poly.map(rg=>{ const o = []; for(const [x,y] of rg){ const q = [r4(x), r4(y)]; const l = o[o.length-1]; if(!l || l[0]!==q[0] || l[1]!==q[1]) o.push(q); } if(o.length && (o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1])) o.push(o[0]); return o; }).filter(rg=>rg.length >= 4)).filter(poly=>poly.length);
const histParts = {};
for(const h of HIST){
  let cut = pc.intersection(h.shape(), geomOf(h.within));
  if(!cut.length) throw new Error('empty historical piece '+h.id);
  cut = clean4(simp(clean4(cut), 0.003)).filter(p=>area(p) > 20).map(poly=>[poly[0]].concat(poly.slice(1).filter(h=>area([h]) > 50)));
  histParts[h.id] = cut;
  let big = cut[0]; cut.forEach(p=>{ if(area(p) > area(big)) big = p; });
  const c = d3.polygonCentroid(big[0]);
  h.km2 = Math.round(cut.reduce((t,p)=>t+area(p),0)); h.c = [r3(c[0]), r3(c[1])];
  console.log('hist', h.id.padEnd(12), String(h.km2).padStart(9), 'km²', h.c.join(','));
}
const HU = clean4(Object.values(histParts).reduce((a,b)=> a ? clean4(pc.union(a,b)) : b, null));
/* ---------- lands joined to the rest at the user's request (2026-10-06): NOT ruled by a counted caliphate ----------
   The ruled parts of the western Mediterranean left Corsica, the north of Sardinia, central and northern Italy and the
   Alpes-Maritimes lying between them. These are added so that Iberia, Provence, Italy, Sicily, Sardinia and Corsica form one
   connected territory. They are kept apart from the ruled parts in the tables and labelled as the user's addition. */
/* Second round (2026-10-06, after three screenshots of the Black Sea, the Caspian and the Adriatic): the ruled lands of the
   Balkans and the Black Sea did not touch Italy, nor the Kuban and Azov, nor each other across the north of the Caspian.
   Added, whole: Slovenia, the rest of Croatia, Hungary and Ukraine, and Russia's Southern and North Caucasian federal
   districts (Adygea, Astrakhan, Volgograd, Kalmykia, Rostov, Dagestan, Ingushetia, Kabardino-Balkaria, Karachay-Cherkessia,
   North Ossetia, Stavropol, Chechnya; Krasnodar and Crimea are already in). `state` names the state whose ruled part is split off. */
const RUS_SOUTH = ["Adygey","Astrakhan'","Volgograd","Kalmyk","Rostov","Dagestan","Ingush","Kabardin-Balkar","Karachay-Cherkess","North Ossetia","Stavropol'","Chechnya"];
const JOIN = [
  {id:'join_italy', n:'Italy, joined', sub:'the rest of it · added to join the lands, not ruled', within:['380','674'], state:'380', row:'Italy: the rest of it, north and centre and Sardinia’s north', shape:()=>geomOf(['380','674'])},
  /* round 3 (2026-10-07, Nawaz's request): all of metropolitan France, not only Corsica and the Alpes-Maritimes; Andorra too,
     which would otherwise be a hole between France and Spain */
  {id:'join_france', n:'France, joined', sub:'beyond Septimania and Fraxinetum · added, not ruled', within:['FRA'], state:'FRA', row:'France: the rest of it, beyond Septimania and Fraxinetum, with Corsica', shape:()=>geomOf(['FRA'])},
  {id:'join_andorra', n:'Andorra', sub:'added, not ruled', within:['020'], whole:'020', shape:()=>geomOf(['020'])},
  /* round 4 (2026-10-07, Nawaz's request): Austria, whole. The Ottomans besieged Vienna (1529, 1683) and raided Styria and
     Carinthia, but never ruled Austria, so it is joined, not ruled. */
  {id:'join_austria', n:'Austria, joined', sub:'besieged and raided, never ruled · added', within:['040'], whole:'040', shape:()=>geomOf(['040'])},
  {id:'join_slovenia', n:'Slovenia, joined', sub:'joins Italy to the Balkans · added, not ruled', within:['705'], whole:'705', shape:()=>geomOf(['705'])},
  {id:'join_croatia', n:'Croatia, the rest', sub:'Istria, Zagreb and the north-west · added, not ruled', within:['191'], state:'191', row:'Croatia: the rest of it, Istria, Zagreb and the north-west', shape:()=>geomOf(['191'])},
  {id:'join_hungary', n:'Hungary, the far west', sub:'added to join the lands, not ruled', within:['348'], state:'348', row:'Hungary: the far west', shape:()=>geomOf(['348'])},
  {id:'join_ukraine', n:'Ukraine, the rest', sub:'north, east and west · added to join the lands, not ruled', within:['804'], state:'804', row:'Ukraine: the rest of it, north, east and west', shape:()=>geomOf(['804'])},
  {id:'join_russia', n:'Southern Russia, joined', sub:'Southern and North Caucasus districts · added, not ruled', within:['643'], state:'643', row:'Russia: the rest of the Southern and North Caucasus districts', shape:()=>prov('RUS',RUS_SOUTH.concat(['Krasnodar']))}
];
const joinParts = {};
for(const j of JOIN){
  let cut = pc.intersection(j.shape(), geomOf(j.within));
  if(!cut.length) throw new Error('empty joined piece '+j.id);
  cut = clean4(simp(clean4(cut), 0.003)).filter(p=>area(p) > 20).map(poly=>[poly[0]].concat(poly.slice(1).filter(h=>area([h]) > 50)));
  joinParts[j.id] = cut;
  /* label at the middle of the land that is only joined, not of the whole country */
  let rest = cut; try { const d = clean4(pc.difference(cut, HU)).filter(p=>area(p) > 20); if(d.length) rest = d; } catch(e){}
  let big = rest[0]; rest.forEach(p=>{ if(area(p) > area(big)) big = p; });
  const c = d3.polygonCentroid(big[0]); j.c = [r3(c[0]), r3(c[1])];
}
/* Monaco sits on the coast between the Alpes-Maritimes and Liguria: take it whole so the line does not break there */
joinParts.monaco = clean4(geomOf(['492']));
const JU = clean4(Object.values(joinParts).reduce((a,b)=> a ? clean4(pc.union(a,b)) : b, null));
const HUALL = clean4(pc.union(HU, JU));
/* ---------- Greater Middle East: the core outline, unchanged, plus the surrounding region (user's request) ----------
   The ring is built on the core exactly as drawn, so wherever the core is the outer edge the two lines coincide. */
const GME_IDS = {
  maghrib: ['434','788','012','504','732','478'],          // Libya, Tunisia, Algeria, Morocco, Western Sahara, Mauritania
  centralasia: ['398','KAB','860','795','417','762'],      // Kazakhstan (with Baikonur), Uzbekistan, Turkmenistan, Kyrgyzstan, Tajikistan
  khurasan: ['004','586']                                   // Afghanistan, Pakistan
};
/* Muslim-majority countries of Africa that the core and the Maghrib do not already hold (user's request, 2026-10-06).
   Criterion: Muslims are more than half of the population in the Pew Research Center's 2020 estimates (published June 2025,
   appendix B, "Religious composition table"). Eritrea (51.7%) is already in the core. Not counted: Côte d'Ivoire (46.3%) and
   Tanzania (29.9%), below half; Mayotte (a French department) and Zanzibar (part of Tanzania), which are not countries.
   Nigeria and Guinea-Bissau are marked: their national counts or other surveys put the Muslim share at or below half. */
const AFR = [
  {id:'466', pew:94.1}, {id:'562', pew:98.1}, {id:'854', pew:67.4}, {id:'148', pew:56.4}, {id:'566', pew:56.1, flag:'sources differ'},
  {id:'686', pew:97.6}, {id:'270', pew:97.0}, {id:'624', pew:56.0, flag:'sources differ'}, {id:'324', pew:86.8}, {id:'694', pew:80.1},
  {id:'174', pew:98.3}
];
const AFR_IDS = AFR.map(a=>a.id);
const allGME = [].concat(GME_IDS.maghrib, GME_IDS.centralasia, GME_IDS.khurasan);
const allG = allGME.concat(AFR_IDS);
const coreDrawn = out.x.polys;
let addDrawn = simp(geomOf(allG).map(p=>[p[0]]), 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)])));
const histDrawn = simp(HU, 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)])));
const joinDrawn = simp(JU, 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)])));
let GD = pc.union(pc.union(pc.union(coreDrawn, addDrawn), histDrawn), joinDrawn);
GD = GD.map(poly => [poly[0]].concat(poly.slice(1).filter(h => area([h]) > 2500))).filter(poly => area(poly) > 40);
// areas from the full-detail shapes
const GA = clean4(pc.union(clean4(pc.union(X, geomOf(allG))), HUALL));
const totalG = GA.reduce((t,poly)=>t+area(poly), 0);
let statesG = tidyStates(GA);
{ const kab = statesG.find(x=>x.id==='KAB'), kaz = statesG.find(x=>String(x.id)==='398');
  if(kab && kaz){ kaz.km2 += kab.km2; statesG = statesG.filter(x=>x !== kab); }
  statesG.forEach(x=>{ if(x.id==='732' || x.n==='W. Sahara') x.n = 'Western Sahara'; });
  statesG.sort((a,b)=>b.km2-a.km2); }
const coreIds = new Set(statesX.map(x=>String(x.id)));
const gmeIds = new Set(allGME.map(String).concat(['KAB']));
const afrIds = new Set(AFR_IDS);
/* a state only partly in the core (Libya, Greece) gets two rows: its core part (dup, counted once) and the rest */
const coreKm = Object.fromEntries(statesX.map(s=>[String(s.id), s.km2]));
const CORE_PART_N = {'434':'Libya: Cyrenaica (in the complete version)', '300':'Greece: Crete, the Aegean islands and the Morea (in the complete version)', '800':'Uganda: the north (in the complete version)'};
function splitCore(list){
  const extra = [];
  list.forEach(x=>{ const ck = coreKm[String(x.id)]; x.core = ck != null && x.km2 - ck < 1000;
    if(ck != null && !x.core){ const whole = x.pct, all = x.km2; x.km2 = all - ck; x.pct = Math.max(1, Math.round(whole * x.km2 / all));
      extra.push({id:String(x.id)+'_C', n:CORE_PART_N[String(x.id)] || (x.n+' (in the complete version)'), km2:ck, pct:Math.max(1, Math.round(whole * ck / all)), core:true, dup:true}); } });
  return list.concat(extra);
}
statesG = splitCore(statesG);
statesG.forEach(x=>{ if(x.dup) return; x.afr = !x.core && afrIds.has(String(x.id)); x.hist = !x.core && !x.afr && !gmeIds.has(String(x.id)); });
/* shares: the base map is cut to the sheet, so measure each state's share against its full Natural Earth area */
{ const NE = JSON.parse(fs.readFileSync('ne_10m_admin_0_countries.geojson','utf8')).features;
  const full = new Map(); for(const f of NE){ const a3 = f.properties.ADM0_A3, n3 = f.properties.ISO_N3; const id = n3 && n3 !== '-99' ? n3 : a3; const PP = f.geometry.type==='Polygon' ? [f.geometry.coordinates] : f.geometry.coordinates; full.set(String(id), PP.reduce((t,p)=>t+area(p),0)); }
  statesG.forEach(x=>{ const fa = full.get(String(x.id)); if(fa) x.pct = Math.max(1, Math.min(100, Math.round(100*x.km2/fa))); }); }
/* the African additions are whole countries: say so, and carry the Pew figure and any flag */
statesG.forEach(x=>{ if(x.afr){ const a = AFR.find(a=>a.id===String(x.id)); x.pct = 100; x.pew = a.pew; if(a.flag) x.flag = a.flag; } });
/* Crimea: in Natural Earth's de facto map it lies inside Russia; list it on its own row */
{ const cr = pc.intersection(GA, prov('RUS',['Crimea','Sevastopol'])); const crKm = Math.round(cr.reduce((t,p)=>t+area(p),0));
  const ru = statesG.find(x=>String(x.id)==='643');
  if(ru && crKm){ ru.km2 -= crKm; ru.pct = Math.max(1, Math.round(ru.pct * ru.km2 / (ru.km2 + crKm))); ru.n = 'Russia (Kuban, Azov, Derbent)'; statesG.push({id:'CRI', n:'Crimea (annexed by Russia in 2014; recognised internationally as Ukraine)', km2:crKm, pct:100, core:false, hist:true}); }
  statesG.sort((a,b)=>b.km2-a.km2); }
/* Italy and France are each part ruled, part joined at the user's request: show the two parts as separate rows (the second marked dup, so a state is counted once) */
for(const j of JOIN){
  if(j.whole){ /* a whole state added for the join (Slovenia): its own row, counted as a state */
    const row = statesG.find(x=>String(x.id)===j.whole); if(!row) throw new Error('no state '+j.whole);
    row.hist = false; row.join = true; j.km2 = row.km2; console.log('joined whole', j.whole, row.km2); continue; }
  const id = j.state, row = statesG.find(x=>String(x.id)===id); if(!row) throw new Error('no state '+id);
  let ruled = pc.intersection(HU, geomOf([id]));
  if(id === '643') ruled = pc.difference(clean4(ruled), prov('RUS',['Crimea','Sevastopol'])); /* Crimea has its own row */
  const rk = Math.round(ruled.reduce((t,p)=>t+area(p),0)), jk = row.km2 - rk, whole = row.pct;
  row.km2 = rk; row.pct = Math.max(1, Math.round(whole * rk / (rk + jk)));
  statesG.push({id:id+'_J', n:j.row, km2:jk, pct:Math.max(1, Math.round(whole * jk / (rk + jk))), core:false, afr:false, hist:false, join:true, dup:true});
  j.km2 = jk;
  console.log('joined', id, 'ruled', rk, 'joined', jk);
}
statesG.sort((a,b)=>b.km2-a.km2);
/* regional index: classical name, the modern states in it, and whether it lies in the core or the ring */
const REG = [
  {id:'maghrib', n:'al-Maghrib', ar:'المغرب', en:'North Africa (Libya is now in the core)', ring:true, b:[[-17.5,14.5],[12.0,38.0]], ids:['504','732','012','788','478']},
  {id:'nile', n:'Wādī al-Nīl · al-Nūbah', ar:'وادي النيل', en:'Egypt and the Sudans', b:[[23.5,3.0],[38.6,32.0]], ids:['818','729','728','BRT']},
  {id:'horn', n:'al-Ḥabashah · Bilād al-Barbar', ar:'الحبشة', en:'the Horn of Africa', b:[[32.8,-2.0],[51.6,18.2]], ids:['232','262','231','706','SOL']},
  {id:'arabia', n:'Jazīrat al-ʿArab', ar:'جزيرة العرب', en:'the Arabian Peninsula', b:[[34.4,12.0],[60.0,32.4]], ids:['682','887','512','784','634','048','414']},
  {id:'sham', n:'Bilād al-Shām', ar:'بلاد الشام', en:'the Levant', b:[[33.8,29.2],[42.6,37.4]], ids:['760','422','400','376','275']},
  {id:'iraq', n:'al-ʿIrāq', ar:'العراق', en:'Iraq', b:[[38.6,29.0],[48.8,37.5]], ids:['368']},
  {id:'iran', n:'Bilād Fāris · al-Jibāl', ar:'بلاد فارس', en:'Iran', b:[[43.8,24.8],[63.5,40.0]], ids:['364']},
  {id:'rum', n:'Bilād al-Rūm', ar:'بلاد الروم', en:'Anatolia and Cyprus', b:[[25.6,34.4],[45.0,42.3]], ids:['792','CYP']},
  {id:'misrheld', n:'Barqah · Ṭarābulus · al-Yūnān', ar:'برقة وطرابلس واليونان', en:'all of Libya and Greece, with northern Uganda (Equatoria) · added at your request', b:[[9.0,0.0],[33.5,42.0]], ids:['434','300','800']},
  {id:'qabq', n:'al-Qabq · Arrān · Armīniyah', ar:'القبق', en:'the South Caucasus', b:[[39.6,38.2],[51.2,43.9]], ids:['268','051','031']},
  {id:'centralasia', n:'Mā warāʾ al-Nahr · Khwārazm', ar:'ما وراء النهر', en:'Central Asia', ring:true, b:[[46.0,35.0],[88.0,55.6]], ids:['398','860','795','417','762']},
  {id:'khurasan', n:'Khurāsān · al-Sind', ar:'خراسان والسند', en:'Afghanistan and Pakistan', ring:true, b:[[60.3,23.5],[77.9,38.6]], ids:['004','586']},
  /* Muslim-majority countries of Africa (whole countries) */
  {id:'sudan', n:'Bilād al-Sūdān', ar:'بلاد السودان', en:'the Sahel and Nigeria', afr:true, b:[[-12.5,4.0],[24.0,25.0]], ids:['466','562','854','148','566']},
  {id:'takrur', n:'Bilād al-Takrūr', ar:'بلاد التكرور', en:'Senegambia and the Guinea coast', afr:true, b:[[-17.7,6.8],[-7.5,16.8]], ids:['686','270','624','324','694']},
  {id:'qamar', n:'Juzur al-Qamar', ar:'جزر القمر', en:'the Comoros', afr:true, b:[[43.0,-12.7],[44.7,-11.2]], ids:['174']},
  /* lands once ruled by caliphates (only the parts that were ruled) */
  {id:'andalus', n:'al-Andalus', ar:'الأندلس', en:'Spain, Portugal and Gibraltar', hist:true, b:[[-10.0,35.5],[4.6,44.0]], ids:['724','620']},
  {id:'ifranj', n:'Arbūnah · Fraxinetum', ar:'أربونة', en:'southern France', hist:true, b:[[1.5,42.2],[7.2,44.6]], ids:['FRA']},
  {id:'siqilliyah', n:'Ṣiqilliyah · Qalawriyah · Mālṭah', ar:'صقلية', en:'Sicily, southern Italy, Sardinia and Malta', hist:true, b:[[8.0,35.6],[18.7,42.0]], ids:['380','470']},
  {id:'rumeli', n:'al-Rūmīlī', ar:'الروملي', en:'the Balkans (Greece is now in the core)', hist:true, b:[[13.4,39.6],[29.8,46.3]], ids:['100','008','807','KOS','688','499','070','191']},
  {id:'danube', n:'Budin · Eflak · Boğdan', ar:'المجر والأفلاق والبغدان', en:'Hungary, Slovakia, Romania and Moldova', hist:true, b:[[16.0,43.5],[30.4,49.7]], ids:['348','703','642','498']},
  {id:'qirim', n:'al-Qirim · Azāq · Bāb al-Abwāb', ar:'القرم', en:'southern Ukraine, Crimea, the Kuban and Derbent', hist:true, b:[[26.0,41.2],[49.0,50.0]], ids:['804','CRI','643']},
  {id:'sokoto', n:'Ṣakkwatu · Tibesti', ar:'صكتو', en:'Sokoto’s outer lands, in Cameroon and the Central African Republic. Its heartland and Tibesti lie in countries counted whole above', hist:true, b:[[11.0,5.0],[16.0,13.8]], ids:['120','140']},
  {id:'hind', n:'al-Hind · Bangālah', ar:'الهند والبنغال', en:'India and Bangladesh', hist:true, b:[[67.5,7.5],[92.0,32.5]], ids:['356','050']},
  {id:'kashghar', n:'Kāshghar', ar:'كاشغر', en:'Kashgaria, in Xinjiang', hist:true, b:[[73.0,35.0],[91.0,44.0]], ids:['156']},
  /* joined at the user's request: not ruled */
  {id:'join', n:'Italy, France and Andorra', ar:'', en:'joined to the ruled lands around them, at your request; no counted caliphate ruled them (Septimania, Fraxinetum and the south of Italy were ruled, and are counted above)', join:true, b:[[-5.2,36.6],[18.6,51.2]], ids:['380_J','FRA_J','020']},
  {id:'join_adriatic', n:'Austria and Slovenia, and the rest of Croatia and Hungary', ar:'', en:'join Italy to the Balkans and Hungary, at your request; no counted caliphate ruled these parts (the Ottomans besieged Vienna in 1529 and 1683 and raided Austria, but never ruled it)', join:true, b:[[9.3,44.2],[18.4,49.1]], ids:['040','705','191_J','348_J']},
  {id:'join_pontic', n:'Ukraine and the south of Russia', ar:'', en:'joins the Black Sea lands to the Caucasus and the Caspian, at your request; no counted caliphate ruled these parts', join:true, b:[[22.0,41.0],[49.8,52.6]], ids:['804_J','643_J']}
];
const byIdG = new Map(statesG.map(x=>[String(x.id), x]));
REG.forEach(r=>{ r.states = r.ids.map(id=>byIdG.get(id)).filter(Boolean).map(x=>({n:x.n, km2:x.km2, pct:x.pct, ...(x.flag ? {flag:x.flag} : {})})); r.km2 = r.states.reduce((t,x)=>t+x.km2,0); });
out.g = {polys: GD, km2:Math.round(totalG), states:statesG, regions:REG, hist:HIST.map(h=>({id:h.id, n:h.n, sub:h.sub, km2:h.km2, c:h.c})).concat(JOIN.map(j=>({id:j.id, n:j.n, sub:j.sub, km2:j.km2, c:j.c, join:true}))), afr:AFR.map(a=>({id:a.id, n:(byIdG.get(a.id)||{}).n, pew:a.pew, flag:a.flag||null}))};
console.log('--- Greater Middle East: polygons', GD.length, 'km2', Math.round(totalG), 'states', statesG.length, '| added:', statesG.filter(x=>!x.core).map(x=>x.n).join(', '));
REG.forEach(r=>console.log('  ', r.id.padEnd(12), r.states.length, 'states', r.km2));
/* ---------- Complete Caliphate V2 (Nawaz's request, 2026-10-07) ----------
   The complete core plus every land on the Greater Middle East reference map (reference/Greater_Middle_East_orthographic.svg):
   the Maghrib, Central Asia, Afghanistan and Pakistan. Each of those lands carries its history province by province, from
   v2_history.json (made by tools/make_v2_history.py): cat = direct | dynasty | tributary | islamic | temporary | influence. */
const V2H = JSON.parse(fs.readFileSync('v2_history.json','utf8'));
const V2_CLIP = {MAR:['504'], SAH:['732'], DZA:['012'], TUN:['788'], LBY:['434'], MRT:['478'], KAZ:['398','KAB'], UZB:['860'], TKM:['795'], KGZ:['417'], TJK:['762'], AFG:['004'], PAK:['586']};
const V2_ID = {MAR:'504', SAH:'732', DZA:'012', TUN:'788', LBY:'434', MRT:'478', KAZ:'398', UZB:'860', TKM:'795', KGZ:'417', TJK:'762', AFG:'004', PAK:'586'};
const V2A = clean4(pc.union(X, geomOf(allGME)));
let V2D = pc.union(coreDrawn, simp(geomOf(allGME).map(p=>[p[0]]), 0.012).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)]))));
V2D = V2D.map(poly => [poly[0]].concat(poly.slice(1).filter(h => area([h]) > 2500))).filter(poly => area(poly) > 40);
let statesV2 = tidyStates(V2A);
{ const kab = statesV2.find(x=>x.id==='KAB'), kaz = statesV2.find(x=>String(x.id)==='398');
  if(kab && kaz){ kaz.km2 += kab.km2; statesV2 = statesV2.filter(x=>x !== kab); }
  statesV2.forEach(x=>{ if(x.id==='732' || x.n==='W. Sahara') x.n = 'Western Sahara'; }); statesV2 = splitCore(statesV2); }
const v2units = [], v2share = {};
for(const c of V2H){
  const clip = geomOf(V2_CLIP[c.a3]); const sh = v2share[V2_ID[c.a3]] = {direct:0, dynasty:0, tributary:0, islamic:0, temporary:0, influence:0};
  for(const u of c.units){
    let cut = [];
    try { cut = pc.intersection(clean4(prov(c.a3, u.provinces)), clip); } catch(e){ cut = pc.intersection(clean4(simp(prov(c.a3, u.provinces), 0.002)), clip); }
    cut = clean4(cut).filter(p=>area(p) > 30);
    const km2 = Math.round(cut.reduce((t,p)=>t+area(p),0)); sh[u.cat] += km2;
    let big = cut[0]; cut.forEach(p=>{ if(area(p) > area(big)) big = p; });
    const cc = big ? d3.polygonCentroid(big[0]) : null;
    v2units.push({a3:c.a3, country:c.country, label:u.label, cat:u.cat, conf:u.conf, km2, c: cc ? [r3(cc[0]), r3(cc[1])] : null,
      polys: simp(cut, 0.015).map(poly=>poly.map(rg=>rg.map(([x,y])=>[r3(x),r3(y)]))),
      who:u.who, dates:u.dates, nominal:u.nominal, states:u.states, notes:u.notes, uncertain:u.uncertain, adj:u.adj, sources:u.sources});
  }
}
statesV2.forEach(x=>{ const sh = v2share[String(x.id)]; if(!sh) return; const t = Object.values(sh).reduce((a,b)=>a+b,0) || 1;
  x.hs = Object.fromEntries(Object.entries(sh).filter(([,v])=>v > 0).map(([k,v])=>[k, Math.round(100*v/t)])); });
statesV2.sort((a,b)=>b.km2-a.km2);
out.v2 = {polys: V2D, km2: Math.round(V2A.reduce((t,p)=>t+area(p),0)), states: statesV2, units: v2units,
  countries: V2H.map(c=>({a3:c.a3, n:c.country, summary:c.summary}))};
console.log('--- V2: km2', out.v2.km2, 'states', statesV2.length, 'units', v2units.length, 'drawn units', v2units.filter(u=>u.polys.length).length);
statesV2.filter(x=>x.hs).forEach(x=>console.log('  ', x.n.padEnd(16), JSON.stringify(x.hs)));
fs.writeFileSync('src/caliph.json', JSON.stringify(out));
console.log('polygons', U.length, 'rings', U.map(p=>p.length).join(','), 'points', U.reduce((s,p)=>s+p.reduce((t,r)=>t+r.length,0),0));
console.log('total km2', out.km2);
states.forEach(s=>console.log(s.n.padEnd(24), String(s.km2).padStart(8), 'km²', String(s.pct).padStart(4)+'% of the state'));
console.log('--- expanded: polygons', X.length, 'km2', out.x.km2);
statesX.forEach(s=>console.log(s.n.padEnd(24), String(s.km2).padStart(8), 'km²', String(s.pct).padStart(4)+'%'));

console.log('--- to Iraq\'s border: km2', out.xw.km2, 'states', statesXW.length, statesXW.map(x=>x.n).join(', '));
