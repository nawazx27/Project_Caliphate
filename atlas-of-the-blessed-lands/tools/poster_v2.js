/* V2 as an atlas plate (2026-10-11, Nawaz: "Can the poster be even more beautiful like an Atlas map?").
   A classic atlas page: cream paper, the colour shaded relief (tools/relief/shadedrelief.jpg) warped into the atlas's Mercator by
   tools/poster_relief.py, layered sea tints along the coasts, a 5° graticule with degrees in the margin and a chequered neat line,
   today's countries in spaced capitals, the classical region names in red italic with their Arabic, cities, rivers and lakes; V2 shown
   the atlas way, as a red boundary ribbon with the land outside it veiled. A locator globe, a legend and scale bars in km and miles.
   Run: node tools/poster_v2.js  → posters/v2_atlas.png (3400×3400) and posters/v2_atlas.jpg */
const fs = require('fs'), path = require('path'), {execFileSync} = require('child_process');
const ROOT = path.join(__dirname, '..');
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const C = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/caliph.json')));
const OUT = path.join(ROOT, 'posters'), TMP = path.join(OUT, 'tmp');
fs.mkdirSync(TMP, {recursive:true});

/* page and frame */
const W = 3400, H = 3400, FX = 130, FY = 560, FW = W - 2*FX, FH = H - FY - 130;
const LON0 = 3, LON1 = 82, LATTOP = 47.6;
const k = FW / ((LON1 - LON0) * Math.PI/180);
const proj = d3.geoMercator().scale(k).translate([0, 0]);
const t0 = proj([LON0, LATTOP]); proj.translate([FX - t0[0], FY - t0[1]]);
const [tx, ty] = proj.translate();
const P = d3.geoPath(proj).digits(1);
const xy = (lo, la) => proj([lo, la]);
const latAt = y => (2*Math.atan(Math.exp((ty - y)/k)) - Math.PI/2) * 180/Math.PI;
const LATBOT = latAt(FY + FH);

/* the relief, warped to the frame */
const relPng = path.join(TMP, 'relief.png');
fs.writeFileSync(path.join(TMP, 'params.json'), JSON.stringify({k, tx, ty, x0:FX, y0:FY, w:FW, h:FH}));
execFileSync('python3', ['-I', path.join(ROOT, 'tools/poster_relief.py'), path.join(TMP, 'params.json'), relPng, path.join(ROOT, 'tools/relief/shadedrelief.jpg')], {stdio:'inherit'});
const relief = 'data:image/png;base64,' + fs.readFileSync(relPng).toString('base64');

/* geometry */
const fixRing = r => d3.geoArea({type:'Polygon', coordinates:[r]}) > 2*Math.PI ? r.slice().reverse() : r;
const V2 = {type:'MultiPolygon', coordinates:C.x.polys.map(p => [fixRing(p[0]), ...p.slice(1).map(r => fixRing(r).slice().reverse())])};
const f = o => topojson.feature(geo, geo.objects[o]);
const land = topojson.merge(geo, geo.objects.countries.geometries);
const borders = topojson.mesh(geo, geo.objects.countries, (a, b) => a !== b);
const bigLand = {type:'MultiPolygon', coordinates:(land.geometry ? land.geometry : land).coordinates.filter(p => d3.geoArea({type:'Polygon', coordinates:p}) > 2.5e-4)};
const lakes = f('lakes'), rivers = f('rivers');
const grat = d3.geoGraticule().step([5, 5]).extent([[-10, -40], [100, 70]])();
const km = (C.x.km2/1e6).toFixed(2);

