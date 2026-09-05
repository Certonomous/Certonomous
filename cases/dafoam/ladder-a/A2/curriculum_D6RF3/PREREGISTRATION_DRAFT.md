# ⚠ DRAFT — NOT A REGISTRATION, NOT FROZEN, NOT ENQUEUED

**Item id (proposed):** `D6RF3` — dafoam curriculum successor to `D6RF2`, on the A2 wing multipoint
problem. **Team:** dafoam. **Drafted:** 2026-09-04 by a `lab-lane` at the dafoam-supervisor's
instruction, to feed the deferred registration decision on `D6RF2`'s `F_mp` arm.

> **THIS FILE IS UNFROZEN AND BINDS NOTHING.** No gate in it is in force. No threshold, cap, band or
> label here has any standing. It is a proposal for the dafoam-supervisor to rule on, amend or
> refuse. **It becomes a registration only if a supervisor freezes it by commit, at which point
> `CLAUDE.md` rule 2 closes its gates and rule 6 forbids editing it.** Until then every number below
> is a draft number.
>
> **This item has burned 0 core-min, started no container, has no run root and IS NOT ENQUEUED.**
> **SUBMISSIONS PARKED** (rule 7). **Nothing here is sent, filed, uploaded, registered, posted or
> commented.**

**Run root (proposed):** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd`.
Asserted **ABSENT BY EXECUTION 2026-09-04** (`[ -e … ] || echo ABSENT` → `ABSENT`), together with
`cases/dafoam/ladder-a/A2/curriculum_D6RF3` itself, which did not exist before this draft was
written. **A freeze must re-assert both by execution at the freeze commit** — rule 2's *"name the run
directory that does not exist"*, checked by running the check.

---

## 0. WHY A SUCCESSOR AND NOT AN AMENDMENT TO `D6RF2`

`D6RF2` has had compute. Its ledger row is on disk:

    ARM=F_mp ROW=PATCHED IMG=dafoam-idwarp-rot:v1 rc=2 wall_s=69 ranks=4 core_min=4.6
    cap_core_min=480.0 container_wall_s=47 cpuset=2,3,4,14 memory=20g
    (…_ARM_F_mp_EXTRACT_REFUSE_20260903T231107Z/ledger.txt)

`VERIFICATION_CHARTER.md` §2d therefore closes `D6RF2`'s gates. The change this item needs — naming a
different producer for `CDᵢ(mp)` — **moves what is measured by a gated quantity**, so it is not an
addendum and it is not a §2d.1 repair. §5 of this draft states, with the measurement behind it, why
the §2d.1 route is refused rather than merely not taken.

This is the lineage's own precedent for an unrunnable registration: `D6`→`D6R`, `A1WR`→`A1WRT`,
`D6RF`→`D6RF2`.

**INHERITED BY CITATION, UNCHANGED, AND NOT RESTATED HERE:** `D6RF` §2's two arms and five FD
components; §2a's staging contract S1–S8 with its no-`rm -rf`, refuse-on-stale-directory rule; §3b
`G-DVL`; §3c `G-FD` and band D; §3g `G-CAPS`/`G9`/`G12`; §4's anchors and the cap form.
`D6RF2` §3's `G-ANCHOR` is inherited in full. **What this item changes is enumerated in §2 and §3 and
nowhere else.**

---

## 1. THE DEFECTS CARRIED FORWARD — **SIX**, each verified against the record, not copied

Every row below was re-derived from the artefact named in it. Four were known; **`D6RF3-DEF-5` is the
most dangerous**, because unlike the others it fails *silently*; **`D6RF3-DEF-6` is newer still and is
recorded at §9b**, found while writing the instruments rather than by inspection of prose.

**RE-VERIFIED INDEPENDENTLY 2026-09-05** by reading `OptView.hst` with **stdlib `sqlite3` + `pickle`
only — not pyOptSparse, not the extractor, not in a container** — so the defect and the instrument
that reports it do not share a reader. Every figure below held exactly: **1,013 rows / 6 named keys /
1,007 iteration records, indices 0–1006, all `isMajor=True`** (so `getValues(major=True)` filters
nothing and `arr[-1,:]` is genuinely row 1006); **863 rows carry `funcs`; 687 of them non-finite
`obj.J`; the trailing 8 (999–1006) all non-finite; the last FINITE major is index 998 at
`J = 0.022238800232340834`** with `CL = 0.39997369 / 0.49993216 / 0.59985632`; **row 1006's `funcs`
are `NaN` throughout**; and the distinct `funcs` names are exactly the six named — **`CD` appears
nowhere.** `d6rf2_grade.py` re-hashed at `32a539780e34fe6d7945b7e301badc0f`, **43,462 bytes, zero
occurrences of `isfinite`/`isnan`/`isinf`, and zero `assert` statements**; `NaN < 0.0`, `NaN <= 1.0e-3`
and `NaN <= cd_ref` all confirmed `False` by execution. §2b's composite identity recomputed:
**residual `9.840833e-12` absolute, `4.425074e-10` relative**; §5's deciding price recomputed at
**`+6.3558538176e-04`**.

### 1a. `D6RF-DEF-2` (inherited, already repaired in `D6RF`) — in-place `F_mp` staging on the optimiser's own output directories

`D6R`'s `d6r_run_arm.sh:310` took the branch `if [ "$ARM" != "F_mp" ]` and set `WORK="$BASE/O_mp"`
(`:341`), running the FD arm **inside** the finished optimiser directory.
`D6RF/PREREGISTRATION.md:142-148` measures the exposure: **77 time directories in each of four
processor directories per point, of which 76 are outputs — 912 output directories across the three
points.** DAFoam's `pyDAFoam.py:1543` `renameSolution` refuses to move a solution onto an existing
directory, which is D4's arm `F2`, `rc=1` at 56 s.

**RE-VERIFIED BY THIS LANE ON DISK 2026-09-04:** `ls O_mp/mp0k/processor0 | grep -cE '^[0-9]+(\.[0-9]+)?$'`
→ **77** for each of `mp04`, `mp05`, `mp06`. 76 outputs × 4 processors × 3 points = **912**. The
figure holds.

**Carried forward:** `D6RF` §2a's staging contract, unchanged. `F_mp` gets its own arm directory in
**this item's own run root**; `D6R`'s preserved root sits at the head of `FORBIDDEN_ROOTS`.

### 1b. `D6RF-DEF-3` (inherited, already repaired in `D6RF`) — `REF_off`'s cap was 3.16× short and its deadline 1.63× short

`D6R` registered `REF_off` at 17.1 core-min predicted, cap **40.0**, in-container deadline **510 s**,
from an anchor written `10.5 × 1.6308` for which `D6RF`'s lane *"could find no source, artefact or
ledger row anywhere"* (`D6RF/PREREGISTRATION.md:170-174`). The measured anchor is the
`findFeasibleDesign` trim in `D6R`'s own `O_mp` log: **833 s × 4 ÷ 60 = 55.53 core-min** against a
40.0 cap — **`REF_off` would have been killed `rc=124` at 510 s, about 61 % through its trim**
(`:176-188`). 55.53/17.1 = 3.247; the 3.16× figure is against the cap-implied rate and is `D6RF`'s
own statement of it; **either way the arm could not have finished.**

**RE-VERIFIED:** `D6RF` §4c's replacement estimate is **60.07 core-min** (55.53 trim + 4.54 closing
primal) with cap **190.0**. Carried forward unchanged.

### 1c. `D6RF-BLOCKING-1` (inherited, already repaired in `D6RF2`) — the sentence explaining the anchor contained the anchor

`d6r_opt_runScript.py` carried `# OpenMDAO setup` **twice** — at `:230`, the real anchor, and at
`:21`, inside the module docstring in the sentence explaining why the anchor exists. Both consumers
refuse on a count other than one (`d6r_fd_endpoint.py:67`, `d6r_ref_off.py:53`), so **both arms were
unrunnable, and so were `D6R`'s** (`D6RF2/PREREGISTRATION.md:39-57`). `split(ANCHOR)[0]` returned
**1,396 characters of a 12,861-character file** against a correct header of **10,275**.

