// iPhone 16 Pro Max checks.  usage: node shot_ip.js <outdir> <job,job,...>
const path = require('path');
let chromium; try { ({chromium} = require('playwright')); } catch(e){ ({chromium} = require('/opt/npm-tools/node_modules/playwright')); }
const fs = require('fs');
const out = process.argv[2] || 'ip';
const jobs = (process.argv[3] || 'base').split(',');
fs.mkdirSync(out, {recursive:true});
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8');
const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
const UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1';
const SIZES = { por:{width:440,height:830}, porfull:{width:440,height:956}, lan:{width:956,height:400}, lansafe:{width:832,height:400} };
(async()=>{
  const browser = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', headless:true, args:['--no-sandbox','--proxy-server=direct://','--proxy-bypass-list=*','--disable-gpu']});
  async function mk(vp, extra){
    const ctx = await browser.newContext(Object.assign({viewport:vp, deviceScaleFactor:2, isMobile:true, hasTouch:true, userAgent:UA, colorScheme:'light'}, extra||{}));
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', e=>errs.push('PAGEERROR '+e.message));
    page.on('console', m=>{ if(m.type()==='error' && !/ERR_FAILED/.test(m.text())) errs.push('console: '+m.text()); });
    await page.route('**/*', route=>{
      const u = route.request().url();
      if(u.includes('d3.min.js')) return route.fulfill({contentType:'application/javascript', body:d3src});
      if(u.includes('topojson-client')) return route.fulfill({contentType:'application/javascript', body:tsrc});
      if(u.startsWith('file:')) return route.continue();
      return route.abort();
    });
    return {ctx,page,errs};
  }
  const url = 'file://'+path.resolve('test.html');
  const ovf = page => page.evaluate(()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth}));
  const rects = page => page.evaluate(()=>{ const r = s=>{ const e=document.querySelector(s); if(!e) return null; const b=e.getBoundingClientRect(); const cs=getComputedStyle(e); return cs.display==='none'||cs.visibility==='hidden' ? 'hidden' : [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)]; };
    return {wrap:r('#mapwrap'), ctl:r('.mapctl'), xt:r('.xtoggle.onmap'), scale:r('.scale'), legend:r('#legend'), layers:r('#layerscard'), notes:r('#infocard'), full:r('#zfull'), bars:r('.mapbars'), fs:!!document.fullscreenElement, cls:document.getElementById('map-section').className}; });

  for(const name of Object.keys(SIZES)){
    if(!jobs.includes('base') && !jobs.includes(name)) continue;
    const vp = SIZES[name];
    const {ctx,page,errs} = await mk(vp);
    await page.goto(url); await page.waitForTimeout(1500);
    await page.screenshot({path:`${out}/${name}_top.png`});
    const mw = await page.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
    await page.evaluate(()=>{ const m=document.getElementById('mapwrap'); window.scrollBy(0, m.getBoundingClientRect().top - 8); }); await page.waitForTimeout(400);
    await page.screenshot({path:`${out}/${name}_map.png`});
    console.log(name, JSON.stringify(await rects(page)), JSON.stringify(await ovf(page)), errs.slice(0,4));
    await ctx.close();
  }
  if(jobs.includes('full')){
    for(const name of ['por','porfull','lan','lansafe']){
      const {ctx,page,errs} = await mk(SIZES[name]);
      await page.goto(url); await page.waitForTimeout(1400);
      await page.click('#fullbtn'); await page.waitForTimeout(900);
      await page.screenshot({path:`${out}/full_${name}.png`});
      console.log('full', name, JSON.stringify(await rects(page)));
      await page.click('#openLayers'); await page.waitForTimeout(500);
      await page.screenshot({path:`${out}/full_${name}_layers.png`});
      await page.click('#layerscard [data-close]'); await page.waitForTimeout(400);
      await page.click('#openNotes'); await page.waitForTimeout(500);
      await page.screenshot({path:`${out}/full_${name}_notes.png`});
      await page.click('#infocard [data-close]'); await page.waitForTimeout(400);
      await page.click('#zfull'); await page.waitForTimeout(700);
      console.log('after exit', name, JSON.stringify(await rects(page)), JSON.stringify(await ovf(page)), errs.slice(0,4));
      await ctx.close();
    }
  }
  if(jobs.includes('hash')){
    const {ctx,page,errs} = await mk(SIZES.por);
    await page.goto(url+'#fullmap'); await page.waitForTimeout(1800);
    await page.screenshot({path:`${out}/hash_fullmap.png`});
    console.log('hash fullmap', JSON.stringify(await rects(page)), errs.slice(0,4));
    await page.keyboard.press('Escape'); await page.waitForTimeout(500);
    console.log('after esc', JSON.stringify(await rects(page)));
    await ctx.close();
  }
  if(jobs.includes('rotate')){
    const {ctx,page,errs} = await mk(SIZES.por);
    await page.goto(url); await page.waitForTimeout(1400);
    await page.evaluate(()=>{ const m=document.getElementById('mapwrap'); window.scrollBy(0, m.getBoundingClientRect().top - 60); }); await page.waitForTimeout(300);
    await page.setViewportSize(SIZES.lan); await page.waitForTimeout(1200);
    await page.screenshot({path:`${out}/rotate_lan.png`});
    console.log('rotated', JSON.stringify(await rects(page)), errs.slice(0,4));
    await page.setViewportSize(SIZES.por); await page.waitForTimeout(1200);
    await page.screenshot({path:`${out}/rotate_back.png`});
    console.log('back', JSON.stringify(await rects(page)), JSON.stringify(await ovf(page)));
    await ctx.close();
  }
  if(jobs.includes('desk')){
    for(const vp of [{width:1440,height:900},{width:820,height:1180}]){
      const ctx = await browser.newContext({viewport:vp}); const page = await ctx.newPage(); const errs=[];
      page.on('pageerror', e=>errs.push('PAGEERROR '+e.message));
      await page.route('**/*', route=>{ const u = route.request().url(); if(u.includes('d3.min.js')) return route.fulfill({contentType:'application/javascript', body:d3src}); if(u.includes('topojson-client')) return route.fulfill({contentType:'application/javascript', body:tsrc}); if(u.startsWith('file:')) return route.continue(); return route.abort(); });
      await page.goto(url); await page.waitForTimeout(1500);
      const mw = await page.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
      await page.screenshot({path:`${out}/desk_${vp.width}.png`});
      await page.click('#zfull'); await page.waitForTimeout(900);
      await page.screenshot({path:`${out}/desk_${vp.width}_full.png`});
      console.log('desk full', vp.width, JSON.stringify(await rects(page)));
      await page.keyboard.press('Escape'); await page.waitForTimeout(600);
      console.log('desk exit', vp.width, JSON.stringify(await rects(page)), JSON.stringify(await ovf(page)), errs.slice(0,4));
      await ctx.close();
    }
  }
  await browser.close();
})();
