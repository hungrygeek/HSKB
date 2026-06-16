"""Render a hi-res top-down + a zoomed front-right view to locate the embossed logo."""
import bpy, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN, OUT_PREFIX = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
obj = bpy.context.active_object or bpy.context.selected_objects[0]
me = obj.data
co = [v.co for v in me.vertices]
mn = [min(c[i] for c in co) for i in range(3)]; mx = [max(c[i] for c in co) for i in range(3)]
center = Vector(((mn[0]+mx[0])/2, (mn[1]+mx[1])/2, (mn[2]+mx[2])/2))

mat = bpy.data.materials.new("clay"); mat.use_nodes = True
b = mat.node_tree.nodes.get("Principled BSDF")
b.inputs["Base Color"].default_value = (0.55, 0.57, 0.64, 1); b.inputs["Roughness"].default_value = 0.42
obj.data.materials.clear(); obj.data.materials.append(mat)

sd = bpy.data.lights.new("s", 'SUN'); sd.energy = 3.5
sun = bpy.data.objects.new("s", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(45), math.radians(10), math.radians(30))
sd2 = bpy.data.lights.new("s2", 'SUN'); sd2.energy = 2.5            # grazing light to reveal shallow embossing
sun2 = bpy.data.objects.new("s2", sd2); bpy.context.collection.objects.link(sun2)
sun2.rotation_euler = (math.radians(80), 0, math.radians(120))
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.8, 0.82, 0.86, 1); bg.inputs[1].default_value = 0.5

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 48
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'

cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt)
cam.constraints.new('TRACK_TO').target = tgt

def rf(loc, ortho, path, tgtloc):
    tgt.location = tgtloc; cam.location = Vector(loc); cd.ortho_scale = ortho
    bpy.context.view_layer.update(); sc.render.filepath = path
    bpy.ops.render.render(write_still=True); print("RENDERED", path)

ax, ay = mx[0]-mn[0], mx[1]-mn[1]
# full top-down, hi-res
sc.render.resolution_x = 2400; sc.render.resolution_y = int(2400*ay/ax) + 6
rf((center.x, center.y, center.z+200), max(ax, ay)*1.02, OUT_PREFIX+"_topdown.png", center)
# zoomed low front-right (where the logo sits in the photos)
fr = Vector((mx[0]-32, mn[1]+14, mx[2]))
sc.render.resolution_x = 1600; sc.render.resolution_y = 1200
rf((fr.x+55, fr.y-120, fr.z+75), 95, OUT_PREFIX+"_frontright.png", fr)
