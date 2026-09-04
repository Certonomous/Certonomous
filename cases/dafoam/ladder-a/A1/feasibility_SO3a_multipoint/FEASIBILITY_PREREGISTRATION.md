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

---

## STAGE-2 AMENDMENT — THE THREE OWED FILES EXIST. Dated **2026-09-03**. Version **1.0 → 1.1**.

> **lines whose number changed above this section: 0** — asserted by execution in the committing invocation, against both the pre-append snapshot and `git show HEAD:`.

**This is a PRE-COMPUTE amendment, which §8 anticipated in these words:** *"These land as a dated Stage-2 amendment BEFORE first compute, which `CLAUDE.md` rule 2 permits explicitly."*

> **CONDITION CHECKED BY EXECUTION, 2026-09-03**, in the invocation that wrote this section, **beside a known positive** exactly as §2 requires: the run root `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility` — **ABSENT**, while `/home/ubuntu/certonomous-runs/CURRICULUM-SO3aF-a1-naca0012-alpha-feasibility` read by the same test — **EXISTS**. The absence is a reading of the disk, not of a broken test. `verification/queue/` — **0** rows matching `so3af2`. **This item has still burned 0 core-min and started no container.**

**It moves no prediction, no band, no cap, no label and no NO-LAUNCH rc.** §5's F1–F5, §6's four branches, §7's caps and the `K_F = 2.0` / `band_REP = 1.0e-4 %` plant constants stand exactly as frozen.

### S2.1 The three files §8 owed, now pinned

| file | role | md5 | lines |
|---|---|---|---|
| `so3af2_runScript.py` | **the producer** — §8 item 1 | `4359b9b7c04a81b9e56231481f4e0ccb` | **435** |
| `so3af2_runScript_DELTAS_from_so3ar2.diff` | every byte of the deletion, as a diff — §8 item 1 | `217383144f65ac720c138678908bf1da` | 295 |
| `so3af2_run_arm.sh` | **the launcher** — §8 item 2 | `9dec28b7119c901c68d2399d0c3248c2` | **230** |
| `so3af2_pin_selftest.sh` | **the pin census** — §8 item 3 | `039e18f3775e837ac88ed84c34aabf6e` | 248 |
| `so3af2_read.py` | the reader, **UNCHANGED from the 2026-08-31 freeze** | `d5f4149d43abe3a165ffe7e653b78bee` | 560 |

**The reader is byte-unchanged and re-driven at this amendment: `SELFTEST PASS 17/17`, `failures=0`, under `python3` AND `python3 -O`.**

### S2.2 ⚠ A DEFECT IN THE FROZEN TEXT, FOUND WHILE DERIVING THE PRODUCER, AND DISCLOSED RATHER THAN QUIETLY WORKED AROUND

**§3 and §6 NL-2 are jointly satisfiable ONLY if the deletion reaches every mention of the forbidden token — and §3, read alone, does not say that.**

§3 registers the deletion as *"the `compute_totals` and `check_totals` task branches (`so3ar2_runScript.py:394-408`) and the `of=`/`wrt=` lists they consume"*. §6 NL-2 refuses the launch if the token *"appears **anywhere** in it"*.

**MEASURED: the parent carries the token at SEVEN sites, only FOUR of which are inside that line range** — the header docstring (`:28`), the argparse help string (`:135`), the two `elif` branches (`:394`, `:402`), the totals call (`:399`), and the final else-clause message (`:409`).

> **Deleting exactly the range §3 names would have left the token at three surviving sites, and NL-2 WOULD HAVE FIRED ON EVERY LAUNCH OF THIS ITEM, FOREVER.** The item would have been unable to start, on a guard that was right, against a producer that was correct.

**The resolution is the one the freeze plainly intends and is not a change to it.** §3's own words say NL-2's second clause *"is the structural half of the no-gradient promise (§3)"* — the two clauses are one instrument described twice, and the promise is *"produces no gradient number at all"*, not "has no reachable branch". **Every occurrence is therefore deleted**, and the producer's own docstring section (A) records why. `grep -c` over the staged producer returns **0**. **No frozen text is edited; the discrepancy is disclosed here and carried forward as a registered defect binding on any successor.**

This is the **tenth** unsatisfiable-by-construction condition this family has met in one day, and the **second inside a frozen registration** rather than an instrument.

### S2.3 The producer — what was deleted, and what was NOT touched

**Deleted:** the two gradient task branches, the `of=`/`wrt=` lists they consume, and every mention of the forbidden token. The only task string the file knows is `run_model`; any other `-task` value exits **1** with a named message.

**Not touched, and cited rather than re-decided:** `DASimpleFoam`, Spalart–Allmaras, `U0 = 10.0`, `A0 = 0.1`, `rho0 = 1.0`, `primalMinResTol 1.0e-8`, `useWallFunction True`, the FFD box, the shape functions, the geometric constraints, the **shared** geometry, and the per-point `run_directory` repair (`RUN_DIRS` derived from `SCENARIOS`, never spelled out). `ALPHAS`, `WEIGHTS` and `SCENARIOS` are byte-identical to the parent's.

