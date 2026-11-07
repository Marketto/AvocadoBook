"""Toy clamshell laptop for Anycubic Kobra X (bed 260x260x260) - v7 (snap-together; base 13.4, lid 7 mm; paper screen behind a press-fit bezel; v8: peg clearance; v9: lid 5 mm; v10: avocado logo; v11: tolerances from test prints; v12: bezel = slice of the lid, chamfered edges; v13: corner hooks; v14: edge hooks barb outwards; v15: stiffer bezel, more pegs; v16: fully printed key springs + click; v17: thinner base 10 mm; v18: real hook ledge, intermediate hooks, 45deg double-leaf click, 3 spring types; v18c: printable frame grooves, stiffer mat; v19: self-tightening ramp hooks, soft spring, keys face down; v20: tapered stronger springs, higher keys, more pins; v21: free tongue + keycap stem, filleted root).

- clicky keys with letters (captive printed keycaps on 6x6x5 mm tactile switches)
- clicky trackpad (2 tactile switches)
- hinge: axle bars printed with the lid, slid into open cradles of the base, locked by keys of the top case
- no hard stop: lid opens to ~180 deg (tablet); detent clicks when closed and at ~105 deg (breakaway, kid-safe)
- top case snaps onto the bottom case with hidden hooks

Modelled in CLOSED pose: base on z=0, lid lying on it (screen face down).
Base = bottom case (A) + top case (B, snap hooks). Lid = C. Keycaps = D. Bezel = E. Key spring/click mats = F.
"""
import os, sys, pickle
_HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
if not os.path.exists(os.path.join(_HERE, "tasto_z.py")):      # exec'd from another script: tools pass __file__
    _HERE = os.environ.get("AVB_SRC", os.path.join(os.getcwd(), "src"))
BUILD = os.path.join(os.path.dirname(_HERE), "build")       # generated data (parts pickle), not versioned
import numpy as np, trimesh, manifold3d as mf, matplotlib
from manifold3d import Manifold, CrossSection
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

SEG = 64
RJ = dict(join_type=mf.JoinType.Round, circular_segments=SEG)

# ---------------- main dimensions (mm) ----------------
BED = 260.0
W = BED - 10.0                   # overall width: bed minus 5 mm margin per side
ASPECT = (16, 10)
BZ_SIDE, BZ_TOP, BZ_BOT = 10.0, 10.0, 16.0     # bezels (BOT = hinge side)
SCR_W = W - 2*BZ_SIDE
SCR_H = SCR_W * ASPECT[1] / ASPECT[0]
H     = 10.0                     # base thickness (v17: thinner, printed key mechanism is lower)
SPLIT = 6.8                      # bottom case / top case split height
T     = 5.0                      # lid thickness
RK    = 4.75                     # hinge barrel radius (> T/2: barrel bulges towards the screen side only)
GAP   = 0.6                      # air gap between closed lid and base deck
R_PLAN = 16.0                    # plan corner radius (base AND lid)
R_IN  = 3.0                      # (unused since v12)
CH_IN = 1.5                      # 45 deg chamfer on the edges facing each other when closed (base top, lid screen side)
R_OUT = 2.0                      # outer edges (both on the bed when printing)
LS    = BZ_TOP + SCR_H + BZ_BOT  # lid: front edge -> hinge axis
AY, AZ = LS, H + GAP + T - RK    # hinge axis: barrel flush with the lid outer face
ZD = AZ - RK - GAP               # floor of the deck channel under the barrel
DB    = AY + RK + GAP + 1.0      # base depth (base ends right behind the barrel, like the lid)
KN = [(40.0, 72.0), (W - 72.0, W - 40.0)]   # base cradles (x ranges)
KN_CLR = 0.6
AX_R, AX_HOLE = 3.0, 3.1         # lid axle radius / cradle bore radius (0.1 mm radial play)
NOTCH = 9.0                      # lid notch depth in front of the axis
KEY_Y0, KEY_YB = AY - 6.0, AY - AX_HOLE    # top-case lock key: front / back face
FIT = 0.2                        # clearance between printed mating parts
INLAY, LOGO_D = 0.6, 0.6          # 3 layers of colour each
# paper 'screen': separate black bezel frame pressed onto the lid, 0.5 mm paper gap behind it
FRAME_T, PAPER_GAP, PAPER_OVL = 1.2, 0.5, 3.0   # frame lip (v15: 1.2, stiffer), paper gap, paper overlap under the frame (side channels)
FRAME_X0, FRAME_BOT = 3.5, 8.0                  # frame inset from lid sides, frame extent below the window
PEG_D, PEG_L, PEG_HOLE = 2.4, 2.0, 2.9          # pegs (frame) -> holes (lid): 2.9 = value from the printed calibration (test 1, hole 4)
PEG_RIB = 0.25                                   # 3 crush ribs on each peg give the grip (Ø over ribs = PEG_D + 2*PEG_RIB)
FRAME_CLR = 0.35                                 # frame outline <-> recess (cosmetic gap, pegs do the holding)
FL_W, FL_T = 2.5, 0.6
USB = (8.5, 2.75, 9.0)           # v26i: realistic USB-C opening (real 8.34 x 2.56, plug 8.25 x 2.4): snug fit

# keys / switches  (6x6x5 mm tactile switch: body 6x6, plunger top 5.0 above body bottom)
SW_H = 2.2                       # distance key bottom -> mat (pocket floor); v17
SW_LEGS = []
KEY_TOP = H                      # v20: keycap top; at rest +REST_UP -> 0.3 above the deck, 0.3 below the closed lid
KEY_BOT = SPLIT - 0.3 - 1.0      # keycap bottom = flange bottom (rests on plunger)
SW_Z0 = KEY_BOT - SW_H           # switch body bottom = pocket floor
WELL_TOP = H - 1.6               # keyboard well surface (frame = WELL_TOP - SPLIT); v18: keys protrude 1.5 mm
KEY_CLR = 0.3                    # keycap <-> frame hole
TAB_W, TAB_L = 6.0, 0.7          # retaining/guide tabs (v23: 0.7, row gap = 2.6 like the column gap)
LETTER_D = 0.6                   # letter inlay depth (3 layers)
PITCH_Y = 18.0                        # v23b: row pitch as before; columns use the same pitch -> square keys, no bigger
KEY_GAP_X = 2.6

# detent: leaf springs in the deck under the lid barrel, ridge -> grooves on the barrel
DET_P = 1.2                      # ridge apex above deck (0.6 gap + 0.6 interference on the barrel)
GR = 1.5                         # groove radius (wider/deeper than the ridge -> it seats fully)
RIDGE_R = 0.8
SUP_GAP = 0.1                    # axle support gap: print the support in PLA (does not bond to PETG)
DET_OPEN = 105.0                 # second groove: holds the lid open here
LEAF_L, LEAF_W, LEAF_T = 20.0, 6.0, 1.0
DET_X = [28.0, W/2 - 30, W/2 + 30, W - 28.0]

# snap hooks (bottom case -> top case)
HOOK_W, HOOK_T, HOOK_BARB, HOOK_Z0 = 8.0, 1.4, 0.7, 1.0   # v24: barb 0.7 (was 1.0: too hard to snap)
HOOK_LEDGE = 1.1                 # v18: thickness of the catch ledge in the top case (was ~0 in v6..v17!)
HOOK_RAMP = 25.0                 # v19: catch face inclined 25 deg -> self-tightening, absorbs print tolerance
HOOK_PRELOAD = 0.10              # v19: vertical interference -> the hook pulls the top case down
# alignment pins (bottom case) -> holes in the top case: they take all sideways play
ALIGN = [(52, AY - 11), (W - 52, AY - 11), (12, DB*0.52), (W - 12, DB*0.52), (45, 18), (W - 45, 18),
         (24, 58), (105, 58), (W - 105, 58), (W - 24, 58)]   # v20: pins in the intermediate row too
