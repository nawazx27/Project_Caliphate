/* ================= v4 engine, part C: overlay, collisions, zoom ================= */
const ov = svg.append('g');
let ovGrat, ovBack, ovLead, ovMain, ovBadge, ovTop, qa1, qa2;
let pts = [], lbls = [], sbs = [];
let TIER = null, TIER_KEEP = false, flashPt = null, XV = 'full';   /* XV (Version 66 numbering by size): 'me' (V1, the Middle East), 'full' (V2, Complete), 'fullb' (V2-B, V2 without the Balkan Peninsula, Version 108), 'v3' (V5, Complete extended), 'v2' (V6, Greater Middle East); 'gme' (V7, Greater Caliphate) was deleted in Version 155 at the author's request; the V7 added in Version 159 ('full7': V2 plus the Himalayas, the Vale of Kashmir, the Deccan Plateau and the Sahara) was deleted in Version 169 at the author's request; 'west' (V3, to Iraq's border) was deleted in Version 157 at the author's request. Before: 'full' (core, complete), 'west' (core to Iraq's border), 'gme' (the Greater Caliphate: the core, extended, in one colour), 'v2' (Complete V2) or 'nat' (the territory inside the natural line) */   /* XV: version of the user's outline, 'full' or 'west' (to Iraq's border) */   /* source-tier filter; pulse marker for search results */
const SHORT = {1:"al-Masjid al-Ḥarām",2:"ʿArafah · Muzdalifah · Minā",3:"al-Masjid al-Nabawī",4:"Qubāʾ",5:"al-ʿAqīq",6:"Uḥud",7:"Wajj",8:"",9:"The Holy Land",10:"The land We blessed",11:"al-Shām in the Sunnah",12:"al-Ṭūr · Ṭuwā",13:"The fig and the olive",14:"al-Yaman",15:"Miṣr",16:"Iraq and the East",17:"The mawāqīt",18:"al-Isrāʾ and the qibla",19:"Sabaʾ · Quraysh",20:"al-Ḥabashah",21:"Bilād al-Rūm",22:"End-of-time places"};
/* short tags for the province labels when zoomed far out (the pattern of your ŠM, ḤJ, YM) */
const REGION_TAG = {sham:'ŠM', hijaz:'ḤJ', yemen:'YM', jazirah:'JA', upper:'JZ', iraq:'ʿR', misr:'MṢ', najd:'NJ', rum:'RM', habashah:'ḤB'}, TAG_K = 0.45;
const DAR_AT = [38.2, 19.3];   /* the country name sits over the Red Sea and western Arabia */
const STAR5 = "M0.00,-5.20L1.26,-1.74L4.95,-1.61L2.04,0.66L3.06,4.21L0.00,2.15L-3.06,4.21L-2.04,0.66L-4.95,-1.61L-1.26,-1.74Z";   /* five-pointed star of the capital marker */
/* the one sea chokepoint on the natural ring (the ring runs out through the Strait of Gibraltar); a name is shown only until the base map's own label takes over */
const NAT_PTS = [
  {sym:'gate', ll:[-5.60,35.96], title:'Strait of Gibraltar (al-Zuqāq) · sea chokepoint on the ring', name:'Gibraltar', k:0.6, maxK:2.4}
];
const RING_DASH = {rev:null, salaf:"5 3.4", later:".5 3.9", disp:".5 3.9"};
function makeText(cls, lines, back){
  const t = (back ? ovBack : ovMain).append('text').attr('class','lbl '+(cls||''));
  const subs = [];
  lines.forEach((ln,i)=>{
    if(!ln || !ln[0]) return;
    const ts = t.append('tspan').text(ln[0]).attr('class', ln[1]||null);
    if(i>0){ ts.attr('x',0).attr('dy', ln[2]||'1.2em'); subs.push(ts); }
  });
  return {t, subs};
}
function addLabel(layer, lines, ll, o){
  o = o||{};
  const {t, subs} = makeText(o.cls, lines, o.back);
  t.attr('text-anchor', o.anchor||'middle');
  if(o.color) t.style('fill', `var(${o.color})`);
  const item = {t, subs, v:P(ll), layer, minK:o.minK||0, subK:o.subK!=null?o.subK:(o.minK||0), dx:o.dx||0, dy:o.dy||0, pri:o.pri!=null?o.pri:10, nudge:!!(o.cls && !/note/.test(o.cls) && !o.point && !o.free), maxK:o.maxK||0, free:!!o.free, noClean:!!o.noClean};
  /* Version 176: a label may lie along a narrow sea (rot, degrees) and may have other spots to try (alts, [lon,lat]) when the first is crowded */
  if(o.rot){ item.rot = o.rot; t.attr('text-anchor','middle'); }
  if(o.alts) item.av = o.alts.map(P);
  if(o.strict) item.strict = true;
  if(o.cls && /\bsea\b/.test(o.cls) && !/small/.test(o.cls)) item.sea = true;   /* shown only where it crosses no outline */
  lbls.push(item); return item;
}
function addPoint(layer, ll, o){
  const g = ovMain.append('g').attr('class','pt').attr('data-sel', o.info||'');
  g.append('circle').attr('class','hit').attr('r',12);
  g.append('circle').attr('class','ring').attr('r',8.5);
  const c = o.color ? `var(${o.color})` : null;
  if(o.sym==='diamond') g.append('path').attr('class','sym').attr('d','M0,-6.5L6.5,0L0,6.5L-6.5,0Z').style('fill', c);
  else if(o.sym==='tri') g.append('path').attr('class','sym').attr('d','M0,-6L5.5,4.5L-5.5,4.5Z').style('fill', c);
  else if(o.sym==='ring') { g.append('circle').attr('class','sym').attr('r',5).style('fill','var(--halo)').style('stroke',c).style('stroke-width',2.4); g.append('circle').attr('r',1.6).style('fill',c); }
  else if(o.sym==='badge'){ g.attr('class','pt badge'); g.append('circle').attr('class','bg').attr('r',8); g.append('text').text(o.letter); }
  else if(o.sym==='pass'){ g.append('path').attr('class','passm').attr('d','M-4.5,-4.5Q-1.2,0 -4.5,4.5M4.5,-4.5Q1.2,0 4.5,4.5'); }
  else if(o.sym==='gate'){ g.attr('class','pt natpt'); g.append('path').attr('class','gate').attr('d','M-6,-5.5L-2,-1.6L-2,1.6L-6,5.5M6,-5.5L2,-1.6L2,1.6L6,5.5'); }
  else if(o.sym==='fort'){ g.attr('class','pt natpt'); g.append('path').attr('class','fort').attr('d','M-6,5V-2H-4V-4.5H-1.5V-2H1.5V-4.5H4V-2H6V5Z'); }
  else if(o.sym==='watch'){ g.attr('class','pt natpt'); g.append('circle').attr('class','watch').attr('r',6.5); g.append('path').attr('class','passm').attr('d','M-3.4,-3.4Q-0.9,0 -3.4,3.4M3.4,-3.4Q0.9,0 3.4,3.4'); }
  else if(o.sym==='capital'){ g.select('circle.hit').remove(); g.attr('class','pt capital');
    g.append('circle').attr('class','capring').attr('r',11);
    g.append('path').attr('class','capstar').attr('d', STAR5).attr('transform','translate(0,11.5) scale(1.2)'); }
  else if(o.sym==='square') g.append('rect').attr('class','sym').attr('x',-4).attr('y',-4).attr('width',8).attr('height',8).style('fill', c);
  else g.append('circle').attr('class','dot').attr('r', o.r||3.2).style('fill', o.hollow? 'var(--halo)' : c).style('stroke', o.hollow? c : null);
  if(o.info) g.on('click', e=>{ e.stopPropagation(); select(o.info); }); else g.style('cursor','default');
  if(o.title) g.append('title').text(o.title);
  const pt = {g, v:P(ll), layer, minK:o.minK||0, keep:!!o.keep, vis:false, sym:o.sym||null};
  pts.push(pt);
  if(o.name){
    const right = o.anchor!=='l';
    const it = addLabel(layer, [[o.name], o.sub?[o.sub,'sub']:null], ll, {cls:o.cls, side:'r', dy:4, minK:o.minK||0, maxK:o.maxK, subK:o.subK, pri:o.pri, color:o.lcolor});
    it.point = true; it.pref = right ? 'r' : 'l'; it.ptRef = pt;
  }
  return pt;
}
function addStatusBadge(s){
  const kc = `var(${KIND[s.kind].col})`;
  const lead = ovLead.append('path').attr('class','sleader').style('stroke', kc);
  const dot = ovLead.append('circle').attr('class','sdot').attr('r',2.8).style('fill', kc);
  const g = ovBadge.append('g').attr('class','sb').attr('data-sel','st'+s.n).attr('tabindex',0).attr('role','button').attr('aria-label', `Sacred status ${s.n}: ${s.name}`);
  g.append('circle').attr('class','hit').attr('r',17);
  g.append('circle').attr('class','under').attr('r',16.5);
  const rg = g.append('circle').attr('class','rg').attr('r',14.2).style('stroke', kc);
  const dash = RING_DASH[s.level]; if(dash) rg.style('stroke-dasharray', dash).style('stroke-linecap','round');
  g.append('circle').attr('class','dc').attr('r',10.6).style('fill', kc);
  g.append('text').attr('class','num').text(s.n);
  if(s.level==='disp'){ const qm = g.append('g').attr('transform','translate(10.5,-10.5)'); qm.append('circle').attr('r',6).attr('class','qm'); qm.append('text').attr('class','qmt').text('?'); }
  g.append('title').text(`${s.n} · ${s.name}`);
  const tx = ovBadge.append('text').attr('class','lbl small sname').text(SHORT[s.n]||'');
  const open = ()=>select('st'+s.n);
  g.on('click', e=>{ e.stopPropagation(); open(); });
  g.on('keydown', e=>{ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); open(); } });
  sbs.push({g, lead, dot, tx, level:s.level, hasName:!!SHORT[s.n], tw:60, v:P(s.ll), off:s.off||[0,0], pri:s.pri||5, minK:s.minK||0, layer:KIND[s.kind].layer, far:Math.hypot((s.off||[0,0])[0],(s.off||[0,0])[1])>12, show:false});
}
/* Version 123: when the page opens the overlay (names, markers, discs) is first set up empty, so the map itself reaches the screen
   sooner; it is built a moment later (see src/start.js). OVERLAY_LATER is true only during that first opening. */
