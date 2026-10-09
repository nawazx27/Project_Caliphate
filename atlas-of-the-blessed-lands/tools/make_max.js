/* Version 45 (2026-10-08, Nawaz's specification): "Maximum" — the Complete outline plus the lands on Nawaz's list.
   Whole countries come from the base map (geo2.json). Part-countries (northern Nigeria, coastal Kenya and Tanzania,
   northern coastal Mozambique, southern and western Kazakhstan, the Caspian-basin provinces of Russia) are made of whole
   provinces from Natural Earth admin-1 (ne_10m_admin_1_states_provinces.geojson, downloaded from the natural-earth-vector
   GitHub repository), widened by 4 km and cut to the base-map country, so the outer edges are the base map's own.
   Run: A1=<path to admin-1 geojson> TB=<folder holding @turf/buffer> node tools/make_max.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const buffer = require(path.join(process.env.TB, '@turf/buffer')).default || require(path.join(process.env.TB, '@turf/buffer'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(process.env.A1));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));

const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const KM = 6371.0088**2;
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const G = geo.objects.countries.geometries;
const mpOf = id => asMp(topojson.feature(geo, G.find(g => String(g.id) === id)).geometry);
const nameOf = id => G.find(g => String(g.id) === id).properties.n;

/* simple Douglas–Peucker, to keep the province edges light */
function rdp(pts, eps){ if(pts.length < 3) return pts; let dmax = 0, idx = 0; const [a, b] = [pts[0], pts[pts.length-1]];
  for(let i = 1; i < pts.length-1; i++){ const p = pts[i], dx = b[0]-a[0], dy = b[1]-a[1], L = dx*dx+dy*dy;
    let t = L ? ((p[0]-a[0])*dx + (p[1]-a[1])*dy)/L : 0; t = Math.max(0, Math.min(1, t));
    const d = Math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy); if(d > dmax){ dmax = d; idx = i; } }
  if(dmax > eps){ const l = rdp(pts.slice(0, idx+1), eps), r = rdp(pts.slice(idx), eps); return l.slice(0,-1).concat(r); }
  return [a, b]; }
const simp = mp => mp.map(p => p.map(r => { const s = rdp(r, 0.01); return s.length >= 4 ? s : r; }));

/* ---- Nawaz's list ---- */
const WHOLE = {
  '788':'Tunisia', '012':'Algeria', '504':'Morocco', '732':'Western Sahara', '478':'Mauritania',     /* 1 Greater Maghreb (Western Sahara joins Morocco to Mauritania along the coast) */
  '148':'Chad', '562':'Niger', '466':'Mali', '686':'Senegal', '270':'Gambia',                          /* 2 Sahel (the Gambia lies inside Senegal) */
  '800':'Uganda', '646':'Rwanda', '108':'Burundi',                                                      /* 3 Nile sources */
  '795':'Turkmenistan', '860':'Uzbekistan', '762':'Tajikistan', '417':'Kyrgyzstan', 'KAB':'Baikonur',  /* 4 Central Asia (Baikonur: leased to Russia, inside Kazakhstan's Qyzylorda) */
  '004':'Afghanistan', '586':'Pakistan',                                                               /* 5 Indus (Pakistan as the base map draws it, with Azad Kashmir and Gilgit-Baltistan; Siachen left out) */
  '470':'Malta', '462':'Maldives', '174':'Comoros'};                                                    /* 6 islands (Crete and Socotra are already inside) */
