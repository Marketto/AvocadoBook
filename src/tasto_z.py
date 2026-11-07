"""Variant 3 key (v22): two vertical S springs under the key, like a fidget clicker.
Each spring is a flat strip printed LYING on the plate (the S is drawn in the plate plane, so the arms bend
inside the layers: strong, no delamination); it then stands upright in a channel of the base floor.
The keycap is hollow, printed face down, and keeps the v21 stem with teeth -> click against the base leaves.
Requires the generator globals (exec'd before)."""
import numpy as np

ZS_B = 2.0            # v22b: strip thickness (= print height, 10 layers); was 2.4 in test 10
ZS_L = 10.0           # arm span
ZS_ARMS = (3.9, 5.4, 6.9, 8.4)   # arm centre heights (model pose = key at rest)
ZS_PAD = 1.8          # contact pad width
ZS_CAP = (0.0, 0.0)   # v25f: no top bar (test 18b: the plain pad works better); was (8.0, 0.5)
ZS_PRE = 0.8          # preload against the key top plate at rest
ZS_DY = 4.6           # strips at yc +- ZS_DY (v22b: moved out, room for the guide pins)
RAIL_Z0, RAIL_Z1 = 0.9, 2.3     # rail in a channel of the floor (channel top = pocket floor MZ)
ZK_TOP_T = 1.2        # hollow keycap: top plate
ZK_WALL = 1.2
ZS_T = {"morbida": 0.7, "media": 0.8, "dura": 0.95}   # v22b: "dura" (test 10 favourite) = 0.9 at 2.4 thick -> 0.95 at 2.0
# v22b: 4 guide pins on the keycap sliding in holes of the base (no sideways play)
KEY_CLICK = False             # v22d: click only on the trackpad; keys have no stem/leaves
GUIDE_PINS = False            # v22c: removed (friction: pins + tabs over-constrained the key in test 12)
GP_D, GP_HOLE = 1.8, 2.5      # pin / hole (small vertical holes print ~0.4 undersize -> ~0.25 clearance)
GP_DY = 1.6                   # pins at yc +- GP_DY, near the left/right walls
GP_BOT = 2.3                  # pin bottom at rest (absolute z)
GP_COLLAR = 4.0               # guide collar top (below the pressed keycap wall: 4.3)
GP_FLOOR = 0.6                # hole bottom (pressed pin bottom = 0.8)
LEAF_SIDE = LEAF_FACE + LEAF_T + 0.5


def zs_profile(t, top, L=None, arms=None, cap=None):
    """2D outline (x, z) of one S strip, centred on x=0: rail + post + arms with round turns + pad."""
    L = ZS_L if L is None else L
    cs = CrossSection.square((L + 2.0, RAIL_Z1 - RAIL_Z0)).translate((-L/2 - 1.0, RAIL_Z0))     # rail
    z = list(ZS_ARMS if arms is None else arms)
    cs += CrossSection.square((t, z[0] - RAIL_Z1 + t/2)).translate((-L/2 - t/2, RAIL_Z1 - 0.01))   # post
    side, x0 = -1, -L/2
    for i in range(len(z)):
        if i < len(z) - 1:
            r = (z[i + 1] - z[i])/2
            xe = (L/2 - r) if side < 0 else (-L/2 + r)
            xa, xb = sorted([x0, xe])
            cs += CrossSection.square((xb - xa, t)).translate((xa, z[i] - t/2))
            ring = CrossSection.circle(r + t/2, 48) - CrossSection.circle(r - t/2, 48)
            half = CrossSection.square((r + t, 2*r + 2*t)).translate((0 if side < 0 else -(r + t), -r - t))
            cs += (ring ^ half).translate((xe, z[i] + r))
            side, x0 = -side, xe
        else:    # last arm: from the turn to the centre, then the pad
            xa, xb = sorted([x0, 0.0])
            cs += CrossSection.square((xb - xa + ZS_PAD/2, t)).translate((xa - (ZS_PAD/2 if x0 > 0 else 0), z[i] - t/2))
            cs += CrossSection.square((ZS_PAD, top - z[i])).translate((-ZS_PAD/2, z[i]))
            cw, ct = ZS_CAP if cap is None else cap
            if cw > 0:                                    # v25: flat bar on top (stable contact, like the rail below)
                cs += CrossSection.square((cw, ct)).translate((-cw/2, top - ct))
    return cs


