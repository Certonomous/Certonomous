# A3GC MESH-GENERATION FEASIBILITY PROBE — COST CALIBRATION ROW, **PARKED**

> **⚠ PARKED, NOT FILED.** This row is **NOT** appended to `docs/COST_CALIBRATION.md`.
> `scripts/append_record.py` currently refuses every team's append at **exit 7** on a
> malformed `cfd` row; that register repair belongs to `verification`, not to `dafoam`.
> This file is the durable home of the row until the register accepts it. It was **not**
> hand-landed through the private index either.
>
> **⚠ THE PROBE IS `prereg=FEASIBILITY` AND IS NOT GRADEABLE.** No verdict from the fixed
> vocabulary (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
> `PENDING`) is emitted here or is available to it. Nothing below is a gate reading.
> **SUBMISSIONS PARKED.**

Dated **2026-09-11**. Lane: `dafoam` `lab-lane`. Rung: **A3GC** (ONERA M6, three-level
mesh family). Probe root: `/home/ubuntu/certonomous-runs/A3GC-meshgen-probe/`.

---

## 1. THE PRE-REGISTERED FIGURE — ⚠ THIS SECTION IS **STRUCK AND CORRECTED**; SEE CORRECTION 1 AT THE FOOT

**Estimate / real stop: 105 core-min**, handed to this lane by the `dafoam-supervisor`
as pre-registered by them.

~~⚠ **I could not locate the 105 core-min figure in a committed artefact.**~~ **STRUCK 2026-09-11 — THE CLAIM IS FALSE AS TO FACT. The figure IS committed: `docs/LAB_STATE.md:7061`. See CORRECTION 1.** The struck paragraph is left visible because the challenge it carried is what produced both the supervisor's concession and the enforcement-gap finding in CORRECTION 1; a tidy record would have lost both. What remains true in it: I read
`cases/dafoam/ladder-a/A3/curriculum_A3GC/PREREGISTRATION.md` in full for it: §5's cost
table registers the **graded** item at **≈1,525 core-min estimate / 2,290 core-min cap**
(`:365`, `:366`), which is a different and much larger envelope, and no occurrence of
`105` appears anywhere in that file. The probe cap therefore reaches me from a
supervisor's brief rather than from a frozen document. **An agent's message is not a
pre-registration** (`CLAUDE.md` rule 9). I enforced the 105 figure exactly as instructed
and it is the number this row calibrates against; the supervisor should say where it is
registered, or register it, because a cap that exists only in a dispatch message cannot
be audited later.

---

## 2. THE MEASURED SPEND — host wall x ranks / 60, ranks = 1 on every level

Every level ran as a detached `docker run --cpus=1` container
(image `sha256:8352629516bb363345fd802ed6092f878bad0a612c05c98d492a14bd94729d46`),
so **ranks = 1 and core-min == wall minutes** by construction.

| # | item | wall s | **core-min** | rc | artefact the figure is read from |
|---|---|---|---|---|---|
| 1 | **L3 attempt 1** — died on a `set -u` bug | 1 | **0.02** | `DOCKER_RC=1` | `A3GC-meshgen-probe/L3_launch.out` |
| 2 | **L3 re-run** — complete, 7/7 steps rc=0 | ~150 † | **2.50** † | 0 | `A3GC-meshgen-probe/L3/STEPS.tsv` |
| 3 | **L2** — complete, 7/7 steps rc=0 | 2,403 | **40.05** | `DOCKER_RC=0` | `A3GC-meshgen-probe/L2_launch.out` |
| 4 | **L1** — **STOPPED AT THE CAP, INCOMPLETE** | 3,762 | **62.70** | *none written* ‡ | `L1_launch.out` `HOST_START_EPOCH=…16:27:08Z` + `BUDGET_WATCHDOG.log` `STOP COMPLETE` 17:29:50Z |
| | **TOTAL AGAINST THE 105 CAP** | **6,316** | **105.27** | | `BUDGET_WATCHDOG.log` read 6,305 s at the stop decision; +11 s for `docker stop` to complete |

