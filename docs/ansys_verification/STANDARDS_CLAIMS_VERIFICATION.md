# STANDARDS_CLAIMS_VERIFICATION — an adversarial check of three claims bearing on VMFL045-R2

**Nothing in this document is sent, emailed, uploaded, filed, posted, registered or
commented outside this box (CLAUDE.md rule 7). It is an internal record.**

- **Lane:** `ansys-lane-opus`, adversarial verification pass, 2026-08-25.
- **Mandate:** `SUPERVISION_CHARTER.md` §3 check 3 — a claim bearing on a live
  credential is not relayed upward until it has been checked independently.
  Each claim was **assumed wrong** and defended against its own evidence.
- **Compute:** **ZERO.** No solver, no mesher, no new directory under
  `verification/runs/`. Every number below is re-derived by this lane from
  artifacts already on disk. Two pure functions from `sdk/chief_engineer/`
  were called over existing logs; that is reading, not computing.
- **Nothing frozen was edited.** VMFL045-R2's pre-registration
  (`592e872b5738f33cbbbb5eac6440e7174cbed95e`) and comparator
  (`382ff4975801c5911277fb463076d1a14dd813c6`) are untouched. This file is a
  **disclosure, not a repair**.
- **Nothing was reverted, deleted, moved or cleaned** (rule 10). The unexpected
  artifact of Claim 3 was inspected in place and left exactly as found.

---

## SUMMARY — the three verdicts

| Claim | This lane's finding |
|---|---|
| **1 — Courant** | **CONFIRMED in substance, CORRECTED in one stated detail.** The exceedance is real, is above S8's tolerance at L3, and is level-dependent. The claimed denominator was mis-stated. **It did not move the graded quantity and does not move the verdict** — established four independent ways below, not asserted. |
| **2 — plateau window** | **CONFIRMED on both re-derived numbers, and INCOMPLETE as reported.** COARSE reads **0.06100 %**, exactly as claimed. The two levels the claim did not name read **0.00979 %** and **0.01239 %** and **pass**. VMFL051 does get more robust. Material caveats on scope and threshold sensitivity are recorded. |
| **3 — smoke directory** | **PARTLY CONFIRMED, PARTLY REFUTED.** The directory exists inside the runs tree — confirmed. But **the smoke test did not run there**: it ran in `/tmp`, as the rule requires. The directory is an evidence copy made 23 minutes later. **Nothing could have read it and nothing did.** |

---

## CLAIM 1 — THE COURANT NUMBER

### 1.1 The clause the 2 % is drawn from, quoted with its file and section

The claim cited "a 2 % tolerance in `docs/standards/`" without naming the clause.
It is real and it is here:

> **`docs/standards/MONITOR_STANDARD.md`, §"S8. Courant excursion (same proposal)", lines 456–489.**
>
> Detection rule (line 463): *"`Courant Number max` exceeding the case limit by
> more than the tolerance an adaptive time step explains, or growing
> monotonically across 20 consecutive time steps while the time step is held
> fixed."*
>
> The tolerance (lines 470–474): *"In those four healthy archived runs, between
> 27 and 43 percent of all time steps are strictly above the limit… The largest
> overshoot anywhere in the archive is 0.403 percent. **The adopted tolerance is
> 2 percent**, five times that, so ordinary adaptive stepping never trips it
> while a real excursion still does."*
>
> Severity (line 480): *"FLAG at the limit, FATAL on monotonic growth with the
> time step fixed. Action: reduce the time step or enable adaptive stepping; **a
> transient result computed above its Courant limit is not evidence.**"*

**The denominator is fixed by the implementation, not by reading.**
`detect_courant_excursion` in `sdk/chief_engineer/log_signatures.py` documents
*"`limit` is the case's own requested maximum (`maxCo`)"*, sets
`threshold = limit * (1.0 + tolerance)` with `COURANT_TOLERANCE = 0.02`, and
fires when `peak > threshold`. For VMFL045-R2, `system/controlDict` at every
level carries `adjustTimeStep yes;` and `maxCo 0.4;`, so **the limit is 0.400
and the threshold is 0.408.**