**Added:** the artefact writer for `XM/so3af2_M.json` (`points` with `alpha`/`CD`/`CL`, `J`, `residual_histories`, plus `weights`, `scenarios` and `run_dirs` for a reader's cross-check), and a refusal on a pre-existing artefact.

> **⚠ THE PRINCIPAL LAUNCH RISK, NAMED HERE RATHER THAN DISCOVERED AT ARM TIME.** §5 F1 requires the residual-history count to **agree** with the count of `satisfied the prescribed tolerance` lines, and the reader **refuses** on a disagreement. **This lane has spent ZERO solver core-minutes and has therefore NOT exercised the residual-history lookup against a live container.** The mphys path `<scenario>.coupling.solver` is **corroborated by evidence on disk** — OpenMDAO deprecation warnings in `CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log` name `cl04.coupling.solver` explicitly — but **which attribute carries a residual history is NOT corroborated**, and the producer tries four candidate names in order.
>
> **The producer therefore REFUSES (exit 7, `RESIDUAL_HISTORY_UNAVAILABLE`) and writes NO artefact rather than writing one with a short list.** A short list would reach the reader as a **CONVERGENCE DISAGREEMENT** — which §5 F1 defines as a finding about the multipoint assembly — when its true cause was the producer failing a lookup. **Manufacturing that finding would be worse than failing to run**, and this is the one place the item may need a bounded repair after its first container. It is registered as a foreseen outcome, not as an excuse.

### S2.4 The launcher — the four NO-LAUNCH branches, and the half of NL-3 a file cannot do

All four branches write their **named** file and exit with their **named** rc, and all four read **`BLOCKED`** — a branch that fires is the launcher declining to start, never a measurement that failed. The cpuset is **fixed against live containers at arm time** and refuses on collision, with **core 9 excluded by name** (§7: held by SO-2MR). The image is verified **by digest**, SHIPPED only. An overrun **stops** the arm at its cap with a named abort.

> **NL-3 names *"the reader's or launcher's md5"*, and a file cannot contain its own md5** — writing the value changes the value. **The launcher enforces the half it can** (the reader's pin, in-process) and **self-hashes into the ledger and every NOLAUNCH file**; **the half it cannot is enforced from outside** by `so3af2_pin_selftest.sh` against the value pinned in S2.1 above. The split is stated rather than fudged.

### S2.5 The pin census — a COUNT, not a claim

It carries **no list of pins**. It **enumerates** every `MD5_*=` assignment out of the launcher's own bytes, maps each through one table, and **refuses if any enumerated pin has no registered target**; driven and existing counts are printed side by side and must be equal. **A pin added to the launcher with no row FAILS the census.** (The measured failure this repairs: SO-1c's driver carried twelve pins and its selftest drove four while claiming "every pin".)

**DRIVEN AT THIS AMENDMENT — 14 legs, PASS 14, FAIL 0, NOT RUN 0:**

- **Pin census** — `MD5_READER`, `MD5_PRODUCER`, driven **2**, existing **2**, **equal**; and the launcher's own md5 confirmed pinned in this document.
- **All four NO-LAUNCH branches driven REFUSING**, each writing its named file with its named rc: NL-3 → rc **5**, NL-2 md5 → rc **4**, NL-2 **token** → rc **4**, NL-1 → rc **3**, NL-4 → rc **6**.
- **NL-2's token clause driven BY NAME**, with the producer's pin moved onto the tainted bytes **so the md5 clause passes and the token clause is what fires** — otherwise the leg would pass for the wrong reason, which is a failure mode this lane hit earlier the same day and did not repeat.
- **ALL FOUR DRIVEN PASSING**, every guard printing its PASS line — **the leg that proves the four guards are SATISFIABLE and not unsatisfiable-by-construction.** The run then ends at the **image-digest** guard, which cannot read a digest from the stub; `docker run` is never reached, and the leg's message says exactly that rather than implying it got further.
- **Safety, read rather than promised:** the real run root **still ABSENT** at the end; `docker` reached **4 times**, every call hitting a **stub that exits 99 and starts nothing**, with the stub's transcript printed; cleanup **by name**, and a **decoy the file did not create SURVIVED** it.

**No leg starts a container and no leg touches the real run root**, so both sentences of §2 are still true after this amendment — which is checked, not asserted.

### S2.6 What is still NOT discharged

- **`SUPERVISION_CHARTER.md` §3 check 4 — arming — is the supervisor's and is not taken here.** **THE ITEM IS NOT ENQUEUED, NOT LAUNCHED, AND NO QUEUE ENTRY IS FILED BY THIS COMMIT.**
- **§0.2 stands undiminished:** this item never calls `solve_linear` and **cannot** show SO-3aR's adjoint collision is fixed. That proof belongs to SO-3aR2 under its own freeze, with an FD table beside it.
- **`SUBMISSIONS PARKED.`**

**END OF STAGE-2 AMENDMENT.**

---

## CORRECTION 1 TO THE STAGE-2 AMENDMENT — **THE COUNTS IN S2.2 ARE WRONG. THE FINDING IS NOT.** Dated **2026-09-03**. Version **1.1 → 1.1a**.

> **lines whose number changed above this section: 0** — asserted by execution. **S2.2 IS NOT REWRITTEN.** Its wrong figures are STRUCK BY QUOTE below and left standing in place, per `CLAUDE.md` rule 6: *originals are struck, never rewritten.* A reader arriving at S2.2 must be able to see what it said and what was wrong with it.

**Raised by the `dafoam-supervisor` on his own independent measurement of the parent file, and re-measured by this lane before correcting anything. A disclosure that OVERSTATES a defect is still a wrong record, and the direction of the error does not excuse it.**

### C1.1 What S2.2 says, struck

> ~~"the parent carries the token at **SEVEN** sites, only **FOUR** of which are inside that line range"~~ — **STRUCK. WRONG.**
> ~~"...the header docstring (`:28`), the argparse help string (`:135`), the two `elif` branches (`:394`, `:402`), the totals call (`:399`), and the final else-clause message (`:409`)"~~ — **STRUCK. WRONG**, and note that this enumeration names **six** things while the sentence claims seven: **a census whose own enumeration does not self-add.**
> ~~"Deleting exactly the range §3 names would have left the token at **three surviving sites**"~~ — the *number* three is **CORRECT**; the *fraction* it was presented as (3 of 7) is not.

### C1.2 The correct counts, measured by this lane in the correcting invocation

**The forbidden token is `compute_totals` and ONLY that string** — `so3af2_read.py:72`, `FORBIDDEN_PRODUCER_TOKEN = "compute_totals"`, and §6 NL-2 names that clause and no other.

| quantity | value | lines |
|---|---|---|
| occurrences of `compute_totals` in `so3ar2_runScript.py` | **5** | `:28`, `:135`, `:394`, `:399`, `:409` |
| inside the registered range **394–408** | **2** | `:394`, `:399` |
| **outside** the range — the survivors | **3** | `:28`, `:135`, `:409` |

**The counts are 5 / 2 / 3.**

**THE CAUSE OF THE ERROR, NAMED.** This lane grepped `compute_totals\|check_totals` — **the count of lines matching EITHER token**, which is 7 lines (`:28, :135, :394, :399, :402, :407, :409`) with 4 in range (`:394, :399, :402, :407`). **`check_totals` is not the forbidden token.** `:402` and `:407` carry `check_totals` alone and contain no forbidden token at all. **The figure reported was a measurement of a different quantity from the one NL-2 tests**, and the tell was visible in the record itself: the prose enumerated six items under a heading that said seven. **A census whose own enumeration does not self-add is not to be trusted, and this one was mine.**

### C1.3 ⚠ THE FINDING SURVIVES INTACT — this is a CORRECTION, not a withdrawal

Deleting exactly the range §3 names leaves **3 occurrences** of the forbidden token, so `grep -c` returns **3**, `TOKEN_HITS != 0`, and **NL-2 FIRES ON EVERY LAUNCH OF THIS ITEM, FOREVER** — the item unable to start, on a guard that is right, against a producer that is correct. **The tenth unsatisfiable-by-construction condition is real. It is 3 survivors, not 3-of-7.**

### C1.4 The resolution is an INTERPRETATION, and both readings are stated in full

**It is labelled as an interpretation and not as what the text obviously said**, because resolving an ambiguity in a frozen document in the direction that lets one's own item start is the shape of choosing the reading to fit the answer.

> **READING A — the narrow one.** §3 registers the deletion as *"the `compute_totals` and `check_totals` task branches (`so3ar2_runScript.py:394-408`) and the `of=`/`wrt=` lists they consume"*. Read as a line range and nothing more, the deletion touches `:394` and `:399` only, and `:28`, `:135` and `:409` survive.
>
> **READING B — the wider one, ADOPTED.** §6 NL-2 refuses if the token appears *"anywhere in it"*, and §3's own words call that clause *"the structural half of the no-gradient promise (§3)"*. On this reading the two clauses are **one instrument described twice**, the promise being *"produces no gradient number at all"* — which a docstring cannot violate and a deleted branch cannot satisfy by halves. Every occurrence goes.

**THE TEST READING B HAD TO PASS, and it is not that it makes the item runnable.** *Does the wider deletion change any measured quantity, any gate, any threshold or any label?* **The three extra occurrences are a module docstring line, an argparse help string, and an error message in the else-branch. NOT ONE IS EXECUTABLE GRADIENT CODE.** Deleting them changes no computation the producer performs and no number the reader reads. **The wider reading repairs the document's EXPRESSION, not its CONTENT, and that is the only ground on which it is admissible.**

**And NL-2 keeps its full discriminating power** — reintroduce the token by any future edit and it fires. **That is proved rather than asserted**: the pin census drives the token clause **by name**, with the producer's md5 pin moved onto the tainted bytes so the md5 clause passes and the token clause is what fires. Without that control the leg would have passed for the wrong reason, and that single control is what makes this resolution safe.

### C1.5 Registered as a carried-forward defect

**The §3/§6 NL-2 discrepancy is a defect OF THE FROZEN DOCUMENT, binding on any successor**, exactly as SO-3D's §5-versus-§8 contradiction is. **No frozen text is edited by this correction or by the amendment above it.**

**Second contradiction inside a frozen registration in one day, and the fourth this lab has met** — after heat-transfer's T8 §12 axis-extrapolation, K0d's odd cell count, and SO-3D's §5/§8. Carried upward as a class, not as a fourth isolated incident.

### C1.6 Unchanged by this correction

Every pin in S2.1, the producer's bytes, the launcher, the pin census and its 14/14, the reader's 17/17, the residual-history refusal of S2.3, the NL-3 split of S2.4, and every prediction, band, cap, label and NO-LAUNCH rc. **NOT ARMED. NOT ENQUEUED. ZERO SOLVER CORE-MINUTES. SUBMISSIONS PARKED.**

**END OF CORRECTION 1.**

---

## ADDENDUM 1 — THE MESH ARM HAD NO STAGING STEP AT ALL. Dated **2026-09-03**. Version **1.1a → 1.2**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**⚠ THIS ITEM HAS RUN A CONTAINER.** The MESH arm launched 2026-09-03T21:48:15Z and exited **rc=127** in 1 second, **0.0167 core-min**, named as **waste**. This addendum is lawful after that container because **it moves no gate, no threshold, no prediction, no band, no cap and no label**, and because every change it makes **can only ever refuse MORE, never less**.

### A1.1 The defect — and it is not a missing file

`so3af2_run_arm.sh` created the arm directory with `mkdir -p`, mounted it, and told the container to run `./preProcessing.sh` inside it. **There was no `cp`, no `rsync`, no `tar`, no symlink and no source constant for the MESH arm anywhere in the file.** The run root confirms it from the other end: `MESH/` contained `checkMesh.log` and nothing else, and that file exists only because the redirect created it.

> `bash: line 1: ./preProcessing.sh: No such file or directory`

**The MESH arm could never have run, at any budget, on any box.** `rc=127` is bash saying *command not found*, and it was right. **Eleventh unsatisfiable-by-construction condition of the day; third in this item's lineage.**

### A1.2 ⚠ AND THE SIBLING BRANCH STAGED CORRECTLY — the part that should sting

**The XM arm stages its producer at `:199`. The MESH arm staged nothing.** The author thought about staging, implemented it for one arm, and did not for its neighbour. **That is the `A1ZE` `occ_wait` finding of `S-34` §2 in the same shape — a pattern applied to one branch and not the sibling beside it — twice in one night, in two items, by different hands. It is invisible to every guard we write, because each branch looks correct in isolation.**

### A1.3 THE GENERALISATION, WHICH IS THE REAL FINDING

**All four NO-LAUNCH guards passed and the image digest verified — and every one of them checks an INSTRUMENT, not an INPUT.** Producer md5, forbidden token, reader pin, image digest: the launcher verified everything about the tools and nothing about whether the case was there. **A guard set that checks every instrument and no input will happily launch a container into an empty directory, and here it did.** `A1WRT`'s missing FFD was the same hole and was *masked* by its controlDict abort; here nothing masked it and it cost a container start.

### A1.4 The repair — the staging source, and why THIS source

**`MESH_SRC = /home/ubuntu/certonomous-runs/CURRICULUM-SO3aR2-a1-naca0012-alpha-multipoint-gradient/base`**, pinned by a **tree manifest** `MD5_MESH_SRC_MANIFEST = b7bf0eca3185b7d9af93e61ca122201b` over sorted relative paths **and** content hashes, so a moved file, a renamed file and a changed byte are all visible where a `md5sum *` would see none of them. **Asserted on BOTH SIDES of the copy** — source before, staged tree after.

**Why this source and not another, stated rather than assumed.** §3 registers this item's producer as *derived from* `curriculum_SO3aR2/so3ar2_runScript.py`, so SO-3aR2's own case skeleton is the same lineage and the same case. It carries **exactly 7 entries and 21 files** — `0.orig FFD constant genAirFoilMesh.py preProcessing.sh profiles system` — and **no `constant/polyMesh` and no `0/`**. SO-2MR's skeleton was compared and is **byte-identical as a tree**, so the choice is not load-bearing between the two.

**The staged SET was derived from `preProcessing.sh`'s OWN BYTES, not from the error message.** It runs `python genAirFoilMesh.py` (needs `genAirFoilMesh.py`, `profiles/`), then `plot3dToFoam`, `autoPatch`, `createPatch -overwrite`, `renumberMesh -overwrite` (need `system/`, `constant/`), then `cp -r 0.orig 0` (needs `0.orig/`). **`rc=127` names the FIRST missing thing, never the last.**

**G-COLD, and it guards the opposite error.** Staging *too much* is worse than staging nothing: the parent's own `case/` is a POST-RUN directory carrying `constant/polyMesh` — **the very thing this arm exists to produce** — so copying it would give a mesh arm that inherits a mesh and reports success. The launcher **refuses** if the source carries `constant/polyMesh` or `0/`.

### A1.5 The staging precondition — rc **9**, and it is NOT a fifth NO-LAUNCH branch

**§6's taxonomy of four branches and their rcs 3/4/5/6 is UNCHANGED in what it refuses.** The new assert has its **own rc 9** and its own file `NOLAUNCH_STAGING.txt`, distinct from those four, from the producer's exit **7**, and from the cap's exit **8**. **A change that can only ever refuse MORE is not a weakening, and that is the ground on which it is lawful after a container has run.**

It asserts the working directory contains **the set** `preProcessing.sh genAirFoilMesh.py profiles system constant 0.orig`, that `preProcessing.sh` is **executable** (a present-but-not-executable script answers 126, not 127), and on success **NAMES WHAT IT FOUND** and the file count — not a bare success line.

### A1.6 A taxonomy error the census exposed, repaired in the same pass

A failed `docker run` was reusing **`NOLAUNCH_ROOT.txt` / rc 3**, so *"the run root already exists"* and *"the container could not be started"* were **indistinguishable to any reader of the rc**. It now has its own `NOLAUNCH_DOCKER.txt` / **rc 10**.

### A1.7 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_run_arm.sh` | `353f9936ef2c08a33c19a1ade8adaecd` | **RE-PINNED**; supersedes `9dec28b7119c901c68d2399d0c3248c2` |
| `so3af2_pin_selftest.sh` | `e55c6c9ce868eca8bfb777e323cecec0` | **RE-PINNED**; supersedes `039e18f3775e837ac88ed84c34aabf6e` |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED** — the frozen reader is not touched |
| `so3af2_runScript.py` | `4359b9b7c04a81b9e56231481f4e0ccb` | **UNCHANGED** by this addendum |

**Census re-driven: 18 legs, PASS 17, FAIL 1** — the single FAIL is `NL-3-OUTSIDE` reporting the launcher md5 not yet pinned, which **this table is what fixes**; it is re-driven to 18/18 in the committing invocation and the evidence file carries that run. New legs: the staging manifest clause, the precondition clause **driven BY NAME with the source re-pinned onto doctored bytes so the manifest clause passes and the precondition clause is what fires**, and staging added to the all-guards-satisfiable leg.

**Two census defects found and repaired in this pass, both this lane's own.** (i) The docker stub refused *every* call including `image inspect`, so the digest guard fired first and **every leg beyond it was unreachable** — the suite would have tested four guards and silently skipped the rest while reporting PASS. The stub now answers **only** `image inspect` and refuses everything else, `docker run` included. (ii) The safety leg asserted the real run root was **ABSENT** — true at the Stage-2 amendment and made **false** by the daemon's launch. An assertion that only holds before the item's first container is not a safety property of the census; it now asserts the root's **manifest is unchanged across the run**, which is what this file actually owns.

### A1.8 ⚠ XM MEASURED, NOT ASSUMED — and it is WORSE than the hypothesis

The supervisor predicted XM would carry the same defect *"in a milder form"* and instructed that it be measured. **Measured, it is more severe: four distinct defects, and XM MUST NOT BE QUEUED.**

1. **XM stages one file into an otherwise empty directory.** The producer needs a full case per operating point: `gridFile = os.path.join(os.getcwd(), RUN_DIRS[point])` gives `XM/mp0`, `XM/mp1`, `XM/mp2`, and `OM_DVGEOCOMP(file="FFD/wingFFD.xyz")` is cwd-relative. **Three full case copies plus the FFD, not one directory.**
2. **⚠ THE PER-POINT DIRECTORIES LAND WHERE THE FROZEN READER DOES NOT LOOK.** The producer creates `XM/mp<i>`; the reader's F3 reads `read_run_dirs(os.path.join(root, "XM", "case"))` — **`XM/case/mp<i>`**. The reader is **FROZEN and unchanged since 2026-08-31**, so this cannot be repaired there, and F3 would score MISS on a separation that had actually worked.
3. **THE ARTEFACT PATH IS WRONG, AND IT IS THIS LANE'S OWN DEFECT IN THE PRODUCER.** It writes `os.path.join(os.getcwd(), "XM")` with cwd already `/mnt/XM` — **`<root>/XM/XM/so3af2_M.json`, one nested `XM` too many** — while the reader reads `<root>/XM/so3af2_M.json`.
4. **NOTHING INVOKES THE READER.** `so3af2_read.py` is *pinned* by the launcher and *never called* by it or by anything else. **The item's entire scoring instrument is never run**, and no registered artifact fixes what `--root` it would be given — which is also why findings 2 and 3 cannot be resolved by choosing a convenient `root`.

**No XM repair is attempted here.** Findings 2 and 4 bear on the frozen reader's contract and are the supervisor's to rule on before any XM instrument is written.

### A1.9 What is unchanged

Every prediction F1–F5, every band, both caps, the ceiling, the memory floor, the four NO-LAUNCH branches and their rcs, the plant constants `K_F = 2.0` and `band_REP = 1.0e-4 %`, and **§0.2 in full**. The MESH arm's verdict is **PENDING**; nothing is scored; **waste 0.0167 core-min named as waste and never absorbed into a ratio**. **NOT RE-FIRED. XM NOT QUEUED. SUBMISSIONS PARKED.**

**END OF ADDENDUM 1.**

---

## ADDENDUM 2 — FINDING 4 WAS OVERSTATED AND IS CORRECTED; THE PRODUCER NOW CONFORMS TO THE FROZEN READER'S CONTRACT. Dated **2026-09-03**. Version **1.2 → 1.3**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`. **ADDENDUM 1 §A1.8 IS NOT REWRITTEN**; its overstated sentences are struck by quote below and left standing in place (`CLAUDE.md` rule 6).

**Moves no gate, no threshold, no prediction, no band, no cap and no label.**

### A2.1 ⚠ CORRECTION — ADDENDUM 1's finding 4 was one size too large

> ~~"**NOTHING INVOKES THE READER.** `so3af2_read.py` is *pinned* by the launcher and *never called* by it or by anything else. **The item's entire scoring instrument is never run**"~~ — **STRUCK. WRONG.**
> ~~"an item whose reader is never invoked cannot produce a reading at all"~~ — **STRUCK. WRONG.**

**POST-HOC GRADING IS THIS FAMILY'S NORM, AND THE EVIDENCE IS ANOTHER ITEM'S LAUNCHER.** `a1wrt_run_unit.sh:768`, verbatim:

> `NOTE: this launcher does not GRADE.  a1wrt_read.py is the frozen grading` / `path and reads G-PATCH clause 3, G-COMPLETE, G-CAPS, G-REPRO and` / `G-PATCHPAIR off these logs afterward.`

and `:27`: the rc line *"is read AFTER, by `a1wrt_read.py`"*. **Measured by this lane in the correcting invocation: that launcher makes ZERO invocations of its reader** and references it only in prose. **A launcher that pins its reader and does not call it is following the pattern, not breaking it**, and `so3af2_run_arm.sh:126-131` uses `` for exactly what the reference is for — existence, md5 pin, `SO3AF2_NL3_PASS`.

**WHAT SURVIVES IS THE NARROWER CLAUSE, AND IT IS REAL: no registered artifact fixes what `--root` the reader receives.** The freeze pins the reader, records its 17/17 selftest under both interpreters and names its constants, and **nowhere states the grading invocation or its root.** That is a specification gap, not an unscoreable item, and §A2.3 closes it.

**AND THE PATTERN IS NAMED BECAUSE IT IS THE SECOND TIME TONIGHT.** The token count was reported as 7/4 when it was 5/2/3; finding 4 was reported as *"never run"* when it was *"root unspecified"*. **Twice this lane measured a real defect and reported it one size too large.** *A disclosure that OVERSTATES a defect is still a wrong record, and the direction of the error does not excuse it.* The cure is the one already named — add up your own claim before reporting it — plus a second: **check whether the thing you are calling broken is how every sibling item works.**

### A2.2 The two path mismatches — CONFIRMED, and the producer conforms

Both confirmed against the frozen reader by both the supervisor and this lane:

| | the reader (FROZEN, `d5f4149d…`, unchanged since 2026-08-31) | the producer, before |
|---|---|---|
| artefact | `:284` `os.path.join(root, "XM", "so3af2_M.json")` → `<root>/XM/so3af2_M.json` | `<root>/XM/**XM**/so3af2_M.json` — one nested `XM` too many |
| run dirs | `:321` `read_run_dirs(os.path.join(root, "XM", "case"))` → `<root>/XM/case/mp<i>` | `<root>/XM/mp<i>` |

**F3 would have scored MISS on a separation that had actually worked — a confident negative on a working mechanism.**

**RULING APPLIED: THE PRODUCER CONFORMS TO THE FROZEN READER'S CONTRACT, NEVER THE REVERSE.** The reader is not touched. The producer is this item's own Stage-2 artefact and is corrected.

**AND THE PATHS ARE DERIVED, NOT TRANSCRIBED** — the `a1wrt_controldict.py` shape. Transcribing would put the same literal in two files and let a future edit to one silently reopen exactly this defect. The producer parses the **staged reader's own bytes** with `ast` and refuses on anything not uniquely determined. The launcher stages the reader beside the producer for the XM arm; its md5 is verified against the pin at NL-3 first, so what is parsed is the frozen reader and not some other file of that name.

> **⚠ AND THE FIRST DERIVATION RULE WAS WRONG, CAUGHT BY ITS OWN REFUSAL.** A first draft took the case path to be *"the `os.path.join(root, …)` that is not a `.json`"*. Driven against the real reader it **REFUSED**: there are **three** — `<root>/XM/XM.log`, `<root>/XM` and `<root>/XM/case`. **The refusal was right and the rule was wrong — it used a PROXY for the quantity instead of the relation that defines it**, which is the same disease as the token alternation of CORRECTION 1. The case path is now identified by its **consumer**: the argument of the call to `read_run_dirs`, the function whose result F3 is scored from, and nothing else.

**Driven, both directions:** against the real reader it derives `['XM','so3af2_M.json']`, `['XM','case']`, `['mp0','mp1','mp2']` — **matching the reader's own lines exactly** — and it **REFUSES 4 of 4** on an absent reader, a removed `RUN_DIRS`, a second `.json` join and a second `read_run_dirs` call.

**A missing case directory now REFUSES BY NAME** (`CASE_DIRECTORY_ABSENT`, exit 9) instead of failing somewhere inside DAFoam. **ADDENDUM 1 finding 1 — the XM arm stages one file into an otherwise empty directory — is NOT repaired here**, and this refusal is what makes it legible rather than a crash.

### A2.3 The `--root` gap, closed

**THE GRADING INVOCATION IS REGISTERED HERE AND WAS NOT REGISTERED BEFORE:**

> `python3 so3af2_read.py --root /home/ubuntu/certonomous-runs/CURRICULUM-SO3aF2-a1-naca0012-multipoint-feasibility --out <out>`

**`--root` is the ITEM'S RUN ROOT** — the directory the launcher mounts at `/mnt` — so the reader's `os.path.join(root, "XM", …)` resolves to the same paths the producer now writes. **It is run AFTER the arms, off their artefacts, by the lane, and NOT by the launcher** — the A1WRT pattern of §A2.1. Registering it fixes nothing that was moving and closes a gap that was genuinely open.

### A2.4 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **RE-PINNED**; supersedes `4359b9b7c04a81b9e56231481f4e0ccb` |
| `so3af2_run_arm.sh` | `ec02bf5b220f7e72393c71604e5af6eb` | **RE-PINNED**; supersedes `353f9936ef2c08a33c19a1ade8adaecd` |
| `so3af2_pin_selftest.sh` | `a86587b43dfcaba9acc1ba7102576971` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |

**Census: 20 legs, PASS 20, FAIL 0, NOT RUN 0** in the committing invocation, with two new legs driving the path derivation — one that it matches the reader, one that it refuses 4/4. The producer carries **0 `assert` statements** and **0 occurrences of the forbidden token**, both re-measured.

### A2.5 Unchanged

F1–F5, every band, both caps, the ceiling, the memory floor, the four NO-LAUNCH branches and their rcs, the staging precondition (9), the docker-start rc (10), the plant constants, and **§0.2 in full**. MESH **PENDING**, nothing scored, **waste 0.0167 core-min** named as waste. **NOT RE-FIRED. XM NOT QUEUED. SUBMISSIONS PARKED.**

**END OF ADDENDUM 2.**

---

## ADDENDUM 3 — THE ARM COMMAND NEVER LOADED THE DAFoam ENVIRONMENT. Dated **2026-09-03**. Version **1.3 → 1.4**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label.** An environment assertion can only ever refuse **more**.

### A3.1 The second rc=127, and it is a different condition from the first

MESH r2 launched 2026-09-03T22:12:06Z. **The staging repair worked**: 2 files became 22, the manifest matched on both sides, and the precondition named what it found. `preProcessing.sh` was staged, executable, and **ran** — then exited at its own first guard:

> `OpenFOAM environment not found, forgot to source the OpenFOAM bashrc?`
> `bash: line 1: checkMesh: command not found`

**Both lines are one cause: the arm command never sourced the DAFoam environment.** And `bash -lc` does not supply it — a non-interactive login shell reads `/etc/profile` and the first of `~/.bash_profile` / `~/.bash_login` / `~/.profile`, **not `~/.bashrc`**, which is where a DAFoam image's environment hangs.

**MEASURED: the string `source /home/dafoamuser/dafoam/loadDAFoam.sh` appears 110 times across this family's drivers, and 0 times in this launcher.** `a1wr_chain_driver.sh:173` — the driver that ran the alpha sweep this ladder is built on — carries it explicitly.

### A3.2 ⚠ THE SAME CLASS AS THE FIRST ABORT — and that is the finding

The first was **inputs**: nothing staged. This is **environment**: nothing sourced. **Both are things the arm needs that are not the instrument, and all four NO-LAUNCH guards check an instrument** — producer md5, forbidden token, reader pin, image digest. **A guard set that verifies every instrument and no precondition will launch a container into an empty directory, and then into an unloaded environment.** Twice, in one item, in one hour.

**And it is the THIRD appearance of one specific shape**: a pattern known in this family, applied in one place and not its neighbour. `A1ZE`'s `occ_wait` handled an unreadable `MemAvailable` one line above a `docker ps` census that did not; `:199` staged the XM producer while MESH staged nothing; A1WR's driver sources the environment and this one did not. **Three items, three authors, one shape — and each branch is perfectly correct read on its own.**

### A3.3 The repair — both arms, in one pass

**THE LOADER PATH IS DERIVED FROM A1WR'S DRIVER BYTES, NOT RETYPED.** `A1WR_DRIVER` is pinned at `9bff59b63509e76d5dfa373a42a47074`; the launcher greps the distinct `source …loadDAFoam.sh` values out of it, **counts them, and refuses on anything but exactly one** — *take the first match* is the trap `D6RF-BLOCKING-1` was paid for. Measured: **1 distinct value**, `/home/dafoamuser/dafoam/loadDAFoam.sh`. A drift in A1WR's driver **refuses** rather than silently splitting the two items.

**AND THE `source` IS NOT TRUSTED.** `so3af2_env_assert.sh` runs inside the container ahead of every arm: it sources the loader, then **interrogates the environment itself** and refuses by name — **ENV-1** loader not a file, **ENV-2** source returned non-zero, **ENV-3** `checkMesh` not on `PATH`, **ENV-4** `FOAM_APPBIN` empty, **ENV-5** `WM_PROJECT` empty. **ENV-5 is the load-bearing one: `$WM_PROJECT` is the exact variable `preProcessing.sh` tests in its own first three lines**, so the assertion checks the variable the arm's own script checks rather than one this lane chose. It then `exec`s the arm command. **rc 11**, distinct from 3/4/5/6 (NO-LAUNCH), 7 (producer), 8 (cap), 9 (staging) and 10 (docker start).

**BOTH ARMS GO THROUGH IT.** Each arm now writes its command to `so3af2_cmd.sh` — A1WR's own shape — and the single `CMD` is `bash /mnt/so3af2_env_assert.sh $LOADER bash /mnt/$ARM/so3af2_cmd.sh`. **The two arms differ only in their command file.** Repairing MESH and rediscovering this on XM would have been the sibling-branch defect a fourth time.

**Driven both ways on the HOST, no container needed** — the script sources a loader and interrogates the environment, so a fake loader exercises the real code path: absent loader → **rc 11, ENV-1 by name**; a loader that loads nothing → **rc 11, ENV-3 by name**; a good loader → **rc 0, `SO3AF2_ENV_OK` printed, and the arm command actually RAN** (the `exec` is verified, not assumed).

### A3.4 ⚠ A CENSUS BLINDNESS FOUND IN THE SAME PASS, AND IT IS THE WORST OF THE THREE

The pin census enumerated pins with `^MD5_[A-Z_]+=`. **`MD5_A1WR_DRIVER` carries a digit and was therefore never enumerated at all** — and the census printed **`driven=4 exist=4 — EQUAL, so every pin is driven as a COUNT`** while **five** pins existed.

> **THE EQUALITY WAS TRUE AND VACUOUS, BECAUSE BOTH SIDES OF THE COMPARISON USED THE SAME BROKEN REGEX.** A census that enumerates with the same rule it counts with **cannot detect its own blindness**. This is the instrument whose entire purpose is to make *"every pin is driven"* a count rather than a claim, and it was making a claim.

It was found **only** because a newly added pin failed to appear — the same accident that surfaced the two earlier coverage lies. **That is three coverage lies in one night, in one suite, none visible in its own summary line**, and it is why the invariant registered at §A3.6 is registered *because we have no way to detect these except by accident*, not as a nice-to-have.

Repaired to `^MD5_[A-Z_0-9]+=`; the census now reports **driven=5 exist=5**.

### A3.5 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_env_assert.sh` | `68811e246aed84778fe2878f8538d726` | **NEW** — the environment assertion |
| `so3af2_run_arm.sh` | `209898b426ccce9d5e267bf0a7506e8b` | **RE-PINNED**; supersedes `ec02bf5b220f7e72393c71604e5af6eb` |
| `so3af2_pin_selftest.sh` | `a0ac8f6b2c21e4a94fedf127c0ba25a6` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **UNCHANGED** by this addendum |
| `a1wr_chain_driver.sh` | `9bff59b63509e76d5dfa373a42a47074` | **ANOTHER ITEM'S FILE, PINNED AND NOT TOUCHED** — the loader path is derived from it |

**Census: 26 legs, PASS 26, FAIL 0, NOT RUN 0** in the committing invocation.

### A3.6 The guard-suite invariant, REGISTERED AND NOT BUILT

**Registered for this family's NEXT guard suites, forward-only, no retrofit of landed suites, and NOT started now** — building instrument infrastructure must not displace items in flight. Stated in the lane's own words and adopted by the supervisor:

> *Both of tonight's census failures were **coverage lies, not logic errors**: a leg that passes for a reason other than the one it claims, and a leg that is unreachable while reporting PASS. Neither is visible in a suite's own summary line. The check worth adding is not another control but an **invariant on the suite itself**: every leg must be shown to fail for its own named reason, not merely to fail.*

**It is registered BECAUSE WE HAVE NO WAY TO DETECT THESE EXCEPT BY ACCIDENT** — all three surfaced only because a new leg happened to fail carrying someone else's message, or failed to appear at all. **Luck is not a control.** It is the natural completion of `CLAUDE.md` rule 3: rule 3 proves a *reader* can see a non-zero; this proves a *control* fails for its own reason. **Sent to the chief as a lab-wide candidate**, since it bears on every team's comparators.

### A3.7 Also registered: a capacity figure is quoted with its clock or not at all

The supervisor's 22:07:46Z reading of 90.5 % busy predicted this row would queue; by the 22:12:06Z tick the box was **72.2 %**, `D6RF2` held on the **rank arithmetic** rather than the ceiling, and the 1-rank row **launched**. He flagged the staleness in advance, which is not the same as it being current. **The lane at the tick measures; not the supervisor minutes before.**

### A3.8 Unchanged

F1–F5, every band, both caps, the ceiling, the memory floor, the four NO-LAUNCH branches and their rcs, the staging precondition (9), the docker-start rc (10), the plant constants, and **§0.2 in full**. **ADDENDUM 1 finding 1 — XM stages one file into an otherwise empty directory — is STILL NOT REPAIRED and XM is NOT QUEUED.** MESH **PENDING**; cumulative waste across both attempts **0.0167 core-min**, named as waste and never absorbed into a ratio. **NOT RE-FIRED. SUBMISSIONS PARKED.**

**END OF ADDENDUM 3.**

---

## ADDENDUM 4 — `set -u` KILLED THE ENVIRONMENT ASSERTION FROM INSIDE, AND THE INSTRUMENT SAID NOTHING ABOUT ITSELF. Dated **2026-09-03**. Version **1.4 → 1.5**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label.** Both changes can only ever refuse **more** or report **more**.

### A4.1 The third rc, and it was the instrument rather than the case

MESH r3 launched 22:24:16Z and returned **rc=1** — outside this item's entire registered set. The loader derived correctly (1 distinct value from A1WR's pinned bytes), staging was intact at 22 files, and then:

> `/home/dafoamuser/dafoam/OpenFOAM/OpenFOAM-v2506/etc/bashrc: line 180: WM_PROJECT_DIR: unbound variable`

**`so3af2_env_assert.sh` ran `source "$LOADER"` with `set -u` ACTIVE.** OpenFOAM's own `etc/bashrc` references `WM_PROJECT_DIR` before setting it — **entirely normal for an init script** — so bash aborted **inside the source**, exit 1, **before any ENV-n check could execute**. The failing line is in the image's file; **the cause was in mine.**

**And A1WR's driver carries `set -uo pipefail` too, at `:27`, and works** — because its `source` at `:172-173` runs inside a **fresh `bash -lc` in the container**, which does not inherit the host script's shell options. **A1WR's `set -u` and A1WR's `source` are in different shells on different machines. Mine were in one shell.** Verified by this lane in the repairing invocation.

### A4.2 ⚠ THE SYMMETRY — one shell option, two items, opposite causes, identical signatures

| | what was unbound | signature |
|---|---|---|
| **A1WRT**, rc 127 | a variable **we** needed — `FFD_SRC` — referenced and never defined | bare bash error, no named refusal, **empty evidence file** |
| **SO3aF2**, rc 1 | a variable a **third party** legitimately leaves unset, referenced by its own init script | bare bash error, no named refusal, **no ENV line at all** |

**`set -u` is the right default and it is exactly wrong across a foreign init script.**

### A4.3 Repair 1 — `set -u` relaxed across ONE line, and restored immediately

`set +u; source "$LOADER"; SRC_RC=$?; set -u`, disclosed in the file with the reason: **a third-party init script's unbound references are expected behaviour, not a defect to be caught.**

**THIS WEAKENS NOTHING.** ENV-1 through ENV-5 are the actual verification and **every one runs with `set -u` restored**. The relaxation covers exactly one line, whose failure is now **reported by ENV-2's `SRC_RC`** instead of by a dead shell.

**Driven, with the r3 shape reproduced exactly**: a fixture loader that reads an unset variable before setting it — OpenFOAM's own shape — **aborts under the old code path with `unbound variable`** and under the repaired one returns **rc 0, prints `SO3AF2_ENV_OK`, and the arm command RUNS.**

### A4.4 Repair 2 — ENV-0, the silent-exit trap. rc **12**

On 22:24:16Z the instrument **neither passed nor refused**. It emitted no ENV-n refusal and no `SO3AF2_ENV_OK`.

> **THAT IS THE THIRD MEMBER OF TONIGHT'S COVERAGE-LIE FAMILY AND THE ONE THE OTHER TWO DO NOT COVER: a leg that passes for the wrong reason, a leg unreachable while reporting PASS — and now a leg that is SILENT rather than wrong. A silent instrument is the hardest of the three to notice, because there is nothing to read.**

**THE RULE IT ENFORCES: an instrument must always say which of its outcomes occurred, INCLUDING "neither".** An `EXIT` trap fires on any exit that reached neither a named refusal nor the OK line, prints **the last checkpoint reached** so the silence itself becomes evidence, and exits **12** — distinct from 3/4/5/6 (NO-LAUNCH), 7 (producer), 8 (cap), 9 (staging), 10 (docker start) and 11 (environment refusals).

**All seven exit paths mark the verdict as emitted** — the usage error, ENV-1 through ENV-5, and the OK path — enumerated from the file's own bytes rather than counted from memory. *(A first count of "6 expected" was this lane's miscount and is corrected here rather than left in a comment.)*

**Driven both ways, and the second leg is the one that matters: a loader that exits mid-source produces `rc 12`, the line `ENV-0 ASSERT TERMINATED WITHOUT VERDICT`, and the last checkpoint reached — and the arm command DOES NOT RUN.** That leg would have caught r3 on its own.

### A4.5 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_env_assert.sh` | `a5b7fcae05aab420d94623582d45f897` | **RE-PINNED**; supersedes `68811e246aed84778fe2878f8538d726` |
| `so3af2_run_arm.sh` | `0e9198ac111bcea18168306fe993ee0d` | **RE-PINNED**; supersedes `209898b426ccce9d5e267bf0a7506e8b` |
| `so3af2_pin_selftest.sh` | `c0629f8c01965f574284344189d9086a` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **UNCHANGED** |

**Census: 29 legs, PASS 29, FAIL 0, NOT RUN 0** in the committing invocation.

### A4.6 The probe regime, re-checked against its own three clauses

