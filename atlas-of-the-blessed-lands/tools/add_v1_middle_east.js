/* Version 66 (2026-10-11, Nawaz's request: "Add a new Caliphate toggle for this land", with a Middle East reference map).
   The new V1, the smallest outline: the sixteen states the map shades, whole: Türkiye, Syria, Lebanon, Israel, Palestine, Jordan,
   Iraq, Iran, Egypt (with the Halaʾib triangle, as the map shades it), Saudi Arabia, Kuwait, Bahrain, Qatar, the UAE, Oman and Yemen
   (with Socotra). Cyprus and Bir Tawil are left out, as on the map. The shapes are the base map's own countries (geo2.json).
   Run once: node tools/add_v1_middle_east.js */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const topojson = require(path.join(ROOT, 'node_modules/topojson-client'));
const pc = require(path.join(ROOT, 'node_modules/polygon-clipping'));
const d3 = require(path.join(ROOT, 'node_modules/d3'));
const geo = JSON.parse(fs.readFileSync(path.join(ROOT, 'geo2.json')));
const F = path.join(ROOT, 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const IDS = ['792','760','422','376','275','400','368','364','818','682','414','048','634','784','512','887'];
const KM = 6371.0088**2;
const ringSr = r => { const a = d3.geoArea({type:'Polygon', coordinates:[r]}); return Math.min(a, 4*Math.PI - a); };
const area = mp => Math.round(mp.reduce((t, poly) => t + ringSr(poly[0]) - poly.slice(1).reduce((h, r) => h + ringSr(r), 0), 0) * KM);
const R3 = v => Math.round(v*1000)/1000;
const R3mp = mp => mp.map(p => p.map(r => r.map(q => [R3(q[0]), R3(q[1])])));
const asMp = g => g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
const geoms = IDS.map(id => { const g = geo.objects.countries.geometries.find(g => String(g.id) === id); if(!g) throw new Error('no country ' + id); return R3mp(asMp(topojson.feature(geo, g).geometry)); });
let X = R3mp(pc.union(...geoms));
X = X.filter(p => ringSr(p[0])*KM >= 1).map(p => [p[0], ...p.slice(1).filter(r => ringSr(r)*KM >= 50)]);   /* drop slivers left where neighbours' borders do not quite meet */
/* the table rows are the same as in the other versions (V4 lists every one of these states whole) */
const states = IDS.map(id => { const s = C.x3.states.find(s => s.id === id); if(!s) throw new Error('no row ' + id); return {...s}; }).sort((a, b) => b.km2 - a.km2);
C.me = {polys: X, km2: area(X), states, ref:'Version 66: the sixteen states of the Middle East reference map Nawaz supplied, whole'};
fs.writeFileSync(F, JSON.stringify(C));
console.log('V1 Middle East', C.me.km2, 'km² (sum of rows', states.reduce((t, s) => t + s.km2, 0), ') pieces', X.length, 'holes', X.reduce((t, p) => t + p.length - 1, 0));
