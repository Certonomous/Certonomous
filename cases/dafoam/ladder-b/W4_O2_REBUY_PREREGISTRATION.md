# W4 stage O2 re-buy — pre-registration: the offline exact-LU factorization of the already-paid-for NASA-hump adjoint operator

**Status: NOT FILED ANYWHERE. NOTHING IN THIS DOCUMENT IS SENT, POSTED, UPLOADED, REGISTERED,
EMAILED OR COMMENTED OUTSIDE THIS BOX.** Filing is Sanaa's decision alone (`CLAUDE.md` rule 7;
`DAFOAM_CHARTER.md` §10). **NOT FILED. Parked is not cancelled; readiness never slides into sending.**

**Status: PRE-REGISTRATION. NO COMPUTE HAS BEEN RUN FOR THIS ITEM.** This file is committed
**before** any container launches, and its freeze is its entire evidentiary content (`CLAUDE.md`
rule 2; `SUPERVISION_CHARTER.md` §3 check 4). At the moment of the commit that carries it, **the log
file named in §6 does not exist**, no `analyze_dump3.py` output on the hump dump exists anywhere on
this box, and nothing below has been launched or staged for launch. Grading verifies this file **is**
the file that ran by hashing it against the committed blob.

| field | value |
|---|---|
| Item | **stage O2 only** — `analyze_dump3.py` on the existing hump dump, and nothing else |
| Lane | Lane X (`lab-lane`), DAFoam family |
| Supervisor | `dafoam-supervisor` (Fable), session `01ENBw3KPr5gMaj8Vt7rcxSB` |
| Date registered | 2026-08-23 (UTC) |
| Case | NASA 2D wall-mounted hump, 51,626 cells, 517,240 adjoint states — **the dump already on disk**, not a new solve |
| Predicted cost | **35.0 core-min**, **$0.02993** |
| Hard ceiling | **50.0 core-min**, **$0.04275** — an overrun **STOPS the run**; it does not get a new budget |
| Wired stop | `timeout 2700` at `--cpus=1` = **45.0 core-min**, inside the ceiling (§4) |
| Memory stop | **kernel-enforced cgroup cap** `--memory=20g --memory-swap=20g`, plus `--oom-score-adj=500` (§7) |
| Verdict vocabulary | `PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` / `PENDING` and no other word (`DAFOAM_CHARTER.md` §8) |
| Launch authorisation | **NOT GRANTED BY THIS DOCUMENT.** The supervisor verifies the freeze personally and authorises separately. No agent message is Sanaa's consent (`CLAUDE.md` rule 9). |

---

## 1. What is being bought, and why it is a new item rather than a continuation

`cases/dafoam/ladder-b/W4_M1M2_RESULTS.md` (committed `64479072`) records that W4 M1+M2 ran, bought
the expensive half of M1, and **did not buy the answer**:

> `W4_M1M2_RESULTS.md:22` — **M1** overall — the §3 decision | **PENDING** | stage **O2 was not
> launched**: the budget rule left 19.88 core-min against a registered 25.0 launch floor

and:

> `W4_M1M2_RESULTS.md:319` — **O2 no longer needs a solver.** `hump_dump/{pmat,rhs}.dat` are on disk,
> verified against the solver's own residual, and are inputs to an offline factorization.

The dump is **paid for and verified**. Both files are on disk at the byte sizes the frozen
predictions M1-P4 and M1-P5 named, and `‖b‖₂ = 1.094138002900e+00` equals the solver's own printed
iteration-0 residual to 13 digits (`W4_M1M2_RESULTS.md:21`, `:118`, `:119`, `:344`). Nothing in this
item re-derives that; §8 asserts the two byte sizes and stops if either has moved.

**This is a NEW mini-item, not a continuation.** `CLAUDE.md` rule 12: an overrun stops the run and
does not get a new budget. The 60.0 core-min ceiling of `c8254a4a` stopped that item; this file
carries its **own** price and its **own** ceiling, and `W4_M1M2_RESULTS.md:327-329` says so
explicitly (*"a re-buy is a new decision with its own price, not a continuation of this one"*).

**What is in scope:** one container, one unmodified script, one log.
**What is NOT in scope:** DAFoam, MPI, any case directory, any solver, any mesh, any gradient, and
**stage O3** (§10).

---

## 2. The instrument — frozen, unmodified, asserted and printed before the run

| path | md5 that must hold | line count | role |
|---|---|---|---|
| `/home/ubuntu/certonomous-runs/W4-cbfs-reordering/analyze_dump3.py` | `f85140f675bcc287f6e4aaf01276c0e4` | 33 | **the whole of O2** — `spilu` × 4 `(drop_tol, fill)` settings, `splu` × 3 `diag_pivot_thresh` values |

This md5 is the one frozen at `c8254a4a` §5 (`W4_M1M2_PREREGISTRATION.md:238`) and it is
**re-measured on disk 2026-08-23 for this file: `f85140f675bcc287f6e4aaf01276c0e4`, 33 lines —
equal.** The script is **not edited**, and it is bind-mounted **read-only** into the container so a
run cannot modify it. The launch command in §6 **prints the md5 before the container starts** and
**asserts equality**, so the freeze is checked by the run and not merely by this paragraph.

The script hardcodes `/mnt/cbfs_dump/{pmat,rhs}.dat`. **It is not edited to point elsewhere**; the
hump dump is bind-mounted at that container path, exactly as `c8254a4a` §6 registered
(`W4_M1M2_PREREGISTRATION.md:384-387`).