### 1.2 The three numbers, re-derived by this lane

Source: `verification/runs/ansys_verification/VMFL045/R2/<level>/log.rhoCentralFoam`,
field 2 of every `Mean and max Courant Numbers` line.

| Level | steps | max over run | final line | excess vs **maxCo 0.400** | excess vs **final line** | steps > 0.408 |
|---|---|---|---|---|---|---|
| `L1_90x76` | 3 127 | **0.4059224004** | 0.4021990508 | **+1.4806 %** | +0.9257 % | **0** |
| `L2_180x152` | 6 305 | **0.4073086079** | 0.3974445991 | **+1.8272 %** | +2.4819 % | **0** |
| `L3_360x304` | 12 661 | **0.4129360787** | 0.4002067166 | **+3.2340 %** | +3.1807 % | **32** |

**The claim's L3 max (0.412936) and final line (0.400207) are exactly right.**

**The claim's percentage is right and its stated denominator is wrong.** +3.23 %
is the excess of the maximum over **maxCo = 0.400**, which is the correct S8
denominator. It is **not** the excess over the final line, which is +3.18 %. The
two agree to two figures only because this run's final Courant happens to land
at 0.4002 — a coincidence that does not survive to L2, where the same two
denominators give **+1.83 %** and **+2.48 %** and disagree about whether the 2 %
figure is crossed. **A finding stated against the wrong denominator is right by
accident on one level and wrong on another**, so the correction is recorded.

### 1.3 "Level-dependent" — demonstrated, with numbers

**Confirmed.** Against the correct limit the excess is **+1.4806 % → +1.8272 % →
+3.2340 %**, rising monotonically with refinement, and **only L3 crosses the 2 %
threshold**. Running the lab's own detector over the three series returns
`None` for L1, `None` for L2, and for L3 a finding of kind `courant-excursion`,
severity **`flag`**, `limit` 0.4, `threshold` 0.408, `peak` 0.4129360787,
`exceedances` **32** of 12 661 steps (0.25 %).

**Severity is FLAG, not FATAL.** S8's FATAL branch requires
`fixed_time_step=True`; every level runs `adjustTimeStep yes`, so that branch
cannot fire. The claim did not overstate severity, and this lane does not
understate it either.

### 1.4 Do the comparators read Courant? — CONFIRMED, they do not

Read as code, not grepped and assumed. Across **all seven** comparators in
`cases/ansys_verification/` — `grade_vmfl001.py`, `grade_vmfl001_r2.py`,
`grade_vmfl003.py`, `grade_vmfl005.py`, `grade_vmfl045.py`,
`grade_vmfl045_r2.py`, `grade_vmfl051.py` — the strings `courant`, `maxCo` and
`CFL` do not appear, in any case. The two **compressible** comparators
(`grade_vmfl045_r2.py` and `grade_vmfl051.py`, both `rhoCentralFoam`) open
`log.rhoCentralFoam` for exactly two purposes, at `grade_vmfl045_r2.py:535–560`:
to assert an `End` line exists, and to read the `Time = ` lines so the log's
final time can be matched against the last time directory. **The
`Mean and max Courant Numbers` lines are read past and discarded.** The claim is
correct and the gap is real.

**Context that neither excuses it nor is allowed to bury it.** The standard
corrects itself at `MONITOR_STANDARD.md:293–302`: *"S6 (residual stall) and S8
(Courant excursion) **cannot fire on any production run**, and could not on the
day it was written"* — no construction site supplies `courant_limit`. So the
lab's own live monitor is as blind to this quantity as this team's comparators
are. **That makes the gap lab-wide rather than team-specific; it does not make
it smaller,** and S8's rule text stands unwithdrawn.

### 1.5 THE QUESTION THAT MATTERS — could this have moved M₂, and how do I know?

