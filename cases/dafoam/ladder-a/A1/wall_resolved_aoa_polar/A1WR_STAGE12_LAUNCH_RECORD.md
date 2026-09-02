# A1WR STAGES 1–2 + MAAOA — LAUNCH RECORD (2026-09-02, dafoam lane)

Sanaa's order (verbatim in
`etc/sessions/2026-09-02T1900Z_sanaa_fine_sweeps_launch_order.md`, both
messages): launch the fine-grid 0–18° sweeps for both solvers NOW; then the
(Ma, AoA) sweep for both; durable — *"even if the fleet dies, they still
run"*; parallel; **lift kept fixed**; fine mesh; **the PATCHED build**;
immediate, box filled minus filming headroom. Her explicit exception to the
demo freeze. **Nothing was ever launched on the unpatched build.**

## What launched, and how it survives fleet death

**Fire history, disclosed — three fires, every failure at its own guard,
0.0 solver iterations wasted:**
- **Fire 1** (18:09/18:10Z, prereg `07667a58`): the staging cleanup glob
  `[0-9]*` matched `0.orig` and both chains failed closed at their
  point-of-use asserts before any container existed; 0.0 core-min. ADDENDUM
  D / MAAOA AMENDMENT 1 (`80e1b91a`); archived at
  `…/A1WR/STAGE12_failed_staging_20260902T180915Z`.
- **Fire 2** (18:13:25Z, prereg `80e1b91a`): DAFoam's internal `DACheckMesh`
  default `maxAspectRatio = 1000` refused the §13.7-dispositioned
  single-cell-span AR (212,104 at L3), and the compressible script's physics
  self-assert split literals still named D19M; **the Stage-1 gate REFUSED
  fail-closed at 1.02 core-min, zero solver iterations, and MAAOA took its
  registered `BLOCKED` branch at 0.0** — the chain's own protections, doing
  their jobs. ADDENDUM E / MAAOA AMENDMENT 2 (`586b72ca`); archived at
  `…/A1WR/STAGE12_failed_meshcheck_20260902T181325Z`. Repairs proven
  pre-fire: planted staging fixture; no-solve model build on the real L3
  mesh in the patched image (`AOAC_PHYSICS_MD5_PASS`, dispatcher reached).
- **Fire 3** — the live one, rows below. **Stage 1 COMPLETED and the gate
  PASSED at 18:35:58Z**: field-exact y+ at α = 18 after the fixed 1,500
  iterations, min/max/avg — incompressible **0.00054 / 0.03679 / 0.00982**,
  compressible **0.00226 / 0.90466 / 0.21980**; both arms under the frozen
  1.0 threshold (the compressible arm by 9.5 % — v1.1's 0.203 prediction was
  4.5× optimistic, which is precisely why the probe was registered), the two
  channels agreeing to ~1e-10 relative. Stage-1 spend 15.38 + 16.37 =
  **31.75 core-min against the 120 cap**. Stage 2's 8 units launched
  18:35:58–18:36:01Z on cores 8–15; MAAOA read the PASS at 18:36:40Z and
  launched its 6 compressible points on cores 2–7 (INCOMP queues for the
  first freed core). **14 solver containers live at 18:36:48Z — the box is
  full, per her "immediate" order, with cores 0–1 unpinned.**

| item | queue entry (now in `launched/`) | governing freeze | launch |
|---|---|---|---|
| A1WR stages 1–2 | `verification/queue/dafoam/launched/A1WR_chain.json` | `A1WR_PREREGISTRATION.md` v1.6 (Addenda C–E) at commit `586b72caf39dad1f79b028cf590818da585688a2` | daemon tick after 18:19:06Z; pid in `LAUNCH_LOG.tsv` and the entry's `_launch` block |
| MAAOA fixed-lift (Ma, AoA) | `verification/queue/dafoam/launched/MAAOA_chain.json` | `MAAOA_PREREGISTRATION.md` + Amendments 1–2 (both pre-compute) at the same commit | next daemon tick after item 1 (her sequencing: "Once that is launched") |

