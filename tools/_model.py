"""Shared loader: runs src/genera_laptop.py up to its '# === checks' marker and returns the namespace
(all solids: bottom, top_case, lid, frame, keycaps_m, trackpad, combs_kb, ...; helpers: box, xcyl, rot_lid, ...).
Slow (~1-3 min): load once per tool run."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
GEN = os.path.join(SRC, "genera_laptop.py")


def load():
    sys.argv = ["x"]
    sys.path.insert(0, SRC)
    ns = {"__file__": GEN, "__name__": "avb_model"}
    code = open(GEN).read().split("# ================= checks")[0]
    exec(compile(code, GEN, "exec"), ns)
    return ns
