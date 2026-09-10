# D6RF10 (A2 MACH wing) — RENDER PREPARATION — 2026-09-10

**No verdict claimed** — demo preparation, no pre-registered gate. `[lab-attributed]` under
`CASE_PROTOCOL_CHARTER.md` §9. **Zero solver compute.** Graded run root **provably untouched**.

## THE HEADLINE, AND IT IS NOT ABOUT RENDERING

**The graded R3 leg's fields DO NOT EXIST. They were destroyed by its own successor's launch, and no
future lane can recover them without re-running the leg.**

Verified by me first-hand on the **original** (read-only), not relayed:

- **Line 27 of EVERY leg command script** — `d6rf10_cmd_R3.sh`, `d6rf10_cmd_R3_control.sh`,
  `d6rf10_cmd_R2_control.sh` alike — is
  `rm -rf processor* mp04/processor* mp05/processor* mp06/processor* 2>/dev/null || true`.
  **Each leg wipes all decomposed state before it runs.** R3_control ran after R3.
- The `controlDict` on disk now reads **`endTime 1000`**, `writeInterval 1000` — **R3_control's** config
  (`DARhoSimpleFoam`, SIMPLE, nNonOrth 3, relax_p 0.30), **not** the graded R3 candidate's
  (`DARhoSimpleCFoam`, SIMPLEC, nNonOrth 12, relax_p 0.70, `endTime 2000`).
- **There are ZERO `2000/` directories anywhere in the case.** `mp04/processor0` holds `0` and `1000`
  only; `mp05` and `mp06` hold `0` only.
- The lane's timing corroboration: processor dirs created 05:47:25.48, fields at `1000/` written
  05:48:58.39–.54 — **93.1 s apart**, against `d6rf10_leg_R3_control.json`'s recorded
  `wall_s: 93.525`. An exact match. The R3 candidate finished ~05:46.

**Consequence, stated plainly: `R3_autograde.json`'s graded binding number
`p_first_uncorrected = 6.3233727e-06` (leg R3, `final_time` 2000, `DARhoSimpleCFoam`, read from log line
2687) has NO field data behind it on disk. No frame can carry that number.** The **grade itself stands**
— it was read from the solver log, which survives — but nothing field-based about R3 is recoverable.

## MY DECISION (§9 authority), AND ITS REASONS

