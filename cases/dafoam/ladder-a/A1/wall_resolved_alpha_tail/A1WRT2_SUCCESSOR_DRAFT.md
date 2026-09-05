# A1WRT2 — THE WALL-RESOLVED α-TAIL, ON `symmetry` — **SUCCESSOR PRE-REGISTRATION, DRAFT**

> ## ⚠ NOT FROZEN. NOT PINNED. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT.
>
> **This document is a DRAFT and has no evidentiary force.** No gate, threshold,
> cap or label in it is closed. It is written to be read as a diff by the
> `dafoam-supervisor` (`SUPERVISION_CHARTER.md` §3 check 1, not delegable) and to
> be argued with. **It authorises nothing.** No instrument named below exists
> yet; where a file is named it is named as *to be written*, and the document
> says so at every occurrence.
>
> **NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED, POSTED OR REGISTERED ANYWHERE**
> (`CLAUDE.md` rule 7). **SUBMISSIONS PARKED.**
>
> **Predecessor:** `A1WRT`, frozen `a62d8d75`, both units run, **NO ITEM VERDICT
> BY CONSTRUCTION** (that item's ADDENDUM 8 §A8.1). This document's §1 is the
> repair of that, and it is the reason the document exists.
>
> **This is a NEW ITEM on a FRESH RUN ROOT with its OWN budget.** It is not a
> restart of `A1WRT` and it is not a restart of `A1WR` Stage 2.

**Item:** `A1WRT2` — NACA0012 α 13…18 on the A1WR wall-resolved L3 mesh,
incompressible (`DASimpleFoam`), **on `symmetry`**, CONTINUED from `A1WRT` U1's
landed `4000/` state. **Two arms, six new points, one seam probe.**
**Team:** dafoam · **Lane:** lab-lane · **Drafted:** 2026-09-04
**Verdict class:** `FEASIBILITY`. **Verdict ceiling:** `GATE REACHED`.
**REGISTERED SUCCESS LABEL:** `GATE REACHED` — §1 says what reaches it and what
emits it.

---

## 0. WHY THIS SUCCESSOR EXISTS — THE PREDECESSOR'S NO-VERDICT, MECHANISM NAMED

`A1WRT` ran both its units, produced eight gate readings, and **emits no
item-level verdict.** The mechanism is stated here because it decides what this
document must fix, and because it is **NOT** the mechanism `SO3aF2` failed by.

### 0.1 `A1WRT`'s mechanism — a REGISTERED composition with NO IMPLEMENTATION

`A1WRT`'s registration **does** register a success label and **does** register a
composition rule. `PREREGISTRATION_DRAFT.md:657-659`, verbatim:

> **Composition:** D19M's repaired `compose_item` from `verdict_before_ceiling`,
> hard-gate list tested for **both** `GATE FAIL` and `NOT A RESULT`. Ceiling
> `GATE REACHED`.

and `:61`: **`Verdict class: FEASIBILITY. Verdict ceiling: GATE REACHED.`**

**The frozen grading path does not contain it.** Measured in this drafting
invocation, with a live positive control on the same reader so a zero is not
believed from a reader never shown able to see a non-zero (`CLAUDE.md` rule 3):

| token | hits in `a1wrt_read.py` (md5 `705db5f7e972f6c033cbe303b7a6038f`) |
|---|---|
| `G-STALL` — **the positive control, known present** | **7** |
| `compose_item` | **0** |
| `verdict_before_ceiling` | **0** |
| `ITEM VERDICT` | **0** |
| `def compose` (any) | **0** |

`compose_item` is implemented in exactly four tracked files —
`cases/dafoam/a2gc_grade.py`, `curriculum_D19M/d19m_grade.py`,
`curriculum_D19O/d19o_grade.py`, `curriculum_D19T/d19t_grade.py` — and
`a1wrt_read.py` is not among them. `verdict_before_ceiling` appears in
`A1WRT`'s registration prose and in `A1WR_PREREGISTRATION.md`, **and in no A1
instrument.**

**So the label was registered and the emitter was never written.** That is
`DAFOAM_CHARTER.md` §18.3's class one step further out than §18.3 reaches:
§18.3 legislates a registered gate whose implementing file is absent from the
instrument table; here the composition's implementing function is **absent from
every file**, and the registration named it by importing another item's
identifier as though naming it made it present.

### 0.2 `SO3aF2`'s mechanism — a LABEL SET with no success token

`FEASIBILITY_PREREGISTRATION.md:269-275`, verbatim:

> **These are predictions, not gates. A MISS is a FINDING and is reported as one;
> it is never written as `GATE FAIL`, because this item has no gates** (§0). **The
> only verdict vocabulary this item may emit is `BLOCKED` … or `NOT A RESULT` …**

Both registered tokens are failure tokens. `SO3aF2` could have scored **F1–F5 all
HIT — its own written prediction (`:285`)** — and still had nothing to say, because
no success token was in the registered set.

### 0.3 ⚠ THEY ARE **DIFFERENT** MECHANISMS, AND THE DISTINCTION DECIDES THIS DOCUMENT

| | `SO3aF2` | `A1WRT` |
|---|---|---|
| success label registered? | **NO** — the label set is two failure tokens | **YES** — `GATE REACHED` ceiling, `:61` and `:659` |
| composition rule registered? | **NO** — no gates at all | **YES** — `:657-659`, by name |
| emitter implemented? | n/a | **NO** — 0 hits, control 7 |
| what a full success would have produced | **nothing sayable** | **nothing emitted** |
| the repair | register a success token | **write the emitter, and pin it** |

**The supervisor's ruling that "two is a pattern in registration DESIGN, not a
gap in the vocabulary" survives this reading and is strengthened by it** — but the
pattern is one level more general than "no success label was registered". It is:
**an item's registration was never driven end-to-end against the question *what
does this instrument print if everything goes right?*** `SO3aF2` could not answer
it because no token existed; `A1WRT` could not answer it because no code did.
**A registration that cannot answer that question in one sentence, naming the
line that prints it, is not finished.** §1 answers it for this item in that form.

### 0.4 One further reading, disclosed because it makes the pattern three and not two

`a1wr_read.py` — `A1WR`'s frozen reader — carries `compose_item` **0**,
`verdict_before_ceiling` **0**, `ITEM VERDICT` **0**, against a positive control
`G-YPLUS` = **5**. `A1WR_PREREGISTRATION.md` names `verdict_before_ceiling`.
**The A1 branch has now registered a composition rule by name three times and
implemented it zero times.** It did not surface at `A1WR` because that item's
verdict was `NOT A RESULT` on other grounds. **A composition that is never
exercised on a green run is not evidence that it exists** — the same shape
`d19m_grade.py:1551-1554` records against `d19o_grade.py`.

**And a sibling in the same subtree does it correctly:** `A1ZE`'s
`a1ze_grade.py` prints `A1ZE_VERDICT <token>` at `:648`, with explicit
`NOT A RESULT` / `PENDING` branches at `:625`, `:635`, `:638`, `:645`. **The
working emitter is one directory away and was frozen the same day.** This item
ports from there, not from D19M, because it is the nearer neighbour and its
ceiling logic already matches.

---

## 1. ⚠ THE REGISTERED SUCCESS LABEL — WHAT PASSING IS CALLED, AND WHAT PRINTS IT

**This section is the point of the document. It is written first in the order a
reader needs it and is not buried under the design.**

> **`A1WRT2` CAN SUCCEED. Success is called `GATE REACHED`.**
>
> **It is emitted by `a1wrt2_grade.py` (TO BE WRITTEN), by a function
> `compose_item()` whose last statement prints the single line
> `A1WRT2_VERDICT <token>`, and by nothing else.** No verdict for this item is
> composed by a supervisor, by a lane, by a board write or by a commit message.
> If that line is absent from the grader's stdout, **this item has no verdict**,
> and the honest statement is `PENDING`, never a token inferred from the gates.

**The composition, registered as arithmetic and not as prose:**

```
hard = [G-PATCH, G-COLDSTART-SEAM, G-IMG, G-FREEZE, G-UNBOUND,
        G-NOGRAD, G-WARPPROBE, G-FIXTURE, G-NOBAND, G-STALL]
soft = [G-SEAM, G-TAILCOUNT, G-RC-HONEST, G-YPLUS, G-CAPS, G-CEILING]

if "NOT A RESULT" in hard or "NOT A RESULT" in soft:  raw = "NOT A RESULT"
elif "BLOCKED"    in hard or "BLOCKED"    in soft:    raw = "BLOCKED"
elif "GATE FAIL"  in hard or "GATE FAIL"  in soft:    raw = "GATE FAIL"
elif "GATE REACHED" in soft:                          raw = "GATE REACHED"
else:                                                 raw = "PASS"
final = min(raw, CEILING)     # CEILING = "GATE REACHED"
assert final in {"PASS","GATE REACHED","GATE FAIL","NOT A RESULT",
                 "BLOCKED","PENDING"}   # else REFUSE, exit 2
```

**Every hard list is tested for BOTH `GATE FAIL` and `NOT A RESULT`** — the
`D19M-COMPOSE-DEF-1` repair (`d19m_grade.py:1533-1554`), where a hard gate
reporting `NOT A RESULT` fell through to `PASS` and was then capped to
`GATE REACHED`, inverting `CLAUDE.md` rule 5's direction. **That defect is
carried forward as a control, not as a comment:** control `Q-COMPOSE-1` below
plants `NOT A RESULT` into one hard gate and asserts the composed token is
`NOT A RESULT` and **not** `GATE REACHED`.

**`PASS` IS UNREACHABLE AND THAT IS REGISTERED, NOT AN OVERSIGHT.** The ceiling
is `GATE REACHED` because the L3 family has no Roache triple, so no value this
item produces can be grid-converged or carry a band (`G-NOBAND`, inherited from
`A1WRT` §5 unweakened). `min(raw, CEILING)` therefore caps a `PASS` to
`GATE REACHED` **and the grader prints both `raw` and `final` so the cap is
visible**, exactly as `verdict_before_ceiling` was supposed to.

**What reaches `GATE REACHED`, stated so a reader can predict it before the run:**
all six declared tail points executed and honestly certified, the seam probe
reproducing U1's terminal state inside its registered band, and no hard gate
firing. **What does not:** any of §4's failure conditions, each with its own
token named in §4's table.

**⚠ `NO ITEM VERDICT BY CONSTRUCTION` IS NOT AVAILABLE TO THIS ITEM.** It was
`A1WRT`'s *outcome*; it is registered here as **forbidden**. If
`a1wrt2_grade.py` reaches its end without printing `A1WRT2_VERDICT`, an `EXIT`
trap prints `A1WRT2_VERDICT PENDING -- the composer did not run, last checkpoint
<n>` and exits **12** — the `SO3aF2` ADDENDUM 4 §A4.4 repair, ported by name:
*"an instrument must always say which of its outcomes occurred, INCLUDING
'neither'."*

---

## 2. WHAT IS ALREADY MEASURED, AND IS **NOT** RE-BOUGHT

**A successor that re-learns something already measured is not mandatory work; it
is waste with a registration attached.** Four things are closed. Each is stated
with its artefact and its tag.

**2.1 `empty` IS UNUSABLE IN DAFoam ON THIS CASE FAMILY. CLOSED.**
`[MEASURED, /home/ubuntu/certonomous-runs/A1WRT/tail_empty/out/sweep.log]` — the
solver prints `Mesh has 2 solution (non-empty) directions (1 1 0)` and then
`--> FOAM FATAL ERROR: (openfoam-2506) / Mesh geometric directions is less than 3
and not supported! / From Foam::label Foam::checkGeometry(...) in file
DACheckMesh/DACheckGeometry.C at line 278`, `Signal: Aborted (6)`, **zero
`Time =` lines, zero `End`, zero `AOA_POINT_END`**, unit `rc=97`, 0.683 core-min.
**Measured a second time, independently, in a different item on the same image:**
`A1ZE` arm `Ec`, `rc=97 wall_s=88 core_min=1.4667` at 19:05Z, with its sibling
arm `Sc` on `symmetry` printing `3 solution (non-empty) directions (1 1 1)` and
**no abort** — the two arms differ in the treatment and in nothing else
`[MEASURED, docs/COST_CALIBRATION.md row C-20260903T224408.032809Z-bdbf23b5]`.
**This item does not run an `empty` arm and registers no `empty` gate.**

> **⚠ AND IT INVERTS `A1WRT`'s OWN PREMISE, WHICH MUST BE SAID PLAINLY.**
> `A1WRT` §2.0 classed the `symmetry` bounding planes as a **blocking physics
> defect** under Sanaa's 2026-09-03 classification and registered *"the tail runs
> on `empty`"* (`:137`). **DAFoam refuses `empty` on a one-cell-thick mesh in its
> own source.** Within this toolchain `symmetry` is therefore not the defective
> choice — **it is the only admissible one**, and the mesh `A1WR` built was
> configured the only way DAFoam accepts. `A1WRT` could not have known: it froze
> at `a62d8d75` (18:31Z) **before `A1ZE` ran** (19:05Z), and `DACheckGeometry`,
> `geometric direction`, `nGeometricD` and `A1ZE` all occur **0** times in the
> frozen document. **This is the ladder learning something that retroactively
> kills a registered arm, which is what a ladder is for.**

**2.2 THE `symmetry`-versus-`empty` COEFFICIENT COMPARISON IS `A1ZE`'s QUESTION,
AND IT IS BLOCKED AT THE TOOLCHAIN. THIS ITEM DOES NOT RE-REGISTER IT.**
`cases/dafoam/ladder-a/A1/z_direction_empty_control/A1ZE_PREREGISTRATION.md` is
frozen, carries `G-COEF` as *"THE GATE THAT MATTERS"* (§5.4) with a `G-STAT`
stationarity precondition, and its chain stopped at
`rc=73 phase=ARM-Ec spend_core_min=4.9` `[MEASURED, that item's
STATUS.A1ZE_chain]`. **`A1WRT`'s `G-PATCHPAIR` asked the same question and
returned `NOT A RESULT` — *"one side of the pair is absent"* — and no
re-registration can restore that side inside DAFoam.** Registering it again here
would buy a second `NOT A RESULT` for the same measured reason. **The open
question belongs to `A1ZE`'s successor and is named for that item's supervisor,
not taken here.**

**2.3 COLD ≠ CONTINUED AT α = 12 ON L3. MEASURED IN TWO INDEPENDENT CHANNELS.
CLOSED AS A RESULT.** This is what `A1WRT` U1's 55.317 core-min bought and it is
the item's strongest product.

*Coefficient channel* `[MEASURED, A1WRT ADDENDUM 8 §A8.2, from
alpha12_symmetry/out/sweep.log and a1wr_alpha12_reference.tsv]`: `G-REPRO`
**GATE FAIL** — R1 band 1.0e-03, CL rel **6.013254e-03 OUTSIDE**, CD rel
**3.018116e-03 OUTSIDE**; R2 band 1.0e-04, extrapolated plateaus, CL rel
**2.542431e-02 OUTSIDE**, CD rel **5.614858e-04 OUTSIDE**. All four outside.

*Residual channel — and it is the stronger of the two, because it carries no
A8.3 caveat* `[MEASURED, this drafting invocation, from the two sweep logs
named]`. Same mesh, same image, same solver, same α, same 4,000-iteration budget;
one variable moved:

| | A1WR `sweep_I` α = 12, **CONTINUED** | A1WRT U1 α = 12, **COLD** |
|---|---|---|
| `Primal min residual` printed | **0 times** | **1**, value `1.051926887799928e-06` |
| `Primal solution failed` printed | **0 times** | **2** |
| `satisfied the prescribed tolerance` | **0 times** | **0 times** |
| the point's own `AOA_POINT_VALUES` | `CL=1.19079592024 CD=0.030665481166 err=NONE` | `CL=NA CD=NA err=AnalysisError(… Primal solution failed!)` |

**The solver's own certification state flips.** The continued point's residual sat
inside the deliberate 100× dead band between `primalMinResTol` (1e-8) and
`primalMinResTol × primalMinResTolDiff` (1e-6) — never converged, never flagged;
the cold point's crossed 1e-6 and DAFoam declared it failed. **`A1WRT` §7
registered and derived that dead band before the run (`:771-782`) and this is its
first live confirmation.**

**⚠ THE A8.3 CAVEAT TRAVELS AND IS NOT DROPPED HERE:** `G-REPRO`'s CL/CD are read
from per-iteration prints on a point whose solver wrote `CL=NA CD=NA`. **The
residual-channel row above is free of that caveat** — `Primal min residual` is
DAFoam's own certified quantity — **which is why this document leads with it.**

**2.4 THE PREDICTION MACHINERY WORKS. NOT RE-DEMONSTRATED.** `A1WRT` ADDENDUM 7
registered *"U2 IS PREDICTED TO ABORT at `DACheckGeometry.C:278`"* at commit
`d1665410`, `2026-09-03T22:32:39+00:00`; the U2 container started
`2026-09-03T22:33:23.307570829Z` — **44 seconds later** `[MEASURED, git log and
launcher.queue.out:30]`. Exit code, mechanism, file, line and zero-time-steps
were all exact. **Magnitude was not: the prediction said "order 1.5 core-min" and
measured 0.683, low by 2.1×** — recorded because a prediction's misses are what
make its hits evidence.

---

## 3. THE DESIGN — TWO ARMS, ONE VARIABLE EACH

**The item's own registered deliverable is unbought: α 13…18 does not exist.**
`A1WRT` §0: *"The tail α 13…18 is the part of the registered polar that does not
exist, and this item gets it legally."* **Zero of the seven declared tail points
ran.** This item buys them, on the only patch identity DAFoam accepts.

| arm | patch | start | points | iterations | what it isolates |
|---|---|---|---|---|---|
| **`SEAM`** | `symmetry` | CONTINUED from `A1WRT` U1's `4000/` | α = 12 | **200** (`endTime` 4000 → 4200) | **that the restart actually loaded the state** — the restart-fidelity control, and nothing else |
| **`TAIL`** | `symmetry` | CONTINUED from `SEAM`'s final state, in the same process | α = 13,14,15,16,17,18 | 4,000 each | **the tail** |

**Inherited unchanged, by md5, and nothing about the discretisation, numerics or
build moves:** `a1wr_runScript_incomp.py` `d48f48c5e2e41e86981acbf6feccb3c4`;
mesh `A1WR` L3, 130,304 cells; image `dafoam-idwarp-rot:v1`,
`sha256:2927768a16ac…`, `libidwarp` md5 `85f59e87253e0a71a813f64ca6e4c425`;
`primalMinResTol = 1.0e-8`, SA, `useWallFunction: False`, np = 1,
`OMP_NUM_THREADS=1`, one-core cpuset. **Changing any of them would make the tail
non-comparable to the α 0…12 body it extends.**

**The continuation asset exists on disk and is not re-bought.** `A1WRT` U1's
`/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry/4000/` holds
`U.gz p.gz nut.gz nuTilda.gz phi.gz yPlus.gz alphaPorosity.gz betaFINuTilda.gz
fvSource.gz meshPhi.gz polyMesh/ uniform/` — a complete SA state at
`Time = 4000 == endTime`, with `1` `End` line and `41` anchored `^Time = ` lines
`[MEASURED, this drafting invocation]`. **This item stages a COPY of it and never
writes into `A1WRT`'s run root.**

**⚠ THE `SEAM` ARM'S `endTime` CHANGE IS REGISTERED AS A CONTROL AND IS FENCED.**
Raising `endTime` 4000 → 4200 for `SEAM` is a **two-variable move against the
tail** and is therefore ring-fenced: **`SEAM`'s coefficients are used by
`G-SEAM` and by nothing else, are never compared against any 4,000-iteration
value as physics, and never enter a polar.** `CLAUDE.md` rule 2 and `A1WRT`
§7's closing clause forbid raising `endTime` **to manufacture a convergence**;
this raises it to read a restart back, and the fence is what keeps the two apart.
**If the supervisor judges the fence insufficient, the alternative is registered
and costs nothing: drop `SEAM` and take the restart-fidelity reading from
`TAIL`'s own first print at α = 13, accepting that it then moves α as well as the
restart and is a weaker control.** The stronger design is registered; the fallback
is named so the choice is visible.

**No point is retried, relaxed, re-tuned or dropped.** A point that fails is
recorded with its residual history and the sweep continues, every subsequent
point flagged `after_exception=TRUE`. **A missing point on a polar is a lie by
omission.**

---

## 4. GATES, WITH THE PLANTED CONTROL THAT MUST BE SHOWN ABLE TO FAIL

**`CLAUDE.md` rule 3, taken at its strength: a control that is merely present is
not a control.** Every gate below that reads a number carries a control that
**reads the target bytes before mutating, asserts the bytes actually changed,
drives the REAL gate function, asserts the verdict FLIPPED, restores, and
re-asserts the restore landed.** A no-op mutation followed by a passing check
proves nothing (`A1WR` §10).

**And every control reports one of three states — `EXERCISED-PASS`,
`EXERCISED-FAIL`, `NOT EXERCISED` — printed beside the verdict it accompanies.**
`NOT EXERCISED` is never counted as a pass and is never inferred from the absence
of a failure. *(This adopts `DAFOAM_CHARTER.md` §18.5, which is a **PROPOSAL, NOT
ENACTED** and is verification's to weigh and Sanaa's to rule. **Adopting it
voluntarily inside one item's own registration is not ratifying it**, and this
item claims no charter authority; it is registered here because `A1WRT`'s
`G-PATCHPAIR` short-circuited on an absent side and its planted controls' silence
was indistinguishable from their success.)*

| gate | subject | verdict rule | its planted control, and the direction it must fail in |
|---|---|---|---|
| **`G-SEAM`** | `SEAM`'s coefficients at its first print after restart vs U1's terminal `CL 1.1836353615763` / `CD 0.030758033132912` | inside band → `PASS`; outside → **`GATE FAIL`**, and the finding is *the restart did not load the state* | **known-positive is MEASURED and FREE: the cold α = 12 run is U1 itself**, whose terminal CL differs from A1WR's continued α = 12 by **6.013254e-03**. The control drives `G-SEAM` against U1-vs-A1WR and asserts **`GATE FAIL`**; it drives it against U1-vs-U1 and asserts `PASS`. **Both directions, on real bytes, at zero compute.** |
| **`G-TAILCOUNT`** | declared vs executed, where *executed* means **a point that produced a value or a certified failure with a residual history**, never a printed marker | 6 of 6 → `PASS`; fewer → **`GATE FAIL`** with the gap named per α; unreadable → `NOT A RESULT` | **known-positive is MEASURED and FREE: `A1WRT` U1's own log**, which carries `AOA_POINT_END` **1** against `n_executed=0`. The control asserts `G-TAILCOUNT` reads **0**, not 1, on those bytes — see §4.1, which is why this gate exists at all. |
| **`G-RC-HONEST`** | the unit's rc **as the producer set it**, propagated, not recomputed from markers | producer rc 0 and 6/6 → `PASS`; producer rc ≠ 0 → **`GATE FAIL`** on rule 4's rc clause; rc artefact absent → **REFUSE, exit 2** | control writes rc `97` into a static fixture, asserts `GATE FAIL`; deletes it, asserts **exit 2** and no verdict printed |
| **`G-UNBOUND`** | every `$VAR` expansion in the frozen launcher, under `set -u`, assigned before first use | any unassigned → **`BLOCKED`**, launcher does not run | **see §8 — the honest control, and why the obvious one does not work** |
| **`G-NOGRAD`** | `compute_totals` appears **0** times in the staged producer | ≥ 1 → **`BLOCKED`** | control plants `compute_totals` into a static copy, asserts `BLOCKED`; removes it, asserts clean |
| **`G-WARPPROBE`** | `{"warper_init": N, "warper_jacvec": M}` read from the run's own probe output | both 0 → `PASS` and §7's two-row obligation is **discharged by measurement**; either ≠ 0 → **`GATE FAIL`**, and the shipped-toolchain arm becomes owed | control plants `warper_jacvec: 1`, asserts `GATE FAIL`; restores, asserts `PASS` |
| **`G-PATCH`** | mesh `boundary` types, every `0.orig/` field entry, **and the solver's own `Mesh has 3 solution (non-empty) directions (1 1 1)` line** | anything but **3 (1 1 1)** → refuse, exit 2 | control feeds the **real** `tail_empty/out/sweep.log`, which prints `2 (1 1 0)`, and asserts **exit 2**. A measured known-positive, on this box, from this family. |
| **`G-COLDSTART-SEAM`** | the staged `4000/` read back from disk field-by-field and asserted **NONUNIFORM** in `U`, and `0/` asserted absent | a uniform `U` at `4000/` means the state did not stage → refuse, exit 2 | **the inverse of `A1WR`'s `G-COLDSTART`, and it is inverted deliberately:** `A1WRT` asserted `0/` uniform for a COLD start; this asserts a CONTINUED start actually carries a field. Control plants a uniform `U`, asserts exit 2 |
| **`G-CAPS`** | measured core-min per arm against §5's caps, computed by the grader and printed | cap-stop ⇒ `NOT A RESULT` on the affected points | control feeds a fixture ledger row over cap, asserts `NOT A RESULT` |
| **`G-CEILING`** | §6's cumulative item-ceiling reading, from the ledger, **before** each arm | projection > ceiling ⇒ the arm **does not launch**; `BLOCKED` | **see §6, including the refusal on an UNMEASURED prior spend** |
| **`G-YPLUS`** | measured y+ min/mean/max on the `wing` patch, every α | y+max ≥ 1.0 anywhere → **`GATE FAIL`**; blind channel on a point that ran ≥ 200 iterations → refuse. **The mesh is NOT re-cut** | control plants a y+ line at 1.4, asserts `GATE FAIL` |
| **`G-STALL`** | no output binds a stall or separation word to a numeric angle | any such binding → refuse, exit 2 | control plants *"stall at 15 degrees"*, asserts exit 2; and asserts it does **NOT** fire on §10's honest caveat text |
| **`G-NOBAND`** | no output presents a value as grid-converged or inside a band | → refuse, exit 2 | control plants *"grid-converged"*, asserts exit 2 |
| **`G-FIXTURE`** | every control fixture is static, committed bytes, **and no fixture path resolves inside this item's run root** | any live fixture → refuse, exit 2 | **the L-435 repair, inherited unweakened.** Control points one fixture at the run root, asserts exit 2 |
| **`G-IMG` / `G-FREEZE`** | image id and `libidwarp` md5 exact; every instrument md5 checked at launch | mismatch → refuse, exit 4 | control perturbs one pin, asserts exit 4 |
| **`Q-COMPOSE-1..4`** | the composer itself | — | Q1: `NOT A RESULT` planted in one **hard** gate ⇒ composed token is `NOT A RESULT`, **not** `GATE REACHED` (the `D19M-COMPOSE-DEF-1` shape). Q2: all gates `PASS` ⇒ `raw = PASS`, `final = GATE REACHED`, **both printed**. Q3: a token outside the six ⇒ **REFUSE**. Q4: the composer not reached ⇒ `PENDING` + exit 12, never silence |

### 4.1 ⚠ `G-TAILCOUNT` EXISTS BECAUSE A LIVE DEFECT SWALLOWED A TRUNCATION, AND `A1WRT` DID NOT SEE IT

**Established in this drafting invocation, from the frozen bytes.**

`a1wr_runScript_incomp.py:357-362` is correct and it fired:

```
    if _executed != len(_alphas):
        print("AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion" ...)
        exit(97)
```

`A1WRT` U1's log carries, verbatim, `AOA_SWEEP_END n_declared=1 n_executed=0` then
`AOA_SWEEP_TRUNCATED n_declared=1 n_executed=0 -- NOT a completion`, and the
container printed `A1WR_SWEEP_RC rc=97` `[MEASURED,
/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry_20260903T211651Z_823815.log:9]`.

**`a1wr_cmd.sh` captures that 97 at `:65`, prints it at `:66`, and never uses it
again** — `grep -n 'SRC'` over the whole 102-line file returns exactly those two
lines. The unit's exit status is decided instead at `:96-102`:

```
if [ "$EXEC" -eq "$DECLARED" ]; then
  echo "A1WR_ALL_POINTS_EXECUTED declared=$DECLARED"
  exit 0
fi
```

where `EXEC` is `grep -c '^AOA_POINT_END '`. **`AOA_POINT_END` is printed for a
point that crashed as well as for one that succeeded**, so U1 scored
`EXEC=1 == DECLARED=1` and **exited 0**, discarding the producer's own 97.

**Consequence, and it is on the record as a clean row:** the launcher's ledger
reads `UNIT=alpha12_symmetry … rc=0 … declared=1 point_end_markers=1`
`[MEASURED, /home/ubuntu/certonomous-runs/A1WRT/ledger.txt:3]` — **a completion-shaped
row for a unit whose own producer declared it NOT a completion and whose
coefficients are `CL=NA CD=NA`.**

**And `A1WRT`'s frozen grader could not have caught it, because it never looked.**
`a1wrt_read.py:949` reads `run / "tail_empty" / "out" / "sweep.log"` and `:965`
reads `run / "tail_empty" / "out" / "rc"`. **`G-COMPLETE` is evaluated on
`tail_empty` alone.** U1 is opened only at `:1038` for `G-REPRO`'s coefficient
series. **U1's rule-4 completion was never gated by anything.**

**This is `DAFOAM_CHARTER.md` §18.7 Requirement 4 one level down** — a non-zero
consumed by a call site, a truncated program announcing itself complete — and
§18.7's own worked instance is `W3`'s `run_stage … || echo`. **The class is
named in the charter and landed again four days later in a different file.**
`G-TAILCOUNT` and `G-RC-HONEST` are the two limbs that read it: one counts what
*executed*, the other propagates what the producer *said*, and the grader
evaluates **both arms, per unit, never one unit only.**

> **⚠ WHAT THIS DOES AND DOES NOT DO TO `A1WRT`.** `A1WRT` is frozen and this
> document amends nothing in it. **No `A1WRT` gate, threshold, cap, label or
> reading is altered, and `A1WRT` still has no item verdict.** This is a defect
> found in an inherited instrument (`a1wr_cmd.sh`, `A1WR`'s file, inherited by
> `A1WRT` unchanged by md5) and carried forward into a successor's gate. **It is
> reported to the `dafoam-supervisor` as a finding about a live instrument that
> will silently mis-certify every future unit of this family that inherits it.**
> Whether `A1WR`'s own record needs an addendum is the supervisor's call and is
> **not taken here.**

---

## 5. COST — REGISTERED IN THIS DOCUMENT, PER ARM, BEFORE ANY COMPUTE

**`CLAUDE.md` rule 12: every run is costed in its pre-registration.** This
family's forward-only rule after the `D6RF2` gap, where caps were in the freeze
and per-arm estimates lived only in the queue row: **the per-arm estimates are
here, in the frozen document, and the queue row will copy them rather than own
them.**

### 5.1 The anchors, with their PROGRAM STATEMENTS and the match assertion (`DAFOAM_CHARTER.md` §18.1)

| anchor | value | ranks | adjoint? | colouring? | tree state | start mode | box state | artefact |
|---|---|---|---|---|---|---|---|---|
| **A-CONT** | **0.46178 s/it** | 1 | **NO** | **NO** | staged, already running | **CONTINUED** | **NOT LABELLED in A1WR's record — disclosed** | `A1WR/STAGE12/sweep_I/out/sweep.log`, `AOA_POINT_VALUES idx=12 alpha=12 … wall_s=1847.1318` over 4,000 iterations `[MEASURED]` |
| **A-COLD** | **0.814982 s/it** | 1 | **NO** | **NO** | cold, `0/` reset from `0.orig` | **COLD** | **MEASURED: 63.1 % min / 76.6 % mean / 90.5 % max busy, 1 sibling** | `A1WRT/alpha12_symmetry/out/sweep.log` final `ExecutionTime = 3259.93 s` over 4,000 it; `docs/COST_CALIBRATION.md` row `C-20260903T223309.077366Z-bc699e66` `[MEASURED]` |

**MATCH ASSERTION.** `A1WRT2`'s registered program is: **ranks 1, adjoint NO,
colouring NO, tree CONTINUED.** It matches **A-CONT on all four terms** and is
priced from it. It differs from **A-COLD on the fourth term (COLD vs CONTINUED)**,
so A-COLD is **not** used as an anchor — it is used only as the pessimistic end of
a bracket, which is a deliberate over-price and is labelled as one.

> **⚠ A-CONT CARRIES AN UNQUANTIFIED CONFOUND AND THE ESTIMATE SAYS SO RATHER
> THAN ABSORBING IT.** `A1WRT` §4.2 labelled every rate row's box state as quiet
> or contended — which is why A-COLD's contention limb could be checked at all —
> **and it did not label start mode**, which is exactly the lesson
> `C-20260903T223309.077366Z-bc699e66` drew against itself: *"an anchor carries
> its START MODE as well as its box state."* **A-CONT is the mode-matched anchor
> and its box state is the term that is missing.** That is why the estimate is a
> **BRACKET and not a point**, and why the cap is sized on the bracket's upper end.

### 5.2 The estimate — per arm, bracketed, with every term named

| arm | term | arithmetic | core-min |
|---|---|---|---|
| **`SEAM`** | 200 it × 0.46178 s/it (A-CONT) | 92.36 s | **1.539** |
| **`SEAM`** | container start + import, 93.85 s `[MEASURED, A1WRT §4.3]` | 93.85 s | **1.564** |
| | **`SEAM` ESTIMATE** | | **≈ 3.10** |
| **`TAIL`** | 6 points × 4,000 it × 0.46178 s/it (A-CONT) | 11,082.7 s | **184.71** |
| **`TAIL`** | container start + import | 93.85 s | **1.564** |
| **`TAIL`** | tail-stiffening allowance on α 14…18, **EXTRAPOLATED** | 5 × 4,000 × 0.46178 × 0.25 = 2,308.9 s | **38.48** |
| | **`TAIL` ESTIMATE (point)** | | **≈ 224.75** |
| | **ITEM ESTIMATE (point)** | 3.10 + 224.75 | **≈ 227.85 core-min** |
| | **ITEM ESTIMATE (pessimistic bracket end**, A-COLD rate substituted**)** | 6 × 4,000 × 0.814982 / 60 + 38.48 + 3.13 | **≈ 367.2 core-min** |

**Dollars: point `$0.19481`, bracket end `$0.31396` — both `DERIVED`, NOT
MEASURED**, at the owner-stated c7a.4xlarge `$0.0513/core-h`; `cost_basis`
**`REPORTED-BY-OWNER`** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Under the `$25` pre-authorisation and still
costed here, because a blanket is not a per-item reading (`CLAUDE.md` rule 9).

**Every point is priced at the FULL 4,000 iterations, and no saving is taken in
advance.** §9's prediction `P3` is that **no tail point converges**, so 4,000 is
the *expected* case rather than a conservative one. **If a point does converge and
stops early, the ratio comes in low and that is reported at calibration as a
favourable misprediction with its cause named** — not quietly absorbed, and it is
also a finding about the tail.

**The term most likely to carry the error is the tail-stiffening allowance**, and
it is `EXTRAPOLATED` and named in advance, as `A1WRT` §4.3 and `A1WR` §7.5 both
named theirs.

### 5.3 The cache-state term (`DAFOAM_CHARTER.md` §18.2)

The **grading pass** runs no solver, so it carries one:
**`COLD`**, **2 run roots**, **≈ 900 files**, **0 copies** — sized on
`C-214`'s carry-forward of **≈ 1.0 s per 1,000 files COLD** (against ≈ 0.15 s
warm), giving **≈ 0.9 s ≈ 0.015 core-min**. `[C-212`/`C-214` are **this family's
own measurements on its own roots on this box, from two roots — NOT constants and
NOT a lab-wide rate**, and a third measurement is expected to move them.]`
Negligible against the arms, and stated because an estimate that does not say
which state it assumes is unfalsifiable by roughly an order of magnitude.

### 5.4 The caps, the deadlines, and the item ceiling

| arm | estimate | **cap** | basis | in-container deadline |
|---|---|---|---|---|
| `SEAM` | 3.10 | **10.0** | 3.2× the estimate | 900 s |
| `TAIL` | 224.75 | **675.0** | 3.0× the estimate, and **1.84× the pessimistic bracket end** | 40,500 s |
| | | **ITEM CEILING 685.0** | the two caps, summed — **not a new budget** | |

Sanaa, 2026-09-03, verbatim: *"still carries a hard per-run cap (set by the team
at ~3× its own estimate, not by me) … The estimate is an instrument, not a
permission slip."* **The deadline lives INSIDE the container**, so the cap stops
the run even if the driver, the daemon and every agent die — `A1WR`'s own kill is
the argument: its driver was polling healthily at 02:24:58Z and the box went down
seven seconds later.

### 5.5 Memory envelope, predicted before the launch (`DAFOAM_CHARTER.md` §7)

**Predicted peak: ≤ 8 GiB per container, one at a time, np = 1.** Basis: `A1WRT`
U1 ran the identical mesh, image and solver at `memory=8g` with
`inspect(exit,oomkilled)=[0 false]`, `memavail_pre_GiB=26.11`,
`memavail_post_GiB=27.42` `[MEASURED, A1WRT ledger.txt:3]`. **Headroom needed:
8 GiB against a ~30.6 GiB box.** No adjoint is built, so §7's A3/A6
mesh-sized-matrix mechanism does not apply and is named as not applying rather
than left unmentioned.

### 5.6 Calibration at completion

**A completion report without the rule-12 comparison is incomplete.** At each
arm's completion a row lands in `docs/COST_CALIBRATION.md` under that file's
append rules and the rule-10 private-index protocol, stating the ratio
actual/predicted, attributing the gap (contention / waste / misprediction, waste
separately named and never absorbed into the ratio), and **naming the item row it
anticipates so no census double-counts** — the census rule
`C-20260903T223309.077366Z-bc699e66` established for `A1WRT`.

---

## 6. `G-CEILING` — THE CUMULATIVE ITEM-CEILING GUARD

> **A ceiling that nothing compares anything to is a number, not an instrument.**

**Registered: before EVERY arm, the guard sums this item's own ledger spend, adds
that arm's registered cap, and REFUSES if the projection crosses the item
ceiling.** A per-arm cap alone cannot see an item walking past its own ceiling one
arm at a time.

**⚠ CORRECTION TO THE DIRECTING BRIEF, AND IT CHANGES WHAT THIS SECTION IS.** The
brief states that `A1WRT`'s driver has **no** cumulative item-ceiling guard and
that only `d6rf_chain_driver.sh:164-169` and `d6rf2_chain_driver.sh:178-179` carry
one. **`A1WRT` carries one, it is implemented at `a1wrt_run_unit.sh:283-317`, and
it FIRED LIVE on the tail unit** `[MEASURED,
cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/launcher.queue.out:4]`:

```
A1WRT_ITEM_CEILING spent_core_min=55.317 + unit_cap=2943.0 = 2998.317 <= ceiling=3304.0 OK
```

**The four-arms-in-three-hours finding belongs to `a1wr_chain_driver.sh` — `A1WR`'s
driver — not to `A1WRT`,** which does not use a chain driver at all: it launches
one unit per invocation of `a1wrt_run_unit.sh`, and the ceiling reading is inside
that launcher. **So this item PORTS a guard it already has, from itself, and adds
the one limb `d6rf` has that it lacks.**

**A1WRT's form is in one respect STRONGER than `d6rf`'s and that limb is kept:**
it refuses on an **UNMEASURED** prior spend (`:296-304`) — *"A zero that means
'could not read' is a planted zero (`CLAUDE.md` rule 3)"* — exiting **65** rather
than assuming zero. `d6rf` has no such branch.
**`d6rf`'s form has two limbs `A1WRT`'s lacks and both are added:** a
**`+0.02` comparison tolerance** against float noise, and a **`STATUS.<arm>` row
written on refusal** so the refusal is durable outside the launcher's stdout.

**The registered union, to be implemented in `a1wrt2_run_arm.sh` (TO BE WRITTEN):**

1. Parse `core_min=` from **every** row of this item's own `ledger.txt`; an
   unparseable ledger ⇒ **`BLOCKED`, exit 65**, never a zero.
2. `PROJ = SPENT + arm_cap`; if `PROJ > 685.0 + 0.02` ⇒ print the spend census,
   write `rc=6 … note=ITEM_CEILING spent=… projected=… ceiling=685.0` to
   `STATUS.<arm>` **and** `chain=ABORT … reason=ITEM_CEILING` to the item status,
   and **exit 6 before the container starts.**
3. Print `A1WRT2_SPEND_CENSUS arm=… spent=… this_arm_cap=… projected=…
   item_ceiling=685.0` on **every** arm, pass or refuse, so the guard's silence is
   never mistaken for its success.

**Its planted control, in both directions, on static fixtures at zero compute:**
a fixture ledger summing **680.0** with `TAIL`'s 675.0 cap must **refuse at 6**;
a fixture summing **3.10** must **pass and print the census**; an unparseable
fixture must **refuse at 65**. **A guard that has never been shown to refuse is a
number.**

> **The class this guard answers, named — and one figure in the directing brief
> is NOT repeated here, because the artefact does not carry it.** The brief states
> `SO3aF2` ran **3.15 %** past its ceiling. What
> `feasibility_SO3a_multipoint/CAP_OVERRUN.txt` actually records, twice, is a
> **per-arm** cap overrun *reported and NOT enforced*: `SO3aF2_ATTRCENSUS` and
> `SO3aF2_ATTRCENSUS_r2`, each `elapsed 120 s > 1.00 x registered CAP 120 s … The
> run was NOT killed`, against a 2.0 core-min cap and a 0.4 core-min estimate
> `[MEASURED, that file]`. **The 3.15 % figure is not in that artefact and this
> lane did not locate it**, so it is not carried forward. **The substance survives
> and is worse than the percentage:** the runner's cap is **advisory, inert and
> off** by construction (`docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md`, D539,
> and switching it on is Sanaa's alone), so the overrun was *reported* by an
> instrument that **cannot stop anything** — which is precisely why this item's
> ceiling is enforced **inside its own launcher, before the container starts**,
> and not by the runner. `A1ZE`'s own ADDENDUM C carries
> the same finding in its own words — *"THE ITEM CEILING OF 370.0 WAS NOT A
> CEILING"* — and adds the general test this item adopts for every guard:
> **can the code path distinguish "the check ran and found nothing" from "the
> check did not run"? If it cannot, its zero must refuse.**

---

## 7. `DAFOAM_CHARTER.md` §2 (FD TABLE) AND §6 (TWO ROWS) — DISCHARGED BY MEASUREMENT, NOT BY ARGUMENT

### 7.1 §2, the FD table — the obligation does not attach, and the promise is STRUCTURAL

§2 binds *"every adjoint gradient"*. **This item computes no gradient: primal
only, undeformed geometry, no optimiser, no trim, no adjoint.** An exemption
argued in prose is worth nothing, so it is made checkable: **`G-NOGRAD` asserts
`compute_totals` appears 0 times in the staged producer**, and the launcher
refuses `BLOCKED` if it does. That is `SO3aF2`'s `NL-2` second clause — *"the
structural half of the no-gradient promise"* — ported by name. **If a successor
ever adds an adjoint arm, `G-NOGRAD` fires and the FD-table obligation attaches
before a core-minute is spent**, which is the point of making it a gate.

### 7.2 §6, shipped and patched are two rows — the obligation is DISCHARGED BY A MEASUREMENT, OR IT BINDS

**`A1WRT` ran `ROW=PATCHED` only** (`dafoam-idwarp-rot:v1`) and its §7 restates the
build confound without discharging it. **This item does not repeat that.**

The patch in the pinned image is the **IDWarp `getRotationMatrix3d`
reverse-derivative** patch, which acts on **mesh-warp derivatives**. This item
runs a fixed, undeformed mesh with no warp in its chain. **That is an argument,
and §6 is not satisfied by arguments** — a version string is not an identity and
neither is a plausible story. So it is converted into a measurement:

> **`G-WARPPROBE`: the run emits `{"warper_init": N, "warper_jacvec": M}` from its
> own process, and the gate reads it off disk.**
>
> - **Both 0 ⇒ the patched library is provably not in the chain of any number this
>   item produces, the shipped/patched distinction cannot move a value, and the
>   two-row obligation is DISCHARGED — with the probe output cited as the
>   discharge.** The record still carries `ROW=PATCHED` on its ledger line, because
>   that is what ran.
> - **Either ≠ 0 ⇒ `GATE FAIL`, and a SHIPPED-image arm becomes owed before any
>   number from this item enters a record.** Its cost is registered now so the
>   obligation is priced rather than discovered: **`SEAM` + `TAIL` re-run on the
>   shipped image ≈ 227.85 core-min, cap 675.0**, and it is **not** launched under
>   this item's ceiling — it is a new item with its own registration.

**Precedent for the probe form:** `S1_FIML_FIELD_INVERSION.md` §1's
`WARP PROBE: {"warper_init": 0, "warper_jacvec": 0}`, cited in
`DAFOAM_CHARTER.md` §2 for exactly this purpose — establishing that a per-cell
field DV has no mesh warp in its chain. **This is that instrument pointed at a
different question.**

---

## 8. THE `rc 127` UNBOUND-VARIABLE CLASS, AS A CHECKED PRECONDITION — AND THE CONTROL THAT DOES **NOT** WORK

**`G-UNBOUND` — registered as a gate, run before the container starts, refusing
`BLOCKED`:** over the frozen launcher, extract every `${VAR}` / `$VAR` expansion,
resolve each against assignments, `read`, `for`-bindings, function parameters and
the environment the queue row declares; **any expansion reachable before its
first assignment, under `set -u`, refuses the launch.** This is
`DAFOAM_CHARTER.md` §18.3's extraction principle — *"an enumeration derived from
the code cannot have that failure mode; a list written from memory always can"* —
applied to shell variables rather than to file dependencies.

**⚠ THE OBVIOUS PLANTED CONTROL DOES NOT WORK, AND THIS IS THE FINDING OF THE
SECTION.** The natural known-positive is `A1WRT`'s own pre-repair launcher, since
`450565e6` records *"`FFD_SRC` and `MD5_FFD` were UNDEFINED under `set -u`, so the
launcher died at 127."* **Measured across every committed version of that file in
this drafting invocation:**

| commit | md5 | `^FFD_SRC=` assignments | `FFD_SRC` uses |
|---|---|---|---|
| `38931ade` | `288bc6904f908eb852e024ca0d61762c` | **0** | **0** |
| `450565e6` | `718b5d47bdc857e074c1f6e6fa18f24f` | 1 | 6 |
| `9a36593a` | `0b00f8bf8d4425131c37bc585e249f4e` | 1 | 6 |
| `01e37859` | `f73191dea23877c99aaf802d21441009` | 1 | 6 |

**The pre-repair blob does not reference `FFD_SRC` at all** — the `S5b` stage did
not yet exist in it. **The defective bytes lived on disk, uncommitted, written by
a lane that was killed mid-edit, and were repaired before anything landed. They
are not in git.** A control anchored on them would be **a control whose
known-positive is not in the searched population, which is not a control** — and
this item declines to build one.

**The registered control instead, and it is guaranteed to be in the population
because it is committed WITH the instrument:**

1. **`fixtures/g_unbound_positive.sh`** — a static committed fixture, six lines,
   carrying `set -u` and one expansion of a variable never assigned. `G-UNBOUND`
   must **FLAG** it. **`EXERCISED-FAIL` expected.**
2. **`fixtures/g_unbound_negative.sh`** — the same file with the assignment
   present. `G-UNBOUND` must **NOT** flag it. **`EXERCISED-PASS` expected.**
3. **A real-world third-party positive, and its limit is stated:** the shape
   `SO3aF2` ADDENDUM 4 §A4.1 measured — OpenFOAM's own `etc/bashrc:180`
   referencing `WM_PROJECT_DIR` before setting it, aborting a `source` under an
   active `set -u`. **`SO3aF2`'s §A4.3 repair is `set +u; source "$LOADER";
   SRC_RC=$?; set -u`, and `G-UNBOUND` must NOT flag that repaired form** —
   otherwise it forbids the one construction that makes sourcing a foreign init
   script legal. **This lane has NOT verified that either the defective or the
   repaired bytes are committed**; item 3 is registered as a *behaviour* the gate
   must exhibit on a fixture reproducing that shape, not as a citation of a blob.

**`set -u` is the right default and it is exactly wrong across a foreign init
script** (`SO3aF2` §A4.2). `G-UNBOUND` therefore carries an explicit allow-list of
`set +u` … `set -u` fenced regions, and **flags a fence that is opened and never
closed** — which is the failure mode the fence itself introduces.

---

## 9. THE REGISTERED PREDICTIONS, AND THE FALSIFIER — WRITTEN BEFORE THE ANSWER EXISTS

**Predictions are scored `HIT` / `MISS`. A `MISS` is a FINDING and is reported as
one; it is never written as `GATE FAIL`. They are not gates and they do not enter
the composition.**

| id | prediction | how scored | what a MISS means |
|---|---|---|---|
| **P1** | `G-SEAM` **PASSES** — the restart loads the state and `SEAM`'s first print reproduces U1's terminal `CL 1.1836353615763` / `CD 0.030758033132912` inside band | the gate's own reading | the continuation is silently cold-starting — the `A1WRT` §2.2 mechanism (*pyDAFoam renames a converged solution back into `0/`*) reaching a CONTINUED arm. **A defect finding, and the most valuable single outcome this item can produce** |
| **P2** | `G-TAILCOUNT` reaches **6 of 6** — every declared point executes and is certified one way or the other | the gate's own reading | the tail is not reachable in one process and the successor is a per-point item |
| **P3** | **ZERO tail points converge** — `satisfied the prescribed tolerance` occurs **0** times across α 13…18 | counted from the log, with the counter shown able to count a planted occurrence | the coupling changes at high α in a way §7's floor analysis does not predict — **a genuine finding about the residual mechanism, and it would be the first convergence this mesh family has ever produced** |
| **P4** | **`dCL/dα` REMAINS POSITIVE across α 13 → 18** | recomputed by the grader from the per-point series | — |
| **P5** | DAFoam prints `Primal solution failed!` for **at least one** point in α 13…18 — i.e. at least one point's residual crosses out of the 1e-6…1e-8 dead band | counted from the log | the dead band swallows the whole tail, and the item's certification channel is blind across its entire range — which would be a finding about the instrument, not the physics |

> ### ⚠ `P4` IS REGISTERED AND IS PREDICTED TO **MISS**
>
> **This lane's honest expectation is that `P4` FAILS.** NACA0012 at α 13…18 is at
> or past the onset of significant separation, `dCL/dα` should flatten and then
> reverse, and `A1WR`'s own α 0…12 body already shows `dCL/dα` **strictly
> decreasing** across its whole range. **`P4` is registered anyway, unhedged, and
> in the direction this lane expects to be wrong**, because a prediction set in
> which every entry is expected to hit is a set chosen to be safe.
>
> **AND IT MAY NOT BE READ AS A STALL MEASUREMENT.** A `P4` MISS is a statement
> about a series of numbers from a model `§10` registers as invalid in this
> regime. **`G-STALL` refuses at exit 2 on any output binding a stall or
> separation word to a numeric angle, and it binds on this row as on every
> other.** The temptation lives exactly here, which is why the gate is carried
> unweakened.

**THE ITEM'S FALSIFIER, singular and stated plainly:** *if `G-SEAM` fails, the
tail this item produces is not a continuation of `A1WR`'s polar and every point in
it is withdrawn as a tail.* The six points would then be six cold-ish solves at
six angles with no established relationship to the α 0…12 body — reported as
that, under `GATE FAIL`, and the item's registered purpose is refuted.

---

## 10. WHAT THIS ITEM MAY NOT CONCLUDE

Inherited from `A1WRT` §7 **unweakened**, and none of it is relaxed:

- **`FEASIBILITY`.** The L3 family has no Roache triple. **No value carries a
  band, none is grid-converged, and `PASS` against a threshold is unavailable on
  any physical quantity.** Ceiling `GATE REACHED`.
- **NO STALL ANGLE IS REPORTED AND NONE MAY BE DERIVED.** `G-STALL` refuses at
  exit 2 on any output binding such a word to a numeric angle. **The tail is
  exactly where that temptation lives.**
- **A non-converged point is not evidence of separation** — it is evidence that
  the steady solver stopped converging, reported with its residual history.
- **A converged high-α point is not evidence of attached flow.** 2-D steady RANS
  with SA past the onset of significant separation is not a valid model of the
  flow at **any** resolution. **Convergence and correctness remain independent
  claims and only the first is measured here.**
- **No adjoint claim.** Primal only, undeformed geometry, no optimiser, no trim.
- **Nothing about `empty`.** §2.1 closed it; this item runs no `empty` arm and its
  results say nothing about that treatment either way.
- **Nothing about the compressible arm**, which remains absent behind a
  DIAGNOSIS and not behind a retry (`A1WRT` §1).
- **Nothing about `symmetry`-versus-`empty` coefficient contamination**, which is
  `A1ZE`'s registered question and is BLOCKED at the toolchain (§2.2).
- **The build confound stands and is restated:** the coarse sweeps ran the
  SHIPPED image; this and `A1WR` run the PATCHED `dafoam-idwarp-rot:v1`. §7.2
  converts it from a caveat into a measurement.

---

## 11. WHAT IS OWED BEFORE THIS CAN FREEZE, AND WHAT IS OWED BEFORE IT CAN LAUNCH

**`[OWED — GATES THE FREEZE]`**

1. **Every instrument written.** `a1wrt2_grade.py` (with the §1 composer and the
   §4 controls), `a1wrt2_run_arm.sh` (with §6's ceiling union and §8's
   `G-UNBOUND`), `a1wrt2_stage.py`, the two static `G-UNBOUND` fixtures, and the
   `G-SEAM` / `G-TAILCOUNT` reference fixtures. **None exists.**
2. **The instrument table enumerated by EXTRACTION, not from memory**
   (`DAFOAM_CHARTER.md` §18.3): every `$HERE/`, `$BASE/`, `$LAUNCHER`-style path
   and every local import pulled out of the frozen scripts, resolved against the
   item directory, and **asserted to EXIST in the freeze commit's tree BEFORE any
   md5 is asserted.** Existence first, separately — *an md5-agreement control can
   read 8 of 8 while a dependency the frozen code executes is absent.*
3. **Every control driven, both directions, with its `EXERCISED-*` state
   printed**, and the selftest's own rc and control count quoted in the freeze
   banner.
4. **The run root `/home/ubuntu/certonomous-runs/A1WRT2/` re-checked ABSENT by
   execution in the freezing shell** — the `CLAUDE.md` rule 2 limb 1 /
   `VERIFICATION_CHARTER.md` §2b condition that makes every pre-freeze edit
   lawful. **Named as the directory that does not exist, and checked, not
   asserted.**

**`[OWED — GATES THE ENQUEUE, NOT THE FREEZE]`**

5. **The `dafoam-supervisor`'s `SUPERVISION_CHARTER.md` §3 check 4, personally**:
   §5's cap arithmetic and §4's control bands read as arithmetic and not as a
   summary. **Not delegable, and a lane's arithmetic is not a substitute for it.**
6. **The §3 check 1 diff read** of every instrument, as a diff.
7. **The queue row drafted and PARKED outside `verification/queue/`** until 5 and
   6 land. **Enqueueing is not authorisation and no lane launches this item.**

**`[OWED — TO THE SUPERVISOR, NOT TO THIS ITEM]`**

8. **The `a1wr_cmd.sh:65-66` swallowed-rc finding (§4.1)** — a live defect in an
   instrument `A1WR`, `A1WRT` and every future member of this family inherit by
   md5. **Reported, not repaired here**: `a1wr_cmd.sh` is a frozen instrument of
   another item, and a lane editing it would break two freezes.
9. **`A1ZE`'s `empty` arms are unreachable inside DAFoam (§2.2)** — that item's
   central gate cannot be satisfied as registered, and its supervisor should know
   before more compute is put behind it.

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---

## 12. CORRECTIONS TO THE DIRECTING BRIEF, RECORDED AS CORRECTIONS

Each was checked against an artefact rather than accepted.

| the brief said | measured | artefact |
|---|---|---|
| `a1wr_chain_driver.sh` is unguarded and **`A1WRT`'s item has no cumulative item-ceiling guard**; only `d6rf`/`d6rf2` have one | **`A1WRT` has one, at `a1wrt_run_unit.sh:283-317`, and it fired live**: `spent=55.317 + cap=2943.0 = 2998.317 <= ceiling=3304.0 OK`. It also carries an **UNMEASURED-refusal limb `d6rf` lacks**. The four-arms finding is `a1wr_chain_driver.sh`'s; `A1WRT` uses no chain driver | `launcher.queue.out:4`; the launcher source |
| the `rc 127` defect is *"the family's signature defect: a pattern applied correctly everywhere except one neighbour"* — usable as the control | **True as an incident; UNUSABLE as a control.** The defective bytes were never committed: the pre-repair blob `288bc690…` references `FFD_SRC` **zero** times. A control anchored there has no known-positive in the searched population | the four historical blobs of `a1wrt_run_unit.sh`, md5'd and grepped |
| `A1WRT` U1 est **32.33** core-min | correct as the registered figure; **actual 55.317, ratio 1.7110** — a 71.1 % overrun on the estimate and 15.32 % of the 361.0 cap. Attribution `NOT SEPARABLE`: contention (63.1–90.5 % busy) and a COLD-vs-CONTINUED anchor mismatch, both named, neither assigned | `A1WRT/ledger.txt:3`; `C-20260903T223309.077366Z-bc699e66` |
| `SO3aF2` ran **3.15 %** past its ceiling and nothing noticed | **NOT REPEATED — the figure is not in the artefact and this lane did not locate it.** `CAP_OVERRUN.txt` records two *per-arm* overruns, `elapsed 120 s > 1.00 x registered CAP 120 s … The run was NOT killed`. **The substance is worse than the number**: the runner's cap is advisory, inert and off by construction, so it reported an overrun it could never stop | `CAP_OVERRUN.txt`; `docs/standards/RUNNER_CAP_ENFORCEMENT_CLAUSE.md` (D539) |
| `A1WRT`'s and `SO3aF2`'s no-verdicts are candidates for the **same** mechanism | **Different mechanisms** (§0.3): `SO3aF2` registered no success token; `A1WRT` registered one and never implemented the emitter. **And the count is three, not two** — `A1WR` has the same unimplemented composition (§0.4) | the four documents and four instruments named in §0 |
| `empty` is *"categorically unusable on this case family"* | **True, and it is sharper than that: it is a DAFoam refusal, not a physics limit.** `DACheckGeometry.C:278` rejects `nGeometricD < 3` unconditionally. Plain OpenFOAM runs `empty` 2-D meshes routinely. **The consequence the brief does not draw: `symmetry` is the only identity DAFoam accepts here, so `A1WRT`'s "blocking physics fix" premise is inverted** | `tail_empty/out/sweep.log`; `A1ZE` `Ec`/`Sc` |

**One thing the brief was right about that this lane initially doubted:** that
`A1WRT`'s no-verdict is a *design* failure rather than a vocabulary gap. It is —
and reading the instrument rather than the prose made it sharper, not softer.

---

**Drafted 2026-09-04 by lab-lane (dafoam). NOT FROZEN, NOT PINNED, NOT ENQUEUED.
No solver, container or queue entry was launched, released or moved, and NO
COMPUTE OF ANY KIND WAS SPENT ON THIS DOCUMENT. Every figure above is read from
an artifact named beside it, and every zero was read by a reader shown able to
return a non-zero.**

### 11.1 AMENDMENT — 2026-09-04, by the dafoam-supervisor. **§11 ITEM 1 IS INSUFFICIENT AS WRITTEN: IT WOULD HAVE READ "EVERY INSTRUMENT WRITTEN" AS SATISFIED WHILE TWO HARD GATES READ AN INPUT NOTHING PRODUCES**

**Lawful because this document is UNFROZEN and no compute has been spent against it** (`CLAUDE.md`
rule 2: before first compute, amendments are legal and must state the condition and how it was
checked). **The condition, checked by execution in the amending invocation and not asserted:** the
run directory `/home/ubuntu/certonomous-runs/A1WRT2` **does not exist**.

**THE DEFECT, MEASURED BY THE SUPERVISOR AT THE NAMED FILES:**

- `a1wrt2_run_arm.sh` contains the string `MANIFEST` **0 times** and `warp_probe` **0 times**.
- `MANIFEST.json` is **read** by the grader at `a1wrt2_grade.py:1137` (inside `grade`) and **written
  at exactly one site in the whole item — `:1390`, inside `_build_happy_root`, WHICH IS THE SELFTEST
  FIXTURE BUILDER.**
- `a1wrt2_stage.py:161` declares it a `PRODUCT`.

**So `G-IMG` and `G-FREEZE` — both HARD gates — plus `G-WARPPROBE` and `G-RC-HONEST` read inputs
that nothing in item 1's list creates at run time.** Item 1 enumerates the instruments and item 2
asserts they EXIST; **neither asks whether anything PRODUCES what the gates consume**, so both would
have passed on an item whose hard gates could only ever have been fed by a test fixture.

> **This is `D6RF2`'s shape one level out: there, `G-DELIVERY` printed `OK 8` while `G-ANCHOR`
> refused on a file `G-DELIVERY` never knew to require. Here an existence check over the DECLARED
> set passes while the PRODUCER of the gates' inputs is absent. A gate frozen without the thing that
> feeds it is not a gate.**

**ITEM 1 IS AMENDED TO ADD, and the wording is the lane's, adopted:**

> *"…and the producer of every name in the stager's `PRODUCTS` tuple, or a named registered statement
> of which is deferred behind `LAUNCH_ENABLED` and what refuses if it is absent."*

**AND A NEW ITEM 1a:** for every gate, the artefact it reads must be traced to a producer **in the
registered set** or to a registered deferral, **and the trace is asserted by extraction rather than
by reading** — the same instrument discipline §11 item 2 already applies to existence. **The
extractor does not do this today; the lane measured finding 5 by reading two named files and said
so.** *Buildable, not built, and named here rather than left for a freeze to discover.*

**NOTHING ELSE IN THIS DOCUMENT MOVES.** No gate, threshold, band, cap, label, prediction or cost
figure is altered by this amendment; it makes the FREEZE GATE stricter and nothing else. `PASS`
remains unreachable by construction and `P4` remains registered unhedged and predicted to MISS.

### 11.2 AMENDMENT — 2026-09-04, the `dafoam-supervisor`'s TWO RULINGS IMPLEMENTED, AND §11.1 ITEM 1a BUILT. **§3's SAME-PROCESS CLAUSE IS STRUCK BY QUOTE.**

**Lawful because this document is UNFROZEN and no compute has been spent against it**
(`CLAUDE.md` rule 2 limb 1: before first compute, amendments are legal **and must state the
condition and how it was checked**). **The condition, CHECKED BY EXECUTION in this amending
invocation and not asserted:** the run directory `/home/ubuntu/certonomous-runs/A1WRT2`
**does not exist** — `ls -la` and `ls -d` both returned rc=2, *"No such file or directory"*,
at **2026-09-04T21:48:07Z** and again at **2026-09-04T22:06:40Z**.

> **⚠ BOTH RULINGS ONLY ADD REFUSALS, AND THAT IS MADE STRUCTURAL RATHER THAN ASSERTED.**
> Neither can move a verdict toward `PASS`. The composer reaches `GATE REACHED` only when no
> gate reports `NOT A RESULT`, `BLOCKED` or `GATE FAIL`, so a NEW gate can only move a verdict
> DOWN; and the two-arm fold uses `worse_of`, which is **monotone downward over all 36 ordered
> pairs of the six tokens** — driven by `Q-ARMFOLD-add-only`. `PASS` remains unreachable by
> registration and `P4` remains registered unhedged and predicted to MISS.

---

#### 11.2.1 RULING 1 — §3's *"in the same process"* IS **STRUCK BY QUOTE**

**The struck text, quoted verbatim from §3's arm table, `TAIL` row, `start` column. It is
STRUCK, NOT REWRITTEN, and the original stands above unaltered (`CLAUDE.md` rule 6):**

> ~~CONTINUED from `SEAM`'s final state, in the same process~~

**REPLACED BY:** *CONTINUED from `SEAM`'s landed final state, in a SEPARATE PROCESS on a
SEPARATE TREE, and only if `SEAM`'s verdict permits it.*

**THE REASON, AND IT IS NOT BOOKKEEPING.** `G-SEAM` is this item's **registered falsifier**
(§9): if it fails, every tail point is withdrawn *as a tail*. **A single process spanning both
arms would have ALREADY COMPUTED THE TAIL by the time the seam could be graded — so the
falsifier could not stop the spend it exists to stop.** `SEAM` is **10.0** core-min and `TAIL`
is **675.0** (§5.4). **675 core-min riding on a control that cannot gate it is not a control;
it is a post-hoc report wearing a stop rule's name** — the shape this family has already met
in an in-container deadline and in a cap watch.

**THE STOP RULE, AS A CHECKED PRECONDITION AND NOT A CONVENTION.** `a1wrt2_grade.py` gains
`seam_precondition(root)` and the CLI entry `--seam-precond ROOT`; `a1wrt2_run_arm.sh` gains
`seam_precondition_guard`, which runs **for the `TAIL` arm only, before the ceiling guard and
before the container**, and exits **7** on anything but `PASS`, writing a durable
`note=SEAM_PRECONDITION_REFUSED` row to `STATUS.TAIL`. `SEAM` carries no such precondition —
**it *is* the precondition**, and a control asserts the guard does not gate it.

**The precondition emits NO item verdict.** §1 reserves `A1WRT2_VERDICT` to `compose_item`; a
launch guard that printed one would be a second emitter for the exact reason this item exists.
`Q-SEAMPRE-no-item-verdict` drives that.

**DRIVEN IN BOTH DIRECTIONS, ON REAL TREES, AT ZERO COMPUTE** — six grader controls and five
launcher controls:

| control | direction | measured |
|---|---|---|
| `Q-SEAMPRE-clean-permits` | pass | a clean SEAM arm → `PASS`, TAIL permitted |
| `Q-SEAMPRE-outside-band-refuses` | fail | SEAM CL perturbed by **6.013254e-03** — the MEASURED `A1WR`-vs-U1 magnitude, 6.0× the 1.0e-03 band → `GATE FAIL`, TAIL refused; restored → `PASS` |
| `Q-SEAMPRE-rc-refuses` | fail | SEAM rc=97 → `GATE FAIL`, TAIL refused |
| `Q-SEAMPRE-absent-blocks` | fail | SEAM arm absent → `BLOCKED`. **An unrun falsifier never reads as a cleared one** |
| `Q-SEAMPRE-rc-absent-blocks` | fail | SEAM rc artefact absent → `BLOCKED` (a missing rc is not rc=0) |
| `seam-precond/absent-seam-refuses-TAIL-at-7` | launcher | rc=**7** |
| `seam-precond/clean-seam-permits-TAIL` | launcher | rc=**0** |
| `seam-precond/seam-rc-97-refuses-TAIL-at-7` | launcher | rc=**7** |
| `seam-precond/does-not-gate-the-SEAM-arm` | launcher | rc=**0** — the limb without which the control could not tell a working precondition from a launcher that refuses everything |
| `seam-precond/status-row-durable` | launcher | `STATUS.TAIL` carries the refusal outside stdout |

> **⚠ A CONSEQUENCE THE RULING SURFACED IN THE EXISTING CONTROLS, REPORTED RATHER THAN
> ABSORBED.** Re-running the launcher selftest unchanged, **two ceiling controls that had
> always passed came back rc=7**: `ceiling/under-passes-and-prints` and
> `ceiling/exactly-at-ceiling-passes`. Not a regression — they drove `--arm TAIL` against a run
> root with **no SEAM arm**, so what they were actually asserting was *"the launcher exits 0"*,
> which conflates the ceiling limb with every other reason the arm might proceed. **A control
> that cannot separate the limb it names from the rest of the launcher passes for reasons it
> does not state.** A clean SEAM arm is now staged into every fixture root that drives `TAIL`,
> so the ceiling controls test the ceiling and the precondition controls test the precondition.

---

#### 11.2.2 RULING 2 — BOTH ARMS. **AND THE RULING'S PREMISE IS AN UNDERSTATEMENT, MEASURED**

**The ruling is right about the rc clause and is CORRECTED UPWARD on the completion clause.**
`grade()` read `TAIL/out/rc` at one site and `SEAM/out/rc` at **none** — the §4.1 asymmetry
reproduced in the successor written to repair it, landing on the arm that carries the
falsifier. **But a token census over `a1wrt2_grade.py`, run with `G-RC-HONEST` (17 hits) as the
live positive control so a zero is not believed from a reader never shown able to return a
non-zero (`CLAUDE.md` rule 3), returned:**

| token | hits in `a1wrt2_grade.py` (pre-amendment) |
|---|---|
| `G-RC-HONEST` — **the positive control, known present** | **17** |
| `endTime` | **0** |
| `"End"` | **0** |
| `G-COMPLETE` | **0** |
| `age guard` | **0** |

**SO THE RULE-4 COMPLETION WAS NOT IMPLEMENTED FOR *EITHER* ARM.** Only rule 4's rc clause
existed, and only on `TAIL`. The ruling is adopted in the stronger form its own reasoning
requires.

**`G-COMPLETE` IS ADDED TO THE HARD LIST**, per arm, folded with `worse_of`. It checks: the rc
artefact **exists** (absent → REFUSE); an `End` line; `AOA_SWEEP_TRUNCATED` **absent**;
`AOA_SWEEP_END` present (missing → `NOT A RESULT`); and **last time == `endTime`, where
`endTime` is read out of THE ARM'S OWN staged `system/controlDict`** — never a constant
retyped in the grader — with an absent or unparseable controlDict **refusing**.

**WHAT `G-COMPLETE` DOES *NOT* CHECK IS NAMED, NOT OMITTED:**
- **`ExecutionTime` count == `endTime`** — **NOT APPLICABLE and it would be WRONG to assert
  it.** This producer prints `Time =` at the write interval, not per iteration: `A1WRT` U1
  carries **41** anchored `^Time = ` lines for **4,000** iterations. A clause copied across
  families because it appears in rule 4's thermal-family enumeration would fail every good run
  of this one.
- **`fields present (T U p_rgh alphat nut k omega)`** — that enumeration is the **thermal**
  family's; this is incompressible with no `T` and no `p_rgh`. The structural equivalent here
  is `G-COLDSTART-SEAM`, which asserts the staged `4000/U` is NONUNIFORM.
- **The age guard** — enforced at **STAGE** time and by construction, not by comparison:
  `a1wrt2_stage.py` clause (12) asserts before the run that every staged file is NOT NEWER than
  the datum **and** that every `PRODUCTS` name is ABSENT, *"so a product can only appear by
  being produced"*.
- **Per-point terminal times** are **reported, not gated**. Clause 5 binds the **last** point
  only: this lane could not establish the producer's per-point time bookkeeping across a
  six-point continued sweep without running it, and **a gate written on a guess would fail good
  runs, which is a worse defect than the one being repaired.**

**THE CONTROL THE RULING ASKED FOR, DRIVEN — the combination that was invisible:**

| control | measured |
|---|---|
| **`Q-ARMFOLD-seam-rc-97`** | **SEAM rc 0→97 with TAIL rc CLEAN: `GATE REACHED` → `GATE FAIL` → restored `GATE REACHED`.** Before this change the grader read `TAIL/out/rc` and nothing else, so this exact combination could not be seen — on the arm carrying the falsifier |
| `Q-ARMFOLD-seam-no-End` | SEAM's `End` line removed → `GATE FAIL`, restored → `GATE REACHED` |
| `Q-ARMFOLD-tail-short-of-endTime` | TAIL's last `Time = 8200` → `8100` against the controlDict's `endTime 8200` → `GATE FAIL`, restored |
| `Q-ARMFOLD-controldict-absent-refuses` | the arm's own controlDict removed → **REFUSE exit 2** |
| `Q-ARMFOLD-dropped-arm-refuses` | an arm ABSENT from either fold **REFUSES** — the asymmetry reappearing as a missing dict key |
| `Q-ARMFOLD-add-only` | `worse_of` monotone downward over **all 36** ordered pairs |
| `Q-ARMFOLD-ordering` | the fold uses the **composer's chain**, not `_OPTIMISM`: chain says `NOT A RESULT` where the ordinal would say `BLOCKED`. The disagreement disclosed at `_OPTIMISM` is pinned by a second test rather than inherited |

---

#### 11.2.3 §11.1 ITEM 1a — THE PRODUCER TRACE, BUILT, PLANTED BOTH WAYS, AND IT FOUND MORE

`a1wrt2_instruments.py` gains `producer_trace`: **every run-root artefact a gate READS on the
graded path is traced to a PRODUCER in the registered set or to a NAMED REGISTERED DEFERRAL,
and `main` returns non-zero on anything else.**

**THE DISCRIMINATOR IS DERIVED, NOT LISTED.** A hand-written list of "fixture builder" names
would carry the same failure mode as every other list written from memory. Instead each
module's own **call graph** is built from its AST: a write reachable from `main` is a producer;
one reachable **only** from `selftest` is a fixture; one reachable from neither is reported.

> **⚠ THE FIRST DRIVE OF THIS TRACE PRINTED A CLEAN TABLE OVER THE VERY DEFECT §11.1 IS ABOUT,
> AND THE CAUSE IS RECORDED BECAUSE IT IS RULE 3 ONE LEVEL UP.** It reported
> `MANIFEST.json  TRACED <- a1wrt2_grade.py:1390 in _build_happy_root [GRADED]`. **Every
> instrument in this item has `main` dispatch `--selftest` to `selftest()`**, so an unstopped
> walk from `main` reaches every fixture builder and the graded/fixture split collapses to
> *"everything is graded"*. `selftest` is now a **CUT NODE** on the graded walk, and
> `producer/cut-node-is-load-bearing` drives the difference: the uncut walk reaches
> `_build_happy_root` (51 functions), the cut walk does not (40). **A checker that has only
> ever reported "all traced" is not evidence.**

**`PRODUCTS` IS DELIBERATELY EXCLUDED FROM THE PRODUCER SET**, and the exclusion is printed
rather than assumed: it declares what the RUN must create, **not that anything creates it**.
Reading it as a producer is precisely the confusion §11.1 caught.
`producer/PRODUCTS-is-not-a-producer` drives that all 7 of its names still trace on their own
merits.

**MEASURED, BEFORE ANY REPAIR** — the trace generalises the supervisor's finding from one
artefact to six:

> **8 gate inputs consumed, 2 traced, 6 UNTRACED** — five written at exactly one site each,
> all inside `_build_happy_root`, **the selftest fixture builder** (`MANIFEST.json`,
> `SEAM/out/sweep.log`, `TAIL/out/sweep.log`, `TAIL/out/rc`, `ledger.txt`), and one
> (`TAIL/out/warp_probe.json`) **written by nothing anywhere.**

**PLANTED BOTH WAYS, ON REAL TREES** (real copies of this item's directory, one thing changed):

| control | direction | measured |
|---|---|---|
| `producer/real-tree-traces-clean` | pass | 9 consumed, **8 traced, 1 deferred, 0 untraced** |
| `producer/removed-producer-is-flagged` | fail | `MANIFEST_PATH` repointed out of the run root → `MANIFEST.json` flagged. **It is the only input of the HARD gates `G-IMG` and `G-FREEZE`** |
| `producer/fixture-only-write-is-flagged` | fail | the §11.1 shape itself: the producer moved out of the graded path → attributed to `_build_happy_root [FIXTURE]` and reported UNTRACED |
| `producer/cut-node-is-load-bearing` | pass | 51 functions uncut vs 40 cut |
| `producer/deferral-without-refusal-flagged` | fail | `refuses_if_absent` removed → registry defect. **A deferral without a refusal is a hole with a name** |
| `producer/PRODUCTS-is-not-a-producer` | pass | 7 names excluded; all 7 trace on their own merits |

**THE PRODUCERS ARE NOW WRITTEN, IN `a1wrt2_run_arm.sh`, AND DRIVEN AT ZERO COMPUTE:**
`MANIFEST.json`, `ledger.txt`, both arms' `out/sweep.log` and `out/rc`. The container bodies
stay **behind `LAUNCH_ENABLED=0`**, which no agent may raise; that is honest rather than a hole
because **`read_text` REFUSES at exit 2 on an absent artefact**, so a product not yet created
reads as a refusal and never as a passing gate.

> **⚠ AND `G-IMG` WOULD HAVE BEEN A MIRROR.** `G-IMG` compares the manifest's `image_digest`
> and `libidwarp_md5` against `PIN_IMG_DIGEST` / `PIN_IDWARP_MD5`. **A producer that wrote
> those fields FROM those same constants would have made the hard gate compare a pin to a copy
> of itself and report `PASS` on any image whatsoever.** `measure_image_pins` therefore reads
> both OUT OF THE IMAGE, and an `UNMEASURED` value makes `G-IMG` **REFUSE at exit 4** — it
> never falls back to the pin. Driven: `producer/unmeasured-digest-refuses` (REFUSE 4) and
> `producer/measured-digest-passes` (PASS), so the refusing limb is not merely a gate that
> refuses everything. **`measure_image_pins` ITSELF IS `NOT EXERCISED`** — driving it needs the
> pinned image and this item is not frozen — **and is declared in that third state, never
> counted as a pass.**

---

#### 11.2.4 ⚠ THE FINDING THAT COSTS THIS ITEM A REGISTERED DISCHARGE — §7.2

**`TAIL/out/warp_probe.json` has NO PRODUCER ANYWHERE**, and it is `G-WARPPROBE`'s only input.
Measured 2026-09-04 over three named files:

| file | `warp_probe` occurrences |
|---|---|
| `a1wr_runScript_incomp.py` — the frozen producer this item stages | **0** |
| `a1wr_cmd.sh` — the frozen container command | **0** |
| `a1wrt2_run_arm.sh` — this item's own launcher | **0** |

The only write anywhere is `a1wrt2_grade.py:1380`, **inside `_build_happy_root`**.

**IT CANNOT BE REPAIRED BY THIS LANE, AND THE REASON IS A RULE AND NOT A DIFFICULTY.** Emitting
the probe means counting `warper_init` / `warper_jacvec` calls from inside the running process,
which means editing `a1wr_runScript_incomp.py` — **another item's FROZEN instrument**
(`CLAUDE.md` rule 6). **Reported, not repaired.** It is registered in
`a1wrt2_stage.DEFERRED_PRODUCERS` with its producer, its reason, and its refusal, and the
refusal is **driven**: `Q-DEFERRAL-warpprobe-absent-refuses` removes the artefact from a real
happy root and requires the grade to **REFUSE at exit 2**.

> **CONSEQUENCE, STATED HERE RATHER THAN LEFT FOR THE FREEZE TO DISCOVER: §7.2's DISCHARGE IS
> NOT AVAILABLE AS THIS ITEM STANDS.** §7.2 registers `G-WARPPROBE` as what discharges
> `DAFOAM_CHARTER.md` §6's two-row obligation — *"with the probe output cited as the
> discharge"*. **The item was one freeze away from discharging a CHARTER OBLIGATION with a
> number only its own test fixture could ever produce.** The gate still exists and still
> refuses; what it can no longer do is **discharge**. **The §6 two-row obligation therefore
> BINDS** unless a successor writes the producer — which is a **new item**, because it needs a
> non-frozen producer. Whether §7.2 is rewritten before the freeze or the obligation is carried
> is **the supervisor's call and is not taken here.**

---

#### 11.2.5 WHAT WAS DRIVEN, AND WHAT WAS NOT

**Every selftest, under `python3` AND under `python3 -O`, rc=0 in both:**

| instrument | legs | controls | EXERCISED-FAIL | EXERCISED-PASS | NOT EXERCISED |
|---|---|---|---|---|---|
| `a1wrt2_grade.py` | 7 | **77** | 48 | 29 | **0** |
| `a1wrt2_instruments.py` | 7 | **17** | 10 | 7 | **0** |
| `a1wrt2_run_arm.sh` | — | 21 | 20 driven | — | 1 **declared** (`measure_image_pins`) |
| `a1wrt2_stage.py` | — | unchanged, re-driven clean | — | — | 0 |

`ast.Assert` = **0** in `a1wrt2_grade.py` (2,954 lines), `a1wrt2_instruments.py` (1,666) and
`a1wrt2_stage.py` (1,254), each audited by its own file's `Q-NOASSERT` / `noassert` control
shown able to see a planted one. `a1wrt2_instruments.py` with no arguments returns **rc=0**:
existence clean, coverage clean, **producer trace clean**.

**NOT ESTABLISHED, AND NOT CLAIMED:**
1. **`measure_image_pins` has never run.** The image digest and `libidwarp` md5 have not been
   read out of the image by this item's own code. What is driven is the REFUSAL on `UNMEASURED`.
2. **The producer's per-point time bookkeeping across a six-point continued sweep.** Clause 5
   binds the last point only, and §11.2.2 says why.
3. **Whether `startTime 4200 / endTime 8200` is the right TAIL configuration for six points.**
   The stager writes it and `G-COMPLETE` now reads it back rather than retyping it, so a
   disagreement would surface as a `GATE FAIL` rather than silently — but the configuration
   itself is unverified and is **the supervisor's §3 check 4 to read as arithmetic.**
4. **Nothing about the physics.** No solver ran. `LAUNCH_ENABLED` is still **0**.

**NOT FROZEN. NOT PINNED. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT.
SUBMISSIONS PARKED — nothing here is filed, sent, uploaded, posted or registered anywhere.**

### 11.3 AMENDMENT — 2026-09-05, by `lab-lane` (dafoam) on the `dafoam-supervisor`'s SINGLE-PASS CENSUS ORDER. **THE RULED §7.2 STRIKE IS IMPLEMENTED, AND A SECOND INPUT WITH NO PRODUCER IS MEASURED — THIS ONE STOPS THE STAGER BEFORE ANY GATE IS REACHED.**

**Lawful because this document is UNFROZEN and no compute has been spent against it** (`CLAUDE.md`
rule 2 limb 1: before first compute, amendments are legal **and must state the condition and how it
was checked**). **The condition, CHECKED BY EXECUTION in this amending invocation and not asserted:**
the run directory `/home/ubuntu/certonomous-runs/A1WRT2` **does not exist** — `ls -d` and `ls -la`
both returned rc=2 in the same shell invocation that appended this section, timestamps printed to
that invocation's own output.

**`CLAUDE.md` rule 6, asserted by measurement and not by claim: lines whose number changed above this
section: 0.** The amendment is APPENDED at the foot; the first 1,151 lines of this file were
compared byte-for-byte against the committed blob `d1b47625f80e3a6f3e642735f74df74fda7944b6` at
`HEAD` in the appending invocation and are **identical**. Nothing above §11.3 is rewritten, and the
struck text in §11.3.1 is struck **by quote**, its original standing unaltered at §7.2.

> **⚠ WHAT THIS AMENDMENT DOES AND DOES NOT DO.** It **implements a ruling already issued** (§11.3.1),
> and it **registers measurements and predictions** (§11.3.2–§11.3.4). **No gate, threshold, band,
> cap, label or cost figure is altered by this lane.** The two arithmetic defects found in §5 are
> **REPORTED, NOT REPAIRED HERE** — a cap is a registered figure and moving one is the supervisor's
> §3 check 4, not a lane's. `PASS` remains unreachable by construction, `P4` remains registered
> UNHEDGED and predicted to MISS, and the ceiling remains `GATE REACHED`.

---

#### 11.3.1 THE RULED §7.2 STRIKE, IMPLEMENTED. **`DAFOAM_CHARTER.md` §6's TWO-ROW OBLIGATION BINDS AND THIS ITEM SHIPS ONE ROW, LABELLED.**

**The `dafoam-supervisor` ruled on §11.2.4's finding: `G-WARPPROBE` has no producer, cannot get one
inside this item (its only possible producers are another item's FROZEN instruments), and the
two-row obligation therefore BINDS. The item ships ONE row, `PATCHED`, labelled as such, and not a
full charter-§6 verdict.** That ruling is settled and is not reopened here; what follows is its
implementation in the registration.

**THE STRUCK TEXT, quoted verbatim from §7.2's registered bullet. IT IS STRUCK, NOT REWRITTEN, and
the original stands above unaltered (`CLAUDE.md` rule 6):**

> ~~Both 0 ⇒ the patched library is provably not in the chain of any number this item produces, the
> shipped/patched distinction cannot move a value, and the two-row obligation is DISCHARGED — with
> the probe output cited as the discharge.~~

**REPLACED BY:** *Both 0 ⇒ `G-WARPPROBE` reports `PASS` and that is **all** it reports. **It
discharges nothing.** `DAFOAM_CHARTER.md` §6's two-row obligation **BINDS** and is carried forward
unsatisfied. This item ships **ONE ROW — `PATCHED`, `dafoam-idwarp-rot:v1`,
`sha256:2927768a16ac…`, `libidwarp` md5 `85f59e87253e0a71a813f64ca6e4c425`** — and **every record
this item produces carries that row LABELLED AS A SINGLE ROW AGAINST A BINDING TWO-ROW
OBLIGATION**, never as a discharged one.*

**AND THE SECOND BULLET'S CONSEQUENT IS STRUCK IN THE SAME BREATH, because it was the other half of
a discharge that no longer exists:**

> ~~either ≠ 0 ⇒ `GATE FAIL`, and a SHIPPED-image arm becomes owed before any number from this item
> enters a record~~

**REPLACED BY:** *either ≠ 0 ⇒ `GATE FAIL`. **The SHIPPED-image arm is owed EITHER WAY** — that is
what "the obligation binds" means — and the `≠ 0` case additionally makes the patched library
demonstrably live in the chain, which is a finding about the number and not only about the paperwork.
Its cost stays registered at **`SEAM` + `TAIL` on the shipped image ≈ 227.85 core-min, cap 675.0**,
**not** launched under this item's ceiling, and it is a NEW ITEM with its own registration.*

**MEASURED, so the label is not a promise:** `a1wrt2_run_arm.sh:343` already writes
`ARM=$arm ROW=PATCHED IMG=$IMG …` into `ledger.txt` — **one row, named `PATCHED`, produced by the
launcher and not by a fixture** (it is one of the five artefacts §11.2.3's producer trace resolves to
`a1wrt2_run_arm.sh` on the GRADED path). **The registration and the instrument now say the same
thing**, which is what §11.2.4 said they did not.

**WHAT IS STILL OWED TO THE CHARTER, STATED AND NOT BURIED:** `DAFOAM_CHARTER.md` §6 is **NOT
SATISFIED BY THIS ITEM.** No reading of this document may cite `A1WRT2` as discharging it.

---

#### 11.3.2 ⚠ THE CENSUS FOUND A SECOND INPUT WITH NO PRODUCER, AND IT IS UPSTREAM OF EVERY GATE: **NOTHING IN THE REGISTERED SET PRODUCES A CONTINUED `system/controlDict`, SO `stage()` REFUSES BOTH ARMS AT CLAUSE (9) AND ZERO OF SEVEN POINTS RUN — AGAIN.**

**This is §11.1's defect one level EARLIER.** §11.1 caught a HARD gate whose input only a fixture
wrote. This is a **stager PRECONDITION** whose input **nothing writes at all** — and the stager runs
before the container, so the item would not reach a gate to fail at. **It would `BLOCK` at zero
physics, which is the exact outcome this item exists to break.**

**MEASURED BY EXECUTION IN THIS INVOCATION, over named files:**

| what was measured | result | artefact |
|---|---|---|
| `controlDict` occurrences in the FROZEN producer | **0** | `a1wr_runScript_incomp.py`, md5 `d48f48c5e2e41e86981acbf6feccb3c4` — re-measured here and **matching §3's registered pin** |
| `controlDict` occurrences in this item's launcher | **0** | `a1wrt2_run_arm.sh` |
| the stager's stance | **REFUSES, DOES NOT AUTHOR** | `a1wrt2_stage.py:590-611`, clause (9), verbatim: *"This file REFUSES rather than authoring a controlDict: no instrument in draft section 11 derives a CONTINUED one"* |
| the REAL staging source's `controlDict` | `startFrom startTime; startTime 0; stopAt endTime; endTime 4000; deltaT 1; writeInterval 4000;` | `/home/ubuntu/certonomous-runs/A1WRT/alpha12_symmetry/system/controlDict` |
| clause (9)'s predicate `("latestTime" in cdt) or _startTime_is(cdt, "4000")` driven against those REAL bytes | **`False` → `abort("CONTROLDICT_NOT_CONTINUED", code 5)`** | the real predicate imported from `a1wrt2_stage.py` and called on the real file |

**THE ZERO IS PLANTED, BOTH LIMBS (`CLAUDE.md` rule 3).** The predicate was first driven against two
mutations of those same real bytes — `startFrom startTime` → `startFrom latestTime`, and
`startTime 0` → `startTime 4000` — and **returned `True` on each**, the two limbs separately. **A
reader shown able to return `True` then returned `False` on the unmutated file.** The mutation was
asserted to have changed the bytes before the predicate was driven.

> **WHY THE §11.2.3 PRODUCER TRACE DID NOT CATCH IT, REPORTED RATHER THAN ABSORBED.** The trace's own
> output puts `RUNROOT:$/case/system/controlDict` under **`DYNAMIC REFERENCES: REPORTED, NOT
> GATED`** — the path is assembled at run time, so it falls out of the traced set and into a bucket
> that is printed and not enforced. **The instrument that exists to find inputs with no producer
> printed this one in its own output, in a section headed "not gated", and the item nearly froze
> over it.** That is a real limit of the trace and it is registered as such below, not repaired here.

**THE MECHANISM IS ALSO MEASURED, AND IT DISCRIMINATES BETWEEN TWO DESIGNS THE REGISTRATION DOES NOT
DISTINGUISH.** `A1WR`'s 13-point `CONTINUED` sweep and `A1WRT` U1's 1-point `COLD` sweep were parsed
per point:

| run | mode | points | first `^Time = ` per point | last `^Time = ` per point | anchored `Time =` lines per point |
|---|---|---|---|---|---|
| `A1WR/STAGE12/sweep_I` | `CONTINUED` | idx 0…12 complete | **1**, every point | **4000**, every point | **41**, every point |
| same, idx 13 (α = 13) | — | killed mid-point | 1 | **2500** | 26 |
| `A1WRT/alpha12_symmetry` | `COLD` | idx 0 | **1** | **4000** | **41** |

**FOURTEEN measured points, and the OpenFOAM time counter RESETS TO 1 AT EVERY POINT.** The
producer's `CONTINUED` mode is an **in-process warm start** — `prob.run_model()` called once per α on
one `Top()` problem, the field state carried in memory — **not an OpenFOAM `latestTime` restart.**
`endTime` is therefore **PER POINT**, not a global counter.

**THREE CONSEQUENCES, EACH STATED AS WHAT IT IS:**

1. **`endTime 8200` is registered nowhere and is wrong under either hypothesis.** The value lives
   only in fixture builders (`a1wrt2_grade.py:1673`, `a1wrt2_stage.py:957`) — **the same
   fixture-only-writer shape as `MANIFEST.json`.** Under the MEASURED per-point reset it gives each
   tail point **8,200** iterations, **2.05×** §3's registered 4,000. Under the alternative
   global-counter hypothesis it gives the whole six-point arm 4,000 iterations, **≈667 per point,
   6× too few.** §3's arm table (*"4,000 each"*) and §5's cost line (*"6 points × 4,000 it"*) are
   the registration; **8200 contradicts both.**
2. **The registered continuation mechanism has NEVER BEEN RUN.** `startFrom latestTime` appears in
   **zero** of the fourteen measured points. §3's `start` column, `G-COLDSTART-SEAM`
   (`a1wrt2_grade.py:448-469`: `4000/U` present and NONUNIFORM, **`0/` REFUSED if it exists**) and
   `G-COMPLETE`'s `last time == endTime` all encode a disk-restart this producer has not been shown
   to accept. **§11.2.2 forbids exactly this: *"a gate written on a guess would fail good runs,
   which is a worse defect than the one being repaired."***
3. **The falsifier for all of it already exists, is registered, and costs 10 core-min.** `SEAM`'s
   entire registered job is *"that the restart actually loaded the state"*, and §11.2.1's
   `seam_precondition_guard` **refuses `TAIL` at rc=7 on anything but `PASS`**. **So the unresolved
   question is bounded at `SEAM`'s 10.0 core-min cap — 1.46 % of the 685.0 item ceiling — and the
   675.0 core-min `TAIL` arm cannot be spent on a wrong answer to it.**

**THIS LANE DOES NOT CHOOSE BETWEEN THE TWO DESIGNS AND SAYS SO.** Both are registration-level and
both move a HARD gate:

* **Design L (`latestTime`)** — commit two static, md5-pinned `controlDict` fixtures under
  `fixtures/`, stage them by name so clause (9) still **asserts and never authors**, and let `SEAM`
  test whether this producer honours a disk restart. **Keeps §3, `G-COLDSTART-SEAM` and §5 exactly
  as registered.** Registered prediction if adopted: **`P-SEAMTIME` — `SEAM`'s log will carry
  `^Time = ` first 4001 and last 4200. If it carries first 1, the producer resets the counter on a
  `latestTime` start too, `G-COMPLETE` reports `GATE FAIL`, the seam precondition refuses `TAIL`,
  and the item stops at ≤ 10.0 core-min with the mechanism MEASURED for the first time.**
* **Design S (`startTime 0`, the fourteen-times-measured form)** — stage `A1WRT` U1's `4000/` fields
  as the arm's `0/` and run `startFrom startTime; startTime 0; endTime 200`. **The continuation is
  then on the only configuration this producer has ever been run with.** But it **REFUSES against
  `G-COLDSTART-SEAM` as registered**, which aborts when `0/` exists — so adopting it requires
  striking and replacing that HARD gate's form (its *intent*, "a continued arm actually carries a
  field", is preserved and would be re-registered on `0/U`).

**BOTH ARE THE SUPERVISOR'S CALL under `SUPERVISION_CHARTER.md` §3 check 4, and neither is taken
here.** Design L is the smaller change and is the one that **buys the measurement**; Design S is the
one that is **already measured** and buys the tail. **Design L costs 10 core-min to find out; Design
S costs a HARD gate's re-registration to avoid finding out.**

---

#### 11.3.3 THE PROCEDURAL GAPS, REGISTERED AS PREDICTIONS RATHER THAN USED AS REASONS NOT TO RUN

**Each is an instrument this item does NOT have. What it would have caught is named, and the risk is
accepted in writing.** *An unbuilt instrument recorded as a risk is science; an unbuilt instrument
used as a reason not to run is governance.*

| # | not built | what it would have caught | risk accepted, and its bound |
|---|---|---|---|
| **B1** | `measure_image_pins` is **half driven**. Its **digest limb IS NOW MEASURED**: `docker image inspect --format '{{index .RepoDigests 0}}'` on `dafoam-idwarp-rot:v1` returned `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, **exactly `PIN_IMG_DIGEST`**, at **zero compute — `image inspect` starts no container**. Its `libidwarp` md5 limb needs one `docker run md5sum` and stays **`NOT EXERCISED`, declared, never counted as a pass** | a broken md5 one-liner → `warp=UNMEASURED` → `G-IMG` **REFUSES at exit 4** | **BOUNDED AT `SEAM`'s 10.0 core-min.** `G-IMG` is HARD, so `SEAM` grades `NOT A RESULT`, the seam precondition refuses `TAIL` at rc=7, and `TAIL`'s 675.0 is never spent. **The pin itself is corroborated independently and MEASURED**: `A1WRT`'s own unit log line 4 carries `A1WRT_IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` from **inside a container on this same image**. What is unmeasured is this launcher's one-liner, not the value |
| **B2** | the §11.2.3 producer trace does **not gate DYNAMIC references**; it prints them under `REPORTED, NOT GATED` | **§11.3.2 itself** — the trace printed `RUNROOT:$/case/system/controlDict` in that bucket. **A checker that reports the class it exists to gate, in a section headed "not gated", found the defect and did not stop it** | accepted. The bucket is 8 entries and is printed on every run; a reader who reads the trace's whole output sees them. **Widening the trace to resolve run-time-assembled paths is a NEW ITEM, not a pre-freeze edit** |
| **B3** | per-point terminal-time bookkeeping is **reported, not gated**; clause 5 binds the LAST point only | a middle point that stopped early while the last one completed | accepted, and now **partly retired by measurement**: §11.3.2's fourteen points show 41 anchored `Time =` lines and last `Time = 4000` for every complete point, so a per-point clause is now derivable — **but deriving it from 14 points of one configuration and freezing it as a gate is exactly the guess §11.2.2 forbids.** Registered as a **successor's** gate |
| **B4** | `G-UNBOUND` item 3 (the OpenFOAM `etc/bashrc:180` shape) is registered as a **behaviour on a fixture**, not as a citation of a committed blob | a `set +u … set -u` fence repair the gate wrongly forbids | accepted and already disclosed at §8 item 3. **The two static fixtures ARE committed** (`fixtures/g_unbound_positive.sh`, `g_unbound_negative.sh`) and both are driven |
| **B5** | `a1wr_cmd.sh:65-66` swallowed-rc defect is **REPORTED, NOT REPAIRED** | every future unit of this family that inherits that file by md5 mis-certifying a truncated run as complete | accepted, and it is **not this item's to repair**: `a1wr_cmd.sh` is another item's FROZEN instrument and editing it would break two freezes (`CLAUDE.md` rule 6). **This item does not consume it** — `a1wrt2_run_arm.sh` propagates the producer's own rc at `:694` / `:713` instead of recomputing it from markers, which is the defect refused by construction |
| **B6** | `A1ZE`'s `empty` arms being unreachable inside DAFoam is **reported to the supervisor**, not acted on | that item's central gate cannot be satisfied as registered | accepted; **it is another team's item and another supervisor's compute** |

