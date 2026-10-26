import json, math, sys
from shapely.geometry import Polygon, MultiPolygon
S = '/tmp/claude-0/-home-user-Project-Caliphate/e227bf79-e0c6-5974-a79a-4f0672b36775/scratchpad/logo'
G = '#C9A24A'; G2 = '#E6C66E'; GD = '#8E6B22'; GR = '#0B3B2B'; CR = '#7A1420'; W = '#F7F3EA'; CREAM = '#F4ECD8'; INK = '#2A1D0E'
C = json.load(open('/home/user/Project_Caliphate/atlas-of-the-blessed-lands/src/caliph.json'))
V = MultiPolygon([Polygon(r[0], r[1:]) for r in C['sah']['polys']]).buffer(0).simplify(0.35)
ps = [p for p in V.geoms if p.area > 2.5]; minx, miny, maxx, maxy = V.bounds
def mp(cx, cy, w):
    s = w / (maxx - minx); h = (maxy - miny) * s
    return ''.join('M' + ' L'.join(f'{cx-w/2+(x-minx)*s:.1f},{cy-h/2+(maxy-y)*s:.1f}' for x, y in p.exterior.coords) + ' Z ' for p in ps)
def s8(cx, cy, R, r): return 'M' + ' L'.join(f'{cx+(R if k%2==0 else r)*math.cos(-math.pi/2+k*math.pi/8):.1f},{cy+(R if k%2==0 else r)*math.sin(-math.pi/2+k*math.pi/8):.1f}' for k in range(16)) + ' Z'
def rays(cx, cy, r1, r2, n=40, w=0.04): return ''.join(f'M{cx+r1*math.cos(k*2*math.pi/n-w):.1f},{cy+r1*math.sin(k*2*math.pi/n-w):.1f} L{cx+r2*math.cos(k*2*math.pi/n):.1f},{cy+r2*math.sin(k*2*math.pi/n):.1f} L{cx+r1*math.cos(k*2*math.pi/n+w):.1f},{cy+r1*math.sin(k*2*math.pi/n+w):.1f} Z ' for k in range(n))
def P(pts): return 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z '
def mirror(pts, cx=200): return [(2*cx - x, y) for x, y in pts]

def wing(side, sx, sy, span, lift, n=7, flen=95):
    """feathers fanning from a shoulder; side=-1 left, +1 right"""
    d = ''
    for k in range(n):
        t = k / (n - 1)
        ang = math.radians(-55 + 80 * t)          # from up-and-out to down-and-out
        ax = sx + side * span * (0.25 + 0.75 * t) * 0.55
        ay = sy - lift * (1 - t) * 0.6 + 10 * t
        L = flen * (1.05 - 0.35 * t)
        tipx = ax + side * L * math.cos(ang); tipy = ay + L * math.sin(ang)
        bw = 13
        base1 = (ax, ay - bw); base2 = (ax, ay + bw)
        d += P([base1, (tipx, tipy - 4), (tipx + side * 8, tipy + 6), base2])
    # wing bar (covert)
    d += P([(sx, sy - 18), (sx + side * span * 0.6, sy - lift * 0.55), (sx + side * span * 0.62, sy - lift * 0.35), (sx, sy + 22)])
    return d

def eagle_head(hx, hy, side, s=1.0):
    pts = [(hx - side*14*s, hy + 24*s), (hx - side*16*s, hy - 6*s), (hx - side*4*s, hy - 22*s), (hx + side*16*s, hy - 18*s),
           (hx + side*30*s, hy - 6*s), (hx + side*22*s, hy + 2*s), (hx + side*28*s, hy + 12*s), (hx + side*12*s, hy + 6*s), (hx + side*8*s, hy + 26*s)]
    return P(pts)

def tail(cx, ty):
    d = ''
    for k in range(-3, 4):
        d += P([(cx + k*9 - 6, ty), (cx + k*16 - 7, ty + 52 - abs(k)*5), (cx + k*16 + 7, ty + 52 - abs(k)*5), (cx + k*9 + 6, ty)])
    return d

