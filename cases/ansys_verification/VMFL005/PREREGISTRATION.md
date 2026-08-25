# VMFL005 — Poiseuille Flow in a Pipe: PRE-REGISTRATION

**NOT FILED ANYWHERE. Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box, now or
on completion** (CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The
manual is proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**NOT YET RUN.** This file is frozen **before any solver starts** (CLAUDE.md rule 2;
`SUPERVISION_CHARTER.md` §3 check 4). At the moment of writing,
**`verification/runs/ansys_verification/VMFL005/` does not exist** — checked, not
assumed, with `ls -d` at 2026-08-24T18:39Z, which returned *No such file or
directory*; the directory holds **0 files** and none of `L1_100x10` / `L2_200x20` /
`L3_400x40`. **Launch authorisation comes from the `ansys-verification-supervisor`
after its own personal freeze verification and its own read of the comparator diff,
and no agent message is Sanaa's consent** (CLAUDE.md rule 9).

**Drafted 2026-08-24 by `ansys-lane-opus48` for the `ansys-verification` team**, on
the supervisor's dictation, under `ANSYS_VERIFICATION_CHARTER.md` §5 and
`VERIFICATION_CHARTER.md` §6. This is **run 1 of VMFL005** — a fresh case, not a
re-run. `RESULTS.md` is written afterwards in this directory and **does not revise
this file**; departures land as dated addenda at the foot, never by editing above.

---

## 0. What this case is

**VMFL005: Poiseuille Flow in a Pipe** — Ansys Fluid Dynamics Verification Manual,
Release 2026 R1, **p. 25**. Steady laminar fully-developed flow in a circular tube;
the pressure drop is compared against the **Hagen–Poiseuille analytical** result.
This lab reproduces it in **OpenFOAM v2606** on an **axisymmetric wedge** and grades
the pressure drop against the manual's tabulated target with a pre-registered gate,
a Roache grid triple, a planted-zero control and the strict completion rule.

**This is a statement about this lab's solver against the manual's reference result.
It is NOT a statement about Ansys** (`ANSYS_VERIFICATION_CHARTER.md` §2). This box has
no Fluent and no CFX; `poiseuille-flow.cas` and `VMFL005B_VV005CFX.def` were not run,
and no VM2026R1 archive was opened to write this file.

## 1. The manual, quoted verbatim (manual p. 25)

**Test Case** (p. 25): *"Fully developed laminar flow in a circular tube is modeled.
Reynolds number based on the tube diameter is 500. Only half of the axisymmetric
domain is modeled."*

**Material Properties** (p. 25): *Density = 1 kg/m3*; *Viscosity = 1e-5 kg/m-s*.
**Geometry** (p. 25): *Length of the pipe = 0.1 m*; *Radius of the pipe = 0.00125 m*.
**Boundary Conditions** (p. 25): *"Fully developed laminar velocity profile at inlet
with an average velocity of 2.00 m/s."*

**Analysis Assumptions and Modeling Notes** (p. 25): *"The flow is steady. A fully
developed laminar velocity profile is prescribed at the inlet. Hagen-Poiseuille
equation is used to determine the pressure drop analytically."*

**Results Comparison for Ansys Fluent, Table .05.1** (p. 25) — Pressure Drop, Pa:

| | Target | Ansys Fluent | Ratio |
|---|---|---|---|
| Pressure Drop, Pa | **10.24** | 10.22 | 0.998 |

**Results Comparison for Ansys CFX, Table .05.2** (p. 26) — Pressure Drop, Pa:

| | Target | Ansys CFX | Ratio |
|---|---|---|---|
| Pressure Drop, Pa | **10.24** | 10.49 | 1.024 |

The manual's stated accuracy goal (**§1.3, p. 5**, verbatim): *"The goal for the test
cases contained in this manual was to have results accuracy within 3% of the target
solution."*

**Reynolds number check.** ρ V D / μ = 1 × 2.0 × (2 × 0.00125) / 1e-5 = **500** — the
manual's stated value, reproduced exactly by the frozen constants (`--selftest`).

## 2. THE REFERENCE and THE GATE

**The reference (analytical, Hagen–Poiseuille).** For fully-developed laminar pipe
flow, ΔP = 8 μ L V_avg / R² = 8 μ L Q / (π R⁴) with Q = V_avg π R². With μ = 1e-5,
L = 0.1, V_avg = 2.0, R = 0.00125, ρ = 1:

> **ΔP_exact = 10.2400 Pa** (6 s.f.), computed two independent ways in the comparator
> and asserted equal (`--selftest`). This IS the manual's "Target" 10.24 Pa to the
> target's printed precision.

**The manual's printed target (the gate is set against this), Table .05.1/.05.2:**
**ΔP_target = 10.24 Pa.**

**THE GATE:** at the finest level L3,
| ΔP_lab − ΔP_target | / | ΔP_target | ≤ **0.02**. Inside ⇒ gate met; outside ⇒
**`GATE FAIL`**. ΔP_lab = ρ · ( ⟨p⟩_inlet − ⟨p⟩_outlet ), ρ = 1 kg/m³ (§5).

**Tolerance justification (2 %).** Required to be justified from the manual's 3 %
goal, its own reported ratio, and the printed precision of the target:

1. **The manual's stated goal is 3 %** (§1.3, quoted above). 2 % is **deliberately
   tighter** than the goal — the same posture as VMFL001.
2. **The exact value and the target coincide** to the target's printed precision
   (10.2400 vs 10.24). Unlike VMFL001 — whose rounded table targets sat up to ~1 %
   from the exact formula, so part of its 2 % had to absorb target-rounding — here
   there is **no target-rounding gap to spend**, so the full 2 % is available for the
   lab's discretisation error.
3. **The target's own printed precision:** 10.24 Pa is 4 s.f.; the rounding
   half-width is ±0.005 Pa = **±0.0488 %** of 10.24. So the target itself is known
   only to ~0.05 %; a gate far tighter than that would be gating on the target's
   rounding, not on physics.
4. **Ansys's own reported ratios:** Fluent **0.998** (0.2 % below target), CFX
   **1.024** (2.4 % above). A value that overshoots the way CFX's does (**2.4 %**)
   would **FAIL** this 2 % gate — so 2 % is a genuine bar, not a formality; and a
   fully-developed laminar pipe with a **prescribed exact parabolic inlet** on a wedge
   is the most benign convergence case in the tranche, so the lab is expected to land
   near Fluent's 0.2 %, comfortably inside 2 %.

Both Ansys numbers (10.22, 10.49) are **CONTEXT ONLY** in the comparator
(`ANSYS_CONTEXT`), never the gate.

## 3. The exact-formula diagnostic (NOT the gate)

Against the exact Hagen–Poiseuille value (10.2400 Pa), at L3:
| ΔP_lab − ΔP_exact | / | ΔP_exact | ≤ **0.01** (1 %), printed beside the gate. A row
that meets the 2 % gate but misses the 1 % diagnostic is a **`PASS`** with the
diagnostic printed beside it. Because the exact value and the target coincide, the
diagnostic is a strictly tighter restatement of the same comparison and catches a
"passes the loose gate but is physically off" row.

## 4. Mesh levels and per-level endTime

**The mesh levels (axisymmetric wedge, single cell thick, `wedge` front/back).** Flow
along +x, 0 ≤ x ≤ L = 0.1 m; radial 0 ≤ r ≤ R = 0.00125 m. Refinement ratio **2
exactly in both directions**; uniform radial grading; constant cell aspect ratio
dx/dr = 8 across all three levels.

| level | axial × radial | cells | endTime (SIMPLE iters) |
|---|---|---|---|
| `L1_100x10` | 100 × 10 | **1000** | 2000 |
| `L2_200x20` | 200 × 20 | **4000** | 3000 |
| `L3_400x40` | 400 × 40 | **16000** | 6000 |

The wall vertices are placed at **exact radius R** (y_w = R cos 2.5°, z_w = ± R sin
2.5°, so |(y_w, z_w)| = 0.00125 m to machine precision), **not** y = R / z = R tan α,
which would put the wall at R/cos α and bias Hagen–Poiseuille's 1/R⁴ by ~0.19 %. The
wedge idiom is copied from `tutorials/compressible/rhoCentralFoam/LadenburgJet60psi`
(single radial block, axis edge collapsed, `mergeType points`).

**Per-level endTime — an ESTIMATE, fixed BEFORE any run, and stated as an estimate.**
No VMFL005 solver has run, so the iteration counts cannot be measured; they are
scaled from **VMFL001's measured** convergence-rate-vs-cell-count (VMFL001 R1 log:
the ~1000-cell level was below 1e-12 by 3000 iterations; the ~16000-cell level
reached only 1.2e-6 at 3000 and its R2 repair used **6000**). VMFL005 L3 (16000
cells) ≈ VMFL001 L3 (16384 cells) ⇒ **6000**; L1/L2 keep generous margins (2000,
3000). **Honest caveat:** VMFL005 is convection-dominated **open** flow (fixed inlet
velocity, fixed outlet pressure), whose SIMPLE convergence character differs from
VMFL001's **closed** recirculating annulus — it may converge faster, or the high
aspect ratio with GAMG may make the pressure equation slower. The **residual < 1e-6
completion clause (§8) is the actual arbiter**: if a level misses it at its endTime
the rung is **`NOT A RESULT`** and re-runs as a new rung (exactly as VMFL001 R1 → R2),
never re-graded in place. Over-budgeting only costs compute (there is no
`residualControl`, so an already-converged level keeps iterating and stays
converged); it is the safe direction and is chosen deliberately.