**RE-VERIFIED:** repaired in `D6RF2` by a one-substitution docstring reword;
`d6rf2_opt_runScript.py` md5 `137539e0a99be27f27fdb69e063b2a87`, and `G-ANCHOR`
(`d6rf2_anchor_gate.py`, md5 `e34c0cb62df30e7a1565b896d07a32e6`) passed at the 2026-09-03 fire:
`readers=2`, both at anchor `'# OpenMDAO setup'`, `count=1`, header 10,536 chars, all 6 symbols
present. **Carried forward with the gate, not merely with the fix.**

### 1d. `D6RF3-DEF-4` — the producing optimisation never recorded per-point CD, so `d6r_major_history.json` cannot be written

**MEASURED BY COMPLETE ENUMERATION OF THE REGISTERED SOURCE**, this lane, 2026-09-04, on
`/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp/OptView.hst`, md5
**`70fafa07bdee618fef13039433c01114`** — byte-identical to the copy `D6RF2` staged into `F_mp/`
(same md5, both hashed today).

The file is **SQLite** (`SQLite format 3` magic), a `sqlitedict` written by pyOptSparse 2.10.1. It
holds **1,013 rows**: 6 named keys (`conInfo`, `objInfo`, `varInfo`, `metadata`, `optProb`, `last`)
and **1,007 iteration records**, of which **1,007/1,007 unpickled successfully — none unreadable.**

| structure | contents, verbatim from the file |
|---|---|
| `objInfo` | `['obj.J']` |
| `conInfo` | `['cl04.aero_post.functionals.CL', 'cl05.aero_post.functionals.CL', 'cl06.aero_post.functionals.CL', 'geometry_cl05.thickcon', 'geometry_cl05.volcon']` |
| `varInfo` | `['dvs.patchV_cl04', 'dvs.patchV_cl05', 'dvs.patchV_cl06', 'dvs.shape', 'dvs.twist']` |
| `funcs` field census, all rows | 6 names on 863 rows: the 3 CL, `thickcon`, `volcon`, `obj.J` |
| `funcsSens` field census, all rows | 8 names on 144 rows: the 3 CL, `lecon`, `tecon`, `thickcon`, `volcon`, `obj.J` |

**No `CD` appears in any structure, in any of the 1,007 records.** The cause is structural, not
accidental: `d6r_opt_runScript.py` registers `obj.J` as the objective and the three CL as
constraints, and **CD is an interior model output** (`reports/…/inputs.html` carries the wiring
`obj.CD04/05/06 ← cl0k.aero_post.functionals.CD` with a setup-time placeholder value `[1]`), so the
driver had nothing to record. `d6r_extract_endpoint.py:66-70` therefore refuses, and the refusal on
2026-09-03 was the instrument working.

**⚠ THE REFUSAL NAMES THE WRONG SCENARIO FOR THE VERDICT.** It names `cl04` because the loop is
`for pt in POINTS: for q in ("CL","CD")` and `cl04`/`CD` is simply the first missing pair. The
verdict depends on **`cl05`** (`d6rf2_grade.py:792`). Both are absent so the outcome is unchanged —
**but a successor acting on the refusal message alone would repair the wrong scenario.**

### 1e. ⚠ `D6RF3-DEF-5` — **NEW, AND IT IS WHY `D6RF2`'s REFUSAL WAS A RESCUE.** The grader turns a `NaN` into `GATE FAIL`, and the endpoint row is `NaN`

**MEASURED, in two independent places, by this lane.**

**(i) The data.** Of the 863 history rows carrying `funcs`, **687 have a non-finite `obj.J`** — the
IPOPT exit `Invalid number in NLP function or derivative detected` (`O_mp/opt_IPOPT.txt:822`) is not
a tail event. **The trailing 8 `funcs` rows are all non-finite.** The last row with a finite
objective is index **998**, `J = 0.022238800232340834`, `CL = [0.39997368604703587,
0.49993215629738436, 0.5998563242119757]`. The last row in the file is index **1006**, whose `funcs`
are `NaN` for `obj.J` and all three `CL`.

`d6r_extract_endpoint.py:53-55` and `:71-74` both take `arr[-1, :]` — **row 1006**. So
`hist["CD_cl05"][-1]`, had CD been present, would have been **`NaN`**, and `out["_final_J"]` is
`NaN` today.

**(ii) The code.** `d6rf2_grade.py` (md5 `32a539780e34fe6d7945b7e301badc0f`, re-hashed today, the
pinned grading path) contains **zero occurrences of `isfinite`, `isnan` or any finiteness guard** in
43,462 bytes. `_f` at `:132-141` parses a float and returns it unchecked. Therefore:

* `gate_price` `:792-797`: `price = NaN − cd_f = NaN`. **`NaN < 0.0` is `False`**, so the registered
  *"negative → NOT A RESULT"* limb does **not** fire; **`NaN <= 1.0e-3` is `False`**, so the `PASS`
  limb does not fire; control reaches `else` → **`GATE FAIL`**.
* `gate_off` `:760-771`: `cd_mp <= cd_ref` with `cd_mp = NaN` is **`False`** → **`GATE FAIL` on all
  three off-design points**, and `res["verdict"]` is `GATE FAIL`.

**Four gated rows would have read `GATE FAIL`, every one of them manufactured from a non-number, and
nothing in the item would have said so.** The registration's own §3i ladder requires `NOT A RESULT`
where an input is absent; a `NaN` is an absent input wearing a float's type. **The `CD` absence is
loud and stops the run; this one is silent and produces a verdict.** `D6RF2`'s extractor refusal is
the only reason it did not happen on 2026-09-03.

**Mitigation, measured and recorded so it is not mistaken for a defence:** the design vector at row
1006 differs from row 998's by at most **4.46e-08** (driver-scaled; 106 of 109 components differ,
`shape` max 1.98e-08, `twist` max 4.46e-08, each `patchV` 1 component at ~4.2e-09). So the FD
endpoint is, to that tolerance, the last finite major's design point. **That is measured, not
registered, and it does not repair `NaN` in the objective and CL/CD channels.**

**REPAIRED IN THIS ITEM** by §3f, the finiteness clause, registered **before** compute.

---

## 2. ARMS, AND THE ONE THING THIS ITEM CHANGES: `CDᵢ(mp)` GETS A SOURCE THAT IS MEASURED TO CONTAIN IT

Two arms, one detached chain, `F_mp` then `REF_off`, stopping at the first non-zero rc — and that
stop is a **gradeable** outcome, not a refusal (`D6RF` §3a, inherited).

| arm | kind | task | work dir | ranks | mem | cpuset |
|---|---|---|---|---|---|---|
| `F_mp` | SOLVER | `d6rf3_endpoint_physical.py --age-datum <epoch>` then `mpirun -np 4 python d6rf3_fd_endpoint.py` | `F_mp/` — this item's own staged copy of `D6R`'s `O_mp/`, per `D6RF` §2a | 4 | 20g | `2,3,4,14` |
| `REF_off` | SCRIPT | `d4_endpoint_physical.py --age-datum <epoch>` then `mpirun -np 4 python d6rf3_ref_off.py` | `REF_off/` — a cold copy of `base/` | 4 | 20g | `2,3,4,14` |

Five FD components, named in advance and unchanged: `shape[46]`, `shape[18]`, `shape[0]`,
`twist[0]`, `patchV_cl05[1]`.

### 2a. `CDᵢ(mp)` — REGISTERED SOURCE, and the source is chosen here because it is measured to contain the quantity

> **`CDᵢ(mp)` for `i ∈ {cl04, cl05, cl06}` is the value of `<pt>.aero_post.CD` returned by
> `prob.get_val()` in the `baseline` primal of `d6rf3_fd_endpoint.py`, written to
> `d6rf3_fd_endpoint.json` under `points.<pt>.CD`, at the endpoint design vector reconstructed to
> PHYSICAL units by `d6rf3_endpoint_physical.py`.**
>
> **`d6r_major_history.json` is NOT the source in this item, and the reason is stated: the producing
> optimiser never recorded CD (§1d, complete enumeration). A file that cannot contain the quantity is
> not a source for it.**

