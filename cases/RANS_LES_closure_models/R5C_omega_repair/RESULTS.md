# RESULTS — R5C, the `omega`-source repair

# VERDICT: GATE FAIL

**Graded against `PREREGISTRATION.md`, frozen and committed ALONE at
`f364cf2d` before any repair code ran on any case.**
Pre-registration sha256 `a1cfae5a49c52ddec41074ee62f92ce56e188e5c40ccc4923d33bf2a1ea1277a` — verified equal to the committed blob.
Comparator `grade_r5c.py`, sha256 `58eb99e389af41ebf02b93859f4a3901a56c21e7d477b98e545bf4e0b25605e5`.
Date: 2026-08-22. Lane: closure, option **C** of `docs/closure/R5_DECISION_MEMO.md`.

**The registered ladder, in the registered order (§3.1):**

| gate | threshold registered before the run | measured | |
|---|---|---|---|
| **G0** planted-zero | three comparators must see `PLANT = 1.234e-03`, else refuse (exit 2) | all three saw it; numeric to **2.4e-10** relative of the analytic value | **PASS** |
| **G2** W2 byte-identity | settle at **1492** / **354** and **14 of 14** `sha256` field matches | settle at **1492** and **354**; **14 of 14** matched | **PASS** |
| **G1** identity on R4's 12 targets | `max` rel L2 of `kDeficit`, `bijDelta` **≤ 1e-6**, and all 12 still COMPLETE **and** CONVERGED | **1.1848e-04** on `alpha_10_12000_4048`; and **3 of the 12** are not CONVERGED under G3 | **GATE FAIL** |
| **G1c** switch-active | `omegaSourceRepair true` in the log and `nNegSourceCells > 0` somewhere, on all 27 | true on 27 of 27; `nNegSourceCells` **476–2,274** | **PASS** |
| **G3** converged, not clipped | five criteria (a)–(e) | **10 of 27** converged | reported |
| **G4** completion count | **PASS at M ≥ 13** of 15, GATE REACHED 1–12, GATE FAIL 0 | **M = 1** | **GATE REACHED** *(overridden)* |

§3.1 rule 2: **G1 fails → the lane's verdict is `GATE FAIL`.** G4's own
`GATE REACHED` does not survive it, and §3.1 rule 4 is explicit that a §5
failure mode "overrides a PASS but never converts a GATE FAIL into a PASS".

**The registered consequence, applied:**

> **R4's 12 targets stand. The 15 hills remain INCOMPLETE. The R5C targets are
> reported and used for nothing.**

No R5C target enters any fit, any propagation, or any comparison that carries a
number. Nothing in `R4_sparta_build/` was edited, moved or regraded by this lane.

---

## 1. What was actually measured, in one paragraph

