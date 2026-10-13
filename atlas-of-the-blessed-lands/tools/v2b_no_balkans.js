/* Version 108 (2026-10-13, Nawaz: "Make a v2 version without our Balkan Peninsula"; he chose the name V2-B and to keep Greece and
   Türkiye). V2-B (CALIPH.xb) is V2 exactly as it was in Version 106, before the Balkan Peninsula went in (Version 107): Greece,
   all of Türkiye and every other land of V2 as then, with the towns of Version 106 kept whole.
   Run: git show ddaa22a:atlas-of-the-blessed-lands/src/caliph.json > /tmp/caliph_v106.json && node tools/v2b_no_balkans.js /tmp/caliph_v106.json */
const fs = require('fs'), path = require('path');
const F = path.join(__dirname, '..', 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
const OLD = JSON.parse(fs.readFileSync(process.argv[2]));
C.xb = JSON.parse(JSON.stringify(OLD.x));
fs.writeFileSync(F, JSON.stringify(C));
console.log('V2-B', C.xb.km2, 'km2,', C.xb.states.length, 'rows; V2', C.x.km2);