**Why this source and not another, and it is chosen BEFORE compute where choosing costs nothing:**

1. **It is already registered code and already runs.** `d6rf2_fd_endpoint.py:114-118` — the file
   `D6RF2` pinned at `0ce81a0b038abe12728b5b062e4420df` — already calls
   `prob.get_val("%s.aero_post.CD" % pt)` for all three points at **every** primal including
   `baseline`, and already emits `{"kind":"primal","tag":"baseline","points":{...}}`. **The CD the
   grader was asking the history for is already measured by the arm's own program.**
2. **Zero marginal core-minutes.** It is inside the `F_mp` estimate of §4; nothing is added.
3. **It is a measurement, not a reconstruction.** It is a converged primal at the endpoint geometry
   on the same mesh, same `np`, same PATCHED digest.

**⚠ WHAT THIS CHANGES ABOUT THE QUANTITY, DISCLOSED HERE AND NOT LEFT TO BE FOUND.** `D6RF` §0a
called `CDᵢ(mp)` *"the LAST ACCEPTED MAJOR of a failed optimisation"*. **The baseline primal is not
that.** It is a fresh evaluation at the endpoint design point. The two agree only to primal
convergence, and this item makes **no claim** that they are the same number. Every row of `G-OFF`
and `G-PRICE` in this item is labelled `CD_mp_source = FD_BASELINE_PRIMAL`, and **no result of this
item may be compared to a `D6R`- or `D6RF`-era `CDᵢ(mp)` without that label travelling with it**
(`DAFOAM_CHARTER.md` §18.6: the tag travels with the number, not in a header).

### 2b. The stdout reconstruction is REGISTERED AS A CROSS-CHECK, REPORTED AND NOT GATED

`D6R`'s `O_mp` stdout log carries per-primal CD. **Measured by this lane:** 977 converged primal
terminations carrying a `CD:`/`CL:` pair; and for the last finite major (row 998) the three values
are recoverable by matching the history's CL to the log's:

| point | log line | CD | CL in log | CL in history row 998 |
|---|---|---|---|---|
| `cl04` | 262185 | 0.01846929883 | 0.399973686 | 0.39997368604703587 |
| `cl05` | 262411 | 0.02176156349 | 0.4999321563 | 0.49993215629738436 |
| `cl06` | 261901 | 0.02696277508 | 0.5998563242 | 0.5998563242119757 |

and the composite identity closes: `0.25·CD04 + 0.50·CD05 + 0.25·CD06 = 0.022238800222500001`
against the history's `J = 0.022238800232340834` — **residual 9.84e-12 absolute, 4.43e-10 relative**,
at the log's 10-significant-figure print precision.

**This is REPORTED beside `G-OFF` and `G-PRICE` and GATES NOTHING**, for three registered reasons:

1. **The series is not reconstructable, only the endpoint.** 977 terminations were recorded against
   the **2,589** point-primals implied by 863 major rows, distributed **760 / 110 / 98** across the
   CL≈0.4 / 0.5 / 0.6 buckets. A per-major CD series does not exist in this log and this item does
   not pretend one does.
2. **The registered instrument said not to.** `d6r_extract_endpoint.py`'s own docstring records that
   the history file was chosen over stdout *because* `OptView.hst` *"is written by rank 0 through
   pyOptSparse's own History object and is immune to the stdout interleave."* This item does not
   reverse that judgement; it demotes the log to a cross-check.
3. **It cannot be the gated source without becoming outcome-selected.** §5 measures why.

**Registered agreement statement, so the cross-check has a meaning fixed in advance:** the row prints
`|CD_baseline − CD_log| / |CD_log|` per point with **no threshold and no verdict**. A disagreement is
a finding to be reported, and the item states in advance that **a disagreement does not move any
gate in this item** — because the gated source is §2a's and was fixed before either number existed.

---

## 3. GATES — registered before compute, every one post-hoc

The grading path is **`d6rf3_grade.py`**, fixed at the freeze commit and **pinned by md5 in §7**. It
verifies at execution that its own bytes on disk equal the committed blob at `HEAD` and **REFUSES**
if they do not. Vocabulary: `PASS` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING`, and no
other word. **`GATE REACHED` is deliberately not registered and the grader does not contain it: this
item runs no optimiser** (`DAFOAM_CHARTER.md` §9).

`G-DVL` (§3b), `G-FD` and band D (§3c), `G-CAPS`/`G9`/`G12` (§3g) and the arm census (§3a) are
**inherited from `D6RF` unchanged**; `G-ANCHOR` from `D6RF2` §3 unchanged. What follows is what
moves.

### 3a. `G-OFF` — three per-point off-design verdicts

For each of `cl04`, `cl05`, `cl06`: `CDᵢ(mp) ≤ CDᵢ(REF_off)` → `PASS`, else `GATE FAIL`. Three
verdicts, **always all three reported**, with `CL` and the trimmed angle of attack beside each.
`CDᵢ(mp)` is **§2a's source**; `CDᵢ(REF_off)` is `d6rf3_ref_off.json`. `D6RF` §0a's caveat — the
producing optimisation exited on a non-finite objective and **no claim of optimality is made
anywhere in this item** — is printed by the instrument beside every row, together with
`CD_mp_source = FD_BASELINE_PRIMAL`.

### 3b. `G-PRICE` — the single-point price at CL 0.5

`CD₀.₅(mp) − CD_f(D4) ∈ [0, 1.0e-3]` → `PASS`; `> 1.0e-3` → `GATE FAIL`; **negative → `NOT A RESULT`
pending triage** (a finding about D4, named in advance). `CD₀.₅(mp)` is **§2a's source at `cl05`**.
`CD_f(D4)` is re-read from
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` (read-only, the single
`^Objective` line, refused if there is not exactly one) and **REFUSED if it differs from the recorded
`2.1125978108239574e-02`**.

