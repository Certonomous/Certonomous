# pyHyp route probe — RESULT: the TOOLCHAIN runs end-to-end on this box

**2026-09-11. Marker `PROBE_MARKER.txt` was written at 17:51:16Z, BEFORE any mesh existed.**
**This is a toolchain probe. It is NOT a graded run, NOT physics, and NOT a configuration
clearance. No gate, threshold or verdict is issued and no flow quantity is produced.**

## 🔴 THE HEADLINE, WHICH IS A LIMIT AND NOT A CLEARANCE

> **A GREEN PROBE HERE CLEARS THE TOOLCHAIN, NOT THE CONFIGURATION.**
> The surface extruded is **WING-ONLY** — measured `rootLen/totLen = 0.5208`, span 3.7667,
> root at the side-of-body. **Hyperbolic extrusion from a CLOSED WING-BODY surface is a
> materially harder problem. That is a STATED EXPECTATION, NOT A MEASUREMENT**, and this
> probe **cannot** test it, because **no CRM wing-body surface exists on this box** (sweep of
> 80+ CGNS files plus the STL libraries, by GEOMETRY not by name).

## WHAT RAN

`pyhyp` inside `dafoam-subpclu:v1`, options copied verbatim from the case's own
`genWingMesh.py` (`N 53`, `s0 1.0e-4`, `marchDist 25 × 3.758151`, `cMax 5.0`).

## WHAT IS BELIEVED, AND WHY IT IS NOT THE EXIT STATUS

**`rc` was captured INSIDE the container wrapper, never around `docker run`. Both readings are
reported; the PRINTED OUTPUT is the verdict.**

| reading | value |
|---|---|
| `docker run` wrapper exit | **0** |
| `PYHYP_RC` captured inside | **0** |
| printed output | 53 layers marched, `Sl = 1.000`, `volumeMesh.xyz` written |

**Two measured reasons the exit status is not relied on, both from THIS probe:**
1. **The first attempt exited `rc=127` (`python3: command not found`, a uid mismatch from
   `-u $(id -u)` breaking the container's conda env) — and the `docker run` wrapper still
   exited `0`.** The wrapper reports its own status, not the work's.
2. 🔴 **`pyhyp_rc.txt` READ `127` FOR FOUR MINUTES WHILE THE SUCCESSFUL RUN WAS MARCHING**,
   because the wrapper writes it only at the end and it was never cleared between attempts.
   **A status artifact that outlives the run it describes reads identically to a current
   result.** Repair, recorded against this wrapper: **clear or timestamp the status artifact
   BEFORE the run, never only after it** — the same principle rule 4's age guard encodes.

## THE EVIDENCE, READ OFF THE COLUMNS RATHER THAN A BANNER

| check | measured |
|---|---|
| **end-of-script marker** (ours, not pyHyp's) | **`PYHYP_WROTE volumeMesh.xyz` present** — the script reached its final line |
| layers marched | **53 of 53**, final row `Sl = 1.000` |
| march distance reached | **94.2** against the registered target `25 × 3.758151 = 93.95` |
| **Min Quality, minimum over ALL layers** | **0.08110 — POSITIVE AT EVERY LAYER** |
| **Min Volume, minimum over ALL layers** | **9.49e-13 — POSITIVE AT EVERY LAYER** |
| quality profile | worst at the FIRST layer (L2, 0.0811), improving monotonically to 0.3236 at L53 — the expected near-wall signature |
| artifact | `work/volumeMesh.xyz`, 163,573,897 bytes |
| errors/warnings in log | **one**, `WARNING 7: VSPAERO Viewer Not Found` — an OpenVSP startup message from the container's environment load, **unrelated to pyHyp**. Explained, not waved through. |

## STATED RESIDUES

- **The volume mesh was NOT quality-checked by `checkMesh` or converted to OpenFOAM.** Only
  pyHyp's own marching columns are read. **A positive marching quality is not a `checkMesh`
  admission**, and no claim is made that this mesh would pass Gate M anything.
- `volumeMesh.xyz` is written **root-owned** by the container. Harmless here (a probe
  directory, not a graded tree) and recorded so it is not a surprise later.
- **No graded tree was touched.** Input is a scratch copy of the surface.
- The 156 MB volume mesh is **deliberately not committed** — it is data, not a record.

**Cost: ~7.5 min wall, 1 rank (pyHyp is serial here) ≈ 7.5 core-min. Zero solver compute.**
