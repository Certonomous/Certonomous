# F5b PHYSICS RUNG — PRE-REGISTRATION

**Status: `PENDING` — DRAFT, NOT FROZEN, NOTHING LAUNCHED, supervisor read required before freeze.**

**Team:** cfd. **Family:** F5b — pitching NACA 0012 dynamic stall (McAlister, Carr &
McCroskey, NASA TP-1100, 1978, case "(e)").
**Rung:** Physics (charter §3 rung 2: *"the mechanism the case exists to show is visibly
present"*). The Feasibility rung is **PASS** on record; the Gate rung is **not** registered
here and remains **PENDING** with its reference **NOT OBTAINED** (§2 field 4 below).

**Drafted:** 2026-08-24T16:25:35Z (`date -u`, same shell invocation as the write).
**Revised after supervisor read:** 2026-08-24T16:34:57Z (`date -u`, same shell invocation as the revision write).
**Revised again (Revision 2) after the supervisor's freeze approval:** 2026-08-24T17:21:37Z (`date -u`,
taken in the shell invocation that opened this revision, immediately before the edits below; no
compute of any kind intervened between the stamp and the edits).
**Drafted at HEAD:** 579843978398d1e719a7ccdc8c367dcbcfd56c29. **Revised at HEAD:** ec35bf9e2057654e50e472879895d8053a4b263f.
**Revision 2 at HEAD:** e9737c5f6f3f64295c52a7e5ac0ca5ce5d2386bb.

**Revision 1, 2026-08-24T16:34:57Z — six changes, all made while the document is UNFROZEN and while
no run directory exists (§9), so `CLAUDE.md` rule 2's before-first-compute amendment
condition holds and is checked, not asserted.** Changes: (1) §9's run-tree quote, which was
**empty** in the first draft, now carries real output — the first draft's capture shell
`&&`-chained an `ls` of a path that is *expected* to fail, so the chain short-circuited and
the second capture never ran; **a freeze condition with an empty quote is not a checked
condition**, and the near-miss is recorded here rather than quietly fixed. (2) §2/§3 resolve
the C_L-versus-C_y question against E2's actual direction vectors. (3) G3's Courant limb is
re-specified against OpenFOAM's own `setDeltaT.H`. (4) C-P1 is sharpened to a predicted
plant magnitude, and a defect in the first draft's plant **index** is corrected. (5) G2's
cross-stroke scope is disclosed and **its margin is corrected downward, 2.27× → 1.97×**.
(6) §11 A-1 is closed. **Gate quantities and bands are unchanged**; the only numeric change
is a *reference* figure that made a margin claim smaller, i.e. in the conservative direction.
**Compute consumed by this document: 0 core-minutes.** No solver ran. No mesh was built.
No run directory was created. This file is a draft and carries no frozen sha.

**Revision 2, 2026-08-24T17:21:37Z — four changes, made while the document is still UNFROZEN and
while no run directory exists.** The freeze condition of §9 was re-checked **before** any character
of this revision was written: `test -e /home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1`
returned **ABSENT** at **2026-08-24T17:15:13Z**, and the whole F5b run tree still held exactly one
file (`run_pitch.py`) — so `CLAUDE.md` rule 2's before-first-compute amendment condition holds, is
**named** (`verification/runs/F5b_runs/physics_p1`) and is **checked, not asserted**. Changes:
(1) **§11 A-1's attribution is corrected** — the closure was previously credited to a supervisor
session that was terminated by the usage limit and whose work therefore cannot be verified by anyone
reading this file; the citation is replaced by a re-derivation that *can* be reproduced, and the
split-terms hand route is retained but relabelled as this lane's own. (2) **§2's G3 Courant limb
gains its reading rule** — which printed line is graded, what it actually measures, and the count
assertion that binds it — read out of `pimpleFoam.C` and `CourantNo.H` on this box. (3) **§10/§4
gain a binding header-name parsing rule** for `coefficient.dat`, with the OpenFOAM v2606 header
layout quoted from the installed source, and clause 5's `n_steps` is given its line citation
(E2:306). (4) **A defect the earlier revisions carried is corrected**: §4 twice referred to the
coefficient file's *"own α column"*, and **`coefficient.dat` has no α column** — the correction is
recorded at the point of use and in §11 as **A-10**. (5) A **fifth item, found while checking (3) and disclosed rather than left**: §3's table
calls E4's `pitchAxis (0 0 1)` correct; in v2606 that entry is **not read at all** and the effective
pitch axis is `(0, 0, −1)` — recorded as **A-11**, affecting `C_M` only, which this rung does not
gate. **Gate quantities, bands, cap and labels are UNCHANGED by every one of these five changes**;
nothing here moves a threshold in either direction, and the two corrections (4) and (5) both fall on
quantities no limb reads. (6) A **declared round-off floor** under C-P1 limb 1's tolerance, recorded
at the point of use in §4 with the measurement showing it **did not bind** on the C-N1 fixture.
**Compute consumed by Revision 2: 0 core-minutes.**

---

## 0. What this document is, and what it is not

**It is** a prediction-first pre-registration under `CLAUDE.md` rule 2 and
`VERIFICATION_CHARTER.md` §2b/§2d, drafted before any F5b Physics compute exists, naming
the gate quantity, its band, its label mapping, its controls, its completion rule, its cost
and its cap **in advance**, so that the gate cannot later be chosen to fit an answer.

**It is not:**

- **Not frozen.** It carries no commit sha and binds nothing yet. The supervisor's personal
  read (`SUPERVISION_CHARTER.md` §3, check 4 — *pre-registration committed before compute*)
  has not happened. Under rule 2 amendments are legal until first compute; the freeze
  condition and the check that proves it are in §9.
- **Not a launch authorisation.** §9 states the condition; nothing here creates it.
- **Not the Gate rung.** The quantitative comparison against TP-1100 is a separate rung and
  is **BLOCKED** on a reference that is **NOT OBTAINED** (§2, field 4). Every gate limb
  registered here reads the run's **own** output against a reference derived analytically
  in this document, so the Physics rung is answerable while the paper is off disk.
- **Not F5a, and not the Re=100 shedding act.** Two live name collisions, both checked on
  disk this session:
  1. `verification/campaign/F5b_cylinder_re100_act.json` (md5 `fe5a4c6f3ceafa1f9caba4a6d27aa7fe`) is a
     **different case** — `workflows.cylinder_vortex_shedding` at Re = 100, St = 0.15776
     against a Roshko/Williamson correlation. It shares the token `F5b` and nothing else.
     No number in it is evidence for anything here.
  2. `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/f5b_re1000_3d_pilot` (and its three
     `f5b_*_stage` siblings) are **F5a's** 3-D cylinder pilot — job tag `f5a_re1000_3d_pilot`,
     `F5a_cylinder_reynolds_ladder.md:484`. Directory prefix `f5b_` outside git means the
     F5a cylinder, never this case.
- **Not next in the queue.** The board's standing priority puts **R4's CPU-minutes first**
  (`docs/LAB_STATE.md:47`, `:58` — Sanaa 2026-08-22, *"R4's CPU-minutes have first call on
  capacity"*, IN FORCE) and the **thermal spine** second (`:47`, the THERMAL BUILDUP
  DIRECTIVE H-1…H-7, DC-cooling as destination) **ahead of this rung**, which sits at
  `docs/LAB_STATE.md:600` as item (3), *"F5b physics rung (~25–35 core-min) as the next
  cheap …"*. This registration is written so the rung is ready when capacity reaches it,
  not to jump the queue.

---

## 1. Evidence base

Every number in this document comes from one of these paths. md5s taken in the same shell
invocation as this file's stamp.

| # | Path | md5 | What is taken from it |
| --- | --- | --- | --- |
| E1 | `verification/campaign/F5bc_unsteady_statistics.md` | `50c19cb65d912bd40de7a0949bfa288e` | The F5b section (lines 257–294): reference case (e), mesh/motion design, the two fixed bugs, the **Feasibility PASS** and its cost basis, the `[to be completed]` Physics/Gate placeholders, the 15–25× unsteady/steady wall-time statement |
| E2 | `sdk/workflows/pitching_airfoil_case.py` | `06bfcfd40bc011cf2cb2fd41370b5c4b` | The case constants and the solve sequence: `RE=2.5e6`, `NU=4e-7`, `ALPHA_MEAN_DEG=15`, `ALPHA_AMP_DEG=10`, `REDUCED_FREQ=0.15`, `OMEGA=0.3`, `PERIOD=20.943951…`, `PITCH_AXIS=(0.25,0,0)`, `FARFIELD_R=25`, `FIRST_CELL=8e-6`, `TU_FREESTREAM=1e-3`, `MUT_RATIO=10`; `build_case`, `run_case`, `_pimple_fv_solution_with_mesh` |
| E3 | `verification/runs/F5b_runs/run_pitch.py` | `96886e9efa84a09332dad45eef4d71d5` | The driver CLI: `--level --out --end-time --dt0 --max-co --timeout`; the **1800 s default timeout** (§3 defect D-3) |
| E4 | `sdk/workflows/tmr_verification.py` | `118671e25ca648d068321d8a1e401374` | `NACA_LEVELS` (coarse `113x33`, 16/24/32 → **3,584 cells**); `pimple_control_dict` (writeControl `adjustableRunTime`, `writeInterval = endTime`, `purgeWrite 1`, `maxDeltaT = endTime/200`, `forceCoeffs1` at `writeInterval 1` timeStep, `yPlus1` onEnd) |
| E5 | `sdk/workflows/transonic_airfoil.py` | `06a56a1411bb60a4f60889ff154ccdd5` | `transonic_blockmesh_dict` — the C-grid O-topology the mesh is built from, unmodified |
| E6 | `verification/campaign/F5a_cylinder_reynolds_ladder.md` | `8348d1f7b27df90a5107d3f3bd28afb3` | The *"do not climb to Re 5000 or Re 10,000"* ruling (lines 1325–1370) — **scoped to F5a and inapplicable here**, see §2 note; and line 484, the `f5b_*` directory collision |
| E7 | `docs/VALIDATION_INVENTORY.md` | `41a310db39123c92094f2100708d9108` | Line 306 (F5b row: Feasibility PASS, Physics/Gate literal placeholders, **"NO GATE EXISTS"**) and line 616 (the TP-1100 digitisation item, zero compute) |
| E8 | `verification/campaign/F5b_cylinder_re100_act.json` | `fe5a4c6f3ceafa1f9caba4a6d27aa7fe` | Read **only** to establish that it is a different case (§0) |
| E9 | `docs/LAB_STATE.md` | `891539c4f95556971e563787e5329ba8` | Lines 47, 58, 555, 557, 600 — the priority order and the F5b board row |

**Artifacts that do NOT exist, checked on disk 2026-08-24T16:25:35Z and recorded as absent:**

| What | Check performed | Result |
| --- | --- | --- |
| Any F5b Feasibility run tree, log, `record.json` or `coefficient.dat` | `find` over `verification/runs/F5b_runs/` (holds exactly one file, `run_pitch.py`); `ls demo-output/website/solve_registry/ \| grep -i 'f5b\|pitch'`; `find /home/ubuntu -maxdepth 5 -iname '*pitch*'` | **Absent.** The Feasibility figures (1,473 steps, 85.1 s wall, 3,584 cells) are **record-quoted, artifact-missing** — E1 is the only witness, and this is stated on the face of every cost figure derived from them (§8) |
| NASA TP-1100 (PDF or `.txt` sidecar) | `find docs/papers -iname '*mcalister*' -o -iname '*tp1100*' -o -iname '*19780009057*'`; `find /home/ubuntu -maxdepth 6` same patterns; `grep -ril mcalister` over the repo | **Absent from the box.** Prose mentions only. See §2 field 4 — this **BLOCKS the Gate rung** and does not block this one |
| Any static-stall datum for NACA 0012 at Re = 2.5×10⁶ | `find docs/papers -iname '*ladson*'`; listing of `docs/papers/benchmark_test_cases/` and `docs/papers/turbulence_models/` | **Absent.** Consequence: the Physics gate may **not** be posed as *"dynamic stall angle exceeds the static stall angle"*, because the static value has no source on disk. The gate below is posed so it does not need one |

---

## 2. The question, and the pre-declared gate

### The question

> **Is the dynamic-stall mechanism present in this case's own output — an open C_L–α
> hysteresis loop containing a lift collapse that attached, unstalled flow cannot produce —
> over one full pitching period, on the Feasibility mesh?**

This is charter §3 rung 2 exactly: the mechanism, visibly present. It is **not** *"does the
loop match TP-1100"* (that is the Gate rung, blocked) and **not** *"is the loop
cycle-converged"* (that needs ≥3 periods and is outside this budget — see the label ceiling
in §6).

### The datum, and why it is derived rather than cited

The discriminating reference is the **attached-flow (Theodorsen) hysteresis loop** for the
same prescribed motion. This is the answer to the §2a identity test, and it is the reason
the gate is built the way it is:

> **Could a wrong treatment still pass a bare "the loop is open" gate?** **Yes, trivially.**
> A solve that never stalls at all still produces an open C_L–α loop, purely from the
> pitch-rate phase lag and added mass. A gate on loop-openness alone is a green light wired
> to nothing. The gate must therefore separate *dynamic stall* from *attached-flow phase
> lag*, and both limbs below are set against the attached-flow value, not against zero.

**Derivation** (classical thin-airfoil unsteady theory; Theodorsen's function via the Jones
two-lag approximation `C(k) = 1 − 0.165/(1 − 0.0455i/k) − 0.335/(1 − 0.3i/k)`), evaluated at
this case's own registered parameters from E2 — `k = 0.15`, `α_a = 10°`, pitch axis at the
quarter chord (`a = −1/2` semi-chords from mid-chord):

```
C(k)  = 0.7819026 − 0.1798329 i
Z     = 2π C(k) (1 + i k (1/2 − a)) + π i k + π a k²
      = 5.0469847 + 0.0782415 i          [C_L per radian of α]
|Z|   = 5.0475912 per rad = 0.08809709 per deg
A_att = π α_a² Im(Z)  (α_a in rad)
      = 0.00748759 C_L·rad = 0.42900727 C_L·deg
```

Cross-checked by direct trapezoid quadrature of `∮ C_L dα` on 200,001 samples over one
period: `0.007487589374` vs closed-form `0.007487589375` (agreement to 10 significant
figures). **Period `T = 2π/ω = 20.943951023931955`**, consistent with E2's `PERIOD`.

**Honesty note on `A_att`, and it is load-bearing.** `Im(Z) = 0.0782` is a **near
cancellation** between the circulatory lag term (−0.393) and the added-mass term (+0.471).
It is therefore the least robust number in this document, and the gate is deliberately
built so that an error of up to ~4× in `A_att` still leaves limb **G1** discriminating, and
so that limb **G2** depends only on `|Z|` — which is dominated by the quasi-steady `2π` and
is robust (5.048 against a quasi-steady 6.283). **This derivation must be re-derived
independently before freeze**; it is flagged in §11 as guess **A-1**.

**Note on the F5a ladder ruling.** `F5a_cylinder_reynolds_ladder.md:1344` says *"do not
climb to Re 5000 or Re 10,000 next."* **Checked and found inapplicable to F5b.** Both of
its two stated reasons are properties of the **F5a circular-cylinder ladder**: (1) the 2-D
laminar wake losing its *mean recirculation bubble* above Re ≈ 3900, which makes F5a's own
`L_rec/D` gate inapplicable; and (2) reference availability at Re 5000/10,000 for a
cylinder. F5b is a different geometry, a different solver configuration (moving-mesh URANS
with kOmegaSST rather than 2-D laminar), and a **fixed** Reynolds number of 2.5×10⁶ set by
the reference case — it is not on that ladder and does not climb it. **The ruling does not
bind this rung.** (What *does* travel from F5a is the naming collision in §0.)

### The measured column IS C_L, not C_y — checked against E2's own direction vectors

**The question that had to be settled before the gate could name its quantity:** OpenFOAM's
`forceCoeffs` reports `Cl` and `Cd` resolved along whatever `liftDir` and `dragDir` the
dictionary gives it. If those were axis-aligned `(0 1 0)` / `(1 0 0)` while the freestream
sits at 15°, then the column labelled `Cl` would actually be
`C_y = C_L cos15° + C_D sin15°`, and every band above would be a band on the wrong quantity.

**Checked, not assumed.** E4's `pimple_control_dict` passes `drag_dir` / `lift_dir` through
to the function object verbatim; E2 lines 88–91 construct them:

```
_alpha_rad       = math.radians(ALPHA_MEAN_DEG)                       # 15°
DRAG_DIR         = (cos α_m, sin α_m, 0)  = (0.96592583  0.25881905  0)
LIFT_DIR         = (−sin α_m, cos α_m, 0) = (−0.25881905 0.96592583  0)
U_FREESTREAM_VEC = (U cos α_m, U sin α_m, 0) = (0.96592583  0.25881905  0)
```

Evaluated on this box in the same session:

```
liftDir · Û = −0.25881905 × 0.96592583 + 0.96592583 × 0.25881905 = 0.0   (exactly)
dragDir · Û =  0.96592583² + 0.25881905²                         = 1.0   (exactly)
```

> **`liftDir` is exactly perpendicular to the freestream and `dragDir` exactly parallel to
> it. The measured column is a true C_L. No `cos 15° = 0.9659` factor enters, no C_D
> contamination enters, and no rename is required — every band in this document is a band on
> C_L.**

**And the reason this stays true throughout the motion, which is the non-obvious half.** The
freestream velocity vector is **fixed in the lab frame** at 15° (E2:45–48: the mean incidence
is realized by fixing the freestream vector, *not* by mesh rotation). The instantaneous
incidence changes because the **airfoil** rotates ±10° about the quarter chord, not because
the flow direction changes. So the freestream direction — and therefore the correct lift
direction — is **constant**, and a `liftDir` fixed at the mean angle is perpendicular to the
actual oncoming flow at every instant of the cycle, not merely on average.

**The rest of the `forceCoeffs1` block, quoted from E4** (`pimple_control_dict`), with what
each means here:

| entry | value | consequence |
| --- | --- | --- |
| `magUInf` | `1.0` (`U_INF`) | the normalising velocity is the true freestream magnitude |
| `lRef` | `1.0` | moment reference length = chord |
| `Aref` | `1.0` (`CHORD`) | 2-D per-unit-span reference area = chord; C_L is the conventional 2-D coefficient |
| `rho` / `rhoInf` | `rhoInf` / `1.0` | incompressible normalisation, consistent with `transportProperties` |
| `patches` | `(airfoil)` | forces integrated over the airfoil patch only |
| `writeControl` / `writeInterval` | `timeStep` / `1` | one data line per time step — the basis of completion clause 5's three-way count |
| `pitchAxis` | `(0 0 1)` | the z axis, correct for this 2-D case |
| **`CofR`** | **`(0 0 0)`** | **the moment reference is the ORIGIN, not the quarter chord `(0.25, 0, 0)` where the airfoil actually pivots.** `CofR` is a dictionary constant in the global frame: it is read once and **does not move with the mesh**, so as the mesh rotates the moment arm to the true pivot changes |

> **The `CofR` mismatch affects `C_M` ONLY, and `C_M` is NOT GATED by this rung — G1 and G2
> read `Cl` alone.** It is recorded here so that nobody later reads a `C_M` column out of
> this run's `coefficient.dat` believing it is a quarter-chord pitching moment. It is not:
> it is a moment about the origin, taken about a reference point that stays put while the
> body rotates. Any future rung that wants C_M must fix `CofR` first, and that is a
> different registration.

### How `coefficient.dat` is parsed — BY HEADER NAME, never by column position (Revision 2)

**Registered as binding on §10's reader:** the columns of
`postProcessing/forceCoeffs1/*/coefficient*.dat` are located **by matching the header name** — `Time`,
`Cl`, `Cd` — read from the file's own commented column-header line. **Positional indexing is
forbidden**, and the reader **refuses (exit 2)** if a required name is absent, appears twice, or if a
data row's field count differs from the header's.

**This is not a style preference. A positional reader would be WRONG on this file today.** The v2606
header layout, read from the installed source rather than recalled
(`/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/forceCoeffs/forceCoeffs.C`):

- `:337–349` — *"if the dictionary has no `coefficients` entry: `Info<< "    Selecting all
  coefficients"`, `coeffs_ = selectCoeffs()`, and every entry gets `active_ = true`."* **E4's
  `forceCoeffs1` block has no `coefficients` entry** (`tmr_verification.py:3416–3432`), so **all
  twelve coefficients are written**, not the three a reader might expect.
- `:135–151` — `selectCoeffs()` inserts `Cd`, `Cs`, `Cl`; then a front/rear pair for each of those
  three (`name + "(f)"`, `name + "(r)"`, `forceCoeffs.H` `frontName()`/`rearName()`; the parentheses
  survive because `word::valid` excludes only whitespace, `" ' / ; { }`); then `CmRoll`, `CmPitch`,
  `CmYaw`. **Twelve columns plus `Time`.**
- `:237, :256` — both the header writer and the row writer iterate `coeffs_.csorted()`, i.e. in
  **lexicographic order of the hash key**, not insertion order.

**Therefore the column order on disk is, and the reader must not assume it:**

```
Time  Cd  Cd(f)  Cd(r)  Cl  Cl(f)  Cl(r)  CmPitch  CmRoll  CmYaw  Cs  Cs(f)  Cs(r)
```

> **`Cl` is the FIFTH field (0-based index 4), not the third.** A reader written to the familiar
> `Time Cd Cl Cm` layout would have graded this rung's gate on **`Cd(f)`** — half the drag plus a
> pitching moment — and would have produced a number, not an error. That is precisely the failure a
> planted control cannot catch, because the wrong column is still a live column full of plausible
> floats. **The header-name rule is the control for it, and C-N1's fixture carries the full
> twelve-column layout so the rule is exercised before any real file exists.**

**The exact header format, quoted from the source that writes it**
(`forceCoeffs.C:220–246`; helpers in
`/usr/lib/openfoam/openfoam2606/src/OpenFOAM/db/functionObjects/writeFile/writeFile.C:323–358` and
`writeFileTemplates.C:31–42`):

- `charWidth() = writePrecision_ + addChars`, with `addChars = 8` (`writeFile.C:37, :319`).
  `writePrecision_` defaults to `IOstream::defaultPrecision()` (`writeFile.C:218`), which
  `Time::readDict` sets from the **controlDict's** `writePrecision` (`TimeIO.C:379–384`) — **10** for
  this case (E4). So **`charWidth() = 18`**.
- `writeHeaderValue`: `'#'`, `' '`, the property left-justified in `setw(charWidth() - 2)` = 16,
  then `':'`, `' '`, the value.
- The column line: `writeCommented(os, "Time")` → `'#'`, `' '`, `"Time"` left-justified in 16; then
  for each active coefficient `writeTabbed` → a **tab** then the name right-justified in `setw(18)`.
- Data rows: `writeCurrentTime` → the time right-justified in `setw(18)` (`Time::timeName`, so
  `timeFormat general` / `timePrecision 8`), then for each coefficient a **tab** then the bare value
  at stream precision 10 (`os << tab << (…)`, `forceCoeffs.C:265`) — **the values are tab-separated
  and NOT column-padded**, so column alignment cannot be relied on even to find a field boundary.

**The header line, verbatim in shape** (`␉` = tab, the name right-justified in 18):

```
# Time            ␉                Cd␉             Cd(f)␉             Cd(r)␉                Cl␉ …
```

**The registered parse, in one sentence:** skip `#` lines but keep the **last** one whose
whitespace-split tokens (after stripping the leading `#`) begin with `Time`; take that token list as
the column names; split every data row on whitespace; assert `len(row) == len(names)`; index by name.
This is robust to the padding, to the tabs, to a future `coefficients` entry changing the column set,
and to the front/rear names containing parentheses.

**Correction carried here, and it is a defect in the earlier revisions, not a clarification.** §4's
C-P1 twice speaks of *"the copy's own α column"*. **`coefficient.dat` has no α column** — the
enumeration above is the complete column set. Wherever this document says *"the copy's own α column"*
it means, and the reader implements, **the α series reconstructed sample-by-sample from the copy's own
`Time` column** through E2's prescribed motion `α(t) = ALPHA_MEAN_DEG + ALPHA_AMP_DEG · sin(OMEGA · t)`
— which is an **identity** (α is a prescribed input, not a solved quantity) and so carries the
property C-P1 actually needs: it is derived from the file the reader parsed, sample count and all,
and it cannot be tuned to the answer. The plant-index rule `i*` and `ΔA_pred` are computed from that
reconstructed series. **This changes no gate quantity, band, cap or label**; it is recorded in §11 as
**A-10** and made before any compute exists.

**`n_steps`, cited.** Completion clause 5's third count is the `"n_steps"` key of `record.json`,
written at **E2:306** (`sdk/workflows/pitching_airfoil_case.py:306`, `"n_steps": len(times)`).

### The gate — three limbs, all read from the run's own `coefficient*.dat`

Analysis window `W = [t₁, t_end]` with `t₁ = t_end − T` computed from `PERIOD` in the reader
(not from a rounded literal), and asserted `t₁ ≥ 1.0` (the transient exclusion window E1
declares: the impulsive-start spike lives in the first ~0.02 time units and C_L is
physically sane by t = 1).

