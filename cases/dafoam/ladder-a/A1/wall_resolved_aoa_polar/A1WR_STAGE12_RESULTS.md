# A1WR STAGES 1–2 — MEASURED RESULTS, AND THE INFRASTRUCTURE KILL THAT TRUNCATED THEM

Governed by `A1WR_PREREGISTRATION.md` v1.6 (Amendment 1, Addenda A–E).
Grading path: `a1wr_read.py`, md5 `22479c8954702fbb6e1b0594fe2b8d4c`, **verified
byte-identical to the committed blob** (`git show HEAD:…/a1wr_read.py | md5sum`
and `sha256sum` both match the worktree file; `md5sum -c A1WR_STAGE12_MD5.txt`
clean on all five instruments). `__pycache__` absent before the run.

**Run root:** `/home/ubuntu/certonomous-runs/A1WR/STAGE12/`

---

## 0. VERDICT OF RECORD

**`NOT A RESULT`** for the item as a whole. Three independent grounds, in order:

1. **The item is TRUNCATED.** 19 points per arm were declared. Arm I delivered
   **13** (α 0–12); arm C delivered **9** (α 0–8), all of them failures.
   The frozen reader names this itself: `DECLARED points: 19 SEGMENTS FOUND: 14`
   (I) / `10` (C), `*** COUNT MISMATCH … the gap is NOT absorbed.`
2. **The frozen reader records ZERO convergences on either arm** —
   `CONVERGED 0` on both. Every arm-I point ran to the 4,000-iteration cap
   without DAFoam emitting its tolerance-satisfied line.
3. **`G-YPLUS` is `GATE FAIL` on arm C**, at 9 of its 10 points.

**Composition is NOT performed by this record.** `a1wr_read.py` states on its own
face that it produces "FEASIBILITY READINGS, NOT VERDICTS"; §1.4 assigns
composition to D19M's `compose_item`, which was not run here. What is stated
above is the gate-by-gate position plus the arithmetic that no composition can
exceed `NOT A RESULT` while a hard gate reads `GATE FAIL` and `G-COMPLETE`
cannot be cleared (§2.3). Overturning this line requires running `compose_item`,
and that is the supervisor's call, not this record's.

**THE TRUNCATION DOES NOT VOID THE COMPLETED PHYSICS** (Sanaa's universal rule,
2026-08-26: bookkeeping never voids physics). The 13 arm-I points are published
in §3 with their measured labels attached. **AND IT DOES NOT REFUND THE SPENT
CORE-MINUTES EITHER** (§6): 1,269.90 core-min of Stage-2 compute is spent and
gone, and the registered per-arm cap is 79.4 % consumed.

**Verdict ceiling `GATE REACHED` (§1.4) is not reached and was never in play.**

---

## 1. WHAT HAPPENED, MEASURED FROM THE BOX'S OWN RECORDS

| instant (UTC) | event | artifact |
|---|---|---|
| 2026-09-02T18:19:35Z | Stage 1 probes launch, α = 18, both arms | `logs/probe_{I,C}.docker.log` |
| 2026-09-02T18:35:58Z | Stage-1 gate `rc=0`, y+max < 1.0 both arms; **Stage 2 launches** | `stage1_gate.json`, `STATUS.A1WR_chain.log` |
| 2026-09-02T19:31:16–17Z | **all six cold controls die `rc=97` (TIMEOUT)** at the 3,300 s deadline, zero completed points | `CHAIN_LEDGER.tsv` |
| 2026-09-03T02:05:15Z | arm I writes its **last** ledger row, α = 12 | `sweep_I/out/LEDGER.tsv` mtime |
| 2026-09-03T02:07:13Z | arm C writes its **last** ledger row, α = 8 | `sweep_C/out/LEDGER.tsv` mtime |
| 2026-09-03T02:24:58Z | chain driver's last liveness poll of both containers | `journalctl -b -1`, `sudo` audit line |
| **2026-09-03T02:25:05.244Z** | **`root : COMMAND=/usr/sbin/shutdown -h now`** | `journalctl -b -1` |
| 2026-09-03T02:25:05.43Z | dockerd `Processing signal 'terminated'` | same |
| **02:25:05.618 / .628Z** | **`a1wr_sweep_I` / `a1wr_sweep_C` exit `143` (SIGTERM)** | `docker inspect .State.FinishedAt` |
| 2026-09-03T02:25:14Z | `Reached target poweroff.target` | same |
| 2026-09-03T15:34:59Z | box boots again — **13 h 09 m dead** | `last -x` |

**This was a poweroff, not a cap-stop.** The registered in-container sweep
deadline was 37,200 s and only **28,147 s** had elapsed; 9,053 s of the
container's own deadline was still unspent. Neither `G-CAPS` nor any registered
gate stopped this run.

**Both sweeps were mid-point when killed.** Arm I was **2,500 of 4,000
iterations into α = 13** (last printed `CL: 1.27168854664896`); arm C was
**1,500 of 4,000 into α = 9**. Neither produced a ledger row and **neither value
is a result** — they are named here only so the discarded work is on the record.

---

## 2. THE FROZEN READER'S OUTPUT — THE VERDICT OF RECORD

`a1wr_read.py <RUN_DIR> I` → **rc = 0**.
`a1wr_read.py <RUN_DIR> C` → **rc = 0**.

**Neither run refused.** No exit-2 path fired (`G-STALL`, `G-WALLTREAT`,
`G-YPLUS`-blind-channel and the control harness all passed), so the readings
below are the reader's own, not a substitute's. Nothing was hand-computed in
place of it and the reader was not edited.

### 2.1 Controls — 18 of 18, and the L-435 question answered

```
SELFTEST PASS: 18 controls, both directions, mutation controls included.
```

All eighteen (`C1–C7b`, `G1–G3`, `Y1–Y4`, `W1`, `B1`, `B1b`) landed, in both
directions, mutation controls included.

**⚠ THE L-435 QUESTION, ANSWERED — AND THE ANSWER IS "IT DID NOT BITE, BUT ONLY
BY ACCIDENT."** MAAOA's grading was voided last night because a control's
fixture was a live artifact of the run being graded. Here the reader reported:

```
  born against  : WRITER_BUILT FIXTURE
```

