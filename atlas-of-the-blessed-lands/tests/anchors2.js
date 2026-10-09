const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 for(const [n,vp,mob] of [['desk',{width:1440,height:900},false],['phone',{width:440,height:830},true]]){
 const ctx=await b.newContext({viewport:vp,isMobile:mob,hasTouch:mob}); const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 await p.goto('file://'+path.resolve(process.argv[2])); await p.waitForTimeout(1500);
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';}); const res=[];
 for(const id of ['evidence','today','honest','synth','regions','sources','colophon','sacred-status','limits']){
   await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(150);
   await p.evaluate(i=>{ document.querySelector('.toc a[href="#'+i+'"]')?.click(); }, id); await p.waitForTimeout(1600);
   res.push(id+':'+await p.evaluate(i=>{ const e=document.getElementById(i); return Math.round(e.getBoundingClientRect().top); }, id));
 }
 // row link from the map notes: status table row scroll
 console.log(n, res.join(' '), errs);
 // inset draws only when near: check count of svg children in insets at top vs after scroll
 await p.evaluate(()=>window.scrollTo(0,0)); await p.waitForTimeout(300);
 await ctx.close(); }
 await b.close(); })();
