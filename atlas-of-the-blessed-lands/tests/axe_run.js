const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
const axe = fs.readFileSync(require.resolve('axe-core/axe.min.js'),'utf8');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 for(const [n,vp,cs] of [['desk-light',{width:1440,height:900},'light'],['desk-dark',{width:1440,height:900},'dark'],['phone',{width:440,height:830},'light']]){
 const ctx=await b.newContext({viewport:vp,colorScheme:cs}); const p=await ctx.newPage();
 await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
 await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1500);
 await p.evaluate(()=>{ document.querySelectorAll('[style*="content-visibility"]').forEach(()=>{}); });
 await p.addScriptTag({content:axe});
 const r = await p.evaluate(async()=>{ const res = await axe.run(document, {resultTypes:['violations'], rules:{'region':{enabled:false}}}); return res.violations.map(v=>({id:v.id, impact:v.impact, n:v.nodes.length, help:v.help, ex:v.nodes.slice(0,40).map(x=>x.target.join(' ')+' :: '+(x.failureSummary||'').split('\n').slice(1,3).join(' ').slice(0,180))})); });
 console.log('=== '+n); r.forEach(v=>console.log(v.impact, v.id, v.n, v.help, '\n   '+v.ex.join('\n   ')));
 await ctx.close(); }
 await b.close(); })();
