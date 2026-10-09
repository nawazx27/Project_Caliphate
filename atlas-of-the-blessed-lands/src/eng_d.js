/* ================= v4 engine, part D: controls, panels, insets, tables ================= */
const FOCUS = [
  {n:"Whole region", b:[[21.2,-2.4],[63.4,42.6]], chip:true, fitH:true},   /* from the Black Sea to the tip of Somalia, from Sudan to Iran */
  {n:"al-Shām", info:"sham", b:[[33.2,29.2],[39.6,37.9]], chip:true},
  {n:"Filasṭīn", info:"filastin", b:[[33.6,29.4],[36.8,33.4]], layer:"filastin", chip:true},
  {n:"Jerusalem", info:"aqsa", b:[[35.205,31.758],[35.265,31.796]], chip:true},
  {n:"Ḥaram of Makkah", info:"makkah", b:[[39.62,21.30],[40.03,21.56]], chip:true},
  {n:"Ḥaram of Madinah", info:"madinah", b:[[39.50,24.36],[39.72,24.56]], chip:true},
  {n:"The mīqāts", info:"miqat", b:[[38.6,20.2],[41.3,24.7]], layer:"miqat", chip:true},
  {n:"al-Ḥijāz", info:"hijaz", b:[[34.4,17.8],[43.2,29.6]], chip:true},
  {n:"Shām–Ḥijāz seam", info:"seam", b:[[34.5,25.6],[42.2,30.4]]},
  {n:"Caravan roads", info:"quraysh", b:[[33.5,14.8],[45.5,33.2]], layer:"trade"},
  {n:"Hajj roads", info:"hajj", b:[[30.8,20.8],[45.2,33.8]], layer:"hajj"},
  {n:"Jazīrat al-ʿArab", info:"jazirah", b:[[33.5,11.5],[60.5,34.5]], layer:"jazirah"},
  {n:"al-Jazīrah (Upper Mesopotamia)", info:"upper", b:[[37.0,33.2],[44.8,38.4]], layer:"upper"},
  {n:"al-ʿIrāq and the Sawād", info:"iraq", b:[[42.0,29.6],[49.0,35.6]], layer:"iraq"},
  {n:"Miṣr and Sinai", info:"misr", b:[[26.5,23.4],[36.6,32.0]], layer:"misr"},
  {n:"Najd", info:"najd", b:[[40.6,20.6],[48.6,28.4]], layer:"najd"},
  {n:"al-Yaman and Sabaʾ", info:"yemen", b:[[41.2,12.2],[53.0,20.8]], layer:"yemen"},
  {n:"al-Ḥabashah", info:"habashah", b:[[35.6,11.0],[42.0,16.8]], layer:"habashah"},
  {n:"Bilād al-Rūm", info:"rum", b:[[26.0,35.4],[40.6,42.0]], layer:"rum"},
  {n:"Peninsula and neighbours", b:[[24.5,8.0],[62.0,42.0]]},
  {n:"Sinai", info:"tuwa", b:[[32.2,27.4],[35.6,30.2]]},
  {n:"Qusṭanṭīniyyah · Istanbul", info:"eg_qust", b:[[28.55,40.84],[29.42,41.26]]},
  {n:"Türkiye and Thrace", b:[[25.6,35.6],[45.0,42.3]]},
  {n:"Greater Iraq: Iraq, Khuzestan and ʿIrāq al-ʿAjam", info:"caliphx", b:[[38.5,29.0],[55.6,37.6]], layer:"caliphx"},
  {n:"Iran", b:[[43.8,24.8],[63.5,40.0]]},
  {n:"The Caucasus: Georgia, Armenia, Azerbaijan", b:[[39.6,38.2],[51.2,43.9]]},
  {n:"Greater Caliphate", b:[[-19.0,-12.5],[93.5,56.5]], chip:true, gc:true}
];
const focusEl = document.getElementById('focus');
const focusBtns = [];
function goFocus(i){ const f = FOCUS[i];
  if(f.gc){ if(!layerOn.caliphx) applyPreset('caliph'); setXV('gme'); chipNext = i; showGME(); showInfo('caliphx'); markSel(null); return; } if(f.layer && !layerOn[f.layer]) setLayer(f.layer, true);
  leaveAutoWide(()=>{ chipNext = i; go(f.b, f.wide, f.fitH); if(f.info && INFO[f.info]){ showInfo(f.info); markSel(null); } }); }
