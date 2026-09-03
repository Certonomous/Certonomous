# GRADING-FIXTURE CENSUS — DOES A CONTROL'S FIXTURE COME FROM THE RUN BEING GRADED?

**Scope:** every `.py` under `/home/ubuntu/Certonomous/cases/dafoam/`.
**Question:** does a planted control's fixture derive, **in any code path**, from
the run the instrument is grading?
**Ordered by:** dafoam-supervisor, 2026-09-03, after `a1wr_read.py` was found to
carry the defect that voided MAAOA's grading (L-435) — *"two readers in my
territory with the same defect, which makes it a class and not an incident."*
**Run by:** lab-lane (dafoam), 2026-09-03.
**Repairs performed: NONE.** A repair to a grading path after first compute is a
`VERIFICATION_CHARTER` §2d/§2d.1 question and is the supervisor's ruling, item by
item. This document reports; it does not fix.

---

## 0. WHY THIS IS A DEFECT AND NOT A REFINEMENT

A planted control exists to prove a reader can see what it claims to see. If the
control's fixture **is** the artifact being graded, the control and the reading
share a failure mode: a reader blind to a feature of *that* artifact is blind to
it in both, and the control passes anyway. **The control then certifies the
reader against the one input it cannot independently check.**

The inverted reasoning is written down in the affected instruments themselves.
`so3af_read.py:441-443`, verbatim:

> *"Locate the artefacts FIRST, so the controls can be cut from the very bytes
> this reader is about to report on. A control planted into an unrelated fixture
> proves less than one planted into the real log."*

**That is exactly backwards, and it is the design intent of four instruments in
this family.** The property a control must have is *independence* from the
graded input, not *proximity* to it.

---

## 1. METHOD, AND WHY IT IS NOT `grep -r`

**`grep` on this box is ugrep. It honours ignore files and it silently missed
five of nine solver logs inside a census whose whole purpose was completeness.**
This census therefore uses **`os.walk` in Python**, reading every file's bytes
directly. No `grep -r` was run at any point.

- **468** `.py` files walked under `cases/dafoam/`.
- **105** carry both a planted-control idiom and verdict vocabulary — the
  candidate grading instruments.
- **8** match any signature by which a control base can be sourced from the
  graded run. Each of the 8 was then **read by hand at its call site**; the
  regex was used to narrow, never to conclude.
- Liveness was determined from the **grading record actually on disk**, not from
  the code's capability.

---

## 2. THE CENSUS

| # | instrument | verdict | defect **LIVE** in the grading of record? | evidence |
|---|---|---|---|---|
| 1 | `ladder-a/A1/feasibility_aoa_polar/aoa_read.py` (md5 `1ce50161…`) | **AFFECTED** | **YES — BOTH ARMS** | `aoa_read.py:398-408` sets `real_seg` from the run's own `out/sweep.log` and passes it to `selftest()`. The archived gradings say so on their face: `AOA_AOAI_read_REPAIRED_20260901T163038Z.txt` reads `born against : REAL RUN ARTEFACT`, `source : .../CURRICULUM-AOAI-.../out/sweep.log (point idx=0, alpha=0.0000)`, `sha256 of base: 77c9d0db…`; `AOA_AOAC_read_20260901T162741Z.txt` the same with `sha256 ef896eae…` |
| 2 | `ladder-a/A1/fixed_lift_mach_sweep/maaoa_read.py` (md5 `79fddadc…`) | **AFFECTED** | **YES** | `maaoa_read.py:161-167` globs the run root's `MA*` and `INCOMP` units and, on the first `out/trim.log` that parses, sets `base, note = lp.read_text(), str(lp)`. MAAOA's `INCOMP` produced a parseable trim log, so the branch was taken. This is the grading `LAB_STATE` S-28 records as **voided** |
| 3 | `ladder-a/A1/wall_resolved_aoa_polar/a1wr_read.py` (md5 `22479c89…`) | **AFFECTED** | **NO — and only by accident** | `a1wr_read.py:447-457` scans the run's own `sweep.log` for the first segment classifying `CONVERGED` **and** carrying a y+ line. **Zero points converged on either arm**, so the list was empty and the controls fell back to the static `FIXTURE`. Confirmed in the grading of record: `born against : WRITER_BUILT FIXTURE`. **Had one point converged, this grading would have carried the defect** |
| 4 | `ladder-a/A1/feasibility_SO3a_alpha/so3af_read.py` (md5 `9f42e4ef…`) | **AFFECTED — BY EXPLICIT DESIGN** | **NOT EVALUABLE** | `so3af_read.py:444-447`: `logs = find_logs(root)`, `sample = logs[0] if logs else None`, `selftest(sample)`; with a sample it prints `REAL RUN ARTEFACT -- controls are cut from its own bytes`. **But the grading of record on disk, `SO3aF_read_20260831T161116Z.txt`, carries none of that harness** — it shows a single line, `PLANTED CONTROL: reader sees CL=0.4987654 CD=0.0123456 from a synthetic log -> FIRES`, and no provenance block. **That output was produced by an EARLIER version of this reader.** The current instrument, run against that run root (3 logs present), *would* take a live sample. What the archived grading actually used cannot be certified from the current code, and re-running it was out of scope |
| 5 | `ladder-a/A1/curriculum_D19M/d19m_grade.py` | **AFFECTED — DISCLOSED BY DESIGN** | **YES** | Its own header, verbatim: *"A control prefers the REAL artefact on this run root. Where the arm did not run, the target is built by the INSTRUMENT'S OWN WRITERS … the register records which it was — `target_kind` `REAL` or `WRITER_BUILT`."* The grading of record `CURRICULUM-D19M-…/D19M_grade_20260901T083034Z.json` records **`"target_kind": "REAL"`** |
| 6 | `ladder-a/A1/curriculum_D19M/d19m_grade_selftest.py` | **AFFECTED** (same harness) | inherits #5 | same `born against` switch |
| 7 | `ladder-a/A1/curriculum_D19O/d19o_grade.py` | **AFFECTED — DISCLOSED BY DESIGN** | **YES** | identical header and mechanism; grading of record `CURRICULUM-D19O-…/D19O_grade_20260901T054304Z.json` records **`"target_kind": "REAL"`**. *(Its `PREREGISTRATION.md` names `WRITER_BUILT`, so the registration and the grading disagree about which kind was used — reported, not adjudicated)* |
| 8 | `ladder-a/A1/curriculum_D19O/d19o_grade_selftest.py` | **AFFECTED** (same harness) | inherits #7 | same `born against` switch |

