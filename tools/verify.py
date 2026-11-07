"""Full verification suite of the model (run after EVERY geometry change, before exporting).
Usage: python tools/verify.py [--fast]     (--fast skips the slow insertion sweeps and the skin scan)
Exit code 1 if a hard check fails. Prints one line per check: OK / FAIL / INFO."""
import sys, math, numpy as np
sys.path.insert(0, __import__("os").path.dirname(__file__))
from _model import load
FAST = "--fast" in sys.argv
g = load()
box, xcyl, rot_lid, union = g["box"], g["xcyl"], g["rot_lid"], g["union"]
bottom, top_case, lid, frame = g["bottom"], g["top_case"], g["lid"], g["frame"]
keys_m, trackpad, ridges = g["keycaps_m"], g["trackpad"], g["ridges_m"]
REST_UP, TRAVEL, TP_TRAVEL, KN, AY, AX_R = g["REST_UP"], g["TRAVEL"], g["TP_TRAVEL"], g["KN"], g["AY"], g["AX_R"]
fails = []
def ov(a, b): return round((a ^ b).volume(), 3)
def check(name, ok, info=""):
    print(("OK   " if ok else "FAIL ") + name + (f"  [{info}]" if info else ""))
    if not ok: fails.append(name)
la = lid + frame
# 1. parts
check("fondo un pezzo", len(bottom.decompose()) == 1)
check("piano un pezzo", len(top_case.decompose()) == 1)
check("fondo/piano solo dentini dei ganci (~7.3 mm3)", ov(bottom, top_case) < 7.5, ov(bottom, top_case))
# 2. keys / trackpad
check("tasti a riposo liberi", ov(keys_m.translate((0, 0, REST_UP)), bottom + top_case) == 0)
check("tasti premuti liberi", ov(keys_m.translate((0, 0, REST_UP - TRAVEL)), bottom) == 0)
check("trackpad a riposo libero", ov(trackpad.translate((0, 0, REST_UP)), bottom + top_case) < 0.01)
check("coperchio chiuso non tocca tasti/trackpad", ov(la, keys_m.translate((0, 0, REST_UP)) + trackpad.translate((0, 0, REST_UP))) == 0)
# 3. lid rotation 0..185 every degree
st = union([bottom - ridges, top_case, keys_m.translate((0, 0, REST_UP)), trackpad.translate((0, 0, REST_UP))])
worst = max(((rot_lid(la, d) ^ st).volume(), d) for d in range(0, 186, 1 if not FAST else 5))
check("rotazione schermo 0-185 senza contatti", worst[0] < 1e-3, f"max {worst[0]:.3f} mm3 a {worst[1]} gradi")
check("scatti: dentini nell'incavo a 0 e 105", ov(la, ridges) > 0.5 and ov(rot_lid(la, 105), ridges) > 0.5)
# 4. axle captured
x0, x1 = KN[0]; axle = xcyl(x0 + 1, x1 - 1, AX_R); walls = bottom + top_case; fr = []
for ang in range(0, 360, 15):
    dy, dz = -math.sin(math.radians(ang)), math.cos(math.radians(ang)); f = 0
    while f < 3 and (axle.translate((0, dy*(f + 0.05), dz*(f + 0.05))) ^ walls).volume() < 1e-3: f += 0.05
    fr.append(f)
check("asse del coperchio bloccato", max(fr) < 0.5, f"corsa max {max(fr):.2f} mm")
# 5. top case lowered onto the mounted axle (lid at >= 105 deg)
tck = top_case ^ union([box(a - 1, b + 1, AY - 15, AY + 2, -1, 30) for a, b in KN])
sw = union([tck.translate((0, 0, dz)) for dz in np.arange(0, 8, 0.1 if not FAST else 0.5)])
check("piano scende sull'asse (coperchio a 105)", ov(sw, bottom + rot_lid(la, 105)) == 0)
# 6. hinge cover robustness (info)
cov = top_case ^ box(x0, x1, AY - 12, AY + 1, g["H"], 30)
print(f"INFO copri-asse: sezione orizzontale minima " +
      f"{min((cov ^ box(x0, x1, AY - 12, AY + 1, z - 0.05, z + 0.05)).volume()/0.1 for z in (10.5, 11.5, 12.5, 13.5, 14.2, 15.0)):.0f} mm2 per aggancio")
if not FAST:
    # 7. insertion from above (springs, keys, trackpad)
    def sweep(m, h=25.0): return union([m.translate((0, 0, dz)) for dz in np.arange(0, h, 0.25)])
    bad = [i for i, c in enumerate(g["combs_kb"] + g["combs_tp"]) if ov(sweep(c), bottom) > 1e-3]
    check("molle si infilano dall'alto", not bad, bad)
    bad = [g["keys"][i]["lab"] for i, k in enumerate(g["keycaps"]) if ov(sweep(k.translate((0, 0, REST_UP))), bottom) > 1e-3]
    check("tasti si infilano dall'alto", not bad, bad)
    # 8. top skin of the top case >= 0.6 mm everywhere (slits over pockets)
    import trimesh
    from collections import defaultdict
    me = top_case.to_mesh(); t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts)
    xs, ys = np.meshgrid(np.arange(0.5, g["W"], 0.7), np.arange(0.5, g["DB"], 0.7))
    o = np.stack([xs.ravel(), ys.ravel(), np.full(xs.size, 40.0)], 1)
    loc, ri, _ = t.ray.intersects_location(o, np.tile([0, 0, -1.0], (len(o), 1)), multiple_hits=True)
    h = defaultdict(list)
    for p, r in zip(loc, ri): h[r].append(p[2])
    thin = [r for r, zz in h.items() if (lambda z: len(z) >= 2 and z[0] >= 9.5 and z[0] - z[1] < 0.6)(sorted(set(np.round(zz, 4)), reverse=True))]
    check("pelle superiore del piano >= 0.6 mm", not thin, f"{len(thin)} punti sottili")
print("\nRISULTATO:", "TUTTO OK" if not fails else "FALLITI: " + ", ".join(fails))
sys.exit(1 if fails else 0)
