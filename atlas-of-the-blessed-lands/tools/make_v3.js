/* Version 55 (2026-10-10, Nawaz's request: "make the current complete caliphate a v3 and remove the max caliphate and for the complete
   caliphate v1 bring back the version where the borders ended near libya"; he chose the Complete of Version 47, just before Tunisia, and to
   keep the other versions as they are, built on V3).
   - CALIPH.x3 (new, "Complete V3") = the Complete outline as it was in Version 54.
   - CALIPH.x ("Complete", V1) = the Complete outline of Version 47 (git commit b477512): Libya's western border is its edge in the west.
   - CALIPH.m (Maximum) is removed; tools/make_max.js is retired.
   To Iraq (xw), V2, Greater (g) and the natural versions are unchanged; their notes now say they are built on Complete V3.
   Needs the Version 47 caliph.json: V47=<path> node tools/make_v3.js   (git show b477512:atlas-of-the-blessed-lands/src/caliph.json > <path>) */
const fs = require('fs'), path = require('path');
const F = path.join(__dirname, '..', 'src/caliph.json'), C = JSON.parse(fs.readFileSync(F));
if(C.x3){ console.log('already done'); process.exit(0); }
const V47 = JSON.parse(fs.readFileSync(process.env.V47));
C.x3 = C.x; C.x = V47.x; delete C.m;
C.v3 = 'Version 55: Complete V3 = the Complete of Version 54; Complete (V1) = the Complete of Version 47; Maximum removed';
fs.writeFileSync(F, JSON.stringify(C));
console.log('V1', C.x.km2, C.x.states.length, '| V3', C.x3.km2, C.x3.states.length, '| keys', Object.keys(C).join(','));
