# G1b — REGRADE OF THE G1 GRID-CONVERGENCE TRIPLE, WITH A REPAIRED FATAL CLAUSE

Rung id: `G1b`
Family: closure, grid-convergence line
Predecessor: `G1` (`cases/RANS_LES_closure_models/G1_grid_triple/`)
Run root: `/home/ubuntu/closure-data/g1` — **the same completed physics, unmodified**
Grading path: `cases/RANS_LES_closure_models/G1b_grid_triple_regrade/grade_g1b.py`
Comparator sha256 at this freeze:
`614e52064b8ade5dbe109c632ddea23274157a263eaf6755b822d1fc3d02535b`
New compute required: **none** (solver core-minutes 0.000)

---

## 0. THE ORDERING, WHICH IS THIS RUNG'S ENTIRE ANTI-GAMING CONTENT

This document and `grade_g1b.py` are frozen and committed **before any G1
functional value has been computed or looked at by anybody in this lab**.

The lane that built this successor was instructed not to compute, print,
estimate or look at `gradP`, `Kint`, `xr`, the triple, `eps21`/`eps32`, `R`, the
observed order `p`, or any GCI, and did not. It never ran `grade_g1b.py` against
the run root, never re-ran `grade_g1.py`, and never opened
`uniform/momentumSourceProperties` or any field file under
`/home/ubuntu/closure-data/g1`. Every comparator test it ran used **synthetic
fixtures** written into a temporary directory.

That ordering is the whole evidentiary content of this rung. A regrade whose
author already knows the answer can choose bands to fit it, and is worthless.
Because no band, threshold, level, functional or ceiling has been changed from
G1 (§4, checked mechanically in §5.2), there is in fact nothing left that
*could* be fitted — but the ordering is registered anyway, because the freeze,
not the claim, is what proves it.

---

## 1. G1's VERDICT IS `NOT A RESULT`, PERMANENTLY, AND IS NOT REVISED HERE

`G1_grid_triple` ran to completion on 2026-08-27 (CHAIN COMPLETE 23:38:44Z,
rc = 0, 127.08 core-min against a 600.0 core-min cap). Its frozen comparator
`cases/RANS_LES_closure_models/G1_grid_triple/grade_g1.py` graded it
**`NOT A RESULT`**.

That verdict stands. It is not appealed, softened, reinterpreted or replaced.
`grade_g1.py` is **frozen and post-compute**: standing rule 2 closes its gates
at first compute and standing rule 6 forbids editing it. It has not been edited;
its sha256 is unchanged at
`253d594252a20e534f1b8191a966307662c101f9db7f38d6044c51b2379c6bb0`.

`G1b` is a **successor rung**, separately registered and separately frozen. It
publishes its own verdict under its own name. Whatever `G1b` reports, the
published G1 verdict remains `NOT A RESULT` forever, and the lab's record
carries both.

---

## 2. WHY A SUCCESSOR EXISTS: G1's FATAL CLAUSE WAS VERY NEARLY A CONSTANT

### 2.1 The defect

`grade_g1.py`'s `parse_log()` sets the P3 "fatal" flag with, verbatim:

    "fatal": bool(re.search(r"FOAM FATAL|Floating point exception|signal", text)),

OpenFOAM writes, at **line 18 of every log it produces**:

    trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).

That line is the solver **announcing that FPE trapping is ENABLED** — a safety
notice emitted on a healthy start. It is not a failure and it is not evidence of
one. The substring `Floating point exception` matches it, so P3 fired on every
level of a run that had completed cleanly, and G1 graded `NOT A RESULT` on a
banner.

### 2.2 The measurement

Triaged personally by the closure supervisor on 2026-08-27, with an instrument
that **grades nothing** — no functional, no order, no GCI, no verdict — over 70
`log.run` files across three families:

| reading | value |
|---|---|
| files on which the G1 clause FIRED | **63 of 70** |
| of those 63, files carrying a clean `End` line | **57** |
| of those 63, files in which EVERY hit is the trapFpe banner | **59** |

A detector that fires on 63 of 70 logs, 57 of which ended cleanly, and whose
every hit is a banner in 59 of them, is not a fatal detector. It is very nearly
a constant.

### 2.3 P3 was the only blocker