**⚠ THE BAND IS `D6RF`'s, UNCHANGED, AND IT IS NOT WIDENED.** `[0, 1.0e-3]` and the negative→`NOT A
RESULT` limb are carried byte-for-byte. Sanaa's standing boundary (2026-09-04 addendum): *"it never
means adjusting the gate until the answer fits."*

### 3c. `R-RED` — REPORTED, NOT GATED

The composite reduction `(J₀ − J_f)/J₀` is printed with the reference band `[15, 40] %` beside it and
gates nothing, for `D6RF` §3f's reason. **In this item it additionally carries §3f's non-finite
disclosure**, because `J_f` from the history is `NaN` (§1e(i)) and the row must say so rather than
print a number derived from one.

### 3d. Cross-check row `X-CDLOG` — REPORTED, NOT GATED

§2b's per-point relative difference between the FD baseline CD and the stdout-recovered CD of the
last finite major, printed with the composite-identity residual beside it. **No threshold. No
verdict. It moves nothing.**

### 3e. THE PLANTED-ZERO CONTROLS (`CLAUDE.md` rule 3) — three, and none is skippable

Each plants `PLANT = 1.234e-03` into a **COPY**, reads it back **from disk through the same reader**,
and **REFUSES (exit 2)** if the reader cannot see it. Each asserts the unperturbed original
**byte-unchanged by md5 before and after** — a control that modifies what it grades is not a control.

* **the FD reader** — planted by key into the first `PLANNED` row's `s_hi` derivative; refuses if
  there is no plantable row at all (L-302).
* **the price reader** — planted by line index into a **copy** of D4's `opt_IPOPT.txt`; **D4's
  preserved artefact is never written to.**
* **NEW — the CD reader**, and this item needs it because the source moved. Planted **by key** into
  a copy of `d6rf3_fd_endpoint.json` at `points.cl05.CD`; the control **REFUSES if the grader's CD
  path returns the unperturbed value**, i.e. if the reader is looking somewhere else. **A CD read
  from a new source is not evidence until a reader has been shown able to see a non-zero in it.**

All three refusals are **DRIVEN against deliberately blind readers** before the freeze, and the
drive output is committed with the freeze.

### 3f. ⚠ THE FINITENESS CLAUSE — `D6RF3-DEF-5`'s repair, registered before compute

> **Every value the grader reads from an artefact and compares against a threshold is checked
> finite at the point of reading. A non-finite value makes its gate `NOT A RESULT` with reason
> `NON_FINITE_INPUT`, naming the artefact, the key and the token as read. It is NEVER `GATE FAIL`
> and never `PASS`.**

This binds `G-OFF` (all three points), `G-PRICE`, `G-FD` (per component and aggregate), `G-DVL` and
`R-RED`. It is **strictly restrictive**: it can only turn a `PASS` or `GATE FAIL` into `NOT A
RESULT`, never the reverse, which is rule 5's own permitted direction.

**A restrictive repair is not self-certifying** (`VERIFICATION_CHARTER.md` §2d.10 line of ruling), so
the clause ships with an executable control: **a mutation harness that writes `NaN`, `+Inf` and
`-Inf` into a copy of each gated input in turn and requires the corresponding gate to return `NOT A
RESULT` with reason `NON_FINITE_INPUT` — and requires the unmutated control to return a verdict that
is not `NOT A RESULT`.** Both directions, or the clause is not established. Driven before the freeze,
count committed with it.

### 3g. THE VERDICT LADDER, in order

A `NOT A RESULT` can only turn a `PASS` or `GATE FAIL` **into** a `NOT A RESULT`, never the reverse.

1. a completion clause failed on an arm that **ran** → `NOT A RESULT`;
2. a registered arm **did not run** → `NOT A RESULT`, arms named — **the item can never be `PASS`
   with an arm unbought**;
3. **any gated input non-finite** (§3f) → `NOT A RESULT`, artefact and key named;
4. `G-DVL` `GATE FAIL` → `NOT A RESULT`;
5. the registered pathologies — `G-FD` ≥ 2 sign flips, `G-PRICE` negative → `NOT A RESULT`;
6. any gate `NOT A RESULT` for want of an input → `NOT A RESULT`;
7. else any gated row `GATE FAIL` → `GATE FAIL`;
8. else → `PASS`.

---

## 4. COST — PER ARM, IN THIS FROZEN DOCUMENT, NOT IN A QUEUE ROW

**This section is in the registration deliberately.** The rule-12 gap found in this family on
2026-09-03 was an estimate that lived only in a queue row; **a queue row is not a pre-registration**,
and rule 12 requires *"every run is costed in its pre-registration."* Forward-only rule for this
family: **the estimate is here or the item does not launch.**

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars are DERIVED, never measured.** The
unit is **core-minutes** (`wall_s × ranks ÷ 60`). **An overrun stops the run; it does not get a new
budget.**

### 4a. Per-arm estimates and caps

Anchors are `D6RF` §4a's, unchanged and re-cited rather than re-derived: **A2** `ACC_mp` 119.933
core-min, **A3** D4 `P2` 36.4, **A4** D4 `F3` 47.267, **A5** the multipoint trim 55.53, **A6** setup
+ one multipoint primal ≤ 68.15 s.

| arm | estimate (core-min) | basis | leg 1 `3.0×` | leg 2 `1.25×(4/3)×` | `max` | **CAP** | deadline `TMO` (s) |
|---|---|---|---|---|---|---|---|
| `F_mp` | **155.70** | A4 × (A2/A3) = 47.267 × 3.2949 = 155.74, registered at 155.70 | 467.1 | 259.5 | 467.1 | **480.0** | **7,110** |
| `REF_off` | **60.07** | A5 + A6 = 55.53 + 4.54 | 180.2 | 100.1 | 180.2 | **190.0** | **2,760** |
| **total** | **215.77** | | | | | **ceiling 670.0** | at `FRAME_ALLOWANCE_S = 90` |

The cap form is the family's ADOPTED `max(3.0 × estimate-at-a-measured-anchor, 1.25 × wall-at-
registered-max-occupancy)` — **a MAX, never a product** (`docs/LAB_STATE.md` block `S-29` §7.4).

### 4a.1 ⚠ THE CAP-versus-DEADLINE REACHABILITY CHECK — RUN, AND IT PASSES ON BOTH ARMS

A cap in **core-minutes** and a deadline in **in-container wall seconds** are two stopping conditions
in two units. If they are not reconciled one of them is decorative — a cap that can never be reached
means a cap breach can never be the recorded stopping condition, and the ledger records the wrong
reason for every stop. **This defect has been found twice in this lab (`W3S`, and inside `A1WRT2`'s
own §5 table), so it is checked here as arithmetic rather than asserted.** It is also **executable**:
`python3 d6rf3_grade.py --cap-arithmetic`, and `cap_reachability()` runs it on **every grading** and
REFUSES if the identity breaks.

Ranks `4`; `FRAME_ALLOWANCE_S = 90`. The registered design is
`cap_core_min × 60 ÷ ranks == TMO + FRAME_ALLOWANCE_S` **exactly** — the deadline bounds the
in-container program, the frame allowance is the container start/stop outside it, and the two
together *are* the cap:

| arm | `cap × 60 ÷ ranks` | `TMO + frame` | residual | max spend at `TMO` = `TMO × ranks ÷ 60` | cap headroom | predicted ≤ cap? |
|---|---|---|---|---|---|---|
| `F_mp` | `480.00 × 60 ÷ 4` = **7 200.0 s** | `7 110 + 90` = **7 200.0 s** | **`+0.0e+00 s`** | `7 110 × 4 ÷ 60` = **474.00 core-min** | **6.00 core-min** | `155.70 ≤ 480.00` **OK** |
| `REF_off` | `190.00 × 60 ÷ 4` = **2 850.0 s** | `2 760 + 90` = **2 850.0 s** | **`+0.0e+00 s`** | `2 760 × 4 ÷ 60` = **184.00 core-min** | **6.00 core-min** | `60.07 ≤ 190.00` **OK** |

**Both residuals are exactly zero and neither stopping condition is decorative.** The 6.00 core-min
of headroom on each arm is not slack — it is precisely the 90 s frame allowance re-expressed
(`90 × 4 ÷ 60 = 6.00`), i.e. the container overhead the cap covers and the in-container deadline does
not. **`D6RF3` does NOT carry the `W3S`/`A1WRT2` defect.** Total predicted **215.77** against ceiling
**670.0** core-min.

**Corroboration for `F_mp`, carried from `D6RF` §4b:** Route B's segment model gives 123.05 core-min
against Route A's 155.74 — **a 26.5 % spread, named rather than smoothed**, with a known direction
(Route B prices all 22 primals at a staged-baseline primal, and the FD primals are at perturbed
geometries that must be re-warped and re-converged, so Route B under-states). **The larger route is
registered.**

**Dollars, DERIVED at $0.0513/core-h, NOT MEASURED:** estimate 215.77 core-min = 3.596 core-h →
**$0.185**; at the 670.0 ceiling = 11.167 core-h → **$0.573**. Both under the $25 pre-authorisation.

### 4b. What `D6RF2` spent, and what it bought

**MEASURED, from `D6RF2`'s own ledger row:** `rc=2 wall_s=69 ranks=4 core_min=4.6
container_wall_s=47 cap_core_min=480.0` — **4.6 core-min, 0.96 % of the cap**, of which the container
itself is `47 × 4 ÷ 60 =` **3.13 core-min**; `delivered_cores_mean=[0.0695 n=3]`, consistent with an
arm that reached no CFD. **Derived: $0.0039.** It bought a measured, registered refusal that
established `D6RF3-DEF-4` and, through it, `D6RF3-DEF-5`. **It is carried as a cost of this lineage
and not written off**; the calibration row is §4c's.

### 4c. Estimate-versus-actual is OWED AT COMPLETION, and it is registered here as an obligation

Rule 12's calibration clause binds this item: at every process completion — each arm graded, the item
closed — the pre-registered estimate above is compared against the actual from the ledger, **stated
in core-minutes**, with dollars derived and **labelled derived-not-measured**; the row states the
ratio `actual/predicted`, attributes the gap (contention / waste / misprediction, **waste named
separately and never absorbed into the ratio**), and lands in **`docs/COST_CALIBRATION.md`** under
that file's append rules and the rule-10 private-index protocol. **A completion report without this
comparison is incomplete.** The family's only measured estimate-versus-actual for a non-optimiser
multipoint arm is `C-220`: **119.933 against 112.40 registered, ratio 1.0670.**

---

## 5. ⚠ WHY THE `§2d.1` REPAIR ROUTE IS REFUSED — and it is refused on a measurement, not on caution

The cheap route is to leave `D6RF2` frozen and repair `d6rf2_grade.py` to read CD from elsewhere
under `VERIFICATION_CHARTER.md` §2d.1. **This draft refuses that route.** The four conditions, tested
one at a time:

| condition | assessment |
|---|---|
| **(1) repairs a DEMONSTRABLE ERROR rather than a preference** | **FAILS for the substitution.** §2d.1 was cut for `K0cS`, where a published wall integral was **wrong by 10–27 %**. Here nothing is wrong; a required **input is absent**. Verification's own `§2p.11` R6 ruling is close to the point: *"A MISSING instrument is neither agreement nor disagreement — the registration does not name the case … condition (2) has no object and §2d stands."* **MET, separately, for `D6RF3-DEF-5`** — a grader that converts `NaN` into `GATE FAIL` is a demonstrable error. |
| **(2) established by an instrument INDEPENDENT OF THE HYPOTHESIS, one that grades nothing** | **MET, and strongly, for the CD recovery.** The composite identity `J = Σ wᵢ·CDᵢ` grades nothing, has no direction, and closed at **4.43e-10 relative** (§2b). That is the `K0cS` heat-balance shape exactly. **NOT MET for `D6RF3-DEF-5`**, which was found by reading the frozen history against the frozen code; no executable independent instrument exists for it yet — §3f builds one. |
| **(3) the record discloses it, names that instrument, and QUANTIFIES WHAT MOVED** | **DISCHARGEABLE BY DISCLOSING AN ABSENCE**, per `§2d.3.3`: graded solves under `D6RF2` = **zero**; the artefacts that do not exist, **asserted absent by execution 2026-09-04** — `d6r_major_history.json`, `d6r_endpoint_dvs.json`, `d6r_fd_endpoint.json`, `d6r_ref_off.json`, `D6RF2_verdict.json`, and the live run root itself. |
| **(4) pre-repair values recorded beside the published ones** | Same absence discharge — there are no published values. |

**AND THEN THE CLOSING SENTENCE DECIDES IT, AGAINST THE ROUTE, ON A NUMBER THIS LANE COMPUTED:**

> *"Nothing a verdict depends on may be repaired on the authority of the verdict it produces."*

The recovered `CD_cl05` of the last finite major is **0.02176156349**. `CD_f(D4)` is
**0.021125978108239574**. Therefore

    price = 0.02176156349 − 0.021125978108239574 = +6.3558538e-04

which lies **inside the registered band `[0, 1.0e-3]` → `PASS`.**

**The repair is visibly outcome-favourable before it is made.** Anyone proposing it can see, from the
artefacts alone and without running anything, that it converts a refusing item into a passing gate.
That is precisely the shape §2d.1's closing sentence forbids, and it does not stop being that shape
because the instrument that found the number is clean. **The instrument is clean; the choice would
not be.**

**In a fresh registration the same number costs nothing**, because the source is named before any of
it exists in this item's run root — which is what rule 2's freeze is for.

---

## 6. TWO ROWS OR IT IS NOT A VERDICT — `DAFOAM_CHARTER.md` §6

> *"Every DAFoam verdict is recorded as two rows — one against the shipped toolchain, one against
> whatever was patched — and a patched row never replaces a shipped row."*

| row | toolchain | state |
|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1`, image digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, patched `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` | **BOUGHT by this item.** `G9` asserts the digest, the `ROW=PATCHED` field and the `.so` md5 on every ledger row and in every log |
| **SHIPPED** | stock IDWarp, no rotation patch | **NOT BOUGHT by this item, and this is stated as a limitation rather than left to be inferred.** The item's honest position is that its verdict is a **PATCHED-row verdict** and is labelled so wherever it appears |