### 2.1 Explicitly CLEAN, checked by hand rather than assumed

| instrument | why clean |
|---|---|
| `ladder-a/A1/feasibility_SO3a_multipoint/so3af2_read.py` | `_fixture()` writes a synthetic JSON into a tempdir from module-level constants (`ALPHAS`, `CD_REF`, `CL_REF`, `J_REF`); `selftest(tmp)` takes only a tempdir, and `--selftest` does not accept `--root` at all. **Nothing from a graded run can reach a control** |
| `curriculum_D17_cone_supersonic/d17_grade.py` | `selftest(tmp)` builds every fixture with `_fixture(tweak)` from literals into a tempdir |
| `curriculum_D18_cone_hypersonic/d18_grade.py` | same. Its comment at 707-708 — *"the gate re-reads the FLOW CONDITION from the run root at grade time, so the fixture must carry what a real run would carry"* — describes a fixture **mimicking** a real run's shape, not one **derived from** the graded run. Clean, and the distinction is the whole point of this census |
| the remaining 97 candidates | no control base reaches a run-derived path; none matched any of the four signatures on a full-bytes read |

---

## 3. WHAT THE CENSUS ESTABLISHES

1. **It is a CLASS, not an incident — six instruments, and five of them live.**
   `aoa_read.py` (both arms), `maaoa_read.py`, `d19m_grade.py` and
   `d19o_grade.py` all graded with a control fixture taken from the run under
   grade. `a1wr_read.py` carries the same code and escaped only because nothing
   converged. `so3af_read.py` carries it by explicit design.

2. **The lineage is visible and it propagated by copying.** `A1WR_PREREGISTRATION`
   §15.3 records that `a1wr_read.py` carries *"the frozen coarse reader's ELEVEN
   controls carried whole (`aoa_read.py`)"*. The defect was inherited with the
   controls, and the inheritance was registered as a **virtue** at the time.

3. **⚠ THE COARSE α-POLAR IS INSIDE THE BLAST RADIUS.** `aoa_read.py` graded
   both `CURRICULUM-AOAI` and `CURRICULUM-AOAC` — the coarse sweeps that produced
   the **"both regimes converged 0–8° and failed 9–18°, the same boundary to the
   degree across a tenfold Reynolds difference"** finding. That finding is the
   baseline the entire A1WR item exists to test, and it is quoted in
   `A1WR_PREREGISTRATION.md` §8. **This census does not overturn it and makes no
   claim about it** — it records that its grading instrument carries the defect
   that voided MAAOA, and that the question is now open and belongs to the
   supervisor.

