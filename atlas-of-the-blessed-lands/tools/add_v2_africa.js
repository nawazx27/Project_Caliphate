/* Version 43 (2026-10-07, Nawaz's request): Complete V2 also takes in, whole, every Muslim-majority country of Africa it did not already hold.
   The list is the one the Greater Caliphate already uses (CALIPH.g states marked afr). Run once: node tools/add_v2_africa.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.v2.africa){ console.log('already added'); process.exit(0); }
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * 6371.0088**2);
const R3 = v => Math.round(v*1000)/1000;
const mpOf = id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); const f = topojson.feature(geo, g).geometry; return f.type === 'Polygon' ? [f.coordinates] : f.coordinates; };
const have = new Set(C.v2.states.map(s => s.id));
const add = C.g.states.filter(s => s.afr && !have.has(s.id));
const before = area(C.v2.polys);
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
C.v2.polys = pc.union(R3mp(C.v2.polys), ...add.map(s => R3mp(mpOf(s.id)))).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const gain = area(C.v2.polys) - before; C.v2.km2 += gain;
add.forEach(s => { const a = area(mpOf(s.id)); C.v2.states.push({id:s.id, n:s.n, km2:a, pct:100, core:false, afr:true}); });
C.v2.states.sort((a, b) => (b.core === true) - (a.core === true) || b.km2 - a.km2);
const GK = ' (From general knowledge; not checked against the sources used for the lands researched province by province.)';
const H = {
  'Chad': 'Ruled by Muslim sultanates (Kanem–Bornu, Baguirmi, Wadai), none of them under a caliph; the Ottomans briefly garrisoned part of the far north early in the 20th century.',
  'Mali': 'Heart of the Muslim empires of Mali and Songhay. In 1591 the Saadian sultan Ahmad al-Mansur, who styled himself caliph, conquered the Niger bend; the Moroccan pashas of Timbuktu soon became independent. The 19th-century Massina caliphate (Hamdullahi) ruled the inner Niger delta.',
  'Niger': 'Part of Songhay in the west and of Bornu in the east; in the 19th century the south was held by the Sokoto Caliphate founded by Uthman dan Fodio.',
  'Nigeria': 'The north was the core of the Sokoto Caliphate (1804–1903) and, in the north-east, of Bornu; the south was never under a Muslim state. Muslims are about half of the population; estimates vary.',
  'Burkina Faso': 'Mostly the Mossi kingdoms, which were not Muslim states; the far north (Liptako) was an emirate in the orbit of the Sokoto Caliphate in the 19th century.',
  'Guinea': 'The Fouta Djallon imamate (from the 1720s to 1896) was a Muslim state of its own, not under a caliph; Samori Ture’s state held the east in the late 19th century.',
  'Senegal': 'Muslim states such as the imamate of Futa Toro arose here, none of them under a caliph.',
  'Sierra Leone': 'Islam spread mainly through traders and clerics; no caliphate or large Muslim state ruled it.',
  'Guinea-Bissau': 'Part of the Kaabu kingdom, later conquered by Fula states from Fouta Djallon; never under a caliph. Muslims are around half of the population; estimates vary.',
  'Gambia': 'Small Mandinka and Wolof states, shaken by 19th-century Muslim reform wars; never under a caliph.',
  'Comoros': 'Ruled by Shirazi Muslim sultanates; never under a caliph.'};
add.forEach(s => C.v2.countries.push({a3:'AF_' + s.id, n:s.n, summary:(H[s.n] || 'No caliphate ruled it.') + GK}));
C.v2.africa = 'Version 43: the Muslim-majority countries of Africa, whole';
fs.writeFileSync(F, JSON.stringify(C));
console.log('added', add.map(s => s.n).join(', '), '| gained', gain, 'km²; V2 now', C.v2.km2);