**A version string is not an identity** (§6): all three images report DAFoam 5.0.0 / OpenFOAM v2506
/ PETSc 3.15.5, and the IDWarp patch moves the reverse-mode derivative on the defect's own DOFs by
seven orders of magnitude while the version string still reads `2.6.2`. Every regrade log prints
`IDWARP_IMPORTED_FROM:` as its provenance stamp.

**⚠ RULED 2026-09-05: THE SHIPPED ROW IS *NOT BOUGHT*, AND IS *PRICED ANYWAY* AT `155.70` core-min.**

The item ships **ONE PATCHED ROW, labelled as such everywhere**, and **is not a full §6 verdict about
DAFoam and must not be reported as one.** The price is `F_mp`'s own registered estimate — a second
`F_mp` on stock IDWarp at the same cap — and it is **NOT added to §4's total**, which stays at
**215.77 core-min against a 670.0 ceiling**; §4's arithmetic is unchanged by this ruling.

**Why price a row nobody is buying:** *an unbought row that is priced can be bought by a successor; an
unbought row that is unpriced quietly becomes never.* The figure is carried on the artefact's own face
— `d6rf3_grade.py` emits `two_row_rule.{row_bought, row_not_bought, shipped_row_price_core_min,
is_a_full_charter_section_6_verdict: false}` into every verdict document and prints it beside the
verdict — so the label travels **with the number** and not in a header (`DAFOAM_CHARTER.md` §18.6
refinement 2).

---

## 7. THE FD TABLE, AND THE STEP PROVED TO LIE IN THE PLATEAU — `DAFOAM_CHARTER.md` §2 and §3

> §2: *"No DAFoam gradient enters a record, a report or an optimisation without a finite-difference
> table beside it."* The aggregate statistic is **this lab's vector-relative error
> `‖J_an − J_fd‖ / ‖J_fd‖` as printed**, with per-component flags reported **beside** it, never
> instead of it.

`G-FD` (inherited, `D6RF` §3c) is this item's centre and it is a **full gate**: the FD bright line
does not need an optimum, it needs a valid geometry, a converged primal and an adjoint at the same
point.

* **Per component**, from `d6rf3_fd_endpoint.json`: relative error `|d(s_hi) − J_adj| / |d(s_hi)| ≤
  5.0 %`; **no sign flip** between `d(s_hi)` and `J_adj`; **plateau**
  `|d(s_hi) − d(s_lo)| / |d(s_hi)| ≤ 10.0 %`.
* **Across the planned components**, aggregate vector-relative error **≤ 5.0 %**.
* **`≥ 2` sign flips → `NOT A RESULT`** — the pathology, named in advance.
* A component whose status is not `PLANNED`, or either of whose FD legs did not evaluate, makes the
  gate `NOT A RESULT` **for want of an input, never `GATE FAIL`**.
* **Band D**, `FD_BAND_PCT 5.0 / AGG_BAND_PCT 5.0 / PLATEAU_TOL_PCT 10.0`, inherited by citation from
  `D6R` §3e. The far tighter `1.0e-3 / 2.2e-5` band at
  `docs/dafoam/ADJOINT_VERIFICATION_STANDARD.md:91-92` governs **np-invariance and partition
  comparisons**, and **this item registers no such limb**: both arms run at `np = 4` on one
  decomposition. **If a decomposition or np arm is ever added it carries that band, not this one.**
* **No grid family exists, so no GCI is quoted anywhere in this item** — and under `CLAUDE.md` rule
  5 no Roache verdict is claimed either.

### 7a. ⚠ THE PLATEAU — **RULED, AND THIS DRAFT'S EARLIER RECOMMENDATION WAS WRONG AND IS STRUCK**

**STRUCK, 2026-09-05, not rewritten** (rule 2's originals-are-struck discipline, applied even
pre-freeze): this draft previously offered *"(A) register the two-point check as what it is — a
plateau **indication**, not a proof — and state in the item that **no §3 plateau proof is
claimed**"*, and recommended it. **That recommendation was WRONG and it is withdrawn.**

`DAFOAM_CHARTER.md` **§20** (addendum 2026-09-04) rules the point directly, and rules it *against its
own author*:

> **`VERIFICATION_CHARTER.md:854-855`** — *"1. Confirm the step sits in the well-converged plateau
> with a **two or three point mini-sweep**. Not assumed."*
>
> **RULED … a two-point mini-sweep SATISFIES §3. Eighteen items in class (b) owe no caveat, and
> writing "no plateau proof is claimed" onto their faces would have been A FALSE SELF-DEPRECATION —
> a misstatement in the modest direction, which is still a misstatement.**

§3 of that charter **delegates the definition** to §7 and *"says nothing about N, and it never did"*;
§3's forbidden list draws the line at *"an FD number from A SINGLE STEP"*, and a two-point pair is on
the compliant side of it. **So: the `s_lo`/`s_hi` ladder IS this item's §3 plateau proof. NO CAVEAT IS
OWED AND NONE IS PRINTED**, and `d6rf3_grade.py` deliberately contains no such string.

**WHAT SURVIVES THE WITHDRAWAL, AND IT IS PRINTED PER COMPONENT.** A two-point pair grades at `s_hi`
with its only neighbour **below**, so **the plateau is one-sided by construction and the coarse side
is unmeasured.** That is *strength of evidence*, not compliance — §7 sanctions it. This family has a
**measured instance of the blind side firing**: `curriculum_D19/D15_D16_FD_STEP_TABLE.md:234`, D16
`PATCHED` `CL` `shape[6]`, **14.0978 % coarse-side deviation against 1.1268 % fine-side** — a
component a two-point pair waves through and a three-point sweep catches. The grader therefore prints
per component `plateau_proved_against`, `plateau_graded_at`, `plateau_sidedness =
ONE-SIDED (fine side only; coarse unmeasured)` and the D16 instance.

**A third, COARSER point is the cheapest evidence available and is a STRENGTHENING, not a duty
(§20.2). THIS ITEM DECLINES IT AND SAYS SO ON THE ARTEFACT'S FACE. Declining it is not a breach.**

**⚠ AND ONE THING TO CARRY UPWARD, NOT SETTLED HERE.** `DAFOAM_CHARTER.md` §20.3 records an
unrepaired self-inconsistency: §2 of that charter cites six ladder-b FD numbers as its own supporting
data, and **an audit measured that FIVE of the six rest on a SINGLE step** — the thing §3's forbidden
list names first. **That disposition is the dafoam-supervisor's and is untouched by this item.**

---

## 8. THE FALSIFIER — what would show this item wrong

Registered before compute, so it cannot be chosen afterwards:

> **`F1` — the item's own claim about its new source.** If `d6rf3_fd_endpoint.json` is produced and
> its `points.<pt>.CD` values disagree with the `X-CDLOG` stdout reconstruction by more than the
> primal's own repeatability — measured in the same run by the `baseline` vs `baseline_repeat`
> primals, whose `|J − J_repeat|` is already computed as `eta_raw` — then **§2a's premise that the
> baseline primal measures the same physical quantity the log recorded is false**, and this item
> reports that as its finding. It is a **reported** falsifier, not a gate, and it does not move
> `G-OFF` or `G-PRICE`, whose source was fixed before either number existed.
>
> **`F2` — the finiteness clause.** If the §3f mutation harness fails in **either** direction — a
> planted `NaN`/`±Inf` that does **not** produce `NOT A RESULT`, or an unmutated control that
> **does** — the clause is not established and **`D6RF3-DEF-5` is not repaired**; the item then
> reports `NOT A RESULT` for want of a working guard rather than shipping gates it cannot trust.
>
> **`F3` — the arm census.** If both arms run clean and every gate reads, and `G-FD`'s aggregate
> lands **above 5.0 %** or with **≥ 2 sign flips**, that is the FD bright line failing on a
> multipoint composite objective — **a physics finding this item is built to be able to report**,
> and it is reported as `GATE FAIL` or `NOT A RESULT` respectively, never softened.

**This item can end at `GATE FAIL` or `NOT A RESULT` and that is a completion, not a failure of the
process** (Sanaa 2026-09-04: a first `GATE FAIL` is a waypoint; the case is then worked until it
passes its gate, **and the gate is never widened to fit**).

---

## 9. INSTRUMENTS — the table a freeze must fill, and the ONE outstanding deliverable

**Every file this item EXECUTES or IMPORTS is enumerated, existence asserted before any md5**
(`DAFOAM_CHARTER.md` §18.3). At the freeze commit each row below carries an md5 and the grading path
verifies its own frozen set against `git cat-file blob HEAD:` at execution.

**FILLED BY EXTRACTION 2026-09-05, NOT WRITTEN FROM MEMORY.** The extraction walks every `.py`/`.sh`
in the item directory, parses each for local imports and quoted local paths, **asserts EXISTENCE for
every extracted dependency BEFORE taking any md5**, and only then hashes. Its verbatim output is
`d6rf3_instrument_table_extraction.txt` beside this file. `DAFOAM_CHARTER.md` §18.3's own sentence is
why the two passes are separate: *"an md5-agreement control over a subset can read agreement on every
pin it holds while a dependency the frozen code executes is absent."*

| file | role | EXISTS | bytes | md5 | `ast.Assert` |
|---|---|---|---|---|---|
| `d6rf3_grade.py` | **THE GRADING PATH** — `G-OFF`/`G-PRICE` re-pointed to §2a's source, §3f's finiteness clause, `X-CDLOG`, `PRODUCT_WRITER`, `cap_reachability` | **YES** | 80,718 | `90e30dfffbac3e87ad6df02af3c1fa0b` | 0 |
| `d6rf3_cd_plant_control.py` | §3e's third planted-zero control **and the item's ONE `CD` reader**, imported by the grader | **YES** | 17,229 | `2808114c5c7214c9b8630b32b6ae357b` | 0 |
| `d6rf3_finiteness_mutation.py` | §3f's two-direction mutation harness (`F2`); also the grader's `--selftest` | **YES** | 15,259 | `c6b6588e48425dc8ae06c17e34d13004` | 0 |
| `d6rf3_fd_endpoint.py` | the FD instrument; **writes `points.<pt>.CD`**, §2a's registered source | **YES** | 12,937 | `24586c9ab7f733cd2b642775aaf7fbe3` | 0 |
| `d6rf3_extract_endpoint.py` | **NEW — POSITION 1.** DVs and `J` only; the CD block is dropped | **YES** | 6,285 | `7adc049421cce82f021603bbbe93dd1e` | 0 |
| `d6rf3_endpoint_physical.py` | driver-scaled → PHYSICAL repair; **re-pinned to the successor extractor** | **YES** | 12,464 | `750fb6336502ca5f71c954298e995f58` | 0 |
| `d6rf3_endpoint_locus.py` | `G-DVL` | **YES** | 29,286 | `341189ca866f302a7e1bba8eefad3a57` | 0 |
| `d6rf3_ref_off.py` | off-design instrument | **YES** | 4,789 | `4f0e564fc9855f179cb3d0e55d306af6` | 0 |
| `d6rf3_anchor_gate.py` | `G-ANCHOR` | **YES** | 11,067 | `e823689c15c2459097d0441e553f565c` | 0 |
| `d6rf3_units_assert.py` | the units gate | **YES** | 18,270 | `885ce236ed20d4be0337f4382346500a` | 0 |
| `d6rf3_opt_runScript.py` | the repaired producer (`D6RF-BLOCKING-1`) | **YES** | 13,122 | `137539e0a99be27f27fdb69e063b2a87` | 0 |
| `d6rf3_run_arm.sh` | launcher; carries `D6RF3-DEF-6`'s **host-side** repair | **YES** | 58,670 | `58684b91f6aced35f500fc947517a8e4` | — |
| `d6rf3_chain_driver.sh` | chain driver; calls the **common** item-ceiling guard | **YES** | 16,627 | `9d2c22d2f84abbead31657288097eccf` | — |

**Cross-item and generated dependencies, all accounted for by the same extraction:**
`../../../_common/item_ceiling_guard.py` (`1ea97c9245dedbc451d62e1bcfe26eb9`),
`../curriculum_D6R/d6r_aggregate_memory.py` (`709ab0b98ef0302a3a3a318588f9493f`), D4's four
instruments, and `d6rf3_cmd.sh` classified **GENERATED** with its generating line named
(`d6rf3_run_arm.sh:870`). **21 dependencies referenced, 21 accounted for, 0 ABSENT.**