ALIGN_D, ALIGN_HOLE, ALIGN_H = 4.0, 4.7, H - SPLIT - 1.2   # v22: 4.2 printed too tight (small holes come out ~0.4 mm undersize)
HOOK_TOP = SPLIT + HOOK_LEDGE + 0.1 + 1.0   # barb: flat catch at SPLIT+LEDGE+0.1, 1 mm tall


def puck(R, h, rt, rb, ct=0.0, cb=0.0):
    """Disc of radius R, height h; top/bottom outer edge: round (rt/rb) or 45 deg chamfer (ct/cb)."""
    pts = [(0, 0)]
    if cb > 0:
        pts += [(R - cb, 0), (R, cb)]
    else:
        for a in np.linspace(-np.pi/2, 0, 10):
            pts.append((R - rb + rb*np.cos(a), rb + rb*np.sin(a)))
    if ct > 0:
        pts += [(R, h - ct), (R - ct, h)]
    else:
        for a in np.linspace(0, np.pi/2, 10):
            pts.append((R - rt + rt*np.cos(a), h - rt + rt*np.sin(a)))
    pts.append((0, h))
    return Manifold.revolve(CrossSection([pts]), SEG)


def rounded_slab(w, d, h, R, rt, rb, ct=0.0, cb=0.0):
    return Manifold.batch_hull([puck(R, h, rt, rb, ct, cb).translate((cx, cy, 0))
                                for cx in (R, w - R) for cy in (R, d - R)])


def rrect(w, h, r, x=0, y=0):
    return CrossSection.square((w - 2*r, h - 2*r)).translate((x + r, y + r)).offset(r, **RJ)


def box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0)).translate((x0, y0, z0))


def xcyl(x0, x1, r, y=AY, z=AZ):
    return Manifold.cylinder(x1 - x0, r, r, SEG).rotate((0, 90, 0)).translate((x0, y, z))


def zcyl(x, y, z0, z1, r):
    return Manifold.cylinder(z1 - z0, r, r, 32).translate((x, y, z0))


def union(ms):
    return Manifold.batch_boolean(list(ms), mf.OpType.Add)


def inlay(cs, z0, depth, visible_up=True, ring=True):
    vis = Manifold.extrude(cs, depth).translate((0, 0, z0))
    fcs = cs.offset(FL_W, **RJ)
    if ring:
        fcs = fcs - cs.offset(-5, **RJ)
    fl = Manifold.extrude(fcs, FL_T)
    return vis + fl.translate((0, 0, z0 - FL_T if visible_up else z0 + depth))


def avocado_logo(size, bite=True):
    """Original stylised avocado half: pear silhouette, round pit (hole), small stem, optional bite on +x."""
    c = lambda x, y, r: CrossSection.circle(r, SEG).translate((x, y))
    body = CrossSection.batch_hull([c(0, -3.0, 6.8), c(0, 4.6, 4.7)])
    body = body.offset(0.8, **RJ).offset(-0.8, **RJ)
    stem = CrossSection.square((1.4, 2.4)).translate((-0.7, 0)).offset(0.35, **RJ).rotate(-14).translate((0.3, 8.6))
    shape = body + stem
    if bite:
        shape = shape - c(6.3, 2.6, 2.3) - c(5.2, 5.4, 1.7)
        shape = shape.offset(0.4, **RJ).offset(-0.4, **RJ)
    pit = c(0.2, -3.3, 3.3)
    shape = (shape - pit).rotate(-10)
    b = shape.bounds()
    s = size / (b[3] - b[1])
    return shape.translate((-(b[0]+b[2])/2, -(b[1]+b[3])/2)).scale((s, s))


FONT = FontProperties(fname=os.path.join(matplotlib.get_data_path(), "fonts/ttf/DejaVuSans-Bold.ttf"))


def glyph(text, cx, cy, cap_h=7.0, box_wh=None):
    """2D outline of `text` centred at (cx, cy). Letters use a common cap height; symbols fit box_wh."""
    p = TextPath((0, 0), text, size=10, prop=FONT)
    polys = [np.asarray(q) for q in p.to_polygons(closed_only=True) if len(q) > 2]
    cs = CrossSection([q[:-1] for q in polys], mf.FillRule.EvenOdd)
    b = cs.bounds()
    if box_wh:
        s = min(box_wh[0] / (b[2] - b[0]), box_wh[1] / (b[3] - b[1]))
    else:
        s = cap_h / 7.29          # DejaVu cap height at size 10
    cs = cs.scale((s, s))
    b = cs.bounds()
    return cs.translate((cx - (b[0]+b[2])/2, cy - (b[1]+b[3])/2))


def clean(m):
    return max(m.decompose(), key=lambda p: p.volume())


def rot_lid(m, deg):
    return m.translate((0, -AY, -AZ)).rotate((-deg, 0, 0)).translate((0, AY, AZ))


# ================= BASE SOLID =================
base = rounded_slab(W, DB, H, R_PLAN, 0, R_OUT, ct=CH_IN)

# ---- keyboard layout ----
# v23c: staggered letter rows like a real keyboard (Q -> A: +1/4 key, A -> Z: +1/2 key), 12 units wide
ROWS = [
    [(c, 1) for c in "1234567890"] + [("⌫", 2.0)],
    [("⇥", 1.0)] + [(c, 1) for c in "QWERTYUIOP"] + [("è", 1.0)],
    [("☺", 1.25)] + [(c, 1) for c in "ASDFGHJKL"] + [("↵", 1.75)],
    [("⇧", 1.75)] + [(c, 1) for c in "ZXCVBNM,."] + [("⇧", 1.25)],
    [("♥", 1.25), ("★", 1.25), ("", 7.0), ("◀", 1.25), ("▶", 1.25)],
]
KB_UNITS = 12.0
assert all(abs(sum(u for _, u in r) - KB_UNITS) < 1e-9 for r in ROWS)
KB_X0, KB_X1 = W/2 - KB_UNITS*PITCH_Y/2, W/2 + KB_UNITS*PITCH_Y/2     # 12 units of 18 mm (216 mm), centred
KB_Y1 = AY - RK - 12.0
KB_Y0 = KB_Y1 - PITCH_Y*len(ROWS)
UNIT = (KB_X1 - KB_X0) / KB_UNITS
CAP_Y = PITCH_Y - KEY_GAP_X        # v23: same gap between rows and columns -> 1u keys are square

keys = []      # dicts: label, cap rect (x0,y0,x1,y1)
for r, row in enumerate(ROWS):
    yc = KB_Y1 - PITCH_Y*(r + 0.5)
    x = KB_X0
    for lab, u in row:
        keys.append(dict(lab=lab, x0=x + KEY_GAP_X/2, x1=x + u*UNIT - KEY_GAP_X/2,
                         y0=yc - CAP_Y/2, y1=yc + CAP_Y/2, row=r))
        x += u*UNIT


def key_switches(k):
    w = k["x1"] - k["x0"]
    xc, yc = (k["x0"] + k["x1"])/2, (k["y0"] + k["y1"])/2
    if w > 4*UNIT:
        return [(xc - w*0.3, yc), (xc + w*0.3, yc)]
    return [(xc, yc)]


def key_tabs_x(k):
    w = k["x1"] - k["x0"]
    xc = (k["x0"] + k["x1"])/2
    if w > 4*UNIT:
        return [xc - w*0.35, xc, xc + w*0.35]
    if w > 1.8*UNIT:
        return [xc - w*0.25, xc + w*0.25]
    return [xc]


