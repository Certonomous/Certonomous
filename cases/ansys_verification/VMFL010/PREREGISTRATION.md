# VMFL010 — Laminar Flow in a 90° Tee-Junction: PRE-REGISTRATION (template form)

**NOT FILED ANYWHERE.** Nothing here or in the case it registers leaves this box
(CLAUDE.md rules 7, 8; `ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

**NOT YET RUN — frozen before any solver starts** (rule 2). At writing,
**`verification/runs/ansys_verification/VMFL010/` did not exist** — `ls -d` at
**2026-08-25T17:08:06Z** returned *No such file or directory*. **Graded compute is
LOCKED**; the `ansys-verification-supervisor` unlocks it after four personal
checks, and **no agent message is Sanaa's consent** (rule 9). Drafted by
`ansys-lane-opus48` on the standard form. Departures = dated addenda at the foot
(rule 6).

**DISCLOSED IN ADVANCE, IN THIS FROZEN DOCUMENT, NOT AFTERWARDS: the reference is a
CODE-TO-CODE number. It buys NEITHER V NOR P. The best verdict this case can earn
is GATE REACHED — never PASS.** A register row scoring it as a validation
credential would rest on a false sentence.

---

## The standard form (frozen)

```
1. CASE       : VMFL010 — Laminar Flow in a 90° Tee-Junction — manual p.39.
                Solver = OpenFOAM v2606 simpleFoam (steady, laminar, incompressible).
                No Fluent/CFX on this box; archive read for setup only. NOT YET RUN;
                run dir absent at 2026-08-25T17:08:06Z.
2. REFERENCE  : flow split (fraction in the upper/main branch) = 0.887.
                Source = R.E. Hayes, K. Nandkumar, H. Nasr-El-Din, "Steady Laminar
                Flow in a 90 Degree Planar Branch", Computers & Fluids 17:537–553
                (1989). Ansys Fluent = 0.884, Ansys CFX = 0.8837 — CONTEXT ONLY.
3. REF KIND   : **code-to-code / published numerical benchmark → buys NEITHER V nor
                P.** The manual's own test text also speaks of comparison "with
                experimental results", but the provenance of the 0.887 value cannot
                be established independently from the manual; the conservative,
                honest classification is therefore NEITHER, and it is frozen here.
4. CEILING    : **GATE REACHED** (band met = we reproduced the reference number).
                It CANNOT reach PASS — reproducing a solver's benchmark is not a
                verification. GATE REACHED is this team's success (Sanaa 2026-08-25).
5. QUANTITIES : mass flow phi on patches inlet, mainOutlet, branchOutlet;
                split = |phi(mainOutlet)| / |phi(inlet)|. Read via flowRatePatch.
6. THE GATE   : |split_lab − 0.887| / 0.887 ≤ 0.03 (3%), at L3. Inside ⇒ GATE
                REACHED; outside ⇒ GATE FAIL. Tol = the manual's own 3% accuracy goal
                (§1.3): with a benchmark reference and no tighter provenance to lean
                on, tightening below the manual's stated class would not be defensible.
7. LADDER     : simpleFoam laminar (nu = 0.003333/1 = 0.003333 m²/s, air, manual p.39);
                fully-developed parabolic inlet Uc = 1.0 m/s via codedFixedValue; two
                pressure outlets at equal static pressure (p=0). Three birth-certified
                meshes (cases/ansys_verification/VMFL010/mesh_birth/).
8. SEED       : r=2 grid triple. N cells across the width W=1: L1/L2/L3 = 20/40/80,
                branch legs 3N. Cell counts 2800 / 11200 / 44800. Serial.
9. RISK       : **GEOMETRY FIDELITY — the named principal risk.** The split is
                sensitive to the exact junction/branch geometry and Reynolds number;
                the archive junction geometry could not be extracted here (no h5py,
                compressed HDF5), so the mesh is a defensible T-junction (junction
                1×1, legs L=3, W=1 per manual), NOT provably Hayes' exact geometry.
                A scratch smoke build of THIS geometry gave split 0.921 (vs 0.887,
                ~3.8% high) — i.e. even a perfect solver on this geometry risks GATE
                FAIL. **Build-time condition (amendable before first compute): extract
                the archive junction/lead geometry before the graded run; if it
                cannot be extracted, the graded verdict is honestly geometry-limited
                and may be GATE FAIL for that reason, recorded as such.**
10. ORDER     : formal p_f = 2 (bounded Gauss linear div, corrected laplacian).
                Expect p_obs ≈ 2 on the split; **p_obs > 2.3 SUSPICIOUS.**
11. WEDGE     : N/A — 2-D planar Cartesian, not axisymmetric. No sin(t)/t term.
12. COST      : ≈ 8 core-minutes total for the triple (2800–44800 cells, SIMPLE to
                residualControl 1e-7; smoke L1 = 1.9 wall-s at 400 iters). Basis =
                reported-by-owner (COMPUTE_BUDGET §5). CAP = 30 core-min; overrun STOPS.
13. CONTROLS  : comparator grade_vmfl010.py, --selftest GREEN. Planted-zero control
                fires on all three flow readers; mass-conservation guard (|in| =
                |main|+|branch| to 0.5%). Strict completion: rc, End, latest==endTime,
                age guard on 0/U (rule 4). Roache gating: non-CONVERGING ⇒ NOT A
                RESULT (rule 5). Success verdict is GATE REACHED, never PASS.
```

## Provenance of the driving input (NOT derived from the target)

The inlet **centerline velocity Uc = 1.0 m/s** (fully-developed parabolic profile)
was read from the **Ansys archive boundary profile** `plarb_r4.set.prof` — the `v`
column peaks at `1.000000e+00` at the width centre and is zero at both walls — **not**
back-solved from the 0.887 split. The manual p.39 text layer drops the profile
formula and its centerline value; the archive supplies it. Air ρ=1, μ=0.003333,
L=3.0, W=1.0 are on manual p.39. The archive's own converged Fluent run gives
mainOutlet/inlet = 0.591/0.667 = 0.887 (CONTEXT ONLY).

**Amendments before first compute** name the absent run directory and state the
condition checked (line 9 carries the one live condition). After first compute:
dated addenda only; no addendum may alter the gate, band, cap or the code-to-code
label.

---

## Amendment — 2026-08-25 — GEOMETRY CORRECTED TO THE ARCHIVE'S OWN MESH COORDINATES (before first compute)

**Appended at the foot. Nothing above is rewritten, edited or struck in place.** The
struck values are named below and declared void; the frozen text above is left byte-for-byte
intact so the prefix-hash assertion at the end of this amendment can be checked. Drafted by
`ansys-lane-opus48`; the `ansys-verification-supervisor` ruled the amendment before first
compute.

### 1. Legality under rule 2 — condition and how it was checked

Rule 2 permits amendments **before first compute** provided the condition and its check are
stated. **The condition: `verification/runs/ansys_verification/VMFL010/` does not exist** — no
graded compute has begun, so gates are still open. This was re-verified with `ls -d` **inside
the same shell invocation that commits this amendment**, and the commit **aborts** if the
directory has appeared. If a run directory existed, this window would be closed and the defect
below would become a post-compute disclosure that changes nothing.

### 2. What changed, and the STRUCK values

The frozen geometry (secs. 7, 8, 9) was a **defensible but GUESSED** T-junction: junction 1x1,
symmetric legs L=3, W=1, domain x,y in [0,4], **no inlet lead**. The following frozen values are
**STRUCK (declared void and superseded)**:
- **sec. 9 / sec. 7 geometry** — "junction 1x1, legs L=3", "the archive junction geometry could
  not be extracted here (no h5py, compressed HDF5)", and the scratch smoke reading **0.921**.
- **sec. 8 cell counts** — "2800 / 11200 / 44800".
- **sec. 12 cost** — estimate "≈ 8 core-minutes", "CAP = 30 core-min".

The **SOURCED replacement geometry**: domain x in [0,4], y in [0,6]; main channel width 1
(x in [0,1]), total length 6 = **inlet leg 2 + junction 1 + downstream leg 3**; inlet at y=0
(x in [0,1]); the straight-through main outlet (the 0.887 leg) at y=6 (x in [0,1]); branch width
1, length 3, on the x=1 wall over y in [2,3]; branchOutlet at x=4 (y in [2,3]). **It differs from
what was registered: the inlet leg is 2, not absent, and the main length is 6, not 4.**

### 3. THE UNCOMFORTABLE SEQUENCE, STATED PLAINLY

**We knew the smoke result on the registered geometry — 0.921, outside the 3% gate — BEFORE we
obtained the true geometry.** This amendment therefore changes an input on a case we already had
reason to think would fail, **and that is exactly the shape of answer-directed selection.** It is
recorded here in those words because **a record that hides its own worst reading is worse than one
that states it.**

### 4. The test that distinguishes this from tuning — stated as a test we would have FAILED if the answer were different

**Would we make this change if the smoke had landed on 0.887 exactly? YES** — because running the
**wrong geometry** against the manual's number measures a different problem, and that is invalid
regardless of whether it happens to agree. **The change is justified by where the numbers came
FROM, never by where they LAND.** The ground is provenance, and only provenance: the registered
geometry was a guess; the archive's own mesh node coordinates are the case's actual geometry.

### 5. The constraint that removes the freedom to tune — NO ADJUSTABLE PARAMETER

Every dimension of the replacement geometry is **read from the archive**, not chosen. **There is
no knob to turn toward 0.887, and none was turned.** Full provenance:
- **Container:** `VMFL010_WB.wbpz` (Fluent Workbench archive; canonical home
  `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/VM2026R1_FLUENT_ARCHIVES/`, sha in
  `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`).
- **Internal member:** `VMFL010_WB_1_files/dp0/FLU/Fluent/plarb_r4-1.cas.h5` (Fluent HDF5 case).
- **Dataset path:** `meshes/1/nodes/coords/1` — 2176 nodes, float64, shape (2176, 2). Measured
  extent: **x in [0.000000, 4.000000], y in [0.000000, 6.000000]**; nodes at x=xmax(4) span
  y in [2,3] (branchOutlet); nodes at y=ymax(6) span x in [0,1] (mainOutlet); nodes at y=0 span
  x in [0,1] (inlet); all 720 nodes with x>1.001 lie in y in [2,3] (branch attaches at x=1).
- **Corroboration 1 (Fluent inlet profile):** `plarb_r4.set.prof`, the `v`-profile `x` column
  spans 0.000000e+00 -> 1.000000e+00 (17 points, peak v=1.0 at centre) — confirms main-channel
  width 1.
- **Corroboration 2 (CFX log maximum extent):** `VMFL010B_plarb_001.out` line 479,
  **"Maximum Extent = 6.0000E+00"** — confirms the domain's largest dimension is 6 (main length),
  which the registered geometry (max extent 4) got wrong.

### 6. THE GATE DOES NOT MOVE

**No gate, threshold, band or label changed.** Reference = flow split **0.887**; band = **3%**
relative; graded at **L3**; verdict ceiling **GATE REACHED** (never PASS). **The reference kind
stands: code-to-code / published numerical benchmark, buys NEITHER V nor P** — correctly stated at
the freeze, unmoved here. **If the corrected geometry still GATE FAILs, that is the result and it
is reported as the result.**

### 7. The principal risk is RETIRED by measurement, not by argument

Sec. 9 named **geometry fidelity as the principal risk**. It is now **retired by measurement**:
the geometry is read from the archive's mesh coordinates with two independent corroborations, and
is **no longer a judgement call**. The scratch smoke on the corrected geometry (sec. 9's stated
build-time condition, now discharged) is reported in sec. 9 below.

### 8. Cost / cap — corrected ARITHMETICALLY from the new cell count

The real domain is **9 unit-squares** (main 1x6 = 6, branch 3x1 = 3) against the registered **7**.
Cell counts per level, N cells across width W: **L1/L2/L3 = 3600 / 14400 / 57600** (= 9N^2 at
N = 20/40/80), sum **75600**, against the struck **2800 / 11200 / 44800**, sum **58800**. The
ratio is exactly **75600/58800 = 9/7 = 1.285714**.
- **Estimate:** struck 8 core-min -> **8 x 9/7 = 10.29 core-min**.
- **CAP:** struck 30 core-min -> **30 x 9/7 = 38.57 core-min** (cell-count-scaled; **not rounded
  up for safety**). Overrun STOPS the run (rule 12).
Basis = reported-by-owner, first-order cell-count scaling (COMPUTE_BUDGET §5); serial.

### 9. The corrected-geometry smoke — reported whatever it gives

A pre-flight smoke was built on the corrected geometry in scratch under `/tmp/claude-1000/`
(**outside `verification/runs/`**, capped at 3 core-min, ~11 wall-s serial, L1 = 3600 cells,
Mesh OK). **Split = |phi(mainOutlet)| / |phi(inlet)| = 0.591371 / 0.667500 = 0.885949**, i.e.
**0.886 vs target 0.887 (-0.12%)**, mass conserved to 6.6e-10. **It is a smoke test, not a
prediction, and it grades nothing** — the graded run stays LOCKED until the supervisor's four
checks. Reported as required including the direction: it lands inside the 3% band, where the
struck 0.921 did not; that fact does not upgrade the case and is not treated as a result.

### 10. The comparator does NOT change

`grade_vmfl010.py` reads flow rates **by patch name** (`inlet`, `mainOutlet`, `branchOutlet`),
which are unchanged, and its split definition, 3% band, planted-zero control and Roache gating do
not depend on geometry. **The grading path is byte-identical; check 4 is NOT re-opened.**

### Rebuilt inputs (separate commit, NO GRADED COMPUTE)

The case tree is rebuilt to the sourced geometry: `case/system/blockMeshDict.template` (four
conformal blocks), `run_vmfl010.sh` (N2 array added, cell-count header), and **three re-certified
birth certificates** at `mesh_birth/L{1,2,3}/` (clean, non-orthogonality 0, skewness ~1e-13).
These land in their own commit declaring NO GRADED COMPUTE.

**Lines whose number changed above this section: 0** — proven by prefix hash: the file as it stood
before this amendment is an exact byte-prefix of the file after it (verified in the committing
invocation by hashing the first N pre-amendment bytes of the amended file and comparing to the
recorded pre-amendment sha256), not merely asserted.