† **L3's host-wall figure is BOUNDED FROM ARTEFACT MTIMES, NOT READ FROM A LAUNCH
RECORD, and that is a gap in the evidence, not a rounding.** L3's first attempt
overwrote `L3_launch.out`, so the successful re-run has no `WALL_S=` line. What *is*
measured is the in-container step sum **146.83 s** (`L3/STEPS.tsv`, seven rows). The
150 s charged here adds container start plus `loadDAFoam.sh`, bounded by the last L3
artefact write at 15:46:04.7Z. **It is charged UPWARD deliberately**: under a real stop
a level whose host wall could not be read must not be under-charged.

‡ **L1 has no `DOCKER_RC=`/`WALL_S=` line because the stop killed the chain script's
process group, and `launch_level.sh L1` — the process that would have written the end
block — died with it.** Its wall is therefore computed from its own recorded
`HOST_START_EPOCH` to the watchdog's `STOP COMPLETE`. This is a **real defect in the
probe harness**: the launcher records the end of a level that finishes and records
nothing about a level that is stopped, which is exactly the level whose cost a cap
enforcement most needs. Named here rather than papered over.

### 2.1 Lane-side probe infrastructure, named separately and NOT folded into any ratio

| item | core-min | what it bought |
|---|---|---|
| planted control on the stop path | **0.08** | one throwaway container started and `docker stop`-ed, to **prove** the exact command the watchdog would run actually stops a live container (1 container → 0) rather than assuming it |

**This is not waste and it is not part of the probe's 105.** A watchdog not shown able
to stop a container is not a watchdog, and a zero from a reader not shown able to see a
non-zero is not evidence (`CLAUDE.md` rule 3, `FILING_CHARTER.md` §5).

---

## 3. ACTUAL / PREDICTED — AND WHY THE HEADLINE RATIO IS A LIE IF QUOTED ALONE

**Headline: actual 105.27 core-min / predicted 105 core-min = ratio 1.003.**

⚠ **THAT RATIO MEASURES THE ENFORCEMENT, NOT THE ESTIMATE.** The run was **truncated at
the cap**, so actual equals predicted *by construction*. Quoting 1.003 as evidence that
the estimate was good would invert the finding. **The registered work did not complete**
— L1 produced no mesh — so the true cost of the three-level probe is **strictly greater
than 105 core-min and its exact value is unknown.**

**The defensible statement is a LOWER BOUND, and it is measured, not estimated:**

| component | core-min | basis |
|---|---|---|
| L3 complete | 2.50 | measured (bounded, §2 †) |
| L2 complete | 40.05 | measured |
| L1 pyHyp, **incomplete** | **> 62.70** | measured; it was still marching when stopped |
| L1 OpenFOAM chain (`plot3dToFoam`→`checkMesh`), never reached | ≈ 7.3 | **DERIVED**: the chain cost 8.90 s at 99,840 cells and 62.60 s at 798,720 cells (`L3/STEPS.tsv`, `L2/STEPS.tsv`) — ratio **7.03** per 8x cells — so 62.60 x 7.03 ≈ 440 s |
| **three-level total** | **> 112.6** | |

**So actual/predicted > 1.07, with the true ratio unbounded above.** The 105 core-min
figure was insufficient for the registered three-level work, and the probe's honest
product is that fact rather than a ratio near one.

### 3.1 Attribution of the gap — misprediction, contention and waste kept apart

`COMPUTE_BUDGET_CHARTER.md` §6 requires waste and contention to stay **separately
named** and never absorbed into the ratio.

- **MISPREDICTION — the dominant term, and its mechanism is now known.** Cost is driven
  by **pyHyp's implicit sub-iteration count**, not by cell count. L3 ran 4→462
  sub-iterations through layer 14, spiked to 3,426 / 3,892 / 1,918 over layers 15–17 and
  finished in **137.93 s**. L2, at 8x the cells, ran **2,336.78 s** — **16.9x L3, for 8x
  the work** — because its sub-iterations reached **10,332** at layer 29 and **8,146** at
  layer 30 and never recovered. Any estimate linear in cells is wrong by roughly 2x per
  refinement step, compounding.