keycaps, letters, frame_holes, switch_pts = [], [], [], []
for k in keys:
    w, h = k["x1"] - k["x0"], k["y1"] - k["y0"]
    xc, yc = (k["x0"] + k["x1"])/2, (k["y0"] + k["y1"])/2
    cap = Manifold.extrude(rrect(w, h, 1.8, k["x0"], k["y0"]), KEY_TOP - KEY_BOT).translate((0, 0, KEY_BOT))
    tabs = [box(tx - TAB_W/2, tx + TAB_W/2, k["y0"] - TAB_L, k["y1"] + TAB_L, KEY_BOT, KEY_BOT + 1.0)
            for tx in key_tabs_x(k)]
    keycap = union([cap] + tabs)
    if k["lab"]:
        if k["lab"] in ",.":       # punctuation sits low, like on real keycaps (bigger so a child can see it)
            g = glyph(k["lab"], xc, yc - 2.5, cap_h=11.0)
        elif k["lab"].isalnum():
            g = glyph(k["lab"], xc, yc, cap_h=7.0)
        else:
            g = glyph(k["lab"], xc, yc, box_wh=(9.0, 8.0))
        let = Manifold.extrude(g, LETTER_D + 0.01).translate((0, 0, KEY_TOP - LETTER_D))
        keycap = keycap - let
        letters.append(let ^ cap)
    keycaps.append(keycap)
    frame_holes.append(Manifold.extrude(rrect(w + 2*KEY_CLR, h + 2*KEY_CLR, 2.0, k["x0"] - KEY_CLR, k["y0"] - KEY_CLR), 20)
                       .translate((0, 0, SPLIT - 1)))
    switch_pts += key_switches(k)

keycaps_m = union(keycaps)
letters_m = union(letters)

# ---- trackpad ----
TP_W, TP_H = 100.0, 40.0
TP_X0, TP_Y0 = (W - TP_W)/2, 12.0
TP_TOP = H - 0.3                 # v23d: at rest (lifted by REST_UP = 0.3) the trackpad is flush with the deck
tp_cs = rrect(TP_W, TP_H, 5, TP_X0, TP_Y0)
trackpad = (Manifold.extrude(tp_cs, TP_TOP - KEY_BOT).translate((0, 0, KEY_BOT)) +
            Manifold.extrude(tp_cs.offset(1.6, **RJ), 1.0).translate((0, 0, KEY_BOT)))
tp_hole = Manifold.extrude(tp_cs.offset(0.4, **RJ), 20).translate((0, 0, SPLIT - 1))
tp_switches = [(W/2 - 30, TP_Y0 + TP_H/2), (W/2 + 30, TP_Y0 + TP_H/2)]
switch_pts += tp_switches

# ---- deck features ----
# v24: keyboard well with a ROUNDED edge (quarter round, radius = depth) instead of a 90-degree step
_wcs = rrect(KB_X1 - KB_X0 + 4, KB_Y1 - KB_Y0 + 4, 4, KB_X0 - 2, KB_Y0 - 2)
_WR = H - WELL_TOP
_lv = [(WELL_TOP + _WR*np.sin(a), _WR*(1 - np.cos(a))) for a in np.linspace(0, np.pi/2, 9)]
_lv = [(z, _WR - np.sqrt(max(_WR**2 - (z - WELL_TOP)**2, 0))) for z, _ in _lv]
well = Manifold.extrude(_wcs, 10).translate((0, 0, WELL_TOP))
for (za, oa), (zb, ob) in zip(_lv[:-1], _lv[1:]):
    well = well + Manifold.batch_hull([Manifold.extrude(_wcs.offset(oa, **RJ), 0.001).translate((0, 0, za)),
                                       Manifold.extrude(_wcs.offset(ob, **RJ), 0.001).translate((0, 0, zb))])
well = well + Manifold.extrude(_wcs.offset(_WR, **RJ), 5).translate((0, 0, H - 0.001))
scoop = Manifold.sphere(1, SEG).scale((32, 10, 5)).translate((W/2, 0, H + 2.5))

uw, uh, ud = USB
def side_slot(w, h, dep, y, z):
    m = Manifold.extrude(rrect(w, h, h/2 - 0.01), dep).rotate((0, 90, 0)).rotate((90, 0, 0))
    b = m.bounding_box()
    return m.translate((-1 - b[0], y - (b[1]+b[4])/2, z - (b[2]+b[5])/2))
USB_Z = 3.6
usb = side_slot(uw, uh, ud + 1, DB*0.62, USB_Z) + side_slot(uw + 0.8, uh + 0.8, 1.4, DB*0.62, USB_Z)   # v26i: thin 0.4 mm step only

base = base - well - scoop - usb
# v26j: USB-C grip like a real port: two spring fingers in the side walls of the port (0.8 mm PETG plates,
# rooted at the inner end, 0.6 mm slot behind them) with a rounded bump that protrudes 0.3 mm into the port
USB_FINGER = dict(t=0.8, gap=0.6, x0=2.0, x1=7.0, bump_x=3.2, bump_r=0.8, bump_in=0.3)
_yu = DB*0.62
_f = USB_FINGER
_fz0, _fz1 = USB_Z - uh/2 - 0.4, USB_Z + uh/2 + 0.4
for _s in (-1, 1):
    _yw = _s*uw/2
    _ya, _yb = sorted([_yu + _yw - _s*0.01, _yu + _yw + _s*(_f["t"] + _f["gap"])])
    base = base - box(_f["x0"] - _f["gap"], _f["x1"], _ya, _yb, _fz0 - 0.5, _fz1 + 0.5)          # room around the finger
    _ya, _yb = sorted([_yu + _yw, _yu + _yw + _s*_f["t"]])
    base = base + box(_f["x0"], _f["x1"] + 0.01, _ya, _yb, _fz0, _fz1)                          # the finger (rooted at x1)
    _bump = zcyl(_f["bump_x"], _yu + _yw + _s*(_f["bump_r"] - _f["bump_in"]), _fz0, _fz1, _f["bump_r"])
    _ya, _yb = sorted([_yu + _yw - _s*_f["bump_in"], _yu + _yw + _s*_f["t"]])
    base = base + (_bump ^ box(_f["x0"], _f["x1"], _ya, _yb, -99, 99))                         # bump only on the port side

# ---- channel in the deck for the hinge barrel (full width, open at the back) ----
base = base - xcyl(-1, W + 1, RK + GAP) - box(-1, W + 1, AY - 6.0, DB + 1, ZD, 100)

# ---- hinge cradles (open towards the front; the lid axle slides in horizontally) ----
for x0, x1 in KN:
    kk = xcyl(x0, x1, RK) + box(x0, x1, KEY_YB + FIT, AY + RK, ZD - 1, AZ)
    kk = kk - xcyl(x0 - 1, x1 + 1, AX_HOLE) - box(x0 - 1, x1 + 1, AY - 20, AY, AZ - AX_HOLE, AZ + 20)
    base = base + kk

# ---- detent leaf springs (fixed at both ends, bridge over a cavity) ----
ridges = []
for xc in DET_X:
    a0, a1 = xc - LEAF_L/2, xc + LEAF_L/2
    z0 = ZD - LEAF_T - 1.5
    base = base - box(a0, a1, AY - LEAF_W/2, AY + LEAF_W/2, z0, ZD - LEAF_T) \
                - box(a0, a1, AY - LEAF_W/2 - 0.8, AY - LEAF_W/2, z0, ZD + 1) \
                - box(a0, a1, AY + LEAF_W/2, AY + LEAF_W/2 + 0.8, z0, ZD + 1)
    ridges.append(xcyl(xc - 3, xc + 3, RIDGE_R, y=AY, z=ZD + DET_P - RIDGE_R))
ridges_m = union(ridges)

def _yz_prism(pts, x0, x1):
    """(y,z) polygon extruded along x (same as yz_prism below, needed earlier for the hinge keys)."""
    m = Manifold.extrude(CrossSection([pts], mf.FillRule.EvenOdd), x1 - x0)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