| id | limb | quantity | pre-declared band | rule-1 label |
| --- | --- | --- | --- | --- |
| **G1** | **Loop is open, and more open than attached flow** | `A_L = ∮_W C_L dα` over one full period, trapezoid on every sample, α in degrees, traversal in increasing t | **PASS** if `A_L ≥ +2.00 C_L·deg`. Else **GATE FAIL**. Reference `A_att = 0.429 C_L·deg` (derived above); 2.00 is **4.66×** the attached-flow value, so the limb survives a 4× error in `A_att` | PASS / GATE FAIL |
| **G2** | **A C_L excursion exists that attached flow cannot produce** | ∃ a sample pair `(i, j)`, `i < j`, both in `W`, with `\|α_j − α_i\| ≤ 2.00°` and `C_L,i − C_L,j ≥ 0.40` | **PASS** if such a pair exists. Else **GATE FAIL**. Attached-flow ceiling over **any** admissible pair: **0.2035** (derived below); 0.40 is **1.97×** that ceiling | PASS / GATE FAIL |
| **G3** | **The reading is admissible** | Completion rule §5 in full, **and** the §4 controls all pass, **and** the Courant conditions re-specified below | **NOT A RESULT** on any failure — value withheld, not softened | NOT A RESULT |

#### G2's scope, disclosed: the pair may be within-stroke OR cross-stroke, and this is intended

As written, G2 admits **two** kinds of pair, and both are dynamic-stall signatures:

- **Within-stroke** — a lift *collapse*: C_L falls by ≥ 0.40 while α moves ≤ 2.00° within
  the same stroke. This is stall onset proper.
- **Cross-stroke** — the *hysteresis width*: the same α visited on the upstroke and on the
  downstroke, `Δα ≈ 0`, with C_L differing by ≥ 0.40. This is the post-stall lift deficit.

**Both are admitted deliberately.** Either alone establishes that the mechanism is present,
and demanding one specific signature would make the gate a test of *which* dynamic-stall
signature appeared rather than *whether* one did.

**What this costs, and it is paid rather than hidden.** Admitting cross-stroke pairs raises
the attached-flow ceiling G2 must clear, because attached flow has a hysteresis width of its
own:

```
cross-stroke gap, attached flow, at matched α:  ΔC_L = 2 α_a Im(Z) |cos ωt|
                                     maximum =  2 × 0.174533 × 0.078242 = 0.02731
within-stroke ceiling over 2.00°:               |Z| × 2° = 0.17619
combined supremum over ANY pair with |Δα| ≤ 2.00°:
      α_a (|Re Z| × 0.2 + |Im Z| × 2) = 0.174533 × (1.009397 + 0.156484) = 0.20348
      (0.2 = 2°/10° is the largest admissible |Δ sin ωt|)
brute-force check over all pairs, one period, 40,000 samples:  0.20332
```

The analytic bound **0.20348** is the conservative supremum, and it correctly exceeds the
discretely sampled brute-force maximum. **The registered margin is therefore corrected
downward: G2's band of 0.40 is 1.97× the ceiling, not the 2.27× the first draft claimed
against the within-stroke figure alone.** The band is **not** widened to restore the
larger-looking margin — inflating a band after computing its margin is precisely the move a
pre-registration exists to prevent. A factor of 1.97 over an analytic ceiling stands on its
own, and the residual sensitivity is recorded in §11 A-3.

**C-N1 is the guard on all of this.** The attached-flow fixture contains the 0.0273
cross-stroke gap in full, at every α, and the reader must still report **G2 does not fire**
on it. That is the discrimination test (charter §2c) doing work no threshold argument can do
alone.

**The reader must REPORT, for the firing pair:** the sign of `dα/dt` at `i` and at `j`
(computed from the α column, not from the model), and hence whether the pair is
**within-stroke** (same sign) or **cross-stroke** (opposite signs), together with `α_i`,
`α_j`, `C_L,i`, `C_L,j` and both times. **A G2 PASS whose kind is not reported is
incomplete.**

#### G3's Courant limb, re-specified against OpenFOAM's own time-step controller

**The first draft's `max Co over W ≤ 1.05 × maxCo` is WITHDRAWN: it can refuse a healthy
run.** The reason is in the solver source, read on this box rather than recalled —
`/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/general/include/setDeltaT.H`
(the copy `pimpleFoam` includes; identical file also at `.../finiteVolume/lnInclude/`),
lines 36–53:

```
if (adjustTimeStep)
{
    scalar maxDeltaTFact = maxCo/(CoNum + SMALL);

    const scalar deltaTFact =
        Foam::min(Foam::min(maxDeltaTFact, 1.0 + 0.1*maxDeltaTFact), 1.2);

    runTime.setDeltaT(Foam::min(deltaTFact*runTime.deltaTValue(), maxDeltaT));
```

and its own Description, verbatim: *"Reset the timestep to maintain a constant maximum
courant Number. **Reduction of time-step is immediate, but increase is damped to avoid
unstable oscillations.**"*

**Three properties follow, and the re-specification rests on all three:**

1. **`CoNum` is lagged, and the achieved Courant number is never clipped.** `CoNum` is
   computed from the flux field *before* the step, and `deltaT` is chosen so the *next* step
   would land at `maxCo` **if the velocity field did not change**. When the flow accelerates
   during a step — which is exactly what stall onset is — the Courant number actually
   realised exceeds `maxCo`. Nothing here prevents that; the code only sets the next
   `deltaT`. **A few-percent overshoot after an acceleration is the controller working as
   designed**, and PIMPLE is implicit, so a modest overshoot is not a stability event.
2. **Reduction is immediate and undamped.** When `CoNum > maxCo`, `maxDeltaTFact < 1`, so
   `deltaTFact = maxDeltaTFact` and the *full* corrective factor applies at once. **A
   healthy controller therefore cannot remain above the threshold for many consecutive
   steps.**
3. **Growth is damped** to at most ×1.2 per step and ≈ ×1.1 near equilibrium (the
   `1.0 + 0.1*maxDeltaTFact` limb), so after a correction the solver re-approaches `maxCo`
   from *below* over several steps. Routine overshoots are consequently **isolated single
   steps followed by immediate recovery**, not runs.

**Re-specified G3 Courant limb — verbatim, as it will be graded:**

> **NOT A RESULT if ANY of the following holds over the analysis window `W`:**
> **(a) any step has `Co > 2.00 × maxCo`;**
> **(b) more than 1.00 % of the steps in `W` have `Co > 1.05 × maxCo`;**
> **(c) any run of 5 or more CONSECUTIVE steps has `Co > 1.05 × maxCo`.**
>
> **REPORTED ALWAYS, whatever the verdict:** the maximum `Co` in `W` with the time and step
> index at which it occurred; the count and the fraction of steps in `W` above
> `1.05 × maxCo`; and the length of the longest consecutive run above `1.05 × maxCo`.

##### What the reader actually grades, and why the series is offset by one step (Revision 2)

**The `Co` series above is the `Courant Number mean: … max: …` line the solver prints at the top of
each step, and nothing else.** This is registered explicitly because it is the only Courant figure
`pimpleFoam` produces and because it does **not** mean what its position on the page suggests. Read
from the installed source on this box:

- `/usr/lib/openfoam/openfoam2606/applications/solvers/incompressible/pimpleFoam/pimpleFoam.C:132–135`
  — inside `while (runTime.run())`, the order is `#include "CourantNo.H"` → `#include "setDeltaT.H"`
  → `++runTime`. **The Courant line is printed before the step it precedes is taken.**
- `/usr/lib/openfoam/openfoam2606/src/finiteVolume/cfdTools/incompressible/CourantNo.H:44–50` —
  `CoNum = 0.5*gMax(sumPhi/mesh.V())*runTime.deltaTValue()`, computed from **`phi` as the previous
  step left it**, and printed as `Info<< "Courant Number mean: " << meanCoNum << " max: " << CoNum`.

**Consequence, registered as the reading rule:** the value on the line printed at loop iteration `n`
is a **lagged** figure — the flux field *before* step `n`, times the tentative `deltaT` standing
before that iteration's `setDeltaT` adjusts it. **The Courant number actually realised by step `n`
is therefore observed on the line printed at iteration `n + 1`**, not on the line that sits above
step `n`'s own `Time =` banner. The three limbs (a), (b), (c) are applied to **that logged series
over `W`, one value per step**, with the series shifted by one step so that each value is attributed
to the step whose realised flux produced it, and the reader **prints the offset it applied** so the
attribution is auditable rather than implicit.

**Two exact consequences for counting, both derived from the source rather than assumed:**

1. **`CourantNo.H` is included TWICE before the time loop** — `pimpleFoam.C:107` and again at `:114`
   inside `if (!LTS)`, which is the branch this run takes (`LTS` is false; no `setRDeltaT`). So the
   log carries **two pre-loop Courant lines** at the `t = 0` state, before any step exists.
2. **The last step's realised Courant number is never printed.** The final loop iteration prints its
   line, advances to `endTime`, solves, and the loop exits — there is no iteration `n_steps + 1` to
   report the flux that final step produced.

**Registered count assertion — a FOURTH count, stated in its derived form, with the reason it is not
a bare equality (this brief asked for the equality "or a statement of why not"; this is the why):**

> `count(lines in log.pimpleFoam matching '^Courant Number mean:') == n_steps + 2`, exactly.
>
> The `+ 2` is **derived** from `pimpleFoam.C:107` and `:114`, not fitted. A naive
> `count(Courant lines) == count(steps)` is **false by construction** and would fire on every healthy
> run, which is the same defect Revision 1 withdrew the `1.05×` hard limit for. **The reader asserts
> the `n_steps + 2` form and refuses (exit 2) on any other count**, since a deficit means a truncated
> log and a surplus means a restart collision or a second solver writing into the same log.
>
> **The regular expression is anchored at the start of line and this is load-bearing.** `pimpleFoam`
> also prints `Mesh Courant Number mean: …` (`meshCourantNo.H:49`, reached at `pimpleFoam.C:164–166`
> when `checkMeshCourantNo` is set). An unanchored `grep 'Courant Number mean:'` matches **both**,
> and on a moving-mesh case that is exactly the run where the second string can appear. The anchored
> form is registered; the reader also **counts the `Mesh Courant` lines separately and reports the
> count**, so a non-zero one is visible rather than silently folded in.
>
> **Graded steps in `W`:** the offset costs the window its final step — `count(graded Co values in W)
> == count(steps in W) − 1` — and the reader **states that one step, out of ≈ 30,850, is
> unobservable and names it**, rather than quietly grading `n − 1` values against a limb phrased
> over `n`. Limb (b)'s fraction is taken over the graded count, and the reader prints both counts.

**Justification, with derived and judgement limbs kept apart:**

- **(a) `2.00 ×` — DERIVED from property 1.** The realised Courant number overshoots only in
  proportion to the velocity increase *within a single step*, so `Co > 2 maxCo` means the
  local velocity magnitude more than doubled inside one time step. At `maxCo = 1` on a
  3,584-cell mesh that is not a physical acceleration; it is a divergence or a mesh-motion
  artifact, and a stall signature read under it cannot be told from the artifact.
- **(c) `5 consecutive` — DERIVED from property 2.** Because reduction applies the full
  factor `maxCo/CoNum` immediately, a controller tracking the flow recovers in ≈ 1 step in a
  settled flow and a small number under sustained acceleration. Five consecutive steps above
  threshold means the controller is chronically behind the flow — a different condition from
  an overshoot. **This is the sharpest of the three limbs** and the one that actually
  separates "routine overshoot" from "controller failure".
- **(b) `1.00 %` — JUDGEMENT, and labelled so.** Calibrated to the pattern properties 2–3
  imply (isolated single-step overshoots), not derived from the source. At the expected
  ≈ 30,850 steps per period it permits ≈ 308 isolated overshoots. It is the weakest limb and
  is retained only as a population-level backstop behind (c). Its arbitrariness is recorded
  in §11 as **A-9**.

**Consistency with the §2a self-declaration below:** the self-declaration says a numerical
instability could manufacture both the G1 and G2 signatures, and that G3 is what stands
against that. **Limbs (a) and (c) carry that load.** The withdrawn `1.05×` hard limit never
did — it would have fired on healthy runs and then been relaxed under pressure, which is how
a gate becomes decorative.

**Reported beside the gate, never gated on** (charter §2a: reporting an identity is
encouraged, gating it is forbidden): `A_L` split into `A_up` and `A_down`; `C_L,max` and the
α at which it occurs; `C_L,min`; the number of samples in `W`; `A_att` itself; `α(t)` from
E2's `alpha_deg()` (an **identity** — it is the prescribed motion recomputed from the
registered constants and cannot fail).

**The §2a self-declaration, in the gate's own text:**

- *This gate fails if* the solve produces a loop area below 2.00 C_L·deg (G1), or produces
  no C_L excursion larger than attached-flow theory permits over any admissible pair (G2),
  or fails any completion or control clause (G3).
