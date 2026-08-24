# W4 stage O2 re-buy — results: incomplete factorization is singular on the hump at all four settings, the complete one does not fit in 20 GiB, and the §3 decision is still `PENDING`

**Status: NOT FILED ANYWHERE. Nothing here is sent, posted, uploaded, registered, emailed or
commented outside this box.** Filing is Sanaa's decision alone (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **NOT FILED.**

Graded against the frozen pre-registration `cases/dafoam/ladder-b/W4_O2_REBUY_PREREGISTRATION.md`,
committed **alone** at `8d48fd46cb7a0e037d8871e63d241f11c2861153` **before any compute**, blob
`47e2988efca221401f0e3b25b463a0aa155e0774`. Re-hashed against the committed blob before grading:
**equal**. Run root `/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/`, log
`logs/o2_rebuy_hump_lu_20260823T211207Z.log`.

---

## 1. Verdicts

| item | verdict | one line |
|---|---|---|
| **The §3 decision rule** | **`PENDING`** | **zero** `splu` factorizations completed — the registered `PENDING` row, fired exactly as written |
| **`spilu` × 4 settings** | **measured, 4 of 4 `Factor is exactly singular`** | the hump's incomplete factorization is singular at every registered strength — **new, and it is the CBFS signature** |
| **`splu` × 3 pivot thresholds** | **`NOT A RESULT`** | the first threshold was **killed by the cgroup at 20.0 GiB** before completing; no threshold ever returned |
| **The item's own conduct** | **stopped by memory, at a registered cap, as registered** | rc **137**, peak **exactly 20.0 GiB**, 900 s wall, 15.00 core-min against a 50.0 core-min ceiling |

**The singular-vs-ill-conditioned-vs-merely-slow question is STILL NOT ANSWERED**, and it is now
unanswered for a **different reason than last time**. The parent item
(`W4_M1M2_RESULTS.md:22`) returned `PENDING` because O2 was never launched on a budget rule. **This
item launched it, and the operator's exact LU did not fit in the memory the item was allowed to
give it.** That is a harder and more informative failure, and it is the one thing this item bought
that nobody had.

**The registered consequence — *"if M1 returns singular or catastrophically ill-conditioned, M4 and
M5 are not bought"* — DID NOT FIRE, because M1 still returns neither.** M4 and M5 remain unbought
for the same reason as before: **M1 has not decided.** That distinction is load-bearing and is not
to be collapsed.

---

## 2. The headline measurement: the hump's incomplete factorization is singular at all four settings

`logs/o2_rebuy_hump_lu_20260823T211207Z.log:1-7`, printed by the unmodified frozen script:

```
n=517240 nnz=33662810 ||b||=1.094138002900e+00

=== ILU strength sweep: does incomplete factorization EVER succeed here? ===
  drop_tol=0.01   fill=3   FAILED: Factor is exactly singular
  drop_tol=0.001  fill=5   FAILED: Factor is exactly singular
  drop_tol=0.0001 fill=5   FAILED: Factor is exactly singular
  drop_tol=1e-05  fill=10  FAILED: Factor is exactly singular
```

**Line 1 is the identity check and it passes on every field.** `n = 517240` is frozen prediction
M1-P2; `nnz = 33662810` is the value measured at stage O1 (`W4_M1M2_RESULTS.md:117`);
`‖b‖₂ = 1.094138002900e+00` is the solver's own printed iteration-0 residual to 13 digits
(`W4_M1M2_RESULTS.md:115`). **The matrix this factorization was run on is the hump's real adjoint
system**, not an unrelated one, and the reader that says so is the frozen script itself.

**What lines 4-7 establish.** The incomplete factorization of the hump's assembled `dRdWTPC` hits an
**exact zero pivot** at every registered strength across four decades of drop tolerance and fill
factors 3 → 10. This is the same result CBFS gave, 4 of 4
(`/home/ubuntu/certonomous-runs/W4-cbfs-reordering/analysis_final.log:4-7`;
`cases/dafoam/PROOF.md:2774-2777`), reproduced now on the hump for the first time — and it is
mechanism-level agreement with the hump's own `-9 DIVERGED_NANORINF` at iteration 0, which this
programme reproduced deliberately twice on 2026-08-23 (`W4_M1M2_RESULTS.md:48-49`).