Established by the supervisor by calling the **frozen, unmodified**
`completion()` and `iterative()` from `grade_g1.py`: on all three levels the
other physics failures are 0, infrastructure defects are 0, `ExecutionTime`
counts exactly equal `endTime` (20000 / 30000 / 60000), `End` is present, the
age guard held, and every iterative clause passes — final initial residuals
Ux 3.3e-09 / 3.7e-10 / 4.0e-11 and p 1.1e-06 / 1.1e-06 / 8.5e-07 for
L1 / L2 / L3.

Nothing in that list is a functional value. None of it constrains the answer.

---

## 3. WHAT `grade_g1b.py` CHANGES, AND NOTHING ELSE

`grade_g1b.py` starts from `grade_g1.py` **byte-for-byte**. Against the
predecessor it removes exactly **eight** source lines and inserts new ones; the
eight removed lines are enumerated in §5.1 and not one of them carries a band,
threshold, level, functional, ceiling or constant.

### 3.1 (a) The fatal clause, repaired

The repaired clause matches only evidence of an **actual** failure:

| signature | why it is failure evidence |
|---|---|
| `FOAM FATAL ERROR` | OpenFOAM's own fatal banner |
| `FOAM FATAL IO ERROR` | OpenFOAM's own fatal IO banner |
| `sigFpe::sigHandler` | the FPE handler **fired**, as opposed to being installed |
| `sigSegv::sigHandler` | the SEGV handler **fired** |
| `Foam::error::printStack` | a stack trace was printed |
| a line **beginning** `Floating point exception` | the shell's own death message |
| a line **beginning** `Segmentation fault` | the shell's own death message |

The last two are anchored at start-of-line under `re.M`. The trapFpe banner line
begins with `trapFpe:`, so the `^` anchor is exactly what separates the banner
from the death message. The clause deliberately does **not** match `trapFpe:`,
`trapping enabled`, or the bare word `signal` (which occurs in ordinary prose).
The measured 63/70, 57-with-`End` and 59-banner-only figures are written into
the comparator as a comment beside the clause.

### 3.2 (b) A planted control ON THE FATAL CHANNEL — the control G1 lacked

Standing rule 3, applied to the channel that broke. `planted_control_fatal()`
**writes real log files to disk** and reads them back through the **same
`parse_log()`** the real run logs go through. It `refuse()`s — and `main()`
exits 2 — if either direction fails.

**Positive direction.** Eight synthetic logs, each carrying **exactly one**
failure signature (so no single alternative can stand in for the others), each
also carrying the trapFpe banner exactly as a real log would. The reader must
report `fatal=True` **and the hit list must contain that fixture's own token** —
firing for the wrong reason is not evidence. The eighth is a realistic combined
sigFpe stack trace of the shape OpenFOAM actually prints.

**Negative direction — the whole point.** One synthetic log that is clean, ends
with `End`, and carries the trapFpe banner **verbatim**. The reader must report
`fatal=False`. *A fatal detector never shown able to return NOT-fatal is a
constant, not a reader* — which is precisely the G1 defect. Before trusting that
`False`, the control additionally requires that (i) the banner really is in the
fixture on disk, and (ii) the **G1 clause DOES fire on it**, so that a fixture
which failed to reproduce the defect cannot certify the repair.

**Transcription controls.** Before any fixture is written, the control refuses
if the repaired clause matches the transcribed banner (the defect in a new
costume), or if the transcribed G1 clause does **not** match the transcribed
banner (which would mean the diagnosis rests on a mis-quote).

**Controls on the control.** `--selftest` swaps in a fatal pattern stuck TRUE
and one stuck FALSE, and requires the planted control to refuse in both cases.

The fatal control runs **before** the completion clauses that consume it. A
control placed after them would never execute on a run the fatal clause blocks —
which is exactly the run G1 produced.

### 3.3 (c) Same run root, strictly read-only

`RUN_ROOT` is unchanged: `/home/ubuntu/closure-data/g1`. `G1b` grades the same
physics, unmodified.

The comparator **never writes, touches or chmods anything under the run root**.
Every plant is written into a `tempfile.TemporaryDirectory()`. This is not only
asserted in prose: `main()` takes a stat digest — relative path, size and
`st_mtime_ns` for every file under the run root, opening none of them — before
and after the grading pass, and `refuse()`s if it moved, because a verdict
produced while the comparator wrote to its own evidence is void. `--selftest`
proves the witness is stable on an unchanged tree and changes under both an
edited file and an added file.

### 3.4 (d) The header banner states the honest state

