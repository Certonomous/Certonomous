# SO-3aF2 — MULTIPOINT-INCOMPRESSIBLE FEASIBILITY PROBE ON THE THREE-ANGLE ALPHA BRACKET (A1 NACA0012)

## ⚠ THIS IS `prereg=FEASIBILITY`. IT IS **NOT** A RULE-2 GRADIENT FREEZE AND MAY **NEVER** BE CITED AS ONE.

**Read this paragraph before any other.** This document registers a **FEASIBILITY
PROBE**. It carries **NO GRADIENT GATE, NO FD TABLE AND NO ADJOINT**, and the item
it registers **PRODUCES NO GRADIENT NUMBER AT ALL** — not one that is ungated, not
one that is "diagnostic only", not one written to a file and left unread.
`DAFOAM_CHARTER.md` §2's bright line is that a gradient number without an FD table
beside it does not enter a record; **this item complies by never computing one**,
and the compliance is **structural, not a convention**: the producer's
`compute_totals` and `check_totals` branches are **physically deleted** (§3), so a
mistyped `-task` argument exits non-zero rather than reaching an adjoint.

**Nothing in this item is a verdict.** Its outputs are **READINGS**. No number
below may be quoted as `PASS`, `GATE REACHED` or `GATE FAIL`, carried into SO-3a's,
SO-3aR's or SO-3aR2's grading, or used to license any gradient claim. It files with
`prereg_commit = "FEASIBILITY"` under Sanaa's ruling of 2026-08-31, quoted verbatim
from `etc/sessions/2026-08-31T1513Z_sanaa_freeze_clock_and_so3_ruling.md:5`:

> "start the L1 feasibility solves on Cases 1 and 2 NOW — no freeze required for
> feasibility/physics rungs, never was."

`scripts/queue_entry_check.py:114` encodes that ruling lab-wide as
`UNREGISTERED_PREREG_TAGS = frozenset({"FEASIBILITY", "PHYSICS"})` (commit
`9154c8ef`), exact-match and case-sensitive.

