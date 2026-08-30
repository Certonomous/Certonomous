# VMFL069 — RESULTS

**LANDED 2026-08-30.** Drafted by `ansys-lane-opus`; the crash triage was performed
**personally by `ansys-verification-supervisor`** before this file was drafted, and this
lane **re-verified every number below against the artefacts rather than accepting the
brief** — including reproducing the comparator's refusal independently. Filed under this
family's convention `cases/ansys_verification/<CASE>/RESULTS.md`, the form every
`RESULTS path` cell in the register uses.

Two Phase Poiseuille Flow, Ansys Fluid Dynamics Verification Manual
**Release 2026 R1, March 2026, printed p. 205 = PDF p. 219**. **FIRST registration of
this case** — `LAUNCH_RECORD.txt` records `supersedes = nothing`, and no prior VMFL069
row, case directory, comparator or run root ever existed.

Graded by the frozen comparator `cases/ansys_verification/VMFL069/grade_vmfl069.py`,
blob **`dcd7f1f9bbbbe748dd33d5337127406344de8f6e`**, against the pre-registration
`cases/ansys_verification/VMFL069/PREREGISTRATION.md`, blob
**`f3d9f37336f0fbfadb60d86c3024af92ba7cfd1a`**, frozen at commit **`4e4819ab`** — the
commit the queue entry names as `prereg_commit`.
**There is no grading record**, and its absence is the correct outcome: the comparator
refused (exit 2) and wrote no JSON.

---

## VERDICT — `NOT A RESULT`

**The solver died of `SIGFPE` at time step 69 of a registered 2 000, at the first and
coarsest level.** `rc = 136 = 128 + 8`. The launcher stopped at the first non-zero rc and
never launched L2 or L3; the frozen comparator refused on the recorded non-zero rc and
wrote no grading JSON. No limb was graded, no triple was formed, no GCI exists, and no
number from this run is offered as a measurement of anything.

**THIS OUTCOME WAS NAMED IN WRITING BEFORE IT HAPPENED.** Pre-registration §10 registered
outcome **8**, verbatim:

> 8. **`rc != 0`, including 124.** The running-total cap fired or the solver died. The
>    launcher **stops at the first non-zero rc and does not launch later levels**; the
>    comparator refuses on a recorded non-zero rc. `NOT A RESULT`, and the spend is
>    reported.

Every clause of it fired, in the order it was written:

| registered clause | what happened | artefact |
|---|---|---|
| "the solver died" | `SIGFPE`, `Foam::sigFpe::sigHandler`, `timeout: the monitored command dumped core` | `L1/log.interFoam` tail |
| `rc != 0` | `rc = 136`, `wait_rc = 136`, **captured inside the detached subshell** | `RUN_RC.L1`, `L1/.solver_rc` |
| "stops at the first non-zero rc and does not launch later levels" | `later levels are NOT launched`; **no `L2/` or `L3/` directory exists** | `LAUNCH_RECORD.txt`; run root |
| "the comparator refuses on a recorded non-zero rc" | **exit 2**, no JSON written | `GRADING_VMFL069.stdout.txt`; reproduced by this lane |
| "`NOT A RESULT`" | the verdict of this row | this file |
| "and the spend is reported" | §5 below | `COST.txt`, `RUN_RC.L1` |

**This is the registration working, and it is recorded as such.** A pre-registered
failure that materialises exactly as registered is the strongest evidence a
pre-registration can produce: the outcome could not have been chosen after the fact,
because it was written down before the solver started. It is not softened here and it is
not described as a setback.

**The verdict is `NOT A RESULT` and no other word is available.** It is not `GATE FAIL` —
a `GATE FAIL` requires a graded number outside a band, and there is no graded number. It
is not `BLOCKED` — nothing prevented the run; it ran and diverged. It is not `PENDING` —
the run is over and will not be resumed.

---

## 1. THE MECHANISM — AND IT IS THE MOST VALUABLE PART OF THIS ROW

### 1.1 The finding, stated plainly

**A BOOKKEEPING CLAUSE OF THE COMPLETION RULE DICTATED A DISCRETISATION CHOICE THAT
DESTROYED THE PHYSICS.**

The frozen `case/system/controlDict.template` fixes `deltaT 1` under `adjustTimeStep no`.
Its own comments say why, and they name the clause. Quoted verbatim, with line numbers,
from the frozen file (blob-identical at HEAD and at `4e4819ab`):

