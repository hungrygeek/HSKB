"""
Engrave text into the top face (front-right) via boolean difference, then export + verify renders.
  blender --background --python engrave_text.py -- <in.stl> <out.stl> <out_prefix> <text> <depth> <cx_off> <cy_off> <width>
cx_off = inward offset from x_max (center X), cy_off = offset from y_min (center Y), width = target text width (mm).
"""
import bpy, bmesh, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT_STL, OUT_PREFIX = argv[0], argv[1], argv[2]
TEXT = argv[3] if len(argv) > 3 else "SSKB"
DEPTH = float(argv[4]) if len(argv) > 4 else 0.4
CXO = float(argv[5]) if len(argv) > 5 else 27.0
CYO = float(argv[6]) if len(argv) > 6 else 9.0
TW = float(argv[7]) if len(argv) > 7 else 32.0

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
case = bpy.context.active_object or bpy.context.selected_objects[0]
co = [v.co for v in case.data.vertices]
mn = [min(c[i] for c in co) for i in range(3)]; mx = [max(c[i] for c in co) for i in range(3)]

# --- build text solid ---
bpy.ops.object.text_add()
txt = bpy.context.active_object
txt.data.body = TEXT
txt.data.align_x = 'CENTER'; txt.data.align_y = 'CENTER'
txt.data.extrude = 1.0                       # 2 mm thick slab (±1 local Z)
bpy.ops.object.convert(target='MESH')
txt = bpy.context.active_object

# scale to target width
tco = [txt.matrix_world @ Vector(c) for c in txt.bound_box]
cur_w = max(p.x for p in tco) - min(p.x for p in tco)
s = TW / cur_w
txt.scale = (s, s, 1.0)
txt.rotation_euler = (0, 0, math.radians(180))   # so it reads upright to the front user

# position over the USER's FRONT-RIGHT border (front = spacebar edge = +Y; user's right = -X)
cx = mn[0] + CXO
cy = mx[1] - CYO
cz = mx[2] - DEPTH + 1.0
txt.location = (cx, cy, cz)
bpy.context.view_layer.update()
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# clean the text solid so the boolean operand is manifold
_tm = txt.data
_tb = bmesh.new(); _tb.from_mesh(_tm)
bmesh.ops.remove_doubles(_tb, verts=_tb.verts, dist=1e-4)
bmesh.ops.recalc_face_normals(_tb, faces=_tb.faces)
_tb.to_mesh(_tm); _tb.free(); _tm.update()

# report text footprint (so we can check it sits on solid border)
tco = [txt.matrix_world @ Vector(c) for c in txt.bound_box]
print(f"DIAG text_bbox x=[{min(p.x for p in tco):.1f},{max(p.x for p in tco):.1f}] "
      f"y=[{min(p.y for p in tco):.1f},{max(p.y for p in tco):.1f}]  case x<= {mx[0]:.1f} y>= {mn[1]:.1f}")

# --- boolean difference (engrave) ---
bpy.context.view_layer.objects.active = case
mod = case.modifiers.new("eng", 'BOOLEAN')
mod.operation = 'DIFFERENCE'; mod.object = txt; mod.solver = 'EXACT'
bpy.ops.object.modifier_apply(modifier="eng")
bpy.data.objects.remove(txt, do_unlink=True)

me = case.data
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.dissolve_degenerate(bm, dist=1e-3, edges=bm.edges)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-3)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.to_mesh(me); bm.free(); me.update()
bm = bmesh.new(); bm.from_mesh(me)
nonman = sum(1 for e in bm.edges if not e.is_manifold); bm.free()
print(f"DIAG after_verts={len(me.vertices)} after_faces={len(me.polygons)} non_manifold={nonman}")

bpy.ops.object.select_all(action='DESELECT'); case.select_set(True)
try: bpy.ops.wm.stl_export(filepath=OUT_STL, export_selected_objects=True)
except Exception: bpy.ops.export_mesh.stl(filepath=OUT_STL, use_selection=True)
print("EXPORTED", OUT_STL)

# --- verify renders (zoom on the engraving, grazing light) ---
mat = bpy.data.materials.new("clay"); mat.use_nodes = True
b = mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.36, 0.20, 0.42, 1); b.inputs["Roughness"].default_value = 0.45  # purple-ish
case.data.materials.clear(); case.data.materials.append(mat)
sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 3.0
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(60), 0, math.radians(25))
sd2 = bpy.data.lights.new("s2", 'SUN'); sd2.energy = 2.2
sun2 = bpy.data.objects.new("s2", sd2); bpy.context.collection.objects.link(sun2)
sun2.rotation_euler = (math.radians(82), 0, math.radians(135))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.8, 0.82, 0.86, 1); bg.inputs[1].default_value = 0.5
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 56
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt)
cam.constraints.new('TRACK_TO').target = tgt
focus = Vector((cx, cy, mx[2]))
def rf(loc, ortho, path):
    tgt.location = focus; cam.location = Vector(loc); cd.ortho_scale = ortho
    bpy.context.view_layer.update(); sc.render.filepath = path
    bpy.ops.render.render(write_still=True); print("RENDERED", path)
sc.render.resolution_x = 1400; sc.render.resolution_y = 1100
rf((cx, cy, mx[2] + 100), TW * 1.8, OUT_PREFIX + "_top.png")          # top-down on logo
# full-board view from the FRONT (+Y) elevated, matching the product photo angle
bx = (mn[0] + mx[0]) / 2; by = (mn[1] + mx[1]) / 2; W = mx[0] - mn[0]; D = mx[1] - mn[1]
tgt.location = Vector((bx, by, mx[2]))
cam.location = Vector((bx - 0.25 * W, mx[1] + 1.3 * D, mx[2] + 1.0 * D)); cd.ortho_scale = W * 1.12
sc.render.resolution_x = 1700; sc.render.resolution_y = 1150
bpy.context.view_layer.update(); sc.render.filepath = OUT_PREFIX + "_front.png"
bpy.ops.render.render(write_still=True); print("RENDERED", OUT_PREFIX + "_front.png")