**No. The verdict does not move.** VMFL045-R2's gate is
`|M₂ − 1.874| / 1.874 ≤ 1.0 %` on **M₂ = 1.874779041082** at L3, met at
**+0.041571 %**. Four independent lines of evidence, each from an artifact on
disk, say the excursion cannot be responsible for that number. They are stated
separately because any one of them alone would be weak.

**(a) The excursion is not in the graded window, and the graded quantity is an
end-of-run value.** The gate is the last row of
`R2/L3_360x304/postProcessing/gateMach/0/volFieldValue.dat` at
t = 6.9997885e−3 s. The peak Courant occurs at **step 1 841 of 12 660,
t = 9.867e−4 s — 14.1 % into the run**, with **85.5 % of the series still to
come.** Over the **last 25 % of the run** the maximum Courant at L3 is
**0.4062296**, i.e. **+1.557 %** — **inside** the 2 % tolerance. In the window
the gate is actually read from, there is no excursion to speak of. The same
holds at L1 (+1.388 %) and L2 (+1.295 %).

**(b) At the instant of the excursion the run had not converged, and it
subsequently travelled away from that state.** The gate Mach at the peak-Courant
row is **1.933768015** against a settled **1.874779041** — **3.146 % away**. The
excursion sits in the startup transient, before the oblique shock has
established. Whatever it perturbed, the solution then ran 10 820 further steps
and plateaued, with peak-to-peak **7.77e−5 in Mach** over the last 2 532 rows.

**(c) The scheme is nowhere near its stability limit, so this is stepper
overshoot, not instability.** `system/fvSchemes` sets `fluxScheme Kurganov` with
`ddtSchemes default Euler`. A peak of 0.413 against a request of 0.400 is the
documented artifact S8 exists to tolerate: *"an adaptive stepper sets the next
step from the previous step's Courant number, so the reported maximum sits a
little above the requested limit by construction."* Between **49.7 % and 56.3 %**
of steps at every level are strictly above 0.400 — squarely inside the
27–43 %-and-up band the standard measured on **healthy** archived runs.

**(d) Two independent instruments agree with the graded number to 1 part in
10⁴, and a grid triple that would have shown a level-specific corruption does
not show one.** The closed-form oblique-shock M₂ for the as-modelled inlet is
**1.874976957681054**; the lab value deviates by **−0.010556 %**. The Roache
triple is **`CONVERGING`**, R = 0.09564, monotone. **This is the load-bearing
argument:** the excursion is *level-dependent and worst at L3*, so if it had
corrupted L3 it would have injected a level-specific error into the finest
member of the triple — precisely the thing a monotone converging triple with
d21 = −2.447e−4 and d32 = −2.559e−3 rules out. A corrupted fine level does not
sit on a clean Richardson line by chance.

**What this lane cannot do, stated plainly.** I cannot **bound** the
time-integration error of a 3.2 % Courant overshoot from first principles, and
the one experiment that would settle it beyond argument — a re-run at
`maxCo 0.2` — is **a NEW RUNG, never a re-grade in place**, and is not run here
under the zero-compute instruction. The four lines above are strong circumstantial
evidence converging from independent directions; they are not a re-run.

### 1.6 The two things that must not be allowed to happen to this finding

1. **The finding must not be softened because the credential is important.** An
   unmonitored quantity crossed a threshold the lab's own standard sets, on the
   level the gate is read from, and no comparator would have noticed. That is
   real, it is this team's gap, and it is recorded here in full.
2. **The finding must not be inflated into a claim that the credential is
   unsound.** It is not one. The graded quantity is unaffected by every measure
   available on disk, and **VMFL045-R2's `PASS` stands**. S8's own action line —
   *"a transient result computed above its Courant limit is not evidence"* —
   is aimed at a result **computed above its limit**; this result is computed in
   a window whose maximum is **inside** the limit's tolerance.

### 1.7 What follows for future work — proposal only, decided by nobody here

