/* ================= v5 engine, part E: who drew it, place search, links ================= */
const ART_URL = "https://claude.ai/artifact/LUPQgg2w4dGSFdLcmR1a4F";

/* ---------------- source tiers ---------------- */
Object.assign(INFO, {
  tier_rev:{title:"What revelation fixes", src:["rev"], cert:null, body:`
    <p>The Qur'an and the authentic Sunnah name every place in this view and give it its status. Only two boundaries come from the texts themselves: the ḥaram of Makkah, which Allah made sacred, and the ḥaram of Madinah, "from ʿAyr to Thawr".</p>
    <p>The Prophet ﷺ also fixed four mīqāts: Dhū al-Ḥulayfah for Madinah, al-Juḥfah for al-Shām, Qarn al-Manāzil for Najd and Yalamlam for Yemen. Dhāt ʿIrq, for Iraq, was set by ʿUmar.</p>
    <p>No text draws a line around al-Shām, Filasṭīn, al-Ḥijāz or any other land, so no region is shaded in this view. Two numbered entries are left out because their status is disputed: Wajj (7) and the fig and the olive (13).</p>`,
    refs:[sn('bukhari',1834,'Al-Bukhārī 1834'), sn('bukhari',6755,'Al-Bukhārī 6755'), sn('muslim',1370,'Muslim 1370'), sn('bukhari',1524,'Al-Bukhārī 1524'), sn('muslim',1181,'Muslim 1181'), sn('bukhari',1531,'Al-Bukhārī 1531')]},
  tier_early:{title:"What the early sources add", src:["early"], cert:null, body:`
    <p>The Companions, the Successors and the scholars of the first three centuries explained the texts and described the land they knew. Four kinds of line come from them:</p>
    <ul>
      <li>Five early views on how far the Holy Land of 5:21 reaches. Open the notes for al-Arḍ al-Muqaddasah to switch between them.</li>
      <li>ʿUmar's army districts (<i>ajnād</i>): Filasṭīn, al-Urdunn, Dimashq and Ḥimṣ, with Qinnasrīn split off afterwards. Their exact edges are known only from later descriptions.</li>
      <li>Places an early report names as an edge (the lettered circles), such as ʿUmar counting Taymāʾ and Wādī al-Qurā as al-Shām (E).</li>
      <li>The jurists' Ḥijāz for the ruling on residence, taken from an earlier atlas and not re-read here, and the winter and summer journeys of Quraysh (106:2) as the tafsir describes them.</li>
    </ul>
    <p>These are explanations and reports, not revelation, and they often disagree.</p>`},
  tier_geo:{title:"What the classical geographers drew", src:["classical"], cert:null, body:`
    <p>From the 4th century AH, geographers such as Ibn Ḥawqal, al-Iṣṭakhrī, Yāqūt and Abū al-Fidāʾ described each land by naming the places on its edges. Every region outline in this view is built from those places, which are the lettered circles (they appear as you zoom in).</p>
    <p>They disagree with each other, and borders moved with wars and governments. That is why most edges are dashed or dotted, and why hatching marks land that some of them include and others leave out.</p>
    <p>Some outlines are my own rough work, because I could not re-read the geographers' formulas for them: al-ʿIrāq and al-Jazīrah follow the rivers, and Najd, al-Baḥrayn and Tihāmah are rough indications only.</p>`}
});
const TIER_BASE = ["relief","desert","graticule","cities"];
const TIERS = [
  {id:null, n:"All"},
  {id:"rev", n:"Revelation", col:"--ink", info:"tier_rev",
    on:STAT_LAYERS.concat(["haram","aqsa","miqat","tuwa","sites","links","saba","eschat"]),
    cap:"The Qur'an and the Sunnah name these places and fix two ḥarams and the mīqāts. They draw no line around any land."},
  {id:"early", n:"Early scholars", col:"--sham", info:"tier_early",
    on:["muq","ajnad","filastin","limits","hijazfiqh","trade"],
    cap:"Companions, Successors and early scholars: the Holy Land views, ʿUmar's districts and the first named edges."},
  {id:"classical", n:"Geographers", col:"--hijaz", info:"tier_geo",
    on:["sham","hijaz","limits","jazirah","yemen","upper","iraq","misr","najd","bahrayn","tihamah","rum","hajj"],
    cap:"Ibn Ḥawqal, Yāqūt and others: the region outlines, built from the places they name as edges."},
  {id:"modern", n:"Modern", col:"--muted", info:"modern",
    on:["modern","disputed"],
    cap:"Present-day states and disputed areas. None of the classical regions follows these lines."}
];
const tierEl = document.getElementById('tiers'), tierCap = document.getElementById('tiercap');
const tierBtns = TIERS.map(t=>{
  const b = document.createElement('button'); b.type = 'button'; b.dataset.t = t.id || '';
  b.innerHTML = (t.col ? `<i style="--c:var(${t.col})"></i>` : '') + t.n;
  b.addEventListener('click', ()=>setTier(t.id)); tierEl.appendChild(b); return b;
});
function syncTierBtns(){
  tierBtns.forEach(b=>{ const on = (b.dataset.t || null) === TIER; b.classList.toggle('on', on); b.setAttribute('aria-pressed', on); });
  if(!TIER){ tierCap.hidden = true; return; }
  const t = TIERS.find(x=>x.id===TIER);
  tierCap.style.setProperty('--c', `var(${t.col})`);
  tierCap.innerHTML = `<b>${t.n}.</b> ${t.cap} <button type="button" class="linkbtn" id="tiermore">Read more</button>`;
  tierCap.hidden = false;
  document.getElementById('tiermore').addEventListener('click', ()=>select(t.info));
}
function setTier(id){
  if(!id){ applyPreset('overview'); return; }
  const t = TIERS.find(x=>x.id===id); if(!t) return;
  const on = new Set(TIER_BASE.concat(t.on));
  LAYER_IDS.forEach(l=>{ layerOn[l] = on.has(l); const cb = document.getElementById('ly-'+l); if(cb) cb.checked = layerOn[l]; });
  TIER = id; setPresetChip(null); syncTierBtns(); applyLayers();
  showInfo(t.info); markSel(null);
}

