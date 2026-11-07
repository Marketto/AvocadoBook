"""Export the print plates (3MF, one per plate), the single STLs and the multi-plate project from build/parts.pkl
(written by genera_laptop.py; parts already in print orientation). Usage: python src/esporta_piatti.py [out_dir]"""
import pickle, numpy as np, trimesh, sys, os
_SRC = os.path.dirname(os.path.abspath(__file__)); _ROOT = os.path.dirname(_SRC)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_ROOT, "build", "print")
printp, closed, opened = pickle.load(open(os.path.join(_ROOT, "build", "parts.pkl"), "rb"))
BED = 260.0
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orecchie import add_ears, add_breakaway_ears, add_corner_ears
from manifold3d import Manifold, Mesh, CrossSection


def with_ears(t):
    """trimesh (print pose) -> same part + built-in anti-lift ears (only on the outside of its hull)."""
    m = add_breakaway_ears(Manifold(Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))).simplify(1e-3)
    me = m.to_mesh()
    out = trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)
    assert out.is_watertight
    return out
REN = {"C_supporto_staccabile": "C_supporto_PLA", "C_cornice": "E_cornice"}


def centre(objs):
    """objs: {name: mesh} -> translated copies centred on the bed (xy)."""
    b = np.vstack([m.bounds for m in objs.values()])
    off = np.array([BED/2 - (b[:, 0].min() + b[:, 0].max())/2, BED/2 - (b[:, 1].min() + b[:, 1].max())/2, -b[:, 2].min()])
    out = {n: m.copy().apply_translation(off) for n, m in objs.items()}
    b = np.vstack([m.bounds for m in out.values()])
    assert b[:, :2].min() >= 0 and b[:, :2].max() <= BED, f"fuori piatto {b[:, :2].min()} {b[:, :2].max()}"
    return out


def stack_y(objs, gap):
    """Place objects one above the other (y), each centred in x, in the given order."""
    y, out = 0.0, {}
    for n, m in objs.items():
        c = m.copy(); b = c.bounds
        c.apply_translation((-(b[0][0] + b[1][0])/2, y - b[0][1], 0))
        out[n] = c; y += b[1][1] - b[0][1] + gap
    return out


def cleaned(t):
    """Merge near-coincident vertices (< 1 micron): STL readers otherwise split the mesh."""
    m = Manifold(Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32))).simplify(1e-3)
    me = m.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)


SHEET_T, SHEET_M = 0.4, 3.0     # v24b: springs printed on a 0.4 mm PLA sheet (test 17b: no ears, they pop off clean)


def on_pla(t):
    """spring (print pose) -> (spring lifted by SHEET_T, PLA sheet = hull of its footprint + 3 mm)."""
    m = Manifold(Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
    import manifold3d as mf
    sheet = Manifold.extrude(m.slice(0.1).hull().offset(SHEET_M, join_type=mf.JoinType.Round, circular_segments=24), SHEET_T)
    tt = lambda q: (lambda me: trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False))(q.simplify(1e-3).to_mesh())
    return tt(m.translate((0, 0, SHEET_T))), tt(sheet)


P = {n: cleaned(printp[n]) for n in printp if not n.startswith("F_molle_S")}


def with_corner_ears(t, hinge_ears=False):
    """v26e/f: breakaway anti-warp ears on big thin flat parts (corners, along y so the width does not grow;
    lid: also two on the hinge edge where it lifted)."""
    m = Manifold(Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
    b = m.bounding_box(); x0, y0, x1, y1 = b[0], b[1], b[3], b[4]
    d = 0.7071
    foot = m.slice(0.1)
    fv = np.vstack([np.asarray(q) for q in foot.to_polygons()])
    pts, dirs = [], []
    for xx in (x0 + 8.0, x1 - 8.0):          # near each corner, far enough from the side that the width does not grow
        pb = (foot ^ CrossSection.square((1.0, y1 - y0)).translate((xx - 0.5, y0))).bounds()
        pts += [(xx, pb[1]), (xx, pb[3])]; dirs += [(0, -1), (0, 1)]
    if hinge_ears:
        for xe in (30.0, b[3] - b[0] - 30.0):
            xx = x0 + xe
            pb = (foot ^ CrossSection.square((1.0, y1 - y0)).translate((xx - 0.5, y0))).bounds()
            pts.append((xx, pb[1])); dirs.append((0, -1))
    mm = add_corner_ears(m, pts, dirs).simplify(1e-3)
    me = mm.to_mesh()
    return trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False)