```
13  // deltaT = 1 s and endTime = __ENDTIME__ s, so the number of time steps EQUALS
14  // the numeric endTime. CLAUDE.md rule 4's clause "ExecutionTime count == endTime"
15  // therefore holds LITERALLY for this transient run, with no adaptation.
```

The time step was chosen **so that a counting clause of `CLAUDE.md` rule 4 would hold
literally without needing a declared adaptation.** That is a bookkeeping motivation, and
the file states it as the first reason given for the choice.

The same file then records, in advance, that the Courant limiter is inert:

```
46  adjustTimeStep  no;
48  // maxCo / maxAlphaCo / maxDeltaT are read UNCONDITIONALLY by interFoam's
49  // readTimeControls (a missing maxAlphaCo is a FATAL IO ERROR -- measured in the
50  // pre-flight toolchain smoke, PREFLIGHT_SMOKE_RECORD.txt). With
51  // `adjustTimeStep no` they LIMIT NOTHING: deltaT stays 1 s for every step. They
52  // are set high and stated here so no reader mistakes them for an active control.
53  maxCo           1e6;
54  maxAlphaCo      1e6;
55  maxDeltaT       1;
```

**So the registration knew the Courant limiter was inert, said so in the frozen file, and
fixed the step anyway.** The physical justification it offered is at lines 17–22 of the
same file:

```
17  // adjustTimeStep no: the transient is not the object of study. The convective
18  // Courant number is large and that is harmless here -- ddt, the laplacian and
19  // div(rhoPhi,U) are all implicit, the wall-normal convective flux is identically
20  // zero, and alpha is x-uniform so its flux differences cancel. The alpha field
21  // is required by the comparator to be UNMOVED at endTime, which is the check
22  // that this reasoning is not merely asserted.
```

**The quoted lines carry the finding and nothing is added to them here.**

### 1.2 What the run measured about that reasoning

The argument at lines 17–22 was not vague — it was specific, falsifiable, and it named
its own falsifier in its last sentence. The run falsified it, and the chronology is
precise. Every figure below is read from `L1/log.interFoam` and each diagnostic line was
mapped to its owning `Time` step, not inferred from line spacing:

| step | convective Courant max | interface Courant max | `Min(alpha.fluid1)` / `Max(alpha.fluid1)` |
|---|---|---|---|
| 1 | **1.99978456347** | 0 | 0 / 1 |
| 2 | 3.44232946868 | 0 | 0 / 1 |
| 63 | 73.201833151 | 0 | 0 / 1 |
| 64 | 73.6387918285 | 0 | 0 / 1 |
| **65** | **1802.76628038** | **1802.76628038** (first non-zero) | 0 / 1 |
| **66** | **8538.46058194** | 7360.85546395 | **−5.73917 / +4.14371** |
| **67** | **8511836.48122** | 5498922.69721 | −1.86e+25 / +3.26e+25 |
| **68** | **2869282454.01** | 1328731520.93 | **−8.25842183013e+109 / +6.22517202049e+109** |
| **69** | — (`SIGFPE` before the report) | — | **−1.55614891104e+107** |

**Four decades of Courant growth in four consecutive time steps: 1802.77 → 8538.46 →
8511836.48 → 2869282454.01.** MULES could not recover the field; `alpha.fluid1` left
`[0, 1]` entirely and the run died.

**Three refinements this lane measured that sharpen the finding, and they cut both ways:**

1. **The Courant number exceeded 1 at the very first step and never returned.** Courant
   max was **1.99978** after `Time = 1` and climbed monotonically to **73.64** by step 64.
   The run was never inside the stability heuristic the limiter would have enforced, from
   the first step onward. There was no window in which the choice looked safe.