Register `maxCo` and the max-over-run Courant as declared quantities in every
future transient pre-registration, and have the compressible comparators parse
the `Mean and max Courant Numbers` lines they already read past and print the
S8 figure **beside the gate, labelled NOT GATED**. A printed discrepancy
labelled non-binding is a known lab failure mode, so it must be printed as a
number with its threshold, not as a reassurance. **Retiring or adopting a gate
threshold is reserved to Sanaa** (CLAUDE.md, FIRST-ACTION rule); this paragraph
proposes and decides nothing.

---

## CLAIM 2 — THE PLATEAU WINDOW

### 2.1 What the standard actually argues, quoted

`docs/standards/MONITOR_STANDARD.md`, §"S13. Converged residuals over a graded
quantity that is still moving", lines ~760–830. Both halves of the claim are in
the text:

> **The normaliser (1.12, D389).** *"The peak-to-peak spread is a percentage of
> **the range the quantity spanned over the whole run**, `max(series) −
> min(series)`, and **not** of its absolute mean… The threshold NUMBER is
> unchanged at **0.02 %**."*

> *"Neither the endpoint difference over the same window nor the drift over the
> last quarter of the run is gated… **a fraction-of-run window silently loosens
> as a run is extended, so the same case passes by being run longer.**"*

S13's own window is **fixed**: *"a fixed window of outer iterations… 0.02 % over
400 iterations sampled every 50, giving 9 samples."*

**The claim's characterisation of the standard is accurate.** The frozen VMFL045
comparator does the opposite on both axes: `grade_vmfl045_r2.py:166–167` sets
`PLATEAU_FRAC = 0.20` (a fraction-of-run window) and `PLATEAU_TOL_MA = 1.0e-3`
(an absolute tolerance, not a fraction of anything).

### 2.2 VMFL045-R2 re-derived — all three levels, not one

Range = `max(series) − min(series)` over the **whole** run of the gate series
`R2/<level>/postProcessing/gateMach/0/volFieldValue.dat`, column
`volAverage(Ma)`. Window = the frozen comparator's own last-20 %-of-rows, so the
only thing changed is the normaliser.

| Level | rows | window k | whole-run range | window ptp | **ptp as % of range** | vs frozen 1.0e−3 | vs S13 0.02 % |
|---|---|---|---|---|---|---|---|
| `L1_90x76` **(COARSE)** | 3 127 | 625 | 6.298623e−01 | 3.842188e−04 | **0.06100 %** | **PASS** (2.6× margin) | **FAIL** |
| `L2_180x152` (MEDIUM) | 6 305 | 1 261 | 6.273463e−01 | 6.140314e−05 | **0.00979 %** | **PASS** | **PASS** |
| `L3_360x304` (FINE) | 12 661 | 2 532 | 6.270528e−01 | 7.768666e−05 | **0.01239 %** | **PASS** | **PASS** |

**The claimed coarse number is confirmed to five significant figures:
0.06100 %.** The `plateau_ptp` values agree exactly with those already recorded
in `GRADING_VMFL045_R2.json`, so this is the frozen comparator's own measurement
re-normalised, not a different measurement.

**The claim was incomplete and the completion changes its weight.** MEDIUM and
FINE **pass** the 0.02 % reading with margins of 2.0× and 1.6×. **The finding is
a one-level finding on the coarsest mesh**, not a family-wide plateau failure —
and the coarsest mesh is where a plateau is worst by construction.

**The window is not the active ingredient.** Re-measuring with a window defined
in **simulation time** (last 20 % of `endTime`, t ≥ 5.5998e−3) instead of rows
returns **identical** ptp values at all three levels, to every printed figure.
Because all three levels share `endTime = 7e−3 s`, rows and time coincide here.
**On this case the normaliser does all the work and the window does none of
it** — which sharpens the finding, since the normaliser is the half S13 argues
hardest for.

### 2.3 Would this move the verdict? — stated honestly, both ways

**Under CLAUDE.md rule 5 step 1, yes it would, and that must not be glossed.**
*"Any level not iteratively converged or not plateaued → `NOT A RESULT`."* A
COARSE level judged not-plateaued condemns the whole triple. **The counterfactual
verdict under an S13-normalised plateau clause is `NOT A RESULT`, not `PASS`.**