**Version 1.0. FROZEN. Dated 2026-08-31.** Lane: dafoam `lab-lane`. Supervisor:
`dafoam-supervisor`. **Nothing here is filed, sent, emailed, uploaded, registered,
posted or commented outside this box** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md`
§10). **SUBMISSIONS PARKED.** Every decision is `[lab-attributed]`.

**THIS ITEM IS FROZEN AND NOT LAUNCHED.** Arming is the supervisor's decision under
`SUPERVISION_CHARTER.md` §3 check 4, not this lane's (`CLAUDE.md` rule 9).

---

## 0. A PREMISE CORRECTION, STATED FIRST BECAUSE IT CHANGES WHAT THIS ITEM IS WORTH

This lane was briefed to register a feasibility probe measuring *"that all three
primals converge and the bracket is feasible"*, on the ground that SO-3aR measured
exactly this before it died. **The second half of that is true. The first half
would buy almost nothing, because that question is already answered TWICE on this
box, and the brief did not know about the second answer.**

**MEASUREMENT 1 — `SO3aF`, a dedicated feasibility item that already ran.**
`cases/dafoam/ladder-a/A1/feasibility_SO3a_alpha/` is **tracked at HEAD**, carries
its own `FEASIBILITY_NOTE.md`, and **completed at 2026-08-31T16:11:51Z** for
**0.5833 core-min** [MEASURED, `feasibility_SO3a_alpha/launcher.queue.out`]. It ran
the three registered angles as primal-only `DASimpleFoam` solves and read back
[MEASURED, `CURRICULUM-SO3aF-…/SO3aF_read_20260831T161116Z.txt`]:

    CD = [0.01723938072177922, 0.02091051000679216, 0.02726805411971688]
    CL = [0.311896, 0.498765, 0.663976]
    CD monotone increasing across the bracket: True
    dCL/dalpha lower 0.093435 /deg, upper 0.082606 /deg, slope ratio 0.8841

**MEASUREMENT 2 — SO-3aR's baseline, and it converged.** `curriculum_SO3aR/RESULTS.md:141-155`
records three primals satisfying the prescribed `1e-8` tolerance at iterations
**1514 / 1644 / 1774**, with `satisfied the prescribed tolerance` counted **3** and
`^End$` counted **3** over the whole log [MEASURED], giving the figures the brief
quoted:

    CD = [0.01723938072177922, 0.020910510045267394, 0.027268054119716875]
    CL = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]
    J  = 0.02180598162892116

**These two independent runs agree to a relative `1.8e-9` on the worst of the six
functionals** (`CD[1]`, the only entry differing above `1e-10`) [computed here from
the two records]. **The bracket's feasibility is therefore not an open question,
and an item whose registered content was "do three primals converge" would be
buying a third copy of a twice-measured answer.**

**SO3aF's `converged: False` column is a READER limitation, not a physics finding,
and is named here so it is not mistaken for one.** That reader reported
`converged=0 of 3` with `final_resid=None, n_res=0` — it found no residual line in
the log shape it was given. SO-3aR's log, read by a different instrument, shows the
same three points converging to `1e-8`. **A disagreement between two readers about
convergence, where one of them recorded no residuals at all, is a reading defect in
that reader.** This item therefore reads convergence from the counted tolerance
line **and** from the residual history, and refuses if the two disagree (§5 F1).

### 0.1 WHAT IS ACTUALLY UNMEASURED, AND IT IS THE ONLY THING THIS ITEM SELLS

**No multipoint assembly has ever been shown to stand up on this case.** Both
measurements above ran the three angles as **three independent single-point
programs**. SO-3aR's *multipoint* assembly died at its second arm, and it died
**before** demonstrating that three `DAFoamBuilder`s can coexist in one invocation,
because the thing that killed it was the shared directory itself.

**The unmeasured question this item answers, for ~1.5 core-min:** *do three
`DAFoamBuilder`s, each given its own `run_directory`, coexist in ONE OpenMDAO
invocation on this case — each building its own `DASolver`, reading its own mesh
copy and writing its own time directories — and do the three points then reproduce
the functionals both prior runs measured?*

That is a **structural precondition of the SO-3aR2 repair**, it has never been run,
and it is buyable without any adjoint and therefore without any gradient number.

### 0.2 THE LIMIT OF WHAT THIS ITEM CAN CLAIM — STATED BEFORE IT RUNS

**THIS ITEM DOES NOT AND CANNOT SHOW THAT SO-3aR's COLLISION IS FIXED, AND NO
READING OF IT MAY BE WRITTEN UP AS IF IT DID.**

SO-3aR died inside the **ADJOINT**, not the primal
(`curriculum_SO3aR/RESULTS.md:174-199` [MEASURED]): `renameSolution` at
`pyDAFoam.py:1543`, reached from `mphys_dafoam.py:483` in **`solve_linear`**, under
`prob.compute_totals(...)`. `point0` renamed `443 -> 0.0001` and succeeded;
`point1` tried `436 -> 0.0001` into the destination `point0` already held. **The
three PRIMALS did not collide** — they converged at increasing times 1514/1644/1774
and the baseline functionals were written.

**Therefore a primal-only item never reaches the failing call site.** This item can
show that the builders coexist and that each owns a separate tree; it **cannot**
show that `solve_linear`'s per-point `solution_counter` no longer collides, because
it never calls `solve_linear`. **That proof belongs to SO-3aR2 under its own
rule-2 freeze, with an FD table beside it.** Saying so here is the point of this
section: an item that quietly let a reader infer the collision was closed would be
worth less than nothing.

---

## 1. ITEM, ROOT, AND WHAT IT IS

**Item id `SO3aF2`.** Run root
`/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility`.
Case dir `cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/`.

Two arms, `np = 1` throughout (`DAFOAM_CHARTER.md` §5: a statement at one np is a
statement about that np). SHIPPED image only — **there is no two-row requirement
here because there is no verdict about DAFoam being made** (`DAFOAM_CHARTER.md` §1's
two-row rule binds verdicts; this item produces readings). The PATCHED row is not
run, and its absence is a stated scope limit, not an omission to be discovered.

| arm | kind | image | ranks | task | artefact |
|---|---|---|---|---|---|
| **MESH** | SCRIPT | SHIPPED `dafoam/opt-packages:latest` `sha256:9d45679d…f07fc` | 1 | the tutorial's `preProcessing.sh` + `checkMesh` | `MESH/checkMesh.log` |
| **XM** | SOLVER | SHIPPED, same digest | 1 | ONE multipoint `prob.run_model()` over the three angles | `XM/so3af2_M.json` |

---

## 2. FREEZE CONDITION — the run directory that does not exist, and how it was checked

At **2026-08-31T22:35Z**, in one invocation and **beside a known positive**
(`CLAUDE.md` rule 3):

* `test -e /home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility`
  → **ABSENT**; the same reader on `CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility`
  → **EXISTS**. The absence is a reading of the disk, not of a broken test.
* `sudo -n docker ps -a` filtered on the `so3af2_` container prefix → **0
  containers**, against 20 containers visible to the same lister on this box.

**This item has burned 0 core-min, started no container and created no run
directory.**

---

## 3. THE PRODUCER, AND WHY IT CANNOT PRODUCE A GRADIENT

`so3af2_runScript.py` is derived from `curriculum_SO3aR2/so3ar2_runScript.py` —
which **already carries the per-point `run_directory` repair** at `:203`, `:260`
and `:286` — with **exactly one class of deletion**: the `compute_totals` and
`check_totals` task branches (`so3ar2_runScript.py:394-408`) and the `of=`/`wrt=`
lists they consume are **REMOVED**, leaving `run_model` as the only reachable task
and an explicit non-zero exit for any other `-task` value.

**This is the enforcement of the no-gradient promise in §0, and it is structural.**
A convention ("we simply will not pass `-task compute_totals`") is a claim about
operator behaviour; a deleted branch is a property of the bytes. The deletion is
shown as a diff in `so3af2_runScript_DELTAS_from_so3ar2.diff`, and the reader
(§4) **refuses** if the string `compute_totals` appears anywhere in the staged
producer.

Physics, unchanged and by citation from `so3ar2_runScript.py`, itself unchanged
from `so2a_runScript.py:39-84`: `DASimpleFoam`, Spalart–Allmaras, `U0 = 10.0`,
`A0 = 0.1`, `rho0 = 1.0`, `primalMinResTol 1.0e-8`, `useWallFunction True`, mesh
**4,032 cells** regenerated by this item's own MESH arm, functionals `CD` and `CL`
only. **`ALPHAS = [3.13918623195176, 5.13918623195176, 7.13918623195176]`**,
**`WEIGHTS = [1/3, 1/3, 1/3]`**, `SCENARIOS = point0/point1/point2`,
`RUN_DIRS = {point_i: "mp<i>"}` derived from `SCENARIOS` and never spelled out.

### 3.1 THE COLLISION-AVOIDANCE CHOICE, AND WHY — per-point `run_directory`, NOT three serial invocations

The brief offered two ways to avoid SO-3aR's collision. **This item takes the
per-point `run_directory` route (D6R's `RUN_DIRS` pattern, `d6r_opt_runScript.py:59`,
`:120`, `:138`), and rejects three separate serial invocations. The reason is that
the rejected option measures nothing this box does not already know.**

* **Three separate serial invocations is what `SO3aF` ALREADY DID** (§0), for
  0.5833 core-min, and what SO-3aR's own three independent primals amounted to.
  Repeating it buys a third copy of a twice-measured answer and, by construction,
  **cannot exercise coexistence at all** — one builder alive at a time is precisely
  the configuration in which the collision cannot occur and therefore the
  configuration in which nothing is learned about it.
* **Per-point `run_directory` in ONE invocation is the configuration that has never
  run.** It puts three `DAFoamBuilder`s, three `DASolver`s and three mesh
  coordinate subsystems in one process simultaneously — the exact structural state
  SO-3aR was in when it died — and asks whether the directory separation holds.
* It is also the configuration **SO-3aR2 will use under its own freeze**, so a
  cheap primal-only pass here de-risks that item's ~400 core-min rather than
  duplicating a rung.

**The honest limit of the choice is §0.2 and is not softened here:** coexistence in
the primal is a weaker statement than collision-freedom in the adjoint.

---

## 4. THE READER, ITS PLANTED CONTROL, AND THE SUFFICIENCY LEG

`so3af2_read.py` is the frozen reader. It computes **no gradient**, and it refuses
(exit 2) rather than degrading (`CLAUDE.md` rule 4's comparator discipline).

### 4.1 Direction A — the reader can see a non-zero

The reader writes a synthetic artefact carrying a known perturbation, **re-reads it
FROM DISK**, and **refuses if the plant is invisible**. The plant changes a value
inside the per-point structure the reader must traverse in full; **a control that
EMPTIES that structure is REFUSED**, because an empty container is seen by a broken
reader too (`CLAUDE.md` rule 3).

### 4.2 Direction B — the reproduction check must be shown able to read MISS, and the plant is RELATIVE

**THE PLANT IS REGISTERED AS A RULE RELATIVE TO THE QUANTITY IT PERTURBS, NOT AS A
BARE ABSOLUTE.** This is the lesson SO-2M paid for and SO-2MR repaired — *an
absolute plant magnitude does not port across functionals*
(`curriculum_SO2MR/PREREGISTRATION.md` §0, §7.2). `CD ≈ 0.017` and `CL ≈ 0.66` here
differ by a factor of 38, so a single absolute plant sized for one is wrong for the
other **by construction**, and porting one would repeat SO-2M's defect knowingly.

For a reproduction target `r` with reference value `v_ref` and read value `v`:

```
need_r = (band_REP / 100) * |v_ref|                  the margin that must be crossed
P_r    = K_F * (band_REP / 100) * |v_ref|            (MAGNITUDE)
s_r    = +1 if v >= v_ref else -1                    (SIGN — AWAY from v_ref)
v'     = v + s_r * P_r
```

**`K_F` IS REGISTERED AT FREEZE AS `K_F = 2.0`**, with **`band_REP = 1.0e-4 %`**
(i.e. a relative `1.0e-6`, §5 F2). Because `s_r` moves `v` **away** from `v_ref`, no
cancellation is reachable from any live position and

```
|v_ref - v'| = |v_ref - v| + P_r   EXACTLY
rel_planted  = rel_live + K_F * band_REP  >=  K_F * band_REP  =  2.0e-4 %
```

against a `1.0e-4 %` band — **the planted copy crosses the reproduction band by
construction, with 100 % margin, at either functional's scale, whatever the live
agreement happens to be.**

**THE SUFFICIENCY LEG.** The reader **re-derives `P_r > need_r` from the row's own
numbers** and **REFUSES `PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION`** if it does not
hold. A freeze-time selftest leg moves `K_F` — and nothing else — to **0.5**,
re-reads the same clean fixture that reads HIT at the registered `K_F`, and
**requires that refusal BY NAME**; a bare "it refused" would be satisfied by any
refusal and could not tell a working assertion from an unrelated crash. `K_F` is
restored in a `finally` and the restore is asserted from outside.

**Why this is not fitting the control to the data:** it moves no band and no
acceptance criterion; `K_F` and `band_REP` are constants in the frozen bytes and
`v_ref` is a number **already on record from two prior runs**, so there is no free
parameter left to choose after seeing an answer; and it makes the control **strictly
harder to pass**, since the reader now refuses a plant it would previously have
shipped.

---

## 5. REGISTERED PREDICTIONS — scored HIT / MISS, and **NOT** gates

**These are predictions, not gates. A MISS is a FINDING and is reported as one; it
is never written as `GATE FAIL`, because this item has no gates** (§0). The only
verdict vocabulary this item may emit is `BLOCKED` (a NO-LAUNCH branch fired) or
`NOT A RESULT` (an infrastructure refusal), and both describe the *item*, never a
number.

| id | prediction | how scored | what a MISS means |
|---|---|---|---|
| **F1** | all three points converge — `satisfied the prescribed tolerance` counted **3** in the log **AND** three residual histories present, the two readings **agreeing** | counted from the log, both ways | a genuine finding: two prior runs converged these angles, so a MISS here points at the multipoint assembly, not the physics. A reader disagreement refuses (§0) rather than reporting a number |
| **F2** | the three points reproduce the recorded functionals to **relative `1.0e-6`**: `CD = [0.01723938072177922, 0.020910510045267394, 0.027268054119716875]`, `CL = [0.31189588769251864, 0.49876526085592926, 0.6639763551107052]`, `J = 0.02180598162892116` | reproduction check, band `1.0e-6` relative, per entry | **the reproduction control fails.** Two independent prior runs agree to `1.8e-9`, so a MISS at `1e-6` means the multipoint assembly changes the answer — a real finding about the assembly and the most valuable outcome this item can produce |
| **F3** | **three DISTINCT run directories `mp0`, `mp1`, `mp2` exist under the case tree, each holding its own time directories**, and no two points write the same directory | directory listing, read from disk | the `run_directory` separation does not take effect, which would mean the SO-3aR2 repair does not do what its source reads as doing — a finding that must reach SO-3aR2 before it freezes |
| **F4** | the token `already exists, moving failed!` appears **0** times in the log | counted per line, with the counter shown able to count a planted occurrence | the collision reaches the primal path too, which would be new and would enlarge the defect's known reach |
| **F5** | `J` equals `SUM_i w_i * CD_i` over the read `CD` to `1e-12`, recomputed by the reader rather than trusted | recomputed | the objective wiring disagrees with the registered weights |

**PREDICTED OUTCOME, WRITTEN BEFORE ANY SOLVER RUNS: F1–F5 all HIT.** That
prediction is deliberately unhedged, because the two prior runs make F1, F2 and F5
likely and **F3 and F4 are the ones carrying real information** — they have never
been observed on this case in a multipoint assembly.

---

## 6. NO-LAUNCH BRANCHES — registered before compute, at 0.00 core-min

| branch | condition | writes | rc | reading |
|---|---|---|---|---|
| **NL-1 ROOT** | the run root already exists, or a live container holds the `so3af2_` prefix | `NOLAUNCH_ROOT.txt` | **3** | **`BLOCKED`** |
| **NL-2 PRODUCER** | the staged `so3af2_runScript.py` md5 is not the frozen one, **or the string `compute_totals` appears anywhere in it** | `NOLAUNCH_PRODUCER.txt` | **4** | **`BLOCKED`** |
| **NL-3 FREEZE** | the reader's or launcher's md5 is not the value pinned at this freeze | `NOLAUNCH_FREEZE.txt` | **5** | **`BLOCKED`** |
| **NL-4 MEM** | a bounded poll on live `MemAvailable` against the 6.0 GiB floor expires (bound 3600 s), terminating **non-zero**, never block-and-continue | `NOLAUNCH_MEM.txt` | **6** | **`BLOCKED`** |

NL-2's second clause is the structural half of the no-gradient promise (§3).

---

## 7. COST — core-minutes, from MEASURED anchors on this box

**Anchors are MEASURED core-minutes read from ledgers on this box, not estimates.**

| arm | point (core-min) | cap (core-min) | basis |
|---|---|---|---|
| MESH | **0.30** | 3.0 | SO-3aR `MESH` **0.267 MEASURED** (`CURRICULUM-SO3aR-…/ledger.txt`, `ARM=MESH … rc=0 wall_s=16 core_min=0.267`) |
| XM | **1.20** | 6.0 | bracketed by two MEASURED figures: **lower** SO3aF **0.5833** for three cold primals in one container; **upper** SO-3aR `X-S` **1.533**, which bought three primals *plus* a baseline *plus* a partial adjoint before dying, so a primal-only multipoint sits strictly below it |
| **total** | **1.50** | **CEILING 9.0** | — |

**The XM point is a bracket, not a single anchor, and is labelled as one.** The
multipoint assembly builds three `DASolver`s where SO3aF built one at a time, so
its init cost is higher than the lower anchor; it computes no adjoint, so it is
below the upper. **`1.20` sits inside `[0.5833, 1.533]` and is `[DERIVED from two
MEASURED figures]`, not measured.**

**Dollars, DERIVED and NOT MEASURED — the box cannot read its own billing**
(`COMPUTE_BUDGET_CHARTER.md` §5): at **$0.0513/core-h on c7a.4xlarge, a rate that
is REPORTED-BY-OWNER (Sanaa, 2026-08-21/22) and is NOT a figure this box measured**
— point **1.50 core-min = 0.025 core-h = $0.0012825**; ceiling **9.0 core-min =
0.15 core-h = $0.007695**. Both far under $25 and therefore pre-authorised; **the
figure is stated anyway, because a blanket is not a per-item read** (`CLAUDE.md`
rules 9 and 12). **An overrun STOPS the run; it does not get a new budget.**

**Calibration row owed at completion** (`CLAUDE.md` rule 12): actual/predicted per
arm from this item's own ledger, landing in `docs/COST_CALIBRATION.md`.

**Memory floor 6.0 GiB**, from D13's MEASURED 1.70 GiB peak RSS for this
4,032-cell 2-D case at np = 1, tripled for three coexisting `DASolver`s and then
given headroom. Container cap **4g**. **cpuset: to be fixed by the launcher against
live containers at arm time and refused on collision** — core 9 is held by SO-2MR
tonight and must not be taken.

---

## 8. WHAT IS FROZEN BY THIS COMMIT, AND WHAT IS STILL OWED — stated plainly rather than implied

**FROZEN HERE, and DRIVEN GREEN before the freeze:**

| file | md5 | role |
|---|---|---|
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | the frozen reader: `FLIP_PLANT_K_F = 2.0`, `BAND_REP_PCT = 1.0e-4`, both planted controls, the sufficiency leg, 17 selftest units |

**DRIVEN GREEN AT FREEZE, 2026-08-31T22:34Z, ZERO CONTAINERS AND ZERO CORE-MINUTES:**

* `python3 so3af2_read.py --selftest` → **`SELFTEST PASS 17/17`**, `failures=0`, rc=0.
* `python3 -O so3af2_read.py --selftest` → **`SELFTEST PASS 17/17`**, `failures=0`,
  rc=0 — **run under `-O` because `-O` strips `assert`, and a control that lives in
  an `assert` is absent in production** (L-332). This reader places **no control
  inside an `assert`**; the `-O` run is the evidence for that, not the intention.
* Leg **S3** is the sufficiency leg **DRIVEN RED**: `K_F` moved to `0.5` and the
  reader required to refuse `PLANT_NOT_SUFFICIENT_BY_CONSTRUCTION` **by name**.
  Leg **S2c** drives the plant algebra at **both** the `CD` scale and the `CL`
  scale — the factor of 38 an absolute plant could not port across, which is the
  whole reason the rule is relative.

**OWED BEFORE THIS ITEM CAN BE ARMED — and it is NOT launch-ready until these land:**

1. `so3af2_runScript.py` — the producer of §3, derived from
   `curriculum_SO3aR2/so3ar2_runScript.py` with the `compute_totals` and
   `check_totals` branches **deleted**, plus
   `so3af2_runScript_DELTAS_from_so3ar2.diff` showing exactly that deletion.
2. `so3af2_run_arm.sh` — the launcher carrying the four §6 NO-LAUNCH branches, the
   md5 pin block, the cpuset guard and the ledger row.
3. A pin census over the launcher's own bytes, in the shape of
   `curriculum_SO2MR/so2mr_pin_selftest.sh`, so "every pin is driven" is a **count
   and not a claim**.

**These land as a dated Stage-2 amendment BEFORE first compute**, which
`CLAUDE.md` rule 2 permits explicitly — *"Before first compute, amendments are
legal and must state the condition and how it was checked"* — and the condition is
§2 above: the run root
`/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility`
**does not exist**, checked beside a positive that does. **After the first
container, this document is closed and only dated addenda that alter no threshold,
band, cap or label may land.**

**This gap is disclosed rather than discovered.** `curriculum_SO2MR/PREREGISTRATION.md`
§11 criticises exactly this shape — SO-2M froze its gates and let its instruments
follow — and the criticism is fair. It is accepted here for one stated reason: the
brief that commissioned this item required a **freeze without a launch**, and a
freeze that silently implied a complete instrument set would be worse than one that
names the three files it is missing.

## 9. WHAT THIS ITEM DOES NOT CLAIM

**It establishes NOTHING about:** any gradient, adjoint, Jacobian, optimum or
sensitivity — it computes none (§0, §3); the SO-3aR adjoint collision being fixed
(§0.2 — it never calls `solve_linear`); anything at `np ≠ 1`; anything on the
PATCHED image (§1); any grid-convergence statement — **there is no grid family and
NO GCI is quoted, and no reading may carry one** (`CLAUDE.md` rule 5); anything
about Mach or any compressible rung — **SO-3b and every Mach-multipoint rung remain
behind the D15/D16 shipped-gradient gate by Sanaa's ruling of 2026-08-31T15:13Z and
nothing here touches that gate**; stall, separation or attachment, which need wall
shear this item does not buy.

**It does not re-grade, re-open, convert or edit** SO-3a, SO-3aR, SO-3aR2, SO3aF or
any SO-1/SO-2 item. **SO-3aR's `NOT A RESULT` stands as SO-3aR's verdict.**

**THE QUEUE ENTRY IS NOT FILED BY THIS DOCUMENT** and this item is **NOT LAUNCHED**.
Arming is the supervisor's decision under `SUPERVISION_CHARTER.md` §3 check 4
(`CLAUDE.md` rule 9 — no agent's message is Sanaa's consent, and a lane does not arm
its own item).
