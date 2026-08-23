# W4 M1 + M2 — results: the hump `-9` reproduced twice, the operator dumped and verified, and the singular-or-not question still unanswered

**Status: NOT FILED ANYWHERE. Nothing here is sent, posted, uploaded, registered or commented
outside this box.** Filing is Sanaa's decision alone (`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

Graded against the frozen pre-registration `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md`,
committed **alone** at `c8254a4a424cc058b88351aa735a44cc6ab6199d` **before any compute**.
Blob `e7b5f0d427401663def453e968356bb8937602ce`; sha256
`92a6831cab7f71a5d16844fc4c5d1de6dddde6012ae3c3e45f5c13ea92348956`. Re-hashed against the
committed blob before grading: **equal**. Run root
`/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/`.

---

## 1. Verdicts

| item | verdict | one line |
|---|---|---|
| **O0** known-answer control | **PASS** | all five published CBFS values reproduced exactly on this box today |
| **M2** negative control | **PASS** | the hump `-9` at iteration 0 reproduced deliberately, patch inert, cold, 6 of 7 predictions HIT |
| **M1-D** assembly-to-dump | **PASS** | `dRdWTPC` and RHS dumped and verified; `‖b‖₂` matches the solver's own iteration-0 residual to 13 digits |
| **M1** overall — the §3 decision | **PENDING** | stage **O2 was not launched**: the budget rule left 19.88 core-min against a registered 25.0 launch floor |
| **O3** `pc_ladder.py` | **BLOCKED** | the mandatory memory guard could not be armed; the stage was not run unguarded |

**The singular-vs-ill-conditioned-vs-merely-slow question is NOT answered.** The §3 registered
consequence — *"if M1 returns singular or catastrophically ill-conditioned, M4 and M5 are not
bought"* — **did not fire**, because M1 returned neither. **M4 and M5 remain unbought for a
different reason: M1 did not decide.** That distinction is load-bearing and is not to be collapsed.

**What the item nevertheless bought, and it is durable:** the hump's assembled `dRdWTPC`
(406,022,696 B) and its RHS (4,137,928 B) are **on disk permanently and verified**. The expensive
half of M1 — the only half that needs a solver — **is paid**. O2 is now a pure offline re-buy with
no DAFoam launch in it at all.

---

## 2. The headline measurement: the hump `-9` was deliberately reproduced, twice, in one afternoon

`docs/INSTRUMENT_INTEGRITY_LEDGER.md:399-402` records the state this item was bought to change:

> **Not one hump failure was ever deliberately re-run as a negative control.** The only env-off
> regression control in the whole programme is on CBFS, not the hump.

Both rows, as `DAFOAM_CHARTER.md` §6 requires — and they agree to every printed digit:

| row | image | `DAFOAM_SUBPC_TYPE` | primal `OBJ cfVar` | iteration-0 KSP residual | outcome | log |
|---|---|---|---|---|---|---|
| **patched, patch inert** (M2) | `dafoam-subpclu:v1` `ba2d16ab9d57` | **unset** | `1.6263651522923017e-01` | `1.094138002900e+00` | `Total iterations: 0. PetscConvergedReason: -9` | `logs/m2_envoff_computetotals.log:1744`, `:2271` |
| **shipped** (M1-D) | `dafoam/opt-packages:latest` `9d45679d55fd` | n/a | `1.6263651522923017e-01` | `1.094138002900e+00` | `Total iterations: 0. PetscConvergedReason: -9` | `logs/m1d_dump_computetotals.log:1744`, `:2271` |
| **A6, 2026-08-04** (the record being controlled) | `dafoam-subpclu:v1` | `lu` | `1.6263651522923017e-01` | `1.094138002900e+00` | no `KSPConvergedReason` ever reached | `W4-adjoint-pc-unblock/hump_sublu_computetotals.log:1744`, `:2268` |

Three independent runs, two images, two sub-PC settings: **the primal objective is bit-identical to
17 digits and the adjoint's iteration-0 residual to 13**. The sub-LU banner
`DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` occurs **zero** times in both of
today's logs (`grep -ac` = 0), which is the standing proof both ran stock in the sub-block
(`DAFOAM_CHARTER.md` §6).

**What this establishes.** The `-9` → sub-LU attribution is now reproducible **on the hump**, not
inherited from CBFS. **What it does not establish**: nothing about the rate, nothing about
`dRdWTMF`, nothing about whether the operator is singular. Those needed O2.

