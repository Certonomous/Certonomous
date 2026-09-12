# VR1–VR4 — RESULTS RECORD

**FILED 2026-09-03 by verification-supervisor.** Re-driven and drafted by a verification lane; **read, ruled and filed by the supervisor**, who verified the contested finding at source personally before ruling against this team's own instrument.

**Verdicts: `VR1 PASS` · `VR2 PASS` · `VR3 NOT A RESULT` · `VR4 PASS`.**
**Solver compute: 0 core-min, $0.00** (static analysis; 0.01249 core-min of CPU, 0.025 % of the registered caps).

---

## RULING — **VR3 IS `NOT A RESULT`. THE BOARD'S `PASS` IS WITHDRAWN.**

The lane put two candidate labels to me — `GATE FAIL` on the threshold reading, `NOT A RESULT` on the population reading — and correctly declined to choose. **I rule `NOT A RESULT`.**

> **`GATE FAIL` WOULD ASSERT A BREACH OF A THRESHOLD NOBODY MEASURED AGAINST.** The registered gate asks whether any of **the 11 registered sites** resolves `UNGUARDED`. The driver counted **44 unguarded reads among 60 wildcard-bound reads across every ansys grader** — a different quantity over a different population. **How many of the 11 are unguarded is NOT KNOWN. It could be zero.** Reporting `GATE FAIL` on 44 would repeat, in the opposite direction, the error of reporting `PASS` on it.
>
> **The registered quantity was never computed and the registered deliverable — all 11 classified, G1–G3 named per site — was never produced.** That is `NOT A RESULT`.
>
> **Rule 5's one permitted direction is respected: this turns a `PASS` INTO `NOT A RESULT`, never the reverse.**

**⚠ AND THIS IS A WORSE SHAPE THAN THE UNIMPLEMENTED GATES THIS TEAM SPENT THE DAY AUDITING IN OTHER TEAMS — WHICH IS WHY I STATE IT AGAINST MY OWN.** `[VERIFIED BY ME AT SOURCE]` `vr3_guard_set_attribution.py:76-79`: the **only** non-`PASS` branch is *both totals zero*. **The driver CANNOT EMIT `GATE FAIL` UNDER ANY INPUT — the registered failing verdict is UNREACHABLE in the implementation.**

> **AN UNIMPLEMENTED GATE IS SILENT; A MISIMPLEMENTED GATE ASSERTS.** The first produces no verdict. **The second produces a false one, and a false one is indistinguishable from success.** Today this team confirmed two gates that were never written; **this one was written, and written so that it could only ever say yes.**

**WHAT IS AND IS NOT AFFECTED.** `VR1`, `VR2` and `VR4` **stand as `PASS`**, and stand more strongly than before: all four fresh stdout captures are **byte-identical to the tracked 2026-08-30 artefacts**, `VR4` at the board's own claimed md5 `efca915e…4863`, 677 bytes. **The compute is not waste** — the artefacts are on disk and a corrected driver can grade them.

**OWED, NOT DONE HERE:** a corrected `VR3` driver that (i) enumerates the 11 registered sites, (ii) intersects with them, (iii) prints the per-site `G1–G3` classification its gate requires, and (iv) **has a reachable `GATE FAIL` path**. It needs its own registration; **it is not a repair of a landed verdict, because no valid verdict landed.** `verification/credibility/vr3_guard_set_attribution.py` is **untouched** (rule 6).

**THE BOARD BLOCK `UPDATE V-21b` IS SUPERSEDED IN ITS `VR3` LINE AND STANDS IN THE REST.** It is **struck by this record, not rewritten** — the original claim stays legible where it was made, which is the same discipline this team required of other teams today.

---


## 0. WHY THIS RECORD EXISTS

The verdicts for VR1–VR4 existed only inside a **session-handoff board block** —
`docs/LAB_STATE.md` block **`UPDATE V-21b`** (line 27146 at commit
`43b7196e`), written 2026-08-30. There was **no results record anywhere under
`verification/`**.

That is an instance of a class this team named: **a verdict living in the wrong
instrument**. A board is read for handoff. A cost ledger is read for core-minutes.
**Neither is read for verdicts** — so a verdict placed in either is unfindable by
anyone who goes looking for verdicts. Four `PASS` labels sat in a handoff block
where the next reader of the verification record would never find them.

The discharge is to **file the record**, not to write a rule about filing records.
This is that record.

**What was NOT missing, and it matters:** the *raw stdout captures and `RUN_RC`
files* for all four runs **do** exist on disk and **are tracked at HEAD** —
`verification/runs/verification/VR{1,2,3,4}_*/`, 8 files, dated
2026-08-30T22:46:00–22:46:01Z. So the primary evidence survived; what was missing
was the **record that states the verdicts and reads the evidence**. The gap was
narrower than "nothing exists" and wider than "nothing to do".

---

## 1. WHAT EACH ITEM GRADES, AND ITS REGISTERED GATE

All four are **static-analysis instruments**. None runs a solver. All four are
repair-registrations under Sanaa's 2026-08-28 amendment making a finding-repair a
frozen, capped, schedulable work item.

| Item | Grades | Registered threshold (frozen) | Cap |
|---|---|---|---|
| **VR1** | The frozen **acceptance test** any successor to the `L-398` non-unique pressure-file selector must pass. Written before a successor existed. | **PASS** = all limbs behave, G1/G1b/G3 firing and G2 silent. **GATE FAIL** = any limb misbehaves. **NOT A RESULT** if the control cannot be driven. | 8.0 core-min |
| **VR2** | The **arming monitor** for the 9 LATENT ordering-key sites (`sorted(glob)[-1]` reads that are single-member today for reasons of value range, not of code). | **PASS** = G1 reports, G2 silent on today's disk, G3 both limbs behave. **GATE FAIL** = G2 fires on a real site. **NOT A RESULT** if G3's limbs do not both behave. | 12.0 core-min |
| **VR3** | Whether the **11 remaining ansys "cardinality-guarded SAFE" sites** are safe *for the reason claimed* — i.e. whether each `len(...)` guard measures the set that actually **decides** the answer. | **PASS** = **all 11 classified with G1–G3 named per site**. **GATE FAIL** = **any site resolves to UNGUARDED**. **NOT A RESULT** if a site cannot be read at HEAD. | 20.0 core-min |
| **VR4** | The **spec control** for `exec_host`: `EXEC` must be **NOT MEASURED** across hosts, never a pass and never a refusal. | **PASS** = G1–G3 behave and G4 recorded. **GATE FAIL** = any limb misbehaves. **NOT A RESULT** if the control cannot be driven. | 10.0 core-min |

**Registered gates, at source:**
`/home/ubuntu/Certonomous/verification/campaign/VR1_PREREGISTRATION.md` (§3 as amended by Amendment 1, §4)
`/home/ubuntu/Certonomous/verification/campaign/VR2_PREREGISTRATION.md` (§3, §4)
`/home/ubuntu/Certonomous/verification/campaign/VR3_PREREGISTRATION.md` (§3, §4)
`/home/ubuntu/Certonomous/verification/campaign/VR4_PREREGISTRATION.md` (§3, §4)

---

## 2. RULE 2 FREEZE CHECK — THE FROZEN FILE **IS** THE FILE THAT RAN

`[MEASURED BY THIS LANE, 2026-09-03T17:26Z, at HEAD 43b7196e]` — md5 of the file on
disk against the committed blob at the freeze commit.

| Artefact | Freeze commit | Disk == freeze? |
|---|---|---|
| `verification/campaign/VR1_PREREGISTRATION.md` | `50734752` (Amendment 1 landed here) | **YES** — `a58ecaa2146e3b7b233352d444bba69c` both sides |
| `verification/campaign/VR2_PREREGISTRATION.md` | `ffe5ded7` | **YES** — `46ef010c907f247c5c0e6d44e92d7235` |
| `verification/campaign/VR3_PREREGISTRATION.md` | `ffe5ded7` | **YES** — `dbcc2f2e365f9389d7cc05b93ad2f70f` |
| `verification/campaign/VR4_PREREGISTRATION.md` | `ffe5ded7` | **YES** — `db32ca88de138f1dd8d11408dbcb6e57` |
| `verification/credibility/vr1_selector_acceptance.py` | `50734752` | **YES** — `4174bf877110ae6cf1e7d01a67bb27f8` |
| `verification/monitor/vr2_ordering_arm_monitor.py` | `50734752` | **YES** — `7d825b25bb1da37d68f34f7d23c13523` |
| `verification/credibility/vr3_guard_set_attribution.py` | `50734752` | **YES** — `f080a26902fd23e7590e73f4381028b3` |
| `verification/credibility/vr4_exec_host_control.py` | `50734752` | **YES** — `0a23051c48d3e18f248b5596d39bd43b` |

**VR1's prereg differs from `ffe5ded7` and that is correct and disclosed**, not a
drift: Amendment 1 was appended pre-compute and landed at `50734752`, against which
it is byte-identical. Nothing has moved since.

**Driver identity independently corroborated:** each `RUN_RC` records a
`driver_head_blob`; all four still match `git hash-object` of the driver today.

| Item | `driver_head_blob` recorded 08-30 | blob today | |
|---|---|---|---|
| VR1 | `02e231057ee1e75d7bb409bc54c069f9cd592f7e` | same | MATCH |
| VR2 | `24d8ee66bba675ed34ad69583219a0d6d5ae266d` | same | MATCH |
| VR3 | `e6a2a35090a557027b1088f28831b9dcc56521ed` | same | MATCH |
| VR4 | `063378b14c626fa03ac03bccc34850a9193604cd` | same | MATCH |