# ================= split base -> bottom case + top case =================
top_region = box(-1, W + 1, -1, AY - 6.0, SPLIT, 100)
top_case = (base ^ top_region) - union(frame_holes) - tp_hole
# v26u: gentle S ramp along the BACK edge of the keyboard well (user's sketch), moved forward: it starts 0.8 mm
# behind the top-row key holes and reaches the deck 3.2 mm later (y 157.0), so the 5 rear hook pockets and the 2
# alignment holes underneath (tops at z 9.2 / 9.1, from y 156.4) keep >= 0.7 mm of skin. (v26q ran to y 159.5 and
# opened slits over them.) The ends of the ramp are rounded in plan (r 3) and fade into the corner quarter rounds.
RB0, RB1 = KB_Y1 + KEY_CLR + 0.5, KB_Y1 + KEY_CLR + 0.5 + 3.2
_rz = lambda yy: WELL_TOP + _WR*(0.5 - 0.5*np.cos(np.pi*np.clip((yy - RB0)/(RB1 - RB0), 0, 1)))
_ys = np.linspace(RB0, RB1, 40)
_fill = [(RB0, WELL_TOP - 0.3)] + [(yy, _rz(yy)) for yy in _ys] + [(RB1, WELL_TOP - 0.3)]
_void = [(RB0 - 0.01, _rz(RB0) + 0.0)] + [(yy, _rz(yy)) for yy in _ys] + [(RB1 + 0.3, H), (RB1 + 0.3, H + 5), (RB0 - 0.01, H + 5)]
_plan = Manifold.extrude(rrect(KB_X1 - KB_X0 - 4.0, RB1 - RB0 + 4.0, 2.5, KB_X0 + 2.0, RB0 - 2.0), 30).translate((0, 0, -5))   # straight part of the back edge, rounded ends
top_case = (top_case - (_yz_prism(_void, -1, W + 1) ^ _plan)) + (_yz_prism(_fill, -1, W + 1) ^ _plan ^ box(-1, W + 1, RB0, RB1, WELL_TOP - 0.3, H))
bottom = base - top_region
# lock keys: rise from the top case and close the cradle in front of / above the axle
for x0, x1 in KN:
    key = box(x0, x1, KEY_Y0 - 1, KEY_YB, SPLIT, AZ) + (xcyl(x0, x1, RK) ^ box(x0, x1, AY - RK - 1, AY, AZ, AZ + RK + 1))
    key = key + box(x0, x1, KEY_Y0 - 1, AY - RK + 0.01, AZ - 0.01, AZ + 1.5)
    key = Manifold.batch_hull([key ^ box(x0, x1, -1, AY, AZ - 0.01, 100), box(x0, x1, KEY_Y0 - 1, KEY_YB, AZ - 0.02, AZ)]) + key
    # v26p: CONVEX cover (user: no concave S, no 90-degree joints): rises from the deck with a small concave fillet
    # (r 1.5) into a convex curve, flat top flush with the closed lid, covers the axle up to the base cradle (0.2 gap);
    # the top edges at the two ends are rounded (r 2) and so are the front corners in plan view (r 3).
    # Over the axle it is only ~1.6 mm thick (bore top 14.1, lid line 15.6) -> printed solid (100 % modifier).
    # Bore play 0.15 (> 0.1 of the base cradle: the axle lifts against the base, not against this thin part).
    HOOD_PLAY, Y0W, Y1W, TOPW = 0.15, AY - NOTCH + 0.25, AY - 3.2, H + GAP + T
    # v26q (user's sketch): fuller dome: front almost vertical at Y0W, big round (r 3) into the flat top
    RD = 3.0
    LEAN = 0.6      # front leans back 0.6 mm (the lid notch edge passes close at ~15 degrees)
    # v26r (2nd sketch): the round becomes a long elliptic shoulder: starts ~1.2 mm above the deck and reaches the flat
    # top 4.1 mm further back (semi-axes 4.1 x 4.4)
    EA, EB = 3.5, 4.4     # v26t (3rd sketch): reaches the flat top a bit earlier
    curve = [(Y0W, H)] + [(Y0W + LEAN + EA - EA*np.cos(t), TOPW - EB + EB*np.sin(t)) for t in np.linspace(0, np.pi/2, 48)]
    front = CrossSection([[(Y0W - 1.5, H - 0.6), (Y0W - 1.5, H)] + curve + [(Y1W + 0.6, TOPW), (Y1W + 0.6, AZ), (KEY_YB, AZ), (KEY_YB, H - 0.6)]], mf.FillRule.EvenOdd)  # v26s: nothing behind KEY_YB below the axle centre (it blocked the piano going down over the axle)
    front = front.offset(2.5, mf.JoinType.Round, circular_segments=64).offset(-2.5, mf.JoinType.Round, circular_segments=64)  # v26t: wide concave fillet (r 2): one line from the keyboard ramp into the cover, no flat step
    front = front ^ CrossSection.square((Y1W + 0.6 - Y0W + 1.0, TOPW + 1)).translate((Y0W - 1.0, 0))
    back = CrossSection([[(Y1W, H - 0.6), (Y1W, TOPW), (AY - FIT, TOPW), (AY - FIT, AZ), (KEY_YB, AZ), (KEY_YB, H - 0.6)]], mf.FillRule.EvenOdd)
    cs = front + back
    cover = Manifold.extrude(cs, x1 - x0).transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])
    RE = 1.2        # v26u: end rounding 1.2 (2.0 left < 0.6 mm over the axle at the two end corners)
    ends = CrossSection.square((x1 - x0, TOPW - RE)).translate((x0, 0)) + \
           CrossSection.square((x1 - x0 - 2*RE, RE + 0.01)).translate((x0 + RE, TOPW - RE - 0.01)) + \
           CrossSection.circle(RE, 32).translate((x0 + RE, TOPW - RE)) + CrossSection.circle(RE, 32).translate((x1 - RE, TOPW - RE))
    cover = cover ^ Manifold.extrude(ends, 40).transform([[1, 0, 0, 0], [0, 0, 1, 150], [0, 1, 0, 0]])     # (x,z) profile along y
    plan = CrossSection.square((x1 - x0, 20)).translate((x0, Y0W + 3.0)) + CrossSection.square((x1 - x0 - 6.0, 3.01)).translate((x0 + 3.0, Y0W)) + \
           CrossSection.circle(3.0, 32).translate((x0 + 3.0, Y0W + 3.0)) + CrossSection.circle(3.0, 32).translate((x1 - 3.0, Y0W + 3.0))
    cover = cover ^ (Manifold.extrude(plan, 20).translate((0, 0, H + 0.001)) + box(x0 - 1, x1 + 1, Y0W - 7, AY + 1, -1, H + 0.002))
    key = key - box(x0 - 1, x1 + 1, Y0W - 0.6, AY + 10, H + 0.001, 100)
    key = key + cover
    key = key - xcyl(x0 - 1, x1 + 1, AX_R + HOOD_PLAY)
    top_case = top_case + key
    bottom = bottom - box(x0 - FIT, x1 + FIT, KEY_Y0 - 1, KEY_YB + FIT, SPLIT, 100)

# ---- v18: fully printed key mechanism (no bought parts) ----
# Flat printed mat on the pocket floor. Under every key: a cantilever tongue (spring) bending into a floor
# cavity, a post on it that pushes the key up, and TWO vertical leaves (one per side, rooted in the floor)
# with 45-degree teeth: the post's teeth must spread them at mid-travel -> click on press and on release.
MAT_T, TG_A, TG_TIP, TG_SLOT = 0.8, 12.0, 2.0, 0.6
MAT_T2 = 1.2                     # v18c: mat thickness where no keycap is above (stiffer, does not curl)
TIP_TAB = (0.6, 0.2)             # v20: one layer only -> snaps by itself at the first press, no residue
SPRINGS = {"morbida": (3.2, 0.0, 3.2), "media": (4.0, 0.0, 4.0), "dura": (4.4, 0.3, 4.4),
           "larga": (4.0, 0.0, 7.0), "larga_forte": (4.0, 0.2, 7.0)}   # v20: (tip width, stiffening rib, root width)
