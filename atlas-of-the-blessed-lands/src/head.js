(function(){
"use strict";
const RELIEF = "__RELIEF__", RELIEF2 = "__RELIEF2__";
/* the outline and base-map data come packed (see build.js): each list of points is a text starting with \u0001 or \u0002; turn it back into pairs */
const unpackRings = o => {
  if(typeof o === 'string'){ const kind = o.charCodeAt(0); if(kind !== 1 && kind !== 2) return o;
    const r = []; let i = 1, x = 0, y = 0; const num = () => { let v = 0, sh = 0, c; do { c = o.charCodeAt(i++) - 63; v |= (c & 0x1f) << sh; sh += 5; } while(c >= 0x20); return v & 1 ? ~(v >> 1) : v >> 1; };
    /* 1: outline points in 0.001° steps from the point before; 2: a base-map arc, its whole numbers as they are */
    while(i < o.length){ if(kind === 1){ x += num(); y += num(); r.push([x/1000, y/1000]); } else r.push([num(), num()]); } return r; }
  if(Array.isArray(o)) return o.map(unpackRings);
  if(o && typeof o === 'object'){ for(const k in o) o[k] = unpackRings(o[k]); return o; }
  return o;
};
const geo = unpackRings(JSON.parse(document.getElementById('geo').textContent));
const geoLo = unpackRings(JSON.parse(document.getElementById('geolo').textContent));   /* a simple land outline for coast decorations */
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
