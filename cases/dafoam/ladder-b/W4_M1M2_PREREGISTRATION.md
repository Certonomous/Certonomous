# W4 M1 + M2 — pre-registration: the NASA-hump adjoint operator, measured offline, plus the negative control the programme never ran

**Status: NOT FILED ANYWHERE. NOTHING IN THIS DOCUMENT IS SENT, POSTED, UPLOADED, REGISTERED
OR COMMENTED OUTSIDE THIS BOX.** Filing is Sanaa's decision alone
(`CLAUDE.md` rule 7; `DAFOAM_CHARTER.md` §10).

**Status: PRE-REGISTRATION. NO COMPUTE HAS BEEN RUN FOR THIS ITEM.** This file is committed
**before** any solver, container or harness launches, and its freeze is its entire evidentiary
content (`CLAUDE.md` rule 2; `SUPERVISION_CHARTER.md` §3 check 4). At the moment of the commit
that carries it, **no run directory named in §6 exists**, no `dRdWTPC` dump of the NASA hump
exists anywhere on this box, and no arm below has been launched. Grading verifies this file
**is** the file that ran by hashing it against the committed blob.

| field | value |
|---|---|
| Item | W4 §5b.1 measurements **M1** and **M2**, and nothing else |
| Lane | Lane W (`lab-lane`), DAFoam family |
| Supervisor | `dafoam-supervisor` (Fable), session `01ENBw3KPr5gMaj8Vt7rcxSB` |
| Date registered | 2026-08-23 (UTC) |
| Case | NASA 2D wall-mounted hump, 51,626 cells, 51,626 `betaFIOmega` DVs, `DASimpleFoam` / kOmegaSST |
| Predicted cost | **40.0 core-min**, **$0.0342** |
| Hard ceiling | **60.0 core-min**, **$0.0513** — an overrun **STOPS the run** |
| Verdict vocabulary | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and no other word (`DAFOAM_CHARTER.md` §8) |
| Launch authorisation | **NOT GRANTED BY THIS DOCUMENT.** The supervisor verifies the freeze personally and authorises separately. No agent message is Sanaa's consent (`CLAUDE.md` rule 9). |

---

## 1. What is being bought, and what question it answers

`ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5b.1 (added 2026-08-11) prices six measurements that would
convert the NASA-hump adjoint boundary from an assumption into a measurement. Its own honest
position, `:235`:

> **The honest position: the NASA-hump adjoint boundary is uncharacterised.**

Two of the six are bought here.

**M1** — one assembly-to-dump run of the hump adjoint (dump `dRdWTPC` and the RHS), then the
**existing** offline harness on the dump: exact LU solve, incomplete-LU pivot behaviour, and the
row/column/diagonal condition statistics — **exactly as `PROOF.md` §25.3 (`:2710-2803`) did for
CBFS**. Registered price **25 core-min**; basis, `W4_ADJOINT_PC_UNBLOCK.md:249`:

> **25** (one assembly-to-dump run ≈ the pre-solve segment plus write-out); each offline variant
> thereafter ~10 s at np=4, **<1 each**

**M2** — the negative control that has never been run on this case: attempt **A6**'s exact
configuration with `DAFOAM_SUBPC_TYPE` **unset**, same image, cold case dir; expected to return at
iteration 0. Registered price **15 core-min**; basis, `W4_ADJOINT_PC_UNBLOCK.md:250`:

> **15** (returns at iteration 0) | pre-solve segment 11.7 + teardown

Attempt A6 is row A6 of the eleven-attempt hump audit,
`docs/INSTRUMENT_INTEGRITY_LEDGER.md:412` — `2026-08-04`, `1cd44c04`,
`hump_sublu_computetotals.log`, *"same script + `DAFOAM_SUBPC_TYPE=lu` (rebuilt `libDASolver`,
image `dafoam-subpclu:v1`)"*, `rc=1 wall=819s ranks=4 core_min=54.60`, **never re-run**.
**This is NOT ladder-a's A6 CRM wing-body.** Nothing on A6 CRM is touched by this item (§10).

---

## 2. The frozen predictions

Every row is a prediction made **before** the run, with a numeric band and a basis cited to an
existing record **by path and line**. HIT means the measured value lands inside the band as
stated; MISS means it does not. A MISS is reported as a miss (`DAFOAM_CHARTER.md` §12) and does
not get re-banded.

### 2a. M1 — the assembly-to-dump run and the dump's own integrity

| id | quantity | frozen prediction (band) | HIT/MISS rule | basis (path:line) |
|---|---|---|---|---|
| **M1-P1** | `\|\|b\|\|₂` of the dumped hump RHS | **1.094138002900e+00**, to all **13** printed digits | HIT iff equal to 13 s.f. to the solver's own iteration-0 residual | `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/hump_sublu_computetotals.log:2268`; identity argument `PROOF.md:2717-2720` (`KSPSetNormType(ksp, KSP_NORM_UNPRECONDITIONED)` ⇒ printed residual **is** `\|\|b\|\|`) |
| **M1-P2** | dimension of dumped `dRdWTPC` | **517,240 × 517,240**, exactly | HIT iff exact | `hump_sublu_computetotals.log:271` `Global Adjoint States: 517240` |
| **M1-P3** | `nnz(A)` | **28.4e6 – 38.8e6**, point **33.7e6** | HIT iff inside band | CBFS 13,710,468 nnz at n=210,592 = **65.10 nnz/row** (`PROOF.md:2717`); scaled by n, ±15 % |
| **M1-P4** | `rhs.dat` size on disk | **exactly 4,137,928 bytes** | HIT iff exact | CBFS `rhs.dat` = 1,684,744 B = 210,592×8+8 (`W4-cbfs-reordering/dump.out`); the same formula gives 517,240×8+8, independently confirmed by `hump_sublu/dRdWColoring_4.bin` = 4,137,928 B |
| **M1-P5** | `pmat.dat` size on disk | **343 – 470 MB**, point **406 MB** | HIT iff inside band | CBFS `pmat.dat` 165,368,000 B / 13,710,468 nnz = **12.06 B/nnz** (`W4-cbfs-reordering/dump.out`), applied to M1-P3 |
| **M1-P6** | zero rows / zero cols / zero diagonal entries | **0 / 0 / 0** | HIT iff all three are 0 | CBFS **0 / 0 / 0** (`PROOF.md:2726`) |
| **M1-P7** | diagonal abs spread, `log10(max/min)` | **7.5 – 11.0**, point **9.0** | HIT iff inside band | CBFS **8.67** (`PROOF.md:2727`); M6 **14.17** is the lab's other anchor (same line). **Reported, not decision-bearing** — `PROOF.md:2729-2730` records that this metric *"does not explain CBFS"* |
| **M1-P8** | `spilu` at the four registered `(drop_tol, fill)` settings | **`Factor is exactly singular` at ≥ 3 of 4** | HIT iff ≥ 3 of 4 raise | CBFS **4 of 4** (`W4-cbfs-reordering/analysis_final.log`; `PROOF.md:2774-2777`), and the hump's own `-9 DIVERGED_NANORINF` at iteration 0 under the identical stock ILU stack (`INSTRUMENT_INTEGRITY_LEDGER.md:407`) |
| **M1-P9** | `splu` (complete LU, partial pivoting) | **completes at ≥ 1 of the three registered `diag_pivot_thresh` values**, with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-9` | HIT iff both clauses hold | CBFS 2.3769e-10 / 6.4063e-12 / 2.5355e-12 at thresh 0 / 0.1 / 1 (`PROOF.md:2778-2780`) |
| **M1-P10** | `nnz(L+U)` from `splu`, at the highest completed threshold | **8.0e8 – 1.35e9**, point **1.05e9** | HIT iff inside band | CBFS 389,944,580 at thresh 1 = **28.4×** `nnz(A)` (`PROOF.md:2780`); linear-fill branch 33.7e6×28.4 = 9.6e8, superlinear (`n^{4/3}`) branch ×2.456^{1/3} = 1.29e9 |
| **M1-P11** | `pc_ladder.py` **control** variant on the hump dump (stage O3, may not be reached) | reason **-9**, its **0**, finalres **1.094138002900e+00** to 13 s.f. | HIT iff all three | CBFS control `RESULT reason -9 its 0 finalres 7.091590452305e-04` = `‖b‖` exactly (`W4_ADJOINT_PC_UNBLOCK.md:77`) |
| **M1-P12** | `pc_ladder.py` **sublu** variant on the hump dump (stage O3, may not be reached) | reason **2**, iterations **150 – 1000** | HIT iff both; a `-3` at the 1000 cap is a **MISS and a measurement**, not a void | CBFS sublu reason 2 at **347** iterations (`W4_ADJOINT_PC_UNBLOCK.md:114`). **Flagged as the least-supported prediction in this file** |