**All three still hold**: the failure was **cheap** (0.0000 core-min, 0.12 s), the abort was **legible** (one line naming its own file and line number), and **the arm produced no number.** Cumulative waste across three attempts remains **0.0167 core-min**, named as waste and never absorbed into a ratio. **The moment this arm computes anything, the probe regime ends and the reading is the supervisor's.**

### A4.7 Unchanged

F1–F5, every band, both caps, the ceiling, the memory floor, the four NO-LAUNCH branches and their rcs, the staging precondition (9), the docker-start rc (10), the environment refusals (11), the plant constants, and **§0.2 in full**. **ADDENDUM 1 finding 1 — XM stages one file into an otherwise empty directory — is STILL NOT REPAIRED and XM is NOT QUEUED.** MESH **PENDING**. **NOT RE-FIRED. SUBMISSIONS PARKED.**

**END OF ADDENDUM 4.**

---

## ADDENDUM 5 — THE MESH ARM IS COMPLETE. Dated **2026-09-03**. Version **1.5 → 1.6**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label. NO MESH GATE IS ADDED — see §A5.3.**

### A5.1 What the arm did

`SO3aF2_MESH_r4` launched 2026-09-03T22:34:26Z and returned **rc = 0**, wall **3 s**, **0.0500 core-min** against a registered cap of 3.0 and an item ceiling of 9.0. `cap_exceeded=0`.

The environment assertion passed for the first time, with paths resolved inside the container:

> `SO3AF2_ENV_OK loader=/home/dafoamuser/dafoam/loadDAFoam.sh checkMesh=…/platforms/linux64GccDPInt32Opt/bin/checkMesh FOAM_APPBIN=…/platforms/linux64GccDPInt32Opt/bin WM_PROJECT=OpenFOAM`

`MESH/` carries `0/`, `constant/polyMesh/` with **8 files**, `volumeMesh.xyz`, `surfaceMesh.xyz`, `logMeshGeneration.txt` and a 3610-byte `checkMesh.log` ending `Mesh OK.` and `End`.

**Completion holds on every limb available to this arm**: `rc = 0`, an `End` line, the mesh written, and `checkMesh` reporting `Mesh OK.` on its own criteria. **`Mesh has 3 solution (non-empty) directions (1 1 1)` is the `symmetry` configuration**, which is what DAFoam requires.

### A5.2 ⚠ THE RULING — MESH IS COMPLETE. IT IS NOT A RESULT, BECAUSE NOTHING GRADES IT

**Ruled by the `dafoam-supervisor`, 2026-09-03.** No gate fires on this arm. The registration carries **no** aspect-ratio, non-orthogonality, skewness or `checkMesh` threshold: **`MESH` is a `SCRIPT` arm whose product is the mesh, and F1–F5 are all XM's.**

- **THE ITEM STAYS `PENDING`.** XM has not run and the gates that decide this item have not been reached.
- **The mesh metrics in `checkMesh.log` are an OBSERVATION and are NOT a verdict.** They are recorded as an observation and nothing in this lab may quote them as a finding.
- **`Mesh OK.` is `checkMesh`'s judgement against its own defaults, not this lab's against a pre-registered threshold, and the two are not the same thing.**

### A5.3 ⚠ A REGISTERED LIMITATION — the registration gates the OUTCOME and not the MESH it rests on

**Nothing in this item would have caught a bad mesh.** F1–F5 gate XM's readings; the mesh those readings are computed on is gated by nothing. **It happens to be a good mesh — and "it happens to be fine" is not a gate.**

**That is tonight's theme one level up.** The NO-LAUNCH guards check instruments and not inputs; the registration checks outcomes and not the mesh they rest on. Same shape, different altitude.

> **NO MESH GATE IS ADDED TO THIS ITEM, AND THAT IS DELIBERATE.** Adding a threshold after seeing the numbers is choosing the threshold to fit the answer, and it is the one thing that would turn a clean arm into a compromised one. **The limitation is registered FORWARD-ONLY: a successor that gates its mesh should exist; this item is not retrofitted to have one.**

### A5.4 The delivery path, four attempts, and what closed

| # | rc | condition | closed by |
|---|---|---|---|
| 1 | 127 | **no staging step at all** — `mkdir -p` then a container told to run a script never put there | ADDENDUM 1: staging from a lineage-matched source, tree-manifest asserted both sides, G-COLD, precondition rc 9 |
| 2 | 127 | **environment never sourced** — and `bash -lc` does not supply it | ADDENDUM 3: loader derived from A1WR's pinned bytes, `so3af2_env_assert.sh`, rc 11 |
| 3 | 1 | **`set -u` aborted inside the foreign init script**, and the instrument emitted neither outcome | ADDENDUM 4: `set +u` across four lines; ENV-0 trap, rc 12 |
| 4 | **0** | — | — |

**0.0667 core-min for all four attempts combined.** Three real defects in the delivery path, now closed: **inputs, environment, and the shell option that hid both.**

### A5.5 ⚠ XM IS NOT A PROBE — the regime is over and it does not resume

**The cheap-firing regime applied only while the arm produced no number. XM produces numbers and those numbers reach F1–F5.**

> **A wrong precondition on MESH cost two cents. A wrong precondition on XM can produce a plausible F3 MISS on a separation that actually worked** — the exact failure found and repaired in ADDENDUM 2's findings 2 and 3, and the reason the reader's contract is derived rather than transcribed.

XM therefore gets the full treatment **before** it fires: the staged set derived from the producer's own references, every path asserted against the frozen reader's expressions, the guard suite driven under both interpreters, and the supervisor's **check 1 on the changed hunks and check 4 before it is queued**. **ADDENDUM 1 finding 1 is still unrepaired and XM is still NOT QUEUED.**

### A5.6 Unchanged

F1–F5, every band, both caps, the ceiling, the memory floor, every rc in the taxonomy, the plant constants, and **§0.2 in full** — this item never calls `solve_linear`, cannot show SO-3aR's adjoint collision is fixed, and **nothing it measures may be quoted toward it**. **SUBMISSIONS PARKED.**

**END OF ADDENDUM 5.**

---

## ADDENDUM 6 — THE XM ARM STAGES A CASE PER OPERATING POINT. Dated **2026-09-03**. Version **1.6 → 1.7**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label.** **XM IS NOT QUEUED BY THIS ADDENDUM.**

### A6.1 What was wrong — ADDENDUM 1 finding 1

The XM arm staged **one file** into an otherwise empty directory. Measured, it needs **a full case per operating point plus the FFD**: `gridFile = os.path.join(os.getcwd(), RUN_DIRS[point])` and `OM_DVGEOCOMP(file="FFD/wingFFD.xyz")` are both **cwd-relative**, and the frozen reader's F3 reads them at `<root>/XM/case/mp<i>`.

### A6.2 ⚠ WHY THIS ARM GOT THE SLOW TREATMENT AND MESH DID NOT

**The probe regime ended when MESH produced a number, and it does not resume.**

> **A wrong precondition on MESH cost two cents and announced itself. A WRONG PRECONDITION ON XM PRODUCES A PLAUSIBLE `F3 MISS` ON A SEPARATION THAT ACTUALLY WORKED** — a confident wrong answer, which is the only kind this lab cannot recover from cheaply, and the exact failure ADDENDUM 2 found and repaired.

### A6.3 Everything is DERIVED, and each derivation asserts its own uniqueness

| what | derived from | uniqueness |
|---|---|---|
| the FFD path | the **producer's** own `OM_DVGEOCOMP(file=…)` | distinct refs **counted**, anything but 1 refuses |
| `mp0 mp1 mp2` | the **frozen reader's** `RUN_DIRS` list literal | declarations **counted**, anything but 1 refuses |
| the `case` segment | the **frozen reader's own `read_run_dirs` call** | taken from the call whose result F3 is scored from |

**Nothing is transcribed.** A literal in two files is a divergence waiting to happen, and this item has already paid for one.

> **⚠ AND THE FIRST FFD DERIVATION WAS WRONG, CAUGHT ON THE HOST BEFORE ANY CONTAINER.** `sed 's/.\*file="//'` yielded **`FFD/wingFFD.xyz"` — with the closing quote** — so the existence check tested a path that can never exist and **this arm would have REFUSED ON EVERY LAUNCH, FOREVER.** It was found by *driving* the derivation against the real producer instead of trusting it. **That is what the slow treatment bought, and it is the twelfth unsatisfiable-by-construction condition of the day.**

### A6.4 What the arm now stages, and the guards on it

XM consumes **MESH's output** and refuses **by name** if MESH has not run, if `constant/polyMesh/boundary` is absent, or if neither `0/U` nor `0/U.gz` is there. It then builds the frozen reader's own layout:

```
<root>/XM/            producer, reader, so3af2_cmd.sh, XM.log, so3af2_M.json
<root>/XM/case/       FFD/wingFFD.xyz          <- cwd for the producer
<root>/XM/case/mp0..2 one FULL case each       <- gridFile and run_directory
```

**G-COLD per point**, because a warm start is silent otherwise: no `processor*`, no numeric time directory but `0`/`0.orig`, `0/U` or `0/U.gz` present, and `constant/polyMesh/boundary` present. **Each refuses by name at rc 9.**

### A6.5 Driven — 36 legs, PASS 36, FAIL 0, NOT RUN 0

Eight legs are new and all use a **fake MESH output**, so **no container is created**:

- the FFD derivation yields exactly one reference **with no trailing quote** — asserted directly, because that was the defect;
- **XM without MESH** → rc 9, and a second leg proves it refused **naming the missing MESH output** rather than with a generic staging error;
- **XM without `polyMesh`** → rc 9;
- **XM stages the reader's layout** → `case/FFD/wingFFD.xyz` and `case/mp0..2` each with `polyMesh` and `0/`, producer and reader beside them;
- **the layout matches the reader** — the per-point directories sit under `read_run_dirs`' own argument;
- **G-COLD warm start** → rc 9.

### A6.6 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_run_arm.sh` | `e4ae5705cdc367aea19109764ebb1d62` | **RE-PINNED**; supersedes `0e9198ac111bcea18168306fe993ee0d` |
| `so3af2_pin_selftest.sh` | `40691238115c0d1557623e35802f69bd` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **UNCHANGED** |
| `so3af2_env_assert.sh` | `a5b7fcae05aab420d94623582d45f897` | **UNCHANGED** |

### A6.7 What is still owed before XM may fire

**The supervisor's check 1 on the changed hunks and check 4 before it is queued.** **XM IS NOT QUEUED.** The MESH arm stands complete and **NOT A RESULT** (§A5.2); the item stays **PENDING**; F1–F5 are unscored; **§0.2 binds in full** — this item never calls `solve_linear` and nothing it measures may be quoted toward SO-3aR's collision proof. **SUBMISSIONS PARKED.**

**END OF ADDENDUM 6.**

---

## ADDENDUM 7 — THE XM ARM RAN AND REFUSED AT `rc=7`. THE REGISTERED RISK LANDED. Dated **2026-09-03**. Version **1.7 → 1.8**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label. F1–F5 ARE UNSCORED.**

### A7.1 What happened

`SO3aF2_XM` launched 2026-09-03T22:49:31Z at 57.3 % box, and exited **rc = 7**, wall **21 s**, **0.3500 core-min** against a cap of 6.0 which was never approached.

> `SO3aF2 PRODUCER REFUSAL: RESIDUAL_HISTORY_UNAVAILABLE {"scenario": "point0", …}` — `XM.log:1799`

**No artefact was written. That is the correct outcome and it was registered before the first container.**

### A7.2 ⚠ THE RULING — AN INSTRUMENT DECLINING TO MANUFACTURE A FINDING

**Ruled by the `dafoam-supervisor`, 2026-09-03: `rc=7` is the registered risk landing, not a defect and not a crash.**

§A2.3 named this outcome, with its reason, **before any container ran**: a short `residual_histories` list would reach the reader as a **CONVERGENCE DISAGREEMENT** — which §5 F1 defines as *a finding about the multipoint assembly* — when its true cause was the producer failing an attribute lookup. **An infrastructure failure wearing a physics finding's clothes is worse than not running.**

**The item stays `PENDING`. F1–F5 are unscored. The reader was never invoked, because no artefact exists for it to read.**

### A7.3 What held

- The **environment assertion** passed with container-resolved paths (`SO3AF2_ENV_OK`, the whole 277-byte container log).
- The **path contract derived correctly**: `artefact=/mnt/XM/so3af2_M.json case=/mnt/XM/case run_dirs=['mp0', 'mp1', 'mp2']` — matching the frozen reader's `:284` and `:321`.
- **Three primals ran and three `satisfied the prescribed tolerance`.**
- The staging built the reader's layout: `case/FFD`, `case/mp0`, `case/mp1`, `case/mp2`.

**Everything the evening's six addenda were for held.**

### A7.4 ⚠ AN OBSERVATION, EXPLICITLY NOT A SCORE — and the reason it is not

The three per-point directories each carry a **distinct** time directory: **`mp0: 443`, `mp1: 436`, `mp2: 424`.**

**THIS IS A DIRECTORY LISTING. IT IS NOT F3 AND F3 IS UNSCORED.** F3 is scored by `so3af2_read.py` and by nothing else, and the reader was never invoked.

> **IT MUST NOT BE READ BY HAND PRECISELY BECAUSE IT CUTS IN THE DIRECTION WE WOULD LIKE.** Three distinct time directories is *prima facie* what a working separation looks like. **A reader who sees three directory names and concludes the separation worked has composed a verdict out of evidence he found congenial** — which is the same offence as choosing a threshold after seeing the answer, in the flattering direction instead of the unflattering one.

> **AND THE STRONGEST EVIDENCE THAT THE PRODUCER'S REFUSAL WAS PRINCIPLED IS THIS: IT MAY HAVE BLOCKED A READING THAT WOULD HAVE BEEN FAVOURABLE TO US.** An instrument that declines to manufacture a finding **even when the finding it declines to manufacture might have gone our way** is an instrument working correctly.

**§0.2 also binds here in full**: whatever those directories show, this item never called `solve_linear` and nothing about them may be quoted toward SO-3aR's adjoint collision.

### A7.5 Cost, and the waste ruling

**0.3500 core-min** against the **1.20** bracket point; cap 6.0 never approached. Item total **0.4167 core-min** across five launches (0.0667 MESH across four, 0.3500 XM).

> **WASTE: NONE. Ruled by the supervisor.** Every core-minute ran **three converged primals** and produced a **registered refusal that prevented a manufactured finding**. **That is an answer, not a loss** — the same ruling made on A1WRT U1 and for the same reason.

### A7.6 The bounded repair, ordered and NOT YET BUILT

The producer tried **four candidate attribute names** and none carried a residual history. **A fifth guess is the wrong move** — it is the proxy-versus-relation disease this item has met three times: guessing at a **name** when what is needed is the **relation**, i.e. which attribute of the live object actually holds the history.

**Ordered: one cheap diagnostic container that ENUMERATES what the live `<scenario>.coupling.solver` object has** — the available attributes and which are non-empty sequences of the right shape — **and records that enumeration as evidence.** The producer then reads the attribute **measured** to exist, pinned against that measurement rather than chosen from plausible spellings.

**It scores nothing, writes no `so3af2_M.json`, carries its own rc, and is capped well under the 6.0 this arm did not approach.** It lands as its own dated addendum.