let OVERLAY_LATER = false;
function emptyOverlay(){
  ov.selectAll('*').remove(); pts = []; lbls = []; sbs = [];
  ovGrat = ov.append('g'); ovBack = ov.append('g'); ovLead = ov.append('g'); ovMain = ov.append('g'); ovBadge = ov.append('g'); ovTop = ov.append('g');
}
function buildOverlay(){
  if(OVERLAY_LATER){ emptyOverlay(); return; }
  emptyOverlay();
  /* Version 176: the Red Sea and the Gulf are named along their length (as on a printed atlas), so the name stays on the water
     instead of sliding onto Arabia or over the coast towns; the Red Sea has two more spots along its axis for close views */
  const SEA_ROT = {'Baḥr al-Qulzum':{rot:57, at:[38.0,21.6], alts:[[36.3,24.4],[39.9,18.2],[34.6,27.0]]}, 'Baḥr al-Rūm':{alts:[[17.5,33.7],[24.6,33.5]]}, 'Baḥr Fāris':{rot:27, at:[51.1,27.45], alts:[[50.0,28.3],[52.6,26.8]]}};
  SEA_LBL.forEach(s=>{ const r = SEA_ROT[s[0]] || {}; addLabel('base', [[s[0]], s[1]?[s[1],'sub']:null], r.at || [s[2],s[3]], {cls:'sea', pri:20, minK:s[4]||0, subK:Math.max(1.2,s[4]||0), rot:r.rot, alts:r.alts, noClean:!!SEA_ROT[s[0]]}); });   /* Version 178: the Arabic sea names (al-Rūm, al-Qulzum, Fāris) go in the clean map (Nawaz) */
  RIVER_LBL.forEach(s=>addLabel('base', [[s[0]]], [s[1],s[2]], {cls:'sea small', minK:s[3]||1.2, pri:22}));
  /* mountain ranges lettered along their length in spaced capitals, as engraved on printed maps (screen degrees, clockwise) */
  const RANGE_ROT = {'Zagros':38, 'Alborz':-4, 'Caucasus · Jabal al-Qabq':17, 'Ṭūrus · Taurus':-4, 'Pontic Mountains':-3, 'Hindu Kush':-27, 'Himalaya':24, 'Karakoram':30, 'Kopet Dag':18, 'Sulaiman Range':78, 'Tian Shan':-8, 'Atlas Mountains':-20, 'al-Sarāt':57, 'Red Sea Hills':60, 'Jabal Lubnān':-62, 'Ṭuwayq':74};
  PHYS_LBL.forEach(s=>{ const rr = RANGE_ROT[s[0]]; addLabel('base', [[s[0]]], [s[1],s[2]], {cls: rr===undefined ? 'phys' : 'phys range', minK:s[3], pri:18, rot: rr}); });
  ISLAND_LBL.forEach(s=>addLabel('base', [[s[0]]], [s[1],s[2]], {cls:'phys isl', minK:s[3], pri:19}));
  HIST_LBL.forEach(s=>addLabel('histreg', [[s[0]], s[1]?[s[1],'arl','1.3em']:null], [s[2],s[3]], {cls:'hist', minK:s[4], subK:s[4]+0.5, pri:15, color:'--gold'}));
  PASSES.forEach(s=>addPoint('base', [s[1],s[2]], {sym:'pass', name:s[0], minK:s[3], anchor:s[4], cls:'small', pri:13, title:s[0]}));
  COUNTRY_LBL.forEach(c=>addLabel('modern', [[c[0]]], [c[1],c[2]], {cls:'country', minK:c[3], pri:24}));
  WORLD_LBL.forEach(c=>addLabel('modern', [[c[0]]], [c[1],c[2]], {cls:'country', minK:c[3], pri:25}));
  /* province (region) labels: smaller than the country name; zoomed far out each shows a short tag instead */
  const R = (layer, name, ar, ll, col, o) => { o = Object.assign({cls:'region', color:col, pri:2}, o||{});
    const tag = REGION_TAG[layer], mk = o.minK||0;
    if(tag && mk < TAG_K) addLabel(layer, [[tag]], ll, Object.assign({}, o, {cls:o.cls+' tag', minK:mk, maxK:TAG_K}));
    return addLabel(layer, [[name], ar?[ar,'arl','1.35em']:null], ll, Object.assign(o, {minK: tag ? Math.max(mk, TAG_K) : mk})); };
  R('sham','Bilād al-Shām','بلاد الشام',[37.8,34.3],'--sham',{cls:'region big', pri:1});
  R('hijaz','al-Ḥijāz','الحجاز',[39.75,23.2],'--hijaz',{cls:'region big', pri:1});
  addLabel('hijaz', [['Shām or Ḥijāz?'],['the sources overlap here','sub']], [37.7,28.15], {cls:'note', minK:1.1, subK:1.6, pri:7, color:'--hijaz'});
  R('filastin','Filasṭīn','فلسطين',[35.02,31.08],'--fil',{minK:1.3, pri:1});
  addLabel('filastin', [['al-Urdunn']], [35.55,32.9], {cls:'region small', color:'--urdunn', minK:2.2, pri:4});
  R('jazirah','Jazīrat al-ʿArab','جزيرة العرب',[47.6,21.3],'--jaz',{cls:'region big', pri:2});
  R('yemen','al-Yaman','اليمن',[48.4,16.4],'--yemen');
  R('upper','al-Jazīrah','الجزيرة',[41.2,36.1],'--upper');
  R('iraq','al-ʿIrāq · al-Sawād','العراق',[45.9,32.9],'--iraq');
  R('misr','Miṣr','مصر',[28.7,28.0],'--misr');
  R('najd','Najd','نجد',[43.6,24.7],'--najd');
  R('bahrayn','al-Baḥrayn','البحرين',[49.1,27.5],'--bahr',{cls:'region small', minK:0.9});
  R('tihamah','Tihāmah','تهامة',[41.65,17.6],'--tiham',{cls:'region small', minK:0.9});
  R('rum','Bilād al-Rūm','بلاد الروم',[32.0,39.4],'--rum');
  R('habashah','al-Ḥabashah','الحبشة',[39.4,12.4],'--hab');
  addLabel('misr', [['toward Barqah']], [20.55,30.7], {cls:'note', anchor:'start', minK:0, pri:8, color:'--misr'});
  AJNAD.forEach(j=>addLabel('ajnad', [[j.name.replace('Jund ','')]], j.at, {cls:'region small', color:j.col, minK:0.9, pri:4}));
  FIQH.forEach(f=>addLabel('hijazfiqh', [[f.n]], [f.c[0], f.c[1]-f.km/111.32-0.12], {cls:'note', minK:f.km>60?0.9:2.2, pri:12, color:'--hijaz'}));
  LAVA.forEach(l=>addLabel('lava', [[l.n]], l.at, {cls:'note', minK:1.8, pri:19}));
  muqLabels.forEach(m=>addLabel('muq', [[m[0]]], [m[1],m[2]], {cls:'note', minK:m[3], pri:6, color:'--muq'}));
  AHQAF.forEach(a=>addLabel('saba', [[a.n]], [a.c[0], a.c[1]-0.62], {cls:'note', minK:2.4, pri:9, color:'--yemen'}));
  addLabel('saba', [['al-Aḥqāf'],['three reports','sub']], [51.4,17.45], {cls:'note', minK:0.9, subK:1.6, pri:8, color:'--yemen'});
  addLabel('caliph', [['One outline around every best land'],['a thought experiment · my synthesis','sub']], [29.4,33.3], {cls:'caliphlbl', minK:0, subK:0, pri:3, color:'--ink', alts:[[16.5,33.2],[24.5,34.0]], strict:true});   /* Version 176: in the open sea west of the coast (it was drawn over the al-Aqṣā markers); start-anchored, so it runs east from here */
  addLabel('caliphxe', [['ʿIrāq al-ʿAjam'],['the old Jibāl','sub']], [50.2,34.15], {cls:'caliphlbl x', minK:0.9, subK:1.3, pri:4, color:'--xcal'});
  addLabel('caliphxe', [['Khūzistān'],['al-Ahwāz','sub']], [49.2,31.55], {cls:'caliphlbl x', minK:1.1, subK:1.6, pri:4, color:'--xcal'});
  /* the country name, your choice: drawn behind every other label and never pushed aside by them */
  { const dl = addLabel('caliphx', [['DĀR AL-AMĀN'],['دار الأمان','arl dar','1.3em']], DAR_AT, {cls:'darlbl', back:true, free:true, minK:0, maxK:2.6, subK:0, pri:-9});
    if(dl) dl.alts = [DAR_AT, [44.5, 23.5], [31.5, 21.0], [45.5, 19.5], [33.0, 17.5], [47.0, 26.5], [29.0, 22.5], [30.0, 17.0], [30.5, 12.5], [31.0, 9.0], [20.3, 26.4], [21.5, 25.0]]; }   /* Version 176: two more over the Libyan and Western deserts (in every version), for the phone's whole-region view */   /* all over lands every version holds */
  addLabel('caliphv2', [['V7'],['the Super Caliphate · history in the notes','sub']], [1.2,25.6], {cls:'caliphlbl x big', minK:0, subK:0, pri:3, color:'--xcal'});
  addLabel('caliphv2', [['V7'],['the author’s specification · not from the sources','sub']], [66.0,46.6], {cls:'caliphlbl x big', minK:0.45, subK:0.45, pri:3, color:'--xcal'});
  addLabel('caliphv2', [['V7'],['the author’s specification · not from the sources','sub']], [79.5,22.5], {cls:'caliphlbl x big', minK:0.45, subK:0.45, pri:3, color:'--xcal'});   /* Version 219: central India */
  addLabel('caliphv2', [['V7'],['the author’s specification · not from the sources','sub']], [27.6,12.6], {cls:'caliphlbl x', minK:0.7, subK:0.7, pri:4, color:'--xcal'});
  addLabel('caliphv3', [['V6'],['a wide complete outline · the author’s specification','sub']], [1.2,25.6], {cls:'caliphlbl x big', minK:0, subK:0, pri:3, color:'--xcal'});
  /* natural borders and internal lines (your design): names only where the base map has none */
  /* the ring: each name sits just outside it, on the side away from the territory */
  /* region labels are always centred, so a name that belongs to the left or right of its line is moved sideways by half its width (estimated) plus a gap */
  const NL = (layer, name, ll, minK, o) => { o = o || {}; const w = name.length * 6.6 / 2 + 6;
    return addLabel(layer, [[name]].concat(o.sub ? [[o.sub,'sub']] : []), ll, {cls:'natlbl', minK, subK:o.subK || minK + 0.7, pri:12, color:'--natb', dx: o.side === 'l' ? -w : o.side === 'r' ? w : 0, dy:o.dy || 0}); };
  NL('natbMain', 'Risnjak', [14.60,45.43], 2.2, {dy:-9});
  NL('natbMain', 'Kupa', [15.05,45.52], 1.4, {dy:-9});
  NL('natbMain', 'Sava', [17.7,45.18], 1.1, {dy:-9});
  NL('natbMain', 'Danube', [25.4,43.72], 0.9, {dy:-10});
  NL('natbMain', 'Chilia arm', [29.0,45.42], 2.0, {dy:-9});
  NL('natbMain', 'Greater Caucasus', [42.6,43.1], 0.9, {dy:-10, sub:'main crest', subK:1.6});
  NL('natbMain', 'Samur', [48.15,41.98], 2.0, {side:'l', dy:-6});
  NL('natbMain', 'Ustyurt escarpment', [55.2,41.9], 1.0, {dy:-10});
  NL('natbMain', 'Aral Sea', [58.75,44.05], 1.2, {dy:-9, sub:'historic shore', subK:1.6});
  NL('natbMain', 'Amu Darya', [62.6,40.6], 1.0, {side:'r', dy:-6});
  NL('natbMain', 'Panj', [70.3,38.0], 1.3, {dy:-9});
  NL('natbMain', 'Pamir knot', [74.8,37.25], 1.6, {side:'r', dy:-4});
  NL('natbMain', 'Karakoram', [76.0,36.25], 1.2, {side:'r', dy:-6, sub:'crest', subK:2.0});
  NL('natbMain', 'Indus basin rim', [79.7,34.2], 1.1, {side:'r', dy:0});
  NL('natbMain', 'Kailash', [82.05,31.05], 1.6, {side:'r', dy:0, sub:'round the Indus and Sutlej sources', subK:2.2});
  NL('natbMain', 'Sutlej–Ganges divide', [79.7,30.7], 1.4, {dy:12});
  NL('natbMain', 'Yamuna', [77.75,28.6], 1.3, {side:'r', dy:0});
  NL('natbMain', 'Chambal', [77.9,26.1], 1.3, {side:'r', dy:8});
  NL('natbMain', 'Malwa Plateau', [75.3,22.45], 1.6, {dy:12});
  NL('natbMain', 'Mahi', [73.9,23.0], 1.6, {side:'r', dy:8});
  NL('natbMain', 'Tana', [39.6,-1.25], 1.3, {side:'l', dy:6});
  NL('natbMain', 'Aberdares', [36.62,-0.30], 2.2, {side:'r', dy:10});
  NL('natbMain', 'Eburru', [36.24,-0.63], 2.2, {dy:12, sub:'Naivasha–Nakuru divide', subK:2.8});
  NL('natbMain', 'Mau', [35.86,-0.42], 1.9, {side:'l', dy:0});
  NL('natbMain', 'Nyando', [35.3,-0.15], 2.2, {dy:12});
  NL('natbMain', 'Winam Gulf', [34.55,-0.30], 2.4, {dy:14});
  NL('natbMain', 'Victoria Nile', [32.55,1.35], 1.5, {side:'l', dy:8, sub:'through Lake Kyoga', subK:2.2});
  NL('natbMain', 'L. Albert', [30.95,1.85], 1.7, {side:'l', dy:4});
  NL('natbMain', 'Nile–Congo divide', [28.9,4.3], 0.9, {side:'l', dy:6});
  NL('natbMain', 'Mbomou', [25.0,4.75], 1.1, {dy:12});
  NL('natbMain', 'Ubangi', [18.4,1.6], 1.2, {side:'r', dy:0});
  NL('natbMain', 'Sangha', [16.25,0.3], 1.3, {side:'l', dy:0});
  NL('natbMain', 'Mambéré', [15.62,4.5], 1.6, {side:'l', dy:0});
  NL('natbMain', 'Yadé Massif', [14.62,6.15], 1.6, {side:'l', dy:0});
  NL('natbMain', 'Adamawa', [13.9,6.95], 1.4, {dy:12});
  NL('natbMain', 'Benue', [10.0,7.95], 1.1, {dy:12});
  NL('natbMain', 'Niger', [5.4,9.4], 1.0, {side:'l', dy:8});
  NL('natbMain', 'Fouta Djallon', [-11.7,10.1], 1.3, {side:'l', dy:8});
  NL('natbMain', 'Senegal', [-14.2,16.35], 1.0, {dy:12});
  addLabel('intlAny', [['Taurus divide']], [33.4,37.55], {cls:'natlbl intl', minK:0.8, pri:12, color:'--natb'});
  addLabel('intlAny', [['the central axis']], [37.25,22.9], {cls:'natlbl intl', minK:0.9, pri:12, color:'--natb'});
  NAT_PTS.forEach(c=>addPoint(c.lay || 'natbAny', c.ll, {sym:c.sym, name:c.name || null, sub:c.sub || null, minK:c.k || 0, subK:(c.k || 0) + 0.6, maxK:c.maxK, anchor:c.a || 'r', cls:'small', pri:9, info:'natb', title:c.title, lcolor:'--natb', keep:true}));
  addLabel('links', [['al-Isrāʾ (rough sketch)']], [37.45,26.55], {cls:'note', minK:0.9, pri:9, color:'--miqat'});
  CITIES.forEach(c=>addPoint('cities', [c[2],c[3]], {name:c[0], sub:c[1], minK:c[4], subK:c[4]+0.9, anchor:c[5], pri:c[6]}));
  addPoint('ajnad', [37.00,35.99], {name:"Qinnasrīn", sub:"old capital", minK:1.6, anchor:"l", info:"jund_qinnasrin", pri:9});
  STATIONS.forEach(s=>addPoint(s[5], [s[1],s[2]], {name:s[0], minK:s[4], anchor:s[3], r:2.6, color: s[5]==='hajj'?'--hajj':'--trade', info: s[5]==='hajj'?'hajj':'quraysh', cls:'small', pri:14}));
  ALL_LIMITS.forEach(l=>{ const lay = l.layer==='hijazfiqh' ? 'hijazfiqh' : (l.layer==='misr' ? 'misr' : 'limits');
    const pt = addPoint(lay, l.ll, {sym:'badge', letter:l.id, info:'lim_'+l.id, minK: l.layer==='filastin' ? 2.2 : 0.9, title:`${l.id} · ${l.n}`, keep:true});
    pt.badge = true; pt.tiers = lay==='limits' ? ((INFO['lim_'+l.id]||{}).src||[]) : null; });
  MIQATS.forEach(m=>addPoint('miqat', m.ll, {sym:'ring', color:'--miqat', name:m.n, sub:m.s, minK:2.6, subK:5, anchor:m.a, info:'miqat', pri:5, title:m.n, keep:true}));
  SITES.forEach(s=>addPoint(s.id==='tayyi'?'sham':'sites', s.ll, {sym:'square', color:'--site', name:s.n, sub:s.s, minK:s.k, subK:s.k*1.4, anchor:s.a, info:s.info||('site_'+s.id), pri:6, cls:'small', title:s.n}));
  addPoint('aqsa', QIBLA.aqsa, {sym:'diamond', color:'--sacred', name:"al-Masjid al-Aqṣā", sub:"Bayt al-Maqdis · Jerusalem", minK:0, subK:1.4, anchor:'r', info:'aqsa', title:'al-Masjid al-Aqṣā', pri:0, keep:true});
  /* Arwād (Aradus), off Ṭarṭūs: taken in ʿUthmān's time (Version 51, Nawaz's brief); too small for the base map, so it is marked, not shaded */
  addPoint('caliphxArwad', [35.858,34.856], {name:'Arwād', sub:'island · in the outline', minK:1.6, subK:2.8, anchor:'l', info:'caliphx', r:2.6, color:'--xcal', cls:'small', pri:8, title:'Arwād (Aradus): an island too small for the base map, inside the outline'});
  addPoint('caliphx', QIBLA.aqsa, {sym:'capital', info:'capital', title:'al-Quds (Jerusalem): capital of Dār al-Amān · the author’s choice, not from the sources', minK:0, keep:true});
  addPoint('haram', QIBLA.makkah, {sym:'diamond', color:'--haram', minK:0, info:'makkah', title:'al-Masjid al-Ḥarām', keep:true});
  addPoint('haram', QIBLA.madinah, {sym:'diamond', color:'--haram', minK:0, info:'madinah', title:'al-Masjid al-Nabawī', keep:true});
  HARAM_PTS.forEach(h=>addPoint('haram', h.ll, {name:h.n, sub:h.s, minK:h.k, subK:h.k*1.4, anchor:h.a, info:h.info, r:3, hollow:!!h.out, color:'--haram', cls:'small', pri:3}));
  addPoint('tuwa', [33.975,28.539], {sym:'tri', color:'--sacred', name:"Ṭuwā · Ṭūr Sīnāʾ", sub:"traditional site, uncertain", minK:0, subK:1.4, anchor:'r', info:'tuwa', title:'Traditional site of Mount Sinai', pri:2, keep:true});
  addPoint('saba', MARIB, {sym:'square', color:'--yemen', name:"Maʾrib", sub:"Sabaʾ · the dam", minK:0.9, subK:1.6, anchor:'r', info:'saba', title:'Maʾrib (Sabaʾ)', pri:6, cls:'small'});
  addPoint('habashah', AKSUM, {sym:'square', color:'--hab', name:"Aksūm", sub:"heart of the Najāshī's kingdom", minK:0, subK:1.4, anchor:'r', info:'habashah', title:'Aksūm (marker for al-Ḥabashah)', pri:6, cls:'small'});
  addPoint('bahrayn', [49.64,25.45], {sym:'square', color:'--bahr', name:"Jawāthā", sub:"by tradition, near al-Aḥsāʾ", minK:1.6, subK:2.4, anchor:'l', info:'bahrayn', title:'Jawāthā (approximate)', pri:7, cls:'small'});
  ESCHAT.forEach(e=>addPoint('eschat', e.ll, {sym:'ring', color:'--eschat', name:e.id==='qustantiniyyah'?null:e.n, sub:e.s, minK:e.k, subK:e.k*1.3, anchor:e.a, info:'eg_'+(e.id==='qustantiniyyah'?'qust':e.id), title:e.n, pri:6, cls:'small', keep:true}));
  STATUS.forEach(addStatusBadge);
  /* qibla arrows at Madinah */
  const qg = ovTop.append('g').attr('data-layer','links').attr('class','qg');
  const mkA = cls => ({line:qg.append('line').attr('class','qline '+cls), head:qg.append('path').attr('class','qhead '+cls), text:qg.append('text').attr('class','lbl small qtxt')});
  qa1 = mkA('first'); qa2 = mkA('now');
  qa1.text.text('first qibla: Bayt al-Maqdis'); qa2.text.text('qibla: the Kaʿbah');
  measure();
}
/* Label sizes. Every write is done first and then every read, so the browser lays the page out once per pass, not
   once per label; a label inside a hidden layer reports 0 and keeps its earlier size. Each label needs its box with its
   second line ("full") and without it ("main"); a place label needs both for text on either side of its dot. Region
   labels and place labels are measured in the same passes, and the left-hand boxes are mirrored, so there are two layouts, not six. */
