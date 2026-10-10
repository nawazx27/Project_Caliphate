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
      <li>The jurists' Ḥijāz for the ruling on residence, taken from the atlas you shared and not re-read here, and the winter and summer journeys of Quraysh (106:2) as the tafsir describes them.</li>
    </ul>
    <p>These are explanations and reports, not revelation, and they often disagree.</p>`},
  tier_geo:{title:"What the classical geographers drew", src:["classical"], cert:null, body:`
    <p>From the 3rd century AH, geographers such as Ibn Ḥawqal, al-Iṣṭakhrī, Yāqūt and Abū al-Fidāʾ described each land by naming the places on its edges. Every region outline in this view is built from those places, which are the lettered circles (they appear as you zoom in).</p>
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
addIx('Your outline, to Iraq’s border', 'View', 'leaves out Iran, the Caucasus, Afghanistan and Pakistan · your specification', 'caliphate west iraq border version', ()=>openOutline('west'), ['outline-iraq']);
addIx('Core caliphate: your complete outline', 'View', 'with Iran, the Caucasus, Turkmenistan, Afghanistan and Pakistan · your specification', 'caliphate full version complete outline', ()=>openOutline('full'), ['outline-complete']);
addIx('Complete Caliphate V2', 'View', 'your complete outline with the lands on your Greater Middle East map · history by province', 'v2 version 2 complete caliphate v2 history ruled tributary maghrib morocco algeria tunisia libya mauritania western sahara kazakhstan uzbekistan turkmenistan kyrgyzstan tajikistan afghanistan pakistan', ()=>openOutline('v2'), ['outline-v2']);
addIx('Greater Caliphate', 'View', 'the core caliphate extended · your specification', 'greater caliphate gme greater middle east caliphate ring maghrib central asia afghanistan pakistan africa muslim majority sahel west africa mali niger chad burkina faso senegal gambia guinea bissau sierra leone comoros andalus spain portugal sicily sardinia corsica france paris andorra italy rome riviera nice monaco joined austria vienna slovenia croatia ukraine kyiv russia caucasus chechnya dagestan rostov volgograd astrakhan kalmykia stavropol malta greece balkans hungary romania crimea sokoto nigeria india bangladesh kashgar historical ruled', ()=>openOutline('gme'), ['outline-gme']);
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
  if(t === 'outline-greater') t = 'outline-gme';
  if(t === 'outline-max') t = 'outline-maximum';
  if(t === 'outline-complete' || t === 'outline-iraq' || t === 'outline-gme' || t === 'outline-v2' || t === 'outline-maximum') return run(()=>openOutline(t === 'outline-iraq' ? 'west' : t === 'outline-gme' ? 'gme' : t === 'outline-v2' ? 'v2' : t === 'outline-maximum' ? 'max' : 'full'));
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
  if(key === 'caliphx' || key === 'caliphg') tok = XV === 'west' ? 'outline-iraq' : XV === 'gme' ? 'outline-greater' : XV === 'v2' ? 'outline-v2' : XV === 'max' ? 'outline-maximum' : XV === 'nat' ? 'natural-borders' : XV === 'natp' ? 'natural-political' : 'outline-complete';
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
const pctTxt = s => s.pct >= 99 ? 'all of it' : s.pct < 1 ? 'under 1%' : `${s.pct}%`;  /* small islands are left off, so 99% reads as all */
const kmTxt = n => { const p = Math.pow(10, Math.max(0, Math.floor(Math.log10(n)) - 2)); return (Math.round(n/p)*p).toLocaleString('en'); };
const listAnd = a => a.length < 3 ? a.join(' and ') : a.slice(0,-1).join(', ') + ' and ' + a[a.length-1];
/* the Muslim-majority countries of Africa added to the Greater Caliphate, with Pew's 2020 share, read from the outline data */
const AFR = CALIPH.g.afr || [];
const theN = n => /^(Gambia|Comoros)$/.test(n) ? 'the ' + n : n;
const AFR_LIST = listAnd(AFR.slice().sort((a,b)=>b.pew-a.pew).map(a=>`${theN(a.n)} (${Math.round(a.pew)}%)`));
const AFR_NAMES = listAnd(AFR.map(a=>theN(a.n)));
const JOIN_BODY = `<p><b>Lands joined to the rest, at your request.</b> The ruled parts left gaps between them, so the Greater Caliphate also takes in the lands that join them up, in two rounds. First the western Mediterranean: the rest of Italy (central and northern Italy, with the north of Sardinia) and all of France beyond Septimania and Fraxinetum, with Corsica, Monaco, San Marino and Andorra, so that Iberia, France, Italy, Sicily, Sardinia and Corsica form one connected territory. Then the Balkans and the Black Sea: Austria, Slovenia and the rest of Croatia and Hungary, which join Italy to the Balkans and Hungary (Austria added later, at your request; the Ottomans besieged Vienna in 1529 and 1683 and raided Styria and Carinthia, but never ruled Austria), and the rest of Ukraine with the Southern and North Caucasus districts of Russia (Adygea, Astrakhan, Volgograd, Kalmykia, Rostov, Dagestan, Ingushetia, Kabardino-Balkaria, Karachay-Cherkessia, North Ossetia, Stavropol and Chechnya), which join the lands north of the Black Sea to the Kuban, the Caucasus and Kazakhstan around the north of the Caspian. The Caspian is now enclosed all round.</p><p><b>What is source and what is mine.</b> No caliphate in the counted list is known to have ruled the western Mediterranean lands added here: Sicily, Bari, Taranto and Calabria and the south of Sardinia were ruled, and Corsica is on the list of lands left out of the ruled parts as unconfirmed. In France only Septimania (Narbonne, about 719/720 to 759) and Fraxinetum (about 887 to 972) were ruled. Elsewhere the Umayyad armies only campaigned or held towns briefly: they were beaten at Toulouse in 721 and between Tours and Poitiers in 732, and Avignon and Arles submitted in 734 but were taken back by Charles Martel from 737. These were raids and short occupations, not rule, so the rest of France is marked as joined. For the Balkan and Black Sea lands I did not research the question again this round. Some of them may have been under an Ottoman or Crimean overlord at some time (my guess, from general knowledge: parts of the Ukrainian steppe, the Circassian and Kabardian lands, and the Sisak area of Croatia), but I have not checked it, so all of them stay in the joined group and out of the ruled one. The rule I used is mine, not the sources’: whole countries or whole districts, only as many as it takes for every land to touch the next by land. Switzerland, Slovakia’s west and the rest of Russia are not in; where the line stops is my choice, and you can move it. These lands are marked as your addition in the tables and on the map, and kept apart from the ruled lands.</p>`;
const AFR_BODY = `<p><b>The Muslim-majority countries of Africa.</b> The Greater Caliphate also takes in, whole, every African country not already in it where Muslims are more than half of the people in the Pew Research Center’s 2020 estimates: ${AFR_LIST}. This is a modern population test, not a historical one; the sources give these lands no status. Eritrea (52%) is already in the core. Left out: Côte d’Ivoire (46%) and Tanzania (30%), which fall below half in the same table, and Mayotte (a French department) and Zanzibar (part of Tanzania), which are not countries. Two of the eleven are close calls and are marked in the tables: Pew puts both Nigeria and Guinea-Bissau at 56%, but Nigeria has no recent official count of religion, and Guinea-Bissau’s 2009 census gave 45%, with later surveys near half. Read both as “about half”. I read Pew’s table through a page-summarising tool, not cell by cell in the PDF.</p>`;
Object.assign(INFO, {
  caliph:{title:"A caliphate of the best lands", src:[], cert:"uncertain", body:`
    <p><b>A thought experiment. This is my synthesis, not a ruling.</b> No text, early scholar or geographer drew this line. It is the smallest single territory that holds every land the sources give a status: al-Ḥijāz with the two ḥarams, al-Shām with Filasṭīn and al-Aqṣā, Sinai and al-Ṭūr, al-Yaman, and the Nile valley and Delta of Miṣr. Where the sources disagree on an edge, I took the widest reading.</p>
    <p>Najd, al-ʿIrāq, the Gulf, al-Ḥabashah and Bilād al-Rūm fall outside, because no status for them is established. The result is a ring around the Red Sea and up the Levant.</p>
    <p>By my rough measurement it covers about ${(CALIPH.km2/1e6).toFixed(1)} million km² in ${CALIPH.states.length} present-day states and territories: ${CALIPH.states.map(s=>`${s.n} (${pctTxt(s)})`).join(', ')}.</p>
    <p><a href="#synth" class="tosynth">What the texts say about the caliphate, and the limits of this outline</a></p>`,
    refs:[`<a href="https://quran.com/24:55" target="_blank" rel="noopener">Qur'an 24:55</a>`, sn('tirmidhi',2226,'Al-Tirmidhī 2226'), sn('abudawud',2535,'Abū Dāwūd 2535'), `<a href="https://dorar.net/h/R7HZBi1v" target="_blank" rel="noopener">The hadith of the stages (dorar.net)</a>`, `<a href="https://en.wikipedia.org/wiki/Letter_to_Baghdadi" target="_blank" rel="noopener">Letter to Baghdadi, 2014</a>`]}
});
Object.assign(INFO, {
  histreg:{title:'Historical region names', src:['classical'], cert:'uncertain', body:`<p>The names the classical geographers used for the lands around the core: al-Andalus and the three parts of al-Maghrib, Ifrīqiyah, Barqah and Fazzān; Bilād al-Sūdān, al-Nūbah and the coast of Bilād al-Zanj; Khurāsān, Mā warāʾ al-Nahr (the land beyond the Oxus), Khwārazm, Farghānah, Sijistān, Makrān and al-Sind; Ṭabaristān, Ādharbayjān, Arrān and Armīniyah; and, further out, al-Hind, Bilād al-Turk and Bilād al-Ṣīn.</p><p>They are drawn as names only, placed approximately. I did not re-read the geographers on their limits, so no edges are drawn.</p>`},
  caliphg:{title:"Greater Caliphate", src:[], cert:"uncertain", body:`<p><b>The core caliphate, extended.</b> Drawn to your specification as one territory in the core's colour: your complete outline, unchanged, with the Maghrib (Libya, Tunisia, Algeria, Morocco, Western Sahara, Mauritania), Central Asia (Kazakhstan, Uzbekistan, Turkmenistan, Kyrgyzstan, Tajikistan), Afghanistan and Pakistan, the Muslim-majority countries of Africa (${AFR_NAMES}), and every land beyond them that a caliphate once ruled, only the part that was ruled, with the lands that join them up (Italy, France, Slovenia, the Balkans, Ukraine and southern Russia, below). It is not from the sources and not a ruling.</p>${AFR_BODY}<p><b>Lands once ruled by caliphates.</b> al-Andalus (Spain, Portugal and Gibraltar, 711 to the 1230s); Septimania around Narbonne (719–759) and Fraxinetum in Provence (about 887–972); Sicily (827–1091), Bari, Taranto and Calabria (840s–880s), Sardinia's south (1015–16) and Malta (870–1091); Greece, with the Cretan emirate (about 827–961) and Ottoman rule to 1912; the Ottoman Balkans, Slavonia, Lika and Dalmatia, with Dubrovnik as a tributary; Ottoman Hungary (1541–1699) and southern and eastern Slovakia; Romania and Moldova as Ottoman provinces and vassals; southern Ukraine and Crimea (the Crimean Khanate, Yedisan and Podolia); the Kuban, Taman and Azov, and Derbent (Bāb al-Abwāb); the Sokoto Caliphate (1804–1903) in Nigeria, Niger, Burkina Faso, Cameroon and its fringes in Chad and the Central African Republic (Nigeria, Niger, Burkina Faso and Chad are now counted whole, above); Tibesti and Borkou (Ottoman garrisons, 1908–13); Equatoria in northern Uganda (Egypt under the Ottomans, 1870s–1889); the Delhi Sultanate at its height, invested by the Abbasid caliph in 1229, with Bengal; and Kashgaria in Xinjiang (the Karakhanids, who recognised the Abbasids, and an Ottoman vassal state in 1873–77). Each is labelled on the map with its caliphate and dates.</p>${JOIN_BODY}<p>The first additions follow the usual definition of the Greater Middle East, a modern geopolitical term; the historical additions come from the dynasty and province histories listed under Sources. The name is yours. The sources give none of these lands a sacred status; their place in Islamic history is conquest history.</p><p><a href="#regions" class="toregions">Regional index</a> · <a href="#synth" class="tosynth">the texts and the limits of these outlines</a></p>`, refs:[]},
  caliphx:{title:"Your complete outline", src:[], cert:"uncertain", body:`
    %%LEAD%%
    <p><b>Not an outline of the best lands.</b> The lands the sources honour are inside the black dotted line. Everything between that line and your outline is your addition.</p>
    <p><b>How I read the two "Greater" terms.</b> Greater Syria is taken as Syria, Lebanon, Jordan, Israel and Palestine, plus Bilād al-Shām's belt in Türkiye. "Greater Israel" is a term from Zionist maximalism and its critics, not an Islamic category; its widest reading runs from the Nile to the Euphrates. With all of Iraq and Egypt already in, neither term adds land of its own.</p>
    %%IRAQ%%
    %%SRC%%
    %%GC%%
    %%AREA%%
    <p><a href="#synth" class="tosynth">The texts, both outlines and their limits</a></p>`,
    refs:[sn('abudawud',4302,'Abū Dāwūd 4302'), sn('bukhari',2924,'Al-Bukhārī 2924'), sn('muslim',2897,'Muslim 2897'), sn('abudawud',2535,'Abū Dāwūd 2535'), `<a href="https://en.wikipedia.org/wiki/Letter_to_Baghdadi" target="_blank" rel="noopener">Letter to Baghdadi, 2014</a>`]}
});
/* ---------------- the versions of the user's outline ---------------- */
const CX_BODY = INFO.caliphx.body;
/* Dār al-Amān: the names you chose, and the capital */
const NAMES_P = `<p><b>Names, your choice.</b> The country is <b>Dār al-Amān</b> (<span lang="ar" dir="rtl">دار الأمان</span>), “the abode of safety”; its formal title is <b>al-Khilāfa al-Amīna</b> (<span lang="ar" dir="rtl">الخلافة الأمينة</span>), “the trustworthy caliphate”; its people are <b>Amānī</b> (plural Amāniyyūn); its capital is al-Quds (Jerusalem), marked with a star. None of these names comes from the sources. In classical law <i>amān</i> is a guarantee of safety given to a person; I found no classical text that uses Dār al-Amān as the name of a state. The province names on the map, and their short tags when zoomed out (ŠM, ḤJ, YM …), are the classical region names used across this atlas.</p>`;
INFO.capital = {title:'al-Quds · capital of Dār al-Amān', src:[], cert:'uncertain', body:`<p><b>Your choice, not from the sources.</b> You chose al-Quds (Bayt al-Maqdis, Jerusalem) as the capital of Dār al-Amān. The gold star and ring mark the city; al-Masjid al-Aqṣā keeps its own marker and notes.</p>
  <p><b>For comparison, where caliphs ruled from.</b> No caliphate had its capital at Jerusalem. The Prophet ﷺ and the first three caliphs ruled from Madinah, ʿAlī from Kufa, the Umayyads from Damascus, the Abbasids chiefly from Baghdad, the Fatimids from Ifrīqiya and then Cairo, the Umayyads of al-Andalus from Córdoba, the Almohads from Marrakesh, the Ottomans from Istanbul and the Sokoto Caliphate from Sokoto. Two links to the city and its province: Muʿāwiya is reported to have received the oath of allegiance as caliph at Jerusalem (Īliyāʾ) in 40/660, and the Umayyad caliph Sulaymān ruled from al-Ramla, the town he founded in Filasṭīn. These two points are from general knowledge; I have not checked them against the chronicles for this atlas.</p>${NAMES_P}`, refs:[]};
