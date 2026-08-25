# Curriculum D8 — LANE REPORT (custody lane)

**Lane:** dafoam `lab-lane`, D8 custody. **Opened 2026-08-25 18:06Z.**
**Status of this file: INTERIM — committed incrementally so a stop loses nothing.**
Nothing here is filed, sent, uploaded, posted or pushed. **SUBMISSIONS ARE PARKED** and sending is
Sanaa's alone (CLAUDE.md rule 7).

This lane **did not launch, restart, stop or touch** the `opt` arm. It inherited a live container from
a lane that was stopped mid-work, verified custody from disk, and watched.

---

## 1. Custody verified from disk, not assumed

| fact | value | artefact |
|---|---|---|
| pre-registration disk blob | `cf57120eddacaa6f7766d4e9e9d3a3d853affea8` | `cases/dafoam/ladder-a/A6/curriculum_D8/PREREGISTRATION.md` |
| same path at HEAD | `cf57120eddacaa6f7766d4e9e9d3a3d853affea8` | `git rev-parse HEAD:<path>` |
| **verdict** | **IDENTICAL — the frozen prereg is the file on disk** | |
| container | `d8_opt_20260825T165153Z_2230005`, image `dafoam-idwarp-rot:v1` | `docker ps` |
| host pids (discriminated with `ps -eo pid,args`, never `pgrep -f`) | 2230005 launcher, 2230027 `timeout 10800 sudo -n docker run`, 2230463 `python runScript.py -task optd8 -optimizer IPOPT` | |
| `MemAvailable` at launch | **26,550,116 kB = 25.32 GiB** against the registered 12 GiB floor | `.../queue_opt.out` |
| G8 cold-start guard | `G8 OK (opt): no written time dirs, no processor*, no reports/, 0/ present` — **proved BEFORE the launch** | `.../queue_opt.out` |

Run root: `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/`.

## 2. Registered envelope, read off the frozen file

Gates G0–G7 plus P-BASE and P-η per §4/§7. `np = 1`, **`numberOfSubdomains 1`**, no decomposition —
§5 states this rather than leaving it blank, because at `np = 1` there is no seed, no rank-order
reduction and no `ranks × wall` vs `cores × wall` ambiguity (`--cpus=1`).

**Cost ceilings, frozen §8:** arm `opt` predicted **89.3**, ceiling **135.0** core-min; arm `fd`
predicted **57.8**, ceiling **75.0**; **TOTAL predicted 147.3, ceiling 215.0 core-min**, plus the
**0.217 core-min** pre-registration image read already billed. **An overrun stops the run.**

**The binding stop is the registered budget, not the container timeout.** `timeout 10800` from
16:51:53Z expires **19:51:53Z**, but the frozen 135.0 core-min ceiling on arm `opt` expires
**19:06:53Z** — 45 minutes earlier. The budget governs.

## 3. Live observations (arm `opt`, in flight)

| t (UTC) | IPOPT major | objective CD | inf_pr | RSS |
|---|---|---|---|---|
| ~17:09 | 0 | `3.8772630e-02` | 1.20e-04 | rising |
| ~17:41 | 1 | `3.8776848e-02` | 3.80e-06 | |
| 17:55 | 2 | `3.8678173e-02` | 2.10e-05 | 9.89 GiB |
| 18:10 | 3 in flight | — | — | **9.892 GiB** |

Source: `opt/opt_IPOPT.txt`, `rss_opt.txt`. At 18:10Z the major-3 flow adjoint was at main iteration
500, KSP residual `2.445170283082e-07` — consistent with the registered 517-iteration anchor.

**RSS is flat at 9.892–9.893 GiB against the 11.0 GiB G6 band and the 12 GiB cgroup cap.** No approach
to the cap; no OOM signal. If it does reach the cap the registered censoring rule applies and the
observation is **`PENDING`**, never `GATE FAIL`.

### 3.1 Graded quantities already on disk