### A7.7 Unchanged

F1–F5, every band, both caps, the ceiling, the memory floor, every rc in the taxonomy, the plant constants, and **§0.2 in full**. **SUBMISSIONS PARKED.**

**END OF ADDENDUM 7.**

---

## ADDENDUM 8 — THE ATTRIBUTE CENSUS. A BOUNDED DIAGNOSTIC THAT ASKS THE OBJECT INSTEAD OF GUESSING. Dated **2026-09-03**. Version **1.8 → 1.9**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label. IT SCORES NOTHING.**

*(Drafting note, disclosed because it touched this file: a first attempt to append this section used an UNQUOTED heredoc, so three backtick-quoted names were COMMAND-SUBSTITUTED and landed as empty strings — the "backticks kill the commit" trap, here eating document text instead of a commit message. The malformed append was never committed; the file was restored BYTE-IDENTICAL to its pre-append state, asserted by diff against both the snapshot and HEAD, and this section is appended with a quoted heredoc. Nothing above line 1024 was ever at risk, and that is checked rather than claimed.)*

### A8.1 Why a census and not a fifth guess

The XM arm refused at `rc=7` because the producer tried **four candidate attribute names** for a residual history and none carried one. **A fifth guess is the wrong move.**

> **It is the proxy-versus-relation disease this item has met three times tonight** — the token alternation that measured a superset of what the guard reads, the case path taken as *"the join that is not a .json"*, and now **guessing at a NAME when what is needed is the RELATION: which attribute of the live object actually holds the history.**

**This arm asks the object.**

### A8.2 What it is, and the constraints ARE the registration

`so3af2_attr_census.py` is **derived from the producer**, header byte-identical up to the task branch, so **the model it censuses is the model the producer builds** rather than a re-creation of it. It runs the same `run_model` and then enumerates what `<scenario>.coupling.solver` and its `DASolver` actually expose — every attribute name, its type, whether it is callable, and for anything sequence-shaped its length — writing that census out as **evidence**.

| constraint | how it is enforced |
|---|---|
| **It scores nothing** | no prediction is evaluated, no band applied, no verdict token emitted; F1–F5 belong to `so3af2_read.py` and are untouched |
| **It never writes the graded artefact** | it writes only `so3af2_attr_census.json`, and **after writing it CHECKS `ARTEFACT_PATH` ON DISK and REFUSES if one exists** |
| **Its own rc is 13** | distinct from 3/4/5/6 (NO-LAUNCH), 7 (producer), 8 (cap), 9 (staging), 10 (docker), 11 (environment), 12 (ENV-0) |
| **It computes no gradient** | the header is byte-identical to the producer's, so the gradient branches are absent exactly as they are there; the forbidden token appears **0** times |
| **An unreadable attribute is RECORDED, never skipped** | a silently omitted attribute is exactly the blindness this census exists to remove |

> **⚠ AND A FIRST DRAFT OF ITS OWN BANNER CLAIMED THE GRADED ARTEFACT'S NAME "appears nowhere below" — WHICH WAS FALSE.** It appears three times, in the inherited header and in the path-contract derivation, both kept byte-identical on purpose. **A CLAIM IN A COMMENT IS NOT A PROPERTY OF THE BYTES** — this item's own standing lesson, and the banner said it about itself. The guarantee is now **structural** (the on-disk check above) and **proved by parsing rather than by grepping a comment**: a census leg walks the AST and asserts **no `open()` call targets `ARTEFACT_PATH`**.

### A8.3 Cost

| field | value |
|---|---|
| ranks | **1** |
| **cap** | **2.0 core-min** — **well under the 6.0 the XM arm did not approach.** Basis: XM ran three primals to its refusal for **0.3500 core-min MEASURED**, and this arm runs the same three plus an enumeration |
| point estimate | **0.40 core-min**, [DERIVED from that MEASURED 0.3500], not measured |
| solver core-min | it launches one container; **it produces no graded number** |
| dollars | **DERIVED, NOT MEASURED** at $0.0513/core-h: 2.0 core-min cap = **$0.00171** |
| calibration | owed at completion, **its own row**, not covered by the MESH or XM rows |

### A8.4 Driven — 41 legs, PASS 41, FAIL 0, NOT RUN 0

New legs: the census instrument **pinned and enumerated** by the pin census (**driven=6 exist=6**); **ATTRCENSUS stages its own arm directory** with the instrument, the FFD and `mp0..2`; **its command names its own directory and instrument** and did not inherit XM's; a **drifted census instrument REFUSES** at rc 9; and the **no-graded-artefact guarantee proved by AST**.

> **⚠ AND A LEG CAUGHT A REAL DEFECT IN THE SAME PASS.** The staging evidence lines hard-coded `arm=XM`, so the ATTRCENSUS arm **announced itself as XM** in its own log. **A label that does not track the branch it is in is the sibling-branch defect wearing a different hat**, and it was found by the leg that checked the label rather than the behaviour. The arm name now tracks `$ARM`.

### A8.5 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_attr_census.py` | `2fd479d881f63b529605b3a45d0154f3` | **NEW** |
| `so3af2_run_arm.sh` | `feab8825c8789a5c32625845292e74f9` | **RE-PINNED** |
| `so3af2_pin_selftest.sh` | `a483850797f01c5418adf7448acecbb5` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **UNCHANGED** |

### A8.6 Standing

**NOT QUEUED. NOT FIRED.** Check 1 and check 4 are the supervisor's. The XM arm's `rc=7` stands as the **registered risk landing**; MESH stands **complete and NOT A RESULT**; the item stays **PENDING**; **F1–F5 are unscored**; and **§0.2 binds in full — whatever the census shows, this item never called `solve_linear` and nothing here may be quoted toward SO-3aR's adjoint collision.** **SUBMISSIONS PARKED.**

**END OF ADDENDUM 8.**

---

## ADDENDUM 9 — THE CENSUS OVERRAN ITS CAP AND I STOPPED IT BY HAND. THE CAP COULD NOT STOP IT. Dated **2026-09-03**. Version **1.9 → 1.10**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label. NO ENUMERATION WAS PRODUCED.**

### A9.1 What happened

`SO3aF2_ATTRCENSUS` launched 2026-09-03T23:02:42Z. At **199 s** — against a registered cap of **2.0 core-min = 120 s wall at ranks 1** — it had produced **208 bytes of log**, static for roughly two minutes, at **1.55 % CPU**. **The cap was already exceeded by 66 %.**

**I stopped it.** `CLAUDE.md` rule 12: *an overrun **stops** the run; it does not get a new budget.*

Final: **`rc=9`, wall 221 s, 3.6833 core-min against a 2.0 cap, `cap_exceeded=1`.** **`so3af2_attr_census.json` was never written. There is no enumeration.** The graded artefact `XM/so3af2_M.json` remains **ABSENT**, which is correct.

### A9.2 ⚠ THE STOP IS AN INTERVENTION, NOT A MEASUREMENT

`DAFOAM_CHARTER.md` §7: *a run that stops because a human or a watchdog intervened on a shared box records that too, **by name**, and claims nothing about the envelope.*

**It is recorded by name in the item's own ledger**, with `stopped_by=dafoam-lab-lane` and the note that it *claims nothing about why it was slow*. **I am not diagnosing why the census was slow and this addendum does not.** The 208 bytes it did emit are recorded verbatim in the evidence file; whatever they suggest, **a stop is not a measurement**, and this lane has read the record of a lab that once published one as if it were.

**Two ledger rows exist for one event** — the launcher's (`wall_s=221`, `core_min=3.6833`, measured to container exit) and the lane's intervention note (`wall_s=222`, `core_min=3.7000`, measured to the stop command returning). **They are the same event and must not be double-counted.** The launcher's is the figure of record.

### A9.3 ⚠ THE REAL FINDING — THE CAP CANNOT STOP A RUN, IT CAN ONLY REPORT ONE

The launcher's cap check runs **after `docker wait` returns**. It computed `cap_exceeded=1` correctly — **but only because I had already stopped the container.** Had I not, `docker wait` would have blocked indefinitely and the registered stop rule would never have fired.

> **THE REGISTERED STOP RULE IS NOT ENFORCED BY THE INSTRUMENT. It is a post-hoc report wearing a stop rule's name.** Rule 12 says an overrun **stops** the run; this launcher's cap **describes** one, afterwards, if something else ends the container first.

**The family's other launchers do not have this hole:** `a1wr_chain_driver.sh:173` wraps its arm command in `timeout -k 60 $((tmo + 900))`, so the deadline lives **inside** the container and fires without anyone watching. **This launcher has no deadline at all**, and the three arms that preceded this one finished in 3, 21 and 3 seconds, so nothing ever tested it.

**That is the same shape as everything else this item has produced tonight: a guard whose predicate was never exercised because the happy path was fast.** It is registered here as a defect; **the repair is not made in this addendum** and is the supervisor's to order.

### A9.4 Cost, and this one IS waste

**3.6833 core-min against a 2.0 cap — an overrun of 84 %.** Item total across six launches: **0.0667 (MESH ×4) + 0.3500 (XM) + 3.6833 (census) = 4.1000 core-min.**

> **WASTE: 3.6833 core-min, ALL OF IT, named as waste and never absorbed into any ratio.** The census produced **no enumeration**, which was its only product. Unlike the XM arm — where the supervisor ruled the spend an answer because it bought three converged primals and a registered refusal — **this run bought nothing.** It is named as a loss because it was one.

**Dollars: $0.00315 DERIVED at $0.0513/core-h, never measured.**

### A9.5 Standing

**No enumeration exists, so the producer's attribute question is exactly where it was.** The XM arm's `rc=7` stands as the registered risk landing; MESH stands complete and **NOT A RESULT**; the item stays **PENDING**; **F1–F5 are unscored**; and **§0.2 binds in full.** **SUBMISSIONS PARKED.**

**END OF ADDENDUM 9.**

---

## ADDENDUM 10 — THE DEADLINE MOVES INSIDE THE CONTAINER. ENFORCEMENT AND REPORT ARE NOW TWO THINGS. Dated **2026-09-03**. Version **1.10 → 1.11**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label.** It makes the **already-registered** cap enforceable, which strictly increases refusal capability.

### A10.1 The defect

> **The registered stop rule was not enforced by the instrument. It was a post-hoc report wearing a stop rule's name.**

The launcher's cap check runs **after `docker wait` returns**. On 2026-09-03T23:02:42Z it computed `cap_exceeded=1` correctly — **only because a lane had already stopped the container by hand.** Left alone, `docker wait` blocks indefinitely and **the registered stop rule never fires at all.**

**`a1wr_chain_driver.sh:173` has carried the fix all along** — `timeout -k 60 $((tmo + 900))`, so its deadline lives **inside** the container. **One launcher and not its neighbour: the seventh instance of that signature in one night.** And nobody caught it because **the three arms before this finished in 3, 21 and 3 seconds — the guard's predicate was never exercised because the happy path was fast.**

### A10.2 The repair — two things, named separately

**ENFORCEMENT: an in-container deadline.** `timeout -k <K> <D>` now wraps the arm command inside the container, so **it fires with no agent alive** — the standing rule that a task must never depend on an agent being alive at a future instant.

- **`K` is DERIVED from `a1wr_chain_driver.sh`'s own bytes**, distinct values counted, anything but one refusing. Measured: **1 distinct value.**
- **`D` is INVERTED FROM THE REGISTERED CAP** so the two cannot drift: `cap × 60 / ranks − FRAME_ALLOWANCE_S(15)`. **MESH 165 s, XM 345 s, ATTRCENSUS 105 s.** A non-positive deadline **refuses** — it would kill an arm instantly, which is the "cap 3.16× short" class in a new place.
- The **environment assertion runs first and unwrapped** (milliseconds, and its own refusals must not be masked by a kill); it then `exec`s the deadline, which owns the solver.

**REPORT: the post-`docker wait` cap check stays, and is named as what it is.** It cannot stop anything; it **records** that a cap was exceeded, which is a different and still useful thing.

> **ONE IS ENFORCEMENT, THE OTHER IS A RECORD, AND THE ITEM NOW HAS BOTH INSTEAD OF A REPORT NAMED AS IF IT WERE ENFORCEMENT.**

**What it would have bought:** the census reached **199 s** before a hand-stop. Its deadline is **105 s**. It would have been killed at 105 s by the container itself, with nobody watching.

### A10.3 Driven — 45 legs, PASS 45, FAIL 0, NOT RUN 0

- **the deadline lets work finish** — `rc=0`, the arm command ran; it does not fire early;
- **the deadline kills an overrun** — **`rc=124`, `timeout`'s own code**, the arm **STARTED and was CUT OFF** before finishing;
- **the kill came from inside** — `rc 124` is produced by the arm's own process tree; **no watcher, no polling loop, no agent exists in that leg**;
- **the deadline is positive for every registered arm**, each inverted from its own cap.

### A10.4 ⚠ THE CONTROLLED RESULT — n=2, same agent, same error, one hour apart

This is recorded because it is a **measurement**, and everything else this item has said about guards is reasoning.

**The same lane made the same mistake twice: beginning a commit invocation with a `cd` into the case directory, so every repo-relative path resolved against the wrong root.**

| | outcome |
|---|---|
| **first**, before the guard | `commit-tree` produced an **empty commit** whose message announced work its tree did not contain, and it landed at HEAD |
| **second**, after the guard | the sequence **aborted before `commit-tree`**; HEAD never moved; the work was redone correctly |

**The only variable was a guard added in between** — comparing the written tree against its parent and refusing an empty one, and reading the `diff-tree` assertion instead of running past it.

> **THE HABIT DID NOT IMPROVE. THE INSTRUMENT DID.**
>
> **A rule that requires you to remember it protects nothing; an instrument that reads its own assertion protects you on the night you forget.**

That is the closure-over-detection argument with a measurement under it rather than an example beside it.