**The one registered, disclosed deviation from the CBFS invocation, carried forward from
`c8254a4a` §6 (`W4_M1M2_PREREGISTRATION.md:409-413`):** `python -u`. CBFS used plain `python`
(`chain_analysis.sh:6`). `-u` is required because this run may be stopped by `timeout` or by the
cgroup, and block-buffered stdout would lose the `spilu` and `splu` rows already computed — the rows
the §3 decision rule reads. It is an interpreter flag on the launch command, not a change to the
script; the md5 is unchanged and `-u` cannot affect numerics.

### 2a. Toolchain identity — tag **and** image ID (`DAFOAM_CHARTER.md` §6)

| tag | image ID | used by |
|---|---|---|
| `dafoam/opt-packages:latest` | `sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc` | this item's single stage |

Read on this box 2026-08-23 for this file and **equal** to the ID frozen at `c8254a4a` §5b
(`W4_M1M2_PREREGISTRATION.md:274`). This is the **shipped** image, not a patched one: no
`dafoam-subpclu` image is used by this item, and no `DAFOAM_SUBPC_TYPE` is set or read anywhere in
it. §6 asserts the ID before the container starts.

---

## 3. The decision rule — inherited VERBATIM from `c8254a4a` §3, and not re-opened

This item feeds the rule below and **decides nothing else**. The rule is not re-derived, re-worded,
re-thresholded or extended here. It is quoted in full from
`cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md` §3 (`:118-154`), committed `c8254a4a` before any
compute, blob `e7b5f0d427401663def453e968356bb8937602ce`:

> ## 3. The decision rule — what M1's pivot and condition statistics decide
>
> Registered **now**, before any dump exists. The axis is the one `PROOF.md` §25.3 established as
> the mechanism — complete-versus-incomplete factorization — **not** the diagonal-spread metric,
> which the same section records as non-explanatory for CBFS (`PROOF.md:2729-2730`). All quantities
> below are printed by the unmodified frozen scripts named in §5.
>
> | verdict | registered threshold | consequence |
> |---|---|---|
> | **D-SINGULAR** | `splu` raises at **all three** `diag_pivot_thresh` values (0, 0.1, 1) — **or** `analyze_dump.py` reports zero rows > 0 **or** zero cols > 0 | The assembled hump `dRdWTPC` is **singular**. **M4 and M5 are not bought.** |
> | **D-ILLCOND-CATASTROPHIC** | `splu` completes at ≥ 1 threshold **and** the minimum `‖Ax−b‖/‖b‖` over the completed thresholds is **> 1.0e-6** | The assembled operator is **catastrophically ill-conditioned**: a complete factorization with partial pivoting cannot itself reach the tolerance the Krylov solve is asked for (`gmresRelTol: 1.0e-6`, `runScript_hump.py:74`). **M4 and M5 are not bought.** |
> | **D-MERELY-SLOW** | `splu` completes with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-6` **and** `spilu` raises `Factor is exactly singular` at **≥ 1** of the four registered settings | The hump is in **CBFS's mechanism class**: the incomplete factorization is singular, the complete one is not. The operator is exonerated; the blocker is not rank or conditioning of the assembled matrix. **M4/M5 become purchasable — by Sanaa, not by this lane.** |
> | **D-UNREGISTERED-CLASS** | `splu` completes with `min ‖Ax−b‖/‖b‖ ≤ 1.0e-6` **and** `spilu` succeeds at **all four** settings | The hump is **not** in CBFS's mechanism class, and none of the three verdicts above applies. Recorded as `NOT A RESULT` **for the singular-or-not question**, with the four `spilu` rows printed beside it. No consequence for M4/M5 is registered for this branch, deliberately. |
> | **PENDING** | stage O2 not launched, or launched and stopped by the budget ceiling or the memory guard with **zero** completed `splu` factorizations | `PENDING`. Nothing is decided; the price of finishing is reported. |
>
> **The registered consequence, carried verbatim as instructed:**
>
> > **if M1 returns singular or catastrophically ill-conditioned, M4 and M5 are not bought**
>
> **And the source sentence it comes from, carried verbatim from
> `W4_ADJOINT_PC_UNBLOCK.md:257-260`:**
>
> > M1 + M2 first: **40 core-min buys the singular-or-not answer offline plus the negative control
> > the programme never ran** — and if M1 returns a singular or catastrophically ill-conditioned
> > assembled operator, M4 and M5 should not be bought at all.
>
> **Partial-but-decisive is registered too.** Stage O2's script prints incrementally, and the
> `spilu` sweep completes in seconds while each `splu` takes minutes. A stop after the four `spilu`
> rows and **≥ 1** completed `splu` is sufficient for D-SINGULAR, D-ILLCOND-CATASTROPHIC,
> D-MERELY-SLOW and D-UNREGISTERED-CLASS as written above, and is graded, not voided. A stop with
> **zero** completed `splu` is `PENDING`.
>
> **The caveat this rule inherits and does not repair**, carried from `PROOF.md:2800-2803` and
> restated in `W4_ADJOINT_PC_UNBLOCK.md:222-226`: `dRdWTPC` is the **assembled preconditioner**
> approximation, not the matrix-free `dRdWTMF` that GMRES actually applies. Every verdict above is a
> statement about the assembled matrix. It is corroborative of, not identical to, the real solve,
> and no verdict in this file may be reported as a statement about `dRdWTMF`.

**Three notes on how this item reads that inherited rule, and none of them changes it.**

1. **The `analyze_dump.py` clause of D-SINGULAR is already settled and is not re-run here.** Zero
   rows = 0, zero cols = 0, zero diagonal entries = 0 were measured at stage O1 and graded HIT
   (`W4_M1M2_RESULTS.md:99-101`, `:120`). That closes the cheap half of D-SINGULAR. **The `splu`
   half is what this item buys**, and D-SINGULAR as a whole remains open until it returns.
2. **The `PENDING` row's phrase "stopped by … the memory guard" covers this item's stop** even
   though the mechanism is a cgroup and not a watcher script (§7). A stop is a stop; the row grades
   on **how many `splu` factorizations completed**, not on which instrument stopped it.
3. **The `dRdWTPC`-is-not-`dRdWTMF` caveat is carried, not repaired.** No verdict this item produces
   may be reported as a statement about `dRdWTMF`, and none will be.

---

## 4. Cost

**Unit: core-minutes = wall s × ranks ÷ 60** (`CLAUDE.md` rule 12). This lane bills **cores × wall
for the whole clock**, because a `docker run` holds its `--cpus` whether the process saturates it or
not (`DAFOAM_CHARTER.md` §12). At `--cpus=1`, **core-min = wall-min**.

| item | figure | source |
|---|---|---|
| **Registered price** | **35.0 core-min** = **$0.02993** | §4a, from the CBFS `scipy` basis |
| **Hard ceiling** | **50.0 core-min** = **$0.04275** | registered here; **an overrun STOPS the run** |
| **Wired stop** | `timeout` = `min(2700, 50.0 × 60)` = **2700 s** = **45.0 core-min** at `--cpus=1` | §6 |

```
cost_basis: c7a.4xlarge at $0.0513/core-hour, REPORTED-BY-OWNER (owner-stated 2026-08-21/22),
            NOT MEASURED -- the box cannot read its own billing
            (COMPUTE_BUDGET_CHARTER.md section 5; CLAUDE.md rule 12).
