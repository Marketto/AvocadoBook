"""One project 3MF with several plates, in the exact structure written by Anycubic Slicer Next 2.0
(sample saved by the user: 4 plates with a cube). Per plate: one object per material group, the pieces as named
parts with the filament slot preset (1 grey, 2 black, 3 white, 4 PLA). Objects are centred on their own origin
and placed with the build transform; plates are spaced 314.4 mm (x) and 328.8 mm (y), columns = Bambu rule.
A material that starts above the bed shares the object of the material it rests on (cannot be dropped)."""
import zipfile, math, uuid, numpy as np
from gruppi_3mf import material, GROUPS

SLOT = {"grigio": 1, "bianco": 2, "nero": 3, "PLA": 4}   # user's ACE: 1 PETG grey, 2 PETG white, 3 PETG black, 4 PLA red
LABEL = dict((k, g) for g, k in GROUPS)
STRIDE_X, STRIDE_Y = 314.4, 328.8            # from the Anycubic Slicer Next sample (Kobra X)
NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')


def _cols(n):
    v = math.sqrt(n); r = round(v)
    return int(r + 1 if v > r else r)


def _u():
    return str(uuid.uuid4())


def write(path, plates, settings=None, overrides=None, modifiers=None):
    """plates: list of (plate_name, {piece_name: trimesh in plate coordinates 0..260}).
    modifiers: {plate_name: [(name, trimesh in plate coordinates, {setting: value})]} -> modifier parts (local
    settings, e.g. 100 % infill) added to the plate's first object."""
    files, main_obj, build, cfg_obj, cfg_plate, assemble, rels = {}, [], [], [], [], [], []
    oid = 1
    cols = _cols(len(plates))
    for pi, (pname, parts) in enumerate(plates):
        ox, oy = (pi % cols)*STRIDE_X, -(pi // cols)*STRIDE_Y
        groups = {}
        for n, m in parts.items():
            groups.setdefault(material(n), []).append((n, m))
        zr = {k: (min(m.bounds[0][2] for _, m in v), max(m.bounds[1][2] for _, m in v)) for k, v in groups.items()}
        # v27e: ONE object per plate, one part per material (ACnext warned that separate per-colour objects touching
        # each other - logo inlay, key legends, black text - were "too close, collisions may occur")
        host0 = min(groups, key=lambda h: (zr[h][0] > 0.01, [g for _, g in GROUPS].index(h)))
        objs = {host0: list(groups)}
        inst = []
        for host, mats in objs.items():
            mats = [g for _, g in GROUPS if g in mats]
            import trimesh as _tm
            pieces = [(LABEL[k] + " – " + ", ".join(n for n, _ in groups[k]), _tm.util.concatenate([m for _, m in groups[k]]), k) for k in mats]
            allv = np.vstack([m.vertices for _, m, _ in pieces])
            c = (allv.min(0) + allv.max(0))/2
            fname = f"/3D/Objects/piatto{pi + 1}_{SLOT[host]}.model"
            mesh_xml, comps, part_cfg = [], [], []
            mods = (modifiers or {}).get(pname, []) if not inst else []
            for n, m, k in pieces + [(mn, mm, None) for mn, mm, _ in mods]:
                v = np.asarray(m.vertices) - c; f = np.asarray(m.faces)
                vs = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{cc:.4f}"/>' for a, b, cc in v)
                ts = "".join(f'<triangle v1="{a}" v2="{b}" v3="{d}"/>' for a, b, d in f)
                mesh_xml.append(f'<object id="{oid}" p:UUID="{_u()}" type="model"><mesh><vertices>{vs}</vertices><triangles>{ts}</triangles></mesh></object>')
                comps.append(f'<component p:path="{fname}" objectid="{oid}" p:UUID="{_u()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>')
                if k is None:      # modifier part: no filament, only local settings
                    ms = dict((mn, st) for mn, _, st in mods)[n]
                    part_cfg.append(f'<part id="{oid}" subtype="modifier_part"><metadata key="name" value="{n}"/>'
                                    f'<metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>' +
                                    "".join(f'<metadata key="{a}" value="{b}"/>' for a, b in ms.items()) + '</part>')
                else:
                    part_cfg.append(f'<part id="{oid}" subtype="normal_part"><metadata key="name" value="{n}"/>'
                                    f'<metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>'
                                    f'<metadata key="extruder" value="{SLOT[k]}"/></part>')
                oid += 1
            files[fname] = (f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" {NS}>'
                            '<metadata name="BambuStudio:3mfVersion">1</metadata><resources>' + "".join(mesh_xml) + '</resources><build/></model>')
            rels.append(fname)
            main_obj.append(f'<object id="{oid}" p:UUID="{_u()}" type="model"><components>{"".join(comps)}</components></object>')
            t = f"1 0 0 0 1 0 0 0 1 {c[0] + ox:.4f} {c[1] + oy:.4f} {c[2]:.4f}"
            build.append(f'<item objectid="{oid}" p:UUID="{_u()}" transform="{t}" printable="1"/>')
            assemble.append(f'<assemble_item object_id="{oid}" instance_id="0" transform="{t}" offset="0 0 0" />')
            label = " + ".join(LABEL[k] for k in mats)   # object name: plate + materials
            ov = "".join(f'<metadata key="{k}" value="{v}"/>' for k, v in ((overrides or {}).get(pname, {})).items())
            cfg_obj.append(f'<object id="{oid}"><metadata key="name" value="{pname} - {label}"/>'
                           f'<metadata key="extruder" value="{SLOT[host]}"/>' + ov + "".join(part_cfg) + '</object>')
            inst.append(oid); oid += 1
        mi = "".join(f'<model_instance><metadata key="object_id" value="{i}"/><metadata key="instance_id" value="0"/>'
                     f'<metadata key="identify_id" value="{1000 + i}"/></model_instance>' for i in inst)
        cfg_plate.append(f'<plate><metadata key="plater_id" value="{pi + 1}"/><metadata key="plater_name" value="{pname}"/>'
                         f'<metadata key="locked" value="false"/>{mi}</plate>')
    main = (f'<?xml version="1.0" encoding="UTF-8"?><model unit="millimeter" xml:lang="en-US" {NS}>'
            '<metadata name="Application">BambuStudio-2.0.0.3</metadata><metadata name="BambuStudio:3mfVersion">1</metadata>'
            '<metadata name="Title">Laptop giocattolo</metadata>'
            '<resources>' + "".join(main_obj) + f'</resources><build p:UUID="{_u()}">' + "".join(build) + '</build></model>')
    cfg = ('<?xml version="1.0" encoding="UTF-8"?><config>' + "".join(cfg_obj) + "".join(cfg_plate) +
           '<assemble>' + "".join(assemble) + '</assemble></config>')
    model_rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
                  "".join(f'<Relationship Target="{f}" Id="rel-{i + 1}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>' for i, f in enumerate(rels)) +
                  '</Relationships>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="png" ContentType="image/png"/><Default Extension="gcode" ContentType="text/x.gcode"/></Types>')
    rootrels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    info = ('<?xml version="1.0" encoding="UTF-8"?><config><header><header_item key="X-ACNext-Client-Type" value="slicer"/>'
            '<header_item key="X-ACNext-Client-Version" value="2.0.0.3 20260904033713"/></header></config>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rootrels)
        z.writestr("3D/3dmodel.model", main); z.writestr("3D/_rels/3dmodel.model.rels", model_rels)
        for f, x in files.items():
            z.writestr(f.lstrip("/"), x)
        z.writestr("Metadata/model_settings.config", cfg); z.writestr("Metadata/slice_info.config", info)
        if settings is not None:
            import json
            z.writestr("Metadata/project_settings.config", json.dumps(settings, indent=4, ensure_ascii=False))
    return cols