P["C_coperchio_corpo"] = with_corner_ears(printp["C_coperchio_corpo"], hinge_ears=True)
P["B_piano"] = with_corner_ears(printp["B_piano"])
P["C_cornice"] = with_corner_ears(printp["C_cornice"])
SPR = {n: on_pla(printp[n]) for n in printp if n.startswith("F_molle_S")}
# plate 7 (v25): trackpad face down with a built-in support under the overhanging flange and fins:
# grey PETG ring + 2 layers of PLA on top (PLA does not bond to PETG -> clean underside, no strings)
def trackpad_plate():
    import manifold3d as mf
    t = P["B_trackpad"]
    m = Manifold(Mesh(np.asarray(t.vertices, np.float32), np.asarray(t.faces, np.uint32)))
    zf = None
    for z in np.arange(0.1, 6.0, 0.1):            # flange underside = first height where the outline grows
        if m.slice(z).hull().area() > m.slice(0.1).hull().area() + 50:
            zf = round(z - 0.1, 1); break
    body = m.slice(0.1)
    # v25c: support ENTIRELY in PLA (a PETG body is hard to remove: test 18a); 0.25 mm from the walls is enough,
    # PLA does not bond to PETG
    over = m.slice(zf + 0.3).hull() - body.offset(0.25, join_type=mf.JoinType.Miter)
    pla = Manifold.extrude(over, zf)
    tt = lambda q: (lambda me: trimesh.Trimesh(me.vert_properties[:, :3], me.tri_verts, process=False))(q.simplify(1e-3).to_mesh())
    print(f"   trackpad: sporgenza a {zf} mm dal piatto -> supporto tutto in PLA 0-{zf}")
    return {"B_trackpad": t, "B_trackpad_SUPPORTO_DA_STACCARE_PLA": tt(pla)}


# plate 6: long strips stacked at the front, the two short trackpad strips at the back right
# (back-left corner free for the purge tower: PETG + PLA = 2 materials)
def spring_plate():
    out, y = {}, 0.0
    names = sorted(n for n in SPR if "fila" in n)
    for n in names:
        sp, sh = SPR[n]
        b = sh.bounds
        d = (-b[1][0], y - b[0][1], 0)
        out[n] = sp.copy().apply_translation(d); out["PLA_" + n] = sh.copy().apply_translation(d)
        y += b[1][1] - b[0][1] + 2.0
    for i, n in enumerate(sorted(n for n in SPR if "trackpad" in n)):
        sp, sh = SPR[n]
        b = sh.bounds
        d = (-b[1][0], y - b[0][1], 0)
        out[n] = sp.copy().apply_translation(d); out["PLA_" + n] = sh.copy().apply_translation(d)
        y += b[1][1] - b[0][1] + 2.0
    springs = {n: m for n, m in out.items() if not n.startswith("PLA_")}
    springs["F_fogli_PLA"] = trimesh.util.concatenate([m for n, m in out.items() if n.startswith("PLA_")])
    return springs