2. **The registration's physical argument held EXACTLY for 64 steps, then failed.** The
   interface Courant number was **identically zero** through step 64 — precisely the
   design premise of §6.2 (*"the wall-normal volumetric flux is identically zero and alpha
   is uniform in `x`, so both the advective and the compression fluxes across the
   interface vanish"*) — and became non-zero for the first time at step 65. **The
   argument was not wrong about the mechanism; it was wrong about the mechanism's
   durability.** The exact cancellation it relied on is exact only while `alpha` is exactly
   uniform, and nothing held it there.
3. **The loss of boundedness began at round-off scale, not at the blow-up.**
   `Min(alpha.fluid1)` first went negative after step **59**, at **−1.3792e-11**, with the
   volume fraction still reading exactly 0.5; `Max` first exceeded 1 after step **60**, at
   1.00000000005. Six steps of sub-nanoscale bound violation preceded the visible
   divergence. **The failure was not sudden — it was seeded at round-off and amplified by
   an unbounded convective operator until MULES lost the field.**

**The comparator's interface-stationarity check — the "check that this reasoning is not
merely asserted", named at controlDict line 21 — never got to run**, because it is applied
at `endTime` and the solver never reached it. The reasoning was falsified by the log, not
by the check that was registered to test it. That check remains the right check; it was
simply overtaken.

### 1.3 The registration named this mechanism too, in a second place

§10 outcome **4** reads, verbatim:

> 4. **The interface moves.** MULES at a large Courant number is the plausible mechanism.
>    The comparator **REFUSES**; `NOT A RESULT`.

**The physical mechanism that actually occurred was named in advance, separately from the
procedural clause that carried the row.** Stated honestly and without inflating it: the
operative clause is **outcome 8**, because what stopped the run was a non-zero rc, and
outcome 4's refusal path (the comparator's interface check) was never reached. Outcome 4
is not claimed as the verdict's ground. But "MULES at a large Courant number" is written
in the frozen file, before compute, and it is what the log shows — and that is recorded
rather than left for a reader to notice.

---

## 2. STRICT COMPLETION — `CLAUDE.md` RULE 4 — **FAILS, ON MULTIPLE CLAUSES**

Completion was never reached and the comparator never evaluated most of these clauses: it
refused at the rc gate, which is checked first (`grade_vmfl069.py:571-574`). The table
below is this lane's own reading of the artefacts, recorded so the failure is on the
record in full rather than implied by the refusal.

| rule 4 clause | required | measured | holds? |
|---|---|---|---|
| `rc = 0` | 0 | **136** (`RUN_RC.L1`, `L1/.solver_rc`) | **NO** |
| an `End` line | ≥ 1 | **0** (`End_lines = 0`) | **NO** |
| last time == `endTime` | 2000 | **69** | **NO** |
| fields present at `endTime` | — | **no time directory was ever written** (`latest_time_dir = none`) | **NO** |
| `ExecutionTime` count == `endTime` | 2000 | **68** | **NO** |
| age guard — fields newer than `0/U` | — | **not applicable, no fields** (`field_at_latest_newer_than_0_U = no`) | **NO** |

**The `ExecutionTime` count is 68 against 69 `Time` lines**, because step 69 raised
`SIGFPE` after printing its `Time` header and its first `alpha.fluid1` solve, before
reaching the end-of-step `ExecutionTime` report. The step count and the counting clause
disagree by exactly the step that killed the run.

**No time directory exists at all.** `writeInterval` is **500** time steps
(`controlDict.template:36`) and the solver died at step 69, so the first field write was
never due. This is also why no gate quantity could have been extracted from this run even
by an agent who wanted to: there is nothing on disk to extract one from.

---

## 3. THE FREEZE — VERIFIED BY THIS LANE, NOT ACCEPTED ON REPORT

`git hash-object` on disk, compared against the blob at **HEAD** and against the blob at
the freeze commit **`4e4819ab`**. All three files are **the same object at all three
points**:

| file | blob | on disk | at HEAD | at `4e4819ab` |
|---|---|---|---|---|
| `PREREGISTRATION.md` | `f3d9f37336f0fbfadb60d86c3024af92ba7cfd1a` | ✅ | ✅ | ✅ |
| `grade_vmfl069.py` | `dcd7f1f9bbbbe748dd33d5337127406344de8f6e` | ✅ | ✅ | ✅ |
| `run_vmfl069.sh` | `31ba108607c384a3b805f3336f725a8f4b844dd8` | ✅ | ✅ | ✅ |

The launcher performed the same check at launch time and printed **`freeze OK`** for the
pre-registration and the comparator, plus **`case inputs OK: 12 files, each byte-identical
to its HEAD blob`** and **`controls OK: --selftest 67/67 PASS`**, with `python3` and
`python3 -O` agreeing on 67/67 and both carrying the AST guard marker
(`launcher.queue.out`).

**Nothing was edited after the freeze, and nothing was edited to accommodate this
outcome.** The `SUPERVISOR_RULING_SEC3.3.txt` filed 2026-08-30 is a **record, not an
amendment** — it declined an amendment and changed zero bytes; the three blobs above are
byte-identical to their `4e4819ab` originals, which is what the table verifies.