**What lines 4-7 do NOT establish, and this is the whole reason §3 says `PENDING`.** `spilu` failing
is **one half** of D-MERELY-SLOW. The other half — that `splu`, the *complete* factorization with
pivoting, **succeeds** — is what separates *"the preconditioner is the problem"* from *"the operator
is singular"*. **That half did not run to an answer.** Under §3 as frozen, `spilu` failing at 4 of 4
is compatible with **D-SINGULAR** and with **D-MERELY-SLOW** alike, and nothing here chooses between
them.

---

## 3. Why `splu` never returned: the cgroup kill, at exactly the registered cap

`logs/o2_rebuy_hump_lu_20260823T211207Z.log:9-12`:

```
=== the same factorization WITH pivoting (splu) as the control ===
bash: line 1:   245 Killed                  python -u /scripts/analyze_dump3.py
CGROUP_PEAK_BYTES=21474836480
O2 REBUY rc=137
```

| reading | value |
|---|---|
| `rc` (from `PIPESTATUS[0]`, as registered) | **137** = SIGKILL = **the cgroup OOM kill**, the §6 registered reading |
| `CGROUP_PEAK_BYTES` | **21,474,836,480 B = exactly 20.0000 GiB** — the cap, to the byte |
| wall | `21:12:13Z` → `21:27:13Z` = **900 s** = **15.00 core-min** at `--cpus=1` |
| `splu` rows completed | **0 of 3** |

**The kill landed inside the first `diag_pivot_thresh = 0` factorization.** The section header at
`:9` printed and no `splu` row ever followed it. `python -u` is why the header and all four `spilu`
rows survived the kill at all — the registered, disclosed deviation earning its place.

**The peak read is exactly the cap, and that is a censoring, not a coincidence.** `memory.peak`
cannot exceed the limit that killed the process; **20.0 GiB is a lower bound on what the exact LU
wanted, not a measurement of what it needed.** The true requirement is `> 20.0 GiB` by an unknown
margin. The `bash -lc` wrapper survived (only the largest process in the cgroup was killed), which
is why the peak line printed at all rather than being lost with the child.

### 3a. Evidence that bears on `nnz(L+U)` but is NOT the registered instrument — quarantined

Reported because it exists, and quarantined because O2R-P1 named the `splu`-printed
`nnz(L+U)` and nothing else. **No verdict is drawn from any of it.**

SuperLU had committed ≥ 20.0 GiB at `diag_pivot_thresh = 0` before dying. Subtracting the CSR and
CSC copies of a 33,662,810-nnz matrix (≈ 0.82 GiB) and page cache for the 410,160,624 B of dump
files charged to the same cgroup (≤ 0.39 GiB) leaves **≥ ~18.8 GiB** inside SuperLU. At CBFS's own
7.7 B/nnz that is ≳ 2.6e9 nnz; at a 12 B/nnz double-plus-int32 accounting, ≳ 1.7e9.

**Both figures sit above the frozen O2R-P1 / M1-P10 band's top of 1.35e9.** This is **not** promoted
to a MISS on O2R-P1, for a stated reason: SuperLU's resident set includes realloc slack, the
elimination tree, permutation vectors and panel workspace, none of which is `nnz(L+U)`, and the
margin between "committed 20 GiB" and "the factors contain N nonzeros" is not calibrated on this
box. **O2R-P1 is `PENDING`, not MISS**, and this paragraph is a hint for whoever prices the re-run —
not a measurement.

CBFS is the contrast that makes it worth writing down: **CBFS's complete LU finished inside a
`--memory=10g` container** (`/home/ubuntu/certonomous-runs/W4-cbfs-reordering/chain_analysis.sh:6`)
at 3.22e8 – 3.90e8 nnz(L+U). **The hump did not finish inside twice that.**

---

## 4. Per-prediction grading

Bands are as frozen. **A MISS is reported as a miss and is not re-banded**
(`DAFOAM_CHARTER.md` §12). The distinction between **MISS** and **PENDING** is applied strictly:
a prediction whose instrument never reported is `PENDING`, not a MISS, and a prediction whose
instrument reported a value outside the band is a MISS however sympathetic the cause.