* **P-BASE — `PASS`.** `D8_COLD_CD 0.03506349413916734` (`opt.log`), **exactly** equal to the
  registered `0.03506349413916734` reproduced five times. The twist-only edit is numerically inert on
  the primal, so the stored gradient column still describes this configuration.
* **`D8_START_CD 0.03877565033718443`** — the post-trim start, and the `cd_s` G3 reads.
* **G0 activity strings**, counted in `opt.log`: `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` ×1;
  `transonicPCOption 1;` ×1; `Global Cells: 41760` ×2; `^nProcs : 1$` ×4. `Mesh region0 size: 41760`
  occurs **×0** in `opt.log` and ×1 in `base/logMeshGeneration.txt` — see §4.
* `D8_FINAL_CD`, `D8_FINAL_CL`, `ADJ_DERIV`, `D8_OPT_ARM_COMPLETE`: **×0 — not yet emitted.**

**G1 is expected to be `GATE REACHED`, not `PASS`,** by construction: IPOPT ran with `max_iter 3`
(`opt/opt_IPOPT.txt` user-options block), so the registered 3-major cap terminates it with
`Maximum Number of Iterations Exceeded`. **A stop is not a measurement.**

---

## 4. INSTRUMENT DEFECT — Amendment 1 to `d8_grade.py` is INERT. Reported, NOT repaired.

**This is the finding of the lane so far and it is decisive.**

Commit `b8039512` landed `d8_grade.py` v1.0 → v1.1 as a `VERIFICATION_CHARTER` §2d.1 repair: the
frozen v1.0 G0 gate tested for `Mesh region0 size: 41760` in the **arm** log, a string DAFoam runtime
never emits, so as frozen G0 could not pass and its failure branch **voids the arm**. The amendment's
diagnosis is **correct** — I confirm the string occurs **zero** times in the live `opt.log` — and its
four §2d.1 conditions are properly stated. Rule 6 is honoured literally: zero lines above the banner
moved, and the amended `main` is appended below it.

**But the amended `main` never executes.**

* v1.0 `main` is defined at **line 264**.
* `if __name__ == "__main__":` … `sys.exit(main(sys.argv[1]))` is at **line 398**.
* The v1.1 `main` is defined at **line 449** — *51 lines below the dispatch that calls it.*

Python evaluates top to bottom. By the time `sys.exit(main(sys.argv[1]))` runs, `globals()["main"]`
is still the **v1.0** function; the interpreter exits inside that call and **line 449 is never
reached.** On every command-line invocation the v1.1 body is **dead code**.

**Proved by planted control, not by reading.** I built a scratch root whose `opt.log` carries
`Global Cells: 41760` and **not** `Mesh region0 size: 41760` — exactly the live arm's condition — with
`Mesh region0 size: 41760` present in `base/logMeshGeneration.txt` where v1.1 looks for it. Executed
as `__main__` the grader printed the **v1.0** check name and refused:

> `G0 Mesh region0 size: 41760   FAIL` →
> `REFUSE: G0 failed -- the arm is VOID on identity/activity; nothing below is graded`

The same file **imported** (which evaluates line 449 and never runs the `__main__` block) binds
`main.__code__.co_firstlineno == 449` and prints all six v1.1 G0 checks **OK** on the identical
planted root. The two routes disagree; only the import route carries the amendment.

**Consequence:** run as delivered, the D8 grader will **refuse at G0 and grade nothing** on a healthy
arm — precisely the failure Amendment 1 declared it had repaired. The 18 selftest checks and all six
negative controls pass in both routes, so **the selftest cannot see this defect**: it exercises
`gate_fd`, `read_scalar`, `read_peak_rss` and `read_eta` directly and never exercises the entry point.

**A second, independent copy problem.** Two graders exist and neither is usable as invoked:

| path | md5 | version |
|---|---|---|
| `/home/ubuntu/certonomous-runs/CURRICULUM-D8-a6-twist-opt/d8_grade.py` (19,157 B) | `04bba79c2a303bc3cf70af723da81dce` | **v1.0** — the md5 frozen in prereg §9 |
| `cases/dafoam/ladder-a/A6/curriculum_D8/d8_grade.py` (29,510 B, at HEAD) | `0b1907a994b626d5d869ce159bd181df` | **v1.1** |

The run-directory copy was never updated by the amendment, so grading from the run root uses v1.0 and
refuses by the original defect; grading from the case directory uses v1.1 and refuses because the
amendment is unreachable. `d8_run_arm.sh` (`cd66ead4b0dc1a26e460ea6bcc719551`) and `d8_stepplan.py`
(`8be156d5cff3ef373d3bf359eddcb317`) both still match their frozen §9 md5s exactly.

**I have not touched either grader.** Per the standing instruction a mid-item instrument rewrite needs
the supervisor's §2d.1 ruling, and this one is not mine to make: it changes the executable grading
path after compute has started and after a graded quantity (P-BASE) exists on disk. **The repair is
one line — moving the `if __name__` dispatch below line 449, or re-binding `main` after it — but the
question of whether that is a §2d.1 repair at this point in the item is the supervisor's.**

### 4.1 Three further instrument observations, bounded honestly

1. **`rc` is read and discarded.** `main` parses `rc_opt` from the ledger and prints it in the G1
   line, but **no branch gates on it** — the G1 verdict is decided by `exit_ok`, `capped`, `complete`
   and `oom` alone. Prereg §7 registers `rc = 0` as a completion clause (CLAUDE.md rule 4). The
   practical exposure is narrow — a `timeout` kill gives rc 124 *and* no `D8_OPT_ARM_COMPLETE`, so
   `complete` is false and G1 falls to `NOT A RESULT`; an OOM is caught by the `oom` branch off
   `docker inspect` — but the window "marker printed **and** rc ≠ 0" is ungated, and rule 4 is
   all-or-nothing by design.
2. **`read_adj` is the one reader with no plant and no proved refusal.** The selftest plants and
   proves refusals for `read_scalar`, `read_peak_rss` (three refusals), `read_eta` and `gate_fd` (five
   negative controls). `read_adj` gets none, and returns `{}` silently on an unparseable block. It
   cannot produce a **silent** zero — `main` prints `ADJ components parsed: %d` and `gate_fd` refuses
   per component on `adj.get(key) is None` — but that is structural containment downstream, not a
   control, and the D3 defect class this grader was built against is exactly "present key, empty
   value".
3. **Plant medium.** `read_peak_rss` plants to a real file **on disk** and reads it back, satisfying
   CLAUDE.md rule 3 literally. `read_scalar`, `read_fd` and `read_eta` plant into **in-memory
   strings**; their refusals are proved, but the disk round-trip is not.

### 4.2 The age guard — D13's caveat does NOT arise here, and the reason is on record

`d8_grade.py` implements **no** age guard, and this is by design rather than omission: prereg §7
discharges the completion rule through the launcher's **pre-launch** G8 cold-start guard, which
refuses to launch into a directory holding a written time directory, a `processor*` or a `reports/`.
That guard **fired and passed** — `G8 OK (opt)` in `queue_opt.out` — so every time directory under
`opt/` (`0.0001` … `0.0008`) was demonstrably produced by this run.

For this purpose the pre-launch guard is **stronger** than the post-hoc age guard, not weaker: it
proves the directory was empty *before* the solver started, rather than inferring it from mtimes
afterwards. Consequently the D13 situation — where DAFoam gzips `0/U` → `0/U.gz` mid-solve and
falsifies rule 4's "`0/T` is touched last at launch" premise — **does not arise for D8, and no
`AGE_GUARD_NO_REFERENCE` refusal is expected.** Stated plainly rather than left to be assumed.

## 5. `twist` idx6 — 8-of-9 BY CONSTRUCTION