`grade_g1.py` printed `(DRAFT, NOT FROZEN)` — a stale string in a file that is
in fact frozen, recorded by the supervisor as a defect. `grade_g1b.py` prints
`(FROZEN)`, states that the grading path is fixed at this pre-registration
commit, and prints **its own sha256 at run time** so the reader can hash it
against the committed blob without trusting the banner.

### 3.5 (e) L-332 and the two interpreters

The AST control is kept unchanged: the module refuses if its own source holds
any `ast.Assert` node, and the counter is itself controlled against a snippet
holding exactly one. Measured on `grade_g1b.py`: **0** `ast.Assert` nodes. Every
refusal is a real `refuse()`, so every one of them fires under `python3 -O`.
`--selftest` returns rc 0 under both `python3` and `python3 -O` (§5.3).

### 3.6 (f) The defect is carried into the record as INFRASTRUCTURE

`parse_log()` now also counts, per log, how many lines the **G1 clause** would
have matched (`legacy_hits`) and how many of those are the trapFpe banner
(`banner_hits`). `completion()` records this as infrastructure clause **I5**.

Under L-342 an infrastructure defect is named and recorded and **can never by
itself void the physics**: `I5` gates nothing, ever. It exists so the graded
record carries the evidence of the defect this successor was built to repair.

---

## 4. EVERY BAND, THRESHOLD, LEVEL AND CEILING — COPIED VERBATIM, NOTHING WIDENED

Written out here so a reader can check them against `grade_g1b.py` **without
trusting this document**.

### 4.1 The three levels and the refinement family

| level | cells | endTime | Roache index |
|---|---|---|---|
| `L1` | 3840 | 20000 | 3 (coarsest) |
| `L2` | 15360 | 30000 | 2 |
| `L3` | 61440 | 60000 | 1 (finest) |

`D_SPATIAL = 2` · `R21 = 2.0` · `R32 = 2.0` · `FS = 1.25`
`DOMAIN_VOLUME = 5.0826` m^3 · `DOMAIN_VOLUME_RTOL = 1e-4`

### 4.2 Completion and iterative convergence

`REQ_FIELDS = ("U", "p", "k", "omega", "nut")` · `AGE_MARKER = "0/U"`
`RES_MAX = {Ux 1e-5, Uy 1e-5, Uz 1e-5, k 1e-5, omega 1e-5, p 1e-4}`
`RES_REQUIRED = ("Ux", "Uy", "p", "k", "omega")`
`PLATEAU_TAIL_FRAC = 0.10` · `PLATEAU_RTOL = 1e-4` · `DISK_VS_LOG_RTOL = 1e-9`

### 4.3 The reattachment functional

`X_REF_ATTACHED = 6.5` · `X_SEARCH_MIN = 0.5` · `TAU_FLOOR = 1e-8`

### 4.4 The functional registry, with its bands and ceilings

| key | role | unit | `p_lo` | `p_hi` | GCI ceiling | floor mode | floor |
|---|---|---|---|---|---|---|---|
| `gradP` | PRIMARY mean streamwise momentum source | m/s2 | **1.0** | **3.0** | **5.0 %** | rel | 1e-4 |
| `Kint` | SECONDARY-A volume-integrated k | m5/s2 | **0.5** | **3.0** | **10.0 %** | rel | 1e-4 |
| `xr` | SECONDARY-B lower-wall reattachment length | h | **0.5** | **3.0** | **10.0 %** | abs | 1e-3 |

### 4.5 Planted-control constants

`PLANT_GRADP = 1.234567e-03` · `PLANT_K = 9.876543e+02` ·
`PLANT_KUNIFORM = 2.0` · `PLANT_XR = 4.2345`

### 4.6 Verdict mapping (standing rules 1 and 5), unchanged

`VERDICTS = ("PASS", "GATE REACHED", "GATE FAIL", "NOT A RESULT", "BLOCKED", "PENDING")`

1. Any level not complete or not iteratively converged → **`NOT A RESULT`**.
2. Triple `DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` → **`NOT A RESULT`**;
   no order and no GCI are quoted, because the three values are not monotone.
3. Triple `CONVERGING` and `p_lo <= p <= p_hi` and `GCI <= ceiling` → **`PASS`**;
   otherwise **`GATE FAIL`**. GCI at `Fs = 1.25`, computed and printed only
   inside the `CONVERGING` branch.

