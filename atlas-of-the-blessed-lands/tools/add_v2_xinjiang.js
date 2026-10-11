/* Version 62 (2026-10-11, Nawaz's request with two orthographic maps: "Add these lands (the light and dark shaded regions) to the V2
   Caliphate"). Map 1 is a locator map of Yettishar, Yaqub Beg's state (dark: the Tarim basin; hatched: the rest of western and northern
   Xinjiang); map 2 is the Ili Kazakh Autonomous Prefecture. Both lie wholly in China (Xinjiang). The maps were lined up with the base map
   (orthographic, centre 92.56°E 50.53°N, fitted to the land pattern, 96% agreement) and traced: tools/data/xinjiang_trace.json.
   The white country borders on the maps are taken in and the shapes clipped to China, so the outer edge is the real border; the inner
   edges (towards Tibet, Qinghai and Gansu, and between the three provinces) are the maps' own, traced approximately.
   Version 63 (2026-10-11): Nawaz sent a third map, of East Turkestan, and chose to redraw V2's Xinjiang to it. Its inset was matched to the
   base map's borders (linear fit, mean error about 8 km; tools/data/xinjiang_trace.json, et) and is now the outer shape; the two earlier
   maps only divide it into the three provinces. The map's East Turkestan reaches about 99°E, beyond Xinjiang's official eastern end
   (about 96.4°E), so it takes in a strip of western Gansu.
   Three V2 provinces, each with its history; China joins the V2 table as East Turkestan. Run once: node tools/add_v2_xinjiang.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const T = JSON.parse(fs.readFileSync(path.join(__dirname, 'data/xinjiang_trace.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.v2.xinjiang){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const CN = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '156')).geometry));
/* drop holes under 5,000 km² (hairline gaps between the traced shapes and the border) */
const fillSmall = mp => mp.map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 5000)]);
const clipCN = mp => fillSmall(R3mp(pc.intersection(R3mp(mp), CN)));
/* The maps' borders sit a few pixels off the base map's, so a strip up to ~35 km wide along China's international border was left out.
   snap() adds, on a 0.05° grid, every cell of China within 0.6° of the traced shape that is also within 0.6° of another country:
   the shape then reaches the real border, while its inner edges (towards Tibet, Qinghai and Gansu) stay where the map draws them. */
const G = 0.05, GX0 = 72, GY1 = 50.5, GW = 510, GH = 350, NEAR = 12;
const inside = (mp, pt) => mp.some(p => d3.polygonContains(p[0], pt) && !p.slice(1).some(h => d3.polygonContains(h, pt)));
const cellPt = (i, j) => [GX0 + (i + 0.5)*G, GY1 - (j + 0.5)*G];
const inCN = new Uint8Array(GW*GH); for(let j = 0; j < GH; j++) for(let i = 0; i < GW; i++) inCN[j*GW + i] = inside(CN, cellPt(i, j)) ? 1 : 0;
const near = src => { const d = new Int16Array(GW*GH).fill(999), q = []; src.forEach((v, k) => { if(v){ d[k] = 0; q.push(k); } });
  for(let h = 0; h < q.length; h++){ const k = q[h], i = k % GW, j = (k / GW) | 0; if(d[k] >= NEAR) continue;
    for(let dj = -1; dj <= 1; dj++) for(let di = -1; di <= 1; di++){ const ii = i + di, jj = j + dj; if(ii < 0 || jj < 0 || ii >= GW || jj >= GH) continue; const kk = jj*GW + ii; if(d[kk] > d[k] + 1){ d[kk] = d[k] + 1; q.push(kk); } } }
  return d; };