const bx = r => ({x:r.x, y:r.y, w:r.width, h:r.height});
function measure(){
  sbs.forEach(b=>{ b.tx.style('display', null).attr('text-anchor','start'); });
  sbs.forEach(b=>{ const w = b.tx.node().getBBox().width; if(w > 0 || b.tw == null) b.tw = w; });
  lbls.forEach(l=>{ l.t.style('display', null).attr('transform', null); if(!l.point && !l.rot) l.t.attr('text-anchor', null); });
  const pts = lbls.filter(l=>l.point);
  const pass = (arr, anchor, subsShown, part)=>{
    arr.forEach(l=>{ if(anchor && l.point) l.t.attr('text-anchor', anchor); l.subs.forEach(s=>s.style('display', subsShown ? null : 'none')); });
    arr.forEach(l=>{ const key = !l.point ? 'bbC' : anchor === 'end' ? 'bbL' : 'bbR';
      const r = l.t.node().getBBox(); const o = l[key] || (l[key] = {full:null, main:null}); if(r.width > 0 || !o[part]) o[part] = bx(r); });
  };
  pass(lbls, 'start', true, 'full'); pass(lbls, 'start', false, 'main');   /* place labels to the right of the dot, and region labels */
  /* place labels to the left: every line of a label starts at x = 0, so with the text anchored at its end each box is the
     start-anchored box mirrored about x = 0 (Version 98: this saves two of the four layout passes when the page opens) */
  const mir = r => r && {x:-(r.x + r.w), y:r.y, w:r.w, h:r.h};
  pts.forEach(l=>{ const R = l.bbR; if(R) l.bbL = {full:mir(R.full) || (l.bbL && l.bbL.full) || null, main:mir(R.main) || (l.bbL && l.bbL.main) || null}; l.side = null; });
}

