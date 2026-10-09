const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 // 1. primary library host down: fallback hosts serve
 { const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage(); const errs=[]; const got=[]; p.on('pageerror',e=>errs.push(e.message));
   await p.route('**/*', r=>{ const u=r.request().url(); if(u.startsWith('file:')) return r.continue();
     if(u.includes('cdnjs.cloudflare.com')||u.includes('cdn.jsdelivr.net/npm/topojson')) { got.push('blocked '+u.split('/')[2]); return r.abort(); }
     if(u.includes('cdn.jsdelivr.net/npm/d3@')) { got.push('fallback d3'); return r.fulfill({contentType:'application/javascript',body:d3src}); }
     if(u.includes('unpkg.com/topojson-client')) { got.push('fallback topojson'); return r.fulfill({contentType:'application/javascript',body:tsrc}); }
     return r.abort(); });
   await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1800);
   console.log('fallback:', got, 'ready', await p.evaluate(()=>!!window.__atlasTest), 'loading hidden', await p.evaluate(()=>getComputedStyle(document.getElementById('maploading')).display), errs); }
 // 2. full-screen exit returns to the same place
 for(const vp of [{width:440,height:830,m:true},{width:956,height:410,m:true},{width:1440,height:900,m:false}]){
   const ctx=await b.newContext({viewport:{width:vp.width,height:vp.height},isMobile:vp.m,hasTouch:vp.m}); const p=await ctx.newPage();
   await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
   await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1500);
   await p.evaluate(()=>{ document.documentElement.style.scrollBehavior='auto'; const m=document.getElementById('mapwrap'); window.scrollBy(0, m.getBoundingClientRect().top - 10); });
   await p.waitForTimeout(300); const y0=await p.evaluate(()=>scrollY);
   await p.click('#zfull'); await p.waitForTimeout(800); await p.keyboard.press('Escape'); await p.waitForTimeout(1000);
   const y1=await p.evaluate(()=>scrollY);
   await p.click('#zfull'); await p.waitForTimeout(800); await p.click('#zfull'); await p.waitForTimeout(1000);
   const y2=await p.evaluate(()=>scrollY);
   console.log('fullscreen round trip', vp.width, 'before', y0, 'after Esc', y1, 'after button', y2);
   await ctx.close(); }
 await b.close(); })();