`twist` idx6 is registered **`NOT A RESULT` in advance** (prereg §6; the row-37 flag), FD-ungradeable
on this rung: plateau disagreement **83.53 %** against a 10 % bar, best clearance **2.42×** against a
bar of 5. It is excluded **by name** from every table, aggregate and average, and it is **not
measured**, not merely omitted. `d8_stepplan.py` declines to rescue it even though the D8 extended
ladder would nominally reach `C ≥ 5` at `3e-1` on its stored `|J_adj| = 1.3619e-04`.

> **The endpoint gradient verification of this item is 8-of-9 BY CONSTRUCTION. It is not 9-of-9, it
> will not be reported as 9-of-9, and no reader may take its G4 verdict as one.**

## 6. What is not yet verified

* G1, G2, G3, G4, G5, G6, G7 — **`PENDING`**, arm `opt` still in flight at time of writing.
* **The bright line is not yet crossed.** `DAFOAM_CHARTER.md` §2: a DAFoam gradient is not a result
  until a finite-difference table stands beside it at a step proved to lie in the plateau. Arm `fd`
  (task `fdsub8`) **has not run**; `fd.log` does not exist; **zero `FD_DERIV` lines exist anywhere.**
  Until it returns, G4/G5/G7 are **`PENDING`** — named and priced, never absorbed — and this item
  claims **no** verified endpoint gradient.
* The **shipped** toolchain row is **NOT BOUGHT and named unbought** (prereg §10). Whatever G4 returns
  is a statement about DAFoam **with the IDWarp rotation patch applied** and about nothing else.
* Cost calibration row: **`PENDING`** until arm completion.

---

# UPDATE 1 — 2026-08-25 18:17Z — arm `opt` optimiser phase COMPLETE

The optimiser terminated while this lane watched. **Nothing was killed, stopped or restarted.**
At the time of writing the arm's final CD adjoint is still solving (main iteration 370, KSP residual
`3.989626945519e-06`); the ledger has not been written, so `rc`, `wall_s`, `core_min`,
`cgroup_memory_peak_B` and the `docker inspect` verdict are all still **`PENDING`**.

## 7. Arm `opt` — the optimiser's own record

`opt/opt_IPOPT.txt`, IPOPT 3.13.5, MUMPS, `max_iter 3`, `tol 1e-5`, `constr_viol_tol 1e-5`:

| major | objective CD | inf_pr | alpha_pr |
|---|---|---|---|
| 0 | `3.8772630e-02` | 1.20e-04 | — |
| 1 | `3.8776848e-02` | 3.80e-06 | 9.90e-01 h |
| 2 | `3.8678173e-02` | 2.10e-05 | 1.00e+00 h |
| **3** | **`3.8654633e-02`** | **1.34e-05** | 1.00e+00 h |

`EXIT: Maximum Number of Iterations Exceeded.` — Number of Iterations 3; unscaled objective
`3.8654633402661211e-02`; constraint violation `1.3351581499565501e-05`; overall NLP error
`8.6145237449880563e-04`; 4 objective evaluations and 4 gradient evaluations; **Total CPU secs in NLP
function evaluations 4133.719** against 0.015 s inside IPOPT itself.

Every major took a near-full step (`alpha_pr` 0.99, 1.00, 1.00) with `ls 1` — **no line-search
primals were bought**, which is the D1 behaviour the frozen §8 named as the reason its estimate errs
high.

### 7.1 Endpoint scalars, read from `opt.log`

| marker | value |
|---|---|
| `D8_COLD_CD` | `0.03506349413916734` |
| `D8_COLD_CL` | `0.45742680993954304` |
| `D8_START_CD` | `0.03877565033718443` |
| `D8_START_CL` | `0.4998809292514875` |
| `D8_FINAL_CD` | `0.03866430994135252` |
| `D8_FINAL_CL` | `0.49998857573476463` |
| `D8_ADJPOINT_CD` | `0.03865796797318573` |

