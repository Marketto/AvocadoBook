"""Previews. Usage: python tools/render.py [preview|section|bottom|all] [out_dir=build/img]
preview: laptop from 4 views (open/closed); section: hinge cross-section at x=56; bottom: underside text close-up."""
import os, sys, numpy as np, trimesh
sys.path.insert(0, os.path.dirname(__file__))
from rast import view
from PIL import Image
from _model import load, ROOT
what = sys.argv[1] if len(sys.argv) > 1 else "all"
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "build", "img"); os.makedirs(out, exist_ok=True)
g = load()
tm = lambda m: (lambda me: trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False))(m.to_mesh())
GREY, BLACK, WHITE = np.array((.62, .63, .65)), np.array((.08, .08, .09)), np.array((.97, .97, .97))
parts = [(g["bottom"], GREY), (g["bottom_text"], BLACK), (g["top_case"], GREY), (g["trackpad"].translate((0, 0, g["REST_UP"])), GREY),
         (g["keycaps_m"].translate((0, 0, g["REST_UP"])), BLACK), (g["letters_m"].translate((0, 0, g["REST_UP"])), WHITE)]
lidp = [(g["lid"], GREY), (g["screen"], BLACK), (g["logo"], WHITE), (g["frame"], BLACK)]
if what in ("preview", "all"):
    O = [(tm(m), c) for m, c in parts] + [(tm(g["rot_lid"](m, 105)), c) for m, c in lidp]
    C = [(tm(m), c) for m, c in parts + lidp]
    img = np.vstack([np.hstack([view(O, 28, -30, 640), view(O, 22, 150, 640)]), np.hstack([view(C, 30, -35, 640), view(O, 75, 0, 640)])])
    Image.fromarray(img).save(os.path.join(out, "anteprima.png")); print("anteprima.png")
if what in ("section", "all"):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 5), dpi=150)
    for m, col in ((g["bottom"], "#9a9a9a"), (g["top_case"], "#d08c4c"), (g["lid"], "#8a9bb5")):
        s = tm(m).section(plane_origin=(56, 0, 0), plane_normal=(1, 0, 0))
        if s is not None:
            for e in s.discrete: ax.fill(e[:, 1], e[:, 2], color=col, ec="k", lw=0.5)
    ax.set_xlim(148, 177); ax.set_ylim(0, 18); ax.set_aspect("equal"); ax.set_title("Cerniera, sezione x=56 (arancio = piano)")
    fig.savefig(os.path.join(out, "sezione_cerniera.png"), bbox_inches="tight"); print("sezione_cerniera.png")
if what in ("bottom", "all"):
    b = g["_dii"].bounds(); clip = g["box"](b[0] - 4, b[2] + 4, b[1] - 3, b[3] + 3, -1, 2.0)
    ms = []
    for m, c in ((g["bottom"] ^ clip, GREY), (g["bottom_text"], BLACK)):
        t = tm(m); t.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [0, 1, 0])); ms.append((t, c))
    im = Image.fromarray(view(ms, 58, 0, 1100)); bb = im.convert("L").point(lambda v: 255 if v < 240 else 0).getbbox()
    im.crop(bb).save(os.path.join(out, "fondo_scritta.png")); print("fondo_scritta.png")
