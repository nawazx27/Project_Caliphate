/* V4 as a dark vintage-atlas poster (2026-10-30, Nawaz, with an "Ottoman Empire, the Sultanate's zenith" poster: "Make a poster of v4 like this").
   Full-bleed Mercator from the Atlantic to the Altai: deep blue sea, parchment land with the shaded relief (tools/relief/shadedrelief.jpg warped
   by tools/poster_relief.py and toned here), V4 in crimson relief with a gold edge, a curved engraved title, a medallion with the flag's star,
   compass roses, classical sea names, a dark vignette, a gold frame with corner rosettes and a cartouche.
   Run: node tools/poster_v4.js  → posters/v4_poster.png (4200×3200) and posters/v4_poster.jpg */
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');
const ROOT = path.join(__dirname, '..');
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const C = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/caliph.json')));
const OUT = path.join(ROOT, 'posters'), TMP = path.join(OUT, 'tmp'), NAME = 'v4_poster';
fs.mkdirSync(TMP, {recursive:true});

const W = 4200, H = 3200, LON0 = -24, LON1 = 94, LATTOP = 59;
const k = W / ((LON1 - LON0) * Math.PI/180);
const proj = d3.geoMercator().scale(k).translate([0, 0]);
const t0 = proj([LON0, LATTOP]); proj.translate([-t0[0], -t0[1] + 0]);
const [tx, ty] = proj.translate();
const P = d3.geoPath(proj).digits(1);
const xy = (lo, la) => proj([lo, la]);

/* relief: warped, then toned to parchment (land) and crimson (V4) */
const rel = path.join(TMP, NAME + '_relief.png');
fs.writeFileSync(path.join(TMP, NAME + '_params.json'), JSON.stringify({k, tx, ty, x0:0, y0:0, w:W, h:H}));
execFileSync('python3', ['-I', path.join(ROOT, 'tools/poster_relief.py'), path.join(TMP, NAME + '_params.json'), rel, path.join(ROOT, 'tools/relief/shadedrelief.jpg')], {stdio:'inherit'});
const par = path.join(TMP, NAME + '_par.jpg'), red = path.join(TMP, NAME + '_red.jpg');
execFileSync('python3', ['-I', '-c', `
import numpy as np
from PIL import Image, ImageFilter
a = np.asarray(Image.open('${rel}').convert('RGB')).astype(np.float32) / 255
L = 0.30*a[...,0] + 0.59*a[...,1] + 0.11*a[...,2]
hp = L - np.asarray(Image.fromarray((L*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))).astype(np.float32)/255
s = np.clip(0.80 + 1.9*hp + 0.25*(L - L.mean()), 0.35, 1.25)[..., None]
Image.fromarray(np.clip(np.array([206, 186, 148]) * s, 0, 255).astype(np.uint8)).save('${par}', quality=88)
Image.fromarray(np.clip(np.array([140, 32, 26]) * (0.10 + 0.85*s) + np.array([20, 4, 2]) * (s - 0.8), 0, 255).astype(np.uint8)).save('${red}', quality=88)
`]);
const b64 = f => 'data:image/jpeg;base64,' + fs.readFileSync(f).toString('base64');

/* geometry */
const fixRing = r => d3.geoArea({type:'Polygon', coordinates:[r]}) > 2*Math.PI ? r.slice().reverse() : r;
const V4 = {type:'MultiPolygon', coordinates:C.me9.polys.map(p => [fixRing(p[0]), ...p.slice(1).map(r => fixRing(r).slice().reverse())])};
const f = o => topojson.feature(geo, geo.objects[o]);
const land = topojson.merge(geo, geo.objects.countries.geometries);
const borders = topojson.mesh(geo, geo.objects.countries, (a, b) => a !== b);
const lakes = f('lakes'), rivers = f('rivers');
const bigLand = {type:'MultiPolygon', coordinates:(land.geometry ? land.geometry : land).coordinates.filter(p => d3.geoArea({type:'Polygon', coordinates:p}) > 1.5e-4).map(p => [p[0]])};
const PR = d3.geoPath(proj).digits(0);

