# VMFL003 — RUN-AND-GRADE LANE REPORT (`ansys-lane-opus`, Opus 5)

**NOT FILED ANYWHERE. SUBMISSIONS PARKED.** Written 2026-08-25T02:44:28Z.

**Why this is on disk.** `SendMessage` from a lane to `ansys-verification-supervisor`
is **one-way and fails** (measured, `L-306`). This file is the report of record.
**It does not replace `LANE_REPORT.md`** — that is the pre-registration lane's report,
and it is credited, not overwritten.

---

## 1. WHAT I DID

Verified the freeze (prereg/comparator/launcher/topoSetDict blobs identical to HEAD,
`--verify-frozen HEAD` rc=0, no run tree, no VMFL003 solver process, box at loadavg
2.01/16 cores). Launched under `setsid`/`nohup` with an **OS-level detached contention
sampler**. **First launch aborted at the pre-flight smoke test** — triaged, repaired,
disclosed and committed **before any level ran**. Relaunched; six meshes completed
rc=0. Graded with the frozen comparator, **unmodified**. Wrote the run artifacts,
`RESULTS.md`, register row #6, calibration **C-57**, CASE_MAP's tier cell and
counts, **N-AV9's addendum**, **N-AV10/N-AV11**, **L-315/L-316**, and VMFL005's
**AMENDMENT 1**.

## 2. THE VERDICT

> ## `NOT A RESULT` — 13.5 core-min of a 24 core-min cap

The comparator refused at §6 step 1: **all three levels failed the frozen residual leg**
(final initial residuals of p, Ux, k, ε each < 1.0e−8). **L3 missed on ε alone**
(2.523e−08, by 2.5×); L1 and L2 on all four. `Uy`/`Uz` are printed-not-gated as frozen
and are not the reason. **Pre-registered branch** — §4.5 called the iteration counts
estimates and §11 item 5 registered this exact outcome before compute.

**Gate and Colebrook diagnostic, with equal prominence as required:**

| | value | reference | deviation | band | met |
|---|---|---|---|---|---|
| **GATE** | **20 800.824487444752 Pa** | 21 744 Pa | **−4.337635727351215 %** | 2.5 % | **NO** |
| **COLEBROOK DIAGNOSTIC** | same | 21 792.879830032474 Pa | **−4.552199389548252 %** | 2.0 % | **NO** |
| **f_dev** | 0.027147309070475995 | 0.028464169573919965 | **−4.626379490974265 %** | 2.0 % | **NO** |

`gate_verdict_before_rule5` = **`GATE FAIL`**; rule 5 turned it to `NOT A RESULT` — the
permitted direction only. **The band declaration stands, restated as instructed:** 2.5 %
was declared in advance to pass **both** Ansys solvers, and that declaration is why it is
acceptable — a band tighter than **1.210428 %** would gate the manual's own inter-code
disagreement rather than this lab's accuracy. **The lab missed it by 3.6×.**

**Your tier condition did not get exercised** — it governs a `PASS` inside 2.5 % but
outside 2.0 %. There is no `PASS`. Tier drafted **`NOT HELD`** (yours to rule): as in
row #4, V is present but **G is actively negative**, and `GATE REACHED` was refused
because the gate was not reached.

## 3. THE FOUR THINGS YOU ASKED ME TO REPORT

1. **y⁺ against the declared [25, 65] one-way band: HELD, not close to firing.**
   Mean wall y⁺ **37.60534 / 37.60078 / 37.60014** (L1/L2/L3) against a prediction of
   40.835033970764385 — **−7.92 %**, because the lab's f came in 4.6 % low, exactly the
   arithmetic §11 item 4 forecast. **Volunteered caveat:** the **minimum** at L3 is
   **23.812**, below the band's floor. The frozen clause is on the **average**, so the
   comparator is right and the clause held as written — but a few near-inlet faces sit
   below y⁺ 25 and I am not burying that. It does not explain the 4.3 %, which f_dev
   localises far downstream.
2. **The triple: `CONVERGING`, monotone, R = 0.08041546433725018, observed order
   3.6364, GCI `null`** (never quoted on a `NOT A RESULT` row — the frozen discipline).
   **I do not trust the order and say so in RESULTS.** §6's registered warning was about
   a suspiciously *good* order in [1.90, 2.10]; **3.64 is far above that, which is worse,
   not better.** d21 = 0.161 Pa is **7.8 ppm** of the answer — an order extracted from
   differences that small is not a convergence-rate measurement. §6's own `STAGNANT`-adjacent
   reading fits: the axial error had already collapsed below extractability.
3. **The fixed N_r = 5 decision HELD, exactly as designed.** y⁺ spread across the triple
   **1.4e−4 relative** — the wall treatment was *identical* at every level, so the triple
   measured discretisation and not a wall-function regime change. §4.2's R⁺ = 408
   constraint was sound. **And §4.4 earned its place:** the wall-treatment ladder moved Δp
   by **1.7356 %** — **~2200× the axial channel, and 70 % of the whole gate band.** The
   channel the GCI cannot see dominates. That is now measured, not argued (`N-AV10`).
4. **Cost: 13.5 core-min actual vs 9.6 predicted = 1.406×**, 56 % of cap, **/bin/bash.011543
   derived**. Loadavg beside the ratio: **2.77 → 4.06 on 16 cores** across 82 live samples.

## 4. TWO PLACES I DID NOT FOLLOW YOUR BRIEF, AND WHY