FOCUS.forEach((f,i)=>{ if(!f.chip){ focusBtns[i] = {classList:{toggle(){}}}; return; }
  const b=document.createElement('button'); b.type='button'; b.textContent=f.n; b.addEventListener('click',()=>goFocus(i)); focusEl.appendChild(b); focusBtns[i]=b; });
{ const sel = document.createElement('select'); sel.className = 'moreplaces'; sel.setAttribute('aria-label','More places');
  sel.innerHTML = `<option value="">More places…</option>` + FOCUS.map((f,i)=>f.chip?'':`<option value="${i}">${f.n}</option>`).join('');
  sel.addEventListener('change', ()=>{ if(sel.value!==''){ goFocus(+sel.value); sel.value=''; } });
  focusEl.appendChild(sel);
  /* the widest view sits next to 'Whole region' */
  const gme = focusBtns[FOCUS.length-1]; if(gme && gme.nodeType) focusEl.insertBefore(gme, focusBtns[0].nextSibling); }
document.getElementById('zin').onclick = ()=>{ wheelTarget = null; wrapSel.transition().duration(reduced?0:320).call(zoom.scaleBy, 2); };
document.getElementById('zout').onclick = ()=>{ wheelTarget = null; wrapSel.transition().duration(reduced?0:320).call(zoom.scaleBy, 0.5); };
document.getElementById('zreset').onclick = ()=> goFocus(0);
const coordsEl = document.getElementById('coords');
svg.on('pointermove', e=>{ const ll = proj.invert(T.invert(d3.pointer(e, wrapEl))); if(!ll) return;
  coordsEl.textContent = `${Math.abs(ll[1]).toFixed(3)}° ${ll[1]>=0?'N':'S'} · ${Math.abs(ll[0]).toFixed(3)}° ${ll[0]>=0?'E':'W'}`; });
const legendEl = document.getElementById('legend');
if(legendEl) legendEl.addEventListener('toggle', ()=>{ setTimeout(()=>{ measureChrome(); update(); }, 0); });

/* ---------------- sheets (phone) ---------------- */
function sheetMode(){ return mobileQ.matches || (fullOn && !deskQ.matches); }
function openSheet(id){ if(!sheetMode()) return; document.querySelectorAll('.sheet').forEach(s=>s.classList.toggle('open', s.id===id)); }
function closeSheets(){ document.querySelectorAll('.sheet').forEach(s=>s.classList.remove('open')); }
document.querySelectorAll('[data-close]').forEach(b=>b.addEventListener('click', closeSheets));
document.getElementById('openLayers').onclick = ()=>{ const s=document.getElementById('layerscard'); s.classList.contains('open') ? closeSheets() : openSheet('layerscard'); };
document.getElementById('openNotes').onclick = ()=>{ const s=document.getElementById('infocard'); s.classList.contains('open') ? closeSheets() : openSheet('infocard'); };
document.addEventListener('keydown', e=>{ if(e.key!=='Escape') return; if(document.querySelector('.sheet.open')){ closeSheets(); return; } if(e.target && e.target.id === 'placeq') return; if(fullOn) exitFull(); });

