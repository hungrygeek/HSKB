# Ordering the VoidHHKB-Hotswap PCB (turnkey)

The files in this folder upload to JLCPCB as-is — every assembly part now has an LCSC number.

## Files
- `VoidHHKB-Hotswap.zip` — Gerbers (upload as the PCB)
- `bom.csv` — assembly BOM (all lines have LCSC #s)
- `positions.csv` — CPL / placement file (143 parts, bottom layer)

## Resolved assembly parts
The original BOM was missing LCSC numbers for two lines; now filled in:
- 60× `1N4148W` diode, SOD-123 → **C81598** (JLC basic part)
- 60× Kailh MX hotswap socket, CPG151101S11 → **C5184526** (extended part — expect a one-time feeder fee)

## JLCPCB settings
- Quantity: **5** (JLC minimum). Assemble **3** (or all 5 — setup/stencil fees dominate, so 5 is barely more).
- Surface finish: **ENIG**. Remove order number: **Yes**.
- **PCB Assembly: ON** → Assembly side **Bottom**, type **Standard**.
- Upload `bom.csv` + `positions.csv` → *Process BOM & CPL*.
- ⚠️ In the placement preview, **rotate the hotswap sockets** if they look mis-oriented.
- Product description: `Keyboard - HS Code 847330`.
- Shipping: **DHL/FedEx/UPS express** for fastest delivery to the US.

MCU is **STM32F072** (STM32 DFU bootloader) — see `../README.md` for flashing.
