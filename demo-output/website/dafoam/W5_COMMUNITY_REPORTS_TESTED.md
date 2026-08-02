# W5 — the two community reports, opened rather than cited

**2026-08-02, zero solver compute against a filed estimate of 20 measured
core-minutes.** Serves docket item
`w5-test-community-reports-against-mechanism`, *"Run DAFoam discussions 905 and
914 against the degenerate-branch mechanism instead of guessing."*

The item's premise is that these are **"two open, undiagnosed community
reports"** and that each is **"one `useRotations=False` run away from an
answer"** (`ROOTCAUSE_getRotationMatrix3d.md` §2.5, §5.2).

**Both premises are false, and the first thing this item needed was to read the
threads.** Neither is open. Both were resolved upstream, one of them with a
diagnosis in the thread that this lab's record does not mention.

---

## 1. `mdolab/dafoam` discussion #905 — REPRODUCED, and the cause is the FD step

### 1.1 What the thread actually says

* Case: the **NACA0012-incompressible tutorial**, meshed by `naca0012_rans.py`
  (a finer mesh than earlier versions).
* Steps used when the errors were reported: **1e-5 to 1e-7**.
* Reported: `CD` wrt `patchV` analytic 2.314747e-02 against FD 4.256817e-02;
  `CL` wrt `shape` analytic 1.617682e+01 against FD 1.432387e+02, relative error
  **1.061604e+00**.
* **Maintainer `friedenhe`: *"You should not use such a small step in
  finite-difference. Try to use 1e-3 or 1e-4."***
* The reporter re-ran at step **1e-3** and reported `CD` wrt `patchV` at
  **5.559751e-03**, with the `naca0012_rans.py` mesh *"improved significantly"*.
* **Status: resolved.**

Our §2.5 records it as *"opened 2025-11-05, unresolved"*.

### 1.2 Reproduced on this lab's own NACA0012, at zero additional compute

`ladder-a/A_stepsize_study.json` (2026-07-28) swept the central-difference step
on **the same tutorial**, `dCD/dshape`, 4,032 cells, np=2:

| step | rel. err | regime, as recorded then |
| --- | --- | --- |
| 1e-8 | **94.951%** | roundoff-dominated |
| 1e-7 | **52.879%** | roundoff-dominated |
| 1e-6 | **17.640%** | roundoff-dominated |
| 1e-5 | 12.270% | transition |
| 1e-4 | 11.520% | well-converged plateau |
| **1e-3** | **11.427%** | well-converged plateau |

**#905 reported 40–126% at steps of 1e-5 to 1e-7. This lab's own NACA0012 reads
52.9% at 1e-7 and 95.0% at 1e-8, inside that band, and collapses to 11.4% at
1e-3 — which is precisely the step the maintainer prescribed and precisely the
recovery the reporter measured.** The report is reproduced, and what it
reproduces is a finite-difference step below the case's roundoff floor.

### 1.3 The reading in §2.5 that does not survive

> *"the error tracks which mesh generator produced the grid rather than the
> flow. Mesh-dependence with flow-independence points at the warp."*

The thread shows the **coarser** `genAirFoilMesh.py` grid clean at step 1e-3 and
the **finer** `naca0012_rans.py` grid needing the larger step. A roundoff-limited
FD floor scales with the perturbation relative to the cell size, so a finer grid
fails at a step a coarser grid tolerates. **That is step-versus-mesh-scale, not a
generator-dependent warp defect**, and it is the same ordering this lab's own
sweep shows across steps at fixed mesh.

### 1.4 What is NOT determinable from the report

The reporter's post-fix number, 5.559751e-03, is on **`CD` wrt `patchV`** — a
freestream-velocity design variable that **never enters `warpDeriv`**. This
lab's own A1 table shows `patchV` rows reading 0.2317% identically with and
without the patch, i.e. that chain is blind to the mechanism by construction.
**The thread never reports a shape derivative at a plateau step**, so whether a
residual shape-derivative defect remains in #905 after the step is fixed
**cannot be decided from the information given**. It is recorded as such.

### 1.5 The error under both `useRotations` settings

Measured on the equivalent case — the same tutorial, this lab's A1
(`W5_GRADIENT_REGRADE.md` §1, np=2, 2026-08-01):