**R3 will NOT be re-run to obtain render fields.** Cost would be **617.6 core-min** (9264 wall s × 4
ranks, the ledger's own figure) and ~2.6 h wall. **Under Sanaa's 2026-09-10 exemption no cap would stop
it — I am declining it on judgment, not on budget:**

1. **A3 ONERA M6 and D8R are stronger demo assets and are ready now.** A3 is a converged, experimentally
   validated M6 with its VTK already written; D8R is a two-row `PASS` with 48 reconstructed time steps.
   D6RF10 is the weakest of the three.
2. **The frame it would buy is weak.** R3's rung verdict is `GATE FAIL` (`nuTilda` at 1.392× the floor).
   It may never be captioned `PASS`, so 2.6 hours buys a picture whose honest caption is about flow and
   geometry — which R3_control's existing field already supplies.
3. **A re-run risks the banked grade.** A second R3 under different contention could produce a different
   number beside an already-graded one. **Re-running a graded leg to get a picture is a bad trade.**

**This is recorded as a decision with its basis (§6), not deferred upward (§8).** If the demo later needs
the SIMPLEC field specifically, the re-run is a registered successor, not an ad-hoc relaunch.

## WHAT EXISTS AND IS RENDERABLE

Copy at **`/home/ubuntu/certonomous-runs/D6RF10-RENDER-COPY-20260910T174434Z/`** (46 M → 49 M;
416-file sha256 manifest of the copy verified against the original).
`reconstructPar` on `P_conv/mp04` in the bought image (`sha256:2927768a…30f6d35`, ID verified against the
registry before use), **rc captured INSIDE the container: `RECON_RC_INSIDE=0`**, `End` line present,
102 wall s serial.

**The one flow field in this case is R3_CONTROL's, and it must be labelled as such:**
`DARhoSimpleFoam` (SIMPLE, **not** SIMPLEC), nNonOrth 3, relax_p 0.30, `endTime 1000`, **mp04 only** —
`mp05`/`mp06` hold uniform initial conditions only, consistent with the driver stopping after the `cl04`
primal raised.

| | |
|---|---|
| entry point | `…/D6RF10-RENDER-COPY-20260910T174434Z/P_conv/mp04`, time **1000** |
| **use `1000/polyMesh/points.gz`, NOT `constant/polyMesh`** | all 40,209 points differ; rendering `constant` would show baseline geometry carrying the deformed solution |
| mesh | 38,304 cells / 40,209 points / 116,756 faces |
| patches | `wing` (wall, 1008), `inout` (patch, 1008), `sym` (symmetry, 1672) — half-wing on `z=0` |
| renderable | `U`, `p`, `T`, `nut`, `nuTilda`, `alphat`, `rho` |
| ranges | \|U\| 23.165–128.832 m/s; `p` 97224.4–106131.3; `T` 296.770–303.701; `rho` 1.13396–1.21762 |
| physics | RAS Spalart–Allmaras, `Prt 1.0`; `hePsiThermo`/`perfectGas`, Cp 1005, molWeight 28.97, mu 1.8e-05, Pr 0.7 |

**DEGENERATE — none may be coloured:** `betaFINuTilda` `uniform 1` (**the same field that was degenerate
on D8R**), `fvSource` `uniform (0 0 0)`, `fvSourceEnergy` `uniform 0`, `meshPhi` `uniform 0`. The
`meshPhi` zero also says the mesh was **warped once before time-stepping**, not moved per step — unlike
D8R, **there is no animation here.**

**No early time exists for a before/after pair** — time `0` is uniform initial conditions, as on D8R.

## THE READ-BACK PLANT — four ways, and one clause did all the work

Reader required jointly: parses `nonuniform`, declared count == `nCells` 38304, **and `spread > 0`**.
(1) all-zero field of **correct** length → **BAD, spread == 0** — *an existence-and-length check passes
this*; (2) constant-nonzero (101325 everywhere), correct length → **BAD, spread == 0** — the clause
catches degenerate-but-nonzero too; (3) real spread, length 38297 → **BAD, count mismatch** — the count
clause exercised independently; (4) positive control → **OK**, so the seven field OKs are not a stuck
verdict. **Both failure modes and the success mode are demonstrated live.**

## ORIGINAL ROOT — UNTOUCHED, two channels, comparator probed both ways

Comparator probed **before** use: identical manifest → `MANIFEST_MATCH` rc=0; one character flipped in one
of 416 hashes → `MANIFEST_DIFFER` rc=3, **naming the exact file**. Not a blind zero.
**Result: sha256 of all 416 files before vs after → `MANIFEST_MATCH`; type/size/mtime of all 523 tree
entries → `TREE_MATCH`.** No new time directory, no touched `0/T`, no age-guard exposure.

## COST

`reconstructPar` 102 wall s = **1.700 core-min**; copy 0.017; whole lane gross 418 wall s =
**6.97 core-min** = 0.116 core-h → **$0.0060 DERIVED, NOT MEASURED** at $0.0513/core-h. 0 GPU-h.

## HONEST CAPTIONS — no frame carries a graded number

The graded number has no fields; the rung verdict is two clauses and may never read `PASS`. Captions are
about the flow and the geometry only:

1. *"Compressible RANS over a 3D half-wing — 38,304 cells, Spalart–Allmaras, symmetry plane at the root.
   Pressure field after 1,000 SIMPLE iterations."*
2. *"Velocity magnitude, 23.2 to 128.8 m/s, over the wing at its optimised shape — 96 shape and 7 twist
   design variables from the D6RF7 endpoint."*
3. Geometry only: *"Baseline against optimised wing surface: the shape variables move the surface by up to
   0.18 on a 9.0 chord."*

**A graded number beside this picture is FORBIDDEN** — they are different legs and different solvers, and
a number and a picture on one slide read as the same run.

## WHAT IS NOT VERIFIED

- **R3_control's time-1000 field is NOT graded and NOT verified converged.** Its leg JSON records the same
  `Primal solution failed!` `AnalysisError` as every other leg. The field is non-degenerate and
  physically ranged; that is all that is claimed.
- **The farfield moved far more than the wing** — `inout` median displacement **7.443** against `wing`'s
  **0.0329**. Measured, **not diagnosed**. If a frame shows the outer domain, understand this first.
- **Whether the R3 candidate ever wrote a `2000/` at all is unestablished** — its `endTime 2000` and
  `writeInterval 1000` imply writes at 1000 and 2000, but the evidence is gone.
- **Mach ≈ 0.29 and Re ≈ 5.9e7 are DERIVED by the lane from BCs and thermophysical properties, read from
  no record.** They may not go in a caption on that basis.
- **The point-index correspondence was self-checked**, not assumed: all 1,716 `sym` points remain at
  exactly `|z| = 0` after reconstruction, which a mismatched ordering would have scattered. **PASS.**
- **The render copy is outside git**, so nothing in the repository points at it except this file.