predicted:  35.0 core-min / 60 * $0.0513 = $0.029925  -> $0.02993
ceiling:    50.0 core-min / 60 * $0.0513 = $0.042750  -> $0.04275
wired stop: 2700 s at --cpus=1 = 45.0 core-min = $0.038475
```

Both figures are far under the \$25 pre-authorisation and are costed anyway: **a blanket is not a
per-item read** (`CLAUDE.md` rule 9).

**The wired stop is 5.0 core-min stricter than the ceiling, and that is deliberate.** `timeout 2700`
means the ceiling **cannot** be reached by this command. The gap is the margin for the container's
own start-up and teardown, which this lane bills but does not control. **The registered ceiling is
still 50.0 core-min**; if any accounting of the launch lands above it, the item is over its ceiling
and is reported as an overrun regardless of what the `timeout` did.

### 4a. Where the 35.0 core-min comes from

The basis is the CBFS `scipy` measurement cited in `c8254a4a` §4b, re-cited by path:

> `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md:212-216` — The CBFS `scipy` analysis measured
> **≈ 10.5 wall-minutes at `--cpus=4`** — the `chain_analysis.sh` window from the force dump's
> completion (`force_dump.out`, 06:37) to `ANALYSIS_DONE 2026-08-02T06:47:57Z`
> (`analysis_final.log`) — i.e. ≈ 42 core-min as this lane bills, against a line item priced at
> "<1 each".

Three adjustments, each stated rather than folded in:

1. **`--cpus=4` → `--cpus=1` does not change the wall clock much.** `scipy.sparse.linalg.splu` is
   SuperLU, serial; the CBFS window was serial work inside a 4-cpu container. The wall is carried
   forward roughly unchanged, and the **billing** falls by 4× because this item holds one core.
2. **The CBFS window also contained `analyze_force_rhs.py`** (`chain_analysis.sh:6` runs both
   scripts under one `docker run`), so ≈ 10.5 wall-min is an **upper** bound on CBFS's
   `analyze_dump3.py` alone. This is an over-estimate of the basis, carried as-is.
3. **The hump is bigger.** Predicted `nnz(L+U)` is **2.1 – 3.5×** CBFS's 3.90e8 (§5, O2R-P1), and
   SuperLU's factorization cost grows faster than linearly in fill. Taking a 2.4 – 4.3× wall
   multiplier on ≈ 10.5 wall-min gives **25 – 45 wall-min**, which is also the band
   `W4_M1M2_RESULTS.md:324` already priced the re-buy at (*"25 – 45 core-min"*). The registered
   price is the band's midpoint, **35.0**.

### 4b. The C-P1 hypothesis, registered here as this item's own formal prediction

`W4_M1M2_RESULTS.md` §4f graded C-P1 a MISS and recorded, honestly, that its hypothesis was never
tested:

> `W4_M1M2_RESULTS.md:199-204` — C-P1 predicted that the `scipy` exact-LU factorization would blow
> M1's 25.0 core-min price. **That factorization never ran**, so the claim is untested, not refuted
> — M1 came in cheap precisely by not doing the expensive thing. Reporting C-P1 as a clean MISS
> would flatter this lane; it is a MISS whose hypothesis is still open, and O2's re-buy is the test.

**This item is that test, and the hypothesis is re-registered as a prediction before the spend:**

| id | frozen prediction | HIT/MISS rule |
|---|---|---|
| **C-P1R** | the `scipy` exact-LU factorization of the hump `dRdWTPC` **exceeds 25.0 core-min** as this lane bills | HIT iff measured O2 spend > 25.0 core-min. A `timeout` stop at 2700 s **HITs** it (45.0 > 25.0) and says so; a completion under 25.0 core-min is a clean **MISS** |

**And the harder-test disclosure, because it would be easy to hide.** The original C-P1's basis was
≈ 42 core-min *at `--cpus=4`*. Running at `--cpus=1` divides the billing by four, so C-P1R needs
**more than 25 wall-minutes** where C-P1 would have needed only 6.25. **This lane is registering the
hypothesis on the harder billing rather than re-billing at `--cpus=4` to flatter it.** `--cpus=1` is
chosen because the work is serial and a co-tenant should have the other cores, not because it makes
the number look better — and it makes the number look worse.

### 4c. Registered deliverable — predicted-vs-actual cost comparison

Standing directive from Sanaa, 2026-08-23, relayed verbatim through the supervisor chain:

> "for all teams involved once a process is completed, the estimated costs must be compared with the
> actual incurred costs so we can improve the lab's estimates."

**Registered here, before the spend, as a deliverable of this item's RESULTS record** — not as a
gate, threshold, cap or label, and it changes none of them. The RESULTS for this item **must** carry:

| field | how it is produced | labelling |
|---|---|---|
| **predicted core-min** | **35.0**, frozen in §4 above | registered prediction |
| **actual core-min** | wall from `$LOG.start` / `$LOG.end` (§6) × 1 cpu ÷ 60 | **MEASURED**, from this item's own log artifacts |
| **predicted \$** | \$0.02993 | **DERIVED** at \$0.0513/core-h, REPORTED-BY-OWNER, **not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| **actual \$** | actual core-min ÷ 60 × \$0.0513 | **DERIVED**, same rate, same caveat |
| **ratio** | actual ÷ predicted core-min, to 2 d.p. | arithmetic on the two rows above |
| **gap attribution** | the difference split three ways: **contention** (a shared box slowing a fixed amount of work) / **waste** (compute that produced no measurement) / **misprediction** (the estimate itself being wrong) | each with its own core-min figure; the three must sum to the gap or the shortfall is named |

**Waste is named separately and never folded into misprediction.** The model is the parent item's own
row: `W4_M1M2_RESULTS.md:215` and §5a (`:240-266`) carry **20.00 core-min of waste** from a staging
fault as a line of its own, with its cause and its class, and `CLAUDE.md` rule 12's *"waste is
reported, not absorbed"* is why. If this item's actual lands near 35.0 for offsetting reasons, that
coincidence is stated as one — the parent record's §5 does exactly that at `:232-235`.

**Where the row lands.** At completion the comparison row is appended to
**`docs/COST_CALIBRATION.md`**, the central ledger, under concurrent-append discipline like the
docket's: re-derive at append time, in the same shell invocation, and stage only that path under the
private-index protocol (`CLAUDE.md` rules 10, 11). **That file does not exist on this box at the
moment of this freeze** (checked 2026-08-23); if it still does not exist at this item's completion,
**the row is drafted inside this item's RESULTS for the supervisor to land**, and this lane appends
it nowhere else.

---

## 5. The frozen predictions

Every row is a prediction made **before** the run, with a numeric band and a basis cited to an
existing record **by path and line**. HIT means the measured value lands inside the band as stated;
MISS means it does not. **A MISS is reported as a miss (`DAFOAM_CHARTER.md` §12) and does not get
re-banded.** All six quantities are printed by the unmodified `analyze_dump3.py` except O2R-P5 and
O2R-P6, whose instruments are named in §6 and §7.

| id | quantity | frozen prediction (band) | HIT/MISS rule | basis (path:line) |
|---|---|---|---|---|
| **O2R-P1** | `nnz(L+U)` from `splu`, at the **highest completed** `diag_pivot_thresh` | **8.0e8 – 1.35e9**, point **1.05e9** | HIT iff inside band | **Inherited verbatim from the frozen prediction M1-P10**, `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md:80` (CBFS 389,944,580 at thresh 1 = 28.4× `nnz(A)`; linear-fill branch 9.6e8, superlinear `n^{4/3}` branch 1.29e9). The hump's `nnz(A)` is now **measured** at 33,662,810 (`W4_M1M2_RESULTS.md:117`), which lands 0.1 % from the 33.7e6 the band was built on, so the band is carried unchanged rather than re-fitted |
| **O2R-P2** | number of the **3** `diag_pivot_thresh` values (0, 0.1, 1) at which `splu` **completes** | **exactly 3 of 3** | HIT iff exactly 3; **any other count is a MISS** and is still graded under §3 | CBFS completed 3 of 3 (`/home/ubuntu/certonomous-runs/W4-cbfs-reordering/analysis_final.log:10-12`; `cases/dafoam/PROOF.md:2778-2780`). Supported on the hump by zero rows / zero cols / zero diagonal entries all **0** (`W4_M1M2_RESULTS.md:120`), which closes the cheap half of D-SINGULAR. **Argued against** by the hump's 13.01-decade diagonal spread vs CBFS's 8.67 (`W4_M1M2_RESULTS.md:139`) — this lane predicts 3 anyway, and records that it is predicting against its own strongest contrary hint |
| **O2R-P3** | `min ‖Ax−b‖/‖b‖` over the completed `splu` thresholds | **1.0e-13 – 1.0e-7**, point **1.0e-10** | HIT iff inside band; PENDING iff zero `splu` completed | CBFS min = 2.5355e-12 at thresh 1 (`analysis_final.log:12`; `PROOF.md:2780`). Band widened **six decades** upward from CBFS's value to cover the hump's 4.3 extra decades of diagonal spread (`W4_M1M2_RESULTS.md:139`), which `PROOF.md:2729-2730` records as **non-explanatory** and which is therefore used only to widen a band, never to move a threshold |
| **O2R-P4** | number of the **4** registered `spilu` `(drop_tol, fill)` settings that raise `Factor is exactly singular` | **exactly 4 of 4** | HIT iff exactly 4. **The graded §3 input is the frozen M1-P8 rule of ≥ 3 of 4** (`W4_M1M2_PREREGISTRATION.md:78`); O2R-P4 is a sharper sub-prediction and does not replace it | CBFS 4 of 4 (`analysis_final.log:4-7`; `PROOF.md:2774-2777`), and the hump's own `-9 DIVERGED_NANORINF` at iteration 0 under the identical stock ILU stack, now reproduced **twice deliberately in one afternoon** on this box (`W4_M1M2_RESULTS.md:48-49`) |
| **O2R-P5** | wall time of the container, `--cpus=1` | **1500 – 2700 s** = **25.0 – 45.0 core-min**, point **2100 s / 35.0 core-min** | HIT iff the run **completes** with wall inside the band. A `timeout` stop at 2700 s is **MISS (high)**; completion under 1500 s is **MISS (low)** | §4a: `W4_M1M2_PREREGISTRATION.md:212-216` (≈ 10.5 wall-min at `--cpus=4`, CBFS) × 2.4 – 4.3 fill multiplier; band equal to the re-buy price already published at `W4_M1M2_RESULTS.md:324` |
| **O2R-P6** | peak container memory high-water (cgroup, §7b) | **8.0 – 20.0 GiB**, point **13.5 GiB** | HIT iff inside band. A **cgroup kill** is **MISS (high)** and is a right-censored measurement of "≥ 20.0 GiB", not a void. An `UNAVAILABLE` cgroup read is **PENDING**, not MISS | Frozen §7a O2 band **8.0 – 22.0 GiB, point 14.0** (`W4_M1M2_PREREGISTRATION.md:449`), truncated at this item's 20.0 GiB cap (§7a). **No measured CBFS `scipy` peak exists on this box** — see §7a |

**What this item does NOT predict, and will not report as if it had.** It makes no prediction about
`dRdWTMF`, about the hump's Krylov convergence **rate**, about whether the hump is memory-bound
(`CLAUDE.md` rule 12 / L-15 — an abort with headroom unused is a convergence statement, not a RAM
statement), or about anything O3 would have measured.

### 5a. The known-answer control question, answered honestly rather than re-charged

`CLAUDE.md` rule 3 requires a reader be shown able to see a non-zero before its zero counts.
**The known-answer control for these exact readers was already run and PASSED**, at stage O0 of the
prior item: `analyze_dump.py` unmodified on the CBFS dump reproduced every published value
(`W4_M1M2_RESULTS.md:186-190`). **It is not re-bought here**, and this file states plainly what that
does and does not carry:

- It **does** establish that this box and this image reproduce the published CBFS numbers today.
- It does **not** establish that `analyze_dump3.py`'s `splu`/`spilu` path reproduces CBFS today —
  O0 exercised `analyze_dump.py`, a **different script**. `analyze_dump3.py` has never been re-run
  on CBFS on this box.
- **The registered mitigation is that this item does not need it to be.** `analyze_dump3.py`'s own
  `spilu` sweep is a four-way negative control **inside the same run**: a reader that cannot raise
  `Factor is exactly singular` at any setting while `splu` completes lands in
  **D-UNREGISTERED-CLASS**, which §3 grades `NOT A RESULT` rather than as a positive finding.
- No perturbation is planted into the hump matrix and **this file does not claim one is**.

Re-running `analyze_dump3.py` on the CBFS dump as a paid control would cost ≈ 10.5 core-min at
`--cpus=1` — **it is priced here and deliberately NOT bought**, because it would consume a fifth of
this item's ceiling to re-certify a script whose output on CBFS is already published to every digit
(`analysis_final.log:1-12`). That is a judgement, it is recorded before the run, and if the
supervisor wants it bought it is a separate decision.

---

## 6. The exact launch command, registered

```
BASE     = /home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning
SCRIPTS  = /home/ubuntu/certonomous-runs/W4-cbfs-reordering
LOG      = $BASE/logs/o2_rebuy_hump_lu_<UTC-STAMP>.log   -- does not exist at the freeze
```

**Nothing below is launched by this document.** Launch authorisation comes from the supervisor as a
separate message after the freeze is verified personally. No agent message is Sanaa's consent
(`CLAUDE.md` rule 9).

```bash
set -u
BASE=/home/ubuntu/certonomous-runs/W4-m1m2-hump-conditioning
SCRIPTS=/home/ubuntu/certonomous-runs/W4-cbfs-reordering
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
LOG="$BASE/logs/o2_rebuy_hump_lu_$STAMP.log"

