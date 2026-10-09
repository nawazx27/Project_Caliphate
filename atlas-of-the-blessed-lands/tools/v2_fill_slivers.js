/* Version 44: fill the hairline gaps left where the old V2 edge met the added African countries (all under 5,000 km²). Run after add_v2_africa.js. */
const fs=require('fs'),path=require('path'),d3=require(path.join(__dirname,'../node_modules/d3'));
const F=path.join(__dirname,'../src/caliph.json'),C=JSON.parse(fs.readFileSync(F));
const sr=r=>{const a=d3.geoArea({type:'Polygon',coordinates:[r]});return Math.min(a,4*Math.PI-a)*6371.0088**2};
let n=0,km=0;
C.v2.polys=C.v2.polys.map(p=>[p[0],...p.slice(1).filter(r=>{const a=sr(r);if(a<5000){n++;km+=a;return false}return true})]);
C.v2.km2+=Math.round(km);C.v2.slivers='filled '+n;
fs.writeFileSync(F,JSON.stringify(C));console.log('filled',n,'gaps,',Math.round(km),'km²');