**A measurement that falls out of the pair, and it is new.** A6's iteration-0 print came at
**174.97 s**; today's stock runs printed it at **73.83 s** (M2) and **73.71 s** (M1-D). The
difference is the ASM sub-block **complete-LU factorization**, which therefore costs ≈ **100 s wall
at np=4** on this case — a number the programme did not have, and the reason the §5b.1 pre-solve
price of 11.7 core-min over-priced a stock arm by ~40 %.

---

## 3. The §3 decision rule — PENDING, and exactly why

The rule was registered on the complete-versus-incomplete factorization axis and reads its inputs
from stage **O2** (`analyze_dump3.py`: `spilu` × 4 settings, `splu` × 3 pivot thresholds). **O2 did
not run.** The frozen §4a rule:

> If O2 cannot be given at least **1500 s** (25.0 core-min at `--cpus=1`), **O2 is not launched**
> and M1 is `PENDING` with the reason recorded as the budget ceiling.

Applied, with the arithmetic printed rather than asserted:

```
cumulative (O0 run1 at its 3.00 core-min BOUND) = 40.12 core-min
remaining to 60.0 ceiling                        = 19.88 core-min
O2 registered launch floor                       = 25.00 core-min
O2 DECISION: NOT LAUNCHED -> M1 PENDING
```

**The decision is robust to the one unmeasured item.** O0 run 1 is carried at its 3.00 core-min
*bound*; even if its true cost were ~0.25 core-min, remaining would be 22.63 — still below 25.0.
The rule fires either way.

**What consumed O2's funding is named in §5: a 20.00 core-min staging fault.** Nothing about the
physics, the box or the operator prevented O2. A permissions mistake in this lane's own staging did.

### 3a. Evidence that bears on the §3 question but is NOT the registered instrument

Reported because it exists, and quarantined because §3 named `splu`/`spilu` and nothing else.

- `zero rows = 0`, `zero cols = 0`, `zero diagonal entries = 0` (M1-P6, HIT). This **rules out the
  cheap half of D-SINGULAR** — the branch *"or `analyze_dump.py` reports zero rows > 0 or zero
  cols > 0"* is closed. The `splu` branch is untested, so D-SINGULAR as a whole is **not** ruled out.
- `‖b‖₂` matches the solver's own printed iteration-0 residual to 13 digits, so the dumped system
  **is** the real system and not an unrelated one — the same check `PROOF.md:2717-2720` used on CBFS.

**No verdict is drawn from either.** `PENDING` stands.

---

## 4. Per-prediction grading

### 4a. M1 — 6 HIT, 1 MISS, 5 PENDING

| id | prediction | measured | grade |
|---|---|---|---|
| M1-P1 | `‖b‖₂` = `1.094138002900e+00`, 13 digits | **`1.094138002900e+00`** | **HIT** |
| M1-P2 | `517,240 × 517,240` exactly | **`517240 x 517240`** | **HIT** |
| M1-P3 | `nnz(A)` 28.4e6 – 38.8e6, point 33.7e6 | **33,662,810** | **HIT** (0.1 % from the point) |
| M1-P4 | `rhs.dat` **exactly 4,137,928 B** | **4,137,928 B** | **HIT** (exact) |
| M1-P5 | `pmat.dat` 343 – 470 MB, point 406 MB | **406,022,696 B = 406.0 MB** | **HIT** |
| M1-P6 | zero rows/cols/diag `0 / 0 / 0` | **0 / 0 / 0** | **HIT** |
| M1-P7 | diagonal abs spread `log10` **7.5 – 11.0**, point 9.0 | **13.01** | **MISS (high)** |
| M1-P8 | `spilu` singular at ≥ 3 of 4 | O2 not launched | **PENDING** |
| M1-P9 | `splu` completes, `min ‖Ax−b‖/‖b‖ ≤ 1e-9` | O2 not launched | **PENDING** |
| M1-P10 | `nnz(L+U)` 8.0e8 – 1.35e9 | O2 not launched | **PENDING** |
| M1-P11 | `pc_ladder` control: `-9`, its 0, finalres = `‖b‖` | O3 BLOCKED | **PENDING** |
| M1-P12 | `pc_ladder` sublu: reason 2, 150–1000 its | O3 BLOCKED | **PENDING** |

