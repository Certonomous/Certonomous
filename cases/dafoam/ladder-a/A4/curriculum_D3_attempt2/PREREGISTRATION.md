# Curriculum item D3 — A4 Ahmed body, CONSTRAINED drag minimisation: PRE-REGISTRATION, **ATTEMPT 2**

**Frozen 2026-08-24T18:17:55Z** (`date -u`, read in the shell invocation that wrote this file; the
commit invocation re-reads it and asserts this stamp present in the committed blob — §15).
**Author:** dafoam `lab-lane` (Opus), dispatched by dafoam-supervisor. **PHASE 1 ONLY.**

**NO SOLVER COMPUTE HAS BEEN SPENT ON THIS ATTEMPT, and the run root
`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/` does not exist** — its absence is
asserted inside the commit invocation that freezes this file (§15). **One pre-freeze diagnostic
container WAS run, under an explicit ≤ 0.5 core-min permission, and it is declared here in full
(§2.2): 0.1833 core-min measured, no flow solve, in its own probe root.** Declaring it is the point:
a pre-registration that hid a pre-freeze reading would be worthless.

**This is a NEW mini-item, not an edit.** Attempt 1
(`cases/dafoam/ladder-a/A4/curriculum_D3/`, frozen at `0cbf463c` with authorisation addendum A1) is
**not edited, not moved and not re-graded here**, and its run root
`/home/ubuntu/certonomous-runs/D3-a4-constrained/` is **preserved evidence, read-only to this lane**.
That is attempt 1's own §4.3 repair policy, in the D1-C′ pattern, applied to itself.