---

#### 11.3.4 ⚠ TWO ARITHMETIC DEFECTS IN §5, REPORTED AND **NOT REPAIRED BY THIS LANE** — THEY ARE THE §3 CHECK 4 READING

**A cap is a registered figure. A lane that quietly corrects one has moved a gate.** Both are stated
as arithmetic so the supervisor can read them as arithmetic.

1. **`SEAM`'s in-container deadline CANNOT ENFORCE its cap.** §5.4 registers `SEAM` cap
   **10.0 core-min** and in-container deadline **900 s**. At the registered `ranks = 1`,
   **900 s × 1 ÷ 60 = 15.0 core-min**, which is **1.50× the cap**. **The deadline sits ABOVE the
   cap, so the mechanism §5.4 relies on — *"the deadline lives INSIDE the container, so the cap
   stops the run even if the driver, the daemon and every agent die"* — does not hold for `SEAM`.**
   The figure that would make it hold is **600 s**. **`TAIL` is CONSISTENT and is shown for
   contrast: 40,500 s × 1 ÷ 60 = 675.0 core-min = its cap exactly.**
   *This is the `SO3aF2` cap-watch shape §12 already recorded — "a cap that is advisory, inert and
   off by construction" — appearing in this item's own table.*
2. **The pessimistic bracket end does not equal its own stated expression.** §5.2 prints
   **≈ 367.2 core-min** for `6 × 4,000 × 0.814982 / 60 + 38.48 + 3.13`. Evaluated:
   **24,000 × 0.814982 = 19,559.568 s; ÷ 60 = 325.9928; + 38.48 = 364.4728; + 3.13 = 367.6028.**
   **The stated expression evaluates to 367.60, not 367.2 — a 0.40 core-min discrepancy.**
   **The cap claim SURVIVES at both values** and is shown so the supervisor need not re-derive it:
   **675.0 ÷ 367.60 = 1.8362** and **675.0 ÷ 367.20 = 1.8382**, both **1.84** at the registered two
   decimal places. **The defect is in the printed bracket end, not in the cap.**