/* the parts of the outline note that differ between the three versions */
const CX_SPEC = '<b>Drawn to your specification. It is not from the sources, and not a ruling.</b>';
const CX_CORE = (iran)=> `the whole Arabian Peninsula; Greater Syria; Greater Israel in its widest reading; all of Iraq${iran ? ' and Iran, with Greater Iraq inside them' : ''}; all of Türkiye;${iran ? ' Georgia, Armenia and Azerbaijan, with Derbent (Bāb al-Abwāb) on the Caspian coast of Dagestan and the Samur valley between it and Azerbaijan (that strip is my drawing, so the land is one piece);' : ''} the whole island of Cyprus, and the island of Arwād off Ṭarṭūs (marked with a dot: it is too small for the base map); all of Egypt, Sudan, South Sudan, Somalia (with Somaliland), Ethiopia, Eritrea and Djibouti; and, at your request, all of Tunisia, Libya and Greece, with northern Uganda (Equatoria)${iran ? ', and all of Turkmenistan, Afghanistan and Pakistan (Pakistan as the base map draws it, with Azad Kashmir and Gilgit-Baltistan)' : ''}${iran ? '; from the map of the caliphate under ʿUthmān you shared, the Dagestan coast north of Derbent' : ''}; and, at your request, all of Algeria, Morocco (within its internationally recognised border: Western Sahara is not included), Spain and Portugal with their islands, Sicily with its islands, and Malta${iran ? ', and all of Uzbekistan and Tajikistan' : ''}`;
const CX_EGYPT = `<p><b>Lands Egypt once held, added at your request.</b> They come from a list of lands Egypt ruled, held or touched at different times, which you shared. Most of that list was already inside (Egypt and Sinai, Sudan with Darfur, South Sudan, the Eritrean and Somali coasts, Harar, the Levant, the Hejaz, Cilicia and Adana, Cyprus). New here: Cyrenaica, with the Libyan borderlands by Egypt (Ptolemaic, 4th to 1st century BC; the line follows today’s districts and takes in desert the Ptolemies did not hold); northern Uganda (Equatoria, Egypt under the Ottomans, 1870s–1889); Crete (Muḥammad ʿAlī’s Egypt, about 1830–1840); the Aegean islands (only some were Ptolemaic, such as the Cyclades and Samos; earlier there was only trade and tribute); and the Morea (Ibrāhīm Pasha’s campaign, 1825–1828, with Missolonghi in western Greece, 1826). Two cautions. Pharaonic and Ptolemaic rule was long before Islam and says nothing about a caliphate; and in Muḥammad ʿAlī’s time Egypt was itself an Ottoman province, so Crete and the Morea were already Ottoman lands. Egypt never held all of these at once. I checked the main dates against Wikipedia’s articles on Muḥammad ʿAlī, the Khedivate of Egypt and the Ptolemaic Kingdom: the Ptolemies held Cyrenaica and some Aegean islands from the late 4th century BC, losing most overseas lands in the 3rd; Egypt held the Hejaz from 1812 and Syria from 1831, and gave up Crete, the Hejaz and Syria in 1840. The Morea dates and Equatoria’s are from general knowledge. The Morea and western Greece do not touch the rest of the outline by land. <b>Then, at your request, all of Libya and all of Greece.</b> That takes in Tripolitania and the Fezzan and mainland Greece and the Ionian islands as well. Neither has a sacred status in the sources; their place in Islamic history is conquest history. Libya was conquered under the Rashidun from 642–643 and Greece was Ottoman for centuries, as the Greater Caliphate’s notes on the lands once ruled set out.</p>`;
const CX_LEAD = {
  v2: `<p>${CX_SPEC} <b>Complete Caliphate V2</b> is your complete outline with every land on the Greater Middle East map you shared added to it. That map (the same file as <i>reference/Greater_Middle_East_orthographic.svg</i>) adds four lands to the complete version: Western Sahara (both the part Morocco holds and the rest) and Mauritania; Kazakhstan and Kyrgyzstan. Every other land on it is already in the complete version: Libya, and, since you added them, Tunisia, Algeria, Morocco, Turkmenistan, Uzbekistan, Tajikistan, Afghanistan and Pakistan; their history is still set out below. The complete version holds the best-lands outline and adds ${CX_CORE(true)}. At your request it also takes in the islands of Corsica and Sardinia (Spain and Portugal, which it took in earlier, are now in the complete version). It also takes in, whole, the Muslim-majority countries of Africa not already inside: Chad, Mali, Niger, Nigeria, Burkina Faso, Guinea, Senegal, Sierra Leone, Guinea-Bissau, the Gambia and the Comoros. In Nigeria and Guinea-Bissau Muslims are about half the population, and estimates vary. On the map V2 is drawn in the same neutral colour as the complete version and the Greater Caliphate; how Muslim rulers actually held each land from your map, Libya, Tunisia, Turkmenistan, Afghanistan and Pakistan included, province by province, is set out below.</p>`,
  max: `<p>${CX_SPEC} <b>Maximum</b> is your complete outline with the lands on your list for its “maximum stable expansion” added to it. How I read each part of the list:</p>
  <ul class="maxlist">
  <li><b>The Greater Maghreb:</b> Mauritania, whole (Tunisia, Algeria and Morocco, also on your list, are now in the complete version). Western Sahara is taken too, because without it the coast would break between Morocco and Mauritania.</li>
  <li><b>The Sahel:</b> Chad, Niger, Mali and Senegal, whole, with the Gambia, which lies inside Senegal. <b>Northern Nigeria</b> is read as its twelve northern states (Sokoto, Kebbi, Zamfara, Katsina, Kano, Jigawa, Yobe, Borno, Bauchi, Gombe, Kaduna and Niger), the heart of the Sokoto Caliphate and of Bornu. Adamawa (the Yola emirate) and Kwara (the Ilorin emirate) were Sokoto emirates too but are left out.</li>
  <li><b>The Nile sources and the Swahili coast:</b> Uganda, Rwanda and Burundi, whole, and all the water of Lake Victoria. The coast is taken province by province: Kenya’s old Coast Province; Tanzania’s Tanga, Pwani, Dar es Salaam, Lindi and Mtwara, with Zanzibar and Pemba; and, at your choice, Mozambique’s Cabo Delgado, Nampula and Zambezia, down to the Zambezi. The rivers that feed Lake Victoria from Kenya and Tanzania (the Mara, the Nzoia and others) are not taken, and Lake Tanganyika is touched only along Burundi’s shore.</li>
  <li><b>Central Asia and the Caspian:</b> Kyrgyzstan, whole (Turkmenistan, Uzbekistan and Tajikistan, also on your list, are now in the complete version). Kazakhstan’s south (Mangystau, Kyzylorda, Turkistan, Zhambyl and Almaty, with Baikonur) and, for the Caspian basin, its west (Atyrau, West Kazakhstan and Aktobe). At your choice the whole Caspian drainage basin is inside, so the outline takes in the Russian provinces of the Volga, the Ural, the Terek and the Kuma: from Tver and Moscow down to Astrakhan and Dagestan, and east to Perm, Bashkortostan and Orenburg. The Caspian Sea itself is enclosed.</li>
  <li><b>The Indus:</b> Afghanistan and Pakistan, whole; both are now in the complete version, so here they add nothing of their own. Pakistan is drawn as the base map draws it, with Azad Kashmir and Gilgit-Baltistan; the Siachen Glacier and Indian-administered Kashmir stay out, and the edge is Pakistan’s border with India.</li>
  <li><b>Islands:</b> the Maldives and the Comoros are added. Crete, Socotra and Malta are already in the complete version.</li>
  </ul>
  <p><b>Approximate.</b> The part-countries are made of whole provinces, so their edges are province borders, not the exact lines on your list. The Caspian basin is the roughest: the hydrology data that traces drainage divides could not be reached from here. So a province is counted when a large part of it, roughly a third or more, drains to the Caspian. That takes in Volgograd, which lies mostly in the Don basin but carries the Volga to the sea, and Tambov, Oryol and Stavropol, which are split. It leaves out Vologda, Sverdlovsk and Chelyabinsk, which have only an edge in the basin. Almaty province reaches past the Tian Shan to Lake Balkhash. This version is not checked against the natural ring: Tanzania, Mozambique, Rwanda, Burundi, Kazakhstan, Kyrgyzstan and the Russian provinces lie outside it. Whether this expansion would be stable is your judgement; the atlas does not measure it.</p>`,
  full: `<p>${CX_SPEC} It holds the best-lands outline and adds ${CX_CORE(true)}.</p>${CX_EGYPT}`,
  west: `<p>${CX_SPEC} It holds the best-lands outline and adds ${CX_CORE(false)}. It stops at Iraq’s eastern border: Iran (with Khuzestan and ʿIrāq al-ʿAjam), Georgia, Armenia and Azerbaijan are left out, and so are Derbent and the Dagestan coast, Turkmenistan, Uzbekistan, Tajikistan, Afghanistan and Pakistan.</p>`,
  nat: `<p>${CX_SPEC} <b>Natural borders</b> redraws Dār al-Amān inside one ring of natural features (coasts, rivers, cliffs, mountain crests and watersheds) instead of today’s state borders. It is the ring you specified, starting from your complete outline: the ring goes round the outline and takes in a good deal more. Large parts of the complete outline, added after the ring was drawn, are outside it, about 1.24 million km² in all: Spain and Portugal with their islands (about 0.6 million km²); Uzbekistan, Tajikistan and the right (north-east) bank of the Amu Darya in Turkmenistan, which the ring follows (about 0.59 million km²; you chose to keep Turkmenistan whole rather than trim it to the river); Derbent, the Samur valley and the Dagestan coast, north of the Samur where the ring leaves the Caucasus crest for the Caspian (about 26,000 km²); and Sicily with its islands (about 26,000 km²). Clockwise from the Adriatic it runs up the Kupa and down the Sava and the Danube to the Black Sea, along the crest of the Greater Caucasus, across the Caspian to the Ustyurt escarpment and the old shore of the Aral, up the Amu Darya and the Panj to the Pamir knot, round the rim of the Indus basin by the Karakoram and Kailash, down the Yamuna, up the Chambal and down the Mahi to the Gulf of Khambhat, by sea to the Tana, past Mount Kenya, over the Aberdares, the Eburru divide and the Mau, and down the Nyando to Lake Victoria, down the Victoria Nile to Lake Albert, along the Nile–Congo divide, the Mbomou, the Ubangi, the Sangha and the Mambéré, over the Adamawa, down the Benue, up the Niger, over the Fouta Djallon and down the Senegal, and by the Atlantic and the Mediterranean back to the Adriatic. The natural line, with Gibraltar marked on it, and the internal lines come with it.</p>`,
  natp: `<p>${CX_SPEC} <b>Natural + political</b> starts from the natural ring and makes every edge a border that states already recognise. Wherever the ring cuts a present-day state in two, that state is taken whole if more than half of it lies inside the ring and left out whole if not; every state in your complete outline is taken whole (Uganda among them, with 48% inside the ring), except Russia and Italy, of which the complete outline holds only small parts (Derbent with the Dagestan coast, and Sicily); so Spain, Portugal, Uzbekistan, Tajikistan and Malta are taken whole, though the ring itself barely touches them. So every edge here is an international border or a coast. The natural ring is drawn with it for comparison.</p>`,
  gme: `<p>${CX_SPEC} The Greater Caliphate is the whole core caliphate, drawn in the same colour as one territory, extended to the rest of the Maghrib (Western Sahara and Mauritania; Libya, Tunisia, Algeria and Morocco are in the core), the rest of Central Asia (Kazakhstan and Kyrgyzstan; Turkmenistan, Uzbekistan, Tajikistan, Afghanistan and Pakistan are in the core), to the Muslim-majority countries of Africa (${AFR_NAMES}), and to every land beyond them that a caliphate once ruled, taking only the part that was ruled, with Austria, Slovenia, Andorra and the rest of Italy, France, Croatia, Hungary, Ukraine and the south of Russia added to join those lands up. The core it contains holds the best-lands outline and adds ${CX_CORE(true)}.</p>`
};
const CX_IRAQ = {
  in: `<p><b>How I read "Greater Iraq".</b> You chose both readings: Khuzestan (al-Ahwāz), the modern irredentist claim, and ʿIrāq al-ʿAjam, the "Persian Iraq" of the later geographers, which is the old Jibāl of western Iran (Hamadān, Iṣfahān, Rayy, Qum, Qazvīn, Kirmānshāh). With the whole of Iran inside the outline, they add no land of their own; their names stay on the map to show where they lie.</p>`,
  out: `<p><b>How I read "Greater Iraq".</b> You chose both readings: Khuzestan (al-Ahwāz) and ʿIrāq al-ʿAjam, the old Jibāl of western Iran. Both lie in today’s Iran, so this version leaves them out; the complete version includes them.</p>`
};
CX_IRAQ.nat = `<p><b>How I read "Greater Iraq".</b> You chose both readings: Khuzestan (al-Ahwāz) and ʿIrāq al-ʿAjam, the old Jibāl of western Iran. Both lie inside the natural line, and so does the rest of Iran: the line runs far beyond Iran’s eastern border, so Khurāsān (with Mashhad) and Sīstān are inside this version.</p>`;
const CX_SRC = (iran, nat)=> `<p><b>What the sources say about the added lands.</b> The atlas finds no established sacred status for most of them. Ibn Kathīr, on 24:55, lists Cyprus among the lands taken in ʿUthmān's time; for Türkiye, the old Bilād al-Rūm${nat ? ' (in this version the Bosphorus is the line, so Istanbul’s European half is outside)' : ' with Istanbul on both sides of the Bosphorus'}, the hadith praise an army, not the land (al-Bukhārī 2924; Muslim 2897). The island of Arwād off Ṭarṭūs, taken and garrisoned in ʿUthmān’s time according to your brief (not checked by me), is too small for the base map and is marked with a dot. Tunisia, roughly the old Ifrīqiya, has none either: Ibn Kathīr, on 24:55, names Kairouan among the lands of the west conquered under ʿUthmān (the name Ifrīqiya for Tunisia is from general knowledge).${iran ? " Iran is the old land of Fāris and the Jibāl: Ibn Kathīr, on 24:55, describes most of Persia taken under ʿUmar, and Khurāsān and al-Ahwāz under ʿUthmān. The South Caucasus, the old Armenia and Arrān, has no status in the sources either, and most people in Georgia and Armenia are Christian. Derbent (Bāb al-Abwāb), the gate between the Caucasus and the Caspian, was taken in 22/643 under ʿUmar and held under ʿUthmān, as the brief you sent says (its sources are modern Arabic works; I have not checked them, and Ibn Kathīr’s note on 24:55 does not name Derbent). Turkmenistan, Afghanistan and Pakistan, roughly the old Khurāsān with part of Khwārazm, and al-Sind with its borderlands, have no status in the sources either: Ibn Kathīr, on 24:55, names Khurāsān among the lands conquered under ʿUthmān, and modern historians date the conquest of Sind to the Umayyads, around 711–714 (the region names and the Sind date are from general knowledge)." : ''} The lands from your map of the caliphate under ʿUthmān: Ibn Kathīr, on 24:55, says that under ʿUthmān “the lands of the west were conquered as far as Cyprus and Andalusia, Kairouan and Sebta” (Sebta is Ceuta, on Morocco’s north coast). Modern historians, as far as I know (general knowledge, not checked for this atlas), put the lasting conquest of the Maghrib beyond Ifrīqiya, and of al-Andalus, under the Umayyads (about 670–711), and count ʿUthmān’s western campaigns and the raid on Sicily (652) as raids rather than rule; your map’s light green seems to mark that difference. Both shades are inside the outline now, traced approximately from your map. al-Andalus (Spain and Portugal), Sicily and Malta, and Transoxiana (Uzbekistan and Tajikistan), which you added whole, entered Islamic rule after the Rashidun: al-Andalus and Transoxiana under the Umayyads (from 711, and about 705–715), Sicily and Malta under the Aghlabids (from 827 and 870), as the Greater Caliphate’s notes set out; none of them has a status in the sources. That is conquest history, not a status. For al-Ḥabashah the Sunnah says the opposite of a claim: "Let the Abyssinians alone as long as they let you alone" (Abū Dāwūd 4302; ḥasan according to al-Albānī).</p>`;
const CX_GC = `<p><b>Where the Greater Caliphate’s edge comes from.</b> Sudan, South Sudan, the Horn and the Caucasus are already in the core. The first additions follow the usual definition of the Greater Middle East, a modern geopolitical term (used notably for the 2004 G8 initiative on the “Broader Middle East and North Africa”), as in the reference map you shared; the name Greater Caliphate is yours.</p>
    ${AFR_BODY}
    <p><b>Lands once ruled by caliphates.</b> Spain, Portugal, Sicily and Malta among them are now part of the core, at your request. Beyond those, the outline takes in the part of every land that a caliphate, or a dynasty formally under a caliph, once ruled: al-Andalus (Spain, Portugal and Gibraltar, 711 to the 1230s); Septimania around Narbonne (719–759) and Fraxinetum in Provence (about 887–972); Sicily (827–1091), Bari, Taranto and Calabria (840s–880s), Sardinia's south (1015–16) and Malta (870–1091); Greece, with the Cretan emirate (about 827–961) and Ottoman rule to 1912; the Ottoman Balkans, Slavonia, Lika and Dalmatia, with Dubrovnik as a tributary; Ottoman Hungary (1541–1699) and southern and eastern Slovakia; Romania and Moldova as Ottoman provinces and vassals; southern Ukraine and Crimea (the Crimean Khanate, Yedisan and Podolia); the Kuban, Taman and Azov, and Derbent (Bāb al-Abwāb); the Sokoto Caliphate (1804–1903) in Nigeria, Niger, Burkina Faso, Cameroon and its fringes in Chad and the Central African Republic (Nigeria, Niger, Burkina Faso and Chad are counted whole, above, so only Cameroon and the Central African Republic add land here); Tibesti and Borkou (Ottoman garrisons, 1908–13); Equatoria in northern Uganda (Egypt under the Ottomans, 1870s–1889); the Delhi Sultanate at its height, invested by the Abbasid caliph in 1229, with Bengal; and Kashgaria in Xinjiang (the Karakhanids, who recognised the Abbasids, and an Ottoman vassal state in 1873–77). Counted: the Rashidun, Umayyad, Abbasid, Fatimid, Córdoba and Almohad caliphates, the Ottomans from 1517, when they took the caliphal title, and the Sokoto Caliphate. Ruled parts were traced from today's province boundaries and are approximate. Left out as disputed or unconfirmed: Corsica (as a ruled land; it is inside the outline only as one of the joined lands, below), the Garigliano camp and the Alpine passes in Italy, Dār Fertit and the edge of Equatoria in the Congo. Left out as allegiance without rule: Aceh in Indonesia (1564), the Swahili towns of Kenya (1585–89) and Volga Bulgaria (922). Crimea is counted separately in the table: Russia annexed it in 2014, and most states recognise it as Ukraine.</p>
    ${JOIN_BODY}
    <p><b>What the sources say.</b> They give these lands no sacred status either: Ibn Kathīr, on 24:55, describes ʿUthmān's conquests reaching Cyprus, al-Andalus, Kairouan and Sebta in the west and Khurāsān in the east; modern historians date the conquest of al-Andalus, like those of Transoxiana and Sind, to the Umayyad period, around 705–715.</p>`;
