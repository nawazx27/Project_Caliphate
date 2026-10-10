/* Version 54 (2026-10-10, Nawaz's request: "add krygyzstan to it aswell"): Kyrgyzstan, whole, joins the Complete outline. Not the version to
   Iraq's border (east of Iraq). V2, Maximum and Greater hold it whole already: there it now counts as core, and in Greater it joins the
   Mā warāʾ al-Nahr core card. Run once: node tools/add_core_kyrgyzstan.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreKyrgyzstan){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const KGZ = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '417')).geometry));
const km2 = area(KGZ);

/* union, then fill the new hairline gaps along the old edge; holes that were there before stay */
const V = C.x, before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = pc.union(R3mp(V.polys), KGZ).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
let filled = 0, fk = 0;
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
  const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
  if(!old && a < 5000){ filled++; fk += a; return false; } return true; })]);
const gain = area(X) - before; V.polys = X; V.km2 += gain;
V.states.push({id:'417', n:'Kyrgyzstan', km2, pct:100}); V.states.sort((a, b) => b.km2 - a.km2);
console.log('Complete + ' + gain + ' km² -> ' + V.km2 + ' | ' + V.states.length + ' states | gaps filled ' + filled + ' (' + Math.round(fk) + ' km²)');

for(const k of ['v2', 'm', 'g']) C[k].states.forEach(s => { if(String(s.id) === '417'){ s.core = true; if(k === 'm') delete s.add; if(k === 'g'){ s.afr = false; s.hist = false; } } });
const R = C.g.regions, byId = new Map(C.g.states.filter(s => !s.dup).map(s => [String(s.id), s]));
const card = (r, fields) => { Object.assign(r, fields); r.states = r.ids.map(id => byId.get(id)).filter(Boolean).map(x => ({n:x.n, km2:x.km2, pct:x.pct, ...(x.flag ? {flag:x.flag} : {})})); r.km2 = r.states.reduce((t, s) => t + s.km2, 0); };
card(R.find(r => r.id === 'centralasia'), {ids:['398'], en:'Kazakhstan (Turkmenistan, Uzbekistan, Tajikistan and Kyrgyzstan are now in the core)'});
card(R.find(r => r.id === 'transox'), {ids:['860','762','417'], n:'Mā warāʾ al-Nahr · Farghāna', ar:'ما وراء النهر وفرغانة', en:'all of Uzbekistan, Tajikistan and Kyrgyzstan · added at your request', b:[[55.8,36.5],[80.5,45.8]]});
C.coreKyrgyzstan = 'Version 54: Kyrgyzstan in the complete version';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Kyrgyzstan', km2, 'km²');
