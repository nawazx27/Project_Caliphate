/* ---------------- start ---------------- */
/* Version 123: on the usual openings (no link, or a link to a version) the names and markers are built just after the map is
   on screen; any other link (a place, a note) builds everything at once, as before, since it may point at a marker */
const LATER_OK = !location.hash || /^#outline-/.test(location.hash);
OVERLAY_LATER = LATER_OK;
size();
renderStatusTable();
renderLimits();
drawMuq();
applyPreset('overview');
showInfo('intro');
VIEW_SET = true; wrapSel.call(zoom.transform, boundsT(FOCUS[0].b, W, H, undefined, false, true)); update();
focusBtns[0].classList.add('on');
renderInsets();
if(document.fonts && document.fonts.ready) document.fonts.ready.then(()=>{ measure(); measureChrome(); update(); renderInsets(); });
let rt; window.addEventListener('resize', ()=>{ clearTimeout(rt); rt = setTimeout(()=>{ const c = T.invert([W/2,H/2]); size(); wrapSel.call(zoom.transform, d3.zoomIdentity.translate(W/2 - T.k*c[0], H/2 - T.k*c[1]).scale(T.k)); renderInsets(); if(!sheetMode()) document.querySelectorAll('.sheet').forEach(s=>s.classList.remove('open')); }, 150); });
openToken(location.hash.slice(1), true);
{ const ml = document.getElementById('maploading'); if(ml) ml.classList.add('done'); }
if(OVERLAY_LATER) requestAnimationFrame(()=>setTimeout(()=>{ OVERLAY_LATER = false; buildOverlay(); applyLayers(); update(); }, 0));
setTimeout(()=>whenIdle(()=>{ landLOD(0); landLOD(1); landLOD(2); }), 1200);   /* the coarse coastlines, ready before they are needed */
/* Version 120: every version's outline is built in quiet moments after the page opens, one per idle slot, so switching versions is
   instant (the first switch to a version used to build it on the spot and stall the page for a second or two on a phone) */
setTimeout(()=>{ const keys = ['me9','me8','sah','me2','v2','af','eu','ca'];
  const next = () => { const k = keys.shift(); if(!k) return; whenIdle(()=>{ void CX.d[k]; [0,1,2].forEach(lv=>CX.lod(k, lv)); next(); }); };
  next(); }, 2500);
/* rows of chips that scroll sideways fade at the edge that has more */
{ const rows = [...document.querySelectorAll('.viewbar, .focus, .toc, .insets')];
  const fade = el=>{ const more = el.scrollWidth - el.clientWidth > 4; el.classList.toggle('fadeR', more && el.scrollLeft + el.clientWidth < el.scrollWidth - 4); el.classList.toggle('fadeL', more && el.scrollLeft > 4); };
  rows.forEach(el=>{ el.addEventListener('scroll', ()=>fade(el), {passive:true}); fade(el); });
  window.addEventListener('resize', ()=>rows.forEach(fade)); if(document.fonts && document.fonts.ready) document.fonts.ready.then(()=>rows.forEach(fade)); }

/* test hook for automated performance checks (no effect on the page) */
window.__atlasTest = { goB:b=>{ wrapSel.call(zoom.transform, boundsT(b, W, H)); update(); }, go:(x,y,k)=>{ wrapSel.call(zoom.transform, d3.zoomIdentity.translate(x,y).scale(k)); update(); }, T:()=>({x:T.x,y:T.y,k:T.k}), update:()=>update(), bt:(b,wide)=>{ const t=boundsT(b,W,H,undefined,wide); return {x:t.x,y:t.y,k:t.k,W,H,ext:zoom.scaleExtent(),coverK}; } };
