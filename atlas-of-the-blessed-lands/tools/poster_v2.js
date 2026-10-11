/* A poster of V2 (2026-10-11, Nawaz: "Make a beautiful image of V2"). Draws the V2 outline (CALIPH.x) on the atlas's own base map and
   shaded relief, in the atlas's Mercator, and saves posters/v2_poster.png (and the page it is drawn from, posters/v2_poster.html).
   Run: node tools/poster_v2.js   (needs the Playwright Chromium the tests use) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const C = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/caliph.json')));
const W = 3200, H = 2800, M = 70;
/* the outline's rings run the planar way round; d3 reads them on the sphere, so turn any ring that would cover the rest of the globe */
const fixRing = r => d3.geoArea({type:'Polygon', coordinates:[r]}) > 2*Math.PI ? r.slice().reverse() : r;
const V2 = {type:'MultiPolygon', coordinates:C.x.polys.map(p => [fixRing(p[0]), ...p.slice(1).map(r => fixRing(r).slice().reverse())])};
/* frame: V2's extent, with room at the bottom right (the Indian Ocean) for the title */
const proj = d3.geoMercator().fitExtent([[M + 40, M + 60], [W - M - 40, H - M - 60]], {type:'MultiPoint', coordinates:[[6, 47], [79, 47], [6, -13], [79, -13]]});
const P = d3.geoPath(proj).digits(1);
const f = o => topojson.feature(geo, geo.objects[o]);
const countries = f('countries'), lakes = f('lakes'), rivers = f('rivers');
const land = topojson.merge(geo, geo.objects.countries.geometries);
const borders = topojson.mesh(geo, geo.objects.countries, (a, b) => a !== b);
const grat = d3.geoGraticule().step([10, 10])();
/* relief: Mercator rows from 30° W to 104° E and 36.5° S to 60° N (as in src/eng_b.js) */
const r0 = proj([-30, 60]), r1 = proj([104, -36.5]);
const relief = 'data:image/webp;base64,' + fs.readFileSync(path.join(ROOT, 'relief_full.webp')).toString('base64');
const BIG = ['Nile', 'Euphrates', 'Tigris', 'Dicle', 'Fırat', 'Amu Darya', 'Syr Darya', 'Indus', 'Blue Nile', 'White Nile', 'Atbara', 'Helmand', 'Kura', 'Aras', 'Zarafshan', 'Murghab', 'Hari'];
const rivPath = P({type:'FeatureCollection', features:rivers.features});
const PLACES = [
  ['Makkah', 'مكة', 39.826, 21.4225, 'holy'], ['al-Madīnah', 'المدينة', 39.611, 24.467, 'holy'], ['al-Quds', 'القدس', 35.2355, 31.7779, 'capital'],
  ['Dimashq', '', 36.29, 33.51], ['Baghdād', '', 44.36, 33.31], ['al-Qāhira', '', 31.24, 30.04], ['Istanbul', '', 28.98, 41.01], ['Ṭihrān', '', 51.39, 35.69],
  ['Mashhad', '', 59.6, 36.3], ['Samarqand', '', 66.96, 39.65], ['Bukhārā', '', 64.42, 39.77, 'left'], ['Kābul', '', 69.17, 34.53], ['Karāchī', '', 67.0, 24.86],
  ['al-Kharṭūm', '', 32.53, 15.5], ['Addis Ababa', '', 38.75, 9.03], ['Nairobi', '', 36.82, -1.29], ['Ṣanʿāʾ', '', 44.2, 15.35], ['Ṭarābulus', '', 13.19, 32.89],
  ['Tūnis', '', 10.18, 36.8], ['Athens', '', 23.73, 37.98], ['Harāt', '', 62.2, 34.35], ['Masqaṭ', '', 58.4, 23.6], ['Bākū', '', 49.87, 40.41], ['Lahore', '', 74.35, 31.55],
  ['Dar es Salaam', '', 39.28, -6.8], ['Muqdisho', '', 45.34, 2.05], ['Dushanbe', '', 68.77, 38.56], ['Tashkent', '', 69.24, 41.31], ['Ankara', '', 32.86, 39.93],
  ['Iṣfahān', '', 51.67, 32.65], ['al-Riyāḍ', '', 46.72, 24.69], ['Kampala', '', 32.58, 0.35]];