**⚠ THE EXTRACTION WAS WRONG THREE TIMES BEFORE IT WAS RIGHT, AND ITS OWN FILE RECORDS ALL THREE.**
v1 missed `AGGREGATE_READER="$D6R_CASE_DIR/d6r_aggregate_memory.py"` — a reference through a shell
variable the pattern did not admit. v2 reported the runtime-generated `d6rf3_cmd.sh` as `ABSENT`.
v3 **still missed `CEILING_GUARD="$HERE/../../../_common/item_ceiling_guard.py"`**, because the
pattern allowed no path *segments* between the variable and the file — **it was blind to the single
most important dependency added that day, the one that closes the fail-open ceiling guard**, and it
was caught only by asking the finished list whether it contained what had just been added.
**That is `SO2a-DRIVER-DEF-1`'s shape occurring inside the check written against it**, and §18.3's own
sentence is the lesson: *a check can pass, correctly, on the question it asks, while the thing that
mattered is broken.*

`d6rf3_endpoint_locus.py` and `d6rf3_opt_runScript.py` are **BYTE-IDENTICAL to their parents** and
their md5s are deliberately unchanged — the runscript's especially, so `G-ANCHOR`'s single-occurrence
assertion on `# OpenMDAO setup` (`D6RF-BLOCKING-1`'s repair) carries over rather than being
re-established. Every other successor ships a `*_DELTAS_from_*.diff` beside it.

**Cross-item dependencies, asserted present by execution 2026-09-05:**
`curriculum_D4/d4_opt_runScript.py` (`2906d52a5dbed2bacbaeaf85a37d3fe8`),
`curriculum_D6R/d6r_opt_runScript.py` (`93edb4a231e13a7af065368f61a468ef`), and
`/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/O/opt_IPOPT.txt` — **exactly one
`^Objective` line, reading `2.1125978108239574e-02`, identical to `CD_F_D4_RECORDED`.**

### 9a. ⚠ THE EXTRACTOR QUESTION IS RULED AND IMPLEMENTED — POSITION 1

The supervisor ruled **Position 1**: a successor extractor reading **DVs and `J` only**, dropping the
CD block. `d6rf3_extract_endpoint.py` implements it. The measured ground: `_final_CD_*` and
`_final_CL_*` — the only things the dropped block wrote — **are read by nothing**, zero references
across every in-container instrument of this lineage; the per-major `CD_<pt>` series was read only at
`d6rf2_grade.py:760` and `:792`, and §2a re-points both. The design-vector path (`arr[-1,:]` over the
five DV keys) is unchanged, and **CD played no part in constructing it.**

**A COUPLED CONSEQUENCE THE RULING DID NOT NAME, AND IT WOULD HAVE ABORTED THE FIRST FIRE.**
`d6rf2_endpoint_physical.py` does not merely sit beside the extractor — it **invokes** it (C3,
`importlib` on the committed blob) and **pins its md5** at C1. So Position 1 lands in *two* files, not
one. `d6rf3_endpoint_physical.py` re-pins `MD5_EXTRACT` to `7adc049421cce82f021603bbbe93dd1e`. Had it
not, C1 would have refused before the extractor ever ran.

### 9b. ⚠ `D6RF3-DEF-6` — NEW, FOUND WHILE WRITING THESE INSTRUMENTS, AND IT MADE `D6RF2` UNGRADEABLE

`d6rf2_grade.py:94`, `:104`, `:458` and `d6rf2_run_arm.sh:546` all register
**`d6rf2_endpoint_dvs_PHYSICAL.json`**. `d6rf2_endpoint_physical.py:75` — **the only file that writes
it** — still writes `D6RF`'s **`d6rf_endpoint_dvs_PHYSICAL.json`** (no `2`). Verified by grep across
both directories.

Read from the frozen bytes: `gate_g1`'s age guard walks `REGISTERED_PRODUCTS["F_mp"]`, whose first
entry is that name, and **refuses `registered_product_absent` when the producing arm RAN**
(`d6rf2_grade.py:326-329`). **So `D6RF2` would have refused at grading however clean its arms were** —
a second, independent blocker behind `D6RF3-DEF-4`. And no md5 freeze could have seen it: every pinned
file hashed correctly. That is `DAFOAM_CHARTER.md` §18.3's exact failure mode one level down, on
*products* rather than instruments.

**REPAIRED AND GUARDED.** The successor writes `d6rf3_endpoint_dvs_PHYSICAL.json`, and
`d6rf3_grade.py` carries an executable `PRODUCT_WRITER` check that asserts, for every registered
product, that the instrument registered as writing it **names it as a literal** — writer existence
asserted before the read. It refuses rather than grading, because a product-name disagreement makes
every downstream reading meaningless rather than merely failing.

---

## 10. WHAT THIS ITEM MAY NOT CONCLUDE

* **It may not conclude anything about `D6R`.** `D6R` is `NOT A RESULT`, graded by `D6RG`
  (`curriculum_D6RG/D6RG_regrade.json`), and it stays so. This item repairs nothing upstream and
  re-opens nothing.
* **It may not conclude optimality.** The producing optimisation exited on a non-finite objective and
  **687 of its 863 recorded `funcs` rows are non-finite** (§1e). **No claim of optimality is made
  anywhere in this item**, and the caveat is printed by the instrument beside every `G-OFF` and
  `G-PRICE` row.
* **It may not compare its `CDᵢ(mp)` to a `D6R`- or `D6RF`-era one without the source label**
  (§2a).
* **It may not quote a GCI or a Roache order.** No grid family exists.
* **It may not report a two-row DAFoam verdict on one row** (§6).
* **It may not claim a §3 plateau proof from a two-point check** (§7).

---

## 11. STATE OF THIS DRAFT — what is done and what a freeze still owes

**Done, and measured by this lane on 2026-09-04:** the five defects of §1 re-verified against the
artefacts named in each; the complete enumeration of `OptView.hst` behind `D6RF3-DEF-4`; the code and
data behind `D6RF3-DEF-5`; the composite-identity cross-check at 4.43e-10; the §5 assessment of the
four §2d.1 conditions and the price number that decides it; the §4 cost table re-derived from
`D6RF` §4a's anchors; the instrument md5s in §9 re-hashed on disk.

**DISCHARGED 2026-09-05, by a `lab-lane`, with zero solver core-minutes:**

1. ✅ **All three supervisor rulings implemented, not merely recorded.** §9's extractor → **Position 1**
   (`d6rf3_extract_endpoint.py`, plus the coupled re-pin in `d6rf3_endpoint_physical.py` that the
   ruling did not name and that would have aborted the first fire). §7's plateau → the earlier
   recommendation **struck and withdrawn** per `DAFOAM_CHARTER.md` §20; no caveat printed. §6's
   shipped row → **not bought, priced at 155.70 core-min**, on the artefact's face.
2. ✅ **Every instrument written by DERIVATION, with a `*_DELTAS_from_*.diff` beside it**, and driven:
   * §3e's third planted control — `d6rf3_cd_plant_control.py --drive`: **direction 1 EXERCISED-PASS
     at delta `1.234000e-03`; direction 2 REFUSED on all FOUR deliberately blind readers, and the
     drive asserts THE REASON (`PLANT_CD` with `reader_saw_the_plant` false), never merely the `rc`**;
     the `NOT EXERCISED` token itself exercised. `rc=0`.
   * §3f's mutation harness — `d6rf3_finiteness_mutation.py`: **direction 1 `30/30`** (NaN, +Inf, −Inf
     into each of 10 gated inputs, each requiring `NOT A RESULT` **and** `NON_FINITE_INPUT` **and**
     the artefact and key named), **direction 2 `10/10`** (unmutated → a verdict that is not `NOT A
     RESULT`), **`NOT EXERCISED` = 0**. `rc=0`. **`F2` is satisfied: the clause IS established.**
   * `ast.Assert` = **0** across all eleven `.py` files. Drive output: `d6rf3_drive_evidence.txt`.
