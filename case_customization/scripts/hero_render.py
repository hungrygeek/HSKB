"""
Assembled hero render of the case (top + bottom) in metallic-purple, front-3/4, plus an SSKB close-up.
  blender --background --python hero_render.py -- <top.stl> <bottom.stl> <out_prefix>
"""
import bpy, sys, math
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
TOP, BOT, OUT = argv[0], argv[1], argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)

def imp(path):
    bpy.ops.object.select_all(action='DESELECT')
    try: bpy.ops.wm.stl_import(filepath=path)
    except Exception:
        try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
        except Exception: pass
        bpy.ops.import_mesh.stl(filepath=path)
    return bpy.context.active_object

def bbox(o):
    c = [o.matrix_world @ Vector(v) for v in o.bound_box]
    return (Vector((min(p[i] for p in c) for i in range(3))),
            Vector((max(p[i] for p in c) for i in range(3))))

top = imp(TOP)
bot = imp(BOT)

# bottom: height is on Y in its file -> rotate so it points up (+Z), opening up
bot.rotation_euler = (math.radians(90), 0, 0)
bpy.context.view_layer.objects.active = bot
bpy.ops.object.select_all(action='DESELECT'); bot.select_set(True)
bpy.ops.object.transform_apply(rotation=True)

# center both in XY, then stack bottom on the ground and top on the bottom
for o in (top, bot):
    mn, mx = bbox(o); ctr = (mn + mx) / 2
    o.location.x -= ctr.x; o.location.y -= ctr.y
bpy.context.view_layer.update()
mn, mx = bbox(bot); bot.location.z -= mn.z
bpy.context.view_layer.update()
mnb, mxb = bbox(bot)
mnt, mxt = bbox(top); top.location.z += (mxb.z - mnt.z)
bpy.context.view_layer.update()

# silk-PLA-ish purple (slightly metallic, glossy)
def purple(o):
    m = bpy.data.materials.new("pp"); m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (0.30, 0.05, 0.45, 1)
    p.inputs["Metallic"].default_value = 0.45
    p.inputs["Roughness"].default_value = 0.30
    o.data.materials.clear(); o.data.materials.append(m)
purple(top); purple(bot)

# scene bounds
mnb, mxb = bbox(bot); mnt, mxt = bbox(top)
amn = Vector((min(mnb[i], mnt[i]) for i in range(3)))
amx = Vector((max(mxb[i], mxt[i]) for i in range(3)))
center = (amn + amx) / 2
maxdim = max((amx - amn)[i] for i in range(3))

# ground + bright studio world (so the metal has something to reflect)
bpy.ops.mesh.primitive_plane_add(size=maxdim * 10, location=(center.x, center.y, amn.z - 0.02))
pl = bpy.context.active_object
gm = bpy.data.materials.new("g"); gm.use_nodes = True
gp = gm.node_tree.nodes.get("Principled BSDF")
gp.inputs["Base Color"].default_value = (0.62, 0.63, 0.66, 1); gp.inputs["Roughness"].default_value = 0.55
pl.data.materials.append(gm)
w = bpy.data.worlds.new("w"); bpy.context.scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.7, 0.72, 0.78, 1); bg.inputs[1].default_value = 1.0
sd = bpy.data.lights.new("key", 'SUN'); sd.energy = 3.2; sd.angle = math.radians(4)
sun = bpy.data.objects.new("key", sd); bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(52), math.radians(8), math.radians(40))

# camera (ortho for reliable framing)
cd = bpy.data.cameras.new("c"); cd.type = 'ORTHO'
cam = bpy.data.objects.new("c", cd); bpy.context.collection.objects.link(cam); bpy.context.scene.camera = cam
tgt = bpy.data.objects.new("t", None); bpy.context.collection.objects.link(tgt)
cam.constraints.new('TRACK_TO').target = tgt

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 140
try: sc.cycles.use_denoising = True
except Exception: pass
sc.render.image_settings.file_format = 'PNG'

def shot(direction, target, ortho, res, path):
    cam.location = Vector(target) + Vector(direction).normalized() * maxdim * 2.0
    cd.ortho_scale = ortho
    sc.render.resolution_x, sc.render.resolution_y = res
    tgt.location = Vector(target)
    bpy.context.view_layer.update(); sc.render.filepath = path
    bpy.ops.render.render(write_still=True); print("RENDERED", path)

# full hero, from the FRONT (+Y) elevated, viewed from the user's-right (-X)
shot((-0.35, 1.0, 0.6), center, maxdim * 1.12, (1700, 1200), OUT + "_hero.png")
# SSKB close-up (user's front-right of the top: X-min, Y-max)
ssk = Vector((mnt.x + 24, mxt.y - 10, mxt.z))
shot((-0.5, 1.0, 0.65), ssk, 80, (1500, 1100), OUT + "_sskb.png")