### 2b. M2 — the negative control

| id | quantity | frozen prediction (band) | HIT/MISS rule | basis (path:line) |
|---|---|---|---|---|
| **M2-P1** | `OBJ cfVar` | **1.6263651522923017e-01**, all **17** digits | HIT iff bit-equal as printed | `hump_sublu_computetotals.log:1744` |
| **M2-P2** | first `Time step continuity errors : sum local` | **7.98671e-05** as printed | HIT iff equal as printed | `hump_sublu_computetotals.log:710`; the cold-start discriminator is validated at `cases/dafoam/WARMSTART_AUDIT.md` §"Signature revision" |
| **M2-P3** | KSP outcome | `Total iterations: 0` **and** `PetscConvergedReason: -9` | HIT iff both strings present | `INSTRUMENT_INTEGRITY_LEDGER.md:407` (attempt A1, the same script, stock sub-PC) |
| **M2-P4** | iteration-0 KSP residual | **1.094138002900e+00**, 13 s.f. | HIT iff equal to 13 s.f. | `hump_sublu_computetotals.log:2268`; A1's identical value at `INSTRUMENT_INTEGRITY_LEDGER.md:407` |
| **M2-P5** | sub-LU banner | `DAFOAM_SUBPC_TYPE=lu: ASM sub-block PC set to complete LU` occurs **zero** times | HIT iff `grep -c` returns 0 | `DAFOAM_CHARTER.md` §6: *"its absence is the standing proof a run was stock"*; present in A6 at `hump_sublu_computetotals.log:2256` |
| **M2-P6** | process exit code | **rc = 1** (`AnalysisError: Adjoint solution failed!`) | HIT iff rc == 1 | `INSTRUMENT_INTEGRITY_LEDGER.md:407` |
| **M2-P7** | wall time / spend | **150 – 260 s** at np=4 = **10.0 – 17.3 core-min**, point **175 s / 11.7 core-min** | HIT iff inside band | `W4_ADJOINT_PC_UNBLOCK.md:244-245`: iteration 0 printed at **174.97 s**, *"the pre-solve segment … ≈ 175 s wall ≈ 11.7 core-min"* |

### 2c. The known-answer control, run BEFORE the treatment

`CLAUDE.md` rule 3 requires that a reader be shown able to see a non-zero before its zero counts.
The M1 offline stage has no natural planted perturbation, so the equivalent is registered as a
**known-answer control on the same readers**, and it is run first — the pattern
`W4_ADJOINT_PC_UNBLOCK.md:143-145` used (*"Regression control, run before the treatment"*).

| id | quantity | frozen prediction | HIT/MISS rule | basis |
|---|---|---|---|---|
| **O0-P1** | `analyze_dump.py` re-run **unmodified** on the **CBFS** dump, read-only | `n = 210592`, `nnz = 13710468`, `‖b‖₂ = 7.091590452305e-04`, zero rows/cols/diag `0/0/0`, diagonal `log10 = 8.67` | HIT iff every one reproduces as published | `PROOF.md:2717`, `:2726-2727`; `W4-cbfs-reordering/analysis_final.log` |

**Registered consequence of an O0 MISS:** the readers do not reproduce a known answer, so **M1 is
`VOID` and no hump arm is bought.** The item stops, the spend is reported, and the cause is
triaged before anything is re-bought. This is a refusal, not a degradation.

**What O0 does and does not establish, stated so it is not over-read.** It establishes that this
box, this image and these unmodified scripts reproduce the published CBFS numbers today. It does
**not** establish that the readers can see a defect they have never been shown; no perturbation is
planted into the hump matrix, and this file does not claim one is.

---

## 3. The decision rule — what M1's pivot and condition statistics decide

