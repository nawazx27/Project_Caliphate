/* Version 126 (2026-10-14, Nawaz, circling the Taman peninsula, Anapa and the lower Kuban on a screenshot: "It should cover this land
   and add entire modern Uzbekistan"). In V2 and V2-B: tools/data/taman_districts.geojson (tools/taman_districts.py: five whole districts)
   is added, and Uzbekistan whole (geo2) replaces row 860_K with 860. Row 643_N is recounted (tools/v2_caucasus_districts.js rows).
   Run: node tools/v2_taman_uzbekistan.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const TAMAN = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/taman_districts.geojson'))).features[0];
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const UZB = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '860')).geometry));
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys), fail = 0;
  for (const poly of [...R3mp(asMp(TAMAN.geometry)), ...UZB]) { try { X = R3mp(pc.union(X, [poly])); } catch (e) { fail++; } }
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => !['860_K', '860'].includes(s.id));
  V.states.push({id: '860', n: 'Uzbekistan', km2: area(UZB), pct: 100});
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(+', V.km2 - before, ') failed', fail);
}
fs.writeFileSync(F, JSON.stringify(C));
