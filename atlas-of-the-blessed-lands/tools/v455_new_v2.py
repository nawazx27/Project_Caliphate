"""Version 455 (Nawaz: "Push this as new v2", on the preview built in Versions 452-454 on top of V1: the whole Nile and its basin, Ethiopia, Somalia,
Somaliland, Kenya, Uganda, Rwanda, Burundi, Tanzania and all of Libya). The preview's outline becomes a NEW V2 (key CALIPH.arb, reused: the old arb, V1 +
Arabia, was hidden in Version 426); V1 is unchanged; the old V2-V6 (me2, me9, grm, tib, sup) become V3-V7. Page text renumbered (every V2-V6 outside
comments in src/body.html and src/eng_e.js moved up one; XNAME/XNUM/OUTLINE_TOK set by hand). Usage: python3 tools/v455_new_v2.py <preview caliph.json>."""
import json, re, os, sys
HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
P = json.load(open(sys.argv[1]))['shj']
F = os.path.join(HERE, 'src/caliph.json'); C = json.load(open(F))
C['arb'] = {'polys': P['polys'], 'km2': P['km2'], 'states': P['states']}
json.dump(C, open(F + '.tmp', 'w'), separators=(',', ':'), ensure_ascii=False); os.replace(F + '.tmp', F)
rx = re.compile(r'V([2-6])(?![_0-9A-Za-z])')
bump = lambda m: 'V' + str(int(m.group(1)) + 1)
def outside_comments(s):
    parts = re.split(r'(/\*.*?\*/|<!--.*?-->)', s, flags=re.S)
    return ''.join(p if (p.startswith('/*') or p.startswith('<!--')) else rx.sub(bump, p) for p in parts)
# ---- body.html
bp = os.path.join(HERE, 'src/body.html'); b = open(bp).read()
b = outside_comments(b)
TITLE = ('V2: V1 with the whole Nile and its basin to Lake Victoria and the Kagera sources, the Horn of Africa and East Africa (Ethiopia, Somalia, '
         'Somaliland, Uganda, Rwanda, Burundi, Kenya and Tanzania, whole) and all of Libya (the author’s specification)')
btn = '<button type="button" data-xv="arb" aria-pressed="false" class="v2btn" title="' + TITLE + '"><span class="lgt">V2</span><span class="sht">V2</span></button>'
b, n = re.subn(r'(<button type="button" data-xv="shj"[^>]*>.*?</button>)', lambda m: m.group(1) + btn, b)
print('buttons inserted', n)
a = '<b>V3</b>, the heartland'; assert b.count(a) == 1
b = b.replace(a, '<b>V2</b> is V1 with the whole Nile and its basin to Lake Victoria and the Kagera sources, and with all of Libya, Ethiopia, Somalia, '
              'Somaliland, Kenya, Uganda, Rwanda, Burundi and Tanzania (about 15.0 million km²). ' + a)
open(bp, 'w').write(b)
# ---- eng_e.js
ep = os.path.join(HERE, 'src/eng_e.js'); e = open(ep).read()
out = []
for L in e.split('\n'):
    if L.startswith('const XNAME') or L.startswith('const XNUM') or 'const OUTLINE_TOK' in L: out.append(L)
    else: out.append(outside_comments(L))
e = '\n'.join(out)
MAP = "sup:'V7', tib:'V6', grm:'V5', shj:'V1', arb:'V2', me8:'V3', me2:'V3', ca:'V4', me9:'V4', sas:'V5', rom:'V6', v2:'V6', eu:'V6', sah:'V4', af:'V4', me:'V3', full:'V3', v3:'V6'"
e = re.sub(r"(const XNAME = \{)[^}]*\}", lambda m: m.group(1) + MAP + '}', e, count=1)
e = re.sub(r"(const XNUM = \{)[^}]*\}", lambda m: m.group(1) + MAP + '}', e, count=1)
a = "'outline-v2':'me2', 'outline-v3':'me9', 'outline-v4':'grm', 'outline-v5':'tib', 'outline-v6':'sup', 'outline-v7':'sup'"; assert e.count(a) == 1
e = e.replace(a, "'outline-v2':'arb', 'outline-v3':'me2', 'outline-v4':'me9', 'outline-v5':'grm', 'outline-v6':'tib', 'outline-v7':'sup'")
i = e.index('CX_LEAD.arb = `'); j = e.index('`;', i) + 2
e = e[:i] + ("CX_LEAD.arb = `<p>${CX_SPEC} <b>V2</b> is V1 with <b>the whole Nile</b> and its basin, from the Delta to Lake Victoria and the Kagera sources "
             "in Rwanda and Burundi (the basin traced from the Wikimedia map the author supplied, a few tens of kilometres approximate), with <b>East Africa and "
             "the Horn</b>: Ethiopia, Somalia, Somaliland, Kenya, Uganda, Rwanda, Burundi and Tanzania, each whole, and with <b>all of Libya</b>, Tripolitania "
             "and the Fezzan. The outlines are the author’s specification, not a ruling. About ${(CALIPH.arb.km2/1e6).toFixed(1)} million km².</p>`;") + e[j:]
a = "const WIDEV = v => v === 'shj' ||"; assert e.count(a) == 1; e = e.replace(a, "const WIDEV = v => v === 'shj' || v === 'arb' ||")
a = "XV === 'shj' ? SHJ_B :"; assert e.count(a) == 1; e = e.replace(a, "XV === 'shj' ? SHJ_B : XV === 'arb' ? ARB_B :")
a = "const SHJ_B ="; assert e.count(a) == 1
e = e.replace(a, "const ARB_B = [[8.5,-12.5],[64.5,43.0]];   /* Version 455: V2 (arb), Libya to Iran, the Black Sea to southern Tanzania */\n" + a)
open(ep, 'w').write(e)
print('done')
