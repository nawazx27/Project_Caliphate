// Builds tools/data_mod.js: the atlas's region shapes and notes as a Node module, read by caliph_gen.js.
// Run from the project folder:  node tools/make_data_mod.js
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..'); process.chdir(root);
const R = f => fs.readFileSync(f, 'utf8');
const gen = JSON.stringify(JSON.parse(R('src/generated.json')));
const js = `const q=s=>s; const SRC={rev:1,early:1,classical:1,modern:1}; const CERT={firm:1,approx:1,uncertain:1};\n` + R('src/old_data.js') + '\n' + R('src/new_geom.js').replace('__GENERATED__', gen).replace('__CALIPH__', fs.existsSync('src/caliph.json') ? R('src/caliph.json') : '{}') + '\n' + R('src/new_info.js') + `
Object.assign(INFO, INFO_NEW); const ALL_LIMITS = LIMITS.concat(LIMITS_NEW);
module.exports={INFO,ALL_LIMITS,STATUS,MIQATS,SITES,ESCHAT,SHAM_OUTER,SHAM_CORE,FIL_OUTER,HIJAZ_OUTER,HIJAZ_CORE,TIHAMAH,YEMEN,MISR_CORE,DELTA};`;
fs.writeFileSync(path.join(__dirname, 'data_mod.js'), js);
console.log('wrote tools/data_mod.js');
