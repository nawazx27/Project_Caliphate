(function(){
"use strict";
const RELIEF = "__RELIEF__";
const geo = JSON.parse(document.getElementById('geo').textContent);
const geoLo = JSON.parse(document.getElementById('geolo').textContent);   /* a simple land outline for coast decorations */
const q = s => `<span class="q" lang="ar" dir="rtl">${s}</span>`;
/* Layers/Notes as sheets on phones and tablets (up to 980 px) and on any phone held sideways */
if(!document.documentElement.lang) document.documentElement.lang = 'en';
const mobileQ = window.matchMedia('(max-width:980px), (orientation:landscape) and (max-height:520px)');
const shortQ = window.matchMedia('(orientation:landscape) and (max-height:520px)');
let fullOn = false;   /* full-screen map (see eng_e) */

const SRC = {
  rev:{label:"Revelation", tip:"Qur'an or authentic Sunnah", color:"var(--ink)"},
  early:{label:"Companions & early sources", tip:"Companions, Tābiʿūn and early reports", color:"var(--sham)"},
  classical:{label:"Classical scholars & geographers", tip:"Later jurists, lexicographers, geographers and historians", color:"var(--hijaz)"},
  modern:{label:"Modern", tip:"Present-day states and identifications", color:"var(--muted)"}
};
const CERT = {
  firm:{label:"Well established", dash:null, w:2},
  approx:{label:"Approximate", dash:"8 5", w:2},
  uncertain:{label:"Disputed or uncertain", dash:".5 5.5", w:2.6}
};
