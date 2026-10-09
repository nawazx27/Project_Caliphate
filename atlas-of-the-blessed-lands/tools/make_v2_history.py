"""Merge the province-by-province research for Complete Caliphate V2 (scratch research files) into v2_history.json.
Each unit gets `cat`, one of: direct, dynasty, tributary, islamic, temporary, influence.
Claude's own adjustments to the researchers' calls are listed in ADJ and recorded on the unit as `adj`."""
import json, sys, os
src = sys.argv[1] if len(sys.argv) > 1 else '.'
ADJ = {
 ('MAR','Atlantic plains'): ('direct', 'Raised from "via a dynasty": the Almohads, a counted caliphate, ruled it directly 1147–1269.'),
 ('MAR','Sous and the Draa'): ('direct', 'Raised from "via a dynasty": the Almohads, a counted caliphate, ruled it directly 1147–1269.'),
 ('DZA','Central Tell'): ('direct', 'Raised from "via a dynasty": the Almohads ruled it directly, and it was the seat of the Ottoman Regency of Algiers (Ottomans counted from 1517).'),
 ('DZA','Western Tell'): ('direct', 'Raised from "via a dynasty": Umayyad governors 708–740, then the Almohads directly and the Ottoman Regency.'),
 ('DZA','Greater Kabylia'): ('tributary', 'Lowered from "ruled": the Kingdom of Kuku paid tribute to Algiers, and Ottoman forts held only the valleys; the mountains kept their own rule.'),
 ('DZA','Ouargla'): ('tributary', 'Lowered from "ruled": Touggourt and Ouargla paid tribute to Ottoman Algiers; the earlier Hammadid governor is undated.'),
 ('DZA','The Mzab'): ('tributary', 'Changed from "other Islamic state": the Ibadi towns ruled themselves but recognised and paid Ottoman Algiers, so they were tributary to a caliphate.'),
}
MAP = {'direct':'direct','via_dynasty':'dynasty','tributary':'tributary'}
FALL = {'islamic_state_ruled':'islamic','temporary':'temporary','influence':'influence','tributary':'tributary','caliphate_ruled':'dynasty'}
out = []
for f in ['maghrib.json','centralasia.json','afpak.json']:
    for c in json.load(open(os.path.join(src, f), encoding='utf-8')):
        units = []
        for u in c['units']:
            st = u['caliphate'].get('status','none')
            cat = MAP.get(st) or FALL[u['category']]
            if st in ('temporary','raided') and u['category'] == 'temporary': cat = 'temporary'
            adj = ''
            for (a3, key), (newcat, why) in ADJ.items():
                if a3 == c['a3'] and u['label'].startswith(key): cat, adj = newcat, why
            units.append({'label':u['label'], 'provinces':u['provinces'], 'cat':cat, 'conf':u['confidence'],
                          'who':u['caliphate'].get('who',''), 'dates':u['caliphate'].get('dates',''), 'nominal':bool(u['caliphate'].get('nominal')),
                          'states':[{'n':s.get('name',''), 'd':s.get('dates',''), 'r':s.get('recognised_caliph','')} for s in u.get('islamic_states',[])],
                          'notes':u.get('notes',''), 'uncertain':u.get('uncertain',''), 'adj':adj,
                          'sources':[{'t':s.get('title',''), 'u':s.get('url',''), 'k':s.get('kind','modern'), 's':s.get('supports','')} for s in u.get('sources',[])]})
        out.append({'a3':c['a3'], 'country':c['country'], 'summary':c['summary'], 'units':units})
used = {k for k in ADJ}; hit = {(c['a3'], k) for c in out for u in c['units'] for (a,k) in ADJ if a == c['a3'] and u['label'].startswith(k)}
missing = used - hit
if missing: raise SystemExit('adjustment not applied: %r' % missing)
json.dump(out, open('v2_history.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
from collections import Counter
print('units', sum(len(c['units']) for c in out), Counter(u['cat'] for c in out for u in c['units']))
