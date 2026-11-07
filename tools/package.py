"""Builds the upload package for Maker Online / MakerWorld: build/package/AvocadoBook_package.zip
(project 3MF, plates, STL, PDFs IT+EN, images, descriptions) and regenerates descriptions/00_TUTTE_LE_LINGUE_da_incollare.txt
from the 12 language files. Usage: python tools/package.py"""
import glob, os, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "descriptions")
flags = {"IT": "🇮🇹 ITALIANO", "EN": "🇬🇧 ENGLISH", "FR": "🇫🇷 FRANÇAIS", "DE": "🇩🇪 DEUTSCH", "ES": "🇪🇸 ESPAÑOL", "PT": "🇵🇹 PORTUGUÊS",
         "NL": "🇳🇱 NEDERLANDS", "PL": "🇵🇱 POLSKI", "ZH": "🇨🇳 中文", "JA": "🇯🇵 日本語", "RU": "🇷🇺 РУССКИЙ", "AR": "🇸🇦 العربية"}
out = ["🥑 AvocadoBook", "🌍 " + " · ".join(flags.values()), ""]
for f in sorted(glob.glob(os.path.join(D, "[01][0-9]_*.txt"))):
    if os.path.basename(f).startswith("00_"): continue
    code = os.path.basename(f).split("_")[1]; lines = open(f).read().splitlines()
    i = next(k for k, l in enumerate(lines) if k > 4 and l.strip() and l.strip() == l.strip().upper())   # DESCRIPTION header
    out += ["━" * 20, flags[code], "━" * 20, lines[4], ""] + lines[i + 1:] + [""]
open(os.path.join(D, "00_TUTTE_LE_LINGUE_da_incollare.txt"), "w").write("\n".join(out))
os.makedirs(os.path.join(ROOT, "build", "package"), exist_ok=True)
zp = os.path.join(ROOT, "build", "package", "AvocadoBook_package.zip")
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for pat in ("print/*.3mf", "print/plates/*.3mf", "print/stl/*.stl", "docs/pdf/*.pdf", "docs/img/*.png", "descriptions/*.txt"):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))):
            z.write(f, os.path.relpath(f, ROOT))
print(zp, os.path.getsize(zp)//1024, "KB")
