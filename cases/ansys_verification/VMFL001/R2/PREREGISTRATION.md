# VMFL001-R2 — Flow Between Rotating and Stationary Concentric Cylinders: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN.** This file is frozen **before any solver starts** (CLAUDE.md rule 2;
`SUPERVISION_CHARTER.md` §3 check 4). At the moment of writing, **`verification/runs/
ansys_verification/VMFL001/R2/` does not exist** — checked, not assumed, with `ls -d`
at 2026-08-24T18:03:32Z, which returned *No such file or directory*; the directory
holds **0 files** and none of `L1_16x64` / `L2_32x128` / `L3_64x256`. **Launch
authorisation comes from the `ansys-verification-supervisor` after its own personal
freeze verification and its own read of the comparator diff, and no agent message is
Sanaa's consent** (CLAUDE.md rule 9).

**Drafted 2026-08-24 by `ansys-lane-opus48` for the `ansys-verification` team**, on
the supervisor's dictation, under `ANSYS_VERIFICATION_CHARTER.md` §5 and
`VERIFICATION_CHARTER.md` §6 (a re-run after a repair is a **new rung** that **cites
the old one**; it does not re-grade the old run's tree). `RESULTS.md` is written
afterwards in this directory and **does not revise this file**; departures land as
dated addenda at the foot, never by editing above.

---

## 0. What this rung is, and why it is a NEW row

This is **VMFL001-R2**, the re-run of VMFL001 after **run 1 returned `NOT A RESULT`**.
Per `VERIFICATION_CHARTER.md` §6, a re-run after a repair is a **new row** in the
register that **cites** the row it repairs; run 1's `NOT A RESULT` is never removed,
re-labelled or softened. The gate, tolerance, exact-formula diagnostic, mesh levels,
solver settings and Roache triple quantity are **UNCHANGED** from run 1's
pre-registration; only two things move, and both are repairs of the two mechanisms
that made run 1 `NOT A RESULT`:

1. **the comparator's reader** is matched to what OpenFOAM v2606 actually writes; and
2. **the finest level's endTime** is raised from 3000 to 6000 iterations so L3 meets
   the registered iterative-convergence clause.

## 1. Run 1, cited exactly (the row this rung repairs)

| what | value |
|---|---|
| run-1 pre-registration | `cases/ansys_verification/VMFL001/PREREGISTRATION.md`, frozen blob **`d6ea5de9286ad5c8699b6e709e105c2cd484e8c1`** (with Amendment 1, pre-compute) |
| run-1 RESULTS | `cases/ansys_verification/VMFL001/RESULTS.md` |
| run-1 verdict | **`NOT A RESULT`** |
| register row | **#1**, `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` |
| run-1 commits | `ae30f914` (artifacts: three levels complete, 1.9833 core-min measured) and `dee5870d` (VERDICT `NOT A RESULT`; register row #1; calibration C-37) |
| run-1 cost | **1.9833 core-min** measured (L1 2 s, L2 13 s, L3 104 s wall, serial); **$0.0017 derived**, not measured |

**The two mechanisms that made run 1 `NOT A RESULT`, either sufficient alone**
(run-1 `RESULTS.md` §1):

1. **The frozen comparator REFUSED (exit 2).** It was frozen to read a file named
   `<field>_<setName>.<ext>` (e.g. `U_gateAxis.raw`) carrying a `#` column header.
   OpenFOAM v2606's `sets`/`raw` writer instead writes the sampled set **headerless**
   as `postProcessing/<fo>/<time>/<setName>_<fields alphabetical>.<ext>` — the real
   files are `gateAxis_p_U.xy` and `azimuthCheck_p_U.xy`, seven columns
   `x y z p U_x U_y U_z`, no `#` line. The reader could not find its file and refused
   rather than guess a column — the correct behaviour, and the repair is the reader,
   not the discipline.
2. **The finest level L3 failed the registered iterative-convergence clause**
   (run-1 `PREREGISTRATION.md` §7): its **final `Ux` initial residual was
   `1.19876e-06` > `1e-6` at iteration 3000**, and its probe plateau peak-to-peak was
   **`2.772e-05` m/s > `1e-6` m/s**. Under CLAUDE.md rule 5 step 1 this makes the rung
   `NOT A RESULT` **before the Roache triple is classified**, so a repaired parser
   alone would not have rescued run 1. L1 and L2 had already converged to `1e-14` and
   `1e-12` at 3000 — they need no change.

## 2. UNCHANGED from run 1 — stated by reference to blob `d6ea5de9`, values repeated

Everything in this section is **identical** to run-1 `PREREGISTRATION.md`
(blob `d6ea5de9`) and is repeated here so the freeze is self-contained. **None of it
is chosen after seeing any R2 number — there is no R2 number.**

**The reference (analytical, White §3-2.3):**
v_θ(r) = ω R_i² (R_o² − r²) / ( r (R_o² − R_i²) ), with ρ = 1 kg/m³, μ = 2.0×10⁻⁴
kg/m-s (ν = 2.0×10⁻⁴ m²/s), R_i = 17.8 mm, R_o = 46.28 mm, ω = 1 rad/s (manual p. 15).

**The manual's printed targets (the gate is set against these), manual Table .01.1:**

| location | manual target, m/s | exact v_θ, m/s (6 s.f.) |
|---|---|---|
| r = 20 mm | 0.0151 | 0.0151201 |
| r = 25 mm | 0.0105 | 0.0105336 |
| r = 30 mm | 0.0072 | 0.00718656 |
| r = 35 mm | 0.0046 | 0.00454781 |

**THE GATE (unchanged):** at the finest level L3, for **all four radii**,
| v_lab(r) − v_manual_target(r) | / | v_manual_target(r) | ≤ **0.02**. All four inside
⇒ gate met; any one outside ⇒ **`GATE FAIL`**. Justification unchanged: the manual's
printed targets are rounded (worth up to 1.148 % at 35 mm), Ansys's own worst reported
ratio is 0.976, and the manual's own stated goal is 3 % — 2 % is deliberately tighter.

**The diagnostic (unchanged, and NOT the gate):** against the exact formula,
| v_lab(r) − v_exact(r) | / | v_exact(r) | ≤ **0.005** at all four radii, printed beside
the gate. A row that meets the gate and misses the diagnostic is a `PASS` with the
diagnostic printed beside it.

**The mesh levels (unchanged):** `L1_16x64` (16×64, 1024 cells), `L2_32x128`
(32×128, 4096), `L3_64x256` (64×256, 16384); refinement ratio 2 exactly in both
directions; `blockMeshDict.template` blob **`45286819…`** (byte-identical to R1).

**The Roache triple quantity (unchanged):** v_θ at **r = 35 mm**, the manual's
worst-agreement point; Fs = 1.25; classification thresholds (EPS_ABS 1e-12,
STAG_TOL 1e-3) unchanged.

**The solver settings (unchanged):** OpenFOAM v2606 `simpleFoam`, steady laminar,
full 360° planar annulus, `innerWall` `rotatingWallVelocity` ω=1 axis (0 0 1),
`outerWall` `noSlip`, `frontAndBack` `empty`; `fvSchemes` blob **`b22740ae…`**,
`fvSolution` blob **`6f88ec55…`**, `0/U` blob **`fd65259a…`** — all byte-identical to
R1. `constant/transportProperties` ν = 2.0e-4 (blob `bd490e11…`), `turbulenceProperties`
`laminar` (blob `6d5b3af6…`), `0/p` (blob `10de5943…`) — all byte-identical to R1.

## 3. WHAT CHANGED, and why — the whole of it

### 3.1 The reader, matched to v2606's actual writer

The comparator's file-finder and reader are repaired to read exactly what the run
produced, verified against run 1's real output on disk. Each change is marked
`# R2 CHANGE:` in `grade_vmfl001_r2.py`, and the diff against the R1 comparator
(blob `8cb29610`) shows **only** the marked hunks (audited: 15 hunks, every one
carrying an `R2 CHANGE` marker):

- **(a)** `find_set_file` locates `postProcessing/*/<endTime>/<setName>_*.xy`,
  requires **exactly one** hit, and **derives the column layout from the filename**:
  coords `x y z`, then each field after the set name in the order written, scalar 1
  column, vector 3 (`p`→1, `U`→3), so `gateAxis_p_U.xy` ⇒ `x y z p U_x U_y U_z`. It
  **REFUSES** if the filename's field list is not exactly `{p, U}` in some order, or
  (in `read_raw_set`) if a data row's width ≠ 3 + Σ field widths.
- **(b)** `read_raw_set` accepts a **headerless** file when the layout is supplied by
  (a), and still refuses a file whose rows disagree in width (and still honours a `#`
  header if one is ever present).
- **(c)** `plant_into_raw` plants `PLANT = 1.234e-3` m/s into the **derived `U_y`
  column index** (index 5 of `x y z p U_x U_y U_z`).
- **(e)** `RUN_ROOT` and `OUT_JSON` move under `…/VMFL001/R2`
  (`GRADING_VMFL001_R2.json`).
- **(f)** the `--selftest` gains a fixture written in the **REAL** v2606 format
  (headerless, `gateAxis_p_U.xy` naming) and a new `--dryrun-reader <path>` mode that
  runs the reader on a real file and prints **only** whether it parsed and the row
  count — never a value.

**Pre-freeze external-reader check (the lesson from run 1).** Before this freeze, the
repaired reader was run once on run 1's own L1 sampled file:

```
python3 cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py --dryrun-reader \
  verification/runs/ansys_verification/VMFL001/L1_16x64/postProcessing/radialProbes/3000/gateAxis_p_U.xy
→ dryrun-reader: parsed, 4 rows
```

**`parsed, 4 rows`** — the reader now sees the real writer's output (4 gate radii = 4
rows), which is precisely what run 1's frozen reader could not do. This is a
provenance/format check on the reader, **not** a physics result, and it never prints
a velocity. The full `--selftest` (exact formula, headerless reader, width-refusal and
bad-field-list refusal, planted-zero both arms, Roache classifier, gate both arms)
passed all checks at the comparator's commit, with zero solver compute.

### 3.2 Per-level endTime, from a decay fit fixed BEFORE this run — change (d)

**(d)** the comparator carries a per-level endTime
`ENDTIME_BY_LEVEL = {L1_16x64: 3000, L2_32x128: 3000, L3_64x256: 6000}`, and strict
completion checks each level's `ExecutionTime` count == that level's endTime and last
time == it. The run script substitutes the per-level endTime into `controlDict` from
`controlDict.template` (an `__ENDTIME__` placeholder on both `endTime` and
`writeInterval`, sed'd per level with a survivor-refusal assertion).

**The fit, and N, chosen from run 1's log alone (no R2 run exists).** From run 1's
`L3_64x256/log.simpleFoam`, the `Ux` initial residual over the **last 1000
iterations** (Time 2000→3000) fits log10(residual) vs iteration as a straight line:

- **slope = −9.6065×10⁻⁴ decades/iteration** (≈ **0.96 decades per 1000 iterations**),
  intercept −3.0398;
- extrapolated, the residual reaches **1e-6 at ~3081**, and **1e-8 at ~5163**
  iterations;
- **N is set so the extrapolated residual is < 1e-8** (two decades of margin below the
  registered 1e-6 criterion), **rounded up to a multiple of 1000 ⇒ N = 6000**;
- predicted residual at N = 6000: **≈ 1.57×10⁻⁹** — comfortably below 1e-8.

L1 and L2 keep endTime 3000 (already at 1e-14 / 1e-12 at 3000). **This fit and N were
fixed before any R2 solver ran**, from run 1's disk, and they change no gate,
threshold, cap or label — only how many iterations L3 is allowed so its registered
convergence clause can be met.

## 4. THE VERDICT ORDER (CLAUDE.md rule 5), restated

1. any level not iteratively converged (final `Ux`/`Uy`/`p` residual < 1e-6 **and**
   probe plateau ptp < 1e-6 m/s over the last 20 %) or not plateaued ⇒ **`NOT A
   RESULT`**;
2. Roache triple on v_θ(35 mm) `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` ⇒
   **`NOT A RESULT`**, with the three values, R and both triples printed beside it;
3. `CONVERGING` ⇒ **`PASS`** inside the 2 % band else **`GATE FAIL`**, GCI at Fs = 1.25
   printed. No GCI is quoted when the three values are not monotone. The gate can only
   turn a PASS/GATE FAIL **into** `NOT A RESULT`, never the reverse.

## 5. Planted-zero control (CLAUDE.md rule 3), restated

The comparator copies the finest level's sampled `gateAxis_p_U.xy` to a temp tree,
adds `PLANT = 1.234×10⁻³` m/s to the **derived `U_y` column** of the r = 35 mm row,
reads it back from disk, and re-runs the same extraction. The extracted v_θ(35 mm)
must move by exactly PLANT (to 1e-15 m/s) and no other radius may move; otherwise the
comparator **refuses (exit 2)**. The run tree is never modified — only the temp copy.

## 6. Strict completion (CLAUDE.md rule 4), restated with the per-level endTime

The comparator refuses (exit 2) on any failed clause: `rc = 0`; an `End` line;
**last time == that level's endTime** (L1/L2 3000, L3 6000); fields `U` and `p`
present at endTime; **`ExecutionTime` count == that level's endTime**; and the **age
guard** — every field at endTime strictly newer than the case's own `0/U`, touched
immediately before launch. The run script refuses to start into any pre-existing
level directory, refuses unless this pre-registration is committed at HEAD, and
enforces the cap with `timeout`.

## 7. Cost (CLAUDE.md rule 12)

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| basis | run 1's **measured** per-level wall times: L1 2 s, L2 13 s, L3 104 s per 3000 iterations |
| scaling | L1, L2 unchanged (3000 iters); **L3 scaled by N/3000 = 6000/3000 = 2 ⇒ 104 × 2 = 208 s** |
| **estimate** | wall 2 + 13 + 208 = **223 s = 3.72 core-min** (3.7167) |
| **CAP** | **10 core-minutes** = ⌈2.5 × 3.7167⌉ = ⌈9.29⌉, enforced by `timeout` inside `run_vmfl001_r2.sh`; **an overrun STOPS the run and it does not get a new budget** |
| dollars at the estimate | **$0.003178** (3.7167 core-min ÷ 60 × $0.0513/core-h) |
| dollars at the cap | **$0.008550** |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). The wall-time basis is run 1's measurement; the L3 scaling is an estimate, not a measurement. |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; **this is a per-item cost, not a new ceiling** (rule 9) |
| calibration | at completion, actual core-minutes from `RUN_RC.txt`/`COST.txt` against this estimate, ratio and attribution, one row appended to `docs/COST_CALIBRATION.md` (rule 12) |

## 8. The grading path, frozen (VERIFICATION_CHARTER §2d)

The comparator, run script and case were **committed BEFORE this file** (commit
`a37170a9`, "VMFL001-R2 inputs and comparator … NO COMPUTE, prereg not yet frozen"),
and both commits precede any solver. At analysis time the grading path is re-hashed
against these shas; a freeze that is claimed and not checked is a claim about intent.

| what | path | committed blob sha |
|---|---|---|
| **comparator** | `cases/ansys_verification/VMFL001/R2/grade_vmfl001_r2.py` | **`64b02be807a8adb6c2638fe739c55f735c8259ca`** |
| run script | `cases/ansys_verification/VMFL001/R2/run_vmfl001_r2.sh` | `116c7c2d5fc5ebe1ac742f69478d66ed37dbfc17` |
| controlDict template (per-level endTime) | `case/system/controlDict.template` | `ecb4514c62b5d2e14baac90c16b7ea9d3d675749` |
| blockMeshDict template | `case/system/blockMeshDict.template` | `45286819aa46b5df7fc0b938da1694ebdeb03068` (= R1) |
| fvSchemes | `case/system/fvSchemes` | `b22740ae317a6eb5ca7e67feca94699e27e15dcf` (= R1) |
| fvSolution | `case/system/fvSolution` | `6f88ec556d6e4725986565b02f8dfea73e4d405a` (= R1) |
| `0/U` (BCs + age-guard marker) | `case/0/U` | `fd65259adff3152407a40e4decf6191d6dd2e350` (= R1) |
| `0/p` | `case/0/p` | `10de59431bdcf5d7d1d27e29f219b49f32e5da1a` (= R1) |
| transportProperties | `case/constant/transportProperties` | `bd490e1105d34e8672cd5251dabd27614d4d5051` (= R1) |
| turbulenceProperties | `case/constant/turbulenceProperties` | `6d5b3af67a1fa836a5a9ac06235d34db6fbdd73e` (= R1) |

**Run outputs go to `verification/runs/ansys_verification/VMFL001/R2/<level>/`**,
never beside this prose (FILING_CHARTER R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL001/R2/GRADING_VMFL001_R2.json`.**

**What the comparator has NOT been exercised on, stated plainly.** No R2 solver has
run, so its full OpenFOAM-output parsing on a live R2 tree is untested. What *has*
fired, with zero R2 solver compute: the `--selftest` (all checks passed) and the
`--dryrun-reader` on run 1's real L1 file (`parsed, 4 rows`, §3.1). If the comparator
cannot parse the real R2 output at grade time, it refuses and the rung is `NOT A
RESULT` — it never guesses a column. Any change to the parser after the first R2 solve
is a dated addendum disclosing exactly what changed and whether it could move a number,
read by the supervisor before any re-grade.

## 9. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). **Nothing about Ansys** — Ansys's numbers are context
(run-1 §2.3); this box has no Fluent and no CFX, and no VM2026R1 archive was opened to
write this file. **Nothing about the transport properties** beyond the comparator's
provenance checks (the gated v_θ cannot see μ or ρ). The verdict is a statement about
this lab's solver against the manual's reference result, and only a `PASS` is a
credential; a `GATE FAIL` is a finding that is never removed or softened.