const dForeign = near(inCN.map(v => v ? 0 : 1));
function snap(shape){
  const has = new Uint8Array(GW*GH); for(let j = 0; j < GH; j++) for(let i = 0; i < GW; i++) has[j*GW + i] = inside(shape, cellPt(i, j)) ? 1 : 0;
  const dS = near(has), add = new Array(GW*GH).fill(0);
  for(let k = 0; k < GW*GH; k++) if(inCN[k] && !has[k] && dS[k] <= NEAR && dForeign[k] <= NEAR) add[k] = 1;
  const [ct] = d3.contours().size([GW, GH]).thresholds([0.5])(add);
  const cells = ct.coordinates.map(p => p.map(r => r.map(([x, y]) => [R3(GX0 + x*G), R3(GY1 - y*G)])));
  return cells.length ? clipCN(pc.union(R3mp(shape), cells)) : shape;
}
/* polygon-clipping can fail on near-coincident edges: retry on a slightly coarser grid */
const Rq = q => mp => mp.map(p => p.map(r => r.map(([x, y]) => [Math.round(x/q)*q, Math.round(y/q)*q].map(R3))));
const safe = (op, ...args) => { for(const q of [0.001, 0.002, 0.004]){ try { return R3mp(pc[op](...args.map(Rq(q)))); } catch(e){ if(q === 0.004) throw e; } } };
const ET = snap(clipCN(T.et));
const ILI = safe('intersection', snap(clipCN(T.m2_dark)), ET);
const TARIM = safe('difference', safe('intersection', snap(clipCN(T.m1_dark)), ET), ILI);
const ALL = fillSmall(snap(clipCN(T.et))).filter(p => ringSr(p[0])*KM >= 50);   /* East Turkestan, as the third map draws it (inland slivers under 50 km² dropped) */
const EAST = safe('difference', ALL, TARIM, ILI).filter(p => ringSr(p[0])*KM >= 2000);   /* slivers along the shared edges stay with their neighbours */
const cen = mp => { let best = mp[0]; mp.forEach(p => { if(ringSr(p[0]) > ringSr(best[0])) best = p; }); const c = d3.geoCentroid({type:'Polygon', coordinates:[best[0]]}); return [R3(c[0]), R3(c[1])]; };
const S = {
  yet:{t:'Yettishar (Wikipedia)', u:'https://en.wikipedia.org/wiki/Yettishar', k:'modern', s:'Yaqub Beg’s state in the Tarim basin, 1864/65–1877; Kashgar its capital'},
  yetc:{t:'Coin of Yaqub Beg naming the Ottoman sultan (NumisBids lot note)', u:'https://www.numisbids.com/sale/8237/lot/1601', k:'modern', s:'allegiance to the Ottoman sultan-caliph ʿAbd al-ʿAzīz in 1873, the title of Emir in return; ruled Yangi Hisar, Yarkand, Khotan, Aqsu, Kucha, Korla, Turfan, Urumqi and Kara Sheher; died at Korla in 1877'},
  yetk:{t:'Yaqub Beg coins dated from 1873 in the name of ʿAbd al-ʿAzīz (Spink)', u:'https://www.spink.com/lot/CSS36001508', k:'modern', s:'named on a series of coins from 1873'},
  kk:{t:'Kara-Khanid Khanate (Wikipedia)', u:'https://en.wikipedia.org/wiki/Kara-Khanid_Khanate', k:'modern', s:'the first Turkic Muslim dynasty; Kashgar one of its capitals'},
  kho:{t:'The Qarakhanid campaign against Khotan (Study Buddhism)', u:'https://studybuddhism.com/en/advanced-studies/history-culture/buddhism-islam-advanced/buddhist-muslim-interaction-later-abbasid-period/qarakhanid-campaign-against-khotan', k:'modern', s:'Khotan taken about 1006 and absorbed into the Qarakhanid realm'},
  ili:{t:'Ili Kazakh Autonomous Prefecture (Wikipedia)', u:'https://en.wikipedia.org/wiki/Ili_Kazakh_Autonomous_Prefecture', k:'modern', s:'the Taranchi Sultanate formed by Dungans and Taranchis in the Muslim revolt of 1864; part returned to China by the Treaty of Saint Petersburg, 1881'},
  ilr:{t:'Russia’s withdrawal from the Ili valley in 1881 (The Cartographer)', u:'https://cartographer.substack.com/p/russias-withdrawal-from-the-ili-river', k:'modern', s:'Russian occupation of Ili from 1871'}
};
const GK = 'From general knowledge, not checked against the sources: ';
const UNITS = [
  {shape:TARIM, label:'The Tarim basin (Altishahr: Kashgar, Yarkand, Khotan, Aksu, Kucha)', cat:'dynasty', conf:'medium',
   who:'The Karakhanids, who recognised the Abbasid caliph (Kashgar from the 10th century, Khotan from about 1006); then Yettishar under Yaqub Beg, who gave his allegiance to the Ottoman sultan-caliph in 1873 and struck coins in his name',
   dates:'about 1006 to the 1130s in the west (Karakhanid); 1873–1877 (Yettishar under the Ottoman caliph)', nominal:true,
   states:[{n:'Karakhanids', d:'10th century–1130s (then under Qara Khitai overlordship)', r:'yes'}, {n:'Chagatai khans and Moghulistan', d:'14th–15th centuries', r:'no'}, {n:'Yarkand Khanate', d:'1514–1705', r:'no'}, {n:'Yettishar (Yaqub Beg)', d:'1864/65–1877; under the Ottoman caliph from 1873', r:'yes'}],
   notes:'Kashgar was a Karakhanid capital and Khotan was taken from its Buddhist kings about 1006; the eastern oases (Kucha, Korla) came under Muslim rule later. Yaqub Beg made Kashgar his capital in 1865; in 1873 he offered his allegiance to the Ottoman sultan ʿAbd al-ʿAzīz as caliph, received the title of Emir, and struck coins in his name. He died at Korla in 1877, and the Qing retook the region by 1878. The tie to a caliph was nominal both times.',
   uncertain:GK + 'the dates of the Chagatai, Moghulistan and Yarkand khanates, and the Qing conquest of 1759. The search found no source for the Karakhanids’ recognition of the Abbasids beyond the one used for southern Kazakhstan in this table.',
   sources:[S.kk, S.kho, S.yet, S.yetc, S.yetk]},
  {shape:EAST, label:'Turfan, Ürümqi and the east (with the strip of western Gansu the map takes in)', cat:'dynasty', conf:'low',
   who:'Yettishar under Yaqub Beg, who held Turfan, Ürümqi and Karashahr in the 1870s and gave his allegiance to the Ottoman sultan-caliph in 1873',
   dates:'1870s to 1877 (Yettishar, under the Ottoman caliph from 1873)', nominal:true,
   states:[{n:'Moghulistan and the Turfan khans', d:'15th–17th centuries', r:'no'}, {n:'Dungan risings (Ürümqi)', d:'1864–1870', r:'no'}, {n:'Yettishar (Yaqub Beg)', d:'1870s–1877', r:'yes'}],
   notes:'The hatched part of the Yettishar map: the lands Yettishar held for part of its existence. A coin-catalogue note lists Turfan, Ürümqi and Karashahr among Yaqub Beg’s lands. Hami (Kumul) in the far east, and much of northern Dzungaria, were probably never his; the map draws them hatched as well. The East Turkestan map also takes in a strip of western Gansu, east of Xinjiang’s official boundary (to about 99°E), which Yettishar never held.',
   uncertain:'When exactly Yaqub Beg took Turfan and Ürümqi, and how far east his rule reached, was not confirmed. ' + GK + 'the Turfan basin was Buddhist under the Uyghur kingdom of Qocho until it became Muslim in the 15th century; Hami was a Muslim khanate under the Qing.',
   sources:[S.yet, S.yetc]},
  {shape:ILI, label:'The Ili region (Ili, Tacheng and Altay)', cat:'islamic', conf:'low',
   who:'No caliphate. Muslim rulers: the Taranchi Sultanate (1864–1871)',
   dates:'1864–1871 (Taranchi Sultanate)', nominal:false,
   states:[{n:'Chagatai khans and Moghulistan (Almaliq)', d:'14th century', r:'no'}, {n:'Taranchi Sultanate', d:'1864–1871', r:'no'}],
   notes:'The second map: the Ili Kazakh Autonomous Prefecture. In the Muslim revolt of 1864 the Dungans and Taranchis of the Ili valley set up the Taranchi Sultanate; Russia occupied Ili in 1871 and returned most of it to China by the Treaty of Saint Petersburg (1881). Yettishar did not hold Ili.',
   uncertain:GK + 'the Muslim Chagatai khans at Almaliq in the 14th century; Tacheng and the Altai were probably never under a Muslim state at all, so for them “influence only” may be the truer shade.',
   sources:[S.ili, S.ilr]}
];
const before = area(C.v2.polys), oldHoles = C.v2.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = R3mp(pc.union(R3mp(C.v2.polys), ALL));
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]);
const gain = area(X) - before; C.v2.polys = X; C.v2.km2 += gain;
const tot = area(ALL), hs = {};
UNITS.forEach(u => { const km2 = area(u.shape); hs[u.cat] = (hs[u.cat] || 0) + km2;
  const {shape, ...rest} = u; C.v2.units.push({a3:'XJ', country:'China (Xinjiang)', ...rest, km2, c:cen(shape), polys:shape}); });