Registered **now**, before any dump exists. The axis is the one `PROOF.md` §25.3 established as
the mechanism — complete-versus-incomplete factorization — **not** the diagonal-spread metric,
which the same section records as non-explanatory for CBFS (`PROOF.md:2729-2730`). All quantities
below are printed by the unmodified frozen scripts named in §5.

| verdict | registered threshold | consequence |
|---|---|---|
| **D-SINGULAR** | `splu` raises at **all three** `diag_pivot_thresh` values (0, 0.1, 1) — **or** `analyze_dump.py` reports zero rows > 0 **or** zero cols > 0 | The assembled hump `dRdWTPC` is **singular**. **M4 and M5 are not bought.** |
| **D-ILLCOND-CATASTROPHIC** | `splu` completes at ≥ 1 threshold **and** the minimum `‖Ax−b‖/‖b‖` over the completed thresholds is **> 1.0e-6** | The assembled operator is **catastrophically ill-conditioned**: a complete factorization with partial pivoting cannot itself reach the tolerance the Krylov solve is asked for (`gmresRelTol: 1.0e-6`, `runScript_hump.py:74`). **M4 and M5 are not bought.** |
| **D-MERELY-SLOW** | `splu` completes with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-6` **and** `spilu` raises `Factor is exactly singular` at **≥ 1** of the four registered settings | The hump is in **CBFS's mechanism class**: the incomplete factorization is singular, the complete one is not. The operator is exonerated; the blocker is not rank or conditioning of the assembled matrix. **M4/M5 become purchasable — by Sanaa, not by this lane.** |
| **D-UNREGISTERED-CLASS** | `splu` completes with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-6` **and** `spilu` succeeds at **all four** settings | The hump is **not** in CBFS's mechanism class, and none of the three verdicts above applies. Recorded as `NOT A RESULT` **for the singular-or-not question**, with the four `spilu` rows printed beside it. No consequence for M4/M5 is registered for this branch, deliberately. |
| **PENDING** | stage O2 not launched, or launched and stopped by the budget ceiling or the memory guard with **zero** completed `splu` factorizations | `PENDING`. Nothing is decided; the price of finishing is reported. |

**The registered consequence, carried verbatim as instructed:**

> **if M1 returns singular or catastrophically ill-conditioned, M4 and M5 are not bought**

**And the source sentence it comes from, carried verbatim from
`W4_ADJOINT_PC_UNBLOCK.md:257-260`:**

> M1 + M2 first: **40 core-min buys the singular-or-not answer offline plus the negative control
> the programme never ran** — and if M1 returns a singular or catastrophically ill-conditioned
> assembled operator, M4 and M5 should not be bought at all.

**Partial-but-decisive is registered too.** Stage O2's script prints incrementally, and the
`spilu` sweep completes in seconds while each `splu` takes minutes. A stop after the four `spilu`
rows and **≥ 1** completed `splu` is sufficient for D-SINGULAR, D-ILLCOND-CATASTROPHIC,
D-MERELY-SLOW and D-UNREGISTERED-CLASS as written above, and is graded, not voided. A stop with
**zero** completed `splu` is `PENDING`.

**The caveat this rule inherits and does not repair**, carried from `PROOF.md:2800-2803` and
restated in `W4_ADJOINT_PC_UNBLOCK.md:222-226`: `dRdWTPC` is the **assembled preconditioner**
approximation, not the matrix-free `dRdWTMF` that GMRES actually applies. Every verdict above is a
statement about the assembled matrix. It is corroborative of, not identical to, the real solve,
and no verdict in this file may be reported as a statement about `dRdWTMF`.

---

## 4. Cost

**Unit: core-minutes = wall s × ranks ÷ 60** (`CLAUDE.md` rule 12). This lane bills **cores × wall
for the whole clock**, because a `docker run` holds its `--cpus` whether the solver saturates it or
not (`DAFOAM_CHARTER.md` §12; `patched_build/subpclu/BUILD.md` §2).

| item | registered price | source |
|---|---|---|
| M1 | **25.0 core-min** | `W4_ADJOINT_PC_UNBLOCK.md:249` |
| M2 | **15.0 core-min** | `W4_ADJOINT_PC_UNBLOCK.md:250` |
| **Predicted total** | **40.0 core-min** | `W4_ADJOINT_PC_UNBLOCK.md:257` |
| **Hard ceiling** | **60.0 core-min** | registered here; **an overrun STOPS the run** |

```
cost_basis: c7a.4xlarge at $0.0513/core-hour, REPORTED-BY-OWNER (owner-stated 2026-08-21/22),
            NOT MEASURED -- the box cannot read its own billing
            (COMPUTE_BUDGET_CHARTER.md section 5; CLAUDE.md rule 12).
predicted:  40.0 core-min / 60 * $0.0513 = $0.03420
ceiling:    60.0 core-min / 60 * $0.0513 = $0.05130
```

Both figures are under the \$25 pre-authorisation, and are costed anyway: a blanket is not a
per-item read (`CLAUDE.md` rule 9).

### 4a. Per-stage caps, and how the ceiling is actually enforced

Every cap below is a `timeout` value in the registered launch command, so the ceiling is wired,
not aspirational.

| stage | what | image | `--cpus` | `--memory` | `timeout` | cap (core-min) | predicted (core-min) |
|---|---|---|---|---|---|---|---|
| **O0** | known-answer control, CBFS, `analyze_dump.py` | `dafoam/opt-packages:latest` | 1 | `8g` | 180 s | 3.0 | 1.0 – 3.0 |
| **M2** | negative control, hump, env unset | `dafoam-subpclu:v1` | 4 | `14g` | 300 s | 20.0 | 10.0 – 17.3 |
| **M1-D** | assembly-to-dump run, hump | `dafoam/opt-packages:latest` | 4 | `14g` | 300 s | 20.0 | 13.3 – 20.0 |
| **O1** | `analyze_dump.py` on the hump dump | `dafoam/opt-packages:latest` | 1 | `8g` | 300 s | 5.0 | 1.0 – 5.0 |
| **O2** | `analyze_dump3.py` on the hump dump — **the decisive stage** | `dafoam/opt-packages:latest` | 1 | `18g` | `min(2700, remaining)` s | ≤ remaining | 25 – 45 |
| **O3** | `pc_ladder.py` control + sublu on the hump dump | `dafoam/opt-packages:latest` | 4 | `18g` | 600 s | 40.0 | not expected to be reached |