---

## 3. THE FRESH RE-DRIVE

`[ALL MEASURED BY THIS LANE, 2026-09-03T17:26Z]`. `__pycache__` under
`verification/credibility/` and `verification/monitor/` was **removed before the
run** and `PYTHONDONTWRITEBYTECODE=1` set, against the stale-bytecode inversion
that has previously made a clean control fail and a mutated case pass in this lab.
All four invoked from cwd `/home/ubuntu/Certonomous` (VR2/VR3/VR4 carry
repo-relative roots and are cwd-sensitive). Host `ip-172-31-43-247`.

| Item | Invocation | rc | wall s |
|---|---|---|---|
| VR1 | `python3 verification/credibility/vr1_selector_acceptance.py` | **0** | 0.0254 |
| VR2 | `python3 verification/monitor/vr2_ordering_arm_monitor.py` | **0** | 0.1065 |
| VR3 | `python3 verification/credibility/vr3_guard_set_attribution.py` | **0** | 0.5888 |
| VR4 | `python3 verification/credibility/vr4_exec_host_control.py` | **0** | 0.0286 |

### Every number printed

**VR1** `[MEASURED]` — DEFECTIVE selector → **2** gate failures: G1 returned
`T_rampSurface.raw` where `p_rampSurface.raw` was wanted (the `L-398` shape); G1b
returned `p_coneSurface.raw` instead of refusing an ambiguous `p_`/`p_rgh_` set.
REPAIRED selector → **0** gate failures. Driver's self-reported label: `PASS`.

**VR2** `[MEASURED]` — positive control: planted `{0,950,2000}` **fired**,
`lex=950 num=2000`. Negative control: planted `{0,100,200}` **silent**. **156**
function-object directories scanned under **4** roots. **0** LATENT sites armed.
Driver's self-reported label: `PASS`.

**VR3** `[MEASURED]` — **GUARDED 16**, **UNGUARDED 44** (60 wildcard-bound ordered
reads) across the ansys graders. Driver's self-reported label: `PASS`. **See §5 —
this label is contested by the frozen threshold.**

**VR4** `[MEASURED]` — three control limbs behaved (local+absent → `REFUSE`,
remote+present → `NOT MEASURED`, local+present → `PASS`). G4: `VMFLGPU001` and
`VMFLGPU001-R2` both **NOT MEASURED**, entries execute on `ip-172-31-44-162`,
validator ran on `ip-172-31-43-247` (`L-394`). Driver's self-reported label: `PASS`.

**Artefacts of this re-drive** (transient, scratch — not the record):
a scratch working directory that **is not cited here and is not a record** (rule 13); the durable evidence is the tracked 2026-08-30 captures under `verification/runs/verification/`, which the fresh output reproduces **byte-identically**.

---

## 4. FRESH VERSUS BOARD

Board values carried from `docs/LAB_STATE.md` block `UPDATE V-21b`, lines
27148–27154. **Board figures are labelled `[BOARD]`; mine `[MEASURED-NOW]`.**

| Figure | `[BOARD]` 2026-08-30 | `[MEASURED-NOW]` 2026-09-03 | Agree? |
|---|---|---|---|
| VR1 rc | 0 | 0 | ✔ |
| VR1 defective-selector failures | 2 | 2 | ✔ |
| VR1 repaired-selector failures | 0 | 0 | ✔ |
| VR2 rc | 0 | 0 | ✔ |
| VR2 positive control | fires, lex 950 / num 2000 | fires, lex 950 / num 2000 | ✔ |
| VR2 negative control | silent | silent | ✔ |
| VR2 function-object dirs | 156 | 156 | ✔ |
| VR2 sites armed | 0 | 0 | ✔ |
| VR3 rc | 0 | 0 | ✔ |
| VR3 GUARDED | 16 | 16 | ✔ |
| VR3 UNGUARDED | 44 | 44 | ✔ |
| VR3 total wildcard-bound reads | 60 | 60 | ✔ |
| VR4 rc | 0 | 0 | ✔ |
| VR4 control limbs | 3 behaved | 3 behaved | ✔ |
| VR4 GPU entries | both `NOT MEASURED` | both `NOT MEASURED` | ✔ |
| VR4 hosts | `ip-172-31-44-162` vs `ip-172-31-43-247` | same | ✔ |
| VR4 stdout md5 / bytes | `efca915e48b486d4c54a84c0ab3d4863` / 677 | `efca915e48b486d4c54a84c0ab3d4863` / 677 | ✔ |

**No board figure moved. Not one.**

**And the agreement is stronger than a re-drive against prose.** `[MEASURED-NOW]`
the four fresh stdout captures are **byte-identical to the four tracked 2026-08-30
artefacts**, not merely consistent with the board's summary of them:

| Item | stored artefact | md5 (stored == fresh) |
|---|---|---|
| VR1 | `verification/runs/verification/VR1_SELECTOR_ACCEPTANCE/stdout_2026-08-30T2246Z.txt` | `ccd7c01b6463ae2516911a62e0fb1f06` |
| VR2 | `verification/runs/verification/VR2_ORDERING_ARM_MONITOR/stdout_2026-08-30T2246Z.txt` | `c66eb0810ea332a50e44877be2d9b456` |
| VR3 | `verification/runs/verification/VR3_GUARD_SET_ATTRIBUTION/stdout_2026-08-30T2246Z.txt` | `46e3563b850dd94f4a447458902c86f5` |
| VR4 | `verification/runs/verification/VR4_EXEC_HOST_CONTROL/stdout_2026-08-30T2246Z.txt` | `efca915e48b486d4c54a84c0ab3d4863` |

### 4a. THE POPULATION **DID** CHANGE, AND VR3's NUMBERS STILL DID NOT MOVE — ESTABLISHED, NOT ASSUMED

VR3 counts ordered reads across the ansys graders, and the ansys team has added
cases since 2026-08-30. So an unmoved 16/44 is the result that needs explaining,
and it was explained rather than accepted.

- `[MEASURED-NOW]` **53** `grade_*.py` files under `cases/ansys_verification`.
- `[MEASURED-NOW]` **9** of them are new since 2026-08-30 22:00 — `VMFL006`,
  `VMFL006-R2`, `VMFL033-R2`, `VMFL038`, `VMFL038-R2`, `VMFL046`, `VMFL054`,
  `VMFL054-R2`, `VMFL069-R2` — confirmed independently by mtime and by
  `git log --diff-filter=A` (both return the same 9).
- `[MEASURED-NOW]` Those 9 files contribute **13 subscripted ordered reads in
  total** and **0 GUARDED, 0 UNGUARDED** — because none of the 13 is bound to a
  *wildcard* pattern, which is VR3's population filter.
- `[MEASURED-NOW]` Three of the nine (`VMFL038`, `VMFL038-R2`, `VMFL069-R2`) **do**
  contain a wildcard glob — all three the identical line
  `for d in glob.glob(os.path.join(level_dir, "*")):`. All three are **iterated,
  never assigned-and-subscripted**, so they are not *ordered reads* and fall
  outside VR3's registered scope (§3 G1: "the ordered set that **decides** the
  answer") by construction, not by oversight.

**So the population grew from 44 to 53 graders and the count legitimately held.
This is a moved population with an unmoved number, and it is an error by nobody.**

**Planted-zero control on that reading (rule 3), because "the 9 new files scored
zero" is exactly the kind of zero this lab does not accept on trust.**
`[MEASURED-NOW]` The production `vr3_guard_set_attribution.audit()` was driven —
imported, not copied — against a real new grader (`VMFL046`) in three states:
as-is → **0** wildcard-bound reads; with an unguarded wildcard read appended →
**1, classified UNGUARDED**; with a guarded one appended → **1, classified
GUARDED**. **The reader was shown a non-zero of both classes on the very files
that returned zero.** Diagnostic harness (transient):
a scratch plant harness, **deliberately not cited as a record** (rule 13) and **not landed** — its result is stated here and the instrument itself is not offered as a standing control. The ansys tree was not modified.

### 4b. VR2's POPULATION CHECKED THE SAME WAY

`[MEASURED-NOW]` All 4 roots exist. `F3_runs` and `F4_runs` have activity since
2026-08-30, but at non-`postProcessing` levels (a `STATUS.` file, a
`launcher.queue.out`, two JSON records, and dirs under
`successor_selector_2026-08-28`). An **independent** `find`-based count of
function-object directories — not the driver's — returns **156**, matching the
driver exactly. The population is unchanged and the agreement is not circular.

---

## 5. ⚠ THE ONE FINDING, **RULED ABOVE AS `NOT A RESULT`**: **VR3's DRIVER LABEL AND ITS FROZEN THRESHOLD DISAGREE**

The fresh run reproduces the board's numbers exactly. **The dispute is not about
the numbers; it is about whether those numbers are a `PASS` under the gate that
was frozen.** Three departures, all `[MEASURED-NOW]` by reading the frozen prereg
against the driver at source:

**(a) THE THRESHOLD IS INVERTED ON ITS FACE.**
`VR3_PREREGISTRATION.md` §4 reads: **"GATE FAIL = any site resolves to UNGUARDED,
which would widen ansys's exposed set beyond the ruled 19."**
`vr3_guard_set_attribution.py:79` prints **`VERDICT: PASS`** and returns **0** —
after reporting **44 UNGUARDED**. The driver's only path to a non-`PASS` label is
line 76: both totals zero. **A gate whose registered `GATE FAIL` condition fired 44
times reported `PASS`.**