- **CONTENTION — present, bounded, and NOT the main term.** The box carried `cfd`'s
  8-rank `SUBOFF_A1` `snappyHexMesh` plus two other-team solvers at load 11–14 on 16
  vCPU for the whole of L3 and most of L2 (`L3_launch.out` and `L2_launch.out` each
  capture `uptime` + `vmstat` at start; `L3_contention_mid.out` captures a mid-L3
  reading at 15:45:45Z showing load 12.19 and run-queue 12–16). **However**, `docker
  stats` read the probe container at **100.13%** and **100.08%** of its one CPU while
  that load was live, so contention did **not** starve it of its allotted core; the
  residual effect is on shared LLC and memory bandwidth and is **not quantified**. The
  figures above are **GROSS**, and contention inflates them by an unmeasured amount.
- **WASTE — 0.02 core-min, named on its own line and never folded in.** L3's first
  launch attempt died `DOCKER_RC=1` after 1 wall s on a `set -u` bug in `level_chain.sh`
  (`loadDAFoam.sh` references unset variables and aborts under `set -u`). Cause
  infrastructural, diagnosed, fixed, re-run succeeded. **0.019% of the spend.**
- **NOT waste: L1's 62.70 core-min.** It produced no mesh, but it bought a measured
  lower bound on L1's cost, which is the one number the probe was commissioned for. It
  is spend that produced a measurement instead of an artefact, and it is recorded as
  such rather than as loss.

---

## 4. DOLLARS — **DERIVED, NOT MEASURED**

**The box cannot read its own billing** (`COMPUTE_BUDGET_CHARTER.md` §5), so no dollar
figure here is measured.

- Rate **$0.0513/core-h on c7a.4xlarge** — **REPORTED-BY-OWNER** (Sanaa, 2026-08-21/22),
  corroborated at `cases/dafoam/.../Xiao2016_EnKF/PREREGISTRATION.md:197`. Not a figure
  this box measured.
- **105.27 core-min = 1.7545 core-h x $0.0513 = $0.0900** — **DERIVED, NOT MEASURED.**
- Predicted 105 core-min = 1.75 core-h = **$0.0898** — DERIVED, NOT MEASURED.
- Under the $25 pre-authorisation. **The figure is stated anyway, because a blanket is
  not a per-item read** (`CLAUDE.md` rules 9 and 12).

---

## 5. THE STOP WAS REAL, AND IT WAS VERIFIED BEFORE IT WAS RELIED ON

`CLAUDE.md` rule 12: *an overrun stops the run; it does not get a new budget.* **No
extension was requested by this lane and none was taken.**

- Enforcer: `A3GC-meshgen-probe/budget_watchdog.sh`, a **detached** `setsid` process
  (pid 2105407) independent of any agent, polling every 20 s.
- ⚠ **BUT IT DID NOT EXIST FOR THE FIRST 34 MINUTES — see CORRECTION 1 §C1.2.**
- Fired: **`2026-09-11T17:29:39Z CAP REACHED at TOTAL_S=6305 — REAL STOP`**
  (`BUDGET_WATCHDOG.log`), then `docker stop a3gc_probe_L1 rc=0`, then
  **`17:29:50Z STOP COMPLETE`**, then `WATCHDOG_EXIT_RC=0`.
- **Verified, not assumed, BEFORE the cap:** (a) its arithmetic recomputed independently
  against its own log and agreeing; (b) the exact `docker stop -t 10` command **proved**
  on a throwaway container, 1 → 0; (c) its `name=a3gc_probe_` filter shown to select the
  live container; (d) the chain script's process group confirmed to contain only itself
  and its `sleep`, so the group kill could not reach another team's work.
- Post-stop: container gone, `chain_L1_after_L2.sh` gone, no `a3gc_probe_` container
  remaining.

---

## 6. CALIBRATION LESSONS THIS ROW CARRIES FORWARD

1. **Do not estimate hyperbolic-extrusion mesh cost linearly in cells.** Measured 16.9x
   per 8x cells on this geometry, driven by pyHyp sub-iteration growth. A per-level
   factor of ~2x on top of the cell ratio is the minimum defensible allowance, and it is
   a floor, not a centre.
2. **A cap that truncates makes actual/predicted uninformative.** Any calibration row
   from a capped run must state the lower bound separately, or it will read as a
   successful prediction.