4. **Disclosure is not immunity, and D19M/D19O are the sharp case.** Those two
   readers *say* which kind of fixture they used and record it in a machine field
   (`target_kind`). That is better practice than the readers that say nothing —
   and it did not prevent the defect; it only made it auditable after the fact.
   **A control that discloses it was born against the graded run is still a
   control born against the graded run.**

---

## 4. WHAT THIS CENSUS DOES **NOT** DO

- **It repairs nothing.** Every listed instrument is untouched.
- **It voids nothing.** Whether a live defect voids a grading is a §2d/§2d.1
  ruling, and the supervisor's other lane has just had the §2d.1 exception
  **refused** for MAAOA on three of its four conditions, on the §2d.3.3/§2d.4.1
  precedent that the absence shortcut is unavailable once a rung has produced
  numbers. That precedent is named here, not applied here.
- **It does not certify the 97.** It certifies that none of them matched any of
  four signatures on a full-bytes read of every file, and that the 8 that did
  were read by hand. A signature-based census can only report what its signatures
  can see, and that limit is stated rather than hidden.
- **It says nothing about instruments outside `cases/dafoam/`.** The same
  question is open for every other team's graders and this census does not
  answer it.

---

## 5. THE REPAIR SHAPE, REGISTERED FOR WHOEVER IS RULED TO OWN IT

Not applied anywhere by this document. Registered as `G-FIXTURE` in
`cases/dafoam/ladder-a/A1/wall_resolved_alpha_tail/PREREGISTRATION_DRAFT.md` §6,
for the successor's reader, which has produced no numbers and is therefore free
of the §2d question:

> Every control fixture is **static**, committed beside the reader, and
> **md5-pinned**. The reader **refuses at exit 2** if any fixture path resolves
> inside the run root it is grading, and asserts
> `mtime(fixture) < mtime(run root)` **by execution**. The provenance line states
> the fixture's origin and sha256 and **must be true about the disk**.