**Three things bound that counterfactual, and none of them is a softening:**

1. **The frozen clause is the absolute one, and L1 passes it with 2.6× margin**
   (3.842e−4 against 1.0e−3). **That clause is not edited.** It was frozen
   pre-compute at blob `592e872b…`, the run is post-compute, and rule 2 closes
   gates at first compute. Rule 6 forbids editing the frozen file at all.
2. **S13's stated threshold-sensitivity band contains this number near its
   edge.** The standard records: *"identical verdict set for any value in
   (0.0027 %, 0.0642 %], a 24× span."* L1's **0.06100 %** sits inside that band
   and **5 % below its upper edge** — at any threshold in (0.0610 %, 0.0642 %]
   L1 would pass. The failure is real at 0.02 % and it is **marginal within the
   standard's own declared indifference range**.
3. **S13's scope is thermal and the standard says so itself.** The threshold key
   is `thermal.monitor_peak_to_peak_max_pct`; the corpus is *"eleven committed
   K0c solver logs… **one solver** (`buoyantBoussinesqSimpleFoam`), **one case
   class**… **one physics regime** (laminar natural convection)"*, and the
   standard states in terms: *"**no rate measured on it transfers to the registry
   at large**"* and *"S13 and S15 are additionally **not general log rules**"*.
   Applying a thermal-scoped threshold to a shock-capturing transient is an
   extrapolation. **The ARGUMENT (normalise by range; do not use a
   fraction-of-run window) is general and this lane accepts it. The NUMBER
   0.02 % is not established for this case class.**

**One further sensitivity, labelled as this lane's own extrapolation and not a
clause.** S13 derives 0.02 % as *"one fiftieth of the tightest pass band K0c
gated on"*. VMFL045-R2's pass band is 1.0 % of 1.874 = 1.874e−2 in Mach; one
fiftieth is **3.748e−4**. L1's ptp is **3.842e−4** — failing by 2.5 %, i.e.
marginally, by the same construction. This is offered as a cross-check that the
0.02 %-of-range failure is not an artifact of transplanting a foreign number;
it is **not** a standard and nothing is graded against it.

### 2.4 VMFL051 — does its `NOT A RESULT` get more robust? CONFIRMED

VMFL051's recorded verdict (`GRADING_VMFL051.json`) is **`NOT A RESULT`**,
reason: *"level L1_120x52 has not plateaued: peak-to-peak … 6.240e−03 >
1.000e−03 (rule 5 step 1)"*. Its triple is independently **`OSCILLATORY`**
(R = −1.3486), which condemns it a second time under rule 5 step 2.

| Level | gate series | range | window ptp | **% of range** | frozen 1.0e−3 | S13 0.02 % |
|---|---|---|---|---|---|---|
| `L1_120x52` | `gateMach` | 7.327972e−01 | 6.2402e−03 | **0.85156 %** | FAIL | FAIL |
| `L2_240x104` | `gateMach` | 7.267068e−01 | 3.5354e−03 | **0.48650 %** | FAIL | FAIL |
| `L3_480x208` | `gateMach` | 7.300566e−01 | 8.5488e−04 | **0.11710 %** | **PASS** | **FAIL** |
| `L3_480x208` | `gateMachInner` | 7.311736e−01 | 1.1890e−03 | **0.16261 %** | FAIL | FAIL |

**Confirmed, and quantified.** Under the frozen absolute clause VMFL051 fails at
**two of three** levels, its finest passing at 8.55e−4. Under the range reading
it fails at **all three**, the finest by **5.9×** the threshold. The
`NOT A RESULT` moves from doubly to triply over-determined. **A reading that
makes a `NOT A RESULT` more robust cannot be suspected of having been chosen to
produce a convenient answer**, which is the only reason this row is worth
anything — and it is the strongest argument in the claim's favour.

### 2.5 The instruction, honoured