`D8_DVS [('dvs.patchV', 2), ('dvs.twist', 7)]` — **9 design variables, `shape` absent**, confirming
the twist-only edit took. `D8_RESPONSES` carries `thickcon` 750, `volcon` 1, CD, CL — the registered
constraint set, with **no `lecon`/`tecon`**, as §1 registered.

Endpoint design (`d8_dvs.json`): `twist` = 0.4515, 0.1427, −0.1810, −0.5388, −0.6959, −0.6284,
−0.2127 deg; `patchV` = 295.0 m s⁻¹, AoA 2.4292 deg.

### 7.2 Gates decidable now, graded against the frozen bands only

* **P-BASE — `PASS`.** `D8_COLD_CD` = `0.03506349413916734`, **exactly** the five-times-reproduced
  registered value. The twist-only edit is numerically inert on the primal.
* **G1 optimiser termination — `GATE REACHED`** (subject to the `D8_OPT_ARM_COMPLETE` marker, still
  `PENDING`). The registered 3-major cap was reached; §7 forbids `PASS` here. **A stop is not a
  measurement.**
* **G2 CL feasibility — `PASS`.** |CL_final − 0.5| = **1.1424265235e-05** against a band of 5.0e-03:
  **437.7× inside** the band, and inside IPOPT's own 1e-5 `constr_viol_tol` as well.
* **G3 drag reduction — `PASS`,** and the margin is stated because the value is what carries the
  honesty. CD_start − CD_final = **1.1134039583e-04**, against the frozen requirement of
  10 η = **1.0910e-04**. That is **10.205 η against a 10 η bar** — a relative drop of **0.28714 %**
  of the trimmed start.

> **The margin above the bar is 2.2404e-06 = 0.2054 η, i.e. 2.05 %.** Measured in the same arm, the
> **same-design re-evaluation scatter is 6.3420e-06 = 0.581 η**: `D8_FINAL_CD` `0.03866430994135252`
> and `D8_ADJPOINT_CD` `0.03865796797318573` are two evaluations of CD at *identical* design
> variables. **The G3 margin over its threshold is 0.35× that scatter, so the PASS is not robust to a
> re-evaluation of the same design.** The verdict is `PASS` — the band was frozen before compute and
> the value clears it — and this paragraph does not soften it. It reports the interval, which is the
> channel CLAUDE.md rule 1 reserves for exactly this.