SPRING_DEFAULT = "morbida"       # v19: chosen after the test (key Z)
TG_WMAX = 7.0                    # v20: widest root (tapered tongues)
POST_D = 3.5
PR = POST_D/2
REST_UP = 0.3                    # key pushed up until its tabs touch the frame
PRELOAD = 0.5                    # v20: keys feel 'full' at rest
POST_TOP = KEY_BOT + REST_UP + PRELOAD          # (v16-v20 post on the mat; v21: stem on the keycap)
STEM_BOT = SW_Z0 + 0.8 - PRELOAD - REST_UP           # keycap stem bottom (model pose) -> presses the free tongue tip
TRAVEL = 1.5
TP_TRAVEL = 1.2                  # v23d: trackpad: short travel like a real one
TP_CLICK_AT = 0.6                # v23d: the click snaps after ~0.6 mm (teeth pass at 0.45-0.75)
TOOTH_P = 0.5                    # 45 deg teeth (on the post and on each leaf)
CLICK_I = 0.25                   # v22c: stronger click (0.25 was masked by the stiff S springs)
LEAF_T = 0.6
LEAF_FACE = PR + 2*TOOTH_P - CLICK_I      # leaf inner face, from the post axis
BUMP_Z = STEM_BOT + 1.2          # v21: teeth on the keycap stem (model pose); at rest REST_UP higher
RIDGE_Z = BUMP_Z + REST_UP - TP_CLICK_AT   # v23d: at rest the stem teeth sit TP_CLICK_AT above the leaf teeth (trackpad only)
LEAF_ROOT = 1.0
LEAF_TOP = RIDGE_Z + TOOTH_P + 0.2
CAV_D = 2.5
MZ = SW_Z0                       # mat bottom = pocket floor


def ycyl(y0, y1, r, x, z):
    return Manifold.cylinder(y1 - y0, r, r, 24).rotate((-90, 0, 0)).translate((x, y0, z))


def xz_prism(pts, y0, y1):
    """Extrude an (x,z) polygon along y from y0 to y1."""
    m = Manifold.extrude(CrossSection([pts], mf.FillRule.EvenOdd), y1 - y0)
    return m.transform([[1, 0, 0, 0], [0, 0, -1, y1], [0, 1, 0, 0]])

# ================= v23 KEY MECHANISM (test 10-14): hollow keys on two vertical S springs =================
# - every key: hollow keycap (printed face down) + tabs centred on the 4 sides, sliding in channels of the
#   base (ribs in the gaps between keys and between rows) -> straight travel, tabs = end stop + retention
# - springs: per row two COMBS (front/back) printed lying flat: a rail in a floor channel + one vertical S per
#   switch point; the S pushes the key top plate (preload 0.8)
# - click only on the trackpad (stem with teeth on the trackpad, two leaves in the base)
exec(open(os.path.join(_HERE, "tasto_z.py")).read())
exec(open(os.path.join(_HERE, "guide_alette.py")).read())
ZS_KIND = "dura"                   # test 10: favourite
TP_ZS = dict(L=14.0, t=1.0, arms=(3.9, 5.5, 7.1))       # v24: 6 springs (3 per comb) -> ~2.1 N at rest, ~5 N at the bottom
TP_SPRING_X = (-35.0, 0.0, 35.0)   # v24: spring positions from the trackpad centre (test 15: 4 springs could not lift it)
TP_SKIRT = 1.5
TP_FLOOR = KEY_BOT + REST_UP - TP_TRAVEL - TP_SKIRT - 0.4   # trackpad pocket floor
FIN_BOT = 3.0                      # v26: fins hang lower (their top is the 45-degree slope), bottom = end stop
TP_GCLR = 0.6                      # v24: loose pocket all around (test 15: the full guided rim jammed)
TP_FINS = [(-30.0, -1), (30.0, -1), (-30.0, 1), (30.0, 1), (None, -1), (None, 1)]   # (x from centre | None = short side, side)
TP_FIN_W, TP_FIN_OUT, TP_FIN_CLR = 6.0, 2.8 - 0.15 + 0.15, 0.15

# ---- pockets ----
kb_pocket = Manifold.extrude(rrect(KB_X1 - KB_X0 + 3, KB_Y1 - KB_Y0 + 3, 3, KB_X0 - 1.5, KB_Y0 - 1.5), SPLIT - SW_Z0 + 1).translate((0, 0, SW_Z0))
tp_pocket = Manifold.extrude(tp_cs.offset(1.6 + TP_GCLR, **RJ), SPLIT - TP_FLOOR + 1).translate((0, 0, TP_FLOOR))
bottom = bottom - kb_pocket - tp_pocket

# ---- keycaps: hollow shell + tabs ----
lab_keys = [k for k in keys if k["lab"]]
keycaps = []
for k in keys:
    w, h = k["x1"] - k["x0"], k["y1"] - k["y0"]
    cap = Manifold.extrude(rrect(w, h, 1.8, k["x0"], k["y0"]), KEY_TOP - KEY_BOT).translate((0, 0, KEY_BOT))
    inner = Manifold.extrude(rrect(w - 2*ZK_WALL, h - 2*ZK_WALL, 1.0, k["x0"] + ZK_WALL, k["y0"] + ZK_WALL),
                             KEY_TOP - ZK_TOP_T - KEY_BOT + 0.01).translate((0, 0, KEY_BOT - 0.01))
    ytabs = [box(tx - TAB_W/2, tx + TAB_W/2, a, b, KEY_BOT, KEY_BOT + 1.0)
             for tx in key_tabs_x(k) for a, b in ((k["y0"] - TAB_L, k["y0"] + ZK_WALL), (k["y1"] - ZK_WALL, k["y1"] + TAB_L))]
    kc_ = cap - inner + union(ytabs) + side_tabs(k)
    if k["lab"]:
        kc_ = kc_ - letters[lab_keys.index(k)]
    keycaps.append(kc_)
keycaps_m = union(keycaps)

# ---- guides: ribs with sliding channels in the gaps between keys and between rows ----
g_add, g_cut = guide_parts(keys)
bottom = bottom + g_add

# ---- spring combs (one per row and side) + floor channels ----
def comb(xs, ys, x0, x1, t, mirror, top, L=None, arms=None, cap=None):
    """Comb in the model (rest pose): rail x0..x1 at y=ys, one S per x in xs."""
    cs = CrossSection.square((x1 - x0, RAIL_Z1 - RAIL_Z0)).translate((x0, RAIL_Z0))
    for x in xs:
        p = zs_profile(t, top, L, arms, cap)
        cs = cs + (p.mirror((1, 0)) if mirror else p).translate((x, 0))
    m = Manifold.extrude(cs, ZS_B).transform([[1, 0, 0, 0], [0, 0, 1, -ZS_B/2], [0, 1, 0, 0]])
    return m.translate((0, ys, 0))


def chan_box(x0, x1, ys):
    return box(x0 - FIT - 0.3, x1 + FIT + 0.3, ys - ZS_B/2 - FIT, ys + ZS_B/2 + FIT, RAIL_Z0 - 0.01, MZ + 0.01)


KEY_SPRING_TOP = KEY_TOP + REST_UP - ZK_TOP_T + ZS_PRE
combs_kb, chans = [], []
for r in range(len(ROWS)):
    row = [k for k in keys if k["row"] == r]
    yc = (row[0]["y0"] + row[0]["y1"])/2
    xs = [p[0] for k in row for p in key_switches(k)]
    x0, x1 = row[0]["x0"] + 1.0, row[-1]["x1"] - 1.0
    for sgn, mir in ((-1, False), (1, True)):
        combs_kb.append(comb(xs, yc + sgn*ZS_DY, x0, x1, ZS_T[ZS_KIND], mir, KEY_SPRING_TOP))
        chans.append(chan_box(x0, x1, yc + sgn*ZS_DY))

