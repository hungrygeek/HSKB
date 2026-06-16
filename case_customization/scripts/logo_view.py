"""Render a zoomed close-up of the logo from the USER's front viewpoint (camera = eyes in front).
  blender --background --python logo_view.py -- <in.stl> <out.png> <R|L>
"""
import bpy, sys, math
from mathutils import Vector
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT = argv[0], argv[1]
SIDE = argv[2] if len(argv) > 2 else "R"
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
o = bpy.context.active_object or bpy.context.selected_objects[0]
co = [v.co for v in o.data.vertices]
mn = [min(c[i] for c in co) for i in range(3)]; mx = [max(c[i] for c in co) for i in range(3)]
lx = (mx[0] - 27) if SIDE == "R" else (mn[0] + 27)
ly = mx[1] - 10; lz = mx[2]
focus = Vector((lx, ly, lz))

m = bpy.data.materials.new("p"); m.use_nodes = True
b = m.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.32, 0.06, 0.46, 1); b.inputs["Roughness"].default_value = 0.35
o.data.materials.clear(); o.data.materials.append(m)

sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 3.2
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(40), 0, math.radians(15))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.78, 0.8, 0.85, 1); bg.inputs[1].default_value = 0.7

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'
sc.render.resolution_x = 1200; sc.render.resolution_y = 900
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'; cd.ortho_scale = 70
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt); tgt.location = focus
cam.constraints.new('TRACK_TO').target = tgt
# camera in FRONT (+Y, beyond the front edge) and above — i.e. where the user's eyes are
cam.location = focus + Vector((0, 60, 38))
bpy.context.view_layer.update()
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("RENDERED", OUT)
