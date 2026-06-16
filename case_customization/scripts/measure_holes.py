"""Find small round holes (screw holes/standoffs) in an STL, orientation-agnostic.
  blender --background --python measure_holes.py -- <in.stl>
Auto-detects the height axis (smallest extent); reports holes in the footprint plane.
"""
import bpy, sys, math, statistics
from collections import defaultdict

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
vs = [v.co for v in o.data.vertices]
mn = [min(v[i] for v in vs) for i in range(3)]
mx = [max(v[i] for v in vs) for i in range(3)]
ext = [mx[i] - mn[i] for i in range(3)]
H = ext.index(min(ext)); F = [i for i in range(3) if i != H]
AX = "XYZ"
print(f"bbox X[{mn[0]:.1f},{mx[0]:.1f}] Y[{mn[1]:.1f},{mx[1]:.1f}] Z[{mn[2]:.1f},{mx[2]:.1f}]  height_axis={AX[H]} footprint={AX[F[0]]}{AX[F[1]]}")

buck = defaultdict(lambda: [1e9, -1e9])
for v in vs:
    k = (round(v[F[0]], 1), round(v[F[1]], 1))
    b = buck[k]; b[0] = min(b[0], v[H]); b[1] = max(b[1], v[H])
pts = [k for k, b in buck.items() if b[1] - b[0] > 0.8]

used = [False] * len(pts); clusters = []
for i in range(len(pts)):
    if used[i]: continue
    stack = [i]; used[i] = True; cl = [pts[i]]
    while stack:
        a = stack.pop(); ax, ay = pts[a]
        for j in range(len(pts)):
            if not used[j] and (ax - pts[j][0])**2 + (ay - pts[j][1])**2 < 9:
                used[j] = True; stack.append(j); cl.append(pts[j])
    clusters.append(cl)

rows = []
for cl in clusters:
    cx = sum(p[0] for p in cl) / len(cl); cy = sum(p[1] for p in cl) / len(cl)
    dists = [math.hypot(p[0] - cx, p[1] - cy) for p in cl]
    md = sum(dists) / len(dists); mxd = max(dists)
    rnd = statistics.pstdev(dists) / md if md > 0 else 9
    rows.append((2 * md, 2 * mxd, cx, cy, len(cl), rnd))
rows.sort()
print(f"dia_avg dia_max  center({AX[F[0]]},{AX[F[1]]})   npts roundness")
for d, dm, cx, cy, n, r in rows:
    if d < 12 and n >= 5:
        tag = "  <-- ROUND" if r < 0.18 else ""
        print(f"{d:6.2f} {dm:6.2f}  ({cx:7.1f},{cy:7.1f}) {n:4d}  {r:.2f}{tag}")