/* ---------------- layers, zoom, update ---------------- */
function applyLayers(){
  const natMode = inNat();   /* the natural-borders version: its line, chokepoints and passes always go with it, and the internal lines until you switch them off */
  if((layerOn.natb || layerOn.intl || natMode) && !NAT_BUILT) buildNat();
  layerOn.caliphnat = natMode; layerOn.caliphnp = !!layerOn.caliphx && XV === 'natp'; layerOn.caliphnatx = natMode; layerOn.natbAny = !!layerOn.natb || natMode; layerOn.intlAny = natMode ? !INTL_OFF : !!layerOn.intl;
  layerOn.caliphxe = !!layerOn.caliphx; layerOn.caliphxc = !!layerOn.caliphx && XV === 'full'; layerOn.caliphv2 = !!layerOn.caliphx && XV === 'v2'; layerOn.caliphv3 = !!layerOn.caliphx && XV === 'v3'; layerOn.caliphxArwad = !!layerOn.caliphx && !['full','fulln','nat','natp'].includes(XV); layerOn.caliphv2h = false;
  /* natural borders: the Libya variant goes with Complete V2, the far-east line with the Greater Caliphate */
  layerOn.natbMain = layerOn.natbAny;
  document.querySelectorAll('[data-lyt]').forEach(b=>b.setAttribute('aria-pressed', b.dataset.lyt === 'natb' ? layerOn.natbAny : b.dataset.lyt === 'intl' ? layerOn.intlAny : !!layerOn[b.dataset.lyt]));
  document.querySelectorAll('.xtoggle.onmap').forEach(el=>{ el.hidden = !layerOn.caliphx; });
  const cleanOn = CLEAN && !!layerOn.caliphx;   /* the class hides the key, scale, compass, coordinates and degree labels; render() hides the outline's captions and markers */
  wrapEl.classList.toggle('clean', cleanOn);
  document.querySelectorAll('[data-clean]').forEach(b=>b.setAttribute('aria-pressed', cleanOn));
  let anyLg = false; document.querySelectorAll('[data-lg]').forEach(el=>{ const on = !!layerOn[el.dataset.lg]; el.hidden = !on; anyLg = anyLg || on; });
  const hrl = document.querySelector('[data-lgany]'); if(hrl) hrl.hidden = !anyLg;
  if(typeof measureChrome === 'function' && wrapEl) measureChrome();
  svg.selectAll('[data-layer]').each(function(){ const id=this.getAttribute('data-layer'); if(id in layerOn) this.style.display = layerOn[id] ? null : 'none'; });
  update();
}
let T = d3.zoomIdentity, W = 800, H = 600, coverK = 0.6;
/* Smooth interaction: while a gesture runs, the whole map moves as one GPU layer (a CSS transform on the <svg>);
   the vector map, labels and patterns are redrawn only when the gesture pauses, or when the layer has been
   stretched too far to stay sharp. R is the transform the vector map was last drawn at. */
let R = d3.zoomIdentity, rafZ = 0, idleZ = 0, lastCommit = 0, lastZ = 0, dueZ = 0, lateZ = false, LIGHT = false, redrawMs = 30, OX = 200, OY = 150;   /* OX, OY: margin of map drawn beyond each edge of the view */
const svgEl = document.getElementById('mapmove'), wrapSel = d3.select(wrapEl);   /* svgEl: the HTML wrapper that moves; moving the <svg> itself forces a full repaint */
const CHROME_SEL = '.mapctl,.minilegend,.scale,.coords,.xtoggle,button,a,input,select,summary,label';
const zfilter = e => (!e.ctrlKey || e.type === 'wheel') && !e.button && !(e.target && e.target.closest && e.target.closest(CHROME_SEL));
/* Version 119: while the map moves, its shapes do not answer the pointer: the browser otherwise tests the finger or mouse against
   every clickable shape (the countries' 120,000-point click areas, the outline) after each frame, about a quarter of the work */
let MOVING = false;
const setMoving = on => { if(on !== MOVING){ MOVING = on; wrapEl.classList.toggle('moving', on); } };
const zoom = d3.zoom().scaleExtent([0.2, 3000]).filter(zfilter).on('zoom', e=>{ T = e.transform; lastZ = performance.now(); setMoving(true); if(!rafZ) rafZ = requestAnimationFrame(frameZ); });
/* The map is redrawn when the gesture has really stopped. The timer only asks "has it been quiet for a moment?": a
   late timer (the page was busy drawing) must not fire in the middle of a gesture and start another slow redraw, so
   when it runs late, or the browser says input is waiting, it looks once more shortly. A mouse wheel sends a step
   every 100-250 ms, so the pause is long enough to join the steps into one gesture and redraw once at the end. */