def shield(cx, cy, w, h):
    x0, x1, y0 = cx - w/2, cx + w/2, cy - h/2
    return f'M{x0:.1f},{y0:.1f} L{x1:.1f},{y0:.1f} L{x1:.1f},{y0+h*0.55:.1f} Q{x1:.1f},{y0+h*0.85:.1f} {cx:.1f},{y0+h:.1f} Q{x0:.1f},{y0+h*0.85:.1f} {x0:.1f},{y0+h*0.55:.1f} Z'

def flag_shield(cx, cy, w, h, cid):
    x0, y0 = cx - w/2, cy - h/2
    return f'''<clipPath id="{cid}"><path d="{shield(cx,cy,w,h)}"/></clipPath>
<g clip-path="url(#{cid})"><rect x="{x0}" y="{y0}" width="{w}" height="{h/3}" fill="{W}"/><rect x="{x0}" y="{y0+h/3}" width="{w}" height="{h/3}" fill="{CR}"/><rect x="{x0}" y="{y0+2*h/3}" width="{w}" height="{h/3+2}" fill="{GR}"/>
<path d="M{x0},{y0} L{x0+w*0.55},{cy} L{x0},{y0+h} Z" fill="{G}"/><path d="{s8(x0+w*0.17,cy,w*0.13,w*0.1)}" fill="{CR}"/></g>
<path d="{shield(cx,cy,w,h)}" fill="none" stroke="{G2}" stroke-width="4"/>'''

def scimitar(x0, y0, x1, y1, curve, side):
    # blade as a curved wedge from hilt (x0,y0) to tip (x1,y1)
    mx, my = (x0+x1)/2, (y0+y1)/2; nx, ny = -(y1-y0), (x1-x0); L = math.hypot(nx, ny); nx, ny = nx/L*curve*side, ny/L*curve*side
    blade = f'M{x0:.1f},{y0:.1f} Q{mx+nx:.1f},{my+ny:.1f} {x1:.1f},{y1:.1f} Q{mx+nx*0.55:.1f},{my+ny*0.55:.1f} {x0+ (ny/curve*side)*0:.1f},{y0+9:.1f} Z'
    ux, uy = (x0-x1), (y0-y1); L2 = math.hypot(ux, uy); ux, uy = ux/L2, uy/L2
    gx, gy = -uy*22, ux*22
    guard = P([(x0+gx, y0+gy), (x0-gx, y0-gy), (x0-gx+ux*6, y0-gy+uy*6), (x0+gx+ux*6, y0+gy+uy*6)])
    grip = P([(x0+ux*6-uy*5, y0+uy*6+ux*5), (x0+ux*40-uy*5, y0+uy*40+ux*5), (x0+ux*40+uy*5, y0+uy*40-ux*5), (x0+ux*6+uy*5, y0+uy*6-ux*5)])
    return blade, guard, grip

out = {}
# ---------- Crest 1: Eagle of Saladin, gold on crimson, flag shield on its chest
body = P([(200, 120), (232, 150), (238, 230), (220, 300), (200, 312), (180, 300), (162, 230), (168, 150)])
out['K1'] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420"><rect width="400" height="420" fill="{CR}"/>
<circle cx="200" cy="205" r="196" fill="none" stroke="{G}" stroke-width="6"/>
<path d="{wing(-1,172,170,175,110,7,72)}{wing(1,228,170,175,110,7,72)}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{tail(200,295)}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{body}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{eagle_head(196,108,1,1.15)}" fill="{G}" stroke="{GD}" stroke-width="2"/><circle cx="208" cy="98" r="3.5" fill="{CR}"/>
<defs></defs>{flag_shield(200,222,76,96,'s1')}
<path d="M120,330 L165,315 L160,340 Z M280,330 L235,315 L240,340 Z" fill="{G}"/>
<path d="M95,355 Q200,392 305,355 L297,392 Q200,422 103,392 Z" fill="{GR}" stroke="{G}" stroke-width="3"/>
<text x="200" y="391" font-family="DejaVu Sans" font-weight="bold" font-size="18" fill="{G2}" text-anchor="middle" letter-spacing="3">DĀR AL-AMĀN</text></svg>'''

# ---------- Crest 2: Seljuk double-headed eagle, gold on green
body2 = P([(200, 135), (236, 160), (240, 235), (222, 300), (200, 312), (178, 300), (160, 235), (164, 160)])
neckL = P([(186, 145), (172, 110), (160, 92), (176, 88), (194, 120), (204, 145)])
neckR = P(mirror([(186, 145), (172, 110), (160, 92), (176, 88), (194, 120), (204, 145)]))
out['K2'] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420"><rect width="400" height="420" fill="{GR}"/>
<path d="{rays(200,200,150,200,48)}" fill="{G}" opacity="0.35"/>
<path d="{wing(-1,172,175,180,115,8,74)}{wing(1,228,175,180,115,8,74)}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{tail(200,298)}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{body2}{neckL}{neckR}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<path d="{eagle_head(166,80,-1,1.0)}{eagle_head(234,80,1,1.0)}" fill="{G}" stroke="{GD}" stroke-width="2"/>
<circle cx="157" cy="72" r="3" fill="{CR}"/><circle cx="243" cy="72" r="3" fill="{CR}"/>
<path d="{s8(200,40,24,18)}" fill="{CR}" stroke="{G}" stroke-width="3"/>
{flag_shield(200,228,78,98,'s2')}
<path d="M95,355 Q200,392 305,355 L297,392 Q200,422 103,392 Z" fill="{CR}" stroke="{G}" stroke-width="3"/>
<text x="200" y="391" font-family="DejaVu Sans" font-weight="bold" font-size="15" fill="{G2}" text-anchor="middle" letter-spacing="2">AL-KHILĀFA AL-AMĪNA</text></svg>'''

