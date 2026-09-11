# DRIVAER R1 STAGE A — GRADING RECORD

**Rung:** `DRIVAER_R1_STAGE_A` · **Team:** cfd · **Graded:** 2026-09-11T16:20Z
**Pre-registration:** `verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md`
(frozen `903dc88d1`; Addendum 1 `5e12ce4ba`, Addendum A1 `90f2fcbdd`, Addendum A2 `b06e0526b`)
**Report artifact:** `verification/runs/navier_class/DRIVAER/r1_fine/STAGE_A_REPORT.json`

---

## 0. NOTHING IS WITHDRAWN — THIS IS THE FIRST STAGE A VERDICT

**No Stage A value has ever been published in a committed repository document.** Before
today the registered invocation exited **2** on its own p-field planted control and wrote
no report. `git log --all -- verification/campaign/DRIVAER_R1_STAGE_A_RESULTS.md` returns
nothing: this file is created, not revised. **Nothing here retracts, withdraws or corrects
a previously stated number, because there was none.** A reader who infers a withdrawal has
inferred something that did not happen.

**One uncommitted artifact predates this grading and is preserved, not overwritten.** A
`STAGE_A_REPORT.json` was written at **2026-09-11T16:04:38Z**, 67 s after the A2 repair
commit, by an invocation this lane did not make. It is kept byte-intact at
`verification/runs/navier_class/DRIVAER/r1_fine/STAGE_A_REPORT.PRE_LANE_1604Z.json`
(sha256 `f09e490b3c7aa16d9b40639fa2a58e25ee66e0d8b856ff3ab768cf9e3a48a7f0`). This lane's
independent re-run reproduces it **identically** on every planted-control field, every
multiplicity, the whole histogram and all three gate verdicts.

---

## 1. THE VERDICT

| item | verdict | basis |
|---|---|---|
| **RUNG — Stage A** | **NOT A RESULT** | CLAUDE.md rule 5 limb (1): the single level is neither iteratively converged nor plateaued |
| Gate A1 completion and instrument | **GATE FAIL** | iterative `NOT_CONVERGED`; Cd `NOT_PLATEAUED`; Cl `NOT_PLATEAUED` |
| Gate A2 Cd gross-error band | band verdict **PASS**, converted to **NOT A RESULT** | Cd 0.29795528411 inside [0.15, 0.60]; converted by rule-5 limb (1) |
| Gate A3 Cl gross-error band | band verdict **PASS**, converted to **NOT A RESULT** | Cl 0.0078616272713 inside [−0.50, +0.50]; converted by rule-5 limb (1) |

**Rule 5 applied in order, and the direction is one-way.** The band verdicts were computed
**first and unconditionally** — A2 and A3 each returned **PASS** on their own terms, and
that is recorded above rather than suppressed. Limb (1) then converted those PASSes **into**
`NOT A RESULT`. Nothing was converted in the reverse direction and no `NOT A RESULT` became
a PASS. **Gate A1's `GATE FAIL` stands as recorded**: A1 is the limb whose job is to detect
the non-convergence, and erasing its finding would erase the reason the rung is not a result.