/* ---------------- info panel ---------------- */
const infoEl = document.getElementById('infobody');
const lineSample = c => { const s=CERT[c]; return `<svg width="26" height="8" aria-hidden="true"><line x1="2" y1="4" x2="25" y2="4" stroke="currentColor" stroke-width="${s.w}" ${s.dash?`stroke-dasharray="${s.dash}" stroke-linecap="round"`:''}/></svg>`; };
const ringSample = (level, col) => { const d = RING_DASH[level]; return `<svg width="22" height="22" viewBox="-11 -11 22 22" aria-hidden="true" style="flex:none"><circle r="8.6" fill="none" stroke="var(${col})" stroke-width="2" ${d?`stroke-dasharray="${d}" stroke-linecap="round"`:''}/><circle r="5.2" style="fill:var(${col})"/>${level==='disp'?'<text y="1" text-anchor="middle" dominant-baseline="central" style="font:700 7px var(--font-mono);fill:var(--st-on)">?</text>':''}</svg>`; };
function showInfo(key, extraTitle){
  const d = INFO[key]; if(!d) return;
  let h = '';
  if(d.status){
    const s = d.status, kc = KIND[s.kind];
    h += `<div class="sthead"><span class="sdisc" style="--c:var(${kc.col})">${s.n}</span><h2>${s.name}</h2></div>`;
    h += `<div class="chips">` + (s.kinds.length ? s.kinds.map(k=>`<span class="chipx" title="${KIND[k].sub}"><span class="d" style="background:var(${KIND[k].col})"></span>${KIND[k].label}</span>`).join('') : `<span class="chipx"><span class="d" style="background:var(--st-none)"></span>No status established</span>`) + `<span class="chipx lv">${ringSample(s.level, kc.col)}${s.lvl}</span></div>`;
  } else {
    h += `<h2>${extraTitle || d.title}</h2>`;
    if(extraTitle) h += `<div class="fine" style="margin-top:2px">${d.title}</div>`;
    if(d.ar) h += `<div class="arh" lang="ar" dir="rtl">${d.ar}</div>`;
    if((d.src&&d.src.length) || d.cert){
      h += `<div class="chips">` + (d.src||[]).map(s=>`<span class="chipx" title="${SRC[s].tip}"><span class="d" style="background:${SRC[s].color}"></span>${SRC[s].label}</span>`).join('');
      if(d.cert) h += `<span class="chipx">${lineSample(d.cert)}${CERT[d.cert].label}</span>`;
      h += `</div>`;
    }
  }
  h += `<div class="body">${d.body}</div>`;
  if(key==='muq') h += `<div class="views" role="radiogroup" aria-label="Early views on the extent">` + MUQ_VIEWS.map(v=>`<label><input type="radio" name="muqv" id="muqv-${v.id}" value="${v.id}" ${v.id===muqView?'checked':''}><span>${v.label}</span></label>`).join('') + `</div>`;
  if(d.status) h += `<button type="button" class="gobtn" data-go="${d.status.n}">Show on the map</button> <a class="rowlink" href="#sacred-status" data-row="${d.status.n}">See the table row</a>`;
  if(d.refs && d.refs.length) h += `<ul class="refs">${d.refs.map(r=>`<li>${r}</li>`).join('')}</ul>`;
  infoEl.innerHTML = h;
  document.getElementById('infocard').scrollTop = 0;
  if(key==='muq') infoEl.querySelectorAll('input[name=muqv]').forEach(r=>r.addEventListener('change', ()=>{ muqView = r.value; if(!layerOn.muq) setLayer('muq', true); drawMuq(); markSel('muq'); }));
  const gb = infoEl.querySelector('.gobtn'); if(gb) gb.addEventListener('click', ()=>{ goStatus(+gb.dataset.go); });
  const rl = infoEl.querySelector('.rowlink'); if(rl) rl.addEventListener('click', e=>{ e.preventDefault(); closeSheets(); const row = document.getElementById('srow-'+rl.dataset.row); if(row){ row.scrollIntoView({behavior:reduced?'auto':'smooth', block:'center'}); row.classList.add('flash'); setTimeout(()=>row.classList.remove('flash'), 1800); } });
}
function markSel(key){ svg.selectAll('.sel').classed('sel', false); if(key) svg.selectAll(`[data-sel="${key}"]`).classed('sel', true); }
function select(key){ showInfo(key); markSel(key); openSheet('infocard'); }
function scrollToMap(){ if(fullOn) return; wrapEl.scrollIntoView({behavior:reduced?'auto':'smooth', block:'center'}); }
function goStatus(n, scroll){
  const s = STATUS.find(x=>x.n===n); if(!s) return;
  [KIND[s.kind].layer, s.goto].forEach(id=>{ if(id && layerOn[id]===false) setLayer(id, true); });
  const f = FOCUS[s.focus]; if(f.layer && !layerOn[f.layer]) setLayer(f.layer, true);
  go(f.b); select('st'+n); if(scroll) scrollToMap();
}
function goLimit(id){
  const l = ALL_LIMITS.find(x=>x.id===id); if(!l) return;
  const lay = l.layer==='hijazfiqh' ? 'hijazfiqh' : (l.layer==='misr' ? 'misr' : 'limits');
  if(!layerOn[lay]) setLayer(lay, true); if(l.layer==='filastin' && !layerOn.filastin) setLayer('filastin', true);
  const d = l.layer==='filastin' ? 0.9 : 2.6; go([[l.ll[0]-d*1.3, l.ll[1]-d],[l.ll[0]+d*1.3, l.ll[1]+d]]); select('lim_'+id); scrollToMap();
}

