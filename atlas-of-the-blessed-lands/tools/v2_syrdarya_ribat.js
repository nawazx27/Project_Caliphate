/* Version 79 (2026-10-11, Nawaz: "find out how big was transoxiana Mawarāʾ al-Nahr and include these as well").
   Sources (read through search summaries; see notes.md): Bosworth, "Mā warāʾ al-nahr", Encyclopaedia Iranica (Sogdia, Čaḡāniyān, Ḵottal,
   Waḵān, Ošrusana, Čāč/Šāš, Farḡāna; northern frontier ill-defined); Le Strange, Lands of the Eastern Caliphate, ch. XXXIV (the Isbījāb
   district: Sayrām, Fārāb/Utrār, Yasī, Ṣabrān, Ṭarāz, Mirkī; Jand and Yanghikant as Oghuz dependencies); Ibn Ḥawqal (Khwārazm counted in).
   V2 already held everything Muslim-held except the middle Syr Darya ribāṭ towns of the Isbījāb district: Fārāb (Otrār), Yasī (Turkistan),
   Ṣabrān (Sauran) and Shāwghar (near Turkistan, not located). Added as the hull of 40 km round Otrār, Turkistan, Sauran and Isbījāb, in
   Kazakhstan (my construction). Jand and Yanghikant (Oghuz, not Muslim-ruled) and Barskhān and Nawākath beyond Muslim rule are not added
   for that reason (Barskhān and Nawākath lie in Kyrgyzstan, which is whole in V2 anyway). Run: node tools/v2_syrdarya_ribat.js */
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
const KAZ = country('398');
const disc = (c, km) => d3.geoCircle().center(c).radius(km/111.32).precision(5)().coordinates[0];
const pts = [[68.303, 42.852], [68.25, 43.30], [67.769, 43.515], [69.77, 42.30]].flatMap(c => disc(c, 40));
const hull = d3.polygonHull(pts); hull.push(hull[0]);
const ADD = R3mp(pc.intersection(R3mp([[hull.reverse()]]), KAZ));
const before = C.x.km2;
let X = R3mp(pc.union(R3mp(C.x.polys), ADD));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
C.x.polys = X; C.x.km2 = area(X);
const kz = area(R3mp(pc.intersection(X, KAZ)));
Object.assign(C.x.states.find(s => s.id === '398_T'), {n:'Kazakhstan: Mawarāʾ al-Nahr as drawn on the author’s maps, with the Isbījāb district (Isbījāb, Ṭarāz, and the Syr Darya ribāṭ towns Fārāb/Otrār, Yasī and Ṣabrān) and the land round Lake Balkhash', km2:kz, pct:Math.round(1000*kz/area(KAZ))/10});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.syrdarya = 'Version 79: the middle Syr Darya ribāṭ towns of the Isbījāb district (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '(+', C.x.km2 - before, ') | Kazakhstan', kz);
