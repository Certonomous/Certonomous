# SUBOFF **A1d** — THE BARE-HULL α SWEEP — **THE ONLY ROUTE TO A MEASURED-TIER SUBOFF FORCE RESULT** — PRE-REGISTRATION

**STATUS: DRAFT. NOT FROZEN. NOT LAUNCHED.** §10 is blank and is the cfd-supervisor's
personally, undelegated (check 4).

**Author:** cfd `lab-lane`, 2026-09-12.
**Authorised by:** cfd-supervisor's ruling on `SUBOFF_A1c_PREREGISTRATION.md` §6.2 — the
bare-hull arm runs **FIRST, ahead of hull+sail**, because it validates the whole method
(mesh → solver → `forceCoeffs` → α sweep → antisymmetry → derivative fit) **against
measurement** before the larger sum is spent on the configuration that can only be graded
against ourselves.

**Pre-compute condition (rule 2), checked not assumed:** the run directories named in §6 —
`verification/runs/navier_class/SUBOFF_A1d/` — **do not exist**, no mesh for this arm exists
(§3), and no queue entry references A1d.

---

## 1. WHY A1d EXISTS, IN ONE PARAGRAPH

A1c can grade `Z_w'` and `M_w'` for **hull + sail** only against a **bracket this lab
constructed for itself**, because Roddy 1990 never measured a hull+sail body in the vertical
plane (A1c §1). A1d grades the **bare hull**, where Roddy *did* measure, where axisymmetry
makes the plane-equivalence **exact rather than approximate**, and where the band therefore
carries a **measured 4 % width from the source**. **A1d is the only run in the SUBOFF
campaign that can reach MEASURED tier.**

---

## 2. 🔴 THE REFERENCE — VERIFIED TO BE A STATIC SWEEP, NOT A DERIVED NUMBER

A first reading of Roddy's Table 3 through the OCR text layer appeared to show
**Configuration 3 with no static-stability row** — which would have meant `Y_v'` was derived
rather than measured, and would have destroyed A1d's MEASURED tier before it began. **This
lane rendered the page rather than trusting that reading.**

Roddy **Table 3**, report p. 17 (PDF p. 25 of the filed file), rendered at 150 dpi and read:

> **CONFIGURATION 3 — HORIZONTAL PLANE, BARE HULL**
> | Type of Test | Angles of Drift (deg) | Rudder Angles | Model Speeds (knots) | Omega |
> |---|---|---|---|---|
> | **Static Stability** | **±18** | NA | **6.5** | — |
> | Swaying | 0 | NA | 0.0 | 1.112 & 2.220 |
> | Yawing | 0 | NA | 0.0 | 1.112 & 2.220 |
> | Yawing | 0 | NA | 4.5, 5.0, 6.0, 6.5 | 2.220 |

**The static sweep exists: ±18° of drift at 6.5 knots.** The OCR had dropped the row. So
`Y_v' = −0.005948` and `N_v' = −0.012795` are **measured static-sweep derivatives**, read as
the slope at zero body angle, exactly as for Configs 1 and 4. **MEASURED tier holds.**

> **And a consequence that is pure gain: Roddy's measured range is ±18°, so our sweep at
> ±12° sits INSIDE it. A1d extrapolates nothing.**

**Plane-equivalence, and why it is exact here.** The bare hull is a body of revolution. Its
vertical and horizontal planes are related by a rigid rotation about the x axis, so
`|Z_w'| = |Y_v'|` and `|M_w'| = |N_v'|` are **identities, not approximations** — unlike
A1c's hull+sail case, where the sail breaks the equivalence and forced a bracket. Signs
follow the convention verified in A1c §7.1 and signed by the cfd-supervisor: `Z_w' = Y_v'`,
`M_w' = −N_v'`.

---

## 3. 🔴 THE EXISTING BARE-HULL MESHES **CANNOT BE USED**, AND THIS IS THE COST THE RULING DID NOT YET HAVE

The ruling reasoned that the bare hull is "a simpler geometry". **It is — but the lab's
existing bare-hull meshes are not reusable for a sweep, and the arm is not free.**