/* ---------------- layer panel and presets ---------------- */
const layersEl = document.getElementById('layers');
const presetEl = document.getElementById('presets');
function setPresetChip(id){ presetEl.querySelectorAll('button').forEach(b=>b.classList.toggle('on', b.dataset.p===id)); }
function setLayer(id, on, keepPreset){ layerOn[id] = on; const cb = document.getElementById('ly-'+id); if(cb) cb.checked = on; if(!keepPreset){ setPresetChip(null); if(TIER && !TIER_KEEP){ TIER = null; syncTierBtns(); } } applyLayers(); }
function applyPreset(id){
  const p = PRESETS.find(x=>x.id===id); if(!p) return;
  LAYER_IDS.forEach(l=>{ if(p.keep && p.keep.includes(l)) return; layerOn[l] = p.all ? true : p.on.includes(l); const cb = document.getElementById('ly-'+l); if(cb) cb.checked = layerOn[l]; });
  TIER = null; syncTierBtns();
  applyLayers(); setPresetChip(id);
  const after = ()=>{ if(p.b){ go(p.b); showInfo('caliph'); markSel(null); } };
  if(id !== 'caliph' && autoWide) leaveAutoWide(after); else after();
}
PRESETS.forEach(p=>{ const b = document.createElement('button'); b.type='button'; b.dataset.p = p.id; b.textContent = p.n; b.title = p.tip; b.addEventListener('click', ()=>applyPreset(p.id)); presetEl.appendChild(b); });
const OPEN_GROUPS = ["Sacred status","Sacred places","Classical regions","Neighbouring lands","Roads","Thought experiment"];
LAYERS.forEach(grp=>{
  const g = document.createElement('details'); g.className='lgroup'; if(OPEN_GROUPS.includes(grp.g)) g.open = true;
  g.innerHTML = `<summary class="gt">${grp.g}</summary>`;
  grp.items.forEach(l=>{
    const row = document.createElement('div'); row.className='lrow';
    const c = CERT[l.cert||'firm'];
    const sw = l.disc ? `<span class="dsw" style="--c:var(${l.color})"></span>` : `<svg width="30" height="10" aria-hidden="true"><line x1="2" y1="5" x2="28" y2="5" stroke="var(${l.color})" stroke-width="${c.w+0.6}" ${c.dash?`stroke-dasharray="${c.dash}" stroke-linecap="round"`:''}/></svg>`;
    row.innerHTML = `<input type="checkbox" id="ly-${l.id}" ${l.on?'checked':''}>${sw}
      <label class="nm" for="ly-${l.id}">${l.name}<small>${l.sub}</small></label>
      ${l.info?`<button type="button" class="ib" aria-label="About ${l.name}">About</button>`:'<span></span>'}`;
    row.querySelector('input').addEventListener('change', e=>{ setLayer(l.id, e.target.checked); if(e.target.checked && l.info && !mobileQ.matches) select(l.info); });
    const ib = row.querySelector('.ib'); if(ib) ib.addEventListener('click', ()=>select(l.info));
    g.appendChild(row);
  });
  layersEl.appendChild(g);
});
{ const sk = document.getElementById('srckey'); if(sk) sk.innerHTML = Object.values(SRC).map(s=>`<span class="chipx" title="${s.tip}"><span class="d" style="background:${s.color}"></span>${s.label}</span>`).join(''); }