Both are OS processes started by the queue daemon (`scripts/queue_runner.py
--daemon`, pid 1645): no agent holds them. Every solver deadline sits
**inside its docker container**, so caps stop runs even if the drivers die.

## The gating no agent touches

- **A1WR:** probe (α = 18, fixed 1,500 iters, both arms, L3) → `a1wr_stage1_gate.py`
  writes `…/A1WR/STAGE12/stage1_gate.json` → Stage 2's 8 units launch **only
  on PASS**; `GATE FAIL` (y+max ≥ 1.0) stops with the wall-resolved claim
  withdrawn, mesh **not** re-cut; `REFUSED` (blind channel) stops as
  unmeasured.
- **MAAOA:** its driver polls that same gate file (60 s, 12 h bound) and
  launches nothing before `PASS`; upstream failure ⇒ `BLOCKED`, spend 0.0.

## Layout and filming headroom (16 vCPU, measured 30 GiB)

- A1WR: cores **8–15** (2 probes → 2 sweeps + 6 colds, all np = 1, one core
  each, `OMP_NUM_THREADS=1`, docker mem 4g/3g, MemAvailable floor 4.0 GiB).
- MAAOA: pool **2–7** (≤ 6 concurrent trim points, np = 1, 3g, floor 6.0 GiB
  → self-staggers behind A1WR's peak hour).
- **Cores 0–1 carry no pin from either item** — that plus every solver being
  hard-pinned off 0–1 is the filming headroom; the demo server on :8765 was
  not touched. Peak pinned load = 14 cores for roughly the first hour (colds
  + trim points), settling to 2–3 pinned cores for the ~7-hour serial sweeps.

## Registered cost (rule 12)

| item | estimate (EXTRAPOLATED, anchors MEASURED) | caps |
|---|---|---|
| A1WR stages 1–2 | 932.4 core-min | stage 1 = 120; stage 2 = **800/arm** (allocated 785 + conditional 55 duplicate); entry cap 1,720 |
| MAAOA | 315 core-min | 120/point; item 900 |
| instrument checks on foreign/scratch artifacts (Addenda C §15.4, E) | ~2.6 core-min spent | — |
| fires 1–2 container startup (zero solver iterations) | 1.02 core-min spent | reported, not absorbed |

Dollars DERIVED at c7a.4xlarge $0.0513/core-h (owner-stated, not measured):
caps 2,620 core-min = $2.24. Estimate-vs-actual calibration rows are **OWED**
to `docs/COST_CALIBRATION.md` at each completion, contention attributed
separately.

## The fixed-lift interpretation, as frozen (for Sanaa to confirm or correct)

> At every operating point the wing is TRIMMED in angle of attack to the
> lab's fixed lift target CL = 0.5 (the D19-family target), so the Mach sweep
> reports the trim angle α(Ma) and the drag at fixed lift CD(Ma; CL = 0.5);
> "for both" means both solver arms, with the incompressible arm running its
> fixed-lift trim at its single regime as the control — a Mach axis exists
> only in the compressible arm and no incompressible Mach axis is fabricated.

Her correction lands as a **pre-compute amendment** to
`MAAOA_PREREGISTRATION.md` while MAAOA waits on the A1WR probe (its freeze
window is open until its first solver runs). The plain 0–18° polars
inherently sweep lift; the fixed-lift clause binds the (Ma, AoA) item.

## Where the state lives (this record replaces a LAB_STATE edit)

`docs/LAB_STATE.md`'s dafoam section is supervisor-owned with a section-stamp
discipline; a lane edit would not be a pure insertion, so the live state is
carried here and in: `STATUS.A1WR_chain(.log)` beside this file,
`STATUS.MAAOA_chain` beside the MAAOA prereg, `…/A1WR/STAGE12/` and
`…/MAAOA/` (chain ledgers, gate json, reader outputs, COST files), and
`verification/queue/LAUNCH_LOG.tsv`.

**NOTHING IN EITHER ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**