# ---------- Crest 3: Crossed scimitars behind the flag shield, radiant star crown
b1, g1, h1 = scimitar(150, 300, 330, 70, 40, 1)
b2, g2, h2 = scimitar(250, 300, 70, 70, 40, -1)
out['K3'] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420"><rect width="400" height="420" fill="{INK}"/>
<path d="{rays(200,190,130,200,56,0.03)}" fill="{G}" opacity="0.55"/>
<path d="{b1}{b2}" fill="#DCD6C8" stroke="{G}" stroke-width="2"/>
<path d="{g1}{g2}{h1}{h2}" fill="{G}" stroke="{GD}" stroke-width="1.5"/>
{flag_shield(200,200,130,160,'s3')}
<path d="{rays(200,88,30,58,24)}" fill="{G}"/><path d="{s8(200,88,32,25)}" fill="{CR}" stroke="{G}" stroke-width="4"/>
<path d="M85,345 Q200,385 315,345 L307,385 Q200,418 93,385 Z" fill="{CR}" stroke="{G}" stroke-width="3"/>
<text x="200" y="383" font-family="DejaVu Sans" font-weight="bold" font-size="18" fill="{G2}" text-anchor="middle" letter-spacing="3">DĀR AL-AMĀN</text></svg>'''

# ---------- Emblem 4: War seal: star of empire with the outline, double ring of rays, crimson
out['K4'] = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 420"><rect width="400" height="420" fill="{CR}"/>
<path d="{rays(200,205,150,200,64,0.035)}" fill="{G}"/>
<circle cx="200" cy="205" r="150" fill="{GR}" stroke="{G}" stroke-width="8"/>
<circle cx="200" cy="205" r="134" fill="none" stroke="{G}" stroke-width="2" stroke-dasharray="4 6"/>
<path d="{s8(200,205,125,96)}" fill="{G}"/><path d="{s8(200,205,108,84)}" fill="{CR}"/>
<path d="{mp(200,205,150)}" fill="{G2}"/></svg>'''

for k, v in out.items(): open(f'{S}/{k}.svg', 'w').write(v)
cap = {'K1': 'Crest A: Eagle of Saladin with the flag shield', 'K2': 'Crest B: Seljuk double-headed eagle', 'K3': 'Crest C: Crossed scimitars and radiant star', 'K4': 'Emblem D: War seal of the empire'}
html = '<html><body style="margin:0;background:#ddd;padding:16px"><div style="display:grid;grid-template-columns:repeat(2,420px);gap:18px">' + ''.join(f'<div><img src="{k}.svg" width="420" height="441"><div style="font:bold 15px sans-serif">{cap[k]}</div></div>' for k in out) + '</div></body></html>'
open(f'{S}/crests.html', 'w').write(html)