# ---- VOID-CONDITION ASSERTIONS (section 8). Any failure stops the item BEFORE compute. ----
M=$(md5sum "$SCRIPTS/analyze_dump3.py" | awk '{print $1}')
echo "analyze_dump3.py md5 = $M"
[ "$M" = "f85140f675bcc287f6e4aaf01276c0e4" ] || { echo "VOID: script md5"; exit 2; }

P=$(stat -c %s "$BASE/hump_dump/pmat.dat"); R=$(stat -c %s "$BASE/hump_dump/rhs.dat")
echo "pmat.dat = $P B   rhs.dat = $R B"
[ "$P" = "406022696" ] && [ "$R" = "4137928" ] || { echo "VOID: dump sizes"; exit 2; }

I=$(sudo -n docker images --no-trunc --format '{{.ID}}' dafoam/opt-packages:latest)
echo "image = $I"
[ "$I" = "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc" ] \
  || { echo "VOID: image id"; exit 2; }

# ---- LAUNCH GATE (section 9), re-run immediately before launch, never inherited ----
free_cores=$(( 16 - $(for i in 1 2 3 4 5; do awk '{split($4,a,"/"); print a[1]}' /proc/loadavg; sleep 1; done | sort -n | sed -n '3p') ))
memavail_gib=$(awk '/^MemAvailable:/{printf "%.2f", $2/1048576}' /proc/meminfo)
echo "GATE free_cores=$free_cores memavail_gib=$memavail_gib"
awk -v c="$free_cores" -v m="$memavail_gib" 'BEGIN{exit !(c>=4 && m>=24.0)}' \
  || { echo "GATE NOT MET -- BLOCKED, not launched"; exit 3; }