/* title along a curve over the lands, sea names, compasses */
const [ax, ay] = xy(-9, 25.5), [bx, by] = xy(30, 45), [cx2, cy2] = xy(70, 27.5);
const arc = `M${ax},${ay} Q${bx},${by} ${cx2},${cy2}`;
const SEAS = [['al-Baḥr al-Muḥīṭ', -14.5, 45, 52, 0], ['Baḥr al-Rūm', 5.5, 38.6, 50, 0], ['Baḥr al-Hind', 69, 4, 70, 0], ['Baḥr al-Qulzum', 38.3, 20.8, 34, 57], ['Baḥr Fāris', 51.4, 27.3, 30, 34], ['Baḥr al-Khazar', 50.6, 42, 32, 72]];
const rose = (x, y, r) => `<g transform="translate(${x},${y})" opacity=".85">
 <circle r="${r}" fill="none" stroke="#d8b25a" stroke-width="3"/><circle r="${r*0.9}" fill="none" stroke="#d8b25a" stroke-width="1.2" stroke-dasharray="3 7"/>
 ${[0, 45, 90, 135, 180, 225, 270, 315].map(a => { const L = a % 90 ? r*0.55 : r*0.95, w = a % 90 ? r*0.09 : r*0.15; return `<g transform="rotate(${a})"><path d="M0,${-L}L${w},0L0,0Z" fill="#7a5a22"/><path d="M0,${-L}L${-w},0L0,0Z" fill="#e8cf8a"/></g>`; }).join('')}
 <circle r="${r*0.07}" fill="#7a1420" stroke="#e8cf8a" stroke-width="2"/></g>`;
const star = (r) => { let d = ''; for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI/2, q = i % 2 ? r*0.62 : r; d += (i ? 'L' : 'M') + (q*Math.cos(a)).toFixed(1) + ',' + (q*Math.sin(a)).toFixed(1); } return d + 'Z'; };
const [mx, my] = xy(25.5, 23.5);
const corner = (x, y, sx, sy) => `<g transform="translate(${x},${y}) scale(${sx},${sy})" fill="none" stroke="#c9a24a" stroke-width="5" stroke-linecap="round">
 <path d="M0,260 C0,120 40,40 160,0 M0,160 C20,90 60,55 110,40 M40,300 C60,200 120,140 220,120 C170,170 150,200 150,250"/>
 <path d="M60,60 c40,-10 70,20 55,55 c-15,35 -60,25 -55,-10" stroke-width="4"/>
 <circle cx="95" cy="95" r="14" fill="#7a1420" stroke-width="4"/><circle cx="95" cy="95" r="5" fill="#e8cf8a" stroke="none"/>
 <path d="M250,30 c30,-25 70,-25 100,0 M30,250 c-25,30 -25,70 0,100" stroke-width="3.5"/></g>`;

const serpent = (x, y, sc, fl) => `<g transform="translate(${x},${y}) scale(${fl*sc},${sc})" opacity=".9" filter="url(#tsh)">
 <path d="M0,0 c50,-70 120,-70 160,-10 s110,70 160,0 s100,-70 150,-5" fill="none" stroke="#3a2208" stroke-width="46" stroke-linecap="round"/>
 <path d="M0,0 c50,-70 120,-70 160,-10 s110,70 160,0 s100,-70 150,-5" fill="none" stroke="url(#sg)" stroke-width="36" stroke-linecap="round"/>
 <path d="M0,0 c50,-70 120,-70 160,-10 s110,70 160,0 s100,-70 150,-5" fill="none" stroke="#7a1420" stroke-width="6" stroke-dasharray="8 16"/>
 ${[40,85,130,345,390,430].map((t,i)=>`<path d="M${t},${i<3?-52+Math.abs(t-85)*0.5:-52+Math.abs(t-390)*0.4} l18,-48 l18,48z" fill="url(#sg)" stroke="#3a2208" stroke-width="2"/>`).join('')}
 <path d="M462,-5 c30,-45 95,-45 110,0 c-14,35 -70,42 -110,0z" fill="url(#sg)" stroke="#3a2208" stroke-width="3"/><circle cx="525" cy="-8" r="6" fill="#7a1420"/>
 <path d="M548,-2 l40,-8 M548,4 l38,10" stroke="#e8cf8a" stroke-width="4"/>
 <path d="M0,0 c-30,10 -50,40 -40,70 c10,-25 30,-40 45,-45" fill="url(#sg)" stroke="#3a2208" stroke-width="2"/>
 <path d="M150,-25 c-20,-40 -60,-50 -80,-40 c30,5 50,25 60,50z M310,25 c20,40 60,45 80,35 c-30,-5 -50,-25 -60,-45z" fill="url(#sg)" stroke="#3a2208" stroke-width="2" opacity=".9"/></g>`;
