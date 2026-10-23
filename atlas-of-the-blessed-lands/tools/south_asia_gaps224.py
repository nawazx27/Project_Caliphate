"""Version 224: the no-gaps rule for V10, the South Asia caliphate (key 'sa'), after tools/south_asia224.py sa and tools/fill_gaps.py sa:
runs tools/silhouette_gaps204.py for 'sa' only (pockets fill=True or with at least 80% of their edge on the outline; never Indian land,
which is inside anyway). Run: python3 tools/south_asia_gaps224.py"""
import os
P = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(P, 'silhouette_gaps204.py')).read()
assert src.count("for k in ['x3', 'v2']:") == 1
exec(compile(src.replace("for k in ['x3', 'v2']:", "for k in ['sa']:").replace("os.path.dirname(os.path.abspath(__file__))", repr(P)), 'silhouette_gaps204', 'exec'))