plates = {
    "1_fondo": {"A_fondo": P["A_fondo"], "A_fondo_scritta_nera": P["A_fondo_scritta_nera"]},   # v27d: black text inlay
    # v26n: the hinge lock keys broke when the plate was flexed: solid (100 %) with more walls via a modifier
    "2_piano": {"B_piano": P["B_piano"], **{f"MOD_cerniera_piena_{i + 1}": trimesh.creation.box(bounds=[[xa, 160.5, 0.0], [xb, 169.55, 8.8]])
                                          for i, (xa, xb) in enumerate([(38.5, 73.5), (176.5, 211.5)])}},
    "7_trackpad": {"B_trackpad": P["B_trackpad"]},          # v26: self-supporting 45-degree flange, no support
    "3_coperchio": {n: P[n] for n in ("C_coperchio_corpo", "C_supporto_staccabile", "C_coperchio_schermo", "C_coperchio_logo")},
    "4_tasti": {"D_tasti": P["D_tasti"], "D_lettere": P["D_lettere"]},
    "5_cornice_schermo": {"C_cornice": P["C_cornice"]},
    "6_molle_S": spring_plate(),
}
os.makedirs(OUT, exist_ok=True)
MULTI = ("1_fondo", "3_coperchio", "4_tasti", "6_molle_S")          # multicolour plates: keep the back-left corner free for the purge tower
TOWER_FREE = (0.0, 85.0, 196.0, BED)        # back-left area kept empty for the purge tower (lid ears need 4 mm more)


def free_corner(objs, margin=5.0):
    """Push everything to the front-right corner of the bed and check the back-left area is empty."""
    b = np.vstack([m.bounds for m in objs.values()])
    off = np.array([BED - margin - b[:, 0].max(), margin - b[:, 1].min(), -b[:, 2].min()])
    out = {n: m.copy().apply_translation(off) for n, m in objs.items()}
    x0, x1, y0, y1 = TOWER_FREE
    for n, m in out.items():
        v = m.vertices
        assert not np.any((v[:, 0] > x0) & (v[:, 0] < x1) & (v[:, 1] > y0) & (v[:, 1] < y1)), f"{n} occupa l'angolo della torre"
    return out


ALL, MODS = [], {}
for pn, objs in plates.items():
    objs = free_corner(objs) if pn in MULTI else centre(objs)
    for n_, m_ in objs.items():      # drop degenerate slivers (zero-volume triangle patches left by the ear unions)
        if n_.startswith("MOD_"): continue
        cs_ = m_.split(only_watertight=False)
        if len(cs_) > 1 and min(abs(c.volume) for c in cs_) < 1e-3:
            keep = [c for c in cs_ if abs(c.volume) >= 1e-3]
            objs[n_] = keep[0] if len(keep) == 1 else trimesh.util.concatenate(keep)
        t2 = objs[n_].copy(); t2.merge_vertices(); t2.update_faces(t2.area_faces > 1e-9); t2.remove_unreferenced_vertices()
        if t2.is_watertight and len(t2.split(only_watertight=False)) <= len(objs[n_].split(only_watertight=False)):
            objs[n_] = t2      # same solid without zero-area triangles (they become loose slivers in the STL)
    mods = [n for n in objs if n.startswith("MOD_")]
    if mods:
        MODS[pn] = [(n, objs.pop(n), {"sparse_infill_density": "100%", "wall_loops": "6", "top_shell_layers": "8"}) for n in mods]
    ALL.append((pn, {REN.get(n, n): m for n, m in objs.items()}))
    sc = trimesh.Scene()
    for n, m in objs.items():
        nn = REN.get(n, n)
        assert m.is_watertight, nn
        sc.add_geometry(m, node_name=nn, geom_name=nn)
        m.export(os.path.join(OUT, nn + ".stl"))
    import gruppi_3mf
    gr, fl = gruppi_3mf.write(os.path.join(OUT, pn + ".3mf"), {REN.get(n, n): m for n, m in objs.items()}, pn)
    ext = np.ptp(np.vstack([m.bounds for m in objs.values()]), 0).round(1)
    print(f"{pn:20s} {ext}  " + " | ".join(f"{g}: {len(v)}" for g, v in gr.items()) + (f"   [sopra il piatto: {fl} -> anche _oggetto_unico]" if fl else ""))