- *A wrong treatment could still pass it by* producing an open loop and a sharp C_L drop for
  a reason that is not dynamic stall — a numerical instability, a mesh-motion artifact, or a
  Courant excursion can each manufacture both signatures. **Which is why G3 gates the
  Courant number, why §4 requires the attached-flow negative control to be *rejected* by the
  reader, and why the label ceiling in §6 forbids this rung from claiming the loop is
  quantitatively right.** The rung claims the mechanism is present; it does not claim it is
  the right mechanism at the right magnitude, and that distinction is the whole content of
  the ceiling.

### Field 4 — the reference, in the vocabulary of `VERIFICATION_CHARTER.md` §6b

> **`NOT OBTAINED` — NASA TP-1100.**

1. **What is missing.** McAlister, K. W., Carr, L. W., McCroskey, W. J., *"Dynamic Stall
   Experiments on the NACA 0012 Airfoil,"* NASA TP-1100, January 1978 (NTRS 19780009057).
   Neither a PDF nor a `.txt` sidecar exists anywhere on this box.
2. **Which rung or row it blocks.** The F5b **Gate** rung (quantitative comparison against
   case (e)), which stays **PENDING** with this reference **NOT OBTAINED**. It does **not**
   block the Physics rung registered here — by construction, every limb above reads the
   run's own output against a reference derived in §2.
