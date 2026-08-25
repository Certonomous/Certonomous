# D4-DEF-4 — SUPERVISOR'S RULING ON THE REPAIR, and a correction to my own brief

**Written 2026-08-25 by dafoam-supervisor.** This is a **ruling, not a parked referral**,
under Sanaa's 2026-08-25 desk-item disposal rule. It is committed **before** any lane acts
on it, because a ruling that authorises a re-freeze belongs in the record and not in a
lane brief.

**Nothing here is sent, filed, uploaded, posted or commented. SUBMISSIONS ARE PARKED and
sending is Sanaa's decision alone** (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10). The
defect is in **this lab's own instrument**, not in DAFoam, OpenMDAO, IPOPT or pyOptSparse
— **no upstream report arises and none is to be drafted.**

---

## 1. I VERIFIED THE DIAGNOSIS MYSELF BEFORE BELIEVING IT (SUPERVISION §3 check 3)

A conclusion large enough to change this family's direction gets my own read, and this one
changes it. **I did not accept the lane's report.** I read the registration and the
extracted artifact directly:

`d4_opt_runScript.py` line 24 sets `U0 = 100.0`, and its design-variable block registers

| variable | bounds | scaler |
|---|---|---|
| `twist` | `[-10.0, 10.0]` | **0.1** |
| `shape` | `[-1.0, 1.0]` | **10.0** |
| `patchV` | `lower=[U0, 0.0]`, `upper=[U0, 10.0]` | **0.1** |

`F/d4_endpoint_dvs.json` as extracted:

| variable | extracted | ÷ registered scaler | inside bounds? |
|---|---|---|---|
| `patchV[0]` | **10.0** | **100.0** | pinned value, exact |
| `shape` | max **6.024591873823496** | **0.6024591873823496** | yes, `[-1,1]` |
| `twist` | min **−0.28020223162835683** | **−2.8020223162835683** | yes, `[-10,10]` |

**`patchV[0]` is PINNED — `lower` and `upper` are the same number, `U0 = 100.0` — so its
physical value is definitionally 100.0 and no optimiser can move it. The extractor returns
exactly `100.0 × 0.1`.** No second explanation survives for a pinned variable. **The
diagnosis is confirmed by my own read, not relayed.**

## 2. THE SENTENCE THAT MATTERS, AND WHY THIS IS A CLASS AND NOT AN INCIDENT

`shape`'s scaler is **10**, so the corruption was a factor of ten and the mesh could not
survive it: 2,989 non-orthogonality errors, 6,090 mis-oriented face pyramids, `AnalysisError:
Mesh quality error!` on the first primal, 15 wall s, `rc=1`.

**Had that scaler been 1.0 — as it is for the objective and both aerodynamic constraints —
every primal would have converged and arm F would have produced a complete, well-formed,
plausible FD table AT A DESIGN POINT THAT IS NOT THE OPTIMUM**, with `twist` 10× wrong and
the freestream 10 m/s instead of 100 m/s underneath it. Five components requested, five rows
returned, in the registered order: **every count refusal passes, G6's plant is seen, G6b's
blind reader is refused, G7's four mutations each raise their named refusal. THE FULLY ARMED
INSTRUMENT SET WOULD HAVE CERTIFIED IT.**

**A UNITS ERROR IS INVISIBLE TO EVERY COUNT-BASED, PLANT-BASED AND ORDER-BASED CONTROL IN
THIS FAMILY'S GATE SET. They check THAT n components were measured. They never check WHERE.**

This is the D3 catastrophe with the corruption **moved one stage upstream, out of the grader
and into the PRODUCER.** Every D4 control lives downstream of `d4_endpoint_dvs.json` and
takes its contents as given. **The crash is lucky, not designed.**

## 3. THE RULING — §2d.1 IS SATISFIED, AND I APPLY THE STRICT READING TO GET THERE

Arm F produced **no graded quantity** — it crashed before the first primal converged — so a
convenient reading says §2d never engaged for the FD path and no exception is needed. **I do
not take that reading.** Arm O **is** graded and committed (`9dd0054a`, nine gates PASS), and
the extractor sits in the instrument set of a rung that has graded quantities. I therefore
treat §2d as engaged and require the **§2d.1 four-condition exception** to be met in full.

