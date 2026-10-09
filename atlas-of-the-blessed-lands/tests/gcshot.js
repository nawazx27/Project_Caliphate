const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
const out=process.argv[2]||'gc'; fs.mkdirSync(out,{recursive:true});
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 const ctx=await b.newContext({viewport:{width:1440,height:900},colorScheme:process.argv[3]||'light'}); const p=await ctx.newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1500);
 await p.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';});
 const mshot=async n=>{ const mw=await p.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await p.waitForTimeout(500); await mw.screenshot({path:`${out}/${n}.png`}); };
 await p.click('#focus button:has-text("Greater Caliphate")'); await p.waitForTimeout(3000); await mshot('gc_whole');
 for(const [n,bb] of [['europe',[[-10,34],[32,50]]],['africa',[[-2,0],[36,24]]],['asia',[[66,7],[92,44]]],['blacksea',[[26,40],[50,50]]]]){
   await p.evaluate(bb=>window.__atlasTest.goB(bb), bb); await p.waitForTimeout(900); await mshot(n);
 }
 const tb=await p.$('#synth .cwrap'); await tb.scrollIntoViewIfNeeded(); await p.waitForTimeout(300); await tb.screenshot({path:`${out}/table.png`});
 const rg=await p.$('#regions'); await rg.scrollIntoViewIfNeeded(); await p.waitForTimeout(600); await rg.screenshot({path:`${out}/regions.png`});
 console.log('errs', errs);
 await b.close(); })();
