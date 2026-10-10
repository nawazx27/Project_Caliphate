/* Version 53 (2026-10-10, Nawaz's request, with a Google Maps screenshot of Sicily and Malta: "Add entire Algeria, Morocco, Spain, Portugal,
   Uzbekistan, Tajikistan and the islands in the image to the complete caliphate").
   - Algeria, Spain (with the Balearics, the Canaries, Ceuta and Melilla), Portugal (with Madeira and the Azores, as far as the sheet goes),
     Uzbekistan, Tajikistan and Malta: whole, from the base map.
   - Morocco: whole within its internationally recognised border (north of 27°40′N). The base map draws Morocco as it is held de facto, with
     most of Western Sahara; that part (status disputed) is NOT added here.
   - The islands in the screenshot: all of Sicily with Ustica, the Aeolian and Egadi islands, Pantelleria and Lampedusa (Linosa and Lampione
     are too small for the base map), and Malta.
   Complete and To Iraq (all but Uzbekistan and Tajikistan) take them; V2 and Maximum, which hold Complete, take what they lacked; Greater
   holds them already (its rows and cards are re-labelled). Run once: node tools/add_core_west.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.coreWest){ console.log('already added'); process.exit(0); }
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const mpOf = id => R3mp(asMp(topojson.feature(geo, geo.objects.countries.geometries.find(g => String(g.id) === id)).geometry));
const closed = pts => { const o = pts.slice(); if(o[0][0]!==o[o.length-1][0] || o[0][1]!==o[o.length-1][1]) o.push(o[0]); return o; };

const MOROCCO = R3mp(pc.intersection(mpOf('504'), [[closed([[-18.5,27.667],[0.5,27.667],[0.5,36.5],[-18.5,36.5]])]]));
const SICILY = mpOf('380').filter(p => { const c = d3.polygonCentroid(p[0]); return c[0] > 11.5 && c[0] < 15.8 && c[1] > 35.3 && c[1] < 39.1; });
const PIECES = {
  '012': {n:'Algeria', mp:mpOf('012'), west:true},
  '504': {n:'Morocco (without Western Sahara)', mp:MOROCCO, west:true, flag:'internationally recognised border'},
  '724': {n:'Spain', mp:mpOf('724'), west:true},
  '620': {n:'Portugal', mp:mpOf('620'), west:true},
  '380': {n:'Italy: Sicily and its islands', mp:SICILY, west:true, part:true},
  '470': {n:'Malta', mp:mpOf('470'), west:true},
  '860': {n:'Uzbekistan', mp:mpOf('860')},
  '762': {n:'Tajikistan', mp:mpOf('762')}};
const NE = JSON.parse(fs.readFileSync(path.join(ROOT, 'ne_10m_admin_0_countries.geojson'))).features;
const fullKm = id => { const f = NE.find(f => f.properties.ISO_N3 === id); return f ? area(asMp(f.geometry)) : null; };
for(const [id, p] of Object.entries(PIECES)){ p.km2 = area(p.mp); p.pct = p.part ? Math.max(1, Math.round(100 * p.km2 / fullKm(id))) : 100; console.log(id, p.n.padEnd(34), p.km2, 'km²', p.pct + '%'); }

function grow(V, ids, label){
  const add = pc.union(...ids.map(id => PIECES[id].mp));
  const before = area(V.polys), oldHoles = V.polys.flatMap(p => p.slice(1)).map(r => d3.polygonCentroid(r));
  let X = pc.union(R3mp(V.polys), add).map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
  let filled = 0, fk = 0;
  X = X.map(p => [p[0], ...p.slice(1).filter(r => { const a = ringSr(r)*KM, c = d3.polygonCentroid(r);
    const old = oldHoles.some(o => Math.abs(o[0]-c[0]) < 0.01 && Math.abs(o[1]-c[1]) < 0.01);
    if(!old && a < 5000){ filled++; fk += a; return false; } return true; })]);
  const gain = area(X) - before; V.polys = X; V.km2 += gain;
  console.log(label.padEnd(9), '+', gain, 'km² ->', V.km2, '| gaps filled', filled, Math.round(fk), 'km²');
}
/* one row per added state in a table: the earlier part-rows (id or id_C) give way to it */
function setRows(V, ids, extra){
  for(const id of ids){
    const p = PIECES[id], old = V.states.find(s => String(s.id) === id && !s.dup);
    V.states = V.states.filter(s => !(String(s.id) === id + '_C') && !(String(s.id) === id && !s.dup && !p.part) && !(p.part && String(s.id) === id && V === C.x));
    if(p.part && V !== C.x && V !== C.xw){   /* Greater, V2, Maximum: Italy keeps its own row; Sicily is the core part */
      const r = V.states.find(s => String(s.id) === id && !s.dup);
      V.states.push({id:id + '_C', n:p.n + ' (in the complete version)', km2:p.km2, pct:p.pct, core:true, dup:!!r});
      continue; }
    V.states = V.states.filter(s => String(s.id) !== id || s.dup);
    V.states.push(Object.assign({id, n:p.n, km2:p.km2, pct:p.pct}, p.flag ? {flag:p.flag} : {}, extra ? extra(old) : {}));
  }
  V.states.sort((a, b) => b.km2 - a.km2);
}
const ALL = Object.keys(PIECES), WEST = ALL.filter(id => PIECES[id].west);
grow(C.x, ALL, 'Complete'); setRows(C.x, ALL);
grow(C.xw, WEST, 'To Iraq'); setRows(C.xw, WEST);
grow(C.v2, ['380', '470'], 'V2');   /* V2 holds Algeria, Morocco, Spain, Portugal, Uzbekistan and Tajikistan whole already */
setRows(C.v2, ALL, old => Object.assign({core:true}, old && old.hs ? {hs:old.hs} : {}));
grow(C.m, ['724', '620', '380'], 'Max');   /* Maximum holds Algeria, Morocco, Uzbekistan, Tajikistan and Malta whole already */
setRows(C.m, ALL, () => ({core:true}));
/* V2, Maximum and Greater already held the base map's whole Morocco, which includes the part of Western Sahara Morocco holds: that part keeps a row of its own, outside the core */
const WS_HELD = area(mpOf('504')) - PIECES['504'].km2;
const wsRow = extra => Object.assign({id:'504_W', n:'Western Sahara, the part held by Morocco', km2:WS_HELD, pct:Math.round(100 * WS_HELD / (WS_HELD + area(mpOf('732')))), flag:'status internationally disputed'}, extra);
C.v2.states.push(wsRow({core:false})); C.m.states.push(wsRow({core:false, add:'whole'}));
/* Greater: same land. In its Italy rows the ruled part loses Sicily to the core part */
{ const it = C.g.states.find(s => s.id === '380'), oldC = C.g.states.find(s => s.id === '380_C');
  const prevCore = oldC ? oldC.km2 : 0; it.km2 -= (PIECES['380'].km2 - prevCore); }
