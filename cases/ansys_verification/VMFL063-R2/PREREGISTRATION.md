# PRE-REGISTRATION — VMFL063-R2: Separated Laminar Flow Over a Blunt Plate

**Ansys Fluid Dynamics Verification Manual, Release 2026 R1, March 2026 — page 193
(Test Case and geometry), page 194 Table .63.1 (Results Comparison for Ansys Fluent)
and Table .63.2 (Ansys CFX).** Sidecar title-page verified against the PDF beside it
under `CLAUDE.md` rule 15 for the base registration VMFL063 (RESULTS.md PROVENANCE, and
PREREGISTRATION.md lines 3–11): PDF page 1 reads *"Ansys Fluid Dynamics Verification
Manual / ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release
2026 R1 / March 2026"*, `pdfinfo` `Title: Fluid Dynamics Verification Manual`,
`Pages: 290`; VMFL063 is PDF page 207 = printed page 193, Tables .63.1/.63.2 PDF page
208 = printed page 194. Not by filename, file type or hash.

Drafted by `ansys-lane-opus`, **2026-09-07**, for the supervisor to freeze. This file is
a frozen file under `CLAUDE.md` rule 6 from the moment its commit lands: departures are
dated addenda at the foot, never edits above.

**SUCCESSOR to VMFL063** (register row **#44**, `GATE FAIL`; base freeze `2df23798`
v1.0 → `3602cbf3` v1.1). It supersedes the OWED dated plan carried for VMFL063 in
`docs/ansys_verification/FIX_SUCCESSOR_REGISTRY.md`. It does **not** vacate row #44,
which stands as the honest record of the base result.

---

## 0. THE RULE-2 CONDITION, AND HOW IT WAS CHECKED

**NOT YET RUN. NO VMFL063-R2 SOLVER HAS EVER STARTED, ANYWHERE ON THIS BOX.** The gate,
the band, the ceilings, the mesh family, the cap and the named outcomes below are
therefore predictions, which is the entire evidentiary content of this document.

Checked at **2026-09-07T16:57:57Z**, HEAD **`7db1df83`**, and stated so a reader can
re-run each check:

| condition | how it was checked | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL063-R2` | **"No such file or directory"** |
| zero paths under the R2 run root at HEAD | `git ls-tree -r HEAD --name-only \| grep -c VMFL063-R2` | **0** |
| the register carries no VMFL063-R2 row | `grep -c VMFL063-R2` on `ANSYS_VALIDATION_REGISTER.md` | **0** |
| this case directory holds no `0/` or numeric time directory | the case directory holds only `case/`, this file, the comparator and the launcher | **no answer on disk** |

**There is no VMFL063-R2 number on this box for any band, cap or window in this document
to have been fitted to.** Amendments before first compute are legal and must restate
this condition, naming the run directory that does not exist
(`verification/runs/ansys_verification/VMFL063-R2`). After first compute the gates close:
dated addenda only, and no addendum may alter a gate, threshold, band, cap or ceiling.

---

## 1. WHY R2 EXISTS, AND THE FALSIFICATION THAT RESHAPED IT

### 1.1 What the base found (row #44, `GATE FAIL`)

VMFL063 graded `GATE FAIL`: at the finest level **L3** (92 160 cells) `LR/(2t) = 5.600237`
against the manual's experimental Target **4.0**, a **40.01 %** deviation on a
**`CONVERGING`** triple. The triple L1/L2/L3 = **6.788127 / 6.164703 / 5.600237** marched
monotonically **toward** 4.0 but had not stopped: `R = 0.905428` (near 1), observed order
`p = 0.143328` (far below the scheme's formal order), `GCI_fine = 120.62 %` (larger than
the value it qualifies). Limb B (serial determinism) was `PASS`; the row took the worse
limb. Two problems: **(1) the triple never reached the asymptotic range**, and **(2) the
value was 40 % out of band**.

### 1.2 The dated plan's lever was FALSIFIED before this freeze

The OWED dated plan prescribed *"finer, separation-region graded mesh **plus higher-order
convection (linearUpwind→linear)**."* **The base VMFL063 never used `linearUpwind`.** Its
frozen `div(phi,U)` scheme, in `cases/ansys_verification/VMFL063/case/system/fvSchemes`
(blob **`0b7e18377a27ddc07c21f9b5f9b0c27af905aa45`**, verified disk == HEAD — the file
that actually ran at freeze `2df23798`), is:

```
div(phi,U)      bounded Gauss linear;   // 2nd order
```

`bounded Gauss linear` **is** pure 2nd-order central differencing (the "linear" the plan
wanted to switch *to*), the **least-diffusive** convection scheme available. There is no
`linearUpwind` anywhere in that file's history, and nothing higher-order than central to
switch to. The plan's mental model was backwards: it assumed the base was diffusive and
sought less diffusion; the base was already at **zero** numerical diffusion. The scheme
clause was therefore a **no-op** — re-running with it would reproduce the same
non-asymptotic triple at higher cost — and freezing it would put a false statement into a
rule-6 record.

**RULING.** The `ansys-verification` supervisor's §3 check-2 ruling of 2026-09-07
(verified the falsification independently: base blob `0b7e1837`, disk == HEAD, zero
`linearUpwind` in the file's full history) **struck the "linearUpwind→linear" clause** and
adopted a **RESOLUTION-ONLY** lever, schemes unchanged. This is a legal pre-compute
correction (rule 2): grounded in the frozen base file, it moves no gate, band, cap,
ceiling or label. `[lab-attributed]` — not Sanaa's word and not any agent's consent
(rule 9).

### 1.3 The corrected diagnosis, made ANSWER-BLIND, of BOTH base problems

- **Problem 1 — non-asymptotic triple (p = 0.143).** With an already-2nd-order central
  scheme, `p ≈ 0.14` is not a scheme-order defect. It is the signature of a solution that
  is **not smooth at the grid scale**: the **blunt leading-edge corner is a geometric
  singularity** (separation is pinned there), which caps the *global* observed order below
  the formal 2 and slows convergence; and the **separated shear layer / bubble** is
  under-resolved at 92 160 cells (Δx ≈ 4.11 mm at the crossing). Lever: **resolution**.
- **Problem 2 — value 40 % high.** Central differencing carries no numerical diffusion,
  and `LR/(2t)` **decreases monotonically toward 4.0** with refinement (6.79 → 6.16 →
  5.60). The overprediction is therefore **under-resolution**, not a scheme artefact. The
  setup was audited against the manual and matches (see §2); no setup bug was found. The
  only unquantified setup difference is Ansys's own domain from the unopened `.wbpz`
  archive — blockage `t/H = 2.5 %`, far too small to explain a 40 % deviation. **Whether a
  properly resolved 2nd-order triple lands inside ±10 % is NOT predicted here** (that would
  be gate-fitting); the falsifiable content is §10.

### 1.4 The lever, and why it is DOF-free (L-501)

**The R2 case inputs are BYTE-IDENTICAL to VMFL063's** — all nine case files hash equal to
the base's blobs (`fvSchemes` `0b7e1837`, `fvSolution` `abd77454`, `blockMeshDict.template`
`c9f13019`, `0/U` `c4865c13`, `0/p` `d464d974`, `transportProperties` `c9155718`,
`momentumTransport`/`turbulenceProperties` `f7d93d54`, `controlDict.template` `6f66d474`).
**The only change in R2 is the cell count.** The schemes, boundary conditions, materials,
geometry law and grading law are provably unchanged, which is exactly what "resolution-only"
must mean.

The triple **inherits the base's own self-similar grading verbatim** and shifts the family
**up one octave** (§4): R2 L1 = base L2, R2 L2 = base L3, R2 L3 = a new finest at 4× the
base's finest. Because the grading ratios are inherited unchanged and every count doubles
per level (`r = 2`), there is **no continuous grading degree of freedom** to tune — the
VMFL022 grading-DOF hazard the supervisor rejected (L-501) is absent by construction. Cell
counts were sized by an **answer-blind buildability + cost smoke** (§7), never by reading
`LR`.

---

## 2. THE CASE, EXACTLY AS THE MANUAL STATES IT (UNCHANGED FROM THE BASE)

Manual p.193, load-bearing numbers reproduced without adjustment; the frozen case files
are byte-identical to VMFL063's, so this table is the base's, re-audited at this freeze:

| quantity | manual value | in the frozen case files |
|---|---|---|
| density | 1 kg/m³ | kinematic pressure, `rho = 1` |
| viscosity | 1.7894e-5 kg/m-s | `constant/transportProperties`: `nu 1.7894e-05` |
| plate thickness 2t | 90 mm | `TWO_T = 0.090`; plate top surface at `y = t = 0.045` |
| plate length | 1500 mm | outlet at `x = 1.5 m` |
| inlet velocity | 0.0517 m/s | `0/U`: `fixedValue uniform (0.0517 0 0)` |
| Reynolds number | 260 | derived `0.0517·0.090/1.7894e-5 = 260.03`; the comparator's `--selftest` checks this reproduces 260 to better than 2e-4 |
| turbulence | laminar | `constant/momentumTransport`: `simulationType laminar` |
| convection scheme | (manual: "high resolution") | `div(phi,U) bounded Gauss linear` — **2nd-order central, UNCHANGED from base** |

**Setup audit for a bug (Problem 2, option b): none found.** Inlet `fixedValue` 0.0517,
outlet `zeroGradient U` / `p = 0`, `plateFace`/`plateTop` `noSlip`, `centreline`/`farfield`
`symmetryPlane`, `frontAndBack` `empty`; half-domain by symmetry about the plate centreline
`y = 0`; blunt face at `x = 0`, `0 ≤ y ≤ 0.045`; plate top at `y = 0.045`. All consistent
with the manual. (Cosmetic only, carried verbatim to preserve byte-identity: the
`turbulenceProperties` file header reads `object momentumTransport;`; its content is
`laminar` and OpenFOAM reads it correctly.)

**THE ARCHIVE WAS NOT OPENED.** `VMFL063_WB.wbpz` (sha256 `8b037b7b79cf13b9…`) was not
read; Ansys's domain extents remain unknown to this registration and the domain is this
lab's choice (§4), disclosed with its blockage (§9). Neither archive copy is written,
moved or deleted.

---

## 3. THE REFERENCE TIER, AND WHY `PASS` IS OUT OF REACH FOR LIMB A (UNCHANGED)

**Reference kind: EXPERIMENTAL** — Lane & Loehrke measured the reattachment length; the
manual carries their value as *Target 4.0*. Limb A makes a **CONTINUUM claim**, whose
ceiling under `VERIFICATION_CHARTER` §2f.3 is **`GATE REACHED`** — *"a property of the
continuum solution, from which discretisation error is not separable … `PASS` is
unavailable."* The ceiling is hard-coded (`TIER_CEILING_A = "GATE REACHED"`) and
`verdict_for_limb_a()` **refuses (exit 2) if it ever produces `PASS`**.

**Limb B is a SAME-DISCRETE-PROBLEM IDENTITY claim** (§2f.3, second row) — L1 vs its twin
L1D, same discrete problem solved twice; the error cancels exactly, a triple is
irrelevant, `PASS` is available. **The ROW verdict is the WORST limb** (`row_verdict()`
minimises over `NOT A RESULT < GATE FAIL < GATE REACHED < PASS`), so **the best possible
R2 row is `GATE REACHED`, which is not a credential** (`ANSYS_VERIFICATION_CHARTER` §6:
*"Only `PASS` rows are credentials."*). Stated before compute so nobody later reads limb
B's `PASS` as one.

---

## 4. THE MESH FAMILY AND THE ROACHE TRIPLE (THE ONE THING R2 CHANGES)

Cartesian 2-D, all-hex, three blocks, built by `blockMesh` from
`case/system/blockMeshDict.template` — **byte-identical to the base template** (blob
`c9f13019`). Origin at the blunt leading-edge face on the plate centreline. Domain,
inherited a priori and never from a run: upstream `Lu = 0.900 m = 10·2t`; downstream
`Ld = 1.500 m` (the manual's plate length, outlet at the plate end); far field
`H = 1.800 m = 20·2t`. Boundaries as the base (§2).

### The grading, inherited VERBATIM (no new DOF)

Block A `simpleGrading (0.1 0.2 1)`, block B `(0.1 160 1)`, block C `(20 160 1)` — the
downstream graded region concentrates cells at the leading edge (x, last/first = 20) and
at the plate top (y, last/first = 160). **These ratios are the base's, unchanged.** The
`r = 2` family doubles all four counts per level, so every local cell dimension halves and
the meshes remain one self-similar family.

### The three levels, r = 2 — the family shifted up one octave

| level | NXU | NXD | NYL | NYU | block A | block B | block C | **total cells** | = base level |
|---|---|---|---|---|---|---|---|---|---|
| **L1** | 64 | 160 | 24 | 96 | 1 536 | 6 144 | 15 360 | **23 040** | base L2 |
| **L2** | 128 | 320 | 48 | 192 | 6 144 | 24 576 | 61 440 | **92 160** | base L3 |
| **L3** | 256 | 640 | 96 | 384 | 24 576 | 98 304 | 245 760 | **368 640** | **new finest, 4× base L3** |
| L1D | 64 | 160 | 24 | 96 | 1 536 | 6 144 | 15 360 | 23 040 (limb B twin, identical to L1) |

**Resolution (mm), computed by halving from the base's own frozen resolution table** (the
identical grading law):

| resolution | L1 (=base L2) | L2 (=base L3) | L3 (new) |
|---|---|---|---|
| first cell off `plateTop` | 0.5740 | 0.2894 | **0.1447** |
| first cell at the leading edge, Δx | 1.4721 | 0.7376 | **0.3688** |
| Δx at the expected reattachment x = 0.36 m | 8.1761 | 4.1130 | **2.0565** |

The finest R2 level resolves the reattachment region to Δx ≈ 2.06 mm, **twice as fine as
the base's finest** (4.11 mm), and the leading-edge first cell to 0.37 mm.

**The r-honesty limit is inherited too:** with the total expansion ratios held fixed while
counts double, the *local* size ratio between consecutive levels lies in
**[1.967, 2.052]**, i.e. within −1.65 % / +2.60 % of the formula's `r = 2.0`, giving at
most **3.75 %** in the observed order `p` and comparably in the GCI. Stated, not adjusted.

### The triple, and rule 5

- Functional: **`LR/(2t)` itself**, at each level, read exactly as the base read it (the
  LAST reversed-to-attached crossing of the physical `plateTop` wall shear in the frozen
  window, linearly interpolated). **The reduction is unchanged.**
- `roache(f_L1, f_L2, f_L3)` with `r = 2.0`, **`Fs = 1.25`**, floor **`P_MIN = 0.05`**.
- **A triple that is not `CONVERGING` makes the row `NOT A RESULT`, whatever the value**
  (rule 5 step 2). A GCI is quoted only on a `CONVERGING` triple; rule 5 is one-way.

---

## 5. THE GATE — BYTE-IDENTICAL TO THE BASE (L-487)

### Limb A — CONTINUUM, ceiling `GATE REACHED`

```
LR = the LAST reversed-to-attached crossing of the physical wall shear on plateTop,
     inside the frozen window  X_WIN_LO < x <= X_WIN_HI,  linearly interpolated.
