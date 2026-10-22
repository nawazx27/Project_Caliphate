/* Version 211: the premium layer's behaviour (styles at the end of src/style.css). Reading progress, back to top, sections that
   rise into view once, and a soft cross-fade of the note panel. Scroll work is batched into one animation frame; nothing here
   touches the map's drawing. */
(()=>{
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches, doc = document.documentElement;
  const bar = document.createElement('div'); bar.id = 'readbar'; bar.setAttribute('aria-hidden', 'true');
  const top = document.createElement('button'); top.id = 'totop'; top.type = 'button'; top.setAttribute('aria-label', 'Back to the top');
  top.innerHTML = '<svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 10l4.5-4.5 4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  document.body.append(bar, top);
  top.addEventListener('click', ()=>{ window.scrollTo({top:0, behavior: reduce ? 'auto' : 'smooth'}); (document.querySelector('.mast h1') || document.body).focus?.({preventScroll:true}); });
  const mapSec = document.getElementById('map-section');
  let ticking = false;
  const onScroll = () => { if(ticking) return; ticking = true; requestAnimationFrame(()=>{ ticking = false;
    const y = window.scrollY, h = doc.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, y / h) : 0).toFixed(4) + ')';
    const past = mapSec ? mapSec.getBoundingClientRect().bottom < 0 : y > innerHeight * 1.5;
    top.classList.toggle('on', past); }); };
  addEventListener('scroll', onScroll, {passive:true}); addEventListener('resize', onScroll, {passive:true}); onScroll();

  /* sections below the first screen start slightly lowered and transparent, and rise once when they come into view */
  if(!reduce && 'IntersectionObserver' in window && !location.hash){
    const els = [...document.querySelectorAll('.sec, .keyfind')].filter(el => el.getBoundingClientRect().top > innerHeight * 0.9);
    if(els.length){
      els.forEach(el => el.classList.add('rv')); doc.classList.add('reveal-on');
      const io = new IntersectionObserver(es => es.forEach(e => { if(e.isIntersecting){ e.target.classList.remove('rv'); io.unobserve(e.target); } }), {rootMargin:'0px 0px -6% 0px', threshold:0.04});
      els.forEach(el => io.observe(el));
      /* a jump link or search result lands on a section that has not risen yet: show it at once */
      addEventListener('hashchange', ()=>els.forEach(el=>el.classList.remove('rv')));
    }
  }

  /* the note panel: a short ease-in each time its content is replaced */
  const ib = document.getElementById('infobody');
  if(ib && !reduce){ let last = 0; new MutationObserver(()=>{ const now = performance.now(); if(now - last < 120) return; last = now;
    ib.classList.remove('swap'); void ib.offsetWidth; ib.classList.add('swap'); }).observe(ib, {childList:true}); }
})();