setRows(C.g, ALL, () => ({core:true, afr:false, hist:false}));
C.g.states.push(wsRow({core:false, afr:false, hist:false}));
C.g.states.sort((a, b) => b.km2 - a.km2);
const R = C.g.regions, byId = new Map(C.g.states.filter(s => !s.dup).map(s => [String(s.id), s]));   /* 504_W is not dup, so cards find it */
const cardStates = ids => ids.map(id => byId.get(id)).filter(Boolean).map(x => ({n:x.n, km2:x.km2, pct:x.pct, ...(x.flag ? {flag:x.flag} : {})}));
const card = (r, fields) => { Object.assign(r, fields); r.states = cardStates(r.ids); r.km2 = r.states.reduce((t, s) => t + s.km2, 0); return r; };
card(R.find(r => r.id === 'maghrib'), {ids:['504_W','732','478'], en:'Western Sahara and Mauritania (Libya, Tunisia, Algeria and Morocco are now in the core)'});
card(R.find(r => r.id === 'centralasia'), {ids:['398','417'], en:'Kazakhstan and Kyrgyzstan (Turkmenistan, Uzbekistan and Tajikistan are now in the core)'});
const an = R.find(r => r.id === 'andalus'); delete an.hist; card(an, {en:'Spain and Portugal, whole · added to the complete version at your request'});
R.find(r => r.id === 'siqilliyah').en = 'southern Italy and Sardinia (Sicily, its islands and Malta are now in the core)';
const newCards = [
  card({id:'maghribcore', n:'al-Maghrib al-Awsaṭ · al-Aqṣā', ar:'المغرب الأوسط والأقصى', en:'all of Algeria and Morocco (without Western Sahara) · added at your request', b:[[-13.5,18.5],[12.2,37.5]]}, {ids:['012','504']}),
  card({id:'transox', n:'Mā warāʾ al-Nahr · al-Khuttal', ar:'ما وراء النهر', en:'all of Uzbekistan and Tajikistan · added at your request', b:[[55.8,36.5],[75.5,45.8]]}, {ids:['860','762']}),
  card({id:'siqcore', n:'Ṣiqilliyah · Mālṭah', ar:'صقلية ومالطة', en:'Sicily with its islands, and Malta · added at your request', b:[[11.8,35.3],[15.8,39.0]]}, {ids:[]})];
newCards[2].states = [{n:PIECES['380'].n, km2:PIECES['380'].km2, pct:PIECES['380'].pct}, {n:'Malta', km2:PIECES['470'].km2, pct:100}]; newCards[2].km2 = PIECES['380'].km2 + PIECES['470'].km2;
const moved = R.splice(R.indexOf(an), 1);
R.splice(R.findIndex(r => r.id === 'khurasan') + 1, 0, ...newCards, ...moved);
C.coreWest = 'Version 53: Algeria, Morocco, Spain, Portugal, Uzbekistan, Tajikistan, Sicily with its islands and Malta in the complete version';
fs.writeFileSync(F, JSON.stringify(C));
console.log('Complete', C.x.km2, C.x.states.length, '| To Iraq', C.xw.km2, C.xw.states.length, '| V2', C.v2.km2, C.v2.states.length, '| Max', C.m.km2);
console.log('Complete rows:', C.x.states.filter(s => ALL.includes(String(s.id))).map(s => s.n + ' ' + s.km2).join('; '));
