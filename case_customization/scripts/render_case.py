"""
Inspect + render an STL from a few angles using Cycles (CPU, headless-safe).
  blender --background --python render_case.py -- <in.stl> <out_prefix>
Prints DIAG lines; writes <out_prefix>_iso.png, _corner.png, _top.png
"""
import bpy, bmesh, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN = argv[0]
OUT_PREFIX = argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)

# --- import STL (4.2+ importer first, legacy fallback) ---
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception as e:
    print("wm.stl_import failed, trying legacy:", e)
    try:
        bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception:
        pass
    bpy.ops.import_mesh.stl(filepath=IN)

obj = bpy.context.active_object or bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = obj
me = obj.data

# --- diagnostics ---
d = obj.dimensions
print(f"DIAG dims_mm=({d.x:.2f},{d.y:.2f},{d.z:.2f})")
print(f"DIAG verts={len(me.vertices)} edges={len(me.edges)} faces={len(me.polygons)}")
bm = bmesh.new(); bm.from_mesh(me)
nonman = sum(1 for e in bm.edges if not e.is_manifold)
print(f"DIAG non_manifold_edges={nonman}")
bm.free()

# --- clay material, semi-gloss so edges catch highlights ---
mat = bpy.data.materials.new("clay"); mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.58, 0.60, 0.67, 1)
bsdf.inputs["Roughness"].default_value = 0.35
obj.data.materials.clear(); obj.data.materials.append(mat)

# --- bbox ---
bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
center = sum(bb, Vector()) / 8.0
maxdim = max(d.x, d.y, d.z)
minz = min(v.z for v in bb)

# --- ground plane ---
bpy.ops.mesh.primitive_plane_add(size=maxdim * 6, location=(center.x, center.y, minz - 0.05))
plane = bpy.context.active_object
pm = bpy.data.materials.new("ground"); pm.use_nodes = True
pm.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.88, 0.88, 0.9, 1)
plane.data.materials.append(pm)
bpy.context.view_layer.objects.active = obj

# --- camera w/ track-to ---
tgt = bpy.data.objects.new("tgt", None); bpy.context.collection.objects.link(tgt); tgt.location = center
cam_data = bpy.data.cameras.new("cam"); cam_data.type = 'ORTHO'
cam = bpy.data.objects.new("cam", cam_data); bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
con = cam.constraints.new('TRACK_TO'); con.target = tgt

# --- lights ---
sd = bpy.data.lights.new("sun", 'SUN'); sd.energy = 4.0; sd.angle = math.radians(3)
sun = bpy.data.objects.new("sun", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
world = bpy.data.worlds.new("w"); bpy.context.scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.85, 0.87, 0.9, 1); bg.inputs[1].default_value = 0.6

# --- cycles cpu ---
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 24
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'
sc.render.resolution_x = 1280; sc.render.resolution_y = 960

def render_from(direction, dist_mult, ortho_mult, path):
    cam.location = center + Vector(direction).normalized() * maxdim * dist_mult
    cam_data.ortho_scale = maxdim * ortho_mult
    bpy.context.view_layer.update()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)

render_from(( 1.0, -1.2, 0.80), 3.0, 1.25, OUT_PREFIX + "_iso.png")
render_from((-0.6, -1.4, 0.45), 1.6, 0.55, OUT_PREFIX + "_corner.png")
render_from(( 0.0, 0.001, 1.0), 3.0, 1.15, OUT_PREFIX + "_top.png")