**Curriculum authority:** `cases/dafoam/EXPERTISE_CURRICULUM.md` §3, Tier 1, row **D3** —
*"Ahmed drag min + volume/rear-slant constraints (A4 case) | 3D constraints on separation-dominated
flow | A4 PASS — met | ~70 core-min, $0.06 | as D1; separation-onset monitor registered | wake
bistability making the objective noisy (η measured first, per N-D15's δ_repeat discipline)"*.
Ratified under `EXPERTISE_CURRICULUM.md` §7 (Sanaa 2026-08-23) on the conservative reading quoted in
attempt 1 §0 — **starting execution**, each item under its own frozen costed pre-registration,
pre-authorised class only, and *"anything unusual, above pre-authorised cost, or outside these pages
goes back to Sanaa costed, not read into the blanket."* §14 applies that test again, item by item,
including to this attempt's own diagnostic probe.

**Nothing is filed, sent, uploaded, posted or pushed anywhere** (`CLAUDE.md` rule 7). SUBMISSIONS
PARKED.

---

## 0. What this attempt is, in four lines

1. Attempt 1's Stage G — the zero-flow geometry probe — **did its registered job and returned a
   defect in the frozen producer**: the script never registers a surface with `DVConstraints`, so the
   first constraint call raised `KeyError` and the item ended `BLOCKED` at **0.300 core-min**.
2. This attempt re-registers the same item with **one repair, two executable lines**, and everything
   else — gates, bands, ceilings, comparator, monitor — carried unchanged.
3. The repair's mechanism is **established from the installed pyGeo source by file and line** (§2.1)
   and **proved to clear the crash by a costed pre-freeze probe** (§2.2). What the probe does **not**
   prove is registered as loudly as what it does (§2.3).
4. Its claim is still about **constrained optimisation and gradients**, never about Ahmed-body
   aerodynamics; the separation content the curriculum row names is **absent on this mesh** and the
   item does not claim it (§9).

---

## 1. What attempt 1 established, and what carries forward

### 1.1 The finding, and the correction to F1's registered interpretation

`/home/ubuntu/certonomous-runs/D3-a4-constrained/geom.log:472-491` — the staged frozen producer died
inside `Top.configure()`, reached from module-level `prob.setup(mode="rev")`:

```
File "/mnt/geom/runScript.py", line 195, in <module>      prob.setup(mode="rev")
File "/mnt/geom/runScript.py", line 154, in configure     self.geometry.nom_addThicknessConstraints2D(
File ".../pygeo/mphys/mphys_dvgeo.py", line 429           self.DVCon.addThicknessConstraints2D(
File ".../pygeo/constraints/DVCon.py", line 593           coords = self._generateIntersections(...)
File ".../pygeo/constraints/DVCon.py", line 3233          p0, p1, p2 = self._getSurfaceVertices(...)
File ".../pygeo/constraints/DVCon.py", line 3219          raise KeyError('Need to add surface "' ...)
KeyError: 'Need to add surface "default" to the DVConstraints object'
```

Attempt 1 §15.1 registered **F1** as *"Stage G crashes in any DVCon call ⇒ the JBC_Hull/D1-C′ API
precedent does not transfer to a 3×2×2 FFD on a blunt body."* **The event fired; that interpretation
is wrong**, and attempt 1's `RESULTS.md` §3.4 says so on the record: nothing about a 3×2×2 FFD or a
blunt body was ever reached, because the call never got as far as any geometry. **This attempt
therefore splits F1 into three classes with a decision rule (§17), so the same event can never again
be read as the wrong finding.**

### 1.2 The supervisor's four rulings, carried forward verbatim in substance

From attempt 1 `PREREGISTRATION.md` §18.1 (addendum A1, dated 2026-08-24T17:53:21Z). They are
rulings about the **item**, not about attempt 1's file, and they bind this attempt unchanged:

1. **The DV extension 1 → 2 is AUTHORISED** — the curriculum row specifies *"volume/rear-slant
   constraints"*, and a rear-slant constraint is **inexpressible with a single design variable**;
   the extension is inside these pages and does not go to Sanaa under §7 clause 2.
2. **The shipped row bought as endpoint-only is ACCEPTED** — Stage T buys the endpoint gradient on
   both images at the same design vector reached by the same path; the **full shipped optimisation
   twin is DEFERRED**, priced at **≈ 17 core-min ≈ $0.0145 DERIVED**.
3. **The item PROCEEDS with the separation content honestly absent** — the supervisor independently
   counted reverse-flow cells on every 2,777-cell A4 field on disk: **zero everywhere**, min U_x
   ≈ **+23.5 m/s** against U₀ = 40, against **528** reverse cells on a 79,439-cell Ahmed-25 field and
   **780** on the cfd team's 9,050-cell F5c field. **P11 is expected to HIT.**
4. **`NOT AN INSTRUMENT` is a printed REASON, never a verdict** — in `RESULTS.md` the **Gs cell reads
   `NOT A RESULT`** with `NOT AN INSTRUMENT` and the failed instrument conditions printed beside it.
   `d3_sep_monitor.py` is not edited; the mapping happens in the record.

### 1.3 What attempt 1 measured, and what it did not buy

| | attempt 1 |
|---|---|
| spend | **0.300 core-min MEASURED** (18 wall s × 1 rank ÷ 60, `<attempt-1 root>/ledger.txt`), plus a **bounded ≤ 0.30** read-only triage container disclosed in its `RESULTS.md` §6.1/§7.2 |
| gates decided | **G5 PASS** (12 controls, exit 0), **G6 PASS**, **G7 PASS** (`IDWARP_SO_MD5 85f59e87…` from inside the loading process), **G8 PASS**, **G9 PASS** (peak 0.607 GiB, rc 1 not 137), **G10 PASS** |
| gates `PENDING` | Gη, G1, G2, G3, G4, Gs, Gθ — the stages never launched |
| predictions | **P1 MISS**; P2–P13 **NOT TESTED**; **P14 HIT trivially and uninformatively** (0.30 of ≤ 51.6) |
| item verdict | **`BLOCKED`** |

**None of those `PENDING`/`NOT TESTED` rows is inherited as evidence here.** They are re-registered
below and must be bought again.

---

## 2. The diagnosis — established from the installed source, then probed

### 2.1 Two hypotheses were put; the second held, and the first is refuted by the traceback itself

**Hypothesis A (put by the supervisor, to be tested not assumed):** *Stage G runs with no flow setup,
so `DVConstraints.setSurface` is never reached — the defect is in the PROBE's design, which does not
reproduce the setup path Stage O would take.*

**REFUTED, from attempt 1's own artifacts.** The raise happens inside `Top.configure()`, called from
**module-level `prob.setup(mode="rev")`** at staged `runScript.py:195` — code that executes on
**every** `-task`, before the first `if args.task ==` branch. Attempt 1's Stage G **did** reproduce
Stage O's setup path exactly; **Stage O would have died at the same line, after paying for a cold
primal it never got to run.** The probe design was not the defect — the probe was the instrument that
found it, at 1 % of the item's budget.

**Hypothesis B (the alternative):** *the script lacks the surface set-up that A1's working script
has.* **CONFIRMED**, from the installed image `dafoam-idwarp-rot:v1`, read read-only:

| file:line (inside the image) | what it establishes |
|---|---|
| `pygeo/mphys/mphys_dvgeo.py:417-425` | `nom_addThicknessConstraints2D(..., surfaceName="default", ...)` — the **consumer defaults to the name `"default"`** |
| `pygeo/mphys/mphys_dvgeo.py:429-436` | forwards `surfaceName=surfaceName` into `DVCon.addThicknessConstraints2D` |
| `pygeo/mphys/mphys_dvgeo.py:446` | `nom_addVolumeConstraint(..., surfaceName="default")` — the same default on the volume constraint |
| `pygeo/constraints/DVCon.py:593` | `coords = self._generateIntersections(leList, teList, nSpan, nChord, surfaceName)` |
| `pygeo/constraints/DVCon.py:3233` | `p0, p1, p2 = self._getSurfaceVertices(surfaceName=surfaceName)` |
| `pygeo/constraints/DVCon.py:3217-3219` | `if surfaceName not in self.surfaces.keys(): raise KeyError('Need to add surface "…"')` — **the raise** |
| `pygeo/constraints/DVCon.py:86, 129-132` | `def setSurface(self, surf, name="default", …)` … `self.surfaces[name] = []` — **the only writer of `self.surfaces`** |
| `pygeo/mphys/mphys_dvgeo.py:541-545` | `def nom_setConstraintSurface(...)` → `self.DVCon.setSurface(...)` — **the only mphys path that reaches it** |
| `pygeo/mphys/mphys_dvgeo.py:103-116` | `nom_add_discipline_coords` calls `nom_addPointSet` and `add_input/add_output` — **it never touches `self.DVCon`** |
| `dafoam/mphys/mphys_dafoam.py:655-659` | `mphys_get_triangulated_surface()` → `DASolver.getTriangulatedMeshSurface()` — the supplier of the surface |
| `dafoam/pyDAFoam.py:1049-1067` | `getTriangulatedMeshSurface(groupName=None)` defaults to `self.allWallsGroup`; returns `[p0, v1, v2]`, i.e. the **`point-vector`** format `setSurface` defaults to. On this case `allWalls = ['body']` (attempt 1 `geom.log`: `OrderedDict([('body', [0]), ('farfield', [1]), ('allSurfaces', [0, 1]), ('allWalls', [0]), ('designSurfaces', [0])])`) |

**And the lab's own working precedents do call it, ~40 lines before their constraint calls:**

| file | the two lines attempt 1 lacked |
|---|---|
| `A1/curriculum_D1_Cprime/d1c_runScript.py` (ran to **PASS**) | **:134** `tri_points = self.mesh.mphys_get_triangulated_surface()` · **:135** `self.geometry.nom_setConstraintSurface(tri_points)` |
| `/home/ubuntu/dafoam-tutorials/JBC_Hull/runScript.py` | **:106** · **:107**, same pair |
| `/home/ubuntu/dafoam-tutorials/NACA0012_Airfoil/incompressible/runScript.py` | **:134** · **:135**, same pair, before `nom_addThicknessConstraints2D` at **:154** |
| **attempt 1 `curriculum_D3/d3_runScript.py`** | **ABSENT** — `nom_add_discipline_coords` at **:137**, then straight to the constraint calls at **:154** and **:156** |

`A4/…/opt_runScript.py` (the file attempt 1 derived from) has **no constraints at all** — `:101`
`nom_add_discipline_coords`, `:110` the single shape DV, no `add_constraint` anywhere in 195 lines —
so **it never needed a surface**. The omission entered when the constraint calls were copied from
precedents cited **at the constraint lines only** (attempt 1 §1 cites `JBC_Hull:175,180,185` and
`d1c:152-156, 175-177`); **not one cited line was the prerequisite.** That is a *missing-prerequisite*
defect, not a *transferability* finding, and §17 now makes the two impossible to confuse.

### 2.2 The pre-freeze diagnostic probe — declared in full, with its cost

Authorised by the dispatching brief as *a geometry-only probe of ≤ 0.5 core-min in a container, for
diagnosis only, if costed and recorded in the pre-registration*. It is recorded here.

| item | value |
|---|---|
| what ran | `probe_setup.py` — attempt 1's `configure()` **plus the two candidate repair lines**, stopping immediately after `prob.setup(mode="rev")`. **No `-task` block, no `om.n2`, no flow solve, no optimiser.** |
| where | **its own probe root** `/home/ubuntu/certonomous-runs/D3-a4-attempt2-probe/`, on a fresh cold copy of `P3-a4-opt-shipped/base` — **never** in attempt 1's run root and **never** in this attempt's run root, which does not exist |
| image / caps | `dafoam-idwarp-rot:v1`, `--cpus=1 --memory=6g --memory-swap=6g --oom-score-adj=500`, `timeout 30` (= the 0.5 core-min permission expressed as a wall cap) |
| result | **rc = 0**, wall **11 s**, ranks 1 ⇒ **0.1833 core-min MEASURED**, of the 0.5 permitted. `$0.000157 DERIVED` at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED |
| artifacts | `<probe root>/probe.log`, `<probe root>/probe_ledger.txt`, `<probe root>/case/probe_setup.py` |
| what it printed | `PROBE_SETUP_COMPLETED: True` · `PROBE_EXCEPTION:` (empty) · `PROBE_DVCON_SURFACE_NAMES: ['default']` · `PROBE_END` |

**What it deliberately did NOT print, and therefore did not observe:** no constraint value, no
`thickcon_slant`, no `volcon_aft`, no FFD Jacobian, no symmetry residual, no CD, no field, no row
count. Those are the graded quantities and they remain **unobserved at this freeze**.

**What it does pre-observe, disclosed rather than buried:** that the two DVCon calls **return without
raising** on this case with the repair in place, and that `DVCon.surfaces` then holds the name
`"default"` the consumers default to. Attempt 1's **P1** bundled *"Stage G completes"* with *"values
finite and within 1e-6 of 1.0"*. **P1 is therefore split (§7): P1a is DISCLOSED AS PRE-OBSERVED and
is not graded as a prediction; P1b — the values — is unobserved and is graded.**

### 2.3 What the probe does NOT prove — registered as loudly as what it does

1. **The `KeyError` was the FIRST defect the interpreter met, not necessarily the only one.** The
   probe advances the failure frontier to the end of `prob.setup(mode="rev")` and no further. **The
   whole `geom_probe` task block (`d3_runScript.py:248` onward) is still unexercised** — `dvg.update("aero")`,
   the `z_at` selections at the two probe points, the symmetry loop, the JSON dump. A failure there is
   a **new defect** and is registered as falsifier class **F1c**, never as a repeat of F1.
2. **It proves nothing about any measured value.** A projection that returns *some* numbers is not a
   projection that returns *correct* numbers; P1b, P2 and P3 exist precisely to test that.
3. **It is not a Stage G.** Stage G runs the **frozen** producer, in the item's own run root, from a
   cold start, under G6/G7/G8, and writes `d3_summary.json`. The probe wrote none of that and grades
   nothing.

---

## 3. The exact diff from attempt 1's frozen files — every changed line, classified

`diff -u curriculum_D3/d3_runScript.py curriculum_D3_attempt2/d3_runScript.py` — **19 lines inserted,
0 lines deleted, 0 lines modified**, in three hunks:

| hunk | lines | what | class |
|---|---|---|---|
| `@@ -1,6 +1,10 @@` | **4 inserted** | module docstring: this is ATTEMPT 2, built from attempt 1's frozen producer (`md5 af2ce474e7954c03e3937161510f6590`, committed `0cbf463c`), which is **not edited and not moved** | **DOCUMENTATION** |
| `@@ -18,6 +22,12 @@` | **6 inserted** | docstring bullet **D3-6**, naming the repair and its source lines (`mphys_dvgeo.py:541-545` the only registrar; `:425`/`:446` the defaulting consumers; `DVCon.py:3217-3219` the raise; attempt 1 `geom.log:491`) | **DOCUMENTATION** |
| `@@ -136,6 +146,15 @@` | **9 inserted**: 1 blank + 6 comment + **2 executable** | in `configure()`, immediately after `nom_add_discipline_coords("aero", points)` and before `getLocalIndex(0)`:<br>`tri_points = self.mesh.mphys_get_triangulated_surface()`<br>`self.geometry.nom_setConstraintSurface(tri_points)` | **THE REPAIR** (2 lines) + **DOCUMENTATION** (7) |

**Executable change: exactly two statements.** Everything else in the 352-line producer — the flow
parameters and `daOptions` carried byte-identical from A4 `opt_runScript.py:32-83`, both shape-function
DVs, both constraint calls with their bounds, `LE_AFT`/`TE_AFT`, `N_SPAN`/`N_CHORD`, the θ probe
constants, `ETA_PLANT`, the IPOPT `opt_settings` including `max_iter 15`, all four `-task` blocks, the
`d3_summary.json` key set — is **unchanged, byte for byte**.

**The comparator and the monitor are carried BYTE-IDENTICAL and the repair does not touch them:**

| file | md5 | status |
|---|---|---|
| `d3_runScript.py` | **`4dd289f275b512598e74daf2eb39d729`** | **NEW** (attempt 1: `af2ce474e7954c03e3937161510f6590`) |
| `d3_grade.py` | **`a32f075853e264910ee0a6c2473fd948`** | **byte-identical to attempt 1 / `0cbf463c`** |
| `d3_sep_monitor.py` | **`cd07d7b8a70627579384f263ba92194e`** | **byte-identical to attempt 1 / `0cbf463c`** |

The commit invocation asserts that identity with **`cmp`** against **both** the attempt-1 working-tree
files **and** the `0cbf463c` committed blobs, and refuses on any difference (§15). All three pass
`python3 -m py_compile`. **Same honest limitation as attempt 1 §4.1:** `py_compile` checks syntax
only; `openmdao`, `dafoam`, `pygeo` and `idwarp` exist only inside the container. §2.2's probe closes
that gap **as far as `prob.setup`** and no further (§2.3).

**Producer/consumer key-set assertion re-run on the NEW producer** (L-273; zero compute):
`python3 d3_grade.py --keycheck d3_runScript.py` → `KEYCHECK producer keys (47)` /
`consumer keys (9)` / **`consumed-but-never-produced: NONE`** / **`KEYCHECK: OK`, exit 0**. The
producer's key set is unchanged by the repair, which is why the comparator can be carried unchanged.

---

## 4. The problem, unchanged from attempt 1 §2

Restated here so this file stands alone; **no number below differs from attempt 1's frozen values**.

**Design variables** — two shape-function DVs, each a symmetric pair of FFD control points moved
purely in z, in A4 `opt_runScript.py:109`'s own pattern:

| DV | FFD points | x of the i-plane | bounds |
|---|---|---|---|
| `shapeBreak` | `pts[1,0,1]`, `pts[1,1,1]` | 0.80 | [−0.05, +0.05] |
| `shapeRear` | `pts[2,0,1]`, `pts[2,1,1]` | 1.07 | [−0.05, +0.05] |

**Constraints** — `thickcon_slant` via `nom_addThicknessConstraints2D(..., nSpan=5, nChord=6)`,
bounds **[0.85, 1.15]**; `volcon_aft` via `nom_addVolumeConstraint(..., nSpan=5, nChord=6)`, bound
**≥ 0.98**; region frozen inside the body in all three coordinates:

```
LE_AFT = [[0.86, -0.17, 0.10], [0.86, 0.17, 0.10]]
TE_AFT = [[1.03, -0.17, 0.10], [1.03, 0.17, 0.10]]
```

**Symmetry** is by construction (both j control points of a pair always move together), and
`nom_addLinearConstraintsShape` stays **DECLINED BY NAME**; the decline carries a measurement, not an
assumption — Stage G reports `max |z(x,+y) − z(x,−y)|` against the registered **≤ 1e-9**.

**Rear-slant angle**, a graded **monitor** and not an optimiser constraint: break `(0.8428, 0.288)` →
rear-edge top `(1.044, 0.1942)`, θ = 25.00° by design;
`θ(d1,d2) = atan((0.0938 + 0.72287·d1 − 0.43863·d2)/0.2012)`; the comparator's control [12] returns
**24.9951°** at `d = (0,0)` and control [13] returns **15.990°** at A4's optimum. **Band [12.0°, 25.0°]**;
Stage G re-measures both coefficients and the comparator substitutes the measured pair when present;
**agreement threshold 2 %**.

---

## 5. Toolchain — two rows (`DAFOAM_CHARTER.md` §6)

| row | image | `libidwarp.so` md5 | stages | graded? |
|---|---|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1` | `85f59e87253e0a71a813f64ca6e4c425` | **G, η, O, T-patched** | **YES** |
| **SHIPPED** | `dafoam/opt-packages:latest` | `f0fcb488e0e98156575cd19548e91663` | **T-shipped only** | own row; not the graded row |

Unchanged from attempt 1 §3, including ruling 2's endpoint-only shipped row and the **≈ 17 core-min /
$0.0145 DERIVED** price of the deferred full shipped twin. **New corroboration available to this
attempt:** the patched row's hash was read **live** at run time from inside the loading process in
attempt 1 (`geom.log:4`, G7 **PASS**) — it is no longer inherited-only for that row. The **shipped**
row's hash remains inherited from the A4 record and is re-verified at Stage T-shipped by G7.

---

## 6. Stages, executables and repair policy

| stage | what runs | image | flow solves | `-task` |
|---|---|---|---|---|
| **G** | geometry probe: every DVGeo/DVCon call, the FFD z-Jacobian at both probe points, the symmetry measurement, the constraint values at baseline, `d3_summary.json` | patched | **none** | `geom_probe` |
| **η** | δ_repeat of CD at the baseline + the planted perturbation | patched | 3 primals | `eta` |
| **O** | the constrained optimisation + the in-process endpoint FD sweep at the optimum | patched | many | `run_driver` |
| **T** | endpoint gradient at Stage O's frozen design vector, cold, once per image | patched, then shipped | 2 × 5 primals | `endpoint_at` |

**Stage G runs first and is not flow, and this attempt is the proof that the pattern earns its
price**: it cost 1 % of the item's budget and returned a producer defect that would otherwise have
surfaced after a paid cold primal.

**§6.1 Frozen executables:** the three md5s of §3. The grading path is fixed at this commit; the
launch invocation re-hashes all three **on disk** against the **committed blobs at the freeze sha**
and refuses to stage on any mismatch (`CLAUDE.md` rule 2).

**§6.2 Design-vector handoff:** Stage T reads `{"shapeBreak": …, "shapeRear": …}` from a JSON written
by the launcher out of Stage O's `d3_summary.json`. Stage T's first assertion is that its own
`run_model` reproduces Stage O's `final_CD` to **≤ 1e-9 relative** on the patched arm; a wider gap
means the handoff did not deliver the design vector and Stage T is **`NOT A RESULT`**.

**§6.3 Repair policy — unchanged, and now applied to this file too.** If any stage crashes, that stage
is **`BLOCKED`**, the crash is a **finding** until triage says otherwise (`SUPERVISION_CHARTER.md`
§3), and **no frozen file is edited**. A repair is a `VERIFICATION_CHARTER.md` §2d.1 four-condition
decision **for the supervisor**, and any re-registered work is a **new mini-item** — an attempt 3
directory, never an edit of this one.

---

## 7. Predictions, with bands and the basis of each

**Bands are carried from attempt 1 unchanged except where the diagnosis changed a basis; every change
is named.**

| id | prediction | band / HIT rule | basis | changed? |
|---|---|---|---|---|
| **P1a** | the DVCon calls return without raising | — | **DISCLOSED AS PRE-OBSERVED by §2.2's probe. NOT GRADED as a prediction of this attempt** | **YES — split out of attempt 1's P1 and removed from grading** |
| **P1b** | every DVCon baseline value is finite and within **1e-6 of 1.0** | `thickcon_slant` (30 rows) and `volcon_aft` (1 row) non-empty, all finite, all within 1e-6 of 1.0 | pyGeo normalises both families to the baseline (JBC_Hull `:202-204`; D1-C′ `:175-177`) | band unchanged |
| **P2** | Stage G's measured FFD Jacobian agrees with §4's frozen coefficients | measured `(cB, cR)` within **2 %** of `(+0.72287, −0.43863)` | analytic trilinear FFD; the 24.9951°-vs-25.00° check | unchanged |
| **P3** | symmetry residual | `max|z(+y) − z(−y)| ≤ 1e-9` | symmetry by construction | unchanged |
| **P4** | δ_repeat at the baseline | **[0, 1.4e-05]**, point estimate ≈ 1e-06 | N-D15's 2.2104e-06 on A6 scaled to CD = 0.153; A4's baseline CD bit-identical across two images and two days | unchanged |
| **P5** | the η plant is seen | `|ΔCD|` from `shapeBreak = 1e-4` in **[1.0e-05, 4.0e-05]**, point estimate **2.415e-05** | A4's patched baseline gradient `0.24149949` × 1e-4 | unchanged |
| **P6** | Stage O termination | `EXIT: Optimal Solution Found.`, NLP error < 1e-6, **majors ∈ [7, 14]** | A4 took 6 with 1 DV and no constraints | unchanged |
| **P7** | CD reduction | **≥ 7.478 %**, band **[7.4 %, 16 %]**, point estimate ≈ 9 % | A4 reached −7.4775 % with `shapeBreak` alone | unchanged |
| **P8** | the A4 immateriality re-test | the two images' **analytic** gradients at Stage T's design point agree to **≤ 1e-4 relative per component** | A4 measured 3.9e-06 at 1 DV | unchanged |
| **P9** | endpoint FD | per-component relative error in **[0.1 %, 2.0 %]**, **zero sign flips** | A4 endpoint 0.3112 % shipped / 0.4936 % patched | unchanged |
| **P10** | rear-slant angle at the optimum | **θ ∈ [14°, 22°]** inside Gθ's [12°, 25°] | A4's optimum computes to 15.990° | unchanged |
| **P11** | **the separation monitor REFUSES** | `n_rev_global = 0` and `n_cells(B) < 20` on Stage η's own baseline field ⇒ `NOT AN INSTRUMENT`, reported as `NOT A RESULT` per ruling 4 | §9; three archived A4 fields at freeze **plus** the supervisor's independent count over every 2,777-cell A4 field on disk — zero everywhere | unchanged; **P11 stands** |
| **P12** | wake momentum ratio | `m_def_global` at the optimum in **[0.45, 0.75]** | measured 0.5882 / 0.6024 / 0.6021 on three archived A4 fields | unchanged |
| **P13** | peak RSS | **≤ 2.5 GiB**, point estimate 1.4 GiB | A4 measured 1.007 / 1.331 GiB at np=1. *(Attempt 1's Stage G read 0.607 GiB on a no-flow stage; that is not this prediction's experiment and is not carried as a HIT.)* | unchanged |
| **P14** | cost | attempt-2 total **≤ 59.2 core-min** (prediction + 100 % contingency), **HARD ≤ 69.2** | §10 | **YES — Stage G's price re-based on §2.2's measurement; totals move accordingly** |
| **P15** | **Stage G runs the WHOLE `geom_probe` block to completion** | `d3_summary.json` exists and carries all eight `G_*` keys (`G_nsurf`, `G_zbreak0`, `G_nbreak`, `G_zrear0`, `G_nrear`, `G_thickcon_slant0`, `G_volcon_aft0`, `G_jac`), and the process exits **rc = 0** | **NEW.** §2.3(1): the probe advanced the frontier only to the end of `prob.setup`; the task block is unexercised code | **NEW** |

---

## 8. Gates — every one with its number

**Gη — the noise-floor stop rule. Stage O does not launch until this passes.** Registered signal
reference **A4's own first-major |ΔCD| = 1.40780e-03**.

| outcome | condition | consequence |
|---|---|---|
| **REFUSE** | the planted perturbation moves CD by **< 1.0e-05** | the reader is not shown able to see a non-zero ⇒ item **`BLOCKED`**, Stage O NOT LAUNCHED (rule 3) |
| **η-PASS** | δ_repeat ≤ **1.4078e-05** | Stage O launches, all gates live |
| **η-MARGINAL** | 1.4078e-05 < δ_repeat ≤ **1.4078e-04** | **`GATE REACHED`**; Stage O launches under the frozen restriction: every major whose accepted \|ΔCD\| < 10·δ_repeat is **`NOT A RESULT`** in advance, and the reported reduction carries ±10·δ_repeat |
| **η-FAIL** | δ_repeat > **1.4078e-04** | **`GATE FAIL`** ⇒ item **`BLOCKED`**, Stage O NOT LAUNCHED, noise floor reported, nothing further spent |

The graded quantity is **δ_repeat**, the solve-to-solve difference between two back-to-back
`run_model` calls in one process — **not** the within-run wobble (N-D15). `δ_repeat = 0.0` exactly is
a legitimate η-PASS **only** with the plant seen, reported as *below the write precision* with the
plant's own ΔCD as the resolution bound. **Disclosed, not graded:** A4 §3.2's **0.183 %** FD-reference
path-dependence is the floor on the *instrument*, not on the objective; the two are never substituted.

**G1 — constraint satisfaction.** IPOPT's own `Constraint violation....: ≤ 1e-6` **AND**, re-read
independently from `d3_summary.json`: every `thickcon_slant` in **[0.85 − 1e-6, 1.15 + 1e-6]** and
every `volcon_aft` ≥ **0.98 − 1e-6**. An **empty** constraint array is **`NOT A RESULT`**, never a pass.

**G2 — termination.** `PASS` only on `EXIT: Optimal Solution Found.` **with** Overall NLP error < 1e-6.
A stop on `max_iter 15`, on the `timeout` or on any external cap is **`GATE REACHED`** where the
registered intermediate threshold (reduction ≥ 7.478 %) was met and **`NOT A RESULT`** otherwise —
never `PASS`, and never described by the size of the improvement it reached.

**G3 — endpoint FD per component.** Steps swept in-process at Stage O's optimum: **{1e-1, 1e-2, 1e-3,
1e-4}**, central, `step_calc=abs`. **Frozen plateau rule:** the graded step is the one in {1e-2, 1e-3,
1e-4} whose FD value differs from **both** neighbours by ≤ 25 % **for every component**; if none
does, **G3 is `NOT A RESULT`**. **Band: per-component relative error ≤ 15 %, zero sign flips**; the
aggregate is never the graded quantity.

**G4 — trivial baseline.** Step **1e-1** must **FAIL** the 15 % band or produce a sign flip; if the
deliberately wrong step also passes, the gate is not discriminating and **G3 is `NOT A RESULT`**.

**G5 — planted-zero control.** Re-run before this freeze at zero compute, now **including plants into
an artifact the D3 producer itself wrote** — §16.

**G6 — launch gate**, run as its **own** command before **every** launch: **`free_cores ≥ 4` AND
`MemAvailable ≥ 12 GiB`**, `free_cores := nproc − load1`, stamped into `preflight_history.txt` and
**read before** the launch command is issued. Never polled, never inferred. A shut gate means the arm
**waits**; any departure must be directed in writing by the supervisor and recorded as a dated
amendment **before** the launch.

**G7 — image identity.** `IDWARP_SO_MD5` printed **from inside the process that loaded the library**
equals `85f59e87…` (G, η, O, T-patched) or `f0fcb488…` (T-shipped). A mismatch **voids that stage**.
`nProcs : 1` asserted in every log.

**G8 — cold start, verified before each launch, never after.** No `processor*`, no numeric time
directory but `0`, `0/` restored from `0.orig/`, no `reports/` carried over. Stage η's `eta_call1_CD`
reproducing **`0.1529738469354696`** is the free check that it held.

**G9 — memory envelope.** Predicted peak 1.4 GiB, ceiling 2.5 GiB; kernel cap `--memory=6g
--memory-swap=6g` (equal — no swap escape), `--oom-score-adj=500`, per-stage `timeout`. A container
the kernel OOM-killed (exit 137) is **`NOT A RESULT` about convergence**; a failure with headroom
unused is **not** a memory finding either, and the measured peak is reported beside the cap.

**G10 — cost ceiling. HARD 69.2 core-min for this attempt** (§10). An overrun **stops the run**; it
does not get a new budget.

### G11 — **NEW: Stage G's probe reproduces Stage O's setup path**, and how that is verified

Attempt 1's supervisor triage asked whether the zero-flow probe exercises the setup Stage O would
take. §2.1 answers it for attempt 1 from the traceback; **this gate makes the answer checkable on
every future run of this item, and it needs no change to the comparator.** Three limbs, all of which
must hold; any limb failing is **`GATE FAIL` on G11**, and Stage G is then **not read as a proxy for
Stage O's setup** — Stage G's own measurements stand, but no claim is made that Stage O's setup was
exercised.

**(a) STATIC, frozen here, zero compute — measured on the attempt-2 producer at this freeze:**

| reading | value |
|---|---|
| `class Top(` at line | **132** |
| `prob = om.Problem()` at line | **190** (occurrences in file: **1**) |
| `prob.setup(mode="rev")` at line | **214** |
| first `if args.task ==` at line | **248** → **setup precedes the task branch: True** |
| `def configure(self)` definitions | **1** |
| occurrences of `args.task` inside `class Top` | **0** |
| executable `self.geometry.nom_setConstraintSurface` calls | **1** |

Therefore **`configure()` is task-independent by construction**: the identical `setup` → `configure`
path executes for `geom_probe`, `eta`, `run_driver` and `endpoint_at` alike, and any failure inside it
is common to all four. The launch invocation re-derives these seven numbers from the **staged** file
and refuses on any difference.

**(b) STATIC, at staging:** the md5 of the staged `runScript.py` equals **`4dd289f275b512598e74daf2eb39d729`**
in **every** stage directory, asserted after the copy and again immediately before each launch. Same
file ⇒ same setup path.

**(c) RUNTIME, per stage, from logs the run already writes — no producer or comparator change.** Five
literal setup markers, each verified present in attempt 1's **no-flow** `geom.log` (counts in
parentheses) and in §2.2's probe log:

```
Reading the OpenFOAM mesh..            (2)
('designSurfaces', [0])                (1)
dRdWT Jacobian Free created!           (1)
<class DAFoamSolver>                   (1)
<class DAFoamFunctions>                (2)
```

**Registered check:** all five must appear at least once in `geom.log`, `eta.log` and `opt.log`. A
marker present in one stage's log and absent from another falsifies "same setup path" ⇒ **G11
`GATE FAIL`** (falsifier **F13**).

**(d) CRASH-FRAME RULE:** if any stage aborts, the traceback's **final producer frame** is recorded
with its line number. A frame **at or above line 214** is inside the common setup path and the
failure is, by construction, one every stage would meet; a frame **at or below line 248** is inside a
task block and is that stage's own. This rule is what decides falsifier class F1c versus F1a/F1b
(§17).

**Gs — the separation-onset monitor**, §9, registered together with its predicted refusal.
**Gθ — the rear-slant angle monitor**, §4, band **[12.0°, 25.0°]**.

---

## 9. The separation-onset monitor — carried unchanged, with P11 standing

`d3_sep_monitor.py` reads `U` and the `polyMesh` in pure Python; **the monitor costs zero solver
time**. **Primary graded scalar: `m_def_global = min over all cells of U_x / U0`** — exact,
whole-domain, no box, no cell-centre approximation. **Band [0.45, 0.75]** (P12). **Secondary:
`f_sep(B)`**, the reverse-flow cell fraction in the frozen box `B = x[0.84,1.10] × y[−0.20,0.20] ×
z[0.10,0.35]`, whose cell centres are the vertex average of each cell's face vertices — an
approximation used **only** for box membership, never for a graded number.

**Instrument conditions, frozen:** (i) `n_cells(B) ≥ 20`; (ii) the reader must be shown able to see a
non-zero on a case of this class; (iii) `n_rev_global ≥ 1` on the graded field. **(i) or (iii)
failing ⇒ `NOT AN INSTRUMENT`, exit 3** — the registered refusal, rendered in the record as
**`NOT A RESULT`** with the reason printed beside it (ruling 4).

**Freeze-time measurement, on three archived A4 fields:** `n_rev_global = 0` on all three;
`min U_x` **23.526 / 24.084 / 24.095 m/s**; `m_def_global` **0.5882 / 0.6021 / 0.6024**; `n_cells(B) = 2`.
The zero is evidence because **the plant was seen**: the identical reader on an Ahmed-25° case at
**79,439 cells** finds **528 reverse-flow cells and min U_x = −13.77 m/s** *(disclosed: that case's
STL is not byte-identical to A4's; the plant is a **reader-capability control**, not a physics
comparison)*.

**On this mesh there is not one cell of reverse axial flow anywhere in the domain at any tested design
point.** The curriculum row's *"separation-dominated flow"* premise is **not met by this mesh**; the
expertise D3 buys is **3D geometric constraints under a 3D adjoint**, and the item does not claim the
separation content. A refusal does **not** fail the item — the optimiser, constraint, gradient and
cost gates stand on their own. A band exit on `m_def_global` converts every **aerodynamic** reading to
**`NOT A RESULT`** while those gates stand. With `n_cells(B) = 2`, `f_sep(B)` is a **weak instrument**
and can never carry a `PASS`.

---

## 10. Cost (`CLAUDE.md` rule 12; `DAFOAM_CHARTER.md` §12)

`cost_basis:` **c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER (owner-stated 2026-08-21/22), NOT
MEASURED.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5); **every dollar
figure here is DERIVED from core-minutes and is never quoted as measured.**

### 10.1 This attempt's own price

| stage | work priced | predicted core-min | **stage ceiling** | `timeout` | margin | loss bound if it hangs |
|---|---|---|---|---|---|---|
| **G** | container + setup + the whole `geom_probe` block, no flow | **0.8** | 3.0 | **180 s** | 3.0× | 3.0 |
| **η** | 1 cold + 2 warm + 1 plant primal | **2.5** | 6.0 | **360 s** | 2.4× | 6.0 |
| **O** | cold baseline + ≈11 adjoints + ≈25 primals + 4-step endpoint sweep | **21.0** | 42.0 | **1900 s** | 1.5× | 31.7 |
| **T** | 2 arms × (1 cold primal + 4-step sweep) | **5.3** | 12.0 | **420 s** ea. | 2.6× | 7.0 ea. |
| **TOTAL** | | **29.6** | **63.0** | **3280 s** | | **54.7 = 79 % of this attempt's HARD** |

**Stage G's price is the one number re-based by the diagnosis, and its basis is named:** §2.2's probe
measured **container + `prob.setup` = 0.1833 core-min (11 s)**; attempt 1's crashing Stage G measured
**0.300 core-min (18 s)**; the `geom_probe` block adds two `DVGeo.update` calls and an O(n²) symmetry
loop over the body surface points. **0.8 predicted, 3.0 ceiling** (attempt 1 priced 1.0/3.0 with no
measurement behind it). Every other stage price is attempt 1's, unchanged.

**Predicted 29.6 core-min. With the registered 100 % contingency: 59.2. HARD ceiling for this
attempt: 69.2 core-min = $0.0592 DERIVED.** Pre-authorised class (< $25).

### 10.2 Why 69.2 and not 70.0 — the two-attempt item total

The curriculum prices the **item** at ~70 core-min / $0.06. Attempt 1 is **its own registration** and
its 0.300 core-min is **not** charged to this attempt's stages — but it **is** charged to the item, or
the item's ceiling would silently grow with every attempt.

| line | core-min | basis |
|---|---|---|
| attempt 1, Stage G | **0.300** | MEASURED, `<attempt-1 root>/ledger.txt` |
| attempt 1, triage container | **≤ 0.30** | **BOUND, not a measurement** — attempt 1 `RESULTS.md` §6.1/§7.2 |
| attempt 2, pre-freeze diagnostic probe (§2.2) | **0.1833** | MEASURED, `<probe root>/probe_ledger.txt` |
| **prior spend, worst case** | **≤ 0.7833** | |
| **attempt 2 HARD ceiling** | **69.2** | 70.0 − 0.7833, rounded **down** |
| **item two-attempt total, worst case** | **≤ 70.0** | **= the curriculum figure, $0.0598 DERIVED** |

**Waste, named separately and never absorbed into any ratio (`COMPUTE_BUDGET_CHARTER.md` §6):**
attempt 1's **0.300 core-min** returned a defect rather than the P1/P2/P3 measurements it was priced
for, and attempt 1's `RESULTS.md` §6.1 reports it gross as an unrecovered cost. **This attempt does
not re-report it as its own waste and does not net it against anything.** §2.2's **0.1833 core-min**
is **not** waste: it bought the diagnosis that this registration rests on, and it is charged to the
item at full price above.

### 10.3 Estimate-versus-actual calibration — a registered deliverable

Sanaa's directive, verbatim (2026-08-23): *"for all teams involved once a process is completed, the
estimated costs must be compared with the actual incurred costs so we can improve the lab's
estimates"*. On completion this item reports, **per stage and in total**: predicted core-min, actual
core-min **from the run ledgers**, the **ratio actual/predicted**, and an attribution of the gap
between contention, waste and misprediction — **waste separately named**. Dollars are derived at the
recorded rate and labelled **derived, not measured**. **Contention basis, registered now:** the
like-for-like marker is the same internal work item in two logs (A4's `dRdWTPC: 800 of 1087` pattern,
which measured 1.104× inflation); **whole-arm wall clocks are NOT an inflation figure.**

**Who writes the row:** this lane **DRAFTS** the calibration row into this item's `RESULTS.md`; the
**supervisor lands it** in `docs/COST_CALIBRATION.md`. **No lane writes that file.** The row must
carry **both attempts** and must say that attempt 1's total ratio is **not** a calibration of the
estimate — three of its four stages never launched.

---

## 11. Environment pinning (L-251) and staging discipline (L-252)

**L-251 — uid and directory mode, pinned in the same sentence.** The container runs as its **image
default (root, `mpirun --allow-run-as-root`), with NO `-u` flag**, and the run root is created
**`chmod 0777`** by the launching shell **before the first container starts**, so OpenMDAO's
`reports/` write cannot hit the `PermissionError` that killed W4 M2. Mount `-v <run root>:/mnt`,
`-w /mnt/<stage>`; after each stage `chown -R ubuntu:ubuntu` over that stage's directory and logs;
`--rm` is used and an OOM is read from exit 137. *(This is the invocation §2.2's probe also used, and
it worked: rc = 0, no permission error.)*

**L-252 — per-invocation unique names.** Every staged artifact carries a unique suffix
`$(date -u +%s)_$$`; every staged file is `test -s`-checked **and** asserted to have been produced by
**this** chain in **this** invocation before it is used; steps are chained with explicit `|| exit 1`,
never on `set -e` alone.

**Staging source, fixed here:** `/home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base/` — the pristine
2,777-cell directory A4 ran from, `ahmed_25.stl` md5 **`ec3abd312d3e3e9d15340b95365ff62f`**. **The
mesh is inherited byte-for-byte and is NOT regenerated, NOT refined and NOT re-decomposed.** The
frozen `d3_runScript.py` is copied in as `runScript.py` and its md5 asserted **after** the copy and
**before** the launch.

---

## 12. Run root

**`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/`** — created in **phase 2 only**, with
subdirectories `geom/`, `eta/`, `opt/`, `endpoint_patched/`, `endpoint_shipped/`. **Its absence at
this freeze is asserted inside the commit invocation** (§15). It read **ABSENT** at 18:17:55Z when
this file was written.

**Two other roots exist and are named so neither is confused with it:**
`/home/ubuntu/certonomous-runs/D3-a4-constrained/` — **attempt 1's, preserved evidence, read-only**;
`/home/ubuntu/certonomous-runs/D3-a4-attempt2-probe/` — §2.2's diagnostic probe root, which is **not
a run root of this item**, produces no graded artifact, and is cited only as the evidence for §2.2 and
§16.

---

## 13. What this attempt will NOT touch, listed by name

1. **`cases/dafoam/ladder-a/A4/curriculum_D3/`** — attempt 1's frozen item directory, including its
   `RESULTS.md`. Read-only to this lane, at every step.
2. **`/home/ubuntu/certonomous-runs/D3-a4-constrained/`** — attempt 1's run root. **Preserved
   evidence.** §16's plants are made on **copies** placed under the probe root; the originals are not
   written to, renamed or deleted.
3. **The A4 frozen records** — `A4_ahmed_body.md`, `A4_ahmed_body.json`, `logs_A4/`,
   `first_optimisation_np1/`, `shipped_optimisation_np1/`.
4. **The A4 mesh.** No regeneration, refinement, `snappyHexMesh` or `decomposePar`.
5. **np > 1.** np=1 is required, not chosen: the `scotch` decomposition defect this case
   characterised makes an np>1 A4 adjoint not the transpose Jacobian's solution.
6. **The five upstream defect drafts** — all **NOT FILED**; nothing here files anything.
7. **A6 N=29 and the D464 two-reading gate, the GAMG→PBiCGStab ADF sweep, the `useMeanStates` arm,
   B3 Stage 4 fork-adoption, `DAFOAM_CHARTER.md` §13 PROPOSAL** — untouched.
8. **The MemAvailable 12 GiB floor** — used as a gate, never argued with.
9. **`docs/LAB_STATE.md`, `docs/DOCKET.md`, `docs/LESSONS.md`, `docs/NUMERICS_KNOWLEDGE.md`,
   `docs/COST_CALIBRATION.md`** — this lane writes none of them; records are **drafted** in this
   item's `RESULTS.md` and landed by the supervisor.
10. **`A1/curriculum_D1/`, `A1/curriculum_D1_Cprime/`, `A1/curriculum_D2/`** — read as precedent
    only; no file is shared and none is edited.
11. **`cellLimited Gauss linear 1`** on the momentum equation is live on this case and is **not
    varied**; defect **D-B2** reads 92.8 % on A1 with the rotation patch already in place. Every
    verdict here is a verdict **for this scheme configuration only**.

---

## 14. The §7 "unusual" test, applied again — including to the probe

| candidate | reading | referred to Sanaa? |
|---|---|---|
| the repair itself | two executable lines restoring a **prerequisite** that every working precedent on this box already calls; no new API, no new geometry, no mesh change | **No** |
| **the pre-freeze diagnostic probe (§2.2)** | **0.1833 core-min, no flow solve, inside the ≤ 0.5 permission it was given, in its own probe root, fully declared, charged to the item** | **No — but it is a pre-freeze reading and is DISCLOSED to the supervisor by name (§17.2)** |
| np = 1 | required by the decomposition defect | **No** |
| memory | cap 6 GiB, predicted peak 1.4 GiB, host floor 12 GiB untouched | **No** |
| mesh | inherited byte-for-byte | **No — there is no mesh change** |
| cost | 29.6 predicted, HARD 69.2, **$0.0592 DERIVED**; item two-attempt total ≤ 70.0 / $0.0598 | **No — pre-authorised class (<$25)** |
| GPU / instance change | none; nothing leaves this box | **No** |
| DV extension 1 → 2 | **already ruled AUTHORISED** (ruling 1) | **No** |
| shipped row endpoint-only | **already ruled ACCEPTED** (ruling 2), deferral priced ≈17 core-min | **No** |
| **the mesh cannot carry the separation content** | unchanged: the 45,760-cell successor is a **mesh change** and is **UNPRICED on this case** — the 500–1,500 core-min figure is a cross-anchor scaling, explicitly not a costed proposal | **YES — flagged, costed, NOT run; nothing about it is staged or prepared here** |

---

## 15. Freeze assertions made inside the commit invocation

Every one is executed in the **single shell invocation** that builds and lands the commit, each step
guarded `|| exit 1`, and the commit is refused on any failure:

1. `date -u` re-read and recorded; the **18:17:55Z** stamp at the head of this file asserted present
   in the committed blob.
2. **`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/` asserted ABSENT** (`test ! -e`).
3. The three md5s of §3 re-computed on disk and asserted equal.
4. **`cmp`** asserts `d3_grade.py` and `d3_sep_monitor.py` byte-identical to **both** the attempt-1
   working-tree files **and** the **`0cbf463c` committed blobs**.
5. `diff` asserts the producer differs from attempt 1's **by insertions only** — **19 added, 0
   removed**.
6. `python3 scripts/check_filing.py` run over this directory.
7. HEAD captured **once**; `git diff-tree --stat` asserts the tree carries **only** this item's four
   paths and that the tree differs from the parent; `git update-ref` CAS on that same HEAD; and
   `git diff HEAD~1 HEAD --stat` verifies the same **after** the commit (L-223 — the CAS proves the
   parent, nothing about the tree).

---

## 16. G5 — the planted-zero control, re-run at zero compute BEFORE this freeze

### 16.1 The twelve controls, on files the A4 producer actually wrote

`python3 d3_grade.py --selftest` — run with **this directory's carried copy** of the comparator,
**exit 0**:

```
=== CONTROL SUMMARY ===
  IPOPT exit + constraint violation                    SEEN
  G2 refuses a cap-stop                                SEEN
  check_totals reads a real block                      SEEN
  per-component sign flip is seen                      SEEN
  a 30% error exceeds the 15% band                     SEEN
  G-eta refuses an unseen plant                        SEEN
  G-eta blocks above the noise ceiling                 SEEN
  G-eta passes a quiet objective                       SEEN
  G1 sees an out-of-bound constraint                   SEEN
  G1 passes an in-bound design                         SEEN
  G-theta sees an out-of-band angle                    SEEN
  G-theta reproduces the 25 deg design angle           SEEN

ALL CONTROLS SEEN.
```

### 16.2 **NEW — four controls against an artifact the D3 producer itself wrote**

Attempt 1 could only plant into **A4's** artifacts, because no D3 producer output existed. One now
does: attempt 1's Stage G wrote `geom.log` (502 lines) before it died. It is **copied** into the probe
root and planted there; **the original is never written to.**

| control | file | comparator reading |
|---|---|---|
| **[A] UNPLANTED** | `geom_real.log` (byte copy of attempt 1's) | **G7 `PASS`** — read `85f59e87253e0a71a813f64ca6e4c425`, registered the same; **G3+G4 `NOT A RESULT`** — *"plateau needs all of [0.01, 0.001, 0.0001]; log has []"*. Reproduces attempt 1's own archived `grade_geom.txt` |
| **[B] PLANTED image hash** (`85f59e87…` → `000…0`) | `geom_planted_md5.log` | **G7 `GATE FAIL`** — *"read 00000000000000000000000000000000, registered 85f59e87…"*. **The reader sees a corrupted identity in a D3-written file.** |
| **[C] PLANTED `check_totals`** — a **real** block lifted from A4's own `opt.log`, wrapped in the producer's `D3_CHECK_TOTALS_BEGIN/END` markers at all three plateau steps | `geom_planted_ct.log` | reader now finds the block in the **D3-written** file: *"plateau step = 0.001 … `dvs.shape idx0: analytic 2.14102040e-01 fd 2.14770370e-01 rel 0.3112% flip=False`"*, and still returns **`NOT A RESULT`** because *"trivial baseline at step 0.1 absent — the gate was never shown to discriminate"*. **The empty-log zero in [A] is therefore evidence: the same reader on the same file reads a non-zero when one is planted.** |
| **[D] PLANTED sign flip** (same block, FD sign inverted) | `geom_planted_ct_flip.log` | *"analytic 2.14102040e-01 fd −2.14770370e-01 **rel 199.6888% flip=True**"* — **the per-component flip is seen** |

Artifacts: `<probe root>/g5_controls/{selftest.txt, geom_real.log, geom_planted_md5.log,
geom_planted_ct.log, geom_planted_ct_flip.log, grade_geom_real.txt, grade_geom_planted_md5.txt,
grade_geom_planted_ct.txt, grade_geom_planted_ct_flip.txt}`.

### 16.3 What these controls still cannot catch, stated honestly

The key-set control (§3) parses **names**; the selftest plants **values**. **Neither can see a missing
API call** — that is exactly what attempt 1 proved, and it is why **Stage G exists** and why **P15**
(the full-path prediction) is registered. A control that could have caught attempt 1's defect at zero
compute does not exist on this box; the cheapest instrument that catches it is a **no-flow container**,
and it costs **≈ 0.2–0.3 core-min**.

---

## 17. Falsifiers, and what is on the supervisor's desk

### 17.1 Falsifiers — **F1 is now three classes with a decision rule**

The class is decided by the traceback's final frames under **G11(d)**, never by the fact that a crash
happened.

| id | falsifier | decision rule | what it falsifies |
|---|---|---|---|
| **F1a** | **MISSING-PREREQUISITE class** — a call fails because a **setup call was never made** | the raise is a `KeyError`/`AttributeError` about an unregistered object (e.g. `'Need to add surface …'`), **or** the frame is in a pyGeo/DAFoam registrar entered from `configure()` before any geometry is touched | **the repair set is incomplete** — another prerequisite is missing. Stage G **`BLOCKED`**, §6.3 governs, **no in-place edit**, a new mini-item. **This is NOT a transferability finding** and must never be recorded as one *(attempt 1's F1 was, and its `RESULTS.md` §3.4 corrects it)* |
| **F1b** | **TRANSFERABILITY class** — a DVCon call **reaches the geometry** with the surface registered and fails there | the frame is inside `_generateIntersections` / projection code **after** `_getSurfaceVertices` returns, e.g. no intersections found on the `LE_AFT`/`TE_AFT` lines, or a degenerate projection | **the JBC_Hull/D1-C′ constraint recipe does not transfer to a 3×2×2 FFD on a blunt body** — the finding attempt 1's F1 named but never earned. Stage G **`BLOCKED`**; the constraint geometry of §4 is the suspect |
| **F1c** | **DOWNSTREAM-PRODUCER class** — setup completes and the **`geom_probe` block** fails | the final producer frame is **at or below line 248** (the task branch) | a producer defect **after** setup — `dvg.update`, the `z_at` selection returning `None`, the symmetry loop, the JSON dump. Stage G **`BLOCKED`**; **P15 MISS**; §2.3(1) said this was possible and unproven |
| **F2** | measured FFD Jacobian differs from `(+0.72287, −0.43863)` by > 2 % | | the geometry model is wrong; **Gθ `NOT A RESULT`** and §4's 24.9951° agreement was a coincidence |
| **F3** | symmetry residual > 1e-9 | | "symmetric by construction" is false and the decline of `nom_addLinearConstraintsShape` was wrong |
| **F4** | the η plant moves CD by < 1e-05 | | the η reader cannot see a non-zero ⇒ item **`BLOCKED`** (rule 3) |
| **F5** | δ_repeat > 1.4078e-04 | | the objective's noise swamps the signal ⇒ item **`BLOCKED`**, Stage O never launched |
| **F6** | `eta_call1_CD` ≠ `0.1529738469354696` | | the cold start did not hold, or the case is not A4's — G8 fails and every downstream number is suspect |
| **F7** | Stage O reduction < 7.478 % with `EXIT: Optimal Solution Found.` | | a constraint binds harder than predicted: the constrained optimum is **worse** than A4's unconstrained one. A legitimate, informative result and a **P7 MISS**, not a failure |
| **F8** | the deliberately wrong step (1e-1) **passes** the 15 % band | | G3 is not discriminating ⇒ **`NOT A RESULT`** |
| **F9** | no plateau step exists | | the FD instrument has no flat region here ⇒ **G3 `NOT A RESULT`** |
| **F10** | the two images' analytic gradients differ by > 1e-3 relative at Stage T | | **A4's immateriality does not transfer to two DVs** — the strongest single result this item could produce |
| **F11** | `n_rev_global ≥ 1` on Stage η's baseline field | | **P11 wrong in the informative direction**: this mesh does carry separation, the monitor is an instrument, `f_sep(B)` is graded |
| **F12** | any stage exceeds its ceiling | | the run **stops**; it does not get a new budget |
| **F13** | **NEW** — any G11 limb fails: a static reading differs from §8 G11(a), a staged md5 drifts, or a setup marker present in one stage's log is absent from another | | **Stage G is not a proxy for Stage O's setup path** on this run. **G11 `GATE FAIL`**; Stage G's own measurements stand, but no transfer claim is made |

### 17.2 On the supervisor's desk before launch is authorised

1. **The pre-freeze diagnostic probe (§2.2), by name** — 0.1833 core-min, what it printed, and the
   fact that it **pre-observed P1a**, which is why P1a is disclosed and not graded. The supervisor's
   §3 big-claim check is what decides whether that disclosure is handled correctly.
2. **The repair diff (§3), read as a diff, not as a summary** — 19 inserted lines, 2 executable, and
   the `cmp` assertions that the comparator and monitor are unchanged.
3. **The corrected F1 interpretation (§1.1, §17.1)** — attempt 1's registered reading of its own
   falsifier was wrong, and the correction is a record candidate the supervisor lands, not this lane.
4. **The two-attempt cost accounting (§10.2)** — this lane's reading is that attempt 1's spend is
   charged to the **item** and this attempt's ceiling drops to **69.2** accordingly. A supervisor who
   reads it otherwise should say so **before** launch, because it moves G10.
5. **The four §3 checks are the supervisor's and may not be delegated:** this file read as a diff,
   the pre-registration **committed** before any compute, crash triage, big-claim verification.
   **This lane has launched no stage and will launch none without that authorisation.**

---

## 18. Verdict vocabulary

**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING** — and no synonyms.

- An optimiser stopped by an iteration cap, a wall clock or a budget is **`GATE REACHED`** (registered
  intermediate threshold met) or **`NOT A RESULT`** (not met) — **never `PASS`**, and never described
  by the size of the improvement it reached.
- A stage the kernel OOM-killed is **`NOT A RESULT` about convergence**.
- **η-FAIL, an unseen η plant, or a Stage-G crash of any class makes the item `BLOCKED`** — a
  precondition prevented the measurement — not `NOT A RESULT`, which is reserved for a value produced
  and ungradeable.
- The separation monitor's refusal prints **`NOT AN INSTRUMENT`**, which is a **reason, not a
  verdict**; the Gs cell reads **`NOT A RESULT`** with the reason beside it (ruling 4).
- Shipped and patched are **separate rows** and are never merged into one verdict.
- **`PENDING`** is used only for "not yet run", never to soften a `GATE FAIL`.

---

## 19. Exact launch sequence for phase 2

Run **only** after the supervisor has verified this freeze and authorised launch (§17.2). Every step
is a separate command; **G6 is re-read before each container start**; every step guarded `|| exit 1`.

```
# 0. verify the freeze is the file that will run (CLAUDE.md rule 2)
git show <freeze-sha>:cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/d3_runScript.py | md5sum  # 4dd289f2...
git show <freeze-sha>:cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/d3_grade.py     | md5sum  # a32f0758...
git show <freeze-sha>:cases/dafoam/ladder-a/A4/curriculum_D3_attempt2/d3_sep_monitor.py | md5sum # cd07d7b8...
# and: cmp the two carried files against the 0cbf463c blobs -- byte-identical

# 1. run root + staging (L-251 mode, L-252 unique names, G8 cold start)
test ! -e /home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2   # REFUSE if present
mkdir -p <root> && chmod 0777 <root>
cp -a /home/ubuntu/certonomous-runs/P3-a4-opt-shipped/base <root>/{geom,eta,opt,endpoint_patched,endpoint_shipped}
# assert per stage: no processor*, no numeric time dir but 0, 0/ from 0.orig/, no reports/
# copy d3_runScript.py in as runScript.py; assert md5 4dd289f2... AFTER the copy  (G11 limb b)

# 1b. G11 limb (a): re-derive the seven static readings of sec.8 from the STAGED file; refuse on any diff

# 2. G6 as its OWN command, appended to preflight_history.txt, READ before launching
#    free_cores >= 4 AND MemAvailable >= 12 GiB

# 3. STAGE G   -task geom_probe   timeout 180s   patched   --cpus=1 --memory=6g --memory-swap=6g
#    -> P1b / P2 / P3 / P15. A crash is classified F1a / F1b / F1c by G11(d) BEFORE anything else.
#    -> if it crashes: BLOCKED, sec.6.3, no edit, a new mini-item.

# 4. G6 again. STAGE ETA   -task eta   timeout 360s   patched
#    -> d3_grade.py --eta-summary <root>/eta/d3_summary.json
#    -> Geta PASS / GATE REACHED(marginal) / BLOCKED.  BLOCKED => STOP. Nothing further is spent.
#    -> d3_sep_monitor.py --u <eta time dir>/U --mesh <eta>/constant/polyMesh \
#         --plant /home/ubuntu/certonomous-runs/act7-ahmed_25-b14562/154/U    (P11)
#    -> G11 limb (c): the five setup markers of sec.8 present in geom.log AND eta.log

# 5. G6 again. STAGE O   -task run_driver   timeout 1900s   patched
#    -> d3_grade.py --summary ... --ipopt <root>/opt/opt_IPOPT.txt --log <root>/opt.log \
#         --row patched --core-min <measured>
#    -> G11 limb (c) again across geom.log / eta.log / opt.log

# 6. write the design-vector JSON from Stage O's d3_summary.json (sec.6.2)
# 7. G6 again. STAGE T-patched   -task endpoint_at -dvfile ...   timeout 420s   patched
# 8. G6 again. STAGE T-shipped   -task endpoint_at -dvfile ...   timeout 420s   SHIPPED image
#    -> P8 / F10: the clean toolchain comparison A4 could not make.

# 9. RESULTS.md: six report headings, both toolchain rows, the two-attempt calibration draft
#    (sec.10.3), every verdict from the sec.18 vocabulary. Records drafted here, landed by the
#    supervisor.
```

---

**END OF PRE-REGISTRATION. Frozen by commit. Nothing below this line existed when the gates,
thresholds, caps and labels above were fixed. NO SOLVER COMPUTE SPENT ON THIS ATTEMPT; the one
pre-freeze diagnostic container is declared in §2.2 and costed in §10.2. NOT FILED ANYWHERE.**

---

## 20. ADDENDUM A1 — Supervisor launch authorisation (dated; version bump v1.0 → v1.1)

**Dated 2026-08-24T18:29:24Z** (`date -u`, read in the shell invocation that wrote this addendum, asserted the
run root absent, built the tree and landed the commit carrying it).

**lines whose number changed above this section: 0** — this addendum is appended at the foot of the
frozen file; the 823 lines above it are byte-identical to the `092e54e7` blob, asserted by md5 of
`head -n 823` taken before and after the append in the same invocation. Nothing above was touched,
re-flowed or re-numbered (`CLAUDE.md` rule 6).

**Version.** The frozen document carried no explicit version token. This addendum designates the
state committed at `092e54e7` as **v1.0**, and this file with this addendum as **v1.1**.

**Condition asserted, and how it was checked (`CLAUDE.md` rule 2, before-first-compute clause).**
**NO SOLVER COMPUTE HAS BEEN SPENT ON THIS ATTEMPT WHEN THIS ADDENDUM IS COMMITTED.** The run root
`/home/ubuntu/certonomous-runs/D3-a4-constrained-attempt2/` **does not exist**: `test ! -d` on that
exact path is executed **inside the same shell invocation** that writes this addendum and that builds
and lands the commit carrying it, and the commit is refused if the path is present. No container of
this attempt has been started, no image has been run, and no solver has executed. The one pre-freeze
diagnostic container is the one declared in §2.2 and costed in §10.2; it predates the freeze, ran in
its own probe root, and is not compute of this attempt's stages. The `date -u` stamp at the head of
this section is read in that same invocation.

**No gate, band, threshold, cap or label is altered by this addendum.** Every number in §7, §8, §9
and §10 stands exactly as frozen.

### 20.1 The authorisation, as directed by the dafoam-supervisor

**Launch of phase 2 is AUTHORISED, dated 2026-08-24**, after the supervisor's own §17.2 item-5 checks,
performed personally and not on relay:

1. **The freeze was verified by the supervisor at 18:26Z** — the three frozen executables on disk were
   hashed against the committed blobs at `092e54e7` and found equal
   (`d3_runScript.py` `4dd289f275b512598e74daf2eb39d729`, `d3_grade.py`
   `a32f075853e264910ee0a6c2473fd948`, `d3_sep_monitor.py` `cd07d7b8a70627579384f263ba92194e`), and the
   latter two additionally byte-identical to the attempt-1 `0cbf463c` blobs.
2. **The repair diff was read as a diff, not as a summary** (§17.2 item 2). The supervisor read the two
   executable lines of the repair:
   `tri_points = self.mesh.mphys_get_triangulated_surface()` and
   `self.geometry.nom_setConstraintSurface(tri_points)`, at the attempt-2 producer's lines 155–156,
   inside `configure()` between `nom_add_discipline_coords` and `getLocalIndex(0)`. The remaining 17
   inserted lines are documentation; nothing is deleted or modified.
3. **The pre-freeze diagnostic probe (§2.2) was read by name** — 0.1833 core-min, no flow solve, its own
   probe root — and its consequence accepted: **P1a is disclosed as pre-observed and is NOT graded**,
   while P1b, P2, P3 and P15 remain unobserved and are graded.
4. **The two-attempt cost accounting of §10.2 is RULED to stand.** The supervisor's reading is this
   lane's reading: attempt 1's spend is charged to the **item**, and **the HARD ceiling for this attempt
   is 69.2 core-min**, not 70.0. §17.2 item 4 asked for this to be said before launch, because it moves
   G10; it is said here. **69.2 stands.** An overrun stops the run; it does not get a new budget
   (`CLAUDE.md` rule 12, F12).

The four rulings carried from attempt 1 (§1.2) are unchanged and are not re-argued: DV 1 → 2
authorised; the shipped row bought as endpoint-only accepted; the item proceeds with the separation
content honestly absent; `NOT AN INSTRUMENT` is a printed reason and the Gs cell reads `NOT A RESULT`
with that reason beside it.

**Nothing is filed, sent, uploaded, posted or pushed anywhere** (`CLAUDE.md` rule 7). SUBMISSIONS
PARKED.

**END OF ADDENDUM A1. Phase 2 may launch. Nothing below the line above existed when the gates,
thresholds, caps and labels were fixed.**
