# VMFL010-R2 — Laminar Flow in a 90° Tee-Junction, MESH-TRIPLE REPOSITIONING: PRE-REGISTRATION

**NOT FILED ANYWHERE.** Nothing here or in the case it registers leaves this box
(CLAUDE.md rules 7, 8; `ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

**NOT YET RUN — frozen before any solver starts** (rule 2). At writing,
**`verification/runs/ansys_verification/VMFL010-R2/` did not exist** — `ls -d` at
**2026-09-07T15:11:47Z** returned *No such file or directory*. **Graded compute is
LOCKED**; the `ansys-verification-supervisor` unlocks it after the four personal §3
checks, and **no agent message is Sanaa's consent** (rule 9). A launch-permission
block is on Sanaa's desk and is being HELD — this document and its comparator stop at
a committed freeze; **no queue entry, no launch.** Drafted by `ansys-lane-opus48`
(running as claude-opus-4-8). Departures = dated addenda at the foot (rule 6).

**DISCLOSED IN ADVANCE, IN THIS FROZEN DOCUMENT, NOT AFTERWARDS: the reference is a
CODE-TO-CODE number. It buys NEITHER V NOR P. The best verdict this case can earn is
GATE REACHED — never PASS.** Unchanged from the base VMFL010 freeze; a mesh-triple
repositioning cannot upgrade the reference kind.

---

## 0. WHAT R2 CHANGES, AND THE FINDING THAT SHAPES IT

**The base VMFL010 landed `NOT A RESULT`** (register row #14, 2026-08-25): the Roache
grid triple was **OSCILLATORY** — split L1/L2/L3 = 0.885949 / 0.884453 / 0.884749
(N = 20/40/80, cells 3600/14400/57600). Second difference sign-flipped:
Δ(L1→L2) = −1.4964e-3, Δ(L2→L3) = **+2.958e-4**. The finest value 0.884749 is 0.26 %
from the 0.887 target — inside the 3 % band on VALUE alone — but rule 5 disqualifies a
non-monotone triple, whatever its value. Cost 3.5833 core-min.

**THE REGISTRY'S DATED-PLAN HYPOTHESIS IS FALSIFIED BY INSPECTION.** The
`FIX_SUCCESSOR_REGISTRY.md` plan read the base oscillation as a mesh that "did not
refine cleanly by r=2 (non-similar meshes across levels)." **On inspection that is not
the defect.** The base was *already* a genuinely self-similar structured hex triple,
r=2 at the junction:
- The base `blockMeshDict.template` is a 4-block structured hex mesh (inletleg N×2N,
  junction N×N, mainleg N×3N, branchleg 3N×N) with uniform `simpleGrading (1 1 1)` and
  square cells W/N × W/N. Every block's cell count doubles per level → clean r=2, the
  junction block included (20×20 → 40×40 → 80×80).
- The three base birth certificates (`cases/ansys_verification/VMFL010/mesh_birth/`)
  certify it AS BUILT: **3600 / 14400 / 57600 cells, all hexahedra, max aspect ratio
  1.0, max non-orthogonality 0.0, max skewness ~1e-13**, exactly ×4 per level.

**The actual mechanism (base RESULTS.md diagnosis + a magnitude check).** The base
sequence is **textbook 2nd-order in MAGNITUDE**: |Δ32/Δ21| = 2.958e-4 / 1.4964e-3 =
**0.198**, against the 0.25 a clean p=2, r=2 sequence predicts; the implied order from
the magnitudes alone is p ≈ log(1.4964e-3/2.958e-4)/log 2 = **2.34**. The *only* defect
is that the tiny finest-level second difference (+2.958e-4) is **sign-flipped** — the
signature of a **~1e-4 iterative/round-off perturbation** (the base ran to
`residualControl` 1e-7, whose final Ux initial residual sat at ~9.9e-8 for all three
levels) sitting on top of an otherwise-converging sequence, and of a finest level (N=80)
whose grid-to-grid difference had fallen into that perturbation's noise floor. The base
lane recorded the honest repair: **"a coarser triple that keeps the leading term
dominant"** — NOT further refinement ("refining further will not fix this by itself").

**R2's lever, therefore (a MESH-QUALITY lever, NOT a gate change):**
1. **Reposition the self-similar r=2 triple into the leading-term-dominant regime.** Keep
   the base's proven self-similar structured-hex family (topology byte-identical — it was
   never the problem) but move the triple so the **finest level is N=40, not N=80**:
   **N = 10 / 20 / 40**. The base's own convergence proves the leading (2nd-order)
   truncation term is dominant and CLEAN across N=20→40 (Δ = −1.5e-3, textbook) and is
   lost into the ~1e-4 noise floor only by N=40→80 (Δ = +3e-4, sign-flipped). Placing all
   three levels at N ≤ 40 keeps every grid-to-grid difference above the perturbation, so
   the Roache sign is meaningful.
2. **Tighten iterative convergence** two orders, `residualControl` 1e-7 → **1e-9** on both
   U and p (linear-solver tolerances 1e-9 → 1e-11), so the split's iterative uncertainty
   is far below the grid-to-grid difference. This strengthens rule-4/rule-5 iterative
   convergence; it changes NO discretisation scheme (still `bounded Gauss linear`, p=2)
   and NO gate.

**THE GATE DOES NOT MOVE** (L-487): reference flow split **0.887**, band **±3 % relative**,
graded at the finest level, verdict ceiling **GATE REACHED** (never PASS). Neither the
repositioning nor the tighter iteration touches the band, and neither is sized from it.

**Honest disclosure of the informed prior.** The R2 finest level (N=40) is the base's L2,
whose split (0.884453) is on the record. So R2's finest-level *value* is **not** unknown to
the drafting lane, and I do not claim answer-blindness on it; the scratch smoke below was
kept answer-blind (the split was never read) as belt-and-braces. The **open question — the
verdict — is whether the repositioned triple is CONVERGING**, which is genuinely unknown at
freeze. The gate is fixed by the manual and unchanged; knowing the finest value cannot tune it.

---

## The standard form (frozen)

```
1. CASE       : VMFL010-R2 — Laminar Flow in a 90° Tee-Junction — manual p.39 (VM2026R1,
                title-page verified against the PDF, rule 15: "Ansys Fluid Dynamics
                Verification Manual", Release 2026 R1, March 2026; VMFL010 printed p.39).
                Solver = OpenFOAM v2606 simpleFoam (steady, laminar, incompressible).
                Successor to VMFL010 (NOT A RESULT, OSCILLATORY). NOT YET RUN; run dir
                absent at 2026-09-07T15:11:47Z.
2. REFERENCE  : flow split (fraction in the straight-through / upper "main" branch) = 0.887.
                Source = R.E. Hayes, K. Nandkumar, H. Nasr-El-Din, "Steady Laminar Flow in
                a 90 Degree Planar Branch", Computers & Fluids 17:537–553 (1989). Ansys
                Fluent = 0.884 (ratio 0.997), Ansys CFX = 0.8837 (ratio 0.9962) — CONTEXT ONLY.
3. REF KIND   : code-to-code / published numerical benchmark → buys NEITHER V nor P.
                Frozen identically to the base; unchanged by a mesh-triple repositioning.
4. CEILING    : GATE REACHED (band met = we reproduced the reference number). CANNOT reach PASS.
5. QUANTITIES : mass flow phi on patches inlet, mainOutlet, branchOutlet;
                split = |phi(mainOutlet)| / |phi(inlet)|. Read via flowRatePatch, latestTime.
6. THE GATE   : |split_lab − 0.887| / 0.887 ≤ 0.03 (3 %), at the FINEST level (N=40).
                Inside ⇒ GATE REACHED; outside ⇒ GATE FAIL. Tol = the manual's own 3 %
                accuracy goal. BYTE-IDENTICAL to the base band (L-487 — the mesh fix cannot
                move the band).
7. LADDER     : simpleFoam laminar. nu = mu/rho = 0.003333 m²/s (air, rho=1, mu=0.003333,
                manual p.39). Re = rho·Vc·W/mu = 300 (manual p.39, PDF) ⇒ Vc = 300·0.003333
                = 0.99999 ≈ 1.0 m/s — an INDEPENDENT manual corroboration of the archive-read
                centreline velocity Uc=1.0. Fully-developed parabolic inlet Uc=1.0 via
                codedFixedValue; two pressure outlets at equal static pressure (Ps=0, manual).
8. SEED       : self-similar structured HEX triple, r=2, junction included. N cells across
                width W=1: L1/L2/L3 = 10 / 20 / 40. Cell counts (9N²) = 900 / 3600 / 14400.
                Serial. Topology = the base's certified self-similar family; the triple is
                repositioned so the finest level is N=40 (base L2), not N=80.
9. RISK       : the split may be GENUINELY mesh-sensitive at Re=300 near its converged value
                (a functional whose grid response is set by cancellation at the fine end),
                OR N=10 may be too coarse to sit inside the asymptotic range. Either outcome
                is a FINDING and is reported as such — NOT rescued by widening the band or
                trying other triples (§9 prediction states this bind explicitly).
10. ORDER     : formal p_f = 2 (bounded Gauss linear div, corrected laplacian). The base
                magnitudes implied p ≈ 2.34; on the repositioned triple expect p in ~[0.4, 2.5];
                p_obs > 2.5 SUSPICIOUS (report GCI only when the triple is monotone).
11. WEDGE     : N/A — 2-D planar Cartesian, not axisymmetric.
12. COST      : est ≈ 1.1 core-min for the triple (finest N=40 MEASURED at 0.667 core-min in
                the answer-blind smoke, 1490 iters to residualControl 1e-9). CAP = 7.0 core-min
                running total. Basis = reported-by-owner (COMPUTE_BUDGET §5). Overrun STOPS.
13. CONTROLS  : comparator grade_vmfl010_r2.py, --selftest reports N/N. Planted-zero control
                (rule 3, L-487) on the flow readers the split depends on. Strict completion:
                rc=0, End, no FOAM FATAL, fields at latestTime, age guard on 0/U, iterative
                convergence (residualControl 1e-9 met). last==endTime DELIBERATELY INAPPLICABLE
                (residualControl-terminated steady solve — same basis as VMFL038/054/063).
                Roache gating (rule 5): non-CONVERGING ⇒ NOT A RESULT. Gate-blind physical-range
                refusal: split ∈ (0,1) and mass conserved. Success verdict = GATE REACHED, never PASS.
```

## Provenance of the driving input (NOT derived from the target)

The inlet **centreline velocity Uc = 1.0 m/s** is fixed independently of the 0.887 split by
**two** sources that agree: (a) the manual p.39 itself — **Re = rho·Vc·W/mu = 300** with
rho=1, W=1, mu=0.003333 gives Vc = 0.99999 ≈ 1.0 (read from the PDF; the .txt sidecar dropped
this formula); and (b) the Ansys archive boundary profile `plarb_r4.set.prof`, whose `v` column
peaks at 1.000000e+00 at the width centre. The geometry (domain x∈[0,4], y∈[0,6]; inlet leg 2,
junction 1, main leg 3, branch length 3 over y∈[2,3]) is the base's archive-sourced geometry,
independently corroborated by the manual figure (inlet leg 2/3·L=2.0, main leg L=3.0, branch
length L=3.0, junction height W=1.0). No dimension and no driving value is back-solved from 0.887.

---

## 1. The gate (frozen, UNCHANGED from the base — L-487)

`|split_lab − 0.887| / 0.887 ≤ 0.03`, evaluated at the finest level **only when the Roache
triple is CONVERGING** (rule 5). Inside ⇒ GATE REACHED; outside ⇒ GATE FAIL; a non-CONVERGING
triple ⇒ NOT A RESULT whatever the value. The band, the reference and the reference kind are
byte-identical to the base VMFL010 freeze. **The mesh-triple repositioning and the tighter
iteration cannot, and do not, move any of them** (L-487 anti-circularity).

## 2. The self-similar structured hex triple (a-priori, named)

| level | N (cells/width) | 2N | 3N | total cells (9N²) | junction block |
|---|---|---|---|---|---|
| L1 | 10 | 20 | 30 | 900   | 10×10 |
| L2 | 20 | 40 | 60 | 3 600 | 20×20 |
| L3 | 40 | 80 | 120| 14 400| 40×40 |

**Self-similarity, junction included, is GUARANTEED by construction:** all three levels are the
SAME 4-block `blockMeshDict.template` with uniform `simpleGrading (1 1 1)`, only the substituted
N doubling per level. Each block's cell count is exactly ×4 per level (2-D r=2), the junction
block among them (10×10 → 20×20 → 40×40). Cells are square W/N × W/N at every level. Each level's
mesh will be re-certified at graded-run time with a fresh birth certificate (checkMesh: expect
non-orthogonality 0, skewness ~1e-13, aspect ratio 1.0, as the base certified). **The graded
triple is L1/L2/L3 = 10/20/40, named here; no other triple is run, and none is selected on
outcome.**

## 3. Roache triple gating (rule 5), written in a-priori

In order: **(1)** any level not iteratively converged (residualControl 1e-9 not met /
"SIMPLE solution converged" absent) or not plateaued → **NOT A RESULT**; **(2)** the graded
triple L1/L2/L3 not `CONVERGING` (i.e. `DIVERGENT`, `OSCILLATORY`, `STAGNANT` or `EXACT`) →
**NOT A RESULT**, value and both triple/order printed beside it; **(3)** `CONVERGING` → the
gate (§1) is evaluated: inside ⇒ **GATE REACHED**, outside ⇒ **GATE FAIL**, with GCI at
Fs=1.25 printed. The gate can only turn a reached/failed gate INTO NOT A RESULT, never the
reverse. **GCI is never quoted when the three values are not monotone.**

## 4. Strict completion (rule 4) + age guard, written in a-priori

Per level, ALL must hold or the comparator REFUSES (exit 2, never degrades):
- solver `rc = 0` (persisted as `RUN_RC.txt`);
- an `End` line in `log.simpleFoam` (matched by exact filename, never a `log*` glob — a glob
  matches `log.blockMesh` first and would read the mesher's End line) AND no `FOAM FATAL`;
- fields present at the latest written time > 0;
- **the age guard** — the field at the latest time is NEWER than the case's own `0/U` (which is
  touched last at launch); a level whose `0` or a time dir already existed is refused;
- iterative convergence — residualControl 1e-9 met ("SIMPLE solution converged" present).

**`last time == endTime` and the `ExecutionTime` count are DELIBERATELY INAPPLICABLE** to a
`residualControl`-terminated steady solve, which stops BEFORE `endTime` on purpose — the same
declared basis used by VMFL038, VMFL054 and VMFL063. They are not checked.

## 5. Guards (all REFUSE exit 2; validated by --selftest, §8)

- **(1) Planted-zero (rule 3), on the flow readers the gate depends on.** A known delta is
  planted into a COPY of a `flowRatePatch` `.dat`, read back, and the control REFUSES if unseen.
  **L-487 compliance:** the gate reduction is a DIRECT read of ONE scalar per patch — the LAST
  data row's last column of a single-patch file — NOT a sum/mean/integral (which would cancel a
  full-set plant), NOT a peak-to-peak/range (which would absorb an interior plant), NOT a
  max/min over a set. The plant is added to *exactly the row the reader reads*, so it is seen by
  **identity** (expected shift == PLANT), and the split ratio inherits it. The comparator carries
  a **known-bad arm** as standing proof the control is load-bearing: a plant written to a
  DIFFERENT row than the reader reads leaves the read unchanged, and the control MUST report that
  blindness (passed=False). If you can write an input on which this control passes while the
  reader is blind, the control is inert (L-487's general test) — the known-bad arm is that input,
  asserted to fail.
- **(2) Strict completion (rule 4)** — §4.
- **(3) Known-bad input** — a corrupted / unparseable data row is fed to the reader, which MUST
  refuse rather than coerce it to a number.
- **(4) Gate-blind physical range** — the split must be a physically admissible fractional flow
  split, strictly in **(0, 1)**, and mass must be conserved (|in| = |main|+|branch| to 0.5 %).
  Outside ⇒ REFUSE. **This references NEITHER the ±3 % band NOR the 0.887 target** — only the
  physical plausibility of a dividing-flow fraction — so it cannot fit the gate; it only rejects
  a garbage read (a NaN-parsed-as-0, a units error, a reversed patch) before it can masquerade
  as a convergence datum.

## 6. Cost (rule 12)

- **Ranks:** 1 (serial, matching the base for a clean r=2 comparison).

  | Level | N | cells | core-min |
  |---|---|---|---|
  | L1 | 10 | 900   | ~0.10 ESTIMATED (cell/iter-scaled from L3) |
  | L2 | 20 | 3 600 | ~0.30 ESTIMATED |
  | L3 | 40 | 14 400| **0.667 MEASURED** (answer-blind smoke: 40 wall-s, 1490 iters to residualControl 1e-9) |

- **Pre-registered estimate for the graded triple:** **~1.1 core-min.**
- **Running-total cap in the driver: `CAP_CORE_MIN = 7.0` core-min** (~6× margin; an overrun
  STOPS the run — rule 12). Well under the $25/run pre-authorisation: 1.1 core-min = 0.0183
  core-h × $0.0513 ≈ **$0.0009 DERIVED**; the 7.0 cap ≈ **$0.006 DERIVED**.
- **`cost_basis`:** core-minutes = wall_s × ranks ÷ 60, MEASURED from the driver's own timing.
  Any dollar figure is DERIVED at **$0.0513/core-h, owner-stated, NOT measured** — this box
  cannot read its own billing (COMPUTE_BUDGET §5). The completion report will compare actual vs
  this estimate per rule 12 (`docs/COST_CALIBRATION.md`).

## 7. Solver / config path and buildability (FIX-UNTIL-RUNS, §2ay)

- **Solver:** `simpleFoam` (OpenFOAM v2606), steady laminar SIMPLEC (`consistent yes`),
  `bounded Gauss linear` convection (2nd order), `Gauss linear corrected` diffusion, 2-D
  (frontBack empty). **The case already runs to rc=0 on this solver** — the base graded
  L1/L2/L3 clean, and R2's finest level (N=40) is the base's L2. **No new capability is needed.**
- **Mesh:** `case/system/blockMeshDict.template`, the base's certified 4-block self-similar hex
  family; `run_vmfl010_r2.sh` substitutes N/2N/3N per level (10/20/40 → 20/40/80 → 30/60/120).
- **Iterative config:** `case/system/fvSolution` tightened to residualControl 1e-9 (linear
  tolerances 1e-11); schemes unchanged.
- **Buildability CONFIRMED (answer-blind smoke, §8):** `blockMesh` at N=40 → 14400 cells, rc=0;
  `simpleFoam` reached residualControl 1e-9 in 1490 iterations (End line present, "SIMPLE
  solution converged"), 40 wall-s = 0.667 core-min, ~10× under the 7.0 core-min cap. The split
  was **NOT read** (answer-blind).

## 8. Disclosed scratch feasibility (NOT the freeze; sets NO gate/band)

Run in the scratchpad, OUTSIDE `verification/runs/` (so it cannot disarm rule 4's age guard on
the frozen run root), on the FINEST level only (so no coarser level's value exists to select a
triple from), kept **answer-blind** (the split / patch flows were never read):
1. **N=40 buildability + convergence + cost smoke:** `blockMesh` → 14400 cells, rc=0; `simpleFoam`
   → residualControl 1e-9 in 1490 iters, End line, "SIMPLE solution converged", 40 wall-s =
   0.667 core-min. Confirms the tightened floor converges well within cap on the finest grid.
2. **Comparator `--selftest`:** reports N/N (§ the comparator file). Arms: split reader, planted
   present (seen), planted known-bad (blindness detected → refuse), gate-blind physical-range
   good/collapsed/out-of-range, CONVERGING + OSCILLATORY classifiers, strict-completion good +
   bad limbs. Each BAD arm visibly refuses.

## 9. THE LAB'S PREDICTION (stated before any graded run)

**Predicted verdict: GATE REACHED, MODERATE confidence.** With the ~1e-4 iterative perturbation
removed (residualControl 1e-9) and the triple repositioned so all three levels sit in the
leading-term-dominant regime (finest N=40, not N=80), the split is predicted to converge
**MONOTONICALLY DECREASING** — f(N=10) > f(N=20) ≈ 0.8859 > f(N=40) ≈ 0.8845 (from the base's
own N=20/40 values and the physical expectation that a coarser mesh's numerical diffusion pushes
the split higher) — giving a `CONVERGING` triple with p in roughly [0.4, 2.5], finest split
≈ 0.8845 (0.26 % from 0.887, inside the 3 % band). **The residual risk, disclosed:** N=10 may be
too coarse to lie inside the asymptotic range (breaking monotonicity from the coarse end), OR the
split may be genuinely mesh-sensitive at Re=300 near its converged value. **If the repositioned,
tightly-converged triple STILL oscillates (or is otherwise non-CONVERGING), that is the RESULT and
it is reported as `NOT A RESULT` with a finding — NOT rescued by widening the band, refining
further, or trying other triples.** The band is fixed; the verdict rides on the triple's
admissibility, which is the genuinely open question.

---

**This document is frozen by its committing sha. The grading path is `grade_vmfl010_r2.py` as
committed at the same sha; the launcher verifies the frozen prereg and comparator blobs against
HEAD before any solver starts (rule 2), and no solver starts under this freeze — the launch
permission is HELD on Sanaa's desk (rule 9).**