const REGIONS = [['al-Ḥijāz', 'الحجاز', 39.4, 26.3, 0], ['al-Shām', 'الشام', 38.2, 34.6, 0], ['al-ʿIrāq', 'العراق', 44.6, 32.2, 0], ['Miṣr', 'مصر', 29.4, 26.4, 0],
  ['Khurāsān', 'خراسان', 61.5, 33.2, 0], ['Mā warāʾ al-Nahr', 'ما وراء النهر', 63.6, 41.5, -6], ['al-Yaman', 'اليمن', 47.5, 16.8, 0], ['Fāris', 'فارس', 54.0, 29.6, 0],
  ['Bilād al-Rūm', 'بلاد الروم', 33.5, 38.8, 0], ['Ifrīqiya', 'إفريقية', 9.6, 33.6, 0], ['al-Ḥabasha', 'الحبشة', 39.5, 7.8, 0], ['Nūba', 'النوبة', 31.0, 19.5, 0],
  ['al-Sind', 'السند', 68.2, 27.0, 0], ['Sijistān', 'سجستان', 63.6, 30.8, 0], ['Arrān', 'أران', 46.5, 40.6, 0]];
const xy = (lo, la) => proj([lo, la]).map(v => v.toFixed(1));
const star = fs.readFileSync(path.join(ROOT, 'src/star.path'), 'utf8').trim();
const km = (C.x.km2/1e6).toFixed(2);
const places = PLACES.map(([n, ar, lo, la, k]) => { const [x, y] = xy(lo, la);
  if (k === 'capital') return `<g transform="translate(${x},${y})"><path d="${star}" transform="scale(2.6)" class="star"/><text x="18" y="7" class="pl big">${n}</text><text x="18" y="38" class="ar">${ar}</text></g>`;
  if (k === 'holy') return `<g transform="translate(${x},${y})"><circle r="9" class="holy"/><circle r="15" class="holyring"/><text x="22" y="7" class="pl big">${n}</text><text x="22" y="38" class="ar">${ar}</text></g>`;
  if (k === 'left') return `<g transform="translate(${x},${y})"><circle r="5.5" class="dot"/><text x="-11" y="6" class="pl" text-anchor="end">${n}</text></g>`;
  return `<g transform="translate(${x},${y})"><circle r="5.5" class="dot"/><text x="11" y="6" class="pl">${n}</text></g>`; }).join('\n');