const IDLE_MS = 260;
function armIdle(ms){ dueZ = performance.now() + ms; idleZ = setTimeout(idleCheck, ms); }
function idleCheck(){
  idleZ = 0; const now = performance.now(), quiet = now - lastZ;
  if(quiet < IDLE_MS - 20){ armIdle(IDLE_MS - quiet); return; }
  const pending = navigator.scheduling && navigator.scheduling.isInputPending && navigator.scheduling.isInputPending();
  if(!lateZ && (now - dueZ > 60 || pending)){ lateZ = true; armIdle(100); return; }
  lateZ = false; update();
}
function frameZ(){
  rafZ = 0; lateZ = false;
  const s = T.k / R.k, tx = T.x - s*R.x, ty = T.y - s*R.y;
  svgEl.style.transform = (s === 1 && tx === 0 && ty === 0) ? '' : `translate3d(${tx.toFixed(2)}px,${ty.toFixed(2)}px,0) scale(${s.toFixed(5)})`;
  if(!idleZ) armIdle(IDLE_MS);
  /* mid-gesture redraws are rare: only when the drawn margin no longer covers the view, or the layer is
     stretched too far to stay sharp. How rare adapts to the device: redrawMs is how long the last redraw took to
     reach the screen. A slow device waits longer, stretches the layer further, and draws a light version (without
     the engraved water lines and border halos) until the gesture ends. */
  const gap = Math.max(tx - OX*s, W - (tx + (W+OX)*s), ty - OY*s, H - (ty + (H+OY)*s));   /* px of view the drawn margin no longer covers */
  const now = performance.now(), slow = redrawMs > 120, hold = Math.max(650, redrawMs*5);
  if(((gap > 36 || s > (slow ? 4 : 2.6) || s < (slow ? 0.25 : 0.38)) && now - lastCommit > hold) || (gap > 160 && now - lastCommit > Math.max(300, redrawMs*2))) update(true);   /* Version 228: a redraw in the middle of a gesture is always the light one */
}
let chrome = [];
function measureChrome(){
  const r = wrapEl.getBoundingClientRect(); chrome = [];
  [...wrapEl.querySelectorAll('.mapctl,.minilegend,.scale,.coords,.xtoggle:not([hidden])'), ...document.querySelectorAll('.atlas.full .mapbars .find, .atlas.full .mapbars .viewbar:not(.tierbar)')].forEach(el=>{ const b = el.getBoundingClientRect(); if(b.width && b.height) chrome.push({x:b.left-r.left-4, y:b.top-r.top-4, w:b.width+8, h:b.height+8}); });
}
function size(){ const r = wrapEl.getBoundingClientRect(); W = Math.max(200, r.width); H = Math.max(200, r.height); zoom.extent([[0,0],[W,H]]);
  /* Version 65: the map is the whole Earth and always fills the screen, as in a maps app: the smallest zoom is the one at which
     the world just covers the view (on a tall phone that shows about half the world's width; pan sideways for the rest) */
  const s0 = SHEET_NW(), s1 = SHEET_SE(), sw = s1[0]-s0[0], sh = s1[1]-s0[1];
  coverK = Math.max(W/sw, H/sh);
  zoom.translateExtent([s0, s1]).scaleExtent([coverK, 3000]);
  /* the moving layer is drawn a fifth of the view larger on every side (a quarter before Version 228; each redraw now paints about 13% less), so panning seldom shows a blank edge */
  OX = Math.round(W*0.2); OY = Math.round(H*0.2);
  Object.assign(svgEl.style, {inset:'auto', left:-OX+'px', top:-OY+'px', width:(W+2*OX)+'px', height:(H+2*OY)+'px', transformOrigin:`${OX}px ${OY}px`});
  svg.attr('width', W+2*OX).attr('height', H+2*OY); ov.attr('transform', `translate(${OX},${OY})`);
  measureChrome(); }
wrapSel.call(zoom).on('dblclick.zoom', null);
/* smooth wheel zoom: each wheel step sets a target and the map eases toward it, anchored at the pointer */
let wheelTarget = null, wheelP = null, wheelRaf = 0;
wrapSel.on('wheel.zoom', null).on('wheel.smooth', ev => {
  if(!zfilter(ev)) return;
  ev.preventDefault();
  const step = -ev.deltaY * (ev.deltaMode === 1 ? 0.05 : ev.deltaMode ? 1 : 0.002) * (ev.ctrlKey ? 8 : 1);
  const [k0, k1] = zoom.scaleExtent();
  wheelTarget = Math.max(k0, Math.min(k1, (wheelTarget == null ? T.k : wheelTarget) * Math.pow(2, step)));
  wheelP = d3.pointer(ev, wrapEl);
  if(!wheelRaf) wheelRaf = requestAnimationFrame(stepWheel);
}, {passive:false});
function stepWheel(){
  wheelRaf = 0; if(wheelTarget == null) return;
  const lk = Math.log(T.k), lt = Math.log(wheelTarget), done = Math.abs(lt - lk) < 0.003;
  wrapSel.call(zoom.scaleTo, done ? wheelTarget : Math.exp(lk + (lt - lk) * (reduced ? 1 : 0.32)), wheelP);
  if(done || reduced){ wheelTarget = null; return; }
  wheelRaf = requestAnimationFrame(stepWheel);
}
/* keyboard: arrows pan, + and - zoom, 0 shows the whole region */
wrapEl.addEventListener('keydown', ev => {
  if(ev.target.closest && ev.target.closest('input,select,textarea,button,summary,a')) return;
  const d = ev.shiftKey ? 240 : 110, t = wrapSel.transition().duration(reduced ? 0 : 220);
  const map = {ArrowLeft:[d,0], ArrowRight:[-d,0], ArrowUp:[0,d], ArrowDown:[0,-d]};
  if(map[ev.key]){ ev.preventDefault(); t.call(zoom.translateBy, map[ev.key][0]/T.k, map[ev.key][1]/T.k); }
  else if(ev.key === '+' || ev.key === '='){ ev.preventDefault(); t.call(zoom.scaleBy, 1.6); }
  else if(ev.key === '-' || ev.key === '_'){ ev.preventDefault(); t.call(zoom.scaleBy, 1/1.6); }
  else if(ev.key === '0'){ ev.preventDefault(); goFocus(0); }
});
let raf = 0;
function schedule(){ if(!raf) raf = requestAnimationFrame(()=>{ raf = 0; update(); }); }
let timing = false;
/* draw the vector map at the current transform and drop the temporary GPU transform; light: leave out the costly decorations (mid-gesture only) */
function update(light){ clearTimeout(idleZ); idleZ = 0; R = T; LIGHT = !!light; world.attr('transform', `translate(${OX},${OY}) ${T}`); svgEl.style.transform = ''; const t0 = lastCommit = performance.now(); render();
  /* time this redraw until it reaches the screen (two frames on), to learn how heavy it is on this device */
  if(!timing){ timing = true; requestAnimationFrame(()=>requestAnimationFrame(()=>{ timing = false; redrawMs = 0.6*redrawMs + 0.4*Math.min(2000, performance.now() - t0); })); }
  if(light) armIdle(IDLE_MS);   /* a light redraw is only for the gesture: the full one follows when it ends */
  else setMoving(false);   /* back on with the full redraw (in the same style pass; a separate one later costs more) */
}
const sandPat = d3.select('#sand'), lavaPat = d3.select('#lava'), hSham = d3.select('#h-sham'), hHijaz = d3.select('#h-hijaz'), hFil = d3.select('#h-fil'), hMisr = d3.select('#h-misr'), hDisp = d3.select('#h-disp');
const GSTEPS = [0.0001,0.0002,0.0005,0.001,0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,20,30];
function updateGrat(k){
  if(!layerOn.graticule){ ovGrat.selectAll('text').remove(); ovGrat.selectAll('path.gtick').attr('d',''); return []; }
  const tl = T.invert([-OX,-OY]), br = T.invert([W+OX,H+OY]);   /* lines cover the drawn margin too */
  const a0 = proj.invert(tl), b0 = proj.invert(br); if(!a0||!b0) return [];
  const c = proj.invert(T.invert([W/2,H/2])); const lat0 = Math.max(-80, Math.min(80, c[1]));
  const pa = P([c[0], lat0]), pb = P([c[0]+1, lat0]); const pxDeg = (pb[0]-pa[0])*k;
  let step = 30; for(const s of GSTEPS){ if(s*pxDeg >= 96){ step = s; break; } }
  const lonMin = a0[0], lonMax = b0[0], latMax = a0[1], latMin = b0[1];
  const i0 = Math.ceil(lonMin/step), i1 = Math.floor(lonMax/step), j0 = Math.ceil(latMin/step), j1 = Math.floor(latMax/step);
  const dig = step>=1 ? 0 : Math.min(4, Math.ceil(-Math.log10(step)-1e-9));
  let d = ''; const labs = [];
  if(i1-i0 < 80) for(let i=i0;i<=i1;i++){ if(i*step < SHEET.w || i*step > SHEET.e) continue; const lon=i*step, x=P([lon,0])[0]; d += `M${x.toFixed(4)},${(tl[1]-4).toFixed(2)}L${x.toFixed(4)},${(br[1]+4).toFixed(2)}`; labs.push({k:'x'+i, x:T.applyX(x), y:H-23, t:Math.abs(lon).toFixed(dig)+'°'+(lon<0?'W':'E'), a:'middle'}); }
  if(j1-j0 < 80) for(let j=j0;j<=j1;j++){ if(j*step < SHEET.s || j*step > SHEET.n) continue; const lat=j*step, y=P([0,lat])[1]; d += `M${(tl[0]-4).toFixed(2)},${y.toFixed(4)}L${(br[0]+4).toFixed(2)},${y.toFixed(4)}`; labs.push({k:'y'+j, x:23, y:T.applyY(y)+3.5, t:Math.abs(lat).toFixed(dig)+'°'+(lat<0?'S':'N'), a:'start'}); }
  gratPath.attr('d', d);
  /* degree ticks on the inner neatline (6px in from the edge) */
  let tk = '';
  labs.forEach(l=>{ if(l.a==='middle'){ if(l.x>8 && l.x<W-8) tk += `M${l.x.toFixed(1)},14v6M${l.x.toFixed(1)},${H-14}v-6`; }
    else { const y = l.y-3.5; if(y>16 && y<H-16) tk += `M14,${y.toFixed(1)}h6M${W-14},${y.toFixed(1)}h-6`; } });
  let tp = ovGrat.select('path.gtick'); if(tp.empty()) tp = ovGrat.insert('path',':first-child').attr('class','gtick');
  tp.attr('d', tk);
  const ok = labs.filter(l=>{ const b = l.a==='middle' ? {x:l.x-22,y:l.y-12,w:44,h:16} : {x:l.x-4,y:l.y-12,w:44,h:16}; if(l.a==='middle' && (l.x<40||l.x>W-40)) return false; if(l.a==='start' && (l.y<24||l.y>H-30)) return false; return !chrome.some(c=>b.x<c.x+c.w&&b.x+b.w>c.x&&b.y<c.y+c.h&&b.y+b.h>c.y); });
  ovGrat.selectAll('text.glbl').data(ok, d=>d.k).join('text').attr('class','glbl').attr('x',d=>d.x).attr('y',d=>d.y).attr('text-anchor',d=>d.a).text(d=>d.t);
  /* Version 176: their boxes, so names keep clear of the degree figures along the edges (not in the clean map, which hides them) */
  return wrapEl.classList.contains('clean') ? [] : ok.map(l=> l.a==='middle' ? {x:l.x-18, y:l.y-10, w:36, h:13} : {x:l.x-2, y:l.y-10, w:34, h:13});
}
/* Version 176: the outline's line (and the dotted line of the best lands) in screen cells of OGS px, made once per redraw from the
   projected points (about 50,000 at most, a millisecond or two); labels then prefer a spot that does not cross it. The full lines of a
   version are projected in a quiet moment the first time, not while the page opens; until then labels are placed as before. */
