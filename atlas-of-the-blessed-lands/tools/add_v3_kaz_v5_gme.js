/* Version 73 (2026-10-11, Nawaz: "Add the southern Kazakhstan strip to V3 and include these lands in image in v5", with the
   Greater Middle East globe map, the same lands as the reference map behind V6).
   V3 (CALIPH.x): the South Kazakhstan (Turkistan) and Zhambyl regions (Natural Earth admin-1), cut to the base map's Kazakhstan:
   the old northern edge of Transoxiana (Isbījāb/Sayram, Otrār, Ṭarāz, Shymkent).
   V5 (CALIPH.x3): every land the map shades that V5 lacked: Western Sahara (the part Morocco holds and the rest), Mauritania and
   Kazakhstan, whole. V6 and V7 already held them; their rows now count them as part of V5 (core).
   Run once: node tools/add_v3_kaz_v5_gme.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.x3.gme){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); if(!g) throw new Error('no country ' + id); return R3mp(asMp(topojson.feature(geo, g).geometry)); };
const addTo = (V, shapes) => { const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = R3mp(pc.union(R3mp(V.polys), ...shapes));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]).filter(p => ringSr(p[0])*KM >= 1);
  const gain = area(X) - before; V.polys = X; V.km2 += gain; return gain; };
/* V3: the southern strip */
const KAZ = country('398'), kazKm = area(KAZ);
const prov = n => { const f = A1.find(f => f.properties.adm0_a3 === 'KAZ' && f.properties.name === n); if(!f) throw new Error('no province ' + n); return R3mp(asMp(f.geometry)); };
const STRIP = R3mp(pc.intersection(R3mp(pc.union(prov('South Kazakhstan'), prov('Zhambyl'))), KAZ)).filter(p => ringSr(p[0])*KM >= 50);
const stripKm = area(STRIP);
const g3 = addTo(C.x, [STRIP]);
C.x.states.push({id:'398_S', n:'Kazakhstan: the South Kazakhstan (Turkistan) and Zhambyl regions', km2:stripKm, pct:Math.round(1000*stripKm/kazKm)/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.kazStrip = 'Version 73: the South Kazakhstan (Turkistan) and Zhambyl regions in V3 (Nawaz)';
/* V5: Western Sahara (both parts), Mauritania, Kazakhstan */
const g5 = addTo(C.x3, ['504', '732', '478', '398', 'KAB'].map(country));   /* KAB: Baikonur, drawn apart on the base map (leased to Russia); without it V5 had a hole */
const fromV6 = id => { const s = C.v2.states.find(s => s.id === id); if(!s) throw new Error('no V6 row ' + id); const {core, hs, ...r} = s; return r; };
['504_W', '732', '478', '398'].forEach(id => C.x3.states.push(id === '732' ? {...fromV6(id), n:'Western Sahara, the rest'} : fromV6(id)));
C.x3.states.push({id:'KAB', n:'Baikonur (Kazakh land leased to Russia)', km2:area(country('KAB')), pct:100});
C.x3.states.sort((a, b) => b.km2 - a.km2);
C.x3.gme = 'Version 73: Western Sahara (both parts), Mauritania and Kazakhstan, whole, in V5: every land of the Greater Middle East map (Nawaz)';
/* V6 and V7 held these already: they now count as part of V5 */
const MOVED = ['504_W', '732', '478', '398'];
C.v2.states.forEach(s => { if(MOVED.includes(s.id)) s.core = true; });
C.g.states.forEach(s => { if(MOVED.includes(s.id)) s.core = true; });
for(const r of C.g.regions){ if(r.id === 'maghrib'){ delete r.ring; r.en = 'Western Sahara and Mauritania'; } if(r.id === 'centralasia'){ delete r.ring; r.en = 'Kazakhstan'; } }
fs.writeFileSync(F, JSON.stringify(C));
console.log('V3 +', g3, '->', C.x.km2, '| strip', stripKm, 'of Kazakhstan', kazKm, '| V5 +', g5, '->', C.x3.km2, '| V4', C.me2.km2, 'V6', C.v2.km2);