**THE §5 CAP ARITHMETIC, LAID OUT IN FULL FOR THE §3 CHECK 4 READING** (every term from §5.2/§5.4,
recomputed here from the anchors; **A-CONT = 0.46178 s/it, A-COLD = 0.814982 s/it, ranks = 1**):

| line | expression | value |
|---|---|---|
| `SEAM` solve | 200 × 0.46178 ÷ 60 | **1.53927** core-min |
| `SEAM` container start + import | 93.85 ÷ 60 | **1.56417** |
| **`SEAM` estimate** | 1.53927 + 1.56417 | **3.10344** (doc prints 3.10) |
| `SEAM` cap | 3.10344 × 3.2 = 9.931 → registered | **10.0** |
| `SEAM` cap ÷ estimate | 10.0 ÷ 3.10344 | **3.222×** (doc claims 3.2×) ✓ |
| `SEAM` deadline as core-min | 900 × 1 ÷ 60 | **15.0 — ABOVE the 10.0 cap ✗ (defect 1)** |
| `TAIL` solve | 6 × 4,000 × 0.46178 ÷ 60 | **184.712** |
| `TAIL` container start + import | 93.85 ÷ 60 | **1.56417** |
| `TAIL` stiffening (EXTRAPOLATED) | 5 × 4,000 × 0.46178 × 0.25 ÷ 60 | **38.4817** |
| **`TAIL` estimate** | 184.712 + 1.56417 + 38.4817 | **224.758** (doc prints 224.75) |
| `TAIL` cap ÷ estimate | 675.0 ÷ 224.758 | **3.003×** (doc claims 3.0×) ✓ |
| `TAIL` deadline as core-min | 40,500 × 1 ÷ 60 | **675.0 = the cap exactly ✓** |
| **ITEM estimate** | 3.10344 + 224.758 | **227.861** (doc prints 227.85) |
| **ITEM CEILING** | 10.0 + 675.0 | **685.0 ✓** |
| pessimistic bracket end | 325.9928 + 38.48 + 3.13 | **367.603 (doc prints 367.2) ✗ (defect 2)** |
| `TAIL` cap ÷ bracket end | 675.0 ÷ 367.603 | **1.836× → 1.84 ✓ (the claim survives)** |
| dollars, point | 227.861 ÷ 60 × $0.0513 | **$0.19482 — DERIVED, not measured; `cost_basis` REPORTED-BY-OWNER** |
| dollars, bracket end | 367.603 ÷ 60 × $0.0513 | **$0.31430 — DERIVED (doc prints $0.31396, consistent with its 367.2)** |