/* ---------------- place search ---------------- */
const norm = s => (s||'').normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[ʿʾ'’‘`ʻ]/g,'').toLowerCase().replace(/[^a-z0-9؀-ۿ]+/g,' ').trim();
const ALIAS = {sham:"syria levant greater syria al sham", filastin:"palestine jund filastin urdunn jordan", hijaz:"hejaz hijaz", jazirah:"arabia arabian peninsula", yemen:"yemen saba", upper:"upper mesopotamia jazira", iraq:"iraq sawad mesopotamia", misr:"egypt nile sinai", najd:"nejd", bahrayn:"bahrain ahsa hasa eastern province", tihamah:"tihama coast", rum:"byzantium byzantine anatolia rome turkey constantinople", habashah:"abyssinia ethiopia axum aksum najashi negus", muq:"holy land ard muqaddasah", tuwa:"mount sinai tur", eschat:"end of time hour", aqsa:"jerusalem al quds bayt al maqdis temple mount haram sharif dome of the rock", haram:"mecca medina", miqat:"miqat ihram", ajnad:"ajnad districts", saba:"sheba marib aḥqaf", trade:"quraysh winter summer journey", hajj:"pilgrim road darb zubaydah", hijazfiqh:"jurists residence", caliph:"caliphate khilafah khalifah caliph union ummah", caliphx:"caliphate complete expanded iran persia caucasus georgia armenia azerbaijan greater syria greater israel greater iraq iraq al ajam jibal khuzestan ahwaz horn of africa sudan ethiopia somalia iraq cyprus turkey turkiye turkey turkiye"};
const CITY_ALIAS = {Makkah:"mecca", Madinah:"medina", Damascus:"sham", Aqaba:"aylah", Istanbul:"constantinople qustantiniyyah byzantium"};
const INDEX = [];
const addIx = (label, kind, sub, extra, act, keys, rank) => INDEX.push({label, kind, sub:sub||'', act, keys:keys||[], rank:rank==null?50:rank, n:norm(label), t:norm([label, sub, extra].join(' '))});
LAYERS.forEach(g=>{ if(!["Sacred places","Classical regions","Neighbouring lands","Roads","Thought experiment"].includes(g.g)) return;
  g.items.forEach(l=>{ const fi = FOCUS.findIndex(f=>f.layer===l.id);
    addIx(l.name, g.g==='Roads' ? 'Road' : 'Land or layer', l.sub, ALIAS[l.id], ()=>{ TIER_KEEP = false; if(!layerOn[l.id]) setLayer(l.id, true); if(fi>=0) goFocus(fi); if(l.info) select(l.info); }, [l.id, l.info]); }); });
FOCUS.forEach((f,i)=>{ if(i===0) return; addIx(f.n, 'View', 'zoom to this area', '', ()=>goFocus(i), [norm(f.n).replace(/ /g,'-')]); });
STATUS.forEach(s=>addIx(`${s.n} · ${s.name}`, 'Sacred status', s.lvl, '', ()=>goStatus(s.n), ['st'+s.n]));
ALL_LIMITS.forEach(l=>addIx(`${l.id} · ${l.n}`, 'Named limit', '', '', ()=>goLimit(l.id), ['lim-'+l.id.toLowerCase()]));
const near = (ll, d) => [[ll[0]-d*1.25, ll[1]-d],[ll[0]+d*1.25, ll[1]+d]];
CITIES.forEach(c=>{ const ll = [c[2],c[3]];
  addIx(c[0], 'City', c[1], CITY_ALIAS[c[0]], ()=>{ if(!layerOn.cities) setLayer('cities', true); go(near(ll, 0.7)); flash(ll); scrollToMap(); }, null, c[6]); });
MIQATS.forEach(m=>addIx(m.n, 'Mīqāt', m.s, 'miqat ihram', ()=>{ if(!layerOn.miqat) setLayer('miqat', true); go(near(m.ll, 0.4)); flash(m.ll); select('miqat'); }));
SITES.forEach(s=>{ const lay = s.id==='tayyi' ? 'sham' : 'sites';
  addIx(s.n, 'Site', s.s, '', ()=>{ if(!layerOn[lay]) setLayer(lay, true); go(near(s.ll, 0.18)); flash(s.ll); select(s.info||('site_'+s.id)); }); });
ESCHAT.forEach(e=>{ const key = 'eg_'+(e.id==='qustantiniyyah' ? 'qust' : e.id);
  addIx(e.n, 'Hadith place', e.s, 'end of time' + (e.id==='qustantiniyyah' ? ' constantinople istanbul' : ''), ()=>{ if(!layerOn.eschat) setLayer('eschat', true); go(near(e.ll, 0.5)); flash(e.ll); select(key); }); });
HARAM_PTS.forEach(h=>addIx(h.n, 'Ḥaram marker', h.s, '', ()=>{ if(!layerOn.haram) setLayer('haram', true); go(near(h.ll, 0.07)); flash(h.ll); select(h.info); }));
addIx('V2', 'View', 'the Middle East map with Libya, the whole Nile and the Horn of Africa, and Tunisia, Afghanistan, Pakistan, Turkmenistan, Bulgaria, Albania and North Macedonia, whole, and the whole Nile and the Horn of Africa · the author’s specification', 'v3 version 3 turkmenistan bulgaria albania north macedonia macedonia balkans tunisia eritrea djibouti somaliland somalia middle east afghanistan pakistan libya greece caliphate', ()=>openOutline('me2'), ['outline-v3']);
addIx('V8', 'View', 'the largest outline, the Super Caliphate: a wide complete outline with the Muslim-majority countries of Africa, Cameroon, Bulgaria, Albania and North Macedonia, South Asia with all of Kashmir, Greater Tibet, East Turkestan, and Southeast Asia to Papua New Guinea · history by province', 'v11 version 11 super caliphate balkans north macedonia albania bulgaria india nepal bhutan bangladesh sri lanka maldives andaman nicobar kashmir jammu aksai chin shaksgam siachen tibet greater tibet qinghai myanmar burma thailand laos cambodia vietnam malaysia singapore brunei indonesia philippines east timor timor-leste papua new guinea south asia southeast asia east turkestan uyghur xinjiang kashgar kashgaria tarim yettishar yaqub beg ili turfan urumqi greater middle east caliphate history ruled tributary cameroon adamawa maghrib morocco algeria tunisia libya mauritania western sahara kazakhstan uzbekistan turkmenistan kyrgyzstan tajikistan afghanistan pakistan', ()=>openOutline('v2'), ['outline-v11']);
addIx('Maʾrib', 'Site', 'Sabaʾ · the dam', 'marib sheba saba', ()=>{ if(!layerOn.saba) setLayer('saba', true); go(near(MARIB, 1)); flash(MARIB); select('saba'); });
addIx('Aksūm', 'Site', "heart of the Najāshī's kingdom", 'axum ethiopia abyssinia', ()=>{ if(!layerOn.habashah) setLayer('habashah', true); go(near(AKSUM, 1.2)); flash(AKSUM); select('habashah'); });

const KIND_ORDER = ['Sacred status','City','Land or layer','Site','Mīqāt','Hadith place','Named limit','Ḥaram marker','View','Road'];
function searchPlaces(q){
  const nq = norm(q); if(!nq) return [];
  const toks = nq.split(' ');
  const out = [];
  for(const e of INDEX){
    const words = e.t.split(' '), lw = e.n.split(' '), lj = e.n.replace(/ /g,''), qj = nq.replace(/ /g,'');
    const wordHit = t => words.some(w=>w.startsWith(t) || (t.length>=3 && w.includes(t)));
    if(!(toks.every(wordHit) || (qj.length>=3 && lj.includes(qj)))) continue;
    /* exact word in the name, then name starts with it, then a word starts with it, then inside the name, then only in aliases */
    const sc = toks.every(t=>lw.includes(t)) ? 0 : e.n.startsWith(nq) ? 1 : toks.every(t=>lw.some(w=>w.startsWith(t))) ? 2 : lj.includes(qj) ? 3 : 4;
    out.push({e, sc});
  }
  out.sort((a,b)=>a.sc-b.sc || KIND_ORDER.indexOf(a.e.kind)-KIND_ORDER.indexOf(b.e.kind) || a.e.rank-b.e.rank || a.e.label.length-b.e.label.length);   /* rank: a city's map priority, so Madinah comes before Madrid */
  const seen = new Set();
  return out.filter(o=>{ const k = o.e.kind+'|'+o.e.label; if(seen.has(k)) return false; seen.add(k); return true; }).slice(0, 8).map(o=>o.e);
}
const qEl = document.getElementById('placeq'), listEl = document.getElementById('placelist');
let hits = [], active = -1;
const esc = s => s.replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function renderHits(){
  if(!qEl.value.trim()){ listEl.hidden = true; qEl.setAttribute('aria-expanded','false'); return; }
  listEl.innerHTML = hits.length ? hits.map((e,i)=>`<li role="option" id="po-${i}" data-i="${i}" aria-selected="${i===active}"><b>${esc(e.label)}</b><span>${esc(e.kind)}${e.sub?' · '+esc(e.sub):''}</span></li>`).join('')
    : `<li class="none" role="option" aria-disabled="true">No place by that name on this map</li>`;
  listEl.hidden = false; qEl.setAttribute('aria-expanded','true');
  if(active>=0) qEl.setAttribute('aria-activedescendant', 'po-'+active); else qEl.removeAttribute('aria-activedescendant');
}
function pick(i){ const e = hits[i]; if(!e) return; qEl.value = e.label; listEl.hidden = true; qEl.setAttribute('aria-expanded','false'); qEl.blur(); e.act(); }
qEl.addEventListener('input', ()=>{ hits = searchPlaces(qEl.value); active = hits.length ? 0 : -1; renderHits(); });
qEl.addEventListener('focus', ()=>{ if(qEl.value.trim()){ hits = searchPlaces(qEl.value); renderHits(); } });
qEl.addEventListener('keydown', e=>{
  if(e.key==='ArrowDown'){ e.preventDefault(); if(hits.length){ active = (active+1) % hits.length; renderHits(); } }
  else if(e.key==='ArrowUp'){ e.preventDefault(); if(hits.length){ active = (active-1+hits.length) % hits.length; renderHits(); } }
  else if(e.key==='Enter'){ e.preventDefault(); pick(active>=0 ? active : 0); }
  else if(e.key==='Escape'){ listEl.hidden = true; qEl.setAttribute('aria-expanded','false'); }
});
listEl.addEventListener('pointerdown', e=>{ const li = e.target.closest('li[data-i]'); if(li){ e.preventDefault(); pick(+li.dataset.i); } });
document.addEventListener('pointerdown', e=>{ if(!e.target.closest('.find')){ listEl.hidden = true; qEl.setAttribute('aria-expanded','false'); } });

/* ---------------- links to a place ---------------- */
function tokenFor(key){
  if(/^st\d+$/.test(key)) return key;
  if(/^lim_[A-P]$/.test(key)) return 'lim-'+key.slice(4).toLowerCase();
  /* the overlays open with their layer switched on */
  if(key === 'natb') return 'natural-line';
  if(key === 'intl') return 'internal-lines';
  return /^[a-z0-9_]+$/i.test(key) ? key : null;
}
const OLD_HASH = {makkah:[4,'makkah'], madinah:[5,'madinah'], jerusalem:[3,'aqsa'], sham:[1,'sham'], miqat:[6,'miqat'], hijaz:[7,'hijaz']};
function openToken(tok, first){
  if(!tok || !/^[A-Za-z0-9._~-]+$/.test(tok)) return;
  if(/^(fullmap|full|full-map|fullscreen)$/i.test(tok)) return enterFull(!first);
  if(document.getElementById(tok)) return;   /* a section anchor, not a place */
  let t = tok.toLowerCase(), m;
  const run = f => first ? setTimeout(f, 350) : f();
  if((m = t.match(/^st(\d{1,2})$/))) return run(()=>goStatus(+m[1], true));
  if((m = t.match(/^lim-([a-p])$/))) return run(()=>goLimit(m[1].toUpperCase()));
  /* Version 169: the outlines are numbered V1-V6 by size and the tokens #outline-v1 ... #outline-v6 (and #v1 ... #v6, found by the search entry's name) open the NEW V1 ... V6
     (keys: V1 'me', V2 'me2', V3 'fullb', V4 'full', V5 'v3', V6 'v2'; the keys did not change). Comments in this file written before Version 169 use the OLD names:
     old V2 = now V4 ('full'), old V2-B = now V3 ('fullb'), old V4 = now V2 ('me2').
     Old names that no longer exist open the map they stood for: #outline-v2-b, #outline-v2b, #v2-b, #v2b -> V3 ('fullb', the same map); #outline-v2n, #outline-v2-natural, #outline-complete -> V4 ('full').
     Both earlier V7s are gone (the Greater Caliphate V7, deleted in Version 155, and the V7 of Version 159, deleted in Version 169): #outline-greater, #outline-gme, #greater-caliphate, #caliphg open V6.
     Version 179: a NEW V7 ('full7', CALIPH.x7: V2 with India, Nepal, Bhutan, Greater Tibet, Myanmar, Bangladesh, Sri Lanka, the Maldives and all of Kashmir) takes #outline-v7, #v7 and #outline-india.
     V3 (to Iraq's border) was deleted in Version 157: #outline-iraq, #outline-west, #caliphxw open V4 ('full'), the nearest (it was V2 then). */
  const OUTLINE_TOK = {'outline-v1':'me8', 'outline-middle-east-16':'me8', 'outline-v2':'me2', 'outline-middle-east':'me2', 'outline-v3':'ca', 'outline-borderlands':'me2', 'outline-v4':'me9', 'outline-v2-b':'ca', 'outline-v2b':'ca', 'v2-b':'ca', 'v2b':'ca', 'outline-v2n':'ca', 'outline-v2-natural':'ca', 'outline-complete':'ca', 'outline-v5':'sah', 'outline-central-asia':'ca', 'outline-v6':'af', 'outline-north-africa':'me9', 'outline-v7':'eu', 'outline-sahara':'sah', 'outline-v8':'v2', 'outline-complete-v3':'sah', 'outline-v9':'v2', 'outline-africa':'af', 'outline-all-africa':'af', 'outline-v11':'v2', 'outline-super':'v2', 'outline-super-caliphate':'v2', 'outline-v10':'v2', 'outline-mediterranean':'eu', 'outline-south-asia':'v2', 'outline-greater-middle-east':'v2', 'outline-greater':'v2', 'outline-gme':'v2', 'greater-caliphate':'v2', 'caliphg':'v2', 'outline-iraq':'ca', 'outline-west':'ca', 'caliphxw':'ca'};   /* Version 225: V4 (Libya–Chad Borderlands, me10) and V5 (V6 without the Balkans, fullb) removed and V6–V9 renumbered V4–V7 by size; old links #outline-v8 and #outline-v9 still open the maps they named (now V6, V7), #outline-borderlands opens V3, the V2-B links V4 */
  if(OUTLINE_TOK[t]) return run(()=>openOutline(OUTLINE_TOK[t]));
  if((m = t.match(/^who-(rev|early|geo|modern)$/))) return run(()=>{ setTier(m[1]==='geo' ? 'classical' : m[1]); scrollToMap(); });
  if(OLD_HASH[t]) return run(()=>{ goFocus(OLD_HASH[t][0]); select(OLD_HASH[t][1]); scrollToMap(); });
  const hit = INDEX.find(e=>e.keys.includes(t)) || INDEX.find(e=>e.n.replace(/ /g,'-')===t);
  if(hit) return run(()=>{ hit.act(); scrollToMap(); });
  if(INFO[t]) return run(()=>select(t));
}
window.addEventListener('hashchange', ()=>openToken(location.hash.slice(1)));
/* a copy-link button on every note */
const _showInfo = showInfo;
showInfo = function(key, extraTitle){
  _showInfo(key, extraTitle);
  let tok = tokenFor(key); if(!tok || key==='intro') return;
  if(key === 'caliphx') tok = 'outline-' + XNUM[XV].toLowerCase();
  const url = `${ART_URL}#${tok}`;
  const box = document.createElement('div'); box.className = 'sharebox';
  box.innerHTML = `<button type="button" class="linkbtn copyl">Copy a link to this note</button><input type="text" readonly value="${url}" aria-label="Link to this note" hidden>`;
  const refs = infoEl.querySelector('.refs'); refs ? infoEl.insertBefore(box, refs) : infoEl.appendChild(box);
  const btn = box.querySelector('button'), inp = box.querySelector('input');
  btn.addEventListener('click', ()=>{
    const fallback = ()=>{ inp.hidden = false; inp.focus(); inp.select(); btn.textContent = 'Copy this link:'; };
    try { navigator.clipboard.writeText(url).then(()=>{ btn.textContent = 'Link copied'; setTimeout(()=>{ btn.textContent = 'Copy a link to this note'; }, 2200); }, fallback); } catch(e){ fallback(); }
  });
};

/* ---------------- the caliphate thought experiment ---------------- */
const pctTxt = s => s.pct == null ? 'water' : s.pct >= 99 ? 'all of it' : s.pct < 1 ? 'under 1%' : `${s.pct}%`;  /* null: a stretch of sea, not a state */
const kmTxt = n => { const p = Math.pow(10, Math.max(0, Math.floor(Math.log10(n)) - 2)); return (Math.round(n/p)*p).toLocaleString('en'); };
const listAnd = a => a.length < 3 ? a.join(' and ') : a.slice(0,-1).join(', ') + ' and ' + a[a.length-1];
Object.assign(INFO, {
  caliph:{title:"A caliphate of the best lands", src:[], cert:"uncertain", body:`
    <p><b>A thought experiment. This is my synthesis, not a ruling.</b> No text, early scholar or geographer drew this line. It is the smallest single territory that holds every land the sources give a status: al-Ḥijāz with the two ḥarams, al-Shām with Filasṭīn and al-Aqṣā, Sinai and al-Ṭūr, al-Yaman, and the Nile valley and Delta of Miṣr. Where the sources disagree on an edge, I took the widest reading.</p>
    <p>Najd, al-ʿIrāq, the Gulf, al-Ḥabashah and Bilād al-Rūm fall outside, because no status for them is established. The result is a ring around the Red Sea and up the Levant.</p>
    <p>By my rough measurement it covers about ${(CALIPH.km2/1e6).toFixed(1)} million km² in ${CALIPH.states.length} present-day states and territories: ${CALIPH.states.map(s=>`${s.n} (${pctTxt(s)})`).join(', ')}.</p>
    <p><a href="#synth" class="tosynth">What the texts say about the caliphate, and the limits of this outline</a></p>`,
    refs:[`<a href="https://quran.com/24:55" target="_blank" rel="noopener">Qur'an 24:55</a>`, sn('tirmidhi',2226,'Al-Tirmidhī 2226'), sn('abudawud',2535,'Abū Dāwūd 2535'), `<a href="https://dorar.net/h/R7HZBi1v" target="_blank" rel="noopener">The hadith of the stages (dorar.net)</a>`, `<a href="https://en.wikipedia.org/wiki/Letter_to_Baghdadi" target="_blank" rel="noopener">Letter to Baghdadi, 2014</a>`]}
});
Object.assign(INFO, {
  histreg:{title:'Historical region names', src:['classical'], cert:'uncertain', body:`<p>The names the classical geographers used for the lands around the core: al-Andalus and the three parts of al-Maghrib, Barqah and Fazzān; Bilād al-Sūdān, al-Nūbah and the coast of Bilād al-Zanj; Khurāsān, Mā warāʾ al-Nahr (the land beyond the Oxus), Khwārazm, Farghānah, Sijistān, Makrān and al-Sind; Ṭabaristān, Ādharbayjān, Arrān and Armīniyah; and, further out, al-Hind, Bilād al-Turk and Bilād al-Ṣīn.</p><p><b>The three parts of al-Maghrib</b> (“the West”, where the sun sets) are placed as the medieval Muslim historians and geographers divided it: <i>al-Maghrib al-Adnā</i>, the Near West, also called Ifrīqiyah, from Alexandria to Tripoli; <i>al-Maghrib al-Awsaṭ</i>, the Middle West, from Tripoli to Bijāyah (Béjaïa); and <i>al-Maghrib al-Aqṣā</i>, the Farthest West, from Tāhart (Tiaret) to the Atlantic (El Hareir and Mbaye, <i>The Spread of Islam Throughout the World</i>, UNESCO 2011, as cited in Wikipedia’s “Maghreb”). The writers disagreed on the eastern edge: some began al-Maghrib at the Red Sea, with Egypt and Barqah; Ibn Khaldūn began it at Tripoli. Elsewhere Ifrīqiyah usually means the land round Qayrawān and Tunis. Today al-Maghrib alone is also Morocco’s name, and the Greater Maghreb (al-Maghrib al-Kabīr) is Morocco, Algeria, Tunisia, Libya and Mauritania, with Western Sahara (the Arab Maghreb Union, 1989).</p><p>They are drawn as names only, placed approximately. I did not re-read the geographers on their limits, so no edges are drawn.</p>`},
  caliphx:{title:"The complete outline", src:[], cert:"uncertain", body:`
    %%LEAD%%
    <p><b>Not an outline of the best lands.</b> The lands the sources honour are inside the black dotted line. Everything between that line and this outline comes from the author’s specification.</p>
    <p><b>How I read the two "Greater" terms.</b> Greater Syria is taken as Syria, Lebanon, Jordan, Israel and Palestine, plus Bilād al-Shām's belt in Türkiye. "Greater Israel" is a term from Zionist maximalism and its critics, not an Islamic category; its widest reading runs from the Nile to the Euphrates. With all of Iraq and Egypt already in, neither term adds land of its own.</p>
    %%IRAQ%%
    %%SRC%%
    %%GC%%
    %%AREA%%
    <p><a href="#synth" class="tosynth">The texts, both outlines and their limits</a></p>`,
    refs:[sn('muslim',2839,'Muslim 2839'), sn('muslim','2546b','Muslim 2546'), sn('bukhari',3207,'Al-Bukhārī 3207'), sn('bukhari',3887,'Al-Bukhārī 3887'), sn('muslim',164,'Muslim 164'), sn('abudawud',4302,'Abū Dāwūd 4302'), sn('bukhari',2924,'Al-Bukhārī 2924'), sn('muslim',2897,'Muslim 2897'), sn('abudawud',2535,'Abū Dāwūd 2535'), `<a href="https://en.wikipedia.org/wiki/Letter_to_Baghdadi" target="_blank" rel="noopener">Letter to Baghdadi, 2014</a>`]}
});
/* ---------------- the versions of the user's outline ---------------- */
const CX_BODY = INFO.caliphx.body;
/* Dār al-Amān: the names chosen for the outline, and the capital */
const NAMES_P = `<p><b>Names, the author’s choice.</b> The country is <b>Dār al-Amān</b> (<span lang="ar" dir="rtl">دار الأمان</span>), “the abode of safety”; its formal title is <b>al-Khilāfa al-Amīna</b> (<span lang="ar" dir="rtl">الخلافة الأمينة</span>), “the trustworthy caliphate”; its people are <b>Amānī</b> (plural Amāniyyūn); its capital is al-Quds (Jerusalem), marked with a star. None of these names comes from the sources. In classical law <i>amān</i> is a guarantee of safety given to a person; I found no classical text that uses Dār al-Amān as the name of a state. The province names on the map, and their short tags when zoomed out (ŠM, ḤJ, YM …), are the classical region names used across this atlas.</p>`;
INFO.capital = {title:'al-Quds · capital of Dār al-Amān', src:[], cert:'uncertain', body:`<p><b>The author’s choice, not from the sources.</b> al-Quds (Bayt al-Maqdis, Jerusalem) is the capital of Dār al-Amān in this outline. The gold star and ring mark the city; al-Masjid al-Aqṣā keeps its own marker and notes.</p>
  <p><b>For comparison, where caliphs ruled from.</b> No caliphate had its capital at Jerusalem. The Prophet ﷺ and the first three caliphs ruled from Madinah, ʿAlī from Kufa, the Umayyads from Damascus, the Abbasids chiefly from Baghdad, the Fatimids from Ifrīqiya and then Cairo, the Umayyads of al-Andalus from Córdoba, the Almohads from Marrakesh, the Ottomans from Istanbul and the Sokoto Caliphate from Sokoto. Two links to the city and its province: Muʿāwiya is reported to have received the oath of allegiance as caliph at Jerusalem (Īliyāʾ) in 40/660, and the Umayyad caliph Sulaymān ruled from al-Ramla, the town he founded in Filasṭīn. These two points are from general knowledge; I have not checked them against the chronicles for this atlas.</p>${NAMES_P}`, refs:[]};
/* the parts of the outline note that differ between the three versions */
/* Version 71: the four rivers of the hadith, end to end in every version (the author's request) */
const RIVERS_P = `<p><b>The four rivers, end to end, at the author’s request.</b> Every version holds whole the four rivers that a hadith names among the rivers of Paradise: “Sayḥān, Jayḥān, the Euphrates and the Nile are all among the rivers of Paradise” (Ṣaḥīḥ Muslim 2839, from Abū Hurayrah). Sayḥān and Jayḥān are taken here as the rivers of Adana and al-Maṣṣīṣa in southern Türkiye, today’s Seyhan and Ceyhan, not the Sayḥūn and Jayḥūn of Central Asia (the Syr Darya and Amu Darya); that identification is reported from al-Nawawī’s commentary on Muslim, which I could not open to check. In the account of the Night Journey, the Nile and the Euphrates are the two outward rivers at the root of the Lote Tree of the Furthest Boundary (al-Bukhārī 3207 and 3887; Muslim 164). The hadith speaks of the rivers; it gives the lands along them no status, and taking those lands in is the author’s specification, not a ruling.</p>`;
const CX_SPEC = '<b>Drawn to the author’s specification. It is not from the sources, and not a ruling.</b>';
/* V2 (Complete; V1 before Version 66): the Complete outline of Version 47 (restored in Version 55) */
const CX_CORE = (iran, nf, nb)=> `the whole Arabian Peninsula; Greater Syria; Greater Israel in its widest reading; all of Iraq${iran ? ' and Iran, with Greater Iraq inside them' : ''}; all of Türkiye;${iran ? ' Georgia, Armenia and Azerbaijan, and the Caucasus north of them as the author’s orange map shades it, with Greater Georgia’s Russian lands;' : ''} the whole island of Cyprus; all of Egypt, Sudan, South Sudan, Somalia (with Somaliland), Ethiopia, Eritrea and Djibouti, with Uganda, Kenya, Tanzania, Rwanda and Burundi, whole, so that the whole Nile, from its farthest headstream to the sea, and Lake Victoria lie inside, with all of Lake Albert, DR Congo’s half included; the Comoros and Mayotte; ${iran ? '' : 'and '}all of Libya, Tunisia and Greece${iran ? ', so that, with Türkiye, Cyprus, Georgia, Syria and Iraq, Greater Turkey as the Misak-ı Millî map draws it lies inside' + (nb ? '' : '; and the whole Balkan Peninsula as Wikipedia’s map draws it (Bulgaria, Bosnia and Herzegovina, Montenegro, Albania, Kosovo and North Macedonia whole, with Croatia south of the Sava and Kupa and all its islands, Serbia south of the Sava and Danube, south-western Slovenia, Romania’s Dobruja and Trieste)') : ''}${iran ? '; and all of Pakistan (with Azad Kashmir and Gilgit-Baltistan), Afghanistan and Turkmenistan, by today’s borders, with Greater Khurāsān at the widest extent any classical source or geographer gives it: the author’s three Khorasan maps; all of Transoxiana and Khwārazm as his maps draw them (all of Tajikistan and all of Uzbekistan, with Nukus, the Ustyurt and the Farghāna valley with Osh), and Manqishlāq on the Caspian (Kazakhstan’s Mangystau region, with Aktau); Isbījāb’s district (Shymkent, Turkistan, Otrār, Ṭarāz to Mirkī); the edge towns the geographers name, Jand and Yanghikant on the lower Syr Darya (the Qyzylorda region, with Aralsk and Baikonur) and Nawākath and Barskhān in the Chu valley and by Issyk-Kul (Bishkek, Tokmok, Karakol), with the Naryn country enclosed between them, so that all of Kyrgyzstan is inside; and, on Lambton’s reading of “the Chinese desert and the Pamirs”, the Kashgar oasis to the Taklamakan’s edge; and the India–Pakistan border as it is today' : ''}`;
/* V5 (Complete, extended; Complete V3 before Version 66): the Complete outline of Version 54; V6 is built on it */
const CX_CORE3 = ()=> `the whole Arabian Peninsula; Greater Syria; Greater Israel in its widest reading; all of Iraq and Iran, with Greater Iraq inside them; all of Türkiye; Georgia, Armenia and Azerbaijan, to their northern borders (at the author’s request the wide complete outline follows political borders, not traced lines, Lake Albert apart; it holds no Russian land); the whole island of Cyprus, and the island of Arwād off Ṭarṭūs (marked with a dot); all of Egypt, Sudan, South Sudan, Somalia (with Somaliland), Ethiopia, Eritrea and Djibouti, with Uganda, Kenya, Tanzania, Rwanda and Burundi, whole, so that the whole Nile, from its farthest headstream to the sea, and Lake Victoria lie inside; all of Libya, Tunisia, Algeria and Morocco, with Western Sahara (both the part Morocco holds and the rest) and Mauritania; all of West Africa to Cameroon (every country whole, from Senegal and Cabo Verde to Nigeria and Cameroon, with Saint Helena, which the UN counts in West Africa), Chad and the Central African Republic, at the author’s request; all of Greece, Spain and Portugal with their islands, and Malta (Sicily was taken out at his request); and all of Kazakhstan, Turkmenistan, Uzbekistan, Tajikistan, Kyrgyzstan, Afghanistan and Pakistan (with Azad Kashmir and Gilgit-Baltistan)`;
const CX_LEAD = {
  me2: `<p>${CX_SPEC} <b>V2</b>, the heartland, is V1 with Libya, the lands of the whole Nile (Sudan with Bir Tawil, South Sudan, Ethiopia, Uganda, Kenya, Tanzania, Rwanda and Burundi), the Horn of Africa (Eritrea, Djibouti, Somaliland and Somalia) and Greece, and with Tunisia, Afghanistan, Pakistan (with Azad Kashmir and Gilgit-Baltistan), Turkmenistan, Bulgaria, Albania and North Macedonia, each whole. It runs unbroken from Libya to the Indus, up the Nile to Lake Victoria and round the Horn of Africa. It keeps to official borders: it takes no doubtful or disputed land. The best-lands outline lies wholly inside it. About ${(CALIPH.me2.km2/1e6).toFixed(1)} million km².</p>`,
  me: `<p>${CX_SPEC} This outline is no longer on the list.</p>`,
  v2: `<p>${CX_SPEC} <b>V8</b>, the largest outline, is the author’s <b>Super Caliphate</b>. It is built on a wide complete outline that holds every land on a Greater Middle East reference map supplied by the author, and adds, every land whole: the Muslim-majority countries of Africa not already inside (Chad, Mali, Niger, Nigeria, Burkina Faso, Guinea, Senegal, Sierra Leone, Guinea-Bissau, the Gambia and the Comoros), Cameroon, whose north was the Sokoto Caliphate’s Adamawa emirate, the Central African Republic and all of West Africa (with Cabo Verde and Saint Helena); in the Balkans, Greece, Bulgaria, Albania and North Macedonia; the whole of South Asia: India (with the Andaman and Nicobar Islands and the Siachen Glacier), Nepal, Bhutan, Bangladesh, Sri Lanka and the Maldives, with Afghanistan, Pakistan and all of Jammu and Kashmir, including the parts China administers (Aksai Chin and the Shaksgam valley); Greater Tibet, the three Tibetan provinces of Ü-Tsang, Kham and Amdo as the Tibetan government in exile counts them (the widest of three public sets of lines, Overture Maps, Natural Earth and geoBoundaries, about 2.17 million km²); East Turkestan as its government in exile defines it (Xinjiang without Aksai Chin, with the edges of western Gansu and Qinghai); and all of Southeast Asia (Myanmar, Thailand, Laos, Cambodia, Vietnam, Malaysia, Singapore, Brunei, Indonesia, the Philippines and East Timor) with Papua New Guinea. Most of the people of these eastern lands are not Muslim; in Nigeria and Guinea-Bissau Muslims are about half. Corsica, Sardinia and Sicily are out (Malta stays), and in the Caucasus it keeps to the modern borders of Azerbaijan and Georgia. That outline holds the best-lands outline and adds ${CX_CORE3()}. How Muslim rulers held each land of the reference map, province by province, is set out below.</p>`,
  v3: `<p>${CX_SPEC} This outline is no longer on the list.</p>`,
  full: `<p>${CX_SPEC} This outline is no longer on the list.</p>`
};
/* Version 187: V8 = the sixteen states of the Middle East reference map, each whole, with the lands every outline holds (CALIPH.me8, tools/v8_me16_187.py) */
CX_LEAD.me8 = `<p>${CX_SPEC} <b>V1</b>, the smallest outline, is the Middle East reference map supplied by the author: the sixteen states it shades, each whole (Türkiye, Syria, Lebanon, Israel, Palestine, Jordan, Iraq, Iran, Egypt, Saudi Arabia, Kuwait, Bahrain, Qatar, the United Arab Emirates, Oman and Yemen). Like every outline it also holds the whole island of Cyprus, Azerbaijan, Georgia, Armenia and the whole of Lake Albert. About ${(CALIPH.me8.km2/1e6).toFixed(1)} million km².</p>`;
/* Version 237: V3 = V2 with all of Central Asia (CALIPH.ca, tools/v5_ca237.py) */
CX_LEAD.ca = `<p>${CX_SPEC} <b>V3</b> is V2 with all of Central Asia, every land whole: Kazakhstan (with Baikonur), Uzbekistan, Kyrgyzstan and Tajikistan. It holds the whole of Transoxiana (Mā warāʾ al-Nahr) and Khwārazm, the Syr Darya and Amu Darya end to end, and the Kazakh steppe to the Altai. About ${(CALIPH.ca.km2/1e6).toFixed(1)} million km².</p>`;
/* Version 239: V5 = V4 + the whole Sahara (CALIPH.sah, tools/v7_sahara239.py) */
CX_LEAD.sah = `<p>${CX_SPEC} <b>V5</b> is V4 with the whole Sahara: Niger and Burkina Faso, each whole, and northern Chad (Borkou, Ennedi and Tibesti, the part Libya claimed in the Chad–Libya conflict; Chad’s south is left out). The Sahara is inside from the Atlantic to the Nile, and the southern frontier runs along the Sahel from Liberia to Sudan. Like V4 it holds Iberia, the Maghreb, West Africa to Liberia, the Nile and the Horn, Arabia, Iran, Pakistan, Afghanistan, Central Asia and the whole Greater Middle East. <b>The Balkan Peninsula (Version 258)</b>, drawn to the outline on Wikipedia’s map of the Balkans (OpenStreetMap’s “Balkans” peninsula), whose northern edge runs along the Kupa, Sava and Danube: Bulgaria, Bosnia and Herzegovina, Montenegro, Albania, Kosovo and North Macedonia whole; Croatia south of the Kupa and Sava with every island, Serbia south of the Sava and Danube, Slovenia’s south-west with its coast, Trieste and Romania’s Dobruja; towns the line cuts, such as Belgrade and Zagreb, are taken whole. With Greece and Türkiye it joins the two shores of the straits. About ${(CALIPH.sah.km2/1e6).toFixed(1)} million km².</p>`;
/* Version 229: V8 = V3 with all of Central Asia and the whole African continent (CALIPH.af, tools/v8_africa229.py) */
CX_LEAD.af = `<p>${CX_SPEC} <b>V6</b> is V2 with all of Central Asia and the whole African continent, every land whole: every African state from Morocco, Western Sahara and Mauritania to South Africa, with Ceuta and Melilla, and the islands on Africa’s shelf or counted in the UN’s African regions: the Canaries and Madeira, Cabo Verde, Saint Helena with Ascension and Tristan da Cunha, São Tomé and Príncipe, Madagascar, the Comoros, Mayotte, Réunion, Mauritius, the Seychelles, the Chagos Islands, the French Southern Territories and Italy’s Pelagie Islands and Pantelleria. It ends at the Strait of Gibraltar. About ${(CALIPH.af.km2/1e6).toFixed(1)} million km².</p>`;
/* Version 232: V9 = V8 with the European side of the Mediterranean (CALIPH.eu, tools/v9_med232.py) */
CX_LEAD.eu = `<p>${CX_SPEC} <b>V7</b> is V6 with the whole European side of the Mediterranean and the lands behind it, every land whole: Spain and Portugal with their islands, Andorra, France (its mainland with Corsica), Monaco, Italy with Sicily and Sardinia, San Marino, Malta, Switzerland, Liechtenstein, Austria, Slovakia, Hungary, Moldova, and the whole Balkan Peninsula (Slovenia, Croatia, Bosnia and Herzegovina, Serbia, Kosovo, Montenegro and Romania, with Greece, Bulgaria, Albania and North Macedonia). It holds every shore of the Mediterranean and its whole basin. About ${(CALIPH.eu.km2/1e6).toFixed(1)} million km².</p>`;
/* Version 189: V9 = all of V2 with the whole of North Africa (CALIPH.me9, tools/v9_north_africa189.py) */
CX_LEAD.me9 = `<p>${CX_SPEC} <b>V4</b> runs from the Atlantic to the Altai, every land whole. It holds V2 (without Bulgaria, Albania and North Macedonia) with the whole Greater Maghreb (al-Maghrib al-Kabīr: Morocco, Algeria, Tunisia, Libya, Mauritania and Western Sahara); all of Central Asia; West Africa from Senegal, the Gambia and Mali to Guinea, Guinea-Bissau, Sierra Leone and Liberia, so the whole Atlantic coast from Gibraltar to Liberia is inside; the Comoros and Mayotte (French, and claimed by the Comoros); and the whole Iberian Peninsula: Spain and Portugal with their islands, Andorra, the French Cerdagne on the Spanish side of the Pyrenees, Ceuta, Melilla and Gibraltar, that is al-Andalus, which the Umayyads held from 711. It holds the whole Greater Middle East, every Arab League member among them. About ${(CALIPH.me9.km2/1e6).toFixed(1)} million km².</p>`;

const CX_IRAQ = `<p><b>How I read "Greater Iraq".</b> Both readings are included: Khuzestan (al-Ahwāz), the modern irredentist claim, and ʿIrāq al-ʿAjam, the "Persian Iraq" of the later geographers, which is the old Jibāl of western Iran (Hamadān, Iṣfahān, Rayy, Qum, Qazvīn, Kirmānshāh). With the whole of Iran inside the outline, they add no land of their own; their names stay on the map to show where they lie.</p>`;
const CX_SRC = (nat, v3)=> `<p><b>What the sources say about the added lands.</b> The atlas finds no established sacred status for most of them; their place in Islamic history is conquest history, not a status. Ibn Kathīr, on 24:55, lists Cyprus among the lands taken in ʿUthmān's time; for Türkiye, the old Bilād al-Rūm${nat ? ' (in this version the Bosphorus is the line, so Istanbul’s European half is outside)' : ' with Istanbul on both sides of the Bosphorus'}, the hadith praise an army, not the land (al-Bukhārī 2924; Muslim 2897). Libya was conquered under the Rashidun from 642–643${v3 ? '' : '; Tunisia is the old Ifrīqiya, and Ibn Kathīr, on 24:55, counts Kairouan, in Tunisia, among the lands of the west conquered in ʿUthmān’s time'}, Greece was Ottoman for centuries, and northern Uganda (Equatoria) was held by Egypt under the Ottomans, 1870s–1889 (general knowledge). The rest of Uganda, and Kenya, Tanzania, Rwanda and Burundi, are inside only so that the whole Nile lies inside, at the author’s request; this atlas counts no caliphate’s rule there.${v3 ? " The island of Arwād off Ṭarṭūs was taken in ʿUthmān’s time (649–650) and razed; Muslims settled there only later, under Muʿāwiyah." : ''}${" Iran is the old land of Fāris and the Jibāl: Ibn Kathīr, on 24:55, describes most of Persia taken under ʿUmar, and Khurāsān and al-Ahwāz under ʿUthmān. The South Caucasus, the old Armenia and Arrān, has no status in the sources either, and most people in Georgia and Armenia are Christian." + " Derbent (Bāb al-Abwāb), the gate between the Caucasus and the Caspian, was taken in 22/643 under ʿUmar, as modern histories also date it (Ibn Kathīr’s note on 24:55 does not name it)." + " Turkmenistan, Afghanistan and Pakistan are roughly the old Khurāsān with part of Khwārazm, and al-Sind with its borderlands: Ibn Kathīr, on 24:55, names Khurāsān among the lands conquered under ʿUthmān, and modern historians date the conquest of Sind to the Umayyads, around 711–714 (the region names and the Sind date are from general knowledge)."}${v3 ? " In the west, Ibn Kathīr, on 24:55, says that under ʿUthmān “the lands of the west were conquered as far as Cyprus and Andalusia, Kairouan and Sebta” (Kairouan is in Tunisia, the old Ifrīqiya; Sebta is Ceuta, on Morocco’s north coast). Modern historians (general knowledge, not checked for this atlas) put the lasting conquest of the Maghrib beyond Ifrīqiya, and of al-Andalus, under the Umayyads (about 670–711), and count ʿUthmān’s western campaigns and the raid on Sicily (652) as raids rather than rule. Sicily and Malta came under the Aghlabids (from 827 and 870)" + (", and Transoxiana with Farghāna (Uzbekistan, Tajikistan and Kyrgyzstan) under the Umayyads, by Qutayba b. Muslim in the reign of al-Walīd I (705–715; this date checked in Wikipedia, “Muslim conquest of Transoxiana”)") + "." : ''} For al-Ḥabashah the Sunnah says the opposite of a claim: "Let the Abyssinians alone as long as they let you alone" (Abū Dāwūd 4302; ḥasan according to al-Albānī).</p>`;
/* V1: only the lands it holds beyond the best-lands outline; the wording is the same as in the larger versions' note */
const CX_SRC_ME = `<p><b>What the sources say about the added lands.</b> The atlas finds no established sacred status for them; their place in Islamic history is conquest history, not a status. For Türkiye, the old Bilād al-Rūm with Istanbul on both sides of the Bosphorus, the hadith praise an army, not the land (al-Bukhārī 2924; Muslim 2897). Iran is the old land of Fāris and the Jibāl: Ibn Kathīr, on 24:55, describes most of Persia taken under ʿUmar, and Khurāsān and al-Ahwāz under ʿUthmān. Libya was conquered under the Rashidun from 642–643 (general knowledge). For al-Ḥabashah (Ethiopia) the Sunnah says the opposite of a claim: "Let the Abyssinians alone as long as they let you alone" (Abū Dāwūd 4302; ḥasan according to al-Albānī). Sudan, South Sudan, Ethiopia and the lands of the White Nile’s sources (Uganda, Kenya, Tanzania, Rwanda and Burundi) are inside so that the whole Nile lies inside, at the author’s request; this atlas counts no caliphate’s rule south of Egypt except northern Uganda under Egypt in the Ottoman period (1870s–1889, general knowledge).</p>`;
const CX_SRC_ME8 = CX_SRC_ME.replace(/ Libya was conquered[\s\S]*<\/p>$/, '</p>');   /* the wide complete outline: Türkiye and Iran only; no Libya or Nile lands */
/* V4: V1's lines, and the Maghrib and Afghanistan and Pakistan, in the wording the larger versions use */
const CX_SRC_ME2 = CX_SRC_ME.replace('</p>', ` In the west, Ibn Kathīr, on 24:55, says that under ʿUthmān “the lands of the west were conquered as far as Cyprus and Andalusia, Kairouan and Sebta” (Kairouan is in Tunisia, the old Ifrīqiya; Sebta is Ceuta, on Morocco’s north coast); modern historians (general knowledge, not checked for this atlas) put the lasting conquest of the Maghrib beyond Ifrīqiya under the Umayyads (about 670–711). In the east, Afghanistan and Pakistan are roughly part of the old Khurāsān, and al-Sind with its borderlands: Ibn Kathīr, on 24:55, names Khurāsān among the lands conquered under ʿUthmān, and modern historians date the conquest of Sind to the Umayyads, around 711–714 (the region names and the Sind date are from general knowledge).</p>`);
/* ---------- V6 (Greater Middle East; Complete V2 before Version 66): the history of the added lands ---------- */
const V2U = (CALIPH.v2 && CALIPH.v2.units) || [];
/* Plain words for the province notes: the data file uses internal category names and map terms; the reader sees the names used in the key */
const PLAIN_V2 = t => t
  .replace(/'?\b(islamic_state_ruled|caliphate_ruled|via_dynasty)\b'?/g, (m, k) => `“${V2CAT[{islamic_state_ruled:'islamic', caliphate_ruled:'direct', via_dynasty:'dynasty'}[k]].label}”`)
  .replace(/'(temporary|influence|direct)'/g, (m, k) => `“${V2CAT[k].label}”`)
  .replace(/admin-1 polygons/g, 'regional areas').replace(/Morocco's admin-1/g, "Morocco's regions")
  .replace(/\bpolygons\b/g, 'areas').replace(/\bpolygon\b/g, 'area');
V2U.forEach(u=>{ ['label', 'notes', 'uncertain', 'adj'].forEach(k=>{ if(typeof u[k] === 'string') u[k] = PLAIN_V2(u[k]); }); });
const CONF = {high:'well attested', medium:'fairly sure', low:'uncertain'};
const v2sw = c => `<span class="v2sw c-${c}" aria-hidden="true"></span>`;
const V2_DEFS = `<p><b>How the added lands are shaded.</b> “Counted caliphates” are the same as everywhere in the atlas: the Rashidun, the Umayyads, the Abbasids, the Fatimids, the Umayyads of Córdoba, the Almohads, the Ottomans from 1517, and Sokoto. Each province gets the strongest tie it ever had, in this order:</p><ul class="v2defs">${Object.entries(V2CAT).map(([k,c])=>`<li>${v2sw(k)}<b>${c.label}</b>: ${c.tip}.</li>`).join('')}</ul><p>Muslims living in a land, or Islam spreading there, does not count as rule. A dotted edge on the map means the call is uncertain. Click a shaded province for its dates, rulers and sources.</p>`;
const v2Line = (u,i) => `<li>${v2sw(u.cat)}<button type="button" class="linkbtn v2go" data-v2u="${i}">${esc(u.label)}</button>: ${V2CAT[u.cat].label.toLowerCase()}${u.dates ? ` (${esc(u.dates)})` : ''}${u.conf === 'low' ? ' · <i>uncertain</i>' : ''}</li>`;
function v2History(){
  const C = (CALIPH.v2 && CALIPH.v2.countries) || [];
  return `<h3 class="v2h">How the added lands were held</h3>` + V2_DEFS + C.map(c=>`<div class="v2c"><p><b>${esc(c.n)}.</b> ${esc(c.summary)}</p><ul class="v2list">${V2U.map((u,i)=>[u,i]).filter(([u])=>u.a3 === c.a3).map(([u,i])=>v2Line(u,i)).join('')}</ul></div>`).join('')
    + `<p class="fine"><b>How this was checked.</b> Researched province by province on 7 October 2026 from Encyclopaedia Iranica, Encyclopaedia Britannica, the International Court of Justice (Western Sahara, 1975) and Wikipedia articles with the scholarship they cite; the sources are listed on each province’s note. No classical text was read directly; where a classical author is named, it is as quoted by a modern work. Seven calls were changed to follow the rules above, and each change is marked on the province’s note. The other core lands were not checked here.</p>`;
}
V2U.forEach((u,i)=>{
  const st = (u.states||[]).filter(x=>x.n).map(x=>`${esc(x.n)}${x.d ? ` (${esc(x.d)})` : ''}${x.r && x.r !== 'no' ? `, caliph: ${esc(x.r)}` : ''}`);
  const seen = new Set(), refs = (u.sources||[]).filter(x=>x.u && !seen.has(x.u) && seen.add(x.u)).map(x=>`<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t || x.u)}</a>${x.k === 'classical' ? ' (quotes a classical source)' : ''}`);
  INFO['v2u_'+i] = {title: u.label, src:[], body:
    `<p class="v2tag">${v2sw(u.cat)}<b>${V2CAT[u.cat].label}</b> · ${esc(u.country)} · ${CONF[u.conf] || u.conf} · about ${kmTxt(u.km2)} km²</p>`
    + (u.who ? `<p><b>Caliphate:</b> ${esc(u.who)}${u.dates ? ` <span class="fine">(${esc(u.dates)})</span>` : ''}${u.nominal ? ' <i>Only nominal or partial.</i>' : ''}</p>` : `<p><b>Caliphate:</b> none ruled it.</p>`)
    + (st.length ? `<p><b>Other Muslim rulers:</b> ${st.join('; ')}.</p>` : '')
    + (u.notes ? `<p>${esc(u.notes)}</p>` : '')
    + (u.adj ? `<p><b>Changed from the research:</b> ${esc(u.adj)}</p>` : '')
    + (u.uncertain ? `<p class="fine"><b>Not checked or unsure:</b> ${esc(u.uncertain)}</p>` : '')
    + `<p class="fine">Part of V8, the author’s specification. The shading is a historical summary, not a claim to the land.</p>`,
    refs};
});
const V2_B = [[-19.0,-13.0],[156.5,56.5]];   /* Version 219: the Canaries to Papua New Guinea */
const V3_B = [[-19.0,-12.0],[87.5,55.5]];   /* V3: the Canaries to Kyrgyzstan, southern Tanzania to the Aral Sea (Version 70: the Nile lands) */
const W2 = (()=>{ const u = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'], t = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']; return Array.from({length:100}, (_,n)=> n < 20 ? u[n] : t[Math.floor(n/10)] + (n%10 ? '-' + u[n%10] : '')); })();
const W2_OLD = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','twenty-one','twenty-two','twenty-three','twenty-four','twenty-five','twenty-six','twenty-seven','twenty-eight','twenty-nine','thirty','thirty-one','thirty-two','thirty-three','thirty-four','thirty-five','thirty-six','thirty-seven','thirty-eight','thirty-nine','forty','forty-one','forty-two','forty-three','forty-four','forty-five'];
const cxData = () => XV === 'sah' ? CALIPH.sah : XV === 'ca' ? CALIPH.ca : XV === 'eu' ? CALIPH.eu : XV === 'af' ? CALIPH.af : XV === 'me9' ? CALIPH.me9 : XV === 'me8' ? CALIPH.me8 : XV === 'me' ? CALIPH.me : XV === 'me2' ? CALIPH.me2 : XV === 'v2' ? CALIPH.v2 : XV === 'v3' ? CALIPH.x3 : CALIPH.x;
/* Version 66: the versions are numbered by size, from the smallest (V1) to the largest (V6; the old V7 was deleted in Version 155 and V3 in Version 157, at the author's request; the NEW V7 of Version 159, V2 plus four physical regions, was deleted in Version 169); the internal keys keep their old names */
const XNAME = {me8:'V1', me2:'V2', ca:'V3', me9:'V4', sah:'V5', af:'V6', eu:'V7', v2:'V8', me:'V2', full:'V3', v3:'V5'};
const XNUM = {me8:'V1', me2:'V2', ca:'V3', me9:'V4', sah:'V5', af:'V6', eu:'V7', v2:'V8', me:'V2', full:'V3', v3:'V5'};   /* Version 241: V2 (me), V4 (full) and V8 (x3/'v3') removed from the list at the author's request (data kept: the Super Caliphate is built on x3); the rest renumbered V1–V8 by size; the removed keys map to the nearest kept version */
const WIDEV = v => v === 'sah' || v === 'ca' || v === 'v2' || v === 'v3' || v === 'me2' || v === 'me9' || v === 'af' || v === 'eu';   /* the views that need the whole sheet */
const mkm = n => (n/1e6).toFixed(1);
function cxArea(){
  const d = cxData();
  if(XV === 'v2'){ const add = d.states.filter(s=>!s.core), sum = a => a.reduce((t,s)=>t+s.km2,0), tot = {};
    V2U.forEach(u=>{ tot[u.cat] = (tot[u.cat]||0) + u.km2; }); const all = Object.values(tot).reduce((a,b)=>a+b,0) || 1;
    return `<p><b>V8 view.</b> All of the wide complete outline it is built on, ${mkm(CALIPH.x3.km2)} million km² in ${CALIPH.x3.states.length} states and territories, with ${W2[add.length]} lands added, ${mkm(sum(add))} million km². Together, by my rough measurement, about ${mkm(d.km2)} million km² in ${d.states.filter(s=>!s.dup).length} states and territories. Of the added lands’ area: ${Object.keys(V2CAT).filter(k=>tot[k]).map(k=>`${V2CAT[k].label.toLowerCase()}, ${Math.round(100*tot[k]/all)}%`).join('; ')}. Most of what was never ruled by a caliphate is desert and steppe: the central Sahara, Mauritania and the Kazakh steppe.</p>`; }
  if(XV === 'v3'){ return `<p><b>the wide complete outline view.</b> By my rough measurement about ${mkm(d.km2)} million km² in ${d.states.filter(s=>s.pct!=null).length} present-day states and territories, many of whose people are not Muslim; the old Complete outline is ${mkm(CALIPH.x.km2)} million km² in ${CALIPH.x.states.length}. It holds every land of the Greater Middle East reference map the author supplied, Western Sahara (both parts), Mauritania and Kazakhstan included.</p>`; }
  const lead = `<b>${XNAME[XV]} view.</b>`;
  return `<p>${lead} By my rough measurement it covers about ${mkm(d.km2)} million km² in ${d.states.filter(s=>s.pct!=null).length} present-day states and territories, many of whose people are not Muslim.</p>`;
}
const row = s => `<tr><td>${s.n}${s.flag ? ` <small class="flag">${s.flag}</small>` : ''}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`;
function renderCX(){
  const d = cxData();
  INFO.caliphx.body = NAMES_P + RIVERS_P + CX_BODY.replace('%%LEAD%%', CX_LEAD[XV]).replace('%%IRAQ%%', CX_IRAQ).replace('%%SRC%%', XV === 'me' ? CX_SRC_ME : XV === 'me8' ? CX_SRC_ME8 : XV === 'me2' || XV === 'ca' || XV === 'me9' || XV === 'sah' || XV === 'af' || XV === 'eu' ? CX_SRC_ME2 : CX_SRC(false, XV !== 'full' && XV !== 'fullb')).replace('%%GC%%', () => XV === 'v2' ? v2History() : '').replace('%%AREA%%', cxArea());
  INFO.caliphx.title = XNAME[XV];
  document.querySelectorAll('.nx').forEach(el=>{ const n = d.states.filter(s=>!s.dup).length; el.textContent = W2[n] || n; });
  const tx = document.getElementById('caliphxrows');
  if(tx){
    if(XV === 'v2'){
      const add = d.states.filter(s=>!s.core);
      const hs = s => s.hs ? `<small class="hs">${Object.entries(s.hs).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${v2sw(k)}${V2CAT[k].label.replace(/^Ruled by a caliphate, directly$/,'ruled directly').replace(/^Ruled by a dynasty under a caliph$/,'dynasty under a caliph').replace(/^Ruled by other Islamic states only$/,'other Islamic states').replace(/^Tributary to a caliphate$/,'tributary').replace(/^Briefly held or raided only$/,'brief or raids').replace(/^Influence only$/,'influence only')} ${v}%`).join(' · ')}</small>` : '';
      tx.innerHTML = `<tr class="grp"><td colspan="3">The wide complete outline, all of it · ${CALIPH.x3.states.length} states and territories</td></tr>`
        + `<tr class="sub"><td>All of it, as listed there</td><td class="num">${kmTxt(CALIPH.x3.km2)}</td><td class="num">all of it</td></tr>`
        + `<tr class="grp g"><td colspan="3">Added · ${add.length} · how each was held, by area</td></tr>`
        + add.map(s=>`<tr><td>${s.n}${hs(s)}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`).join('')
        + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
    } else tx.innerHTML = d.states.map(row).join('') + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
  }
  const cap = document.getElementById('caliphxcap');
  if(cap) cap.textContent = `Present-day states and territories inside the outline, ${XNAME[XV]}. Areas are my rough measurement; every land listed whole includes all its islands.`;
  document.querySelectorAll('.lgx').forEach(el=>{ el.textContent = XNAME[XV]; });
  document.querySelectorAll('[data-xv]').forEach(b=>b.setAttribute('aria-pressed', b.dataset.xv === XV));
}
let natLineHTML = '';   /* filled in with the natural-line note, below */
let keyWasOpen = null;   /* the key folds away while a wide version (V2, V5, V6) is shown, and comes back after */
function setXV(v){
  if(!XNAME[v]) return;
  const lg = document.getElementById('legend');
  if(lg){ if(WIDEV(v) && XV !== v){ if(!WIDEV(XV)) keyWasOpen = lg.open; lg.open = false; } else if(!WIDEV(v) && WIDEV(XV) && keyWasOpen !== null){ lg.open = keyWasOpen; keyWasOpen = null; } }
  XV = v;
  CX.lk = CX.lk2(); const dd = CX.lod(XK(), cxLv()); [CX.clip, CX.wash].forEach(el=>el && el.attr('d', dd)); if(CX.dim) CX.dim.attr('d', CX.DIM_SHEET + dd);
  /* band and line follow in render (clipped close in) */
  renderCX();
  const h2 = infoEl.querySelector('h2'); if(h2 && /^(V[1-6]$|Your (complete )?outline|The complete outline|Core caliphate|Greater Caliphate|Complete Caliphate|Natural borders|Natural \+ political)/.test(h2.textContent)) showInfo('caliphx');
  applyLayers();
}
/* wide layout: the map takes the full page width and the notes move below it (desktop only) */
const atlasEl = document.getElementById('map-section'), wideBtn = document.getElementById('zwide');
const deskQ = window.matchMedia('(min-width:981px)');
function setWide(on, then){
  if(!deskQ.matches) on = false;
  const c = T.invert([W/2, H/2]);
  atlasEl.classList.toggle('wide', on); if(wideBtn) wideBtn.setAttribute('aria-pressed', on);
  requestAnimationFrame(()=>{ size(); wrapSel.call(zoom.transform, d3.zoomIdentity.translate(W/2 - T.k*c[0], H/2 - T.k*c[1]).scale(T.k)); update(); renderInsets(); if(then) then(); });
}
if(wideBtn) wideBtn.addEventListener('click', ()=>{ autoWide = false; setWide(!atlasEl.classList.contains('wide')); });

/* ---------- full-screen map ----------
   The map and its controls fill the whole screen. Where the browser allows it (desktop, Android) the real
   full-screen mode is used as well; on iPhone, where Safari keeps that for video only, the page itself fills the screen.
   Leave with the same button, Esc, or the phone's Back gesture. */
const fullBtn = document.getElementById('zfull'), openFullBtn = document.getElementById('fullbtn'), tipEl = document.getElementById('fulltip');
let wasWide = false, fullPushed = false, apiFull = false, tipShown = false, tipTimer, savedY = 0;
function keepCentre(){ const c = T.invert([W/2, H/2]), k = T.k;
  const run = ()=>{ size(); wrapSel.call(zoom.transform, d3.zoomIdentity.translate(W/2 - k*c[0], H/2 - k*c[1]).scale(k)); update(); renderInsets(); };
  requestAnimationFrame(()=>requestAnimationFrame(run)); }
function syncFullBtns(){ if(fullBtn){ fullBtn.setAttribute('aria-pressed', fullOn); const l = fullOn ? 'Leave full screen' : 'Full-screen map'; fullBtn.setAttribute('aria-label', l); fullBtn.title = l; } }
function enterFull(useApi){
  if(fullOn) return;
  fullOn = true; savedY = window.scrollY; wasWide = atlasEl.classList.contains('wide');
  if(wasWide){ atlasEl.classList.remove('wide'); if(wideBtn) wideBtn.setAttribute('aria-pressed', false); }
  closeSheets();
  atlasEl.classList.add('full'); document.documentElement.classList.add('fullmap'); syncFullBtns();
  /* Version 214: the page underneath goes to its very top while the map fills the screen (put back on leaving, savedY). The Claude
     app shows its own header see-through, floating over the map, only when the page is at the top; scrolled, it draws a solid white bar */
  window.scrollTo({top:0, left:0, behavior:'instant'});
  if(useApi){
    const rq = atlasEl.requestFullscreen || atlasEl.webkitRequestFullscreen;
    if(rq && (document.fullscreenEnabled || document.webkitFullscreenEnabled)){
      try { const p = rq.call(atlasEl, {navigationUI:'hide'}); if(p && p.catch) p.catch(()=>{}); } catch(e){}
    }
  }
  try { history.pushState({atlasFull:1}, ''); fullPushed = true; } catch(e){ fullPushed = false; }
  keepCentre();
  try { wrapEl.focus({preventScroll:true}); } catch(e){}
  /* a one-time hint on a phone held upright */
  if(tipEl && !tipShown && window.matchMedia('(max-width:760px) and (orientation:portrait)').matches){
    tipShown = true; tipEl.hidden = false; clearTimeout(tipTimer); tipTimer = setTimeout(()=>{ tipEl.hidden = true; }, 3400);
  }
}
function exitFull(fromPop){
  if(!fullOn) return;
  fullOn = false;
  if(document.fullscreenElement || document.webkitFullscreenElement){
    const ex = document.exitFullscreen || document.webkitExitFullscreen;
    try { const p = ex.call(document); if(p && p.catch) p.catch(()=>{}); } catch(e){}
  }
  apiFull = false;
  if(tipEl){ tipEl.hidden = true; clearTimeout(tipTimer); }
  /* without this the browser's scroll anchoring can throw the reader a screen or more past the map */
  const html = document.documentElement; html.style.overflowAnchor = 'none';
  atlasEl.classList.remove('full'); html.classList.remove('fullmap');
  const back = ()=>window.scrollTo({top:savedY, left:0, behavior:'instant'});
  back(); requestAnimationFrame(()=>{ back(); requestAnimationFrame(()=>{ back(); html.style.overflowAnchor = ''; }); });
  restoreUntil = Date.now() + 600;
  if(wasWide && deskQ.matches){ atlasEl.classList.add('wide'); if(wideBtn) wideBtn.setAttribute('aria-pressed', true); }
  if(!mobileQ.matches) closeSheets();
  syncFullBtns();
  if(fullPushed && !fromPop){ fullPushed = false; try { if(history.state && history.state.atlasFull) history.back(); } catch(e){} } else fullPushed = false;
  keepCentre();
}
let restoreUntil = 0;
function onFsChange(){ const el = document.fullscreenElement || document.webkitFullscreenElement;
  if(el === atlasEl) apiFull = true;
  else if(apiFull && fullOn){ apiFull = false; exitFull(); } }
document.addEventListener('fullscreenchange', onFsChange); document.addEventListener('webkitfullscreenchange', onFsChange);
window.addEventListener('popstate', ()=>{ if(fullOn) exitFull(true); else if(Date.now() < restoreUntil) window.scrollTo({top:savedY, left:0, behavior:'instant'}); });
if(fullBtn) fullBtn.addEventListener('click', ()=>{ fullOn ? exitFull() : enterFull(true); });
if(openFullBtn) openFullBtn.addEventListener('click', ()=>enterFull(true));
/* turning a phone (either way) while the map is on screen brings the whole map back into view */
let mapVis = false;
if('IntersectionObserver' in window) new IntersectionObserver(es=>{ mapVis = es[es.length-1].intersectionRatio > 0.3; }, {threshold:[0,.3,.6,1]}).observe(wrapEl);
if(shortQ.addEventListener) shortQ.addEventListener('change', ()=>{
  if(fullOn || !mapVis) return;
  setTimeout(()=>{ wrapEl.scrollIntoView({block:'center'}); }, 320);
});
/* the ring needs the room: widen on desktop; on a phone, fill the frame and let the reader pan */
/* the sheet is now large enough that every view fills the frame; only a reader's own zoom shows the sheet's edge */
let autoWide = false;   /* true while the page widened itself for a wide version (V2, V5, V6); the reader's own choice is kept */
/* the whole territory with a margin: the sheet now runs past it on every side */
function showWide(b){ b = b || (XV === 'v3' ? V3_B : XV === 'me2' ? ME2_B : XV === 'ca' ? CA_B : XV === 'me8' ? V8_B : XV === 'me9' || XV === 'sah' ? V9_B : XV === 'af' ? AF_B : XV === 'eu' ? EU_B : V2_B); if(deskQ.matches){ if(atlasEl.classList.contains('wide')) go(b); else { autoWide = true; setWide(true, ()=>go(b)); } } else go(b); }
function leaveAutoWide(then){ if(autoWide && atlasEl.classList.contains('wide')){ autoWide = false; setWide(false, then); } else { autoWide = false; if(then) then(); } }
const V8_B = [[24.5,11.5],[63.5,43.0]];   /* V8: Egypt to Iran, Yemen to the Caucasus (Version 187) */
const V9_B = [[-17.5,-12.0],[88.0,55.5]];   /* V5 (me9): with Central Asia to the Altai (Version 234) */
const AF_B = [[-18.0,-35.5],[88.0,55.5]];
const CA_B = [[8.0,-12.0],[88.0,55.5]];   /* V5 (ca): the Balkans and the Sahara to the Altai, Tanzania to Siberia (Version 237) */
const EU_B = [[-18.0,-35.5],[88.0,55.5]];   /* V9 (eu): as V8, with Europe to the Channel (Version 232) */   /* V8 (af): the Cape to Kazakhstan, the Atlantic coast to the Tian Shan (Version 229) */   /* V9: Mauritania's coast to Pakistan (Version 189) */
const ME2_B = [[-17.5,-12.0],[77.5,42.4]];   /* V4: Western Sahara's Atlantic coast to Pakistan's Kashmir, Yemen to the Black Sea (Version 68) */
const ME_B = [[9.0,-12.0],[63.6,42.4]];   /* V1, the Middle East with Libya: Libya's western border to Iran's eastern, Yemen to the Black Sea (Version 66) */
function openOutline(v){
  setXV(v); applyPreset('caliph');
  const done = ()=>{ showInfo('caliphx'); markSel(null); };
  if(WIDEV(v)){ showWide(); done(); } else leaveAutoWide(()=>{ go(v === 'me' ? ME_B : PRESETS.find(p=>p.id==='caliph').b); done(); });
  scrollToMap();
}
document.querySelectorAll('[data-xv]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation();
  const v = b.dataset.xv;
  if(!layerOn.caliphx && b.closest('.insec')){ openOutline(v); return; }
  const wasG = WIDEV(XV);
  /* Version 120: the outline cross-fades into the new version, and the view glides to frame it unless the reader is zoomed in close
     (then the view stays, so a detail can be compared between versions) */
  const swap = ()=>{ setXV(v); if(b.closest('.onmap')){ showInfo('caliphx'); markSel(null); }
    if(WIDEV(v)) showWide(); else if(wasG) leaveAutoWide(glide); else glide(); };
  const glide = ()=>{ const bb = v === 'me' ? ME_B : PRESETS.find(p=>p.id==='caliph').b, t = boundsT(bb, W, H);
    if(T.k < t.k * 2.5) go(bb); };
  const layers = [...document.querySelectorAll('[data-layer="caliphx"]')];
  if(reduced || v === XV || !layers.length || !layers[0].animate){ swap(); return; }
  const tok = ++xFadeTok, fade = (from, to, ms, ease, keep) => layers.forEach(el=>{ el.getAnimations().forEach(a=>a.cancel()); el.animate([{opacity:from},{opacity:to}], {duration:ms, easing:ease, fill:keep ? 'forwards' : 'none'}); });
  fade(1, 0.12, 140, 'ease-in', true);
  setTimeout(()=>{ if(tok !== xFadeTok) return; swap(); fade(0.12, 1, 320, 'ease-out', false); }, 140);   /* a later click wins */
}));
let xFadeTok = 0;
renderCX();
{ const tb = document.getElementById('caliphrows');
  if(tb) tb.innerHTML = CALIPH.states.map(s=>`<tr><td>${s.n}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`).join('')
    + `<tr class="tot"><td>Total</td><td class="num">about ${(CALIPH.km2/1e6).toFixed(1)} million</td><td></td></tr>`;
  const sb = document.getElementById('showcaliph'); if(sb) sb.addEventListener('click', ()=>{ applyPreset('caliph'); scrollToMap(); });
  document.addEventListener('click', e=>{ const a = e.target.closest('a.tosynth'); if(a){ e.preventDefault(); closeSheets(); document.getElementById('synth').scrollIntoView({behavior:reduced?'auto':'smooth', block:'start'}); } });
}

/* ---------------- regional index ---------------- */
/* the regions of the core caliphate (V5); V7's added regions went with V7 in Version 155 (the author's request) */
{ const el = document.getElementById('regioncards');
  if(el){
    const R = CALIPH.regions || [];
    const card = (r,i)=>`<article class="reg core">
      <header><span class="rk core">Core caliphate</span>
        <h3>${r.n}</h3>${r.ar ? `<div class="regar" lang="ar" dir="rtl">${r.ar}</div>` : ''}<div class="regen">${r.en}</div></header>
      <ul>${r.states.map(s=>`<li><span>${s.n}${s.flag ? ` <small class="flag">${s.flag}</small>` : ''}</span><span class="num">${kmTxt(s.km2)}</span></li>`).join('')}</ul>
      <footer><span class="num">about ${kmTxt(r.km2)} km²</span><button type="button" class="linkbtn" data-reg="${i}">Show on the map</button></footer>
    </article>`;
    el.innerHTML = `<h3 class="reggrp core">Core caliphate <small>the wide complete outline · ${mkm(CALIPH.x3.km2)} million km²</small></h3><div class="regrow r4">${R.map(card).join('')}</div>`;
    el.querySelectorAll('[data-reg]').forEach(btn=>btn.addEventListener('click', ()=>{
      const r = R[+btn.dataset.reg];
      if(!layerOn.caliphx) applyPreset('caliph');
      leaveAutoWide(()=>{ go(r.b); showInfo('caliphx'); markSel(null); });
      scrollToMap();
    }));
    const intro = document.querySelector('#regions .intro');
    const cap = w => w.charAt(0).toUpperCase() + w.slice(1);
    if(intro) intro.textContent = `${cap(W2[R.length])} regions, named as the classical geographers and chroniclers named them, with the present-day states in each. They make up the core caliphate (the wide complete outline on which V8, the Super Caliphate, is built). Tap a region to see it on the map. Areas are my rough measurement; classical names are approximate guides, not borders.`;
  } }
/* V6 (Greater Middle East; Complete V2 before Version 66): a province named in a note goes to that province on the map */
document.addEventListener('click', e=>{ const b = e.target.closest('.v2go'); if(!b) return; e.preventDefault();
  const i = +b.dataset.v2u, u = V2U[i]; if(!u) return;
  if(!layerOn.caliphx) applyPreset('caliph'); if(XV !== 'v2') setXV('v2');
  const [x0, y0, x1, y1] = u.b || [0, 0, 0, 0];   /* the province's box, from build.js */
  if(x1 > x0){ const px = Math.max(0.6, (x1-x0)*0.25), py = Math.max(0.6, (y1-y0)*0.25); go([[x0-px, y0-py],[x1+px, y1+py]]); }
  select('v2u_'+i); scrollToMap(); });

/* ---------- Dār al-Amān: natural borders and internal lines (the author’s design, 2026-10-07) ---------- */
{
  const mk = n => (n/1e6).toFixed(1);
  const shareTxt = c => c.pct >= 99 ? 'all' : c.pct >= 1 ? c.pct + '%' : 'under 1%';
  const inPct = id => (NAT.main.states.find(s=>s.id === id) || {pct:0}).pct;
  const cList = v => listAnd(NAT[v].states.map(c=>`${c.n.replace(/ \(.*\)$/, '')} (${shareTxt(c)}${c.id === '732' ? '; status internationally disputed' : ''})`));
  INFO.natb = {title:'The natural ring of Dār al-Amān', src:[], cert:'approx', body:`<p><b>The author’s design, not from the sources.</b> No classical geographer drew this line. It is one closed ring of natural features (coasts, rivers, cliffs, mountain crests and watersheds) drawn round the complete outline. The “Natural line” button draws it over any version of the outline.</p>
  <p><b>The ring, clockwise from the Adriatic.</b> Every stretch follows a natural feature (a river, a lake or sea shore, a crest, an escarpment or a watershed), and all are drawn the same way. Some are placed by hand and so only approximately (listed under “How it was drawn”); two of the links are low divides rather than high ground (see below). Where the ring runs at sea it is not drawn: the coast is the edge there, and the map’s own coastline shows it.</p>
  <ol class="natlegs">
    <li><b>Balkans.</b> From the Adriatic at Rijeka up the Rječina valley and over the Adriatic–Black Sea watershed by Risnjak to the spring of the Kupa; the Kupa past Karlovac to the Sava at Sisak; the Sava to Belgrade; the Danube to the Black Sea by its northern arm, the Chilia, so the whole Romanian delta and Dobruja are inside, and Thrace with them.</li>
    <li><b>Black Sea and Caucasus.</b> Across the Black Sea to the western end of the Greater Caucasus by Anapa; the main crest east to Bazardüzü; then down the Samur to the Caspian.</li>
    <li><b>Caspian and Aral.</b> Across the Caspian to the coast just north of the Garabogaz Gulf; the southern escarpment of the Ustyurt, round the north side of the Sarykamysh hollow and up the plateau’s eastern escarpment to the historic west shore of the Aral Sea; then the historic south shore east to the Amu Darya delta.</li>
    <li><b>Central Asia.</b> The Amu Darya upstream, then the Panj and its headwater the Pamir River to Lake Zorkul, and the short crest east to the Pamir knot, where Afghanistan, Tajikistan and China meet. The whole Wakhan is inside.</li>
    <li><b>Himalaya.</b> The rim of the Indus basin: the Karakoram crest to the Karakoram Pass; then north of the Shyok’s headwaters, west of the Pangong basin and north of the Indus into Tibet, round the Indus source and Kailash, east of Lake Manasarovar, and west round the head of the Karnali to the India–China border by Lipulekh; then north-west along the Sutlej–Ganges divide and over to the source of the Yamuna.</li>
    <li><b>India.</b> The Yamuna down past Delhi to the Chambal near Etawah; the Chambal up to its source near Mhow; west along the top of the Vindhya scarp on the Malwa Plateau to the source of the Mahi; the Mahi down to the Gulf of Khambhat.</li>
    <li><b>Seas.</b> Down the Gulf of Khambhat, across the Arabian Sea south of Socotra, past the Gulf of Aden, and down the Somali and Kenyan coast to the mouth of the Tana at Kipini.</li>
    <li><b>East Africa.</b> The Tana upstream past the south of Mount Kenya to its source on the Aberdares, so Mount Kenya lies inside; the Aberdare crest; across the Rift Valley on the divide between the basins of Lake Naivasha and Lake Nakuru, over the Eburru volcano; the crest of the Mau to Mau Summit; the Nyando river down to the head of the Winam Gulf; the north shore of Lake Victoria to Jinja; the Victoria Nile through Lake Kyoga to Lake Albert.</li>
    <li><b>Central Africa.</b> The Nile–Congo divide north-west from Lake Albert to the source of the Mbomou; the Mbomou and the Ubangi down to the Congo; the Congo to the mouth of the Sangha near Mossaka; the Sangha and its headwater the Mambéré upstream to the Yadé Massif; then west along the Adamawa Plateau to the source of the Benue.</li>
    <li><b>West Africa.</b> The Benue down to the Niger at Lokoja; the Niger upstream through its great bend to its source; over the Fouta Djallon to the source of the Bafing; the Bafing and the Senegal down to the sea at Saint-Louis.</li>
    <li><b>Atlantic and Mediterranean.</b> North along the Atlantic coast to Gibraltar, east through the Mediterranean between Africa and Europe, and up the Adriatic back to Rijeka.</li>
  </ol>
  <p><b>Notes on three stretches.</b> (a) <b>The Aral.</b> The ring follows the sea’s <i>historic</i> shoreline, as Natural Earth draws it before the sea shrank, not today’s much smaller lakes; most of what lies inside that old shore is now the dry Aralkum. (b) <b>The two watersheds</b>, the rim of the Indus basin and the Nile–Congo divide, are lines along high ground, where the land drains one way on one side and the other way on the other; they are not rivers. (c) <b>Through Kashmir</b> the ring follows the physical crest, the Karakoram and the rim of the Indus basin, not any political boundary: the Line of Control, the Line of Actual Control and the claims of India, Pakistan and China all lie inside it or cross it, and the ring takes no side among them.</p>
  <p><b>Islands.</b> The median-line rule: an island nearer to a shore inside the ring is inside. Distances run from each island to the nearest mainland shore inside and outside the ring, largest islands first, and an island of 5,000 km² or more, once decided, counts as a shore for smaller ones near it (so Sicily counts for Malta, and Madagascar for the Seychelles). Some islands are set by the specification instead. Inside: Crete, Rhodes and the Dodecanese, the other Greek islands, the Turkish islands, Cyprus, Pantelleria and Lampedusa, Kerkennah and Djerba, Bahrain and the other Gulf islands, Masirah, Socotra and Abd al-Kuri, the Dahlak and Farasan islands, the Lamu islands, most of the Croatian islands, and, by the rule, the Canary Islands and Madeira, which are nearer Africa than Europe. Outside: Sicily, Malta, Sardinia, Corsica, the Balearics, Cres and Lošinj (nearer Istria, which is outside), Cape Verde, Bioko, Zanzibar, Pemba, the Comoros, Madagascar and the Seychelles. Sardinia is the one island where the rule and the specification disagree: it is about 185 km from Tunisia and 190 km from mainland Italy, so the rule would put it inside by a hair; the specification puts it outside.</p>
  <p><b>The complete outlines and the ring.</b> The ring was drawn round the complete outline as it was then, trimmed back to the Victoria Nile between Murchison Falls and Lake Albert. The outlines now take in the whole Nile and Lake Victoria, so about 1.32 million km² of the Nile’s source lands (southern Uganda, Kenya, Tanzania, Rwanda and Burundi) lie outside the ring, which still follows the Victoria Nile and the Tana. Beyond those, the old Complete outline lies inside the ring except a strip of Turkmenistan on the Amu Darya’s north-east bank; the Khurāsān of the author’s maps beyond the Oxus (Uzbekistan, Tajikistan, Kyrgyzstan and the edges of Kazakhstan and China), at its widest and fullest: Transoxiana, Khwārazm, Isbījāb’s district, the lower Syr Darya, the Chu valley and Issyk-Kul, the Kashgar oasis, Manqishlāq and the Ustyurt; a strip of the Balkan Peninsula along its northern edge (about 14,000 km²); and the wide complete outline’s Dagestan block (about 12,000 km² of it). About 2.9 million km² of the old Complete outline lies outside it in all. About 5.46 million km² of the wide complete outline lies outside it: the Nile’s source lands, most of Kazakhstan, Iberia, Sicily and Malta, the rest of Central Asia and Dagestan. Western Sahara and Mauritania lie inside it.</p>
  <p><b>Size.</b> About ${mk(NAT.main.km2)} million km² of land (my rough measurement, without the seas and the two lakes). Inside: ${cList('main')}.</p>
  <p><b>How it was drawn.</b> Coasts, lakes, borders and rivers are from Natural Earth (1:10 million scale); the Aral’s old shore is from its historic-lakes file. Where a river of the ring is also a national border, the border line is used. No elevation data was available, so the watersheds follow borders that were defined on them (the Nile–Congo divide, the Karakoram, the Sutlej–Ganges divide) or were placed by hand from the shaded relief, the rivers and named places: the rest of the Indus rim through Ladakh and western Tibet, the watershed by Risnjak, the Kupa’s bend to Karlovac, the Ustyurt escarpment, the link to the Yamuna’s source, the Malwa link along the Vindhya scarp, the Aberdare, Eburru and Mau crests and the Nyando in Kenya, the Mambéré, the Yadé–Adamawa crest and the Fouta Djallon link. Treat these as approximate. Two links are low: the Eburru divide crosses the floor of the Rift Valley and the Malwa link runs over a plateau; both are real watersheds, not mountain barriers.</p>
  <p><b>Choices I made.</b> The Greater Caucasus crest ends at Bazardüzü, and from there the ring follows the Samur to the Caspian (the Russia–Azerbaijan border): the complete outline holds all of Azerbaijan, and the bare crest, which runs on to the Absheron, would cut off its northern slope. The Danube reaches the sea by the Chilia arm, the border with Ukraine. Across the Caspian the ring meets the coast just north of the Garabogaz Gulf, where the Kazakhstan–Turkmenistan border runs along the foot of the Ustyurt, so all of Turkmenistan west of the Amu Darya is inside, the Garabogaz with it. Up the Panj the ring takes the Pamir River, the border, to Lake Zorkul. The ring runs down the middle of the Gulf of Khambhat, so Saurashtra and Kutch are inside and Surat is outside. Western Sahara lies inside; its status is internationally disputed, and the map follows Natural Earth’s drawing of it as a separate territory. Spain (Ceuta, Melilla and the Canary Islands), Portugal (Madeira), Italy (Lampedusa and Pantelleria), Russia (the Black Sea coast south of the crest) and China (the upper Indus and Sutlej in western Tibet) appear in the table for small parts only.</p>`, refs:[]};
  /* the version's own note carries the same account of the line, without the opening paragraph and the size, which the version states for itself */
  natLineHTML = '<h3 class="v2h">How the line runs</h3>' + INFO.natb.body.split(/\n\s*(?=<p>)/).filter((x,i)=>i > 0 && !/^<p><b>Size\./.test(x)).join('');
  INFO.intl = {title:'Internal lines', src:[], cert:'approx', body:`<p><b>The author’s design, not from the sources.</b> Lighter lines inside Dār al-Amān: the Taurus divide between Anatolia, the Levant and Mesopotamia; the Nile, the Tigris and the Euphrates as the core waterways; and the Red Sea as the central axis joining the African and Arabian halves.</p>
  <p><b>How they were drawn.</b> The rivers come from Natural Earth: the White Nile, the Nile and its delta branches from the base map, and the Blue Nile from Natural Earth’s fuller rivers file, because the base map leaves it out. The Taurus line is my own series of points along the main crest, from the Lycian Taurus above Antalya to Hakkari; the Red Sea axis runs down the middle of the sea from the Gulf of Suez to Bāb al-Mandab. Both are approximate.</p>
  <p><b>History, for comparison.</b> In early Islamic times the Taurus was the frontier with Byzantium, held by the fortress zone the Arab sources call al-Thughūr and al-ʿAwāṣim; the Cilician Gates were the main pass. This is from general knowledge.</p>`, refs:[]};
  /* the natural borders are a version of the outline; the line alone can also be drawn over any version */
  const openLineOnly = ()=>{ if(!layerOn.caliphx) applyPreset('caliph'); setLayer('natb', true, true); go(NAT_B); showInfo('natb'); markSel(null); scrollToMap(); };
  addIx('V7', 'View', 'V6 with the whole European side of the Mediterranean: Iberia, France, Italy, Malta, the Alps and the whole Balkan Peninsula, every land whole · the author’s specification', 'v10 version 10 mediterranean europe iberia spain portugal france italy malta switzerland austria slovakia hungary moldova balkans serbia croatia bosnia romania andalus', ()=>openOutline('eu'), ['outline-v10']);
  addIx('V3', 'View', 'V2 with all of Central Asia (Kazakhstan, Uzbekistan, Kyrgyzstan and Tajikistan), every land whole · the author’s specification', 'v5 version 5 central asia kazakhstan uzbekistan kyrgyzstan tajikistan turkmenistan transoxiana steppe baikonur', ()=>openOutline('ca'), ['outline-v5']);
  addIx('V5', 'View', 'V4 with the whole Sahara: Niger, Burkina Faso and northern Chad (Borkou, Ennedi and Tibesti) added, and the Balkan Peninsula · the author’s specification', 'balkans balkan peninsula bulgaria bosnia albania kosovo serbia croatia montenegro macedonia v7 version 7 sahara sahel niger burkina faso chad tibesti borkou ennedi bet', ()=>openOutline('sah'), ['outline-v7']);
  addIx('V6', 'View', 'V2 with all of Central Asia and the whole African continent, every land whole, with Africa’s islands · the author’s specification', 'v9 version 9 africa all of africa whole africa african continent central asia kazakhstan uzbekistan kyrgyzstan tajikistan nigeria congo south africa madagascar angola ethiopia', ()=>openOutline('af'), ['outline-v9']);
  addIx('V4', 'View', 'V2 with all of Central Asia, the whole Greater Maghreb (Morocco, Algeria, Western Sahara and Mauritania added), Senegal, the Gambia, Mali, Guinea, Guinea-Bissau, Sierra Leone and Liberia, and the whole Iberian Peninsula · the author’s specification', 'v6 version 6 senegal gambia mali guinea guinea-bissau sierra leone liberia andorra cerdagne iberian peninsula central asia kazakhstan uzbekistan kyrgyzstan tajikistan turkmenistan greater maghreb maghrib north africa algeria morocco western sahara mauritania tunisia libya spain portugal iberia andalus al-andalus', ()=>openOutline('me9'), ['outline-v6']);
  addIx('V1', 'View', 'the sixteen states of the Middle East reference map, each whole, the smallest outline · the author’s specification', 'v1 version 1 middle east sixteen states reference map smallest turkey iran egypt arabia levant iraq', ()=>openOutline('me8'), ['outline-v1']);
  addIx('Natural line', 'View', 'one ring of coasts, rivers, crests and watersheds, drawn over any version · the author’s design', 'natural line overlay border ring natural borders kupa sava danube caucasus samur ustyurt aral amu darya panj pamir karakoram indus kailash sutlej yamuna chambal malwa mahi khambhat tana mount kenya aberdares mau victoria nile kyoga albert nile congo divide mbomou ubangi sangha mambere yade adamawa benue niger fouta djallon senegal gibraltar islands median line', openLineOnly, ['natural-line', 'natural-borders', 'natural-political', 'natural-libya']);
  addIx('Clean map', 'View', 'hide the numbered discs, dots, place names, key, captions, scale and coordinates while an outline shows', 'clean map hide numbers discs dots markers key legend labels captions scale compass coordinates uncluttered', ()=>{ if(!layerOn.caliphx) openOutline(XV); CLEAN = true; applyLayers(); scrollToMap(); }, ['clean-map']);
  addIx('Internal lines', 'View', 'the Taurus divide, the Nile, Tigris and Euphrates, the Red Sea axis · the author’s design', 'internal lines taurus nile tigris euphrates red sea axis', ()=>{ if(inNat()) INTL_OFF = false; else setLayer('intl', true, true); applyLayers(); go([[26,10],[50,40]]); showInfo('intl'); markSel(null); scrollToMap(); }, ['internal-lines']);
  addIx('Dār al-Amān', 'View', 'al-Khilāfa al-Amīna · the names chosen for the core caliphate', 'dar al aman darul aman khilafa amina amani amaniyyun caliphate name', ()=>openOutline('sah'), ['dar-al-aman']);
  addIx('al-Quds, capital of Dār al-Amān', 'Place', 'the author’s choice · Jerusalem', 'capital jerusalem quds', ()=>{ if(!layerOn.caliphx) openOutline(XV); go(near(QIBLA.aqsa, 1.2)); flash(QIBLA.aqsa); select('capital'); }, ['capital']);
  document.querySelectorAll('[data-lyt]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation();
    const id = b.dataset.lyt;
    if(inNat()){   /* in the natural-borders version the line is the border and cannot be switched off; the internal lines can */
      if(id === 'natb'){ showInfo('natb'); markSel(null); return; }
      INTL_OFF = !INTL_OFF; applyLayers(); if(!INTL_OFF){ showInfo('intl'); markSel(null); } return; }
    const on = !layerOn[id];
    setLayer(id, on, true); if(on){ showInfo(id); markSel(null); } }));
  document.querySelectorAll('[data-clean]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation(); CLEAN = !CLEAN; applyLayers(); }));
}