**Mesh, from the level's own `checkMesh` birth certificate** (`MESH_STANDARD` §6):
`cells 256`, `mesh_ok true`, `failed_checks 0`, max non-orthogonality **0.0**, max skewness
**2.13e-14**, max aspect ratio **2.0** — exactly the registered L1 (8 × 32). **The mesh is
not implicated.** The case was correctly built and correctly launched; it was the time step
that killed it.

---

## 4. THE COMPARATOR'S REFUSAL, REPRODUCED INDEPENDENTLY BY THIS LANE

The recorded refusal in `GRADING_VMFL069.stdout.txt` was not taken on trust. This lane
cleared `__pycache__` and re-ran the frozen comparator against the same run root, writing
to a scratch output path so nothing under the run root could be disturbed:

- **exit code 2**, matching the record;
- stderr identical to the recorded line: `REFUSING (exit 2): rc=136 recorded for L1
  (124 == the cap fired). A RECORDED non-zero rc is evidence about the SOLVER and refuses
  (L-342).`
- **no JSON written**, at the scratch path or the registered path.

The refusal site is `grade_vmfl069.py:571-574`:

```python
out["rc"], out["rc_status"] = int(m.group(1)), "MEASURED"
if out["rc"] != 0:
    raise SystemExit2("rc=%d recorded for %s (124 == the cap fired). A RECORDED "
                      "non-zero rc is evidence about the SOLVER and refuses "
                      "(L-342)." % (out["rc"], level))
```

**The refusal message names 124 because 124 is the cap-fire code the clause was written
around; the rc here is 136, and the clause is written on `rc != 0`, so it covers both.**
The message is slightly misleading read alone — it reads as though 124 were the value
seen — and that is recorded here as a **cosmetic defect in a refusal string, gating
nothing**, not repaired after the fact and not written into any gate.

**The L-342 split was honoured and is worth naming.** `RUN_RC.L1` is classified
INFRASTRUCTURE by its own note, and the comparator degrades gracefully when it is *absent*
(`rc_status = "NOT MEASURED"`, grade proceeds on physics-critical clauses). But a
**present and non-zero** rc is evidence about the solver, and it refuses. That distinction
— absent means unknown, present-and-non-zero means dead — is the correct one and it was
frozen before the run.

**`STATUS.VMFL069` reads `launcher_rc=136` and says so about itself:**
`note=exit-status-of-the-launch-argv-NOT-the-solver-rc`. **That field is not evidence about
the solver and is not used as such here.** The solver rc is the one captured **inside** the
detached subshell — `L1/.solver_rc` = `136`, mirrored into `RUN_RC.L1` as `rc = 136`,
`wait_rc = 136` — and that is what the comparator read. Had the rc been taken around the
`setsid` line it would have read 0 for every outcome, and this row would have been graded
as if the solver had exited cleanly.

---

## 5. COST — ESTIMATE VERSUS ACTUAL (`CLAUDE.md` RULE 12)

| | predicted | actual | ratio |
|---|---|---|---|
| **total core-min** | **8** (registered §7, frozen before compute) | **0.05** | **0.00625** |
| **$ (DERIVED, NOT MEASURED)** | $0.006840 | **$0.00004275** | — |

**0.05 core-min = 3 wall s × 1 rank ÷ 60**, from `RUN_RC.L1` (`wall_s = 3`, `ranks = 1`),
mirrored in `COST.txt` as `total_core_min = 0.05`. Against the registered running-total cap
of **45 core-min**, **0.1111 % was used** and **44.95 core-min went unspent**. The cap never
came near firing; the launcher's `timeout` was set to the full 2 700 s and the solver died
after 3.

**WASTE: 0.05 CORE-MIN SPENT FOR NO VERDICT, NAMED SEPARATELY AND NEVER ABSORBED**
(`COMPUTE_BUDGET_CHARTER` §6). The entire spend is waste under that charter's definition:
it produced no graded number. It is small, and it is named at its true size rather than
rounded to nothing.

**THE RATIO 0.00625 IS NOT A CALIBRATION OF THE COST MODEL AND MUST NOT BE READ AS ONE.**
The registered 8 core-min was a projection of **three complete solves totalling 6 000 time
steps**. What was actually bought was **69 time steps of the coarsest level alone** —
**3.45 %** of L1's own registered step count and **1.15 %** of the registered three-level
total. **A cost model is not tested by a run that died in its first 3 % of its first
level.** The ratio is recorded because rule 12 requires the comparison at every process
completion; what it tells us is stated in §6 of the calibration row and repeated here: it
says the run stopped early and it says nothing about whether 8 core-min was the right
number.