**Every figure above is under the `$25` pre-authorisation and is still costed here, because a
blanket is not a per-item reading (`CLAUDE.md` rule 9).**

---

#### 11.3.5 WHAT THIS INVOCATION DROVE, AND WHAT IT DID NOT

**Driven on host python, zero compute, zero containers started, `__pycache__` cleared first:**

| instrument | rc | legs | controls | EXERCISED-FAIL | EXERCISED-PASS | NOT EXERCISED |
|---|---|---|---|---|---|---|
| `a1wrt2_instruments.py` (no args: existence, coverage, producer trace) | **0** | — | — | — | — | — |
| `a1wrt2_instruments.py --selftest` | **0** | 7 | **17** | 10 | 7 | **0** |
| `a1wrt2_grade.py --selftest` (and under `python3 -O`) | **0** | 7 | **77** | 48 | 29 | **0** |
| `a1wrt2_stage.py --selftest` | **0** | 5 | **26** | 16 | 10 | **0** |
| `a1wrt2_run_arm.sh --selftest` | **0** | — | 21 | 20 driven | — | **1 declared** (`producer/image-pins-measured`) |

`ast.Assert` = **0** across the three python instruments, audited by each file's own control shown
able to see a planted one. The producer trace reads **9 gate inputs consumed, 8 traced, 1 covered by
a NAMED registered deferral, 0 UNTRACED** — **§11.1's `MANIFEST.json` defect is CLOSED**, and the
five artefacts that were fixture-only in §11.2.3's first measurement now resolve to
`a1wrt2_run_arm.sh` on the graded path.

