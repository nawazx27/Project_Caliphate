// Flexible QA screenshots.  usage: node shot2.js <outdir> <job,job,...>
const path = require('path');
let chromium; try { ({chromium} = require('playwright')); } catch(e){ ({chromium} = require('/opt/npm-tools/node_modules/playwright')); }
const fs = require('fs');
const out = process.argv[2] || 'shots';
const jobs = (process.argv[3] || 'presets').split(',');
fs.mkdirSync(out, {recursive:true});
const d3src = fs.readFileSync('node_modules/d3/dist/d3.min.js','utf8');
const tsrc = fs.readFileSync('node_modules/topojson-client/dist/topojson-client.min.js','utf8');
(async()=>{
  const browser = await chromium.launch({executablePath:'/opt/pw-browsers/chromium', headless:true, args:['--no-sandbox','--disable-background-networking','--disable-sync','--no-first-run','--disable-component-update','--disable-default-apps','--proxy-server=direct://','--proxy-bypass-list=*','--disable-gpu']});
  async function mk(opts){
    const ctx = await browser.newContext(opts);
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
  const mapShot = async (page, name)=>{ const mw = await page.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await page.waitForTimeout(500); await mw.screenshot({path:`${out}/${name}.png`}); };
  async function clickPreset(page, id){ await page.click(`#presets button[data-p="${id}"]`); await page.waitForTimeout(500); }
  async function clickFocus(page, text){ const b = await page.$(`#focus button:has-text("${text}")`); if(b){ await b.click(); await page.waitForTimeout(1600); } else console.log('no focus chip', text); }

  if(jobs.includes('presets')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    for(const p of ['overview','lands','status','roads','everything']){ await clickPreset(page,p); await mapShot(page,'p_'+p); }
    console.log('errs presets', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('dark')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'dark'});
    await page.goto(url); await page.waitForTimeout(1500);
    await page.screenshot({path:out+'/dk_top.png'});
    await mapShot(page,'dk_overview'); await clickPreset(page,'lands'); await mapShot(page,'dk_lands');
    console.log('errs dark', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('focus')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    const chips = await page.$$eval('#focus button', bs=>bs.map(b=>b.textContent));
    console.log('chips:', chips.join(' | '));
    const want = (process.argv[4]||'').split(',').filter(Boolean);
    for(const t of want){ await clickFocus(page, t); await mapShot(page,'f_'+t.replace(/\W+/g,'_')); }
    console.log('errs focus', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('phone')){
    const {ctx,page,errs} = await mk({viewport:{width:390,height:844}, deviceScaleFactor:2, colorScheme:'light', isMobile:true, hasTouch:true});
    await page.goto(url); await page.waitForTimeout(1500);
    await page.screenshot({path:out+'/ph_top.png'});
    await mapShot(page,'ph_map');
    await page.screenshot({path:out+'/ph_map_view.png'});
    const ov = await page.$('#openLayers'); if(ov){ await ov.click(); await page.waitForTimeout(600); await page.screenshot({path:out+'/ph_layers.png'}); await page.keyboard.press('Escape'); }
    console.log('errs phone', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('page')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    const h = await page.evaluate(()=>document.documentElement.scrollHeight);
    console.log('page height', h);
    let i=0; for(let y=0;y<h;y+=900){ await page.evaluate(yy=>window.scrollTo(0,yy), y); await page.waitForTimeout(250); await page.screenshot({path:`${out}/pg_${String(i++).padStart(2,'0')}.png`}); }
    console.log('errs page', errs.slice(0,6)); await ctx.close();
  }

  if(jobs.includes('status')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    const want = (process.argv[4]||'13,14,12,5,9,20').split(',');
    for(const n of want){ await page.click(`#srow-${n} button.sdisc`); await page.waitForTimeout(1800); await mapShot(page,'s_'+n); }
    console.log('errs status', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('sections')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    for(const id of (process.argv[4]||'sacred-status,limits,evidence,today,colophon,synth').split(',')){ const el = await page.$('#'+id); if(el){ await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(300); await el.screenshot({path:`${out}/sec_${id}.png`}); } else console.log('no section', id); }
    const ph = await mk({viewport:{width:390,height:844}, deviceScaleFactor:1.5, colorScheme:'light', isMobile:true, hasTouch:true});
    await ph.page.goto(url); await ph.page.waitForTimeout(1500);
    for(const id of ['sacred-status','today']){ const el = await ph.page.$('#'+id); if(el){ await el.scrollIntoViewIfNeeded(); await ph.page.waitForTimeout(300); const bb = await el.boundingBox(); await ph.page.screenshot({path:`${out}/secph_${id}.png`, clip:{x:0,y:bb.y>0?bb.y:0,width:390,height:Math.min(bb.height,2400)}, fullPage:true}); } }
    console.log('errs sections', errs.slice(0,6), ph.errs.slice(0,6)); await ctx.close(); await ph.ctx.close();
  }

  if(jobs.includes('insets')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    const el = await page.$('#insets'); await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(400); await el.screenshot({path:out+'/insets.png'});
    await page.click('#srow-8 button.sdisc'); await page.waitForTimeout(1800);
    const ic = await page.$('#infocard'); await ic.screenshot({path:out+'/infocard8.png'});
    console.log('errs insets', errs.slice(0,6)); await ctx.close();
  }

  if(jobs.includes('tiers')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    for(const t of ['rev','early','classical','modern']){ await page.click(`#tiers button[data-t="${t}"]`); await page.waitForTimeout(600);
      const mb = await page.$('.mapcol'); await mb.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
      const bb = await mb.boundingBox(); await page.screenshot({path:`${out}/t_${t}.png`, clip:{x:bb.x, y:bb.y, width:bb.width, height:Math.min(bb.height, 900)}}); }
    await page.click('#presets button[data-p="overview"]'); await page.waitForTimeout(300);
    const on = await page.$$eval('#tiers button.on', bs=>bs.map(b=>b.textContent));
    console.log('after preset, tier on:', on, 'cap hidden:', await page.$eval('#tiercap', e=>e.hidden));
    console.log('errs tiers', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('search')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    for(const q of ['aqsa','mecca','dabiq','sham','zz']){
      await page.fill('#placeq', ''); await page.type('#placeq', q, {delay:20}); await page.waitForTimeout(250);
      const items = await page.$$eval('#placelist li', ls=>ls.map(l=>l.innerText.replace(/\n/g,' | ')));
      console.log('Q', q, '=>', JSON.stringify(items.slice(0,6)));
      if(q==='aqsa'){ const mb = await page.$('.mapcol'); const bb = await mb.boundingBox(); await page.screenshot({path:`${out}/q_list.png`, clip:{x:bb.x, y:bb.y, width:bb.width, height:520}}); }
    }
    await page.fill('#placeq',''); await page.type('#placeq','dabiq'); await page.keyboard.press('Enter'); await page.waitForTimeout(1700);
    const mw = await page.$('#mapwrap'); await mw.screenshot({path:`${out}/q_dabiq.png`});
    console.log('note title:', await page.$eval('#infobody h2', e=>e.textContent));
    console.log('share:', await page.$eval('#infobody .sharebox input', e=>e.value).catch(()=>'none'));
    await page.fill('#placeq',''); await page.type('#placeq','yanbu'); await page.keyboard.press('Enter'); await page.waitForTimeout(1700);
    await mw.screenshot({path:`${out}/q_yanbu.png`});
    console.log('errs search', errs.slice(0,6)); await ctx.close();
  }
  if(jobs.includes('hash')){
    for(const h of ['st12','lim-e','who-early','dabiq','madinah']){
      const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
      await page.goto(url+'#'+h); await page.waitForTimeout(2600);
      const t = await page.$eval('#infobody h2', e=>e.textContent).catch(()=>'?');
      const tier = await page.$$eval('#tiers button.on', bs=>bs.map(b=>b.textContent));
      console.log('HASH', h, '-> note:', t, '| tier:', tier.join(','), errs.slice(0,3));
      await ctx.close();
    }
  }

  if(jobs.includes('caliph')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    await page.click('#presets button[data-p="caliph"]'); await page.waitForTimeout(1600);
    await mapShot(page,'c_map');
    const ic = await page.$('#infocard'); await ic.screenshot({path:out+'/c_note.png'});
    const sec = await page.$('#synth'); await sec.scrollIntoViewIfNeeded(); await page.waitForTimeout(300); await sec.screenshot({path:out+'/c_section.png'});
    console.log('errs caliph', errs.slice(0,6)); await ctx.close();
    const d = await mk({viewport:{width:1440,height:900}, colorScheme:'dark'});
    await d.page.goto(url); await d.page.waitForTimeout(1500); await d.page.click('#presets button[data-p="caliph"]'); await d.page.waitForTimeout(1600); await mapShot(d.page,'c_map_dark'); await d.ctx.close();
    const ph = await mk({viewport:{width:390,height:844}, deviceScaleFactor:2, colorScheme:'light', isMobile:true, hasTouch:true});
    await ph.page.goto(url); await ph.page.waitForTimeout(1500);
    const seg = await ph.page.$('#presets button[data-p="caliph"]'); await seg.scrollIntoViewIfNeeded(); await seg.click(); await ph.page.waitForTimeout(1600);
    await mapShot(ph.page,'c_map_phone');
    const s2 = await ph.page.$('#synth'); await s2.scrollIntoViewIfNeeded(); await ph.page.waitForTimeout(300); await s2.screenshot({path:out+'/c_section_phone.png'});
    console.log('errs caliph phone', ph.errs.slice(0,6)); await ph.ctx.close();
  }

  if(jobs.includes('turkey')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    for(const [q,name] of (process.argv[4] ? process.argv[4].split(',').map(x=>[x, 'q_'+x.replace(/\W+/g,'_')]) : [['istanbul','tk_istanbul'],['turkiye and','tk_turkiye']])){
      await page.fill('#placeq',''); await page.type('#placeq', q, {delay:20}); await page.waitForTimeout(250);
      const items = await page.$$eval('#placelist li', ls=>ls.map(l=>l.innerText.replace(/\n/g,' | ')));
      console.log('Q', q, JSON.stringify(items.slice(0,4)));
      await page.keyboard.press('Enter'); await page.waitForTimeout(1800); await mapShot(page, name);
    }
    console.log('errs turkey', errs.slice(0,6)); await ctx.close();
  }

  if(jobs.includes('xv')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    console.log('toggle hidden at start:', await page.$eval('.xtoggle.onmap', e=>e.hidden));
    await page.click('#presets button[data-p="caliph"]'); await page.waitForTimeout(1600);
    console.log('toggle hidden in caliph view:', await page.$eval('.xtoggle.onmap', e=>e.hidden));
    await page.click('.xtoggle.onmap button[data-xv="west"]'); await page.waitForTimeout(700);
    await mapShot(page,'xv_west');
    console.log('note h2:', await page.$eval('#infobody h2', e=>e.textContent));
    console.log('legend:', await page.$eval('.lgx', e=>e.textContent), '| nx:', await page.$eval('.nx', e=>e.textContent));
    console.log('total row:', await page.$eval('#caliphxrows tr.tot', e=>e.innerText.replace(/\s+/g,' ')));
    console.log('share:', await page.$eval('#infobody .sharebox input', e=>e.value).catch(()=>'none'));
    await page.click('.xtoggle.onmap button[data-xv="full"]'); await page.waitForTimeout(700);
    console.log('total row full:', await page.$eval('#caliphxrows tr.tot', e=>e.innerText.replace(/\s+/g,' ')));
    const sec = await page.$('#synth'); await sec.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
    const card = await page.$('.xtoggle.insec'); await card.scrollIntoViewIfNeeded(); await page.waitForTimeout(300); const art = await card.evaluateHandle(e=>e.closest('article')); await art.asElement().screenshot({path:out+'/xv_sec.png'});
    console.log('errs xv', errs.slice(0,6)); await ctx.close();
    const ph = await mk({viewport:{width:390,height:844}, deviceScaleFactor:2, colorScheme:'dark', isMobile:true, hasTouch:true});
    await ph.page.goto(url+'#outline-iraq'); await ph.page.waitForTimeout(2600);
    await mapShot(ph.page,'xv_phone');
    console.log('phone pressed:', await ph.page.$$eval('.xtoggle.onmap button', bs=>bs.map(b=>b.textContent+':'+b.getAttribute('aria-pressed')).join(' ')), ph.errs.slice(0,4));
    await ph.ctx.close();
  }

  if(jobs.includes('gme')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    await page.click('#focus button:has-text("Greater Caliphate")'); await page.waitForTimeout(1500);
    await mapShot(page,'gme');
    // drag-pan with the mouse: screenshot mid-drag to check there is no blank edge
    const mw = await page.$('#mapwrap'); const bb = await mw.boundingBox();
    await page.click('#focus button:has-text("Whole region")'); await page.waitForTimeout(1500);
    await page.mouse.move(bb.x+bb.width/2, bb.y+bb.height/2); await page.mouse.down();
    for(let i=1;i<=12;i++){ await page.mouse.move(bb.x+bb.width/2 + i*18, bb.y+bb.height/2 + i*12); await page.waitForTimeout(16); }
    await mw.screenshot({path:out+'/drag_mid.png'});
    await page.mouse.up(); await page.waitForTimeout(500); await mw.screenshot({path:out+'/drag_end.png'});
    // wheel zoom out to the widest
    await page.mouse.move(bb.x+bb.width/2, bb.y+bb.height/2);
    for(let i=0;i<14;i++){ await page.mouse.wheel(0, 240); await page.waitForTimeout(40); }
    await page.waitForTimeout(900); await mw.screenshot({path:out+'/wheel_out.png'});
    console.log('errs gme', errs.slice(0,6)); await ctx.close();
  }

  if(jobs.includes('taps')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    const mw = await page.$('#mapwrap'); await mw.scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
    await page.click('.sb[data-sel="st8"]'); await page.waitForTimeout(400);
    console.log('tap disc 8 ->', await page.$eval('#infobody h2', e=>e.textContent));
    await page.click('.mapctl #zin'); await page.waitForTimeout(900);
    await page.keyboard.press('Tab');
    await mw.focus().catch(()=>{}); await page.keyboard.press('ArrowDown'); await page.waitForTimeout(500);
    console.log('errs taps', errs.slice(0,6)); await ctx.close();
  }

  if(jobs.includes('gmev')){
    const {ctx,page,errs} = await mk({viewport:{width:1440,height:900}, colorScheme:'light'});
    await page.goto(url); await page.waitForTimeout(1500);
    await page.click('#presets button[data-p="caliph"]'); await page.waitForTimeout(1500);
    await page.click('.xtoggle.onmap button[data-xv="gme"]'); await page.waitForTimeout(1800);
    await mapShot(page,'gmev_map');
    console.log('note h2:', await page.$eval('#infobody h2', e=>e.textContent), '| nx:', await page.$eval('.nx', e=>e.textContent));
    console.log('legend rows visible:', await page.$$eval('[data-lg]', es=>es.filter(e=>!e.hidden).map(e=>e.innerText.replace(/\s+/g,' ')).join(' || ')));
    const ic = await page.$('#infocard'); await ic.screenshot({path:out+'/gmev_note.png'});
    console.log('share:', await page.$eval('#infobody .sharebox input', e=>e.value).catch(()=>'none'));
    await page.click('.xtoggle.onmap button[data-xv="full"]'); await page.waitForTimeout(1200); await mapShot(page,'gmev_full');
    console.log('errs gmev', errs.slice(0,6)); await ctx.close();
    const ph = await mk({viewport:{width:390,height:844}, deviceScaleFactor:2, colorScheme:'dark', isMobile:true, hasTouch:true});
    await ph.page.goto(url+'#outline-gme'); await ph.page.waitForTimeout(3000);
    await mapShot(ph.page,'gmev_phone'); console.log('phone errs', ph.errs.slice(0,4)); await ph.ctx.close();
  }
  await browser.close();
})();
