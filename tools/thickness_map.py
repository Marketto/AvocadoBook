"""Solid thickness map from the underside of a part (where can we engrave/cut without breaking into cavities?).
Usage: python tools/thickness_map.py [bottom|top_case] [x0 x1 y0 y1 step]   -> build/img/spessore_<part>.png + ASCII map (# = >=1.6 mm)"""
import os, sys, numpy as np, trimesh
from collections import defaultdict
sys.path.insert(0, os.path.dirname(__file__))
from _model import load, ROOT
part = sys.argv[1] if len(sys.argv) > 1 else "bottom"
args = [float(v) for v in sys.argv[2:7]] if len(sys.argv) > 6 else None      # read before load(): it resets sys.argv
g = load(); m = g[part]; me = m.to_mesh(); t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts)
x0, x1, y0, y1, s = args if args else (0, g["W"], 0, g["DB"], 2.0)
xs, ys = np.meshgrid(np.arange(x0, x1, s), np.arange(y0, y1, s))
o = np.stack([xs.ravel(), ys.ravel(), np.full(xs.size, -5.0)], 1)
loc, ri, _ = t.ray.intersects_location(o, np.tile([0, 0, 1.0], (len(o), 1)), multiple_hits=True)
h = defaultdict(list)
for p, r in zip(loc, ri): h[r].append(p[2])
th = np.zeros(len(o))
for r, zz in h.items():
    zz = sorted(set(np.round(zz, 3)))
    if zz[0] < 0.05: th[r] = (zz[1] if len(zz) > 1 else 99) - zz[0]
th = th.reshape(xs.shape)
for j in range(th.shape[0] - 1, -1, -max(1, th.shape[0]//40)):
    print(f"y={ys[j, 0]:6.1f} " + "".join("#" if v >= 1.6 else "." for v in th[j, ::max(1, th.shape[1]//100)]))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
os.makedirs(os.path.join(ROOT, "build", "img"), exist_ok=True)
plt.figure(figsize=(10, 7)); plt.imshow(np.clip(th, 0, 4), origin="lower", extent=[x0, x1, y0, y1]); plt.colorbar(label="mm pieni dal fondo")
plt.savefig(os.path.join(ROOT, "build", "img", f"spessore_{part}.png"), dpi=80)