Two further notes for the reader. **The drag reduction is measured from the trimmed start, not the
cold baseline**, and this matters: trimming CL from 0.4574 to 0.4999 *raised* CD from 0.0350635 to
0.0387757, **+3.7122e-03 — thirty-three times the whole optimisation's gain.** The item measures what
the optimiser did at fixed CL, which is the registered quantity; it does not claim a drag reduction
against the untrimmed cold aircraft. And **major 1 raised the objective** (`3.8776848e-02` above major
0's `3.8772630e-02`) while cutting `inf_pr` from 1.20e-04 to 3.80e-06 — IPOPT bought feasibility
first, as expected of a restoration-free full step, and the net gain arrives in majors 2 and 3.

## 8. Measured cost rates — the frozen estimate erred HIGH, in the direction §8 predicted

From the `ExecutionTime` trace in `opt.log`, at the eleven primal completions (`Time = 1000`):

* cumulative (s): 69, 154, 218, 283, 347, 409, 1888, 2768, 3678, 4552, 4612
* **a primal costs 61–85 s, and 63–65 s once warm** — the frozen §8 priced **105 s**, so the primal
  basis is **~0.62×** its prediction. `endTime 1000` with `primalMinIters 1000` makes every primal run
  exactly 1000 iterations, which is why the figure is so nearly constant.
* the three optimiser majors that carry two flow adjoints each show gaps of **880, 909, 874 s**; net
  of their ~64 s primal that is **~410 s per flow adjoint** against the frozen **570 s** basis, i.e.
  **~0.72×**.
* the major-0→1 gap is **1479 s**, carrying the one-off `dRdWColoring_1.bin` construction
  (`opt/dRdWColoring_1.bin`, 3,033,080 B, written 17:09Z) on top of two adjoints.

**Projection for arm `fd` on measured rates:** 16 plan entries × 2 signs + 1 baseline = **33 primals**
× ~65 s ≈ **35.8 core-min**, against the frozen prediction of 57.8 and ceiling of 75.0.

## 9. Arm `fd` prepared, and the generation method PROVED

`fd/` was created from `base/` and passed through the frozen producer
`d8_gen_arm.py`, which asserts anchor count == 1 on each of its eight edits and dies otherwise.

**The method is proved, not asserted:** running the same producer on a scratch copy of
`base/runScript.py` reproduces `opt/runScript.py` — the script the live arm is running — **byte for
byte** (`diff -q` identical). The `fd` arm's `runScript.py` is likewise byte-identical to the live
`opt` arm's. `base/runScript.py` md5 `0de915d21166a91a9a54b37ab11214cf` matches the frozen §9
producer input exactly.

G8 preconditions for `fd` verified: `fd/0/U` present; none of `1000`, `250`, `500`, `750`, `reports`
exists; no `processor*`.

**Frozen instrument selftests, all run and all passing.** `d8_stepplan.py --selftest` reproduces the
`rung_n16_remaining_components` item's own registered `{s_lo, s_hi}` pairs **exactly** on all four of
its twist components — {0.03, 0.1}, {0.03, 0.1}, {0.05, 0.1}, {0.1, 0.2} — proving the arithmetic
frozen for D8 is the arithmetic that produced the published plan, and its negative control refuses a
gradient too small for the ladder. `d8_grade.py --selftest` reports `SELFTEST PASS` in **both**
copies — which is precisely why the selftest cannot see the §4 entry-point defect.

---

# UPDATE 2 — 2026-08-25 18:22Z — arm `opt` CLOSED, arm `fd` LAUNCHED

## 10. Arm `opt` completion — every registered clause holds

From `ledger.txt`, the arm's own record:

`ARM=opt TASK=optd8 IMG_ID=sha256:2927768a…f6d35 **rc=0** wall_s=**5251** ranks=1
**core_min=87.517** inspect(exit,oomkilled)=**[0 false]** cgroup_memory_peak_B=**NOT_MEASURED**
peak_rss_GiB=**9.97** memavail_pre_kB=26550116 memavail_post_kB=22220384 cap=12g`
— with `IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425`, `transonicPCOption 1;`,
`primalMinResTolDiff 10000;`, `nProcs : 1` and **`ASSERT_MD5 OK`**.

**Completion, all registered clauses (prereg §7):** `rc = 0` ✔; `D8_OPT_ARM_COMPLETE` present ×1 ✔;
`ASSERT_MD5 OK` in the ledger ✔; the G8 cold-start guard passed **before** launch ✔. **The arm is
complete. It is not partially complete and it was not stopped.**

* **G0 identity/activity — `PASS`** on the v1.1 substance: `IDWARP_SO_MD5` matches the registered
  patch hash; `transonicPCOption 1;` proves the activity; `^nProcs : 1$` ×4; `Global Cells: 41760` ×2
  in the runtime log and `Mesh region0 size: 41760` ×1 in `base/logMeshGeneration.txt`. **Under the
  frozen v1.0 text this same arm is VOID** — see §4.
* **G6 adjoint memory envelope — `PASS`,** with one corroboration missing and named. Peak RSS
  **9.970 GiB** over **327** samples (`rss_opt.txt`), against a predicted band of 11.0 GiB and a
  12 GiB cap. `OOMKilled = false` and exit code 0, so the observation is **not right-censored** and
  the §7.1 censoring rule does not fire. **But `cgroup_memory_peak_B = NOT_MEASURED`** — neither
  `memory.peak` path the launcher probes was readable — so the kernel's own independent reading of
  peak memory is **absent**, and G6 rests on the `docker stats` sampler alone. Stated rather than
  passed over: the sampler is the same instrument for both, and the second, independent channel the
  launcher was written to provide did not report.

**The endpoint adjoint (9 components, `d8_adj.json` / `ADJ_DERIV` in `opt.log`), CD w.r.t. DV:**
`twist` = −2.3148087e-03, −1.9664349e-03, −1.7271445e-03, −1.2841462e-03, −8.5846864e-04,
−5.4199077e-04, −1.9671544e-04; `patchV` = +8.7228404e-04, +1.0564077e-02. No `D8_OF_FALLBACK` — the
primary `of=` name resolved. The final adjoint converged at **main iteration 510, KSP residual
1.496666317173e-08**, against the registered ≈517-iteration anchor.

### 10.1 The registered reason for extending the FD ladders did NOT materialise — and that is a point in the item's favour

Prereg §4.1 extended the `twist` ladder to 5e-1 and 1e0 because *"near an optimum the reduced gradient
shrinks, so a ladder sized for the start design can run out of rungs at the endpoint."* **Measured, it
grew:**

| component | start-design \|J_adj\| | endpoint \|J_adj\| | ratio |
|---|---|---|---|
| `twist` 1 | 1.750730e-03 | 1.966435e-03 | **1.123×** |
| `twist` 2 | 1.469450e-03 | 1.727145e-03 | **1.175×** |
| `twist` 4 | 6.277000e-04 | 8.584686e-04 | **1.368×** |
| `twist` 5 | 3.797300e-04 | 5.419908e-04 | **1.427×** |
| `twist` 6 (excluded) | 1.361900e-04 | 1.967154e-04 | **1.444×** |

Three majors under a `max_iter 3` cap do not approach an optimum — IPOPT's own dual infeasibility is
**8.6145e-04**, not small — so the endpoint gradients are **1.12–1.44× larger** than at the start.
**Consequently no D8-extended rung was used by any `twist` component:** the selected steps are
s_lo ∈ {0.03, 0.03, 0.03, 0.03, 0.05, 0.1} and s_hi ∈ {0.1, 0.1, 0.1, 0.1, 0.1, 0.2}, all at or below
0.2 and therefore all inside the `rung_n16_remaining_components` ladder whose top rung is 3e-1. **The
extension is precautionary and unexercised; it cannot have functioned as a rescue because it was
never reached.**

## 11. The FD plan — produced mechanically, no human choice

`d8_stepplan.py d8_adj.json fdplan.json`, selftest passing in the same invocation:

| DV, idx | J_adj (endpoint) | s_lo | C(s_lo) | s_hi | C(s_hi) | status |
|---|---|---|---|---|---|---|
| `twist` 0 | −2.314809e-03 | 0.03 | 12.73 | 0.1 | 42.43 | PLANNED |
| `twist` 1 | −1.966435e-03 | 0.03 | 10.81 | 0.1 | 36.05 | PLANNED |
| `twist` 2 | −1.727145e-03 | 0.03 | 9.50 | 0.1 | 31.66 | PLANNED |
| `twist` 3 | −1.284146e-03 | 0.03 | 7.06 | 0.1 | 23.54 | PLANNED |
| `twist` 4 | −8.584686e-04 | 0.05 | 7.87 | 0.1 | 15.74 | PLANNED |
| `twist` 5 | −5.419908e-04 | 0.1 | 9.94 | 0.2 | 19.87 | PLANNED |
| `patchV` 0 | +8.722840e-04 | 0.1 | 15.99 | 0.3 | 47.97 | PLANNED |
| `patchV` 1 | +1.056408e-02 | 0.01 | 19.37 | 0.03 | 58.10 | PLANNED |

`PLANNED_COMPONENTS 8 of 8 gradeable`; `EXCLUDED_BY_NAME_IN_ADVANCE [('twist', 6)]`;
`PLAN_ENTRIES 16  PERTURBED_PRIMALS 32`. **These clearances are computed on the adjoint proxy; G7 is
graded on the measured |J_fd| and is not decided here.**

## 12. Arm `fd` launched — and the timeout disclosure

`./d8_run_arm.sh fd fdsub8 4500`, container `d8_fd_20260825T182022Z_2376204`,
`D8_MEMAVAIL_PRE_KB=22681500` (21.6 GiB, floor 12 GiB), `G8 OK (fd)`.

**Disclosed, because it is a departure from a number in the frozen file.** Prereg §8 gives arm `fd`
**both** a `timeout 7200 s` backstop **and** a registered ceiling of **75.0 core-min**. At 1 rank those
disagree: 7200 s is 120 core-min, **45 core-min above the arm's own registered cap**. Running to the
backstop would let the arm outlive its budget, and CLAUDE.md rule 12 is explicit that **an overrun
stops the run**. I therefore set the container timeout to **4500 s = exactly the registered 75.0
core-min**, making the frozen budget stop mechanical instead of dependent on a lane staying alive to
enforce it. **This cannot make any gate easier to pass**: a shorter arm can only produce a *shorter*
FD table, which `gate_fd` refuses on a component count ≠ 8. No gate, threshold, band or label is
touched. The frozen §8 backstop is not otherwise used.

## 13. Two measurements taken while the FD arm ran

**η is independently corroborated, and the G3 caveat sharpens.** CD has now been evaluated **three
times at the identical endpoint design**, twice in the `opt` container and once in a fresh `fd`
container: `D8_FINAL_CD 0.03866430994135252`, `D8_ADJPOINT_CD 0.03865796797318573`,
`FD_BASELINE_CD 0.03865353428107418`. The spread is **1.0776e-05 = 0.988 η** — the registered noise
floor `1.0910e-05` reproduced to a ratio of **0.988** across a container boundary, which is a genuine
independent check of η rather than a restatement of it. Against that, **G3's margin over its
threshold is 0.2054 η, about one fifth of the demonstrated same-design spread.** The verdict remains
`PASS`; the interval says how much room it has.

**The mechanical 3600-second stall rule MIS-CLASSIFIES this arm, and the row must not be cleaned by
it.** `COMPUTE_BUDGET_CHARTER.md` §2 defines exactly one cleaning rule — *"a ledger row over 3600 wall
seconds is an infrastructure stall, not solver cost"* — and the `opt` row is **5251 wall s**, so the
rule matches it and a mechanically-cleaned figure would be **0.000 core-min**. That is
demonstrably false. The container's own solver clock reaches **5020.30 s** at the final adjoint's last
recorded iteration, so **95.6 % of the 5251 s wall is solver-accounted**, leaving 230.7 s (4.4 %) for
container start, IDWarp import, mesh read, colouring I/O and teardown. **The gross figure 87.517
core-min is the one with evidence behind it**; the mechanical cleaned figure is unusable for this row
and is reported as such rather than quoted. The rule was calibrated on short OpenFOAM ledger rows; a
DAFoam optimisation arm is one long row by construction, and this is flagged upward rather than
silently worked around.

**CPU pinning, measured live.** This item's own draft note (`CPU_BINDING_DEFECT_PROPOSED_NOTE.md`,
**NOT FILED**) records that `mpirun -np 1` inside a container binds every rank to CPU 0, and
`d8_run_arm.sh` sets `--cpus=1` with no `--cpuset-cpus`. Confirmed on this arm: the `fd` solver
(pid 2376667) has **affinity `0`**. It is nevertheless **the only process on this box pinned to CPU 0**
and is taking **99.4 %** of it, with peer containers explicitly pinned elsewhere (cpuset 5,6,7,9 and
11). **The `fd` arm is therefore not CPU-contended**, and its core-minutes are reported gross with
that check named. Box loadavg at launch: 9.72 on 16 cores.
