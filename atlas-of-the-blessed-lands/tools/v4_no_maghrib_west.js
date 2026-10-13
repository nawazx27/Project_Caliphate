/* Version 112 (2026-10-13, Nawaz: "Remove Western Sahara, Morocco and Algeria from v4").
   Takes Morocco (504, which in the base map includes the part of Western Sahara Morocco holds), the rest of Western Sahara (732) and
   Algeria (012) out of V4 (CALIPH.me2). V4 is then V1 with Tunisia, Afghanistan and Pakistan. Run: node tools/v4_no_maghrib_west.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const V = C.me2, before = V.km2;
let X = R3mp(V.polys), fail = 0;
for (const id of ['504', '732', '012']) for (const poly of country(id)) { try { X = R3mp(pc.difference(X, [poly])); } catch (e) { fail++; } }
X = X.filter(p => ringSr(p[0]) * KM >= 1);   // hairline remnants along the cut borders
V.polys = X; V.km2 = area(X);
V.states = V.states.filter(s => !['504', '504_W', '732', '012'].includes(s.id));
let left = 0; for (const id of ['504', '732', '012']) { try { left += area(R3mp(pc.intersection(country(id), X))); } catch (e) { left = -1; } }
let keep = 0; for (const id of ['788', '434', '729']) { try { keep += area(R3mp(pc.difference(country(id), X))); } catch (e) { keep = -1; } }
console.log('V4', before, '->', V.km2, '(', V.km2 - before, ') failed', fail, '| left of the three', left, 'km2 | Tunisia/Libya/Sudan missing', keep, 'km2 |', V.states.length, 'rows');
fs.writeFileSync(F, JSON.stringify(C));