**The 12.06 B/nnz basis behind M1-P5 held to four significant figures.** CBFS:
165,368,000 / 13,710,468 = **12.062**. Hump: 406,022,696 / 33,662,810 = **12.062**. The point
prediction of "406 MB" was arithmetic on a measured constant, and it landed on the byte scale.

### 4b. M1-P7 is the informative MISS, and it is NOT promoted

**Measured 13.01 decades of diagonal spread on the hump**, against a registered band of 7.5 – 11.0.

| case | diagonal abs `log10(max/min)` | row max-abs `log10` | source |
|---|---|---|---|
| CBFS | **8.67** | 6.36 | `PROOF.md:2727`; re-measured today in O0, identical |
| **hump** | **13.01** | **11.19** | `logs/o1_hump_stats.log:14`, `:12` |
| M6 (R5) | **14.17** | — | `PROOF.md:2727` |

The hump sits **far closer to M6 than to CBFS** on the metric R5 used. **This is not promoted to a
verdict, and the pre-registration is the reason.** §2a registered M1-P7 as *"Reported, not
decision-bearing"* and §3 built the decision rule on the factorization axis instead, citing
`PROOF.md:2729-2730`: *"R5's diagonal-spread mechanism does not explain CBFS."* A metric recorded
as non-explanatory does not become explanatory because it came back large. **Registering that
before seeing the number is the whole of why this paragraph can be trusted.**

It is, however, the strongest existing hint about which way O2 will go, and it is the reason O2 is
worth re-buying.

### 4c. A structural difference nobody had looked for

| | CBFS `varianceU` | hump `cfVar` |
|---|---|---|
| RHS nonzeros | 63,000 of 210,592 = **29.92 %** | **2,165 of 517,240 = 0.42 %** |
| `‖b‖₂` | 7.091590452305e-04 | 1.094138002900e+00 |
| `‖A^T b‖` | 1.845943e-02 | **3.925172e+10** |
| `cos(b, A b)` | +6.287343e-03 | +2.161693e-01 |

The hump objective is a **surface** variance of `wallShearStress` on the `bottom` patch, so its seed
touches only near-wall cells; CBFS's `varianceU` is a volume objective. **`cos(b, ·)` is reported
and nothing is concluded from it**: `PROOF.md:2738-2756` **withdrew** control 1 as an explanation
when the force RHS stagnated just as hard, and that withdrawal is not reopened here.

### 4d. M2 — 6 HIT, 1 MISS

| id | prediction | measured | grade |
|---|---|---|---|
| M2-P1 | `OBJ cfVar` = `1.6263651522923017e-01`, 17 digits | **bit-equal** | **HIT** |
| M2-P2 | first continuity error `7.98671e-05` | **`7.98671e-05`** at `:710` | **HIT** |
| M2-P3 | `Total iterations: 0` + `PetscConvergedReason: -9` | **both present** at `:2271` | **HIT** |
| M2-P4 | iteration-0 residual `1.094138002900e+00` | **`1.094138002900e+00`** | **HIT** |
| M2-P5 | sub-LU banner count **zero** | **0** | **HIT** |
| M2-P6 | `rc = 1` | **1** | **HIT** |
| M2-P7 | 150 – 260 s = 10.0 – 17.3 core-min | **148 s = 9.87 core-min** | **MISS (fast, by 2 s)** |

M2-P2 lands on the same value A6 printed at its own `:710`, from an independently re-staged cold
copy whose five §5a md5s were asserted before launch. **The arm is cold and it is A6's start state.**

M2-P7 missed low by 2 s. The cause is measured, not guessed: A6's pre-solve carried the sub-LU
factorization this arm does not build (§2, ≈ 100 s at np=4), and the 11.7 core-min basis was taken
from A6.

### 4e. O0 — PASS

Every published CBFS value reproduced on this box today, unmodified reader, read-only mount:
`n = 210592`, `nnz = 13710468`, `‖b‖₂ = 7.091590452305e-04`, zero rows/cols/diag `0/0/0`,
diagonal `log10 = 8.67`, `cos(b, A b) = +6.287343e-03`. `logs/o0_cbfs_knownanswer.log`.
**M1 is not void.**

### 4f. The cost predictions this lane made about itself — both MISS

| id | prediction | measured | grade |
|---|---|---|---|
| C-P1 | M1's spend **exceeds 25.0 core-min** | M1 = **≤ 10.25** core-min | **MISS** |
| C-P2 | total **45.0 – 60.0** core-min, **stopping at the ceiling**, O3 unreached | total **≤ 40.12**, stopped at the **O2 launch floor**, O3 BLOCKED | **MISS** |