const OGS = 6; let OG = null, OGW = 0, OGH = 0, ogWait = false;
function outlineGrid(){
  OG = null;
  if(!CX.lines) return;
  const sets = [];
  if(layerOn.caliphx){ const a = CX.linesReady(); if(a) sets.push(a); else if(!ogWait){ ogWait = true; whenIdle(()=>{ CX.lines(); ogWait = false; if(!MOVING) update(); }); } }
  if(layerOn.caliph && CX.blines) sets.push(CX.blines());
  if(!sets.length) return;
  OGW = Math.ceil(W/OGS) + 1; OGH = Math.ceil(H/OGS) + 1; const g = OG = new Uint8Array(OGW*OGH);
  const k = T.k, tx = T.x, ty = T.y, st = OGS*0.7;
  for(const lines of sets) for(const a of lines){
    let x0 = a[0]*k + tx, y0 = a[1]*k + ty;
    for(let i = 2; i < a.length; i += 2){
      const x1 = a[i]*k + tx, y1 = a[i+1]*k + ty;
      if(!((x0 < 0 && x1 < 0) || (x0 >= W && x1 >= W) || (y0 < 0 && y1 < 0) || (y0 >= H && y1 >= H))){
        const n = Math.min(3000, Math.ceil(Math.max(Math.abs(x1-x0), Math.abs(y1-y0)) / st));
        for(let j = 0; j <= n; j++){ const x = x0 + (x1-x0)*j/n, y = y0 + (y1-y0)*j/n; if(x >= 0 && x < W && y >= 0 && y < H) g[((y/OGS)|0)*OGW + ((x/OGS)|0)] = 1; }
      }
      x0 = x1; y0 = y1;
    }
  }
}
/* how many cells of the line a box covers */
function ogHit(b){
  if(!OG) return 0; let n = 0;
  const c0 = Math.max(0, Math.floor(b.x/OGS)), c1 = Math.min(OGW-1, Math.floor((b.x+b.w)/OGS)), r0 = Math.max(0, Math.floor(b.y/OGS)), r1 = Math.min(OGH-1, Math.floor((b.y+b.h)/OGS));
  for(let r = r0; r <= r1; r++) for(let c = c0; c <= c1; c++) n += OG[r*OGW + c];
  return n;
}
/* a label laid along a sea: its box is split into squares along its length, each with its own upright box */
function rotBoxes(x, y, bb, deg){
  const a = deg*Math.PI/180, co = Math.cos(a), si = Math.sin(a), m = Math.max(1, Math.ceil(bb.w / bb.h)), pw = bb.w/m, ph = bb.h;
  const hw = (pw*Math.abs(co) + ph*Math.abs(si))/2, hh = (pw*Math.abs(si) + ph*Math.abs(co))/2, out = [];
  for(let i = 0; i < m; i++){ const lx = bb.x + (i+0.5)*pw, ly = bb.y + bb.h/2; const cx = x + lx*co - ly*si, cy = y + lx*si + ly*co; out.push({x:cx-hw, y:cy-hh, w:2*hw, h:2*hh}); }
  return out;
}
function setArrow(A, mx, my, tx, ty, r0, r1){
  const vx=tx-mx, vy=ty-my, L=Math.hypot(vx,vy)||1, ux=vx/L, uy=vy/L;
  const x0=mx+ux*r0, y0=my+uy*r0, x1=mx+ux*r1, y1=my+uy*r1, nx=-uy, ny=ux;
  A.line.attr('x1',x0).attr('y1',y0).attr('x2',x1-ux*7).attr('y2',y1-uy*7);
  A.head.attr('d', `M${x1},${y1}L${x1-ux*10+nx*5},${y1-uy*10+ny*5}L${x1-ux*10-nx*5},${y1-uy*10-ny*5}Z`);
  const right = ux >= 0;
  A.text.attr('x', x1+ux*8+(right?2:-2)).attr('y', y1+uy*8+4).attr('text-anchor', right?'start':'end');
}
/* a wide version (V2, V5, V6) seen whole is about the territory: the discs, cities and classical names wait until the reader zooms in */
const QUIET_LBL = new Set(['base','caliph','caliphx','caliphv2','caliphv3','caliphnat','caliphnp','caliphnatx','caliphxe','caliphxc','natb','natbAny','natbMain','intl','intlAny']), QUIET_PTS = new Set(['haram','aqsa','caliphx','caliphxArwad','natb','natbAny']);
/* "Clean map": no numbered discs (with their leader lines and names), no dots, diamonds, stars or other point markers, no names of places, no qibla arrows, and none of the outline's own captions. Only the map, the outline and the names of regions, countries and seas stay. */
const CLEAN_LBL = new Set(['caliph','caliphx','caliphv2','caliphv3','caliphnat','caliphnp','caliphnatx','caliphxe','caliphxc','natb','natbAny','natbMain','intl','intlAny']);
function render(){
  const k = T.k;
  const clean = CLEAN && !!layerOn.caliphx;
  const quiet = (XV === 'v2' || XV === 'v3' || XV === 'me2' || XV === 'me9' || XV === 'af' || XV === 'eu' || XV === 'nat' || XV === 'natp') && !!layerOn.caliphx && k < 0.9;
  const sc = `scale(${(1/k).toFixed(5)})`;
  sandPat.attr('patternTransform', sc); lavaPat.attr('patternTransform', sc);
  hSham.attr('patternTransform', `${sc} rotate(45)`); hHijaz.attr('patternTransform', `${sc} rotate(-45)`); hFil.attr('patternTransform', `${sc} rotate(30)`); hMisr.attr('patternTransform', `${sc} rotate(90)`); hDisp.attr('patternTransform', `${sc} rotate(-30)`);
  /* Version 176: the relief picture is enlarged more and more as you zoom in, and its soft light-and-shade blobs grew loud (white "snow"
     over the Caucasus, the Zagros and the Pamirs); it now fades gently once each of its pixels covers more than about one and a half on screen */
  { const up = k * RELIEF_W / RELIEF_PX, f = k > 30 ? 0.25 : up <= 1.25 ? 1 : Math.max(0.45, 1 - 0.32*Math.log2(up/1.25));
    reliefImg.style('opacity', f < 1 ? `calc(var(--relief-op) * ${f.toFixed(2)})` : null); }
  /* Where the shaded relief is drawn at 56-100% of its own size the browser's smooth shrinking (it builds shrunken copies each redraw) costs
     about as much as everything else on the map together; plain sampling there looks the same to the eye and costs a third as much */
  reliefImg.style('image-rendering', (k * RELIEF_W / RELIEF_PX >= 0.56 && k * RELIEF_W / RELIEF_PX < 1) ? 'pixelated' : null);
  { const up = k * RELIEFW_W / RELIEFW_PX, f = k > 30 ? 0.25 : up <= 1.25 ? 1 : Math.max(0.45, 1 - 0.32*Math.log2(up/1.25));
    reliefWorld.style('opacity', f < 1 ? `calc(var(--relief-op) * ${f.toFixed(2)})` : null)
      .style('image-rendering', (up >= 0.56 && up < 1) ? 'pixelated' : null); }
  if(VIEW_SET){ const lv = k < 0.25 ? 0 : k < 0.6 ? 1 : k < 1.5 ? 2 : 3; if(lv !== landLv){ landLv = lv; landMP.attr('d', landLOD(lv)); } }   /* coarser land outline while zoomed out */
  if(CX.clip){ const key = CX.lk2(); if(key !== CX.lk){ CX.lk = key; const dd = CX.lod(XK(), cxLv()); CX.clip.attr('d', dd); CX.wash.attr('d', dd); if(CX.dim) CX.dim.attr('d', CX.DIM_SHEET + dd); } }   /* the outline's clip and wash follow its level of detail */
  gWL.style('display', k < 6 && !LIGHT ? null : 'none');   /* the simplified coast would drift from the real one close in */
  BORD.els[0].style('display', LIGHT ? 'none' : null);   /* the border halo goes too in a light redraw */
  lakeRings.style('display', LIGHT ? 'none' : null); engrRect.style('display', LIGHT ? 'none' : null);   /* and the lake rings and the engraved sea (Version 228) */
  /* borders and outlines: the whole line when far out, only the stretch near the view close in */
  { const close = k >= 0.9, vx0 = T.invertX(-OX), vx1 = T.invertX(W+OX), vy0 = T.invertY(-OY), vy1 = T.invertY(H+OY);
    CLIPS.forEach(c=>{ const key = c.key();
      if(!close){ if(c.state !== 'full' || c.k0 !== key){ c.state = 'full'; c.k0 = key; const d = c.full(); c.els.forEach(el=>el.attr('d', d)); } return; }
      const b = c.box;
      if(c.state === 'clip' && c.k0 === key && b && vx0 >= b[0] && vx1 <= b[2] && vy0 >= b[1] && vy1 <= b[3]) return;
      const mx = (vx1 - vx0)*0.5, my = (vy1 - vy0)*0.5;
      c.box = [vx0-mx, vy0-my, vx1+mx, vy1+my]; c.state = 'clip'; c.k0 = key;
      const d = clipD(c.lines(), c.box[0], c.box[1], c.box[2], c.box[3]); c.els.forEach(el=>el.attr('d', d));
    }); }
  /* very close in, every other long path is cut to the area near the view too (see parseD in part B) */
  { const deep = k >= 20;
    if(!DEEP.els){ DEEP.els = []; const skip = new Set(); CLIPS.forEach(c=>c.els.forEach(el=>skip.add(el.node())));
      const ok = el => { if(skip.has(el) || el.classList.contains('grat')) return false; for(let a = el.parentNode; a && a !== svgEl; a = a.parentNode){ if(a.getAttribute && a.getAttribute('transform') && a !== world.node()) return false; } return !el.getAttribute('transform'); };
      world.node().querySelectorAll('path').forEach(el=>{ if(ok(el)) DEEP.els.push(el); });
      sdefs.node().querySelectorAll('clipPath path').forEach(el=>DEEP.els.push(el));
      const lp = document.getElementById('landMP'); if(lp) DEEP.els.push(lp); }
    const vx0 = T.invertX(-OX), vx1 = T.invertX(W+OX), vy0 = T.invertY(-OY), vy1 = T.invertY(H+OY);
    const b = DEEP.box, inBox = b && vx0 >= b[0] && vx1 <= b[2] && vy0 >= b[1] && vy1 <= b[3];
    if(deep && !(DEEP.on && inBox)){
      const mx = (vx1 - vx0)*0.75, my = (vy1 - vy0)*0.75; DEEP.box = [vx0-mx, vy0-my, vx1+mx, vy1+my]; DEEP.on = true;
      for(const el of DEEP.els){ const cur = el.getAttribute('d');
        if(cur !== el.__dc){ el.__d0 = cur; el.__rings = undefined; }
        if(el.__rings === undefined) el.__rings = parseD(el.__d0);
        if(!el.__rings) continue;
        const d = clipPathD(el.__rings, DEEP.box[0], DEEP.box[1], DEEP.box[2], DEEP.box[3]); el.__dc = d; el.setAttribute('d', d); }
    } else if(!deep && DEEP.on){
      DEEP.on = false; DEEP.box = null;
      for(const el of DEEP.els){ if(el.__dc != null && el.getAttribute('d') === el.__dc) el.setAttribute('d', el.__d0); el.__dc = undefined; }
    }
  }
  /* very close in, let the ground show through the region fills */
  gFill.style('opacity', k < 20 ? null : Math.max(0.35, 1 - 0.65*Math.log10(k/20)).toFixed(2));
  const gratB = updateGrat(k);
  outlineGrid();
  const placed = [];
  const hit = (b) => { for(const p of placed){ if(b.x < p.x+p.w && b.x+b.w > p.x && b.y < p.y+p.h && b.y+b.h > p.y) return true; } return false; };
  chrome.forEach(c=>placed.push(c)); gratB.forEach(c=>placed.push(c));
  const chromeHit = b => chrome.some(c=> b.x < c.x+c.w && b.x+b.w > c.x && b.y < c.y+c.h && b.y+b.h > c.y);
  /* 1. status discs, in priority order */
  const bc = [];
  sbs.forEach(b=>{ b.show = false; });
  const order0 = sbs.filter(b=>!quiet && !clean && layerOn[b.layer] && k >= b.minK && (TIER !== 'rev' || b.level === 'rev')).sort((a,b)=>a.pri-b.pri);
  /* Version 121: zoomed far out the discs are drawn smaller (their offsets too), so they no longer cover the lands they mark */
  const ds = k < 0.3 ? 0.62 : k < 0.9 ? 0.8 : 1;
  for(const b of order0){
    const sx = T.applyX(b.v[0]), sy = T.applyY(b.v[1]), bx = sx + b.off[0]*ds, by = sy + b.off[1]*ds, r = 15*ds;
    if(bx < 14 || bx > W-14 || by < 14 || by > H-14) continue;
    const box = {x:bx-r, y:by-r, w:2*r, h:2*r};
    if(chromeHit(box)) continue;
    if(bc.some(c=>Math.hypot(c.x-bx, c.y-by) < 31*ds)) continue;
    bc.push({x:bx, y:by}); placed.push(box); b.show = true; b.pos = [sx,sy,bx,by];
  }
  sbs.forEach(b=>{
    b.g.style('display', b.show ? null : 'none');
    const far = b.show && b.far;
    b.lead.style('display', far ? null : 'none'); b.dot.style('display', far ? null : 'none');
    if(b.show){ const [sx,sy,bx,by] = b.pos; b.g.attr('transform', `translate(${bx.toFixed(1)},${by.toFixed(1)})${ds < 1 ? ` scale(${ds})` : ''}`);
      if(far){ b.lead.attr('d', `M${sx.toFixed(1)},${sy.toFixed(1)}L${bx.toFixed(1)},${by.toFixed(1)}`); b.dot.attr('transform', `translate(${sx.toFixed(1)},${sy.toFixed(1)})`); } }
  });
  /* 1b. a short name beside each disc once there is room */
  sbs.forEach(b=>b.tx.style('display','none'));
  if(k >= 1.1) for(const b of order0){
    if(!b.show || !b.hasName) continue;
    const [,,bx,by] = b.pos;
    for(const sd of (bx > W*0.62 ? ['l','r'] : ['r','l'])){
      const x = bx + (sd==='r' ? 20 : -20), w = b.tw + 4;
      const box = {x: sd==='r' ? x-2 : x-b.tw-2, y: by-9, w, h: 18};
      if(box.x >= 6 && box.x+box.w <= W-6 && box.y >= 6 && box.y+box.h <= H-6 && !hit(box)){
        placed.push(box); b.tx.style('display', null).attr('text-anchor', sd==='r'?'start':'end').attr('transform', `translate(${x.toFixed(1)},${(by+4).toFixed(1)})`); break;
      }
    }
  }
  /* 2. points */
  const bdg = [];
  pts.forEach(p=>{
    /* in a source-tier view the lettered limits are the evidence, so they show earlier and only for that tier */
    const mk = (TIER && p.badge) ? Math.min(p.minK, 0.55) : p.minK;
    let vis = (p.layer==='base' || layerOn[p.layer]) && k >= mk && !(TIER && p.tiers && !p.tiers.includes(TIER)) && (!quiet || QUIET_PTS.has(p.layer)) && !clean, x = 0, y = 0;
    /* Version 121: zoomed far out (the whole region on a phone) the small site symbols (diamonds, triangles, squares, rings) wait for the
       first zoom step, as their names already did; the numbered discs, the capital's star and the city dots stay */
    if(vis && k < 0.25 && p.sym && p.sym !== 'capital' && p.sym !== 'badge') vis = false;
    if(vis){ x = T.applyX(p.v[0]); y = T.applyY(p.v[1]); if(!p.keep && bc.some(c=>Math.hypot(c.x-x, c.y-y) < 21)) vis = false; }
    if(vis && p.badge){ if(bdg.some(c=>Math.hypot(c[0]-x, c[1]-y) < 17)) vis = false; else bdg.push([x,y]); }
    p.vis = vis; p.g.style('display', vis ? null : 'none');
    if(vis){ p.g.attr('transform', `translate(${x.toFixed(1)},${y.toFixed(1)})`); placed.push({x:x-5, y:y-5, w:10, h:10}); }
  });
  /* 3. labels */
  const inView = b => b.x >= 10 && b.x+b.w <= W-10 && b.y >= 10 && b.y+b.h <= H-10;
  const order = lbls.filter(l=>(l.layer==='base' || layerOn[l.layer]) && k >= l.minK && !(l.maxK && k >= l.maxK) && (!l.ptRef || l.ptRef.vis) && (!quiet || QUIET_LBL.has(l.layer)) && !(clean && (CLEAN_LBL.has(l.layer) || l.point || l.noClean))).sort((a,b)=>a.pri-b.pri);
  const shown = new Set();
  for(const l of order){
    const px = T.applyX(l.v[0]), py = T.applyY(l.v[1]) + l.dy;
    if(l.free){   /* the country name: drawn behind the rest; labels placed after it keep clear of it */
      /* Version 121: it takes the first of a few nearby spots (over the Red Sea, central Arabia, the Nubian desert, Najd) that is clear
         of the discs and markers already placed, so it no longer runs through them */
      const fb = k >= l.subK ? l.bbC.full : l.bbC.main;
      let fx = px + l.dx, fy = py;
      /* the clear spot, or else the one that covers least of them */
      const over = b => placed.reduce((t, p)=>t + Math.max(0, Math.min(b.x+b.w, p.x+p.w) - Math.max(b.x, p.x)) * Math.max(0, Math.min(b.y+b.h, p.y+p.h) - Math.max(b.y, p.y)), 0);
      /* each spot is tried at full size and then a little smaller (as the discs are), before the next spot: the name stays over the lands */
      let best = Infinity, fs = 1;
      const boxAt = (x, y, sc) => ({x:x + (fb.x - 4)*sc, y:y + (fb.y - 2)*sc, w:(fb.w + 8)*sc, h:(fb.h + 4)*sc});
      /* Version 176: each spot may also shift a little, and crossing the outline's line counts against a spot too */
      outer: for(const ll of (l.alts || [])){ const q = P(ll), x0 = T.applyX(q[0]) + l.dx, y0 = T.applyY(q[1]) + l.dy;
        for(const sc of [1, 0.82, 0.68, 0.58]) for(const sh of [[0,0],[-40,0],[40,0],[0,-26],[0,26]]){ const x = x0 + sh[0], y = y0 + sh[1], bx = boxAt(x, y, sc); if(!inView(bx)) continue;
          const o = (over(bx) + ogHit(bx)*OGS*OGS*1.5) / sc + (1 - sc)*2200;   /* a smaller title costs a little too, so it shrinks only to keep clear of much */ if(o < best){ best = o; fx = x; fy = y; fs = sc; } if(o === 0) break outer; } }
      placed.push(boxAt(fx, fy, fs));   /* smaller labels give way to it */
      l.t.attr('transform', `translate(${fx.toFixed(1)},${fy.toFixed(1)})${fs < 1 ? ` scale(${fs})` : ''}`); l.subs.forEach(s=>s.style('display', k >= l.subK ? null : 'none')); shown.add(l); continue; }
    if(px < -300 || px > W+300 || py < -80 || py > H+80) continue;
    const withSub = l.subs.length && k >= l.subK;
    const cands = [];
    if(l.point){
      const sides = l.pref==='l' ? ['l','r'] : ['r','l'];
      sides.forEach(sd=>{ const bbs = sd==='r' ? l.bbR : l.bbL; const x = px + (sd==='r'?10:-10);
        if(withSub) cands.push({sd, x, bb:bbs.full, sub:true}); cands.push({sd, x, bb:bbs.main, sub:false}); });
    } else {
      /* area labels may slide a little to find clear ground; notes stay put; a label along a sea slides along its length */
      const nudges = l.rot ? [0,-28,28,-56,56].map(t=>[t*Math.cos(l.rot*Math.PI/180), t*Math.sin(l.rot*Math.PI/180)])
        : l.sea ? [[0,0],[0,-14],[0,14],[-24,0],[24,0]]   /* a sea name only shifts a little, so it stays on the water */
        : l.nudge ? [[0,0],[0,-16],[0,16],[-34,0],[34,0],[0,-32],[0,32],[-34,-16],[34,-16],[-34,16],[34,16],[0,-50],[0,50]] : [[0,0]];
      [[px, py]].concat((l.av || []).map(v=>[T.applyX(v[0]), T.applyY(v[1]) + l.dy])).forEach(([ax, ay])=>
        nudges.forEach(nd=>{ const x = ax + l.dx + nd[0], ny = ay - py + nd[1];
          if(withSub) cands.push({x, ny, bb:l.bbC.full, sub:true}); cands.push({x, ny, bb:l.bbC.main, sub:false}); }));
    }
    /* Version 176: the first spot clear of everything placed and of the outline's line; failing that, the first clear of everything placed (as before) */
    let pick = null, near = null;
    for(const c of cands){ const yy = py + (c.ny||0);
      const boxes = l.rot ? rotBoxes(c.x, yy, c.bb, l.rot) : [{x:c.x+c.bb.x-2, y:yy+c.bb.y-1, w:c.bb.w+4, h:c.bb.h+2}];
      if(!boxes.every(inView) || boxes.some(hit)) continue;
      const cross = boxes.reduce((t, b)=>t + ogHit(b), 0);
      if(!cross){ pick = c; pick.boxes = boxes; pick.y = yy; break; }
      if(!near){ near = Object.assign({}, c, {boxes, y:yy}); }
    }
    if(!pick && !l.strict) pick = near;
    if(!pick && l.pri <= 0){ pick = cands[0]; pick.y = py; pick.boxes = [{x:pick.x+pick.bb.x, y:py+pick.bb.y, w:pick.bb.w, h:pick.bb.h}]; }
    if(!pick) continue;
    pick.boxes.forEach(b=>placed.push(b)); shown.add(l);
    if(l.point && l.side !== pick.sd){ l.t.attr('text-anchor', pick.sd==='r' ? 'start' : 'end'); l.side = pick.sd; }
    l.t.attr('transform', `translate(${pick.x.toFixed(1)},${(pick.y!=null?pick.y:py).toFixed(1)})${l.rot ? ` rotate(${l.rot})` : ''}`);
    l.subs.forEach(s=>s.style('display', pick.sub ? null : 'none'));
  }
  lbls.forEach(l=>l.t.style('display', shown.has(l) ? null : 'none'));
  /* 4. qibla arrows at Madinah */
  const showQ = layerOn.links && k >= 1.8 && !clean && !!qa1;
  d3.select(ovTop.node()).selectAll('.qg').style('display', showQ ? null : 'none');
  if(showQ){
    const mad = P(QIBLA.madinah), mx = T.applyX(mad[0]), my = T.applyY(mad[1]);
    const aq = P(QIBLA.aqsa), mk = P(QIBLA.makkah);
    setArrow(qa1, mx, my, T.applyX(aq[0]), T.applyY(aq[1]), 18, 66);
    setArrow(qa2, mx, my, T.applyX(mk[0]), T.applyY(mk[1]), 18, 66);
  }
  if(flashPt){ flashPt.g.attr('transform', `translate(${T.applyX(flashPt.v[0]).toFixed(1)},${T.applyY(flashPt.v[1]).toFixed(1)})`); }
  updateScale();
}
function flash(ll){
  if(flashPt) flashPt.g.remove();
  const g = ovTop.append('g').attr('class','flashg').attr('aria-hidden','true');
  g.append('circle').attr('class','fl1').attr('r',11); g.append('circle').attr('class','fl2').attr('r',4);
  flashPt = {g, v:P(ll)}; update();
  const me = flashPt; setTimeout(()=>{ if(flashPt===me){ me.g.remove(); flashPt = null; } }, 4200);
}
function updateScale(){
  const c = proj.invert(T.invert([W/2, H/2])); if(!c) return;
  const lat = Math.max(-80, Math.min(80, c[1]));
  const a = P([c[0], lat]), b = P([c[0]+1, lat]);
  const pxPerKm = (b[0]-a[0]) * T.k / (111.32 * Math.cos(lat*Math.PI/180));
  const nice = [0.1,0.2,0.5,1,2,5,10,20,50,100,200,500,1000];
  let best = nice[0]; for(const n of nice){ if(n*pxPerKm <= 130) best = n; }
  document.getElementById('scalebar').style.width = (best*pxPerKm).toFixed(0)+'px';
  document.getElementById('scaletxt').textContent = best<1 ? (best*1000)+' m' : best+' km';
}
/* Version 211: on a phone a bottom sheet (Notes, Layers) covers the lower part of the map; how many pixels of the map it covers,
   and how far the map was moved up to keep the view clear of it (moved back when the sheet closes) */