## 5. The solver, schemes, and the measurement

**Solver.** OpenFOAM v2606 `simpleFoam`, steady laminar (`turbulenceProperties`
`laminar`), ν = μ/ρ = **1e-5 m²/s** (`transportProperties`). Inlet: **codedFixedValue**
parabola u_x(r) = 2 V_avg (1 − (r/R)²), V_avg = 2.0 (u_max = 4.0 on the axis, section
average 2.0), evaluated from the patch face-centre radius so it adapts to every level
(the `pipeCyclic` idiom). **The parabola MUST be prescribed:** the entrance length at
Re = 500 is ~0.05·Re·D ≈ 0.0625 m > half the 0.1 m pipe, so a uniform inlet would
leave the flow developing over most of the pipe and the pressure drop would not be
Hagen–Poiseuille. Outlet: `inletOutlet` U, `fixedValue` p = 0. Walls: `noSlip`,
`zeroGradient` p. `wedge1`/`wedge2`: `wedge`. No `pRefCell` (the outlet pins pressure;
contrast VMFL001's closed domain).

**Schemes (`fvSchemes`).** Unlike VMFL001 (cell Péclet ~0.13, central convection),
VMFL005 is numerically convection-dominated: cell Péclet |u| dx / ν ≈ 4.0·(0.1/N_x)/1e-5
is ~400 at L1, so `div(phi,U)` is `bounded Gauss linearUpwind grad(U)` (second-order,
stable). The viscous/Laplacian term — the one that actually sets the Hagen–Poiseuille
gradient, so the term the Roache triple measures — is `Gauss linear corrected`
(second order). **Judgment:** the upwind convection scheme is a stability choice, not
a physics one; in the fully-developed region u·∇u = 0 (u_x has no axial gradient,
u_r = 0), so convection contributes nothing to the developed pressure gradient and
the scheme does not bias it.

**The measurement instrument — patch-average function objects (NOT `sets`).** ΔP is
read from two `surfaceFieldValue` function objects, `pInletMonitor` and
`pOutletMonitor`, each `areaAverage(p)` over a patch, written every iteration
(`writeControl timeStep`, `writePrecision 12`). The reader is built directly against
the **v2606 writer source** (the lesson of VMFL001 run 1 = N-AV4 / L-286: match the
reader to the REAL writer, not a belief):

- output path `postProcessing/<foName>/<startTime>/surfaceFieldValue.dat` —
  `src/OpenFOAM/db/functionObjects/writeFile/writeFile.C` `baseFileDir()`
  (`globalPath()/"postProcessing"`), `baseTimeDir()` = `prefix_/timeName`, and
  `src/functionObjects/field/fieldValues/fieldValue/fieldValue.C:56` (object name →
  `prefix_`, valueType `"surfaceFieldValue"` → base file name); startTime dir = `0`;
- header lines prefixed `# ` (`writeCommented`), last header line `# Time <tab>
  areaAverage(p)` — `surfaceFieldValue.C` `writeFileHeader` (~:712–755);
- data `<time> <tab> <value>` per write, at the object's `writePrecision`
  (`writeFile::read` honours `writePrecision`, `writeFile.C:248`) —
  `surfaceFieldValueTemplates.C` `writeValues` (~:519/527), `writeCurrentTime`
  `writeFile.C:360`.

**Why `sets` was NOT used.** The v2606 raw `coordSet` writer names its files
`<field>_setName.raw` (`meshTools/coordSet/writers/common/coordSetWriter.C:421`
`getFieldPrefixedPath`; `raw/rawCoordSetWriterImpl.C:109`), which matches neither a
naive belief nor even VMFL001's own empirically-observed `gateAxis_p_U.xy` — precisely
the N-AV4 naming trap. The patch-average `surfaceFieldValue.dat` format is
unambiguous from source, so it is the gated instrument.

**Judgment — a documented half-cell axial bias.** The inlet p BC is `zeroGradient`,
so its patch face value equals the first-cell-centre value (at x = Δx_axial/2), while
the outlet p is `fixedValue 0` at x = L exactly. The measured ΔP is therefore biased
**low** by (dp/dx)(Δx_axial/2): with dp/dx = 102.4 Pa/m, that is ~**0.5 %** at L1
(Δx = 1e-3) shrinking to ~**0.125 %** at L3 (Δx = 2.5e-4), a first-order term. This is
**disclosed, not hidden**: it means the Roache triple is expected to converge from
below at roughly **first order** (dominated by this bias) rather than second, and the
lab value is expected to sit slightly below 10.24 — the same side as, and comparable
in size to, Ansys Fluent's own 0.2 % shortfall (10.22). A CONVERGING first-order
triple is a valid triple; the gate at 2 % contains the residual bias at L3 with wide
margin. RESULTS.md will report the measured triple order, whatever it is.

## 6. THE VERDICT ORDER (CLAUDE.md rule 5)

1. any level not iteratively converged (final `Ux`/`Uy`/`p` initial residual < 1e-6
   **and** inlet-pressure plateau ptp < 1e-4 Pa over the last 20 %) ⇒ **`NOT A
   RESULT`**;
2. Roache triple on ΔP `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` ⇒ **`NOT A
   RESULT`**, with the three values, R and both triples printed beside it;
3. `CONVERGING` ⇒ **`PASS`** inside the 2 % band else **`GATE FAIL`**, GCI at Fs =
   1.25 printed. No GCI is quoted when the three values are not monotone. The gate can
   only turn a PASS/GATE FAIL **into** `NOT A RESULT`, never the reverse.

## 7. Planted-zero control (CLAUDE.md rule 3)

The comparator copies `pInletMonitor`'s `surfaceFieldValue.dat` to a temp tree, adds
**PLANT = 1.234 Pa** to the endTime value, reads it back from disk, and re-runs the
same extraction. The extracted ΔP must move by exactly PLANT (to 1e-9 Pa); otherwise
the comparator **refuses (exit 2)**. The run tree is never modified — only the temp
copy. The `--selftest` exercises both arms (planted ⇒ visible; unplanted ⇒ no signal)
on fixtures in the real `surfaceFieldValue.dat` format.

## 8. Strict completion (CLAUDE.md rule 4)

The comparator refuses (exit 2) on any failed clause: `rc = 0`; an `End` line; **last
time == that level's endTime** (L1 2000, L2 3000, L3 6000); fields `U` and `p` present
at endTime; **`ExecutionTime` count == that level's endTime**; and the **age guard** —
every field at endTime strictly newer than the case's own `0/U`, touched immediately
before launch. The run script refuses to start into any pre-existing level directory,
refuses unless this pre-registration is committed at HEAD, and enforces the cap with
`timeout`. There is **no `residualControl`**, so SIMPLE always runs to endTime and the
"last time == endTime" and "ExecutionTime count == endTime" clauses are meaningful.

## 9. Cost (CLAUDE.md rule 12)

| item | value |
|---|---|
| ranks | **1 (serial)**; core-minutes = wall_s × 1 / 60 |
| basis | VMFL001's **measured** per-cell-iteration rates: L1 6.51e-10, L2 1.06e-9, L3 2.12e-9 s/(cell·iter) (from VMFL001 R1: 2 s / 13 s / 104 s at 3000 iters × 1024 / 4096 / 16384 cells) |
| solver estimate | L1 1000×2000×6.51e-10 = 1.3 s; L2 4000×3000×1.06e-9 = 12.7 s; L3 16000×6000×2.12e-9 = 203.1 s → **217 s** |
| + codedFixedValue runtime compile | ~15 s/level × 3 = **45 s** (one-time per fresh level dir; an estimate) |
| + margin (3rd U component, linearUpwind, 2 per-iteration function objects) | ~15 % of solver ≈ **33 s** |
| **estimate** | 217 + 45 + 33 ≈ **295 s = 4.9 core-min** |
| **CAP** | **13 core-minutes** = ⌈2.5 × 4.9⌉ = ⌈12.25⌉, enforced by `timeout` inside `run_vmfl005.sh`; **an overrun STOPS the run and it does not get a new budget** |
| dollars at the estimate | **$0.004190** (4.9 core-min ÷ 60 × $0.0513/core-h) |
| dollars at the cap | **$0.011115** |
| `cost_basis` | **owner-stated rate $0.0513/core-h (c7a.4xlarge, Sanaa 2026-08-21/22); dollars DERIVED, NOT MEASURED — the box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5). The per-cell-iteration basis is VMFL001's measurement; the VMFL005 scaling, the compile time and the margin are ESTIMATES, not measurements. |
| pre-authorisation | under the 2026-08-21 blanket for CPU runs under $25; **this is a per-item cost, not a new ceiling** (rule 9) |
| calibration | at completion, actual core-minutes from `RUN_RC.txt`/`COST.txt` against this estimate, ratio and attribution, one row appended to `docs/COST_CALIBRATION.md` (rule 12) |