/* ---------- Complete Caliphate V2: the history of the added lands ---------- */
const V2U = (CALIPH.v2 && CALIPH.v2.units) || [];
const CONF = {high:'well attested', medium:'fairly sure', low:'uncertain'};
const v2sw = c => `<span class="v2sw c-${c}" aria-hidden="true"></span>`;
const V2_DEFS = `<p><b>How the added lands are shaded.</b> “Counted caliphates” are the same as everywhere in the atlas: the Rashidun, the Umayyads, the Abbasids, the Fatimids, the Umayyads of Córdoba, the Almohads, the Ottomans from 1517, and Sokoto. Each province gets the strongest tie it ever had, in this order:</p><ul class="v2defs">${Object.entries(V2CAT).map(([k,c])=>`<li>${v2sw(k)}<b>${c.label}</b>: ${c.tip}.</li>`).join('')}</ul><p>Muslims living in a land, or Islam spreading there, does not count as rule. A dotted edge on the map means the call is uncertain. Click a shaded province for its dates, rulers and sources.</p>`;
const v2Line = (u,i) => `<li>${v2sw(u.cat)}<button type="button" class="linkbtn v2go" data-v2u="${i}">${esc(u.label)}</button>: ${V2CAT[u.cat].label.toLowerCase()}${u.dates ? ` (${esc(u.dates)})` : ''}${u.conf === 'low' ? ' · <i>uncertain</i>' : ''}</li>`;
function v2History(){
  const C = (CALIPH.v2 && CALIPH.v2.countries) || [];
  return `<h3 class="v2h">How the lands from your map were held</h3>` + V2_DEFS + C.map(c=>`<div class="v2c"><p><b>${esc(c.n)}.</b> ${esc(c.summary)}</p><ul class="v2list">${V2U.map((u,i)=>[u,i]).filter(([u])=>u.a3 === c.a3).map(([u,i])=>v2Line(u,i)).join('')}</ul></div>`).join('')
    + `<p class="fine"><b>How this was checked.</b> Researched province by province on 7 October 2026 from Encyclopaedia Iranica, Encyclopaedia Britannica, the International Court of Justice (Western Sahara, 1975) and Wikipedia articles with the scholarship they cite; the sources are listed on each province’s note. No classical text was read directly this round; where a classical author is named, it is as quoted by a modern work. I changed seven of the researchers’ calls where they did not follow the rules above, and each change is marked on the province’s note. The other core lands of the complete version were not checked here.</p>`;
}
V2U.forEach((u,i)=>{
  const st = (u.states||[]).filter(x=>x.n).map(x=>`${esc(x.n)}${x.d ? ` (${esc(x.d)})` : ''}${x.r && x.r !== 'no' ? `, caliph: ${esc(x.r)}` : ''}`);
  const seen = new Set(), refs = (u.sources||[]).filter(x=>x.u && !seen.has(x.u) && seen.add(x.u)).map(x=>`<a href="${esc(x.u)}" target="_blank" rel="noopener">${esc(x.t || x.u)}</a>${x.k === 'classical' ? ' (quotes a classical source)' : ''}`);
  INFO['v2u_'+i] = {title: u.label, src:[], body:
    `<p class="v2tag">${v2sw(u.cat)}<b>${V2CAT[u.cat].label}</b> · ${esc(u.country)} · ${CONF[u.conf] || u.conf} · about ${kmTxt(u.km2)} km²</p>`
    + (u.who ? `<p><b>Caliphate:</b> ${esc(u.who)}${u.dates ? ` <span class="fine">(${esc(u.dates)})</span>` : ''}${u.nominal ? ' <i>Only nominal or partial.</i>' : ''}</p>` : `<p><b>Caliphate:</b> none ruled it.</p>`)
    + (st.length ? `<p><b>Other Muslim rulers:</b> ${st.join('; ')}.</p>` : '')
    + (u.notes ? `<p>${esc(u.notes)}</p>` : '')
    + (u.adj ? `<p><b>My change to the research:</b> ${esc(u.adj)}</p>` : '')
    + (u.uncertain ? `<p class="fine"><b>Not checked or unsure:</b> ${esc(u.uncertain)}</p>` : '')
    + `<p class="fine">Part of Complete Caliphate V2, your specification. The shading is a historical summary, not a claim to the land.</p>`,
    refs};
});
const V2_B = [[-19.0,-13.0],[89.0,56.5]];
const MAX_B = [[-19.0,-19.5],[80.0,61.5]];   /* Senegal to the Tian Shan, the Zambezi to Perm and Kirov */   /* Mauritania to the Altai, the Horn to the north of Kazakhstan */
const W2 = (()=>{ const u = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'], t = ['','','twenty','thirty','forty','fifty','sixty','seventy','eighty','ninety']; return Array.from({length:100}, (_,n)=> n < 20 ? u[n] : t[Math.floor(n/10)] + (n%10 ? '-' + u[n%10] : '')); })();
const W2_OLD = ['zero','one','two','three','four','five','six','seven','eight','nine','ten','eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen','twenty','twenty-one','twenty-two','twenty-three','twenty-four','twenty-five','twenty-six','twenty-seven','twenty-eight','twenty-nine','thirty','thirty-one','thirty-two','thirty-three','thirty-four','thirty-five','thirty-six','thirty-seven','thirty-eight','thirty-nine','forty','forty-one','forty-two','forty-three','forty-four','forty-five'];
const cxData = () => XV === 'west' ? CALIPH.xw : XV === 'gme' ? CALIPH.g : XV === 'v2' ? CALIPH.v2 : XV === 'max' ? CALIPH.m : XV === 'nat' ? NAT.main : XV === 'natp' ? NAT.pol : CALIPH.x;
const WIDEV = v => v === 'gme' || v === 'v2' || v === 'max' || v === 'nat' || v === 'natp';   /* the views that need the whole sheet */
const mkm = n => (n/1e6).toFixed(1);
function cxArea(){
  const d = cxData();
  if(XV === 'v2'){ const add = d.states.filter(s=>!s.core), sum = a => a.reduce((t,s)=>t+s.km2,0), tot = {};
    V2U.forEach(u=>{ tot[u.cat] = (tot[u.cat]||0) + u.km2; }); const all = Object.values(tot).reduce((a,b)=>a+b,0) || 1;
    return `<p><b>Complete Caliphate V2 view.</b> The whole complete version, ${mkm(CALIPH.x.km2)} million km² in ${CALIPH.x.states.length} states and territories, with ${W2[add.length]} lands added from your map, ${mkm(sum(add))} million km². Together, by my rough measurement, about ${mkm(d.km2)} million km² in ${d.states.filter(s=>!s.dup).length} states and territories. Of the added lands’ area: ${Object.keys(V2CAT).filter(k=>tot[k]).map(k=>`${V2CAT[k].label.toLowerCase()}, ${Math.round(100*tot[k]/all)}%`).join('; ')}. Most of what was never ruled by a caliphate is desert and steppe: the central Sahara, Mauritania and the Kazakh steppe.</p>`; }
  if(XV === 'max'){ const wh = d.states.filter(s=>s.add === 'whole'), pt = d.states.filter(s=>s.add && s.add !== 'whole'), sum = a => a.reduce((t,s)=>t+s.km2,0);
    return `<p><b>Maximum view.</b> The whole complete version, ${mkm(CALIPH.x.km2)} million km² in ${CALIPH.x.states.length} states and territories, with ${W2[wh.length]} lands added whole and ${W2[pt.length]} in part. Together, by my rough measurement, about ${mkm(d.km2)} million km² in ${d.states.length} present-day states and territories, many of whose people are not Muslim. The Caspian Sea, which it now encloses, is not counted; the water of Lake Victoria is.</p>`; }
  if(XV === 'nat'){ const xs = new Map(CALIPH.x.states.map(s=>[s.id, s])), ns = new Map(d.states.map(s=>[s.id, s]));
    const w = s => s.pct >= 99 ? 'all' : s.pct < 1 ? 'under 1%' : s.pct + '%';
    const added = d.states.filter(s=>!xs.has(s.id)), dropped = CALIPH.x.states.filter(s=>!ns.has(s.id)).map(s=>s.n.replace(/ \(.*\)$/, '')),
      cut = d.states.filter(s=>xs.has(s.id) && s.pct <= xs.get(s.id).pct - 2), more = d.states.filter(s=>xs.has(s.id) && s.pct >= xs.get(s.id).pct + 10);
    const li = a => listAnd(a.map(s=>`${s.n.replace(/ \(.*\)$/, '')} (${w(s)})`));
    return `<p><b>Natural borders view.</b> Dār al-Amān inside the natural ring: by my rough measurement about ${mkm(d.km2)} million km² of land in ${d.states.length} present-day states and territories, many of whose people are not Muslim. The seas the ring takes in (the Red Sea, the Persian Gulf, the eastern Mediterranean and the Aegean, and the southern Black Sea and Caspian) are not counted in the area, and neither is the water of Lake Victoria and Lake Albert.</p>
    <p><b>Compared with your complete outline</b> (${mkm(CALIPH.x.km2)} million km²). It adds ${added.length ? li(added) : 'no whole state'}${dropped.length ? `; it leaves out ${listAnd(dropped)} altogether` : ''}${more.length ? `; it takes more of ${li(more)}` : ''}${cut.length ? `; it takes only part of ${li(cut)}` : ''}. The percentages are the share of each state inside the line.</p>`; }
  if(XV === 'natp'){ const ns = new Map(NAT.main.states.map(s=>[s.id, s]));
    const taken = d.states.filter(s=>ns.has(s.id) && ns.get(s.id).pct < 100), out = NAT.main.states.filter(s=>!d.states.some(x=>x.id === s.id));
    return `<p><b>Natural + political view.</b> About ${mkm(d.km2)} million km² of land in ${d.states.length} whole present-day states and territories (the natural ring alone: ${mkm(NAT.main.km2)} million in ${NAT.main.states.length}). Taken whole, though the ring cuts them: ${listAnd(taken.map(s=>`${s.n} (${ns.get(s.id).pct}% inside the ring)`))}. Left out, though the ring takes part of them: ${listAnd(out.map(s=>`${s.n.replace(/ \(.*\)$/, '')} (${s.pct < 1 ? 'under 1%' : s.pct + '%'})`))}.</p>`; }
  if(XV === 'gme'){ const gA = d.states.filter(s=>!s.core && !s.afr && !s.hist && !s.join), fA = d.states.filter(s=>s.afr), hA = d.states.filter(s=>s.hist), jA = d.states.filter(s=>s.join), sum = a => a.reduce((t,s)=>t+s.km2,0);
    return `<p><b>Greater Caliphate view.</b> The whole core caliphate, ${mkm(CALIPH.x.km2)} million km² in ${CALIPH.x.states.length} states and territories, is part of it, drawn in the same colour. The Greater Caliphate adds the rest of the Maghrib and of Central Asia, ${mkm(sum(gA))} million km² in ${gA.length} states, the ${W2[fA.length]} Muslim-majority countries of Africa, whole, ${mkm(sum(fA))} million km², and the ruled parts of ${hA.length} more states and territories that caliphates once held, ${mkm(sum(hA))} million km². To join those lands up it also takes in, at your request, Austria, Slovenia, Andorra and the unruled rest of Italy, France, Croatia, Hungary, Ukraine and the south of Russia, ${mkm(sum(jA))} million km² in all. Together, by my rough measurement, about ${mkm(d.km2)} million km² in ${d.states.filter(s=>!s.dup).length} states and territories, many of whose people are not Muslim.</p>`; }
  const lead = XV === 'full'
    ? `<b>Complete version.</b> Switch to “To Iraq’s border” to leave out Iran, Georgia, Armenia, Azerbaijan, Derbent and the Dagestan coast, Turkmenistan, Uzbekistan, Tajikistan, Afghanistan and Pakistan, or to “+ Greater Caliphate” to extend it.`
    : `<b>Version to Iraq’s border.</b> North of Iraq, Türkiye’s eastern border forms the edge. Switch to “Complete” to add Iran, the South Caucasus, Turkmenistan, Afghanistan and Pakistan.`;
  return `<p>${lead} By my rough measurement it covers about ${mkm(d.km2)} million km² in ${d.states.length} present-day states and territories, many of whose people are not Muslim.</p>`;
}
const row = s => `<tr><td>${s.n}${s.flag ? ` <small class="flag">${s.flag}</small>` : ''}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`;
function renderCX(){
  const d = cxData();
  INFO.caliphx.body = NAMES_P + CX_BODY.replace('%%LEAD%%', CX_LEAD[XV]).replace('%%IRAQ%%', XV === 'west' ? CX_IRAQ.out : XV === 'nat' ? CX_IRAQ.nat : CX_IRAQ.in).replace('%%SRC%%', CX_SRC(XV !== 'west', false)).replace('%%GC%%', () => XV === 'gme' ? CX_GC : XV === 'v2' ? v2History() : XV === 'max' ? '' : XV === 'nat' ? natLineHTML : XV === 'natp' ? natpHTML() : '').replace('%%AREA%%', cxArea());
  INFO.caliphx.title = XV === 'west' ? 'Your outline, to Iraq’s border' : XV === 'gme' ? 'Greater Caliphate' : XV === 'v2' ? 'Complete Caliphate V2' : XV === 'max' ? 'Maximum' : XV === 'nat' ? 'Natural borders' : XV === 'natp' ? 'Natural + political' : 'Core caliphate: your complete outline';
  document.querySelectorAll('.nx').forEach(el=>{ const n = d.states.filter(s=>!s.dup).length; el.textContent = W2[n] || n; });
  const tx = document.getElementById('caliphxrows');
  if(tx){
    if(XV === 'v2'){
      const add = d.states.filter(s=>!s.core);
      const hs = s => s.hs ? `<small class="hs">${Object.entries(s.hs).sort((a,b)=>b[1]-a[1]).map(([k,v])=>`${v2sw(k)}${V2CAT[k].label.replace(/^Ruled by a caliphate, directly$/,'ruled directly').replace(/^Ruled by a dynasty under a caliph$/,'dynasty under a caliph').replace(/^Ruled by other Islamic states only$/,'other Islamic states').replace(/^Tributary to a caliphate$/,'tributary').replace(/^Briefly held or raided only$/,'brief or raids').replace(/^Influence only$/,'influence only')} ${v}%`).join(' · ')}</small>` : '';
      tx.innerHTML = `<tr class="grp"><td colspan="3">The complete version, all of it · ${CALIPH.x.states.length} states and territories</td></tr>`
        + `<tr class="sub"><td>All of the complete version, as listed there</td><td class="num">${kmTxt(CALIPH.x.km2)}</td><td class="num">all of it</td></tr>`
        + `<tr class="grp g"><td colspan="3">Added from your map and at your request · ${add.length} · how each was held, by area</td></tr>`
        + add.map(s=>`<tr><td>${s.n}${hs(s)}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`).join('')
        + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
    } else if(XV === 'max'){
      const wh = d.states.filter(s=>s.add === 'whole'), pt = d.states.filter(s=>s.add && s.add !== 'whole');
      tx.innerHTML = `<tr class="grp"><td colspan="3">The complete version, all of it · ${CALIPH.x.states.length} states and territories</td></tr>`
        + `<tr class="sub"><td>All of the complete version, as listed there</td><td class="num">${kmTxt(CALIPH.x.km2)}</td><td class="num">all of it</td></tr>`
        + `<tr class="grp g"><td colspan="3">Added whole, from your list · ${wh.length}</td></tr>` + wh.map(row).join('')
        + `<tr class="grp g a"><td colspan="3">Added in part, province by province · ${pt.length}</td></tr>`
        + pt.map(s=>`<tr><td>${s.n}<small class="hs">${esc(s.add)}</small></td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`).join('')
        + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
    } else if(XV === 'gme'){
      const added = d.states.filter(s=>!s.core && !s.afr && !s.hist && !s.join), afr = d.states.filter(s=>s.afr), hist = d.states.filter(s=>s.hist), join = d.states.filter(s=>s.join);
      tx.innerHTML = `<tr class="grp"><td colspan="3">The core caliphate, all of it · ${CALIPH.x.states.length} states and territories</td></tr>`
        + `<tr class="sub"><td>All of the core, as listed in the complete version</td><td class="num">${kmTxt(CALIPH.x.km2)}</td><td class="num">all of it</td></tr>`
        + `<tr class="grp g"><td colspan="3">Added: the Greater Middle East · ${added.length}</td></tr>`
        + added.map(row).join('')
        + `<tr class="grp g a"><td colspan="3">Added: the Muslim-majority countries of Africa, whole · ${afr.length}</td></tr>`
        + afr.map(row).join('')
        + `<tr class="grp g h"><td colspan="3">Added: lands once ruled by caliphates, the ruled part only · ${hist.length}</td></tr>`
        + hist.map(row).join('')
        + `<tr class="grp g j"><td colspan="3">Added: joined to the lands above, at your request, not ruled · ${listAnd(join.filter(x=>!x.dup).map(x=>x.n))} and the unruled rest of ${W2[join.filter(x=>x.dup).length]} states</td></tr>`
        + join.map(row).join('')
        + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
    } else tx.innerHTML = d.states.map(row).join('') + `<tr class="tot"><td>Total</td><td class="num">about ${mkm(d.km2)} million</td><td></td></tr>`;
  }
  const cap = document.getElementById('caliphxcap');
  if(cap) cap.textContent = XV === 'nat' ? `Present-day states and territories inside the natural ring, largest first. Areas are my rough measurement. A state shows less than all where part of it lies outside the ring; the water of Lake Victoria and Lake Albert is not counted as land.`
    : `Present-day states and territories inside your outline, ${XV === 'full' ? 'complete version' : XV === 'gme' ? 'Greater Caliphate' : XV === 'v2' ? 'Complete Caliphate V2' : XV === 'max' ? 'Maximum version' : XV === 'natp' ? 'Natural + political version, whole states only' : 'version to Iraq’s border'}. Areas are my rough measurement; Bahrain shows ${(cxData().states.find(s=>s.id==='048')||{}).pct||92}% only because islets too small to draw are left off.`;
  document.querySelectorAll('.lgx').forEach(el=>{ el.textContent = XV === 'west' ? 'Your outline, to Iraq’s border' : XV === 'gme' ? 'Greater Caliphate (your outline)' : XV === 'v2' ? 'Complete Caliphate V2 (your outline)' : XV === 'max' ? 'Maximum (your outline)' : XV === 'nat' ? 'Natural borders (your design)' : XV === 'natp' ? 'Natural + political (your design)' : 'Core caliphate (your complete outline)'; });
  document.querySelectorAll('[data-lg="caliphx"] svg line:last-child').forEach(l=>{ l.style.display = XV === 'nat' ? 'none' : null; });   /* the natural line is the edge, so the dash-dot outline is not drawn */
  document.querySelectorAll('[data-xv]').forEach(b=>b.setAttribute('aria-pressed', b.dataset.xv === XV));
}
const natpHTML = () => `<h3 class="v2h">Why whole states</h3><p>A natural feature gives a border physical strength, but what makes a border hold politically is agreement: treaties with the neighbours, recognition by other states, and the consent of the people along it. A line that cuts a present-day state in two, however good the river or ridge under it, would be resisted by that state and by the international principle that existing borders stand (the African Union has held its members to their borders at independence since 1964). This version keeps the natural ring wherever it already runs on a coast or an international border, and elsewhere moves to the nearest recognised border by the majority rule. Its edges are therefore no longer all natural, and some are as artificial as borders get: straight colonial lines across the Sahara, for example. That is the trade: politically stronger, physically weaker. <b>Kashmir:</b> the base map’s de facto lines are used, so Pakistan-administered Kashmir and the Siachen Glacier are inside and Indian-administered Kashmir is outside with the rest of India; none of these lines is agreed between the states concerned. The views on political strength are mine, from general knowledge.</p>`;
let natLineHTML = '';   /* filled in with the natural-line note, below */
let keyWasOpen = null;   /* the key folds away while the Greater Caliphate is shown, and comes back after */
function setXV(v){
  if(!['full','west','gme','v2','max','nat','natp'].includes(v)) return;
  if(v === 'natp' && XV !== 'natp' && !layerOn.natb) setLayer('natb', true, true);   /* the natural ring is drawn with it, for comparison; it can be switched off */
  const lg = document.getElementById('legend');
  if(lg){ if(WIDEV(v) && XV !== v){ if(!WIDEV(XV)) keyWasOpen = lg.open; lg.open = false; } else if(!WIDEV(v) && WIDEV(XV) && keyWasOpen !== null){ lg.open = keyWasOpen; keyWasOpen = null; } }
  if(v === 'nat' && XV !== 'nat') INTL_OFF = false;   /* the internal lines come on with the natural borders, until you switch them off */
  XV = v;
  const dd = CX.d[XK()]; [CX.clip, CX.wash].forEach(el=>el && el.attr('d', dd));
  if(CX.wash) CX.wash.classed('natwash', v === 'nat');   /* the natural-borders territory is shown by a stronger wash: its coasts carry no band (see eng_b) */
  if(CX.line) CX.line.style('display', v === 'nat' ? 'none' : null);   /* the natural line is the edge of this version */   /* band and line follow in render (clipped close in) */
  renderCX();
  const h2 = infoEl.querySelector('h2'); if(h2 && /^(Your (complete )?outline|Core caliphate|Greater Caliphate|Complete Caliphate V2|Maximum|Natural borders|Natural \+ political)/.test(h2.textContent)) showInfo('caliphx');
  applyLayers();
}
const GME_B = [[-19.0,-12.5],[93.5,56.5]];   /* Dakar and Mauritania to Kashgar and Bengal, the Comoros to the north of Kazakhstan */
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
let autoWide = false;   /* true while the page widened itself for the Greater Caliphate; the reader's own choice is kept */
/* the whole territory with a margin: the sheet now runs past it on every side */
function showGME(b){ b = b || (XV === 'nat' ? NAT_B : XV === 'natp' ? [[-18.5,-5.5],[79,47]] : XV === 'v2' ? V2_B : XV === 'max' ? MAX_B : GME_B); if(deskQ.matches){ if(atlasEl.classList.contains('wide')) go(b); else { autoWide = true; setWide(true, ()=>go(b)); } } else go(b); }
function leaveAutoWide(then){ if(autoWide && atlasEl.classList.contains('wide')){ autoWide = false; setWide(false, then); } else { autoWide = false; if(then) then(); } }
const WEST_B = [[-18.5,-3.6],[63.6,44.3]];   /* the version to Iraq's border: Tunisia to Iran's western border; the caliphate preset reaches 78°E for Pakistan (Version 46) and 7.5°E for Tunisia (Version 48) */
function openOutline(v){
  setXV(v); applyPreset('caliph');
  const done = ()=>{ showInfo('caliphx'); markSel(null); };
  if(WIDEV(v)){ showGME(); done(); } else leaveAutoWide(()=>{ go(v === 'west' ? WEST_B : PRESETS.find(p=>p.id==='caliph').b); done(); });
  scrollToMap();
}
document.querySelectorAll('[data-xv]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation();
  const v = b.dataset.xv;
  if(!layerOn.caliphx && b.closest('.insec')){ openOutline(v); return; }
  const wasG = WIDEV(XV);
  setXV(v); if(b.closest('.onmap')){ showInfo('caliphx'); markSel(null); }
  if(WIDEV(v)) showGME(); else if(wasG) leaveAutoWide();   /* back to the normal layout, same centre */
}));
renderCX();
{ const tb = document.getElementById('caliphrows');
  if(tb) tb.innerHTML = CALIPH.states.map(s=>`<tr><td>${s.n}</td><td class="num">${kmTxt(s.km2)}</td><td class="num">${pctTxt(s)}</td></tr>`).join('')
    + `<tr class="tot"><td>Total</td><td class="num">about ${(CALIPH.km2/1e6).toFixed(1)} million</td><td></td></tr>`;
  const sb = document.getElementById('showcaliph'); if(sb) sb.addEventListener('click', ()=>{ applyPreset('caliph'); scrollToMap(); });
  document.addEventListener('click', e=>{ const a = e.target.closest('a.tosynth'); if(a){ e.preventDefault(); closeSheets(); document.getElementById('synth').scrollIntoView({behavior:reduced?'auto':'smooth', block:'start'}); } });
}