# one project file with all the plates
import progetto_unico
ORDER = ["1_fondo", "2_piano", "3_coperchio", "4_tasti", "5_cornice_schermo", "6_molle_S", "7_trackpad"]
import json
ST = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "impostazioni_kobrax_utente.json")))
# user's own Kobra X project settings (slots: 1 PETG grey, 2 PETG white, 3 PETG black, 4 PLA red) + values of the print sheet
ST.update({
    "print_settings_id": "0.20mm Standard @Anycubic Kobra X 0.4 nozzle", "layer_height": "0.2", "initial_layer_print_height": "0.2",
    "wall_loops": "4", "top_shell_layers": "5", "bottom_shell_layers": "4", "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid", "wall_generator": "arachne", "elefant_foot_compensation": "0.15",
    "enable_support": "0", "brim_type": "no_brim", "reduce_crossing_wall": "1",
    "flush_into_infill": "1", "flush_multiplier": "1", "enable_prime_tower": "1", "prime_tower_width": "35",
    "wipe_tower_x": ["15"]*4, "wipe_tower_y": ["208"]*4,
    # PETG and PLA together: every temperature must fall inside the range of the others (PETG 220-250, PLA 190-230)
    # -> common window 220-230 (slicer warning on plates with PLA)
    "nozzle_temperature": ["230", "230", "230", "225"], "nozzle_temperature_initial_layer": ["230", "230", "230", "225"],
    # v27f: the per-nozzle-type copies too (ACnext warned: PLA on the HS nozzle was 205 °C, outside the PETG range)
    **{k + sfx: ["230", "230", "230", "225"] for k in ("nozzle_temperature", "nozzle_temperature_initial_layer") for sfx in ("_BRASS", "_HS")},
    # v26e: bed 80 for PETG (the lid warped at 70), less part cooling on PETG
    "textured_plate_temp": ["80", "80", "80", "70"], "textured_plate_temp_initial_layer": ["80", "80", "80", "70"],
    "hot_plate_temp": ["80", "80", "80", "70"], "hot_plate_temp_initial_layer": ["80", "80", "80", "70"],
    "fan_min_speed": ["10", "10", "10", "60"], "fan_max_speed": ["30", "30", "30", "100"], "close_fan_the_first_x_layers": ["5", "5", "5", "1"],
    # quality before time (user's choice): slower visible walls / top surfaces / first layer (= visible face of the
    # parts printed face down), lower accelerations, precise outer wall
    "outer_wall_speed": "60", "inner_wall_speed": "120", "top_surface_speed": "60", "gap_infill_speed": "80",
    "initial_layer_speed": "25", "initial_layer_infill_speed": "50",
    "default_acceleration": "4000", "outer_wall_acceleration": "1000", "top_surface_acceleration": "1000",
    "initial_layer_acceleration": "500", "precise_outer_wall": "1",
})
OVR = {"1_fondo": {"brim_type": "no_brim"},   # v26b: no brim (PETG brim on textured PEI was hard to remove)
       # v26c: deck came out rough (pillowing over 20% infill + ironing on an uneven skin): more top layers, denser
       # infill under the deck, slower top surface, ironing with a bit more flow
       "2_piano": {"sparse_infill_density": "30%", "top_shell_layers": "8", "top_surface_speed": "40",
                   # v26k: PETG ironing dragged flakes over the deck (photo): no ironing, clean monotonic top
                   "ironing_type": "no ironing", "top_surface_pattern": "monotonicline", "top_surface_line_width": "0.4"},
       "3_coperchio": {"sparse_infill_density": "20%"},
       "4_tasti": {"wall_loops": "3", "sparse_infill_density": "20%"}, "5_cornice_schermo": {"wall_loops": "3"},
       "6_molle_S": {"sparse_infill_density": "100%", "wall_loops": "2"}, "7_trackpad": {"sparse_infill_density": "20%"}}
progetto_unico.write(os.path.join(OUT, "AvocadoBook_progetto.3mf"), sorted(ALL, key=lambda t: ORDER.index(t[0])), ST, OVR, MODS)
print("progetto unico: AvocadoBook_progetto.3mf")