`verification/runs/navier_class/SUBOFF/r1b_{coarse,medium,fine}/constant/polyMesh/boundary`
carry the patches **`inlet outlet farfield hull axis frontWedge backWedge`**. That is an
**axisymmetric WEDGE mesh** — a single slice about the axis. The wedge formulation *assumes
the solution is axisymmetric about that axis*. **At α ≠ 0 the flow is not axisymmetric, and
the wedge is invalid by construction.** These meshes can represent exactly one point of the
sweep, α = 0, and they cannot represent the other six.

> **A1d therefore requires a NEW 3-D half-model mesh of the bare hull. It does not inherit
> one. Any plan that assumed reuse is wrong, and I would rather say so before the cost is
> approved than after.**

**A second fact about the foundation, stated plainly:** `SUBOFF_R1b_RESULTS.md` records the
bare-hull α = 0 rung's verdict of record as **`NOT A RESULT`** on a `DIVERGENT` triple.
**A1d is not building on a passing result.** That is an argument *for* A1d, not against it —
the bare hull has never been carried to a defensible force number on this box — but it
forbids any claim that A1d merely extends a working case.

---

## 4. THE BANDS, WRITTEN FIRST

Definitions fixed before any solve, identical to A1c so the two arms are comparable:
`Z_w'`, `M_w'` by least-squares linear fit over the **five points |α| ≤ 8**;
α = ±12 carried but **excluded from the fit** and reported as the linearity check;
`x_np/L ≡ −M_w'/Z_w'`; nondimensionalisation on `L`.

| # | Quantity | Registered band | Tier | Source |
|---|---|---|---|---|
| **D1** | `Z_w'` | `[−0.006186, −0.005710]` (−0.005948 ± 4 %) | 🟢 **MEASURED** | Roddy Table 4 Config 3 `Y_v'`; width from Roddy App. C p.105 |
| **D2** | `M_w'` | `[+0.012283, +0.013307]` (+0.012795 ± 4 %) | 🟢 **MEASURED** | Roddy Table 4 Config 3 `N_v'`, sign per A1c §7.1 as signed |
| **D3** | `x_np/L` | `[1.99, 2.33]` | 🟢 **MEASURED (propagated)** | conservative envelope of D1/D2 corners |
| **D4** | Antisymmetry `\|Z(+α) + Z(−α)\| / \|Z(α=8)\|` | **`≤ 0.5 %`** | **CODE-VERIFIED** | §5 — tighter than A1c's 2 %, and §5 says why |
| **D5** | Linearity: `Z(±12)` deviation from the |α| ≤ 8 fit | **reported, not gated** | reported | the fit is a slope at zero; ±12 is a disclosure, not a gate |

**D3 is the conservative (fully-correlated-adverse) envelope**, `0.012283/0.006186 = 1.986`
to `0.013307/0.005710 = 2.330`, **not** an RSS: `Z_w'` and `M_w'` come from the *same*
experiment and their errors are not independent, so the narrower RSS interval would
understate the band. **Widening on purpose, and saying so, is the honest direction.**

**The verdict rule (rule 1 vocabulary, and no other):** each of D1/D2/D3 is **`PASS`** inside
its band or **`GATE FAIL`** outside it — **unless** the completion rule (rule 4) or D4 fails,
in which case the row is **`NOT A RESULT`** whatever the value, per the A1c/A1b ordering.

---

## 5. WHY D4 IS TIGHTER HERE — THE BARE HULL HAS A FALSIFIER THE HULL+SAIL CANNOT HAVE