# ---- trackpad: hollow, guided skirt, 4 S springs on two combs, click stems ----
TP_PLATE = 1.2
tp_in = tp_cs.offset(-1.6, **RJ)
TP_FLANGE_DROP = 1.0                # v25d: walls + flange go down 1 mm below the trackpad body (strong ring)
# v26: SELF-SUPPORTING flange (printed face down, no support at all): its upper face is a 45-degree slope that
# rests on the edge of the deck hole (offset 0.4) -> retention + self-centring. Test 18a: PLA support every layer
# (PLA/PETG alternating) gave a flange that delaminated.
TP_HOLE_O = 0.4
FL_Z_EDGE = SPLIT - REST_UP                       # model z of the slope at the hole edge (touches the deck at rest)
FL_Z0 = FL_Z_EDGE + TP_HOLE_O                     # slope at the trackpad edge (r = 0)
FL_R = 1.6
tp_body = Manifold.extrude(tp_cs, TP_TOP - KEY_BOT).translate((0, 0, KEY_BOT))
fl_slope = Manifold.batch_hull([Manifold.extrude(tp_cs.offset(FL_R, **RJ), 0.001).translate((0, 0, FL_Z0 - FL_R)),
                                Manifold.extrude(tp_cs, 0.001).translate((0, 0, FL_Z0))])
fl_ring = Manifold.extrude(tp_cs.offset(FL_R, **RJ) - tp_cs.offset(-1.6, **RJ), FL_Z0 - FL_R - (KEY_BOT - TP_FLANGE_DROP) + 0.01).translate((0, 0, KEY_BOT - TP_FLANGE_DROP))
trackpad = tp_body + fl_slope + fl_ring
# v24: 6 guide fins (like the key tabs) sliding in notches of the pocket wall, instead of a full rim
tpc_x, tpc_y = TP_X0 + TP_W/2, TP_Y0 + TP_H/2
fins, fin_cuts = [], []
FIN_OUT = 2.8                      # fin outer face from the trackpad edge (pocket wall at 1.6 + TP_GCLR = 2.2)
def _fin(prof, radial_axis, edge, side, t0, t1):
    """prof: [(r, z)] radial profile (r outwards from the trackpad edge); extruded along the tangent t0..t1."""
    pts = [(edge + side*r, z) for r, z in prof]
    if side < 0:
        pts = pts[::-1]
    m = Manifold.extrude(CrossSection([pts], mf.FillRule.EvenOdd), t1 - t0)     # (u, z) plane, extrusion = tangent
    if radial_axis == "x":    # u = x, extrusion -> y
        return m.transform([[1, 0, 0, 0], [0, 0, 1, t0], [0, 1, 0, 0]]) if False else m.transform([[1, 0, 0, 0], [0, 0, -1, t1], [0, 1, 0, 0]])
    return m.transform([[0, 0, 1, t0], [1, 0, 0, 0], [0, 1, 0, 0]])             # u = y, extrusion -> x


FIN_PROF = [(-0.3, FIN_BOT), (FIN_OUT, FIN_BOT), (FIN_OUT, FL_Z0 - FIN_OUT), (TP_HOLE_O, FL_Z_EDGE), (-0.3, FL_Z_EDGE)]
fin_z0 = FIN_BOT + REST_UP - TP_TRAVEL - 0.1
for fx, side in TP_FINS:
    if fx is None:                 # short side: fin centred on it, radial = x
        xe = TP_X0 if side < 0 else TP_X0 + TP_W
        c, d = tpc_y - TP_FIN_W/2, tpc_y + TP_FIN_W/2
        ca, cb = sorted([xe - side*0.6, xe + side*(FIN_OUT + TP_FIN_CLR)])
        fins.append(_fin(FIN_PROF, "x", xe, side, c, d))
        fin_cuts.append(box(ca, cb, c - TP_FIN_CLR, d + TP_FIN_CLR, fin_z0, SPLIT + 0.01))
    else:                          # long side: radial = y
        ye = TP_Y0 if side < 0 else TP_Y0 + TP_H
        a, b = tpc_x + fx - TP_FIN_W/2, tpc_x + fx + TP_FIN_W/2
        cc, cd = sorted([ye - side*0.6, ye + side*(FIN_OUT + TP_FIN_CLR)])
        fins.append(_fin(FIN_PROF, "y", ye, side, a, b))
        fin_cuts.append(box(a - TP_FIN_CLR, b + TP_FIN_CLR, cc, cd, fin_z0, SPLIT + 0.01))
trackpad = trackpad + union(fins)
trackpad = trackpad - Manifold.extrude(tp_in, TP_TOP - TP_PLATE - 2.0 + 0.01).translate((0, 0, 2.0))
tpy = TP_Y0 + TP_H/2
TP_SPRING_TOP = TP_TOP + REST_UP - TP_PLATE + ZS_PRE
xa_, xb_ = tpc_x + TP_SPRING_X[0] - TP_ZS["L"]/2 - 1.5, tpc_x + TP_SPRING_X[-1] + TP_ZS["L"]/2 + 1.5
combs_tp = []
for sgn, mir in ((-1, False), (1, True)):
    combs_tp.append(comb([tpc_x + dx for dx in TP_SPRING_X], tpy + sgn*ZS_DY, xa_, xb_, TP_ZS["t"], mir, TP_SPRING_TOP, TP_ZS["L"], TP_ZS["arms"], (0.0, 0.0)))   # v25f: plain pad (no top bar)
    chans.append(chan_box(xa_, xb_, tpy + sgn*ZS_DY))
# click (v21 geometry): stem with 45-degree teeth on the trackpad, two leaves with teeth in the base
tp_leaves, tp_stems, tp_rooms = [], [], []
for x, y in tp_switches:
    stem = zcyl(x, y, STEM_BOT + 0.4, TP_TOP - TP_PLATE + 0.01, PR) + Manifold.cylinder(0.4, PR - 0.4, PR, 32).translate((x, y, STEM_BOT))
    for sx in (1, -1):
        bump = xz_prism([(sx*(PR - 0.01), BUMP_Z - TOOTH_P), (sx*(PR + TOOTH_P), BUMP_Z), (sx*(PR - 0.01), BUMP_Z + TOOTH_P)][::sx], y - 1.5, y + 1.5)
        stem = stem + bump.translate((x, 0, 0))
        lx0, lx1 = sorted([sx*LEAF_FACE, sx*(LEAF_FACE + LEAF_T)])
        tp_leaves.append(box(x + lx0, x + lx1, y - 2, y + 2, LEAF_ROOT - 0.01, LEAF_TOP))
        ridge = xz_prism([(sx*(LEAF_FACE + 0.01), RIDGE_Z - TOOTH_P), (sx*(LEAF_FACE - TOOTH_P), RIDGE_Z), (sx*(LEAF_FACE + 0.01), RIDGE_Z + TOOTH_P)][::-sx], y - 1.5, y + 1.5)
        tp_leaves.append(ridge.translate((x, 0, 0)))
    side = LEAF_FACE + LEAF_T + 0.5
    tp_rooms.append(box(x - side, x + side, y - 2.4, y + 2.4, LEAF_ROOT, TP_FLOOR + 0.01))
    tp_stems.append(stem)
trackpad = trackpad + union(tp_stems)
bottom = bottom - union(chans) - union(tp_rooms) + union(tp_leaves) - g_cut - union(fin_cuts)
combs = combs_kb + combs_tp
bottom = bottom + ridges_m


# ---- snap hooks: beam on the bottom case, catch pocket in the top case ----
# (x, y, barb direction in degrees: 0 = +y, 180 = -y, 90 = -x, -90 = +x)
HOOKS = [(30, 30, 0), (W - 30, 30, 0), (30, AY - 11, 180), (80, AY - 11, 180), (W/2, AY - 11, 180), (W - 80, AY - 11, 180), (W - 30, AY - 11, 180),
         # v14: hooks along the side edges turned 90 deg, barb facing the outside edge
         (12, DB*0.30, 90), (W - 12, DB*0.30, -90), (12, DB*0.75, 90), (W - 12, DB*0.75, -90),
         (12, AY - 14, 90), (W - 12, AY - 14, -90), (12, 14, 90), (W - 12, 14, -90),   # v17: rear corner hooks moved forward
         # v18: intermediate row between keyboard and trackpad
         (40, 58, 180), (85, 58, 180), (W/2, 58, 180), (W - 85, 58, 180), (W - 40, 58, 180)]


def yz_prism(pts, x0, x1):
    """Extrude a (y,z) polygon along x from x0 to x1."""
    m = Manifold.extrude(CrossSection([pts], mf.FillRule.EvenOdd), x1 - x0)
    return m.transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])