### A10.5 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_run_arm.sh` | `dcf35e6a36988e9047041a2b62df2920` | **RE-PINNED** |
| `so3af2_pin_selftest.sh` | `940ec695e391b9789b21588f47368216` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_attr_census.py` | `2fd479d881f63b529605b3a45d0154f3` | **UNCHANGED** |
| `so3af2_runScript.py` | `c268633f67e6d2c785feec2ebfc7326c` | **UNCHANGED** |

### A10.6 Standing

**NOT RE-FIRED.** The census produced **no enumeration** and its absence is **not treated as evidence about anything**. The producer's attribute question is exactly where it was. XM `rc=7` stands as the registered risk landing; MESH complete and **NOT A RESULT**; item **PENDING**; **F1–F5 unscored**; **§0.2 binding.** **SUBMISSIONS PARKED.**

**END OF ADDENDUM 10.**

---

## ADDENDUM 11 — THE DEADLINE FIRED. `rc=124`, UNATTENDED. AND IT STILL LANDED OVER ITS CAP. Dated **2026-09-03**. Version **1.11 → 1.12**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap and no label. NO ENUMERATION WAS PRODUCED.**

### A11.1 The repair worked, and here is the measurement

`SO3aF2_ATTRCENSUS_r2` launched 23:17:52Z with a **105 s** in-container deadline.

| | first attempt | this attempt |
|---|---|---|
| how it ended | reached **199 s**, **stopped by a lane by hand**, `rc=9` | **killed at its deadline by the container itself**, `rc=124` |
| who intervened | a lane, watching | **nobody** |

**`rc=124` is `timeout`'s own deadline code.** SIGTERM went at 23:19:37Z; the process died at 23:19:49Z — **33 s later, well inside the 60 s kill-after grace, so SIGKILL was never needed.** No agent was watching, no polling loop existed, nothing was asked to intervene.

**That is the difference between a registered stop rule and an enforced one, measured on the same arm one run apart.**

### A11.2 ⚠ AND IT STILL EXCEEDED ITS OWN CAP — the frame allowance is too small

**`core_min=2.3000` against a cap of `2.0`. `cap_exceeded=1` EVEN THOUGH THE DEADLINE FIRED.**

The deadline is `cap × 60 / ranks − FRAME_ALLOWANCE_S`, with the allowance at **15 s**. **The process took 33 s to die after SIGTERM.** The allowance was sized for container start/stop overhead and **not** for how long a Python/MPI process takes to unwind — so the enforced deadline still lands the total **over** the cap it was inverted from.

> **THE DEADLINE IS NOW ENFORCEMENT, BUT IT IS NOT YET A GUARANTEE THAT THE CAP HOLDS.** Naming that plainly rather than letting `rc=124` read as an unqualified success: **the repair converted an unbounded overrun into a bounded one, and a bounded overrun is still an overrun.** 199 s → 138 s is real; 138 s against a 120 s cap is not yet right.

**No repair is made here.** Sizing the allowance needs the teardown measured rather than guessed, and this is one observation of it. **Registered as an open defect for the supervisor to rule on.**

### A11.3 The census still produced nothing, and that is evidence about nothing

`so3af2_attr_census.json` is **ABSENT** for the second time. The arm log is the **same 208 bytes** as before.

> **THAT IS NOT EVIDENCE THAT THE ATTRIBUTE DOES NOT EXIST, that the object lacks a residual history, or anything else about the model.** The arm was killed before it reached the enumeration. **A killed run is not a measurement**, exactly as a stopped one is not, and **the producer's attribute question is precisely where it was.** No diagnosis of the slowness is offered here or anywhere.

The graded artefact `XM/so3af2_M.json` remains **ABSENT**, which is correct.

### A11.4 Cost

**2.3000 core-min against a 2.0 cap.** Item total across seven launches: **0.0667 (MESH ×4) + 0.3500 (XM) + 3.6833 (census, stopped) + 2.3000 (census, deadline) = 6.4000 core-min.**

> **WASTE: 2.3000 core-min, ALL OF IT.** The arm produced **no enumeration**, which was its only product. **Named as a loss because it was one** — the same ruling as the stopped attempt, and the opposite of XM's, whose spend bought three converged primals and a registered refusal.

**A calibration row is owed and will again DECLINE its ratio**: the run did not do the work the estimate priced.

### A11.5 Standing

**NOT RE-FIRED.** Two attempts have now produced no enumeration, and **the reason for that is not established and is not guessed at here.** XM `rc=7` stands as the registered risk landing; MESH complete and **NOT A RESULT**; item **PENDING**; **F1–F5 unscored**; **§0.2 binding.** **SUBMISSIONS PARKED.**

**END OF ADDENDUM 11.**

---

## ADDENDUM 12 — THE REFUSAL NOW REPORTS WHAT THE OBJECT EXPOSES. THE CENSUS IS PARKED. Dated **2026-09-03**. Version **1.12 → 1.13**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap or label.** It adds what a refusal **reports**, never what it **decides**.

### A12.1 Why the census was the wrong instrument, measured

A static comparison of the census against XM — **artefacts and code only, no container** — established:

- the census stops **exactly where XM printed its path-contract line next**, and never printed it;
- the executable statements before the task branch are **43 in each and AST-identical** ignoring docstrings, with the **same nine module-level imports in the same order**;
- **neither file mentions matplotlib**; the prefixes differ by **2,314 bytes and all of it is docstring**;
- **same image digest**, and an **identical `SO3AF2_ENV_OK` line** in both container logs.

> **THE CENSUS STALLS IN CODE BYTE-IDENTICAL TO THE PRODUCER'S — CODE THE PRODUCER GOT PAST IN 21 SECONDS. THE DIFFERENCE IS NOT IN THIS ITEM'S CODE.**

**And the precision matters more than the finding.** The matplotlib font-cache line is the **first** line, not the last; the **last** is the VSPAERO warning, **which XM also printed**. The cache had already reported before output stopped. **THAT IT IS RELATED TO THE STALL IS UNMEASURED** — it is a difference between the runs, and calling it the cause would be **taking a correlate for the relation**, the error this item has made three times.

### A12.2 The ruling — ask the instrument that already reaches the moment

**XM reaches the exact point of the question in 21 seconds, reliably, twice.** It built the model, derived the path contract, ran **three converged primals**, and refused **at the residual-history lookup** — so **the object whose attributes we want existed in that process, at that moment.**

> **DO NOT BUILD A SECOND INSTRUMENT TO REACH A PLACE THE FIRST ALREADY REACHES. ASK THE PRODUCER TO SAY WHAT IT SAW, AT THE POINT WHERE IT REFUSES.**

That is the closure form applied to the diagnostic itself: instead of a second instrument that must *reach* the state, the instrument that already reaches it is made to *report* what it found. **Its marginal cost is a field in a note rather than a run** — against **6.0 core-min and two stalls** for the arm that tried to reconstruct the moment from scratch.

### A12.3 What changed, and the constraint that bounds it

The `RESIDUAL_HISTORY_UNAVAILABLE` refusal now carries **`candidates_tried`** and **`what_the_object_exposes`** — every attribute of `<scenario>.coupling.solver` and its `DASolver`: name, type, callability, and length for anything sequence-shaped.

> **THE REFUSAL IS UNCHANGED. Same trigger, same `rc=7`, same reason, still no artefact written. THIS ADDS WHAT THE REFUSAL REPORTS, NEVER WHAT IT DECIDES — a refusal that starts producing a product is not a refusal.**

**Proved structurally, not asserted:** a census leg walks the AST and confirms the trigger's body is **exactly one `_fail("RESIDUAL_HISTORY_UNAVAILABLE")` call**, so the enumeration is an **argument** and **cannot gate the refusal**.

**An unreadable attribute is RECORDED, never skipped** — a silently omitted attribute is exactly the blindness this exists to remove. **And nothing in it raises**: a failure to describe must not displace the refusal it describes.

### A12.4 Driven — 50 legs, PASS 50, FAIL 0, NOT RUN 0

Five are new, all on the host against synthetic objects, **no container**:

- **the refusal is unchanged by the note** — the structural AST proof above;
- **shapes reported** — names, types, callability, lengths;
- **the unreadable is recorded** — an attribute that raises on read appears as `UNREADABLE`, not omitted;
- **a missing node is named** — `resolved_to` and `missing_at`, rather than a silently empty result;
- **the enumeration cannot replace the refusal** — a hostile object yields `ENUMERATION_FAILED`, not an exception.

### A12.5 The census is PARKED, not deleted, and its stall stays on record

**Two attempts, 6.0 core-min, no enumeration, the difference measurably NOT in this item's code, and the cause UNMEASURED.** It is not chased and not deleted: **a parked defect with its evidence intact is a finding; a deleted one is nothing.** It remains an unexplained difference between two containers from one digest, and if the extended refusal answers the attribute question the census may never be needed — the stall is still worth having on record.

### A12.6 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_runScript.py` | `0cbff59668dd1a88c155f6728ed0863c` | **RE-PINNED**; every departure in `so3af2_runScript_DELTAS_addendum12.diff` |
| `so3af2_run_arm.sh` | `5e44a11a9020f68c1eb96e3a37bfbc50` | **RE-PINNED** (the producer pin) |
| `so3af2_pin_selftest.sh` | `82011a88ac7ba351b067f33783d48bcc` | **RE-PINNED** |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen reader is not touched** |
| `so3af2_attr_census.py` | `2fd479d881f63b529605b3a45d0154f3` | **UNCHANGED — parked, not deleted** |

### A12.7 Standing

**NOT FIRED.** The open defects stand: the frame allowance under-covers teardown (**n=1**, unresized), and the census stall is **unexplained**. XM `rc=7` remains the registered risk landing; MESH complete and **NOT A RESULT**; item **PENDING**; **F1–F5 unscored**; **§0.2 binding.** **SUBMISSIONS PARKED.**

**END OF ADDENDUM 12.**

---

## ADDENDUM 13 — `F1`'s APPROACH AS REGISTERED CANNOT WORK. THE ROUTE IS CLOSED AND THE ITEM STANDS DOWN. Dated **2026-09-03**. Version **1.13 → 1.14**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap or label. F1–F5 REMAIN UNSCORED.**

### A13.1 ⚠ THE RULING, IN TWO LINES, AND THE TWO CLAIMS ARE NOT THE SAME

> **1. NO RESIDUAL-HISTORY *ATTRIBUTE* EXISTS ON EITHER OBJECT. — MEASURED.**
> All four candidates — `getPrimalResidualHistory`, `primalResidualHistory`, `getResidualHistory`, `residualHistory` — are **absent from both** `DASolver` (87 attributes) **and** the mphys wrapper (298 attributes), 0 unreadable on either. The only two names matching `resid|hist` on `DASolver` are `calcPrimalResidualStatistics` and `getResiduals`, **both methods, neither sequence-shaped**, and every sequence-shaped attribute on `DASolver` is mesh or geometry (`faces`, `owners`, `neighbours`, `xv`, `xv0`, `basicFamilies`, `wallList`, `imOptions`).
>
> **2. WHETHER A RESIDUAL HISTORY IS *OBTAINABLE* IS — UNMEASURED.**
> `getResiduals` and `calcPrimalResidualStatistics` are methods **nobody has called**, and DAFoam may expose a history by some other route entirely. **Nothing here tests that.**

**THE DISTINCTION IS LOAD-BEARING.** A successor who reads *"unobtainable"* where this measured *"absent as an attribute"* will abandon a route that was never tested — **the same scope error as an overclaim, in the direction of giving up instead.**

**RULED: `F1`'s approach as registered cannot work.** The quantity it reads does not exist on the object it reads from, and **no run at any budget would have changed that.** **The fourteenth unsatisfiable-by-construction condition, established for 0.4 core-min by a field in a note.**

### A13.2 What is deferred, and to whom

**What `F1` should read instead — or whether `F1` survives at all — is a REGISTRATION DECISION** and goes on the deferred pile beside `F_mp`'s, **for a fresh session.** Not tonight, and not by the lane. **F1–F5 are unscored and the item is `PENDING`.**

### A13.3 The durable product of this item, which is not its answer

> **A guess about an object can be checked before it is written into an instrument.**

The producer wrote **four guesses into an instrument** and paid **three runs and 6.0 core-min** to learn they were all wrong. **The enumeration cost a field in a note.** The check was available the whole time, at the exact moment of the question, and nobody asked for it until the guesses had been paid for.

**It sits beside the other closure this item produced:** *before building an instrument to reach a state, ask whether something already reaches it.* **Both say one thing from opposite ends — the information you need is usually already within reach of something that works, and the expensive move is building a new way to get it.**

### A13.4 The honest accounting

**Eight launches, 6.8000 core-min.** Produced: a mesh **nothing grades**, one **registered refusal**, one **measured reason `F1` cannot work as written**, and thirteen addenda largely about the delivery path. **Three real defect classes closed** — inputs, environment, and the shell option that hid both — and **a registered stop rule that could not stop is now enforced by an in-container deadline.**

> **THE INSTRUMENTS IMPROVED A GREAT DEAL AND THIS ITEM'S PHYSICS QUESTION DID NOT MOVE.** It is now closed with a **measured** reason rather than an open one, which is a better place to leave it than where it began — **and that is not the same as progress on the physics.**

### A13.5 The two open defects, neither chased nor deleted

1. **The frame allowance under-covers teardown.** The census's enforced 105 s deadline still landed **2.3000 core-min against a 2.0 cap**, because the process took **33 s** to die after SIGTERM and `FRAME_ALLOWANCE_S` is **15**. **DELIBERATELY UNRESIZED: n=1**, and a constant fitted to a single sample is the shape this family was bitten by repeatedly.
2. **The census stall is unexplained.** Two attempts, **6.0 core-min**, no enumeration, the difference measurably **not in this item's code**, cause **UNMEASURED**. **Parked with its evidence intact** — a parked defect with its evidence is a finding; a deleted one is nothing.

### A13.6 Rest state

**`MESH` complete and `NOT A RESULT`. `XM` `rc=7`, the registered risk landing. F1–F5 unscored. Item `PENDING`. §0.2 binding — this item never called `solve_linear` and nothing it measured may be quoted toward SO-3aR's adjoint collision.** **SUBMISSIONS PARKED. NOTHING FURTHER ON SO3aF2.**

### A13.7 The rest state above was then VERIFIED BY EXECUTION, and the verification caught an error in itself

§A13.6 states the rest state. Stating it is not checking it, so it was checked:
`so3af2_reststate_evidence.txt`, beside this file, is the **output** of the
commands, produced 2026-09-03T233750Z — disk-vs-`HEAD` md5 on all eleven touched
files, the run root enumerated rather than summarised, every archive counted,
`so3af2_M.json` absent, containers and queue rows at zero, the guard suite at
`PASS 50 FAIL 0 NOT RUN 0`, and the item cost recomputed from the ledger.

Two things that check earned:

1. **The frozen reader `so3af2_read.py` still hashes to
   `d5f4149d43abe3a165ffe7e653b78bee`**, its value at the 2026-08-31 freeze
   (`3b85e47f0893d322a198e7d52b989e51aa43c205`). Thirteen addenda, eight
   launches and three closed defect classes later, **the scoring instrument was
   never once edited.** That is the only sentence in this document that would
   have been worth anything had the item produced a number.

2. **The check found a defect in itself.** Its first pass printed the launcher-row
   sum as `6.8333`; the correct sum is `6.7833`, and the item total `6.8000`. The
   figure of record was never wrong — every addendum says 6.8000 — but the wrong
   line was the **one line in a "verify, don't claim" step that I did by hand
   instead of by machine.** It is corrected by computation in the evidence file
   and disclosed there rather than quietly fixed, because a stand-down that
   silently repaired its own arithmetic would be exactly the record this item
   spent thirteen addenda learning not to write.

**Assertion:** lines whose number changed above this section: **0**. The single
line displaced is the `END OF ADDENDUM 13.` marker below, which moves down by the
length of this section and is cited by nothing.

**END OF ADDENDUM 13.**

---

## ADDENDUM 14 — A CORRECTION TO ADDENDUM 13's MEASURED LINE, AND THE WASTE COLUMN OVERRULED. Dated **2026-09-03**. Version **1.14 → 1.15**.

> **lines whose number changed above this section: 0** — asserted by execution against both the pre-append snapshot and `git show HEAD:`.

**Moves no gate, no threshold, no prediction, no band, no cap or label. F1–F5 REMAIN UNSCORED. The A13.1 ruling is UNAFFECTED and the reason is given in §A14.2.**

