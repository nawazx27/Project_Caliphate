/* Version 80 (2026-10-11, Nawaz: "Don't leave anything out even if it's in china").
   Until now V2 (the Complete outline, CALIPH.x) took the traced Transoxiana outlines only inside Kazakhstan, Kyrgyzstan, Tajikistan and
   Uzbekistan, and left out the lower Syr Darya towns Jand and Yanghikant. This adds:
   - the parts of the traced outlines that fall in China: the green region of the locator map (tools/data/transoxiana_locator_trace.json,
     Version 78) and the solid Mawarāʾ al-Nahr line of reference/mawarannahr_khwarazm_khorasan.jpg (tools/data/mawarannahr_trace2.json);
     the other traces have nothing outside V2 on land;
   - the lower Syr Darya from Sauran to the Aral shore, with Jand (ruins in the Zhalagash district, south of Akkyr; place estimated at
     45.0 N 64.6 E) and Yanghikant (Jankent ruins, 45.612 N 61.922 E, 25 km south-west of Kazaly): a band of 40 km either side of the
     river through Zhanakorgan, Shieli, Kyzylorda, Zhalagash and Kazaly, in Kazakhstan (my construction), with the strip of Kyzylkum
     desert between that band and the lands already inside, so no inlet is left.
   Run: node tools/v2_include_everything.js */
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
const KAZ = country('398'), CHN = country('156');
/* 1. the traced outlines, in China */
const TR = [D('transoxiana_locator_trace').transoxiana_locator, D('mawarannahr_trace2').mawarannahr_img2];
const CHINA = R3mp(pc.intersection(R3mp(pc.union(...TR.map(t => R3mp([[t]])))), CHN));
/* 2. the lower Syr Darya, Sauran to the Aral shore: hulls of 40 km discs round each pair of neighbouring points */
const disc = (c, km) => d3.geoCircle().center(c).radius(km/111.32).precision(5)().coordinates[0];
const RIVER = [[67.769, 43.515], [67.25, 43.90], [66.75, 44.17], [65.51, 44.85], [64.68, 45.08], [64.6, 45.0], [63.30, 45.45],
  [62.11, 45.76], [61.922, 45.612], [61.10, 46.05]];
const seg = (a, b) => { const h = d3.polygonHull([...disc(a, 40), ...disc(b, 40)]); h.push(h[0]); return R3mp([[h.reverse()]]); };
const BAND = R3mp(pc.intersection(R3mp(pc.union(...RIVER.slice(1).map((b, i) => seg(RIVER[i], b)))), KAZ));
/* and the strip of Kyzylkum desert left between that band and the Khwārazm and Isbījāb lands already inside, so no inlet is left */
const SOUTH = [...RIVER, [60.0, 45.6], [60.0, 43.0], [67.769, 43.0], RIVER[0]];
const INLET = R3mp(pc.difference(R3mp(pc.intersection(R3mp([[SOUTH]]), KAZ)), R3mp(C.x.polys)));
const before = C.x.km2, kzBefore = area(R3mp(pc.intersection(R3mp(C.x.polys), KAZ)));
let X = R3mp(pc.union(R3mp(C.x.polys), CHINA, BAND, INLET));
X = X.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]).filter(p => ringSr(p[0])*KM >= 1);
C.x.polys = X; C.x.km2 = area(X);
const kz = area(R3mp(pc.intersection(X, KAZ))), cn = area(R3mp(pc.intersection(X, CHN)));
Object.assign(C.x.states.find(s => s.id === '398_T'), {n:'Kazakhstan: Mawarāʾ al-Nahr as drawn on the author’s maps, with the Isbījāb district (Isbījāb, Ṭarāz, and the Syr Darya ribāṭ towns Fārāb/Otrār, Yasī and Ṣabrān), the lower Syr Darya with Jand and Yanghikant, and the land round Lake Balkhash', km2:kz, pct:Math.round(1000*kz/area(KAZ))/10});
C.x.states = C.x.states.filter(s => s.id !== '156_T');
if (cn) C.x.states.push({id:'156_T', n:'China: the edge of Mawarāʾ al-Nahr as drawn on the author’s maps (the Xinjiang border strip)', km2:cn, pct:Math.round(10000*cn/area(CHN))/100});
C.x.states.sort((a, b) => b.km2 - a.km2);
C.x.everything = 'Version 80: the traced outlines in China, and the lower Syr Darya with Jand and Yanghikant (Nawaz)';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2', before, '->', C.x.km2, '(+', C.x.km2 - before, ') | Kazakhstan', kzBefore, '->', kz, '| China', cn, '| China traced', area(CHINA), '| band', area(BAND), '| inlet', area(INLET));