3. **Record the end block for a level that is STOPPED**, not only for one that finishes
   — see §2 ‡. The harness defect is real and is in `launch_level.sh` /
   `chain_L1_after_L2.sh`.
4. **Register the cap somewhere a later reader can find it** — see §1.

---

## CORRECTION 1 — 2026-09-11. **§1's CENTRAL FACTUAL CLAIM IS WRONG. THE PRINCIPLE IT RESTED ON SURVIVES, AND CHECKING IT EXPOSED A WORSE DEFECT THAN THE ONE ALLEGED.**

*Lines whose number changed above this section: 0.* §1's heading and its opening
sentence are **struck in place** and nothing else above is rewritten.

### C1.1 The fact: the budget WAS committed, and it was committed BEFORE compute

**Verified by this lane from disk, not accepted on the supervisor's word:**

- `docs/LAB_STATE.md:7061` reads, verbatim: *"Budget **105 core-min (3x the registered
  35)** and **it is a real stop** — the probe is not one of Sanaa's cap-exempt 3D graded
  runs."*
- `git log -S'105 core-min (3' -- docs/LAB_STATE.md` returns exactly one commit,
  **`561f1d24fa34cf1a53595d0316555c10dec9b2c4`**, committer date
  **`2026-09-11T15:36:25+00:00`**, and its diff carries the string.
- The probe's first container started **`2026-09-11T15:42:39Z`**
  (`A3GC-meshgen-probe/L3_launch.out`, `HOST_START_UTC`).

**The budget was committed 6 min 14 s before any compute ran. Prediction-first held on
this probe.** §1's claim that the figure was in no committed artefact is **withdrawn**;
I searched the item's `PREREGISTRATION.md` and not the board, and reported the absence
from the place I looked as an absence from the record.

### C1.2 ⚠ THE DEFECT THE CHALLENGE ACTUALLY FOUND — **THE BUDGET WAS REGISTERED BEFORE LAUNCH; THE ENFORCEMENT WAS NOT**

Raised by the `dafoam-supervisor` and **confirmed here by arithmetic on the probe's own
two records**:

- first container: **15:42:39Z** (`L3_launch.out`)
- `budget_watchdog.sh` first heartbeat: **16:16:52Z** (`BUDGET_WATCHDOG.log`, line 1)
- **gap: 34 min 13 s during which the 105 core-min "real stop" had NOTHING ENFORCING IT.**

It did no harm — L3 and L2 together cost ~42.6 core-min, well inside the cap — **but a
real stop that does not exist yet is not a real stop.** Had the expensive level been L2
rather than L1, the probe would have run past its budget unimpeded and the overrun would
have been discovered only afterwards. **A cap is two artefacts, a committed number and a
live enforcer, and only the first was in place at launch.**

### C1.3 What survives from §1, unchanged, and it is the part that matters

**A board entry is a committed record, but it is not a pre-registration.** Rule 12 says
every run is costed **in its pre-registration**, and this probe has **no pre-registration
document at all**. The supervisor has conceded the point: *"produces no verdict"* was
treated as though it also meant *"needs no registered budget"*, and those are different
things. A probe that cannot produce a result can still spend a hundred core-minutes, and
this one spent 105.27. **The correct artefact was a short pre-registration naming the
budget, the stop and the not-gradeable status.** None was written.

**And the principle stands independently of the fact it was wrongly applied to:** an
agent's message is not a pre-registration (`CLAUDE.md` rule 9). That would have been
true even had the figure been nowhere on disk at all.

### C1.4 One definitional reconciliation, so two numbers do not stand unreconciled

The supervisor's committed calibration row reads **105.08 core-min**, from
`BUDGET_WATCHDOG.log`'s `TOTAL_S=6305` at the stop decision. This file reads **105.27**,
reconstructed from **host** wall — including `docker run` and `loadDAFoam.sh`, plus the
11 s `docker stop` took to complete, and with L3's host wall bounded **upward** from
artefact mtimes because the failed first attempt destroyed its launch record. **The
0.19 core-min gap is definitional — in-container versus host — not a disagreement about
what happened.** Both are disclosed; neither is withdrawn.