### A14.1 ⚠ A CLAUSE IN THE MEASURED LINE IS WRONG. STRUCK BY QUOTE, NOT REWRITTEN.

A13.1 line 1344 states, of `DASolver`:

> ~~"every sequence-shaped attribute on `DASolver` is mesh or geometry (`faces`, `owners`, `neighbours`, `xv`, `xv0`, `basicFamilies`, `wallList`, `imOptions`)"~~ — **STRUCK.**

**Re-counted from the artefact `XM/XM.log`: `DASolver` has 21 sequence-shaped attributes. I named 8 and characterised all 21.** The thirteen I did not name are `allSurfacesGroup`, `allWallsGroup`, `boundaries`, `defaultOptions`, `designSurfacesGroup`, `dtype`, `families`, `fileNames`, `name`, `options`, `parallelFlag`, `solverRegistry`, `version` — and **eight of those are configuration, registry or version data, not mesh or geometry at all.**

**This is the same defect as the other four in this document's ledger of them, in its purest form: a universal claim ("every") resting on an enumeration I did not finish.** It differs from the arithmetic error in A13.7 in one way that makes it worse — **that one was in a working note; this one is in a line labelled MEASURED.**

**How it happened, stated plainly:** the eight names are the sequence-shaped attributes that are *interesting* — the ones a reader hunting a residual history would weigh. I wrote down the ones I had reasoned about and quantified them with the word "every". **The census had all 21 on disk the whole time.**

### A14.2 THE RULING IS UNAFFECTED, AND THIS IS WHY — NOT AN ASSERTION THAT IT SURVIVES

**Checked, not assumed: none of the thirteen unnamed attributes is a residual history.** No name among them matches `resid|hist` at all, and their types are `str`, `dict` and `OrderedDict` holding configuration. **The A13.1 ruling rests on the four registered candidate names being absent from both objects — re-verified here, present in 0 of the 2 enumerated attribute sets — and on the only two `resid|hist` names on `DASolver` being `calcPrimalResidualStatistics` and `getResiduals`, both recorded by the artefact as `{"type": "method", "callable": true, "sequence_shaped": false}`.** Every one of those figures re-checked against `XM/XM.log` and every one confirmed: `DASolver` **87** attributes, wrapper **298**, **0 UNREADABLE on either**.

**So the struck clause was decorative and the load-bearing clauses were sound — but that is a fact about which sentence happened to be sloppy, not a property of how the line was written.** Had the wrong sentence been the careless one, the ruling would have been false and equally well-dressed.

**One honest note on the census's own predicate:** `sequence_shaped` is true for `str`, so `version`, `name`, `dtype` and `parallelFlag` are counted sequence-shaped. That is a broad predicate, deliberately — a census that guesses which sequences matter is the blindness it exists to remove — but it means "sequence-shaped" in these counts is **`__len__`-bearing**, not "array-like", and a successor reading 21 should read it that way.

### A14.3 THE WASTE COLUMN — I WAS OVERRULED AND THE OVERRULE IS RIGHT

The close-out row `C-20260903T234227.693660Z-ef853022` recorded waste **0.0167** and declined to count the 6.0 core-min census stall, on the ground that *"a spend whose cause is UNMEASURED cannot be classified"*.

**Overruled by the dafoam supervisor, and the reasoning is recorded here because it is a lasting rule and not a one-off correction:**

> **Waste names an OUTCOME, not a culpability.** It is core-minutes that bought nothing. **Whether the spend was avoidable is a question about CAUSE, and cause has its own field.**

**And the decisive argument is the practical one: if a spend that bought nothing escapes the waste column BECAUSE its cause is unmeasured, then every unexplained spend escapes it — and unexplained spends are exactly what the column is for.** A waste figure that counts only the losses we can explain will always look small, and always wrong in the same direction.

**The charter is on the supervisor's side, and I checked it rather than taking the ruling on authority:** `COMPUTE_BUDGET_CHARTER` §5 lines 107–110 define the split as labelling *"solver cost that bought nothing"* — **an outcome test, with no culpability clause.**

**The factual premise was checked too, by execution, before accepting:** both census container logs (`ATTRCENSUS_2026-09-03T230242Z.container.log`, `…T231752Z.container.log`) end at `SO3AF2_ENV_OK`, the line before the Python invocation; the only `so3af2_attr_census.py` artefacts on disk are the **script**, never an output. **The two attempts produced no enumeration. They bought nothing, and that is measured.**

**Corrected figure: waste 6.0167 core-min — 88.5 % of the item's 6.8000.** Components: **6.0000** the two census attempts (rc: hand-stopped `rc=9` staging-precondition archive, then a second attempt that reached `ENV_OK` and produced no enumeration), **cause UNMEASURED**; **0.0167** the three `rc=127`/`rc=1` `MESH` aborts, cause measured and closed. A correcting row is appended to `docs/COST_CALIBRATION.md`; the original row is **struck by the correcting row, never edited**.

**What the item's remaining 0.7833 core-min bought** is stated so the 6.0167 is not read as the whole story: the `MESH` arm (0.0500, complete, `NOT A RESULT`) and the two `XM` launches (0.3500 + 0.4000), the second of which produced the refusal enumeration that **is** the artefact behind A13.1. **The item's one measured finding cost 0.4 core-min. Delivering it cost 6.4.**

**END OF ADDENDUM 14.**

---

## ADDENDUM 15 — **ADDENDUM 13's RULING WAS WRONG. `F1`'s APPROACH AS REGISTERED WORKS; THE PRODUCER'S UNREGISTERED SUBSTITUTE DID NOT.** Dated **2026-09-04**. Version **1.15 → 1.16**.

> **lines whose number changed above this section: 0** — **PROVED ON BYTES, not asserted.** Before the append the file was **124,195 bytes, 1,459 lines, md5 `adae31bfb5c5cd24d8568b16cbce550f`**, verified byte-identical to `git show HEAD:` at the moment of copying. After the append the first 124,195 bytes were compared against that copy with `cmp -n 124195`, byte for byte. The append was made by `scripts/append_block.py`, which reads this body from a FILE as bytes so that no shell ever sees it and which re-reads the landed tail and reverts on any difference — **no heredoc anywhere on this path** (`L-405`).

**Moves no gate, no threshold, no prediction, no band, no cap and no label.** **F1–F5 REMAIN UNSCORED. The item remains `PENDING`. The frozen reader `so3af2_read.py` is NOT TOUCHED and still hashes to `d5f4149d43abe3a165ffe7e653b78bee`.**

### A15.1 ⚠ THE CORRECTION, AND IT OVERTURNS A SUPERVISOR'S RULING RATHER THAN A LANE'S NOTE

ADDENDUM 13 §A13.1 concluded, and the `dafoam-supervisor` ruled at S-46:

> ~~"**RULED: `F1`'s approach as registered cannot work.** The quantity it reads does not exist on the object it reads from, and **no run at any budget would have changed that.** **The fourteenth unsatisfiable-by-construction condition**"~~ — **STRUCK BY QUOTE. The ruling was WRONG.**

**`F1`'s approach as registered works, and the data it reads was on disk the whole time.** §5 at line 279 scores `F1` **"counted from the log, both ways."** The producer did not do that. It read the second count from an **object attribute on a live `DASolver`** — four guessed names — which is **a route the registration never names.** What ADDENDUM 13 measured is true and stands: no residual-history attribute exists on either object. What it *ruled* is false: it attributed **the instrument's limitation to the document the instrument was supposed to implement.**

**This is the mirror image of the defect this item has spent fourteen addenda hunting.** Every other entry in its ledger is an instrument claiming more than it measured. **This one is a reading that claimed less than the registration offered** — and it is the same failure to keep the map and the territory apart, pointed the other way. **It cost this item its stand-down.**

> **The closure, and it belongs beside §A13.3's rather than replacing it: BEFORE BUILDING AN INSTRUMENT TO REACH A QUANTITY, READ WHAT THE REGISTRATION SAID THE QUANTITY WOULD BE READ FROM.** §A13.3 says *before building an instrument to reach a state, ask whether something already reaches it.* **Both are one sentence: the thing you need is usually already within reach of something that works — and the registration is one of the things that works.**

### A15.2 THE MEASUREMENT, IN TWO CLAIMS THAT ARE NOT THE SAME CLAIM

§A13.1 kept its two claims apart deliberately and this addendum keeps the discipline.

> **1. THE TWO UNCALLED METHODS DO NOT CARRY A HISTORY — MEASURED FROM SOURCE, NOT FROM THEIR NAMES.**
> `getResiduals` (`dafoam/pyDAFoam.py:2121-2130` → `src/adjoint/DASolver/DASolver.C:1157`) calls `updateStateBoundaryConditions()` then `calcResiduals()` and copies the **current** residual fields into a caller-supplied flat array of length `getNLocalAdjointStates()` — **a spatial field, one entry per local adjoint DOF, with no time or iteration index.** `calcPrimalResidualStatistics` (`pyDAFoam.py:901-905` → `DASolver.C:745`) **has no `return` statement in Python and is `void` in C++**; it recomputes and **prints**. `mphys/mphys_dafoam.py:353-357` calls it with `"print"` immediately after the primal — **that call is the `Printing Primal Residual Statistics.` block in `XM.log`.** **Calling either would not have produced a history, and a fifth guessed name would not have either.**

> **2. A RESIDUAL HISTORY IS OBTAINABLE — MEASURED, AND IT WAS ALREADY ON DISK.**
> `DAUtility::primalResidualControl` (`src/adjoint/DAUtility/DAUtility.C:735-800`) prints `<var> initRes: <a> finalRes: <b> nIters: <n>` per equation, gated on `printToScreen`, which `DASolver.C:225` sets from `isPrintTime(runTime, printInterval_)` — true when `timeIndex % printInterval == 0 || timeIndex == 1` (`DASolver.C:2765-2771`). **Three histories, five equations each, five samples each, were parsed out of the XM arm's own preserved `XM.log` at ZERO solver core-minutes**, and the identical counts come out of the earlier container's log independently.

**All source citations above are from the image `dafoam/opt-packages:latest`, digest `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`** — the digest, not the tag, because DAFOAM_CHARTER §6 makes the identity an image ID and never a version string. It was read by `docker create` + `docker cp` with **no container ever started**: nothing executed, no solver ran, and source that exists only inside image layers is unreadable any other way.

### A15.3 ⚠ A NEGATIVE SEARCH, STATED WITH ITS EXACT PREDICATE

Case-insensitive `hist`, as a **substring**, matches **0 lines** in **seven named files**: `pyDAFoam.py`, `mphys_dafoam.py`, `DASolver.C`, `DASolver.H`, `DASolvers.H`, `pyDASolvers.pyx`, `DAUtility.C`. **That is evidence about those seven files and about nothing else.** DAFoam is not enumerated here and **no universal is claimed over it** — the failure §A14.1 recorded, in a line labelled MEASURED, is not repeated.

### A15.4 THE REPAIR — PRODUCER ONLY, AND THE GRADER IS NOT TOUCHED

Every departure is in `so3af2_runScript_DELTAS_addendum15.diff` beside this file. **Three files change; `so3af2_read.py` is absent from that diff by design, and its absence is the load-bearing fact.**

1. **The four attribute names are GONE from the producer**, not bypassed — the unregistered substitute is removed.
2. **The log is resolved from the process's own `fd 1`**, not guessed by name: `os.readlink("/proc/self/fd/1")`, refusing unless it names a regular file on disk. The arm redirects `python so3af2_runScript.py -task run_model > XM.log 2>&1` **into the mounted run root**, so fd 1 **is** the log. Resolving it this way means the producer **cannot** read a sibling arm's file, a stale log from an earlier container, or nothing at all if the redirect ever changes — each of which a hard-coded `XM.log` would do without saying so.
3. **The producer can read its own log while it runs, and that is a property of OpenFOAM rather than a hope.** `Foam::endl` reaches `OSstream::endl()`, whose entire body is `write('\n'); os_.flush();` (`OSstream.C:301-305`, read in the registered image). **Every `Info << … << endl` flushes, so a residual line printed is a residual line on disk.** Verified from source, not inferred from the log's ordering.
4. **The block-to-scenario mapping is MEASURED, not assumed.** The i-th primal block's converged `CD:` is compared against the functional the model reports for the i-th scenario, to `1.0e-12` relative; a mismatch refuses. **Order is the obvious assumption and it is exactly the kind this item may not make silently** — attaching a history to the wrong point is a confident wrong answer.
5. **`printInterval` IS NOT CHANGED.** The histories are at the registered sampling interval. **`F1` requires three histories PRESENT and the two counts to AGREE; it does not require per-iteration resolution, and the frozen reader never looks inside a history.** Changing the option would buy nothing `F1` needs and would introduce an unregistered difference between `XM` and `XM2` on an item whose entire remaining value is that its instrument was never edited.

**A DRAFT PREDICTION IS WITHDRAWN WITH THE CHANGE THAT NEEDED IT.** The lane's draft carried a second falsifier — *at `printInterval: 1` each primal's sample count must equal its final time index* — and flagged its own supporting argument as an argument rather than a measurement. **With `printInterval` left alone that falsifier tests nothing that happens, and it is dropped rather than carried.** A prediction kept past the change that motivated it is decoration.

### A15.5 THE PLANTED-ZERO CONTROL, AND A CONTROL SHOWN FAILING

**`CLAUDE.md` rule 3 applies to a THREE exactly as it applies to a zero.** In the same invocation that writes the artefact, the producer strips the `initRes:` lines of the **last** primal block from a **scratch copy**, re-parses **from disk**, and requires the read to come back with exactly one fewer block carrying residuals. **If the planted short read is invisible, the producer REFUSES and writes nothing.** The plant is a precondition on the reading, not a note beside it.

**Driven against the arm's own preserved artefact: live 3 → planted 2, `demonstrated=True`.** And the control was then **shown able to FAIL**: driven with a parser that cannot see the plant, the same control reads `demonstrated=False`. **A control never observed failing is not a control.**

### A15.6 ⚠ BOTH `F1` READINGS NOW COME FROM ONE FILE — THE SHARED FAILURE MODE, NAMED

`n_tol` is counted from `XM/XM.log`; `residual_histories` is now parsed from **the same file**. §5 says *"counted from the log, both ways"*, so this is **registered and not a deviation** — **and "registered" is not permitted to do the work that "measured" should.**

> **THE TWO READINGS SHARE A FAILURE MODE: a truncated, unwritten or unflushed log moves BOTH counts together, and their agreement would then mean nothing.**

**What the guard still catches, measured rather than argued:** the two counts read **different tokens**. A primal that runs but does not converge emits `initRes:` lines and **no** tolerance line; a tolerance line with no residual block is the reverse. The plant of §A15.5 produced exactly `n_tol=3 / n_resid=2` — **the disagreement `so3af2_read.py:306` refuses on.** **The discrimination that survives is the discrimination that was measured; the shared mode is stated so no reader mistakes agreement for independence.**

### A15.7 `VERIFICATION_CHARTER` §2d.1's FOUR CONDITIONS, DISCHARGED IN ORDER