The repair is **not** a null result and it is **not** a success. The
Patankar-split source removes the `omega` clipping almost completely — **10 of
the 15 hills R4 left INCOMPLETE are now COMPLETE under the strict six-condition
rule**, with **zero** `bound(omega)` events where R4 clipped on all 5,000
iterations, and the remaining five clip on **5–29** iterations instead of 5,000.
**But the same damping that stops the clipping also makes a change-based settle
criterion fire earlier**, and on one of R4's twelve targets it fired **37 %
earlier** (iteration **853** against R4's **1362**) and stopped **1.18e-04**
away in relative L2 — 118 times the registered `1e-6` bar. The identity gate
caught it. That is what the gate was for.

---

## 2. The 27 rows

Settle iteration is the solver's own `CONVERGED (settle criterion) at iteration
N`; the write is at `N + ceil(N/5)`. "bound events" is the number of
iterations on which `bound(omega, omegaMin)` fired before the field write —
L-235's own counter, now inside the solver. G3 flags are (a) zero bound events,
(b) `min(omega) > 0` read from disk, (c) `convergedAt ≥ 100`, (d) residual
fall `≥ 1e6`, (e) zero iterations with `maxRelDomega == 0` before the settle
window opened. Identity columns are populated only for R4's 12 COMPLETE cases,
because those are the only ones with an R4 target to compare against.

| case | family | R4 | R5C COMPLETE | R5C CONVERGED (G3) | settle it. R4 → R5C | bound events | G3 a/b/c/d/e | identity rel L2 `kDeficit` | `bijDelta` | ExecutionTime s |
|---|---|---|---|---|---|---|---|---|---|---|
| `alpha_05_10071_3036` | hills | INCOMPLETE | INCOMPLETE | not converged | — → 80 | 5 | **n**/Y/**n**/**n**/Y | — | — | 6.07 |
| `alpha_05_4071_3036` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 841 | 0 | Y/Y/Y/**n**/Y | — | — | 18.60 |
| `alpha_05_7071_2024` | hills | INCOMPLETE | INCOMPLETE | not converged | 51 → 68 | 17 | **n**/Y/**n**/Y/Y | — | — | 5.96 |
| `alpha_05_7071_3036` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 69 | 0 | Y/Y/**n**/Y/Y | — | — | 8.24 |
| `alpha_05_7071_4048` | hills | INCOMPLETE | INCOMPLETE | not converged | 51 → 69 | 18 | **n**/Y/**n**/Y/Y | — | — | 7.22 |
| `alpha_075` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 123 | 0 | Y/Y/Y/**n**/Y | — | — | 7.41 |
| `alpha_10_12000_2024` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 111 | 0 | Y/Y/Y/**n**/Y | — | — | 8.04 |
| `alpha_10_12000_3036` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 114 | 0 | Y/Y/Y/**n**/Y | — | — | 7.23 |
| `alpha_10_12000_4048` | hills | COMPLETE | **COMPLETE** | not converged | 1362 → 853 | 0 | Y/Y/Y/**n**/Y | 1.1848e-04 | 1.1737e-08 | 14.32 |
| `alpha_10_6000_2024` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 71 | 0 | Y/Y/**n**/Y/Y | — | — | 6.34 |
| `alpha_10_6000_3036` | hills | INCOMPLETE | **COMPLETE** | **CONVERGED** | — → 1162 | 0 | Y/Y/Y/Y/Y | — | — | 21.34 |
| `alpha_10_6000_4048` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 1134 | 0 | Y/Y/Y/**n**/Y | — | — | 19.56 |
| `alpha_10_9000_2024` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 69 | 0 | Y/Y/**n**/Y/Y | — | — | 7.60 |
| `alpha_10_9000_3036` | hills | INCOMPLETE | **COMPLETE** | not converged | — → 1230 | 0 | Y/Y/Y/**n**/Y | — | — | 19.72 |
| `alpha_10_9000_4048` | hills | INCOMPLETE | INCOMPLETE | not converged | — → 67 | 7 | **n**/Y/**n**/Y/Y | — | — | 6.37 |
| `alpha_125` | hills | COMPLETE | **COMPLETE** | **CONVERGED** | 1391 → 1392 | 0 | Y/Y/Y/Y/Y | 3.5973e-08 | 2.4885e-07 | 20.64 |
| `alpha_15_10929_2024` | hills | INCOMPLETE | INCOMPLETE | not converged | — → 862 | 29 | **n**/Y/Y/**n**/Y | — | — | 13.69 |
| `alpha_15_10929_3036` | hills | COMPLETE | **COMPLETE** | **CONVERGED** | 1346 → 1346 | 0 | Y/Y/Y/Y/Y | 1.4753e-07 | 1.0670e-06 | 19.54 |
| `alpha_15_10929_4048` | hills | COMPLETE | **COMPLETE** | not converged | 1382 → 1382 | 0 | Y/Y/Y/**n**/Y | 4.3853e-09 | 9.0868e-08 | 20.42 |
| `alpha_15_13929_3036` | hills | COMPLETE | **COMPLETE** | **CONVERGED** | 1174 → 1174 | 0 | Y/Y/Y/Y/Y | 4.2566e-08 | 3.4490e-07 | 17.95 |
| `alpha_15_7929_3036` | hills | COMPLETE | **COMPLETE** | **CONVERGED** | 1625 → 1628 | 0 | Y/Y/Y/Y/Y | 3.9621e-08 | 2.6122e-07 | 21.73 |
| `AR_1_Ret_180` | ducts | COMPLETE | **COMPLETE** | **CONVERGED** | 133 → 133 | 0 | Y/Y/Y/Y/Y | 1.5248e-11 | 8.1757e-11 | 3.54 |
| `AR_3_Ret_180` | ducts | COMPLETE | **COMPLETE** | **CONVERGED** | 392 → 392 | 0 | Y/Y/Y/Y/Y | 5.7229e-11 | 5.8942e-10 | 14.63 |
| `AR_5_Ret_180` | ducts | COMPLETE | **COMPLETE** | **CONVERGED** | 694 → 694 | 0 | Y/Y/Y/Y/Y | 1.0082e-10 | 1.2744e-09 | 33.12 |
| `AR_10_Ret_180` | ducts | COMPLETE | **COMPLETE** | **CONVERGED** | 1378 → 1378 | 0 | Y/Y/Y/Y/Y | 1.4560e-10 | 2.1713e-09 | 108.72 |
| `PHLL10595` | PHLL10595 | COMPLETE | **COMPLETE** | not converged | 1243 → 1243 | 0 | Y/Y/Y/**n**/Y | 5.9503e-10 | 3.6237e-09 | 20.36 |
| `CBFS13700` | CBFS13700 | COMPLETE | **COMPLETE** | **CONVERGED** | 295 → 295 | 0 | Y/Y/Y/Y/Y | 1.5504e-10 | 1.7348e-10 | 13.90 |

**Counts.** R5C: **20 of 27 COMPLETE** under the strict rule against R4's
**12 of 27**; **10 of 27 CONVERGED** under G3. Of R4's 15 INCOMPLETE hills,
**10 are now COMPLETE** and **5 still clip**. All **12** R4-COMPLETE cases are
still COMPLETE; **3 of them** (`alpha_10_12000_4048`, `alpha_15_10929_4048`,
`PHLL10595`) fail G3(d).

---

## 3. G0 — the planted-zero control, run first

`PLANT = 1.234e-03`, planted into cell 0 of a **scratch copy** of
`alpha_10_12000_4048/1024/kDeficit` (the alphabetically first R4-COMPLETE
case; the choice is in code, not in prose). No R5C artefact was modified.

| control | planted | comparator must report | reported |
|---|---|---|---|
| **G0a** numeric | `kDeficit[0]` `-0.02167…` → `-0.02043…` | rel L2 within 1 % of the analytic `PLANT/‖f‖₂` | expected **5.144477e-12**, measured **5.144477e-12**, relative error **2.391e-10** |
| **G0b** byte | the same file | **DIFFERS** | DIFFERS |
| **G0c** history | a synthetic run converged on every other criterion, carrying (i) one `maxRelDomega = 0.0` row inside the pre-settle window, (ii) three `bounding omega` lines | **NOT CONVERGED** on each signature **independently** | NOT CONVERGED on both |

The comparator refuses (exit 2) on any of these; it did not have to.

---

## 4. G2 — the W2 byte-identical reproduction: the build is not a new solver

`kCorrectiveFrozenFoamV2` with `omegaSourceRepair false` — the legacy branch —
on fresh copies of the W2 record's own `0/`, `constant/` and `system/`.

| case | settle iteration | record | `sha256` matches |
|---|---|---|---|
| `ph` → `verification/runs/W2_sparta_runs/ph_frozen/1492/` | 1243, writes **1492** | **1492** | **7 of 7** |
| `cbfs` → `.../cbfs_frozen/354/` | 295, writes **354** | **354** | **7 of 7** |

Fields compared: `U`, `k`, `omega`, `nut`, `bijData`, `bijDelta`,
`kDeficit` — **14 of 14 byte-identical**, per-file hashes in
`artefacts/r5c_grading.json`. **The legacy branch of the new binary IS R4's
operator**, so every difference reported under G1 is the repair's and nothing
else's — not a compiler, not a rebuild, not a case file.

---

## 5. G1 — the identity gate, and exactly why it failed

### 5.1 The measurement

| case | settle it. R4 → R5C | shift | rel L2 `kDeficit` | rel L2 `bijDelta` |
|---|---|---|---|---|
| `alpha_10_12000_4048` | 1362 → **853** | **−37.4 %** | **1.1848e-04** | 1.1737e-08 |
| `alpha_125` | 1391 → 1392 | +0.1 % | 3.5973e-08 | 2.4885e-07 |
| `alpha_15_10929_3036` | 1346 → 1346 | 0.0 % | 1.4753e-07 | 1.0670e-06 |
| `alpha_15_10929_4048` | 1382 → 1382 | 0.0 % | 4.3853e-09 | 9.0868e-08 |
| `alpha_15_13929_3036` | 1174 → 1174 | 0.0 % | 4.2566e-08 | 3.4490e-07 |
| `alpha_15_7929_3036` | 1625 → 1628 | +0.2 % | 3.9621e-08 | 2.6122e-07 |
| `AR_1_Ret_180` | 133 → 133 | 0.0 % | **1.5248e-11** | 8.1757e-11 |
| `AR_3_Ret_180` | 392 → 392 | 0.0 % | 5.7229e-11 | 5.8942e-10 |
| `AR_5_Ret_180` | 694 → 694 | 0.0 % | 1.0082e-10 | 1.2744e-09 |
| `AR_10_Ret_180` | 1378 → 1378 | 0.0 % | 1.4560e-10 | 2.1713e-09 |
| `PHLL10595` | 1243 → 1243 | 0.0 % | 5.9503e-10 | 3.6237e-09 |
| `CBFS13700` | 295 → 295 | 0.0 % | 1.5504e-10 | 1.7348e-10 |

**The correlation is perfect and it is the whole diagnosis.** Eleven of twelve
cases settle at the **identical iteration** under the repaired operator and
agree with R4's targets to **1e-7 – 1e-11**. The one case whose settle iteration
**moved** is the one — and the only one — that fails. **The registered
fixed-point identity of §2.2 is confirmed, not falsified**: where the two
iterations stop at the same place they produce the same target to eleven
figures on the ducts.

### 5.2 Why the twelfth case moved — and what it says about the settle criterion

On `alpha_10_12000_4048` the difference is **not** concentrated in a few cells:
the largest single cell carries **0.08 %** of the squared error, the top 20 cells
**1.4 %**. It is a broad, small drift — `omega` differs by **1.87e-05** relative
L2, `nut` by **5.44e-03**, `k` by **exactly 0** (it is frozen data). The
repaired run settled **509 iterations earlier** and therefore stopped **further
from the shared fixed point**.

**The mechanism, stated as a defect in the criterion rather than in the repair.**
The settle criterion is `omega initRes < 1e-8` **and**
`max|Δomega|/max|omega| < 1e-9`, sustained 50 iterations — both **change**
measures, and `max|omega|` normalises globally, so a field whose maximum is
`O(1e6)` can still drift in its low-`omega` regions while the criterion is
satisfied. **The Patankar sink damps the iteration more strongly** — that is
precisely what stops `omega` going negative — **so the change bar is reached
sooner, at a point that is further from the answer.** A criterion that measures
change cannot bound the distance to the fixed point, and a more damped iteration
exploits that gap.

That is **L-235 one notch subtler.** L-235: *a settle criterion that measures
change cannot tell convergence from clipping.* Here: **it cannot tell convergence
from damping**, and the field it returns is not flat, not clipped, and not
obviously wrong — it is simply 1.2e-04 away.

### 5.3 What the pre-registration got wrong, said plainly

§2.2's registered claim — that the two operators share a fixed point in exact
arithmetic — **is confirmed** (§5.1). What was wrong is §3's **derivation of the
`1e-6` tolerance**, which read:

> *"the only admissible source of difference is the distance at which each run's
> outer iteration stops, bounded by the solver's own settle criterion (`omega
> initRes < 1e-8` and `max rel domega < 1e-9`…). `1e-6` therefore sits …
> two orders above the `1e-8` residual tolerance."*

**That conflated a linear-solver residual with a distance in field space.** A
residual bound of `1e-8` on the `omega` matrix does not bound `‖kDeficit_R5C
− kDeficit_R4‖/‖kDeficit_R4‖` at `1e-6`, and the measurement falsified it at
`1.18e-04`. The threshold is **not** changed — gates are closed after first
compute (rule 2) — and the verdict stands as it fired.

### 5.4 G1c — the repair was actually exercised

`omegaSourceRepair` reads **true** in all 27 logs, and `nNegSourceCells`
reaches **476–2,274** cells per case (it is **476** even on the converged
`PHLL10595` legacy run). **The negative source is not a hill pathology; it is
present on every case in the training set**, including the two the W2 record
validates. A silent no-op is ruled out by measurement, not by inspection.

---

## 6. G3 — converged, not clipped: 10 of 27, and one registered criterion was
   miscalibrated

### 6.1 What (a), (b), (c) and (e) did

* **(a) bound events.** R4: six hills at **0**, thirteen at **5,000**, two at
  **1**. R5C: **22 of 27 at 0**, five at **5, 7, 17, 18, 29**. The clipping is
  removed, not merely reduced, on 22 cases.
* **(b) `min(omega)` from disk.** Positive on **27 of 27**. The
  `max(omega, omegaMin_)` clamp inside the repair was **never active**: the
  smallest written `omega` anywhere is **1.42e-11** and `omegaMin_` is
  `SMALL`.
* **(c) `convergedAt ≥ 100`.** Excluded **7** cases that settled at
  **67–80**. R4's two false convergences settled at **51**; these settle only a
  little later and are the same shape — under-converged, not converged.
* **(e) zero `maxRelDomega == 0` rows before the settle window.** **0 on all
  27.** Nothing in R5C is clipped flat.

### 6.2 What (d) did, and it is a gate-design finding

**(d) required `initRes(1)/initRes(convergedAt) ≥ 1e6`.** It excluded
**12** cases, including **3 of R4's own 12 COMPLETE targets** — among them
**`PHLL10595`**, whose R4 run is the W2-validated reference, at **9.167e5**,
i.e. **8.3 % short of the bar**.

The registered reason for `1e6` was *"the hills start at `O(1e-1)`–`O(1)`
… so a genuine fall is ≥ 7 orders"*. **Measured, that premise is false.**
`initRes` at iteration 1 across the 27:

| `initRes(1)` | cases |
|---|---|
| `4.7e-05` – `9.9e-05` | 4 (`alpha_10_12000_4048` **4.70e-05**, `alpha_075`, `alpha_10_6000_4048`, `alpha_05_4071_3036`) |
| `2.1e-04` – `9.9e-04` | 7 |
| `3.8e-03` – `1.1e-02` | 13 |
| `2.0e-01` – `5.6e-01` | 3 (the two R4 clipped-flat hills and `alpha_05_7071_3036`) |

Only **3 of 27** start at `O(1e-1)`. The initial condition is the **baseline
k-omega SST `omega` field**, which is a *good* initial guess on most cases, so
`initRes(1)` measures **the quality of the initial guess**, not the depth of
convergence — and a case that starts closer has less distance to fall.
Meanwhile `initRes(convergedAt)` is `1e-9`–`1e-13` on **all 27**, because
the solver's own settle criterion already enforces `< 1e-8`.

**The reading: (d) is a ratio where an absolute bar was needed, and the absolute
bar was already in the settle criterion. It is redundant at best and, as
registered, it rejects R4's own W2-validated reference case.** It is left
standing and its exclusions are reported, because a threshold is not rewritten
after it fires (rule 2). A future pre-registration should replace it with a
criterion that bounds **distance to the fixed point**, which is the quantity
§5.2 shows nothing here measures.

---

## 7. G4 — the completion count

**M = 1 of 15** (`alpha_10_6000_3036`, settle 1162, 0 bound events, all five
G3 criteria met). Registered ladder: PASS at ≥ 13, GATE REACHED at 1–12, GATE
FAIL at 0 → **GATE REACHED**, **overridden by G1's GATE FAIL** under §3.1.

The number that is *not* the gate but is the finding: **10 of the 15 are
COMPLETE under the strict six-condition rule**, against **0 of 15** in R4. The
gap between 10 and 1 is entirely G3(c) and G3(d) — three of the ten fail (c)
only, six fail (d) only, and one passes both. Under §6.2's reading of (d) that
gap is mostly an artefact of a miscalibrated criterion; **that is an argument
for a new pre-registration, not for regrading this one.**

The registered partial-outcome rule applies unchanged: the 27 R5C targets are
one set under one operator, **used together or not at all**, and under this
verdict they are used for nothing.

---

## 8. Departures — dated

**D-1 (2026-08-22). The four DUCT cases were mis-built on the first attempt and
were discarded, not restarted.** `build_r5c_cases.py` initially copied only
`0/`, `constant/` and `system/`, and the DUCT family's `0/U` carries
`#include "../caseDef"` — a **case-root** file. `kCorrectiveFrozenFoamV2`
exited on `FOAM FATAL IO ERROR … Cannot open include file … /../caseDef while
reading dictionary "0/U"` **before iteration 1**, writing no time directory
(`rc = 1`, ~0.8 s wall each). Because the pre-registration's §4 guard forbids
restarting a case in place, the four destinations were **deleted entirely** —
after asserting that none held a numeric time directory — and rebuilt from
source. The script now copies case-root regular files and skips run artefacts
(`rc`, `wall_seconds`, `omegaHistory.csv`, `log.*`). **Waste: 3.2 s wall,
0.0009 core-h, $0.00005.** No gate, threshold, cap or label moved. A build
defect of this lane's, reported rather than absorbed.

**D-2 (2026-08-22). The first compile of `libspartaFrozenV2` failed and was
corrected before any case ran.** `this->subOrEmptyDict("RAS").getOrDefault
<Switch>(...)` needs a dependent-name `template` disambiguator; it was
replaced with `Switch::getOrDefault("omegaSourceRepair", dict, Switch(false))`,
which reads the same key from the same dictionary with the same default. Zero
compute, zero cases affected — the binary that failed to link never existed.

**D-3 (2026-08-22). `build_r5c_cases.py` gained an `--only <case>…` flag
after first compute**, to rebuild the four cases of D-1 without touching the
23 that had already run. It is a build-script convenience: the §4 guard is
unchanged and still refuses any destination holding a `0/` or a numeric time
directory, so `--only` cannot silently re-open a run that produced an answer.
No gate, threshold, cap or label moved.

**D-4 (2026-08-23, closure supervisor — the re-formed one; the grading lane was
killed by the session limit before commit 3).** Three disclosures, none moving a
gate, threshold, cap or label. **(a) Commit plan.** §7 registered the comparator
in commit 2; `23b9d7ba` (commit 2) carried the solver, build log, build and run
scripts but **not** `grade_r5c.py` (mtime 20:58Z, after the 20:56:27Z commit).
The comparator lands in commit 3 instead. The grading path itself was fixed at
commit 1 as §7 requires — the frozen `PREREGISTRATION.md` on disk was re-hashed
against the committed blob (`a1cfae5a…1277a`, equal) before grading. **(b)
Artefact names.** `artefacts/inputs_sha256.json`, `artefacts/pids.json` and
`artefacts/g2_w2_sha256.json`, named in §2.4, §6 and G2, were never written as
separate files. Their content exists: the `0/`-field copy identity was asserted
in code at build time (`build_r5c_cases.py` `assert a == b` per field) and the
G2 per-file sha256 pairs are in `artefacts/r5c_grading.json`. **(c) Independent
re-grade.** On 2026-08-23 the supervisor re-ran the comparator (same sha256
`58eb99…605e5`) end to end — G0 replanted and re-passed, all 27 rows and both
W2 legacy runs re-read from disk. The regenerated `r5c_grading.json` differs
from the 2026-08-22 grading in **zero** fields. The verdict of record is the
comparator's own, twice: **GATE FAIL**.

**Not a departure, recorded because a reader will look for it.** §6's reduction
clause ("if, after the first 6 hills complete, the projected 27-case total
exceeds 0.6 core-h, drop to concurrency 3") was **never triggered** — the whole
set finished at **0.140 core-h**.

---

## 9. Compute — actual against registered

Rate **$0.0513 per core-hour**, c7a.4xlarge, **owner-stated 2026-08-21/22,
reported-by-owner and NOT measured** (`COMPUTE_BUDGET_CHARTER.md` §5,
CLAUDE.md rule 12). Core-hours are each case's own `ExecutionTime` × 1 rank
÷ 3600. All runs serial.

| item | registered | actual |
|---|---|---|
| 27 repaired re-extractions | 0.184 core-h | **0.1256 core-h** (452.1 s) |
| 2 legacy W2 reproductions (G2) | 0.00603 core-h | **0.0140 core-h** (50.2 s) |
| `postProcess -func 'grad(U)'`, 29 dirs | 0.020 core-h (estimate) | **not separately instrumented** — `postProcess` writes no `ExecutionTime` line; bounded above by recorded wall minus solver `ExecutionTime` = **101.4 s = 0.028 core-h** |
| four discarded duct attempts (D-1) | — | **0.0009 core-h** |
| **total** | **0.210 core-h = $0.0108** | **0.140 core-h measured + ≤ 0.028 bounded = ≤ 0.168 core-h = ≤ $0.0086** |

**Under the registered estimate (≤ 80 % of it) and at ≤ 17 % of the registered
1.0 core-h / $0.0513 cap.** Total recorded wall across the 29 case directories:
**603.7 s**, at ≤ 6 concurrent serial ranks against a box load of ~13 from the
T-family thermal lane. **Nothing was reniced and no other lane's job was
touched.**

The memo's headline for option C was **0.184 core-h / $0.009**; this lane spent
**0.140 core-h measured**, on 29 runs rather than 27.

---

## 10. Artefacts, and what is not committed

| what | where |
|---|---|
| frozen pre-registration | `PREREGISTRATION.md`, sha256 `a1cfae5a49c52ddec41074ee62f92ce56e188e5c40ccc4923d33bf2a1ea1277a`, commit `f364cf2d` |
| comparator | `grade_r5c.py`, sha256 `58eb99e389af41ebf02b93859f4a3901a56c21e7d477b98e545bf4e0b25605e5` |
| full grading record, all gates, all 27 rows, every `sha256` | `artefacts/r5c_grading.json` |
| build log tails, and the mtimes proving R4's binaries were not rebuilt | `artefacts/build_log_tail.txt` |
| repaired solver and library | `sdk/openfoam/sparta/spartaFrozenV2/`, `sdk/openfoam/sparta/kCorrectiveFrozenFoamV2/` |
| **bulk field data — NOT committed** | `/home/ubuntu/closure-data/r5c/frozen/<case>/` (27), `/home/ubuntu/closure-data/r5c/w2_legacy/{ph,cbfs}/` (2), `/home/ubuntu/closure-data/r5c/build/`, `/home/ubuntu/closure-data/r5c/grading_scratch/` |
| per-iteration convergence history | `/home/ubuntu/closure-data/r5c/frozen/<case>/omegaHistory.csv` |

**R4's artefacts are untouched.** `libspartaTurbulenceModels.so` (Aug 1 01:09)
and `kCorrectiveFrozenFoam` (Aug 1 00:15) were not rebuilt;
`/home/ubuntu/closure-data/r4/` was read and never written;
`cases/RANS_LES_closure_models/R4_sparta_build/` was read and never edited.
`docs/LAB_STATE.md` carries the pointer line.

**Two new compiled artifacts exist that `docs/OPENFOAM_SOLVER_BUILD.md` §1 does
not list** — `libspartaFrozenV2.so` and `kCorrectiveFrozenFoamV2`, both under
`sdk/openfoam/sparta/`, both building with plain `wmake libso` / `wmake` in
that order. That page belongs to another team; the fact is recorded here rather
than edited into it.

---

## 11. What this lane did NOT do

No fit. No selection. No propagation. No model. **No TEST or VALIDATION case was
opened for any purpose** — `r4_lib.assert_no_test_case` is called on the case
list in `build_r5c_cases.py` and the assertion is in the code. Options **A**,
**A′**, **B1**, **B2**, **C2** and **D** were not started; the **R5 direction**
and any re-opening of **R2/R3** were not touched. They remain Sanaa's.

Nothing was sent, filed, uploaded, posted or registered outside this box.