| id | prediction | measured | grade |
|---|---|---|---|
| **O2R-P1** | `nnz(L+U)` at highest completed threshold, 8.0e8 – 1.35e9 | no `splu` completed | **PENDING** |
| **O2R-P2** | `splu` completes at **exactly 3 of 3** thresholds | killed inside the first threshold: it neither completed **nor** raised | **PENDING** — see below |
| **O2R-P3** | `min ‖Ax−b‖/‖b‖` ∈ 1.0e-13 – 1.0e-7 | no `splu` completed | **PENDING** (the frozen rule says so explicitly) |
| **O2R-P4** | `spilu` singular at **exactly 4 of 4** | **4 of 4** | **HIT** |
| **O2R-P5** | wall **1500 – 2700 s**, and the run **completes** | **900 s**, and it did **not** complete | **MISS** — both clauses fail |
| **O2R-P6** | peak cgroup high-water **8.0 – 20.0 GiB** | **≥ 20.0 GiB** (right-censored at the cap) | **MISS (high)** |
| **C-P1R** | the scipy exact-LU **exceeds 25.0 core-min** | **15.00 core-min**, stopped by memory rather than by time | **MISS** — see §4b |

**Also graded, because this item is the instrument the parent's frozen prediction was waiting for:**

| id (frozen at `c8254a4a` §2a) | prediction | measured | grade |
|---|---|---|---|
| **M1-P8** (`W4_M1M2_PREREGISTRATION.md:78`) | `spilu` raises `Factor is exactly singular` at **≥ 3 of 4** | **4 of 4** | **HIT** |
| **M1-P9** (`:79`) | `splu` completes at ≥ 1 threshold with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-9` | no `splu` completed | **PENDING** (unchanged) |
| **M1-P10** (`:80`) | `nnz(L+U)` 8.0e8 – 1.35e9 | not printed | **PENDING** (unchanged) |

### 4a. Why O2R-P2 is `PENDING` and not a MISS, stated before anyone can call it a save

O2R-P2 predicted **exactly 3 of 3** `splu` completions. Zero completed. It would be arithmetically
defensible to write **MISS** — and it would be **wrong**, because the quantity O2R-P2 names is
*"the number of thresholds at which `splu` **completes**"*, and completion is measured against
**termination**. The first threshold did not terminate: it was killed. A threshold that was killed
is not a threshold that failed to complete on the operator's account; it is a threshold that was
never asked the question to the end.

**The frozen text is what decides this, not this paragraph's reasoning.** §3, inherited verbatim,
routes a stop with **zero completed `splu`** to `PENDING` and not to any verdict — and O2R-P2's own
row grades the same quantity §3 reads. Calling it MISS would report a fact about this lane's memory
cap as a fact about the hump's matrix.

**And the opposite trap is named too.** This is not a licence to grade every inconvenient outcome
`PENDING`. O2R-P5 and O2R-P6 are graded **MISS** in the same table, on the same run, and O2R-P6's
MISS is the one that cost this item its answer.

### 4b. C-P1R is a MISS, and its hypothesis is STILL untested — for the second time

`W4_M1M2_RESULTS.md:199-204` recorded C-P1 as *"a MISS whose hypothesis is still open, and O2's
re-buy is the test."* **The re-buy ran and the hypothesis is still open.**

C-P1R predicted the scipy exact-LU would exceed 25.0 core-min. Measured: **15.00 core-min** — a
clean MISS on the number. But the factorization **did not finish**; it was stopped by a memory cap
at an unknown fraction of its work. **15.00 core-min is a lower bound on the exact LU's true cost,
not its cost.** The honest position:

- **The prediction is MISS.** It named a threshold and the measured spend fell below it. It is not
  re-banded and it is not converted to `PENDING` to protect it.
- **The hypothesis behind it is untested, twice over.** First the factorization never ran; now it
  ran and never finished. **Two MISSes, zero tests.**
- **A third attempt should not be sold as "the test" a third time** without changing the thing that
  stopped it. The blocker is no longer budget and is not time — **it is memory**, and §7 prices it.

---

## 5. Cost ledger

Billed **cores × wall for the whole clock** (`DAFOAM_CHARTER.md` §12). At `--cpus=1`,
core-min = wall-min.

| # | stage | wall | cpus | core-min | note |
|---|---|---|---|---|---|
| 1 | gate poll, attempt 1 (21:07:02Z) | — | 0 | **0.00** | assertions + gate only, **no container**; gate closed at 19.77 GiB |
| 2 | **O2 re-buy** (21:12:13Z → 21:27:13Z) | **900 s** | 1 | **15.00** | 4 `spilu` rows measured; `splu` killed by the cgroup |
| | **GROSS TOTAL** | | | **15.00** | against **35.0** registered, **50.0** ceiling |

```
cost_basis: c7a.4xlarge at $0.0513/core-hour, REPORTED-BY-OWNER (owner-stated 2026-08-21/22),
            NOT MEASURED -- the box cannot read its own billing
            (COMPUTE_BUDGET_CHARTER.md section 5; CLAUDE.md rule 12).
