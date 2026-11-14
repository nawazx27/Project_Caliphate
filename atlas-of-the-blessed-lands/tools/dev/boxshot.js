// usage: node boxshot.js <dir with index.html> <out.png> w s e n   (env OV=outline-v5, CLEAN=1 for the clean map)
const { chromium } = require(require('path').join(process.argv[2],'node_modules/playwright'));
const fs = require('fs');
const path = require('path');
const d3 = require(path.join(process.argv[2], 'node_modules/d3'));
(async () => {
  const [dir, out, w, s, e, n] = process.argv.slice(2);
  const proj = d3.geoMercator().fitSize([1000,1000], {type:"MultiPoint", coordinates:[[27,9],[61,41]]});
  const a = proj([+w, +n]), b = proj([+e, +s]);
  const br = await chromium.launch();
  const pg = await br.newPage({ viewport: { width: 1550, height: 1000 }, deviceScaleFactor: 1 });
  const ND = path.join(dir, 'node_modules');
  await pg.route(/d3(@|\/)7\.9\.0.*d3\.min\.js/, r => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(ND, 'd3/dist/d3.min.js')) }));
  await pg.route(/topojson-client@3\.1\.0.*\.js/, r => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(path.join(ND, 'topojson-client/dist/topojson-client.min.js')) }));
  await pg.goto('file://' + path.resolve(dir, 'index.html') + '#' + (process.env.OV || 'outline-v5'));
  await pg.waitForFunction(() => window.__atlasTest, null, { timeout: 60000 });
  await pg.waitForTimeout(4000);
  if (process.env.CLEAN) { await pg.evaluate(() => { const b = [...document.querySelectorAll('[data-clean]')].find(x => x.offsetParent); if (b) b.click(); }); await pg.waitForTimeout(1500); }   // env CLEAN=1: the Clean map view
  await pg.evaluate(bb => { window.__atlasTest.goB(bb); }, [[+w, +s], [+e, +n]]);
  await pg.waitForTimeout(4000);
  await pg.screenshot({ path: out, clip: { x: 88, y: 113, width: 1374, height: 784 } });
  await br.close();
})();
