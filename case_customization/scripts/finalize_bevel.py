"""
Orientation-agnostic selective bevel + export + upright verify render.
  blender --background --python finalize_bevel.py -- <in.stl> <out.stl> <out_prefix> <width> <segs> <side>
Auto-detects the height axis (smallest extent). side: 'hi' rounds the high end, 'lo' the low end.
width 0 = no bevel (inspection render only, no export).
"""
import bpy, bmesh, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT_STL, OUT_PREFIX = argv[0], argv[1], argv[2]
WIDTH = float(argv[3]) if len(argv) > 3 else 2.5
SEGS = int(argv[4]) if len(argv) > 4 else 6
SIDE = argv[5] if len(argv) > 5 else 'hi'

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
obj = bpy.context.active_object or bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj
me = obj.data

co = [v.co for v in me.vertices]
mn = [min(c[i] for c in co) for i in range(3)]
mx = [max(c[i] for c in co) for i in range(3)]
ext = [mx[i] - mn[i] for i in range(3)]
H = ext.index(min(ext))          # height axis = smallest extent
F = [i for i in range(3) if i != H]  # footprint axes
print(f"DIAG extents={[round(e,2) for e in ext]} height_axis={'XYZ'[H]}")
TOL = 0.8; ZTOL = 1.2

def on_outer(v):
    return any(abs(v.co[a] - mn[a]) < TOL or abs(v.co[a] - mx[a]) < TOL for a in F)

if WIDTH > 0:
    bm = bmesh.new(); bm.from_mesh(me); bm.edges.ensure_lookup_table()
    sel = []
    for e in bm.edges:
        if not e.is_manifold: continue
        try: ang = e.calc_face_angle()
        except Exception: continue
        if ang < math.radians(25): continue
        v1, v2 = e.verts
        if not (on_outer(v1) and on_outer(v2)): continue
        if SIDE == 'hi':
            if max(v1.co[H], v2.co[H]) < mx[H] - ZTOL: continue
        else:
            if min(v1.co[H], v2.co[H]) > mn[H] + ZTOL: continue
        sel.append(e)
    print(f"DIAG side={SIDE} selected_edges={len(sel)} width={WIDTH} segs={SEGS}")
    bmesh.ops.bevel(bm, geom=sel, offset=WIDTH, offset_type='OFFSET',
                    segments=SEGS, profile=0.5, affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update(); bm.to_mesh(me); bm.free(); me.update()
    bm2 = bmesh.new(); bm2.from_mesh(me)
    nonman = sum(1 for e in bm2.edges if not e.is_manifold); bm2.free()
    print(f"DIAG after_verts={len(me.vertices)} after_faces={len(me.polygons)} non_manifold={nonman}")
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    try: bpy.ops.wm.stl_export(filepath=OUT_STL, export_selected_objects=True)
    except Exception: bpy.ops.export_mesh.stl(filepath=OUT_STL, use_selection=True)
    print("EXPORTED", OUT_STL)

# rotate upright for a sensible view: bring height axis -> +Z
if H == 1:   obj.rotation_euler = (math.radians(90), 0, 0)
elif H == 0: obj.rotation_euler = (0, math.radians(-90), 0)
bpy.context.view_layer.update()

mat = bpy.data.materials.new("clay"); mat.use_nodes = True
b = mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.58, 0.60, 0.67, 1); b.inputs["Roughness"].default_value = 0.32
obj.data.materials.clear(); obj.data.materials.append(mat)

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
wmn = Vector((min(p[i] for p in bb) for i in range(3)))
wmx = Vector((max(p[i] for p in bb) for i in range(3)))
center = (wmn + wmx) / 2.0
maxdim = max((wmx - wmn)[i] for i in range(3))

bpy.ops.mesh.primitive_plane_add(size=maxdim * 6, location=(center.x, center.y, wmn.z - 0.05))
pl = bpy.context.active_object; pm = bpy.data.materials.new("g"); pm.use_nodes = True
pm.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.88, 0.88, 0.9, 1)
pl.data.materials.append(pm)
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt); tgt.location = center
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
cam.constraints.new('TRACK_TO').target = tgt
sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 4.0; sd.angle = math.radians(3)
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bgn = w.node_tree.nodes["Background"]; bgn.inputs[0].default_value = (0.85, 0.87, 0.9, 1); bgn.inputs[1].default_value = 0.6
sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 28
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.resolution_x = 1280; sc.render.resolution_y = 960
def rf(direction, dist_mult, ortho_mult, path):
    cam.location = center + Vector(direction).normalized() * maxdim * dist_mult
    cd.ortho_scale = maxdim * ortho_mult
    bpy.context.view_layer.update(); sc.render.filepath = path
    bpy.ops.render.render(write_still=True); print("RENDERED", path)
rf(( 1.0, -1.2, 0.6), 3.0, 1.25, OUT_PREFIX + "_iso.png")
rf((-0.7, -1.4, 0.4), 1.6, 0.6, OUT_PREFIX + "_corner.png")