def hook_parts():
    """Hook at the origin, barb towards +y: (slot in bottom case, hook body, pocket in top case).
    v19: catch face and ledge are inclined (rising outwards by HOOK_RAMP); the barb is modelled HOOK_PRELOAD
    lower than the ledge, so once snapped the beam stays slightly bent and the ramp pulls the top case down."""
    hx0, hx1 = -HOOK_W/2, HOOK_W/2
    face, back, t = HOOK_T/2, -HOOK_T/2, HOOK_TOP
    tg = np.tan(np.radians(HOOK_RAMP))
    L = SPLIT + HOOK_LEDGE                            # ledge top at its inner edge (y = face + 0.2)
    y_in, y_out = face + 0.2, face + HOOK_BARB + 0.3
    ledge_z = lambda yy: L + (yy - y_in)*tg
    slot = box(hx0 - 0.4, hx1 + 0.4, back - 1.2, face + 0.3, HOOK_Z0, SPLIT + 1)
    beam = box(hx0, hx1, back, face, HOOK_Z0 - 0.5, t)
    u0 = ledge_z(face) - HOOK_PRELOAD                 # barb underside at the beam
    u1 = ledge_z(face + HOOK_BARB) - HOOK_PRELOAD     # ... and at the tip
    barb = yz_prism([(face - 0.01, u0), (face + HOOK_BARB, u1), (face + HOOK_BARB, u1 + 0.05), (face - 0.01, t)], hx0, hx1)   # v24: long lead-in ramp
    entrance = box(hx0 - 0.4, hx1 + 0.4, back - 1.2, y_in, SPLIT - 1, t + 0.2)
    entrance = entrance + yz_prism([(y_in - 0.01, SPLIT - 0.01), (y_in + 0.6, SPLIT - 0.01), (y_in - 0.01, SPLIT + 0.6)], hx0 - 0.4, hx1 + 0.4)   # v24: chamfer on the catch edge
    room = yz_prism([(face, ledge_z(face) - 0.01), (y_out, ledge_z(y_out)), (y_out, t + 0.2), (face, t + 0.2)], hx0 - 0.4, hx1 + 0.4)
    return slot, beam + barb, entrance + room


H_SLOT, H_BODY, H_POCKET = hook_parts()
for hx, hy, ang in HOOKS:
    place = lambda m: m.rotate((0, 0, ang)).translate((hx, hy, 0))
    bottom = bottom - place(H_SLOT) + place(H_BODY)
    top_case = top_case - place(H_POCKET)

for ax_, ay_ in ALIGN:
    pin_ = zcyl(ax_, ay_, SPLIT - 1, SPLIT + ALIGN_H - 0.6, ALIGN_D/2) + Manifold.cylinder(0.6, ALIGN_D/2, ALIGN_D/2 - 0.6, 32).translate((ax_, ay_, SPLIT + ALIGN_H - 0.6))
    bottom = bottom + pin_
    top_case = top_case - zcyl(ax_, ay_, SPLIT - 1, SPLIT + ALIGN_H + 0.3, ALIGN_HOLE/2) \
        - Manifold.cylinder(0.6, ALIGN_HOLE/2 + 0.6, ALIGN_HOLE/2, 32).translate((ax_, ay_, SPLIT - 0.01))

def union2d(cs_list):
    out = CrossSection()
    for c in cs_list:
        out = out + c
    return out


# ---- v27b: bottom engraving (user's choice B): "AvocadoBook" on top, below a simple Colosseum + "Designed in Italy";
# the two lines are justified (same left and right edges). Debossed 0.4 mm under the trackpad area (x 75-175,
# y 6-26 has >= 1.6 mm of solid floor). Mirrored in x: reads correctly when the laptop is turned over like a book page.
def colosseum(w=13.0, h=5.4):
    """Simple wide Colosseum elevation: 3 tiers, few arches, ruined (stepped) on the right; arches left raised."""
    th = h/3
    tiers = [(0.0, th, 1.00, 5), (th, 2*th, 1.00, 5), (2*th, h, 0.66, 3)]
    wall, holes = CrossSection(), []
    for z0, z1, f, n in tiers:
        x1 = w*f
        band = CrossSection.square((x1, z1 - z0)).translate((0, z0))
        if f < 1.0:
            band = band + CrossSection([[(x1, z0), (x1 + 1.4, z0), (x1, z1)]], mf.FillRule.EvenOdd)
        wall = wall + band
        pitch = w/5; ah = (z1 - z0) - 0.6; aw = min(pitch*0.45, ah)    # same column grid on every tier
        for k in range(n):
            cx = pitch*(k + 0.5)
            if cx + aw/2 > x1 - 0.2: continue
            holes.append(CrossSection.square((aw, ah - aw/2)).translate((cx - aw/2, z0 + 0.3)) +
                         CrossSection.circle(aw/2, 24).translate((cx, z0 + 0.3 + ah - aw/2)))
    return wall - union2d(holes)


DII_DEPTH = 0.6        # v27d: black inlay (3 layers, opaque), flush with the underside
_name = glyph("AvocadoBook", 0, 0, cap_h=5.5)
_dsg = glyph("Designed in Italy", 0, 0, cap_h=3.2)
_nb, _db = _name.bounds(), _dsg.bounds()
# v27c: Colosseum removed (user): two centred lines
_name = _name.translate((W/2 - (_nb[0] + _nb[2])/2, 20.5 - (_nb[1] + _nb[3])/2))
_dsg = _dsg.translate((W/2 - (_db[0] + _db[2])/2, 11.5 - (_db[1] + _db[3])/2))
_dii = (_name + _dsg).mirror((1, 0)).translate((W, 0))
designed_in_italy = Manifold.extrude(_dii, DII_DEPTH + 1).translate((0, 0, -1))
bottom = bottom - designed_in_italy
bottom_text = Manifold.extrude(_dii, DII_DEPTH)          # v27d: printed in black PETG in the recess (first 3 layers)


# ================= LID (closed pose) =================
LZ0 = H + GAP
lid = rounded_slab(W, AY + RK, T, R_PLAN, R_OUT, 0, cb=CH_IN).translate((0, 0, LZ0))
lid_plan = Manifold.extrude(rrect(W, AY + RK, R_PLAN), 100).translate((0, 0, -10))
lid = (lid ^ box(-1, W + 1, -1, AY, -1, 100)) + (lid_plan ^ xcyl(-1, W + 1, RK))
supports = []
for x0, x1 in KN:
    lid = lid - box(x0 - KN_CLR, x1 + KN_CLR, AY - NOTCH, AY + RK + 1, AZ - RK - 1, AZ + RK + 1)
    lid = lid + xcyl(x0 - KN_CLR - 1, x1 + KN_CLR + 1, AX_R)          # integral axle bar
    # breakaway support under the axle bar (lid is printed outer face down)
    # v26d: wedge, 1.2 mm at the axle, 8 mm on the bed (the 1.2 mm strip was knocked over by the nozzle)
    zb_, zt_ = AZ + AX_R + SUP_GAP, LZ0 + T
    supports.append(yz_prism([(AY - 0.6, zb_), (AY + 0.6, zb_), (AY + 4.0, zt_), (AY - 4.0, zt_)], x0 - KN_CLR + 1, x1 + KN_CLR - 1))
support = union(supports)
# detent grooves: closed position + open position
for xc in DET_X:
    g = xcyl(xc - 5, xc + 5, GR, y=AY, z=ZD + DET_P - 0.1 - GR)   # 0.1 preload in the groove: centred, no play
    lid = lid - g - rot_lid(g, -DET_OPEN)