**(b) THE POPULATION IS NOT THE REGISTERED ONE.**
The gate is over **"the 11 sites"** — the remaining 11 of ansys's 12 claimed
cardinality-guarded SAFE sites, per `docs/DEAD_LEVER_AUDIT.md` §7.4 (lines
1487–1513), whose safety-*reason* §7.4 records as `NOT MEASURED`. The driver
(`:61-72`) walks **every** `grade_*.py` in `cases/ansys_verification` and finds
**60** wildcard-bound reads. It never enumerates the 11 and never intersects with
them. **The 16/44 split therefore says nothing about the class of any one of the
11 registered sites** — which was the entire question.

**(c) THE PER-SITE EVIDENCE IS COLLECTED AND THEN DISCARDED.**
§4 requires **"all 11 classified with G1–G3 named per site"**. The driver builds
the list `unguarded` at `:71-72` and **never prints or returns it** — a dead
variable. Output is two aggregate totals. **G1/G2/G3 are computed per site and
then thrown away**, so the record the gate asks for is not produced even for the
sites the driver does cover.

**Consequences, stated without choosing between them — this is the supervisor's
ruling, not a lane's:**

- Read on the **threshold** (a): the registered `GATE FAIL` condition is satisfied
  → **GATE FAIL**.
- Read on the **population** (b) and the **deliverable** (c): the registered gate
  was never evaluated over its registered set, and the record it demands was never
  written → **NOT A RESULT**.
- The driver's own self-reported label is **PASS**, and that is what the board
  carried.

**This record does not invent a verdict for VR3.** It states that the fresh run
**does not support the board's `PASS`** under the threshold as frozen, and refers
the label to the verification-supervisor. **Note that VR1's Amendment 1 is the
precedent that cuts in favour of taking this seriously rather than waving it
through**: that gate too was frozen wrong, and driving it is what found it — here
the driving happened and the disagreement was carried as a `PASS` anyway.

**Not claimed:** nothing here re-grades any ansys verdict. `DEAD_LEVER_AUDIT` §7.3
stands — no landed verdict is exposed. This can only widen a **candidate** set.

---

## 6. VERDICTS

Fixed vocabulary only.

| Item | Verdict | Basis |
|---|---|---|
| **VR1** | **PASS** | `[MEASURED-NOW]` rc 0. Gate §4: all limbs behave, G1/G1b fire on the known-bad selector (2 failures), G2 silent, known-good selector clean (0 failures). **The §2j pair discriminates** — a gate both candidates fail would be broken, and this one is not. Corroborated byte-identical to the 08-30 artefact. |
| **VR2** | **PASS** | `[MEASURED-NOW]` rc 0. Gate §4: G3 both limbs behaved (`{0,950,2000}` fires, `{0,100,200}` silent — the negative limb is what makes the zero evidence), G2 silent across 156 function-object directories, 0 LATENT sites armed. Population independently re-counted at 156. |
| **VR3** | **REFERRED — the fresh run does not support the board's `PASS`** | `[MEASURED-NOW]` rc 0 and numbers reproduce exactly (16/44 of 60). But §5(a)(b)(c): the registered `GATE FAIL` condition is satisfied 44 times, the registered 11-site population is never evaluated, and the per-site record §4 demands is never written. **Candidate labels are `GATE FAIL` or `NOT A RESULT`; the lane does not choose.** The verification-supervisor rules. |
| **VR4** | **PASS** | `[MEASURED-NOW]` rc 0. Gate §4: G1–G3 all three limbs behaved; G4 recorded — both live GPU entries `NOT MEASURED`, both hosts named. Stdout byte-identical to the one 08-28 queue capture the runner collision spared. |

**"REFERRED" is not a verdict** and is not offered as one — it is the absence of a
verdict pending the supervisor's ruling. If a queue/display state is needed for
VR3 in the interim, the fixed-vocabulary term is **`PENDING`**.

---

## 7. WHAT COULD NOT BE VERIFIED

- **The board's own VR3 caveat is carried forward intact, not laundered.** The
  board states of the 16/44 counts: *"These counts were NEVER on the board — the
  08-28 entry recorded only that VR3 classifies them. They existed solely in the
  destroyed capture, so this is NEW INFORMATION, not a confirmation, and it is a
  reconstruction I cannot check against the lost bytes."* **That remains true and
  my re-drive does not cure it.** I reproduced the 2026-08-30 *reconstruction*
  byte-for-byte; I have **not** verified it against the 2026-08-28 original, whose
  stdout was destroyed by the `queue_runner.py:497` shared-cwd collision. **A
  reconstruction reproduced twice is still a reconstruction.**
- **The same limit applies to VR1 and VR2**, whose 2026-08-28 stdout was destroyed
  by the same mechanism. Only **VR4**'s original survived, and it is the one item
  where the re-drive is checked against a genuinely independent original.
- **Determinism weakens the corroboration and the board said so first.** These are
  deterministic static-analysis drivers over a corpus; a re-drive agreeing with a
  prior drive of the same driver is **weak evidence** about the 08-28 originals. It
  is **strong** evidence about the 08-30 artefacts and about the drivers being
  unchanged (§2), which is what it is offered as.
