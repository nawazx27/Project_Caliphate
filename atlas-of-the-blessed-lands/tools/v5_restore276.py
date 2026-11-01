"""Version 276: put the saved V5 shape (tools/data/v5_shape_v276.json, V5 as in Versions 272/275) back into CALIPH.sas.
The page does not show sas since Version 276 (build.js HIDDEN_OUTLINES); to show it again, also undo the Version 276 page edits.
Run only if Nawaz asks."""
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
S = json.load(open(os.path.join(P, 'tools/data/v5_shape_v276.json')))
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
C['sas'] = S['sas']
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V5 (sas) restored,', C['sas']['km2'], 'km2')
