/* Version 133 (2026-10-14, Nawaz: "Maintain political border with India"). India's land (geo2 id 356: the Punjab and Himachal strip to
   the Beas and Sutlej, with Pathankot and Kathua, added in Versions 92–116) is taken out of V2 and V2-B, so the outline follows the
   India–Pakistan border (as geo2 draws it, with Azad Kashmir and Gilgit-Baltistan on Pakistan's side). Row 356_P removed.
   Run: node tools/v2_india_border.js */
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
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates.filter(Array.isArray);
const IND = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '356')).geometry));
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(pc.difference(R3mp(V.polys), IND));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
  V.polys = X; V.km2 = area(X);
  V.states = V.states.filter(s => !/^356/.test(String(s.id)));
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ')');
}
fs.writeFileSync(F, JSON.stringify(C));
