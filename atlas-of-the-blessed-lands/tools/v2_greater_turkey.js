/* Version 97 (2026-10-12, Nawaz: "Greater turkey should look like this", three maps and the Misak-ı Millî; he chose "Balkans out,
   maps' part only"). V2 (CALIPH.x) and V2N (CALIPH.xn) go back to their Version 95 land (the Ottoman Balkans of Version 96 taken out)
   and gain only the part of Bulgaria, and a sliver of North Macedonia, that his maps colour red (tools/data/greater_turkey.geojson,
   made by tools/greater_turkey.py). Greater Turkey itself, the union of what his maps colour, is stored as CALIPH.gtr (clipped to V2's
   land) and drawn on V2 and V2N as a named outline; all of it already lies inside V2 apart from that Bulgarian part.
   Run: node tools/v2_greater_turkey.js base.json   (base.json: the Version 95 data, e.g.
   git show 9c00a88:atlas-of-the-blessed-lands/src/caliph.json > base.json) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F)), BASE = JSON.parse(fs.readFileSync(process.argv[2]));
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const country = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const GT = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/data/greater_turkey.geojson'))).features;
const OUTLINE = R3mp(asMp(GT.find(f => f.properties.part === 'outline').geometry));
const ADD = R3mp(asMp(GT.find(f => f.properties.part === 'v2_add').geometry));
const BGR = country('100'), MKD = country('807');
for (const k of ['x', 'xn']) {
  const V = C[k], before = V.km2;
  if (BASE[k].ottomanBalkans) throw new Error('base.json must be the Version 95 data');
  let X = R3mp(pc.union(R3mp(BASE[k].polys), ADD));
  X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
  /* every land the version lists whole is put back where the coast or a border had come out a little short (about 100 km² of
     Cyprus's coast and a few km² of Türkiye were missing since before Version 81); country by country, piece by piece, since one big
     union makes polygon-clipping fail */
  const G = {}; geo.objects.countries.geometries.forEach(g => { G[String(g.id)] = g; });
  let fixed = 0, failed = [];
  for (const s of BASE[k].states.filter(s => G[s.id] && s.pct >= 99.5)) {
    for (const poly of country(s.id)) {
      let miss; try { miss = R3mp(pc.difference([poly], X)); } catch (e) { failed.push(s.id); continue; }
      const a = area(miss); if (a < 0.5) continue;
      try { X = R3mp(pc.union(X, miss)); fixed += a; } catch (e) { failed.push(s.id); }
    }
  }
  console.log(k, 'whole lands put back', fixed, 'km²', failed.length ? 'could not check: ' + [...new Set(failed)].join(',') : '');
  V.polys = X; V.km2 = area(X); delete V.ottomanBalkans;
  V.states = BASE[k].states.filter(s => !['100_G', '807_G'].includes(s.id));
  const bg = area(R3mp(pc.intersection(X, BGR))), mk = area(R3mp(pc.intersection(X, MKD)));
  V.states.push({id:'100_G', n:'Bulgaria: the south and east, as the author’s Greater Turkey maps colour it (Burgas, Varna, Shumen, Targovishte, Sliven, Yambol, Stara Zagora, Haskovo, Kardzhali, Smolyan, Plovdiv, Pazardzhik and Blagoevgrad provinces, and the traced edge)', km2:bg, pct:Math.round(1000*bg/area(BGR))/10});
  V.states.push({id:'807_G', n:'North Macedonia: a sliver by Dojran and Bogdanci, where the traced silk map runs over the border (doubtful)', km2:mk, pct:Math.round(1000*mk/area(MKD))/10});
  V.states.sort((a, b) => b.km2 - a.km2);
  V.greaterTurkey = 'Version 97: Greater Turkey as the author’s maps draw it; only its Bulgarian part (and a North Macedonian sliver) was added';
  console.log(k, 'Version 96', before, '-> Version 97', V.km2, '| Bulgaria', bg, '| N. Macedonia', mk);
}
let G = R3mp(pc.intersection(OUTLINE, R3mp(C.x.polys)));
C.gtr = {polys:G, km2:area(G), n:'Greater Turkey (Misak-ı Millî), as the author’s maps draw it'};
let out = 0; try { out = area(R3mp(pc.difference(OUTLINE, R3mp(C.x.polys)))); } catch (e) { out = -1; }
console.log('Greater Turkey on land in V2', C.gtr.km2, '| its traced outline outside V2 (sea and the silk’s ragged edge)', out, '| V3', C.xw.km2);
fs.writeFileSync(F, JSON.stringify(C));