**No frozen clause was edited.** `cases/ansys_verification/VMFL045/R2/PREREGISTRATION.md`
and `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py` are byte-unchanged
by this lane. **VMFL045-R2's `PASS` stands as graded.** This section is a
disclosure against frozen work and a design input to future
pre-registrations — where the plateau clause **should** be written
range-normalised over a fixed window from the outset, before any compute, which
is the only place it can legally be written.

---

## CLAIM 3 — `SMOKE_ABORT_0215Z` INSIDE THE RUNS TREE

### 3.1 Existence and location — CONFIRMED

`verification/runs/ansys_verification/VMFL003/SMOKE_ABORT_0215Z/` exists. It is
**inside** the runs tree, at the VMFL003 run-root, alongside the six level
directories. It contains exactly three files — `log.blockMesh`, `log.checkMesh`,
`log.topoSet`, 9 122 bytes total. It is **untracked by git** (`git ls-files`
returns nothing for it), so it is on disk only.

### 3.2 The rule, and whether it was actually broken — REFUTED as stated

The rule lives in the launcher itself, `cases/ansys_verification/VMFL003/run_vmfl003.sh:126–148`,
headed *"PRE-FLIGHT SMOKE TEST — ONE TIMESTEP, COARSEST MESH, **IN A SCRATCH
DIRECTORY**"* and commented *"The smoke tree is deleted and NOTHING it produces
is ever graded."* The implementation is `SMOKE=$(mktemp -d "${TMPDIR:-/tmp}/vmfl003-smoke-XXXXXX")`,
followed by `echo "  pre-flight smoke test in $SMOKE (outside verification/runs)"`
and `rm -rf "$SMOKE"` on success.

**The smoke test did not run in the runs tree.** The three archived logs carry
their own provenance in their OpenFOAM headers:

> `Exec : blockMesh` / `Date : Aug 25 2026` / `Time : 02:15:23` /
> `Case : /tmp/vmfl003-smoke-JBEQXv/smoke`

All three read `Case : /tmp/vmfl003-smoke-JBEQXv/smoke`. **The rule was obeyed.**
The successful launcher's own record, `verification/runs/ansys_verification/VMFL003/LAUNCHER.log`,
confirms it for its own run at 02:21:36Z: *"pre-flight smoke test in
/tmp/vmfl003-smoke-gK8REm (outside verification/runs)"*.

