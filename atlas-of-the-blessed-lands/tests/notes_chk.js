const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 const p=await (await b.newContext({viewport:{width:1440,height:900}})).newPage(); const errs=[]; p.on('pageerror',e=>errs.push(e.message));
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1500);
 for(const h of ['outline-complete','outline-iraq','outline-greater']){ await p.evaluate(h=>location.hash=h, h); await p.waitForTimeout(1800);
   console.log('=== '+h+'\n'+(await p.evaluate(()=>document.getElementById('infobody').innerText)).split('\n').filter(l=>l.trim()).slice(0,9).map(l=>l.slice(0,330)).join('\n')); }
 await p.fill('#placeq','mad'); await p.waitForTimeout(400); console.log('mad →', await p.evaluate(()=>[...document.querySelectorAll('#placelist li')].slice(0,3).map(l=>l.innerText.replace(/\n/g,' ')).join(' | ')));
 await p.fill('#placeq','constantinople'); await p.waitForTimeout(400); console.log('constantinople →', await p.evaluate(()=>[...document.querySelectorAll('#placelist li')].slice(0,4).map(l=>l.innerText.replace(/\n/g,' ')).join(' | ')));
 await p.click('#ly-tuwa ~ * button, [data-info="tuwa"]').catch(()=>{});
 console.log('tuwa text', await p.evaluate(()=>{ const s=document.body.innerHTML; const i=s.indexOf('blessed valley of Ṭuwā'); return i>0; }));
 console.log('errs', errs); await b.close(); })();
