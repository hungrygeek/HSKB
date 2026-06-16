"""Ray-cast a grid over the top plate and print an ASCII occupancy map to lock orientation.
  blender --background --python grid_map.py -- <top.stl>
'#' = solid plate, ' ' = cutout/opening. Printed with Y-max row at the TOP.
"""
import bpy, sys
from mathutils import Vector

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
o = bpy.context.active_object or bpy.context.selected_objects[0]
me = o.data
xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
xmn, xmx = min(xs), max(xs); ymn, ymx = min(ys), max(ys); zmx = max(zs)
print(f"X[{xmn:.0f},{xmx:.0f}]  Y[{ymn:.0f},{ymx:.0f}]  Zmax={zmx:.1f}")
print("Top row = Y-max ; left col = X-min ; '#'=solid plate, ' '=cutout")
NX, NY = 96, 32
down = Vector((0, 0, -1))
print("      " + "".join("L" if i == 0 else ("R" if i == NX - 1 else ".") for i in range(NX)))
for j in range(NY):
    y = ymx - (ymx - ymn) * j / (NY - 1)
    row = ""
    for i in range(NX):
        x = xmn + (xmx - xmn) * i / (NX - 1)
        res = o.ray_cast(Vector((x, y, zmx + 5)), down)
        row += "#" if (res[0] and res[1].z > zmx - 1.0) else " "
    tag = "<Ymax(front?)" if j == 0 else ("<Ymin(back?)" if j == NY - 1 else "")
    print(f"{y:5.0f}|{row}|{tag}")