**Both MISSes are honest but neither refutes the reasoning behind them.** C-P1 predicted that the
`scipy` exact-LU factorization would blow M1's 25.0 core-min price. **That factorization never ran**,
so the claim is untested, not refuted — M1 came in cheap precisely by not doing the expensive thing.
Reporting C-P1 as a clean MISS would flatter this lane; it is a MISS whose hypothesis is still open,
and O2's re-buy is the test.

---

## 5. Cost ledger — gross, with the waste named

Billed **cores × wall for the whole clock** (`DAFOAM_CHARTER.md` §12).

| # | stage | wall | cpus | core-min | note |
|---|---|---|---|---|---|
| 1 | O0 run 1 | **UNMEASURED** | 1 | **≤ 3.00 (BOUND)** | ran without output redirection, so no log artifact and no timestamps; carried at its 180 s timeout cap. **A bound, not a measurement** |
| 2 | O0 run 2 | 3 s | 1 | 0.05 | produced the log artifact; output bit-identical to run 1 |
| 3 | **M2 attempt 1** | 300 s | 4 | **20.00** | **WASTE — staging fault, zero measurement** (§5a) |
| 4 | M2 attempt 2 | 148 s | 4 | 9.87 | PASS |
| 5 | M1-D | 107 s | 4 | 7.13 | dump written |
| 6 | O1 | 4 s | 1 | 0.07 | statistics |
| 7 | O2 | not launched | — | 0 | budget floor |
| 8 | O3 | not launched | — | 0 | BLOCKED, guard unarmable |
| | **GROSS TOTAL** | | | **≤ 40.12** | against **40.0** registered, **60.0** ceiling |
| | **CLEANED** (excl. row 3) | | | **≤ 20.12** | |

```
cost_basis: c7a.4xlarge at $0.0513/core-hour, REPORTED-BY-OWNER (owner-stated 2026-08-21/22),
            NOT MEASURED -- the box cannot read its own billing.
gross:   40.12 core-min / 60 * $0.0513 = $0.03430   (registered prediction $0.03420)
cleaned: 20.12 core-min / 60 * $0.0513 = $0.01720
ceiling: 60.00 core-min                = $0.05130   -- NOT reached
```

**The gross total landing within 0.3 % of the registered 40.0 is a coincidence and is reported as
one.** The 20.00 core-min of waste almost exactly replaced the unbought O2. A prediction that lands
because two errors cancelled is not a prediction that was right, and this row exists so nobody
later reads 40.12-against-40.0 as accuracy.

**Two rows are not measurements and say so.** Row 1 is a bound. The `≤` on every total is that
bound propagating.

### 5a. The waste, in full — a staging fault that cost 20.00 core-min

M2 attempt 1 died in `prob.setup()` before the primal:

```
FileNotFoundError: [Errno 2] No such file or directory: 'reports/runScript_hump'
PermissionError: [Errno 13] Permission denied: 'reports'
```

**Cause.** OpenMDAO creates `reports/<script>` in the working directory. The container runs
`-u 1002:1002` (mandatory on this case — `W4_ADJOINT_PC_UNBLOCK.md:174-176`), and this lane created
the run root mode `drwxrwxr-x`, so uid 1002 could not write it. **A6's own run root is
`drwxrwxrwx`** and its `reports/` directory exists — the pre-registration copied A6's *invocation*
and did not copy A6's *directory mode*. Repaired with `chmod 777` on the run root; zero compute.

**Why it cost 20.00 and not 0.7.** The Python traceback fired at ≈ 20 s, then `mpirun` did not exit —
it logged `Forwarding signal 18 to job` and hung until the registered 300 s `timeout` fired. **The
registered cap worked; it is the only reason this was 20.00 core-min and not unbounded.** The
container held 1.13 GiB flat for the whole five minutes, which is the signature of a hung job rather
than a working one.

**Class.** The same family as A7 and A8, the two hump staging faults in
`INSTRUMENT_INTEGRITY_LEDGER.md:413-414`, both *"Diagnosed (trivial)"*. Those cost ~40 s between
them. This one cost 20.00 core-min because a hung `mpirun` sat under a 300 s cap, and **it is the
single reason the §3 decision was not bought.**

**Reported, not absorbed** (`CLAUDE.md` rule 12).

---