/* ---------------- status table and limit cards ---------------- */
const lvlCell = s => `<div class="lvl">${ringSample(s.level, KIND[s.kind].col)}<span>${s.lvl}</span></div>`;
function renderStatusTable(){
  const el = document.getElementById('statusrows'); if(!el) return;
  el.innerHTML = STATUS.map(s=>{
    const kc = KIND[s.kind];
    const kinds = s.kinds.length ? s.kinds.map(k=>`<span class="kd" style="--c:var(${KIND[k].col})">${KIND[k].label.toLowerCase()}</span>`).join('') : `<span class="kd" style="--c:var(--st-none)">none established</span>`;
    const tags = s.kinds.concat(s.kinds.length?[]:['none']).join(' ');
    return `<tr id="srow-${s.n}" data-kinds="${tags}">
      <td class="c-n"><button type="button" class="sdisc big" style="--c:var(${kc.col})" data-n="${s.n}" aria-label="Show ${s.name} on the map">${s.n}</button></td>
      <td class="c-p" data-l="Place"><b>${s.name}</b><div class="kds">${kinds}</div></td>
      <td class="c-r" data-l="Status rests on">${s.rests}</td>
      <td class="c-l" data-l="Level">${lvlCell(s)}</td>
      <td class="c-w" data-l="Where, and how far">${s.where}${s.refs&&s.refs.length?`<div class="refs2">${s.refs.join(' · ')}</div>`:''}</td></tr>`;
  }).join('');
  el.querySelectorAll('button.sdisc').forEach(b=>b.addEventListener('click', ()=>goStatus(+b.dataset.n, true)));
  const fl = document.getElementById('statusfilter'); if(!fl) return;
  const opts = [["all","All 22"],["haram","Ḥaram"],["muq","Muqaddas"],["mub","Mubārak"],["fad","Faḍīla"],["link","Links"],["none","None established"]];
  fl.innerHTML = opts.map((o,i)=>`<button type="button" data-f="${o[0]}" class="${i===0?'on':''}">${o[1]}</button>`).join('');
  fl.querySelectorAll('button').forEach(b=>b.addEventListener('click', ()=>{
    fl.querySelectorAll('button').forEach(x=>x.classList.toggle('on', x===b));
    el.querySelectorAll('tr').forEach(tr=>{ const ks = tr.dataset.kinds.split(' '); tr.hidden = !(b.dataset.f==='all' || ks.includes(b.dataset.f)); });
  }));
}
function renderLimits(){
  const el = document.getElementById('limitcards'); if(!el) return;
  const layerName = {sham:"al-Shām", hijaz:"al-Ḥijāz", filastin:"Filasṭīn", hijazfiqh:"Jurists' layer", misr:"Miṣr"};
  el.innerHTML = ALL_LIMITS.map(l=>{
    const d = INFO['lim_'+l.id];
    return `<article class="lim" id="lim-${l.id}"><header><button type="button" class="lbadge" data-l="${l.id}" aria-label="Show ${l.n} on the map">${l.id}</button><div><h3>${l.n}</h3><span class="ltag">${layerName[l.layer]||''}</span></div></header>
      <div class="lbody">${d.body}</div>
      <div class="lchips">${(d.src||[]).map(s=>`<span class="chipx" title="${SRC[s].tip}"><span class="d" style="background:${SRC[s].color}"></span>${SRC[s].label}</span>`).join('')}<span class="chipx">${lineSample(d.cert)}${CERT[d.cert].label}</span></div>
      ${d.refs&&d.refs.length?`<div class="lrefs">${d.refs.join(' · ')}</div>`:''}</article>`;
  }).join('');
  el.querySelectorAll('button.lbadge').forEach(b=>b.addEventListener('click', ()=>goLimit(b.dataset.l)));
}

