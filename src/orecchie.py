"""Built-in anti-lift 'ears' for thin flat parts (spring combs): thin discs that touch the part only on the
outside of its convex hull, so they never fill the gaps between the S arms (a slicer brim would)."""
import numpy as np
from manifold3d import Manifold, CrossSection
import manifold3d as mf

EAR_R, EAR_H, EAR_STEP = 4.0, 0.4, 16.0      # radius, height (2 layers), min distance between ears


def add_ears(m, r=EAR_R, h=EAR_H, step=EAR_STEP):
    """m: part in print pose (bottom at z=0). Returns m + ears."""
    foot = m.slice(0.1)
    hull = foot.hull()
    poly = np.vstack([np.asarray(q) for q in hull.to_polygons()])
    # points along the hull outline (every 1 mm) that lie on the real part outline -> ears touch the part there
    cand = []
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        n = max(1, int(np.hypot(*(b - a))))
        for t in np.linspace(0, 1, n, endpoint=False):
            q = a + (b - a)*t
            if (foot ^ CrossSection.circle(0.3, 12).translate((float(q[0]), float(q[1])))).area() > 0.1:
                cand.append(q)
    cand = np.array(cand)
    # two groups (upper / lower half of the part): ears at least `step` apart inside a group,
    # and at least one diameter apart from the other group -> every S pad gets an ear, plus the rail
    ym = (cand[:, 1].min() + cand[:, 1].max())/2
    grp = (cand[:, 1] > ym).astype(int)
    order = [cand[:, 0].argmin(), cand[:, 0].argmax()] + list(np.argsort(-grp, kind="stable"))
    chosen = []
    for i in order:
        q, g = cand[i], grp[i]
        if all(np.hypot(*(q - c)) >= (step if g == cg else 2*r + 0.5) for c, cg in chosen):
            chosen.append((q, g))
    R_UP = 2.2     # small ears on the S pads: a big one would touch the nearby turn of the S
    chosen = [(c, r if g == 0 else R_UP) for c, g in chosen]
    discs = None
    for p, rr in chosen:
        d = CrossSection.circle(rr, 32).translate((float(p[0]), float(p[1])))
        discs = d if discs is None else discs + d
    ears = discs - hull.offset(-0.3, join_type=mf.JoinType.Miter)        # outside the hull, 0.3 mm overlap into the part
    keep = [e for e in ears.decompose() if (e ^ foot).area() > 0.5]         # only ears really joined to the part
    if not keep:
        return m
    out = m + Manifold.extrude(CrossSection.batch_boolean(keep, mf.OpType.Add) if len(keep) > 1 else keep[0], h)
    parts = out.decompose()
    return max(parts, key=lambda q: q.volume()) if len(parts) > 1 else out


def add_breakaway_ears(m, r=4.0, h=0.4, neck_w=1.0, neck_l=1.5, step=45.0):
    """v24: ears only on the rail (ends + along the bottom edge), each joined by a thin neck (1.0 x 0.4 mm):
    they snap off by hand, no scissors, and nothing touches the S springs."""
    b = m.bounding_box()
    foot = m.slice(0.1)
    x0, x1, y0 = b[0], b[3], b[1]
    pieces = []
    rail_y = y0 + 0.7                                      # inside the rail, near its bottom edge
    for xe, sx in ((x0, -1), (x1, 1)):                     # rail ends
        pieces.append(CrossSection.square((neck_l + 0.3, neck_w)).translate((xe - (neck_l if sx < 0 else 0.3) if sx < 0 else xe - 0.3, rail_y - neck_w/2)))
        pieces.append(CrossSection.circle(r, 32).translate((xe + sx*(neck_l + r - 0.2), rail_y)))
    n = max(1, int((x1 - x0)//step))
    for i in range(1, n + 1):                              # along the bottom edge of the rail
        x = x0 + (x1 - x0)*i/(n + 1)
        pieces.append(CrossSection.square((neck_w, neck_l + 0.3)).translate((x - neck_w/2, y0 - neck_l)))
        pieces.append(CrossSection.circle(r, 32).translate((x, y0 - neck_l - r + 0.2)))
    ears = CrossSection.batch_boolean(pieces, mf.OpType.Add) - foot.offset(-0.3, join_type=mf.JoinType.Miter)
    out = m + Manifold.extrude(ears, h)
    assert len(out.decompose()) == 1
    return out


def add_corner_ears(m, pts, out_dirs, r=6.0, h=0.4, neck_w=4.0, neck_l=0.6):   # v26g: stronger (test: 1.2 mm necks tore off)
    """v26e: anti-warp ears for a big flat part (the lid): disc r at distance neck_l outside each given edge point,
    joined by a thin neck (snaps off by hand). pts: [(x, y)] on the outline, out_dirs: unit vectors pointing out."""
    foot = m.slice(0.1)
    pieces = []
    for (x, y), (dx, dy) in zip(pts, out_dirs):
        rr = r if dy <= 0 else min(r, 4.5)        # back edge: smaller (room for the purge tower)
        cx, cy = x + dx*(neck_l + rr), y + dy*(neck_l + rr)
        pieces.append(CrossSection.circle(rr, 40).translate((cx, cy)))
        # neck: rectangle from 0.5 mm inside the part to the disc
        L = neck_l + 0.8
        nk = CrossSection.square((L, neck_w)).translate((-0.5, -neck_w/2))
        ang = np.degrees(np.arctan2(dy, dx))
        pieces.append(nk.rotate(ang).translate((x, y)))
    ears = CrossSection.batch_boolean(pieces, mf.OpType.Add) - foot.offset(-0.5, join_type=mf.JoinType.Miter)
    out = m + Manifold.extrude(ears, h)
    assert len(out.decompose()) == 1
    return out
