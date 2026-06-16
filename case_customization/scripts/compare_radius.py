"""
Render a TIGHT macro close-up of one outer corner for radius comparison.
  blender --background --python compare_radius.py -- <in.stl> <out.png> <width_mm> <segments>
width 0 = leave sharp (baseline).  segments 1 = chamfer; >1 = round.
"""
import bpy, bmesh, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT_PNG = argv[0], argv[1]
WIDTH = float(argv[2]) if len(argv) > 2 else 0.0
SEGS = int(argv[3]) if len(argv) > 3 else 5

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

xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys); zmin, zmax = min(zs), max(zs)
TOL = 0.8; ZTOL = 1.2
def on_outer(v):
    return (abs(v.co.x - xmin) < TOL or abs(v.co.x - xmax) < TOL or
            abs(v.co.y - ymin) < TOL or abs(v.co.y - ymax) < TOL)

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
        if max(v1.co.z, v2.co.z) < zmax - ZTOL: continue
        sel.append(e)
    bmesh.ops.bevel(bm, geom=sel, offset=WIDTH, offset_type='OFFSET',
                    segments=SEGS, profile=0.5, affect='EDGES', clamp_overlap=True)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.normal_update(); bm.to_mesh(me); bm.free(); me.update()
    print(f"DIAG width={WIDTH} segs={SEGS} faces={len(me.polygons)}")

mat = bpy.data.materials.new("clay"); mat.use_nodes = True
b = mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.58, 0.60, 0.67, 1); b.inputs["Roughness"].default_value = 0.30
obj.data.materials.clear(); obj.data.materials.append(mat)

# tight macro on the front-right-top corner
corner = Vector((xmax, ymin, zmax))
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.ortho_scale = 26.0
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt); tgt.location = corner
cam.constraints.new('TRACK_TO').target = tgt
cam.location = corner + Vector((1.0, -1.0, 0.7)).normalized() * 120

sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 4.0; sd.angle = math.radians(2)
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.85, 0.87, 0.9, 1); bg.inputs[1].default_value = 0.6

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.resolution_x = 1000; sc.render.resolution_y = 1000
sc.render.filepath = OUT_PNG
bpy.context.view_layer.update()
bpy.ops.render.render(write_still=True)
print("RENDERED", OUT_PNG)
