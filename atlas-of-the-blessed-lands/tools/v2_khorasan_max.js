/* Version 87 (2026-10-11, Nawaz: "Include this land (maximum khorasan)!!!", with three maps:
   1. reference/transoxiana_khwarazm_khorasan.webp (its dashed Khorasan, traced in Version 74: tools/data/transoxiana_trace.json 'khorasan');
   2. reference/greater_khorasan_map.png, the "Greater Khorasan" map drawn on today's provinces (traced here: tools/data/greater_khorasan_wiki_trace.json;
      the map is a plain longitude/latitude grid, fitted to 24 labelled cities, error about 2 km);
   3. reference/khorasan_express_map.webp, a small blurry map (traced here: tools/data/khorasan_express_trace.json; fitted to 13 cities, error
      10–30 km, so its edges are rough).
   V2 (CALIPH.x) takes the union of all three, nothing cut, wherever it falls (Uzbekistan, Tajikistan, Kyrgyzstan, Kazakhstan, China, the Caspian).
   Where the union covers a province of Uzbekistan, Tajikistan, Kyrgyzstan or Kazakhstan to 99% or more (map 2 follows province lines), the
   whole province is taken, so no hairline is left at its edge; Tajikistan is thus whole. Run: node tools/v2_khorasan_max.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const D = n => JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data', n + '.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const MAPS = [[[D('transoxiana_trace').khorasan]], ...D('greater_khorasan_wiki_trace').map(r => [[r]]), ...D('khorasan_express_trace').map(r => [[r]])].map(R3mp);
const KHMAX = R3mp(pc.union(...MAPS));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features.filter(f => ['UZB', 'TJK', 'KGZ', 'KAZ'].includes(f.properties.adm0_a3));
const whole = [];
for (const f of A1) { const g = R3mp(asMp(f.geometry)), a = area(g), i = area(R3mp(pc.intersection(g, KHMAX))); if (a && i/a >= 0.99) whole.push(g); }
const ADD = R3mp(pc.union(KHMAX, ...whole));
const before = C.x.km2;
let X = R3mp(pc.union(R3mp(C.x.polys), ADD));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
C.x.polys = X; C.x.km2 = area(X);
const kmIn = mp => area(R3mp(pc.intersection(X, mp)));
const rows = [['860', 'Uzbekistan'], ['762', 'Tajikistan'], ['417', 'Kyrgyzstan'], ['398', 'Kazakhstan'], ['156', 'China']].map(([id, nm]) => { const c = country(id), a = area(c), i = kmIn(c); return {id, nm, a, i}; });
C.x.states = C.x.states.filter(s => !['762_K', '860_K', '860', '762', '417', '398_T', '156_T', '417_K', '398_K', '156_K'].includes(s.id));
for (const r of rows) {
  if (r.i < 1) continue;
  const pct = Math.round(1000*r.i/r.a)/10;
  if (pct >= 99.5) C.x.states.push({id:r.id, n:r.nm, km2:r.a, pct:100});
  else C.x.states.push({id:r.id + '_K', n:r.nm + ': the part of Greater Khurāsān as the author’s maps draw it (the widest of them)', km2:r.i, pct});
}
C.x.states.sort((a, b) => b.km2 - a.km2);
delete C.x.khorasanStrict;
C.x.khorasanMax = 'Version 87: the widest Greater Khurāsān of the author’s three maps (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('maximum Khurasan (three maps)', area(KHMAX), '| whole provinces', whole.length, '| added area', area(ADD), '| V2', before, '->', C.x.km2,
  '|', rows.map(r => r.nm + ' ' + r.i + '/' + r.a).join(', '), '| V3', C.xw.km2);