3. ✅ **§9 filled BY EXTRACTION, existence asserted before any md5** —
   `d6rf3_instrument_table_extraction.txt`; cross-item dependencies asserted present by execution.
4. ✅ **§4's cap/deadline reachability run as arithmetic** (§4a.1): both residuals exactly `0.0 s`.
5. ✅ **Run root re-asserted ABSENT BY EXECUTION 2026-09-05** —
   `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd` → `ABSENT`. **This does not
   discharge item 8 below**, which requires the same assertion *in the freeze commit's own invocation*.

6. ✅ **`P1` and `P2` RULED AND BUILT** (§11a) — the launcher pair, with the fail-open ceiling guard
   replaced by the common one and driven four ways; §3f widened to `G-CAPS`/`G1` and driven
   `45/45` + `15/15`. **Nothing in §11a remains a prediction.**
7. ✅ **The §9 extraction re-run and now complete: 21 dependencies referenced, 21 accounted for,
   0 ABSENT** — including the three occasions the extractor itself was wrong, recorded in its own
   output rather than quietly corrected.

**RESERVED TO THE SUPERVISOR — and this is now the whole list:**

7a. **Read `d6rf3_grade_DELTAS_from_d6rf2.diff` AS A DIFF** (920 changed lines after the P2
   widening), together with `d6rf3_run_arm_DELTAS_from_d6rf2.diff` (188) and
   `d6rf3_chain_driver_DELTAS_from_d6rf2.diff` (140). `SUPERVISION_CHARTER.md` §3 check 1; it may
   not be delegated and a lane's summary is not it.
8. **The freeze commit, in its own invocation**, re-asserting root absence *there*, with a sibling
   name in the same invocation, and the grading path hashed against the committed blob.
   **⚠ THE RENAME IS PART OF THE FREEZE AND IS NOT COSMETIC.** `d6rf3_grade.py`'s `freeze_check`
   list names **`PREREGISTRATION.md`**, and this file is `PREREGISTRATION_DRAFT.md`. If the freeze
   commit does not rename it, `freeze_check` **REFUSES `absent_on_disk` on its first line** and the
   item cannot grade — §18.3's failure mode a third time, on the registration itself. Probed
   2026-09-05 with the other nine paths: **9 of 9 read `disk == committed blob at HEAD`**, and
   `PREREGISTRATION.md` was deliberately excluded from that probe **because it does not yet exist**.
9. **A queue row that cites this document**, never one carrying an estimate this document does not.

---

## 11a. `P1` AND `P2` — RULED 2026-09-05, AND **BUILT**, NOT LEFT AS PREDICTIONS

Both were recorded as predictions and the dafoam-supervisor ruled to build both, before the freeze.
**Both are discharged. Zero solver core-minutes.**

### P1 — the launcher pair, BUILT, with the fail-open ceiling guard REPLACED

`d6rf3_run_arm.sh` (`58684b91f6aced35f500fc947517a8e4`) and `d6rf3_chain_driver.sh`
(`9d2c22d2f84abbead31657288097eccf`), derived from `b45cdcb6be230949c08630639c4749b2` /
`cfe78028b41872e5e2177aa492161e3a`, `bash -n` clean, DELTAS diffs beside them (188 and 140 changed
lines). Every staged-instrument md5 re-pinned to this item's files, existence asserted before each
hash; `MD5_LAUNCHER` re-pinned and the driver's own assertion driven.

**They carry `D6RF3-DEF-6`'s host side**: `d6rf3_run_arm.sh:546` now names
`d6rf3_endpoint_dvs_PHYSICAL.json`, agreeing with the writer and the grader.

**⚠ THE CEILING GUARD IS NOT PORTED AND NOT RE-IMPLEMENTED.** The inherited guard **fails open two
ways**, both measured in `d6rf_chain_driver.sh`: (i) `except IOError: pass` then `print('%.3f' % tot)`,
so an absent or unreadable ledger returns **`0.000`** — indistinguishable from a ledger recording
nothing spent, *a planted zero inside the guard's own input*; and (ii) its regex `\bcore_min=([0-9.]+)`
puts a literal dot in a character class, so `core_min=1.2.3` is captured whole, `float()` raises
uncaught, **`$SPENT` comes back EMPTY**, and `print('%.3f' % ( $SPENT + $ACAP ))` becomes Python's
**unary plus** on the cap — the projection prints a clean `480.000` and **the guard PASSES with the
prior spend silently dropped**.

This item calls `cases/dafoam/_common/item_ceiling_guard.py` (`1ea97c9245dedbc451d62e1bcfe26eb9`),
md5-asserted by the driver before use. **No spend figure is interpolated into any shell arithmetic
context — the guard answers on its EXIT CODE.** Driven four ways:

| condition | rc | what the parent did here |
|---|---|---|
| within ceiling | **0** — proceed | 0 |
| over ceiling (`600.0` spent + `480.0` cap vs `670.0`) | **65** — refused | 65 |
| **ABSENT ledger** | **65** — `UNMEASURED`, refuses | **returned `0.000` and PASSED** |
| **malformed token `core_min=1.2.3`** | **65** — refuses | **`$SPENT` emptied → unary plus → PASSED** |

### P2 — §3f WIDENED to `G-CAPS` and `G1`, and the widening DRIVEN

**Widened before first compute**, with rule 2's condition stated and checked: the run root was
asserted **ABSENT BY EXECUTION** and this item has burned **0 core-min**. **It only ever ADDS
refusals** — a finiteness check can turn a `PASS` or `GATE FAIL` *into* a `NOT A RESULT` and can do
nothing else — so nothing moves toward `PASS`.

`gate_caps` now checks `core_min`, `container_wall_s`, `wall_s` and `frame_allowance_s`; `gate_g1`
checks `core_min` and `wall_s`. **The shape closed is the most damaging form of `D6RF3-DEF-5`:**
`nan <= cap` is False, so a malformed `core_min` set `within_cap` False and produced
**`G-CAPS GATE FAIL`** — *an accusation that an arm breached its budget, manufactured from a
non-number.* A cap breach is a finding about discipline, not about physics.

**One coupled change, and it moves a REASON and never a VERDICT.** A non-finite `core_min` sets
`clauses_all_pass` False, so without a hoist the item would have reported *"completion clause failed
on arm F_mp"* — accusing the **run** of misbehaving because a **bookkeeping field** was unreadable.
That is *bookkeeping never voids physics* inverted into bookkeeping **slandering** physics. The
non-finite scan is therefore **rung 0**, above rung 1. Both rungs return `NOT A RESULT`, so **no row
moves between verdict tokens and nothing that could previously have failed can now pass.**

**Driven, in both directions, exactly like the rest** (`d6rf3_finiteness_mutation.py`, with a fixture
complete enough that `G1` and `G-CAPS` are drivable, mutations injected **as text tokens in the ledger
row** as a malformed launcher would have written them):

* **direction 1: `45 / 45`** — `NaN`, `+Inf`, `-Inf` into each of **15** gated inputs, each requiring
  `NOT A RESULT` **and** `NON_FINITE_INPUT` **and** the artefact and key named; the `G1` cases
  additionally require the composed verdict to reach **rung 0** for that reason.
* **direction 2: `15 / 15`** — every gate, unmutated, returning a verdict that is **not** `NOT A
  RESULT`. *A guard that returns `NOT A RESULT` for everything satisfies direction 1 perfectly and is
  worthless.*
* **`NOT EXERCISED`: `0`.** `F2` satisfied.

### The `PRODUCT_WRITER` check is now THREE-SIDED, and planted both ways

`D6RF3-DEF-6` was a **three-way** disagreement: grader and launcher agreed, only the writer differed.
The check now asserts that **both** the writer **and** the launcher name every registered product, so
the defect cannot reappear by moving which of the three is the odd one out. **All six products, all
three sides agreeing.** And per rule 3 applied to the checker itself — *a check reporting zero
findings must be shown able to report a non-zero* — the defect was **planted back in both
directions**: renaming the product in `d6rf3_endpoint_physical.py` (re-creating `D6RF2`'s actual
defect) and in `d6rf3_run_arm.sh`. **Both REFUSED, with the reason asserted, not merely the `rc`.**
