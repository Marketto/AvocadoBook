"""TEST 20: realistic USB-C port (8.5 x 2.75 stadium, thin 0.4 mm step) cut from the v26 base."""
import sys, os, numpy as np, trimesh
sys.argv = ["x"]
import os
_SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(_SRC), "build", "tests") + "/"; os.makedirs(OUT, exist_ok=True)
_g = os.path.join(_SRC, "genera_laptop.py"); __file__ = _g; exec(compile(open(_g).read().split("# ================= checks")[0], _g, "exec"), globals())
sys.path.insert(0, _SRC); import gruppi_3mf
yu = DB*0.62
cut = box(-1, 16, yu - 11, yu + 11, -1, 100)
piece = clean(bottom ^ cut)
assert len(piece.decompose()) == 1
me = piece.simplify(1e-3).to_mesh()
t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)
t.apply_translation((130 - (t.bounds[0][0] + t.bounds[1][0])/2, 130 - (t.bounds[0][1] + t.bounds[1][1])/2, -t.bounds[0][2]))
assert t.is_watertight
name = "TEST_20_porta_usbc"
gruppi_3mf.write(OUT + name + ".3mf", {"fondo_porta_usbc": t}, name)
print(name, t.extents.round(1), f"{t.volume/1000:.1f} cm3")
