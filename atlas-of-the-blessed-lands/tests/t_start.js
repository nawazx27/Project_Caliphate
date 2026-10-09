const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://','--enable-precise-memory-info','--js-flags=--expose-gc']});
 for(const [n,vp,mob] of [['phone',{width:440,height:830},true],['desk',{width:1440,height:900},false]]){
 const runs=[];
 for(let i=0;i<3;i++){
 const ctx=await b.newContext({viewport:vp,isMobile:mob,hasTouch:mob,deviceScaleFactor:2}); const p=await ctx.newPage();
 await p.addInitScript(()=>{ window.__lt=[]; try{ new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__lt.push(Math.round(e.duration)))).observe({entryTypes:['longtask']}); }catch(e){} });
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 const t0=Date.now(); await p.goto('file://'+path.resolve(process.argv[2]||'test.html'),{waitUntil:'load'}); const tl=Date.now()-t0;
 await p.waitForFunction(()=>window.__atlasTest); const tr=Date.now()-t0; await p.waitForTimeout(1500);
 const m=await p.evaluate(()=>({lt:window.__lt, heap:Math.round(performance.memory.usedJSHeapSize/1e6), nodes:document.querySelectorAll('*').length, svgn:document.querySelectorAll('svg *').length}));
 runs.push({load:tl, ready:tr, ...m}); await ctx.close(); }
 console.log(n, JSON.stringify(runs)); }
 await b.close(); })();
