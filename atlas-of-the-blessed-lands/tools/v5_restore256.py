"""Restores V5 (CALIPH.sah) exactly as it was in Version 256 (North Caucasus to his line, Kuban settlements, Derbent, Dagestan,
Chechnya) from tools/data/v5_shape_v256.json. Only when Nawaz asks for that shape back."""
import json, os
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
F_ = os.path.join(P, 'src/caliph.json'); C = json.load(open(F_))
C['sah'] = json.load(open(os.path.join(P, 'tools/data/v5_shape_v256.json')))['sah']
json.dump(C, open(F_ + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F_ + '.tmp', F_)
print('V5 restored to Version 256,', C['sah']['km2'], 'km2')