/* labels */
const COUNTRIES = [  /* name, lon, lat, size, inside V2 */
  ['SAUDI ARABIA', 47.6, 22.6, 34, 1], ['LIBYA', 17.5, 27.2, 40, 1], ['SUDAN', 29.6, 15.6, 40, 1], ['SOUTH SUDAN', 30.4, 7.6, 30, 1], ['ETHIOPIA', 39.6, 10.8, 36, 1],
  ['SOMALIA', 45.6, 5.0, 30, 1], ['KENYA', 37.9, 0.9, 30, 1], ['TANZANIA', 33.4, -4.4, 30, 1], ['UGANDA', 32.6, 2.0, 22, 1], ['ERITREA', 38.0, 16.2, 20, 1],
  ['OMAN', 56.4, 20.4, 28, 1], ['SYRIA', 37.8, 35.8, 26, 1], ['TÜRKİYE', 34.5, 39.4, 40, 1], ['IRAN', 56.8, 32.5, 44, 1], ['TURKMENISTAN', 59.0, 39.4, 26, 1],
  ['UZBEKISTAN', 61.0, 43.0, 24, 0], ['TAJIKISTAN', 72.9, 37.75, 22, 1], ['KYRGYZSTAN', 74.8, 41.7, 22, 0], ['KAZAKHSTAN', 66.0, 46.2, 34, 0],
  ['AFGHANISTAN', 66.2, 33.4, 32, 1], ['PAKISTAN', 69.8, 29.8, 34, 1], ['INDIA', 77.5, 22.5, 40, 0], ['GREECE', 21.9, 39.7, 24, 1], ['ITALY', 13.2, 42.4, 28, 0],
  ['ALGERIA', 6.8, 28.0, 36, 0], ['CHAD', 18.6, 15.6, 34, 0], ['NIGER', 8.6, 17.4, 32, 0], ['CENTRAL AFRICAN REP.', 20.6, 6.7, 22, 0], ['D.R. CONGO', 23.0, -3.0, 34, 0],
  ['GEORGIA', 43.4, 42.2, 20, 1], ['AZERBAIJAN', 48.0, 41.0, 18, 1], ['RUSSIA', 44.0, 46.6, 32, 0], ['UKRAINE', 32.5, 47.0, 28, 0], ['BULGARIA', 25.2, 42.8, 18, 0],
  ['ZAMBIA', 27.5, -13.0, 26, 0], ['IRAQ', 43.5, 33.6, 28, 1], ['EGYPT', 28.6, 24.2, 34, 1], ['JORDAN', 36.9, 31.0, 16, 1]];
const REGIONS = [  /* classical names: Latin, Arabic, lon, lat, rotate */
  ['al-Ḥijāz', 'الحجاز', 39.0, 26.6, 0], ['al-Shām', 'الشام', 40.2, 34.7, 0], ['al-ʿIrāq', 'العراق', 45.4, 31.6, 0], ['Miṣr', 'مصر', 30.4, 27.4, 0],
  ['Khurāsān', 'خراسان', 64.2, 36.7, 0], ['Mā warāʾ al-Nahr', 'ما وراء النهر', 64.4, 41.5, -6], ['al-Yaman', 'اليمن', 45.2, 16.9, 0], ['Fāris', 'فارس', 52.8, 29.3, 0],
  ['Bilād al-Rūm', 'بلاد الروم', 31.5, 37.8, 0], ['Ifrīqiya', 'إفريقية', 10.4, 35.0, 0], ['al-Ḥabasha', 'الحبشة', 38.2, 7.4, 0], ['al-Nūba', 'النوبة', 31.4, 19.6, 0],
  ['al-Sind', 'السند', 68.4, 26.6, 0], ['Sijistān', 'سجستان', 62.4, 30.6, 0], ['Arrān', 'أران', 46.9, 39.7, 0], ['Barqa', 'برقة', 22.2, 31.0, 0], ['al-Jibāl', 'الجبال', 48.6, 34.6, 0]];