**NOT ESTABLISHED, AND NOT CLAIMED — the §11.2.5 list, carried forward and one item retired:**
1. **`measure_image_pins`'s `libidwarp` limb has never run.** Its **digest limb HAS now**, at zero
   compute, and matches the pin exactly. *(Partly retired.)*
2. **Whether this producer honours `startFrom latestTime` at all.** §11.3.2: **zero of fourteen
   measured points used it.** *(Sharpened from "unverified" to "never once exercised".)*
3. **The per-point time bookkeeping across a six-point CONTINUED sweep** is now **measured on
   thirteen points of a different arm** and is still **not gated**, for the §11.2.2 reason.
4. **Nothing about the physics. No solver ran. `LAUNCH_ENABLED` is still 0.**

**NOT FROZEN. NOT PINNED. NOT ENQUEUED. NOT LAUNCHED. ZERO COMPUTE SPENT — no container was started
by this invocation and `docker image inspect` starts none.
SUBMISSIONS PARKED — nothing here is filed, sent, uploaded, posted or registered anywhere.**

### 11.4 AMENDMENT — 2026-09-05, the `dafoam-supervisor`'s RULINGS IMPLEMENTED. **DESIGN L IS BUILT; DRIVING `measure_image_pins` FOR THE FIRST TIME FOUND TWO DEFECTS THAT WOULD HAVE STOPPED THE SOLVER DEAD; AND §11.3.4's DEFECT 1 IS RETRACTED — THIS LANE HAD THE CAP RULE BACKWARDS.**

