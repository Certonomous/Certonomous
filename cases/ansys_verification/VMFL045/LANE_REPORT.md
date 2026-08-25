# VMFL045 — lane report to `ansys-verification-supervisor`

**From:** `ansys-lane-opus48` (Opus 4.8). **Date:** 2026-08-25.
**Delivery:** FALLBACK per L-306 — `SendMessage` to `ansys-verification-supervisor`
returned *"No agent named 'ansys-verification-supervisor' is reachable"* on every
attempt (you can reach me; I cannot reach you). This committed file is the report of
record. Nothing here is sent outside the box.

**HEADLINE: the pre-registration is FROZEN and was ACCEPTED by you; compute was
AUTHORISED by you and I LAUNCHED it; rhoCentralFoam CRASHED at L1 start (rc=1,
wall=0 s). This is a CRASH-FINDING pending your triage. I did NOT repair the frozen
inputs and did NOT re-run — triage and the repair decision are yours.**

---

## 1. Freeze (accepted by you)

- Inputs+comparator commit **`2198f9b2`** (NO COMPUTE); freeze commit **`6a9701e1`**
  (PREREGISTRATION.md only). `grade_vmfl045.py --verify-frozen` passes; `--selftest`
  45 ok / 0 FAIL.
- **Gate G-VMFL045:** at L3_360x304, |M_lab − 1.874|/1.874 ≤ 1.0 % (manual printed
  target Mach, Tables .45.1/.45.2).
- **Exact reference (derived, full double precision, as-modelled velocity BC → M₁ =
  2.501814636762496, γ = 1.4):** β_weak = 36.92317760072534°, **M₂ =
  1.8749769576810524**, T₂ = 382.1100763833985 K, ρ₂ = 2.2778835945694422. Weak root
  confirmed (M₂ > 1; detachment θ_max = 29.82°). Cross-checked vs NACA 1135 and the
  M=2 normal-shock relations.
- **Cells:** L1 6,840; L2 27,360; L3 109,440 (r = 2 by construction).
- **Cost:** point 20.4 core-min, cap 48 core-min (serial, timeout 2880 s). Dollars
  DERIVED: $0.01745 / $0.04104.
- **Plateau hazard** addressed four ways (§7): 8.6 flow-throughs (vs VMFL051's 4),
  per-level plateau clause as arbiter, tol 19× tighter than the gate, volume average.
- **Expected observed order p ≈ 1** (shock capture), stated before compute.

## 2. Manual findings recorded before compute (drafted for docs / N-AV; NOT FILED)

1. **Under-specification:** no Cp in the VMFL045 section → γ fixed at 1.4 from the
   case's over-determined inlet data (ρ₁ = p₁/RT₁ matches 1.22 to 2.3e−5; oblique
   relations at γ = 1.4 reproduce all three targets to <0.03 %); Cp = 1004.8565342807
   set to realise it.
2. **Internal inconsistency:** velocity BC 852.68 implies M₁ = 2.5018, but the target
   table was computed at M₁ = 2.5 exactly (fits ~3× better). We honour the velocity
   BC; the 0.0521 % offset is budgeted in §3.3.
3. **Under-specified geometry** (domain figure absent from text) → reconstructed in §4.

Gate note (frozen, restated per your request): this 1 % gate would **FAIL** Ansys
Fluent's own reported Mach (1.902, +1.494 %) and **PASS** CFX's (1.871, −0.160 %). A
near-Fluent lab value is a `GATE FAIL` and will not be narrated as agreement with
Ansys.

## 3. THE RUN AND THE CRASH-FINDING

**Launch:** authorised by you; my own pre-launch check clean (no run dir, no solver,
prereg committed at HEAD); launch-time load 2.07 on 16 cores. `run_vmfl045.sh` ran
serial.

**What succeeded on L1_90x76:** `blockMesh` OK; `checkMesh` **Mesh OK** (max
non-orthogonality 14.9°, max skewness 0.398, max aspect ratio 1.49 — a clean mesh);
`topoSet` filled both frozen zones — **gateZone 252 cells, gateZoneInner 148 cells**,
matching the pre-registration's predicted ~252. The frozen sampling rule is sound.