## 6. Memory envelope — measured against §7a

Two instruments, both registered in advance: **(i)** host `baseline MemAvailable − minimum
MemAvailable`, the same instrument as A6's own memlog; **(ii)** container-side `docker stats`
sampled every 30 s. §7a registered that where they disagree by more than 20 %, **both are printed
and neither is preferred.** They disagree on both solver stages, so both are printed.

| stage | predicted (§7a) | (i) host drawdown | (ii) container max | grade | guard |
|---|---|---|---|---|---|
| M2 | 6.0 – 16.0 GiB, point 10.0 | **9.28 GiB** | **4.445 GiB** | (i) **HIT** · (ii) **MISS (low)** | no abort |
| M1-D | 6.0 – 16.0 GiB, point 10.0 | **3.34 GiB** | **4.40 GiB** | **MISS (low)** on both | no abort |
| O0 / O1 | 1.0 – 4.0 GiB | O1 **0.46 GiB** | not sampled (ran in 4 s) | **MISS (low)** | no abort |
| O2 | 8.0 – 22.0 GiB | not launched | — | **PENDING** | — |
| O3 | 10.0 – 26.0 GiB | not launched | — | **PENDING** | — |

**The honest reading, and it corrects this lane's own prediction.** The two instruments agree on one
thing: the stock-ILU pre-solve segment on the hump peaks at ≈ **4.4 GiB container-side**, which is
**below** the registered 6.0 – 16.0 GiB band. The band was anchored on A6's pre-solve *including*
the complete-LU sub-block factors, and the subtraction made for removing them was far too
conservative. **The assembly-to-dump run is a small-memory operation and this item measured it.**

M2's host drawdown of 9.28 GiB against a 4.445 GiB container is co-tenant traffic on a shared box,
not this arm — which is exactly why §7a registered two instruments instead of trusting A6's single
one. **The `MemAvailable`-drawdown instrument overstates on a shared box, and this item has the
matched pair that shows it.**

**No memory abort fired at any point.** Every guard log ends `DONE container_gone`. The 6.0 GiB soft
floor was never approached: the lowest `MemAvailable` recorded across all four guarded stages was
**18,697,604 kB = 17.83 GiB** (M2 attempt 2), nearly **3×** the floor.

### 6a. O3 is BLOCKED because the guard could not be armed

O3 passed its budget rule (19.88 ≥ 10.0 core-min) and its memory gate (25.91 ≥ 25.0 GiB), and its
`timeout` computed to 298 s. **It was not run**: the command that starts
`w4_m1m2_memguard.sh` was refused by this session's permission system, and §7 makes the guard
mandatory for every container stage.

O3 is the memory-riskiest stage in the item — predicted peak **10.0 – 26.0 GiB against a
30.65 GiB box**. **Running the one stage most likely to breach the floor with nothing wired to stop
it is precisely the L-239 failure the pre-registration exists to prevent**, so it was not run. The
verdict is `BLOCKED`, the cost is zero, and M1-P11 / M1-P12 are `PENDING`.

Recorded as a finding about this item's own instrument chain: **a mandatory guard that cannot be
armed stops the stage.** That is the guard working, from an unexpected direction.

---

## 7. What is still owed, and what it now costs

**O2 no longer needs a solver.** `hump_dump/{pmat,rhs}.dat` are on disk, verified against the
solver's own residual, and are inputs to an offline factorization.

| item | price | what it buys | note |
|---|---|---|---|
| **O2 re-buy** — `analyze_dump3.py`, `--cpus=1`, on the existing dump | **25 – 45 core-min** | **the entire §3 decision rule**, and with it whether M4/M5 may be bought | no DAFoam, no MPI, no case dir. The dump is paid for |
| **O3 re-buy** — `pc_ladder.py` control + sublu | ~10 – 40 core-min | M1-P11, M1-P12 | needs the guard armable |

**Both are the supervisor's and Sanaa's to authorise, not this lane's.** The 60.0 core-min ceiling
stopped this item and **an overrun does not get a new budget** (`CLAUDE.md` rule 12); a re-buy is a
new decision with its own price, not a continuation of this one.

**Nothing from §10 of the pre-registration was touched.** M3–M8, the ~5 core-min GAMG → PBiCGStab
ADF sweep, the `useMeanStates` + `fieldAverage` arm, and everything on A6 CRM N=29 are exactly as
they were. **`N=29` remains `NOT RUN` under either reading.** Nothing was filed anywhere.

