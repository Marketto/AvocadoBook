"""TEST 27: hinge cover v26u + keyboard ramp that keeps the hook pockets closed cut from the piano, to try on the printed base."""
import sys, trimesh
sys.argv = ["x"]
import os
_SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(_SRC), "build", "tests") + "/"; os.makedirs(OUT, exist_ok=True)
_g = os.path.join(_SRC, "genera_laptop.py"); __file__ = _g; exec(compile(open(_g).read().split("# ================= checks")[0], _g, "exec"), globals())
sys.path.insert(0, _SRC); import gruppi_3mf
x0, x1 = KN[0]
piece = clean(top_case ^ box(x0 - 6, x1 + 6, 154.0, DB + 1, -1, 100))
assert len(piece.decompose()) == 1, len(piece.decompose())
me = piece.to_mesh()
t = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)
t.apply_translation((130 - (t.bounds[0][0] + t.bounds[1][0])/2, 130 - (t.bounds[0][1] + t.bounds[1][1])/2, -t.bounds[0][2]))
assert t.is_watertight
name = "TEST_27_cerniera_senza_fessure"
import progetto_unico
progetto_unico.write(OUT + name + ".3mf", [(name, {"piano_aggancio_cerniera": t})], None,
                     {name: {"sparse_infill_density": "100%", "wall_loops": "6", "top_shell_layers": "8"}})
print(name, t.extents.round(1), f"{t.volume/1000:.1f} cm3")