const PART = {
  '566': {a3:'NGA', why:'Northern Nigeria: the twelve northern states (the heart of the Sokoto Caliphate and Bornu)',
          take:['Sokoto','Kebbi','Zamfara','Katsina','Kano','Jigawa','Yobe','Borno','Bauchi','Gombe','Kaduna','Niger']},
  '404': {a3:'KEN', why:'Coastal Kenya: the old Coast Province', take:['Coast']},
  '834': {a3:'TZA', why:'Coastal Tanzania with Zanzibar and Pemba',
          take:['Tanga','Pwani','Dar-Es-Salaam','Lindi','Mtwara','Kaskazini-Pemba','Kusini-Pemba','Kaskazini-Unguja','Zanzibar South and Central','Zanzibar West']},
  '508': {a3:'MOZ', why:'Coastal Mozambique from the Ruvuma down to the Zambezi', take:['Cabo Delgado','Nampula','Zambezia']},
  '398': {a3:'KAZ', why:'Kazakhstan: the south (to the Tian Shan) and the west (the Caspian basin)',
          take:['Mangghystau','Qyzylorda','South Kazakhstan','Zhambyl','Almaty','Almaty City','Atyrau','West Kazakhstan','Aqtöbe']},
  '643': {a3:'RUS', why:'Russia: the provinces lying wholly or largely in the Caspian drainage basin (Volga, Ural, Terek, Kuma)',
          take:["Tver'",'Moskovskaya','Moskva',"Yaroslavl'",'Kostroma','Ivanovo','Vladimir',"Ryazan'",'Kaluga','Tula','Orel','Tambov',
                'Nizhegorod','Kirov','Mariy-El','Chuvash','Tatarstan','Udmurt',"Perm'",'Bashkortostan','Mordovia','Penza',"Ul'yanovsk",
                'Samara','Saratov','Volgograd',"Astrakhan'",'Kalmyk','Orenburg',"Stavropol'",'Dagestan','Chechnya','Ingush','North Ossetia','Kabardin-Balkar']}};

let pieces = [R3mp(C.x.polys)];
for(const id in WHOLE) pieces.push(R3mp(mpOf(id)));
const partGeo = {};
for(const id in PART){
  const P = PART[id], feats = A1.features.filter(f => f.properties.adm0_a3 === P.a3 && P.take.includes(f.properties.name));
  const got = new Set(feats.map(f => f.properties.name)), miss = P.take.filter(n => !got.has(n));
  if(miss.length) throw new Error(P.a3 + ' missing provinces: ' + miss.join(', '));
  const u = pc.union(...feats.map(f => simp(asMp(f.geometry))));
  const b = buffer({type:'Feature', properties:{}, geometry:{type:'MultiPolygon', coordinates:u}}, 4, {units:'kilometers', steps:4}).geometry;
  const cut = pc.intersection(R3mp(mpOf(id)), R3mp(asMp(b)));
  partGeo[id] = cut; pieces.push(cut);
  console.log(P.a3, 'part', area(cut), 'km² of', area(mpOf(id)));
}
const vic = geo.objects.lakes.geometries.find(g => g.properties.n === 'Lake Victoria');
pieces.push(R3mp(asMp(topojson.feature(geo, vic).geometry)));   /* the whole of Lake Victoria */

let M = pc.union(...pieces).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
let filled = 0; M = M.map(p => [p[0], ...p.slice(1).filter(r => { if(ringSr(r)*KM < 5000){ filled++; return false; } return true; })]);
const km2 = area(M);
console.log('holes filled', filled, '| kept holes', M.reduce((t,p)=>t+p.length-1,0), '| total', km2);

/* states: share of each base-map country inside */
const [[x0,y0],[x1,y1]] = d3.geoBounds({type:'MultiPolygon', coordinates:M});
const states = [];
for(const g of G){ const f = topojson.feature(geo, g); const [[a0,b0],[a1,b1]] = d3.geoBounds(f);
  if(a1 < x0 || a0 > x1 || b1 < y0 || b0 > y1) continue;
  const mp = R3mp(asMp(f.geometry)), full = area(mp); if(!full) continue;
  let ins = 0; try { ins = area(pc.intersection(mp, M)); } catch(e){   /* polygon-clipping can fail on a shared edge: go piece by piece, nudging a piece that still fails */
    for(const poly of mp){ try { ins += area(pc.intersection([poly], M)); } catch(e2){ ins += area(pc.intersection([poly.map(r => r.map(q => [q[0]+1e-6, q[1]+1e-6]))], M)); } } }
  if(ins < 50) continue;
  const id = String(g.id), pct = Math.min(100, Math.max(0.1, Math.round(ins/full*1000)/10));
  states.push({id, n:g.properties.n, km2:ins, pct, core:!!C.x.states.find(s => s.id === id || s.n === g.properties.n),
    add: WHOLE[id] ? 'whole' : PART[id] ? PART[id].why : undefined});
}
states.sort((a,b) => b.km2 - a.km2);
C.m = {polys:M, km2, states, made:'Version 45: Complete + Nawaz’s list (maximum stable expansion)'};
fs.writeFileSync(F, JSON.stringify(C));
console.log(states.length, 'states;', states.slice(0,60).map(s => s.n + ' ' + s.pct).join(', '));
