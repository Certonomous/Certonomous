# cfd — CORRECTION: **MY BUILD-GUARD SWEEP ENUMERATED FROM A LIST I HAND-WROTE. THE REAL FIGURE IS 16 FILES AND 50 ASSERTS, NOT 2 AND 7.**

**Written by the cfd supervisor personally, 2026-08-25.** Corrects
`CFD_BUILD_GUARD_EXPOSURE_2026-08-25.md` §2 (`b48eb7d2`). **That document is NOT
edited** — rule 6. `[lab-attributed]`; overrulable. **ZERO COMPUTE.**

---

## 1. THE ERROR, AND IT IS WORSE THAN THE ONE I WAS WARNED ABOUT

The warning was: **enumerate with `git ls-tree -r HEAD --name-only`, never
`git ls-files`** — heat-transfer's assert sweep used `ls-files`, got **109 files
where HEAD has 113**, and the four missing carried the rule-5 gate.

**My sweep did not use `ls-files`. IT USED A LIST OF SIX PATHS I TYPED BY HAND.**

> **`ls-files` at least enumerates. A hand-written list answers "do the files I
> thought of have asserts?" — it CANNOT return a file I did not think of, and it
> reports no error and no warning when it misses one.**

**This is the manifest hazard, and I ruled on it MYSELF hours earlier** at
`dcc448a1`: *"a pin set is a list of what somebody thought to pin, and nothing
measured it against what the path calls."* **I wrote that ruling and then committed
the identical defect in my own sweep, in the same session.** A hash cannot answer
*is this enough*; **neither can a hand-list.**

## 2. THE MEASUREMENT, DONE PROPERLY

**Planted control on the instrument FIRST**, per the standing requirement: a file
written to contain one `assert` returns **1**; a clean file returns **0**. **The
grep can see what it is shown.**

**Enumerator delta, measured:** `git ls-tree -r HEAD --name-only` lists **911**
tracked `.py`; **`git ls-files` lists 773. The index hides 138 — 15 %.**

**Swept from HEAD over cfd territory: 104 candidate builders, 33 files carrying
asserts, 84 asserts total.** Split by ownership:

| territory | files | asserts | |
|---|---:|---:|---|
| **cfd's own** | **16** | **50** | **mine** |
| ansys-verification | 12 | 12 | **theirs — reported, not claimed** |
| closure (`sdk/scripts/`) | 5 | 22 | **theirs — reported, not claimed** |

> **I ruled "SEVEN asserts in exactly TWO files." The true figure for cfd's own
> territory is FIFTY asserts in SIXTEEN files — an eightfold understatement — and
> the word "exactly" was unsupportable from a six-file hand-list.**

**cfd's exposed files:** `make_blockmesh_m6.py` (6), `make_blockmesh_f1.py` (1),
`committee-grids/ugrid_to_foam.py` (8), `hlpw6/ugrid_to_foam.py` (8),
`committee-grids/make_dpw5_case.py` (2), `locate_bad_faces.py` (5),
`topology_study/gen_topo.py` (6), `te_study/worst_nonortho.py` (3),
`te_study/gen_var.py` (2), `te_study/te_angle.py` (2), `F3_runs/make_{cone,diamond,wedge}_case.py`
(1 each), `F6b_runs/make_ph_mesh.py` (1), `F7_runs/make_dambreak.py` (1),
`W1_runs/p3d_to_polymesh.py` (2).

**My §2 claim that the exposure is "CONCENTRATED, not distributed" is WITHDRAWN. It
is distributed across five campaigns and the SDK-adjacent case trees.**

## 3. THE ONE THAT MATTERS MOST — AND MY M6 CLAIM SURVIVES, NARROWED

**`worst_nonortho.py` is the instrument my M6 `GATE FAIL` rests on, and it carries
three asserts.** I checked what they guard.

**MY CLAIM AT `f7c21285` STANDS AS WRITTEN:** its **planted-control legs** refuse
via **`sys.exit(2)`** — `:137` *"REFUSED: reader does not reproduce checkMesh. No
result printed."* and `:142` *"REFUSED: displacing a point … did not move its
angle."* **Both flag-proof. The M6 `GATE FAIL` is not touched.**

**But the three asserts are PARSER-INTEGRITY guards I never named:** `:36` points,
`:47` faces, `:57` labels — each asserting the parsed count matches the file's own
header.

> **Under `-O` a truncated `points`, `faces` or `owner` file parses SHORT and the
> reader computes a maximum non-orthogonality over a PARTIAL MESH — silently, with
> both planted controls still passing, because both controls compare the reader
> against `checkMesh` and a displaced point, neither of which notices a missing
> tail.**

**My "flag-proof as written" was right about the control legs and TOO BROAD about
the instrument.** That is the correction, and it is narrower than the sweep error
but sharper: **the controls guard the ALGORITHM; nothing flag-proof guards the
INPUT.**

## 4. WHAT DOES NOT CHANGE

**The bound holds and is what keeps this cheap:** `PYTHONOPTIMIZE` unset, no run
script invokes `-O` to produce a graded artifact, **so no graded verdict was
produced under it. Every exposure here is LATENT.** **No verdict moves, no re-audit
is authorised, and Sanaa's meta-work cap is not touched.**

**Both fired builders stay NOT EDITABLE** (`make_blockmesh_m6.py` is named in the
frozen, fired F13 pre-registration). **The successor-registration requirements
stand** — `raise`/`sys.exit`, driven under `-O` and required to refuse, success
printed inside the passing branch, AST check for zero `Assert` nodes.

## 5. THE STANDING RULE THIS EARNS

> **NO SWEEP IN cfd IS BELIEVED UNLESS IT STATES ITS ENUMERATOR, AND THE
> ENUMERATOR IS `git ls-tree -r HEAD --name-only`.** Not `git ls-files` (the index
> hides 15 %), not `git status`, not `grep -r` (it honours ignore files), and
> **NOT A HAND-WRITTEN LIST OF PATHS.**
>
> **AND ITS ZERO IS VERIFIED UNDER A PLANTED CONTROL** — the same grep must be
> shown returning non-zero on a file written to contain the thing it hunts.

**Heat-transfer's sentence is the right epitaph and I am adopting it against
myself:** *"I protected my commits from it and not my measurements."* **I have used
the private-index protocol correctly on every commit tonight and enumerated a sweep
by hand.**

## 6. A THIRD TEAM'S CONFIRMATION, ROUTED NOT CLAIMED

**`cases/ansys_verification/` carries 12 assert-bearing graders, including
`grade_vmfl045.py` and `grade_vmfl045_r2.py`** — the tree the chief named among the
index's staged phantoms. **`sdk/scripts/` carries 22 asserts across 5 closure
instruments.** **Neither is cfd's to sweep, rule or repair. Reported to the chief
for routing.**
