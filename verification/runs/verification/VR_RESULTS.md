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
