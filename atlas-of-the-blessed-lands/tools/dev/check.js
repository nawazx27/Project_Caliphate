// usage: node check.js <dir>  -- loads each outline view, reports page errors and the V5 area sentence
const path = require('path'), fs = require('fs');
const dir = process.argv[2];
const { chromium } = require(path.join(dir, 'node_modules/playwright'));
(async () => {
  const br = await chromium.launch(); const errors = [];
  for (const tok of ['outline-v1', 'outline-v2', 'outline-v3', 'outline-v4', 'outline-v5', 'outline-v6']) {
    const pg = await br.newPage({ viewport: { width: 1400, height: 900 } });
    pg.on('pageerror', e => errors.push(tok + ': ' + e.message));
    pg.on('console', m => { if (m.type() === 'error' && !/favicon|ERR_|net::/.test(m.text())) errors.push(tok + ' console: ' + m.text()); });
    const ND = path.join(dir, 'node_modules');
    await pg.route(/d3(@|\/)7\.9\.0.*d3\.min\.js/, r => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(ND, 'd3/dist/d3.min.js')) }));
    await pg.route(/topojson-client@3\.1\.0.*\.js/, r => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(ND, 'topojson-client/dist/topojson-client.min.js')) }));
    await pg.goto('file://' + path.resolve(dir, 'index.html') + '#' + tok);
    await pg.waitForFunction(() => window.__atlasTest, null, { timeout: 60000 });
    await pg.waitForTimeout(2500);
    const txt = await pg.evaluate(() => { const m = document.body.innerText.match(/(\d+(\.\d+)?) million km²/); return m ? m[0] : null; });
    console.log(tok, 'ok', txt);
    await pg.close();
  }
  await br.close();
  console.log('errors', JSON.stringify(errors));
})();