**What failed:** `rhoCentralFoam` returned **rc=1 at wall=0 s** — it crashed inside
the first pseudo-timestep (deltaT = 1.2e−8), before any real solve, with:

> `FOAM FATAL IO ERROR: Entry 'e' not found in dictionary
> "system/fvSolution/solvers"` (dictionary.C:457)

The launcher correctly **refused (exit 2)** — "a crash is a finding, triage before
anything else" — and never proceeded to L2/L3. The comparator, run against the tree,
correctly **refuses (C1, rc=1)** and does not grade. Both instruments behaved.

### Triage (confirmed, not inferred)

With `energy sensibleInternalEnergy`, the thermo energy field is **`e`**. When the
viscosity is **nonzero**, `rhoCentralFoam` performs a viscous energy diffusion
correction that solves a linear system for `e`, and therefore requires a solver entry
named `e` (or a regex covering it) in `fvSolution/solvers`. The frozen `fvSolution`,
cloned from VMFL051, provides **`h`** and no `e`.

**The load-bearing difference from VMFL051, verified against HEAD:**

| | viscosity | viscous energy corrector | `fvSolution/solvers` energy entry | outcome |
|---|---|---|---|---|
| VMFL051 | **mu = 0** | **skipped** (inviscid) | `h` only | ran (the missing `e` was **latent**) |
| VMFL045 | **mu = 1e-8** (manual's own) | **runs** (mu ≠ 0) | `h` only | **crash: no `e`** |

So VMFL045 honouring the manual's stated nonzero viscosity exercised a code path
VMFL051's `mu = 0` never touched, exposing that the inherited `fvSolution` is
incomplete for the viscous energy equation. **This is a setup defect in the frozen
inputs, not a numerical failure of the case.** (Also worth a lesson: a case cloned
from an inviscid precedent silently inherits an `fvSolution` incomplete for the
viscous path — latent until a nonzero viscosity invokes the energy corrector.)

### Candidate repairs — for YOUR decision (I did not apply any)

All three touch **no gate, threshold, cap, label or reference** — only a linear-solver
dictionary entry — but each changes a frozen grading-path blob (`fvSolution`, §10), so
it is a `VERIFICATION_CHARTER.md` §2d.1 repair decision and yours to make:

- **(a)** widen the energy entry to a regex, `"(h|e)"`, so it serves whichever energy
  variable the thermo selects (most robust; matches the OpenFOAM idiom);
- **(b)** rename the `h` entry to `e` (matches `sensibleInternalEnergy` exactly);
- **(c)** switch `energy` to `sensibleEnthalpy` so the existing `h` entry is correct
  (changes the thermo, larger footprint — not recommended).

My recommendation is **(a)**. Whichever you choose, the failed L1 directory must be
cleared first (launcher guard 1 refuses to run into an existing level dir), which is
also your call, and the repair would re-freeze `fvSolution` under §2d.1 with a dated
addendum to the pre-registration that alters no gate.

### Cost / contention

The run consumed effectively **0 core-min** (crash at wall = 0 s), so the
controlled contention comparison against VMFL051's 2.06× did not happen — there was no
real compute to time. `CONTENTION.txt` in the run root records the launch sample
(01:36:38Z, load 2.07/2.39/5.68) and the end sample; no mid-L3 sample exists because
L3 was never reached. No cost-calibration row is warranted for a zero-compute crash;
one will follow the successful re-run.

### What I did NOT do (reserved to you)

I did not edit the frozen `fvSolution` or any frozen input; did not clear the failed L1
dir; did not re-run; did not grade (the comparator refuses); did not write a register
row or a verdict — a crash is a finding until your triage says otherwise, and I have
recorded it as one.

## 4. Run-tree state

`verification/runs/ansys_verification/VMFL045/L1_90x76/` exists with `0/`, `constant/`,
`system/`, `postProcessing/`, `log.blockMesh`, `log.checkMesh`, `log.topoSet`,
`log.rhoCentralFoam` (the fatal), `RUN_RC.txt` (rc=1). No time directories, no fields.
L2 and L3 were never created. `verification/runs/…/VMFL045/COST.txt` was not written
(the launcher refused before the summary).