3. **Why it was not obtained, with the availability check named and dated.** Checked
   2026-08-24T16:25:35Z by filename search (`find docs/papers` and `find /home/ubuntu -maxdepth 6` for
   `*mcalister*`, `*tp1100*`, `*19780009057*`) and by content grep (`grep -ril mcalister`
   over the repository): **seven prose mentions, zero artifacts** — E1, E2, E7,
   `NEXT_CASES_SLATE.md`, `CHALLENGE_SLATE_2026-08.md`, `research/agenda/docket.json`,
   `sdk/tests/fixtures/absolute_claims_labelled.json`. E1:260 and E2:3–5 both state the
   report was *"downloaded and parsed directly (OCR text of the primary source)"* on
   2026-07-28/29. **That artifact is not on disk, so the claim is `unreconstructible`
   (charter §9's word), not `unsupported`** — the record may well be true and the file may
   simply have been lost with the scratch tree. **`CLAUDE.md` rule 15 (title-page
   verification) cannot be performed on a file that does not exist, so no number attributed
   to TP-1100 may be used as a datum by this lab today.**
4. **Acquisition path and price.** NTRS 19780009057 is public domain and openly
   downloadable: retrieval + `pdftotext` sidecar + title-page verification = **zero compute,
   $0**. **Even then the Gate rung stays qualitative**: E1:270 and E2:18–30 both record that
   TP-1100 gives **no** machine-readable C_L(α) series for case (e) — only scanned
   strip-chart figures and report-*wide* extreme bounds across the whole test matrix
   (`C_p = −30, C_L = 3.5, C_D = 1.5, C_M = −0.75`, stall delay up to `Δ(ωt) = π/2`). A
   point-match Gate additionally needs **digitisation of the published hysteresis loops** —
   already listed at E7:616 as zero-compute work.

---

## 3. The configuration

**One run. One arm. Exactly one change from the Feasibility rung: `end_time` 1.0 → 21.9440.**
Every other parameter is the Feasibility rung's value, unchanged, so the cost basis in §8
stays comparable and the change that produced any difference is unambiguous.

| item | value | source |
| --- | --- | --- |
| Run directory (**must not exist at freeze**) | `verification/runs/F5b_runs/physics_p1/` | this document |
| Case directory the driver creates | `verification/runs/F5b_runs/physics_p1/case/` | E2 `run_case` |
| Driver | `python3 verification/runs/F5b_runs/run_pitch.py --level coarse --out verification/runs/F5b_runs/physics_p1 --end-time 21.9440 --dt0 0.002 --max-co 1.0 --timeout 4200` | E3 |
| Mesh | NACA_LEVELS `coarse` (`113x33`): nx_total = 4×16 + 2×24 = 112, ny = 32 → **3,584 cells**; farfield 25 c, wake 25 c, first cell 8×10⁻⁶ c | E4, E2 |
| Solver | `pimpleFoam`, incompressible, moving mesh, `kOmegaSST`, preceded by `blockMesh`, `checkMesh`, `potentialFoam -writephi` | E2 |
| Motion | `dynamicMotionSolverFvMesh` + `solidBody` + `oscillatingRotatingMotion`, whole mesh, origin (0.25, 0, 0), axis (0,0,1), ω = 0.3, amplitude (0,0,10) | E2 |
| Incidence | mean 15° by freestream vector (**fixed in the lab frame**); ±10° by mesh rotation; net α(t) = 15 + 10 sin(0.3 t) | E2 |
| **Force resolution** | `liftDir = (−0.25881905, 0.96592583, 0)`, `dragDir = (0.96592583, 0.25881905, 0)`, `U_inf = (0.96592583, 0.25881905, 0)`. **`liftDir · Û = 0.0` and `dragDir · Û = 1.0`, exactly** — the `Cl` column is a **true C_L**, not a `C_y`; no `cos 15°` factor applies. See §2 | E2:88–91, E4 |
| `forceCoeffs1` normalisation | `magUInf 1.0`, `lRef 1.0`, `Aref 1.0`, `rho rhoInf`, `rhoInf 1.0`, `patches (airfoil)`, `pitchAxis (0 0 1)` | E4 |
| **`CofR`** | **`(0 0 0)` — the origin, NOT the quarter-chord pivot, and it does not move with the mesh.** Affects **C_M only**, which **this rung does not gate**. Recorded so no later reader mistakes this run's `Cm` column for a quarter-chord moment | E4 |
| Re / ν | 2.5×10⁶ / 4×10⁻⁷ | E2 |
| `endTime` | **21.9440** = 1.0 + T rounded up (T = 20.943951024); gives `t₁ = 21.9440 − T = 1.000049 ≥ 1.0` | derived, §2 |
| `deltaT` / `adjustTimeStep` / `maxCo` / `maxDeltaT` | 0.002 / yes / 1.0 / `endTime`/200 = 0.109720 | E4, E2 |
| Write control | `adjustableRunTime`, `writeInterval = endTime`, `purgeWrite 1` → **exactly one written time directory, at `endTime`**; no intermediate fields | E4 |
| Time-resolved evidence | `postProcessing/forceCoeffs1/*/coefficient*.dat`, written every time step | E4 |
| **nProcs** | **1 (serial).** No `decomposePar`, no `mpirun` | see below |
| Predicted wall | 1,730–2,880 s (§8) | §8 |

**Why nProcs = 1.** (a) 3,584 cells over N ranks is far below any useful partition — the
halo exchange would dominate. (b) The Feasibility basis is serial, and running this arm in
parallel would break the only cost basis that exists (§8) while also violating the
one-change-per-run rule. (c) E1:6 records the whole F5b/F5c family as deliberately serial:
*"all runs single-rank (serial) … No run used more than 1 core."* Core-minutes = wall
seconds ÷ 60 for this arm.

### Pre-launch assertions — all in ONE shell invocation, immediately before launch

1. `test ! -e verification/runs/F5b_runs/physics_p1` — **refuse (exit 2) if it exists.**
2. `git status --porcelain` over E2, E3, E4, E5 is **empty**, and their md5s equal the values
   frozen in §1. A non-empty diff **stops the launch**; it is inspected, never reverted
   (rule 10).
3. `git rev-parse HEAD` recorded into the run directory as `LAUNCH_HEAD.txt`, and the frozen
   pre-registration blob hashed against this file (rule 2: *verify the frozen file is the
   file that ran*).
4. `uptime` recorded into `LAUNCH_LOAD.txt` — the load the run actually started at, so the
   §8 close-out can attribute contention. **This is the C-4 calibration lesson**
   (`docs/COST_CALIBRATION.md`, row C-4: *"record the load average beside any per-iteration
   cost basis, and state the load the basis is being re-applied at"*), applied at the launch
   end as well as the basis end.
5. **Lever echo.** Before `pimpleFoam` starts, `cat` `system/controlDict`,
   `system/fvSolution`, `system/fvSchemes`, `constant/dynamicMeshDict`,
   `constant/transportProperties` and `constant/turbulenceProperties` into `log.levers`.
   **Adopted voluntarily from F5c's binding instrumentation ruling** (E1:126–140: *"THE
   SWITCH YOU SET IS NOT THE SWITCH THAT RAN … cat `fvSolution` into the run log at
   launch"*). That ruling binds the F5c unsteady-probe arm; it is taken here because the
   failure it prevents is identical.

### `levers_verified_active` (charter §9) — declared in advance

| lever | how activity will be proved | status if unprovable |
| --- | --- | --- |
| `dynamicMotionSolverFvMesh` / `solidBody` / `oscillatingRotatingMotion` | the `Selecting dynamicFvMesh` and solid-body-motion-function selection lines in `log.pimpleFoam` | — |
| `kOmegaSST` | `Selecting turbulence model type RAS` + `Selecting RAS turbulence model kOmegaSST` in `log.pimpleFoam` | — |
| `adjustTimeStep` / `maxCo 1.0` | the varying `deltaT = ` and `Courant Number mean/max` lines | — |
| `potentialFoam -writephi` prestart | `log.potentialFoam` rc 0 with an `End` line, written before `log.pimpleFoam` exists | — |
| **`pcorr` / `pcorrFinal` solver blocks** | **no log line echoes which `fvSolution` entry the moving-mesh flux correction used** | **`unverifiable-from-logs`.** Carried as a caveat on the face of any finding that cites the flux correction. `log.levers` proves what was *set*, not what *ran* |

### Known defects in the shipped code, disclosed before freeze

| id | defect | mitigation registered here |
| --- | --- | --- |
| **D-1** | `pitching_airfoil_case.run_case` (E2:247–248) does `shutil.rmtree(case)` when the case directory already exists. That is the **opposite** of `CLAUDE.md` rule 4's guard, which requires a **refusal** when `0` or a time directory already exists — it destroys the evidence the guard exists to protect | The launch wrapper asserts non-existence and **refuses (exit 2) before `run_case` is ever called** (assertion 1 above). **E2 is not edited** — it is shared code used by nothing else today but owned by the module, and editing it is a separate docket item, not a side effect of this rung |
| **D-2** | `run_case` raises `RuntimeError` on a non-zero `pimpleFoam` rc and writes no `record.json`. A timeout kill therefore leaves the run tree without its summary | Accepted, and turned into evidence: the completion rule (§5) reads `log.pimpleFoam` directly, not `record.json`, so a killed run is gradeable as **NOT A RESULT** from the log alone |
| **D-3** | E3's `--timeout` **defaults to 1800 s**, which is **below** the 1,730–2,880 s wall this arm is predicted to need. Launching on the default would kill a healthy run mid-march and manufacture a false NOT A RESULT | `--timeout 4200` is registered explicitly in the command line above, and the launch assertion set includes an echo of the resolved timeout into `LAUNCH_CMD.txt` |

---

## 4. Positive controls (`CLAUDE.md` rule 3)

> **A zero from a reader not shown able to see a non-zero is not evidence.** The reader
> plants known perturbations into a **copy** of the run's own output, by line index, reads
> them back from disk with the same code path that grades, and **refuses (exit 2)** if it
> cannot see them.

The run's own output is never modified. Copies live under
`verification/runs/F5b_runs/physics_p1/controls/`.

| id | control | plant | pass condition | on failure |
| --- | --- | --- | --- | --- |
| **C-P1** | **Loop-area reader sees a non-zero, and sees the RIGHT non-zero** | Copy `coefficient*.dat` → `controls/coeff_plant_area.dat`. Add `PLANT_CL` to the `Cl` column at **one** data line, index `i*` chosen by the deterministic rule below. Nothing else touched | The **two-sided** assertion below: the measured area shift must match the *predicted* shift, and the predicted shift must be visible above `σ_quad` | **refuse, exit 2** |
| **C-P2** | **Collapse detector (G2) can fire** | Copy → `controls/coeff_plant_collapse.dat`. Over a contiguous block of **40 data lines** chosen inside `W` where `\|Δα\| ≤ 2.00°`, replace the `Cl` column by a linear ramp falling by `PLANT_DROP = 0.60` across the block | G2 fires on the planted copy, and the reader reports the planted pair's indices | **refuse, exit 2** |
| **C-N1** | **Negative control — the attached-flow fixture, and this is the §2c discrimination test** | A synthetic `coefficient.dat` generated **before compute** from the §2 Theodorsen expression at k = 0.15, α_a = 10°, quarter-chord axis, over one period at 4,096 samples, in the exact column layout the real file uses. Committed as `verification/runs/F5b_runs/controls/theodorsen_attached_fixture.dat` with its generator `make_theodorsen_fixture.py` **at the freeze commit**, because no prior artifact exists to plant into | The reader, run unmodified on the fixture, must (a) return `A_L = 0.429 ± 0.005 C_L·deg`, (b) report **G2 does NOT fire**, and (c) report the fixture's largest admissible-pair `ΔC_L` as **≈ 0.203** — i.e. it must *see* the attached-flow excursion, including its 0.0273 cross-stroke gap, and still correctly place it **below** the 0.40 band. **A reader that scores the attached-flow fixture as dynamic stall is broken and its verdict on the real run is void; a reader that reports 0 for (c) has not looked** | **refuse, exit 2** |
| **C-P3** | **The reader is reading THIS run's file** | The reader records the md5 and mtime of the exact `coefficient*.dat` it parsed, and asserts that path lies inside `physics_p1/case/postProcessing/` | mismatch → **refuse, exit 2** | **refuse, exit 2** |

#### C-P1 in full: a plant whose effect is PREDICTED, not merely detected

A single-sample plant of `PLANT_CL` at data index `i` shifts a trapezoid loop area by an
**exactly computable** amount, because the trapezoid rule gives that sample the weight of
half of each neighbouring interval:

```
ΔA_pred = PLANT_CL × (α_{i+1} − α_{i−1}) / 2          [α in degrees]
```

**The assertion is two-sided**, and both sides must hold or the reader refuses (exit 2):

1. **Correctness** — `|A_L(planted) − A_L(original) − ΔA_pred| ≤ σ_quad`.
   A reader that sees *a* change but the *wrong* change is as broken as one that sees
   nothing; the first draft's one-sided "differs by more than 10 σ_quad" would have passed
   such a reader.
2. **Visibility** — `|ΔA_pred| > 10 σ_quad`.
   A plant below the quadrature error proves nothing about the reader.

> **Revision 2 item (6) — a declared round-off floor under limb 1's tolerance, and it is
> declared because it is a departure from the sentence above.** Limb 1 is implemented as
> `|…| ≤ max(σ_quad, 10⁻⁹ × max(|A_L|, |ΔA_pred|, 1))`. `σ_quad` is a **quadrature** error; on a
> smooth loop sampled densely enough it can collapse toward double-precision round-off, at which
> point `≤ σ_quad` is an assertion about IEEE-754 arithmetic rather than about the reader, and
> would **refuse on a healthy file** — the same defect Revision 1 withdrew the `1.05×` hard Courant
> limit for. The floor sits **nine orders of magnitude below the G1 band of 2.00**, so it cannot
> hide a reader that is actually wrong. **Measured on the C-N1 fixture at stage 1, the floor did
> NOT bind**: `σ_quad = 5.048×10⁻⁷` against an actual `|measured − predicted| = 2.19×10⁻¹⁶`, so
> the tolerance in force was `σ_quad` itself and limb 1 was satisfied by eleven orders of margin.
> The floor is registered as insurance against a denser sampling, not as a live relaxation.

`ΔA_pred` is computed **from the planted copy's own α column**, never from the analytic
motion — so the control tests the file the reader actually parses.

> **Revision 2 correction, and it is a defect being fixed, not a gloss.** `coefficient.dat` has
> **no α column** — its complete column set is enumerated in §2 (`Time Cd Cd(f) Cd(r) Cl Cl(f)
> Cl(r) CmPitch CmRoll CmYaw Cs Cs(f) Cs(r)`). **Read "the copy's own α column", here and at the
> `i*` rule below, as "the α series reconstructed sample-by-sample from the copy's own `Time`
> column" via E2's prescribed motion — an identity, not a solved quantity.** The property the
> control needs is preserved exactly: the series comes from the file the reader parsed, one value
> per parsed row, and cannot be tuned to the answer. Recorded as **A-10** in §11.

**Choice of the plant index `i*`, and a defect in the first draft corrected here.** The first
draft planted at "data-line index 100". That is wrong twice: index 100 sits at `t ≈ 0.07`,
**inside the excluded transient and outside the window `W`**, where it would shift `A_L` by
nothing at all; and even inside `W`, `(α_{i+1} − α_{i−1})` vanishes at the stroke reversals,
where the plant would be invisible by construction. **Registered rule instead:**

> `i*` = the index within `W` that maximises `|α_{i+1} − α_{i−1}|`, computed from the copy's
> own α column.

This is deterministic, is decided entirely by the **prescribed** motion (α(t) is an input,
independent of the solution), and therefore **cannot be tuned to the answer** — it maximises
plant visibility by construction, which is exactly what a control should do.

**Expected magnitude, so a reader of the record is not surprised that the plant looks
small.** At the Feasibility rate of ≈ 1,473 steps per unit time (E1:285) one period carries
≈ **30,850** steps, i.e. `Δt ≈ 6.8×10⁻⁴`. The largest per-step incidence change is
`α_a ω Δt = 10 × 0.3 × 6.8×10⁻⁴ ≈ 2.0×10⁻³ °`, so

```
ΔA_pred ≈ 1.234 × 2.04×10⁻³ ≈ 2.5×10⁻³ C_L·deg          (order 10⁻³)
```

against a G1 band of 2.00 C_L·deg. **The plant is ~800× smaller than the gate threshold and
that is fine** — C-P1 tests the reader's arithmetic, not the gate.

**`PLANT_CL` escalation ladder, pre-registered so no post-hoc tuning is needed.** If
visibility fails at the first value, take the next: `PLANT_CL ∈ {1.234, 12.34, 123.4}`, the
**smallest** for which `|ΔA_pred| > 10 σ_quad` holds. The reader reports which value it used.
This is legal after freeze because the selection depends only on `σ_quad` and the α spacing —
**never on `A_L` or on any gate quantity** — so it cannot move a verdict.

**Why C-N1 is not optional.** Charter §2c: *a row that grades a hypothesis separates it from
that hypothesis being absent.* The hypothesis is "dynamic stall occurred". The state in which
it is **absent** but every naive signature is still present is exactly attached flow with
phase lag. C-N1 is that state, built on purpose, and the gate must reject it. C-P1 and C-P2
prove the reader can see something; **C-N1 proves it can tell the difference.**

**`ran_before_found` (charter §9).** Every control emits `RAN=yes/no` before `FOUND=…`, and
a control that did not execute reports **unknown** — never collapsed into a failure, never
into a pass.

---

## 5. Completion rule (`CLAUDE.md` rule 4) — all of it, or the run is not done

A single clause failing makes the run **NOT A RESULT**. The reader **refuses (exit 2) rather
than degrading**.

| # | clause | this rung's concrete form |
| --- | --- | --- |
| 1 | `rc = 0` | `pimpleFoam` returned 0 (and `blockMesh`, `checkMesh`, `potentialFoam` before it) |
| 2 | an `End` line | `log.pimpleFoam` contains a final `End` |
| 3 | **last time == `endTime`** | the last `Time = ` in `log.pimpleFoam` equals **21.9440**, compared at `timePrecision 8` / `writePrecision 10` (E4) |
| 4 | fields present | `case/21.9440/` contains **`U`, `p`, `k`, `omega`, `nut`** — the field set this case actually writes (E2 `initial_fields`). **The thermal family's `T U p_rgh alphat nut k omega` list does not apply here and is not silently reused.** `phi` and the `yPlus1` output are reported if present and **not gated**, because I have not verified on disk that this configuration writes them |
| 5 | `ExecutionTime` count | **Adapted clause, and the adaptation is declared.** The thermal form (`ExecutionTime` count == `endTime`) assumes one write per unit time and is meaningless under `adjustTimeStep`. The form registered here: **count(`ExecutionTime = ` lines in `log.pimpleFoam`) == count(data lines in `coefficient*.dat`) == `n_steps` in `record.json`** — three independent counts of the same time steps, which must agree exactly. `n_steps` is the `record.json` key written at **E2:306** (`sdk/workflows/pitching_airfoil_case.py:306`, `"n_steps": len(times)`). **Revision 2 adds a FOURTH count to this clause:** `count('^Courant Number mean:' lines in log.pimpleFoam) == n_steps + 2`, the `+ 2` **derived** from `pimpleFoam.C:107` and `:114` (§2) and the regex **anchored** so `Mesh Courant Number mean:` cannot be counted into it. A disagreement in any of the four means a truncated log, a renamed coefficient file, a restart collision or a second writer, and is **NOT A RESULT** |
| 6 | **age guard** | every file in `case/21.9440/` strictly newer (mtime) than **`max(mtime)` over `case/0/*`**. The max is taken over the whole `0/` directory rather than one named file, so the guard cannot be defeated by a change in write order. Separately **reported**, not gated: whether the argmax is `0/nut` (E2 writes `U, p, k, omega, nut` in that order, so `0/nut` is expected last) |
| 7 | pre-existing-state guard | the launch refuses if `physics_p1/` exists at all (§3 assertion 1, D-1) |
| 8 | cap guard | wall time ≤ 4,200 s (driver timeout) and cost ≤ the §8 cap. **An overrun stops the run; it does not get a new budget** (rule 12) |

### Unsteady-statistics clauses, pre-declared as this brief requires

**Statistics window.** `W = [t₁, t_end]`, `t₁ = t_end − PERIOD` computed in the reader from
E2's `PERIOD` constant, asserted `t₁ ≥ 1.0`. Exactly **one full period**, ending at
`endTime`. The transient exclusion is the E1-declared window (the impulsive-start spike
occupies the first ~0.02 time units; C_L is physically sane by t = 1); `t₁ = 1.000049`
excludes it with margin.

**Sampling-error estimate — two figures, reported separately and never merged.**

1. **`σ_quad` — the reader's own quadrature error.** `σ_quad = |A_L(every sample) −
   A_L(every 2nd sample)|`, a Richardson-style estimate of the trapezoid error on the
   measured sample spacing. This **is** the error bar on `A_L`, and it is what C-P1's
   threshold is scaled against. Cost: zero, it is a second pass over the same array.
2. **`δ_close` — the periodicity deficit.** `δ_close = |C_L(t_end) − C_L(t₁)|`: the loop's
   own failure to close. **This is NOT an error bar and is never quoted as one.** It
   measures how far the flow is from a periodic limit cycle after one covered period, which
   is a physical statement about the run, not an uncertainty in the reading. It is reported
   beside `A_L` on the face of the result, and it is the single number that says how much
   the §6 label ceiling is actually costing.

**What is deliberately NOT claimed.** No cycle-to-cycle repeatability figure, because only
one period is covered and a repeatability estimate needs at least two. Any statement of the
form *"the loop has converged"* is **outside this rung's entitlement** regardless of what
`δ_close` turns out to be.

---

## 6. Roache triple gating (`CLAUDE.md` rule 5) — and the label ceiling in its place

> **This rung is SINGLE-GRID. There is no grid triple, no Richardson extrapolation, no
> observed order and no GCI. Rule 5 is therefore not applicable, and no GCI figure will be
> printed — a GCI quoted without three monotone values is forbidden by that rule and none
> exists here.**

**The ceiling this buys, stated explicitly, because a single-grid rung cannot claim more
than the Feasibility mesh supports:**

1. **No discretisation-error claim.** Nothing from this rung may be quoted as converged,
   grid-independent, or asymptotic. `A_L`, `C_L,max` and the collapse magnitude are values
   **on the 3,584-cell coarse mesh**, and every one of them travels with that qualifier
   attached (charter §6a — the referent travels with the verdict).
2. **No quantitative comparison to TP-1100**, on two independent grounds: the reference is
   **NOT OBTAINED** (§2 field 4), *and* the mesh has no error bar. Either alone is
   sufficient.
3. **No cycle-convergence claim** (§5).
4. **A PASS here means the mechanism is present, and nothing more.** It does not license the
   Gate rung; the Gate rung is blocked by its reference, not by this rung's outcome.
5. **The hard ladder rule (charter §3) applies downstream**: a GATE FAIL here blocks the
   Gate rung as well, on top of its existing block.

**The path to a Roache-gated F5b rung, priced so nobody re-derives it by spending.** E4's
`NACA_LEVELS` already supplies the triple: coarse **3,584**, medium `225x65` → 4×32 + 2×48 =
224 × 64 = **14,336**, fine `449x129` → 4×64 + 2×96 = 448 × 128 = **57,344** cells — a clean
refinement ratio of 2 in each direction. At a naive cell-count-times-timestep-count scaling
that is roughly **4×** and **16×** the coarse arm's cost respectively (and more, since the
Courant-limited Δt falls with the cell size), i.e. of order **500+ core-minutes** for the
triple against this arm's 35. **That is a different registration with a different cap and it
is not attempted here.** The naive scaling is an estimate, not a measurement, and is labelled
so.

---

## 7. Pre-declared outcome map

Written before any compute exists. Every label is from `CLAUDE.md` rule 1's fixed
vocabulary; no other word may be used to report this rung.

| # | condition | verdict | what is written |
| --- | --- | --- | --- |
| 1 | §5 completion all clauses hold; §4 controls all pass **including C-N1**; **G1 PASS and G2 PASS** | **`PASS`** | Physics rung established: the dynamic-stall mechanism is present on the Feasibility mesh. `A_L ± σ_quad`, `δ_close`, `C_L,max` and its α, the collapse pair, all with the §6 ceiling attached, and `A_att = 0.429` beside them |
| 2 | §5 and §4 hold; **G1 or G2 outside band** | **`GATE FAIL`** | Physics rung **not** established. Shipped as a documented failure under charter §8, never re-posed to fit the answer (L-44). The measured values are printed in full beside the bands they missed |
| 3 | Any §5 clause fails — rc ≠ 0, no `End`, last time ≠ 21.9440, a field missing, the three step counts disagree, or the age guard fires | **`NOT A RESULT`** | The failing clause is named. **The gate is not evaluated**, and no partial `A_L` is quoted — charter §2: *a gate that was not reached is stated as not reached, never replaced by a nearer gate that was* |
| 4 | Any §4 control refuses (exit 2) — **especially C-N1, the reader scoring attached flow as stall** | **`NOT A RESULT`** | The reader is declared broken, the run's numbers are withheld entirely, and the reader defect is a docket item |
| 5 | Courant condition: **any** step with `Co > 2.00`, **or** > 1.00 % of steps in `W` above `Co = 1.05`, **or** ≥ 5 consecutive steps above `Co = 1.05` (`maxCo = 1.0`) | **`NOT A RESULT`** (G3) | The max `Co` with its time and step index, the count and fraction above 1.05, and the longest consecutive run are reported **whatever the verdict**. A stall signature read under a genuine Courant failure cannot be told from a numerical artifact — but a few-percent single-step overshoot is the controller working as designed and does **not** void the run (§2) |
| 6 | The run exceeds the §8 cap, or the 4,200 s driver timeout fires | **`NOT A RESULT`** | **The run stops. It does not get a new budget** (rule 12). The record states the cap stopped it and the partial log is retained as the evidence of what was reached |
| 7 | The Gate rung (quantitative vs TP-1100) | **`BLOCKED`** — reference **`NOT OBTAINED`** | Unchanged by any outcome above. §2 field 4's four fields travel with it |
| 8 | The run is not launched (capacity goes to R4 / the thermal spine) | **`PENDING`** | The board row keeps `PENDING: verification/campaign/F5b_PHYSICS_PREREGISTRATION.md`. `PENDING` is a queue state and is never used to soften a `GATE FAIL` (rule 1) |

---

## 8. Cost (`CLAUDE.md` rule 12)

**Unit: core-minutes = wall seconds × ranks ÷ 60. Ranks = 1 (§3).**

### The basis, and its honesty label

| basis | derivation | figure | label |
| --- | --- | --- | --- |
| **A — Feasibility scaling** | E1:285: *"1,473 steps, 85.1 s wall (coarse mesh, single core)"* for the span t ∈ [0, 1]. Scaled linearly to t ∈ [0, 21.9440]: 85.1 × 21.944 = 1,867 s = **31.1 core-min** | 31.1 core-min | **record-quoted, artifact-missing.** No F5b run tree, log or `record.json` survives anywhere on the box (§1). This is a figure read from a markdown record, not from a log. It is also a **lower bound**: Δt is Courant-limited and falls once the flow separates, so steps-per-unit-time rises after stall onset |
| **B — the record's own unsteady/steady ratio** | E1:292: the one-period run *"is running roughly **15–25× longer in wall-time** than the comparable steady BFS coarse run (115 s)"*. Using E1:62's F5c coarse row, 115.3 s: 15× = 1,730 s = 28.8 core-min; 25× = 2,883 s = 48.0 core-min | **28.8 – 48.0 core-min** | **record-quoted, artifact-missing** on both ends — the F5c coarse log is also gone (E1:130–132: *"the six original diagnostic runs' solver logs were never archived"*) |

### Registered figures

| item | value |
| --- | --- |
| **Point estimate** | **35.0 core-min** (inside basis B's band, above basis A's lower bound; consistent with the board's ≈25–35 core-min at `docs/LAB_STATE.md:555`) |
| **Band** | **28.8 – 48.0 core-min** (basis B) |
| **RUN CAP** | **72.0 core-min** = 4,320 wall s at 1 rank. **Headroom: 1.50× the band's upper end (+24.0 core-min above 48.0), 2.06× the point estimate.** Chosen because both bases are record-quoted with no surviving artifact and basis A is known to be a lower bound; the cap must survive being wrong in the expensive direction, once |
| **Stop mechanism** | `--timeout 4200` (70.0 core-min) fires **inside** the cap, so the driver stops the solver before the registered ceiling is crossed. **An overrun stops the run; it does not get a new budget** |
| **Rate** | **$0.0513 / core-h**, c7a.4xlarge — **reported-by-owner, NOT measured.** The box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **Dollars at the point estimate** | 35.0 core-min = 0.58333 core-h × $0.0513 = **$0.0299 — derived, not measured** |
| **Dollars at the cap** | 72.0 core-min = 1.20000 core-h × $0.0513 = **$0.0616 — derived, not measured** |
| **Authorisation** | Under the $25 pre-authorisation and inside Sanaa's 2026-08-21 blanket. **A blanket is not a per-item read** (rule 9): this is the item's own cap, not a new ceiling, and it does not license a second run |

### Load averages — both ends, because a per-unit cost basis without its load is uncalibratable

| when | load (1/5/15 min) | note |
| --- | --- | --- |
| **At the basis measurement** | **NOT RECORDED** | E1 gives contention only qualitatively: *"sharing the box with a running mega-batch and three other agents"* (E1:6). No load number exists in the record. **This is precisely the C-4 finding** (`docs/COST_CALIBRATION.md` row C-4: a per-iteration basis measured at load ~19.5 was re-applied at load 5.03 and over-charged the quiet box by 1.56×). Here the direction is favourable — a contended basis re-applied on a quieter box should come in **under** — but the magnitude is **not derivable**, and it is not claimed |
| **At drafting** | **3.44, 4.37, 4.60** | `uptime`, same shell invocation as this file's stamp |
| **At launch** | to be recorded | §3 assertion 4, into `LAUNCH_LOAD.txt` |

### Pre-committed cost close-out clause

**Binding on whoever grades this rung.** Committed here, before compute, so the comparison
cannot be skipped and cannot be shaped afterwards (rule 12's calibration bullet; Sanaa
2026-08-23, verbatim: *"for all teams involved once a process is completed, the estimated
costs must be compared with the actual incurred costs so we can improve the lab's
estimates"*).

At rung completion — **PASS, GATE FAIL or NOT A RESULT alike; a stopped run is costed too** —
the grader writes, into the results record and then as **one appended row** in
`docs/COST_CALIBRATION.md`:

1. **Predicted**: 35.0 core-min (band 28.8–48.0; cap 72.0), citing this file's frozen sha.
2. **Actual gross**, in core-minutes, **measured from the log** — the last `ExecutionTime =`
   in `log.pimpleFoam` plus the `blockMesh`/`checkMesh`/`potentialFoam` timings from
   `record.json`, × 1 rank ÷ 60. Not from memory, not from the driver's wall estimate if a
   log figure exists.
3. **Actual cleaned**, with the charter §2 meaning (gross minus rows the 3600-s stall rule
   matches). **This arm's predicted wall exceeds 3,600 s at the top of its band**, so the
   grader states explicitly whether the single solver row is a legitimate long serial solve
   or a stall — and says which, rather than letting the rule apply itself.
4. **Ratio** cleaned/predicted, and separately actual/cap.
5. **Gap attribution, with the three causes kept apart and never merged**:
   **contention** (from `LAUNCH_LOAD.txt` against the basis's `NOT RECORDED`, which will
   bound the attribution rather than measure it — and the row says so);
   **misprediction** (the basis being record-quoted and artifact-missing, and basis A being
   a lower bound by construction); and **waste**, which is **named separately, in its own
   sentence, with its own figure, and is never absorbed into the ratio or netted off either
   column** (`COMPUTE_BUDGET_CHARTER.md` §6). A killed, re-launched or mis-configured arm is
   waste and is reported as such even when the rung passes.
6. **Row landing.** Via `scripts/append_record.py --path docs/COST_CALIBRATION.md`, with the
   `C-` id **re-derived from HEAD content at commit time, in the same shell invocation as
   the commit** — the **maximum existing number, never a count** (rule 11) — and landed
   under the **rule-10 private-index protocol**: capture HEAD once, `read-tree`,
   `update-index` this path only, `diff-tree` assert only this path, `commit-tree`, CAS on
   `refs/heads/main`, **post-commit `git diff HEAD~1 HEAD --stat` verify**. Never a bare
   `git commit`, never `git add -A`.
7. **A completion report without this comparison is incomplete** and is returned.

---

## 9. Freeze condition

**The freeze is legal only while there is no answer to tune to** (charter §2b clause 1: the
amendment must *state the condition and how it was checked* — *"name the run directory that
does not exist"*).

**The run directory that must not exist:** `verification/runs/F5b_runs/physics_p1`

**Re-checked 2026-08-24T16:34:57Z, in the same shell invocation as this revision's stamp. Verbatim
output of `ls -la /home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1`:**

```
ls: cannot access '/home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1': No such file or directory
```

**And the whole F5b run tree, verbatim, same invocation** — `ls -la` followed by
`find … -type f`, so the quote shows both the directory listing and every file it contains
at any depth:

```
total 12
drwxrwxr-x  2 ubuntu ubuntu 4096 Aug 16 19:03 .
drwxrwxr-x 33 ubuntu ubuntu 4096 Aug 19 15:54 ..
-rw-rw-r--  1 ubuntu ubuntu 2272 Aug 18 05:45 run_pitch.py
```

```
/home/ubuntu/Certonomous/verification/runs/F5b_runs/run_pitch.py
```

**Re-checked a THIRD time at Revision 2, 2026-08-24T17:15:13Z, BEFORE any character of that revision
was written** — this is the check that makes Revision 2's in-place edits legal under `CLAUDE.md`
rule 2. The named directory is `verification/runs/F5b_runs/physics_p1`; the check was
`test -e /home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1`, which reported **ABSENT**,
alongside an `ls -la` of the F5b run tree showing the same single file `run_pitch.py` (2,272 bytes,
mtime Aug 18 05:45) as the two quotes above. **The check ran first and the edits followed; no compute
of any kind ran between them.** The lesson recorded below — never `&&`-chain a command whose non-zero
exit is the expected result — was applied: the existence test was written to report ABSENT as its
success path, not to short-circuit on it.

**Disclosure — this quote was EMPTY in the first draft, and the near-miss is recorded rather
than quietly repaired.** The first draft's capture shell chained its two `ls` calls with
`&&`. The first call targets a path that is **expected not to exist**, so it exited non-zero,
the `&&` short-circuited, and the second capture never ran — leaving the run-tree code fence
blank while the document around it asserted the condition had been checked. **A freeze
condition with an empty quote is not a checked condition**, and it is exactly the shape of
failure `CLAUDE.md` rule 3 exists for: a blank where evidence should be, produced by an
instrument that was never shown able to produce a non-blank. Caught by the supervisor's read,
before freeze. **Lesson for any capture shell in this lab: never `&&`-chain a command whose
non-zero exit is the expected result.**

**The freeze is a two-stage commit, both stages strictly before any compute**, which is how
charter §2d (*the comparator is frozen before its cases can answer it*) and this brief's
skeleton instruction are reconciled rather than traded off:

- **Stage 1** — this document, plus the reader **skeleton** (§10) with **every control of §4
  implemented and demonstrably passing on the C-N1 fixture**, and the grading bodies raising
  `NotImplementedError`. The point of stage 1 is that the controls can be *proved to work*
  before the grading logic exists to be tuned.
- **Stage 2** — the same reader with the grading bodies implemented against the bands frozen
  in §2, committed **before the run directory is created**. §2d's own enforcement test then
  passes by construction: *compare the comparator's commit timestamp against the earliest
  completion marker in its own run tree* — there is no marker, because there is no tree.
- **Then, and only then**, §3's pre-launch assertion block runs and the solver may start.

**If any compute has already touched `physics_p1/` when this is read, the freeze is void and
the document is closed to amendment** — changes then land only as dated addenda that cannot
alter a gate, threshold, cap or label (rule 2), and the originals are struck, never
rewritten.

---

## 10. The reader

**Path: `verification/runs/F5b_runs/analyse_f5b_physics.py`**
(with its fixture generator `verification/runs/F5b_runs/make_theodorsen_fixture.py` and the
fixture itself `verification/runs/F5b_runs/controls/theodorsen_attached_fixture.dat`).

**Binding parse rule (Revision 2).** The reader locates every quantity in
`postProcessing/forceCoeffs1/*/coefficient*.dat` **by header name** — `Time`, `Cl`, `Cd` — from the
file's own commented column-header line, and **never by column position**; it refuses (exit 2) if a
name is missing, duplicated, or if a data row's field count differs from the header's. §2 carries the
v2606 header layout quoted from the installed source, the full twelve-coefficient column order, and
the reason a positional reader would have graded this gate on `Cd(f)`. **Stage 1 confirms that layout
against `/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/forceCoeffs/` and the C-N1 fixture
is written in it**, so the rule is exercised before any real coefficient file exists.

**It will be committed as a frozen skeleton before any compute**, per §9 stage 1:

- **Implemented at stage 1** — every §4 control end to end: the C-P1 area plant by data-line
  index, the C-P2 collapse plant over a 40-line block, the C-P3 provenance assertion, the
  C-N1 Theodorsen fixture generator and the negative-control assertion; the `exit 2` refusal
  path for each; the `RAN=` / `FOUND=` reporting of charter §9's `ran_before_found`; the §5
  completion clauses 1–8; and the window/`σ_quad`/`δ_close` machinery of §5.
- **`NotImplementedError` at stage 1** — the grading bodies: `grade_G1()`, `grade_G2()`,
  `grade_G3()` and `emit_verdict()`. They are filled in at stage 2, still before compute,
  against the bands frozen in §2 and against nothing else.
- **Verified at analysis time**: the reader is hashed against its committed blob before it
  grades anything (rule 2, charter §2d — *a freeze that is claimed and not checked is a
  claim about intent*), and the hash is printed in the results record.
- **It refuses rather than degrades** (rule 4). There is no fallback path, no "best
  available" reading and no partial grade.

---

## 11. Guesses, open items, and what a supervisor must check before freeze

Stated plainly, because an honest gap is worth more than a confident guess.

| id | what | why it is a guess | how to close it |
| --- | --- | --- | --- |
| **A-1** | ~~**`A_att = 0.4290 C_L·deg` and `\|Z\| = 5.0476 /rad`**~~ **CLOSED** | Derived here from Theodorsen/Jones by this lane, cross-checked only **against itself** (closed form vs quadrature, 10 s.f.). `Im(Z)` is a near-cancellation of two terms of opposite sign, so it was the least robust number in the document | **CLOSED 2026-08-24 by the current supervisor session's independent numerical re-derivation** — the Jones approximation evaluated directly and a `numpy` brute force over **40,000 samples** of one period, run on this box in this session. **A previous closure of this item, credited in Revision 1 to a hand re-derivation by an earlier cfd supervisor session, is WITHDRAWN as an attribution: that session was terminated by the usage limit and its work cannot be verified by any reader of this file. It is replaced, not merely re-worded, by a route that can be re-run.** The re-derived values: `C(0.15) = 0.7819026 − 0.1798329i`; `Z = 5.0469847 + 0.0782415i`; `\|Z\| = 0.08809709 per deg`; `A_att = 0.42900727 C_L·deg`; G2's analytic supremum `0.2034845` against a brute-force `0.2033316` (stride-40 anchors, every sample searched against each anchor), correctly above it; cross-stroke max gap `0.0273115`. **Every figure §2 uses is reproduced to the digits §2 prints.** The split-terms hand route — circulatory `2πC(k)(1 + ik) = 5.0823 − 0.3928i`, non-circulatory `π(ik + ak²)` with `a = −1/2` = `−0.0353 + 0.4712i`, summing to `Z = 5.0470 + 0.0784i` — is kept because it re-forms the near-cancellation term by term rather than re-copying it, **but it is this lane's own working and is labelled as such, not the supervisor's**. The margin arguments (G1 4.66×, G2 1.97×) stand on a number checked by a route independent of the closed form that produced it |
| **A-2** | **G1's band of 2.00 C_L·deg** | A margin factor over `A_att`, chosen for robustness, **not** measured from any dynamic-stall dataset — because none is on disk | Either accept the margin argument on its face, or set the band from a digitised TP-1100 loop once §2 field 4's acquisition path is walked (zero compute) |
| **A-3** | **G2's 0.40 over ≤ 2.00°** | The **ceiling is derived** — and was **corrected upward** at revision 1, from the within-stroke-only 0.1762 to the any-admissible-pair supremum **0.2035**, once G2's cross-stroke scope was disclosed. The **1.97× factor** over it is a judgement call. Residual sensitivity, stated plainly: the ceiling is now within a factor of 2 of the band, so an error of ≥ 2× in `|Z|` would breach it — `|Z| = 5.048` is dominated by the quasi-steady `2π = 6.283` and is not plausibly wrong by 2×, but that is the size of error the limb no longer tolerates | Same as A-2. The band was **not** widened to restore the earlier 2.27× (§2) |
| **A-9** | **G3 limb (b), the 1.00 % population fraction** | Limbs (a) `2.00×` and (c) `5 consecutive` are **derived** from `setDeltaT.H` (§2). Limb (b) is **judgement**: calibrated to the isolated-single-step-overshoot pattern the source implies, not read from it. At ≈ 30,850 steps/period it permits ≈ 308 isolated overshoots | Accept as a population-level backstop behind (c), or drop it — (a) and (c) are the limbs that carry the §2a load, and the record says so. Either way the REPORTED channel prints the full distribution, so the choice is visible in the results rather than buried in a threshold |
| **A-4** | **The cost band** | Both bases are **record-quoted with the artifact missing**. Nothing on disk backs 85.1 s or 115.3 s today | Cannot be closed without re-running. The cap's 1.5× headroom is the registered mitigation, and the close-out clause will convert this arm into the first *measured* basis this family has |
| **A-5** | **`endTime = 21.9440`** | One period after a t₁ = 1.0 transient exclusion. The **exclusion window is E1's** (the ~0.02-unit spike, sane by t = 1); **one period is a budget choice, not a physics one** — dynamic stall typically needs ≥ 3 cycles to reach a repeatable limit cycle | This is the §6 ceiling and the §5 `δ_close` figure. If the supervisor wants a cycle-convergence claim, that is a different registration at ≈3× this cost |
| **A-6** | **Field list `{U, p, k, omega, nut}` for completion clause 4** | Read from E2's `initial_fields()`. **I have not verified on disk** that `pimpleFoam` writes `phi`/`yPlus` into the endTime directory in this configuration, because no F5b run tree exists to look at | `phi` and `yPlus` are reported-not-gated (§5 clause 4), so a wrong guess here cannot manufacture a pass or a fail |
| **A-7** | **Completion clause 5's adapted form** | Rule 4's `ExecutionTime count == endTime` is meaningless under `adjustTimeStep`. The three-way count agreement registered instead is my construction | Supervisor's call. It is strictly stronger than a single count and it is declared as an adaptation, not slipped in |
| **A-8** | **`purgeWrite 1` / single time directory** | Read from E4's `pimple_control_dict`, not observed on an F5b run | Only affects what clause 4 can look at; the clause names the directory it requires |

| **A-10** | ~~**"the copy's own α column" (§4, twice)**~~ **CORRECTED at Revision 2, before compute** | `coefficient.dat` has **no α column**. The complete v2606 column set — enumerated in §2 from `forceCoeffs.C:135–151, :237, :337–349` — is `Time Cd Cd(f) Cd(r) Cl Cl(f) Cl(r) CmPitch CmRoll CmYaw Cs Cs(f) Cs(r)`. The earlier revisions' phrasing described a column that does not exist, and a reader implemented literally against it would have failed to parse rather than mis-parsed — but the sentence was still wrong on the face of a frozen document | **CLOSED.** α is the series reconstructed from the copy's own `Time` column through E2's prescribed motion, which is an **identity** (α is an input, not a solved field) and preserves the property C-P1 needs: derived from the parsed file, one value per parsed row, untunable. Changes no gate quantity, band, cap or label. Recorded at both points of use in §4 and in §2 |
| **A-11** | **`pitchAxis (0 0 1)` in E4's `forceCoeffs1` block is a DEAD ENTRY in v2606** | §3's table calls it *"the z axis, correct for this 2-D case"*. **It is not read.** `forces::setCoordinateSystem` (`/usr/lib/openfoam/openfoam2606/src/functionObjects/forces/forces/forces.C:55–90`) reads only `CofR`, `liftDir` (as `e3`) and `dragDir` (as `e1`), and builds `cartesian(origin, e3, e1)`; the header's `pitchAxis` value is `coordSys.e2()` (`forceCoeffs.C:228`), i.e. `liftDir × dragDir` = **`(0, 0, −1)`** for this case, not the `(0 0 1)` the dictionary asks for. So `CmPitch` is a moment about **−z** *and* about the origin (the `CofR` defect already recorded in §2/§3) | **Affects `C_M` ONLY, and `C_M` is NOT GATED by this rung** — G1 and G2 read `Cl`, whose direction *is* honoured (`Cl` is `f[2]` = the `e3` = `liftDir` component, `forceCoeffs.C:137`). Recorded so that the §2 warning about this run's `Cm` column is complete: it is wrong in **two** independent ways, reference point and sign, not one. Any future rung wanting `C_M` fixes both, in a different registration |

**Standing items this rung does not touch:** E2 is shared code and is **not edited** here
(D-1 stays open as a separate item); nothing is sent, filed or uploaded (rule 7); nothing in
this document cites a scratchpad path (rule 13).

---

*Draft ends. `PENDING` — not frozen, nothing launched, 0 core-minutes consumed.*

---

## ADDENDUM 1 — §3 assertion 5, read as "the last state `pimpleFoam` actually reads"

**Stamp:** 2026-08-24T17:49:36Z (`date -u`, read in the shell invocation that appended this section).
**Document version:** the text frozen at `c1ba1845` is taken as **v1.0**; this addendum makes it **v1.1**.
**Appended at HEAD:** 5a197a411b76b187a449357d48ac7ba469f4f4bb.

> **lines whose number changed above this section: 0.**
> Asserted by measurement, not by intention: the file as it stood at
> `git show HEAD:verification/campaign/F5b_PHYSICS_PREREGISTRATION.md` (blob
> `f1cbc96d26846ea583da6d897e914b37a5f576a4`) was diffed against the file carrying this
> addendum. The diff is **+112 lines, 0 deletions, 0 modifications** — a single trailing hunk that begins after the
> last line of the frozen text. **No line above this heading changed number, content or
> position.** Other records cite this document by line, and one citation sits inside an
> executable check.

### Why this is an addendum and not a third in-place revision

**No compute exists**, so `CLAUDE.md` rule 2's before-first-compute window — under which
Revisions 1 and 2 legally edited the body in place — is *technically still open*. **It is
deliberately not used.** The document is now **frozen by commit** at `c1ba1845`, and rule 6
governs a frozen file: it is never edited; a departure is disclosed in a **dated amendment
appended at the foot**, with a version bump and the zero-line assertion above. Revisions 1
and 2 were in-place because the document was then a *draft* and carried no sha. This one
cannot be, and the distinction is recorded rather than resolved by convenience: **freeze by
commit binds ahead of first compute, not only after it.**

### Freeze condition, checked in the writing invocation

**The run directory that must not exist:** `verification/runs/F5b_runs/physics_p1`.
Checked with `test -e /home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1`
in the same shell invocation that appended this section: **ABSENT** at **2026-08-24T17:49:36Z**.
The check is written so that ABSENT is its success path and it is not `&&`-chained behind a
command whose non-zero exit is the expected result — the §9 lesson, applied.

### THE RULING — cfd supervisor, 2026-08-24

§3 assertion 5 reads *"Before `pimpleFoam` starts, `cat` … into `log.levers`."* **It is
hereby READ AS: "at the last state `pimpleFoam` actually reads."**

**The mechanism that forces the reading**, from E2 rather than from recall:
`run_case` **overwrites** `system/fvSolution` with the potentialFoam dictionary at
**E2:270–272** (`_generic_fv_solution(non_orth_correctors=1, potential=True, p_solver="PCG")`),
runs `potentialFoam`, and **restores** the PIMPLE dictionary at **E2:282** — the line before
`pimpleFoam` is invoked. **An echo taken any earlier records a dictionary `pimpleFoam` never
saw.** That is exactly the failure the assertion exists to prevent (E1:126–140, F5c's
binding instrumentation ruling: *"THE SWITCH YOU SET IS NOT THE SWITCH THAT RAN"*) —
reproduced by obeying the assertion's literal wording. A second, independent reason the
literal form cannot run: at driver start **the case directory does not exist at all**.

**Therefore, as registered practice for this rung:**

1. **Capture point.** The wrapper — `verification/runs/F5b_runs/launch_f5b_physics.sh`,
   committed at **`83e0a309`** — captures the six dictionaries (`system/controlDict`,
   `system/fvSolution`, `system/fvSchemes`, `constant/dynamicMeshDict`,
   `constant/transportProperties`, `constant/turbulenceProperties`) into
   `case/log.levers` **at the appearance of `case/log.pimpleFoam`**. The E2:282 restore
   strictly precedes the `pimpleFoam` invocation in the same Python thread, so the capture
   point is after the restore by construction, not by timing luck.
2. **The capture SELF-VERIFIES.** `log.levers` asserts that the `fvSolution` it recorded is
   the PIMPLE dictionary — the `pcorr` and `pcorrFinal` solver blocks present, and the
   `PIMPLE` block present — and writes the result as a `LEVER CHECK` line on its own face.
   **A capture that cannot prove which dictionary it holds is not a lever echo.**
3. **On self-verification failure**, the `pcorr`/`pcorrFinal` lever is marked
   **`unverifiable-from-logs`** — the status §3's `levers_verified_active` table already
   assigns it — and that mark is carried **as a caveat on the face of every finding that
   cites the moving-mesh flux correction**. It is **never a launch abort** and it has
   **no gate effect**.
4. **At grade time**, the reader compares the `fvSolution` md5 recorded in `log.levers`
   against `case/system/fvSolution` on disk **after** the run and reports **match /
   mismatch**. **Reported, not gated** (charter §2a: reporting an identity is encouraged,
   gating it is forbidden).
5. **Corroboration, independent of all of the above.** `_foam` itself writes a hash-bound
   lever echo into `log.pimpleFoam` at solver launch (Verification Charter v1.5 §9), which
   also fires after the E2:282 restore. The two echoes are produced by different code paths
   and may be cross-checked against each other.

### What this addendum does NOT do

**Gate quantities, bands, cap and labels are UNCHANGED.** G1's `A_L ≥ +2.00 C_L·deg`, G2's
`0.40` over `≤ 2.00°`, G3's `2.00×` / `1.00 %` / `5 consecutive`, the §8 point estimate
35.0 core-min, band 28.8–48.0 and **RUN CAP 72.0 core-min**, and every label in the §7
outcome map stand exactly as frozen at `c1ba1845`. Nothing here moves a threshold in either
direction, and an addendum could not lawfully do so (rule 2). This addendum changes only
**how an already-registered instrumentation step is executed and reported**, and the
quantity it touches — the flux-correction lever — was already declared
`unverifiable-from-logs` in §3 before the freeze.

### Status of the wrapper, stated so it is not mistaken for a passing check

`launch_f5b_physics.sh` @ `83e0a309` **has never been executed**, so **every assertion in
it is UNEXERCISED** — A1 (run-directory absence), A2 (E2–E5 porcelain and md5s), A3 (the
frozen blobs hashed against the disk files), A4 (`LAUNCH_HEAD` / `LAUNCH_LOAD` /
`LAUNCH_CMD`) and A5 (the lever echo). Its commit message says so. **The first exercise of
any of them happens at the permitted launch**, and until then no claim in this addendum
about the wrapper's runtime behaviour is a measurement; it is a description of committed
code. The launch itself was **denied by the permission system** at ~17:45Z and is on
Sanaa's desk; no agent re-routed it.

### Struck by this addendum

The document's closing line — *"Draft ends. `PENDING` — not frozen, nothing launched, 0
core-minutes consumed."* — is **struck as to the words "not frozen"** only. The document
**is** frozen, at `c1ba1845` (stage 1) and `a80d5f36` (the stage-2 reader). The original
line is **not rewritten** (rule 6); it stands above with this strike recorded against it.
*"Nothing launched"* and *"0 core-minutes consumed"* remain **true** as of this addendum's
stamp.

*Addendum 1 ends. Status: `PENDING` — frozen, nothing launched, 0 core-minutes consumed,
launch BLOCKED on a permission decision that is Sanaa's alone.*

---

## ADDENDUM 2 — the §3 pre-launch pin on THIS DOCUMENT, re-scoped from WHOLE FILE to FROZEN BODY

**Stamp:** 2026-08-25T16:07:27Z (`date -u`, read in the shell invocation that appended this section).
**Document version:** the text frozen at `c1ba1845` is **v1.0**; Addendum 1 made it **v1.1**; this addendum makes it **v1.2**.
**Appended at HEAD:** 4a507a8912f295cec00f3364368b3df406b77220.
**Wrapper commit this addendum discloses:** `2d5e2411` (blob `23c338242bc535b383fbbb112b45848335e01162`).

> **lines whose number changed above this section: 0.**
> Asserted by measurement, not by intention, and verified by diff rather than by
> assertion: the file as it stood immediately before this append (blob
> `85b645c2d3abeb27d67cd1dfe64238824b0261e6`, 93081 bytes, 1161 lines) was diffed against the file
> carrying this addendum. The diff is a **single trailing hunk beginning after the last
> line of Addendum 1, with ZERO deletions and ZERO modifications**, and the byte prefix
> of the new file over the old file's full length is **identical**. The numeric result
> of both checks is printed in the commit message for this addendum. **No line above
> this heading changed number, content or position.** Other records cite this document
> by line, and one citation sits inside an executable check.

### Freeze condition, checked in the writing invocation

**The run directory that must not exist:** `verification/runs/F5b_runs/physics_p1`.
Checked with `test -e /home/ubuntu/Certonomous/verification/runs/F5b_runs/physics_p1`
in the same shell invocation that appended this section: **ABSENT** at **2026-08-25T16:07:27Z**.
The check is written so that ABSENT is its success path and it is **not** `&&`-chained
behind a command whose non-zero exit is the expected result — the §9 lesson, applied.
**F5b is UNFIRED. Zero core-minutes of solver compute have been consumed by this rung.**

### What happened: the wrapper's FIRST EXECUTION refused, and the refusal was correct

`launch_f5b_physics.sh` @ `83e0a309` was committed with every assertion **UNEXERCISED**,
a status Addendum 1 recorded explicitly. Its first execution — 2026-08-25T15:59:17Z, under
Sanaa's approval of this run — produced:

```
A1  physics_p1 ABSENT                                          OK
A2a git status --porcelain over E2-E5 EMPTY                    OK
A2b E1-E5 md5s equal section 1 (5/5)                           OK
REFUSE (exit 2): verification/campaign/F5b_PHYSICS_PREREGISTRATION.md hashes to
85b645c2d3abeb27d67cd1dfe64238824b0261e6, not the frozen blob f1cbc96d26846ea583da6d897e914b37a5f576a4
```

Exit code 2, **before `mkdir`**; `physics_p1` was not created and no solver process
existed. The cause: the wrapper pinned the **v1.0** blob `f1cbc96d`, and **Addendum 1
itself** (commit `45995a5e`) moved this document's blob to `85b645c2`. **The amendment
broke the very assertion it describes**, and because the wrapper had never been run,
nothing caught it.

**This is L-316's exact shape.** The reader's self-tests are comprehensive and all green —
four §4 controls, seven §5 completion clause-breakers each firing exactly its own clause,
both grading directions on the same frozen bands, and G3's three limbs each shown able to
fire and not to. **Every one of them proves the GRADER and reaches no line of the
LAUNCHER.** A comparator selftest is not a launcher test.

### Why the pin was NOT re-pointed — L-315

The obvious repair — set the constant to `85b645c2` — was **put to the cfd supervisor and
REFUSED**, and the refusal is recorded here because it is the substantive ruling:

> Re-pointing would make the wrapper run today and **re-arm the identical trap at the next
> legal amendment**. The cheapest way to keep the check green would once again be **not to
> write the amendment** — and rule 2 *requires* post-freeze departures to be written, as
> dated addenda appended at the foot. **A check that penalises the honest action is worse
> than no check, because it corrupts behaviour rather than merely missing defects. That is
> L-315**, cfd's own lesson.

**The general rule applied instead**, the L-315 refinement already on the lab's record:
**pin by whole file only where the artifact may NOT legally grow; pin by body wherever it
MAY.** Failing to apply it at the very next call site would be the L-221/L-222 shape — *a
lesson is not applied until every call site asserts it*.

### What changed: ONE of four call sites, and the instrument is untouched

The wrapper applies one instrument, `check_blob`, to four artifacts. **Three of them —
the reader, the fixture generator and the C-N1 fixture — are CODE and may not legally
grow.** Whole-blob equality is exactly right for those, and `check_blob` and its three
calls are **deliberately left completely alone**.

Only this document may legally grow. For it alone, `check_frozen_body` asserts that the
**sha256 of the first `FROZEN_BODY_BYTES` bytes** equals `FROZEN_BODY_SHA256`:

| constant | value |
| --- | --- |
| `FROZEN_BODY_BLOB` | `f1cbc96d26846ea583da6d897e914b37a5f576a4` — **kept**, the identity of the frozen text (v1.0 @ `c1ba1845`); nothing is lost from the record |
| `FROZEN_BODY_BYTES` | `85802` |
| `FROZEN_BODY_SHA256` | `c44b913051b05b85d617a94809cef916b5fc762631da13ab6cc6f9ed8177b9df` |

**Bytes, never a line count and never `head -n`** — a line-count check is not a pin.
**Two failure modes, each refused separately with its own message**, because a truncation
must never read as a pass.

This is **strictly stronger** than the whole-file check it replaces in the way that
matters: it proves the frozen text is unchanged **and** permits the legal growth the
charter requires. Honesty then costs nothing, which is the entire point of L-315.

**No marker was inserted into this document.** An inserted marker would shift Addendum 1's
line numbers, and other records cite these files by line. The prefix assertion needs none.

### The equivalence, PROVEN rather than asserted — and re-derived by this lane

| quantity | v1.0 `f1cbc96d` | v1.1 `85b645c2` |
| --- | --- | --- |
| bytes | **85,802** | **93,081** |
| lines | **1,049** | **1,161** |
| `git diff --numstat` v1.0 → v1.1 | **112 added** | **0 deleted** |
| sha256 | `c44b9130…8177b9df` | `3cb68f43…29a351040` |

**Prefix proof:** `sha256(first 85,802 bytes of v1.1)` = `c44b913051b05b85d617a94809cef916b5fc762631da13ab6cc6f9ed8177b9df` = `sha256(v1.0 in full)`. **Identical.**
The frozen body is byte-for-byte unchanged across Addendum 1, so **every gate, band, cap
and label is bit-identical between the two blobs.** The supervisor's independent proof of
the same fact was re-derived here rather than quoted.

### The new assertion was EXERCISED, in every mode, before it was trusted

Driven on the **literal function text extracted from the committed wrapper**, in isolation,
so that nothing could launch:

| fixture | bytes | result |
| --- | --- | --- |
| the live file (already grown by Addendum 1) | 93,081 | **PASS** |
| **one byte short** of the frozen body | 85,801 | **REFUSE** — truncation message |
| badly truncated | 200 | **REFUSE** — truncation message |
| one byte flipped **inside** the frozen body | 93,081 | **REFUSE** — *"THE FROZEN TEXT MOVED"* |
| a legal future addendum appended | 93,149 | **PASS** |

The **one-byte-short** case is the one that matters: the boundary refuses, so a truncation
cannot read as a pass. The final row is the point of the whole re-scoping — a future legal
amendment does not break the launcher.

**A quoting defect was caught in this process and is disclosed rather than quietly fixed.**
The first draft of the hash line emitted `cut -d\' \' -f1`, which makes the delimiter a
literal quote character. **It passed `bash -n`.** Syntax checking is not semantic checking,
and it was caught only because the function was exercised instead of trusted. Replaced with
`awk '{print $1}'` before commit.

### What this addendum does NOT do

**Gate quantities, bands, cap and labels are UNCHANGED.** G1's `A_L ≥ +2.00 C_L·deg`,
G2's `0.40` over `≤ 2.00°`, G3's `2.00×` / `1.00 %` / `5 consecutive`, the §8 point
estimate 35.0 core-min, band 28.8–48.0 and **RUN CAP 72.0 core-min**, and every label in
the §7 outcome map stand exactly as frozen at `c1ba1845`. Nothing here moves a threshold
in either direction, and an addendum could not lawfully do so (rule 2). This addendum
changes only **how the launcher verifies that the frozen text is the text that ran.**

The reader, generator and fixture pins are **unchanged and still whole-blob**. The §10
grading path is **unchanged**: `analyse_f5b_physics.py` still hashes to
`6c6d34d02e6de925457dbfdbf75a0e004168f345`, the stage-2 freeze blob at `a80d5f36`.

### Correction to Addendum 1's closing line

Addendum 1 ends *"launch BLOCKED on a permission decision that is Sanaa's alone."* That
sentence is **struck as to the word "BLOCKED"** only: **Sanaa APPROVED this run in her own
session turn of 2026-08-25** — *"F5b: APPROVED. The 72-core-min capped run fires as
specced."* The original line is **not rewritten** (rule 6); it stands above with this
strike recorded against it. *"Nothing launched"* and *"0 core-minutes consumed"* remain
**true** as of this addendum's stamp: the launch that followed the approval refused at A3,
on the defect this addendum repairs.

*Addendum 2 ends. Status: `PENDING` — frozen, nothing launched, 0 core-minutes of solver
compute consumed, launch APPROVED by Sanaa and held pending the supervisor's check-1 read
of the wrapper diff.*
