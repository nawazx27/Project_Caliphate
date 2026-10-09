const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage();
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 await p.goto('file://'+path.resolve(process.argv[2]||'test.html')); await p.waitForTimeout(1500);
 await p.click('#presets button[data-p="everything"]'); await p.waitForTimeout(800);
 for(const chip of ['Jerusalem','Ḥaram of Makkah','al-Shām']){
   await p.click(`#focus button:has-text("${chip}")`); await p.waitForTimeout(3500);
   const r = await p.evaluate(async()=>{ const t=window.__atlasTest.T(); const times=[];
     for(let i=0;i<6;i++){ const t0=performance.now(); window.__atlasTest.go(t.x+ (i%2?40:-40), t.y+20*i, t.k); await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))); times.push(Math.round(performance.now()-t0)); }
     return {k:t.k.toFixed(1), times}; });
   console.log(chip, JSON.stringify(r));
 }
 await b.close(); })();