GATE:  |LR/(2t) - 4.0| / 4.0  <=  0.10     at the finest level L3
AND    the Roache triple on LR/(2t) is CONVERGING
```

**Every gate constant is byte-identical to the base comparator** (blob `fc339a79`),
verified constant-by-constant at this freeze: `REF_LR2T = 4.0`, `TOL = 0.10`,
`X_WIN_LO/X_WIN_HI = 0.0/1.2`, `X_SIGN_REF = 1.35`, `TAU_EPS = 1e-14`, `FS = 1.25`,
`RATIO = 2.0`, `P_MIN = 0.05`, `K_PLANT = K_PLANT_U = 0.05`, `CROSS_TOL_CELLS = 3.0`,
`TIER_CEILING_A = "GATE REACHED"`, `TIER_CEILING_B = "PASS"`. **The gate is not touched by
R2** — R2 changes only the mesh (§1.4, L-487: a successor never widens the band). The
justification for the 10 % band is the base's (PREREGISTRATION §5): the register's existing
band for this quantity class (row #30, VMFL064-R2), wider than the manual's own agreement
class (Fluent 1.04, CFX 1.01), and no tighter than the two-significant-figure Target can
support (±1.25 %).

**The sign convention is fixed from the data** at `X_SIGN_REF = 1.35 m` (outside the
window); the cross-instrument check (near-wall `u_x`, `CROSS_TOL_CELLS = 3.0` local cell
widths) gates; the last-crossing (not first-crossing) reader is inherited (the corner-eddy
repair adopted in advance for VMFL064's row-#29 defect). All unchanged from the base.

### Limb A — GATE-BLIND PHYSICAL-RANGE REFUSAL (new in R2)

Before any value is graded, the comparator refuses (exit 2) if `LR` is not a positive
distance lying inside the frozen search window: `physical_range_refuse(lr, lr/2t, level)`
requires `0 < LR ≤ X_WIN_HI` and `0 < LR/(2t) ≤ LR2T_PHYS_MAX = X_WIN_HI/TWO_T = 13.333…`.
**This bound is GEOMETRIC — it references the frozen window and the plate thickness ONLY,
and NEITHER the Target 4.0 NOR the ±10 % band** — so it cannot be a disguised gate: a value
inside it is not thereby `PASS`, and the band still decides. `--selftest` drives it to both
outcomes and checks the bound is `X_WIN_HI/TWO_T`, not `REF_LR2T`.

### Limb B — SAME-DISCRETE-PROBLEM IDENTITY, ceiling `PASS` (retained)

```
L1D is a SECOND independent solve of L1's discrete problem: identical inputs, mesh,
endTime, run in its own directory.
GATE:  same converged iteration count
  AND  sha256(<t>/{wallShearStress,U,p}) identical between L1 and L1D
  AND  LR bitwise equal between L1 and L1D