so **no control on this grading was born against an artifact of this run**, and
L-435 does not reach it. **But that is not by design.** `a1wr_read.py:447-457`
*prefers* a live artifact: it scans the run's own `sweep.log`, takes the first
segment that classifies `CONVERGED` **and** carries a y+ line, and uses that as
the control base. It fell back to the synthetic fixture **only because no point
in either arm classified `CONVERGED`** — the list was empty. **Had a single
point converged, this grading would have carried the exact defect that voided
MAAOA.** Registered here as a defect of the frozen instrument, for a successor's
attention; it is not repaired here, because the frozen reader is not edited.

**A second, smaller defect in the same code path:** the provenance line reads
`source: no sweep log on disk yet -- controls born against the WRITER_BUILT
fixture`. **That statement is false about the disk** — `sweep_I/out/sweep.log`
is 520,063 bytes and the reader parses it four lines later. The string is the
`not sweep_log.is_file()` branch's note, reused unchanged for the
"log present, nothing converged" case. Reported, not repaired.

### 2.2 Gate readings, both arms

| gate | arm I | arm C |
|---|---|---|
| `G-WALLTREAT` | **PASS** — 5 unit logs, every one carries `BCType=nutLowReWallFunction`, none carries the Spalding line | **PASS** — same, 5 unit logs |
| `G-YPLUS` | **PASS** — worst y+max **0.0404**, 14 of 14 points carried a reading | **`GATE FAIL`** — y+max ≥ 1.0 at α 0,1,2,3,4,6,7,8,9; worst **4.9806** at α = 8 |
| `G-STALL` | **PASS** — no stall word bound to an angle in the output | **PASS** |
| `G-NOBAND` | **PASS** — scope statement printed | **PASS** |
| `G-COLD` | **NOT EVALUABLE** (§4) | **NOT EVALUABLE** (§4) |
| `G-CONCURRENCY-BITS` | **`NOT A RESULT`** — `NOT RUN`, alone-copy absent (§4.2) | n/a |
| `G-CAPS` | see §6 — **not implemented as arithmetic in the frozen reader** | same |
| `G-COMPLETE` | **NO VERDICT EXISTS** — see §2.3 | same |

### 2.3 ⚠ `G-COMPLETE` IS REGISTERED IN §9 AND IS **NOT IMPLEMENTED** IN THE FROZEN READER

`grep -c 'G-COMPLETE' a1wr_read.py` returns **0**. The gate §9 registers —
rule 4 in all its clauses, "refuse (exit 2) rather than degrade" — has no code
in the grading path. The reader reports the truncation as a bare
`*** COUNT MISMATCH`, without naming the gate and without refusing.

**This record does not supply the missing verdict.** Hand-computing a gate the
frozen grading path does not implement is substituting a reader, which D19/D19R2
forbids. The gap is reported as a gap. Its practical consequence is stated
plainly: the item's completeness gate is **unadjudicated**, and no reading below
may be presented as having cleared it.

`G-MESHFAM` (Stage 0) and `G-PLACEMENT` are likewise absent from this reader;
`G-MESHFAM` was adjudicated at Stage 0 (`A1WR_STAGE0_RESULTS.md`).

### 2.4 Truncation behaviour — what the reader does with 13 rows where 19 were declared