| condition | met? | on what |
|---|---|---|
| **(1)** repairs a DEMONSTRABLE ERROR, not a preference | **YES** | an extractor returning 10.0 for a variable pinned at 100.0 is arithmetically wrong, not differently preferred |
| **(2)** established by an instrument INDEPENDENT OF THE HYPOTHESIS — one that GRADES NOTHING | **YES, THREE INDEPENDENT WAYS** | (a) the **pinned-variable identity** `patchV[0] ≡ U0`, a near-identity that grades nothing and has no direction to be selected toward; (b) the **bound-violation guard** — 62 of 96 `shape` components outside `[-1,1]`, and IPOPT does not violate bound constraints; (c) the in-container reading that `getValues(scale=False)` and `getValues(scale=True)` return IDENTICAL values and `getDVInfo()` shows bounds already multiplied — a direct measurement that grades nothing |
| **(3)** record discloses it, NAMES the instrument, QUANTIFIES what moved | **REQUIRED, and it is on the lane** | the table in §1 is the quantification: `shape` 6.0246 → 0.6025, `twist` −0.2802 → −2.8020 deg, `patchV` 10.0 → 100.0 m/s |
| **(4)** pre-repair values recorded BESIDE the published ones | **REQUIRED, and it is on the lane** | `F/d4_endpoint_dvs.json` is preserved byte-for-byte; the corrected file is a NEW artifact beside it, never a rewrite |

**Condition (2) is the load-bearing one and §2d.1 says so explicitly. It is met by the
pinned variable, which is this case's exact analogue of the K0cS heat balance: a
near-identity that is reported, gates nothing, and cannot have been selected to move a
verdict in a wanted direction because it does not know which direction that is.**

**RULING: THE REPAIR IS PERMITTED.** Three limits bind it.

### LIMIT 1 — THE REPAIR IS NOT FROZEN UNTIL A SOLVE PROVES IT. This is the whole ruling.

The lane named the gap itself and did not paper over it: **the corrected physical values are
NOT verified by a solve.** No primal has been run at the ÷scaler point, so it is **not
demonstrated** that the corrected point reproduces `CD = 2.1125978e-02`.

**I make that reproduction a PRECONDITION of the freeze, not a follow-up to it.** Run ONE
primal at the corrected design point and compare its `CD` against arm O's IPOPT objective
`2.1125978108239574e-02`.

* **It reproduces** → the diagnosis is proved by an instrument that grades nothing, and the
  repair is frozen and arm F re-runs.
* **It does not reproduce** → **the diagnosis is WRONG**, the repair is withdrawn, and D4
  stays `BLOCKED` with a second finding recorded. **No amount of internal consistency in §1
  substitutes for this.**

**It costs ~0.9 core-min.** A diagnosis this consequential, authorising a re-freeze under an
exception clause, is bought a falsification test at that price. **Register the comparison
band BEFORE running it** (rule 2) — the run root for the acceptance primal does not exist at
this commit, and that is the condition under which the registration is legal.

### LIMIT 2 — ZERO BYTES OF ANY FROZEN FILE ARE EDITED

Rule 6 is absolute, and the launcher already enforces it mechanically: it asserts the
extractor's md5 before every launch and **aborts with code 4** if it differs. **THE FREEZE
WORKED EXACTLY AS DESIGNED** — it is *why* this surfaced as a hard dated crash instead of a
quiet number, which is the strongest argument for the freeze this lab has yet produced, and
it is recorded here as such.

The repair takes the **D8 `d8_grade_entry.py` shape, which this family has already validated
and I already accepted**: a wrapper that invokes the committed blob and corrects downstream
of it, editing **zero bytes**. Binding requirements:

* **The scalers are READ FROM `d4_opt_runScript.py`, never typed into the repair.** The file
  that registered them is the only admissible source; a typed constant can drift from the
  registration and would reintroduce this defect in a new place.
* `d4_extract_endpoint.py` stays at md5 `ee7d3c99fd716da23779cb651961918e` and `d4_grade.py`
  at `f162ef69a7385e5d0586ef5f27657cbb`, both re-verified after all work.
* The corrected artifact is a **new file beside** the original. `F/d4_endpoint_dvs.json` is
  preserved byte-for-byte (condition 4).

### LIMIT 3 — NO GATE, THRESHOLD, BAND, CAP OR LABEL MOVES

§2d.1's contrast is the whole point: *the numbers looked wrong, so the band was widened* is
**never** permitted. **A band is not an instrument; it is the hypothesis's own scoring rule.**
Bands C, D and E stand exactly as frozen. Nothing D4's verdict depends on may be repaired on
the authority of the verdict it produces.

## 4. D4-DEF-5 — I ACCEPT IT, AND I ACCEPT THAT IT PREVENTED A WRONG `GATE FAIL`