1. **DEMONSTRABLE ERROR, NOT PREFERENCE.** The producer does not perform the reading the frozen document says the scoring is. The attribute census measured **0 of 4 candidates present** across **87** and **298** attributes with **0 UNREADABLE** on either.
2. **ESTABLISHED BY AN INSTRUMENT INDEPENDENT OF THE HYPOTHESIS.** The attribute census **grades nothing** — §A8.2 registers that it evaluates no prediction, applies no band and emits no verdict token — and its only possible effect on the item was to push toward **refusal**. **It cannot have been selected to move a verdict in a wanted direction.** The instrument is **named**: `so3af2_attr_census.py` / the ADDENDUM 12 refusal enumeration in `XM/XM.log`.
3. **DISCLOSED, AND WHAT MOVED IS QUANTIFIED.** Producer md5 `0cbff59668dd1a88c155f6728ed0863c` → `f3913ddbe0bafe874755332561407d0f`; **+237 / −37 lines across the producer, +90 in the guard suite, 1 line in the launcher pin**; every hunk in `so3af2_runScript_DELTAS_addendum15.diff`. **Reader md5 unchanged.**
4. **THE PRE-REPAIR STATE IS RECORDED BESIDE THE PUBLISHED ONE, AND IT IS STATED RATHER THAN LEFT BLANK.** **Pre-repair: `XM` `rc=7`, NO artefact, NO number, F1–F5 unscored.** Nothing was published that this repair replaces, and that is the honest content of the field — not an absence.

### A15.8 THE GUARD SUITE — 10 NEW LEGS, DRIVEN AGAINST A REAL ARTEFACT

**`SO3aF2 PIN CENSUS: PASS 59 FAIL 0 NOT RUN 0`** at this addendum (was 50). **`NOT RUN 0` remains the load-bearing figure.** The ten new legs (JOB 6) drive the four new functions, extracted by `ast`, **against the XM arm's own preserved `XM.log` rather than a fixture** — a parser proved only against a fixture written beside it is proved against its author.

> **⚠ ONE OF THE NEW LEGS FAILED ON ITS FIRST DRIVE, AND ITS DEFECT IS THE ONE THIS ITEM EXISTS TO TEACH.** A leg named *"printInterval untouched"* tested `"printInterval" not in src` — **a substring test over the whole file, which flagged the producer's own prose promising that printInterval was not changed.** A check that fails on the sentence promising it did not do the thing is a check whose predicate is wider than its name. **Repaired to what it means:** no string **literal** in the producer's AST is equal to `"printInterval"` — a dict key `"printInterval": 1` is such a literal, a docstring mentioning the word is not. **Recorded rather than quietly fixed, because §A14's whole subject is a label that overstates its own predicate, and this one was caught by driving it instead of by reading it.**

### A15.9 THE ARMS, RE-PINNED AND COSTED. Rule 12; DAFOAM_CHARTER §18.1, §18.2.

**COST ANCHOR — PROGRAM STATEMENT, all four terms (§18.1).** Anchor: `ledger.txt:6`, `ITEM=SO3aF2 ARM=XM STAMP=2026-09-03T233357Z rc=7 wall_s=24 ranks=1 core_min=0.4000`. **The program that row priced:** ranks **1**; adjoint **NO**; Jacobian colouring **NO**; tree **COLD** (a case staged fresh per operating point into `mp0`/`mp1`/`mp2`, `decomposePar` not run). It covers mesh check, IDWarp init, **three converged primals** (443 / 436 / 424 iterations) and the refusal. **MATCH ASSERTION against `XM2`:** ranks 1 = 1; adjoint NO = NO; colouring NO = NO; tree COLD = COLD. **Matches on all four terms**, and with `printInterval` unchanged there is **no residual difference in the program at all** — the only change is which lines the producer reads after the solves.

| arm | what it does | solver | estimate | cap | basis |
|---|---|---|---|---|---|
| **R0** | parse the **preserved** `XM.log`; report the three histories | **NO** | **0.02** core-min | **0.20** | instrument-only. **Cache state: WARM** — 1 file, 97,084 B, 0 copies. Cold, at §18.2's own `≈1.0 s / 1000 files` carry-forward (`C-212`/`C-214`), is still **< 0.02** at one file. |
| **XM2** | re-run `XM` with the repaired producer; writes `so3af2_M.json` | **YES** | **0.40** core-min | **6.0** *(unchanged)* | the anchor above, **with no adjustment**, because the registered program is unchanged. |
| **RD** | drive the frozen reader on XM2's artefact; score F1–F5 | **NO** | **0.03** core-min | **0.20** | instrument-only. **Cache state: WARM** — ≈220 files under one run root, 0 copies. |

**Total registered 0.45 core-min, caps 6.40**, inside the item's 9.0 ceiling. **`cost_basis`: REPORTED-BY-OWNER, NOT MEASURED** — wall seconds and ranks from ledger rows; the `$0.0513/core-h` rate is owner-stated and this box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5). **Rule 12's estimate-versus-actual comparison is owed at completion** as a row in `docs/COST_CALIBRATION.md`, with waste named separately and never absorbed into the ratio.

> **⚠ `R0` IS A DIAGNOSTIC AND NOT A GRADED READING. `XM2` IS THE GRADED ARM.** Ruled by the `dafoam-supervisor`, 2026-09-04. Sanaa's *"bookkeeping never voids physics"* (2026-08-26) means the preserved log's physics is real and readable — **it does not mean an arm whose producer REFUSED becomes the artefact of record.** `XM2` buys a clean `rc=0` arm for 0.40 core-min **and removes the argument entirely, which is cheaper than the argument.**

### A15.10 Re-pins

| file | md5 | note |
|---|---|---|
| `so3af2_runScript.py` | `f3913ddbe0bafe874755332561407d0f` | **RE-PINNED**; every departure in `so3af2_runScript_DELTAS_addendum15.diff` |
| `so3af2_run_arm.sh` | `8469c92765e95fe0c1833fc0b21194bf` | **RE-PINNED** (the producer pin, one line) |
| `so3af2_pin_selftest.sh` | `ee0bbe2e0bd33544d137c41e5370fe40` | **RE-PINNED** (JOB 6, ten legs) |
| `so3af2_read.py` | `d5f4149d43abe3a165ffe7e653b78bee` | **UNCHANGED — the frozen grader is not touched, and this line is what makes ADDENDUM 15 a repair rather than a re-registration** |
| `so3af2_env_assert.sh` | `a5b7fcae05aab420d94623582d45f897` | **UNCHANGED** |
| `so3af2_attr_census.py` | `2fd479d881f63b529605b3a45d0154f3` | **UNCHANGED — parked, not deleted; it is the independent instrument of §A15.7 condition 2** |

### A15.11 ROUTES NOT TESTED — an untested route is not a closed one

1. **Calling `getResiduals` / `calcPrimalResidualStatistics` on a live `DASolver`.** Their source is read; they remain **uncalled**. Source reading is strong evidence and is not execution.
2. **The OpenFOAM `residuals` functionObject — the strongest untested route, and deliberately left untested.** No staged `system/controlDict` carries a `functions` block and no `postProcessing/` directory exists under the case tree. It would write a per-iteration `residuals.dat` **independent of `printInterval`**. It is **not load-bearing for `F1`**, so testing it now would be scope creep — **and it is named here because an untested route is not a closed one.**
3. **DAFoam source outside the seven files of §A15.3** — `DAResidual*`, `DAGlobalVar`, `DAOption`, the unsteady solvers, `DAFuncObj`. `primalMaxRes` lives in `daGlobalVarPtr_` and is **not exposed through `pyDASolvers.pyx`** (searched); the rest of that tree is unsearched.
4. **`updateDAOption` (`pyDASolvers.pyx:355`)**, which can change `printInterval` at run time. Never exercised, and this repair does not exercise it.

### A15.12 The two rows. DAFOAM_CHARTER §6.

| row | identity | standing |
|---|---|---|
| **SHIPPED** | `dafoam/opt-packages:latest`, `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | **The only row this work has.** Every count and every source citation in this addendum is from this image. |
| **PATCHED** | **NONE.** No patch is involved, none is proposed, **and no patched row is claimed.** | Stated rather than omitted: §6 requires two rows, and *"there is no patched row"* is a row's worth of information. |

### A15.13 What is unchanged, and what is still owed

**F1–F5, every band, both caps, the ceiling, the memory floor, every rc in the taxonomy (no new rc is registered — `RESIDUAL_LOG_UNRESOLVABLE`, `RESIDUAL_PLANT_NOT_VISIBLE` and `RESIDUAL_HISTORY_SCENARIO_MISMATCH` are new REASONS under the existing producer refusal `rc=7`), the plant constants, and §0.2 in full** — this item never calls `solve_linear`, cannot show SO-3aR's adjoint collision is fixed, and **nothing measured here may be quoted toward it.**

**The two open defects of §A13.5 stand, neither chased nor deleted:** the frame allowance under-covers teardown (**n=1, deliberately unresized**) and the census stall is **UNEXPLAINED**, parked with its evidence intact.

**STILL OWED BEFORE `XM2` MAY FIRE:** the supervisor's **check 1 on the changed hunks, read as a diff**, and **check 4 before it is queued**. **XM2 IS NOT QUEUED AND NOT ARMED.** `MESH` stands complete and **NOT A RESULT**; `XM`'s `rc=7` stands as the registered risk landing and as the pre-repair state of §A15.7; the item stays **PENDING**; **F1–F5 are unscored**. **SUBMISSIONS PARKED.**

**END OF ADDENDUM 15.**

---

## CORRECTION 1 TO ADDENDUM 15 — **TWO FIGURES IN IT ARE WRONG. THE REPAIR AND THE RULING ARE NOT.** Dated **2026-09-04**. Version **1.16 → 1.16a**.

> **lines whose number changed above this section: 0** — **PROVED ON BYTES.** Before the append the file was **143,261 bytes, 1,583 lines**, verified byte-identical to the post-ADDENDUM-15 state at the moment of copying; after the append the first 143,261 bytes were compared with `cmp -n 143261`, byte for byte. Appended by `scripts/append_block.py` from a FILE as bytes; **no heredoc on this path.** **ADDENDUM 15 IS NOT REWRITTEN** — its wrong sentences are struck by quote below and left standing in place (`CLAUDE.md` rule 6).

**Moves no gate, no threshold, no prediction, no band, no cap and no label. F1–F5 REMAIN UNSCORED.**

### C15.1 ⚠ THE GUARD-SUITE FIGURE. STRUCK.

§A15.8 states:

> ~~"`SO3aF2 PIN CENSUS: PASS 59 FAIL 0 NOT RUN 0` at this addendum (was 50)"~~ — **STRUCK.**

**The measured figure is `SO3aF2 PIN CENSUS: PASS 60  FAIL 0  NOT RUN 0`.**

**How the wrong number got written, stated plainly rather than glossed.** `59` was read off the **last drive before the addendum was appended**, when the `NL-3-OUTSIDE` leg was still **failing** — because it checks that the launcher's md5 is pinned in this pre-registration, and the addendum that pins it did not yet exist. That drive read **PASS 59 FAIL 1**. Appending the addendum turned that leg green, which moves the count to **60 PASS, 0 FAIL**. **I wrote a total taken before the change whose whole purpose was to move it.** The arithmetic (50 + 10 new legs = 60) was available the entire time.

**This is `CLAUDE.md` rule 11's shape one document over** — a count re-derived at the wrong moment — and it is the second time in this item's ledger that a figure written by hand, inside a step whose purpose was verification, came out false (§A13.7 was the first). **The remedy both times is the same and it is not diligence: compute the figure at the moment it is written, from the artefact, not from the last thing that scrolled past.**

### C15.2 ⚠ THE DIFF LINE COUNTS. STRUCK.

§A15.7 condition 3 states:

> ~~"**+237 / −37 lines across the producer**, +90 in the guard suite, 1 line in the launcher pin"~~ — **STRUCK.**

**The measured figures, from `git diff --numstat HEAD` rather than from the `--stat` histogram:**

| file | insertions | deletions |
|---|---|---|
| `so3af2_runScript.py` | **+201** | **−36** |
| `so3af2_pin_selftest.sh` | **+90** | **−0** |
| `so3af2_run_arm.sh` | **+1** | **−1** |

**`237` is not an insertion count at all.** It is `--stat`'s **combined** changed-line figure for the producer (201 + 36), and `−37` is the **whole diff's** deletion total (36 producer + 1 launcher) misattributed to one file. **Two numbers from a summary display were transcribed as if they were per-file insertions and deletions, and they are neither.**

**Why this one matters more than its size.** It sits in **§2d.1 condition 3, whose entire content is "quantify what moved"** — the one place in the addendum where a number is the evidence rather than the decoration. **A quantification that misreads its own instrument's output format is not a quantification.** `--stat` renders a histogram for humans; `--numstat` emits the two numbers; **the addendum cited the histogram.**

### C15.3 WHAT SURVIVES, CHECKED RATHER THAN ASSERTED

**Every md5 in §A15.10 was re-verified against the working files after this correction was drafted, and all six agree:** `so3af2_runScript.py` `f3913ddbe0bafe874755332561407d0f`; `so3af2_run_arm.sh` `8469c92765e95fe0c1833fc0b21194bf`; `so3af2_pin_selftest.sh` `ee0bbe2e0bd33544d137c41e5370fe40`; **`so3af2_read.py` `d5f4149d43abe3a165ffe7e653b78bee`, UNCHANGED**; `so3af2_env_assert.sh` `a5b7fcae05aab420d94623582d45f897`; `so3af2_attr_census.py` `2fd479d881f63b529605b3a45d0154f3`.

**`so3af2_runScript_DELTAS_addendum15.diff` was re-verified to be the CURRENT diff**, byte-for-byte from its sixth line, against `git diff HEAD` over the three files at this reading. **The diff the supervisor's check 1 will read is the diff of the files that will run.**

**Unaffected:** the A15.1 correction of ADDENDUM 13's ruling; both claims of A15.2 and every source citation behind them; the negative-search predicate of A15.3; every clause of the repair in A15.4, including that `printInterval` is not changed; the planted control and its failing-control drive in A15.5; the shared-failure-mode statement of A15.6; §2d.1 conditions 1, 2 and 4; the arm table and cost anchor of A15.9; the re-pins of A15.10; the untested routes of A15.11; and the two rows of A15.12.

> **THE TWO STRUCK FIGURES ARE BOTH BOOKKEEPING AND NEITHER IS PHYSICS — and that is an explanation, never a defence.** §A14.2 already recorded the sharp version of this: *"that is a fact about which sentence happened to be sloppy, not a property of how the line was written."* **Both errors here were made in the same pass, by the same hand, in a document whose subject is figures that overstate what was measured.**

### C15.4 Standing

**Unchanged by this correction.** **XM2 IS NOT QUEUED AND NOT ARMED**; the supervisor's **check 1 on the changed hunks and check 4 before enqueue** are still owed. `MESH` complete and **NOT A RESULT**; `XM` `rc=7` the registered risk landing and the pre-repair state; item **PENDING**; **F1–F5 unscored**; **§0.2 binding.** The two open defects of §A13.5 stand with their evidence. **SUBMISSIONS PARKED.**

**END OF CORRECTION 1 TO ADDENDUM 15.**
