# HSKB / SSKB — Complete JLC Ordering Guide

Everything needed to order the **PCB (JLCPCB)** and the **case (JLC3DP)**, plus the
remaining parts to finish the build.

- **Board:** HHKB-layout 60%, **hotswap MX**, 6u spacebar, STM32F072, QMK/VIA.
- **Case:** 2.5 mm rounded edges + **"SSKB"** lightly engraved, printed in **MJF nylon**.
- All files referenced below are in this repo and are upload-ready.

---

## 0. At a glance

| Item | Vendor | Upload / provide | Approx cost | Lead time |
|---|---|---|---|---|
| PCB (assembled) | **JLCPCB** (jlcpcb.com) | gerber zip + `bom.csv` + `positions.csv` | ~$80–160 | ~1.5–2 wk |
| Case (2 parts) | **JLC3DP** (jlc3dp.com) | 2 × STL | ~$60–150 | ~1–1.5 wk |
| Screws / stabs / cable | Amazon etc. | — | ~$20–40 | 1–2 days |

> JLCPCB and JLC3DP are **separate sites/carts** (same login). Place both around the
> same time; they will likely ship separately.

---

## Part A — PCB from JLCPCB

### Files to provide
All in `PCB Files/VoidHHKB-Hotswap/production/`:

| File | Role |
|---|---|
| `VoidHHKB-Hotswap.zip` | Gerbers — upload as the PCB |
| `bom.csv` | Assembly BOM (turnkey — every part has an LCSC #) |
| `positions.csv` | CPL / placement file (143 parts, bottom side) |

### Step by step
1. **jlcpcb.com** → sign in (free account; first orders often get coupons).
2. **Add gerber file** → upload `VoidHHKB-Hotswap.zip`; wait for the top/bottom preview.
3. **Base PCB options:**
   - PCB Qty: **5** (JLC minimum)
   - Surface finish: **ENIG** *(change from default HASL)*
   - PCB color: **Purple** (or your choice) · Remove order number: **Yes**
   - Leave **1.6 mm / 2-layer / 1 oz** at default
4. **Enable PCB Assembly** →
   - Assembly side: **Bottom**
   - Type: **Standard**
   - PCBA Qty: **3** (or **5** — setup/stencil fees dominate, so spares are cheap)
5. **Upload `bom.csv` + `positions.csv`** → **Process BOM & CPL**. Confirm the column
   mapping (Designator / Comment / Footprint / LCSC Part #).
6. **Parts review:** everything auto-matches. The **hotswap socket (C5184526)** is an
   *extended* part → accept the one-time feeder fee.
7. **Placement review:** ⚠️ **rotate the hotswap sockets** if the preview shows them
   mis-oriented; sanity-check diode / USB-C / STM32 placement.
8. **Customs / product description:** `Keyboard - HS Code 847330`.
9. **Checkout** → shipping: **DHL / FedEx / UPS express** to the Bay Area
   *(not "Global Standard")*.

### Resolved BOM parts (already filled in)
- `1N4148W` diode, SOD-123 → **C81598** (JLC basic part)
- Kailh MX hotswap socket, CPG151101S11 → **C5184526** (extended part)

### After it arrives
- Flash `PCB Files/VoidHHKB-Hotswap/firmware/void_voidhhkb_via.bin` with **QMK Toolbox**.
- **MCU = STM32F072 / STM32 DFU** (hold reset to enter bootloader; QMK Toolbox
  auto-detects it). *Not ATmega — ignore any old README note.*

---

## Part B — Case from JLC3DP

### Files to provide
All in `HSKB STL/` — both watertight, in **millimeters**:

| File | Role |
|---|---|
| `HHKB v13 v1_top_rounded_SSKB.stl` | Top: rounded top edge + "SSKB" engraving |
| `HHKB v13 v1_bottom_rounded.stl` | Bottom: rounded base edge |

### Step by step
1. **jlc3dp.com** → **3D Printing quote** → **Add STL** (upload **both** parts).
2. **Process: MJF** · **Material: PA12 Nylon (grey)** — optional **dyed black** for a
   more premium look.
3. Review the instant **DFM check** (flags any wall < 0.8 mm — the case should pass).
4. **Qty per part:** **1** to validate fit first *(recommended)*, or **3**.
5. **Finish:** standard bead-blasted matte = the frosted look; add dyeing if offered.
6. **Checkout** → express shipping to the Bay Area.

### Why MJF nylon (PA12)
Robust and impact-resistant (not brittle like resin), with a premium uniform
matte/frosted finish and no layer lines. The 299 × 113 mm parts fit the MJF envelope,
and the 0.4 mm SSKB engraving renders cleanly. *(SLA resin was only for translucency,
which you don't need.)*

---

## Part C — Other parts to buy (Amazon, McMaster, etc.)

| Part | Spec | Notes |
|---|---|---|
| **Case screws** | **M2.5 button-head assortment, ~10–22 mm** (self-tapping or machine) | Heads sit on the bottom; they self-tap into the top boss. Buy a kit and use the length that seats flush + bites — avoids a wrong-length re-order. |
| **Stabilizers** | **PCB-mount**: 2× **2u** (for the 2.25u Enter + left Shift) + 1× **6u** spacebar | Board has PCB-mount stab footprints. Confirm the 6u spacebar stab spacing. |
| **Switches** | ~**60 × MX** (3- or 5-pin; 5-pin clips into the plate) | 54×1u + 4×1.5u + 2×1.75u + spacebar |
| **Keycaps** | **HHKB 60% set with a 6u spacebar** | (you have these) |
| **USB-C cable** | data-capable | |

Amazon search that covers size + length in one kit: **"M2.5 button head screw assortment kit"**.

---

## Part D — Build order (to avoid re-iterations)

1. Order the **PCB (5 boards, assemble 3)** + **one case set** first.
2. On arrival: flash firmware → install **PCB-mount stabs** → clip in switches →
   seat PCB in the case → fit **M2.5 screws** (pick the length that seats flush) →
   keycaps.
3. **Validate the full fit on this one unit**, then print the remaining **2 cases**.

> Fitment has been verified against the source files: top↔bottom footprints match
> (299.45 × 113 mm), the 4 corner screw points align within ~0.3 mm, and the case
> customizations (rounding + engraving) did not alter any cutouts, screw holes, or
> mating surfaces. Still, a one-unit test build is the cheapest insurance.

---

## Spec sheet (quick reference)

- **Layout:** HHKB 60%, 6u spacebar · **Switches:** hotswap MX · **MCU:** STM32F072 · **Firmware:** QMK/VIA
- **Case:** top + bottom, 2.5 mm rounded edges, "SSKB" engraved 0.4 mm, **MJF PA12 nylon**
- **Screws:** M2.5 · **Stabs:** PCB-mount (2× 2.25u + 1× 6u)
- **Footprint:** 299 × 113 mm
- **PCB BOM key parts:** diode `C81598`, hotswap socket `C5184526`

---
*See also: `PCB Files/VoidHHKB-Hotswap/production/ORDERING.md` (PCB detail) and
`HSKB STL/ROUNDED_VARIANTS.md` (case STL detail).*