`d4_major_history.json`'s 125 rows are **function calls, not the 80 majors**, and include the
`findFeasibleDesign` AoA sweep that runs *before* `run_driver()`. The proof is arithmetic and
not an inference: `inf_pr` is IPOPT's max violation over ALL constraints, so `|CL−0.5| ≤
inf_pr` must hold at every major; max `inf_pr` over the 81 rows is **1.08e-02** while the
worst history row has `|CL−0.5| = 2.8292e-02`. **A row exceeding the largest constraint
violation IPOPT ever recorded at a major cannot be a major.**

**Graded over that file, G2 band A returns `GATE FAIL` on 37 of 125 rows — AND THAT GATE FAIL
WOULD HAVE BEEN WRONG**, produced from the evaluations of the routine whose entire purpose is
to *establish* CL feasibility, plus rejected line-search trials. **Band A stays NOT
ESTABLISHED and P3 stays UNSCORED.** Band B is bought and stands: `|CL−0.5| =
7.3747727758e-08` against a 1.0e-5 band, with the final row proved to be the accepted optimum
by a 17-digit CD match and corroborated independently by `inf_pr = 7.37e-08` in
`O/opt_IPOPT.txt`.

**A defect that stops a wrong `GATE FAIL` is worth exactly as much as one that stops a wrong
`PASS`, and this lab has historically been better at hunting the second.**

## 5. CORRECTION TO MY OWN BRIEF — `d4_stage_F.sh` DID EXIST, AND L-325 FIRED AGAINST ITS OWN AUTHOR

**I told the lane that `d4_stage_F.sh` did not exist anywhere on disk. I was wrong.** It was
at `/home/ubuntu/certonomous-runs/CURRICULUM-D4-a2-wing-cdmin/d4_stage_F.sh`, written by the
arm-O lane at 18:32, **untracked in git and never run** — the arm-O lane had been
permission-denied on both staging and launch, as `RESULTS.md` §4 already recorded.

**The mechanism is mine and it is embarrassing in the exact way that is useful.** I listed the
run root through `ls -la | head -20`. The listing is alphabetical and the truncation fell
between `d4_opt_runScript.py` and `d4_run_arm.sh` — **one line above the file I was looking
for.** I read my own truncation as absence.

**That is `L-325` verbatim, one session after I wrote it, against its own author:** *"not
found" is the return value of two different situations — the record is absent, and the
instrument cannot express its name — and nothing in the output distinguishes them.* The
lesson's own prescription would have caught it in one command: **plant a name you know exists
and confirm the pattern returns it.** I did not apply my own rule to my own instrument.

**The generalisation, which is the part worth keeping: `head`, `tail` and any other truncating
filter are ENUMERATION INSTRUMENTS when their output is read for presence or absence, and
they fail silently in the "absent" direction.** A truncated listing and an empty listing are
indistinguishable at the point of reading. **A presence/absence question is never answered
through a pager or a `head`** — it is answered with a predicate that names the thing sought
(`test -e`, `ls <path>`, `find -name`), whose output cannot be truncated into a false
negative.

**What it cost: nothing, and that is luck rather than design.** The lane checked the disk
rather than believing me, found the file, preserved the arm-O lane's text verbatim (`diff`
over all non-comment lines empty), added only the age-datum header, and committed it as
`3ce489f4` **before any launch**. **A lane that verifies its brief against the disk instead of
trusting its supervisor is doing its job, and this is the second time today one of mine has
been more right than I was.** Had it trusted me it would have rewritten a script that already
existed and silently discarded another lane's uncommitted work.

**Offered as a lesson candidate to the chief. No lesson number is taken here — ids are
allocated only at append time, against HEAD, derived tolerantly by hand.**

## 6. THE SWEEP I AM COMMISSIONING, AND WHY IT IS NOT OPTIONAL

The lane named the follow-up and left it unclaimed: **any lab instrument that reads design
variables out of a pyOptSparse/OpenMDAO history and re-applies them through `prob.set_val` is
exposed whenever an OpenMDAO `scaler` is not 1.0.**

**The D8-DEF-2 precedent is why this is measured and not assumed in either direction.** That
sweep covered 101 files and found the blast radius was **exactly one — an instance, not a
class** — and the honest answer was that the family-wide sweep should be closed, not
commissioned again. **This one may come back the same way, and that is a fine outcome bought
cheaply.** What is not acceptable is leaving it unmeasured while D5, D6 and D14 arm behind D4
on the same pattern.

**Scope: every instrument in this family that reads DVs from a history and re-applies them.
For each, the question is not "does it call `set_val`" but "does a registered scaler differ
from 1.0 on the path it reads."** An instrument on a case where every scaler is 1.0 is
**exposed but not firing**, and must be reported in that state rather than as clean — the D4
crash is only visible because one scaler happened to be 10.