scr_cs = rrect(SCR_W, SCR_H, 5, BZ_SIDE, BZ_TOP)       # visible window
REC = FRAME_T + PAPER_GAP
FR_Y1 = BZ_TOP + SCR_H + FRAME_BOT
paper_cs = CrossSection.square((SCR_W + 2*PAPER_OVL, BZ_TOP + SCR_H + PAPER_OVL + 1)).translate((BZ_SIDE - PAPER_OVL, -1))
# frame = the screen-side slice of the lid itself -> identical outline and edge profile (closed pose: visible face down at LZ0)
frame = lid ^ box(-1, W + 1, -2, FR_Y1, LZ0 - 1, LZ0 + REC)
frame = frame - Manifold.extrude(scr_cs, 10).translate((0, 0, LZ0 - 1)) \
              - Manifold.extrude(paper_cs, PAPER_GAP + 0.01).translate((0, 0, LZ0 + FRAME_T))
bevel = Manifold.batch_hull([Manifold.extrude(scr_cs.offset(0.8, **RJ), 0.01).translate((0, 0, LZ0 - 0.01)),
                             Manifold.extrude(scr_cs, 0.01).translate((0, 0, LZ0 + 0.8))])
frame = frame - bevel
xl = 4.0
yb = (BZ_TOP + SCR_H + PAPER_OVL + FR_Y1)/2
PEG_Y = (18, 40, 62, 84, 106, 128, 150)                       # v15: one peg every ~22 mm
PEGS = [(xl, y) for y in PEG_Y] + [(W - xl, y) for y in PEG_Y] + \
       [(x, yb) for x in (30, 80, 105, W/2, W - 105, W - 80, W - 30)]
def peg_at(px, py, z0):
    p = zcyl(px, py, z0 - 0.01, z0 + PEG_L - 0.4, PEG_D/2) + \
        Manifold.cylinder(0.4, PEG_D/2, PEG_D/2 - 0.4, 24).translate((px, py, z0 + PEG_L - 0.4))
    for a in (0, 120, 240):
        rib = box(PEG_D/2 - 0.1, PEG_D/2 + PEG_RIB, -0.25, 0.25, z0, z0 + PEG_L - 0.6).rotate((0, 0, a))
        p = p + rib.translate((px, py, 0))
    return p


def hole_at(px, py, z0, d=PEG_HOLE):
    return zcyl(px, py, z0 - 0.1, z0 + PEG_L + 0.3, d/2) + \
        Manifold.cylinder(0.5, d/2 + 0.5, d/2, 32).translate((px, py, z0 - 0.01))   # lead-in chamfer


for px, py in PEGS:
    frame = frame + peg_at(px, py, LZ0 + REC)
    lid = lid - hole_at(px, py, LZ0 + REC)
# recess for frame + paper, black floor seen through the window when there is no paper
lid = lid - box(-1, W + 1, -2, FR_Y1 + FRAME_CLR, LZ0 - 1, LZ0 + REC)
screen = inlay(scr_cs.offset(1.0, **RJ), LZ0 + REC, INLAY, visible_up=False)
screen = screen - union([hole_at(px, py, LZ0 + REC) for px, py in PEGS])
LOGO_BITE = True                 # playful bite on the avocado (False = plain avocado)
logo_cs = avocado_logo(SCR_H*0.47, LOGO_BITE).rotate(180).translate((W/2, BZ_TOP + SCR_H*0.5))
logo = inlay(logo_cs, LZ0 + T - LOGO_D, LOGO_D, visible_up=True, ring=False)
lid = clean(lid - screen - logo)
top_case = clean(top_case)
bottom = clean(bottom)

# ================= checks =================
if "--check" in sys.argv:
    static = union([bottom - ridges_m, top_case, keycaps_m, trackpad])
    print('frame vs lid', round((frame ^ lid).volume(), 3), '| frame vs screen', round((frame ^ screen).volume(), 3))
    lid_all = lid + frame
    print("static overlaps (should be ~0):",
          round((bottom ^ top_case).volume(), 3), round((keycaps_m ^ (bottom + top_case)).volume(), 3),
          round((trackpad ^ (bottom + top_case)).volume(), 3))
    for deg in [0, 2, 5, 10, 30, 60, 90, 100, 103, 105, 107, 110, 120, 150, 170, 175, 178, 180, 182, 185]:
        lm = rot_lid(lid_all, deg)
        print(f"open {deg:3d}: lid vs base {(lm ^ static).volume():8.2f} mm3 | lid vs detent ridges {(lm ^ ridges_m).volume():6.2f} mm3")

parts = {
    "A_fondo": bottom, "A_fondo_scritta_nera": bottom_text,
    "B_piano": top_case, "B_trackpad": trackpad,
    "C_coperchio_corpo": lid, "C_supporto_staccabile": support, "C_coperchio_schermo": screen, "C_coperchio_logo": logo,
    "C_cornice": frame,
    "D_tasti": keycaps_m, "D_lettere": letters_m,
    **{f"F_molle_S_fila{i // 2 + 1}_{'davanti' if i % 2 == 0 else 'dietro'}": c for i, c in enumerate(combs_kb)},
    "F_molle_S_trackpad_davanti": combs_tp[0], "F_molle_S_trackpad_dietro": combs_tp[1],
}


def tm(m):
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)


assembled_names = ["A_fondo", "A_fondo_scritta_nera"] + [n for n in parts if n.startswith("F_")] + ["B_piano", "B_trackpad", "C_coperchio_corpo", "C_coperchio_schermo", "C_coperchio_logo", "C_cornice", "D_tasti", "D_lettere"]
closed = {n: tm(parts[n]) for n in assembled_names}
opened = {n: tm(rot_lid(parts[n], 105) if n[0] == "C" else parts[n]) for n in assembled_names}

# ---------- print orientation ----------
pp = dict(parts)
for n in ["C_coperchio_corpo", "C_coperchio_schermo", "C_coperchio_logo", "C_supporto_staccabile"]:
    pp[n] = parts[n].rotate((180, 0, 0)).translate((0, 0, LZ0 + T))
pp["C_cornice"] = parts["C_cornice"].translate((0, 0, -LZ0))     # printed visible face down
pp["B_piano"] = parts["B_piano"].translate((0, 0, -SPLIT))
for n in [n for n in parts if n.startswith("F_")]:      # combs printed lying flat (S in the plate plane)
    pp[n] = strip_print(parts[n])
pp["B_trackpad"] = parts["B_trackpad"].rotate((180, 0, 0)).translate((0, 0, TP_TOP))   # face down (top plate on the bed, skirt and stems grow upwards)
# keycaps: printed FACE DOWN (v19: smooth top from the plate, letters in the first layers); layout spread out
kc, lt = [], []
cx, cy = (KB_X0 + KB_X1)/2, (KB_Y0 + KB_Y1)/2
for k, m in zip(keys, keycaps):
    kx, ky = (k["x0"] + k["x1"])/2, (k["y0"] + k["y1"])/2
    d = ((kx - cx)*0.12, (ky - cy)*0.35, 0)
    kc.append(m.translate(d).rotate((180, 0, 0)).translate((0, 0, KEY_TOP)))
for k, let in zip([k for k in keys if k["lab"]], letters):
    kx, ky = (k["x0"] + k["x1"])/2, (k["y0"] + k["y1"])/2
    lt.append(let.translate(((kx - cx)*0.12, (ky - cy)*0.35, 0)).rotate((180, 0, 0)).translate((0, 0, KEY_TOP)))
pp["D_tasti"], pp["D_lettere"] = union(kc), union(lt)

printp = {n: tm(m) for n, m in pp.items()}
for n, m in parts.items():
    t = printp[n]
    print(f"{n:22s} watertight={t.is_watertight} pieces={len(m.decompose()):3d} vol={t.volume/1000:6.1f}cm3 size={np.ptp(t.bounds, 0).round(1)}")
n_sw = len(switch_pts)
print(f"W={W:.1f} DB={DB:.1f} screen {SCR_W:.0f}x{SCR_H:.0f} ({np.hypot(SCR_W, SCR_H)/25.4:.1f} in), keys={len(keys)}, switches={n_sw}, hooks={len(HOOKS)}")
os.makedirs(BUILD, exist_ok=True)
pickle.dump((printp, closed, opened), open(os.path.join(BUILD, "parts.pkl"), "wb"))