**Lawful because this document is UNFROZEN and no compute has been spent against its gates**
(`CLAUDE.md` rule 2 limb 1). **The condition, CHECKED BY EXECUTION in this amending invocation:**
`/home/ubuntu/certonomous-runs/A1WRT2` **does not exist** — `ls -d` and `ls -la` both rc=2, timestamp
printed to that invocation's own output. **`CLAUDE.md` rule 6: lines whose number changed above this
section: 0** — appended at the foot, prior sections struck by quote only.

---

#### 11.4.1 ⚠ RETRACTION. **§11.3.4's DEFECT 1 IS WRONG. THE CAP RULE RUNS THE OTHER WAY, AND THE EDIT IT PROMPTED HAS BEEN REVERTED.**

**§11.3.4 defect 1 claimed, and it is struck by quote:**

> ~~`SEAM`'s in-container deadline CANNOT ENFORCE its cap. … **900 s × 1 ÷ 60 = 15.0 core-min**, which
> is **1.50× the cap**. **The deadline sits ABOVE the cap, so the mechanism §5.4 relies on … does not
> hold for `SEAM`.** The figure that would make it hold is **600 s**.~~

**THE ARITHMETIC IN THAT SENTENCE IS CORRECT AND THE CONCLUSION IS INVERTED.** The lab's registered
rule, quoted from the instrument the supervisor ordered ported — `w3s_stage_record.py:630` — is:

> **`cap x 60 / ranks < wall_bound`, for every leg**

**A cap must bind BEFORE its timeout.** A cap whose wall-equivalent is at or above its own deadline
is the **DEAD LEVER**: the timeout kills first, always, so the cap is a registered number no
execution path can reach. A cap *below* its deadline — `SEAM`'s 600 s against 900 s — is **healthy**,
with **50.0 % headroom**: the cap stops the run, the deadline is the backstop for when the driver,
the daemon and every agent are dead. **§5.4's own sentence is therefore true as written and this lane
misread it.**

**THE EDIT IS REVERTED.** `a1wrt2_run_arm.sh`'s `SEAM` arm is back to `timeout 900`. Driven: had the
600 s edit stood, **`SEAM` itself would have become the dead lever** (cap_wall 600 s against a 600 s
deadline; `<` is strict, so equality is not reachable). **The repair would have created the defect it
was written to fix.**

> **⚠ AND THE SUPERVISOR RULED ON MY WRONG READING.** The 2026-09-05 ruling adopted *"SEAM's deadline
> 900 s → 600 s"* **on the strength of this lane's report.** That ruling is **VOID for the reason it
> was given**, and it is recorded here rather than quietly not executed. **A check beat an argument,
> which is exactly why the same ruling ordered the check.**

**THE REAL DEAD LEVER IS `TAIL`, AND IT BLOCKS THE FREEZE.** Driven, `a1wrt2_instruments.py` with no
arguments now returns **rc = 64**:

| leg | cap | ranks | cap as wall s | in-container deadline | verdict | headroom |
|---|---|---|---|---|---|---|
| `SEAM` | 10.0 core-min | 1 | **600.0 s** | **900 s** | **REACHABLE** | **50.0 %** |
| `TAIL` | 675.0 core-min | 1 | **40,500.0 s** | **40,500 s** | **DEAD LEVER** | **0.0 %** |

caps sum **685.000** = registered ceiling **685.000** ✓.

**`TAIL`'s cap is EXACTLY its deadline, so the cap can never be the thing that stops the arm.** Moving
either figure is a registered change and is **the supervisor's, not this lane's** — this lane has
already been wrong once today about which way this rule points, and says so rather than editing a
second cap on a second reading. **`SEAM` is REACHABLE and can freeze; `TAIL` cannot until that figure
moves.** *§11.3.4's defect 2 — the bracket end evaluating to 367.603 and not 367.2 — is unaffected
and stands.*

---

#### 11.4.2 ⚠ DRIVING `measure_image_pins` FOR THE FIRST TIME FOUND **TWO** DEFECTS, AND THE SECOND WOULD HAVE MEANT NO SOLVER EVER STARTED