**Registered sequencing rule.** Stages run in the order O0 → M2 → M1-D → O1 → O2 → O3. Before each
stage the lane computes `cumulative` from its own ledger and sets that stage's `timeout` to
`min(registered cap, (60.0 − cumulative) × 60 ÷ cpus)` seconds.
- If O2 cannot be given at least **1500 s** (25.0 core-min at `--cpus=1`), **O2 is not launched**
  and M1 is `PENDING` with the reason recorded as the budget ceiling.
- O3 is launched only if at least **10.0 core-min** remain after O2. It is expected **not** to be
  reached, and M1-P11 / M1-P12 are then `PENDING`, not MISS.

### 4b. A frozen prediction about this item's own cost, registered before the spend

`DAFOAM_CHARTER.md` §12 requires the estimate before the runs and the miss reported as a miss.
**This lane predicts, now, that the registered 25.0 core-min for M1 will be MISSED.**

Basis, and it is a real defect in the §5b.1 price rather than in the plan: `W4_ADJOINT_PC_UNBLOCK.md:249`
prices *"each offline variant thereafter ~10 s at np=4, **<1 each**"*, and that 10 s figure is
measured on **`pc_ladder.py`** — a PETSc GMRES/ASM ladder (`W4_ADJOINT_PC_UNBLOCK.md:82-84`). It does
**not** price the `scipy` exact-LU factorization, which is where the singular-or-not answer actually
comes from. The CBFS `scipy` analysis measured **≈ 10.5 wall-minutes at `--cpus=4`** — the
`chain_analysis.sh` window from the force dump's completion (`force_dump.out`, 06:37) to
`ANALYSIS_DONE 2026-08-02T06:47:57Z` (`analysis_final.log`) — i.e. ≈ 42 core-min as this lane
bills, against a line item priced at "<1 each".

| id | frozen prediction | HIT/MISS rule |
|---|---|---|
| **C-P1** | M1's measured spend **exceeds 25.0 core-min** | HIT iff measured M1 > 25.0 |
| **C-P2** | the item's total measured spend lands in **45.0 – 60.0 core-min** and **stops at the ceiling** with O3 unreached | HIT iff both |

Registering this does not move the price, the cap or the ceiling — the registered price stays
**25.0 / 15.0 / 40.0** and the ceiling stays **60.0**. It records the expected miss before the
spend so that landing at 55 core-min is a predicted overrun stopped at a registered ceiling, and
not a budget quietly discovered to be larger.

---

## 5. Frozen instruments — md5s that must be identical to the cited prior runs

Every measurement below is made by a script that **already exists and is not edited**. The
scripts are bind-mounted **read-only** into the container so a run cannot modify them.

| path | md5 | line count | role | prior run it must match |
|---|---|---|---|---|
| `/home/ubuntu/certonomous-runs/W4-cbfs-reordering/analyze_dump.py` | `d35cb147e0d0e213ff0372aeb2883d1c` | 59 | O0, O1 — row/col/diagonal statistics, RHS norm | `PROOF.md` §25.3 CBFS table |
| `/home/ubuntu/certonomous-runs/W4-cbfs-reordering/analyze_dump3.py` | `f85140f675bcc287f6e4aaf01276c0e4` | 33 | **O2 — the decisive `spilu`×4 / `splu`×3 sweep** | `W4-cbfs-reordering/analysis_final.log`; `PROOF.md:2772-2780` |
| `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/pc_ladder.py` | `b1388434dd5daf87f1f031874faa13e8` | 138 | O3 — the PETSc PC ladder | `W4_ADJOINT_PC_UNBLOCK.md` §1, §3 |
| `/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/runScript_hump.py` | `d146c56a846df5cf147dcce45876eaa7` | 138 | M1-D, M2 — the case script | A6 (`hump_sublu_computetotals.log`); **byte-identical to `S1-fiml/runScript_hump.py`**, same md5 |
| `/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/w4_m1m2_memguard.sh` | `f102eb52c11f8f377b0654a84c97168c` | 118 | §7 — the memory guard, **new for this item** | none; self-tested, §7 |

Cited as **patterns, not executed**: `W4-cbfs-reordering/run_dump.sh`
(`15b4ea432b24eef63fb58a5c9d2aae6b`) supplies the `-ksp_view_pmat` / `-ksp_view_rhs` dump route;
`W4-adjoint-pc-unblock/run_hump_sublu.sh` (`be1e94c9d4fae26d91daa90b52383d9d`) supplies A6's
container invocation. Neither is CBFS-and-hump interchangeable, so the launch commands in §6 are
written out in full and are what is run.

### 5a. Case-state identity, asserted before launch

The staged case must be A6's own start state. Registered pre-launch assertions:

| file, in the staged copy | md5 that must match |
|---|---|
| `0/U` | `0b80aa8c9b4509706a825bc8735f9188` |
| `caseDef` | `ce7c589256b00b44475b69ee29906390` |
| `fieldDef` | `5df70649ab72e9a7e731a0d012df28fc` |
| `dRdWColoring_4.bin` | `c823a5701ac0704645153c96cc6ec5c2` |
| `constant/polyMesh/owner` | `c7f7d0ed25174a9efe3f97b7bc500260` |

All five are simultaneously true of A6's own case directory
(`/home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock/hump_sublu/`) and of its staging source
(`/home/ubuntu/certonomous-runs/S1-fiml/hump/`), measured 2026-08-23. **Cold** here means: a
freshly staged copy carrying exactly these files with **no** `processor*` directories, **no**
`dynamicCode/`, **no** logs and **no** time directory other than `0` — the staged-copy pattern
`WARMSTART_AUDIT.md` recommends and `FAMILY_SUPERVISION_GUIDELINES.md` §8 requires. It is **not** a
claim that A6's `0/U` is itself uniform-cold; that state is S1's and is inherited deliberately, so
that M2 controls A6 rather than something else.

### 5b. Toolchain identity — tag **and** image ID, per `DAFOAM_CHARTER.md` §6

