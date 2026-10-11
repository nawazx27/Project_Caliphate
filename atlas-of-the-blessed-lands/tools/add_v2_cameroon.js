/* Version 64 (2026-10-11, Nawaz's request: "Add Cameroon to the v2 caliphate"). Cameroon, whole, joins Complete V2, as two V2 provinces:
   the north (Extrême-Nord, Nord and Adamaoua: the Adamawa emirate of the Sokoto Caliphate) and the rest (no Muslim state ruled it).
   The provinces are Natural Earth admin-1. Run once: node tools/add_v2_cameroon.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const A1 = JSON.parse(fs.readFileSync(path.join(ROOT, 'admin1_used.geojson'))).features;
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.v2.cameroon){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const CMR = R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === '120')).geometry));
const prov = names => R3mp(pc.union(...names.map(n => { const f = A1.find(f => f.properties.adm0_a3 === 'CMR' && f.properties.name === n); if(!f) throw new Error('no province ' + n); return R3mp(asMp(f.geometry)); })));
const NORTH = R3mp(pc.intersection(prov(['Extrême-Nord', 'Nord', 'Adamaoua']), CMR));
const SOUTH = R3mp(pc.difference(CMR, NORTH)).filter(p => ringSr(p[0])*KM >= 50);
const cen = mp => { let best = mp[0]; mp.forEach(p => { if(ringSr(p[0]) > ringSr(best[0])) best = p; }); const c = d3.geoCentroid({type:'Polygon', coordinates:[best[0]]}); return [R3(c[0]), R3(c[1])]; };
const S = {
  zub:{t:'Zubeiru bi Adama (Wikipedia)', u:'https://en.wikipedia.org/wiki/Zubeiru_bi_Adama', k:'modern', s:'the Adamawa emirate, founded by Modibbo Adama in the Sokoto jihad; partitioned by Britain and Germany in 1901, the larger part going to German Kamerun'},
  dom:{t:'Hans Dominik (Schutztruppe) (Wikipedia)', u:'https://en.wikipedia.org/wiki/Hans_Dominik_(Schutztruppe)', k:'modern', s:'German capture of Ngaoundéré (1901), defeat of the emir near Garoua, and Maroua'},
  yola:{t:'History of Yola (Kupi)', u:'https://kupi.com/en/explore/nigeria/yola/history', k:'modern', s:'Modibbo Adama, emir 1809–1848, founded Yola in 1841'},
  bam:{t:'Ibrahim Njoya (Wikipedia)', u:'https://en.wikipedia.org/wiki/Ibrahim_Njoya', k:'modern', s:'the Bamum king converted to Islam with much of his court (1916; other sources give 1896 or 1918)'},
  isl:{t:'Islam in Cameroon (Wikipedia)', u:'https://en.wikipedia.org/wiki/Islam_in_Cameroon', k:'modern', s:'about 30.6% of the population Muslim (2022 estimate); the Fulani of the north and the Bamum largely Muslim'}
};
const UNITS = [
  {shape:NORTH, label:'Northern Cameroon (Adamawa, the North and the Far North)', cat:'direct', conf:'medium',
   who:'The Sokoto Caliphate, through its Adamawa emirate (Fombina), founded by Modibbo Adama, who carried the Sokoto jihad’s flag; its lamidos owed allegiance to the caliph at Sokoto',
   dates:'about 1809–1901 (Adamawa emirate under the Sokoto Caliphate)', nominal:false,
   states:[{n:'Kanem–Bornu (the Lake Chad shore)', d:'from the medieval period', r:'no'}, {n:'Adamawa emirate (Sokoto Caliphate)', d:'about 1809–1901', r:'yes'}],
   notes:'Modibbo Adama received the flag of the jihad from Uthman dan Fodio and built the Adamawa emirate (Fombina), with sub-emirates such as Garoua, Maroua and Ngaoundéré. In 1901 Britain and Germany partitioned it; the larger part went to German Kamerun. The far north by Lake Chad was in the orbit of Bornu, which did not acknowledge Sokoto.',
   uncertain:'Sources give 1806 or 1809 for the start; how far south and east the emirate’s rule reached at each time (the Adamaoua plateau was raided more than ruled in places) was not checked. The three provinces are taken whole.',
   sources:[S.zub, S.yola, S.dom]},
  {shape:SOUTH, label:'Southern and western Cameroon', cat:'influence', conf:'medium',
   who:'No caliphate and no Muslim state',
   dates:'', nominal:false,
   states:[{n:'Kingdom of Bamum (its king Muslim from 1896–1918, under colonial rule)', d:'late 19th–20th century', r:'no'}],
   notes:'The forest and grasslands of the south were never under a Muslim state. Islam came by trade and through the north; the Bamum king Ibrahim Njoya became Muslim with much of his court, while his kingdom was under German and then French rule.',
   uncertain:'Whether the Bamum kingdom should count as a Muslim state here; it is shaded “influence only”.',
   sources:[S.bam, S.isl]}
];
const before = area(C.v2.polys), oldHoles = C.v2.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
let X = R3mp(pc.union(R3mp(C.v2.polys), CMR));
X = X.map(p => [p[0], ...p.slice(1).filter(r => { const c = d3.polygonCentroid(r); return oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01) || ringSr(r)*KM >= 5000; })]);
const gain = area(X) - before; C.v2.polys = X; C.v2.km2 += gain;
const tot = area(CMR), hs = {};
UNITS.forEach(u => { const km2 = area(u.shape); hs[u.cat] = (hs[u.cat] || 0) + km2;
  const {shape, ...rest} = u; C.v2.units.push({a3:'CMR', country:'Cameroon', ...rest, km2, c:cen(shape), polys:shape}); });
Object.keys(hs).forEach(k => hs[k] = Math.round(100*hs[k]/tot));
C.v2.states.push({id:'120', n:'Cameroon', km2:tot, pct:100, core:false, hs});
C.v2.states.sort((a, b) => (b.core === true) - (a.core === true) || b.km2 - a.km2);
C.v2.countries.push({a3:'CMR', n:'Cameroon', summary:'Added whole at the author’s request. Its north was the Adamawa emirate (Fombina) of the Sokoto Caliphate, from about 1809 until Britain and Germany divided it in 1901; the south was never under a Muslim state. Muslims are about 30% of the people today (2022 estimate).'});
C.v2.cameroon = 'Version 64: Cameroon, whole, in Complete V2';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Cameroon', tot, 'km² | V2 +', gain, '->', C.v2.km2, '| north', area(NORTH), 'south', area(SOUTH), '| hs', JSON.stringify(hs));