**The supervisor authorised the measurement rather than the redefinition — *"spend the ~20 s `docker
run md5sum`"*. It cost 2 wall s × 1 rank = 0.033 core-min and it stopped the freeze twice.**

**DEFECT 1 — THE PIN READER RETURNED A HASH IT HAD NOT READ.** The 2026-09-04 function ran
`--entrypoint /bin/sh … 'md5sum $(python -c "…")'`. In this image **`python` is not on PATH until
`loadDAFoam.sh` is sourced**, and `--entrypoint /bin/sh -c` sources nothing. So the substitution
produced the empty string, `md5sum` was handed **no operand**, fell back to **stdin**, read EOF, and
printed

> **`d41d8cd98f00b204e9800998ecf8427e` — the md5 of the EMPTY STRING — at rc 0.**

**`[ -n "$warp" ]` cannot see that.** The value is non-empty, so the `UNMEASURED` limb never fired,
the manifest would have recorded the md5 of nothing **as a measurement**, and `G-IMG` would have
refused reporting an **image mismatch over an image that is provably correct**. **That is `CLAUDE.md`
rule 3 wearing a hash: not a zero from a blind reader, but a CONSTANT from a reader that read
nothing.** The pins were never in doubt — **both are now MEASURED out of the image and both match**:
`sha256:2927768a16ac…` = `PIN_IMG_DIGEST`, `85f59e87253e0a71a813f64ca6e4c425` = `PIN_IDWARP_MD5`.

**DEFECT 2, AND IT IS THE LARGER ONE — THE ARM BODIES WOULD NEVER HAVE STARTED THE SOLVER.** The
2026-09-04 arm bodies ran `"$IMG" /bin/bash -lc 'cd /mnt && python /run_root/runScript.py -task
sweep'` **with no loader sourced — the same shape that had just been measured returning `python:
command not found`.** Measured on this box: `/bin/sh -c` and `/bin/bash -lc` **both** report
`command not found`; with `source /home/dafoamuser/dafoam/loadDAFoam.sh` prepended, python resolves
and the in-process md5 returns the pin exactly. **`A1WRT` U1 ran because `a1wrt_run_unit.sh:675`
sources the loader. This successor dropped that line.** Both arms would have written an empty
`sweep.log`, propagated a non-zero rc, and produced **no point at all** — *zero of seven again, for a
missing line nobody would have read.*

**THE REPAIRS, EACH DRIVEN:**

| repair | control | measured |
|---|---|---|
| `bash -lc` + the loader, in-process `hashlib`, never `md5sum` over a possibly-empty word | `producer/image-pins-measured` | **EXERCISED-PASS** — both pins read out of the image, both match |
| the empty-input md5 is **refused by name**, and so is anything not 32 hex chars | `producer/md5-of-nothing-is-UNMEASURED` | **EXERCISED-FAIL** — nothing → `UNMEASURED`, while the real pin passes through unchanged. **Both limbs, so it is a classifier and not a guard that refuses everything** |
| the pin refusal moves **BEFORE the container** (`refuse_unmeasured_pins`, exit 4) | `pins/unmeasured-refuses-before-container`, `pins/unmeasured-warp-refuses-before-container`, `pins/measured-pins-permit` | **rc=4, rc=4, rc=0.** A reader defect now costs **0 core-min** instead of an arm's cap |
| every container invocation sources the loader | `loader/every-container-sources-the-loader` | **EXERCISED-PASS — exactly 3**, and the control **excludes its own grep line**, because a control that counts itself has a free pass built in |

> **THE CLASSIFIER AND THE GUARD ARE DRIVEN THROUGH THIS FILE'S OWN CODE**, via two selftest CLI
> entries, **not through a copy pasted into the selftest.** A classifier re-typed inside a selftest is
> a second implementation, and the two agree right up until the moment the first one is wrong — which
> is precisely how `measure_image_pins` sat undriven and broken for a day.

---

#### 11.4.3 DESIGN L, BUILT: THE CONTINUATION `controlDict` IS A COMMITTED, md5-PINNED FIXTURE

**Ruled by the supervisor 2026-09-05, adopting this lane's own framing: *"Design L costs 10 core-min
to find out; Design S costs a HARD gate's re-registration to avoid finding out."***

**Two static fixtures are committed and pinned**, and `a1wrt2_stage.py` gains clause **(8b)**, which
stages the fixture by name **before** clause (9):

| arm | fixture | md5 | start condition |
|---|---|---|---|
| `SEAM` | `fixtures/controlDict_SEAM_continued` | `ddcedcff52df02e9aa8d64ffd504ebdf` | `startFrom latestTime; startTime 4000; endTime 4200` — §3's registered 200 iterations |
| `TAIL` | `fixtures/controlDict_TAIL_continued` | `b81adcc9d4062fa8b121bff0baab22fc` | `startFrom latestTime; startTime 4200; endTime 8200` |

**CLAUSE (9)'s STANCE IS UNCHANGED AND UNWEAKENED.** The stager still does **not author** a start
condition; it stages a **reviewable, committed, md5-pinned artefact** and asserts over the staged
bytes exactly as before. Clause (9)'s stated reason — that a silently authored start condition would
be *"a registered gate where no reviewer would look for it"* — is **satisfied by putting the bytes
where a reviewer does look: in the freeze commit.**

> **⚠ CLAUSE (9)'s CONTROL CHANGED MEANING, AND THE CHANGE IS RECORDED RATHER THAN ABSORBED.** Until
> (8b) existed, `abort/controldict-not-continued` planted a **non-continued SOURCE** — and it stopped
> firing, because a non-continued source can no longer reach clause (9). **That is the repair working,
> not the control failing:** §11.3.2 measured that the real source IS non-continued, so under the old
> code **every real run took that path and both arms aborted.** The control now drives the failure
> mode that actually remains — **a fixture edited to a non-continued start condition AND re-pinned**,
> which the md5 cannot catch because it agrees by construction. Clause (9) is the only thing between a
> re-pinned fixture and a silent cold start, and it is driven with exactly that. **(8b)'s own two
> refusals — fixture absent, fixture md5 drifted — are driven too.**

**REGISTERED PREDICTION `P-SEAMTIME`, written before the answer exists.** `startFrom latestTime` is
**registered and untested**: across the 14 measured points of this producer the OpenFOAM counter
**reset to 1 every point** and ran to `endTime 4000`, and `latestTime` appears in **none** of them.

> **`P-SEAMTIME`: `SEAM`'s `sweep.log` will carry a first anchored `^Time = ` of 4001 and a last of
> 4200.** *If it carries first `1`, the producer resets the counter on a `latestTime` start too,
> `G-COMPLETE` reports `GATE FAIL` on `SEAM`, `seam_precondition_guard` refuses `TAIL` at rc=7, and
> the item stops at ≤ 10.0 core-min with the mechanism MEASURED FOR THE FIRST TIME.* **Either outcome
> is a result. `P-SEAMTIME` is scored `HIT`/`MISS` and a `MISS` is a FINDING, not a failure** — and
> `TAIL`'s 675.0 core-min cannot be spent on a wrong answer to it, because the falsifier sits in
> front of it.

**AND `TAIL`'s FIXTURE IS REGISTERED ON THE HYPOTHESIS `SEAM` TESTS, WHICH COSTS NOTHING.** If
`P-SEAMTIME` misses, `TAIL` is never staged and that fixture is never used. Registering it now is how
the decision rule stays **pre-registered** rather than chosen after the answer.

---

#### 11.4.4 CORRECTION TO §3 AND §11.3.2, ON THE SUPERVISOR'S ORDER: **α = 13 IS NOT UNTOUCHED**

§3 says *"Zero of the seven declared tail points ran"* and this lane repeated it. **Measured and
refined:** the seven are **six tail points (α 13…18) plus `SEAM`'s α = 12**. And `A1WR`'s STAGE12
sweep **reached α = 13 and was killed inside it** — `AOA_POINT_BEGIN idx=13`, 26 anchored `^Time = `
lines, **last `Time = 2500` of a registered 4,000**, against 41 lines and `Time = 4000` for each of
idx 0…12. **α = 13 therefore has a PARTIAL residual history on disk and no `AOA_POINT_VALUES` row.**

**It is `NOT A RESULT` and it is not a point.** But *"zero of seven unbought"* would let a successor
believe α = 13 had never been attempted, and **a partial history is evidence about tail stiffness that
a successor should know exists.** Recorded here rather than left to be rediscovered.

---

#### 11.4.5 WHAT IS DRIVEN NOW — ALL FOUR INSTRUMENTS, **0 NOT EXERCISED**

| instrument | rc | legs | controls | EXERCISED-FAIL | EXERCISED-PASS | NOT EXERCISED |
|---|---|---|---|---|---|---|
| `a1wrt2_grade.py --selftest` (`python3` and `-O`) | **0** | 7 | **77** | 48 | 29 | **0** |
| `a1wrt2_instruments.py --selftest` | **0** | **8** | **21** | 13 | 8 | **0** |
| `a1wrt2_stage.py --selftest` | **0** | 5 | **28** | 18 | 10 | **0** |
| `a1wrt2_run_arm.sh --selftest` | **0** | — | **25** | — | — | **0** |

**`NOT EXERCISED` is now ZERO across the whole item** — the freeze condition the supervisor set, met
by measurement rather than by redefinition. `ast.Assert` = **0** across the three python instruments,
each auditor shown able to see a planted one.

**`a1wrt2_instruments.py` with no arguments returns rc = 64**, not 0: existence clean, coverage clean,
producer trace clean (**9 consumed, 8 traced, 1 named deferral, 0 UNTRACED**), and **CAP REACHABILITY
BLOCKED on `TAIL`.** *That is the ordered check refusing the freeze, which is the check working.*

**THE SELFTEST NOW STARTS ONE CONTAINER** — for the pin measurement only, **~2 wall s × 1 rank ≈
0.033 core-min ≈ $0.00003 `DERIVED`**, `cost_basis` **`REPORTED-BY-OWNER`** (the box cannot read its
own billing). **No solver runs.** The 2026-09-04 banner said *"NO container, NO compute"* and that is
**no longer true**; the banner now says what it does.

**STILL NOT ESTABLISHED, AND NOT CLAIMED:**
1. **Whether this producer honours `startFrom latestTime`** — `P-SEAMTIME` is the registered
   prediction and `SEAM` is the 10.0 core-min experiment. **Zero of fourteen measured points used it.**
2. **`TAIL`'s cap is a DEAD LEVER** and the item does not freeze on that leg until a registered figure
   moves. **The supervisor's call, not taken here.**
3. **Nothing about the physics. No solver has run. `LAUNCH_ENABLED` is still 0.**

**NOT FROZEN. NOT PINNED. NOT ENQUEUED. NOT LAUNCHED. NO SOLVER COMPUTE SPENT — one 2-second
container for the image pins, authorised and costed above.
SUBMISSIONS PARKED — nothing here is filed, sent, uploaded, posted or registered anywhere.**

### 11.5 AMENDMENT — 2026-09-05. **`TAIL`'s IN-CONTAINER DEADLINE 40,500 → 41,400 s, RULED. THE DEAD LEVER IS CLOSED AND BOTH LEGS NOW READ REACHABLE.**

**Lawful because this document is UNFROZEN and no compute has been spent against its gates**
(`CLAUDE.md` rule 2 limb 1). **Condition, CHECKED BY EXECUTION in this amending invocation:**
`/home/ubuntu/certonomous-runs/A1WRT2` **does not exist** — `ls -d` and `ls -la` both rc=2, timestamp
printed to that invocation's own output. **Rule 6: lines whose number changed above this section: 0.**

**THE STRUCK FIGURE, quoted verbatim from §5.4's table, `TAIL` row, in-container deadline column:**

> ~~40,500 s~~

**REPLACED BY: 41,400 s** — `cap × 1.02`. **Ruled by the `dafoam-supervisor` 2026-09-05.**

**WHY, AND THE DIRECTION IS STATED RATHER THAN LEFT TO BE QUESTIONED.** At 40,500 s the deadline was
**exactly** the cap's wall-equivalent (675.0 core-min × 60 ÷ 1 rank), so under the lab's registered
rule `cap × 60 / ranks < deadline` — `<` strict — **the cap could never bind first and was a DEAD
LEVER**: a registered number no execution path could reach, with every sentence about "the cap stops
the run" false of it.

> **THIS IS NOT A THRESHOLD WIDENED TOWARD A PASS, AND NO GATE, BAND OR THRESHOLD MOVES.** A deadline
> sitting at the cap is what made the CAP UNENFORCEABLE. Raising the **backstop** so the **registered
> cap** can actually stop the arm **strengthens** enforcement. The cap itself is unchanged at 675.0,
> `SEAM`'s cap and deadline are unchanged at 10.0 / 900 s, and the caps still sum to the registered
> ceiling — an identity this item has now asserted three times.

**LOWERING THE CAP INSTEAD WAS CONSIDERED AND REJECTED, ON THE RECORD:** it would break
`10.0 + 675.0 = 685.0`, the caps-sum-equals-ceiling identity, which the reachability check refuses on
independently.

**DRIVEN, over BOTH legs, after the change:**

| leg | cap | cap as wall s | deadline | verdict | headroom |
|---|---|---|---|---|---|
| `SEAM` | 10.0 core-min | 600.0 s | 900 s | **REACHABLE** | **50.0 %** |
| `TAIL` | 675.0 core-min | 40,500.0 s | **41,400 s** | **REACHABLE** | **2.2 %** |

caps sum **685.000** = registered ceiling **685.000** ✓ — **`a1wrt2_instruments.py` with no arguments
now returns rc = 0.**

> **⚠ ONE NUMBER, TWO CONVENTIONS, AND THE RECORD SHOULD CARRY ONLY ONE.** The ruling quoted `SEAM`'s
> headroom as **+33.3 %**; this instrument reports **50.0 %**. Both describe the same 300 s gap:
> 33.3 % takes it over the **deadline** ((900−600)/900), 50.0 % over the **cap** (900/600 − 1). **This
> item uses `w3s_stage_record.py`'s definition — a fraction of the cap — so that the two items'
> figures are comparable.** `TAIL`'s **2.2 %** is the same convention and agrees with the ruling.
> *Stated because one number under two conventions is how a record acquires a contradiction nobody
> planted.*

**THE OLD STATE IS PINNED, NOT JUST FIXED.** `cap-reach/tail-tie-is-caught` replays the 40,500 s
deadline and requires **rc = 64 with `TAIL` named as the sole dead lever** — so the state this item
was registered in until today cannot return unnoticed. It sits beside
`cap-reach/inverted-edit-is-caught`, which replays **this lane's own reverted 900 → 600 edit** and
requires `SEAM` to be caught. **Both of this session's cap errors are now controls.**

**NOTHING ELSE MOVES.** `PASS` remains unreachable by construction, `P4` remains registered UNHEDGED
and predicted to MISS, `P-SEAMTIME` stands as written, `DAFOAM_CHARTER.md` §6's two-row obligation
still **BINDS**, and the ceiling remains `GATE REACHED`.

### 11.6 THE FREEZE PACKAGE, HANDED TO THE `dafoam-supervisor`. **EVERY `[OWED — GATES THE FREEZE]` ITEM IS CLOSED BY MEASUREMENT. THE FREEZE COMMIT AND ITS RUN-ROOT CHECK ARE THE SUPERVISOR'S.**

**Condition, CHECKED BY EXECUTION in the invocation that wrote this section:**
`/home/ubuntu/certonomous-runs/A1WRT2` **does not exist** — `ls -d` and `ls -la` both rc=2 at
**2026-09-05T21:50:21Z**. **Rule 6: lines whose number changed above this section: 0.**

> **⚠ THIS IS NOT THE FREEZE.** §11 item 4 requires the run root re-checked **ABSENT BY EXECUTION IN
> THE FREEZING SHELL**, and §11 items 5 and 6 are the supervisor's
> `SUPERVISION_CHARTER.md` §3 checks, **not delegable and not performed here.**
> This section is the package, not the act.
>
> *(Repair note, disclosed rather than silently corrected: this line was written
> through an UNQUOTED heredoc and the shell command-substituted the backticked
> filename, deleting it. One occurrence, restored here; every other line of
> §11.6 was compared against its intended text and is intact. The lab's own
> lesson on backticks in shell-authored text is why it was checked at all.)*

#### 11.6.1 ONE MORE EXTRACTION FINDING, FOUND WHILE ASSEMBLING THIS PACKAGE

**The two new `controlDict` fixtures were staged and md5-asserted by the stager while the extraction
table read `15 present, 0 ABSENT` WITHOUT THEM.** They were bound through a dict of *strings*, and
`a1wrt2_instruments.py` resolves only module-level `HERE`/`FIXTURES` joins out of the AST — so a
path assembled from a dict value is **dynamic and never enters the table.**

**That is §11 item 2's stated failure mode, word for word:** *"an md5-agreement control can read 8 of
8 while a dependency the frozen code executes is absent."* **The item would have frozen with two
executed dependencies outside its own instrument table.** Repaired by binding them as
`FIXTURES / "<literal>"` — **the form the extractor reads directly**, the same lesson
`a1wrt2_run_arm.sh`'s MANIFEST producer already carries. Derived count **15 → 17**.

> **AND THE EXTRACTOR THEN CAUGHT THIS LANE A SECOND TIME.** The `fixture-absent` control named
> `FIXTURES / "no_such_controlDict"` as a literal; the table came back **`17 present, 1 ABSENT`,
> rc=5** — correctly, because a literal join under the item directory is indistinguishable from a
> real dependency. **The repair was to stop naming a repo file that must not exist, NOT to teach the
> extractor to ignore one:** *a checker taught to skip a class of path is a checker with a hole shaped
> like that class.*

#### 11.6.2 THE FOUR FREEZE CONDITIONS, EACH WITH THE MEASUREMENT THAT CLOSES IT

| § | condition | closed by | state |
|---|---|---|---|
| 1 | every instrument written, **and a producer for every `PRODUCTS` name or a named deferral** | producer trace: **9 consumed, 8 traced, 1 named deferral, 0 UNTRACED** | **CLOSED** |
| 1a | the producer trace **by extraction**, not by reading | built §11.2.3, 6 controls, planted both ways | **CLOSED** |
| 2 | instrument table **by extraction**, existence asserted **BEFORE** md5 | **17 present, 0 ABSENT**, then md5 — the two sections print separately and in that order | **CLOSED** |
| 3 | every control driven both directions, **`EXERCISED-*` printed**, counts in the banner | **0 NOT EXERCISED across the whole item** (see table below) | **CLOSED** |
| 4 | run root **ABSENT BY EXECUTION IN THE FREEZING SHELL** | checked here at **2026-09-05T21:50:21Z**, rc=2 — **but the freezing shell's check is the supervisor's** | **SUPERVISOR'S** |

#### 11.6.3 THE CONTROL CENSUS AT HAND-OVER

| instrument | rc (`python3` / `-O`) | legs | controls | EXERCISED-FAIL | EXERCISED-PASS | NOT EXERCISED |
|---|---|---|---|---|---|---|
| `a1wrt2_grade.py` | **0 / 0** | 7 | **77** | 48 | 29 | **0** |
| `a1wrt2_instruments.py` | **0 / 0** | **8** | **22** | 13 | 9 | **0** |
| `a1wrt2_stage.py` | **0 / 0** | 5 | **28** | 18 | 10 | **0** |
| `a1wrt2_run_arm.sh` | **0** | — | **26** | — | — | **0** |
| | | | **153 controls** | | | **0** |

`ast.Assert` = **0** in all three python instruments, each audited by its own file's control shown
able to see a planted one. `a1wrt2_instruments.py` **with no arguments returns rc = 0**: existence
clean, coverage clean, producer trace clean, **cap reachability clean on BOTH legs.**

#### 11.6.4 THE md5 MANIFEST AT HAND-OVER — WHAT THE SUPERVISOR IS FREEZING

| instrument | md5 |
|---|---|
| `a1wrt2_grade.py` | `c6c69e42864acb3dfb1dcd525d8e0c86` |
| `a1wrt2_instruments.py` | `0ce49e043efedb88ff95bd87f6a1dfaa` |
| `a1wrt2_run_arm.sh` | `00caacf4f7772be1e85c5fc5f18d96de` |
| `a1wrt2_stage.py` | `82f23baf911aac5938334e23214d2bd0` |
| `fixtures/controlDict_SEAM_continued` | `ddcedcff52df02e9aa8d64ffd504ebdf` |
| `fixtures/controlDict_TAIL_continued` | `b81adcc9d4062fa8b121bff0baab22fc` |
| `a1wr_runScript_incomp.py` (inherited, another item's frozen instrument) | `d48f48c5e2e41e86981acbf6feccb3c4` |

**Image pins, BOTH MEASURED OUT OF THE IMAGE 2026-09-05:** digest
`sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, `libidwarp`
`85f59e87253e0a71a813f64ca6e4c425` — both equal to their registered pins.

#### 11.6.5 §5's ARITHMETIC AT HAND-OVER, FOR THE §3 CHECK 4 READING

| line | expression | value |
|---|---|---|
| `SEAM` estimate | 200 × 0.46178 ÷ 60 + 93.85 ÷ 60 | **3.10344** core-min |
| `SEAM` cap ÷ estimate | 10.0 ÷ 3.10344 | **3.222×** |
| `SEAM` cap as wall / deadline | 600.0 s / **900 s** | **REACHABLE, 50.0 % headroom** |
| `TAIL` estimate | 184.712 + 1.56417 + 38.4817 | **224.758** |
| `TAIL` cap ÷ estimate | 675.0 ÷ 224.758 | **3.003×** |
| `TAIL` cap as wall / deadline | 40,500.0 s / **41,400 s** *(ruled §11.5)* | **REACHABLE, 2.2 % headroom** |
| ITEM estimate | 3.10344 + 224.758 | **227.861** |
| ITEM CEILING | 10.0 + 675.0 | **685.0** = caps sum ✓ |
| pessimistic bracket end | 325.9928 + 38.48 + 3.13 | **367.603** *(§11.3.4 defect 2; doc prints 367.2)* |
| `TAIL` cap ÷ bracket end | 675.0 ÷ 367.603 | **1.836 → 1.84×** ✓ |
| dollars, point | 227.861 ÷ 60 × $0.0513 | **$0.19482 — DERIVED, `cost_basis` REPORTED-BY-OWNER** |
| spent so far on instruments | one 2 s container × 1 rank | **0.033 core-min, $0.00003 DERIVED** |

#### 11.6.6 WHAT REMAINS TRUE AND IS NOT ARGUED AWAY

**`PASS` is unreachable by construction** — no Roache triple exists in this item. **The tail points
will very likely not converge** (`P3`). **No stall angle may be reported** — `G-STALL` refuses at
exit 2. **`P4` stays registered UNHEDGED and predicted to MISS.** **`DAFOAM_CHARTER.md` §6's two-row
obligation BINDS**; this item ships **ONE row, `PATCHED`, labelled as such** and discharges nothing.
**The ceiling is `GATE REACHED`.**

**And the one thing `SEAM` exists to buy is still unbought and still unknown: whether this producer
honours `startFrom latestTime` at all.** `P-SEAMTIME` is registered, the falsifier sits in front of
the only expensive arm, and **10.0 core-min settles it either way.**

**NOT FROZEN. NOT PINNED. NOT ENQUEUED. NOT LAUNCHED. NO SOLVER COMPUTE SPENT.
SUBMISSIONS PARKED — nothing here is filed, sent, uploaded, posted or registered anywhere.**
