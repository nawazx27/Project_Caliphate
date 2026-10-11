/* Version 65: names for the countries the old label list (COUNTRY_LBL in src/eng_a.js) did not have, now that the map covers the
   whole Earth. Positions and the zoom each name appears at come from Natural Earth (LABEL_X, LABEL_Y, MIN_LABEL).
   Prints the WORLD_LBL line for src/eng_a.js: node tools/make_world_labels.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const src = fs.readFileSync(path.join(ROOT, 'src/eng_a.js'), 'utf8');
const CL = eval(src.match(/const COUNTRY_LBL = (\[[\s\S]*?\n\]);/)[1]);
const fc = JSON.parse(fs.readFileSync(path.join(ROOT, 'ne_10m_admin_0_countries.geojson'), 'utf8'));
const SKIP = new Set(['Iran', 'Sudan', 'Democratic Republic of the Congo', 'Bir Tawil', 'Siachen Glacier', 'Baikonur', 'Mozambique', 'Gibraltar', 'Antarctica', 'Indian Ocean Territories', 'Ashmore and Cartier Islands', 'Coral Sea Islands', 'Clipperton Island', 'Brazilian Island', 'Southern Patagonian Ice Field', 'Bajo Nuevo Bank', 'Serranilla Bank', 'Scarborough Reef', 'Spratly Islands', 'Cyprus No Mans Area', 'US Naval Base Guantanamo Bay', 'Akrotiri', 'Dhekelia', 'Guantanamo Bay Naval Base', 'Scarborough Shoal', 'United States Minor Outlying Islands', 'Wake Island', 'Australian Indian Ocean Territories']);
const NAME = {"People's Republic of China":'China', 'United States of America':'United States', 'Czech Republic':'Czechia', 'Bosnia and Herzegovina':'Bosnia & Herz.', 'British Indian Ocean Territory':'Chagos Is.', 'Federated States of Micronesia':'Micronesia', 'Central African Republic':'Central African Rep.', 'French Southern and Antarctic Lands':'Kerguelen', 'Heard Island and McDonald Islands':'Heard I.', 'South Georgia and the South Sandwich Islands':'South Georgia', 'Saint Helena':'St Helena'};
const minK = m => m < 2 ? 0 : m < 3 ? 0.12 : m < 4 ? 0.25 : m < 5 ? 0.5 : m < 6 ? 1 : 2;
const out = [];
fc.features.forEach(f=>{ const p = f.properties, n = p.NAME_EN || p.NAME, x = p.LABEL_X, y = p.LABEL_Y;
  if(SKIP.has(n) || y < -80 || CL.some(c=>c[0] === n || Math.hypot(c[1]-x, c[2]-y) < 2.5)) return;
  out.push([NAME[n] || n, +x.toFixed(2), +y.toFixed(2), minK(p.MIN_LABEL)]); });
out.sort((a, b)=>a[3]-b[3] || a[0].localeCompare(b[0]));
console.log('const WORLD_LBL = ' + JSON.stringify(out) + ';');