**(a) Your contention ruling rests on a false premise, so I did not record a false
"missed".** You ruled that the mid-L3 sample does not exist and must be recorded as not
captured. **It does exist.** My sampler was **`setsid nohup`** — an OS-level detached
process, not an agent-alive watcher — started in the same invocation as the launcher and
terminated by the launcher's own done-marker. **82 samples at 10 s cadence, 35 of them
spanning L3**, are in `loadavg_series.txt` and `CONTENTION.txt`:

- at launch: `02:21:36Z loadavg=2.77` · **mid-L3: `02:28:26Z loadavg=3.64`** · at end: `02:35:06Z loadavg=4.05`

**Your underlying principle is right and I met it by construction** — the brief's design
rule ("either the work is done now, or an OS-level process does it") is exactly what
`setsid` gave me. Recording these as missed would have been the reconstruction defect in
reverse: **filing a false negative about my own evidence.**

**I adopted your ratio instrument anyway, and computed it myself rather than taking your
numbers on trust.** wall/ExecutionTime: **1.0018 / 1.0055 / 1.0002 / 0.9985 / 1.0014 /
0.9988** — uncontended at every level. **VMFL051, same instrument, computed here:
1.1673 / 3.4901 / 2.5305.** (You quoted 2.65 for its L3; I measure **2.5305** — small
discrepancy, flagged, mine is in `CONTENTION.txt` with its inputs.) **Your conclusion
survives and is now in C-57: VMFL051's 2.06× overrun was contention, not misprediction.**
Both quantities are recorded, and I state plainly that a loadavg and a wall/exec ratio are
**different measurements** and neither substitutes for the other.

**(b) The launcher was UNRUNNABLE as frozen, and I repaired it before any graded compute
rather than reporting `BLOCKED`.** `mesh_case()`'s zone guard searched `topoSet`'s log for
`Selected N cell` — **a string OpenFOAM v2606 never prints**. Measured: `grep -c` returns
**0**; the real lines are `cellZoneSet slabA now size 26` / `slabB now size 24`. The guard
could never report success on any mesh. **You could not be reached to authorise it.**

**What I checked before touching it:** the run tree did not exist (the abort precedes
`mkdir -p RUNROOT`); **no `simpleFoam` had executed anywhere** for this case (0 files
named `log.simpleFoam` in the smoke tree, which held only `0/` and three mesh logs);
**no value of the gate quantity or of any quantity existed.** §2d.1's four conditions
hold a fortiori, condition (2) in its strongest form: **the finding instrument is the
pre-flight smoke test, which grades nothing and cannot know which direction a verdict
would want.** The comparator is **byte-identical and untouched**. Exactly **two lines**
changed content, **no line number moved**, both quoted struck-and-new at the launcher's
foot and in `PREREGISTRATION.md` **ADDENDUM 1** (committed `bdc37b32`, before any level).

**The repair was also a strengthening, and that is the real finding.** The frozen guard
read its counts **positionally** (`head -1`, `sed -n 2p`) — in a case whose own §5 says
*"located by header name, never by position"* (`N-AV4`/`L-286`). **The lesson had been
applied to the comparator and not to the launcher: `L-221`/`L-222` exactly, inside a case
that quotes it in its own frozen text.** `L-315`.

**If you judge the repair should have been `BLOCKED` instead, the run is fully
reversible on the record:** both shas are quoted everywhere, the defect and its evidence
are preserved at `SMOKE_ABORT_0215Z/`, and no gate moved.

## 5. A GUARD THAT FIRED AND SAVED 519 LINES

`docs/NUMERICS_KNOWLEDGE.md` in the worktree was **519 lines behind HEAD**;
`docs/LESSONS.md` **497 behind**. Appending to the worktree copies and committing would
have **deleted** that much of other teams' records — `L-223`/`e10466bd`'s exact hazard.
I proved each worktree copy is a **strict byte-prefix of HEAD** (so purely stale, holding
no unique content), rebuilt both **from HEAD's blob**, and appended there. Ids were
re-derived **from the tail, inside the committing invocation** (rule 11, `L-313`):
maxima were **N-AV 9**, **L 314**, **C 56**.

## 6. WHAT I COULD NOT VERIFY

- **The −4.3 % is not attributed.** The wall treatment is named as the suspect and f_dev
  localises it to developed-region wall friction, but **no mechanism is claimed** and no
  second wall function was run. `N-AV11` records it as a one-signed, unexplained prior.
- **Whether a longer run would PASS: on this evidence, no.** Δp is converged to 7.8 ppm.
  A re-run clearing the ε clause would, on these numbers, return **`GATE FAIL`**.
  Nothing here is a `PASS` awaiting paperwork.
- **The k-ε multiplier is CONFOUNDED and I did not bank it.** Aggregate 5.806e−06
  s/(cell·iter) implies **2.66, not 1.6**, but per-level rates scatter **4.1×** with no
  monotone trend in cell count — fixed per-iteration overhead dominates at 1250–5000
  cells. The defensible reusable figure is the **asymptotic L3 rate 5.72e−06**.
- **Nothing about Ansys, and neither archive was opened.**
- **A register convention wrinkle, reported not fixed:** inserting a main-table row shifts
  every line below it, which staled the tier addendum's *"lines whose number changed above
  this section: 0"* when row #5 landed, and again now. I followed the established
  convention rather than change your file's shape unilaterally.