# ---- THE ONE STAGE ----
date -u +%FT%TZ > "$LOG.start"
timeout 2700 sudo -n docker run --rm --name w4o2_rebuy --cpus=1 \
  --memory=20g --memory-swap=20g --oom-score-adj=500 \
  -v "$SCRIPTS":/scripts:ro \
  -v "$BASE/hump_dump":/mnt/cbfs_dump:ro -w /tmp \
  dafoam/opt-packages:latest bash -lc \
  "source /home/dafoamuser/dafoam/loadDAFoam.sh && python -u /scripts/analyze_dump3.py; \
   rc=\$?; echo CGROUP_PEAK_BYTES=\$(cat /sys/fs/cgroup/memory.peak 2>/dev/null \
     || cat /sys/fs/cgroup/memory/memory.max_usage_in_bytes 2>/dev/null || echo UNAVAILABLE); \
   exit \$rc" \
  2>&1 | tee "$LOG"
rc=${PIPESTATUS[0]}
date -u +%FT%TZ > "$LOG.end"
echo "O2 REBUY rc=$rc" | tee -a "$LOG"
```

**Registered reading of `rc`:** `0` = the script ran to completion; `124` = the **`timeout` fired**
(wired budget stop, O2R-P5 MISS high, §3 partial/PENDING on whatever rows landed); `137` = **SIGKILL,
i.e. the cgroup OOM kill** (§7c); anything else is triaged before grading and is a finding, not a
number to absorb.

**`tee` is registered, and so is its footgun.** `timeout`'s status is taken from `PIPESTATUS[0]`,
not `$?`, because `$?` would report `tee`'s exit. Writing it down is the point: an item whose
budget stop is read off the wrong exit code has no budget stop.

---

## 7. Memory envelope, and the stop that is wired

### 7a. Why the guard is a cgroup and not the watcher script — stated in full

The prior item's mandatory memory guard was `w4_m1m2_memguard.sh`, a host-side watcher.
**That mechanism is NOT used here, and the reason is a rule, not a preference.**

`W4_M1M2_RESULTS.md:300-310` records that **the command that starts `w4_m1m2_memguard.sh` was
refused by a lane's permission system**, and that stage O3 was recorded `BLOCKED` rather than run
unguarded. **Re-attempting that denied command from a different lane, or rewriting it into a form
that slips past the same classifier, is permission laundering** — `CLAUDE.md` rule 9: *an approval
is only as wide as what was approved*, and a denial is not weakened by being re-issued from another
context. **This lane does not re-attempt it and does not route around it.** Unblocking that command
is Sanaa's, and stage O3 remains BLOCKED and out of scope (§10).

**So the stop is moved into the kernel, where it needs no command to arm:**

| element | value | what it does |
|---|---|---|
| `--memory=20g` | **20.0 GiB** | cgroup hard limit; the kernel OOM-kills the container the instant it would exceed it. Nothing has to be running, polling or authorised for this to fire |
| `--memory-swap=20g` | equal to `--memory` | **disables swap for the container**, so the cap is a true resident cap and the process cannot degrade into host-wide thrashing instead of stopping |
| `--oom-score-adj=500` | +500 | if the **host** goes short, the kernel prefers to kill **this** container over a co-tenant. The cgroup cap is independent of this and fires first |
| `timeout 2700` | 45.0 core-min | the budget stop, §4 |

**Derivation of the 20.0 GiB cap, with every input named:**

1. **Frozen band.** `c8254a4a` §7a registered O2's predicted peak as **8.0 – 22.0 GiB, point 14.0**
   (`cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md:449`). That band is inherited, not re-derived.
2. **Measured CBFS `scipy` peak: NONE EXISTS.** No record on this box carries one. The two nearest
   figures are **not** measurements of peak memory and are not treated as such:
   - `/home/ubuntu/certonomous-runs/W4-cbfs-reordering/chain_analysis.sh:6` — CBFS's exact LU
     completed inside a container capped at `--memory=10g`. That is an **upper bound the run did not
     breach**, not a peak.
   - `cases/dafoam/PROOF.md:2782-2784` — the complete factors are *"roughly 3 GB"*. That is an
     **nnz-derived estimate**, not an instrument reading.
   No CBFS `analysis_final.log` line reports RSS, peak or memory at all (checked 2026-08-23).
3. **Box.** `MemTotal = 32,132,604 kB = 30.64 GiB` (read 2026-08-23, §9).
4. **Cap = 20.0 GiB**, i.e. `min(20g, …)` as instructed and below the frozen band's 22.0 GiB top.
   With the §9 launch gate requiring `MemAvailable ≥ 24.0 GiB`, a container that runs all the way to
   its cap still leaves **≥ 4.0 GiB** of the MemAvailable measured at launch that it **cannot**
   touch, and the kernel — not a script, not this lane's judgement — is what enforces that.

**The cost of this design is stated rather than hidden.** The frozen band's top 2.0 GiB
(20.0 – 22.0 GiB) is **unreachable**: a factorization that would have completed at 21 GiB is killed
instead. This item chooses a kernel-enforced stop over a possibly-complete answer in that 2 GiB
window, and records the choice before the run so that a kill in that range is read as a design
consequence and not as a discovery.

**The standing 12 GiB `MemAvailable` launch floor is a registered threshold on Sanaa's desk. It is
neither touched, lowered, re-read nor argued here.** §9's 24.0 GiB requirement **raises** the bar and
never lowers it.

### 7b. How peak is measured, and its honest limits

The graded instrument is the container's **own cgroup high-water**, read from inside the container
after the script exits and printed as `CGROUP_PEAK_BYTES` (§6): `memory.peak` on cgroup v2,
`memory/memory.max_usage_in_bytes` on v1.

- **No host-side sampler runs.** There is no watcher process, no `docker stats` loop and nothing to
  arm — which is the whole point of §7a.
- **The reading includes page cache.** The container reads 410,160,624 B of dump files, whose pages
  are charged to the same cgroup, so `CGROUP_PEAK_BYTES` **overstates anonymous RSS by up to
  ≈ 0.4 GiB**. O2R-P6's band is against the cgroup figure as printed, and this sentence is why the
  band's floor is 8.0 and not 7.6.
- **If the read comes back `UNAVAILABLE`** (cgroup namespace not mounted in this image),
  **O2R-P6 is `PENDING`, not MISS.** An instrument that did not report is not a measurement that
  disagreed.
- **If the container is OOM-killed the line never prints**, and the peak is then known only as
  **≥ 20.0 GiB** — a right-censored measurement, graded MISS (high) against O2R-P6.

### 7c. Registered outcome if the cgroup kill fires

**A cgroup kill is a measurement, not a void.** Registered now, before the run:

1. **The §3 rule is applied to whatever `splu` rows completed**, exactly as its partial-but-decisive
   clause says: ≥ 1 completed `splu` grades D-SINGULAR / D-ILLCOND-CATASTROPHIC / D-MERELY-SLOW /
   D-UNREGISTERED-CLASS; **zero** completed `splu` is `PENDING`. `python -u` is what makes the
   already-printed rows survive the kill.
2. **O2R-P6 is graded MISS (high)** against the 8.0 – 20.0 GiB band, with the peak reported as
   **≥ 20.0 GiB (right-censored)**.
3. **The stage is additionally labelled `stopped by memory`** (`DAFOAM_CHARTER.md` §7), and that
   label claims nothing about the envelope beyond the cap that was breached.
4. **No inference is drawn that the hump is memory-bound.** `COMPUTE_BUDGET_CHARTER.md` L-15 and
   `DAFOAM_CHARTER.md:286-294`: a stage that stops *with headroom unused elsewhere* is bound by its
   own cap, not by the box's RAM. **This lane has made that error before and is naming it in advance.**
5. The spend to the kill is reported gross, and the price of finishing (a larger cap on a larger box)
   is reported, **not spent**.

---

## 8. Void conditions — checked before launch, and they void the item rather than degrade it

| if this differs at launch | consequence |
|---|---|
| `analyze_dump3.py` md5 ≠ `f85140f675bcc287f6e4aaf01276c0e4` (the md5 frozen at `c8254a4a` §5, `W4_M1M2_PREREGISTRATION.md:238`) | **The item is `VOID` before launch.** The container is not started. Nothing is re-bought until the difference is read **as a diff** by the supervisor personally (`CLAUDE.md` TEAM ROSTER: measurement-script diffs are never delegated) |
| `hump_dump/pmat.dat` ≠ **406,022,696 B** | **The item is `VOID` before launch.** The dump would not be the verified operator `W4_M1M2_RESULTS.md:343` describes, and no factorization of a substituted matrix is graded |
| `hump_dump/rhs.dat` ≠ **4,137,928 B** | **The item is `VOID` before launch.** Same reason; `‖b‖₂`'s 13-digit match to the solver's own residual is a property of **that** file |
| `dafoam/opt-packages:latest` image ID ≠ `sha256:9d45679d55fd…` | **The item is `VOID` before launch.** A row must name the image that produced it (`DAFOAM_CHARTER.md` §6) |

All four are **asserted in the launch command itself** (§6), printed to the log, and each exits
non-zero before `docker run`. **A void is a refusal, not a downgrade.** No band in §5 is widened
after a MISS, and no substituted instrument is graded.

### 8a. Completion

**O2 is COMPLETE iff:** all four §8 assertions passed and were printed; the log contains the four
`spilu` rows **and** at least one completed `splu` row; `rc` is `0`; and the ledger row (wall,
cpus, core-min, gross) is written. Anything less is `PENDING` with the missing piece named and
priced, or graded under §3's partial clause where ≥ 1 `splu` landed.

### 8b. Amendment discipline

Before first compute, amendments to this file are legal and **must state the condition and how it
was checked**, naming the artifact that does not exist (`CLAUDE.md` rule 2) — here, the §6 log path.
**After the container starts, the gates, thresholds, caps and labels here are closed**; changes land
only as dated addenda that cannot alter them, and originals are struck, never rewritten
(`CLAUDE.md` rules 2 and 6).

---

## 9. Launch gate

**Registered, and not negotiable by this lane:**

> **`free_cores >= 4` AND `MemAvailable >= 24.0 GiB`**, where
> `free_cores = 16 − median-of-5 runnable count` and the runnable count is the numerator of
> `/proc/loadavg` field 4, sampled at 1 s intervals.

The 24.0 GiB requirement **raises** the standing 12 GiB floor and never lowers it; the standing floor
is a registered threshold on Sanaa's desk and is untouched here (§7a). It is set at 24.0 rather than
25.0 because this item's container is capped at 20.0 GiB by the kernel (§7a), so 24.0 GiB leaves
≥ 4.0 GiB the container provably cannot take.

**The gate is re-run immediately before launch and is never inherited from the reading below.** A
gate that is not met means the stage is recorded **`BLOCKED`** and is **not run** — not run at a
lower bar, not run "briefly", not run with the cap raised.

**Readings taken at the freeze, 2026-08-23T20:58:23Z — a dated observation and nothing more:**

```
  nproc                 16
  MemTotal              32,132,604 kB  = 30.64 GiB
  MemAvailable          18,360,856 kB  = 17.51 GiB    -> requirement >= 24.0 GiB   NOT MET
  median-of-5 runnable  12
  free_cores            16 - 12 = 4                   -> requirement >= 4          MET
  image present         dafoam/opt-packages:latest 9d45679d55fd  (full ID asserted, section 2a)
  analyze_dump3.py      f85140f675bcc287f6e4aaf01276c0e4, 33 lines  -> equal to c8254a4a section 5
  hump_dump/pmat.dat    406,022,696 B                 -> equal to the frozen size
  hump_dump/rhs.dat     4,137,928 B                   -> equal to the frozen size
