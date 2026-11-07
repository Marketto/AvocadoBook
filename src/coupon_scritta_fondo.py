"""TEST 28: AvocadoBook + Colosseum + "Designed in Italy" debossed in the underside of the base (2 mm slab)."""
import sys, trimesh
sys.argv = ["x"]
import os
_SRC = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(os.path.dirname(_SRC), "build", "tests") + "/"; os.makedirs(OUT, exist_ok=True)
_g = os.path.join(_SRC, "genera_laptop.py"); __file__ = _g; exec(compile(open(_g).read().split("# ================= checks")[0], _g, "exec"), globals())
sys.path.insert(0, _SRC); import gruppi_3mf
b = _dii.bounds()
piece = bottom ^ box(b[0] - 4, b[2] + 4, b[1] - 3, b[3] + 3, -1, 2.0)
assert len(piece.decompose()) == 1, len(piece.decompose())
print("sovrapposizione scritta/fondo:", round((bottom_text ^ bottom).volume(), 4))
tm_ = lambda m: (lambda me: trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False))(m.to_mesh())
t, tx = tm_(piece), tm_(bottom_text)
off = (130 - (t.bounds[0][0] + t.bounds[1][0])/2, 70 - (t.bounds[0][1] + t.bounds[1][1])/2, -t.bounds[0][2])   # front of the bed: top-left free for the tower
t.apply_translation(off); tx.apply_translation(off)
assert t.is_watertight and tx.is_watertight
name = "TEST_28_fondo_avocadobook"
gruppi_3mf.write(OUT + name + ".3mf", {"fondo_grigio": t, "A_fondo_scritta_nera": tx}, name)
print(name, t.extents.round(1), f"{t.volume/1000:.1f} cm3")