const SEAS = [  /* name, classical, lon, lat, size, rotate */
  ['MEDITERRANEAN SEA', 'Baḥr al-Rūm', 19.5, 34.3, 44, 0], ['BLACK SEA', 'Baḥr al-Aswad', 34.0, 43.4, 34, 0], ['RED SEA', 'Baḥr al-Qulzum', 37.9, 21.4, 28, 58],
  ['PERSIAN GULF', 'Baḥr Fāris', 51.6, 27.0, 24, 32], ['ARABIAN SEA', '', 63.0, 16.0, 46, 0], ['CASPIAN SEA', '', 50.8, 42.0, 26, 72], ['GULF OF ADEN', '', 48.6, 12.4, 22, 14],
  ['INDIAN OCEAN', 'Baḥr al-Hind', 47.8, -9.9, 42, 0], ['ARAL SEA', '', 59.6, 45.3, 16, 0]];
const PLACES = [  /* name, lon, lat, kind: cap = capital, holy, quds, city; dx side */
  ['Makkah', 39.826, 21.4225, 'holy', 'مكة'], ['al-Madīnah', 39.611, 24.467, 'holy', 'المدينة'], ['al-Quds', 35.2355, 31.7779, 'quds', 'القدس', 'L'],
  ['Dimashq', 36.29, 33.51, 'cap'], ['Baghdād', 44.36, 33.31, 'cap'], ['al-Qāhira', 31.24, 30.04, 'cap'], ['Istanbul', 28.98, 41.01, 'city'], ['Ankara', 32.86, 39.93, 'cap'],
  ['Ṭihrān', 51.39, 35.69, 'cap'], ['Mashhad', 59.6, 36.3, 'city'], ['Samarqand', 66.96, 39.65, 'city'], ['Bukhārā', 64.42, 39.77, 'city', '', 'L'], ['Kābul', 69.17, 34.53, 'cap'],
  ['Islamabad', 73.05, 33.68, 'cap'], ['Karāchī', 67.0, 24.86, 'city'], ['Lahore', 74.35, 31.55, 'city'], ['al-Kharṭūm', 32.53, 15.5, 'cap'], ['Addis Ababa', 38.75, 9.03, 'cap'],
  ['Nairobi', 36.82, -1.29, 'cap'], ['Kampala', 32.58, 0.35, 'cap'], ['Dodoma', 35.74, -6.17, 'cap'], ['Dar es Salaam', 39.28, -6.8, 'city'], ['Muqdisho', 45.34, 2.05, 'cap'],
  ['Ṣanʿāʾ', 44.2, 15.35, 'cap'], ['Masqaṭ', 58.4, 23.6, 'cap'], ['al-Riyāḍ', 46.72, 24.69, 'cap'], ['Ṭarābulus', 13.19, 32.89, 'cap'], ['Tūnis', 10.18, 36.8, 'cap'],
  ['Athens', 23.73, 37.98, 'cap'], ['Baku', 49.87, 40.41, 'cap'], ['Tbilisi', 44.79, 41.72, 'cap', '', 'L'], ['Yerevan', 44.51, 40.18, 'cap', '', 'L'], ['Ashgabat', 58.38, 37.95, 'cap'],
  ['Dushanbe', 68.77, 38.56, 'cap'], ['Tashkent', 69.24, 41.31, 'cap'], ['Harāt', 62.2, 34.35, 'city'], ['Iṣfahān', 51.67, 32.65, 'city'], ['Bayrūt', 35.5, 33.89, 'cap', '', 'L'],
  ['ʿAmmān', 35.93, 31.95, 'cap'], ['al-Kuwayt', 47.98, 29.37, 'cap'], ['Abū Ẓabī', 54.37, 24.45, 'cap', '', 'L'], ['al-Dawḥa', 51.53, 25.29, 'cap', '', 'L'], ['Asmara', 38.93, 15.32, 'cap'],
  ['Juba', 31.58, 4.85, 'cap'], ['Kigali', 30.06, -1.94, 'cap', '', 'L'], ['Gitega', 29.93, -3.43, 'cap', '', 'L'], ['Jibūtī', 43.15, 11.59, 'cap'], ['Hargeisa', 44.06, 9.56, 'city'],
  ['Nīqūsiya', 33.36, 35.17, 'cap'], ['Basra', 47.78, 30.51, 'city'], ['Bishkek', 74.59, 42.87, 'cap'], ['Alexandria', 29.92, 31.2, 'city', '', 'L'], ['Benghazi', 20.07, 32.12, 'city']];
