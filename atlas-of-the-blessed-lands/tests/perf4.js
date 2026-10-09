// Real input: frame intervals during a mouse drag and a wheel zoom, measured in the page.
const path=require('path');let chromium;try{({chromium}=require('playwright'))}catch(e){({chromium}=require('/opt/npm-tools/node_modules/playwright'))}
const fs=require('fs');const d3src=fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8');const tsrc=fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',headless:true,args:['--no-sandbox','--proxy-server=direct://','--proxy-bypass-list=*']});
const c=await b.newContext({viewport:{width:1440,height:900}});const p=await c.newPage();
await p.route('**/*',r=>{const u=r.request().url();if(u.includes('d3.min.js'))return r.fulfill({contentType:'application/javascript',body:d3src});if(u.includes('topojson-client'))return r.fulfill({contentType:'application/javascript',body:tsrc});if(u.startsWith('file:'))return r.continue();return r.abort();});
await p.goto('file://'+path.resolve(process.env.PAGE||'test.html'));await p.waitForTimeout(1500);
const mw=await p.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await p.waitForTimeout(500); const bb=await mw.boundingBox();
const startRec=()=>p.evaluate(()=>{ window.__f=[]; let last=performance.now(); window.__on=true; const loop=t=>{ window.__f.push(t-last); last=t; if(window.__on) requestAnimationFrame(loop); }; requestAnimationFrame(loop); });
const stopRec=async name=>{ const f=await p.evaluate(()=>{ window.__on=false; return window.__f.slice(2); }); f.sort((a,b)=>a-b); const q=x=>f[Math.min(f.length-1,Math.floor(f.length*x))].toFixed(0); console.log(name.padEnd(14),'frames',f.length,'median',q(.5),'p90',q(.9),'max',q(.999)); };
const cx=bb.x+bb.width/2, cy=bb.y+bb.height/2;
await p.mouse.move(cx,cy); await startRec(); await p.mouse.down();
for(let i=1;i<=40;i++){ await p.mouse.move(cx+Math.sin(i/6)*160, cy+i*6-120); }
await p.mouse.up(); await stopRec('drag pan');
await p.waitForTimeout(700); await startRec();
for(let i=0;i<24;i++){ await p.mouse.wheel(0, i<12?-120:120); await p.waitForTimeout(16); }
await p.waitForTimeout(400); await stopRec('wheel zoom');
await b.close();})();