/* ---------------- inset maps ---------------- */
const INSETS = [
  {id:"im", title:"Ḥaram of Makkah", note:"about 25 km across", b:[[39.60,21.29],[40.04,21.57]], info:"makkah", focus:4,
   shapes:[["haramfill",ringD(MAKKAH_HARAM)]], points:HARAM_PTS.filter(h=>h.info==='makkah'&&h.k<40).map(h=>({ll:h.ll,n:h.n,a:h.a,hollow:h.out,color:'--haram'})).concat([{ll:[39.8262,21.4225],n:"al-Masjid al-Ḥarām",a:"r",sym:"diamond",color:'--haram'},{ll:[39.8592,21.4575],n:"Ḥirāʾ",a:"r",sym:"square",color:'--site'},{ll:[39.8506,21.3772],n:"Thawr",a:"l",sym:"square",color:'--site'}])},
  {id:"id", title:"Ḥaram of Madinah", note:"ʿAyr to Thawr, about 16 km", b:[[39.51,24.37],[39.71,24.56]], info:"madinah", focus:5,
   shapes:[["haramfill",ringD(MADINAH_HARAM)]], points:HARAM_PTS.filter(h=>h.info==='madinah'&&h.n!=="Uḥud").map(h=>({ll:h.ll,n:h.n,a:h.a,color:'--haram'})).concat([{ll:QIBLA.madinah,n:"al-Masjid al-Nabawī",a:"r",sym:"diamond",color:'--haram'},{ll:[39.6172,24.4393],n:"Qubāʾ",a:"l",sym:"square",color:'--site'}])},
  {id:"iq", title:"The mīqāts", note:"where iḥrām begins", b:[[38.6,20.2],[41.9,24.7]], info:"miqat", focus:6,
   shapes:[["haramfill",ringD(MAKKAH_HARAM)],["haramfill",ringD(MADINAH_HARAM)]], points:MIQATS.map(m=>({ll:m.ll,n:m.n,a:m.a,sym:"ring",color:'--miqat'})).concat([{ll:QIBLA.makkah,n:"Makkah",a:"r",sym:"diamond",color:'--haram'},{ll:QIBLA.madinah,n:"Madinah",a:"r",sym:"diamond",color:'--haram'}])},
  {id:"iaq", title:"al-Masjid al-Aqṣā", note:"the walled enclosure, about 0.5 km", b:[[35.2300,31.7733],[35.2410,31.7826]], info:"aqsa", focus:3,
   shapes:[["aqsa",ringD(AQSA_ENCL)]], points:AQSA_PTS.map(p=>({ll:p.ll,n:p.n,a:p.a,sym:"diamond",color:'--sacred'})), tags:[{ll:[35.2354,31.7807], t:"the whole enclosure is al-Masjid al-Aqṣā"}]}
];
const insetsEl = document.getElementById('insets');
const insetRenders = [];
/* The four detail maps sit below the main map. They are drawn when they come near the screen, and redrawn
   only if something changed while they were away, so opening the page and resizing stay cheap. */
