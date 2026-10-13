// Assemble the single-file atlas page.
const fs = require('fs');
let esb; try { esb = require('/opt/npm-tools/node_modules/esbuild'); } catch(e){ try { esb = require('esbuild'); } catch(e2){ esb = null; } }
const MIN = esb && !process.argv.includes('--nomin');
const R = f => fs.readFileSync(f, 'utf8');
const gen = JSON.stringify(JSON.parse(R('src/generated.json')));
const relief = 'data:image/webp;base64,' + fs.readFileSync('relief_full.webp').toString('base64');
/* the base maps are TopoJSON whose arcs are already whole-number steps; each arc is packed as text (marker \u0002, see below) */
const packTopo = f => { const t = JSON.parse(R(f)); t.arcs = t.arcs.map(arc => '\u0002' + arc.map(([a, b]) => encNum(a) + encNum(b)).join('')); return JSON.stringify(t).replace(/</g, '\\u003c'); };
/* outline data as a JSON block ("<" escaped so no string can close the script tag) */
/* the V2 province shapes are not drawn on the page (since Version 41): it needs only each province's box, to zoom to it from the notes */
const caliphD = JSON.parse(R('src/caliph.json'));
(caliphD.v2.units || []).forEach(u=>{ let x0 = 180, y0 = 90, x1 = -180, y1 = -90; (u.polys || []).forEach(p=>p[0].forEach(([x,y])=>{ x0 = Math.min(x0,x); x1 = Math.max(x1,x); y0 = Math.min(y0,y); y1 = Math.max(y1,y); }));
  if(x1 > x0) u.b = [x0, y0, x1, y1]; delete u.polys; });
/* every list of points (all are at 0.001°) is packed into a short text: whole-number steps from the point before, written like the
   polyline format (5 bits a character, from '?'); the page unpacks it on load (unpackRings in head.js). Lossless; the data is about a
   third the size. Lists that are not exactly at 0.001° are left as they are. */
const isRing = o => Array.isArray(o) && o.length >= 2 && Array.isArray(o[0]) && o[0].length === 2 && typeof o[0][0] === 'number';
const at3 = r => r.every(q => q.length === 2 && q.every(v => Math.abs(v*1000 - Math.round(v*1000)) < 1e-6));
const encNum = v => { v = v < 0 ? ~(v << 1) : v << 1; let t = ''; while(v >= 0x20){ t += String.fromCharCode((0x20 | (v & 0x1f)) + 63); v >>= 5; } return t + String.fromCharCode(v + 63); };
const encRing = r => { let px = 0, py = 0, t = '\u0001'; for(const [x, y] of r){ const ix = Math.round(x*1000), iy = Math.round(y*1000); t += encNum(ix - px) + encNum(iy - py); px = ix; py = iy; } return t; };
const pack = o => Array.isArray(o) ? (isRing(o) && at3(o) ? encRing(o) : o.map(pack)) : (o && typeof o === 'object') ? Object.fromEntries(Object.entries(o).map(([k, v]) => [k, pack(v)])) : o;
const caliphJ = JSON.stringify(pack(caliphD)).replace(/</g, '\\u003c');
const geo = packTopo('geo2.json'), geoLo = packTopo('landlo.json');
/* Version 98: the two coarse coastlines drawn when zoomed out (landLOD levels 0 and 1 in src/eng_b.js) are made here once,
   with the same projection, data and simplifyD as the page, instead of on the reader's phone each time the page opens */
const landLodJ = (() => {
  const d3n = require('./node_modules/d3'), tj = require('./node_modules/topojson-client'), g = JSON.parse(R('geo2.json'));
  const src = R('src/eng_b.js'), grab = (a, b) => src.slice(src.indexOf(a), src.indexOf(b));
  const simplifyD = new Function(grab('function parseD(', 'function clipRing(') + grab('function simplifyD(', '/* used below k') + 'return simplifyD;')();
  const proj = d3n.geoMercator().fitSize([1000,1000], {type:"MultiPoint", coordinates:[[27,9],[61,41]]});
  const t = g.transform, sx = t ? t.scale[0] : 1, sy = t ? t.scale[1] : 1, tx = t ? t.translate[0] : 0, ty = t ? t.translate[1] : 0;
  const geoP = {type:'Topology', objects:g.objects, arcs:g.arcs.map(arc => { let x = 0, y = 0;
    return arc.map(p => { if(t){ x += p[0]; y += p[1]; } else { x = p[0]; y = p[1]; } return proj([x*sx + tx, y*sy + ty]); }); })};
  const landD = d3n.geoPath()(tj.merge(geoP, geoP.objects.countries.geometries));
  /* packed like the outlines: each ring is 'Z' (closed) or 'O', then whole-number steps in hundredths of a pixel */
  const packD = d => (d.match(/M[^M]*/g) || []).map(r => { const z = /Z\s*$/.test(r); let px = 0, py = 0, t = z ? 'Z' : 'O';
    for(const m of r.matchAll(/[ML]\s*(-?[\d.]+(?:e-?\d+)?)[ ,]+(-?[\d.]+(?:e-?\d+)?)/g)){ const x = Math.round(+m[1]*100), y = Math.round(+m[2]*100); t += encNum(x - px) + encNum(y - py); px = x; py = y; }
    return t; });
  /* Version 123: the same two coarse copies of V2's outline (the version the page opens with), so the opening view does not wait for
     its full 46,000-point path; n (its number of points) lets the page check they were made from this same outline */
  const ringD = rg => 'M' + rg.map(p => proj(p).map(v => v.toFixed(2)).join(',')).join('L') + 'Z';
  const cxD = caliphD.x.polys.map(poly => poly.map(ringD).join('')).join(''), cxN = caliphD.x.polys.flat().reduce((t, r) => t + r.length, 0);
  return JSON.stringify({n:landD.length, lod:[simplifyD(landD, 3), simplifyD(landD, 0.8)].map(packD), cx:{n:cxN, lod:[simplifyD(cxD, 3), simplifyD(cxD, 0.8)].map(packD)}}).replace(/</g, '\\u003c');
})();
const natJ = JSON.stringify(pack(Object.assign(JSON.parse(R('src/nat.json')), {pol: undefined}))).replace(/</g, '\\u003c');   /* Natural + political was removed in Version 60 */

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
<script type="application/json" id="landlod">${landLodJ}</script>
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