const H2 = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
const lbl = [];
for (const [n, lo, la, sz, inV] of COUNTRIES) { const [x, y] = xy(lo, la);
  lbl.push(`<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" class="cty ${inV ? 'in' : 'out'}" style="font-size:${sz}px;letter-spacing:${(sz*0.32).toFixed(1)}px" text-anchor="middle">${H2(n)}</text>`); }
for (const [n, ar, lo, la, rot] of REGIONS) { const [x, y] = xy(lo, la);
  lbl.push(`<g transform="translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${rot})"><text class="rg" text-anchor="middle">${H2(n)}</text><text class="rgar" y="38" text-anchor="middle">${ar}</text></g>`); }
for (const [n, cl, lo, la, sz, rot] of SEAS) { const [x, y] = xy(lo, la);
  lbl.push(`<g transform="translate(${x.toFixed(1)},${y.toFixed(1)}) rotate(${rot})"><text class="sea" style="font-size:${sz}px;letter-spacing:${(sz*0.3).toFixed(1)}px" text-anchor="middle">${n}</text>${cl ? `<text class="seacl" y="${(sz*0.95).toFixed(0)}" style="font-size:${Math.max(20, sz*0.62).toFixed(0)}px" text-anchor="middle">${cl}</text>` : ''}</g>`); }
for (const [n, lo, la, kind, ar, side] of PLACES) { const [x, y] = xy(lo, la), L = side === 'L', a = L ? 'end' : 'start';
  let sym, cls = 'pl', dx = 13;
  if (kind === 'holy') { sym = `<circle r="10" class="holy"/><circle r="4" fill="#fff"/>`; cls = 'pl big'; dx = 18; }
  else if (kind === 'quds') { sym = `<path d="M0,-15L4.4,-6L14.3,-4.6L7.1,2.3L8.8,12.1L0,7.5L-8.8,12.1L-7.1,2.3L-14.3,-4.6L-4.4,-6Z" class="quds"/>`; cls = 'pl big'; dx = 18; }
  else if (kind === 'cap') sym = `<rect x="-6.5" y="-6.5" width="13" height="13" class="cap"/><circle r="2.6" fill="#fff"/>`;
  else sym = `<circle r="5.5" class="city"/>`;
  lbl.push(`<g transform="translate(${x.toFixed(1)},${y.toFixed(1)})">${sym}<text x="${L ? -dx : dx}" y="8" class="${cls}" text-anchor="${a}">${H2(n)}</text>${ar ? `<text x="${L ? -dx : dx}" y="42" class="ar" text-anchor="${a}">${ar}</text>` : ''}</g>`); }

/* margin: degrees and a chequered neat line (1° segments) */
const marg = [];
for (let lo = Math.ceil(LON0); lo <= LON1; lo++) { const x0 = xy(lo, 0)[0], x1 = xy(lo + 1, 0)[0]; if (x1 > FX + FW + 0.5) break;
  const c = lo % 2 ? '#2b2620' : '#f6efdc';
  marg.push(`<rect x="${x0.toFixed(1)}" y="${FY - 16}" width="${(x1 - x0).toFixed(1)}" height="12" fill="${c}"/><rect x="${x0.toFixed(1)}" y="${FY + FH + 4}" width="${(x1 - x0).toFixed(1)}" height="12" fill="${c}"/>`);
  if (lo % 5 === 0) { const t = `${lo}°E`; marg.push(`<text x="${x0.toFixed(1)}" y="${FY - 30}" class="deg" text-anchor="middle">${t}</text><text x="${x0.toFixed(1)}" y="${FY + FH + 52}" class="deg" text-anchor="middle">${t}</text>`); } }