`cost_basis`: c7a.4xlarge at **$0.0513/core-h**, owner-stated 2026-08-21/22 —
**REPORTED-BY-OWNER, NOT MEASURED.** The box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure above is **DERIVED**.

**Contention at launch, named separately and not absorbed:** `CONTENTION.txt` records load
average **1.20 on 16 cores** with 5 `python3` processes live and 29 681 MB available. The
box was quiet. **Contention explains nothing about this outcome**, and is recorded so that
it cannot later be offered as an explanation.

---

## 6. THE PRE-FLIGHT SMOKE COULD NOT HAVE CAUGHT THIS, AND THAT IS A COROLLARY, NOT A CRITICISM

The 2026-08-28 pre-flight smoke (commit **`710a3e9a`**, recorded in
`PREFLIGHT_SMOKE_RECORD.txt`) ran L1 for **three time steps** and reported the launcher's
pass path executing end to end: `blockMesh`, `checkMesh` (`Mesh OK`, 256 cells),
`setFields`, `interFoam` `rc 0` with **1 `End` line and 3 `ExecutionTime` lines**, the
`fvOptions` markers present, and all six guard arms driven to **both** outcomes (L-314).

**IT COULD NOT HAVE CAUGHT THIS DIVERGENCE, AND THE PROOF IS THAT IT SAW THE SAME NUMBERS
THE REAL RUN PRODUCED.** The smoke recorded *"Courant Number mean over the three steps:
0 → 1.78 → 3.44"*. The graded run's own first steps read **0 → 1.78021081765 →
3.44232946868** — **the same numbers to every digit the smoke printed.** The smoke observed
the exact opening the real run had, and the opening was fine. Divergence needed **69**
steps. Three steps is, in the smoke record's own words, *"about 1/600 of one time
constant and roughly 1/670 of the run"*.

The smoke also observed *"Phase-1 volume fraction = 0.5 exactly, Min(alpha)=0, Max(alpha)=1
at every reported step: the interface did not move and stayed sharp"* and *"Interface
Courant Number mean/max: 0 / 0 at EVERY step"*. **Both statements remained true for 58
more steps than the smoke ran**, and both then failed. A three-step observation of a
quantity that holds exactly for 59 steps and then collapses is not weak evidence — it is
evidence about a different question.

**A SMOKE PROVES THE TOOLCHAIN AND NEVER THE NUMERICS.** That is the corollary of the
supervisor's own VMFL006 quarantine rule, which the smoke record states and obeys:

> MAY — exercise the toolchain: mesh, patches, dictionaries, launcher abort paths, reader
> parsing, and that the solver starts and takes steps.
> MAY NOT — produce a converged solve or a gate value.

**A smoke that had been allowed to run long enough to see this divergence would have been
long enough to compute a gate quantity, which is exactly what the quarantine rule forbids.**
The limit is the right limit. This row is not an argument for loosening it; it is the
record of what the limit costs, so that nobody in this family mistakes a green smoke for a
numerically sound registration. **The smoke did its job correctly and completely. It was
never the instrument that could have answered this question.**

The smoke record itself said so in advance, in `PART 4 — WHAT WAS NOT VERIFIED, STATED
PLAINLY`:

> THE 2000-STEP RUN HAS NOT BEEN RUN. Whether interFoam reaches the plateau by t = 2000 at
> every level, whether the interface stays put over 2000 steps at a convective Courant
> number of order 350, and whether the solution stays streamwise-invariant are ALL
> UNVERIFIED.

**It named the risk, at the right order of magnitude, and declined to claim it had been
tested.** The registration was honest about its own exposure before the run, and the run
found it.

---

## 7. WHAT THIS ROW DOES NOT CLAIM

- **It is not a statement about Ansys.** This box has no Ansys solver, and no Ansys number
  was used: the manual prints **Figure .69.2 only** for this case — there is no Target
  table — and the registered reference is the **exact solution of the same continuum
  model**, derived in the pre-registration and re-derived inside the comparator
  (lower-layer mean 10 m/s, upper-layer 50/3 m/s, whole-channel 40/3 m/s). Figure .69.2
  was never read, digitised or compared against. **Nothing here reflects on Fluent, on
  Marchandise & Remacle (2006), or on the manual.**
- **It says nothing about whether this lab could reproduce VMFL069.** The gate was never
  reached. Whether `interFoam` on this case setup lands inside the frozen 1 % band is
  **unknown and is not guessed at.**
