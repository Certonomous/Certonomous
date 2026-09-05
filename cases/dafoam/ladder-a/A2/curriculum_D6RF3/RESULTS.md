# D6RF3 — RESULTS

**Item:** `D6RF3`, A2 wing multipoint FD at the `D6R` endpoint.
**Registration:** `cases/dafoam/ladder-a/A2/curriculum_D6RF3/PREREGISTRATION.md`,
**FROZEN at `9c079a84`**, blob md5 `01079356d794186d21d52e86e1e67907` — verified in this
invocation by `git show 9c079a84:…/PREREGISTRATION.md | md5sum`.
**Run root:** `/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd`.
**Ran:** 2026-09-05T22:22:50Z → 22:23:40Z.
**Written:** 2026-09-06, by a `lab-lane` from the dafoam-supervisor's personally-discharged
crash triage (`SUPERVISION_CHARTER.md` §3 check 2, which may not be delegated), plus the two
cross-checks that triage flagged as unverified and that this lane verified independently.

> ### VERDICT — `NOT A RESULT`
>
> **Ladder rung 2** of §3g's verdict ladder: *"a registered arm did not run → `NOT A RESULT`,
> arms named — the item can never be `PASS` with an arm unbought."* The unbought arm is
> **`REF_off`**. Rung 6 fires independently and would reach the same token: every gated row's
> input is absent (§5 below).
>
> **This is a ONE-ROW `PATCHED` verdict and is NOT a full `DAFOAM_CHARTER.md` §6 verdict about
> DAFoam** (§12.6's registered label, carried here verbatim). The row bought is `PATCHED`,
> image `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`,
> `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425`. The `SHIPPED` row is **NOT BOUGHT** and
> stands **priced at 155.70 core-min** so a successor can buy it.
>
> **Spend: 2.067 core-min against a 480.0 core-min cap** (0.431 % of cap). No overrun.

**A first `GATE FAIL` is a waypoint and this is not even that** — it is a `NOT A RESULT` bought
for 2.067 core-min that measured something no amount of pre-checking had. Sanaa, 2026-09-04: the
case is worked until it passes its gate, **and the gate is never widened to fit.** Nothing in this
record moves a gate, threshold, band, cap or label. **SUBMISSIONS PARKED.**

---

## 1. WHAT HAPPENED — THE PRIMAL DID NOT FAIL. IT CONVERGED TO ITS ITERATION BUDGET AND WAS REFUSED BY A BOOKKEEPING BAR AFTER `End`

`F_mp` exited `rc=1` at 22:23:40Z. `STATUS.chain` reads
`chain=STOPPED_AT_FIRST_NONZERO arm=F_mp rc=1 order=[F_mp REF_off] not_run=[REF_off]`.
**`REF_off` never ran.**

**It is not memory.** `ledger.txt`: `inspect(exit,oomkilled)=[1 false]`,
`memavail_GiB=27.71`, `memavail_pre_GiB=27.71`, `memavail_post_GiB=27.70` — the host lost
**0.01 GiB** across the whole arm. `DAFOAM_CHARTER.md` §7's L-15 caution applies in the
direction it was written for: **naming memory here would be the wrong blocker**, and memory is
not named.

**Every staging and delivery gate PASSED**, from `F_mp_launch.out` and
`F_mp_STAGING_EVIDENCE.txt`: `G_ROOT_PASS`, `G_ROOT5_PASS`, `G_ROW_PASS`, S1, S3, S4, S5, S6,
S7, `G_DELIVERY` (8 instruments, 8 level-0, 0 by closure), `G_ANCHOR` (2 anchor-scoped readers),
`G_COLD` (`age_datum_epoch=1788646989`), `CMDFILE` (md5 `813460d143534cc12a64a04219f821f6`,
`deadline_in_container_s=7110`), `RUNAWAY_GUARD` (cap 480.0, ceiling 1440.0).
**The failure is downstream of all of them and none of them is implicated.**

### 1.1 The solve ran to completion and printed `End`. The refusal came afterwards.

`F_mp_20260905T222250Z_43793.log`, 2,397 lines. The last time step and the refusal:

| artefact line | content |
|---|---|
| `:2085` | `Time = 1000` — the case's `endTime` |
| `:2093` | `Time step continuity errors : global = -2.960749047e-13` |
| `:2097` | `CD: 0.0184758685 final: 0.0184758685` |
| `:2098` | `CL: 0.3999751808 final: 0.3999751808` |
| `:2100` | `ExecutionTime = 19.71 s  ClockTime = 20 s` |
| **`:2102`** | **`End`** |
| `:2105` | `Primal min residual 1.316217833e-05` |
| `:2106` | `did not satisfy the prescribed tolerance 1e-08` |
| `:2107` | `Primal solution failed!` |

**`End` is at `:2102` and the entire refusal block is at `:2104-2108`, banner-wrapped in
`****`.** The solver had already finished. The exception is raised in
`dafoam/mphys/mphys_dafoam.py:345` and surfaces as
`AnalysisError: 'cl04.coupling.solver' <class DAFoamSolver>: Error calling solve_nonlinear(),
Primal solution failed!`.

**This is `N-D42`, a second time and on a different case.** `docs/NUMERICS_KNOWLEDGE.md`
`N-D42` established the post-`End` ordering from **one** log
(`CURRICULUM-D4-SHIPPED-a2-wing-cdmin/F3_20260826T205120Z_411184.log`, `End` at `:864`, failure
block `:866-869`) and explicitly declined to generalise: *"this option, this DAFoam version,
this image"*. **This log is an independent second instance on a different case
(A2 wing multipoint, 3 flight points, cl04's solver) in the same image**, with the same
ordering. It corroborates N-D42; it does not extend its stated scope, and this record does not
extend it either.

### 1.2 ⚠ CORRECTION TO THE TRIAGE'S ARITHMETIC — THE MISS IS **1.316×**, NOT **1316×**, AND `N-D42` IS WHY

The triage handed down reads *"the residual floor is `1.316e-05` against a registered `1e-08` —
**short by a factor of 1316**."* **That is the nominal ratio, and it is not the bar the run was
judged against.** `N-D42` measured the criterion itself:

> `DASolver::checkPrimalFailure()` declares failure iff
> `primalMaxRes / primalMinResTol > primalMinResTolDiff`, so the option is a **ratio bar** and
> the effective accept floor is `primalMinResTol × primalMinResTolDiff`.

This run's own log carries both terms in its case header — `:334` `primalMinResTol 1e-08;` and
`:505` `primalMinResTolDiff 1000;` — so the **effective accept floor is
`1e-08 × 1000 = 1.0e-05`**, and the measured `1.316217833e-05` exceeds it by

    1.316217833e-05 / 1e-08 = 1316.217833   against a bar of 1000
    -> exceeded by 1.3162x, i.e. FAILED BY 32 %, not by three orders of magnitude.

**The parallel to N-D42's own specimen is close and worth keeping:** there the ratio was
`1115.891818` against `1000`, *"exceeded the armed bar by only 1.116×, i.e. it failed by 12 %."*
Here it is **1.316× / 32 %**. **A primal that misses by 32 % and one that misses by a factor of
1316 invite completely different successor decisions**, and the second figure is the one that
would be quoted if this correction were not written down. **The lab has already paid for this
distinction once; N-D42 exists to stop it being paid for twice.**

### 1.3 The primal is converged in every physical sense the log can report

* **Continuity** — `global = -2.960749047e-13` at `Time = 1000`.
* **Steadiness** — `CD` and `CL` carry `initRes == final` at every printed step, and across the
  last five printed steps (`Time = 600 … 1000`, log `:2033`–`:2098`) `CD` spans
  `0.01847587528 … 0.0184758685`, a spread of **6.78e-09 absolute, 3.67e-07 relative**.
* **The residual is flat, not descending** — `p initRes` reads `1.316276465e-05` at
  `Time = 900` (`:2074`) and `1.316217833e-05` at `Time = 1000` (`:2091`): a move of
  **4.5e-05 relative over 100 iterations**. It is a floor, not a trajectory, and 100 more
  iterations would not have crossed anything.
* **Agreement with the producing optimiser's own recorded `CD`** — §4 below, 0.0356 %.

### 1.4 What this record does NOT decide, and may not

**Whether a successor may register a reachable primal tolerance is NOT decided here.** That
touches a registered threshold, and retiring or moving a gate threshold is Sanaa's
(`CLAUDE.md` FIRST-ACTION rule; `ESCALATION_CHARTER.md`). **`primalMinResTol` is not changed
anywhere by this record**, and neither is `primalMinResTolDiff`. The measured floor
`1.316217833e-05`, the effective accept floor `1.0e-05` and the 1.316× miss are recorded as
**evidence**, and this record stops there.

---

## 2. THE VERDICT LADDER, WALKED IN ORDER (§3g)

| rung | test | reading |
|---|---|---|
| 1 | completion clause failed on an arm that **ran** | `F_mp` ran and `rc=1` — rule 4 fails at its first clause. **Fires.** |
| **2** | **a registered arm did not run** | **`REF_off`. FIRES — and this is the operative rung: the item can never be `PASS` with an arm unbought.** |
| 3 | any gated input non-finite (§3f) | not reached — the inputs are **absent**, not non-finite. §3f's `NON_FINITE_INPUT` reason is **not** claimed here, and claiming it would be a false reading. |
| 4 | `G-DVL` `GATE FAIL` | no input |
| 5 | registered pathologies | no input |
| 6 | any gate `NOT A RESULT` for want of an input | **Fires independently** — §5. |
| 7 | any gated row `GATE FAIL` | unreachable |
| 8 | else `PASS` | unreachable |

**`NOT A RESULT`.** Rules 1 and 5 of `CLAUDE.md` permit this direction only: a `NOT A RESULT`
can turn a `PASS` or `GATE FAIL` into itself, never the reverse. Nothing here was turned; there
was never a candidate verdict to turn.

---

## 3. STRICT COMPLETION (`CLAUDE.md` rule 4) — FAILS AT CLAUSE 1

| clause | reading |
|---|---|
| `rc = 0` | **`rc = 1`. FAILS.** `ledger.txt`, and `inspect(exit,oomkilled)=[1 false]` from the kernel. |
| an `End` line | present, `:2102` — **and it is the interesting part, not a pass** |
| last time == `endTime` | `Time = 1000` == `endTime 1000` — held |
| fields present | not applicable: `writeInterval` wrote no output time directory in a 1,000-iteration run |
| `ExecutionTime` count | not asserted; the run stopped before the grader ran |
| age guard | `G_COLD` armed at `age_datum_epoch=1788646989`; no registered product survived to be aged |

**The run is NOT done.** Rule 4 is all-or-nothing and the first clause is enough. **The `End`
line is present and that does not rescue it** — which is precisely the shape N-D42 named.

---

## 4. `X-CDLOG` — ⚠ THE REGISTERED ROW DID **NOT** FIRE. WHAT FIRED IS A DIFFERENT, UNREGISTERED COMPARISON, AND THE DIFFERENCE MATTERS

**This section corrects the triage, which reported that `X-CDLOG` "effectively fired at the
first attempt".** The hedge in that word is doing real work and this record makes it explicit.

### 4.1 The registered row's source does not exist on disk

§3d's `X-CDLOG` compares `d6rf3_fd_endpoint.json`'s `points.<pt>.CD` — §2a's **registered gated
source** — against the `CDLOG` constants frozen in the grader at `d6rf3_grade.py:202`.

**Measured on disk in this invocation:**
`/home/ubuntu/certonomous-runs/CURRICULUM-D6RF3-a2-wing-multipoint-fd/F_mp/d6rf3_fd_endpoint.jsonl`
is **one line long** and that line is
`{"kind": "endpoint_dvs", "n_patchV": {...}, "n_shape": 96, "n_twist": 7, "source": "/mnt/F_mp/OptView.hst"}`.
**No `{"kind":"primal", …}` record was ever emitted, and no `d6rf3_fd_endpoint.json`
exists anywhere in the run root.** `points.cl04.CD` was never written.

**Therefore the registered `X-CDLOG` row did not fire, and neither did the third planted control
(§3e's CD reader), which plants into a copy of that same absent artefact.**

### 4.2 What DID fire is stdout-against-stdout, and it is worth recording as that

Both sides of the comparison below are **stdout `CD:` lines**, and saying so is the point:

| quantity | value | artefact |
|---|---|---|
| this run's endpoint primal, `cl04` | `CD: 0.0184758685` | `F_mp_20260905T222250Z_43793.log:2097` |
| `D6R`'s `O_mp` log, last finite major, `cl04` | `0.01846929883` | frozen at `d6rf3_grade.py:202` as `CDLOG["cl04"] = 1.846929883e-02`; `CDLOG_LINES["cl04"] = 262185` |
| **relative difference** | **`3.557076e-04` = `0.0356 %`** | computed here |

and beside it, `CL`:

| quantity | value |
|---|---|
| this run's `cl04` | `CL: 0.3999751808` (`:2098`) |
| the `cl04` design target | `0.4` |
| **relative difference** | **`0.0062 %`** |

**`CDLOG` is a frozen constant registered in the grader BEFORE this run** — it is in the
blob at `9c079a84`, and the run started at 22:22:50Z. It could not have been chosen to fit.

**What this supports, stated at exactly its strength:** a fresh endpoint primal at the
reconstructed physical design vector, run cold on a staged copy, reproduces the producing
optimiser's own recorded `CD` for `cl04` to **0.0356 %**, and its `CL` sits **0.0062 %** off the
`cl04` design target. **That is real, and it is a finding.** It is *evidence bearing on* §2a's
premise that the baseline primal measures the same physical quantity the log recorded.

**What it is NOT:** it is not the registered `X-CDLOG` row, because that row's numerator does not
exist. A record that reported it as `X-CDLOG` would be reporting a gate that did not run.

### 4.3 ⚠ FALSIFIER `F1` IS **UNRESOLVED** — ITS BAR WAS NEVER MEASURED

The triage reported *"that is falsifier `F1`'s question answered in the affirmative … at
0.0356 % against a yardstick of the primal's own repeatability."* **The artefacts do not support
that, and this is the second correction.**

`F1`'s registered bar, §8, verbatim: *"disagree … by more than the primal's own repeatability —
**measured in the same run by the `baseline` vs `baseline_repeat` primals**, whose
`|J − J_repeat|` is already computed as `eta_raw`."*

**`baseline_repeat` never ran.** The log carries **exactly one `End` line** and **exactly one
`Time = 1000` block**; `cl04`'s first baseline primal was refused and `nonlinear_runonce`'s
Gauss–Seidel sweep aborted the whole model before `cl05`, `cl06`, `baseline_repeat` or any
perturbed primal was attempted. **`eta_raw` was never computed. `F1`'s bar does not exist for
this run.**

> **`F1` is `UNRESOLVED`.** A falsifier whose registered bar was never measured cannot be
> answered in either direction. 0.0356 % is a number without the yardstick it was registered to
> be compared against.

**And §12.5 is why this matters rather than being pedantry.** That section's own lesson — paid
for at 62.33 core-min by `S1FDP` — is *"the falsifier was sized against ONE test and then
asserted to fail a DIFFERENT test … a falsifier can only falsify the gate it actually fails."*
§12.5 then singles out `F1` as **the design the family should prefer**, precisely because its bar
is derived from the same run. **The virtue and the vulnerability are the same property:** a bar
derived from the run does not exist when the run stops early. **That is a new fact about the
design pattern §12.5 recommended, discovered by the first run to exercise it, and it is the most
transferable thing in this record.**

`F1` remains a **reported** falsifier and moves no gate in either state.

### 4.4 `F2` and `F3`

* **`F2`** — the §3f finiteness mutation harness. Discharged **before** the freeze
  (`30/30` and `10/10`, `NOT EXERCISED = 0`, §12.5). This run neither strengthens nor weakens it.
  Nothing in this run exercised `NON_FINITE_INPUT`, because the inputs are absent rather than
  non-finite.
* **`F3`** — the arm census, conditioned on *"if both arms run clean"*. **Its precondition
  failed.** `F3` is **UNRESOLVED**, and no FD aggregate or sign-flip count exists to report.

---

## 5. GATES — EVERY GATED ROW IS `NOT A RESULT` FOR WANT OF AN INPUT

| row | registered source | reading |
|---|---|---|
| `G-OFF` ×3 (`cl04`, `cl05`, `cl06`) | §2a `points.<pt>.CD` **and** `d6rf3_ref_off.json` | **`NOT A RESULT`** — both sources absent; `REF_off` never ran |
| `G-PRICE` | §2a at `cl05` vs `CD_f(D4)` | **`NOT A RESULT`** — numerator absent. D4's `opt_IPOPT.txt` was never read and **was never written to**; the price reader's planted control plants into a copy by design |
| `G-FD` + band D | `d6rf3_fd_endpoint.json` | **`NOT A RESULT`** — no FD row was produced |
| `G-DVL` | as above | **`NOT A RESULT`** |
| `R-RED` (reported, not gated) | history `J_f` | not printed; `J_f` is `NaN` per §1e(i) and the §3f disclosure would have carried it |
| `X-CDLOG` (reported, not gated) | §2b | **DID NOT FIRE** — §4.1 |
| `G-CAPS` / `G1` / `G9` / `G12` | ledger, digest, `.so` md5 | `G9`'s subjects are **present and correct** on the one ledger row written: `ROW=PATCHED`, digest `sha256:2927768a…`, `D4S_IDWARP_SO_MD5: 85f59e87253e0a71a813f64ca6e4c425` |

**`PLATEAU_TOL_PCT` — §12.4's registered report obligation, discharged here in the only way the
artefacts allow.** §12.4 required the result record to print each component's measured
`plateau_pct` beside the `10.0` bar and *"state whether the bar was exercised at all."*

> **The bar was NOT exercised. No component's `plateau_pct` was computed, because no FD component
> was evaluated. `PLATEAU_TOL_PCT = 10.0` carries no information from this run, in either
> direction.** The `PLATEAU_TOL_PCT` question §12.4 opened — that `S1FDP` measured a `10.0` bar
> admitting a step carrying 7.931 % adjoint error — **is untouched by this item and remains
> exactly where §12.4 left it.** The bar is **not** changed here.

---

## 6. TWO ROWS (`DAFOAM_CHARTER.md` §6) — ONE BOUGHT, ONE PRICED

| row | toolchain | state |
|---|---|---|
| **PATCHED** | `dafoam-idwarp-rot:v1`, digest `sha256:2927768a16acdea0330180fff95c8879c1dda9efcf6028728523b7dee30f6d35`, `libidwarp.so` md5 `85f59e87253e0a71a813f64ca6e4c425` | **BOUGHT**, and asserted on the ledger row and in the container log (`D4S_IDWARP_SO_MD5`) |
| **SHIPPED** | stock IDWarp, no rotation patch | **NOT BOUGHT. Priced at 155.70 core-min** so a successor can buy it — §6's *"an unbought row that is priced can be bought by a successor; an unbought row that is unpriced quietly becomes never."* |

**This item's verdict is a `PATCHED`-row verdict and must not be reported as a full
`DAFOAM_CHARTER.md` §6 verdict about DAFoam.** The label travels with the number, not in a
header (`DAFOAM_CHARTER.md` §18.6).

**A version string is not an identity** — all three images report DAFoam 5.0.0 / OpenFOAM v2506
/ PETSc 3.15.5.

---

## 7. COST — MEASURED, AND THE ESTIMATE-VERSUS-ACTUAL RULE 12 OWES

**`cost_basis`: c7a.4xlarge at $0.0513/core-h, REPORTED-BY-OWNER, NOT MEASURED** — the box
cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). **Dollars are DERIVED, never
measured.** Unit: core-minutes, `wall_s × ranks ÷ 60`, billed as cores × wall for the whole
clock (`DAFOAM_CHARTER.md` §12).

| arm | predicted (core-min) | cap | actual (core-min) | basis | derived $ |
|---|---|---|---|---|---|
| `F_mp` | **155.70** | **480.0** | **2.067 GROSS, MEASURED** | `ledger.txt`: `wall_s=31 ranks=4` → `31 × 4 ÷ 60 = 2.0667`, recomputed here | **$0.0018** |
| `REF_off` | 60.07 | 190.0 | **0 — the arm never ran** | `STATUS.chain`: `not_run=[REF_off]` | $0 |
| **item** | **215.77** | ceiling **670.0** | **2.067** | | **$0.0018** |

**Gross == cleaned.** The 3600-s stall rule matches nothing: the arm's whole wall clock is 31 s
and the container's is 28 s. **No overrun; the cap was never approached** (0.431 % of 480.0).

**Container overhead, named rather than absorbed:** `container_wall_s=28` of `wall_s=31`, i.e.
**1.867 of 2.067 core-min is container frame**, and the solver's own `ExecutionTime` at the last
step is **19.71 s**. The registered `FRAME_ALLOWANCE_S = 90` was never approached.

**`delivered_cores_mean=[3.5202 n=1 max_nr_throttled=45]`** against 4 requested — the arm got
**88 %** of its cpuset. Recorded, not attributed: one sample is not a contention measurement.

**Estimate-versus-actual (`CLAUDE.md` rule 12; §4c's registered obligation).**
Ratio `actual/predicted` = **`2.067 / 155.70 = 0.0133`** on `F_mp`, **`2.067 / 215.77 = 0.0096`**
on the item.

> **⚠ THIS RATIO IS NOT AN EFFICIENCY AND MUST NOT BE READ AS ONE. THE ARM DID NOT COMPLETE.**
> §4b's corroboration prices `F_mp` at **22 primals**; this arm evaluated **one** — `cl04`'s
> baseline — to its 1,000-iteration `endTime`, and was refused. **The estimate's model was
> exercised on roughly 1/22 of its scope and is therefore UNTESTED.** No misprediction is
> demonstrated in either direction and none is claimed.
>
> **Gap attribution: TRUNCATION, in full.** Not contention (one sample, 88 % delivery, no
> evidence either way). **Not waste** — the 2.067 core-min bought the N-D42 corroboration, the
> 1.316× arithmetic of §1.2, the 0.0356 % agreement of §4.2 and the `F1` structural finding of
> §4.3, all of which are on this record. **Waste: 0.000 core-min, named separately per
> `COMPUTE_BUDGET_CHARTER.md` §6 and never absorbed into the ratio.**
>
> **What is calibrated by this row: nothing about the 155.70 figure.** The forward-useful fact is
> the one that *is* measurable — **an `F_mp` arm that dies at its first primal costs
> ≈ 2.1 core-min, of which ≈ 1.9 is container frame** — and that is what a successor should price
> a first-primal probe at.

**Lineage cost, carried and not written off:** `D6RF2` spent **4.6 core-min** (§4b) buying the
refusal that established `D6RF3-DEF-4` and `D6RF3-DEF-5`. **Lineage total to date:
4.6 + 2.067 = 6.667 core-min, $0.0057 derived.**

The calibration row lands in `docs/COST_CALIBRATION.md` under that file's append rules and the
`CLAUDE.md` rule-10 private-index protocol.

---

## 8. WHAT THIS ITEM MAY NOT CONCLUDE (§10, carried forward and honoured)

* Nothing about `D6R`, which stays `NOT A RESULT`.
* Nothing about optimality — the producing optimisation exited on a non-finite objective and 687
  of its 863 `funcs` rows are non-finite.
* No `CDᵢ(mp)` comparison to a `D6R`/`D6RF`-era value without the source label. **§4.2's number
  carries a stronger caveat than §2a's label anticipated: it is a stdout `CD:` line, not
  `CD_mp_source = FD_BASELINE_PRIMAL` read from the registered artefact**, because that artefact
  does not exist.
* No GCI, no Roache order — no grid family exists.
* No two-row DAFoam verdict on one row — §6.
* No §3 plateau proof — §5, and the bar was not exercised at all.

---

## 9. THE FREEZE, AND THE ONE POST-COMPUTE ADDENDUM ON THE REGISTRATION

**Frozen at `9c079a84`, blob md5 `01079356d794186d21d52e86e1e67907`** — matched in this
invocation.

**⚠ The registration at `HEAD` is no longer that blob, and the record says so rather than
leaving a reader to find it.** `PREREGISTRATION.md` at `HEAD` has md5
`1ec1f87a84c994dabaaa8a845b748da1`. The difference is **`2201b382`, +42 lines, 0 deletions**: the
post-first-compute **§13 addendum** appended at the foot at 22:28:28Z, which strikes line 1's
`DRAFT — NOT A REGISTRATION, NOT FROZEN, NOT ENQUEUED` banner and §11a's dead chain-driver md5.
**Verified by `git diff 9c079a84 HEAD` in this invocation: insertions only, all after §12.6, and
§13.3's assertion that no gate, threshold, band, cap, deadline, label or prediction moves is
consistent with the diff.** That is a lawful dated addendum under `CLAUDE.md` rule 2 and rule 6.

**Grading path:** `d6rf3_grade.py`, md5-pinned in §7 of the registration, with a `freeze_check`
that refuses unless its bytes on disk equal the committed blob at `HEAD`. **It was never run on
this arm** — the chain stopped before grading, and this record is written from the arm's own
artefacts, each cited by path and line.

---

## 10. WHAT A SUCCESSOR IS OWED, AND WHAT IT MAY NOT DO

1. **`REF_off` is unbought at 60.07 core-min** and `G-OFF`/`G-PRICE` cannot read without it.
2. **The `SHIPPED` row is unbought at 155.70 core-min.**
3. **The primal-acceptance question is ESCALATED, not local.** The measured floor is
   `1.316217833e-05`; the effective accept floor is `1.0e-05`; the miss is **1.316×**. Whether
   any of `primalMinResTol`, `primalMinResTolDiff` or the iteration budget may move is a
   threshold decision and is **not a supervisor's act and not a lane's**. **No successor may
   register a looser acceptance rule as a repair for this record's verdict** — that is the gate
   being widened to fit, which Sanaa's 2026-09-04 boundary forbids in terms.
4. **`F1`'s bar must be produced before `F1` can be scored.** A successor that wants `F1`
   resolved must reach `baseline_repeat`, i.e. must get past the acceptance bar first. **`F1` and
   the acceptance question are therefore coupled, and §12.5's preferred design is the reason.**
5. **`X-CDLOG` has still never fired as registered.** §4.2's 0.0356 % is a *different*
   comparison and a successor must not inherit it as though the row had run.

**SUBMISSIONS PARKED.** The four upstream defect classes remain **NOT FILED ANYWHERE**; nothing
in this item is sent, filed, posted or commented anywhere outside this box.