**NO GCI IS QUOTED, AND THE REASON IS NOT THE KNOWN-FALSE ONE.** Stage A registers **one
level** (`levels: ["fine"]`) and **never routes through `grade_ladder`** (`grade_drivaer.py`
:756–760). There is no grid triple, so there is no order and no GCI to quote. The report
contains no `GCI`, `triple`, `CONVERGING` or `monotone` string — **checked, not assumed.**
The false unconditional reason at `scripts/roache_triple.py:632` ("NO GCI is quoted because
the three values are not monotone") is therefore **NOT inherited by this verdict**. That line
is routed to the verification team and was not touched here.

### CLAIM CAP — carried, not summarised away

`credential_eligible: false`. The fine mesh does not meet `docs/standards/MESH_STANDARD.md`:
**max_skewness 10.315144 against a threshold of 4.0 — 2.579× over, on 16 faces**; max
non-orthogonality 64.940718; `Failed 3 mesh checks`. Matrix status is **STATED LIMITATION**,
never HOLDS and never GATE REACHED. Separately, §3 of the pre-registration forbids reading an
in-band Stage A Cd as agreement with `Cd_ref = 0.2758368`: Stage A has no wall layers and
y+ varies ~4× across levels. **An in-band value here is the absence of a gross error, not
agreement.**

---

## 2. THE DECISIVE MEASUREMENT — the repaired planted control on the real mesh

The control that refused on 2026-09-10 at exactly **3.000000×** its own expectation now
**PASSES on `r1_fine`, with both arms fired.**

| | arm m = 1 | arm m > 1 |
|---|---|---|
| cell | 1563756 | 1702645 |
| multiplicity in face-owner list | 1 | 3 |
| `reader_delta` | 1.980299975912203e-05 | 5.940899927736609e-05 |
| `expected_delta` = m·PLANT/n | 1.98029997584034e-05 | 5.940899927521021e-05 |
| reader/expected | **1.000000000036** | **1.000000000036** |
| `passed` | **True** | **True** |

`passed = True` overall · `planted = 5.0` (`PLANT_KPRESS`) · reader `body_mean_pressure` ·
47 vehicle patches · `base_mean_p` −149.6886460146719 · artifact
`verification/runs/navier_class/DRIVAER/r1_fine/3000/p`.

**Mesh census:** `n_body_cells` **252,487** (face-owner entries) · `n_distinct_owner_cells`
**241,227** · multiplicity histogram **{1: 231554, 2: 8189, 3: 1429, 4: 12, 5: 40, 6: 1,
7: 2}**.

**The histogram closes against both counts, checked:** Σ m·count = **252,487** == `n_body_cells`
and Σ count = **241,227** == `n_distinct_owner_cells`. The 11,260-entry gap between the two
counts is exactly the repeated ownership that produced the false refusal.

**The old formula is still wrong on this mesh, and that is the point.** Under the superseded
`expected = PLANT/n`, the m=3 arm reads 3.000000× expected and refuses. The repair does not
make the reader see more; it makes the *expectation* account for what the reader was always
correctly summing.

---

## 3. GATE A1 — the numbers behind the GATE FAIL

**Iterative convergence: `NOT_CONVERGED`.** Final Initial residuals at iteration 3000 against
`RES_TOL = 1e-4`:

| field | final initial residual | × over tol |
|---|---|---|
| **Uy (worst)** | **1.476127633e-02** | **148×** |
| p | 6.593783263e-03 | 66× |
| Uz | 3.787397511e-03 | 38× |
| Ux | 6.957024841e-04 | 7.0× |
| k | 2.928393973e-04 | 2.9× |
| omega | 7.046433594e-05 | **under tol** |

**Plateau (Addendum A1's repaired windowed limb, 300-sample window = 10 % of `endTime`,
3000 rows available, `armed: true`):**

| quantity | state | excursion (max−min)/|mean| | tol | × over |
|---|---|---|---|---|
| Cd | **NOT_PLATEAUED** | **6.31302e-02** | 5.0e-03 | 12.6× |
| Cl | **NOT_PLATEAUED** | **11.270582** | 5.0e-03 | 2254× |

Cd window mean 0.29982111, min 0.29077325, max 0.30970101. Cl window mean 0.00411303,
min −0.01887977, max 0.02747641 — the Cl excursion is large because the window mean sits
near zero, which is a property of the statistic and is disclosed rather than smoothed.

**Rule-4 completion HOLDS and is NOT the reason for the GATE FAIL.** Verified independently
by this lane on the run directory: `rc=0` sidecar (`rc` and `RC.txt`); exactly **one** `End`
line; last time **3000** == `endTime` 3000; `deltaT` 1 and **3000** `ExecutionTime` lines ==
round(3000/1); fields `p U k omega nut phi` present at `3000/`; age guard clear — `3000/p`
at 2026-09-11T10:45:01Z against `0/U` at 2026-09-11T00:34:23Z, **+36,638 s newer**. The A1
failure list contains only the three convergence and plateau items; no completion clause is
among them.

---

## 4. THE REGISTERED PREDICTIONS — how each limb landed

**A1.5, registered 2026-09-11T04:50:04Z at iteration 1175/3000**, before `endTime` and before
the 300-sample window existed:

> *"the repaired plateau limb will return `NOT_PLATEAUED` for Cd on this run. By rule 5 limb (1)
> the rung is then **NOT A RESULT**."*

**HELD, on both halves.** Cd returned `NOT_PLATEAUED` (excursion 6.31302e-02 against 5.0e-03)
and the rung is `NOT A RESULT`. **The plateau limb did NOT return PLATEAUED**, so the
instrument finding the pre-registration reserved capitals for does not arise.

**A2.8, frozen in commit `b06e0526b` at 2026-09-11T16:03:31Z**, self-split into a non-blind
and a blind half. Every stated number held:

| predicted | measured | held |
|---|---|---|
| m>1 arm delta 5.940899927736609e-05 *(declared NOT blind — printed by the original refusal)* | identical | — |
| m=1 arm `reader_delta` == 1.98029997584034e-05 within 2 % | 1.980299975912203e-05, 3.6e-11 relative | **YES** |
| control `passed = True` | `passed = True` | **YES** |
| histogram {1:231554, 2:8189, 3:1429, 4:12, 5:40, 6:1, 7:2} | identical | **YES** |
| `n_body_cells` 252,487 · `n_distinct_owner_cells` 241,227 | identical | **YES** |
| Gate A1 **GATE FAIL**, Uy 1.476127633e-02, Cd excursion 6.31302e-02, Cl excursion 11.2706 | identical | **YES** |
| Gates A2, A3 **PASS** on their bands; Cd 0.29795528411, Cl 0.0078616272713 | identical | **YES** |

### 4a. A2.8's INTERNAL TIMESTAMP IS INCONSISTENT WITH ITS OWN FILE, AND THE PRIORITY SURVIVES ON THE COMMIT

A2.8 reads *"Registered 2026-09-11T16:07Z"*. That string is **later than the document's own
last write (16:01:05Z) and later than the commit that froze it (16:03:31Z)**, and later than
the 16:04:38Z report it claims to precede. **Read on the string alone the prediction would
look non-blind.** It is rescued by the freeze, not by the stamp: commit `b06e0526b` at
**16:03:31Z** precedes the 16:04:38Z report by **67 seconds**, and that commit is the
evidentiary anchor. **The `16:07Z` string is wrong and should be struck by dated addendum
rather than relied on.** Recorded against interest: 67 s is a thin margin, and this lane
**cannot verify the negative** that the histogram and `n_distinct_owner_cells` were not
computed by anyone before 16:03:31Z. What can be verified is the commit order, and it holds.

---

## 5. FINDINGS AGAINST THE RECORD, STATED RATHER THAN CARRIED SILENTLY

**5.1 — A2.6's cancellation figures understate the measured floating-point deviation by two
to three orders. The conclusion survives; the numbers do not.** A2.6 reports a reconstructed
relative error of **1.5e-13 (m=1) and 3.6e-14 (m=3)**. Measured on the real field, both arms
deviate by **3.6289e-11** — ~240× the m=1 claim and ~1000× the m=3 claim. The likely cause is
visible in the reconstruction's own premise: A2.6 reconstructs *"at p-magnitudes of ±60"*,
while the field's `base_mean_p` is **−149.69**, so the reconstruction used p magnitudes
roughly 2.5× too small. **The supervisor's conclusion is unchanged and is confirmed on the
real data: this is not a hazard.** The margin to the 2 % tolerance is **5.5e8×** —
**8.7 orders**, not the claimed 11. A dedicated point: the two arms deviate by an *identical*
relative amount to twelve digits, which is consistent with the two summations differing only
in one planted term.

**5.2 — COVERAGE FACT, stated as the supervisor requires and not overstated.**
`grade_drivaer.py:893` hardcodes `ctrl_ok = dict(passed=True, ...)` and hands it to
`RT.grade_ladder` at :899, :908, :973, :981. **Confirmed by this lane: there is no control
with `passed=False` anywhere in `grade_drivaer.py`** (grep for `passed=False` returns
nothing). ARMING PROOF 5 proves the control **detects** the defect; **`grade_drivaer.py`'s own
suite never composes a FAILING control with `grade_ladder`.** That composition **is** proven —
`scripts/roache_triple.py` drives a blind reader through `grade_ladder` and asserts it
refuses (:935–942), and `assert_plant_control` refuses on `not pc.get("passed")` (:509) —
but **across two suites, not in one.** This record does not claim `grade_drivaer.py`'s suite
proves the wiring.

**5.3 — the comparator pin in force is A2.7's, and A1.6's is superseded.** On disk
`cases/navier_class/DRIVAER/grade_drivaer.py` hashes to
**`6106cf6db9ac7dd7d767e140de7ba2e389829d02c30f5d251fcec0c6b83c26d7`**, matching **A2.7**
exactly and byte-identical to the blob at HEAD. It does **not** match A1.6's
`1b51dc1d4438f66a…` (superseded by A2) nor §8's `0eddb5588c337114…` (superseded by A1.6).
**Hashing this file against A1.6 or §8 produces a false BLOCKED.** All five remaining §8 pins
verified unchanged on disk: reference `bb504af34ed077f1`, case writer `b1b67ae1249636ce`,
launcher `c8bd51d49f53b687`, mesh generator `0d4e6263e4ffbfd5`, `system/forceCoeffs`
`4482746d0e336546`.

**5.4 — monitor M5 remains as A2.9 disclosed it, and is NOT repaired here.** §10's M5 reads
*"> 3600 wall s with no new write"* without naming which write; `writeInterval 1000` makes
field writes ~12,468 s apart, so read on fields M5 would have fired three times on this
healthy run. It is a registered monitor and was not touched.

---

## 6. WHAT THIS RUNG DOES NEXT

`NOT A RESULT` here is the honest outcome and **not a failure of the case**. The signal is
**drifting, not oscillating**: the case must run **longer**, not differently. It routes to a
dated successor with a longer run and the repaired criterion registered up front. **It is not
a numerics escalation.** The mesh non-conformance (skewness 2.579× over) is a separate defect
and is not cured by running longer.

---

## 7. COST — rule 12, estimate versus actual

The full rule-12 comparison **LANDED in `docs/COST_CALIBRATION.md` as id
`C-20260911T162610.013753Z-ff39f947`**, and its provenance copy is at
`verification/runs/navier_class/DRIVAER/r1_fine/COST_CALIBRATION_ROW_LANDED.md`.

**It was expected to be blocked and was not — recorded because the difference matters.**
The row was drafted at 15:37Z as *parked*, because `scripts/append_record.py` refused
(exit 8, D549 clause 1a) on a pre-existing malformed id at that register's line 522
(`C-20260910T230023.521144Z-mrfr1a1` — a seven-character suffix containing a non-hex
character where 8 hex are required). **The verification team repaired that blocker at commit
`bc5588bc7` while this grading was in progress**, so the registered land command, run to
confirm the refusal was still real, **succeeded and wrote the row.** Neither the row nor the
register was edited to work around anything, and `append_record.py` was not touched.

**DEFECT FOUND IN THE LANDING TOOL, AND IT IS NOT THIS ROW'S.** `append_record.py` writes
`head_text + rows_text` where `rows_text` is **the entire `--rows` file**, not the row lines
parsed out of it. The parked-row pattern put a 44-line explanatory HTML comment inside the
very file its own documented land command names as `--rows`, so that command **injected the
whole comment block into the shared register** — including the sentence "NOT YET LANDED in
docs/COST_CALIBRATION.md", landed. It was removed the same minute by a targeted edit
deleting only the comment block, touching **zero rows**; the register is now HEAD plus
exactly one row line (`git diff HEAD` = 1 insertion, 0 deletions), so append-only rule 1 is
intact. **This is a latent trap for every team that parks a row this way.**
`scripts/append_record.py` is **owned by the verification team**; this lane did not edit it
and proposes no repair here. **NOT FILED — nothing sent (rule 7).**

Headline, all verified against `log.simpleFoam` by this lane:

| | value |
|---|---|
| pre-registered estimate (fine level, §11) | 8,376 core-min |
| **actual, MEASURED** | **4,866.13 core-min** (ClockTime 36,496 s × 8 ranks ÷ 60) |
| **ratio actual/predicted** | **0.581** |
| CPU-held component | 3,957.72 core-min (ExecutionTime 29,682.9 s × 8 ÷ 60) |
| **contention, named separately** | **908.41 core-min, 18.67 % of gross** |
| **waste on the graded run, named separately** | **0.000 core-min** — one uninterrupted march to `endTime` |
| registered cap | 12,000 core-min; run finished at **40.6 %** of it |
| derived dollars | 81.102 core-h × $0.0513 = **$4.16 — DERIVED, NOT MEASURED** |
| grading instrument (this lane) | **0.339 core-min** (20.35 wall s, serial) |
| GPU | 0 GPU-h |

**Gap attributed: MISPREDICTION, in the conservative direction.** The estimate assumed 30,000
cell-iterations per core-second; the run delivered **63,491** CPU-held and **51,638**
wall-inclusive over 1.50768e10 cell-iterations. **Contention is not what produced the
under-spend** — it made the run *more* expensive; without it the ratio would have been 0.472.

---

## 8. PROVENANCE OF THIS GRADING

Registered invocation, run verbatim from §8, exit code **0**:

```
python3 cases/navier_class/DRIVAER/grade_drivaer.py --stage-a \
    --reference verification/runs/navier_class/DRIVAER/drivaer_reference_notchback.json \
    --levels fine=verification/runs/navier_class/DRIVAER/r1_fine \
    --report verification/runs/navier_class/DRIVAER/r1_fine/STAGE_A_REPORT.json
```

`--selftest` run first with `__pycache__` cleared (stale bytecode inverts mutation tests):
**rc 0, `SELFTEST OK`**, ARMING PROOFs 1–5 all green. ARMING PROOF 5 on all four synthetic
meshes: **A** repaired control passes with both arms fired (m=1 delta 8.333333e-01 == expected;
m=3 delta 2.500000e+00 == expected); **A under the superseded formula** refuses at
reader/expected = 3.000000; **B** the superseded control passes silently while the repaired
second arm still refuses the old formula — the mesh dependence measured, not described;
**C** the multiplicity arm reports `UNAVAILABLE` rather than being skipped; **D** refuses
(exit 2) rather than passing when the m=1 arm cannot be armed.

**SUBMISSIONS PARKED (rule 7).** Nothing in this record is sent, filed or registered outside
this box.
