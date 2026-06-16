"""Profile a screw column: inner/outer diameter vs height near a given footprint point.
  blender --background --python screw_profile.py -- <in.stl> <cx> <cy>
(cx,cy) = hole center in the footprint plane (the two non-height axes).
"""
import bpy, sys, math
argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
IN = argv[0]; CX = float(argv[1]); CY = float(argv[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
try:
    bpy.ops.wm.stl_import(filepath=IN)
except Exception:
    try: bpy.ops.preferences.addon_enable(module="io_mesh_stl")
    except Exception: pass
    bpy.ops.import_mesh.stl(filepath=IN)
o = bpy.context.active_object or bpy.context.selected_objects[0]
vs = [v.co for v in o.data.vertices]
mn = [min(v[i] for v in vs) for i in range(3)]; mx = [max(v[i] for v in vs) for i in range(3)]
ext = [mx[i] - mn[i] for i in range(3)]
H = ext.index(min(ext)); F = [i for i in range(3) if i != H]
AX = "XYZ"
print(f"height_axis={AX[H]} footprint={AX[F[0]]}{AX[F[1]]}  H-span overall [{mn[H]:.2f},{mx[H]:.2f}]")

R = 7.0
near = [v for v in vs if (v[F[0]] - CX)**2 + (v[F[1]] - CY)**2 < R * R]
if not near:
    print("no verts near axis"); raise SystemExit
hmin = min(v[H] for v in near); hmax = max(v[H] for v in near)
print(f"column H span [{hmin:.2f},{hmax:.2f}] depth={hmax-hmin:.2f}")
step = 0.5
nb = int((hmax - hmin) / step) + 1
bins = [[] for _ in range(nb)]
for v in near:
    bi = min(nb - 1, int((v[H] - hmin) / step))
    bins[bi].append(math.hypot(v[F[0]] - CX, v[F[1]] - CY))
print("  h(mm)  inner_dia outer_dia  n")
for i, b in enumerate(bins):
    if not b: continue
    print(f"  {hmin + i*step:6.2f}   {2*min(b):6.2f}   {2*max(b):6.2f}   {len(b)}")