actual:   15.00 core-min / 60 * $0.0513 = $0.012825  -> $0.01283   MEASURED core-min, DERIVED dollars
ceiling:  50.00 core-min                = $0.04275   -- NOT reached
```

**The ceiling was not reached and the `timeout` never fired.** The wired 2700 s stop was never
tested: the memory stop fired first, at 900 s. **This item has a proven memory stop and an
still-unproven budget stop**, and that is the honest state of its instrument chain.

**Zero core-min of waste.** Every one of the 15.00 core-min produced a graded measurement — the four
`spilu` rows (O2R-P4 and the parent's M1-P8) and the ≥ 20.0 GiB lower bound on the exact LU. This is
**not** the parent item's 20.00 core-min staging fault (`W4_M1M2_RESULTS.md:215`, §5a), and the two
are not to be filed in the same class.

### 5a. §4c registered deliverable — predicted vs actual, with the gap attributed

Per the frozen §4c of `8d48fd46`, and per Sanaa's 2026-08-23 standing directive that estimated costs
be compared with actual incurred costs so the lab's estimates improve.

| field | value | labelling |
|---|---|---|
| predicted core-min | **35.0** | registered prediction, frozen §4 |
| **actual core-min** | **15.00** | **MEASURED** — `logs/o2_rebuy_hump_lu_20260823T211207Z.log.start` `21:12:13Z` → `.end` `21:27:13Z`, × 1 cpu ÷ 60 |
| predicted \$ | **\$0.02993** | **DERIVED** at \$0.0513/core-h, REPORTED-BY-OWNER, **not measured** |
| **actual \$** | **\$0.01283** | **DERIVED**, same rate, same caveat |
| **ratio** | **0.43** (15.00 ÷ 35.00) | arithmetic on the two rows above |

**Gap attribution: −20.00 core-min, and it is none of the three registered causes.**

| cause | core-min | reading |
|---|---|---|
| contention | **0.00** | the container held a dedicated cpu at **100.05 %** throughout (operator `docker stats` reading mid-run, labelled as an observation, not an artifact). A shared box did not slow this work |
| waste | **0.00** | every core-min produced a graded measurement (§5) |
| misprediction | **0.00** | the 35.0 core-min estimate of *how long the factorization takes* was **never tested** — the run did not stop on time |
| **truncation by the memory cap** | **−20.00** | the run was cut off at 900 s by a stop registered in §7a of the pre-registration. **The entire gap is here** |

**§4c's own escape clause is what makes this reportable rather than fudged:** it required the three
causes to sum to the gap *"or the shortfall is named"*. They sum to zero against a −20.00 gap, so
the shortfall is named, and the fourth cause is written into the row rather than smuggled into
"misprediction". **A cost that came in at 0.43× because the run was killed is not an estimate that
was too high**, and this table exists so nobody later reads it as one.

**Calibration lesson for the ledger, in one line:** *a cost prediction is only tested by a run that
stops for the reason the prediction was about.* Both of this item's spend predictions (O2R-P5,
C-P1R) are MISSes that measured a memory cap rather than a factorization.

---

## 6. Memory envelope — measured against the frozen band

| stage | predicted (frozen) | measured | grade |
|---|---|---|---|
| O2, this lane's own band (O2R-P6) | **8.0 – 20.0 GiB**, point 13.5 | **≥ 20.0 GiB**, right-censored at the cap | **MISS (high)** |
| O2, the parent's §7a band (`W4_M1M2_PREREGISTRATION.md:449`) | **8.0 – 22.0 GiB**, point 14.0 | **≥ 20.0 GiB** | **cannot be resolved** — the truth may be inside the band (20–22) or above it |

**The point predictions were badly low and this is the item's most useful correction.** Both frozen
bands put the point at 13.5 – 14.0 GiB. The true requirement is **more than 20.0 GiB** — above the
90th percentile of the parent's band, and above this lane's entire band. The basis that produced
those points (CBFS's ≈ 3 GB of factors scaled by a predicted 2.1 – 3.5× fill) **under-predicted**,
which is consistent with §3a's quarantined suggestion that the true fill exceeds the frozen
`nnz(L+U)` band.

**The registered §7c outcome fired exactly as written, all five clauses:**

1. §3 applied to the completed `splu` rows — **zero completed ⇒ `PENDING`**. ✔
2. **O2R-P6 graded MISS (high), reported as ≥ 20.0 GiB right-censored.** ✔
3. Stage labelled **`stopped by memory`**, claiming nothing beyond the cap breached. ✔
4. **No inference that the hump is memory-bound.** ✔ — stated again below.
5. Spend reported gross; the price of finishing reported, **not spent** (§7). ✔

**No inference is drawn that the hump adjoint is memory-bound.** `COMPUTE_BUDGET_CHARTER.md` L-15
and `DAFOAM_CHARTER.md:286-294`: what was measured is that **an offline scipy factorization of the
assembled matrix exceeded a 20 GiB cap this lane chose**. It says nothing about DAFoam's own solve,
nothing about `dRdWTMF`, and nothing about whether the real adjoint is bound by RAM. **This lane has
made that error before and refuses it again here.**

### 6a. The guard worked, and it is the reason the item has any measurement at all

The stop was **kernel-enforced** — `--memory=20g --memory-swap=20g --oom-score-adj=500` — precisely
because the watcher-script mechanism's start command was **denied in a peer lane's permission
context** and re-issuing it from here would be permission laundering (`CLAUDE.md` rule 9;
`W4_M1M2_RESULTS.md:300-310`). **That denied command was not re-attempted and was not routed
around.** O3 remains `BLOCKED` and Sanaa's.

**What the design bought.** The kill fired **at the byte**, needed nothing armed, needed no
permission, and could not fail to fire. With swap disabled the container could not degrade into
host-wide thrashing instead of stopping — the box stayed usable and no co-tenant was disturbed.
**A guard that lives in the kernel cannot be denied, cannot be forgotten and cannot be armed too
late** — and the parent item's O3 is the counter-example that makes the point (`L-239`: a registered
stop with nothing wired to trigger it is not a guard).

**What the design cost, and it was registered in advance.** §7a of the pre-registration said, before
the run: *"The frozen band's top 2.0 GiB (20.0 – 22.0 GiB) is **unreachable**: a factorization that
would have completed at 21 GiB is killed instead."* **That is now a realised cost, not a
hypothetical**: the 20.0 GiB cap is why §3 says `PENDING`. Whether a 22 GiB cap would have finished
is **unknown and unknowable from this run** — §3a's arithmetic suggests the requirement may exceed
22 GiB by a wide margin, in which case no cap this box can offer would have helped.

---

## 7. What is still owed, and what it now costs

**The `spilu` half of the §3 question is bought and durable. The `splu` half needs more RAM than
this box can safely give it.**

| item | price | what it buys | blocker |
|---|---|---|---|
| **O2 re-run at a raised cap** on this box, e.g. `--memory=26g` | ≤ 45 core-min | possibly the §3 decision | **Would breach co-tenant safety**: 26 GiB of a 30.64 GiB box, with `MemAvailable` gated at ≥ 24.0 GiB, leaves the host under 5 GiB. **This lane does not propose it and has not run it** |
| **O2 on a larger instance** | unpriced here — a **separate instance**, outside the 2026-08-21 blanket by the same reasoning `CLAUDE.md` rule 12 applies to GPU | the §3 decision, with headroom | **Sanaa's**, not this lane's or the supervisor's |
| **A memory-bounded reformulation** — e.g. `scipy.sparse.linalg.splu` with a fill-reducing `permc_spec` other than the default, or a rank-revealing check that does not build all of `L+U` | unpriced, needs design | possibly D-SINGULAR-vs-not without the full factorization | **would require a NEW script**, hence a new frozen md5 and a new pre-registration. `analyze_dump3.py` is not edited |
| **O3 re-buy** (`pc_ladder.py`, M1-P11 / M1-P12) | ~10 – 40 core-min | M1-P11, M1-P12 | **`BLOCKED` — Sanaa's to unblock.** Unchanged by this item |

**All four are Sanaa's to authorise, not this lane's and not the supervisor's.** `CLAUDE.md`
rule 12: an overrun does not get a new budget, and a re-buy is a new decision with its own price.

**Nothing from §10 of the pre-registration was touched.** M3–M8, the ~5 core-min GAMG → PBiCGStab
ADF sweep, the `useMeanStates` + `fieldAverage` arm, and everything on A6 CRM N=29 are exactly as
they were. **`N=29` remains `NOT RUN` under either reading.** **Nothing was filed anywhere.**

---

## 8. Evidence

`/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/`:

| path | what |
|---|---|
| `logs/o2_rebuy_hump_lu_20260823T211207Z.log` | **the whole measurement** — `:1` identity, `:4-7` the four `spilu` rows, `:9-12` the killed `splu`, the cgroup peak and `rc` |
| `logs/o2_rebuy_hump_lu_20260823T211207Z.log.start` / `.end` | `2026-08-23T21:12:13Z` / `2026-08-23T21:27:13Z` — the wall every core-min figure in §5 is computed from |
| `logs/o2_rebuy_poller.out` | both gate attempts, with all three void assertions printed and passing each time |
| `run_o2_rebuy.sh` | the registered §6 command, transcribed to a file (md5 `4beac779f4d1b18400fa5d71478f9bdf`) — see §8a |
| `poll_o2_gate.sh` | the 5-minute gate poller; zero compute per poll |
| `hump_dump/pmat.dat`, `hump_dump/rhs.dat` | the operator and RHS, **unchanged**: 406,022,696 B and 4,137,928 B, both re-asserted before launch |

**Void conditions: none fired.** All three §8 assertions were printed and passed on **both** gate
attempts — `analyze_dump3.py` md5 `f85140f675bcc287f6e4aaf01276c0e4`, `pmat.dat` 406,022,696 B,
`rhs.dat` 4,137,928 B, image `sha256:9d45679d55fd47f5…`. The instrument that ran **is** the frozen
instrument.

**Launch gate: enforced, and it refused once.** Attempt 1 at `21:07:02Z` read
`free_cores=6 memavail_gib=19.77` and **exited 3 without starting a container** — the gate working,
at zero cost. Attempt 2 at `21:12:07Z` read `free_cores=9 memavail_gib=26.84` and launched. **The
standing 12 GiB floor was neither touched nor argued.**

### 8a. One disclosed deviation, and it is a transcription

The §6 command was registered as an inline block. It was **transcribed verbatim into
`run_o2_rebuy.sh`** and run from there, so that the exact bytes executed are a durable artifact
rather than shell history. **No token of the registered command was changed** — same assertions,
same gate, same `timeout 2700`, same `--cpus=1 --memory=20g --memory-swap=20g --oom-score-adj=500`,
same mounts, same `python -u`, same `PIPESTATUS[0]`. The file adds only a shebang, a provenance
comment, an `echo LOGPATH=` and a final `exit $rc` so the poller could read the status. **Disclosed
here rather than left for a reader to notice.**

---

## 9. Proposed records — DRAFTS ONLY, for the supervisor to append or discard

**This lane appends nothing to `LESSONS.md`, `DOCKET.md`, `NUMERICS_KNOWLEDGE.md` or
`COST_CALIBRATION.md`** (`DAFOAM_CHARTER.md` §11). Numbers are **not** re-derived here; the
supervisor re-derives at append time with the period-anchored regexes, from `git show HEAD:`, inside
the committing invocation, because a number carried in a draft schedules its own correction.

**Proposed numerics fact (N-D family).** NASA hump, 51,626 cells, `DASimpleFoam`/kOmegaSST, 517,240
adjoint states, assembled `dRdWTPC` (33,662,810 nnz): **`scipy.sparse.linalg.spilu` raises
`Factor is exactly singular` at all four registered settings** — `drop_tol` 1e-2/1e-3/1e-4/1e-5 with
`fill_factor` 3/5/5/10 — reproducing CBFS's 4-of-4 result on a second case. The **complete**
factorization `splu(diag_pivot_thresh=0)` **exceeded a 20.0 GiB cgroup cap** without completing,
against CBFS's complete LU finishing inside 10 GiB at 3.22e8 nnz(L+U).

**Proposed lesson A — the one this item paid for.** *A kernel-enforced stop cannot be denied,
forgotten or armed too late, and it fires at the byte; that is why it should be preferred to a
watcher script. But a cap set for co-tenant safety is also a cap on what the item can measure, and
if it binds, the item returns `PENDING` rather than an answer.* Both halves are this run: the guard
worked perfectly (rc 137, peak exactly at the cap, box undisturbed, no permission needed) **and** it
is the sole reason the §3 decision was not bought. The pre-registration registered that trade
explicitly before the run (`W4_O2_REBUY_PREREGISTRATION.md` §7a), which is the only reason this can
be reported as a designed cost rather than discovered as a surprise.

**Proposed lesson B — cost calibration.** *A spend prediction is only tested by a run that stops for
the reason the prediction was about.* This item's two spend predictions (O2R-P5 wall band, C-P1R
"exceeds 25.0 core-min") are both MISSes that measured a memory cap, not a factorization. The
C-P1 hypothesis is now **two attempts and zero tests** old: first the factorization never ran
(`W4_M1M2_RESULTS.md:196-204`), then it ran and never finished. **A third attempt must change the
binding constraint or it will produce a third untested MISS.**

**Proposed docket row.** *The NASA hump's incomplete factorization is singular at all four
registered settings — the CBFS signature, now reproduced on a second case — but the complete
factorization does not fit in 20 GiB, so singular-vs-merely-slow is still undecided.* Falsifier: run
`splu` on `hump_dump/pmat.dat` with enough RAM to complete and the §3 rule returns a verdict. Owner:
whoever Sanaa assigns the memory.

**Proposed `COST_CALIBRATION.md` row — DRAFTED HERE, NOT APPENDED.** That file does not exist on
this box at the time of writing. §5a above **is** the row, in full, with the four-way attribution and
the labelling (`MEASURED` core-min, `DERIVED` dollars). The supervisor lands it; **this lane appends
it nowhere.**

---

## 10. What this item may and may not conclude

- It **may** conclude that the hump's assembled `dRdWTPC` has a **singular incomplete
  factorization** at all four registered `spilu` settings — the CBFS mechanism signature, on a
  second case.
- It may **not** conclude D-SINGULAR, D-ILLCOND-CATASTROPHIC, D-MERELY-SLOW or
  D-UNREGISTERED-CLASS. **All four require a completed `splu` and there was none.** §3 returns
  **`PENDING`**.
- It may **not** conclude that the hump is memory-bound (§6, L-15), nor that DAFoam's own adjoint
  needs > 20 GiB. What was capped was an offline scipy factorization of the assembled matrix.
- It may **not** conclude anything about `dRdWTMF`, the matrix-free operator GMRES actually applies
  — the caveat carried verbatim through §3 of the pre-registration from `PROOF.md:2800-2803`.
- It may **not** conclude anything about the hump's convergence **rate**, which requires M4.
- It may **not** promote §3a's `nnz(L+U)` arithmetic to a MISS on O2R-P1, or the 13.01-decade
  diagonal spread to a verdict (`PROOF.md:2729-2730`; refused twice before).
- **No verdict here is `PASS` on an FD gate: no gradient was produced**, so `DAFOAM_CHARTER.md` §2's
  FD-table requirement is not engaged and no gradient number is quoted.

---

## 11. Related

| document | what it owns that this file does not |
|---|---|
| `cases/dafoam/ladder-b/W4_O2_REBUY_PREREGISTRATION.md` (`8d48fd46`, blob `47e2988e`) | The frozen bands, the §3 rule inherited verbatim, the §7 guard design and its registered abort outcome, the §4c calibration deliverable |
| `cases/dafoam/ladder-b/W4_M1M2_RESULTS.md` (`64479072`) | The dump's provenance and verification; O0; M2's negative control; the first C-P1 MISS; O3's `BLOCKED` |
| `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md` (`c8254a4a`) | M1-P8 / M1-P9 / M1-P10, graded here; the §7a memory band |
| `cases/dafoam/PROOF.md` §25.3 | The CBFS singular-ILU diagnosis this run reproduced on the hump, and the `dRdWTPC`-is-not-`dRdWTMF` caution |

---

## 12. Supervisor close-out — 2026-08-24T16:01:21Z, dafoam-supervisor (session `01ENBw3KPr5gMaj8Vt7rcxSB`)

**Provenance disclosure.** Lane X wrote this record (file mtime 2026-08-23 21:31Z) and was killed by
the session limit before committing it; the supervisor died in the same event. The record is
committed here **as found on disk, byte-for-byte above this section**, ~18 h later, after the
verification below. **Lines whose number changed above this section: 0.**

**Verified personally against the raw artifacts, not against the lane's report:**
- `logs/o2_rebuy_hump_lu_20260823T211207Z.log`: `n=517240 nnz=33662810 ||b||=1.094138002900e+00`;
  four `spilu` rows, every one `FAILED: Factor is exactly singular`; the `splu` header printed and no
  row followed it; `245 Killed`; `CGROUP_PEAK_BYTES=21474836480` = 20 × 1024³ **exactly**;
  `O2 REBUY rc=137`.
- `.start` `2026-08-23T21:12:13Z`, `.end` `2026-08-23T21:27:13Z` → 900 s → **15.00 core-min** at
  `--cpus=1`; **$0.01283 DERIVED** at $0.0513/core-h (reported-by-owner, not measured).
- `o2_rebuy_poller.out`: attempt 1 (21:07:02Z) refused by the registered gate at 19.77 GiB with no
  container started; attempt 2 (21:12:07Z) passed at 26.84 GiB with all three void assertions
  printed equal to the frozen values (`f85140f6…`, 406,022,696 / 4,137,928 B, `sha256:9d45679d…`).

**Grading confirmed as the frozen file requires, unsoftened:** the §3 decision is **`PENDING`**
(zero completed `splu` — the registered row); the `splu` measurement is **`NOT A RESULT`** (killed
at the registered cap before any threshold returned); `spilu` is **4 of 4 exactly singular**
(O2R-P4 HIT; the parent's M1-P8 HIT); O2R-P5 MISS, O2R-P6 MISS (high, right-censored at 20.0 GiB),
C-P1R MISS with its hypothesis still untested — the lane's §4b reading stands. **Zero waste:** the
15.00 core-min bought a graded measurement (the 4-of-4 singularity and the > 20.0 GiB lower bound),
and the cap was the pre-registered instrument (`8d48fd46` §7), so the kill is a **real cost of a
registered measurement**, not waste.

**Calibration.** The §5a row is landed by the supervisor in `docs/COST_CALIBRATION.md` in the commit
following this one. The ledger's reading of the −20.00 core-min gap: **misprediction of the memory
band** (frozen 8.0–20.0 GiB; requirement > 20.0) is the *cause*, **truncation by the registered cap**
the *mechanism*; contention 0, waste 0; the 35.0 core-min duration estimate was never tested.

**What is owed and by whom.** The §3 answer needs a `splu` that completes — a box with more than
20 GiB free to one process, or a factorization that fits; both are new registrations with their own
price, and choosing is on Sanaa's desk beside O3's guard authorization. Nothing here is filed anywhere.
