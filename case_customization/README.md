# Case customization workspace

Tooling and renders used to produce the rounded-edge + **SSKB**-engraved case variants
(the finals live in `../HSKB STL/`). Everything here was generated with **Blender**
(headless, Cycles CPU — Workbench/EEVEE don't render headless on macOS).

## Layout
- `scripts/` — Blender Python scripts (rounding, engraving, measuring, rendering)
- `renders/` — preview / verification renders (incl. the hero shots `hero2_*`)
- `wip_stl/` — intermediate STLs (the print-ready finals are in `../HSKB STL/`)

## Key scripts
| Script | Purpose |
|---|---|
| `finalize_bevel.py` | Orientation-aware selective edge rounding (`hi`/`lo` side, auto height-axis) |
| `engrave_text.py` | Engrave text into the top face via a boolean difference + manifold cleanup |
| `measure_holes.py` | Find screw holes / standoffs and report diameters |
| `screw_profile.py` | Profile a screw column (counterbore / pilot / depth) |
| `hero_render.py` | Assembled top+bottom hero render (metallic purple) |
| `render_case.py`, `compare_radius.py`, `find_text.py` | Inspection / comparison renders |

## Example
```bash
B="/Applications/Blender.app/Contents/MacOS/Blender"
# round the top's top edge at 2.5 mm:
"$B" --background --python scripts/finalize_bevel.py -- \
  "../HSKB STL/HHKB v13 v1_top.stl" out_top.stl prefix 2.5 6 hi
```

## Final settings used
- Edge rounding: **2.5 mm** fillet (top: high side; bottom: base/low side)
- Engraving: **"SSKB"**, 0.4 mm deep, **front-right** border (user's right = −X, spacebar edge = +Y)
- Both final meshes verified watertight (0 non-manifold edges).