---

## 8. Evidence

`/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/`:

| path | what |
|---|---|
| `hump_dump/pmat.dat` | assembled `dRdWTPC`, 517,240², 33,662,810 nnz, **406,022,696 B** |
| `hump_dump/rhs.dat` | adjoint RHS, **4,137,928 B**, `‖b‖₂ = 1.094138002900e+00` |
| `logs/o0_cbfs_knownanswer.log` | O0, the known-answer control |
| `logs/m2_envoff_computetotals.log` | **M2** — `:710`, `:1744`, `:2271` |
| `logs/m1d_dump_computetotals.log` | **M1-D** — `:1744`, `:2267`, `:2271` |
| `logs/o1_hump_stats.log` | **O1** — `:1`, `:5`, `:11`, `:12`, `:14` |
| `logs/{m2,m1d,o1}_mem.log` | guard traces, 5 s cadence, all ending `DONE container_gone` |
| `logs/*.start`, `logs/*.end` | the wall-clock timestamps every core-min figure in §5 is computed from |
| `w4_m1m2_memguard.sh` | the guard, md5 `f102eb52c11f8f377b0654a84c97168c`, unchanged since the freeze |
| `memguard_selftest.log` | the pre-freeze self-test of the guard's trigger path |

Instrument md5s asserted at launch and **all identical** to the frozen §5 values:
`analyze_dump.py d35cb147…`, `analyze_dump3.py f85140f6…`, `pc_ladder.py b1388434…`,
`runScript_hump.py d146c56a…`, `w4_m1m2_memguard.sh f102eb52…`. **No §8a void condition fired.**
Case-state md5s in §5a asserted clean on both arms, and re-asserted on the re-staged M2 copy.

---

## 9. Proposed records — DRAFTS ONLY, for the supervisor to append or discard

**This lane appends nothing to `LESSONS.md`, `DOCKET.md` or `NUMERICS_KNOWLEDGE.md`**
(`DAFOAM_CHARTER.md` §11). Numbers below are **not** re-derived here; the supervisor re-derives at
append time with the period-anchored regexes, because a number carried in a draft schedules its own
correction.

**Proposed lesson A.** A registered per-stage `timeout` is the only thing standing between a hung
`mpirun` and an unbounded burn. M2 attempt 1 crashed in Python at ~20 s and `mpirun` then hung; the
cap turned an unbounded hang into a bounded 20.00 core-min loss. The same cap is also what made the
loss large enough to cost the item its decisive stage — **so the cap should be the smallest value
that still fits the predicted run, not the largest the budget allows.** Registered 300 s against a
predicted 150–260 s run left 280 s of hang inside the cap.

**Proposed lesson B.** Copying a prior run's *invocation* is not copying its *environment*. A6's
`-u 1002:1002` was carried forward; A6's `drwxrwxrwx` run root was not, and OpenMDAO's `reports/`
write is the tripwire. **A pre-registration that pins a container's uid should pin the mount's mode
in the same sentence.**

**Proposed numerics fact (N-D family, next number to be re-derived at append time).** NASA hump,
51,626 cells, `DASimpleFoam`/kOmegaSST, 517,240 adjoint states: the assembled `dRdWTPC` has
**33,662,810 nnz (65.08 per row)**, **zero** zero-rows, zero-cols and zero-diagonal entries, and a
diagonal absolute spread of **13.01 decades** — against CBFS's **8.67** and the M6 family's
**14.17**. The adjoint RHS for the surface objective `cfVar` is nonzero on **2,165 of 517,240**
entries (0.42 %), against CBFS `varianceU`'s 29.92 %. `‖b‖₂ = 1.094138002900e+00`, equal to the
solver's printed iteration-0 residual to 13 digits.

**Proposed numerics fact (second).** The ASM sub-block **complete-LU factorization** on this case
costs ≈ **100 s wall at np=4**: A6 printed iteration 0 at 174.97 s with `DAFOAM_SUBPC_TYPE=lu`;
two stock arms printed it at 73.83 s and 73.71 s with everything else held.

**Proposed docket row.** *The NASA-hump adjoint operator is dumped, verified and on disk; the
singular-or-not question is one offline factorization away and was lost to a 20 core-min staging
fault.* Falsifier: run `analyze_dump3.py` on `hump_dump/` and the §3 rule returns a verdict.
Owner: whoever Sanaa assigns the O2 re-buy.
