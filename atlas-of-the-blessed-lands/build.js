// Assemble the single-file atlas page.
const fs = require('fs');
let esb; try { esb = require('/opt/npm-tools/node_modules/esbuild'); } catch(e){ try { esb = require('esbuild'); } catch(e2){ esb = null; } }
const MIN = esb && !process.argv.includes('--nomin');
const R = f => fs.readFileSync(f, 'utf8');
const gen = JSON.stringify(JSON.parse(R('src/generated.json')));
const relief = 'data:image/webp;base64,' + fs.readFileSync('relief_full.webp').toString('base64');
const geo = R('geo2.json').trim();
const geoLo = R('landlo.json').trim();
/* outline data as a JSON block ("<" escaped so no string can close the script tag) */
const caliphJ = JSON.stringify(JSON.parse(R('src/caliph.json'))).replace(/</g, '\\u003c');
const natJ = JSON.stringify(JSON.parse(R('src/nat.json'))).replace(/</g, '\\u003c');

let js = [R('src/head.js'), R('src/old_data.js'), R('src/new_geom.js').replace('__GENERATED__', gen), R('src/new_info.js'), R('src/eng_a.js'), R('src/eng_b.js'), R('src/eng_c.js'), R('src/eng_d.js'), R('src/eng_e.js'), R('src/start.js')].join('\n');
js = js.replace('__RELIEF__', relief) + '\n})();\n';
if(MIN){ const before = js.length; js = esb.transformSync(js, {minify:true, charset:'utf8', target:'es2020', legalComments:'none'}).code; console.log('js', before, '->', js.length); }

const fonts = `<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,500;0,700;1,500&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&family=Alegreya+Sans+SC:wght@500;700&family=Amiri:wght@400;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">`;

let css = R('src/style.css').replace('__GRAIN__', 'data:image/png;base64,' + R('src/grain.b64').trim()).replace('__GRAIN2__', 'data:image/png;base64,' + R('src/grain2.b64').trim());
if(MIN){ const before = css.length; css = esb.transformSync(css, {loader:'css', minify:true, charset:'utf8'}).code; console.log('css', before, '->', css.length); }
let page = `<title>Atlas of the Blessed Lands</title>
${fonts}
<style>
${css}
</style>
${R('src/body.html')}
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<script>/* if a library host is unreachable, try a second one */window.d3||document.write('<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"><\\/script>');window.topojson||document.write('<script src="https://unpkg.com/topojson-client@3.1.0/dist/topojson-client.min.js"><\\/script>');</script>
<script type="application/json" id="geo">${geo}</script>
<script type="application/json" id="geolo">${geoLo}</script>
<script type="application/json" id="caliph">${caliphJ}</script>
<script type="application/json" id="nat">${natJ}</script>
<script>
${js}</script>
`;

// honorific after the name of Allah (standalone or possessive), once
const before = (page.match(/Allah|Allāh/g) || []).length;
// (not inside a person's name such as ʿAbd Allāh, "servant of Allah", where the name is the man's, not a mention of Allah)
const NAME = String.raw`(?<!\b[ʿ'‘]?Abd[ -])(?<!\b[ʿ'‘]?Abd-?)`;
page = page.replace(new RegExp(NAME + String.raw`\b(Allah|Allāh)(?!['’]s)(?![\wāḥ-])(?!\s*ﷻ)`, 'g'), '$1 ﷻ').replace(new RegExp(NAME + String.raw`\bAllah['’]s(?!\s*ﷻ)`, 'g'), m => m + ' ﷻ');
page = page.replace(/ﷻ\s*ﷻ/g, 'ﷻ');
fs.writeFileSync('index.html', page);
// local test copy wrapped like the publish skeleton
fs.writeFileSync('test.html', '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><link rel="stylesheet" href="test-fonts.css"><style>:root{color-scheme:light;padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}body{margin:0;font:14px system-ui,sans-serif;background:#fafaf9}img{max-width:100%}[hidden]{display:none!important}</style></head><body>' + page + '</body></html>');
const bare = (page.match(new RegExp(NAME + String.raw`(Allah|Allāh)(?!['’]?s? ﷻ)`, 'g')) || []).length;
console.log('written', page.length, 'bytes; Allah mentions', before, 'bare after:', bare);