/* ---------------- regional index ---------------- */
{ const el = document.getElementById('regioncards');
  if(el){
    const R = CALIPH.g.regions;
    const kind = r => r.join ? 'join' : r.hist ? 'hist' : r.afr ? 'afr' : r.ring ? 'ring' : 'core';
    const tag = { core:'Core caliphate', ring:'Added: Greater Middle East', afr:'Added: Muslim-majority Africa', hist:'Added: once ruled by caliphates', join:'Added: joined, your request' };
    const card = (r,i)=>`<article class="reg ${kind(r)}">
      <header><span class="rk ${kind(r)}">${tag[kind(r)]}</span>
        <h3>${r.n}</h3>${r.ar ? `<div class="regar" lang="ar" dir="rtl">${r.ar}</div>` : ''}<div class="regen">${r.en}</div></header>
      <ul>${r.states.map(s=>`<li><span>${s.n}${s.flag ? ` <small class="flag">${s.flag}</small>` : ''}</span><span class="num">${kmTxt(s.km2)}</span></li>`).join('')}</ul>
      <footer><span class="num">about ${kmTxt(r.km2)} km²</span><button type="button" class="linkbtn" data-reg="${i}">Show on the map</button></footer>
    </article>`;
    const idx = R.map((r,i)=>[r,i]);
    el.innerHTML = `<h3 class="reggrp core">Core caliphate <small>your complete outline · ${mkm(CALIPH.x.km2)} million km²</small></h3><div class="regrow r4">${idx.filter(([r])=>kind(r)==='core').map(([r,i])=>card(r,i)).join('')}</div>`
      + `<h3 class="reggrp ring">Added in the Greater Caliphate: the Greater Middle East</h3><div class="regrow r3">${idx.filter(([r])=>kind(r)==='ring').map(([r,i])=>card(r,i)).join('')}</div>`
      + `<h3 class="reggrp afr">Added in the Greater Caliphate: the Muslim-majority countries of Africa <small>whole countries, by Pew’s 2020 estimates</small></h3><div class="regrow r3">${idx.filter(([r])=>kind(r)==='afr').map(([r,i])=>card(r,i)).join('')}</div>`
      + `<h3 class="reggrp hist">Added in the Greater Caliphate: lands once ruled by caliphates <small>the ruled part only</small></h3><div class="regrow r4">${idx.filter(([r])=>kind(r)==='hist').map(([r,i])=>card(r,i)).join('')}</div>`
      + `<h3 class="reggrp join">Added in the Greater Caliphate: lands joined to the rest <small>at your request, not ruled · ${mkm(CALIPH.g.km2)} million km² in all, with the core</small></h3><div class="regrow r3">${idx.filter(([r])=>kind(r)==='join').map(([r,i])=>card(r,i)).join('')}</div>`;
    el.querySelectorAll('[data-reg]').forEach(btn=>btn.addEventListener('click', ()=>{
      const r = R[+btn.dataset.reg];
      if(!layerOn.caliphx) applyPreset('caliph');
      const added = r.ring || r.hist || r.afr || r.join;
      const want = added ? 'gme' : (XV === 'gme' ? 'full' : XV);
      if(XV !== want) setXV(want);
      const goR = ()=>{ go(r.b); showInfo(added ? 'caliphg' : 'caliphx'); markSel(null); };
      if(added && deskQ.matches && !atlasEl.classList.contains('wide')){ autoWide = true; setWide(true, goR); } else if(!added) leaveAutoWide(goR); else goR();
      scrollToMap();
    }));
    const nC = R.filter(r=>kind(r)==='core').length, nG = R.filter(r=>kind(r)==='ring').length, nA = R.filter(r=>kind(r)==='afr').length, nH = R.filter(r=>kind(r)==='hist').length, nJ = R.filter(r=>kind(r)==='join').length, intro = document.querySelector('#regions .intro');
    const cap = w => w.charAt(0).toUpperCase() + w.slice(1);
    if(intro) intro.textContent = `${cap(W2[R.length])} regions, named as the classical geographers and chroniclers named them (the joined lands have no classical name here and are named plainly), with the present-day states in each. ${cap(W2[nC])} make up the core caliphate, your complete outline. The Greater Caliphate takes in all of them, adds ${W2[nG]} from the Greater Middle East, adds ${W2[nA]} for the Muslim-majority countries of Africa, adds ${W2[nH]} that caliphates once ruled, counting only the part that was ruled, and adds ${W2[nJ]} more, joined to the rest at your request. Tap a region to see it on the map. Areas are my rough measurement; classical names are approximate guides, not borders.`;
  } }