```

Band: EXACT IDENTITY; no tolerance. Retained from the base at the supervisor's direction.

---

## 6. STRICT COMPLETION (CLAUDE.md rule 4, IN FULL) — UNCHANGED BASIS

Applied at every level including L1D; the comparator **REFUSES (exit 2)** on any failed
clause. The basis is the base's, declared before compute and unchanged:

1. **`rc = 0`** from `RUN_RC.<level>`, captured *inside* the detached subshell.
2. **An `End` line** in `log.simpleFoam`, matched by exact filename via the cardinality
   guard.
3. **`SIMPLE solution converged` present.**
4. **last `Time` < `endTime`** — the **declared adaptation** of rule 4's "last == endTime"
   clause for a `residualControl`-terminated STEADY solve: `last == endTime` means the
   solver ran out of clock without converging (the opposite of completion). Confirmed
   admissible at R2 by the answer-blind smoke (§7): L1 converged at **1944 iterations**
   against `endTime = 30000`, well short of the ceiling.
5. **`ExecutionTime` count == the iteration count.**
6. **Fields present at that time:** `U`, `p`, `wallShearStress`, `Cx`, `Cy`.
7. **Numerically-latest time directory (key=float) == the log's last `Time`.**
8. **AGE GUARD** — every field at `endTime` strictly newer than the case's own `0/U`,
   which the launcher `touch`es last; the launcher refuses to launch into a level directory
   that already holds a `0/` or a numeric time directory.

**INFRASTRUCTURE (L-342):** `RUN_RC.<level>` absent → rc `NOT MEASURED`, disclosed, grade
proceeds on the physics clauses; present and non-zero → REFUSE.

---

## 7. COST (CLAUDE.md rule 12) — BUILT ON A MEASURED BASIS, ANSWER-BLIND

**Answer-blind sizing smoke, scratch only, 2026-09-07** (`LR`/`wallShearStress` never read
— the smoke deleted the `wallShearStress` output unread). It ran under a scratch directory,
never under `verification/runs/`, so it created no `0/` or time directory there and did not
consume the age guard.

- **Buildability:** the finest R2 level **L3 (368 640 cells)** built with `blockMesh` and
  passed `checkMesh` — `Mesh OK`, `failed_checks: 0`, max non-orthogonality **0**, max
  aspect ratio **62.97** (same family as the base). L1 (23 040) also built clean.
- **Throughput / iterations:** R2 **L1 (23 040)** solved to `residualControl` in **1 944
  iterations** (identical to base L2's 1 944 — the same mesh), **60.4 wall s = 1.007
  core-min** on this box (quiet). Measured throughput ≈ **1.35e-6 s/cell/iteration**.

| solve | cells | predicted iterations | basis | predicted core-min |
|---|---|---|---|---|
| L1 | 23 040 | 1 944 | **measured this box** | **1.1** |
| L1D | 23 040 | 1 944 | = L1 | **1.1** |
| L2 | 92 160 | 4 177 | base actual (same mesh, row #44) | **12.3** |
| L3 | 368 640 | ≈ 8 770 | iters ∝ N^0.552 (base L2→L3) at ≈1.95e-6 s/cell/iter | **≈ 108** |
| **total** | | | | **ESTIMATE 125 core-min** |

| item | value |
|---|---|
| **ranks** | 1 (serial, all four solves) |
| **ESTIMATE** | **125 core-min** total |
| **CAP** | **320 core-min, RUNNING TOTAL across all four solves** (2.56× the estimate) |
| `cost_basis` | c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 — **REPORTED-BY-OWNER, NOT MEASURED**; the box cannot read its own billing. Dollars **DERIVED**. |
| **$ at estimate** | **$0.1069 derived** (125/60 × 0.0513) |
| **$ at cap** | **$0.2736 derived** (320/60 × 0.0513) |

**Why the cap is 2.56× and not the base's 5.6×.** Two of the four solves now have a
*measured* cost on this exact family (L1 measured here; L2 = the base's own L3 actual), so
only L3 is extrapolated. The remaining uncertainty is L3's iteration count (extrapolated
`∝ N^0.552`) and its throughput (which rises with cell count); 320 core-min covers a
1.5× iteration and 1.2× throughput surprise on L3 with margin. **An overrun STOPS the run
(rc 124) and does NOT get a new budget; `endTime` is never reduced to fit a cap.** The cap
is drawn down level by level in the launcher (`timeout_s = remaining_core_min·60/RANKS`).
Both the estimate and the cap sit far under the $25 pre-authorised ceiling.

**Estimate-versus-actual calibration is OWED at completion** (rule 12): actuals from
`COST.txt` and each `RUN_RC.<level>`, the ratio actual/predicted, attribution (contention /
waste / misprediction, waste named separately), dollars derived and labelled, one row in
`docs/COST_CALIBRATION.md`.

---

## 8. THE PLANTED-ZERO CONTROL (CLAUDE.md rule 3), MATCHED TO THE REDUCTION (L-487)

The reduction is a **crossing locator** (the last reversed-to-attached crossing), so
L-487's rule for a location/crossing applies: *the plant must MOVE the feature.* The base's
two-stage control is inherited unchanged and is correct for this reduction:

- **P1a — reader sensitivity:** a sized offset `K_PLANT·max|τ|` added to the x-component of
  **every** `plateTop` face of a **copy of the real solver bytes**, read back **from disk**
  through the real reader; every value must move by exactly the plant.
- **P1b — gate-functional sensitivity:** the same planted file run through the **full gate
  functional**; shifting the physical wall shear up must move the last crossing **upstream**
  or out of the window. The same two stages run on the independent near-wall `u_x` channel.

Either stage failing REFUSES (exit 2). `--selftest` shows the control able to **fail**: it
monkeypatches the writer so the plant never reaches disk (control refuses) and drives a
channel that is identically zero (control refuses — nothing to size against).

**NEW in R2 — the L-487 matched pair, made explicit in `--selftest`.** Two arms on the same
bubble prove the crossing reader is a genuine feature-locator, not a whole-field statistic:
a **GOOD arm** (a whole-profile positive shift moves the crossing upstream) and an
**INERT arm** (an equal shift applied only to already-attached faces downstream of the
crossing leaves the last crossing **unmoved**). If the inert arm moved the crossing, the
reader would be responding to values away from the feature — exactly L-487's failure to
avoid. Both arms are checked.

**The AST guard, cardinality guard and numeric-time-dir cross-check are inherited
unchanged.** `ast.Assert` count **0**, `ast.Raise` count **46** (re-derived at this freeze
by walking the file's AST). `--selftest`: **68 checks, 0 failures, rc 0 under BOTH `python3`
and `python3 -O`** (`__pycache__` cleared before each). The two outputs are not
byte-identical (the sandbox path is random per invocation, as the base's Amendment 1
established); the launcher checks PASS count, FAIL count, exit rc and the AST-guard marker
under both interpreters, the all-checks-passed line, the absence of any `[FAIL]` line, and
the named control markers.

---

## 9. ERROR BUDGET — disclosed BEFORE the freeze (inherited; blockage re-stated)

`ANSYS_VERIFICATION_CHARTER` Amendment 1.4 Clause A (the axisymmetric-`wedge` bias) **does
not apply**: VMFL063-R2 is Cartesian 2-D with `empty` front/back patches — no wedge, no
`sec(t/2)` bias.

| source | magnitude | sign / direction | how obtained |
|---|---|---|---|
| Blockage of the far field | `t/H = 2.50 %`; free stream accelerates by +2.564 % | **SIGN NOT ASSERTED** (no measurement of the effect on LR) | geometry, exactly |
| Reference resolution | Target 4.0, 2 s.f. → ±1.25 % | symmetric | manual Table .63.1 |
| Leading-edge corner singularity | caps the observed order below the formal 2 (§1.3) | reduces `p`; magnitude unknown a priori | numerics of a sharp reentrant corner |
| Refinement ratio | local r ∈ [1.967, 2.052] → ≤ 3.75 % in `p` and the GCI | symmetric | §4 |
| Two-dimensionality | finite-span experiment | NOT QUANTIFIED — named, not priced | — |
| Ansys's own domain | unknown; archive not opened | — | §2 |

**None of these widens the band. The band is 10 % and stays 10 %.**

---

## 10. NAMED LIVE OUTCOMES — every one can happen, each written down now

The fixed vocabulary and nothing else (rule 1).

| # | outcome | the condition that produces it |
|---|---|---|
| 1 | **ROW `GATE REACHED`** *(best attainable)* | triple `CONVERGING`, L3 inside the 10 % band, L1/L1D exactly identical. **Not a credential.** |
| 2 | **ROW `GATE FAIL` (physics)** | triple `CONVERGING`, L3 **outside** the 10 % band. **If a resolved 2nd-order triple is still ~40 % off, this GATE FAIL STANDS** — the mesh and grading are NOT tuned to reach 4.0 (rule 2; L-501). A finding, recorded with its numbers. |
| 3 | **ROW `GATE FAIL` (determinism)** | limb A holds but L1/L1D differ in any hash, iteration count or LR bit. |
| 4 | **ROW `NOT A RESULT` — triple not `CONVERGING`** | `DIVERGENT`, `OSCILLATORY`, `STAGNANT`/`p < P_MIN`, or `EXACT`. **This is the primary risk of R2, named honestly:** the leading-edge corner singularity may cap the observed order so the finer triple still does not reach the asymptotic range. If so the row is `NOT A RESULT` and is **NOT rescued by dropping the level that failed** (L-500), by widening the band (L-487) or by re-picking the triple. No GCI printed. |
| 5 | **`NOT A RESULT` — the solve never converged** | no `SIMPLE solution converged`, or last `Time` == `endTime`. The smoke makes this unlikely at L1/L2; it is retained as admissible for L3. |
| 6 | **`NOT A RESULT` — no crossing in the window** | the bubble does not close in (0, 1.2] m. The comparator refuses; it does not extend the window. |
| 7 | **`NOT A RESULT` — cross-instrument disagreement** | wall shear and near-wall `u_x` locate the event > 3 local cell widths apart. |
| 8 | **`NOT A RESULT` — a control did not fire** | either plant stage unseen on either channel; cardinality ≠ 1; orientation reference \|τ\| < 1e-14; AST guard finding an `assert`; **or the gate-blind physical-range refusal** (LR non-positive or outside the geometric window bound). |
| 9 | **`NOT A RESULT` — completion clause failed** | missing `End`, `ExecutionTime` mismatch, a missing field, the age guard, a recorded non-zero rc, or the time-directory cross-check disagreeing. |
| 10 | **`BLOCKED`** | toolchain absent or `blockMesh` fails. A crash is a FINDING, not a retry. |
| 11 | **`PENDING`** | registered and not yet run — the state this document is in as committed. |

**`PASS` at row level is unreachable by construction (§3).**

**THE PREDICTION.** This lane declines to predict which outcome lands. What is predicted,
and is this document's falsifiable content, is that **the gate above can return any of
them** — it is not constructed so that only one answer is possible — and that the finer
2nd-order triple **directly tests the under-resolution diagnosis of §1.3**: if
under-resolution is the cause, `LR/(2t)` continues to fall toward 4.0 and the triple's GCI
falls below the deviation; if the corner singularity caps the order, the triple does not
reach the asymptotic range and the honest answer is `NOT A RESULT`.

---

## 11. THE GRADING PATH, FROZEN

| artefact | path |
|---|---|
| pre-registration | `cases/ansys_verification/VMFL063-R2/PREREGISTRATION.md` (this file) |
| comparator | `cases/ansys_verification/VMFL063-R2/grade_vmfl063_r2.py` |
| launcher | `cases/ansys_verification/VMFL063-R2/run_vmfl063_r2.sh` |
| case inputs | `cases/ansys_verification/VMFL063-R2/case/` — 9 files, byte-identical to VMFL063's |
| run root | `verification/runs/ansys_verification/VMFL063-R2/` — **does not exist** |

**The launcher refuses to spend a core-minute unless, at launch:** this file and the
comparator on disk hash equal to their HEAD blobs; all nine case inputs hash equal to their
own HEAD blobs; the comparator's `--selftest` is green under both interpreters with the
named control markers; and each level directory holds no `0/` and no numeric time
directory. `grade_vmfl063_r2.py --verify-frozen` re-hashes this file and the comparator
against HEAD at grade time (rc 2 on mismatch).

**PRE-FLIGHT SMOKE** (`ANSYS_VERIFICATION_CHARTER` Amendment 1.4 Clause B). The §7
answer-blind smoke has already exercised `blockMesh`/`checkMesh`/`simpleFoam` on this exact
family in scratch, `LR` never read; it establishes buildability and cost. A graded run is a
SEPARATE act under the frozen launcher, and **is HELD pending Sanaa's launch decision**
(rule 9): nothing in this document authorises a graded solve.

---

## 12. WHAT THIS REGISTRATION DOES NOT CLAIM

- It is not a statement about Ansys; this box has no Ansys solver. Fluent's 4.16 and CFX's
  4.05 are context, never the gate.
- It does not claim the archive's setup; `VMFL063_WB.wbpz` was not opened.
- It cannot earn a credential — ceiling `GATE REACHED` at row level, by construction.
- It establishes nothing about meshes finer than L3.
- It does not assert that a finer triple reaches the asymptotic range; §10 outcome 4 names
  the opposite as the primary risk.
- Nothing here is sent anywhere. Submissions are parked; the manual is proprietary Ansys
  documentation held for this lab's private use (rules 7 and 8).
