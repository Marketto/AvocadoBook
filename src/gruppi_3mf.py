"""Write a 3MF where the parts are grouped by material: one object per material (with the parts as components),
so the slicer shows e.g. '3 BIANCO PETG' and '4 PLA' and the filament is assigned with one click per group."""
import zipfile, os, numpy as np

GROUPS = [("1 GRIGIO PETG", "grigio"), ("2 BIANCO PETG", "bianco"), ("3 NERO PETG", "nero"), ("4 PLA (supporti)", "PLA")]   # = slots of the user's ACE


def material(name):
    n = name.lower()
    if "pla" in n:
        return "PLA"
    if n.startswith(("d_lettere", "c_coperchio_logo", "f_molle")) or "molla" in n or "bianc" in n or "lettera" in n:
        return "bianco"
    if n.startswith(("d_tasti", "c_coperchio_schermo", "c_cornice", "e_cornice", "a_fondo_scritta")) or "tasto" in n and "trackpad" not in n:
        return "nero"
    return "grigio"


def write_single(path, parts, title="laptop"):
    """parts: {name: trimesh} (already placed on the plate).
    v25e: ONE object for the whole plate, with ONE part per material (all pieces of a material merged).
    A separate object per material is NOT safe: the slicer drops every object to the bed, so a group that
    starts above z=0 (springs on the PLA sheets, screen inlay in the lid) would be pushed down into the others."""
    import trimesh
    by = {}
    for name, m in parts.items():
        by.setdefault(material(name), []).append(m)
    res, comp, oid = [], [], 1
    for gname, key in GROUPS:
        if key not in by:
            continue
        m = trimesh.util.concatenate(by[key]) if len(by[key]) > 1 else by[key][0]
        v = np.asarray(m.vertices); f = np.asarray(m.faces)
        vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in v)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
        res.append(f'<object id="{oid}" name="{gname}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        comp.append(oid); oid += 1
    cs = "".join(f'<component objectid="{i}"/>' for i in comp)
    res.append(f'<object id="{oid}" name="{title}" type="model"><components>{cs}</components></object>')
    items = [f'<item objectid="{oid}"/>']
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="it-IT" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + "".join(res) +
             '</resources><build>' + "".join(items) + '</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)
    return {g: [n for n in parts if material(n) == k] for g, k in GROUPS if k in by}



def floating(parts):
    """Materials whose lowest point is above the bed (a slicer may drop that group to z=0)."""
    zmin = {}
    for n, m in parts.items():
        k = material(n); zmin[k] = min(zmin.get(k, 1e9), float(m.bounds[0][2]))
    return [k for k, z in zmin.items() if z > 0.01]


def write(path, parts, title="laptop"):
    """Default (user's rule): one GROUP per material/colour = one object per material with the named pieces as
    components. If a material starts above the bed, also write <name>_oggetto_unico.3mf (single object,
    one part per material) as a safe alternative."""
    res, comp, oid = [], {}, 1
    for name, m in parts.items():
        v = np.asarray(m.vertices); f = np.asarray(m.faces)
        vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in v)
        ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
        res.append(f'<object id="{oid}" name="{name}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
        comp.setdefault(material(name), []).append(oid); oid += 1
    items = []
    for gname, key in GROUPS:
        if key in comp:
            cs = "".join(f'<component objectid="{i}"/>' for i in comp[key])
            res.append(f'<object id="{oid}" name="{gname}" type="model"><components>{cs}</components></object>')
            items.append(f'<item objectid="{oid}"/>'); oid += 1
    _zip(path, res, items)
    fl = floating(parts)
    alt = path[:-4] + "_oggetto_unico.3mf"
    if fl:
        write_single(alt, parts, title)
    elif os.path.exists(alt):
        os.remove(alt)
    return {g: [n for n in parts if material(n) == k] for g, k in GROUPS if k in comp}, fl


def _zip(path, res, items):
    model = ('<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="it-IT" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + "".join(res) +
             '</resources><build>' + "".join(items) + '</build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)