const tulip = (x, y, sc, rot) => `<g transform="translate(${x},${y}) rotate(${rot}) scale(${sc})" filter="url(#tsh)">
 <path d="M0,0 C-10,-60 -10,-120 0,-170" fill="none" stroke="url(#sg)" stroke-width="7"/>
 <path d="M0,-90 c-40,-10 -70,-40 -80,-80 c35,10 65,35 80,80z M0,-60 c40,-10 70,-40 80,-80 c-35,10 -65,35 -80,80z" fill="url(#sg)" stroke="#3a2208" stroke-width="2"/>
 <path d="M0,-170 c-35,-5 -50,-40 -42,-80 c12,18 25,26 42,28 c17,-2 30,-10 42,-28 c8,40 -7,75 -42,80z" fill="#8e1620" stroke="url(#sg)" stroke-width="5"/>
 <path d="M0,-176 c-10,-25 -8,-55 0,-78 c8,23 10,53 0,78z" fill="#c23a2c"/><circle cx="0" cy="0" r="16" fill="#7a1420" stroke="url(#sg)" stroke-width="5"/></g>`;
const fonts = fs.readFileSync(path.join(ROOT, 'test-fonts.css'), 'utf8').replace(/url\('node_modules/g, `url('file://${ROOT}/node_modules`);
const km = (C.me9.km2/1e6).toFixed(1);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${fonts}
body{margin:0;background:#000}svg text{font-family:'Alegreya'}</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs>
 <radialGradient id="sea" cx="45%" cy="45%" r="75%"><stop offset="0" stop-color="#2d55b0"/><stop offset=".6" stop-color="#1b3a8a"/><stop offset="1" stop-color="#0d1d4f"/></radialGradient>
 <radialGradient id="vig" cx="50%" cy="48%" r="72%"><stop offset=".45" stop-color="#000" stop-opacity="0"/><stop offset=".8" stop-color="#0a0604" stop-opacity=".62"/><stop offset="1" stop-color="#050302" stop-opacity=".95"/></radialGradient>
 <radialGradient id="med" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#3a9a8f"/><stop offset=".6" stop-color="#1c615b"/><stop offset="1" stop-color="#0b3330"/></radialGradient>
 <linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbe7a8"/><stop offset=".45" stop-color="#d8b25a"/><stop offset=".55" stop-color="#a57a2a"/><stop offset="1" stop-color="#f0d68e"/></linearGradient>
 <clipPath id="land"><path d="${P(land)}"/></clipPath>
 <clipPath id="v4"><path d="${P(V4)}"/></clipPath>
 <filter id="glow" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="14"/></filter>
 <filter id="sh" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx="6" dy="9" stdDeviation="7" flood-color="#000" flood-opacity=".7"/></filter>
 <filter id="tsh"><feDropShadow dx="5" dy="7" stdDeviation="5" flood-color="#000" flood-opacity=".85"/></filter>
 <path id="arc" d="${arc}"/>
 <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4"/><feColorMatrix values="0 0 0 0 .25  0 0 0 0 .16  0 0 0 0 .08  0 0 0 -1.6 1.25"/></filter>
 <filter id="stain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".0035" numOctaves="4" seed="9"/><feColorMatrix values="0 0 0 0 .18  0 0 0 0 .1  0 0 0 0 .04  0 0 0 -2.4 1.3"/></filter>
 <filter id="waves" x="0" y="0" width="100%" height="100%"><feTurbulence type="turbulence" baseFrequency=".0025 .045" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 .62  0 0 0 0 .75  0 0 0 0 1  0 0 0 3 -1.55"/></filter>
 <filter id="soft"><feGaussianBlur stdDeviation="18"/></filter>
 <filter id="soft2"><feGaussianBlur stdDeviation="6"/></filter>
 <mask id="seaM"><rect width="${W}" height="${H}" fill="#fff"/><path d="${P(land)}" fill="#000"/></mask>
 <linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6dc92"/><stop offset=".5" stop-color="#b98a35"/><stop offset="1" stop-color="#e9c873"/></linearGradient>
</defs>
<rect width="${W}" height="${H}" fill="url(#sea)"/>
<rect width="${W}" height="${H}" filter="url(#waves)" opacity=".55" mask="url(#seaM)"/>
<path d="${P(land)}" fill="none" stroke="#8fb0f0" stroke-opacity=".45" stroke-width="34" filter="url(#glow)"/>
<g stroke-linejoin="round" fill="none"><path d="${PR(bigLand)}" stroke="#c8d6f2" stroke-opacity=".5" stroke-width="86"/><path d="${PR(bigLand)}" stroke="#1f43a0" stroke-width="81"/>
<path d="${PR(bigLand)}" stroke="#c8d6f2" stroke-opacity=".55" stroke-width="44"/><path d="${PR(bigLand)}" stroke="#2550b0" stroke-width="40"/></g>
<path d="${P(land)}" fill="none" stroke="#e8dcc0" stroke-opacity=".5" stroke-width="5"/>
<image href="${b64(par)}" width="${W}" height="${H}" clip-path="url(#land)"/>
<rect width="${W}" height="${H}" fill="#3a2410" opacity=".16" clip-path="url(#land)"/>
<rect width="${W}" height="${H}" filter="url(#stain)" clip-path="url(#land)"/>
<path d="${P(rivers)}" fill="none" stroke="#7d6440" stroke-opacity=".55" stroke-width="2.2"/>
<path d="${P(borders)}" fill="none" stroke="#5a4428" stroke-opacity=".38" stroke-width="2" stroke-dasharray="7 5"/>
<g filter="url(#sh)"><image href="${b64(red)}" width="${W}" height="${H}" clip-path="url(#v4)"/></g>
<g clip-path="url(#v4)"><path d="${P(V4)}" fill="none" stroke="#1a0302" stroke-opacity=".75" stroke-width="70" filter="url(#soft)"/>
<path d="${P(V4)}" fill="none" stroke="#ffb08a" stroke-opacity=".35" stroke-width="16" transform="translate(-9,-11)" filter="url(#soft2)"/></g>
<path d="${P(V4)}" fill="none" stroke="#2a0805" stroke-opacity=".55" stroke-width="12" transform="translate(4,6)"/>
<path d="${P(V4)}" fill="none" stroke="#e7c879" stroke-width="5"/>
<path d="${P(V4)}" fill="none" stroke="#fff3c8" stroke-opacity=".5" stroke-width="1.6"/>
<path d="${P(lakes)}" fill="#2048a0" stroke="#d8b25a" stroke-width="1.5" stroke-opacity=".6"/>
<path d="${P(borders)}" fill="none" stroke="#2a0805" stroke-opacity=".28" stroke-width="2" clip-path="url(#v4)"/>
${SEAS.map(([n, lo, la, s, r]) => { const [x, y] = xy(lo, la); return `<text x="${x}" y="${y}" transform="rotate(${r},${x},${y})" text-anchor="middle" style="font-size:${s}px;font-style:italic;letter-spacing:${s*0.12}px;fill:#e8cf8a;opacity:.82">${n}</text>`; }).join('')}
${rose(...xy(-14, -2), 150)}${rose(...xy(58, -9), 120)}
<g filter="url(#tsh)">${[7,6,5,4,3,2,1].map(i => `<text transform="translate(${i*1.6},${i*2.2})" style="font-size:235px;font-weight:700;letter-spacing:72px;fill:#3a2208"><textPath href="#arc" startOffset="50%" text-anchor="middle">DĀR AL-AMĀN</textPath></text>`).join('')}
<text style="font-size:235px;font-weight:700;letter-spacing:72px;fill:url(#gold);stroke:#fff1c0;stroke-width:2;stroke-opacity:.6"><textPath href="#arc" startOffset="50%" text-anchor="middle">DĀR AL-AMĀN</textPath></text></g>
<g transform="translate(${mx},${my})" filter="url(#tsh)">
 <ellipse rx="215" ry="150" fill="url(#gold)"/><ellipse rx="196" ry="132" fill="url(#med)" stroke="#5a3d10" stroke-width="4"/>
 <ellipse rx="176" ry="114" fill="none" stroke="#e8cf8a" stroke-width="3" stroke-dasharray="2 9"/>
 <g transform="translate(0,-22)"><path d="${star(62)}" fill="url(#gold)" stroke="#5a3d10" stroke-width="3"/><path d="${star(34)}" fill="#7a1420" stroke="#e8cf8a" stroke-width="2"/></g>
 <text y="92" text-anchor="middle" style="font-family:'Amiri';font-size:62px;font-weight:700;fill:url(#gold)">الخلافة الأمينة</text>
</g>
${serpent(...xy(-14.5, -2.5), 1.0, 1)}${serpent(...xy(55, -4), 1.0, 1)}
<rect width="${W}" height="${H}" filter="url(#grain)" opacity=".55" style="mix-blend-mode:multiply"/>
<rect width="${W}" height="${H}" fill="url(#vig)"/>
<path d="M0,0H${W}V${H}H0Z M70,70V${H-70}H${W-70}V70Z" fill-rule="evenodd" fill="#140b05"/>
<rect x="70" y="70" width="${W-140}" height="${H-140}" fill="none" stroke="url(#sg)" stroke-width="7"/>
<rect x="22" y="22" width="${W-44}" height="${H-44}" fill="none" stroke="url(#sg)" stroke-width="4"/>
<rect x="46" y="46" width="${W-92}" height="${H-92}" fill="none" stroke="#c9a24a" stroke-width="2" stroke-dasharray="18 10 4 10"/>
${tulip(150, H-150, 1.25, 45)}${tulip(W-150, H-150, 1.25, -45)}${tulip(150, 150, 1.25, 135)}${tulip(W-150, 150, 1.25, -135)}
<rect x="40" y="40" width="${W-80}" height="${H-80}" fill="none" stroke="#c9a24a" stroke-width="6"/>
<rect x="62" y="62" width="${W-124}" height="${H-124}" fill="none" stroke="#c9a24a" stroke-width="2"/>
${corner(62, 62, 1, 1)}${corner(W-62, 62, -1, 1)}${corner(62, H-62, 1, -1)}${corner(W-62, H-62, -1, -1)}
<g transform="translate(${W-760},${H-520})" filter="url(#tsh)">
 <rect width="620" height="330" rx="14" fill="#2a1a0e" stroke="url(#gold)" stroke-width="8"/><rect x="16" y="16" width="588" height="298" rx="8" fill="none" stroke="#c9a24a" stroke-width="2"/>
 <circle cx="16" cy="16" r="12" fill="#7a1420" stroke="#e8cf8a" stroke-width="3"/><circle cx="604" cy="16" r="12" fill="#7a1420" stroke="#e8cf8a" stroke-width="3"/>
 <circle cx="16" cy="314" r="12" fill="#7a1420" stroke="#e8cf8a" stroke-width="3"/><circle cx="604" cy="314" r="12" fill="#7a1420" stroke="#e8cf8a" stroke-width="3"/>
 <text x="310" y="88" text-anchor="middle" style="font-family:'Alegreya Sans SC';font-size:52px;letter-spacing:8px;fill:#e8cf8a">The Fourth Outline</text>
 <text x="310" y="148" text-anchor="middle" style="font-size:40px;fill:#d8c4a0">— V4 —</text>
 <text x="310" y="210" text-anchor="middle" style="font-size:38px;font-style:italic;fill:#e8cf8a">the Atlantic to the Altai</text>
 <text x="310" y="270" text-anchor="middle" style="font-size:34px;fill:#c9b38a">about ${km} million km²</text>
</g>
<g filter="url(#tsh)">
 <text x="${W/2}" y="${H-300}" text-anchor="middle" style="font-family:'Amiri';font-size:96px;font-weight:700;fill:#fff8ea">دار الأمان</text>
 <text x="${W/2}" y="${H-200}" text-anchor="middle" style="font-family:'Alegreya Sans';font-size:64px;font-weight:700;fill:#fff8ea">Dār al-Amān · al-Khilāfa al-Amīna</text>
</g>
<text x="${W/2}" y="${H-88}" text-anchor="middle" style="font-size:26px;font-style:italic;fill:#bfa97f;opacity:.85">Atlas of the Blessed Lands · drawn to the author’s specification: not from the sources and not a ruling · base map Natural Earth, borders as of today</text>
</svg></body></html>`;
const htmlFile = path.join(TMP, NAME + '.html');
fs.writeFileSync(htmlFile, html);
(async () => {
  const {chromium} = require(path.join(ROOT, 'node_modules/playwright'));
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage({viewport:{width:W, height:H}});
  await p.goto('file://' + htmlFile, {timeout:600000}); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(3000);
  await p.screenshot({path:path.join(OUT, NAME + '.png'), timeout:600000});
  await b.close();
  execFileSync('python3', ['-I', '-c', `from PIL import Image; Image.open('${path.join(OUT, NAME + '.png')}').convert('RGB').save('${path.join(OUT, NAME + '.jpg')}', quality=84, optimize=True)`]);
  console.log('posters/' + NAME + '.png and .jpg', W + 'x' + H);
})();