let sheetShift = 0, sheetInset = 0;
function sheetCover(){
  const sh = document.querySelector('.sheet.open'); if(!sh || window.matchMedia('(orientation:landscape) and (max-height:520px)').matches) return 0;
  const m = wrapEl.getBoundingClientRect(), top = window.innerHeight - sh.offsetHeight;
  return Math.max(0, Math.min(m.bottom, window.innerHeight) - Math.max(top, m.top));
}
function safeInsets(w, h){
  const s = {l:0, t:0, r:0, b:0};
  chrome.forEach(c=>{
    if(c.y < h*0.3 && c.w > w*0.3) s.t = Math.max(s.t, c.y + c.h);                                   /* bars across the top */
    else if(c.x < w*0.3 && c.h > h*0.25 && c.y < h*0.5) s.l = Math.max(s.l, c.x + c.w);              /* the open key */
    else if(c.x + c.w > w*0.8 && c.w < w*0.2 && c.y < h*0.5) s.r = Math.max(s.r, w - c.x);           /* the zoom buttons */
  });
  if(w - s.l - s.r < w*0.5) s.l = s.r = 0;
  if(h - s.t - s.b < h*0.5) s.t = s.b = 0;
  const cov = sheetCover(); sheetInset = 0; if(cov > 40 && h - s.t - cov > h*0.22){ s.b = cov; sheetInset = cov; }   /* frame above an open bottom sheet */
  return s;
}
function boundsT(b, w, h, pad, wide, fitH){
  const p0 = P([b[0][0], b[1][1]]), p1 = P([b[1][0], b[0][1]]);
  const dx = p1[0]-p0[0], dy = p1[1]-p0[1];
  /* ordinary views always fill the frame with mapped area; a 'wide' view may show the sheet's edge */
  /* fitH: on a tall (phone) frame, fit the box's height and let the reader pan sideways */
  /* Version 98: the box is framed in the part of the map left clear by the bars along the top, the key down the left and the
     buttons down the right, so a version or a place opens whole and in view rather than half under the controls */
  const s = safeInsets(w, h), fw = w - s.l - s.r, fh = h - s.t - s.b;
  const fit = (fitH && h > w*1.15) ? fh/dy : Math.min(fw/dx, fh/dy);
  const k = Math.max(wide ? zoom.scaleExtent()[0] : coverK, fit * (pad||0.92));
  let tx = s.l + fw/2 - k*(p0[0]+dx/2), ty = s.t + fh/2 - k*(p0[1]+dy/2);
  /* keep the view on the sheet: d3's zoom.transform does not apply the translate limits by itself */
  const s0 = SHEET_NW(), s1 = SHEET_SE();
  if((s1[0]-s0[0])*k >= w) tx = Math.min(-s0[0]*k, Math.max(w - s1[0]*k, tx));
  if((s1[1]-s0[1])*k >= h) ty = Math.min(-s0[1]*k, Math.max(h - s1[1]*k, ty));
  return d3.zoomIdentity.translate(tx, ty).scale(k);
}
const reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const DEEP = {els:null, box:null, on:false};   /* paths cut to the view when very close in */
let chipNext = null;   /* the Go-to chip whose view go() is about to show; every other chip goes dark */
function go(b, wide, fitH){ try { const c = chipNext; chipNext = null; focusBtns.forEach((x,j)=>x.classList.toggle('on', j === c)); } catch(e){} const t = boundsT(b, W, H, undefined, wide, fitH); sheetShift = sheetInset/2; wheelTarget = null; if(reduced) wrapSel.call(zoom.transform, t); else wrapSel.transition().duration(850).call(zoom.transform, t); }