*(That last clause is owed to a second, smaller defect found in the same code
path: `a1wr_read.py` prints `source: no sweep log on disk yet` while parsing a
520,063-byte sweep log four lines later. The string is the `not is_file()`
branch's note, reused unchanged for the "log present, nothing converged" case.)*

---

## 6. SEPARATE FINDING, FOR CROSS-TEAM AUDIT — REGISTERED GATES WITH NO IMPLEMENTATION

Found while grading A1WR, and stated here so it can be cited:

- **`G-COMPLETE` is registered in `A1WR_PREREGISTRATION.md` §9** — rule 4 in all
  its clauses, *"refuse (exit 2) rather than degrade"* — and
  **`grep -c 'G-COMPLETE' a1wr_read.py` returns 0.** The gate has no code. A1WR's
  completeness gate is **unadjudicated to this day**, and its truncation (13 of
  19 declared points) is reported by the reader as a bare `COUNT MISMATCH` that
  refuses nothing.
- **`G-CAPS` is registered in the same table** and appears in `a1wr_read.py` in
  exactly **one conditional prose sentence**, computing no arithmetic. A1WR's cap
  accounting was done by hand at grade time and is labelled in
  `A1WR_STAGE12_RESULTS.md` §6 as **not coming from the grading path**.
- Alongside **MAAOA §4's assertion of a pre-compute selftest pass that has no
  artifact dated before compute**, that is **two registered checks in one family
  that exist only as text.**

**The general question — how many registered gates lab-wide have no
implementation — is referred upward by the dafoam supervisor and is not answered
here.** This section exists so a cross-team audit can cite the three instances by
file, gate name and the command that demonstrates the absence.

---

**Nothing in this document is filed, sent, uploaded or posted anywhere.**

---
---

# CORRECTION 1 — 2026-09-03 — §6 IS WITHDRAWN. IT WAS A FALSE ACCUSATION.

**`lines whose number changed above this section: 0`**

Nothing above is edited. This section withdraws part of §6 of this same
document, written by this lane earlier today.

## 7. WHAT §6 CLAIMED, AND WHY IT WAS WRONG

§6 recorded that A1WR registers `G-COMPLETE` and `G-CAPS` and never implemented
them, on the evidence that `grep -c 'G-COMPLETE' a1wr_read.py` returns **0**.
**Both claims are withdrawn in full.**

The standard is verification's §2v ruling, which landed while this census was
being written and which refused a specimen of exactly this shape:

> *"a gate is implemented where it must be, not where the reader is — the
> grading path is every frozen instrument the registration names, not the one
> file with `analyse_` in its name."*

**This census applied the wrong test.** It looked in the one file with the
grading harness, found nothing, and inferred absence. **Absence from one
instrument is not absence from the grading path.** In the same referred class
**five of nine flags were false accusations**; this was two more of them, and
they were this lane's.

## 8. WHAT THE §2v TEST ACTUALLY RETURNS — EVERY FROZEN INSTRUMENT, WITH THE LINE

A1WR's registration names its instruments at §15.3 and §11. Checked, all of them:

| gate | implemented at | the line, quoted |
|---|---|---|
| `G-COMPLETE` | `a1wr_runScript_incomp.py:357-362` | `AOA_SWEEP_END n_declared=%d n_executed=%d` then, on mismatch, `AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion` and **`exit(97)`** |
| `G-COMPLETE` | `a1wr_cmd.sh:68-71` | `EXEC="$(grep -c '^AOA_POINT_END ' …)"` → `A1WR_COUNTS declared=$DECLARED point_end_markers=$EXEC converged_lines=$CONV walltreat_lines=$BCOK`; the PROBE branch prints `A1WR_PROBE_NO_ENDTIME_STATE … y+ NOT MEASURED` and **`exit 97`** |
| `G-CAPS` | `a1wr_chain_driver.sh:251-257` | `CAN_DUP="$(python3 -c "print('YES' if $I_SPEND + 55.0 <= $ARM_CAP_MIN else 'NO')")"`, else `A1WR_DUP_CAPSTOP: I-arm spend $I_SPEND + 55 would exceed the $ARM_CAP_MIN cap … A cap-stop is NOT A RESULT on that control.` |

**Both gates are implemented, in frozen instruments the registration names, with
the correct verdict vocabulary.**

## 9. LIVE OR MERELY REACHABLE — THE ANSWER THE FIRST VERSION NEVER ASKED

**`G-COMPLETE` fired LIVE.** All six A1WR cold controls carry
`A1WR_TRUNCATED declared=1 executed=0 -- NOT a completion` in their docker logs
and **exited 97** on it. That is the gate doing its job, on the record, in the
grading of record.

**It did not fire for the two sweeps — and that is not a missing gate.** The
02:25:05Z SIGTERM killed both containers before the unit-end block ran:
`logs/sweep_I.docker.log` and `logs/sweep_C.docker.log` **do not exist**, and
`AOA_SWEEP_END` appears **0 times** in either sweep log. **A gate whose host
process was killed is not an unimplemented gate**, and conflating the two is
exactly how this false accusation was made.

## 10. WHAT SURVIVES, STATED NARROWLY

`a1wr_read.py` does not itself name or adjudicate `G-COMPLETE` or `G-CAPS`; it
prints a bare `COUNT MISMATCH` and returns 0, and its cap line is prose. **That
is an observation about one instrument's division of labour, and under §2v it is
reported CLEAN — not as a suspicion.** A reader is entitled to leave a gate to
the producer and the driver; what it may not do is claim to have adjudicated one.

The one operational consequence worth keeping, stripped of the accusation: **the
A1WR sweeps' completeness was never adjudicated by anything, because the process
that would have adjudicated it was killed.** That is an infrastructure fact about
one run, already recorded in `A1WR_STAGE12_RESULTS.md` §1, and it is not a defect
in any instrument.

## 11. THE MAAOA ITEM IN §6 IS NOT WITHDRAWN AND IS NOT RE-ASSERTED EITHER

§6's third row — MAAOA §4's assertion of a pre-compute selftest pass with no
artifact dated before compute — **was not measured by this lane.** It was
relayed. Under the standard applied here it is therefore **NOT-EVALUABLE by this
census**, and it is downgraded to that rather than left standing as a finding
this document did not earn.

## 12. WHAT THIS CORRECTION DOES NOT TOUCH

**§1–§5 stand unchanged.** The fixture-defect census — six instruments AFFECTED,
five live, three CLEAN — was built by reading every candidate's call site by
hand, and its liveness column was decided from the grading record on disk, which
is the §2v standard. **`aoa_read.py`'s two archived gradings still say
`born against : REAL RUN ARTEFACT` on their own face**, and `d19m`/`d19o` still
record `"target_kind": "REAL"`. Those are quotations from artifacts, not
inferences from an absence, and nothing here weakens them.

**The difference between §1–§5 and the withdrawn §6 is the difference this
correction exists to mark: a finding read off an artifact, versus a finding
inferred from not finding something in one file.**
