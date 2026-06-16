"""
Selectively round the OUTER edges of a keyboard case top, then export + render.
  blender --background --python bevel_case.py -- <in.stl> <out.stl> <out_prefix> [width_mm] [segments]
Rounds: top outer rim + vertical corners.  Leaves: switch/stab cutouts, bottom mating edge.
"""
import bpy, bmesh, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT_STL, OUT_PREFIX = argv[0], argv[1], argv[2]
WIDTH = float(argv[3]) if len(argv) > 3 else 1.5
SEGS = int(argv[4]) if len(argv) > 4 else 5

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

# --- bbox (local coords) ---
xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
xmin, xmax = min(xs), max(xs); ymin, ymax = min(ys), max(ys); zmin, zmax = min(zs), max(zs)
TOL = 0.8    # proximity to an outer side wall (mm)
ZTOL = 1.2   # "near the top" band (mm)

def on_outer(v):
    return (abs(v.co.x - xmin) < TOL or abs(v.co.x - xmax) < TOL or
            abs(v.co.y - ymin) < TOL or abs(v.co.y - ymax) < TOL)

bm = bmesh.new(); bm.from_mesh(me); bm.edges.ensure_lookup_table()
sel = []
for e in bm.edges:
    if not e.is_manifold:
        continue
    try:
        ang = e.calc_face_angle()
    except Exception:
        continue
    if ang < math.radians(25):          # skip flat/triangulation edges
        continue
    v1, v2 = e.verts
    if not (on_outer(v1) and on_outer(v2)):   # outer side walls only
        continue
    if max(v1.co.z, v2.co.z) < zmax - ZTOL:   # exclude bottom mating ring
        continue
    sel.append(e)

print(f"DIAG selected_edges={len(sel)} of {len(bm.edges)}  width={WIDTH} segs={SEGS}")

bmesh.ops.bevel(bm, geom=sel, offset=WIDTH, offset_type='OFFSET',
                segments=SEGS, profile=0.5, affect='EDGES', clamp_overlap=True)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
bm.normal_update()
bm.to_mesh(me); bm.free(); me.update()

# --- validate ---
bm2 = bmesh.new(); bm2.from_mesh(me)
nonman = sum(1 for e in bm2.edges if not e.is_manifold)
bm2.free()
print(f"DIAG after_verts={len(me.vertices)} after_faces={len(me.polygons)} non_manifold={nonman}")

# --- export ONLY the case (before adding render props) ---
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
try:
    bpy.ops.wm.stl_export(filepath=OUT_STL, export_selected_objects=True)
except Exception as e:
    print("wm.stl_export failed:", e); bpy.ops.export_mesh.stl(filepath=OUT_STL, use_selection=True)
print("EXPORTED", OUT_STL)

# ---------- render (Cycles CPU) ----------
mat = bpy.data.materials.new("clay"); mat.use_nodes = True
b = mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.58, 0.60, 0.67, 1); b.inputs["Roughness"].default_value = 0.35
obj.data.materials.clear(); obj.data.materials.append(mat)

bb = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
center = sum(bb, Vector()) / 8.0; maxdim = max(obj.dimensions); minz = min(v.z for v in bb)
bpy.ops.mesh.primitive_plane_add(size=maxdim * 6, location=(center.x, center.y, minz - 0.05))
plane = bpy.context.active_object
pm = bpy.data.materials.new("g"); pm.use_nodes = True
pm.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value = (0.88, 0.88, 0.9, 1)
plane.data.materials.append(pm)

tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt); tgt.location = center
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam
cam.constraints.new('TRACK_TO').target = tgt

sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 4.0; sd.angle = math.radians(3)
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.85, 0.87, 0.9, 1); bg.inputs[1].default_value = 0.6

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 24
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'; sc.render.resolution_x = 1280; sc.render.resolution_y = 960

def render_from(direction, dist_mult, ortho_mult, path):
    cam.location = center + Vector(direction).normalized() * maxdim * dist_mult
    cd.ortho_scale = maxdim * ortho_mult
    bpy.context.view_layer.update()
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path)

render_from(( 1.0, -1.2, 0.80), 3.0, 1.25, OUT_PREFIX + "_iso.png")
render_from((-0.6, -1.4, 0.45), 1.6, 0.55, OUT_PREFIX + "_corner.png")
render_from(( 0.0, 0.001, 1.0), 3.0, 1.15, OUT_PREFIX + "_top.png")