## 10. The grading path, frozen (VERIFICATION_CHARTER §2d)

The comparator, run script and case were **committed BEFORE this file** (commit
**`819c3993`**, "VMFL005 case inputs and comparator — NO COMPUTE, prereg not yet
frozen", parent `c4dad947`), and both commits precede any solver. At analysis time
the grading path is re-hashed against these shas; a freeze that is claimed and not
checked is a claim about intent.

| what | path | committed blob sha |
|---|---|---|
| **comparator** | `cases/ansys_verification/VMFL005/grade_vmfl005.py` | **`8e7410cc356c3e175fe0d993efa366d51085ba81`** |
| run script | `cases/ansys_verification/VMFL005/run_vmfl005.sh` | `06056e18a9fee92e2e8765b279ae31f5373c62c5` |
| blockMeshDict template | `case/system/blockMeshDict.template` | `fbac1ecb3c188f6fa8879504b7339dd79bac7e63` |
| controlDict template (per-level endTime + monitors) | `case/system/controlDict.template` | `5b475c5f6d497494b360deef0582ccc338d46be7` |
| fvSchemes | `case/system/fvSchemes` | `4107b6d9dbb4906333cf040e4141928ccbfa1215` |
| fvSolution | `case/system/fvSolution` | `8a67453acfaaac69d9bf2d8acdfe2fef0e3d43c9` |
| `0/U` (inlet parabola + age-guard marker) | `case/0/U` | `56cab8d5431653b3fa25dc087a14912635bf9816` |
| `0/p` | `case/0/p` | `87772e07e9567d5dc8bdfcbcc370b7e32f12df38` |
| transportProperties | `case/constant/transportProperties` | `2495e25ac12a77b18c072dd0ad9e1f921eb8b1e8` |
| turbulenceProperties | `case/constant/turbulenceProperties` | `6d5b3af67a1fa836a5a9ac06235d34db6fbdd73e` |

**Run outputs go to `verification/runs/ansys_verification/VMFL005/<level>/`**, never
beside this prose (FILING_CHARTER R6). **The grading JSON is
`verification/runs/ansys_verification/VMFL005/GRADING_VMFL005.json`.**

## 11. What CANNOT be verified before the freeze

**No VMFL005 solver has run**, so the comparator's parsing of a **live** v2606 run
tree is untested. What *has* fired, with **zero solver compute**: the `--selftest`
(20/20 — exact formula both forms, Reynolds number, the reader on the real
`surfaceFieldValue.dat` format, a one-column-row refusal, planted-zero both arms, the
Roache classifier across all five states, the gate both arms) and a `--dryrun-reader`
on a hand-written fixture in the real format.

Two things this lab has **not** seen and that the first coarse solve would settle,
each of which the **supervisor must authorise** — even one coarse level is compute and
is not covered by this freeze:

1. **The live `surfaceFieldValue.dat` format.** The reader is built from the v2606
   writer **source** (§5), which is stronger than VMFL001 run 1's belief-based reader,
   but no VMFL005 run has produced the file. The cheap, decisive check is to run the
   first coarse level (`L1_100x10`, ~seconds), then
   `python3 cases/ansys_verification/VMFL005/grade_vmfl005.py --dryrun-reader
   verification/runs/ansys_verification/VMFL005/L1_100x10/postProcessing/pInletMonitor/0/surfaceFieldValue.dat`
   which prints only `parsed, N rows` (never a value) — the exact pre-freeze
   external-reader check L-286 names.
2. **That `codedFixedValue` compiles and runs headless**, and that L3 actually clears
   the 1e-6 residual clause within 6000 iterations (§4 is an estimate). If either
   fails, the run script refuses (a crash is a finding) or the comparator returns
   `NOT A RESULT`, and the rung re-runs as a new row — no gate, threshold, cap or
   label moves.

Any change to the comparator after the first VMFL005 solve is a **dated addendum**
disclosing exactly what changed and whether it could move a number, read by the
supervisor before any re-grade.

## 12. Verdict vocabulary, and what this rung will NOT claim

`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and
nothing else (CLAUDE.md rule 1). **Nothing about Ansys** — the Fluent 10.22 and CFX
10.49 values are context (§1), never the gate; this box has no Fluent and no CFX. The
verdict is a statement about this lab's solver against the manual's Hagen–Poiseuille
reference, and only a `PASS` is a credential; a `GATE FAIL` is a finding that is never
removed or softened.

---

## Amendment record

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-24 | Frozen before any compute; blob `43aaf6bf5c5f1189495e1460e5de415e56860447`, cited as the freeze proof of register row #3. Lines whose number changed above this section: n/a (first version). |
| **1.1** | **2026-08-25T02:23:39Z** | **§9's three per-cell-iteration rates are MISLABELLED BY A FACTOR OF 10³. Every product, total, cap, dollar figure, gate, threshold, label, verdict and credential is UNAFFECTED.** See the amendment below. **Lines whose number changed above this section: 0**, proven by prefix hash: the sha256 of the first **330** lines is unchanged by this append, and equals `2d18e67d01f0f9bfbcd26bcc258f63d995e25cb5b9773e7f15c02d8b16fdb999` (re-derive with `head -n 330 cases/ansys_verification/VMFL005/PREREGISTRATION.md | sha256sum`). |

## AMENDMENT 1 — 2026-08-25T02:23:39Z — §9's THREE EXPONENTS ARE 10³ TOO SMALL; NOTHING THEY FEED IS WRONG

**This file is NOT corrected in place, and the reason is specific.** It is a frozen
pre-registration whose blob `43aaf6bf5c5f1189495e1460e5de415e56860447` is cited in
**register row #3 as the freeze proof of a `PASS` credential**, and other records cite
it by line. An in-place quote-and-strike — the better technique for a body table a
reader consults — would move nothing here but would break the strong form of the
"lines whose number changed above this section: 0" assertion and could disturb line
citations. **The foot append keeps both intact.** §9's body text stands as frozen;
this amendment is what a reader of §9 must read beside it.

**THE DEFECT.** §9's `basis` and `solver estimate` rows (file lines 255 and 256) state
VMFL001's measured per-cell-iteration rates as **`6.51e-10`, `1.06e-9`, `2.12e-9`
s/(cell·iter)**. Re-derived from the very inputs the same row names — VMFL001 R1's
2 s / 13 s / 104 s at 3000 iterations on 1024 / 4096 / 16384 cells:

| level | arithmetic | correct rate | as printed in §9 | error |
|---|---|---|---|---|
| L1 | 2 / (3000 × 1024) = 2 / 3.072e6 | **6.510416666666667e-07** | `6.51e-10` | **10³ too small** |
| L2 | 13 / (3000 × 4096) = 13 / 1.2288e7 | **1.0579427083333333e-06** | `1.06e-9` | **10³ too small** |
| L3 | 104 / (3000 × 16384) = 104 / 4.9152e7 | **2.1158854166666665e-06** | `2.12e-9` | **10³ too small** |

**THE PRODUCTS ARE CORRECT, AND THAT IS HOW THE DEFECT IS BOUNDED.** §9's stated
per-level times reproduce exactly from the **correct** rates and not at all from the
printed ones:

| level | cells × iters | × correct rate | §9 states | × printed rate |
|---|---|---|---|---|
| L1 | 1000 × 2000 = 2.0e6 | **1.302 s** | **1.3 s** ✓ | 1.302e−3 s ✗ |
| L2 | 4000 × 3000 = 1.2e7 | **12.695 s** | **12.7 s** ✓ | 1.270e−2 s ✗ |
| L3 | 16000 × 6000 = 9.6e7 | **203.125 s** | **203.1 s** ✓ | 2.031e−1 s ✗ |
| **total** | | **217.1 s** | **217 s** ✓ | 0.217 s ✗ |

**The arithmetic that was actually performed used the correct rates; only the three
printed exponents are wrong.** A reader who took the printed rates at face value would
have computed a 0.217 s estimate and would have been misled about the *basis*, never
about the *budget*.

**WHAT IS UNAFFECTED — stated exhaustively, because that is the point of this
amendment.** The 217 s solver estimate; the 45 s compile allowance; the 33 s margin;
the **295 s = 4.9 core-min** estimate; the **13 core-minute CAP**; **$0.004190** at the
estimate and **$0.011115** at the cap; the `cost_basis` labelling (dollars **derived,
not measured**); the pre-authorisation clause. **NO GATE, THRESHOLD, BAND, CAP, LABEL,
REFERENCE VALUE, VERDICT OR CREDENTIAL MOVES.** VMFL005's verdict and its register row
#3 are untouched, and **row #3 is append-only and is NOT edited**; a dated note at the
foot of the register records that this file's blob has advanced, quoting both shas.

**PROVENANCE OF THE CATCH, recorded honestly.** The defect was found by this lane
while drafting VMFL003's own cost basis, and was **referred upward rather than
corrected unilaterally**; the `ansys-verification-supervisor` verified the arithmetic
independently and ruled that the repair land as this foot amendment. The lane that
found it did not touch the file until that ruling.

**THE DOWNSTREAM COPY IS ALREADY CORRECT.** VMFL003's `PREREGISTRATION.md` §9.1 cites
these same rates as *"VMFL001's measured per-level rates 6.51e−7 / 1.06e−6 / 2.12e−6
s/(cell·iter)"* — **with the correct exponents.** The error did not propagate.

**THE GENERAL LESSON, drafted for `docs/LESSONS.md`.** A cost basis is three numbers
— rate, count and product — and **only the product was ever checked**, because only
the product feeds the cap. A stated rate that no downstream figure depends on is an
**unchecked cell in a costing table**, and it is exactly the kind of number a later
case borrows as "measured". VMFL003 borrowed this basis and happened to re-derive it;
had it copied the printed exponents, its own budget would have been wrong by 10³.
**Every rate in a cost table should be re-derived from its own stated inputs, not
carried forward on the authority of the product it once produced.**