Object.keys(hs).forEach(k => hs[k] = Math.round(100*hs[k]/tot));
C.v2.states.push({id:'156_X', n:'China: East Turkestan (Xinjiang), as the map draws it', km2:tot, pct:Math.round(100*tot/9596961), core:false, hs});   /* China's whole area (the base map stops at 104°E, so it cannot be measured here) */
C.v2.states.sort((a, b) => (b.core === true) - (a.core === true) || b.km2 - a.km2);
C.v2.countries.push({a3:'XJ', n:'East Turkestan (Xinjiang, China)', summary:'East Turkestan (Uyghur شەرقىي تۈركىستان), the name used for the region by Uyghur nationalists, as the author’s map draws it: all of Xinjiang and a strip of western Gansu. Two further maps divide it here: Yettishar, Yaqub Beg’s state of the 1860s–1870s (its core in the Tarim basin, and the lands it held for a time to the north and east), and the Ili Kazakh Autonomous Prefecture. The western Tarim basin came under the Muslim Karakhanids from the 10th century (Khotan about 1006), who recognised the Abbasid caliph; Yettishar recognised the Ottoman sultan as caliph from 1873. Ili had a Muslim sultanate of its own (1864–1871) but no caliph. The Qing ruled Xinjiang from 1759 and again from 1878; it is now part of China.'});
C.v2.xinjiang = 'Version 62–63: East Turkestan (Xinjiang), divided by the Yettishar and Ili maps, in Complete V2';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Xinjiang', tot, 'km² (', Math.round(100*tot/9596961), '% of China ) | V2 +', gain, '->', C.v2.km2, '| units', UNITS.map(u => u.label.split(' (')[0] + ' ' + area(u.shape)).join('; '), '| hs', JSON.stringify(hs));