let insetDirty = true, insetNear = false;
function flushInsets(){ if(!insetDirty) return; insetDirty = false; insetRenders.forEach(f=>f()); }
function renderInsets(){ insetDirty = true; if(insetNear || !('IntersectionObserver' in window)) flushInsets(); }
if('IntersectionObserver' in window) new IntersectionObserver(es=>{ insetNear = es[es.length-1].isIntersecting; if(insetNear) flushInsets(); }, {rootMargin:'600px 0px'}).observe(document.getElementById('insets'));
INSETS.forEach(ins=>{
  const btn = document.createElement('button'); btn.type='button'; btn.className='inset';
  btn.innerHTML = `<div class="ih"><b>${ins.title}</b><span>${ins.note}</span></div>`;
  const s = d3.select(btn).append('svg').attr('aria-hidden','true');
  btn.addEventListener('click', ()=>{ const f = FOCUS[ins.focus]; if(f.layer && !layerOn[f.layer]) setLayer(f.layer, true); go(f.b); select(ins.info); scrollToMap(); });
  btn.setAttribute('aria-label', `Show ${ins.title} on the map`);
  insetsEl.appendChild(btn);
  const render = ()=>{
    const r = s.node().getBoundingClientRect(); const w = Math.max(120, r.width), h = Math.max(100, r.height);
    s.selectAll('*').remove(); s.attr('viewBox', `0 0 ${w} ${h}`);
    const t = boundsT(ins.b, w, h, 0.95);
    const g = s.append('g').attr('transform', t);
    g.append('use').attr('href','#landP').attr('class','land');
    ins.shapes.forEach(sh=>g.append('path').attr('class', sh[0]).attr('d', sh[1]).style('pointer-events','none'));
    ins.points.forEach(p=>{
      const x = t.applyX(P(p.ll)[0]), y = t.applyY(P(p.ll)[1]);
      const pg = s.append('g').attr('transform', `translate(${x.toFixed(1)},${y.toFixed(1)})`);
      const c = `var(${p.color})`;
      if(p.sym==='diamond') pg.append('path').attr('d','M0,-5.5L5.5,0L0,5.5L-5.5,0Z').style('fill',c).style('stroke','var(--halo)');
      else if(p.sym==='ring'){ pg.append('circle').attr('r',4.5).style('fill','var(--halo)').style('stroke',c).style('stroke-width',2.2); }
      else if(p.sym==='square') pg.append('rect').attr('x',-3.5).attr('y',-3.5).attr('width',7).attr('height',7).style('fill',c).style('stroke','var(--halo)');
      else pg.append('circle').attr('r',2.8).style('fill', p.hollow?'var(--halo)':c).style('stroke', p.hollow?c:'var(--halo)').style('stroke-width',1.4);
      p._g = pg; p._x = x; p._y = y;
    });
    const placed = ins.points.map(p=>({x:p._x-5, y:p._y-5, w:10, h:10}));
    const hit = b => placed.some(q=> b.x < q.x+q.w && b.x+b.w > q.x && b.y < q.y+q.h && b.y+b.h > q.y);
    (ins.tags||[]).forEach(tg=>{ const x = t.applyX(P(tg.ll)[0]), y = t.applyY(P(tg.ll)[1]); const tx = s.append('text').attr('class','lbl small itag').attr('x',x).attr('y',y).attr('text-anchor','middle').text(tg.t); const bb = tx.node().getBBox(); if(bb.x<2||bb.x+bb.width>w-2||bb.y<2) tx.remove(); else placed.push({x:bb.x-2,y:bb.y-1,w:bb.width+4,h:bb.height+2}); });
    ins.points.forEach(p=>{
      const tx = p._g.append('text').attr('class','lbl small').attr('y',3.5).text(p.n);
      const sides = p.a==='l' ? ['l','r'] : ['r','l'];
      let ok = false;
      for(const sd of sides){
        tx.attr('x', sd==='r'?7:-7).attr('text-anchor', sd==='r'?'start':'end');
        const bb = tx.node().getBBox(); const box = {x:p._x+bb.x-2, y:p._y+bb.y-1, w:bb.width+4, h:bb.height+2};
        if(box.x>=2 && box.x+box.w<=w-2 && !hit(box)){ placed.push(box); ok = true; break; }
      }
      if(!ok) tx.remove();
    });
  };
  insetRenders.push(render);
});