It does **not** absorb the gap. It prints the declared/found mismatch as a
starred block, grades the 13 present points, grades the in-flight 14th
`NOT MEASURED` (its `classify()` third branch: no tolerance line **and** no
evidence of reaching the cap — "this reader cannot tell whether the field
converged, and says so rather than guessing"), and returns 0. **It does not
refuse on truncation, because no implemented gate tests it** (§2.3).

---

## 3. THE MEASURED POLAR — ARM I, α 0–12, WALL-RESOLVED L3

**Read from `sweep_I/out/LEDGER.tsv` alone.** Every point carries the frozen
reader's label `NOT CONVERGED` (§3.2). No value here is grid-converged, none
carries a band (`G-NOBAND`, §1.3), and the item's class is `FEASIBILITY`.

| α (deg) | CL | CD | ΔCL per degree | y+max | iters |
|---|---|---|---|---|---|
| 0 | −0.00000157004338125 | 0.0116984626549 | — | 0.0175 | 4000 |
| 1 | 0.105928303214 | 0.0117864755048 | 0.105929873257 | 0.0191 | 4000 |
| 2 | 0.211667986357 | 0.0121532720785 | 0.105739683143 | 0.0208 | 4000 |
| 3 | 0.316965625591 | 0.0127639166522 | 0.105297639234 | 0.0224 | 4000 |
| 4 | 0.421570987296 | 0.0136202282525 | 0.104605361705 | 0.0245 | 4000 |
| 5 | 0.525205355816 | 0.0147296196312 | 0.103634368520 | 0.0263 | 4000 |
| 6 | 0.627603361737 | 0.0161043750757 | 0.102398005921 | 0.0282 | 4000 |
| 7 | 0.728431979873 | 0.0177550698886 | 0.100828618136 | 0.0300 | 4000 |
| 8 | 0.827262457965 | 0.0196907654366 | 0.098830478092 | 0.0317 | 4000 |
| 9 | 0.923631441187 | 0.0219238253286 | 0.096368983222 | 0.0335 | 4000 |
| 10 | 1.01688515559 | 0.0244724675975 | 0.093253714403 | 0.0353 | 4000 |
| 11 | 1.10622471145 | 0.0273680203335 | 0.089339555860 | 0.0370 | 4000 |
| 12 | 1.19079592024 | 0.030665481166 | 0.084571208790 | 0.0388 | 4000 |

y+ column is DAFoam's own per-print `yPlus min/max/mean` line, the **last** in
each point's segment — exact to ≤ 100 iterations before the point stopped
(Addendum C §15.4 mechanism 2), stated per the reader's own caveat.

### 3.1 Is there a break, kink or non-monotonicity through α = 12? **NO.**

Measured, not asserted:

- **CL strictly increasing** across all 13 points.
- **CD strictly increasing** across all 13 points.
- **dCL/dα strictly DECREASING** at every step, 0.105930 → 0.084571 per degree.
- **Every second difference of CL is negative**, and they vary smoothly from
  −1.902e-04 to −4.768e-03 with no jump: the curve softens, monotonically, with
  no discontinuity anywhere in 0 ≤ α ≤ 12.
- Lift slope as α → 0 is **0.105930 /deg = 6.0693 /rad**, which is **96.60 % of
  2π** — the expected viscous-decambering deficit, consistent with a physically
  sensible attached-flow solution and with the registered 20-chord far-field
  blockage disclosure (§2.2).

**There is nothing at 9° in this data.** The coarse sweeps failed to converge
from 9° upward; arm I here produced α = 9, 10, 11 and 12 with no exception and
no feature in CL, CD or their derivatives. **That is a statement about
CONVERGENCE BEHAVIOUR AND NOTHING ELSE** (§6, `G-NOBAND`), it covers only
α ≤ 12, and **no extrapolation beyond α = 12 is made or licensed here.**
`G-STALL` is honoured: no word of that family is bound to any angle in this
record.

### 3.2 ⚠ CORRECTION TO THE BRIEF: `error NONE` IS NOT `CONVERGED`

The brief this lane worked from described arm I as "13 clean rows … all
`error NONE`". The rows do carry `error NONE` — **that is DAFoam's *exception*
channel, and it is not the convergence criterion.** The frozen reader grades all
thirteen **`NOT CONVERGED`**, and it is right:

- The string DAFoam prints on success —
  `Minimal residual <x> satisfied the prescribed tolerance 1e-08` — appears
  **0 times** in `sweep_I/out/sweep.log`.
- The failure banner (`did not satisfy the prescribed tolerance`) appears **0
  times** too: DAFoam raised nothing, so the driver recorded `err=NONE`.
- **Every point ran the full 4,000 iterations** (`Time = 4000` at each point's
  last print). `primalMinResTol = 1.0e-8` never fired an early stop anywhere.
- At α = 12's last print the per-equation initial residuals were U0 **1.18e-08**,
  p **1.66e-08**, nuTilda **2.80e-08** — *above* the registered 1e-8, still
  falling. The point was stopped by the iteration limit, not by convergence.

**PLANTED-ZERO CONTROL ON THIS ZERO (rule 3), ON REAL BYTES, NOT A FIXTURE.**
A reader that reports "no convergence" must be shown able to report one. The
exact criterion string was counted in three independent real logs on this box:

| log | `Minimal residual … satisfied` |
|---|---|
| `CURRICULUM-AOAI-…-incompressible/out/sweep.log` (coarse, `DASimpleFoam`) | **9** |
| `CURRICULUM-AOAC-…-compressible/out/sweep.log` (coarse, `DARhoSimpleFoam`) | **9** |
| `/home/ubuntu/certonomous-runs/MAAOA/INCOMP/out/trim.log` — **the same L3 wall-resolved mesh, the same patched image, the same solver** | **3** (e.g. `9.997083655914609e-09` at `Time = 2946`) |

The channel sees a real convergence on the very mesh in question. **Its zero on
A1WR arm I is evidence, not blindness.**

**Consequence for the item's question, stated conservatively:** on the coarse
wall-functioned mesh both arms converged to 1e-8 at α ≤ 8 and failed from 9°.
On the wall-resolved L3 mesh the incompressible arm reaches **neither** state
at **any** angle 0–12: it neither satisfies the tolerance nor fails, at 4,000
iterations per point. **The character of the convergence changed, and the 9°
boundary did not reappear as a failure.** That is as far as this data goes.

---

## 4. THE CONTROLS THAT BOUGHT NOTHING

### 4.1 `G-COLD` — **NOT EVALUABLE.** All six cold controls timed out.

| unit | rc | wall_s | deadline | last `Time` | outcome |
|---|---|---|---|---|---|
| `cold_I_4` / `_14` / `_17` | 97 | 3317 each | 3300 | **1800** of 4000 | TIMEOUT, no completed point |
| `cold_C_4` / `_14` / `_17` | 97 | 3316/3317/3316 | 3300 | **1600** of 4000 | TIMEOUT, no completed point |

`rc=97` is the unit's TRUNCATED code (`A1WR_TRUNCATED declared=1 executed=0`),
raised on the container's own `rc=124` from `timeout`. **It is a TIMEOUT, not a
solver failure** — confirming `LAB_STATE` S-27 §8's narrowing of S-26.

**The three incompressible colds were healthy and were killed while succeeding.**
Their bounding census is `Bounding nuTilda> ` **only** — 19 occurrences each,
the ordinary SA lower clip — with **zero** `p`, `rho`, `e` or `U` bounding, and
they were producing sensible coefficients at iteration 1800 (`cold_I_4`
CL 0.4353542303709959, y+max 0.0247; `cold_I_14` CL 1.22902982654255;
`cold_I_17` CL 1.073972575415162). The clock cut them, nothing else.

**`G-COLD` cannot be adjudicated from this data**: it compares a cold point's
iteration count against the continued point's, and no cold point ever finished.
The reader says so rather than guessing —
`cold NOT MEASURED (1800 iters) | continued NOT CONVERGED (4000 iters)`.

**⚠ WHY THEY DIED, MEASURED — AND IT IS NOT THE PHYSICS.** Per-iteration cost,
from each log's own `ExecutionTime`:

| condition | s/iteration | ratio |
|---|---|---|
| arm I sweep, α = 9,10,11 (box quiet after 21:58Z) | **0.4193** | 1.00× |
| arm I sweep, α = 0 (14 containers live) | **1.1540** | **2.75×** |
| `cold_I_4/14/17` (14 containers live) | **1.781 / 1.810 / 1.784** | **4.25–4.32×** |
| `cold_C_4/14/17` (14 containers live) | **2.000 / 1.956 / 1.970** | **4.67–4.77×** |

At its measured rate `cold_I_4` needed **7,126 s** to finish its 4,000
iterations against a **3,300 s** deadline — short by 3,826 s. The deadline was
sized from a quiet-box rate and spent on a box the same item had just filled.

**And it is NOT cpuset stacking (§14.1/§14.2 held).** `docker inspect` shows
every cpuset disjoint: A1WR on cores 8–15 (one core each), MAAOA on 2–7. The
degradation is memory-bandwidth contention across 14 concurrent 130,304-cell
SIMPLE solves. **Transferable, and new: a one-core cpuset isolates a core, not
memory bandwidth. On this box, per-core throughput of a 130 k-cell OpenFOAM
SIMPLE solve degrades ~2.8–4.8× at 14-way concurrency.** No gate in this lab
reads that, and every deadline sized on a solo rate is exposed to it.

### 4.2 `G-CONCURRENCY-BITS` — **`NOT A RESULT`, cause INFRASTRUCTURE**

The alone-copy (`dup_I_4`) launches only after Stage 2's units are reaped
(`a1wr_chain_driver.sh:251-257`). Stage 2 never ended, so the branch was never
reached and no alone-copy exists on disk. The reader reports the absence rather
than papering over it. **This is not a cap-stop** — the arm had 165.0 core-min
of cap left, comfortably above the 55.0 the control needed — so the control was
lost to the poweroff, not to the budget.

---

## 5. THE COMPRESSIBLE ARM — `NOT A RESULT`, AND IT IS NOT A NEAR MISS

All 9 points: `Primal solution failed!`, CL and CD `NA` in the ledger. The
solver's own numbers show why this is not "failed to converge by a little":

| α | CL printed | CD printed | y+max |
|---|---|---|---|
| 0 | 10.4445 | 0.6814 | 1.2486 |
| 1 | 79.8907 | 2.5597 | 1.2133 |
| 2 | −19.1632 | 0.1336 | 1.9187 |
| 3 | −0.5797 | **−1.1188** | 3.0780 |
| 4 | −12.2196 | **−2.1712** | 1.7250 |
| 5 | −55.0980 | **−1.0194** | 0.7312 |
| 6 | 3.3228 | **−4.8659** | 2.6628 |
| 7 | −55.0588 | **−4.8926** | 1.5805 |
| 8 | −80.4237 | **−10.1252** | 4.9806 |

**Negative drag on a 2-D aerofoil section is not a converged-solution artefact;
it is a diverged field.** The bounding census confirms it — across 409 print
steps the arm bound `U` 659+507 times, `p` 385+385, `e` 383+384, `rho` 383+371.
**The compressible arm is held together by field clipping on essentially every
print step, from α = 0 onward.** By contrast arm I's entire census is
`Bounding nuTilda>` × 559 — one per print step, the ordinary SA clip, nothing
else.

`G-YPLUS` reads `GATE FAIL` here (9 of 10 points ≥ 1.0). **Under §3.4 the
wall-resolved claim is withdrawn for those points and the mesh is NOT re-cut** —
that line holds. But the honest reading is narrower still: **these y+ values are
sampled from a diverged field and are not a mesh-adequacy measurement at all.**
The Stage-1 probe, which *is* field-exact, measured y+max **0.9046578506834814**
at α = 18 on this arm — under the gate, and by 10 %.

**A continuation of arm C is refused on physics before it is refused on budget:**
nine more rows of `Primal solution failed!` is not a polar.

---

## 6. THE BUDGET — DERIVED FROM ARTIFACTS, NOT FROM THE LEDGER'S OWN TOTALS

Unit is core-minutes = wall_s × ranks ÷ 60; **np = 1 throughout** (Addendum A
§13.5), so core-min = wall-min. Container walls are `docker inspect
.State.StartedAt/.FinishedAt`; cold walls are also given on the driver's
`CHAIN_LEDGER.tsv` basis, which is ~16 s/unit longer (docker-run overhead the
driver counts and the container does not). The ledger basis is used below
because it is the run's own record.

### 6.1 Per arm, against the registered §7.4 cap of **800 core-min per arm**

| | arm I | arm C |
|---|---|---|
| sweep container wall | 28,146.980 s | 28,146.728 s |
| sweep core-min | **469.1163** | **469.1121** |
| 3 cold controls (ledger) | 9,951 s = **165.8500** | 9,949 s = **165.8167** |
| **arm total** | **634.9663** | **634.9288** |
| registered cap | 800 | 800 |
| **cap consumed** | **79.37 %** | **79.37 %** |
| **REMAINING under the cap** | **165.0337 core-min** | **165.0712 core-min** |

*(Container-measured cold walls give 634.1446 / 634.1359 — the conclusion is
identical either way.)*

The registered §15.5 allocation was `sweep 37,200 s + colds 3 × 3,300 s = 785 ≤
800 core-min per arm`; the sweep consumed 28,147 s of its 37,200 s deadline,
leaving **9,053 s = 150.88 core-min** of in-container deadline unspent — which is
*tighter* than the cap remainder, though a fresh container would carry a fresh
deadline, so the **800-core-min arm cap at 165.03 remaining is what binds.**

### 6.2 What a continuation would cost — measured rate, not extrapolation

Every completed point ran **exactly 4,000 iterations**, so per-point cost is
essentially fixed and this is a measurement, not a model.

| | arm I | arm C |
|---|---|---|
| α = 0 (carries process startup + 14-way contention) | 4,610.976 s = 76.85 core-min | 4,848.617 s = 80.81 core-min |
| mean wall per point, α ≥ 1 | **1,860.15 s = 31.00 core-min** | **2,775.29 s = 46.25 core-min** |
| mean of the last 4 points | 1,720.16 s = 28.67 core-min | 2,715.03 s = 45.25 core-min |
| points a continuation needs | **6** (α 13–18) | **10** (α 9–18) |
| **cost at the α ≥ 1 mean** | **186.02 core-min** | **462.55 core-min** |
| cost at the most favourable (last-4) rate | 172.02 core-min | 452.50 core-min |
| **REMAINING under the cap** | **165.03** | **165.07** |
| **fits?** | **NO — over by 20.99** (7.0 even at the best rate) | **NO — over by 297.5** |

**Neither continuation fits, on the most favourable arithmetic available.**
The measured 4,000-iterations-per-point floor means the arm-I figure cannot
improve with luck: six points at 4,000 iterations each cost what they cost.

### 6.3 The exceedance claim, self-checked (Sanaa 2026-09-03 item 4)

Derived independently from `docker inspect`, `CHAIN_LEDGER.tsv`, the two
`LEDGER.tsv` files and the shutdown journal — not from any relayed figure. The
supervisor's figures were **~166 remaining, ~183 needed (I), ~462 needed (C)**.
Measured here: **165.03 / 165.07 remaining, 186.02 needed (I), 462.55 needed
(C)**. The arm-C figure matches to three digits. The arm-I need is **186.02, not
183** — the supervisor's number was ~1.6 % optimistic and in the direction that
*understates* the exceedance. **The conclusion is unchanged and the margin is
slightly worse than reported.**

### 6.4 Waste, named separately and never folded into any ratio

| # | waste | core-min | derived $ | cause |
|---|---|---|---|---|
| 1 | six cold controls, `rc=97` TIMEOUT, **zero completed points, zero coefficients** | **331.6667** | $0.28358 | deadline sized on a quiet-box rate (§4.1) — *not* solver failure |
| 2 | **INFRASTRUCTURE — poweroff.** In-flight α = 13 (I) and α = 9 (C) solver work discarded: 1,190.14 s + 1,071.93 s | **37.7012** | $0.03224 | `shutdown -h now`, 02:25:05Z |
| 3 | fire 2 (Addendum E) — two probes, container startup, **zero solver iterations** | 1.02 | $0.00087 | two instrument defects, both repaired before fire 3 |
| 4 | fire 1 (Addendum D) — aborted inside `stage_unit()` | 0.00 | $0.00000 | cleanup glob ate `0.orig`; the point-of-use assert caught it |
| | **TOTAL WASTE** | **370.39** | **$0.31669** | |

**Item #2 is INFRASTRUCTURE and is named as its own line.** It is not
misprediction, not contention and not solver behaviour, and it is not absorbed
into any actual/predicted ratio anywhere in this record or in
`docs/COST_CALIBRATION.md`.

Dollars throughout are **DERIVED, NOT MEASURED**, at the owner-stated
$0.0513/core-h (c7a.4xlarge); `cost_basis` = **reported-by-owner** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

### 6.5 Item roll-up

| stage | registered | actual (core-min) | ratio | derived $ |
|---|---|---|---|---|
| Stage 0 | cap 40 | **0.4000** | 0.0100 | $0.00034 |
| Stage 1 | ~65 est., cap 120 | **31.7500** | 0.4885 vs est. / 0.2646 vs cap | $0.02715 |
| Stage 2, arm I | 424.5 (Add. A §13.2) / 560 (§7.3), cap 800 | **634.9663** | 1.4958 / 1.1339 / 0.7937 vs cap | $0.54290 |
| Stage 2, arm C | 442.9 / 585, cap 800 | **634.9288** | 1.4336 / 1.0853 / 0.7937 vs cap | $0.54286 |
| aborted fires 1–2 | — | 1.02 | — | $0.00087 |
| **ITEM** | ceiling **1,800** | **1,303.07** | **0.7239 of ceiling** | **$1.11412** |

**⚠ EVERY STAGE-2 RATIO ABOVE IS AGAINST A TRUNCATED DELIVERY AND MUST NOT BE
READ AS AN ESTIMATE-QUALITY FIGURE.** The estimate priced 19 points + 3 colds
per arm; the actual delivered 13 points + 0 colds (I) and 9 non-results + 0
colds (C). The honest estimate-quality reading is on the **transferable unit**:

| | predicted s/iteration (Add. A §13.2, at 130,304 cells, np = 1) | **measured, quiet box** | ratio |
|---|---|---|---|
| arm I (α 9–11) | 0.35625 | **0.41930** | **1.177** |
| arm I (α 11–12, window comparable to C below) | 0.35625 | **0.44023** | 1.236 |
| arm C (α 7–8, quiet box) | 0.37163 | **0.67930** | **1.828** |

**The per-iteration anchor was 18 % low on the incompressible arm and 83 % low
on the compressible arm.** And §7.2's finding that the two solver classes "agree
to 4.3 % per iteration" — measured at 4,032 cells — **does not transfer to the
wall-resolved mesh**: in directly comparable quiet-box windows the compressible
arm costs **1.543×** the incompressible per iteration at 130,304 cells. That
finding is this item's most transferable cost result and it is registered here
against the next estimate.

Calibration rows land in `docs/COST_CALIBRATION.md` per rule 12 and §7.5.

---

## 7. y+ — MEASURED, AGAINST A PREDICTION WRITTEN DOWN FIRST

| | predicted at L3 (Amdt. 1 §12.4) | **measured** | source |
|---|---|---|---|
| incompressible, α = 18 | 0.026 | **0.0367936898591** | Stage-1 probe, field-exact |
| incompressible, α = 12 | — | **0.0387516337878** | sweep last print |
| compressible, α = 18 | 0.203 | **0.9046578506835** | Stage-1 probe, field-exact |

**The incompressible prediction was ~29 % low; the compressible prediction was
low by 4.46×**, landing the binding arm within 10 % of the `G-YPLUS` threshold
instead of the registered 19 % margin. §12.4 named the incidence factor of 1.8
as "the weakest link in the chain" — it is where the miss lives, and the
registration's own disclosure is scored here rather than quietly dropped.

**On the incompressible arm the wall-resolved claim holds and is measured**:
y+max rises smoothly 0.0175 → 0.0388 across α 0 → 12, ~26× under the threshold
at the worst point.

---

## 8. THE ON-DISK STATE — WHY NO FAITHFUL CONTINUATION EXISTS

Independent of the budget. Every field in both sweeps' `case/0/` and
`case/0.orig/` was decompressed **to a scratch copy, never in place**, and its
`internalField` classified.

### 8.1 `sweep_I/case/0/` is **(c) A MIXED, INCONSISTENT STATE** — neither a converged restart point nor a cold start

| field | `internalField` | value / count | mtime (UTC) |
|---|---|---|---|
| `U.gz` | **nonuniform** `List<vector>` | **130,304** | **2026-09-03T02:05:19Z** |
| `p.gz` | uniform | 0 | 2026-09-02T18:36:13Z |
| `nut.gz` | uniform | 4.5e-05 | 2026-09-02T18:36:13Z |
| `nuTilda.gz` | uniform | 4.5e-05 | 2026-09-02T18:36:13Z |
| `k`, `omega`, `epsilon` | uniform | 0.015 / 100 / 0.14 | 2026-09-02T18:35:58Z |

`0.orig/` is uniform in every field, as staged.

**Only the velocity field survived, and it is already stamped for the wrong
angle.** Measured from the file itself:

- the far-field interior cells read `(9.773964…, 2.076975…)` → |U| **9.9922**,
  **α = 11.99695°** — this is the α = 12 converged velocity field;
- the `inout` patch `inletValue` reads `(9.743700647852352 2.24951054343865 0)`
  → |U| **10.000000000**, **α = 13.000000°**.

So `0/U` was written at 02:05:19Z as part of setting up **α = 13**, carrying the
α = 12 interior out with it, while `p`, `nut` and `nuTilda` were never
rewritten and still hold their 18:36:13Z staging values.

**A restart from this directory would be the α = 12 velocity field, under the
α = 13 inlet, with a ZERO pressure field and the SA working variable at its
uniform freestream value everywhere — i.e. the entire turbulence state of a
wall-resolved boundary layer thrown away.** That is not the predecessor's
converged state, and §5 Stage 2's design — "each point inheriting its
predecessor's converged state" — could not be honoured from it. A point started
there and labelled `CONTINUED` would carry a false label, which is precisely
what `G-COLD` exists to catch.

### 8.2 `sweep_C/case/0/` is **(b) A COLD START**

Every field uniform: `U (100 0 0)`, `p 101325`, `T 300`, `alphat 1e-4`,
`nut`/`nuTilda` 4.5e-05, `k 1.5`, `omega 1e4` — identical in substance to
`0.orig/`. `0/U.gz` was rewritten at 02:07:17Z with the α = 9 inlet
(`inletValue (98.76883405951378 15.64344650402309 0)`, |U| 100.000000000,
**α = 9.000000°**) but its interior is still uniform `(100 0 0)`. Consistent
with Addendum C §15.4 mechanism 2: `renameSolution` skips failed primals, and
**every** arm-C primal failed, so no converged interior ever reached disk.

### 8.3 No other checkpoint exists anywhere

Searched with `find` on explicit paths (**not** `grep -r`, which on this box is
ugrep and silently skips gitignored trees):

- `processor*` directories under `/home/ubuntu/certonomous-runs/A1WR`: **0**.
- Time directories under any `case/`: only `0` and `0.orig` for both sweeps and
  all six colds. (The two Stage-1 probes carry a `1500` dir — Stage-1 artifacts,
  not restart points for Stage 2.)
- `*.bin`, `*restart*`, `*.pkl`, `*.pckl`: **none**. The only `.dat` files are
  `postProcessing/yPlus*/0/yPlus.dat`.
- 582 files, 144 MB total under `STAGE12/`.

**CONCLUSION: there is no usable checkpoint for either arm.** The continuation
state was in memory and died with the process at 02:25:05Z.

---

## 9. WHAT THIS RECORD DOES NOT CLAIM

- **No grid-converged value.** The L3 family has no Roache triple (`A1WR-GC` is
  a separate, unrun rung). `G-NOBAND`: nothing above carries a band.
- **No stall or separation claim of any kind is bound to any angle** (§6,
  `G-STALL`), and none may be derived from this record.
- **No extrapolation beyond α = 12**, and no statement about α 13–18 on either
  arm.
- **No adjoint claim.** `useWallFunction: False` was exercised on the primal
  only; whether DAFoam's adjoint differentiates correctly through
  `nutLowReWallFunction` is untested here (§4.1).
- **No convergence claim for any point.** The frozen reader records
  `CONVERGED 0` on both arms.
- **No `G-COMPLETE` verdict** (§2.3), and none is supplied by hand.
- **No comparison to the coarse sweeps free of the disclosed second variable**:
  those ran the SHIPPED image, these the PATCHED `dafoam-idwarp-rot:v1`
  (Addendum C §15.2, on Sanaa's explicit order).

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---

## 10. ARTIFACTS

| what | path |
|---|---|
| run root | `/home/ubuntu/certonomous-runs/A1WR/STAGE12/` |
| polars | `sweep_{I,C}/out/LEDGER.tsv` |
| solver logs | `sweep_{I,C}/out/sweep.log`, `cold_*/out/sweep.log` |
| unit ledger | `CHAIN_LEDGER.tsv`; in-flight roster `inflight.txt` |
| Stage-1 gate | `stage1_gate.json`, `stage1_gate.out` |
| driver trace | `…/wall_resolved_aoa_polar/{STATUS.A1WR_chain.log,launcher.queue.out}` |
| **reader output, written by the frozen reader on rc = 0** | `A1WR_POINTS_I.json`, `A1WR_POINTS_C.json` (both in the run root; created by this grading run — the grading path's own output, disclosed) |
| kill forensics | `journalctl -b -1`, `last -x`, `docker inspect` on the eight `a1wr_*` containers |

**Written 2026-09-03 by lab-lane (dafoam). No solver, container or queue entry
was launched, released or moved by this lane; the run tree was read-only apart
from the frozen reader's own two JSON outputs.**

---
---

# ADDENDUM 1 — 2026-09-03 — SUPERVISOR'S CHECK 4, TWO CORRECTIONS OWNED UPWARD, AND TWO FINDINGS RESTATED FOR CROSS-TEAM CITATION

**`lines whose number changed above this section: 0`**

Nothing above this line has been edited. Appended after the supervisor performed
their `SUPERVISION_CHARTER` §3 check 4 personally on the successor draft.

## 11. TWO CORRECTIONS THE SUPERVISOR RECORDS AS THEIRS

Recorded here at their instruction, in their name, because a correction that is
only made in a message is not made.

1. **The reproduction-control premise was the supervisor's and it was false.**
   The successor's control was directed on the premise that *"a converged steady
   solution should be history-independent, so agreement corroborates that the
   continuation label was live."* **A1WR's α = 12 point is NOT CONVERGED** (§3.2),
   so a cold α = 12 compared against it is not two roads to one fixed point but
   **two roads to iteration 4,000**, which no theory guarantees. A band sized on
   the converged anchors would have been roughly four orders too tight and **would
   have manufactured a false finding.** The two-limb `G-REPRO` now registered in
   the successor draft replaces it.

2. **"13 clean rows, all `error NONE`" was the supervisor's reading and it was
   wrong** — the sixth instance in two days of the same failure, a column read
   outside its scope and called clean. `error NONE` is DAFoam's **exception**
   channel; the convergence criterion is a different string entirely, and the
   frozen reader records **`CONVERGED 0` on both arms** (§3.2). What makes that
   zero admissible is the planted control on **real bytes**: the criterion string
   is counted **9 / 9 / 3** times in the coarse AOAI log, the coarse AOAC log and
   `MAAOA/INCOMP/out/trim.log` — the last on **this mesh, this image, this
   solver**. A zero from a reader shown able to see a non-zero.

## 12. LAB-WIDE FINDING, STATED IN ITS GENERAL FORM

Section 4.1's measurement is not an A1WR fact and is restated here so it can be
cited outside this item:

> **A one-core cpuset isolates a core. It does not isolate memory bandwidth.**
>
> A1WR's cpusets were all **disjoint** — A1WR on cores 8–15, MAAOA on 2–7,
> **verified by `docker inspect`, not assumed** — and per-core throughput of a
> 130,304-cell OpenFOAM SIMPLE solve still degraded **2.75× to 4.77×** under
> 14-way concurrency, one np = 1 process per core on a 16-vCPU box.
>
> **No gate in this lab reads this.** `G-PLACEMENT`-class cpuset-disjointness
> readings are **necessary and not sufficient**. Every in-container deadline in
> the lab is sized on a solo rate, and **331.6667 core-min bought zero physics**
> learning it when all six of A1WR's cold controls timed out — `cold_I_4` needing
> **7,126 s** at its measured 1.781 s/iteration against a **3,300 s** deadline.

The successor registers `G-CONCURRENCY-PRECOND` as a **launch gate** on this
finding, with a census that must itself be proved able to return a non-empty
answer before its empty answer is accepted.

## 13. REGISTERED GATES WITH NO IMPLEMENTATION — STATED PRECISELY ENOUGH TO BE CITED BY A CROSS-TEAM AUDIT

§2.3 records this for `G-COMPLETE`. Restated here in citable form, with the
demonstrating command beside each instance, because the general question — **how
many registered gates lab-wide have no implementation** — is being referred
upward by the dafoam supervisor.

| registered gate | registered at | implementation | demonstration | consequence |
|---|---|---|---|---|
| `G-COMPLETE` | `A1WR_PREREGISTRATION.md` §9 — rule 4 in all clauses, "refuse (exit 2) rather than degrade" | **NONE** | `grep -c 'G-COMPLETE' cases/dafoam/ladder-a/A1/wall_resolved_aoa_polar/a1wr_read.py` → **0** | A1WR's completeness gate is **unadjudicated to this day**. Its truncation, 13 of 19 declared points, is reported by the reader as a bare `COUNT MISMATCH` that refuses nothing |
| `G-CAPS` | same table — "every stage within its registered cap; cap-stop ⇒ `NOT A RESULT`" | **PROSE ONLY** — one conditional sentence, no arithmetic | `grep -n 'G-CAPS' …/a1wr_read.py` → **one line**, inside the `G-CONCURRENCY-BITS` absence note | A1WR's cap accounting was done by hand at grade time and is labelled in §6 as **not from the grading path** |
| MAAOA §4's pre-compute selftest pass | `.../fixed_lift_mach_sweep/` registration | asserted, **no artifact dated before compute** | supervisor's other lane, 2026-09-02 | — |

**Three registered checks in one family that exist only as text.** Stated as a
count of instances found, not as an estimate of the lab-wide total, which this
record does not know.

## 14. THE FIXTURE DEFECT IS A CLASS, NOT AN INCIDENT — CENSUS FILED

§2.1 records that `a1wr_read.py` prefers a live artifact of the graded run as its
control fixture and escaped only because nothing converged. A census of **all 468
`.py` files under `cases/dafoam/`** was run on the supervisor's order and is filed
at **`docs/dafoam/GRADING_FIXTURE_CENSUS.md`**.

**Result: six instruments AFFECTED, five of them with the defect LIVE in the
grading of record** — `aoa_read.py` (both AOAI and AOAC, each archived output
reading `born against : REAL RUN ARTEFACT` with its source path and sha256),
`maaoa_read.py`, `d19m_grade.py` and `d19o_grade.py` (both recording
`"target_kind": "REAL"`), plus `so3af_read.py` affected by explicit design and
**NOT EVALUABLE** for liveness. `a1wr_read.py` is the sixth, affected and not
live. Three instruments were checked by hand and found **CLEAN**.

**⚠ The coarse α-polar is inside the blast radius**: `aoa_read.py` graded both
coarse arms, and those gradings produced the *"same boundary to the degree across
a tenfold Reynolds difference"* finding that §8 of the pre-registration quotes and
that this whole item exists to test. **This record makes no claim about that
finding.** It records that its grading instrument carries the defect that voided
MAAOA, that the question is open, and that it belongs to the supervisor —
`VERIFICATION_CHARTER` §2d/§2d.1 rulings are not a lane's to make. **Nothing was
repaired.**

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---
---

# ADDENDUM 2 — 2026-09-03 — §2.3 AND §13 ARE WITHDRAWN, AND THE MECHANISM BEHIND `CONVERGED 0` IS NOW MEASURED

**`lines whose number changed above this section: 0`**

Nothing above this line has been edited.

## 15. WITHDRAWN: `G-COMPLETE` AND `G-CAPS` **ARE** IMPLEMENTED

**§2.3 and §13 of this record are withdrawn.** They claimed A1WR registers
`G-COMPLETE` and `G-CAPS` and never implemented them, on the evidence that
`grep -c 'G-COMPLETE' a1wr_read.py` returns 0. **That inference was wrong.**

Verification's §2v ruling is the standard: *"a gate is implemented where it must
be, not where the reader is — the grading path is every frozen instrument the
registration names, not the one file with `analyse_` in its name."* Five of nine
flags in that referred class were false accusations. **These were two more, and
they were this lane's.**

Checked against every frozen instrument A1WR's registration names:

| gate | implemented at | the line |
|---|---|---|
| `G-COMPLETE` | `a1wr_runScript_incomp.py:357-362` | `AOA_SWEEP_TRUNCATED n_declared=%d n_executed=%d -- NOT a completion`, then `exit(97)` |
| `G-COMPLETE` | `a1wr_cmd.sh:68-71` | `A1WR_COUNTS declared=… point_end_markers=…`, counted off `^AOA_POINT_END `; PROBE branch `exit 97` on a missing endTime state |
| `G-CAPS` | `a1wr_chain_driver.sh:251-257` | `'YES' if $I_SPEND + 55.0 <= $ARM_CAP_MIN`, else `A1WR_DUP_CAPSTOP … A cap-stop is NOT A RESULT on that control.` |

**`G-COMPLETE` fired LIVE**: all six cold controls carry the truncation marker
and exited **97**. It did not fire for the two sweeps because the SIGTERM killed
both containers before the unit-end block ran — `logs/sweep_{I,C}.docker.log` do
not exist and `AOA_SWEEP_END` appears **0** times in either sweep log. **A gate
whose host process was killed is not an unimplemented gate.**

**What survives, narrowly:** `a1wr_read.py` does not itself adjudicate either
gate. Under §2v that is **CLEAN**, not a suspicion. **The A1WR sweeps'
completeness was never adjudicated by anything** — because the adjudicating
process was killed, which is §1's infrastructure fact and not an instrument
defect. §6's cap arithmetic in this record remains hand-derived and is still
labelled as such; that labelling was correct and is unaffected.

## 16. THE MECHANISM BEHIND `CONVERGED 0` — MEASURED, AND IT IS THE MESH

§3.2 established that no point converged and proved the channel could see a real
convergence. **The cause is now measured, and it is not the flow.**

The L3 mesh's two bounding planes are **`type symmetry`, not `empty`** —
`constant/polyMesh/boundary`, **130,304 faces each**, i.e. every cell's front and
back face. OpenFOAM therefore reports, in the sweep's own log:

> `Mesh has 3 solution (non-empty) directions (1 1 1)`

and **assembles a z-momentum equation on a mesh one cell thick.** `U2` then
floors instead of converging. Measured across all 559 print steps of
`sweep_I/out/sweep.log`, minimum `initRes` reached by each channel:

| channel | minimum `initRes`, whole run |
|---|---|
| U0 | 1.429824e-09 |
| U1 | 1.738461e-09 |
| p | 2.589369e-09 |
| nuTilda | 8.288244e-09 |
| **U2** | **3.238410e-08** |

**Every channel but `U2` reaches below 1e-8. `U2` never does.** It is the largest
last-iteration residual at **12 of the 14 points** (α = 0 and α = 1 excepted,
where U1 dominates).

**`3.238e-08` sits ABOVE the registered `primalMinResTol = 1.0e-8`. These points
could not have converged. The `CONVERGED 0` of §2 is a property of the mesh
configuration, not of the physics and not of the operating point** — and it is
arithmetic, not an interpretation.

Corroborated elsewhere and credited as external: `MAAOA INCOMP` (`U2` 2.48e-08)
and D19T; on the coarse 4,032-cell mesh the same floor sits at ~1.7e-10, so **it
scales with the mesh**, which is why the coarse sweeps could converge to 1e-8 and
this one could not. The mechanism is killed for the compressible arm, where `p`
at 9.29e-01 dominates and the failure is the separate one N-C9 documents.

**WHAT THIS DOES AND DOES NOT CHANGE.** It does not change one number in §3's
polar, and it does not change the item verdict: the readings stand exactly as
recorded. It does not license loosening the tolerance retrospectively — that
would be result-shopping on a closed freeze. **And it does not tell us whether
CL or CD are contaminated: that is UNMEASURED**, and §9's list of things this
record does not claim is extended by one line —

> **no claim, in either direction, about whether the spurious third solution
> direction affects the published CL and CD.**

A separate **one-variable** item registers the `empty`-versus-`symmetry` control,
including whether the coefficients move at all. It is not folded into the tail
successor, whose `G-REPRO` control is only valid against A1WR's own configuration
and would be broken by changing the patch type. **One variable per item is the
standard that caught this.**

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**

---
---

# ADDENDUM 3 — 2026-09-03 — THE OTHER HALF OF THE MECHANISM: A 100× DEAD BAND, READ FROM THE INSTALLED SOURCE

**`lines whose number changed above this section: 0`**

Nothing above this line has been edited. This completes §16, and it closes the
loop on the correction that opened this record: **why the LEDGER read
`err=NONE` on thirteen rows that contained zero convergences.**

§16 established that `U2`'s residual floors at **3.238410e-08**, above the
registered `primalMinResTol = 1.0e-8`, so the points could not converge. **It did
not explain why DAFoam also never raised a failure.** Read from the installed
source in the patched image — not inferred:

| | `DASolver.C` | criterion | threshold with this item's registered values |
|---|---|---|---|
| **early stop / `satisfied` line** | `:188`, `:192-194` | `primalMaxRes < primalMinResTol` | **< 1.0e-8** |
| **`Primal solution failed!`** | `:2745-2753` | `primalMaxRes / primalMinResTol > primalMinResTolDiff` | **> 1.0e-6** |

`primalMinResTolDiff` is registered at **100** (`A1WR_PREREGISTRATION.md:318`),
so **there is a deliberate 100× DEAD BAND between the two thresholds**, and the
measured floor lands inside it:

> **3.238410e-08 = 3.24× the tolerance, and 0.0324× the failure threshold.**

**A1WR's arm I could NEITHER converge NOR be flagged as failed.** DAFoam printed
nothing — no `satisfied` line, no failure banner — the driver caught no
exception, and the ledger recorded `err=NONE`. **That is the entire mechanical
explanation of the "13 clean rows, all `error NONE`" reading that Addendum 1 §11
records as the supervisor's correction, and it vindicates the frozen reader:
`NOT CONVERGED` was the right label and `err=NONE` was never evidence against
it.**

**Bearing on Sanaa's 2026-09-03 taxonomy:** she names *"a residual print that
isn't the max over equations"* as a blocking physics fix. **This one is the max**
— `primalMaxRes` is reset to `-1e10` each iteration (`DASolver.C:224`) and
maximised over the equation set — so that defect does **not** apply here. The
defect that does apply is the patch identity, and it is fixed in the successor,
not retrofitted onto this closed freeze.

**Nothing in this addendum changes a number, a gate or the verdict.** No
tolerance is relaxed retrospectively, and `primalMinResTolDiff` is not
re-litigated on a closed item.

**NOTHING IN THIS ITEM IS FILED, SENT, UPLOADED OR POSTED ANYWHERE.**
