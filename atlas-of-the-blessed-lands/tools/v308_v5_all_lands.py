"""Version 308 (Nawaz: "Push"). V5 (grm) holds every land Rome or the Ottomans held (whole regions), with the Caucasus drawn as on his
Roman map (border on the mountain crest). Runs tools/v308_build/add_regions.py, then tools/v308_build/caucasus.py.
Usage: python3 tools/v308_v5_all_lands.py <caliph.json of Version 305, from: git show a79f13e~1:./src/caliph.json>"""
import os, sys, subprocess
P = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
B = os.path.join(P, 'tools/v308_build')
subprocess.check_call([sys.executable, os.path.join(B, 'add_regions.py'), P, os.path.join(P, 'tools/data/v308_roman_ottoman_regions.parquet')], env=dict(os.environ, DIP=os.path.join(B, 'dip308.json')))
subprocess.check_call([sys.executable, os.path.join(B, 'caucasus.py'), P, sys.argv[1]])
