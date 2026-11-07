"""Checks the EXPORTED files (not the model): every STL closed, project structure as ACnext wants it.
Usage: python tools/check_exports.py [print_dir=build/print]"""
import os, sys, glob, json, re, zipfile, trimesh
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "print")
bad = []
for f in sorted(glob.glob(os.path.join(d, "*.stl"))):
    t = trimesh.load(f)
    n = len(t.split(only_watertight=False))
    print(f"{os.path.basename(f):38s} chiuso={t.is_watertight} corpi={n}")
    if not t.is_watertight: bad.append(f)
proj = glob.glob(os.path.join(d, "*progetto*.3mf"))[0]
z = zipfile.ZipFile(proj); cfg = z.read("Metadata/model_settings.config").decode(); st = json.loads(z.read("Metadata/project_settings.config"))
plates = re.findall(r'<plate>.*?plater_name" value="([^"]+)".*?</plate>', cfg)
objs = re.findall(r'<object id="\d+"><metadata key="name" value="([^"]+)"', cfg)
print("piatti:", plates); print("oggetti:", len(objs), "(deve essere 1 per piatto)")
if len(objs) != len(plates): bad.append("un oggetto per piatto")
print("modificatori:", cfg.count("modifier_part"), "(2 attesi: copri-asse pieni)")
temps = {k: v for k, v in st.items() if k.startswith("nozzle_temperature") and "range" not in k}
print("temperature ugello:", temps)
if len({tuple(v) for v in temps.values()}) != 1: bad.append("temperature non allineate tra i tipi di ugello")
print("\nRISULTATO:", "OK" if not bad else "PROBLEMI: " + ", ".join(map(str, bad)))
sys.exit(1 if bad else 0)