The rung headline is taken from the **primary** functional `gradP`. The
secondaries never change it.

`classify()`, `roache()`, `verdict_for()` and `iterative()` are **byte-identical**
to G1's.

---

## 5. THE MECHANICAL CHECKS BEHIND §3 AND §4

### 5.1 The complete list of source lines removed from `grade_g1.py`

Eight, and no more (`difflib` opcode audit, every non-`equal` opcode enumerated):

1. `"""G1 comparator: strict completion, planted-disk controls, refinement-family`
2. `control, Roache triple classification and GCI.`
3. `  rule 3  planted zero -- three controls, each of which WRITES A REAL FILE,`
4. `          does not satisfy this rule and none is used.`
5. `        "fatal": bool(re.search(r"FOAM FATAL|Floating point exception|signal", text)),`
6. `        phys.append("P3 fatal: log.run holds a FOAM FATAL / FPE / signal line")`
7. `    print("G1 GRID TRIPLE -- comparator  (DRAFT, NOT FROZEN)")`
8. `        return grade(root)`

Lines 1–4 are the module docstring. Line 5 is the defect. Line 6 is the P3
message that reported it. Line 7 is the stale `(DRAFT, NOT FROZEN)` banner. Line
8 is the `main()` call site that now brackets `grade()` with the read-only
witness. Everything else in the file is inserted, never replaced. **Zero**
removed lines carry a band, threshold, level, functional, ceiling or constant.

### 5.2 The auditor was shown a violation before its zero was believed

Standing rule 3 applied to the audit itself. The band-scanner was run a second
time against a copy of `grade_g1b.py` in which the `gradP` band had been widened
from `1.0, 3.0, 5.0` to `1.0, 4.0, 9.0`. It flagged that line (1 hit). On the
real `grade_g1b.py` it flags **0**. A zero from a scanner not shown able to
return non-zero would not be evidence.

Independently, every registry name was imported from both modules and compared
by value: `LEVELS`, `D_SPATIAL`, `R21`, `R32`, `FS`, `DOMAIN_VOLUME`,
`DOMAIN_VOLUME_RTOL`, `REQ_FIELDS`, `AGE_MARKER`, `RES_MAX`, `RES_REQUIRED`,
`PLATEAU_TAIL_FRAC`, `PLATEAU_RTOL`, `DISK_VS_LOG_RTOL`, `X_REF_ATTACHED`,
`X_SEARCH_MIN`, `TAU_FLOOR`, `FUNCTIONALS`, `PLANT_GRADP`, `PLANT_K`,
`PLANT_KUNIFORM`, `PLANT_XR`, `VERDICTS`, `RUN_ROOT` — **all 24 identical**.
`classify()`, `roache()`, `verdict_for()`, `iterative()`, the readers, the
functionals and the three original planted controls are byte-identical by
sha256 of the extracted source region.

### 5.3 Selftest, both interpreters, exit codes captured directly

| command | rc |
|---|---|
| `python3 grade_g1b.py --selftest` | **0** |
| `python3 -O grade_g1b.py --selftest` | **0** |

Captured from `$?` on the command itself, never through a pipe.

### 5.4 The fatal control, both directions, measured on synthetic fixtures

Positive direction — each fixture written to disk and read back through
`parse_log()`:

| fixture | `fatal` | hit |
|---|---|---|
| `FOAM FATAL ERROR` block | True | `FOAM FATAL ERROR` |
| `FOAM FATAL IO ERROR` block | True | `FOAM FATAL IO ERROR` |
| `sigFpe` handler fired | True | `sigFpe::sigHandler` |
| `sigSegv` handler fired | True | `sigSegv::sigHandler` |
| stack trace printed | True | `Foam::error::printStack` |
| shell FPE death message | True | `Floating point exception` |
| shell SEGV death message | True | `Segmentation fault` |
| realistic combined sigFpe trace | True | `Floating point exception`, `Foam::error::printStack`, `sigFpe::sigHandler` |

Negative direction — clean log + trapFpe banner verbatim + `End`:
`fatal = False`, hit list empty, `end = True`, `legacy_hits = 1`,
`banner_hits = 1`.

On the banner string itself: the G1 clause matches it (**True**); the repaired
clause does not (**False**).

### 5.5 The defect and its repair, demonstrated on real data outside G1