On hull+sail the antisymmetry check is soft, because the **sail is dorsal**: the geometry is
genuinely not symmetric top-to-bottom, so `Z(+α) ≠ −Z(−α)` is *physically expected* and the
check can only be loose (A1c's B7 at 2 %).

**The bare hull is a body of revolution.** Top-to-bottom symmetry is exact, so
`Z(+α) = −Z(−α)` and `M(+α) = −M(−α)` are **exact statements about the continuous problem**,
and any departure is **entirely numerical** — mesh asymmetry, an incorrect rotation of
`liftDir`/`dragDir`, a sign error in the moment, or incomplete convergence.

> **This makes A1d a far better test of the METHOD than A1c can be, which is exactly the
> ruling's reasoning.** D4 at 0.5 % is a direct, experiment-free probe of the rotation
> convention and the force post-processing — the machinery A1c then depends on and cannot
> independently check. **If D4 fails on the bare hull, no hull+sail number is trustworthy,
> and we will have learned it on the cheap arm.**

**One further control, cheap and decisive, and it is registered here:** rerun the α = +8
point as a **yaw** case at β = +8 on the same mesh. For a body of revolution the two are the
same computation in a rotated frame, so `Y(β=8)` must equal `Z(α=8)` to the same 0.5 %.
**This catches a class of error that no pitch-only sweep can see** — a coordinate or
`liftDir` convention that is self-consistently wrong across all seven pitch points.

---

## 6. THE RUNS

Carried from A1b §3 / A1c §5 so the arms are comparable: `simpleFoam`, `kOmegaSST`,
`nutUSpaldingWallFunction` on `hull`, **half model with a `symmetryPlane`**,
`Re_L = 1.2e7`, `U = 2.7547576 m/s`, `endTime 3000`, `deltaT 1`, 4 ranks, **no
`residualControl`** (an early residual exit satisfies neither `last == endTime` nor the
`ExecutionTime`-count clause), `0/T` age-guarded, checkpointed at 30 min wall with the last
two kept per Sanaa's run instruction, launched **as `ubuntu`, never root**, detached under
the runner (nothing hand-launched counts as a case).

**Sweep: α = −12, −8, −4, 0, +4, +8, +12** — seven points — plus the **one β = +8 control**
of §5. Eight solves per level. Mesh identical across all eight; only `0/U` and the
`forceCoeffs` directions change.

**Patches expected:** `inlet outlet farfield symm hull` — **five, with no `sail`**. A mesh
presenting a `sail` patch is the wrong geometry and the launcher must refuse it.

**Geometry, from two held and title-page-verified sources rather than one:** Groves 1989
(`groves_1989_dtrc_shd1298_darpa_suboff_geometry.pdf`, the analytic hull definition — the
bare hull regenerates exactly from its equations) **cross-checked against Roddy's own
Table 2**, "Nondimensional offsets and cross sectional areas for the hull" (report p. 16,
PDF p. 24, rendered and read), which tabulates `B/B_x` and `A/A_x` at 25 stations from 0.0
to 20.4167. **Registered check: the built geometry must reproduce Roddy Table 2's `A/A_x` at
all 25 stations to within 0.5 %.** Two independent sources agreeing is worth more than one
source trusted.

> 🔴 **AND THE TABLE'S INTERNAL IDENTITY DOES A SECOND JOB THAT MUST BE NAMED, BECAUSE IT IS
> LOAD-BEARING FOR THIS WHOLE ARM.** `A/A_max ≡ (B/B_max)²` holding at all 25 rows is not
> only a transcription check. **It is an independent confirmation, from the reference itself,
> that the tabulated body IS a body of revolution** — and *that* identity is what makes the
> vertical/horizontal plane-equivalence in §2 **exact rather than approximate**, which is the
> entire reason D1/D2 can be MEASURED-tier bands instead of the brackets A1c was forced into.
> **If that identity failed, A1d would not merely have a transcription problem; it would have
> no reference at all.** The check is therefore registered as a **gate on the reference**, not
> merely a gate on the typing, and it is evaluated before any comparison is attempted.

---

## 7. COST — REGISTERED, DERIVED, AND **NOT A KILL**

**The mesh does not exist, so the cell count is an ESTIMATE and is labelled one.** At A1's
L1 the wall faces are `hull` 116,686 and `sail` 83,291 — **the sail carries 42 % of the wall
faces** despite being a small appendage, because of the fairwater/hull junction refinement.
Removing it, the bare hull at L1-equivalent resolution is estimated at **0.55–0.70 × 3,268,613
≈ 1.8–2.3 M cells**.

| | Basis | Per point | × 8 solves | Derived $ |
|---|---|---|---|---|
| **A1d L1** | 0.62 × A1 L1's 6,280 core-min | ≈ **3,900 core-min** | ≈ **31,200 core-min** | ≈ **$26.68** |

`cost_basis`: **$0.0513/core-h is OWNER-STATED** (Sanaa 2026-08-21/22), **not measured** —
the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). The **cell count is an
estimate, not a measurement**, and the per-point rate inherits A1b §6's anchor on the
**worse, later** measured rate under a 2.4× intra-night swing. **Both are predictions to be
scored at completion under rule 12**, with the actual cell count replacing the estimate and
contention attributed on its own line, landing as a row in `docs/COST_CALIBRATION.md`.