/* Complete Caliphate V2: a province named in a note goes to that province on the map */
document.addEventListener('click', e=>{ const b = e.target.closest('.v2go'); if(!b) return; e.preventDefault();
  const i = +b.dataset.v2u, u = V2U[i]; if(!u) return;
  if(!layerOn.caliphx) applyPreset('caliph'); if(XV !== 'v2') setXV('v2');
  const [x0, y0, x1, y1] = u.b || [0, 0, 0, 0];   /* the province's box, from build.js */
  if(x1 > x0){ const px = Math.max(0.6, (x1-x0)*0.25), py = Math.max(0.6, (y1-y0)*0.25); go([[x0-px, y0-py],[x1+px, y1+py]]); }
  select('v2u_'+i); scrollToMap(); });

/* ---------- Dār al-Amān: natural borders and internal lines (your design, 2026-10-07) ---------- */
{
  const mk = n => (n/1e6).toFixed(1);
  const shareTxt = c => c.pct >= 99 ? 'all' : c.pct >= 1 ? c.pct + '%' : 'under 1%';
  const inPct = id => (NAT.main.states.find(s=>s.id === id) || {pct:0}).pct;
  const cList = v => listAnd(NAT[v].states.map(c=>`${c.n.replace(/ \(.*\)$/, '')} (${shareTxt(c)}${c.id === '732' ? '; status internationally disputed' : ''})`));
  INFO.natb = {title:'The natural ring of Dār al-Amān', src:[], cert:'approx', body:`<p><b>Your design, not from the sources.</b> No classical geographer drew this line. It is one closed ring of natural features (coasts, rivers, cliffs, mountain crests and watersheds) drawn round the whole of your complete outline. The land inside it is a version of the outline in its own right: the <b>Natural borders</b> button beside Complete, Complete V2, To Iraq’s border and + Greater Caliphate. The “Natural line” button in the second row draws just the ring over any other version.</p>
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
  <p><b>Islands.</b> The median-line rule: an island nearer to a shore inside the ring is inside. I measured from each island to the nearest mainland shore inside and outside the ring, largest islands first, and let an island of 5,000 km² or more, once decided, count as a shore for smaller ones near it (so Sicily counts for Malta, and Madagascar for the Seychelles). The islands you named are set as you named them. Inside: Crete, Rhodes and the Dodecanese, the other Greek islands, the Turkish islands, Cyprus, Pantelleria and Lampedusa, Kerkennah and Djerba, Bahrain and the other Gulf islands, Masirah, Socotra and Abd al-Kuri, the Dahlak and Farasan islands, the Lamu islands, most of the Croatian islands, and, by the rule, the Canary Islands and Madeira, which are nearer Africa than Europe. Outside: Sicily, Malta, Sardinia, Corsica, the Balearics, Cres and Lošinj (nearer Istria, which is outside), Cape Verde, Bioko, Zanzibar, Pemba, the Comoros, Madagascar and the Seychelles. Sardinia is the one island where the rule and your list disagree: it is about 185 km from Tunisia and 190 km from mainland Italy, so the rule would put it inside by a hair; it is outside, as you named it.</p>
  <p><b>Your complete outline inside the ring.</b> I checked the whole outline against the ring, and all of it is inside. To get there I made two changes to the complete outline, at your choice: it is trimmed back to the Victoria Nile between Murchison Falls and Lake Albert (about 2,000 km² south of the river, bounded there only by district lines, is now left out of it, and of Complete V2 and the Greater Caliphate), and it is clipped to the ring, which takes off slivers of a few km² along borders where the two had been drawn from slightly different border lines.</p>
  <p><b>Size.</b> About ${mk(NAT.main.km2)} million km² of land (my rough measurement, without the seas and the two lakes). Inside: ${cList('main')}.</p>
  <p><b>How it was drawn.</b> Coasts, lakes and borders are the base map’s (Natural Earth 1:10m). The rivers are Natural Earth’s 1:10m river lines, with the Kupa from its European supplement; the Aral’s old shore is from its historic-lakes file. Where a river of the ring is also a national border (the Kupa between Croatia and Slovenia, the Sava between Croatia and Bosnia, the Danube from the Iron Gates to the sea, the Amu Darya and the Panj along Afghanistan, the Mbomou, the Ubangi and the Congo along DR Congo, and the Senegal), I used the border line itself, so the states table has no slivers. <b>The watersheds:</b> I could not reach HydroSHEDS from the machine I built this on. So the Nile–Congo divide is the Uganda–DR Congo and South Sudan–DR Congo borders, which were defined on it; the Karakoram is the China–Pakistan border and the crest north of the Siachen Glacier; and the Sutlej–Ganges divide from Lipulekh north-west is the India–China border in Uttarakhand. The rest of the Indus rim, from the Karakoram Pass through Ladakh and western Tibet round Kailash to Lipulekh, I traced by hand from the shaded relief and the rivers, keeping north of the Indus and west of the Karnali; treat it as approximate. <b>Placed by hand</b>, from the shaded relief, the rivers and named places, as the Taurus line was: the Rječina and the watershed by Risnjak to the Kupa spring; the Kupa’s bend from Kamanje to Karlovac, which is not in the river data; the Ustyurt escarpment from the Uzbekistan corner round Sarykamysh to the Aral; the link to the Yamuna’s source; the Malwa link, along the top of the Vindhya scarp, which is the watershed between the Chambal and Mahi and the Narmada; in Kenya the Aberdare crest, the Eburru divide, the Mau crest and the Nyando (by Muhoroni and Ahero), none of which is in the base data; the Mambéré, which Natural Earth does not have, from Nola past Carnot to its source in the Yadé Massif; the Yadé–Adamawa crest to the Benue’s source, kept north of the heads of the Lom and the Djérem and south of the Vina; and the Fouta Djallon link, which first follows the Guinea–Sierra Leone border (on the Niger’s watershed) and then the highland to the source of the Bafing. With no elevation data, none of these is snapped to a measured crest. <b>Two low links:</b> the Eburru divide crosses the floor of the Rift Valley, and the Malwa link runs over a plateau; both are real watersheds, but low ones, not mountain barriers.</p>
  <p><b>Choices I made.</b> The Greater Caucasus crest ends at Bazardüzü, and from there the ring follows the Samur to the Caspian (the Russia–Azerbaijan border): your complete outline holds all of Azerbaijan, and the bare crest, which runs on to the Absheron, would cut off its northern slope. The Danube reaches the sea by the Chilia arm, the border with Ukraine. Across the Caspian the ring meets the coast just north of the Garabogaz Gulf, where the Kazakhstan–Turkmenistan border runs along the foot of the Ustyurt, so all of Turkmenistan west of the Amu Darya is inside, the Garabogaz with it. Up the Panj the ring takes the Pamir River, the border, to Lake Zorkul. The ring runs down the middle of the Gulf of Khambhat, so Saurashtra and Kutch are inside and Surat is outside. Western Sahara lies inside; its status is internationally disputed, and the map follows Natural Earth’s drawing of it as a separate territory. Spain (Ceuta, Melilla and the Canary Islands), Portugal (Madeira), Italy (Lampedusa and Pantelleria), Russia (the Black Sea coast south of the crest) and China (the upper Indus and Sutlej in western Tibet) appear in the table for small parts only.</p>`, refs:[]};
  /* the version's own note carries the same account of the line, without the opening paragraph and the size, which the version states for itself */
  natLineHTML = '<h3 class="v2h">How the line runs</h3>' + INFO.natb.body.split(/\n\s*(?=<p>)/).filter((x,i)=>i > 0 && !/^<p><b>Size\./.test(x)).join('');
  INFO.intl = {title:'Internal lines', src:[], cert:'approx', body:`<p><b>Your design, not from the sources.</b> Lighter lines inside Dār al-Amān: the Taurus divide between Anatolia, the Levant and Mesopotamia; the Nile, the Tigris and the Euphrates as the core waterways; and the Red Sea as the central axis joining the African and Arabian halves.</p>
  <p><b>How they were drawn.</b> The rivers come from Natural Earth: the White Nile, the Nile and its delta branches from the base map, and the Blue Nile from Natural Earth’s fuller rivers file, because the base map leaves it out. The Taurus line is my own waypoints along the main crest, from the Lycian Taurus above Antalya to Hakkari; the Red Sea axis runs down the middle of the sea from the Gulf of Suez to Bāb al-Mandab. Both are approximate.</p>
  <p><b>History, for comparison.</b> In early Islamic times the Taurus was the frontier with Byzantium, held by the fortress zone the Arab sources call al-Thughūr and al-ʿAwāṣim; the Cilician Gates were the main pass. This is from general knowledge.</p>`, refs:[]};
  /* the natural borders are a version of the outline; the line alone can also be drawn over any version */
  const openLineOnly = ()=>{ if(!layerOn.caliphx) applyPreset('caliph'); setLayer('natb', true, true); go(NAT_B); showInfo('natb'); markSel(null); scrollToMap(); };
  addIx('Natural borders', 'View', 'Dār al-Amān inside the ring of coasts, rivers, crests and watersheds · your design', 'natural borders ring version kupa sava danube caucasus samur ustyurt aral amu darya panj pamir karakoram indus kailash sutlej yamuna chambal malwa mahi khambhat tana mount kenya aberdares mau victoria nile kyoga albert nile congo divide mbomou ubangi sangha mambere yade adamawa benue niger fouta djallon senegal gibraltar islands median line', ()=>{ openOutline('nat'); }, ['natural-borders', 'natural-libya']);
  addIx('Maximum', 'View', 'your complete outline with the lands on your list · your specification', 'maximum max stable expansion maghreb sahel sokoto northern nigeria uganda rwanda burundi lake victoria swahili coast kenya tanzania zanzibar mozambique zambezi central asia transoxiana kazakhstan caspian basin volga russia afghanistan pakistan indus malta maldives comoros', ()=>openOutline('max'), ['outline-maximum']);
  addIx('Natural + political', 'View', 'the natural ring with every state it cuts taken whole or left out · your design', 'natural political whole states recognised borders majority version', ()=>openOutline('natp'), ['natural-political']);
  addIx('Natural line', 'View', 'draw the natural line over any version · your design', 'natural line overlay border over complete v2 greater', openLineOnly, ['natural-line']);
  addIx('Clean map', 'View', 'hide the numbered discs, dots, place names, key, captions, scale and coordinates while an outline shows', 'clean map hide numbers discs dots markers key legend labels captions scale compass coordinates uncluttered', ()=>{ if(!layerOn.caliphx) openOutline(XV); CLEAN = true; applyLayers(); scrollToMap(); }, ['clean-map']);
  addIx('Internal lines', 'View', 'the Taurus divide, the Nile, Tigris and Euphrates, the Red Sea axis · your design', 'internal lines taurus nile tigris euphrates red sea axis', ()=>{ if(inNat()) INTL_OFF = false; else setLayer('intl', true, true); applyLayers(); go([[26,10],[50,40]]); showInfo('intl'); markSel(null); scrollToMap(); }, ['internal-lines']);
  addIx('Dār al-Amān', 'View', 'al-Khilāfa al-Amīna · your names for the core caliphate', 'dar al aman darul aman khilafa amina amani amaniyyun caliphate name', ()=>openOutline('full'), ['dar-al-aman']);
  addIx('al-Quds, capital of Dār al-Amān', 'Place', 'your choice · Jerusalem', 'capital jerusalem quds', ()=>{ if(!layerOn.caliphx) openOutline(XV); go(near(QIBLA.aqsa, 1.2)); flash(QIBLA.aqsa); select('capital'); }, ['capital']);
  document.querySelectorAll('[data-lyt]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation();
    const id = b.dataset.lyt;
    if(inNat()){   /* in the natural-borders version the line is the border and cannot be switched off; the internal lines can */
      if(id === 'natb'){ showInfo('natb'); markSel(null); return; }
      INTL_OFF = !INTL_OFF; applyLayers(); if(!INTL_OFF){ showInfo('intl'); markSel(null); } return; }
    const on = !layerOn[id];
    setLayer(id, on, true); if(on){ showInfo(id); markSel(null); } }));
  document.querySelectorAll('[data-clean]').forEach(b=>b.addEventListener('click', e=>{ e.stopPropagation(); CLEAN = !CLEAN; applyLayers(); }));
}