| tag | image ID | `DALinearEqn.C` md5 / lines | used by |
|---|---|---|---|
| `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | `f6a89e33b0f4772a0563cb0c8633ac48` / 507 | O0, M1-D, O1, O2, O3 |
| `dafoam-subpclu:v1` | `sha256:ba2d16ab9d575ed3167abe31344aa58fb42fef1a8b27db60baeb505ab9413517` | `89e71ca2db5d80c06b1eda070ffc7a1b` / 526 | **M2 only** |

md5s and line counts from `docs/dafoam/TOOLCHAIN_INVENTORY.md:128-129`; image IDs read on this box
2026-08-23. **M2 uses `v1`, not `v2`,** because M2's whole content is that it is A6's exact
configuration and A6 ran on `v1` (`INSTRUMENT_INTEGRITY_LEDGER.md:412`). `DAFOAM_CHARTER.md` §6
records that `v2` differs from `v1` by 13 lines all inside an `else if` branch entered only for a
`DAFOAM_SUBPC_TYPE` value that is neither unset nor `lu`, so on M2's path the two are numerically
identical — that is a reason `v2` **would** have been acceptable, not a reason to substitute it.

**Both rows, always** (`DAFOAM_CHARTER.md` §6): M2 is a **patched-image** row run with the patch
inert. It is reported as such and never as a shipped-toolchain row, and M2-P5 (banner count zero)
is the evidence that the patch was inert.

---

## 6. The exact launch commands, registered

`BASE=/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning` — **this directory does not exist
except for the guard script and its self-test log at the moment of the freeze**, which is the
"name the run directory that does not exist" condition of `CLAUDE.md` rule 2.

**Nothing below is launched by this document.** Launch authorisation comes from the supervisor as
a separate message after the freeze is verified.

### Stage 0 — staging and the launch gate (no compute)

```bash
BASE=/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning
SRC=/home/ubuntu/certonomous-runs/S1-fiml/hump

mkdir -p "$BASE/hump_dump" "$BASE/logs"
chmod 777 "$BASE/hump_dump"
for arm in m1_dump m2_envoff; do
  rm -rf "$BASE/$arm"; mkdir -p "$BASE/$arm"
  cp -a "$SRC"/0 "$SRC"/constant "$SRC"/system \
        "$SRC"/caseDef "$SRC"/fieldDef \
        "$SRC"/dRdWColoring_4.bin "$SRC"/dRdWColoring_4.bin.info "$BASE/$arm"/
  chmod -R a+rwX "$BASE/$arm"
done