- **It does not establish that a smaller `deltaT` would fix it.** That is the obvious
  hypothesis and it is deliberately not asserted: no such run was made, and this row does
  not invent one after the fact. The successor registration named in §12 of the
  pre-registration is where that question belongs, decided on its own frozen terms.
- **It is not a credential.** Only `PASS` rows are credentials
  (`ANSYS_VERIFICATION_CHARTER` §6). The three `PASS` ceilings ruled by the supervisor at
  `b1b7cfc1` **stood as frozen and never bound on this outcome** — `NOT A RESULT` sits
  below any ceiling — and that is stated so the ruling is not read as having done work it
  did not do.
- **Nothing here is sent anywhere.** Submissions are parked; the manual is proprietary
  Ansys documentation held for this lab's private use (`CLAUDE.md` rules 7 and 8).

---

## PROVENANCE

| item | value |
|---|---|
| manual | Ansys Fluid Dynamics Verification Manual, **Release 2026 R1, March 2026**, printed **p. 205** = **PDF p. 219** |
| title-page verification (rule 15) | **PDF page 1 read directly**, not by filename, file type or hash: it reads *"Ansys Fluid Dynamics Verification Manual"* over the 2026/R1 cover art, with *"ANSYS, Inc. / Southpointe / 2600 Ansys Drive / Canonsburg, PA 15317 / Release 2026 R1 / March 2026"*. The `.txt` sidecar's opening lines carry the same title, release, date and address **verbatim**, and the sidecar's VMFL069 section matches the case's reference, solver, physics, material properties (ν₁ = 0.1, ν₂ = 0.02, equal densities), geometry (2 m × 4 m) and boundary condition (periodic, pressure gradient −0.5 Pa/m) |
| reference | **EXACT SOLUTION OF THE SAME CONTINUUM MODEL**, derived in `PREREGISTRATION.md` §5.1 and re-derived independently inside the comparator. **No Ansys number is used**; the manual prints Figure .69.2 only and no Target table exists for this case |
| pre-registration | `cases/ansys_verification/VMFL069/PREREGISTRATION.md`, blob `f3d9f37336f0fbfadb60d86c3024af92ba7cfd1a` |
| freeze commit | **`4e4819ab61ed96420fb6da987305dcb8375c1982`**, 2026-08-28T17:41:57Z — the `prereg_commit` the queue entry names |
| comparator | `cases/ansys_verification/VMFL069/grade_vmfl069.py`, blob `dcd7f1f9bbbbe748dd33d5337127406344de8f6e` |
| launcher | `cases/ansys_verification/VMFL069/run_vmfl069.sh`, blob `31ba108607c384a3b805f3336f725a8f4b844dd8` |
| freeze re-verified by this lane | on-disk `git hash-object` == blob at HEAD == blob at `4e4819ab`, for **all three** files; launcher printed `freeze OK` at launch plus 12 case inputs byte-identical to their HEAD blobs |
| pre-flight smoke | commit **`710a3e9a`**, 2026-08-28T17:44:06Z, `PREFLIGHT_SMOKE_RECORD.txt` — scratch root only, L1 for 3 steps, `latest_time_dir = none`, **no gate quantity computed** |
| §3.3 ceiling ruling | `cases/ansys_verification/VMFL069/SUPERVISOR_RULING_SEC3.3.txt`, commit `b1b7cfc1` — a **record, not an amendment**; zero bytes changed |
| launched / died | **2026-08-30T22:51:46Z** / **2026-08-30T22:51:50Z**, `LAUNCH_RECORD.txt` |
| solver | `interFoam`, OpenFOAM v2606, `/usr/lib/openfoam/openfoam2606/platforms/linux64GccDPInt32Opt/bin/interFoam`, serial `RANKS = 1` |
| run root | `verification/runs/ansys_verification/VMFL069/` — **L1 only**; no `L2/`, no `L3/` |
| solver log | `verification/runs/ansys_verification/VMFL069/L1/log.interFoam` |
| queue entry | `verification/queue/ansys-verification/launched/VMFL069.json` |
| records commit | `951ec636` (run artefacts and queue entry) |
| grading record | **NONE — the comparator refused (exit 2) and wrote no JSON.** Its absence is the registered outcome, verified by this lane at the registered path and at an independent scratch path |
| comparator exit code | **2** (recorded, and **reproduced independently by this lane**) |
