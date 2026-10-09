const path=require('path'); const {chromium}=require('/opt/npm-tools/node_modules/playwright'); const fs=require('fs');
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8'); const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
const VPS = {desk:[1440,900,'light',false], deskd:[1440,900,'dark',false], tab:[820,1180,'light',false], ph:[440,830,'light',true], phd:[440,830,'dark',true], lan:[956,400,'light',true], s1024:[1024,768,'light',false]};
const only=(process.argv[3]||Object.keys(VPS).join(',')).split(',');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--proxy-server=direct://']});
 for(const k of only){ const [w,h,cs,mob]=VPS[k];
  const ctx=await b.newContext({viewport:{width:w,height:h},isMobile:mob,hasTouch:mob,deviceScaleFactor:mob?2:1,colorScheme:cs}); const p=await ctx.newPage(); const errs=[];
  p.on('pageerror',e=>errs.push(e.message));
  await p.route('**/*', r=>{ const u=r.request().url(); if(u.includes('d3.min.js')) return r.fulfill({contentType:'application/javascript',body:d3src}); if(u.includes('topojson-client')) return r.fulfill({contentType:'application/javascript',body:tsrc}); if(u.startsWith('file:')) return r.continue(); return r.abort(); });
  await p.goto('file://'+path.resolve('test.html')); await p.waitForTimeout(1500);
  await p.screenshot({path:`${out}/${k}.png`});
  const m = await p.evaluate(()=>{ const q=s=>{const e=document.querySelector(s); if(!e) return null; const r=e.getBoundingClientRect(); return [Math.round(r.top),Math.round(r.height),Math.round(r.left),Math.round(r.width)]}; return {mast:q('.mast'),hp:q('.headpiece'),cart:q('.cart'),fullbtn:q('#fullbtn'),mapwrap:q('#mapwrap'),sw:document.documentElement.scrollWidth}; });
  console.log(k, JSON.stringify(m), errs.slice(0,3));
  await ctx.close(); }
 await b.close(); })();