```

**At the freeze the gate is NOT MET on memory: the box is busy.** That is recorded here rather than
smoothed over. It has no bearing on the freeze — this document launches nothing — and the gate is a
re-run condition on the launch instant, not on this paragraph.

---

## 10. What is explicitly NOT run, NOT touched and NOT staged by this item

**Nothing below is launched, staged, queued, meshed, primed or costed here.**

| held item | status | why it is not in this item |
|---|---|---|
| **Stage O3** (`pc_ladder.py` control + sublu, M1-P11 / M1-P12) | **BLOCKED — Sanaa's to unblock** | Its mandatory memory-guard start command was **denied in a lane's permission context** (`W4_M1M2_RESULTS.md:300-310`). **Nobody re-attempts that denied command and nobody routes around it** (`CLAUDE.md` rule 9). O3 is not in scope, not re-priced, not re-designed and not mentioned in any §6 command |
| **M3** reproduction of A6 to iteration 900 | not bought | `W4_ADJOINT_PC_UNBLOCK.md:251`; out of scope |
| **M4** run to a reason code | not bought | **gated on the §3 consequence carried verbatim in §3**; and needs ≥ 64 GB against this box's 30.64 GiB |
| **M5** memory-binding test | not bought | gated on the same consequence |
| **M6, M7, M8** | not bought | depend on M3/M4 |
| the **~5 core-min GAMG → PBiCGStab ADF sweep** | **NOT RUN — held for Sanaa** | A peer session's claim and a different lane's territory. It decides the ADF defect **class**, not the hump operator. Nothing here touches it |
| the **`useMeanStates: True` + `fieldAverage` arm** | **NOT RUN — held for Sanaa** | `ladder-a/A6/rung_n16_remaining_components/RESULTS.md:545`, *"the unbought `useMeanStates` item on Sanaa's desk"* |
| **anything on A6 CRM N=29** | **NOT RUN, under either reading — held for Sanaa** | The gate has two registered readings and **choosing is Sanaa's**. This item touches it in no way |

**Nothing is filed upstream.** The four prepared DAFoam defect classes (`DAFOAM_CHARTER.md` §10)
stay **`NOT FILED`**, and whatever §3 decides adds nothing to and subtracts nothing from that state.

---

## 11. What this item may and may not conclude

- It **may** conclude, per §3 and only per §3, that the **assembled** hump `dRdWTPC` is singular,
  catastrophically ill-conditioned, or in CBFS's mechanism class.
- It **may** conclude that C-P1's hypothesis (§4b) is HIT or MISS — the first time that hypothesis
  is tested at all.
- It may **not** conclude anything about `dRdWTMF`, the matrix-free operator GMRES actually applies
  (§3, closing paragraph, carried verbatim).
- It may **not** conclude anything about the hump's convergence **rate**, which requires a
  terminating `KSPConvergedReason` and therefore M4.
- It may **not** conclude that the hump is memory-bound (§7c item 4).
- It may **not** promote the 13.01-decade diagonal spread to a verdict. `c8254a4a` §2a registered
  that metric *"Reported, not decision-bearing"* and `PROOF.md:2729-2730` records it as
  non-explanatory; `W4_M1M2_RESULTS.md:143-147` already refused that promotion once and this file
  refuses it again in advance.
- **No verdict here is `PASS` on an FD gate: no gradient is produced by this item**, so
  `DAFOAM_CHARTER.md` §2's FD-table requirement is not engaged and no gradient number will be quoted.

---

## 12. Related

| document | what it owns that this file does not |
|---|---|
| `cases/dafoam/ladder-b/W4_M1M2_PREREGISTRATION.md` (`c8254a4a`, blob `e7b5f0d4…`) | The §3 decision rule this item inherits verbatim; the frozen instrument md5s; the §7a memory bands; M1-P8 / M1-P9 / M1-P10 |
| `cases/dafoam/ladder-b/W4_M1M2_RESULTS.md` (`64479072`) | The dump's provenance and verification; the O0 known-answer control; the C-P1 MISS whose hypothesis §4b re-registers; O3's `BLOCKED` |
| `cases/dafoam/PROOF.md` §25.3 | The CBFS singular-ILU diagnosis this stage replicates on the hump, and the `dRdWTPC`-is-not-`dRdWTMF` caution |
| `cases/dafoam/ladder-b/W4_ADJOINT_PC_UNBLOCK.md` §5b.1 | The M-ladder, its prices and its bases |
| `docs/charters/DAFOAM_CHARTER.md` | §6 image identity; §7 memory envelope; §8 verdict vocabulary; §12 cost |