def zs_strip(t, xc, ys, mirror=False, top=None):
    """Strip standing in the model (closed pose, key at rest): extrude the (x,z) outline along y."""
    top = (KEY_TOP + REST_UP - ZK_TOP_T + ZS_PRE) if top is None else top
    cs = zs_profile(t, top)
    if mirror:
        cs = cs.mirror((1, 0))
    m = Manifold.extrude(cs, ZS_B)                                  # (x, z) in the xy plane, thickness along z
    m = m.transform([[1, 0, 0, 0], [0, 0, 1, -ZS_B/2], [0, 1, 0, 0]])   # -> (x, y, z): profile y->z, extrusion -> y
    return m.translate((xc, ys, 0))


def zkey_parts(k, kind="media"):
    """Returns (keycap in model pose, [strip, strip] in rest pose, base_cut, base_refill_box)."""
    i = keys.index(k)
    w, h = k["x1"] - k["x0"], k["y1"] - k["y0"]
    xc, yc = (k["x0"] + k["x1"])/2, (k["y0"] + k["y1"])/2
    inner = Manifold.extrude(rrect(w - 2*ZK_WALL, h - 2*ZK_WALL, 1.0, k["x0"] + ZK_WALL, k["y0"] + ZK_WALL),
                             KEY_TOP - ZK_TOP_T - KEY_BOT + 0.01).translate((0, 0, KEY_BOT - 0.01))
    j = sum(len(key_switches(kk)) for kk in keys[:i])
    stem = union(stems_kb[j:j + len(key_switches(k))])
    keycap = keycaps[i] - inner + (stem + zcyl(xc, yc, STEM_BOT + 1, KEY_TOP - ZK_TOP_T + 0.01, PR))
    if not KEY_CLICK:     # remove the stem with its teeth: hollow key, only the springs underneath
        keycap = keycaps[i] - inner - box(-999, 999, -999, 999, -50, KEY_BOT)
    t = ZS_T[kind]
    strips = [zs_strip(t, xc, yc - ZS_DY), zs_strip(t, xc, yc + ZS_DY, mirror=True)]
    chan = union([box(xc - ZS_L/2 - 1.0 - FIT - 0.5, xc + ZS_L/2 + 1.0 + FIT + 0.5, ys - ZS_B/2 - FIT, ys + ZS_B/2 + FIT, RAIL_Z0, MZ + 0.01)
                  for ys in (yc - ZS_DY, yc + ZS_DY)])
    # guide pins: hang from the top plate, joined to the side wall by a web; collars + holes in the base
    gx = w/2 - ZK_WALL - GP_D/2 - 0.35
    pins, webs, collars, holes = [], [], [], []
    zb = GP_BOT - REST_UP                    # model pose
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = xc + sx*gx, yc + sy*GP_DY
            pins.append(zcyl(px, py, zb + 0.3, KEY_TOP - ZK_TOP_T + 0.01, GP_D/2) +
                        Manifold.cylinder(0.3, GP_D/2 - 0.3, GP_D/2, 24).translate((px, py, zb)))
            wx0, wx1 = sorted([px, xc + sx*(w/2 - ZK_WALL + 0.01)])
            webs.append(box(wx0, wx1, py - 0.5, py + 0.5, KEY_BOT, KEY_TOP - ZK_TOP_T + 0.01))
            collars.append(zcyl(px, py, MZ - 0.01, GP_COLLAR, GP_HOLE/2 + 0.8))
            holes.append(zcyl(px, py, GP_FLOOR, GP_COLLAR + 1, GP_HOLE/2) +
                         Manifold.cylinder(0.4, GP_HOLE/2, GP_HOLE/2 + 0.4, 24).translate((px, py, GP_COLLAR - 0.39)))
    if not GUIDE_PINS:
        return keycap, strips, chan, Manifold(), Manifold()
    keycap = keycap + union(pins + webs)
    return keycap, strips, chan, union(collars), union(holes)


def strip_print(m):
    """Strip lying on the plate (profile in the plate plane)."""
    b = m.bounding_box()
    m = m.translate((0, -(b[1] + b[4])/2, 0)).rotate((-90, 0, 0))
    b = m.bounding_box()
    return m.translate((0, 0, -b[2]))
