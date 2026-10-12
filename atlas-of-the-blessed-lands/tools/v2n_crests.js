/* Version 95 (2026-10-12, Nawaz: "go for the all three things", the third being real height data so the natural frontiers
   follow the mountain crests exactly). Adds to V2N (CALIPH.xn) the land on the inner side of the crests that it did not yet
   hold, as found by tools/v2n_crest_pieces.py (tools/data/v2n_crest_pieces.geojson): a few slivers of the Fergana valley's
   rim (Kyrgyzstan and China) and the Syr Darya side of the Karatau (Qyzylorda and Zhambyl regions of Kazakhstan). Land is only
   added; what V2N holds beyond the crests is kept (my synthesis; Nawaz's rule "leave no area out"). V2 (CALIPH.x) is unchanged.
   Run: python3 tools/v2n_crest_pieces.py && node tools/v2n_crests.js */
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
const P = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/v2n_crest_pieces.geojson'))).features;
const before = C.xn.km2;
let X = R3mp(C.xn.polys);
for (const f of P) X = R3mp(pc.union(X, R3mp(asMp(f.geometry))));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.xn.polys = X; C.xn.km2 = area(X);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
const upd = (id, c, n) => { const i = kmIn(c), a = area(c), s = C.xn.states.find(s => s.id === id); s.km2 = i; s.pct = Math.round(1000*i/a)/10; if (n) s.n = n; };
upd('398_K', country('398'), 'Kazakhstan: the Turkistan region, to the Karatau range (with its whole Syr Darya side, to the crest) and the Moyynkum and Kyzylkum sands, with the Khurāsān maps’ edge');
upd('417_K', country('417'));
upd('156_K', country('156'));
C.xn.states.sort((a, b) => b.km2 - a.km2);
C.xn.crests = 'Version 95: the Syr Darya side of the Karatau and the Fergana valley to its crests, traced on elevation data (Mapzen terrain tiles)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2N', before, '->', C.xn.km2, '(+', C.xn.km2 - before, ')', P.map(f => f.properties.where + ' ' + f.properties.km2).join('; '));
console.log(C.xn.states.filter(s => /^(156|398|417)/.test(s.id)).map(s => s.id + ' ' + s.km2 + ' ' + s.pct).join(' | '), '| V3', C.xw.km2);
