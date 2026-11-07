"""Builds the annotation page (the user draws on an image, the page stores the drawing for Claude).
Usage: python tools/make_editor.py <image.png> [out.html=build/editor/segna.html]
Then publish out.html with the Artifact tool, capabilities {"assets": {}, "db": {}} (first publish only).
Drawings land in db collection "segni" (fields asset_id, url, nota, quando): read the newest, then fetch the asset."""
import base64, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, ".claude", "skills", "avb-sketch-feedback", "editor_template.html")).read()
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "build", "editor", "segna.html")
os.makedirs(os.path.dirname(out), exist_ok=True)
open(out, "w").write(tpl.replace("__IMG__", base64.b64encode(open(sys.argv[1], "rb").read()).decode(), 1))
print(out)