One named non-G1 artifact,
`verification/runs/D5_rsm_runs/LRR/log.run`, read through `grade_g1b.py`'s
`parse_log()`: `fatal = False`, hit list empty, `end = True`,
`legacy_hits = 1`, `banner_hits = 1`. A completed log on which the G1 clause
fires once — on the banner — and the repaired clause does not fire at all.

No file under `/home/ubuntu/closure-data/g1` was opened to establish this.

---

## 6. COST

The physics is already spent. It was charged to G1 and is not charged again.

| item | value |
|---|---|
| **solver core-minutes for G1b** | **0.000** |
| solver core-minutes already spent, charged to G1 | 127.08 (against a 600.0 cap) |
| G1 solver cost, derived at $0.0513/core-h | $0.1087 — **derived, not measured** |
| G1b grading pass, ranks | 1 |
| G1b grading pass, **estimate** | **1.0 core-min** |
| G1b grading pass, **cap** | **10.0 core-min** |
| estimate in dollars, derived | $0.00086 — **derived, not measured** |
| cap in dollars, derived | $0.00855 — **derived, not measured** |

`cost_basis`: the rate **$0.0513/core-h (c7a.4xlarge)** is **owner-stated**
(2026-08-21/22), corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`. This
box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5), so every
dollar figure above is **derived from core-minutes at that rate — derived, not
measured**. Core-minutes for the grading pass will be taken from the wall clock
of the run itself, at 1 rank, and are therefore measurable; the 1.0 core-min
figure above is an **estimate**, not a measurement.

Basis for the estimate, measured on this box on synthetic data:
`--selftest` completes in 0.08 s; `read_scalar_internal` on a 61440-value
nonuniform scalar field (0.9 MB) takes 0.100 s. The graded pass reads on the
order of ten such fields, parses three `log.run` files, and walks the run root
twice for stat only. 1.0 core-min is roughly a 60x margin over that; 10.0
core-min is the cap. **An overrun stops the run; it does not get a new budget**
(standing rule 12).

At completion, the actual grading-pass core-minutes are compared against the
1.0 core-min estimate and the ratio, with its attribution, lands as a row in
`docs/COST_CALIBRATION.md` (standing rule 12, Sanaa's 2026-08-23 directive).

---

## 7. THE GRADING PATH, FIXED AT THIS COMMIT

The grading path is

    cases/RANS_LES_closure_models/G1b_grid_triple_regrade/grade_g1b.py

and it is **fixed at the commit that lands this pre-registration**. Its sha256
at this freeze is

    614e52064b8ade5dbe109c632ddea23274157a263eaf6755b822d1fc3d02535b

Before the graded verdict is published, this file must be hashed against the
committed blob and the two must agree; the comparator prints its own sha256 in
its header at run time so the check needs nothing but the output and `git
cat-file`. From this commit forward the file is **frozen** under standing rule
6: a departure lands as a dated amendment appended at the foot, never as an
edit, and any repair to a gate, threshold, cap or label lands in a further
successor rung, never here.

`grade_g1.py` is not touched by this rung, at this commit or ever.

---

## 8. WHAT THIS RUNG STILL CANNOT SEE

Unchanged from G1, and repeated because a repaired fatal clause changes none of
it:

- This rung grades **numerical convergence only**. It says nothing whatever
  about agreement with LES or DNS truth. No reference field is read, and none
  exists on the L1 or L3 meshes.
- The Roache order and GCI are properties of this three-level family at this
  `simpleGrading`. They do not transfer to another grading, another solver
  setting, or another geometry.
- A `PASS` here would mean the three values are monotone, the observed order sits
  inside the registered band, and the GCI sits under the registered ceiling. It
  would not mean the answer is right.
- The verdict of this rung does not, and cannot, revise G1's.

---

## 9. FILES

| path | role |
|---|---|
| `cases/RANS_LES_closure_models/G1b_grid_triple_regrade/PREREGISTRATION.md` | this document |
| `cases/RANS_LES_closure_models/G1b_grid_triple_regrade/grade_g1b.py` | the frozen grading path |
| `cases/RANS_LES_closure_models/G1_grid_triple/grade_g1.py` | predecessor, frozen, **not edited** |
| `/home/ubuntu/closure-data/g1` | the run root, **read-only evidence** |

No queue entry is registered. `G1b` needs no queue: it is a read-only grading
pass, run by hand by the closure supervisor, requiring no solver and no new
compute.
