/* Version 78 (2026-10-11, Nawaz: "Include this region as well", with a locator map captioned "Location of Transoxiana (An Honorable
   Retelling)", kept as reference/transoxiana_locator_retelling.jpg). The green region was traced (tools/data/transoxiana_locator_trace.json):
   the map was registered by the Aral Sea (historic shoreline), Kara-Bogaz-Gol, Lake Balkhash and Lake Baikal and refined on their shores
   (quadratic fit, median error ~1.3 px; the map is small and simplified, so its own lines are good to some tens of km).
   V2 (the Complete outline, CALIPH.x) takes in the part of it in Central Asia (Kazakhstan, Kyrgyzstan, Tajikistan, Uzbekistan); slivers it
   puts in China or Russia are fitting error and are left out. Run: node tools/v2_transoxiana_locator.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const T = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/transoxiana_locator_trace.json'))).transoxiana_locator;
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const KAZ = country('398'), CA = R3mp(pc.union(KAZ, country('417'), country('762'), country('860')));
const REG = R3mp([[T]]);
const spill = { China: area(R3mp(pc.intersection(REG, country('156')))), Russia: area(R3mp(pc.intersection(REG, country('643')))) };
const ADD = R3mp(pc.intersection(REG, CA));
const before = C.x.km2;
let X = R3mp(pc.union(R3mp(C.x.polys), ADD));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
C.x.polys = X; C.x.km2 = area(X);
const kz = area(R3mp(pc.intersection(X, KAZ)));
const r = C.x.states.find(s => s.id === '398_T');
Object.assign(r, {n:'Kazakhstan: Mawarāʾ al-Nahr as drawn on the author’s maps, with Isbījāb, Ṭarāz and the land round Lake Balkhash (the locator map)', km2:kz, pct:Math.round(1000*kz/area(KAZ))/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.locator = 'Version 78: the green Transoxiana of the author’s locator map (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '| Kazakhstan part', kz, '| spill left out', JSON.stringify(spill), '| V3', C.xw.km2, 'V4', C.me2.km2, 'V5', C.x3.km2, '| holes', X.reduce((t, p) => t + p.length - 1, 0));