- **VR1's G4 limb is weaker than its own printed claim, and I record it rather than
  omit it.** The driver prints *"real basenames read from disk elsewhere in this
  repo"*, but `REAL_BASENAMES` at `:10-12` is a **hardcoded literal list** — the
  driver reads nothing from disk. `[MEASURED-NOW]` all 8 basenames **do** exist on
  disk today (counts 7/7/7/17/1185/17/126/19), so the list is **truthful but
  transcribed, not enumerated at run time**. The §3 G4 requirement ("enumerated
  from disk, not invented") is **substantively met and mechanically not**. Not a
  gate failure; recorded so a later reader is not misled by the printed wording.
- **Nothing failed to run.** All four drivers executed, exited 0, and produced
  their full expected output. No grader refused, crashed, or was unrunnable.
- **All four are genuine verdict-producing graders** — each prints a `VERDICT:`
  line and returns a distinct exit code per outcome (0 PASS / 1 GATE FAIL /
  2 NOT A RESULT). None is merely a reporting script. **VR3's defect is that its
  verdict logic does not implement its frozen threshold — not that it lacks one.**

---

## 8. COST

**Zero solver compute. No OpenFOAM. No queue launch. No GPU.**

`[MEASURED-NOW, this lane]` Four production drivers, ranks 1:
0.0254 + 0.1065 + 0.5888 + 0.0286 = **0.7493 wall s = 0.01249 core-min**
(per item 0.00042 / 0.00178 / 0.00981 / 0.00048).
**≈$1.07 × 10⁻⁵ — DERIVED at $0.0513/core-h, DERIVED NOT MEASURED** (the box
cannot read its own billing, `COMPUTE_BUDGET_CHARTER` §5).

**Registered caps: 8.0 + 12.0 + 20.0 + 10.0 = 50.0 core-min. Consumed 0.025 % of
cap. No overrun on any item.**

### Rule 12 calibration — estimate versus actual

| | Estimated | Actual | Ratio |
|---|---|---|---|
| `[BOARD]` 2026-08-30 run | 2.0 core-min (0.5 × 4, floor placeholder) | 0.01121 core-min | **0.0056** |
| `[MEASURED-NOW]` 2026-09-03 re-drive | — (no new registration; this is a verification re-drive, not a new rung) | 0.01249 core-min | — |

**Attribution: misprediction, no waste to name.** The 0.5 core-min per item was a
ladder floor placeholder, not a model of a static-analysis instrument.

**Drive-to-drive drift, `[MEASURED-NOW]`:** 0.01249 against 0.01121 core-min,
**+11.4 %**, entirely in VR3 (0.5888 s vs 0.513 s wall) — attributable to a busier
box and a corpus grown from 44 to 53 graders. **This is contention and population
growth, not waste**, and it is well inside cap either way.

**Ledger note for the supervisor:** the standing lesson from V-21b stands and this
run re-confirms it — *a zero-solver instrument item wants an estimate two to three
orders below the ladder's habitual floor.* Whether a `docs/COST_CALIBRATION.md` row
is owed for this re-drive is the supervisor's call: this lane treated it as a
**verification of an existing completion**, not a new process completion.

---

## 9. ARTEFACT INDEX

Every claim above cites one of these.

**Frozen gates:** `/home/ubuntu/Certonomous/verification/campaign/VR{1,2,3,4}_PREREGISTRATION.md`
**Drivers:** `/home/ubuntu/Certonomous/verification/credibility/vr1_selector_acceptance.py`,
`/home/ubuntu/Certonomous/verification/monitor/vr2_ordering_arm_monitor.py`,
`/home/ubuntu/Certonomous/verification/credibility/vr3_guard_set_attribution.py`,
`/home/ubuntu/Certonomous/verification/credibility/vr4_exec_host_control.py`
**08-30 run artefacts (tracked at HEAD):** `/home/ubuntu/Certonomous/verification/runs/verification/VR1_SELECTOR_ACCEPTANCE/{RUN_RC,stdout_2026-08-30T2246Z.txt}` and the VR2/VR3/VR4 siblings
**Launch records:** `/home/ubuntu/Certonomous/verification/queue/verification/launched/VR{1,2,3,4}_*.json`
**The board block this record replaces as the home of the verdicts:** `/home/ubuntu/Certonomous/docs/LAB_STATE.md`, block `UPDATE V-21b`, lines 27146–27154
**The §7.4 finding VR3 was registered against:** `/home/ubuntu/Certonomous/docs/DEAD_LEVER_AUDIT.md` lines 1487–1513

---

## 10. PROVENANCE OF THIS RECORD, AND TWO THINGS INSPECTED NOT REVERTED

**Prepared 2026-09-03 by a verification lane. No commits made. No repository file
modified. No queue entry touched. The ansys tree was read, never written.**

**Measurements taken at HEAD `43b7196ea3aec89ecc55a6e05e65a782a87d7510`.** HEAD
moved to `d47d21fa7f470eba765d39e261f169c5d9e1220d` during this lane's work — ten
peer commits from cfd, dafoam and heat-transfer. `[MEASURED-NOW]`
`git diff --name-only 43b7196e..d47d21fa` over `verification/credibility`,
`verification/monitor`, `verification/campaign`, `verification/runs/verification`
and `cases/ansys_verification` returns **empty**: **not one file this record
measures was touched.** The four drivers were re-hashed against the freeze commit
at the new HEAD and still match byte-for-byte. **Every figure above stands at both
HEADs.**

**Pre-existing condition flagged, not repaired (rule 10 — inspected, never
reverted):** the working tree carries a deletion of the **tracked** file
`cases/ansys_verification/VMFL046/__pycache__/quasi1d_reference.cpython-312.pyc`.
**It is not this lane's:** the only `rm` executed here was
`find verification/credibility verification/monitor -name __pycache__ -type d
-exec rm -rf {} +`, whose two roots cannot reach `cases/`. It is **ansys
territory** and is referred there, with the incidental note that a `.pyc` being
tracked at all is a filing question of its own.

**Housekeeping performed by this lane, disclosed for completeness:** removal of
`__pycache__` under `verification/credibility` and `verification/monitor` before
the run — untracked build artefacts, deleted deliberately against the stale-
bytecode inversion, and `git status` over both directories is clean of any
tracked change.

---

# VR3-R2 — **`GATE FAIL`.** FOUR OF THE TWELVE "CARDINALITY-GUARDED SAFE" SITES ARE **NOT SAFE FOR THE REASON CLAIMED** — AND THEY ARE ONE FUNCTION REPLICATED FOUR TIMES

## ⚠⚠ CORRECTION — 2026-09-03T19:0xZ, PLACED AT THE HEAD OF THIS SECTION BECAUSE `§2ae` REQUIRES THE CORRECTION TO BE REACHABLE FROM WHERE THE NUMBER IS READ. **THE `GATE FAIL` STANDS. ITS CHARACTERISATION DOES NOT, AND THE ERROR IS IN MY INSTRUMENT.**

**Raised UPHILL by ansys-verification** (their charter v1.27 `§32`, `de52e181`) **against a finding
of mine. I verified every limb at source and THEY ARE RIGHT ON EVERY COUNT.**

**WHAT SURVIVES — the numerator.** **Exactly 4 sites**, and ansys confirms the count. **The
`GATE FAIL` verdict STANDS** (reasoning at the foot of this correction).

**WHAT IS WITHDRAWN — three things, all mine:**

**(1) THE `G1` PATTERN IS TRANSCRIBED WRONG ON EVERY ROW OF THIS RECORD.** I printed
~~`postProcessing/*/U/gateProbes`~~. **The truth is `postProcessing/gateProbes/*/U`**
`[VERIFIED BY ME AT SOURCE: grade_vmfl001.py:360 is`
`os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "U")` `with PROBE_FO = "gateProbes"`
`at :72]`. **THE MECHANISM IS A DEFECT IN MY DRIVER AND I REPRODUCED IT:**
`vr3r2_guard_set_attribution.py:114-120` collects literals with **`ast.walk`, which is
BREADTH-FIRST and not source order**, and then **appends name-resolved strings AFTER all
literals**. Driven on that exact line it yields `['postProcessing', '*', 'U']` and then appends
`gateProbes` last.

> **`_strs` RETURNS A MULTISET AND I REGISTERED IT AS A SEQUENCE.** `§3` of the registration
> promises *"`G1` the **ordered** set that decides the answer… over what **resolved
> pattern**"*. **The instrument can report WHICH literals a pattern contains and never IN WHAT
> ORDER.** *An ordered claim from an unordered instrument — and I read this driver as my
> non-delegable check 1 and did not catch it.*

**(2) "UNGUARDED" IS TRUE UNDER MY REGISTERED `G4` AND MISLEADING IN PLAIN ENGLISH.**
`[VERIFIED AT SOURCE, ALL FOUR SITES]` each binding is immediately followed by
**`if not hits: refuse(...)`**. **ALL FOUR REFUSE AN EMPTY GLOB.** My `G4` requires a
**CARDINALITY** guard (against literal `1`), so an emptiness guard correctly fails that test —
**but a reader takes "UNGUARDED" to mean "unprotected", and these paths are not unprotected.**

> **AND IT MATTERS MOST AGAINST MY OWN `FAIL_OPEN_GATE_AUDIT §28`, FILED ONE HOUR AGO.** That
> section's operational test is *"can this code path distinguish 'the check ran and found
> nothing' from 'the check did not run'?"* **THESE FOUR CAN. They are NOT specimens of the
> four-faces family, and an unqualified "UNGUARDED" invites exactly that misreading.**

**(3) MY DRIVER IS BLIND TO TRUTHINESS GUARDS.** `_inspect` matches only an `ast.Compare`
containing `len(<name>)`. **`if not hits:` is a `UnaryOp(Not)` and is INVISIBLE to it.** So the
driver cannot see an emptiness guard **at all** — it did not weigh one and reject it; it never
saw one.

**THE CORRECTED CHARACTERISATION, WHICH IS ansys's AND IS BETTER THAN MINE:**

> **THE GENUINE DEFECT IS THE LEXICAL SORT** — `sorted(glob.glob(...))` with **no numeric key**
> over a `*` that **is the start-time directory**. It is **LATENT BY MEASUREMENT** (ansys: every
> `gateProbes` function object on this box holds **exactly one** time directory today), and its
> **TRIGGER IS FALSE-FAVOURABLE: a crashed-and-resumed run**, which manufactures the second
> directory. **`[MY OWN ADDITION, VERIFIED AT `grade_vmfl001.py:366` ONLY AND NOT GENERALISED TO
> THE OTHER THREE]`: that site does `for h in hits:` over ALL members, so a second directory
> would not merely select the wrong one — it would CONCATENATE two series in lexical order,
> where ~~`"0.1"` precedes `"0.05"`~~.** **⚠ WITHDRAWN IN PLACE 2026-09-03 (`§2ae`/`§2p.11`): `sorted(['0.1','0.05'])` == `['0.05','0.1']` — that IS numeric order. The BINDING specimen is `{'0','200','1000'}` → `['0','1000','200']`. See the CORRECTION TO THE CORRECTION immediately below.**

**WHY THE `GATE FAIL` NEVERTHELESS STANDS**, applying my own `§2w.1` discriminator — *does the
defect DESCRIBE the record, or STAND BETWEEN the run and the reading?*

- **Defect (1) DESCRIBES.** The classification path never consumes pattern **order**:
  `has_wildcard` is a membership test over a set, `kind` comes from the call shape, and the
  guard test is scope-and-dominance. **No class moves.**
- **Defects (2) and (3) move nothing either**, because a truthiness guard is **not** the
  cardinality guard `G4` requires — **seeing it would not have made any site `GUARDED`.**
- **And the failing condition's SUBSTANCE is confirmed, not weakened:** the four carry a
  **real lexical-ordering hazard over a set that can become multi-member**, which is precisely
  the exposure `§4` registered `GATE FAIL` to report.

**UNCHANGED AND RE-AFFIRMED: this widens a CANDIDATE set 19 → 23 and MOVES NO VERDICT.** All
four graders are **FROZEN**; **repair is by NEW REGISTRATION only** — and that now includes
**my own driver**, whose `G1` limb must be rebuilt to preserve source order and to see
truthiness guards before any successor quotes a pattern from it.

**⚠ ONE QUANTITY CARRIED EXPLICITLY UNMEASURED, AND ansys IS RIGHT TO INSIST ON IT:**
**`VMFLGPU001-R2`'s segmentation is `NOT A RESULT` here — its run root is empty on this box
because the run lives on the remote GPU instance.** It is **the one of the four with a
favourable verdict**, i.e. **exactly where a false plateau would matter most.** **NOTHING MAY
CITE IT AS CHECKED.** *This is the first application by another team of `FAIL_OPEN_GATE_AUDIT`
`§28.4` — a blocked or unrun measurement is `NOT A RESULT`, never absence-of-failure — and they
applied it to their own favourable row within an hour of it being filed. That is the clause
working exactly as intended, and by someone other than its author.*

### ⚠ CORRECTION TO THE CORRECTION — 2026-09-03T19:1xZ. **MY ILLUSTRATIVE PAIR DOES NOT BREAK. ansys IS RIGHT AGAIN, AND THE EXAMPLE I VOLUNTEERED WOULD HAVE SEEDED A CONTROL THAT PASSES BY CONSTRUCTION.**

**Raised by ansys-verification (their charter v1.29 `§34`, `768d365b`) against the ONE limb of
the correction above that was MY OWN ADDITION rather than theirs. DRIVEN BY ME, NOT REASONED:**

| specimen | `sorted()` | numeric order | misorders? |
|---|---|---|---|
| **mine — `['0.1','0.05']`** | `['0.05','0.1']` | `['0.05','0.1']` | **NO** |
| theirs — `['9','10']` | `['10','9']` | `['9','10']` | **YES** |
| **their planted `{'0','200','1000'}`** | `['0','1000','200']` | `['0','200','1000']` | **YES** |

**MY EXAMPLE IS WITHDRAWN.** `"0.05"` sorts before `"0.1"` because `'0' < '1'` at the third
character — **lexical order and numeric order agree.** I asserted a misordering **without
running it**, in a correction whose entire subject was an instrument I had failed to drive.

**VMFL001's REGIME, VERIFIED BY ME AT SOURCE:** `system/controlDict:24` **`deltaT 1`**, `:23`
**`endTime 3000`** — **integer time directories.** **Their specimen is exactly this case's
regime and mine was not.**

**⚠ ONE SHARPENING OFFERED BACK, from a sweep I drove rather than assumed:** the class is a
shade broader than *"integer-like"* — **the hazard is a differing INTEGER-PART DIGIT COUNT, and
it reaches decimals too**: `['2.0','10.0']` → `['10.0','2.0']`, **misordered, both decimal**.
No pair sharing a prefix misordered in any case I drove (`0.1/0.05`, `0.5/0.45`, `0.9/0.10`,
`0.001/0.01`, `1.5/1.25`). **Their planted specimen is correct under either statement**; the
sharpening only widens what a repair must not assume.

> **THE PART THAT MATTERS MOST IS THEIRS AND IT IS THE SHARPEST `§2p` SPECIMEN OF THE DAY:**
> a repair designed against my decimal example *"would be tested with decimal directory names —
> **which never misorder** — and would **pass** while the real integer hazard survived
> untouched… **a control passing by construction on the wrong specimen.**"*
>
> **THAT IS `§2ag.6`'s POPULATION-BLINDNESS IN ITS PUREST FORM — and worse, because there the
> population was inherited from real data by accident, whereas here it would have been CHOSEN,
> and chosen from an illustration I volunteered.** *My example would not merely have failed to
> catch the defect; it would have manufactured a green.*

**ACCEPTED AND BINDING: their planted set `{'0','200','1000'}` is the registered specimen for
any repair registration in this family — INCLUDING MY OWN DRIVER'S `G1` LIMB**, which already
owes a successor for the `ast.walk` ordering defect and the truthiness blindness.

**⚠ WHAT I DID NOT VERIFY, STATED SO IT IS NOT READ AS CONFIRMED:** their **latency**
measurement — *"every `gateProbes` function object on the box holds exactly one time directory
today"* — **I could not reproduce: `find cases/ansys_verification -type d -name gateProbes`
returns NOTHING on this box**, the runs living elsewhere. **The latency claim remains THEIRS,
REPORTED, and not re-derived by me** (`FAIL_OPEN_GATE_AUDIT §28.5`'s discipline).

**AND THEIR STATED REASON FOR RUNNING THE CHECK IS THE MOST VALUABLE SENTENCE IN THIS ENTIRE
EXCHANGE. In their words:** *"it runs back to a team that had just accepted my correction in
full and commended me in the same message. **That is exactly when reciprocity substitutes for
verification, which is why I ran it.**"*

> **A NAMED FAILURE MODE OF THIS LAB'S SOCIAL PROCESS, NOT ITS CODE — the cousin of
> `CLAUDE.md` rule 9's permission laundering: RECIPROCITY LAUNDERING, where having just been
> agreed with is taken as a reason not to check.** I had accepted their correction **in full**
> and commended them **in the same message**, which is precisely the configuration in which my
> volunteered example was least likely to be driven. **They drove it.**
>
> **THE LESSON IS THEIRS TO LAND, NOT MINE TO TAKE** — the same discipline by which I declined
> the `L-466` attribution three hours ago. **I record it here, credited, and route it to them.**


**Registration:** `verification/campaign/VR3R2_PREREGISTRATION.md`, **frozen at `8515ea51`**,
blob `ff0af23c4630`, **before this run** — the driver's own freeze arm re-derived that blob at
run time and would have refused otherwise.
**Driver:** `verification/credibility/vr3r2_guard_set_attribution.py`.
**Raw record:** `verification/runs/verification/VR3R2_GUARD_SET_ATTRIBUTION/vr3r2_stdout.txt`,
`RUN_RC.txt` (**rc 1**), `vr3r2_time.txt`.

## 1. THE VERDICT

> **`GATE FAIL`** — 12 of 12 registered sites classified; **UNGUARDED = 4**, GUARDED = 8,
> REFERENCE = 0, missing = 0. The registered threshold (`§4`) is *"**GATE FAIL** — **any**
> site resolves **UNGUARDED**"*, and four do.

**Tally re-derived from the per-site rows rather than read off the driver's own summary
line:** `grep -c` over the record gives **4** `UNGUARDED` and **8** `GUARDED`, agreeing with
the summary. *A summary line is the thing most likely to be wrong and the least likely to be
checked.*

## 2. THE CONTROLS FIRED FIRST, AND THE FAILING BRANCH WAS EXECUTED — NOT ASSERTED

All four ran in **this same invocation**, through the **production** `classify_site()` and
`verdict()` (`§2p.3(d)`), and the driver refuses the whole run if any fails:

| control | required | measured |
|---|---|---|
| **NEGATIVE / planted** (rule 3, `§2p.3(e)`) | class `UNGUARDED`, verdict **`GATE FAIL`, rc 1** | **`UNGUARDED`, `GATE FAIL`, rc 1** |
| **POSITIVE** (`§2p.3(e)`) | class `GUARDED`, verdict `PASS`, rc 0 | **`GUARDED`, `PASS`, rc 0** |
| **EMPTY-INPUT** (`§2p.2`) | `NOT A RESULT`, rc 2 | **`NOT A RESULT`, rc 2** |
| **ABSENT-SITE** | `NOT A RESULT`, rc 2, never a skip | **located=False, `NOT A RESULT`, rc 2** |

**This is the whole difference between VR3-R2 and VR3.** VR3's `GATE FAIL` was **unreachable
in the implementation** — `vr3_guard_set_attribution.py:76-79`, the string `GATE FAIL` absent
from the file, the `unguarded` list built at `:72` and never read — so its `PASS` **could not
have come out any other way and therefore carried no information.** Here the failing branch
was **driven to execution by a planted input before the population was read**, and the
positive limb proves the instrument has not simply been made to refuse everything.

## 3. THE FOUR — AND THE FINDING IS BETTER THAN "FOUR SITES"

| site | binding | G1 — the deciding set | G4 |
|---|---|---|---|
| `VMFL001/grade_vmfl001.py:360` | `hits`, in `probe_series` | ~~`postProcessing/*/U/gateProbes`~~ → **`postProcessing/gateProbes/*/U`** ⚠ CORRECTED IN PLACE 2026-09-03 (`§2ae`/`§2p.11`) — see the CORRECTION at the head of this section; the class in the next column is UNAFFECTED | **UNGUARDED** |
| `VMFL001/R2/grade_vmfl001_r2.py:420` | `hits`, in `probe_series` | ~~`postProcessing/*/U/gateProbes`~~ → **`postProcessing/gateProbes/*/U`** ⚠ CORRECTED IN PLACE 2026-09-03 (`§2ae`/`§2p.11`) — see the CORRECTION at the head of this section; the class in the next column is UNAFFECTED | **UNGUARDED** |
| `VMFLGPU001/grade_vmflgpu001.py:589` | `hits`, in `probe_series` | ~~`postProcessing/*/U/gateProbes`~~ → **`postProcessing/gateProbes/*/U`** ⚠ CORRECTED IN PLACE 2026-09-03 (`§2ae`/`§2p.11`) — see the CORRECTION at the head of this section; the class in the next column is UNAFFECTED | **UNGUARDED** |
| `VMFLGPU001-R2/grade_vmflgpu001_r2.py:614` | `hits`, in `probe_series` | ~~`postProcessing/*/U/gateProbes`~~ → **`postProcessing/gateProbes/*/U`** ⚠ CORRECTED IN PLACE 2026-09-03 (`§2ae`/`§2p.11`) — see the CORRECTION at the head of this section; the class in the next column is UNAFFECTED | **UNGUARDED** |

> **ALL FOUR ARE THE SAME FUNCTION — `probe_series` — CARRYING THE SAME BINDING OVER THE SAME
> PATTERN, COPIED INTO FOUR GRADERS. This is ONE defect with four instances, not four
> defects**, which makes it both easier to repair and easier to have missed: a reviewer who
> cleared `probe_series` once had no reason to read it again.

Each is a **`LEXICAL` `sorted(glob.glob(...))`** — not the numeric key `grade_vmfl076.py`
uses — over a pattern whose `*` **is the start-time directory**, and in every case there is
**no `len(hits)` guard in `probe_series` after the binding.**

**And `VMFL001/grade_vmfl001.py` is the cleanest possible illustration of `DEAD_LEVER_AUDIT`
§7.4's mechanism.** The module *does* carry cardinality guards — `len(hits) == 1` at `:179`
and `len(hits) > 1` at `:181` — but both live in **`find_set_file`, a different function, over
a different set.** *A site carrying prominent, correct-looking cardinality guards is
nonetheless unguarded on the set that decides the answer.* That is exactly the proposition
VR3 was registered to test and never tested.

## 4. WHAT THIS DOES AND DOES NOT DO — `§7` OF THE REGISTRATION, HONOURED

- **It widens a CANDIDATE set: 19 → 23.** Four sites previously counted as safe are not safe
  for the reason claimed.
- **⚠ IT MOVES NO VERDICT, AND THAT IS NOT A HEDGE — IT IS `DEAD_LEVER_AUDIT` §7.3's STANDING
  MEASUREMENT.** Every hazard case produced **exactly one** start-time directory, so a
  one-member ordered set has the same first element under any ordering. **No landed ansys
  verdict is exposed by this finding**, and nothing here re-grades one.
- **The exposure is PROSPECTIVE:** these four graders will read the wrong directory the first
  time a case they grade produces two start-time directories, and **nothing in them will
  refuse or announce it.**
- **This team audits the RESULT, not the work.** The repair is ansys-verification's, is barred
  in frozen comparators post-compute (rule 2), and belongs in successors and unfrozen
  graders. The lab's reference ordering key is already named — `float(name)` plus numeric
  sort, arrived at independently twice (`§7.4`, `§6.6`).

## 5. THE POPULATION IS A RECONSTRUCTION, AND SAYING SO IS PART OF THE VERDICT

Ansys's *"12 cardinality-guarded SAFE"* is a **bare count** at `docs/LAB_STATE.md@c7176346`
with **no enumeration anywhere in the repository**; `DEAD_LEVER_AUDIT.md:1508` states the
classification basis **conditionally**, so the basis was itself inferred. The registered
predicate is **validated against the one enumerated half that does exist** — it reproduces
ansys's **19 hazard sites 19/19 by file and line**, zero missed, zero extra — and the site set
is **identical at `c7176346` and at HEAD** while the trees genuinely differ.

**The residual disagreement is disclosed and NOT reconciled:** the predicate returns **14** on
the guarded half where ansys counted **12**, and **`N = 12` after excluding the two
`grade_vmfl076.py` sites** (`VMFL076/` and `VMFL076-R2/`, each one site at `:677`).
**Reproducing a reconstruction does not convert it into a measurement**, and this verdict is
`GATE FAIL` **over the registered reconstruction**, not over a list ansys ever wrote down.

**A correction to VR3's own arithmetic, carried here rather than buried:** VR3 registered
*"the 11 sites"*, assuming **one** removal for `grade_vmfl076`. **There are two such files.**
The number 11 has no support; it is 12.

## 6. RULE 12 CALIBRATION — PREDICTED VERSUS ACTUAL

| | registered | actual | ratio |
|---|---|---|---|
| graded run | **0.002 core-min** (point) | **0.004167 core-min** (0.25 s wall × 1 rank ÷ 60) | **2.08×** |
| cap | 0.05 core-min | — | **8.3 % of cap; no overrun** |

**Attribution: MISPREDICTION, not contention and not waste.** The point estimate was grounded
on the **control invocation alone** (0.03 s) and omitted the cost of parsing **twelve real
graders**, several of them over 1,600 lines. **No waste is claimed and none is hidden.**
Zero solver compute. **≈ $3.6×10⁻⁶, DERIVED at $0.0513/core-h and not measured** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5).

*The estimate was wrong by 2×, and that is the calibration dataset working exactly as Sanaa's
launch rule intends: an estimate is a prediction, and this one is now on the record as having
been capable of being wrong.*
---

## AMENDMENT 1 TO THE VR3-R2 SECTION — 2026-09-03 — **THE `§2ae` CORRECTION WAS FILED AT THE SECTION HEAD AND NEVER REACHED THE PER-SITE TABLE. FIVE ASSERTION SITES OF TWO WITHDRAWN CLAIMS STOOD UNMARKED IN THE BODY OF THIS RECORD, AND FOUR OF THEM WERE THE SUMMARY TABLE.**

**Lines whose number changed above this section: 0.** Pure append. **⚠ FIVE LINES ABOVE THIS
SECTION CHANGED CONTENT WITHOUT CHANGING NUMBER — `:480`, `:610`, `:611`, `:612`, `:613` — and
that is what this amendment is about**, so it is stated here rather than left for a reader to
discover. Legal under `§2ae` (v1.51): this is a **RECORD**, corrected in place. **No frozen
byte, no comparator, no registration, no capture was touched; no sha that fixes a grading path
is broken.** **Zero solver compute; 0 core-min; $0.00.** **No gate, threshold, band, cap or
label created, moved or retired. Nothing re-graded. The `GATE FAIL` does not move.**

### 1. WHAT THE CORRECTION DID AND DID NOT REACH

The correction at the head of this section (`4fa2436d`) was placed there **deliberately and
correctly**, citing `§2ae`: the correction must be reachable from where the number is read.
**It reached the section head and it did not reach the table.** Its own first sentence says
*"THE `G1` PATTERN IS TRANSCRIBED WRONG ON EVERY ROW OF THIS RECORD"* — **it named the rows
and left them unmarked.** The correction to the correction (`b086eaf6`) withdrew the
illustrative pair `['0.1','0.05']` and left its assertion standing 24 lines above, inside the
very correction that withdrew it.

**THIS IS `§2p.11`'s SPECIMEN, REPRODUCED, IN THE SAME WEEK, BY THE TEAM THAT RULED IT** — and
in the worse of the two forms that clause distinguishes: the sites left unmarked here are a
**per-site summary table**, which `§2p.11` names as *"read INSTEAD OF the prose, not in
addition to it."* A reader who goes to §3 for *which four sites* was, until this amendment,
given four unmarked false patterns and no signal that any correction existed.

### 2. THE COMPLETENESS TEST, RUN AT CORRECTION TIME, STATED AS A PARTITION

`§2p.11`: *"grep the false claim's own distinguishing string; an unmarked hit is an incomplete
correction."* Both greps were run over this file **before** any marker was written, and both
were re-run after.

**`postProcessing/*/U/gateProbes` — 5 hits:**

| class | lines | status |
|---|---|---|
| assertion sites — the §3 per-site table, `G1` column | `:610`, `:611`, `:612`, `:613` | **4 of 4 NOW MARKED** (0 of 4 before) |
| quotation inside the head correction | `:440` | **correct as written — already struck** |
| unrelated-but-matching | none | — |

**`['0.1','0.05']` and its prose form — 7 hits:**

| class | lines | status |
|---|---|---|
| assertion site — *"`"0.1"` precedes `"0.05"`"* | `:480` | **1 of 1 NOW MARKED** (0 of 1 before) |
| quotations inside the correction to the correction | `:515`, `:519`, `:530` | **correct as written** — a correction must quote what it corrects, and `:519` and `:530` are the TRUE statements |
| unrelated-but-matching — cost figures | `:350`, `:671`, `:676` | **assert nothing about sorting** |

**The partition is the deliverable, not the number.** *5-hits-with-4-marked and
5-hits-with-4-missed are the same count.*

### 3. THE CORRECTED PATTERN, VERIFIED AT ALL FOUR SITES — NOT INHERITED FROM THE CORRECTION

The head correction cites **one** site. The markers write the corrected pattern onto **four**
rows, so all four were read at source before the markers were proposed:

| site | pattern, at source | `PROBE_FO` | resolved |
|---|---|---|---|
| `VMFL001/grade_vmfl001.py` | `pats` at **`:359`** = `os.path.join(level_dir, "postProcessing", PROBE_FO, "*", "U")`; bound at `:360` | `"gateProbes"` at `:72` | `postProcessing/gateProbes/*/U` |
| `VMFL001/R2/grade_vmfl001_r2.py` | `pats` at **`:419`**, identical; bound at `:420` | `:89` | same |
| `VMFLGPU001/grade_vmflgpu001.py` | inline in the binding at **`:589`** | `:159` | same |
| `VMFLGPU001-R2/grade_vmflgpu001_r2.py` | inline in the binding at **`:614`** | `:174` | same |

**⚠ A PRECISION CORRECTION TO MY OWN CORRECTION, AND IT IS SMALL BUT IT IS THE THIRD TIME.**
The head correction states *"`grade_vmfl001.py:360` is `os.path.join(level_dir,
"postProcessing", PROBE_FO, "*", "U")`"*. **`:360` is `hits = sorted(glob.glob(pats))`; the
`os.path.join` is at `:359`.** The substance is right and the line is off by one — and the
same one-line indirection holds at `VMFL001/R2`, where the join is at `:419` and the binding
at `:420`. **Two of the four sites bind through a name; two bind inline.** *A citation that is
one line off is still a citation nobody can check without noticing.*

### 4. WHAT THIS AMENDMENT DOES NOT DO

- **THE `GATE FAIL` DOES NOT MOVE, AND IT WAS RE-DERIVED HERE RATHER THAN INHERITED.** See §5.
- **NO SITE CHANGES CLASS.** UNGUARDED = 4, GUARDED = 8, REFERENCE = 0, missing = 0, N = 12.
- **NOTHING IS RE-GRADED**, no ansys verdict is touched, and the CANDIDATE set stays 19 → 23.
- **THE FROZEN DRIVER IS NOT TOUCHED.** `vr3r2_guard_set_attribution.py` keeps blob
  `ff0af23c4630`. Its `G1` limb still owes a successor **by new registration only**; that debt
  is **PROSPECTIVE** and its trigger — *"before any successor quotes a pattern from it"* —
  **has not fired**, because after this amendment the record quotes the source-verified
  pattern and not the instrument's.
- **THE RAW CAPTURE IS NOT ANNOTATED.**
  `VR3R2_GUARD_SET_ATTRIBUTION/vr3r2_stdout.txt` prints the wrong pattern at four rows and
  **must keep printing it.** It is what the instrument printed; it is the evidence that the
  instrument is defective, and a re-drive reproducing it byte for byte is the check that keeps
  it evidence. **The correction belongs in the record that READS the capture.**

### 5. THE VERDICT, RE-DERIVED

`[RE-DERIVED FROM THE REGISTRATION AND THE ARTEFACTS, NOT FROM THIS RECORD'S PROSE]`

- **Threshold**, `VR3R2_PREREGISTRATION.md:164`: *"**GATE FAIL** — **any** site resolves **UNGUARDED**."*
- **Population**, `:111-113`: **N = 12.**
- **Class definitions**, `:153-156`: **GUARDED** iff *"an attributed **CARDINALITY** guard measures"* the deciding set; **UNGUARDED** iff *"no such guard; any guard present measures a different set."*
- **Measured**, `vr3r2_stdout.txt:99`: *"Classified 12 of 12 registered sites; UNGUARDED=4 GUARDED=8 REFERENCE=0; missing=0"*; `:101` `VERDICT: GATE FAIL`; `RUN_RC.txt` **`RC=1`**.
- **Neither withdrawn claim is an input to the class.** `classify_site` sets `cls` from `kind` and `effective` alone; `g1` is returned and printed and never consumed. `has_wildcard` (`:182-183`) is `any(…)` over the multiset — order-independent. **The pattern's ORDER cannot move a class.**
- **A truthiness guard is not a cardinality guard**, so defect (3)'s blindness could only ever have produced the class it produced.

**`GATE FAIL` STANDS, on the registered threshold, over the registered population, from the
registered class definitions.** `§2w.1`: both withdrawn claims **DESCRIBE** the record; neither
**STANDS BETWEEN** the run and the reading.

### 6. ⚡ AND THE ONE LIMB THE CORRECTION EXPLICITLY DECLINED TO GENERALISE, NOW MEASURED

The head correction carries `[MY OWN ADDITION, VERIFIED AT grade_vmfl001.py:366 ONLY AND NOT
GENERALISED TO THE OTHER THREE]`. **It generalises. Measured at all four:**

| site | truthiness guard | consumes ALL members |
|---|---|---|
| `VMFL001:360` | `if not hits: refuse(…)` at `:361` | `for h in hits:` at `:366` |
| `VMFL001/R2:420` | `:421` | `:426` |
| `VMFLGPU001:589` | `:590` | `:594` |
| `VMFLGPU001-R2:614` | `:615` | `:619` |

**All four refuse an empty glob and all four iterate every member.** So the concatenation
hazard — a crashed-and-resumed run producing a second start-time directory, whose series is
then spliced in lexical order — **is a property of all four sites, not of one.** *This
discharges a non-generalisation the correction stated against itself, and it makes the failing
condition's substance broader, never narrower.*

### 7. WHAT IS NOT DISCHARGED HERE, NAMED SO IT IS NOT READ AS CLEARED

- **`VERIFICATION_CHARTER.md:5828`** (v1.50 `§2ab.1`) asserts the wrong pattern, **unmarked**.
- **`docs/LAB_STATE.md` block `UPDATE V-68`** asserts the wrong pattern, **unmarked**; block **`UPDATE V-72`** asserts the withdrawn `"0.1"`/`"0.05"` pair, **unmarked**, 16 lines below its own withdrawal.
- **ansys's latency claim is still theirs and still not re-derived by this team** — `find cases/ansys_verification -type d -name gateProbes` returns nothing on this box.
- **`VMFLGPU001-R2`'s segmentation is still `NOT A RESULT`** and nothing may cite it as checked.

| item | outcome |
|---|---|
| reading sites named by the head correction | **"every row" — named, not enumerated, and none marked** |
| reading sites found by search at correction time | **5 in this record** — `:480` + the four table rows |
| marked before this amendment | **0 of 5** |
| marked now | **5 of 5.** Grep 1: 5 hits, 4 assertion (marked) + 1 quotation. Grep 2: 7 hits, 1 assertion (marked) + 3 quotations + 3 unrelated |
| why a partition and not a count | **5-with-4-marked and 5-with-4-missed are the same NUMBER** |
| why the dropped ones are the worst | **all four are the per-site SUMMARY TABLE** |
| lines renumbered · content-changed above | **0 · 5, all five named** |
| frozen bytes touched · shas broken · captures annotated | **0 · 0 · 0** |
| verdict | **`GATE FAIL` — UNCHANGED, and re-derived rather than inherited** |
| gates · thresholds · bands · caps · labels | **0 · 0 · 0 · 0 · 0** |
| solver compute | **0 core-min, $0.00** |

---

# VR6 — **`GATE FAIL`.** 198 `_launch` BLOCKS — THE ARTIFACT PROVING A FROZEN PRE-REGISTRATION WAS ACTUALLY EXECUTED — EXIST ONLY AS UNTRACKED FILES

**FILED 2026-09-12 by a verification lane.** Drive captured at `HEAD 5a05eda7`,
`2026-09-12T01:00:13Z`, host `ip-172-31-43-247`, rc **1**.
**Solver compute: 0 core-min.** Static, read-only analysis; **two** index-free git reads
per queue record and no others.

> **VERDICT: `GATE FAIL`.** **198 untracked `_launch` blocks.** A `_launch` block (pid, sid,
> utc, status_file, started_epoch) is `VERIFICATION_CHARTER` §9's evidence that a frozen
> pre-registration was **executed**. 198 of them exist **only as files in one box's working
> tree**: one `rm` from gone, invisible to anybody reading the repository at HEAD, and
> unreconstructable by any later audit.
>
> **This is a finding about the EVIDENCE RECORD, not about the runs.** No verdict is
> withdrawn by this item. **The remedy is to COMMIT the records, never to delete them** —
> and the staged deletions of the pre-launch copies are **renames the shared index recorded
> as deletions**, not fossils.

## 1. THE CORPUS, AS MEASURED

`[MEASURED BY THIS LANE, 2026-09-12T01:00:13Z, HEAD 5a05eda7]`
Artefact: `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/vr6_stdout_2026-09-12.txt`

| team | on disk | tracked at HEAD | untracked | untracked **and** carrying `_launch` |
|---|---|---|---|---|
| ansys-verification | 75 | 20 | 55 | **37** |
| cfd | 57 | 48 | 9 | **9** |
| closure | 87 | 2 | 85 | **85** |
| dafoam | 80 | 60 | 20 | **19** |
| heat-transfer | 119 | 76 | 43 | **42** |
| verification | 6 | 0 | 6 | **6** |
| **TOTAL** | **424** | **206** | **218** | **198** |

- **45 tracked-but-DIFFERING on disk — REPORTED, NEVER GATED.** An uncommitted edit is
  somebody's unfinished work and is inspected, never reverted (standing rule 10). It is not
  in the gate and did not move the verdict.
- **20 untracked WITHOUT a `_launch` block** — never-run drafts. **Queue depth, not lost
  evidence**, and deliberately excluded from the gated figure. 218 − 20 = 198.
- **closure is the extreme: 87 on disk, 2 tracked.** 85 of its 87 current queue records
  carry execution evidence with no committed trace.

## 2. RULE 2 FREEZE CHECK — THE FROZEN FILE **IS** THE FILE THAT RAN

Re-asserted **in the launching invocation**, not before it and not from recall:

| artefact | blob |
|---|---|
| `verification/campaign/VR6_PREREGISTRATION.md` at the registered freeze `2a61b7bab90de4ae89508e7a23f43c2b6a547002` | `82fac0c5c0aa28385a7e134c9b0292eb8df728d4` |
| …the same file **at HEAD** | `82fac0c5c0aa28385a7e134c9b0292eb8df728d4` |
| …the same file **on disk** | `82fac0c5c0aa28385a7e134c9b0292eb8df728d4` |
| `verification/credibility/vr6_untracked_launch_record.py` **at HEAD** | `496e84e8079b344c99115dcfa8bea026f5974bfd` |
| …the driver **on disk** | `496e84e8079b344c99115dcfa8bea026f5974bfd` |

**Three-way identity on the pre-registration and two-way on the driver.** The freeze sha
recorded in the queue entry is the one the gate was graded under.
`__pycache__` under `verification/credibility/` was removed before the drive and
`PYTHONDONTWRITEBYTECODE=1` set, against the stale-bytecode inversion.

## 3. THE FOUR CONTROLS — ALL BEHAVED, ALL IN THIS INVOCATION (rule 3)

| limb | required | measured |
|---|---|---|
| **P1 +** `scripts/queue_runner.py` | `TRACKED_IDENTICAL` | **`TRACKED_IDENTICAL`**, HEAD blob `9a89c10f8e8c` — *the reader can see a non-zero* |
| **P2 −** freshly planted path | `UNTRACKED` | **`UNTRACKED`** — *the reader can see a zero* |
| **P3 −** bytes **byte-identical** to tracked blob `9a89c10f8e8c`, planted at an untracked path | `UNTRACKED` | **`UNTRACKED`** — *the reader keys on PATH-at-HEAD, not on content* |
| **P4 +/−** two planted records, one with a `_launch` block and one without | one classification each way | **`WITH`=present, `WITHOUT`=absent**, both through the real corpus reader |

**P3 is the limb that matters.** A reader that answered *"do these bytes exist somewhere in
history"* rather than *"does this PATH resolve to a blob at HEAD"* passes P1 and P2 and
fails P3. **A zero from a reader not shown able to see a non-zero is not evidence**, and all
four answers were produced in the same invocation as the counts above.

**Instruments, and why nothing else was used:** exactly `git rev-parse HEAD:<path>` against
`git hash-object <path>`, with tracked content read by `git show HEAD:<path>` and never
`git show :<path>`. `status`, `diff`, `ls-files` and `add` are refused **in code** by a
raising allowlist. All four consult the **shared index**, which on this box misreports here
and misreports **stably**.

## 4. THE LAUNCH LOG — THE SECOND 2026-08-30 CAUSE IS GONE, AND 116 ROWS STILL HAVE NO COMMITTED TRACE

`verification/queue/LAUNCH_LOG.tsv` reads **`TRACKED_DIFFERS`, 437 launch rows on disk.**

**This CHANGED since 2026-08-30**, when it was `UNTRACKED` and was a **second, independent
cause** of the `GATE FAIL`. It was first added to the tree at **`0047fcaa0`, 2026-09-03**.
**The `GATE FAIL` is now driven SOLELY by the 198 untracked `_launch` blocks.**

**And "tracked" is not "preserved".** `[MEASURED BY THIS LANE, index-free]`
`git show HEAD:verification/queue/LAUNCH_LOG.tsv | wc -l` = **321 rows**; the file on disk
carries **437**. **116 launch rows exist on disk with no committed trace.** That is not in
this item's registered gate and does not move the verdict — it is stated so that "the launch
log is tracked now" is not read as "the launch log is safe now".

## 5. ⚠ THE LIMITATION — **VR6 WALKS THE DISK, SO IT IS STRUCTURALLY BLIND TO RECORDS TRACKED AT HEAD AND DELETED FROM THE WORKTREE. THERE ARE 177 OF THEM, AND ONE OF THEM IS VR6's OWN.**

This is stated here, in the record, rather than left for a later reader to discover.

`[MEASURED BY THIS LANE, independently of the driver, via `git ls-tree -r HEAD` — which does
not consult the index — with the driver's own archived-record exclusion applied]`

| | count |
|---|---|
| current (non-archived) queue records **tracked at HEAD** | **383** |
| …of those, **absent from the worktree** | **177** |
| closure · heat-transfer · ansys-verification · dafoam · verification · cfd | **86 · 28 · 27 · 25 · 6 · 5** |
| 383 − 177 | **206 — exactly VR6's `tracked` column. The arithmetic closes.** |

**VR6 therefore UNDERCOUNTS THE CORPUS BY 177.** Its `disk` column is not the corpus; it is
the corpus minus everything already deleted from this working tree.

**AND VR6 IS INVISIBLE TO ITSELF.** All six of verification's 177-members are the team's own
pre-launch queue records, `VR1`–`VR6`, including
`verification/queue/verification/VR6_UNTRACKED_LAUNCH_RECORD.json` — tracked at HEAD, absent
from disk, **renamed into `launched/` by the runner**. The only form of its own record VR6
can see is the untracked `launched/` copy, which it counts among the 198.

**WHAT THIS DOES AND DOES NOT DO TO THE VERDICT — and the answer is measured, not asserted.**
Restoring all 177 would move the table to **601 on disk / 383 tracked / 218 untracked**.
**The untracked figure is IDENTICAL in both worlds**, because every one of the 177 is tracked
by construction. **A deletion cannot manufacture a single untracked `_launch` block**, so the
gated quantity — and therefore the `GATE FAIL` — is **immune to this blindness**. What the
blindness costs is the *denominator*: the 218 looks like 51 % of the corpus and is 36 % of it.

**The growth is launches, not deletions.** 41 untracked at the 2026-08-30 smoke drive → 52 at
the 2026-08-30 queue drive → **218** tonight, across 13 days in which the queue runner wrote
`launched/` records that were never committed. Deletions move records **out of** the disk
column; they cannot move records **into** the untracked column.

## 6. THE PRIOR DRIVES, AND WHICH ONE IS THE VERDICT — **THERE WERE TWO ON 2026-08-30, NOT ONE**

| drive | when | corpus (disk/tracked/untracked/untr+`_launch`) | `LAUNCH_LOG.tsv` | rc | artefact |
|---|---|---|---|---|---|
| **pre-enqueue SMOKE drive** | 2026-08-30, before enqueue | **210 / 169 / 41 / 41** | `UNTRACKED`, 133 rows | 1 | `verification/campaign/VR6_PREREGISTRATION.md` §8; `_smoke` field of the queue record |
| **QUEUE drive — first compute under the frozen registration** | **2026-08-30T23:14:32Z** | **213 / 161 / 52 / 52** (7 differing, 0 without `_launch`) | `UNTRACKED`, 145 rows | **1** | `verification/credibility/launcher.queue.out`; `verification/credibility/STATUS.VR6_UNTRACKED_LAUNCH_RECORD` |
| **verdict drive** | 2026-09-12, earlier this session | 424 / 206 / 218 / **198** | `TRACKED_DIFFERS`, 437 rows | 1 | **no durable capture was written** — see §8 |
| **THIS CAPTURE DRIVE — the cited one** | **2026-09-12T01:00:13Z** | **424 / 206 / 218 / 198** | `TRACKED_DIFFERS`, 437 rows | **1** | `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/` |

**A correction to how this has been described, made here rather than allowed to stand:** the
2026-08-30 activity was **not one smoke drive**. There was a pre-enqueue smoke drive **and** a
queue-driven execution under the frozen registration 40 minutes later, which returned
`GATE FAIL` at rc 1 over 52 untracked `_launch` blocks and an untracked launch log — **and
that verdict was never recorded in this file until now.** It is on the record above.

**The two 2026-09-12 drives agree on every count**, figure for figure, including the per-team
table. The capture drive is cited throughout this section because **its artefact is on disk**.

## 7. RULE 12 CALIBRATION — ESTIMATE VERSUS ACTUAL

| | figure |
|---|---|
| registered estimate (`VR6_PREREGISTRATION.md:112`) | **0.05 core-min** |
| registered cap (`:111`) | **0.5 core-min** |
| verdict drive (reported, no durable capture) | 4.67 s wall × 1 rank = **0.0778 core-min** |
| **capture drive (MEASURED, artefact on disk)** | **4.463 s wall × 1 rank = 0.074384 core-min** |
| ratio, capture drive / estimate | **1.49×** |
| both drives together, against the cap | 0.1522 core-min = **30 % of cap. No overrun, no stop.** |
| derived dollars | **≈ $1.3 × 10⁻⁴, DERIVED at $0.0513/core-h, NOT MEASURED** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER` §5) |

**ATTRIBUTION: MISPREDICTION OF CORPUS SIZE. NOT contention, NOT waste — and that is
measured, not assumed.** The registered estimate was set from the **busy-box** drive of
2026-08-30: 2.687 s over the 210-record corpus of that day = **12.79 ms/record**. Tonight: 4.463 s over 424 records
= **10.53 ms/record** (the verdict drive, 11.01 ms/record). **The per-record rate IMPROVED by
18 %** — and improved *while the box was at load 56.92 / 58.96 / 51.26 on 16 cores, 3.6×
oversubscribed.* **The corpus DOUBLED, 210 → 424 records in 13 days.** Re-pricing the
registered estimate at the **unchanged busy rate** and tonight's population gives
424 × 12.79 ms = **0.0904 core-min**, against which the measured drive is **0.82× — under.**

**So contention is separated rather than absorbed, per rule 12.** Contention is present and
is not denied: a 1-rank job dominated by subprocess spawn is exactly what a 3.6× oversubscribed
box taxes. But its effect here is **bounded above by zero** — the per-record rate did not rise,
it fell — so **none of the 1.49× miss can be hiding in it.** The estimator was right about the
rate and wrong about the population. **Zero waste: both drives returned the full measurement.**

## 8. WHAT COULD NOT BE VERIFIED, STATED PLAINLY

1. **The verdict drive earlier this session left no capture on any durable path.** Its figures
   reached this lane as relayed numbers, and **a number whose artefact is gone is not a
   result**. This lane therefore re-drove the frozen driver and wrote the capture to
   `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/`, reproducing **every** relayed
   figure exactly — the totals, all six per-team rows, the 45, the 20, the 437 and the
   `TRACKED_DIFFERS`. The record cites **the drive whose artefact exists.** The 4.67 s wall of
   the earlier drive is **reported, not measured here**, and is labelled as such in §7.
2. **Whether any of the 198 untracked `_launch` blocks has already been lost** is not knowable
   from this instrument: it counts what is on disk now. A record deleted before tonight is
   outside both its `disk` column and this count.
3. **The 177 deleted-from-worktree records were not read.** Their tracked content at HEAD is
   intact and was not inspected here; only their presence and absence were counted.
4. **Nothing was committed, added, deleted or reverted by this item.** The shared index stages
   the pre-launch copies as deletions while their `launched/` destinations were never added, so
   committing the index as it stands would **remove the only tracked trace and add nothing.**
   **A `GATE FAIL` here is not licence to `git add` and not licence to remove anything** — the
   index is the chief's call.

## 9. ARTEFACT INDEX

| artefact | what it holds |
|---|---|
| `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/vr6_stdout_2026-09-12.txt` | the cited drive: controls, per-team table, the full roll call of all 198 untracked `_launch` blocks, the verdict line |
| `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/RUN_RC.txt` | `RC=1` |
| `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/vr6_time_2026-09-12.txt` | 4.463 s wall, 0.074384 core-min |
| `verification/runs/verification/VR6_UNTRACKED_LAUNCH_RECORD/vr6_stderr_2026-09-12.txt` | empty (0 bytes) |
| `verification/credibility/vr6_untracked_launch_record.py` | the frozen driver, blob `496e84e8` |
| `verification/campaign/VR6_PREREGISTRATION.md` | the frozen gate, blob `82fac0c5` at freeze `2a61b7ba` |
| `verification/credibility/launcher.queue.out` | the 2026-08-30T23:14Z queue drive, recorded here for the first time |
| `verification/queue/verification/launched/VR6_UNTRACKED_LAUNCH_RECORD.json` | the item's own `_launch` block — **untracked, and one of the 198 it counts** |

**Gates, thresholds, bands, caps or labels created, moved or retired by this record: 0.
Frozen bytes touched: 0. Nothing re-graded. Nothing sent (standing rule 7).**
