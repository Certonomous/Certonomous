# VMFL051 — LANE REPORT (`ansys-lane-opus`, Opus 5)

**NOT FILED ANYWHERE. SUBMISSIONS PARKED** (CLAUDE.md rules 7, 8).

On disk in the case directory, on the `ansys-verification-supervisor`'s standing
instruction, because lane addressing failed for other lanes tonight and *a report
that only ever existed in a message is lost when the addressing fails*. The
scratchpad is **not** a fallback for this (rule 13, L-186).

**Status: PRE-REGISTRATION FROZEN, ARMED. Compute authorised by the supervisor after
its own §3 check 4.** This file is updated at completion with the verdict.

---

## 1. THE TWO SHAS THE SUPERVISOR MUST SEE

| what | sha |
|---|---|
| **pre-registration FREEZE COMMIT** | **`22249c824dc38e7fbd22ed34940d703a8bdcf0ab`** |
| **`PREREGISTRATION.md` BLOB at that commit** | **`997bc6cc0aba1554f06e33dee75947cc4e5b8a3e`** |
| grading-path commit (precedes the freeze and all compute) | `dd49dcee476be1b92d48c86155f9f7311aa29427` |
| `grade_vmfl051.py` blob (THE GRADING PATH) | `acad1aff71da4a960045484f9e6f8470f8beccb7` |
| `case/system/topoSetDict` blob (THE FROZEN SAMPLING RULE) | `e594d35fe9aa8accb77bde4a8f3fd335ec2e31d8` |
| Amendment 1 commit (before first compute) | *this commit* |

Verify without `git status` or `git diff HEAD`, which are not valid instruments in
this repository (structural shared-index decay):
`git cat-file -e 22249c82:cases/ansys_verification/VMFL051/PREREGISTRATION.md`,
`git rev-parse 22249c82:cases/ansys_verification/VMFL051/PREREGISTRATION.md`,
`python3 cases/ansys_verification/VMFL051/grade_vmfl051.py --verify-frozen dd49dcee`.

## 2. The case

**VMFL051: Isentropic Expansion of Supersonic Flow Over a Convex Corner**, Ansys
Fluid Dynamics Verification Manual Release 2026 R1, **pp. 165–166**. The team's first
compressible/supersonic case. OpenFOAM v2606 `rhoCentralFoam`, planar 2-D, inviscid
perfect gas, three-level Roache family at r = 2 exactly.

## 3. The gate and the reference

- **THE GATE:** |M_lab − **3.2370**| / 3.2370 ≤ **0.005 (0.5 %)** at L3, against the
  manual's own printed target (Table .51.1).
- **γ derived from the manual's OWN Cp = 1006.43 and MW = 28.966**, with OpenFOAM
  v2606's own `RR = 1e3·N_A·k = 8314.47006650545`:
  R = **287.04239682750293** J/(kg·K), **γ = 1.3990093734749485 — not 1.4.**
- **M₂ exact, this gas = 3.2355411372251863** (−0.04507 % vs the printed target).
- M₂ exact at γ = 1.4 = 3.2368431056638845 (−0.004847 %).
- **DIAGNOSTIC, never the gate:** 0.25 % against the exact value.

**Tolerance derivation (not a round number):** 0.5 % sits between a computed floor of
**0.0605 %** (gas-model bias 0.04507 % + the target's own print rounding 0.01545 %) and
the O(1 %) failure mode it must catch; it is the manual's own 3 % goal ÷ 6, justified
because this target is closed-form exact. It is a real bar — Fluent's own −0.1668 %
passes with 3× margin, but a result three times worse than Fluent's fails.

## 4. Cost, four numbers (L-291)

| component | point | ceiling |
|---|---|---|
| executed compute | **11.3 core-min** | **28 core-min** (enforced by `timeout` in the run script; supervisor authorised 30) |
| lane wall, run-and-grade | 20 lane-min | 40 lane-min |

Dollars **$0.00966** at the point estimate, **derived at $0.0513/core-h, NOT
measured** (`COMPUTE_BUDGET_CHARTER.md` §5).

## 5. Three defects found in the manual (§1a of the pre-registration)

1. p. 165 calls the flow **"incompressible"** while the same page's Physics/Models
   line says "Compressible, inviscid flow". Quantified: an incompressible treatment
   gives no Mach change at all, −22.77 %, failing the gate by 45×.
2. **The printed target 3.2370 is not the exact value at either candidate γ.** It
   matches a **2-decimal ν-table lookup** (ν₂ = 54.12°/54.13° give 3.23664/3.23721)
   and corresponds to a turn of **15.00276°**, not 15°. Generalises: *the manual's
   printed targets may be table lookups, not closed-form evaluations.*
3. Table .51.2 sits under "Results Comparison for Ansys CFX" but its value column is
   headed "Ansys Fluent". Typographic.

All three drafted for `LESSONS` / `NUMERICS_KNOWLEDGE` (family `N-AV`), stamped
**`NOT FILED`** — contacting Ansys is Sanaa's alone.

## 6. Amendment 1 (before first compute) — N-AV7 and N-AV9

- **N-AV7.** The pre-registration now registers, in advance and without predicting
  which will occur, what each Roache outcome MEANS, on the self-scaling criterion
  **dev_extrap ≤ GCI_fine** with **ρ = dev_fine/GCI_fine** printed beside it. The
  load-bearing point: **the extrapolate is read against `M₂_EXACT_GAS`, never against
  the printed 3.2370** — reading it against the printed target would attribute the
  manual's own 0.04507 % table offset to discretisation, which is N-AV7's failure in
  this case's clothing.
- **N-AV9.** **This case is a PLANAR 2-D slab, not an axisymmetric wedge** — verified
  against the committed dictionary: all vertices at z = ±0.01, front/back a single
  `type empty` patch, the token `wedge` absent. **The `sin(t)/t` deficit is exactly
  zero here.** Its structural lesson is carried instead by two named terms that
  refinement cannot remove: the **gas-model term (0.04507 %)** and the **corner
  singularity** (not bounded in advance, and named now so it cannot be invented later).

## 7. VERDICT

**PENDING** — not yet run. Updated here at completion, together with the register row
and the `docs/COST_CALIBRATION.md` C-row.