> **Registered and stopping nothing** (Sanaa, directive #17; and "Cost estimate registered
> too but doesnt stop the run"). **The overrun rule is that a crossed estimate is REPORTED
> and the row is graded on its merits — the run is not killed by a wrapper.**

**Note for the record, not as an authorisation:** ≈ $26.68 is close to the $25 figure in
Sanaa's 2026-08-21 blanket. **A blanket is not a per-item read (rule 9)** — this is cited as
context, and the cost stands or falls on the cfd-supervisor's §10 signature, not on the
blanket.

---

## 8. FALSIFIERS — EACH THE COMPLEMENT OF ITS PREDICTION

**EXECUTION.** X1: any level fails rule 4 (rc = 0, `End` line, `last == endTime`, fields
present, `ExecutionTime` count, every field newer than the case's own `0/T`) → that point is
**`NOT A RESULT`**; a sweep missing any of the five |α| ≤ 8 points cannot produce a
derivative and the whole arm is **`NOT A RESULT`**.

**ARTIFACT.** X2: `forceCoeffs` output absent, or the `hull` integration not reproducing the
total to 1e-9 relative → **`NOT A RESULT`** (the A1c §4 discipline, applied here to a single
patch).

**METHOD.** X3: **D4 > 0.5 %** → **`NOT A RESULT`**, and the arm reports *which* of mesh
asymmetry / rotation convention / moment sign / convergence it was, before any derivative is
quoted. X4: the β = +8 control disagrees with α = +8 by > 0.5 % → same.

**GEOMETRY.** X5: built `A/A_x` departs from Roddy Table 2 by > 0.5 % at any of the 25
stations → the mesh is rejected **before** it is solved.

**HYPOTHESIS.** X6: `Z_w'` outside `[−0.006186, −0.005710]` → **`GATE FAIL` on D1**.
X7: `M_w'` outside `[+0.012283, +0.013307]` → **`GATE FAIL` on D2**. **A `GATE FAIL` here is
a real and publishable outcome** — it would say our RANS setup does not reproduce a measured
submarine stability derivative, which is worth more than a `PASS` obtained by widening a band.

---

## 9. WHAT A1d DOES NOT CLAIM

- It does **not** validate the **hull+sail** configuration. A1d's `PASS` would license the
  *method*, not A1c's geometry; A1c's rows stay lab-constructed brackets regardless.
- It does **not** resolve the **α = 0 surface-pressure anchor**, which remains `PENDING` for
  both arms: the Cp values live in data files not on this box (A1c §3.1).
- It does **not** claim Reynolds parity. **Roddy's static sweeps ran at 6.5 knots,
  `Re_L ≈ 14 million`; ours is `1.2e7`.** Roddy states coefficients vary with Re *"up to a
  Reynolds number … of about 10 to 15 million"* — **our 12 million is inside that band, not
  above it**, so the mismatch is not negligible by his own criterion. **Disclosed,
  un-quantified, and it applies to D1/D2/D3 as a systematic on top of the 4 % band.**
- It does **not** grade a grid triple. A1d as written is a **single-level** arm; no GCI is
  quotable and none will be emitted (rule 5).
- It does **not** freeze itself, launch anything, or send anything outside this box (rule 7).

---

## 10. FREEZE BLOCK — cfd-SUPERVISOR, CHECK 4, UNDELEGATED

**INTENTIONALLY BLANK.**

```
Frozen at commit:      ____________________
Date/time (UTC):       ____________________
Pre-compute condition: verification/runs/navier_class/SUBOFF_A1d/ does not exist;
                       no A1d mesh exists; no queue entry references A1d. Checked by: ______
Signed:                ____________________
```

---

# §11. ADDENDUM 1 — 2026-09-12 — **GATE X5 BUILT AND RUN, AND IT PASSES; PLUS A FALSE FAILURE THAT LOOKED EXACTLY LIKE A REAL DEFECT**

**Pre-compute, and the condition is unchanged and re-checked:** no A1d run directory, no
A1d mesh, no queue entry. **Nothing here moves a gate, a threshold, a cap or a label.**

## 11.1 THE INSTRUMENT

`cases/navier_class/SUBOFF_A1d/check_barehull_geometry.py` implements §8's **X5**: the
built geometry must reproduce Roddy Table 2's 25 stations to **0.5 %**, and the mesh is
**rejected before it is solved** if it does not.

Roddy Table 2 is transcribed into the script from the **rendered page at 150 dpi**, never
from the OCR text layer — which in this very report was already caught **silently dropping
an entire table row** (Table 3, Configuration 3's static-stability line; A1d §2).

**Three controls, because a checker that has not been shown able to fail is not evidence
that it passed (rule 3):**
1. **Transcription self-proof.** For a body of revolution `A/A_max ≡ (B/B_max)²`. All 25
   rows satisfy it to the tabulated 5 dp. This validates the visual transcription, confirms
   the tabulated body **is** a body of revolution — which is the identity A1d's entire
   plane-equivalence argument rests on — and would catch a transposed digit. It needs no
   external input at all.
2. **Planted control.** `--selftest` injects a **+5 % perturbation at station 10.0** and
   **refuses (exit 2) if the checker fails to see it.**
3. **Derived axis.** The station unit is taken from the geometry module and refused if it
   is not 0.70 ft — §11.3.

## 11.2 THE RESULT — **GATE X5 PASS**

```
[ok] transcription self-consistent: A/Amax == (B/Bmax)^2 at all 25 stations
[ok] station axis DERIVED from geometry: 0.6999989 ft/station
[ok] planted control fired: +5% at station 10.0 was caught
GATE X5 PASS — all 25 stations within 0.50 %.       worst deviation 0.081 %
```

> **The lab's analytic hull reproduces Roddy 1990's independently published offsets to
> better than 0.1 % at every one of 25 stations.** Two separately retrieved, separately
> title-page-verified sources — Groves 1989's analytic definition as implemented in
> `build_suboff_a1_geometry.py :: hull_R_ft`, and Roddy 1990 Table 2 — **agree.** That is
> the two-source corroboration §6 required, and it is **passed before any mesh exists.**
> Corroborating detail: the module's `L_AFT_PERP = 13.979167 ft` matches Roddy's stated
> nondimensionalising length of **13.9792 ft**.

## 11.3 🔴 THE FALSE FAILURE, RECORDED BECAUSE IT WAS CONVINCING

**The first run of this gate FAILED, and the failure was wrong — it was mine, not the
geometry's.**

Roddy p. 3 states forces are *"nondimensionalized using the length between perpendiculars
of 13.9792 feet"*. This lane reused that length for the **station axis** (`LBP/20 = 0.69896
ft/station`). The gate then reported **8 of 25 stations failing**, with the error growing
monotonically toward the tail — 0.69 %, 1.43 %, 2.64 %, 4.31 %, 9.99 %, **65.09 %** — and a
**non-zero radius at the closing station** where Roddy has 0.00000.

**That signature reads unmistakably as a truncated stern.** Worse, it is *plausible*: A1b
§2.2 records that this geometry family really does have a truncated base (`L0c` fails Gate
M-b-1 at 6 cells across it). **A defect this lab already has, in the place the signature
pointed to.** It would have been filed as a confirmed geometry finding by anyone who did
not check the axis.

**It was an artifact of the wrong station unit and nothing else.** The station axis runs
0 – 20.4167 over the **overall** length, not the LBP: `14.291667 / 20.4167 = 0.6999989`,
i.e. **0.70 ft exactly**. At the correct unit the same geometry and the same table agree to
0.081 %.

> **The general form, and it is not specific to SUBOFF: a reference length stated for one
> purpose is not the axis for another.** Roddy's LBP is the **force** normalisation; the
> **station** axis is the overall length. Reusing the first for the second produced a
> failure that was large, monotonic, physically interpretable and consistent with a known
> defect — **every property that makes a wrong result get believed.**
>
> **What kept it honest was the order of the controls.** The planted control had already
> fired, so the checker was known able to see a real error; that is exactly what made the
> FAIL worth *investigating* rather than either dismissing or filing. A checker trusted
> without a plant would have made this finding unfalsifiable in both directions.

The script now **derives** the station unit from the geometry module and **refuses** if it
is not 0.70 ft, so a future geometry edit cannot silently move the axis this table is read
against. The trap is recorded as **L-564**.

## 11.4 WHAT REMAINS BEFORE THE FREEZE BLOCK CAN BE SIGNED

Per `MESH_STANDARD` §8.1 and the cfd-supervisor's ruling — **build first, freeze after** —
§10 stays blank until the 3-D half-model mesh exists and is presented with its gates.

**The mesh has NOT been built, and launching it now is forbidden — not by preference but by
Sanaa's own hygiene rules, measured on the box rather than relayed:**
**load average 17.91 against `nproc` 16.** Her run instruction item 18: *"Load above core
count is a defect… stops new launches until cleared"*; item 8's core guard: *"solver ranks
plus fleet processes never exceed 16"*; item 19: *"The runner is the only thing that
launches. Nothing launched by hand counts as a case."* RAM is not the constraint —
110 GiB of 123 GiB available. **The build is prepared and queued behind the ceiling, which
costs nothing, since the mesh must exist before the freeze can be signed anyway.**

---

# §12. ADDENDUM 2 — 2026-09-12 — **THE BUILD IS PREPARED AND HELD. IT IS NOT PLACED, AND THE REASON IS SANAA'S RULE, NOT A PREFERENCE.**

**Still pre-compute.** `verification/runs/navier_class/SUBOFF_A1d/` does not exist, no mesh
exists, and the queue entry sits in `held/`, which the daemon does not poll.

## 12.1 WHAT WAS BUILT (INSTRUMENTS, NOT MESHES)

| Artifact | What it is |
|---|---|
| `cases/navier_class/SUBOFF_A1d/check_barehull_geometry.py` | GATE X5. §11. |
| `cases/navier_class/SUBOFF_A1d/build_barehull_case.py` | Emits the bare-hull case — hull STL, `blockMeshDict`, `snappyHexMeshDict`, manifest. **Runs nothing.** |
| `cases/navier_class/SUBOFF_A1d/build_barehull.sh` | What the runner launches: X5 → emit → `blockMesh` → `snappyHexMesh` → `checkMesh`, rc captured **inside** the wrapper. |
| `verification/queue/cfd/held/SUBOFF-A1D-MESH-BUILD.DRAFT.json` | The queue entry. **HELD.** |

**The geometry function is REUSED, NOT COPIED.** `build_barehull_case.py` imports
`build_suboff_a1_geometry.build_hull_stl` and calls it directly. **That is the exact
function GATE X5 validated to 0.081 %.** A copied-and-edited hull function would be a
*different* function and X5's PASS would not apply to what was actually built — rule 14's
shape: a lesson is not applied until the call site asserts it.

**Emitter verified by running it** (file writes only, no meshing): 214,560 hull triangles,
closed nose and tail (both **refused** if not), background block 140 × 76 × 38 = 404,320
cells, and the four block patches `inlet outlet farfield symm` — `hull` arrives from
snappy, giving the required five.

**X5 runs FIRST in the wrapper, before any geometry or mesh is built**, with `--selftest`
so the planted control is armed before the real comparison. **A geometry gate that can only
be evaluated after a build is a gate evaluated under pressure to pass.**

**Post-build refusals, so the wrong geometry cannot pass quietly:** a `sail` patch → refuse;
patch count ≠ 5 → refuse; any step without an `End` line → refuse; `id -u` = 0 → refuse
(item 6, and a peer team had a root launcher `rm -rf` a run tree earlier today). `checkMesh`
failing its checks is written to `STATUS.build` as `CHECKMESH=FAILED_CHECKS` — **a finding,
never a silent pass.**

## 12.2 🔴 WHY IT IS NOT PLACED

**Measured on the box, not relayed: load average 18.92 against `nproc` 16 at 20:10Z — and
17.91 at 20:05Z, so it is RISING, not clearing.**

- Item 18: *"Load above core count is a defect… stops new launches until cleared."*
- Item 8, core guard: *"solver ranks plus fleet processes never exceed 16."*
- Item 19: *"The runner is the only thing that launches. Nothing launched by hand counts as
  a case."*

**RAM is not the constraint and does not override this** — 110 of 123 GiB available. The
constraint is cores. The entry is declared at **1 rank, serial `snappyHexMesh`**, the
smallest footprint available, and **it still waits.**

## 12.3 WHAT THIS ENTRY IS NOT

It carries **no frozen pre-registration commit, deliberately.** `MESH_STANDARD` §8.1 forbids
a freeze before the graded mesh exists, so the order is **build first, freeze after**. This
entry **builds the mesh the freeze will be written against**. It grades nothing, produces no
verdict, writes no field, and **licenses no solve**. The A1d *solve* entries do not exist and
**cannot be placed until §10 is signed.**

**Building a mesh is not admitting it.** Mesh admission and §10 are the cfd-supervisor's
check 4, personally and undelegated.