**What the directory actually is:** an evidence copy. `stat` gives every file and
the directory itself a **birth time of 2026-08-25 02:38:36**, with mtime and
ctime identical — the signature of a copy, not of a process writing output. The
logs were produced at **02:15:23** in a `/tmp` tree that `rm -rf` or `/tmp`
hygiene would have destroyed, and were preserved because they are the evidence
for a launcher defect (OpenFOAM v2606's `topoSet` prints `cellZoneSet <name> now
size N`, never the `Selected N cell` the frozen guard grepped for; the launcher
as frozen was unrunnable and aborted at that line on first use). The directory is
**deliberately filed and cited by name in three repository records**:
`cases/ansys_verification/VMFL003/RESULTS.md:176` and `:240`,
`cases/ansys_verification/VMFL003/LANE_REPORT_run.md:128`, and
`docs/LESSONS.md:12489`.

**So the claim is right that the directory sits where it should not, and wrong
about what that means.** No smoke test ran inside `verification/runs/`. What sits
there is an archive of a `/tmp` run. The residual fault is a **filing** fault —
run-output space holding an artifact that is evidence for a case record — not the
guard-endangering fault the claim describes. This lane records it as the smaller
thing it is.

### 3.3 Did it affect anything? — established from code and timestamps, NO

Not reasoned from "it probably didn't". Four separate determinations:

**(a) No guard enumerates the run-root, so the directory is invisible by
construction.** GUARD 3 at `run_vmfl003.sh:69–77` iterates the explicit `LEVELS`
array (`L1_250x5`, `L2_500x5`, `L3_1000x5`, `D_500x3`, `D_500x4`, `D_500x6`) and
tests `[ -e "$RUNROOT/$1" ]` for **those six names only**. A seventh directory of
any name cannot be seen by it. The same holds for every other launcher in the
team: `run_vmfl001.sh`, `run_vmfl005.sh`, `run_vmfl045.sh`, `run_vmfl051.sh`,
`run_vmfl001_r2.sh`, `run_vmfl045_r2.sh` all guard against their own named levels.

**(b) No comparator enumerates the run-root either.** `grade_vmfl003.py` builds
its level list from the `LEVELS` constant at line 148 and joins each name onto
the runroot at lines 570 and 642. Every directory scan in every comparator of
this team — `grade_vmfl003.py:339,374`; `grade_vmfl045.py:510,583`;
`grade_vmfl045_r2.py:510,583`; `grade_vmfl051.py:475,550`;
`grade_vmfl001.py:282`; `grade_vmfl001_r2.py:341`; `grade_vmfl005.py:283` — is
rooted at a **named `level_dir`**, never at the runroot. **There is no `glob` or
`listdir` anywhere in this team's code that would return
`SMOKE_ABORT_0215Z`.**

**(c) The age guard cannot touch it, and there is nothing in it to touch.** The
age-guard datum is set per level by `run_vmfl003.sh:184`,
`find "$DEST/0" -type f -exec touch {} +`, scoped to that level's own `0/`
(VMFL045/VMFL051 use `touch "$d"/0/*`, likewise scoped). `SMOKE_ABORT_0215Z`
contains **no `0/` directory, no time directory and no field file** — three text
logs and nothing else. It offers the age guard neither a datum nor a comparand.

**(d) The timeline forecloses it independently.** Directory birth
**02:38:36**. The launcher's guards ran at **02:21:36Z** — the run-root did not
yet contain it, and by the launcher's own foot-note the run-root *"DID NOT
EXIST"* at 02:15Z. All six levels were written **02:23–02:35**.
`GRADING_VMFL003.json` was written at **02:35** — **three and a half minutes
before the directory existed.** Every guard, every solve and the entire grading
pass completed **before** the artifact was created. Even a comparator that did
scan the run-root could not have seen it.

**No graded quantity and no verdict, for VMFL003 or any other case, depended on
this directory.** VMFL003's grading is `GRADING_VMFL003.json`, produced at 02:35
from six named level directories, none of them this one.

### 3.4 Inspected, never reverted

The directory was **not** deleted, moved, renamed, cleaned or modified, per
CLAUDE.md rule 10. It is left exactly as found: an unexpected artifact is
evidence. **This lane recommends nothing be done to it without the supervisor's
read**, since three committed records and `docs/LESSONS.md` cite it by that
path, and moving it would break four citations to fix a filing nit. If it is
relocated, the four citing lines move with it in the same commit.

---

## WHAT THIS LANE COULD NOT VERIFY — stated plainly

1. **That the Courant excursion had no effect on M₂ at the bit level.** Four
   independent lines of evidence say it did not move the graded number, and none
   of them is a re-run. A re-run at `maxCo 0.2` would settle it and would be a
   **new rung**, never a re-grade. Not run: zero-compute instruction.
2. **That S13's 0.02 % threshold is the right number for a shock-capturing
   transient.** It is not established for this case class and the standard says
   so about itself. Only the shape of the argument transfers.
3. **Whether other teams' comparators read Courant.** This lane read only the
   seven `cases/ansys_verification/` comparators. The lab-wide claim rests on the
   standard's own 2026-08-10 correction, which this lane quotes but did not
   re-derive from the monitor's construction sites.
4. **Why `cases/ansys_verification/VMFL003/` and `verification/runs/ansys_verification/VMFL003/`
   show as staged deletions (`D `) in the shared index while the files are
   present on disk.** Noticed while working; **inspected, not touched**; outside
   this lane's brief. Flagged for the supervisor — the index is the chief's call
   (rule 10).

## COST

**0.0000 core-minutes.** No solver, no mesher, no new run directory. Reading
artifacts and calling two pure functions over existing logs. **Cost basis:**
not applicable — nothing was computed, so there is no estimate-versus-actual
row to file under rule 12.