const regions = REGIONS.map(([n, ar, lo, la, rot]) => { const [x, y] = xy(lo, la); return `<g transform="translate(${x},${y}) rotate(${rot})"><text class="rg" text-anchor="middle">${n}</text><text class="rgar" y="40" text-anchor="middle">${ar}</text></g>`; }).join('\n');
const fonts = fs.readFileSync(path.join(ROOT, 'test-fonts.css'), 'utf8').replace(/url\('node_modules/g, `url('file://${ROOT}/node_modules`);
/* scale bar: 1,000 km measured at 25° N */
const sb0 = proj([50, 25]), sb1 = proj([50 + 1000/(111.32*Math.cos(25*Math.PI/180)), 25]), sbw = sb1[0] - sb0[0];
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${fonts}
body{margin:0;background:#0d1b26}
svg text{font-family:'Alegreya',serif;font-variant-ligatures:none;font-feature-settings:'liga' 0,'dlig' 0,'calt' 0}
.sea{fill:url(#seaG)}
.grat{fill:none;stroke:#7fa3b5;stroke-opacity:.16;stroke-width:1.2}
.landout{fill:#b9ad93}
.relief{mix-blend-mode:overlay;opacity:.95}
.v2fill{fill:url(#v2G)}
.border{fill:none;stroke:#6b5a3c;stroke-opacity:.35;stroke-width:1.4;stroke-dasharray:7 5}
.coast{fill:none;stroke:#3d4f5a;stroke-opacity:.55;stroke-width:1.3}
.lake{fill:#5f8ea3;stroke:#3d6576;stroke-width:.8}
.riv{fill:none;stroke:#4f88a3;stroke-opacity:.75;stroke-width:1.6;stroke-linejoin:round;stroke-linecap:round}
.glow{fill:none;stroke:#f2c94c;stroke-opacity:.35;stroke-width:22;filter:url(#blur)}
.edge1{fill:none;stroke:#8a6414;stroke-width:7;stroke-linejoin:round}
.edge2{fill:none;stroke:#f3d27a;stroke-width:2.6;stroke-linejoin:round}
.pl{font-size:27px;fill:#2a2116;paint-order:stroke;stroke:#f6ecd2;stroke-width:6px;stroke-opacity:.85;font-weight:500}
.pl.big{font-size:36px;font-weight:700;fill:#1d1408}
.ar{font-family:'Amiri',serif;font-size:30px;fill:#5a3f10;paint-order:stroke;stroke:#f6ecd2;stroke-width:6px;stroke-opacity:.85}
.dot{fill:#2a2116;stroke:#f6ecd2;stroke-width:2.5}
.holy{fill:#1e6b4f;stroke:#f6ecd2;stroke-width:3}
.holyring{fill:none;stroke:#1e6b4f;stroke-width:2.5}
.star{fill:#b8860b;stroke:#3b2a05;stroke-width:.35}
.rg{font-size:40px;font-style:italic;letter-spacing:4px;fill:#6b4a12;fill-opacity:.82;paint-order:stroke;stroke:#f6ecd2;stroke-width:5px;stroke-opacity:.5}
.rgar{font-family:'Amiri',serif;font-size:32px;fill:#6b4a12;fill-opacity:.7}
.sealbl{font-size:42px;font-style:italic;letter-spacing:10px;fill:#a9c9d6;fill-opacity:.7}
.frame1{fill:none;stroke:#c9a227;stroke-width:6}
.frame2{fill:none;stroke:#c9a227;stroke-width:1.6}
.t1{font-size:132px;font-weight:700;fill:#f3d27a;letter-spacing:6px}
.t1ar{font-family:'Amiri',serif;font-size:112px;fill:#f3d27a}
.t2{font-size:50px;font-style:italic;fill:#e9dcc0}
.t2ar{font-family:'Amiri',serif;font-size:56px;fill:#e9dcc0}
.t3{font-family:'Alegreya Sans SC',sans-serif;font-size:36px;letter-spacing:6px;fill:#c9a227}
.t4{font-family:'Alegreya Sans',sans-serif;font-size:26px;fill:#b9b09a}
.sb{fill:#f3d27a}.sbt{font-family:'Alegreya Sans',sans-serif;font-size:26px;fill:#e9dcc0}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs>
 <radialGradient id="seaG" cx="45%" cy="40%" r="80%"><stop offset="0" stop-color="#1d4a5f"/><stop offset=".6" stop-color="#143447"/><stop offset="1" stop-color="#0b1f2c"/></radialGradient>
 <linearGradient id="v2G" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f7e7b9"/><stop offset=".5" stop-color="#f1d896"/><stop offset="1" stop-color="#e8c77a"/></linearGradient>
 <filter id="blur" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="10"/></filter>
 <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%"><feDropShadow dx="0" dy="6" stdDeviation="14" flood-color="#000" flood-opacity=".55"/></filter>
 <clipPath id="frameclip"><rect x="${M}" y="${M}" width="${W-2*M}" height="${H-2*M}"/></clipPath>
 <clipPath id="landclip"><path d="${P(land)}"/></clipPath>
 <clipPath id="v2clip"><path d="${P(V2)}"/></clipPath>
</defs>
<rect width="${W}" height="${H}" fill="#0b1720"/>
<g clip-path="url(#frameclip)">
 <rect x="${M}" y="${M}" width="${W-2*M}" height="${H-2*M}" class="sea"/>
 <path d="${P(grat)}" class="grat"/>
 <path d="${P(land)}" class="landout"/>
 <path d="${P(V2)}" class="glow"/>
 <path d="${P(V2)}" class="v2fill"/>
 <image href="${relief}" x="${r0[0]}" y="${r0[1]}" width="${r1[0]-r0[0]}" height="${r1[1]-r0[1]}" preserveAspectRatio="none" class="relief"/>
 <path d="${P(borders)}" class="border"/>
 <path d="${rivPath}" class="riv"/>
 <path d="${P(lakes)}" class="lake"/>
 <path d="${P(land)}" class="coast"/>
 <path d="${P(V2)}" class="edge1"/>
 <path d="${P(V2)}" class="edge2"/>
 ${regions}
 ${places}
 <text class="sealbl" text-anchor="middle" transform="translate(${xy(18,35.6)[0]},${xy(18,35.6)[1]})">MEDITERRANEAN</text>
 <text class="sealbl" text-anchor="middle" transform="translate(${xy(62,15.5)[0]},${xy(62,15.5)[1]})">ARABIAN SEA</text>
 <text class="sealbl" text-anchor="middle" transform="translate(${xy(38.3,20.2)[0]},${xy(38.3,20.2)[1]}) rotate(58)" style="font-size:28px;letter-spacing:6px">RED SEA</text>
 <text class="sealbl" text-anchor="middle" transform="translate(${xy(51,42.3)[0]},${xy(51,42.3)[1]}) rotate(80)" style="font-size:30px;letter-spacing:6px">CASPIAN</text>
</g>
<g filter="url(#shadow)">
 <rect x="${W-M-1180}" y="${H-M-640}" width="1110" height="580" rx="6" fill="#0e2230" fill-opacity=".92" stroke="#c9a227" stroke-width="3"/>
 <rect x="${W-M-1164}" y="${H-M-624}" width="1078" height="548" rx="4" fill="none" stroke="#c9a227" stroke-width="1.2"/>
</g>
<g transform="translate(${W-M-625},${H-M-640})" text-anchor="middle">
 <text y="140" class="t1">Dār al-Amān</text>
 <text y="282" class="t1ar">دار الأمان</text>
 <text y="358" class="t2">al-Khilāfa al-Amīna</text>
 <text y="424" class="t2ar">الخلافة الأمينة</text>
 <text y="484" class="t3">VERSION 2 · ABOUT ${km} MILLION KM²</text>
 <text y="530" class="t4">Drawn to the author’s specification, not from the sources and not a ruling · Atlas of the Blessed Lands</text>
</g>
<g filter="url(#shadow)"><rect x="${M+40}" y="${H-M-560}" width="${Math.max(380, sbw+120)}" height="520" rx="6" fill="#0e2230" fill-opacity=".9" stroke="#c9a227" stroke-width="2.5"/></g>
<g transform="translate(${M+100},${H-M-130})">
 <rect width="${sbw/2}" height="12" class="sb"/><rect x="${sbw/2}" width="${sbw/2}" height="12" fill="none" stroke="#f3d27a" stroke-width="2"/>
 <text y="52" class="sbt">0</text><text x="${sbw/2}" y="52" class="sbt" text-anchor="middle">500</text><text x="${sbw}" y="52" class="sbt" text-anchor="middle">1,000 km</text>
</g>
<g transform="translate(${M+40+Math.max(380, sbw+120)/2},${H-M-330})" style="color:#f3d27a">${fs.readFileSync(path.join(ROOT, 'src/rose.svg'), 'utf8').replace(/var\(--ink\)/g, '#f3d27a').replace('width="34" height="34"', 'width="240" height="240" x="-120" y="-120"')}<text y="-135" text-anchor="middle" style="font-family:'Alegreya Sans SC';font-size:40px;fill:#f3d27a">N</text></g>
<rect x="${M}" y="${M}" width="${W-2*M}" height="${H-2*M}" class="frame1"/>
<rect x="${M-22}" y="${M-22}" width="${W-2*M+44}" height="${H-2*M+44}" class="frame2"/>
</svg></body></html>`;
fs.mkdirSync(path.join(ROOT, 'posters'), {recursive:true});
const htmlFile = path.join(ROOT, 'posters/v2_poster.html');
fs.writeFileSync(htmlFile, html);
(async () => {
  const {chromium} = require(path.join(ROOT, 'node_modules/playwright'));
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage({viewport:{width:W, height:H}});
  await p.goto('file://' + htmlFile); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1500);
  await p.screenshot({path:path.join(ROOT, 'posters/v2_poster.png')});
  await b.close(); console.log('posters/v2_poster.png', W + 'x' + H);
})();