for (let la = Math.ceil(LATBOT); la < LATTOP; la++) { const y0 = xy(0, la)[1], y1 = Math.max(xy(0, la + 1)[1], FY); if (y0 > FY + FH + 0.5) continue;
  const c = la % 2 ? '#2b2620' : '#f6efdc', yb = Math.min(y0, FY + FH);
  marg.push(`<rect x="${FX - 16}" y="${y1.toFixed(1)}" width="12" height="${(yb - y1).toFixed(1)}" fill="${c}"/><rect x="${FX + FW + 4}" y="${y1.toFixed(1)}" width="12" height="${(yb - y1).toFixed(1)}" fill="${c}"/>`);
  if (la % 5 === 0) { const t = la === 0 ? 'Equator' : `${Math.abs(la)}°${la > 0 ? 'N' : 'S'}`;
    marg.push(`<text x="${FX - 30}" y="${(y0 + 9).toFixed(1)}" class="deg" text-anchor="end">${t}</text><text x="${FX + FW + 30}" y="${(y0 + 9).toFixed(1)}" class="deg">${t}</text>`); } }

/* locator globe */
const gR = 190, gproj = d3.geoOrthographic().rotate([-42, -22]).scale(gR).translate([0, 0]).clipAngle(90), G = d3.geoPath(gproj).digits(1);
const globe = `<g transform="translate(${FX + 250},${FY - 300})">
  <circle r="${gR + 14}" fill="none" stroke="#7a5c2e" stroke-width="2"/><circle r="${gR}" fill="url(#globeSea)"/>
  <path d="${G(d3.geoGraticule().step([30, 30])())}" fill="none" stroke="#5c88a3" stroke-opacity=".35" stroke-width="1"/>
  <path d="${G(land)}" fill="#e3d8b6" stroke="#8a7a58" stroke-width=".8"/>
  <path d="${G(V2)}" fill="#b3202a" fill-opacity=".85" stroke="#6e0f15" stroke-width="1.2"/>
  <circle r="${gR}" fill="url(#globeShade)"/></g>`;

/* scale bars (true at 25° N) */
const pxKm = (xy(51, 25)[0] - xy(50, 25)[0]) / (111.32*Math.cos(25*Math.PI/180));
const bar = (len, unit, perKm, y) => { const w = len*perKm*pxKm, n = 4; let s = '';
  for (let i = 0; i < n; i++) s += `<rect x="${(i*w/n).toFixed(1)}" y="${y}" width="${(w/n).toFixed(1)}" height="10" fill="${i % 2 ? '#f6efdc' : '#2b2620'}" stroke="#2b2620" stroke-width="1.2"/>`;
  for (let i = 0; i <= n; i++) s += `<text x="${(i*w/n).toFixed(1)}" y="${y + 38}" class="sbt" text-anchor="middle">${len*i/n}${i === n ? ' ' + unit : ''}</text>`;
  return s; };