# section 5a assertions -- ANY mismatch stops the item before compute
md5sum "$BASE"/*/0/U "$BASE"/*/caseDef "$BASE"/*/fieldDef \
       "$BASE"/*/dRdWColoring_4.bin "$BASE"/*/constant/polyMesh/owner

# LAUNCH GATE
free_cores=$(( 16 - $(for i in 1 2 3 4 5; do awk '{split($4,a,"/"); print a[1]}' /proc/loadavg; sleep 1; done | sort -n | sed -n '3p') ))
memavail_gib=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)
echo "GATE free_cores=$free_cores memavail_gib=$memavail_gib"
```

**Launch gate, registered and not negotiable by this lane:**

> **`free_cores >= 4` AND `MemAvailable >= 12 GiB`**, where
> `free_cores = 16 − median-of-5 runnable count` and the runnable count is the numerator of
> `/proc/loadavg` field 4, sampled at 1 s intervals.

**The 12 GiB floor is a registered threshold on Sanaa's desk. It is not lowered, re-read or argued
here.** Two stages carry an **additional, higher** requirement, registered below, which raises the
bar and never lowers it: **M2 and M1-D also require `MemAvailable ≥ 21.0 GiB`; O2 and O3 also
require `MemAvailable ≥ 25.0 GiB`** at their own launch instant. A stage whose extra requirement is
unmet is recorded `BLOCKED` and is not run.

### Stage O0 — known-answer control (CBFS, read-only)

```bash
timeout 180 sudo -n docker run --rm --name w4m1m2_o0 --cpus=1 --memory=8g \
  -v /home/ubuntu/certonomous-runs/W4-cbfs-reordering:/mnt:ro -w /tmp \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && python -u /mnt/analyze_dump.py" \
  > "$BASE/logs/o0_cbfs_knownanswer.log" 2>&1
```

### Stage M2 — the negative control (the only stage on `dafoam-subpclu:v1`)

```bash
"$BASE/w4_m1m2_memguard.sh" w4m1m2_m2 6291456 3145728 "$BASE/logs/m2_mem.log" &
GUARD=$!
timeout 300 sudo -n docker run --rm --name w4m1m2_m2 --cpus=4 --memory=14g -u 1002:1002 \
  -v "$BASE":/mnt -w /mnt \
  dafoam-subpclu:v1 bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd m2_envoff && decomposePar -force > log.decomposePar 2>&1 && cd .. && mpirun -np 4 python -u /mnt/runScript_hump.py -task compute_totals -case m2_envoff -out m2_envoff_out.json" \
  > "$BASE/logs/m2_envoff_computetotals.log" 2>&1
rc=$?; kill $GUARD 2>/dev/null
```

`DAFOAM_SUBPC_TYPE` is **not** passed. `runScript_hump.py` is copied into `$BASE` unchanged
(md5 `d146c56a846df5cf147dcce45876eaa7`, §5) before this stage.

### Stage M1-D — the assembly-to-dump run

```bash
"$BASE/w4_m1m2_memguard.sh" w4m1m2_m1d 6291456 3145728 "$BASE/logs/m1d_mem.log" &
GUARD=$!
timeout 300 sudo -n docker run --rm --name w4m1m2_m1d --cpus=4 --memory=14g -u 1002:1002 \
  -v "$BASE":/mnt -w /mnt \
  -e PETSC_OPTIONS="-ksp_view_pmat binary:/mnt/hump_dump/pmat.dat -ksp_view_rhs binary:/mnt/hump_dump/rhs.dat" \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && cd m1_dump && decomposePar -force > log.decomposePar 2>&1 && cd .. && mpirun -np 4 -x PETSC_OPTIONS python -u /mnt/runScript_hump.py -task compute_totals -case m1_dump -out m1_dump_out.json" \
  > "$BASE/logs/m1d_dump_computetotals.log" 2>&1
rc=$?; kill $GUARD 2>/dev/null
```

`rc = 1` is **expected** here and is not a failure of the stage: the CBFS dump run returned
`rc=1` from its own `-9` and wrote both files (`W4-cbfs-reordering/dump.out`). The stage's
success condition is that `hump_dump/pmat.dat` and `hump_dump/rhs.dat` both exist and satisfy
M1-P1 / M1-P2 / M1-P4 / M1-P5.

### Stages O1, O2 — the offline readers, on the hump dump

The frozen readers hardcode `/mnt/cbfs_dump/{pmat,rhs}.dat`. **They are not edited.** The hump
dump is bind-mounted **at that container path**, and the scripts are mounted separately,
read-only, so their md5s cannot change:

```bash
# O1
timeout 300 sudo -n docker run --rm --name w4m1m2_o1 --cpus=1 --memory=8g \
  -v /home/ubuntu/certonomous-runs/W4-cbfs-reordering:/scripts:ro \
  -v "$BASE/hump_dump":/mnt/cbfs_dump:ro -w /tmp \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && python -u /scripts/analyze_dump.py" \
  > "$BASE/logs/o1_hump_stats.log" 2>&1

# O2 -- THE DECISIVE STAGE. TMO is set per the section 4a sequencing rule.
"$BASE/w4_m1m2_memguard.sh" w4m1m2_o2 6291456 3145728 "$BASE/logs/o2_mem.log" &
GUARD=$!
timeout $TMO sudo -n docker run --rm --name w4m1m2_o2 --cpus=1 --memory=18g \
  -v /home/ubuntu/certonomous-runs/W4-cbfs-reordering:/scripts:ro \
  -v "$BASE/hump_dump":/mnt/cbfs_dump:ro -w /tmp \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && python -u /scripts/analyze_dump3.py" \
  > "$BASE/logs/o2_hump_lu.log" 2>&1
rc=$?; kill $GUARD 2>/dev/null
```

**One registered, disclosed deviation from the cited CBFS invocation:** `python -u`. The CBFS run
used plain `python` (`chain_analysis.sh`). `-u` is required because O2 may be stopped by `timeout`
or by the memory guard, and block-buffered stdout would lose the `spilu` and `splu` rows already
computed — the rows the §3 decision rule reads. It is an interpreter flag on the launch command,
not a change to the script; the script's md5 is unchanged and `-u` cannot affect numerics.

### Stage O3 — `pc_ladder.py`, only if ≥ 10.0 core-min remain

```bash
"$BASE/w4_m1m2_memguard.sh" w4m1m2_o3 6291456 3145728 "$BASE/logs/o3_mem.log" &
GUARD=$!
timeout 600 sudo -n docker run --rm --name w4m1m2_o3 --cpus=4 --memory=18g \
  -v /home/ubuntu/certonomous-runs/W4-adjoint-pc-unblock:/scripts:ro \
  -v "$BASE/hump_dump":/dump:ro -w /tmp \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && mpirun --allow-run-as-root -np 4 python -u /scripts/pc_ladder.py control rcm 1 && mpirun --allow-run-as-root -np 4 python -u /scripts/pc_ladder.py sublu rcm 1" \
  > "$BASE/logs/o3_pc_ladder.log" 2>&1
rc=$?; kill $GUARD 2>/dev/null
```

---

## 7. Memory envelope (`DAFOAM_CHARTER.md` §7) — predicted, stated, and wired to a guard that kills

> A preregistration that launches an adjoint states its predicted peak memory and the host
> headroom it needs, **before the run**. — `DAFOAM_CHARTER.md:258-262`

### 7a. Predicted peak, per stage

Peak is measured two ways, both registered now: **(i)** `baseline MemAvailable − minimum
MemAvailable` over the stage, the same instrument as A6's own `hump_sublu_mem.log`; **(ii)**
best-effort `docker stats` samples taken by the guard every 30 s. (i) is the graded statistic;
(ii) is the cross-check, and where the two disagree by more than 20 % both are printed and neither
is preferred.

| stage | predicted peak footprint | host headroom required at launch | basis |
|---|---|---|---|
| **M1-D** assembly-to-dump | **6.0 – 16.0 GiB**, point **10.0 GiB** | `MemAvailable ≥ 21.0 GiB` | A6's own memlog, same case, same np, same script: 30.45 GB at start (`hump_sublu_mem.log:1`) → 9.81 GB at 15:47:50, the last sample before the GMRES basis allocation, i.e. **≤ 20.6 GiB for the whole pre-solve segment including the complete-LU sub-block factors M1-D does not build.** CBFS measures those factors at **100,311,134 nnz/block against ILU(1)'s 6,963,844** — 14.4× (`W4_ADJOINT_PC_UNBLOCK.md:113-114`) — so removing them is the dominant subtraction |
| **M2** negative control | **6.0 – 16.0 GiB**, point **10.0 GiB** | `MemAvailable ≥ 21.0 GiB` | as M1-D, minus the ~0.4 GB dump write-out |
| **O0**, **O1** statistics readers | **1.0 – 4.0 GiB** | standing gate only | CBFS ran the same reader class under a `--memory=10g` cap (`run_dump.sh:7`, `chain_analysis.sh`); no factorization is performed |
| **O2 exact LU** | **8.0 – 22.0 GiB**, point **14.0 GiB** | `MemAvailable ≥ 25.0 GiB` | **CBFS's exact LU completed inside a `--memory=10g` container cap** (`chain_analysis.sh`) at `nnz(L+U)` 3.22e8 – 3.90e8, described as *"roughly 3 GB"* of factors (`PROOF.md:2782-2784`). The hump's predicted `nnz(L+U)` is **8.0e8 – 1.35e9** (M1-P10), i.e. **2.1 – 3.5×** CBFS's, giving 6.3 – 16.5 GiB of factors at CBFS's own 7.7 B/nnz and up to ~19 GiB at a 12 B/nnz double-plus-int32 accounting, plus ~0.8 GiB for the CSR and CSC copies of a 33.7e6-nnz matrix |
| **O3 `pc_ladder.py` sublu** | **10.0 – 26.0 GiB**, point **17.0 GiB** | `MemAvailable ≥ 25.0 GiB` | CBFS per-ASM-block complete LU **100,311,134 nnz ≈ 0.8 GB** × 4 blocks (`W4_ADJOINT_PC_UNBLOCK.md:114`); hump blocks are 2.456× larger in dimension, ×2.456^{4/3} = 3.3 on fill ⇒ ~3.3e8 nnz/block, ~2.7 GB/block, ~11 GB across four, plus ASM overlap-1 and the GMRES basis |

**The hump exact-LU can approach `MemAvailable`, and this file says so rather than hoping.** O2's
upper band (22.0 GiB) and O3's (26.0 GiB) both sit close to this box's `MemTotal` of
**30.65 GiB**. A measured abort is therefore registered, and it is wired.

**Registered classification of an abort** (`DAFOAM_CHARTER.md` §7): a stage stopped by the guard or
by its `--memory` cap is recorded **stopped by memory**, is `NOT A RESULT` about the operator, and
claims nothing about the envelope beyond the floor that was breached. **The §3 decision rule
deliberately does not depend on O3**, the stage most likely to abort; it rests on O2, and O2's own
partial-but-decisive rule (§3) is what keeps a memory abort from voiding the item.

**And the opposite error is named too, because this lane has made it.** `COMPUTE_BUDGET_CHARTER.md`
L-15 and `DAFOAM_CHARTER.md:286-294`: an adjoint that breaks *with headroom unused* is bound by
convergence, not by RAM. If a stage aborts on memory, this file registers **no** inference that the
hump is memory-bound; that would be the L-15 error again.

### 7b. The guard — it exists, it is executable, and its trigger path has been fired

> **L-239: a registered stop with nothing wired to trigger it is not a guard.**
> A3 rung 2 registered a `MemAvailable < 8 GiB` stop, armed a **record-only** watcher, and held the
> host below that floor for **52.6 %** of the graded arm with **no stop firing**
> (`DAFOAM_CHARTER.md:525-537`, the §13 PROPOSAL — **unratified, and not enforced here**; the
> incident itself is a measured fact and is).
>
> The instrument this replaces is `run_hump_sublu.sh:12` — a five-second `MemAvailable` logger with
> nothing attached. A6 was ended by a **human** issuing `docker stop` at 1.62 GB
> (`W4_ADJOINT_PC_UNBLOCK.md:216-221`).

```
path       /home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning/w4_m1m2_memguard.sh
md5        f102eb52c11f8f377b0654a84c97168c
lines      118
perms      -rwxr-xr-x 1 ubuntu ubuntu 4654 Aug 23 19:26 w4_m1m2_memguard.sh
cadence    5.0 s
```

**Registered floors** (raising, never lowering, the 12 GiB launch gate, which is a different
instrument and is untouched):

| floor | rule | max exposure | consequence |
|---|---|---|---|
| **soft, 6.0 GiB** (`6291456` kB) | **two consecutive** samples strictly below | 10 s | `docker kill` the named container, guard exits **9**, stage recorded **MEMORY-ABORT** |
| **hard, 3.0 GiB** (`3145728` kB) | **one** sample strictly below | 5 s | immediate `docker kill`, guard exits **9** |

6.0 GiB is **3.7×** the 1.62 GB low-water at which a human judged A6's shared box to be in distress
(`hump_sublu_mem.log:164`; `W4_ADJOINT_PC_UNBLOCK.md:195-197`), and it leaves a co-tenant room. The
kill decision is executed **before** any blocking call in the guard's loop, so a slow `docker stats`
can never delay it.

**Self-test, run 2026-08-23 before this file was committed, with no container involved** — a soft
floor of `MemTotal` (unsatisfiable by construction) and the kill command redirected at a sentinel:

```
$ ./w4_m1m2_memguard.sh --selftest ./memguard_selftest.log
memguard selftest: exit=9 sentinel=PRESENT
2026-08-23T19:26:15Z ABORT reason=SOFT_FLOOR_TWO_CONSECUTIVE memavail_kib=29144132 floor_soft_kib=32132604 floor_hard_kib=1 killcmd='touch ./memguard_selftest.log.selftest-fired'
memguard selftest: PASS (trigger path fired, kill command executed)
```

Two samples 5 s apart, the trigger fired, the kill command **executed**, exit code 9. What the
self-test establishes: the sampling loop, the two-consecutive-sample rule, the abort record and the
execution of the kill command all work. What it does **not** establish: that `sudo -n docker kill`
succeeds against a live container, which is not tested because testing it would mean launching one,
and this item launches nothing before authorisation. That limitation is recorded here rather than
discovered later.

---

## 8. Completion and void conditions

**A run is done only if all of it holds** (`CLAUDE.md` rule 4, in the form that applies to an
adjoint arm rather than a thermal primal).

**M2 is COMPLETE iff:** the staged case satisfies every §5a md5; the log contains the M2-P2 cold
discriminator; `Total iterations: 0` and `PetscConvergedReason: -9` both appear; the sub-LU banner
appears **zero** times; `rc = 1`; the guard log records no abort; and the ledger row is written.

**M1 is COMPLETE iff:** O0 reproduces every O0-P1 value; `hump_dump/{pmat,rhs}.dat` both exist and
satisfy M1-P1, M1-P2, M1-P4, M1-P5; O1 completes; and O2 yields the four `spilu` rows plus at least
one completed `splu`. Anything less is `PENDING` with the missing piece named and priced.

### 8a. Void conditions — md5s that must be identical to the cited prior runs

| if this md5 differs from §5 / §5a at launch | what becomes void | what is re-bought |
|---|---|---|
| `analyze_dump.py` `d35cb147…` | **O0 and O1 both.** The known-answer control cannot certify a reader that is not the cited one | nothing is bought until the difference is read as a diff by the supervisor (`CLAUDE.md` §TEAM ROSTER: measurement-script diffs are read personally and never delegated) |
| `analyze_dump3.py` `f85140f6…` | **O2, and with it the entire §3 decision rule.** M1 is `VOID`, not `PENDING` | the whole M1 offline stage, after triage; M2 is unaffected and its spend stands |
| `pc_ladder.py` `b1388434…` | **O3 only** (M1-P11, M1-P12) | O3 alone, ~10 core-min, if the ceiling allows |
| `runScript_hump.py` `d146c56a…` | **M1-D and M2 both** — the arms would no longer be A6's configuration | both, at their registered prices, after the diff is read |
| any §5a case-state md5 | **M2 in full** — it would be a control of some other start state — and M1-D's claim to be A6's configuration | staging is redone from `S1-fiml/hump`; if that source has itself moved, the item stops and reports rather than re-deriving a source |
| `w4_m1m2_memguard.sh` `f102eb52…` | **every stage that cites it**, because the §7 self-test evidence is evidence about **this** file | re-test and re-freeze the guard before any launch |
| either image ID in §5b | **the stage that used it.** A patched row must name the image that produced it (`DAFOAM_CHARTER.md` §6) | that stage, at its registered price |

**A void is a refusal, not a downgrade.** No arm is graded on a substituted instrument, and no band
in §2 is widened after a MISS.

### 8b. Amendment discipline

Before first compute, amendments to this file are legal and must state the condition and how it was
checked, naming the run directory that does not exist (`CLAUDE.md` rule 2). **After the first
container starts, the gates, thresholds, caps and labels here are closed**; changes land only as
dated addenda that cannot alter them, and originals are struck, never rewritten
(`CLAUDE.md` rule 2; frozen files are never edited, rule 6).

---

## 9. What this item may and may not conclude

- It may conclude that the **assembled** `dRdWTPC` of the NASA hump is singular, catastrophically
  ill-conditioned, or in CBFS's mechanism class, per §3.
- It may conclude that the `-9` → sub-LU attribution **does or does not reproduce on the hump**,
  which is M2's entire purpose: `INSTRUMENT_INTEGRITY_LEDGER.md:399-402` records that
  *"Not one hump failure was ever deliberately re-run as a negative control"* and that the only
  env-off control in the programme is on CBFS.
- **If M2 does not return `-9` at iteration 0**, the attribution is not reproduced on the hump, and
  `W4_ADJOINT_PC_UNBLOCK.md` headline 3's `-9`-removal claim rests on an unreproduced baseline. That
  is registered now as a possible outcome, before the run, so it cannot be absorbed afterwards.
- It may **not** conclude anything about `dRdWTMF`, the matrix-free operator GMRES actually applies
  (§3, closing paragraph).
- It may **not** conclude anything about the hump's convergence **rate**, which requires a
  terminating `KSPConvergedReason` and therefore M4 (`W4_ADJOINT_PC_UNBLOCK.md:252`).
- It may **not** conclude that the hump is memory-bound (§7a, L-15).
- No verdict here is `PASS` on an FD gate: **no gradient is produced by this item**, so
  `DAFOAM_CHARTER.md` §2's FD-table requirement is not engaged and no gradient number will be quoted.

---

## 10. What is explicitly NOT run — held for Sanaa

**Nothing below is launched, staged, queued, meshed or costed by this item.** Each is listed with
its price and its discriminating outcome, which is what `DAFOAM_CHARTER.md` §12 calls a deliverable
rather than a refusal.

| held item | price | where it is priced | why it is not run here |
|---|---|---|---|
| **M3** deliberate reproduction of A6 to iteration 900 | 55 core-min | `W4_ADJOINT_PC_UNBLOCK.md:251` | out of scope; §5b.1's own sequencing puts it after M1 |
| **M4** run to a reason code | 100 core-min, **needs ≥ 64 GB** | `:252-253` | **gated on M1** by the consequence carried verbatim in §3; and this box has 30.65 GiB |
| **M5** memory-binding test (`runScript_hump_rich.py`, A10) | 150 core-min, unmeasured multiplier up to ~3× | `:254` | **gated on M1** by the same consequence |
| **M6** cross-residual instrument on a `psi` checkpoint | 20 core-min on top of M3/M4 | `:255` | depends on M3/M4 |
| **M7** produce a hump beta gradient at all, FD-verified (A11's `run_hump_fd.sh`) | 20 core-min | `:269` | conditional on M4 returning reason 2 |
| **M8** second-decomposition re-run | 100 core-min | `:270` | conditional on M4 |
| the **~5 core-min GAMG → PBiCGStab ADF sweep** | ~5 core-min, \$0.004 | `ladder-a/A6/rung_n16_remaining_components/RESULTS.md:547`; `DEFECT_CANDIDATE_adf_primal_nonreproduction.md:156` | different item, different lane's territory; it decides the ADF defect **class**, not the hump operator. **Held for Sanaa** |
| the **`useMeanStates: True` + `fieldAverage` arm** | ~5 core-min, \$0.004 | `ladder-a/A6/rung_n16_remaining_components/RESULTS.md:545` | *"the unbought `useMeanStates` item on Sanaa's desk"* (`:409`). **Held for Sanaa** |
| **anything on A6 CRM N=29** | — | `ladder-a/A6/rung_n16_remaining_components/RESULTS.md:439-464` | *"`N=29` IS `NOT RUN`, UNDER EITHER READING."* The gate has two registered readings and **choosing is Sanaa's**. This item touches it in no way |

**Nothing is filed upstream.** The four prepared DAFoam defect classes (`DAFOAM_CHARTER.md` §10)
stay `NOT FILED`, and whatever §3 decides adds nothing to and subtracts nothing from that state.
**NOT FILED. Parked is not cancelled; readiness never slides into sending.**

---

## 11. Readings taken at the freeze

Recorded so the launch gate can be re-evaluated against a moving box rather than against this
paragraph.

```
2026-08-23  (UTC)
  nproc                 16
  MemTotal              32,132,604 kB  = 30.65 GiB
  MemAvailable          29,072,920 kB  = 27.73 GiB      -> gate >= 12 GiB   PASS
  median-of-5 runnable  5
  free_cores            16 - 5 = 11                     -> gate >= 4        PASS
  images present        dafoam/opt-packages:latest 9d45679d55fd
                        dafoam-subpclu:v1          ba2d16ab9d57
```

**The gate is re-run immediately before each stage, not inherited from this reading.** These are a
dated observation and nothing more.

---

## 12. Related

| document | what it owns that this file does not |
|---|---|
| `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5b.1 | The M-ladder, its prices and its bases; the 2026-08-11 corrections that make the hump boundary uncharacterised |
| `cases/dafoam/PROOF.md` §25.3 | The CBFS singular-ILU diagnosis this item replicates on the hump, and the `dRdWTPC`-is-not-`dRdWTMF` caution |
| `docs/INSTRUMENT_INTEGRITY_LEDGER.md` §5 | The eleven-attempt hump table; A6's row; *"not one hump failure was ever deliberately re-run as a negative control"* |
| `docs/charters/DAFOAM_CHARTER.md` | §7 memory envelope; §8 verdict vocabulary; §12 cost; §6 two rows and image identity |
| `cases/dafoam/WARMSTART_AUDIT.md` | The cold-start discriminator and the staged-copy pattern |
| `docs/dafoam/TOOLCHAIN_INVENTORY.md` | The image md5s and line counts cited in §5b |
