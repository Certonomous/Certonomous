# RC1 — THE BIRTH-REQUIREMENT CONTROL FOR EVERY CLOSURE LOG READER

> **THIS COMMIT IS NOT THE FREEZE.** This document is landed to preserve it and
> to make it reviewable; it is **NOT YET FROZEN** and **NOTHING MAY RUN AGAINST
> IT**. Standing rule 2 fixes the grading path **at the pre-registration
> commit**, and this item's instrument does not exist yet — so the freeze is the
> later commit that carries **this document AND its instrument together**, and
> that commit's sha is the one an entry's `prereg_commit` must cite. Any run
> before it is unregistered and its output is **NOT A RESULT**.
> — closure-supervisor, 2026-08-28


**Rung:** `RC1_birth_requirement_control`
**Team:** closure
**Class:** REPAIR-REGISTRATION (Sanaa's FREEZE-AHEAD amendment, 2026-08-28)
**Status:** `prereg_commit: PENDING_SUPERVISOR_FREEZE`. The gates, thresholds,
cap and label below are drafted and are **not yet closed**; the freeze is the
supervisor's act, performed personally under `SUPERVISION_CHARTER.md` §3 check 4,
and it is a commit whose message carries the sha256 of this document and of the
instrument. **Nothing has been staged into the run root, no queue entry has been
filed, and no compute has been spent.** Standing rule 2 closes these gates at the
freeze; before it, amendments are legal and must state the condition and how it
was checked.
**Drafted:** 2026-08-28, by a closure lane on the closure supervisor's dispatch.

**Why this item exists at all.** Sanaa amended FREEZE-AHEAD on 2026-08-28
(`etc/sessions/2026-08-28T1701Z_sanaa_directives_control_regrade_freezeahead.md`):

> Freeze-ahead counts repair-registrations; a team blocked on findings freezes the
> repairs and runs them — queue depth 0 with open findings is impossible by
> definition.

and, in the same message, canonized the **birth requirement**:

> rule 3's question — *"was this reader ever shown able to see a non-zero through
> the real code path?"* — is now the **birth requirement** for every
> reader/comparator: **no instrument grades anything until that answer is yes,
> demonstrated.**

> A control defined in terms of the thing it controls is not a control. A planted
> control must travel the real production path — written by the real producer's
> code, read through the real reader — and prove the instrument sees a non-zero
> the same way reality would deliver one. A control that empties the tuple it
> tests, or **writes a schema the producer never emits**, tests nothing and
> certifies blindness.

Closure has an open finding — **D548**, the unanchored `Floating point exception`
clause — and it already cost `G1_grid_triple` its verdict on a completed 127.08
core-minute run. RC1 turns the birth requirement from a claim made once, by hand,
for two comparators into a **standing, re-runnable gate over every closure log
reader**.

---

## 1. The question, and what it does not claim

**Question.** For every closure reader whose output feeds a graded verdict from an
OpenFOAM log, has that reader been **shown, on real solver-produced artifacts,
through its own unmodified code path**, to return **both** of the values its
channel can take — and, for a fatal/divergence channel, to return NOT-fatal on a
log whose only match is OpenFOAM's own healthy-start banner?

### 1.1 What RC1 does NOT claim

* **It grades no physics.** No functional, no order, no GCI, no Roache triple, no
  reference field. RC1 produces exactly one class of verdict, about instruments.
* **It is not a correctness proof of any reader.** A corpus demonstration proves
  a reader sees the non-zeros **this corpus happens to contain** (§10 item 1).
* **It is not a repair.** RC1 **edits no comparator**, frozen or otherwise. It
  imports each reader and calls it. Every repair it motivates is a separate,
  separately pre-registered successor.
* **It does not cover field readers.** RC1's channel is the **log** channel only;
  §10 item 4 names the field-derived readers it leaves untouched and why.

### 1.2 Its relation to the two hand demonstrations already on record

The closure supervisor discharged the birth requirement by hand on 2026-08-28 for
`grade_g2.py` and `grade_g1b.py`, recorded at
`cases/RANS_LES_closure_models/G2_grid_triple_duct/BIRTH_REQUIREMENT_CONFIRMATION.md`
with the driver at `.../G2_grid_triple_duct/artefacts/birth_requirement_demo.py`.
**That work is the evidence RC1 builds on, and this lane verified two of its
load-bearing claims rather than re-deriving them** (§2.4). The driver is a
throwaway: it is unfrozen, has **no controls of its own**, and **no gate** — it
prints counts and returns 0 whatever they are. RC1 is the gated instrument the
demonstration was a sketch for.

**One thing the hand demonstration cannot support, measured here and registered
as the reason RC1 fixes its corpus by rule:** its result files report **1,200 real
solver-produced logs** (`artefacts/g2_birth_requirement_2026-08-28.txt`, and
1,200 = 33 + 721 + 446 in the G1b file), but **the enumerated list of those 1,200
paths was not preserved** — the driver takes the list as `sys.argv[2]` and no such
manifest exists under either `artefacts/` directory. This lane could not reproduce
1,200 from any enumeration rule it tried over the three run roots: the natural
candidates measure **762 / 2,244 / 2,365 / 2,745 / 4,072 / 5,638 / 6,536**
(§2.1). The counts are internally consistent and both spot-checked artifacts
verify exactly (§2.4); what is missing is **reproducibility**, and the cause is
standing rule 13 — a list that lived only in the scratchpad is not a handoff
channel. **RC1 therefore registers its corpus as a deterministic enumeration rule
and writes the enumerated manifest to disk as a first-class artifact** (§2.2,
§6.1).

---

## 2. Substrate — the corpus, and every number here was measured on this box

### 2.1 The candidate survey

Three run roots hold this box's OpenFOAM output:
`/home/ubuntu/closure-data`, `/home/ubuntu/certonomous-runs`, and
`/home/ubuntu/Certonomous/verification/runs`.

| enumeration rule | files |
|---|---|
| name matches `log.*` or `*.log` | **6,536** |
| of those, first 16 KiB contains `Create time` (i.e. an OpenFOAM application wrote it) | **5,638** |
| of those, contains a `Time = ` block (a solve, not a utility) | **4,072** |
| of those, contains the `trapFpe` banner anywhere | 5,264 (of the 6,536 name-matched) |
| basename `log.run` / `log.solve` / `log.frozen` / `log.simpleFoam` / `log.calib` | 73 / 384 / 68 / 305 / 1 |
| `log.run`, `log.simpleFoam` or `log.solve` only | 762 |
| `log.*` excluding mesh/utility basenames | 2,244 |
| all `log*` under `closure-data` + `certonomous-runs` | 2,745 |
| `Create time` under `closure-data` + `certonomous-runs` only | 2,365 |

**None of these is 1,200**, which is why §1.2 records the corpus as
non-reproducible and why the rule below is registered rather than inherited.

### 2.2 THE REGISTERED CORPUS, fixed here and re-derived by the instrument

    ROOTS = ( /home/ubuntu/closure-data,
              /home/ubuntu/certonomous-runs,
              /home/ubuntu/Certonomous/verification/runs )

    CORPUS  = every regular file under ROOTS whose basename starts with "log."
              or ends with ".log", whose FIRST 16384 BYTES contain the literal
              "Create time", excluding symlinks and files of zero length.

    CORPUS_A = the subset whose first 2,000,000 bytes contain "\nTime = "  (a solve)
    CORPUS_B = CORPUS minus CORPUS_A                                       (a utility)

**Measured 2026-08-28 on this box:**

| set | files | bytes | largest single file |
|---|---|---|---|
| `CORPUS` | **5,638** | **12.391 GiB** | 504.1 MiB |
| `CORPUS_A` | **4,072** | **12.340 GiB** | |
| `CORPUS_B` | **1,566** | **0.053 GiB** | |

**The corpus is a moving target and the registration says so.** Peers write logs
continuously; the counts above will not be the counts at run time. RC1 therefore
registers the **rule**, not the numbers, and **writes `CORPUS_MANIFEST.json`** —
every path with its size and `mtime_ns`, plus the sha256 of that JSON — into the
run root before any reader is called. The gate arithmetic in §5 is defined
entirely on ratios and existence, never on an absolute count, so a corpus that
has grown between freeze and run cannot move a verdict. **A run whose manifest is
absent is `NOT A RESULT`.**

### 2.3 Producer-matched corpora, because "written by the real producer's code" is the rule

Sanaa's clause is that the control must travel *the real production path*. A
reader that opens `log.frozen` has never been shown anything by a corpus of
`log.simpleFoam` files. Each subject in §3 is therefore run over the corpus its
**own producer** emits:

| producer corpus | rule | files | bytes |
|---|---|---|---|
| `SOLVER` | `CORPUS` (any OpenFOAM application) | 5,638 | 12.391 GiB |
| `RUNLOG` | basename `log.run` | 73 | 0.81 GiB |
| `SOLVELOG` | basename `log.solve` | 384 | 6.56 GiB |
| `FROZENLOG` | basename `log.frozen` | 68 | 0.04 GiB |

**Every one is non-empty**, measured. Had any been empty, the registered outcome
for its subject would be `BLOCKED` — the birth requirement cannot be discharged
without artifacts — and never `PASS`.

### 2.4 The two ground-truth claims this lane VERIFIED rather than re-derived

The supervisor's record makes two checkable claims. Both were re-executed here
through `grade_g2.py`'s own `parse_log`, imported unmodified:

| artifact | claim on the record | measured here |
|---|---|---|
| `certonomous-runs/S1-cbfs-inversion/log.calib` | a three-invocation driver log — 3 `Create time` banners, 2 `End` lines — whose first run died; a genuine fatal that legitimately carries an `End` | `fatal=True`, `end=True`, `Create time` ×**3**, `End` lines ×**2**, first signature `--> FOAM FATAL ERROR`. **CONFIRMED exactly.** |
| `verification/runs/DPW8_V2_runs/run_L4_diagA_relax/log.simpleFoam` | last `Time` is 182, no `End`; cfd's committed `C-4` independently records SIGFPE at iteration 182 of 600 | `fatal=True`, `end=False`, last `Time = 182`, first signature `Foam::sigFpe::sigHandler`. **CONFIRMED exactly.** The cited cfd record exists at `verification/campaign/DPW8_V2_L4_DIVERGENCE_DIAG_RESULTS.md`. |

**That is a different team's committed verdict agreeing with this reader's
non-zero, and nothing in closure's registration could have shaped it.** It is the
strongest single piece of evidence on the record for the positive direction, and
it is reproduced here rather than relayed.

---

## 3. The subjects — every closure log reader on disk, enumerated by measurement

**How they were found, so the list can be audited rather than trusted.** An AST
walk over **all 71 `.py` files** under `cases/RANS_LES_closure_models/` selected
every module containing any of `fatal`, `diverg`, `FOAM FATAL`, `Floating point`,
`sigFpe`, `printStack`, `Segmentation`, `log.run` or `parse_log`, then every
function in those modules whose own source segment carries a crash/convergence
token. Twenty modules matched; ten hold a reader that produces a value feeding a
graded verdict. The other ten are drivers, probes or one-line mentions and are
named in §3.2.

### 3.1 The registered channel table

A **channel** is `(module, reader function, output key, non-zero definition,
class)`. RC1 grades channels, not files.

| # | module (sha256 at drafting, first 16) | reader | channel key | class | producer corpus | signature the instrument calls |
|---|---|---|---|---|---|---|
| **C1** | `G1_grid_triple/grade_g1.py` `253d594252a20e53` | `parse_log` :242 | `fatal` (clause :250) | FATAL | `SOLVER` | `f(path)` |
| **C2** | `G1b_grid_triple_regrade/grade_g1b.py` `614e52064b8ade5d` | `parse_log` :310 | `fatal` (`RE_FATAL` :299) | FATAL | `SOLVER` | `f(path)` |
| **C3** | `G2_grid_triple_duct/grade_g2.py` `6839aad1d91db7c2` | `parse_log` :355 | `fatal` (`FATAL_RE` :129) | FATAL | `SOLVER` | `f(path)` |
| **C4** | `Kaandorp2020_TBRF/aposteriori/run_lane.py` `454e37f426296581` | `parse_log` :165 | `diverged` (clause :175) | FATAL | `RUNLOG` | `f(case_dir)` |
| **C5** | `Kaandorp2020_TBRF/aposteriori/summarise.py` `5a28f6a36bd12912` | `state` :22 | `crashed` → `DIVERGED` (clause :31) | FATAL | `RUNLOG` | `f(case_dir, t0)` |
| **C6** | `NASA_hump_gate/run_gate.py` `d6627afcd93e61cc` | `state_of` :106 | `"DIVERGED-or-FAILED"` (clause :108) | FATAL | `RUNLOG` | `f(case_dir)` |
| **C7** | `R4_sparta_build/score_aposteriori.py` `6dc3cce2ce00f7d3` | `log_facts` :55 | `diverged` (:76), `floating_point_exception` (:70) | FATAL | `SOLVER` | `f(case_dir)` |
| **C8** | `M1_multimodel_sweep/grade_m1.py` `b3decc88aca147c9` | `parse_log` :228 | `end_line`, `exec_count`, `last_time`, `model_from_log` | COMPLETION | `RUNLOG` | `f(path)` |
| **C9** | `R5C_omega_repair/grade_r5c.py` `58eb99e389af41eb` | `log_facts` :137 | `not_converged`, `bound_events`, `converged_at` | COMPLETION | `FROZENLOG` | `f(case_dir)` |
| **C10** | `M2_kepsilon_family/grade_m2.py` `fe4baa85ae4d588f` | *(none separable)* | `infra['End_line']` :142, `phys['P7_ExecutionTime']` :151 | COMPLETION | `SOLVELOG` | **inline in `gate_c_completion` :129** |

### 3.2 What is NOT a subject, and why — named so the omissions are auditable

* `G1_grid_triple/artefacts/p3_completion_probe.py`, `p3_fatal_clause_control.py`,
  `G2_grid_triple_duct/artefacts/birth_requirement_demo.py` — **probes and
  throwaways**; they grade nothing and are not on any grading path.
* `Kaandorp2020_TBRF/aposteriori/frozen_R.py`, `_common/uq_eigenspace/run_resolves.py`
  — the token `parse_log` appears only as a call or a mention; neither defines a
  log reader.
* `M1_multimodel_sweep/stage_m1.py`, `R4_sparta_build/build_aposteriori.py`,
  `_common/make_baselines_md.py`, `R5C_omega_repair/build_r5c_cases.py` —
  **builders and renderers**; the token appears in prose, a status string or a
  staged dictionary, never in a graded read.
* `Xiao2016_EnKF/tau_forward.py` — names a log path, parses none.
* **`grade_m1.py:957 `parse_log_from_text``** is a text-taking sibling of C8 and is
  **not separately registered**: C8's channel keys are the same and RC1 exercises
  the path-taking production entry point, which is what the comparator calls.

### 3.3 C10 is registered as UNREACHABLE, and that is a finding, not an omission

`grade_m2.py` has **no separable log reader**. Its `End_line` and
`P7_ExecutionTime` channels are computed inline inside `gate_c_completion`, which
also calls `read_status`, `time_dirs` and the field readers — so exercising them
over a corpus of bare logs would require RC1 to **reimplement** the clause, which
is precisely the shape Sanaa's directive forbids ("a control defined in terms of
the thing it controls"). RC1 therefore records C10 as **`BLOCKED — no separable
reader`** and **does not grade it**.

**And a second fact about `grade_m2.py` is recorded here because it is worse than
the one RC1 can test: it has no fatal or crash channel at all.** No `FOAM FATAL`,
no `sigFpe`, no signal test appears anywhere in its 758 lines. A solver that dies
mid-run is visible to it only through `rc` — which its own comment classes as
INFRASTRUCTURE that "can never void intact physics fields" — and through the
absent `End` line, also in `infra`. **A crashed solve can therefore reach a
physics gate in `grade_m2.py` with no fatal clause standing in the way.** This is
referred to the closure supervisor as a finding; it is outside RC1's cap and RC1
neither repairs it nor claims to have measured its consequence.

---

## 4. What is measured, per channel

For each channel `C`, over its producer corpus, through its own unmodified
reader called via the adapter of §6.2:

| symbol | meaning |
|---|---|
| `n_read` | logs the reader accepted |
| `n_refused` | logs on which the reader raised or exited (a refusal is a reading, recorded, never an error) |
| `n_pos` | logs returning the channel's **non-zero** |
| `n_neg` | logs returning the channel's **zero** |
| `sig_counts` | for FATAL-class channels, the distinct matched signature text and its count |
| `n_pos_no_end` | of the positives, how many lack a clean `^End$` — independent corroboration that they really died |
| `n_neg_banner` | of the negatives, how many carry the `trapFpe` banner |
| `n_neg_banner_end` | of those, how many also carry a clean `End` |
| `n_banner_only_pos` | logs whose **only** fatal-signature match is the `trapFpe` banner and which nonetheless read **positive** — the D548 defect, counted directly |

`n_banner_only_pos` is computed by an **independent** reference channel, not by
the subject: a log is *banner-only* if the literal
`trapFpe: Floating point exception trapping enabled` occurs in it and **none** of
`--> FOAM FATAL`, `FOAM exiting`, `Foam::sig`, `Foam::error::printStack`,
`^Floating point exception`, `^Segmentation fault` occurs. That definition is
frozen here, in this document, before any subject is run.

---

## 5. Gate, threshold, cap and label

### 5.1 The three birth clauses

For every channel that is not `BLOCKED`:

| clause | applies to | condition | failure means |
|---|---|---|---|
| **B1 — POSITIVE DIRECTION** | all | `n_pos >= 1` | **the channel has never been shown able to see a non-zero through the real code path.** |
| **B2 — NEGATIVE DIRECTION** | all | `n_neg >= 1` | the channel is a **constant**, not a detector. |
| **B3 — DISCRIMINATION** | FATAL class only | `n_banner_only_pos == 0` | the channel reads OpenFOAM's own **safety notice** as a failure — D548 exactly. |

**B2 and B3 are registered deliberately, and the reason is that the defect that
actually cost this lab a verdict was in the direction the brief did not ask
for.** `grade_g1.py`'s clause returns **both** values on real data — it fired on
63 of 70 logs and stayed silent on 7 — so a control that asked only "has it ever
returned a non-zero?" would have **passed the very reader that voided G1's
127.08 core-minute run**. B1 alone is not sufficient, and RC1 says so before it is
run rather than after.

### 5.2 Verdict mapping — the vocabulary is fixed

| condition | channel verdict |
|---|---|
| B1, B2 and (if FATAL) B3 all hold | **`PASS`** |
| any applicable clause fails, corpus non-empty | **`GATE FAIL`** |
| producer corpus empty, or the manifest absent | **`NOT A RESULT`** |
| no separable reader (C10) | **`BLOCKED`** |

**RUNG HEADLINE.** RC1's headline verdict is **`PASS` iff every non-`BLOCKED`
channel is `PASS`**, and **`GATE FAIL` if any channel is `GATE FAIL`**. A
`BLOCKED` channel does not turn the headline into a PASS and does not turn it
into a FAIL; it is carried, named, beside the headline. If any channel is
`NOT A RESULT`, the headline is `NOT A RESULT` under standing rule 5's ordering:
an unmeasured channel outranks a measured one.

The vocabulary is `PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING`, and the instrument passes every verdict through a checker that
**refuses** on a synonym, a hedge or a lower-case variant before it is printed.

### 5.3 THE CONSEQUENCE CLAUSE — what a GATE FAIL obliges, stated before any value exists

> **A comparator channel that fails B1 has never been shown able to see a non-zero
> through its own real code path. It MAY NOT GRADE. Any verdict standing on it is
> `NOT A RESULT` until the channel passes RC1 or is superseded by a reader that
> does.**
>
> A channel that fails **B2** or **B3** is a **constant or a mis-detector**. It
> may not grade either, and — because its defect direction is a **false
> positive** — every verdict it produced must be **re-graded from preserved
> artifacts through a repaired successor**, not merely re-labelled.

This is registered now, before RC1 runs, precisely so that the obligation cannot
be negotiated after the answer is seen. It is the same principle as the anti-gaming
register read in its second direction.

**What RC1 does NOT do with that consequence.** RC1 **executes no re-grade, edits
no comparator and moves no verdict.** It names the channels and their status. Each
repair and each re-grade is a **separate, separately pre-registered successor**;
RC2, registered the same day, is the first of them.

### 5.4 The registered falsifier (`CLOSURE_MODELLING_CHARTER.md` §12)

RC1 is falsified as an instrument if its own planted controls (§6.3) do not fire —
that is, if the harness reports `PASS` for a stuck-False, a stuck-True or a
banner-blind plant. In that case RC1 **refuses (`sys.exit(2)`)** and produces **no
channel verdicts at all**, because a harness that only ever reports PASS certifies
nothing.

### 5.5 THE REGISTERED EXPECTATION, on record before the run

Stated so that a matching outcome is a confirmation and a mismatch is a finding:

| channel | expected | why |
|---|---|---|
| C1 `grade_g1.py` | **`GATE FAIL` on B3** | the clause is unanchored; D548 measured it firing on 63 of 70 logs, 59 of them banner-only. |
| C2 `grade_g1b.py` | `PASS` | repaired successor; the hand demonstration measured 33 positives and 721 negatives. |
| C3 `grade_g2.py` | `PASS` | repaired pre-compute; 35 positives, 1,165 negatives, 1,036 banner-carrying negatives. |
| C4 `run_lane.py` | **`GATE FAIL` on B2 and B3** | RC2 §3 measures `diverged=True` on **16 of 16** rows; a constant. |
| C5 `summarise.py` | `PASS` | its comment documents the trap and its clause avoids it. |
| C6 `run_gate.py` | **at risk on B1** | it has **no FPE channel at all** — only `"FOAM FATAL" in txt`. A SIGFPE death is invisible to it. Whether it has ever seen a `FOAM FATAL` on `log.run` artifacts is exactly what RC1 measures. |
| C7 `score_aposteriori.py` | `PASS` | uses `Foam::sigFpe::sigHandler`, the narrow correct form, with a five-line comment on the trap. |
| C8 `grade_m1.py` | `PASS` on `end_line`; B1/B2 **at risk** on `model_from_log` | most logs will carry a model line; whether any lacks one is measured. |
| C9 `grade_r5c.py` | unpredicted | `log.frozen` is a bespoke driver log; whether 68 of them contain both a `NOT CONVERGED` and a converged case is unknown to this lane. |
| C10 `grade_m2.py` | `BLOCKED` | no separable reader (§3.3). |

**These are predictions, not gates.** No threshold above moves if a prediction is
wrong; the prediction exists so that being wrong is visible.

---

## 6. Controls. Each is a standing rule, not a nicety

### 6.1 THE CORPUS MANIFEST CONTROL

Before any reader is called, the instrument enumerates the corpus by §2.2's rule
and writes `CORPUS_MANIFEST.json` (path, size, `mtime_ns` for every file; the
counts; the sha256 of the JSON body) into the run root. It **refuses
(`sys.exit(2)`)** if the manifest is empty, if any producer corpus is empty, or if
the manifest cannot be re-read from disk and re-parsed to the identical structure.
**Every number in the report cites this manifest.** This is the clause that
answers §1.2: RC1's corpus is reproducible or RC1 does not run.

### 6.2 THE ADAPTER, and why it does not violate "unmodified"

Three signatures exist among the subjects: `f(path)`, `f(case_dir)` and
`f(case_dir, t0)`. RC1 **never edits a reader and never copies its expression.**
For a `case_dir` reader it builds a `tempfile.TemporaryDirectory()` containing a
**symlink** named exactly what that reader opens (`log.run`, `log.frozen`, …)
pointing at the **real corpus file**, and calls the real function on that
directory. The bytes the reader is handed are the producer's own bytes, unmodified
and uncopied; only the directory around them is synthetic.

**The honest limit of the adapter, registered rather than discovered later.** A
`case_dir` reader that also inspects time directories or fields (C5 `summarise.state`
reads `U` at two checkpoints; C7 `score_aposteriori.log_facts` lists `log.*`) sees
an otherwise-empty directory. **RC1 grades only the LOG-DERIVED half of such a
channel** and says so in the report, per channel. The field-derived half is out of
scope (§10 item 4). RC1 **refuses** if a reader raises on the adapter directory in
a way that prevents the log channel being read at all, and records that refusal as
`NOT A RESULT` for the channel — never as a `PASS`.

### 6.3 RC1'S OWN PLANTED CONTROLS — the hazard clause, because RC1 is itself an instrument

**A harness that only ever reports PASS certifies nothing.** Four comparator-shaped
plants are graded through **the same corpus, the same adapter and the same §5 gate
arithmetic** as the real subjects — not through a side path, not on fixtures:

| plant | shape | REQUIRED RC1 outcome |
|---|---|---|
| `PLANT_STUCK_FALSE` | a reader with the real signature returning the channel's zero on every input | **`GATE FAIL` on B1** |
| `PLANT_STUCK_TRUE` | returns the non-zero on every input | **`GATE FAIL` on B2** *and* **B3** |
| `PLANT_BANNER_BLIND` | the **superseded expression verbatim** — `FOAM FATAL\|Floating point exception\|signal \(` — the actual historical defect | **`GATE FAIL` on B3** |
| `PLANT_HEALTHY` | the repaired five-channel `FATAL_RE`, as a positive control on the harness | **`PASS`** |

If **any** plant's outcome differs from the required one, RC1 **refuses
(`sys.exit(2)`) and prints no channel verdict**. `PLANT_HEALTHY` is not decoration:
a harness that fails everything is as useless as one that passes everything, and
without it a universal-refusal bug would look like a thorough audit.

**`PLANT_BANNER_BLIND` is the sharpest of the four and its ground truth is on the
committed record**: that exact expression is what `grade_g1.py:250` holds, and
`1bd6d750` records the `NOT A RESULT` it produced. RC1 is therefore shown firing on
**precisely the defect it was written for**, on real artifacts, not on a fixture.

### 6.4 THE INDEPENDENT-REFERENCE CONTROL

`n_banner_only_pos` (§4) is computed by a reference definition frozen in **this
document**, evaluated **independently of every subject**. A subject cannot pass B3
by agreeing with itself. The reference channel is itself exercised in both
directions on the corpus — it must return "banner-only" on at least one real log
and "not banner-only" on at least one real log, or RC1 **refuses**.

### 6.5 L-332 — no refusal may be an `assert`

`python3 -O` deletes every `assert`. **Every refusal in the instrument is a
`raise` or a `sys.exit(2)`**, and the instrument parses **its own AST** and refuses
if a single `ast.Assert` node exists — with the counter first shown able to count a
**planted** assert, so its zero is a reading and not a blind spot. `--selftest`
must exit 0 under both `python3` and `python3 -O`, with `__pycache__` cleared
before each run (the stale-bytecode inversion is a standing lesson).

### 6.6 L-342 — physics against infrastructure

RC1 grades instruments, so its split is: a channel's **verdict** is physics; the
wall-clock, MaxRSS and manifest-write timings are infrastructure. A lost timing
record is an `INFRASTRUCTURE DEFECT`, printed and carried, and **voids no channel
verdict**.

### 6.7 READ-ONLY, and the running-solver guard

RC1 **opens every corpus file read-only and writes nothing outside its run root.**
Before it starts it asserts that its run root is empty (the age guard of standing
rule 4, applied to a non-solver item) and **refuses** if it is not. It launches no
solver, no `mpirun`, no OpenFOAM binary of any kind.

---

## 7. Cost. Measured basis, and the box cannot read its own billing

**Rates, MEASURED on this box on 2026-08-28, not assumed:**

| reader shape | measurement | rate |
|---|---|---|
| whole-text regex (C1, C2, C3, C5, C6, C7, C9) | 400-file seed-7 sample of `CORPUS`: 17.95 s over 0.815 GiB, two regex searches plus a substring count per file | **46.5 MiB/s** |
| Python line loop (C4, C8) | 60-file seed-11 sample of `CORPUS_A` through `grade_m1.parse_log` itself: 12.53 s over 0.133 GiB | **10.9 MiB/s** |

The line-loop rate is **4.3× slower** and is measured through a real subject's own
code, so it is not an allowance.

| item | corpus | GiB read | rate | wall s |
|---|---|---|---|---|
| C1, C2, C3 | `SOLVER` ×3 | 37.17 | 46.5 | 819 |
| C7 | `SOLVER` | 12.39 | 46.5 | 273 |
| C5, C6 | `RUNLOG` ×2 | 1.62 | 46.5 | 36 |
| C9 | `FROZENLOG` | 0.04 | 46.5 | 1 |
| C4, C8 | `RUNLOG` ×2 | 1.62 | 10.9 | 152 |
| reference channel (§6.4) | `SOLVER` | 12.39 | 46.5 | 273 |
| four plants (§6.3) | plant corpus | 3.2 | 46.5 | 71 |
| manifest enumeration + `stat` + JSON + sha256 of the JSON | | | | 20 |
| interpreter startup, report assembly, selftest ×2 | | | | 60 |
| **solver compute** | | | | **0 — RC1 launches no solver** |

**Plant corpus, registered:** the union of (every corpus file on which **any**
FATAL-class subject returned a positive) and (a **seed-7** random sample of **400**
files from the remainder). This keeps the plants on the real production path — real
producer bytes, real adapter, real gate arithmetic — while bounding four extra
full-corpus passes that would otherwise double the item.

    total wall ≈ 1,705 s at ranks = 1  ->  28.4 core-min

**REGISTERED ESTIMATE: 30.0 core-minutes.**
Derived: 0.500 core-h × $0.0513/core-h = **$0.026 — derived at the owner-stated
rate, reported-by-owner, NOT MEASURED** (`COMPUTE_BUDGET_CHARTER.md` §5: this box
cannot read its own billing).

**REGISTERED CAP: 75.0 core-minutes**, enforced as a wall-clock `timeout 4500`
around the instrument **and** a cumulative watch that refuses to begin a channel
whose projected read would breach the cap.
Derived: 1.250 core-h × $0.0513 = **$0.064 — derived, NOT MEASURED.**

**The cap's 2.5× ratio to the estimate is justified rather than rounded.** Two
named risks drive it: (a) the corpus **grows** between freeze and run — it grew
while this document was drafted — and the estimate is a snapshot; (b) the measured
46.5 MiB/s was taken under whatever contention the box carried at 2026-08-28, with
G2 mid-compute, and 12.4 GiB does not fit the ~15.9 GiB of available RAM alongside
a running solver, so **no warm-cache speedup is assumed and a cold-cache slowdown
is possible.** **An overrun stops the run; it does not get a new budget**
(standing rule 12).

Both figures are far under $25 and so sit inside the 2026-08-21 blanket. **A
blanket is not a per-item read** (standing rule 9); the cost is registered here
regardless.

**Estimate-versus-actual calibration is owed at completion** (standing rule 12):
the instrument records wall seconds and bytes read per channel, and the comparison
— ratio actual/predicted, gap attributed to contention, waste or misprediction,
waste named separately and never absorbed into the ratio — lands as a row in
`docs/COST_CALIBRATION.md`. **A completion report without it is incomplete.**

---

## 8. `memory_floor_gb` — an allowance, and it says so

RC1 holds **one log's text at a time**. The registered ceiling is therefore the
largest corpus file, **measured at 504.1 MiB**, plus the manifest (5,638 entries,
under 2 MiB of JSON) plus the interpreter.

**Registered: `memory_floor_gb = 2.0`, an ALLOWANCE**, roughly 3.5× the largest
single-file read — explicitly **not a measurement**, because this lane did not run
the instrument. The instrument wraps itself in `/usr/bin/time -v` and records
MaxRSS, converting this allowance into a reading for the next pre-registration.
Its absence is an INFRASTRUCTURE defect, not a channel refusal.

**A registered hazard, named because it is real:** a single 504 MiB file read with
`.read()` peaks well above its own size in a Python `str`. The instrument
therefore **refuses** any corpus file above a registered `MAX_FILE_BYTES =
1_073_741_824` and records the refusal as a **skipped artifact in the manifest**,
counted and named — never silently dropped.

---

## 9. Queue entry

`QUEUE_ENTRY_DRAFT.json` sits **beside this document, in the case directory**, and
is **not** in the drop path `verification/queue/closure/`. Two independent things
stop this draft from launching anything:

1. It is not in a drop path.
2. `prereg_commit` is the literal string `PENDING_SUPERVISOR_FREEZE`, which fails
   the validator's full-sha schema check and can never validate until the
   supervisor replaces it with the real freeze sha.

**`enqueued_by` states explicitly that `SUPERVISION_CHARTER.md` §3 check 4 has NOT
been performed.** That check is the supervisor's own and is not delegable; a lane
writing it would be manufacturing the supervisor's non-delegable act.

**`cwd` is the RUN ROOT `/home/ubuntu/closure-data/rc1/`, pre-created empty by the
supervisor at enqueue** — not the repository case directory, because a launch drops
`launcher.queue.out` and `STATUS.<case_id>` into `cwd` and `FILING_CHARTER.md`
forbids that inside the tracked tree. **This lane verified at drafting time that
`/home/ubuntu/closure-data/rc1` does not exist**, and did not create it.

**A green verdict from the validator is not an approval.**

---

## 10. What it cannot see

`CLOSURE_MODELLING_CHARTER.md` §16 makes this section mandatory.

1. **THE HONESTY CLAUSE, and it is the most important sentence in this document.**
   **A corpus-based demonstration proves a reader sees the non-zeros *this corpus
   happens to contain*.** It does **not** prove the reader would see a failure mode
   absent from the corpus. Concretely, on the corpus measured at drafting: the
   signatures observed firing on real artifacts are `Foam::sigFpe::sigHandler`,
   `--> FOAM FATAL ERROR` and `--> FOAM FATAL IO ERROR` — **three** of the seven
   registered `FATAL_RE` alternatives. `FOAM exiting` standing alone,
   `Foam::error::printStack` standing alone, a line-initial `Floating point
   exception` from the shell, and a line-initial `Segmentation fault` are
   confirmed **only synthetically**. A `sigSegv::sigHandler` death, an OOM kill
   that leaves no marker at all, and a solver killed by `timeout` are **not in this
   corpus and RC1 cannot speak to them.** A `PASS` from RC1 is *"shown able to
   distinguish the failures this box has actually produced"*, and nothing wider.
2. **It cannot see whether a reader's non-zero is CORRECT** — only that it is not
   constant and not banner-triggered. Two artifacts are cross-checked against
   independent ground truth (§2.4); the other several thousand are not.
3. **It cannot see a defect in a channel whose two values it never distinguishes.**
   B1/B2/B3 are existence clauses. A reader that returns the right value on 5,637
   logs and the wrong one on the 5,638th passes RC1.
4. **It cannot see the FIELD channel.** Every reader that grades a number from an
   OpenFOAM *field* rather than a log is untouched: `_common/of_read.py`,
   `_common/score_prediction.py`, `_common/sst_baseline_metrics.py`,
   `_common/tensor_basis.py`, `Wu2018_PIML_RF/aposteriori/score.py`,
   `Ling2016_TBNN/gpu/score_gpu_ling.py` and its `arm2` sibling,
   `R4_sparta_build/score_apriori.py`, `Xiao2016_EnKF/tau_forward.py`. **The birth
   requirement binds them exactly as hard**, and discharging it needs a different
   control design — a corpus of real field files with a known non-zero, not a
   corpus of logs. **That is a separate registration and it is not written.**
   `score_gpu_ling.py:85-88` is already on the record as planting a perturbation
   that never round-trips a file, so this gap is not hypothetical.
5. **It cannot see C10.** `grade_m2.py`'s log channel is unreachable without
   reimplementing it (§3.3), and its total absence of a fatal channel is referred,
   not measured.
6. **It cannot see the field-derived half of C5 and C7.** The adapter supplies a
   log and nothing else (§6.2).
7. **It cannot see readers outside `cases/RANS_LES_closure_models/`.** D548's four
   dafoam sites and the `sdk/` helpers are outside closure's fence and are named in
   D548 for their owners, not graded here.
8. **It cannot see whether a channel's verdict is stable over time.** The corpus
   grows; a `PASS` today is a `PASS` on today's manifest. Re-running RC1 is cheap
   and that is deliberate.
9. **It cannot see a reader that is never called.** RC1 grades the channel, not
   whether the comparator's grading path actually reaches it.

---

## 11. The grading path is fixed at the freeze

The instrument is `rc1_control.py` **as it exists at the pre-registration commit**.
Before any RC1 result is believed, the frozen file must be hashed against the
committed blob (standing rule 2; `scripts/check_comparator_freeze.py`).

**A LIFECYCLE FACT THIS DOCUMENT MUST CARRY, stated plainly rather than left for a
reader to discover:** at drafting time **`rc1_control.py` DOES NOT EXIST.** This
lane was dispatched to build the registration, not to run the item, and rule 2
requires the grading path to be fixed at the pre-registration commit. **The freeze
commit must therefore carry both this document and the instrument**, and until the
instrument is written the freeze cannot legally be taken. That is the supervisor's
call and is recorded here as an open condition, not as a defect of this draft.

**After first compute, gates are closed.** Changes land only as dated addenda that
cannot alter a gate, a threshold, a cap or a label; originals are struck, never
rewritten. **Before first compute, amendments are legal and must state the
condition and how it was checked** — for this rung, that the run root
`/home/ubuntu/closure-data/rc1/` **does not exist** and holds 0 core-minutes,
verified by this lane at drafting.

---

## 12. Files

| file | role | exists at drafting |
|---|---|---|
| `PREREGISTRATION.md` | this document | **yes** |
| `QUEUE_ENTRY_DRAFT.json` | the queue entry, unvalidatable until the supervisor freezes | **yes** |
| `rc1_control.py` | the instrument: corpus manifest, adapter, ten channels, four plants, the reference channel, the §5 gate, `--selftest` | **NO — see §11** |
| `CORPUS_MANIFEST.json` | written into the run root at run time, cited by every number | no (run artifact) |
| `RESULTS.md` | written after the run, by the graded record | no |

---

## 13. ANTI-GAMING REGISTER (`docs/standards/NONCONVERGENCE_STANDARD.md`)

The clause is absolute: *"Answer-changing choices are never selected by agreement
with the reference."* **No RC1 run exists; no channel has been graded by this
instrument by anyone.**

| choice | registered reason, which names no answer |
|---|---|
| **corpus = every OpenFOAM-produced log under the three run roots** | it is the widest set of artifacts written by the real producers, defined by a property of the file's own bytes rather than by a directory anyone chose; it was **not** narrowed after seeing any result, and its non-reproducible 1,200-file predecessor is disclosed in §1.2 rather than reused. |
| **producer-matched sub-corpora** | Sanaa's clause requires the control to travel *the real production path*; a reader that opens `log.frozen` has been shown nothing by a corpus of `log.simpleFoam`. |
| **B1, B2 and B3 as three clauses, not one** | B1 alone would have **passed `grade_g1.py`**, the reader whose defect cost a 127.08 core-min verdict (§5.1). The additional clauses are set from the *shape of the known defect*, not from any channel's outcome. |
| **B3's banner-only definition frozen in this document** | a subject cannot pass a clause it also defines (§6.4). |
| **the four plants, including a positive control** | a harness that only ever reports PASS certifies nothing; one that only ever refuses is equally useless. Registered as a pair, before any subject is run. |
| **the adapter uses symlinks, not copies** | the reader must be handed the producer's own bytes; copying 12.4 GiB would also make the item's cost indefensible. |
| **plants run on a stratified sub-corpus with a registered seed** | four extra full passes would double the item's cost for no additional discrimination; the strata **guarantee** at least one true positive, which is what the stuck-False plant must fail against. Seed and strata are fixed here, before any plant runs. |
| **estimate 30.0 / cap 75.0 core-min** | both rates were **measured on this box through a real subject's own code** (§7); the 2.5× ratio is justified by two named risks and is not a rounding. |
| **RC1 executes no re-grade** | a re-grade changes what a record says and needs its own frozen gate; RC1's product is a channel status. RC2 is registered separately for exactly one such re-grade. |

**One disclosure that belongs here rather than in a footnote.** This lane read the
supervisor's hand demonstration and its two result files **before** registering the
gate clauses. What that reading established is a *defect shape* and a *corpus
reproducibility problem* — properties of instruments, not of any answer. It did not
compare candidate gate thresholds, because RC1's clauses are existence tests with
no threshold to tune. The full basis is written into §1.2, §2.1 and §5.1 so a
reader can judge that rather than take this paragraph's word for it.