const fonts = fs.readFileSync(path.join(ROOT, 'test-fonts.css'), 'utf8').replace(/url\('node_modules/g, `url('file://${ROOT}/node_modules`);
const LW = 1020, LH = 760, LX = [FX + FW - LW - 50, xy(0, 9.5)[1]];   /* legend box, in the Arabian Sea / Indian Ocean */
const html = `<!doctype html><html><head><meta charset="utf-8"><style>${fonts}
body{margin:0;background:#efe5cc}
svg text{font-family:'Alegreya',serif;font-variant-ligatures:none}
.paper{fill:url(#paper)}
.cty{font-family:'Alegreya Sans SC',sans-serif;font-weight:500;paint-order:stroke;stroke-linejoin:round}
.cty.in{fill:#4a3b2a;stroke:#f3ead2;stroke-width:5px;stroke-opacity:.6}
.cty.out{fill:#6d6a62;stroke:#eeeee8;stroke-width:5px;stroke-opacity:.55}
.rg{font-size:40px;font-style:italic;fill:#a01d24;letter-spacing:2px;paint-order:stroke;stroke:#fbf3dc;stroke-width:6px;stroke-opacity:.75;stroke-linejoin:round}
.rgar{font-family:'Amiri',serif;font-size:31px;fill:#a01d24;fill-opacity:.85;paint-order:stroke;stroke:#fbf3dc;stroke-width:5px;stroke-opacity:.7}
.sea{font-style:italic;fill:#2f6a8c;fill-opacity:.85}
.seacl{font-style:italic;fill:#2f6a8c;fill-opacity:.75}
.pl{font-size:27px;fill:#1f1a14;paint-order:stroke;stroke:#fbf6e6;stroke-width:6px;stroke-opacity:.85;stroke-linejoin:round}
.pl.big{font-size:36px;font-weight:700}
.ar{font-family:'Amiri',serif;font-size:30px;fill:#1f4d3a;paint-order:stroke;stroke:#fbf6e6;stroke-width:6px;stroke-opacity:.85}
.city{fill:#fbf6e6;stroke:#1f1a14;stroke-width:3}
.cap{fill:#1f1a14;stroke:#fbf6e6;stroke-width:1.5}
.holy{fill:#1e6b4f;stroke:#fbf6e6;stroke-width:3}
.quds{fill:#c99a1e;stroke:#3b2a05;stroke-width:2}
.deg{font-family:'Alegreya Sans',sans-serif;font-size:28px;fill:#4a3f30}
.sbt{font-family:'Alegreya Sans',sans-serif;font-size:24px;fill:#2b2620}
.lg{font-family:'Alegreya Sans',sans-serif;font-size:27px;fill:#2b2620}
.lgh{font-family:'Alegreya Sans SC',sans-serif;font-size:32px;letter-spacing:5px;fill:#7a1219}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">
<defs>
 <radialGradient id="paper" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#f8f0db"/><stop offset=".75" stop-color="#efe3c4"/><stop offset="1" stop-color="#e2d2aa"/></radialGradient>
 <radialGradient id="globeSea" cx="40%" cy="35%" r="70%"><stop offset="0" stop-color="#cfe4ef"/><stop offset="1" stop-color="#8db6cd"/></radialGradient>
 <radialGradient id="globeShade" cx="35%" cy="30%" r="75%"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1b2a33" stop-opacity=".45"/></radialGradient>
 <filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 .45  0 0 0 0 .38  0 0 0 0 .25  0 0 0 .07 0"/></filter>
 <clipPath id="frame"><rect x="${FX}" y="${FY}" width="${FW}" height="${FH}"/></clipPath>
 <clipPath id="landc"><path d="${P(land)}"/></clipPath>
 <clipPath id="v2c"><path d="${P(V2)}"/></clipPath>
 <mask id="outside"><rect x="0" y="0" width="${W}" height="${H}" fill="#fff"/><path d="${P(V2)}" fill="#000"/></mask>
</defs>
<rect width="${W}" height="${H}" class="paper"/>
<rect width="${W}" height="${H}" filter="url(#grain)"/>
<g clip-path="url(#frame)">
 <rect x="${FX}" y="${FY}" width="${FW}" height="${FH}" fill="#9cc3da"/>
 <path d="${P(bigLand)}" fill="none" stroke="#acd0e3" stroke-width="150" stroke-linejoin="round"/>
 <path d="${P(bigLand)}" fill="none" stroke="#bad8e8" stroke-width="84" stroke-linejoin="round"/>
 <path d="${P(bigLand)}" fill="none" stroke="#c9e1ee" stroke-width="40" stroke-linejoin="round"/>
 <path d="${P(land)}" fill="none" stroke="#d8eaf3" stroke-width="14" stroke-linejoin="round"/>
 <g clip-path="url(#landc)"><image href="${relief}" x="${FX}" y="${FY}" width="${FW}" height="${FH}" preserveAspectRatio="none" style="filter:saturate(.92) contrast(1.04)"/></g>
 <path d="${P(land)}" fill="#f6f2e6" fill-opacity=".52" mask="url(#outside)"/>
 <path d="${P(grat)}" fill="none" stroke="#3f6f8f" stroke-opacity=".38" stroke-width="1.3"/>
 <path d="${P(rivers)}" fill="none" stroke="#3d7fb0" stroke-width="2" stroke-opacity=".85" stroke-linejoin="round" stroke-linecap="round"/>
 <path d="${P(lakes)}" fill="#a9cfe4" stroke="#3d7fb0" stroke-width="1.4"/>
 <path d="${P(borders)}" fill="none" stroke="#fbf6e6" stroke-opacity=".8" stroke-width="6"/>
 <path d="${P(borders)}" fill="none" stroke="#6a4f78" stroke-width="2.4" stroke-dasharray="14 5 3 5"/>
 <path d="${P(land)}" fill="none" stroke="#2f5f7d" stroke-width="2.2" stroke-opacity=".9"/>
 <g clip-path="url(#v2c)"><path d="${P(V2)}" fill="none" stroke="#c2262f" stroke-opacity=".32" stroke-width="56" stroke-linejoin="round"/></g>
 <path d="${P(V2)}" fill="none" stroke="#fbf6e6" stroke-width="9" stroke-linejoin="round" stroke-opacity=".9"/>
 <path d="${P(V2)}" fill="none" stroke="#9c1a22" stroke-width="5" stroke-linejoin="round"/>
 ${lbl.join('\n ')}
 <g transform="translate(${LX[0]},${LX[1]})">
  <rect width="${LW}" height="${LH}" fill="#fbf6e6" fill-opacity=".95" stroke="#2b2620" stroke-width="2.5"/>
  <rect x="10" y="10" width="${LW - 20}" height="${LH - 20}" fill="none" stroke="#2b2620" stroke-width="1"/>
  <text x="${LW/2}" y="68" class="lgh" text-anchor="middle">LEGEND · مفتاح</text>
  <g transform="translate(50,120)">
   <rect width="90" height="38" fill="#c2262f" fill-opacity=".32"/><line x1="0" y1="2" x2="90" y2="2" stroke="#9c1a22" stroke-width="5"/>
   <text x="115" y="30" class="lg">Boundary of V2, Dār al-Amān (the author’s specification)</text>
   <line x1="0" y1="92" x2="90" y2="92" stroke="#6a4f78" stroke-width="2.4" stroke-dasharray="14 5 3 5"/><text x="115" y="101" class="lg">International boundary (today)</text>
   <circle cx="45" cy="150" r="10" class="holy"/><circle cx="45" cy="150" r="4" fill="#fff"/><text x="115" y="160" class="lg">The two Ḥarams: Makkah and al-Madīnah</text>
   <path transform="translate(45,206)" d="M0,-15L4.4,-6L14.3,-4.6L7.1,2.3L8.8,12.1L0,7.5L-8.8,12.1L-7.1,2.3L-14.3,-4.6L-4.4,-6Z" class="quds"/><text x="115" y="218" class="lg">al-Quds, the capital the author names</text>
   <rect x="38.5" y="257.5" width="13" height="13" class="cap"/><circle cx="45" cy="264" r="2.6" fill="#fff"/><text x="115" y="274" class="lg">National capital (today)</text>
   <circle cx="45" cy="318" r="5.5" class="city"/><text x="115" y="328" class="lg">Other city</text>
   <text x="45" y="388" text-anchor="middle" class="rg" style="font-size:34px">Miṣr</text><text x="115" y="384" class="lg">Classical region name (red italic, with its Arabic)</text>
  </g>
  <g transform="translate(60,${LH - 150})">${bar(1000, 'km', 1, 0)}</g>
  <g transform="translate(60,${LH - 82})">${bar(600, 'miles', 1.609344, 0)}</g>
  <text x="${LW - 50}" y="${LH - 128}" class="lg" text-anchor="end" style="font-size:23px">Mercator projection</text>
  <text x="${LW - 50}" y="${LH - 96}" class="lg" text-anchor="end" style="font-size:23px">scales true at 25° N</text>
 </g>
</g>
<rect x="${FX}" y="${FY}" width="${FW}" height="${FH}" fill="none" stroke="#2b2620" stroke-width="3"/>
<rect x="${FX - 16}" y="${FY - 16}" width="${FW + 32}" height="${FH + 32}" fill="none" stroke="#2b2620" stroke-width="2"/>
<rect x="${FX - 4}" y="${FY - 4}" width="${FW + 8}" height="${FH + 8}" fill="none" stroke="#2b2620" stroke-width="1.2"/>
${marg.join('\n')}
${globe}
<g text-anchor="middle">
 <text x="${W/2}" y="160" style="font-family:'Alegreya Sans SC';font-size:40px;letter-spacing:16px;fill:#7a1219">ATLAS OF THE BLESSED LANDS · PLATE II</text>
 <text x="${W/2}" y="300" style="font-size:150px;font-weight:700;letter-spacing:10px;fill:#2b2620">DĀR AL-AMĀN</text>
 <text x="${W/2}" y="400" style="font-family:'Amiri';font-size:76px;fill:#7a1219">دار الأمان · الخلافة الأمينة</text>
 <text x="${W/2}" y="466" style="font-size:40px;font-style:italic;fill:#4a3f30">al-Khilāfa al-Amīna · Version 2 · about ${km} million km²</text>
</g>
<g transform="translate(${W - FX - 250},${FY - 300})">
 <circle r="150" fill="none" stroke="#7a5c2e" stroke-width="2"/><circle r="138" fill="none" stroke="#7a5c2e" stroke-width="1" stroke-dasharray="2 6"/>
 ${[0, 45, 90, 135, 180, 225, 270, 315].map(a => { const L = a % 90 ? 70 : 128, w = a % 90 ? 12 : 20; return `<g transform="rotate(${a})"><path d="M0,${-L}L${w},0L0,0Z" fill="#2b2620"/><path d="M0,${-L}L${-w},0L0,0Z" fill="${a ? '#d9c9a0' : '#9c1a22'}" stroke="#2b2620" stroke-width="1"/></g>`; }).join('')}
 <circle r="9" fill="#9c1a22" stroke="#2b2620" stroke-width="1.5"/>
 <text y="-162" text-anchor="middle" style="font-family:'Alegreya Sans SC';font-size:40px;fill:#7a1219">N</text>
</g>
<text x="${W/2}" y="${H - 48}" text-anchor="middle" style="font-size:27px;font-style:italic;fill:#5a4d3a">Drawn to the author’s specification: not from the sources and not a ruling. Base map: Natural Earth; borders as of today.</text>
</svg></body></html>`;
const htmlFile = path.join(TMP, 'v2_atlas.html');
fs.writeFileSync(htmlFile, html);
(async () => {
  const {chromium} = require(path.join(ROOT, 'node_modules/playwright'));
  const b = await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
  const p = await b.newPage({viewport:{width:W, height:H}});
  await p.goto('file://' + htmlFile, {timeout:600000}); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(3000);
  await p.screenshot({path:path.join(OUT, 'v2_atlas.png'), timeout:600000});
  await b.close();
  execFileSync('python3', ['-I', '-c', `from PIL import Image; Image.open('${path.join(OUT, 'v2_atlas.png')}').convert('RGB').save('${path.join(OUT, 'v2_atlas.jpg')}', quality=82, optimize=True)`]);
  console.log('posters/v2_atlas.png and .jpg', W + 'x' + H, '| lat', LATBOT.toFixed(1), 'to', LATTOP);
})();
