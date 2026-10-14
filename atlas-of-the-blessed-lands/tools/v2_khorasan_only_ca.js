/* Version 132 (2026-10-14, Nawaz: "Ykw remove everything except greater khorasan"; asked, he chose the widest Greater Khurāsān (his three
   maps together, as in Version 87) and to keep Turkmenistan, Afghanistan and Pakistan whole). In V2 and V2-B, all land in Kazakhstan
   (with Baikonur), Uzbekistan, Kyrgyzstan, Tajikistan and China is replaced by the widest Greater Khurāsān alone: the union of
   tools/data/transoxiana_trace.json 'khorasan', greater_khorasan_wiki_trace.json and khorasan_express_trace.json, with every province of
   those four Central Asian countries that the union covers to 99% or more taken whole (Version 87's rule; Tajikistan is thus whole).
   Transoxiana, Khwārazm and everything else beyond Khurāsān there go out (Versions 74–131's additions). Rows recounted here.
   Run: node tools/v2_khorasan_only_ca.js   (or "rows" to only recount after town passes and gap filling) */
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
const IDS = [['860', 'Uzbekistan'], ['762', 'Tajikistan'], ['417', 'Kyrgyzstan'], ['398', 'Kazakhstan'], ['156', 'China'], ['KAB', 'Baikonur']];
const CA = R3mp(pc.union(...IDS.map(([id]) => country(id))));
const KEEP = R3mp(pc.intersection(R3mp(pc.union(KHMAX, ...whole)), CA));   // land only
console.log('widest Khurasan', area(KHMAX), 'whole provinces', whole.length, 'kept in the five countries', area(KEEP));
for (const k of ['x', 'xb']) {
  const V = C[k], before = V.km2;
  let X = R3mp(V.polys);
  if (process.argv[2] !== 'rows') {
    X = R3mp(pc.union(R3mp(pc.difference(X, CA)), KEEP));
    X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
    V.polys = X; V.km2 = area(X);
  }
  V.states = V.states.filter(s => !/^(860|762|417|398|156|KAB)(_|$)/.test(String(s.id)));
  for (const [id, nm] of IDS) {
    if (id === 'KAB') continue;
    const c = country(id), a = area(c), i = area(R3mp(pc.intersection(X, c)));
    if (i < 1) continue;
    const pct = Math.round(1000*i/a)/10;
    V.states.push(pct >= 99.5 ? {id, n: nm, km2: a, pct: 100} : {id: id + '_K', n: nm + ': the part of Greater Khurāsān as the author’s maps draw it (the widest of them)', km2: i, pct});
  }
  V.states.sort((a, b) => b.km2 - a.km2);
  console.log(k, before, '->', V.km2, '(', V.km2 - before, ')', V.states.filter(s => /^(860|762|417|398|156)/.test(s.id)).map(s => s.id + ' ' + s.km2 + ' ' + s.pct + '%').join(', '));
}
fs.writeFileSync(F, JSON.stringify(C));