| derivative | stock (rotation branch live) | patched (branch corrected) |
| --- | --- | --- |
| **CD wrt shape** | **11.43%** | **0.03745%** |
| CL wrt shape | 1.671% | 0.01494% |
| CD wrt `patchV` | 0.2317% | 0.2317% |
| CL wrt `patchV` | 0.2316% | 0.2316% |

So on the tutorial #905 used, the mechanism is worth 305× in absolute error on
the shape chain and exactly nothing on the `patchV` chain — the only chain #905
gives a clean post-fix number for.

## 2. `mdolab/dafoam` discussion #914 — NOT REPRODUCIBLE FROM THE INFORMATION GIVEN

### 2.1 What the thread actually says

* 3D steady drag reduction, **DASimpleFoam v4.0.2**, one objective plus
  thickness and volume constraints.
* Thickness constraint absolute error 6.836431e-12 (relative 1.27e-12); volume
  constraint 4.332919e-12 (relative 4.07e-12); **drag objective absolute error
  5.929533e-01, relative 1.27e-02**.
* Primal and adjoint both converged, 301 GMRES iterations.
* **Maintainer `friedenhe`: *"the gradient accuracy is very acceptable for
  practical aerodynamic optimization."*** **Status: resolved.**

Our §2.5 calls the split *"diagnostic"*.

### 2.2 Why the split cannot discriminate

Our reading was that the constraints are *"pure surface functions that never
traverse IDWarp"* while drag is *"the only quantity crossing `warpDeriv`"*.
Both halves are true and the inference still does not follow, because
**A1's own table shows the identical split in BOTH settings**:

| | stock | patched |
| --- | --- | --- |
| `volcon` wrt shape | 4.367e-12 % | 4.367e-12 % |
| `thickcon` wrt shape | 1.265e-11 % | 1.265e-11 % |
| CD wrt shape | 11.43% | **0.03745%** |

A 12-orders-of-magnitude gap between the geometric constraints and the flow
objective is present when the defect is live **and when it is removed**. The
constraints are analytic functions of the FFD that never enter the PDE at all,
so the split separates *adjoint-computed* from *not adjoint-computed* — a far
coarser distinction than *crosses `warpDeriv`*. **Its presence in #914 is
evidence of nothing.**

### 2.3 And the magnitude cannot be read either way

It is tempting to argue that 1.27e-2 is too small to be this defect. **This
lab has already refuted that inference on its own data** (`W5_GRADIENT_REGRADE.md`
§3): A1's `CL wrt shape` read **1.671%** stock — a comfortable-looking aggregate
— and **0.01494%** patched, so that 1.671% was ~99% rotation defect. An aggregate
in the 1–2% band is compatible with the mechanism being fully present. **1.27e-2
is therefore compatible with the defect and compatible with its absence, and
distinguishes neither.**

### 2.4 What would decide it, and why it cannot be run here

The discriminator is the reporter's own case under `useRotations=False`. The
case is a private 3D drag-reduction geometry; **no mesh, FFD or `runScript.py`
is attached to the thread**, and it runs a different major version
(**v4.0.2**, against the **2.6.2** this lab's root-cause analysis is pinned to).
**#914 is explicitly recorded as not reproducible from the information given.**
The unblock is the reporter's case files, not machine time here.

## 3. What this does to the record

* `ROOTCAUSE_getRotationMatrix3d.md` §2.5 and §5.2 are corrected: neither report
  is open, #905 is diagnosed **in its own thread** as an FD step artefact and is
  reproduced as one here, and #914's split is not diagnostic.
* **The scope claim is not widened and it is not narrowed.** The item's stated
  win condition was *"two independent confirmations this lab did not construct
  itself"*. There are none. The item's stated failure condition was *"a second
  mechanism, and our scope claim is too broad"*. There is no evidence of that
  either. **The correct outcome is that these two reports were never evidence in
  either direction, and citing them as *suggestive* was reading a conclusion out
  of a thread nobody had opened.**
* The lab's own A1 step sweep, filed 2026-07-28 for an unrelated purpose, turns
  out to be a complete reproduction of #905. It was on disk the whole time.

## 4. Cost

**Zero core-minutes** against a filed estimate of 20 measured. Two web reads and
two files already in the tree (`ladder-a/A_stepsize_study.json`,
`W5_GRADIENT_REGRADE.md` §1). The 20 core-minutes are not spent, and the reason
they are not spent is that the runs they would have paid for could not have
answered either question.
