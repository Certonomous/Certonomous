# PROBE REPORT — the three curriculum capability probes D10, D11, D12

**Lane:** dafoam `lab-lane`. **Supervisor:** `dafoam-supervisor`. **Date:** 2026-08-25.
**Lane→supervisor messaging is one-way; this committed file is this lane's only channel upward.**
**Nothing here was filed, sent, uploaded, registered, posted or commented** (`CLAUDE.md` rule 7).

**COMPUTE SPENT BY THIS LANE: 0.000 core-min.** No container was started. The reason is §1.

---

## 0. HEADLINE — THE TASK WAS ALREADY DONE, AND THE DISPATCHING CENSUS WAS WRONG

I was dispatched to fire D10, D11 and D12 as unarmed probes, on a census stating that
D10, D11 and D12 had **no directory at HEAD**. **That census is false.** At the dispatching
HEAD `94510794`, all three probes were already armed, fired, graded and committed — as
**nine** pre-registered arms, not three — and **all three capabilities are REACHED.**

| capability | final verdict | reachable? |
|---|---|---|
| **D10** thermal objective on the installed image | **`GATE REACHED`** (at D10-P′) | **YES** |
| **D11** MRF / rotating-frame adjoint | **`GATE REACHED`** (at D11-F′) | **YES** |
| **D12** unsteady adjoint, `DAPimpleFoam`, time-averaged objective | **`GATE REACHED`** (first attempt) | **YES** |

**I therefore refused to launch.** Re-firing an answered, frozen, graded pre-registration is
not a probe — it is duplicate spend on a settled question, and it would have put a second,
younger record beside a graded one for the same run. `CLAUDE.md` rule 9: *an instruction is
answered, not merely obeyed.* The brief's own words instruct this check —
*"Check `docs/dafoam/PRIOR_WORK_INVENTORY.md` before proposing anything as new"* — and the
check fired. **Cost constraints being lifted is not a reason to buy an answer twice.**

**What I did instead** is the work that was genuinely outstanding, all of it at zero compute:
the nine-arm synthesis (§2–§4), independent verification that the cited artifacts still exist
and that the cost ledgers reconcile (§5), the repricing the curriculum's own text demands
(§6), and two open items I flag but do not rule on (§7).

---

## 1. Why this file exists when `probes/LANE_REPORT.md` already does

`cases/dafoam/probes/LANE_REPORT.md` is the prior lane's upward report and it is good. **It is
also one arm stale**, and that is a fact of commit order, not a criticism:

- `LANE_REPORT.md` landed at **`52a213ad`** covering **eight** arms.
- **D11-C′** — the component-1 FD step sweep, `GATE REACHED` — landed **afterwards** at
  **`dd053b35`**, with calibration row **`C-75`**.
- `grep` for `D11-C`, `Cprime` or `D11C` in `LANE_REPORT.md` returns **zero** hits.

So the family's single upward synthesis does not name the arm that supplies **the only
demonstrated FD plateau in the whole campaign**. This file supersedes it as the nine-arm
synthesis. **`LANE_REPORT.md` is not edited, not struck and not contradicted** — every number
in it stands; this one adds the ninth arm and the repricing.

---

## 2. THE NINE ARMS — verdicts, spend, and the ledger each number cites

**Toolchain identity, by hash, one image for all nine arms** (`DAFOAM_CHARTER.md` §11 — the
hash is the identity, the version string is not):

> `dafoam/opt-packages` — **`sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc`**

**Verified by me at report time, and stated precisely because the two are usually different
numbers:** `docker inspect` reports this value as **both** `.Id` (the image config digest)
**and** the sole entry of `.RepoDigests`. On this box those coincide, so the identity is
unambiguous either way it is read. **No GPU. All nine arms np=1** (`numberOfSubdomains 1`),
so **core-min = wall-min** on every figure below and the parallel-determinism question does
not arise.

| # | arm | verdict | predicted | **actual** | ratio | run root |
|---|---|---|---|---|---|---|
| 1 | D10 thermal probe | `NOT A RESULT` | 2.50 | **0.4167** | 0.167× | `…/D10` |
| 2 | **D10-P′** plant re-buy | **`GATE REACHED`** | 0.45 | **0.4168** | 0.926× | `…/D10P` |
| 3 | D11 MRF probe | `NOT A RESULT` | 3.50 | **0.7166** | 0.205× | `…/D11` |
| 4 | D11-D′ dictionary re-buy | `NOT A RESULT` | 1.20 | **0.8334** | 0.694× | `…/D11P` |
| 5 | D11-O′ omega re-buy | `NOT A RESULT` | 1.00 | **0.7167** | 0.717× | `…/D11O` |
| 6 | **D11-F′** CLI re-buy | **`GATE REACHED`** | 0.85 | **0.7501** | 0.883× | `…/D11F` |
| 7 | **D12** unsteady probe | **`GATE REACHED`** | 4.00 | **0.8500** | 0.213× | `…/D12` |
| 8 | D12-E′ envelope 2nd point | `NOT A RESULT` *(registered branch)* | 0.75 | **0.6833** | 0.911× | `…/D12E` |
| 9 | **D11-C′** FD step sweep | **`GATE REACHED`** | 3.20 | **3.0337** | 0.948× | `…/D11C` |
| | **TOTAL, NINE ARMS** | **3 of 3 capabilities REACHED** | **17.45** | **8.4173** | **0.482×** | |

Run roots are under `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/`, outside
git per `docs/LOCATIONS.md`. **Every actual above is the `TOTAL_SPENT_CORE_MIN` line of that
arm's own `ledger.txt`, re-read off disk by me at report time** (§5).

**Derived dollars, nine arms:** predicted **$0.014920**, actual **$0.007197** — at
$0.0513/core-h, c7a.4xlarge, **reported-by-owner**. **DERIVED, NOT MEASURED**: the box cannot
read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**The whole nine-arm campaign cost 8.4173 core-min against the curriculum's `≤15 core-min`
envelope for three probes** (`EXPERTISE_CURRICULUM.md` ordering item 3). Nine arms were bought
for less than the three were budgeted.

---

## 3. REACHABLE OR NOT — the evidence, per capability

### D10 — thermal objective: **REACHABLE**, `GATE REACHED`

`DAFunctionWallHeatFlux`, `addToAdjoint: True`, constructs and reaches the adjoint.
`HFX_base = 2.8462869283e+03`; `max |d(HFX)/d(patchV)| = 1.9771502962e+02` over 2 components.

**The named hazard did NOT occur.** The curriculum names *"a 'supported' thermal objective
failing the probe (the ADF NaN precedent)"*. It did not fail: it evaluated, it was finite, and
it carried a derivative eleven-plus orders above any zero floor.

**The first attempt was `NOT A RESULT`, and that is the more instructive half.** D10's plant
was placed on the **initial internal field** of `0/T` — and a converged steady solve is
independent of its initial guess **by construction**. base, plant and clean agreed to the last
digit at `2846.286928273276`; the plant moved `HFX` by **exactly `0.000000e+00`**. The refusal
was **guaranteed before the container started**. Rule 3 refused, correctly, **on its own
author**. D10-P′ moved the plant to the boundary condition and the same case, byte-identical
run script and byte-identical `0.orig/T` then produced a **`2.056667e-02` relative** response.
**The only difference in the world between the `NOT A RESULT` and the `GATE REACHED` is where
the plant sat.**

### D11 — MRF / rotating-frame adjoint: **REACHABLE**, `GATE REACHED`

`TPIn(ω=30) = 1.1859858226e+00` vs `TPIn(ω=0) = 1.1836719785e+00`;
`max |d(TPIn)/d(patchV)| = 2.3058711101e-01`.

**THE NAMED HAZARD DID NOT OCCUR, AND THIS IS THE LOAD-BEARING RESULT OF THE CAMPAIGN.** The
curriculum names *"MRF interface derivatives silently zero — a planted-perturbation control on
the interface is MANDATORY"*. The MRF-active derivative is `2.3058711101e-01`, **eleven orders
above the `1.0e-12` floor**, is not bit-identical to the MRF-inert one, and — the gate that
actually settles it — **agrees with a central finite difference at `h = 1.0e-3 m/s` to
`1.704895e-07` relative**, against a pre-registered band of `5.0e-2`. A linearisation that had
dropped the MRF term from `dR/dW` would disagree with FD; it agrees to seven digits.

**Registered terminology correction, and it should be carried into D11's own prereg:** in this
build **MRF is a cell-zone formulation, not an interface** (`IOMRFZoneListDF`;
`DAResidualSimpleFoam.C:39–40, :144 MRF_.DDt(U_), :183 makeRelative, :199 constrainPressure,
:246 correctBoundaryVelocity`). **There is no MRF interface object to plant on.** The zone's
`omega` is the parameter that switches the whole contribution on and off, and DAFoam reads it
as a scalar **in rad/s, not rpm** (`MRFZoneDF.C:217`). The curriculum's phrasing of the hazard
names an object this build does not have; the probe planted on the zone's `omega` instead,
which is the control that actually discriminates.

**D11-C′ then bought the plateau D11-F′ had not:** `h ∈ [1.0e-5, 1.0e-1]`, **five consecutive
usable steps**, adjoint `−1.3660119098e-04` against plateau FD `−1.3657515496e-04` at the
reference step — **`1.906351e-04` relative**, inside the `5.0e-2` band. **This is the only
demonstrated FD plateau in the campaign**, it retroactively defends D11-F′'s single step, and
it is the arm the prior synthesis does not name.

### D12 — unsteady adjoint: **REACHABLE**, `GATE REACHED` *on the first attempt*

`DAPimpleFoam` under `DAFoamBuilderUnsteady`, `unsteadyAdjoint: {"mode": "timeAccurate",
"reduceIO": True}`, on the upstream DAFoam `Cylinder` tutorial (2,450 cells) — **which is the
curriculum's own D12 case** — at two registered probe reductions (5 steps not 300; cold start
from `0_orig` not the tutorial's spin-up). Time-averaged `CD = 8.9903939104e-02`;
`max |d(obj)/d(shape)| = 1.1622935280e-01` over 4 components.

---

## 4. THE PLANTED CONTROLS — every one read back off disk

Rule 3 is the campaign's spine and it earned its place twice: it **refused** on D10, and it
**passed only after the instrument was fixed**.

| arm | plant | floor | **response** | read-back on disk |
|---|---|---|---|---|
| D10 | `+1.234 K` into `0/T` **internal field** | 1.0e-6 | **`0.000000e+00` — REFUSED** | plant present, solve indifferent to it |
| **D10-P′** | `+1.234 K` on the **wall BC** | 1.0e-6 | **`2.056667e-02`** | `plant/0/T` = `uniform 354.384`; `base`/`clean` = `uniform 353.15` |
| **D11-F′** | MRF zone `omega` 0 → 30 rad/s | 1.0e-6 | **`1.954802e-03`** | `omegaP`+FD stages carry `omega 30.0`; `omega0`/`clean` carry `omega 0.0` |
| **D12** | `shape[0] = 1.234e-03` | 1.0e-9 | **`6.270133e-04`** | `plant/d12_plant.json` carries the planted value |

Every arm also carried a **clean-copy discrimination control on the same quantity that reaches
the verdict** — each reproducing base to **`0.000e+00` relative** (tol `1.0e-12`) — and a
non-emptiness assertion before every loop. All graders ship `--selftest` proving the control
can both **refuse and pass**; D11-C′'s reads **12/12 PASS** at grading time.

**`check_grader_self_blindness.py` was run on D11-C′'s grader and is clean on both probes.
Clean is NOT proof of correctness and is not offered as one** — and the tool's known blind
spot stands: probe B fires on `os.path.join` and is **silent on `pathlib` and f-strings**.

---

## 5. WHAT I VERIFIED MYSELF, RATHER THAN RELAYING

A relayed check is a summary, not a check. Four things I re-ran at report time:

1. **The artifacts still exist.** All **nine** run roots are present under
   `/home/ubuntu/certonomous-runs/CURRICULUM-PROBES-D10-D11-D12/` — `D10 D10P D11 D11C D11F
   D11O D11P D12 D12E` — and **all nine carry a readable `ledger.txt` with a
   `TOTAL_SPENT_CORE_MIN` line.** Every cost figure in §2 is that line, re-read by me.
   **A number whose artifact is gone is not a result; none of these is gone.**
2. **The cost ledgers reconcile, and they reconcile *through* the one disclosed defect.**
   Enforced caps on disk sum to **42.0 core-min** (six arms at 5.0, two at 6.0, one at 8.0
   → 30 + 12 = 42.0 across the eight C-69 arms). `C-69` registers the total of **39.0**.
   **The 3.0 gap is exactly the disclosed D12-E′ launcher defect** — registered cap `3.0`,
   enforced `6.0`, inherited unchanged from D12's launcher. **The independent arithmetic lands
   precisely on the defect the record already confessed**, which is the outcome that should
   most increase confidence in the rest of the ledger. **No verdict is affected** — D12-E′
   spent 0.6833, `0.228×` of even its *registered* cap. **But a cap that is not the cap you
   registered is not a cap**, and the proposed fix (a launcher asserting its own
   `CAP_CORE_MIN` against the value its prereg names) remains **PROPOSED, NOT ADOPTED** — a
   launcher idiom across a family is not a lane's call (rule 9).
3. **The toolchain hash**, re-resolved from `docker inspect` — see §2.
4. **Commit order**, establishing that D11-C′ post-dates the prior synthesis (§1).

**No `CAP_CORE_MIN` guard fired on any of the nine arms**, so rule 12's *"an overrun stops the
run"* was never engaged and no runaway-guard report is owed to the supervisor.

---

## 6. THE REPRICING — the curriculum's own text demands it

### D12 — `NEEDS COSTING` is **ANSWERED**

From a **two-point measured wall fit**, both points the same case with a byte-identical run
script and only `endTime` changed (29 s at 5 steps, 39 s at 10):

> `wall(n) = 19.0 + 2.000·n` seconds per `compute_totals` invocation

A **300-step window** costs **10.32 core-min per major**, ≈ **11.3** with one line-search
primal. A 10–20-major D12 with spin-up, the FD verification and δ_repeat lands at

> **127.6 – 240.5 core-min = $0.109 – $0.206 DERIVED, not measured**

against the curriculum's **`~1,000–3,000 core-min, $0.9–2.6`**. **The curriculum estimate is
4–23× HIGH for this mesh and this window.**

**Per-step anchors — the first this lab holds for an unsteady adjoint** (2,450 cells, np=1):
primal **0.195 s/step**; unsteady adjoint **2.158 s/step**, ≈ **11× the primal**; `dRdWTPC`
assembly ≈ **3.92 s** at 317 colours; python/IDWarp startup ≈ **7.7 s**.

**δ_repeat on the time-average is NOT measured and must not be assumed.** The curriculum names
limit-cycle phase noise as *"N-D15's lesson at its worst"* and requires δ_repeat measured
first. **This probe did not measure it. D12's own pre-registration must buy it before any FD
step is sized**, because a step sized against an unmeasured repeat noise is a step sized
against nothing.

### D12's memory envelope — **an alarm was RAISED and then RETRACTED before publication**

D12's single point extrapolated to `0.1065 GiB/step`, hence **~32 GiB at a 300-step window —
above this 30 GiB box.** D12-E′ was pre-registered **with the fit frozen in advance** to buy
the second point, and returned **`per_step_GiB = −0.000262` — negative**, firing the
registered `NOT A RESULT` branch. ΔR is `0.532536 GiB` at 5 steps and `0.531223` at 10:
**doubling the window did not measurably change resident memory.** So the 0.53 GiB is
dominated by the **fixed** `dRdWTPC` term and **the 32 GiB alarm is NOT SUPPORTED.**

**Equally, "the envelope is flat" is NOT established** and must not be reported as though it
were. The 1.3 MiB difference is **below the run-to-run RSS noise scale** — the two *primal*
figures alone differ by 4.9 MiB — and with **one run per point** that floor is unmeasured. A
non-positive slope means either `reduceIO: True` is not holding per-step state in RAM, or the
allocator is not returning it to `ru_maxrss`, and **this probe cannot tell those apart.**
Disk is settled and tiny: the adjoint adds **177,009 B ≈ 0.169 MiB** over 5 steps.
**D12's memory question must be closed by D12's own prereg before a 300-step window is
committed to.**

### D11 — stays **`UNPRICED`**, and the reason is registered rather than glossed

The curriculum defers **case selection** to after the probe, and D11's case is **not
selected**. The probe's substrate — a 720-cell 2D channel with an MRF zone in a through-flow —
is **a different case class** from the ducted-fan and swirl-passage candidates. Pricing across
case classes is forbidden by `COMPUTE_BUDGET_CHARTER.md:375-395` and by the curriculum's own
§2 estimation rule. **A price invented here would be a fabrication wearing a decimal point.**

**What the probes DID deliver toward that costing — the lab's first anchors in the MRF case
class** (720 cells, np=1, MRF-active `DASimpleFoam`): primal **0.1167 core-min**;
primal + adjoint **0.2000**; **adjoint increment ≈ 0.083 core-min**.

**And a NAMED BLOCKER ON CASE SELECTION, which is worth more than a price would have been:**
a **300 rad/s** zone **STALLS** the steady SIMPLE primal — continuity plateauing at ≈ `2.5e-4`,
never reaching `primalMinResTol 1e-10` inside 2000 iterations, so DAFoam raises
`AnalysisError: Primal solution failed!`. **It stalls; it does not diverge and it does not
NaN.** At `r ≈ 0.02 m` a 300 rad/s zone drives ≈ 6 m/s of tangential motion against a 10 m/s
through-flow across an abrupt zone boundary. **That is the substrate refusing the magnitude,
not the capability being absent.** Carried forward as a constraint on D11's case:
**a steady MRF-active `DASimpleFoam` substrate must have a zone physically appropriate to a
rotating frame, or the case must be unsteady.**

---

## 7. TWO OPEN ITEMS I FLAG AND DO NOT RULE ON

**(a) The curriculum still reads as though the probes were pending.** `EXPERTISE_CURRICULUM.md`
Tier 4/5 rows still carry **`PROBE FIRST`** for D10, D11 and D12, **`UNPRICED until probe`**
for D11, and **`NEEDS COSTING after probe`** for D12. All three prerequisites are **discharged**
and D12 is **priced** — but a reader of the curriculum alone cannot tell. Sanaa's §7 ratification
requires *"formal .md updates"*. **I did not amend it.** The curriculum is a **ratified**
document, and D12's row carries a **cost figure** — moving a cost row in a ratified curriculum
is not a lane's call (rule 9), and the file's own Amendment 1 §A1.4 sets the precedent that an
amendment there changes *"no gate, no threshold, no cap, no label, no cost figure."*
**Recommended: a dated addendum recording the three discharges and D12's measured reprice,
struck through nothing, authored at the supervisor's level.**

**(b) A charter-reading question on the bright line, for the supervisor, not for me.**
`DAFOAM_CHARTER.md` §2: *"No DAFoam gradient enters a record, a report or an optimisation
without a finite-difference table beside it."* Of the three reached gates:

| capability | gradient reported | FD table beside it? |
|---|---|---|
| D11 | `d(TPIn)/d(patchV)` | **YES** — `1.704895e-07` (F′), plus D11-C′'s five-step plateau |
| D10 | `max \|d(HFX)/d(patchV)\| = 1.9771502962e+02` | **NO** |
| D12 | `max \|d(obj)/d(shape)\| = 1.1622935280e-01` | **NO** |

**The mitigation is real and is on the page:** both D10-P′ §4 and D12 §4 explicitly disclaim
*"nothing about the correctness, accuracy, FD agreement or sign"* of the number, so no gradient
is **claimed as a result** — the value is reported as a reachability datum only. **Whether §2's
"enters a record" is satisfied by an explicit non-claim, or requires the table regardless, is a
charter reading**, and reading a charter clause is above a lane. **I flag it; I do not settle
it.** If the stricter reading governs, the repair is cheap — D10 and D12 each need one FD pair
on the component already computed, on the order of the arms in §2.

---

## 8. COST CALIBRATION — why no new row is owed

**This lane spent 0.000 core-min of compute.** The nine arms are **already fully calibrated**:
**`C-69`** covers the eight (predicted 14.25, actual 5.3836, ratio 0.3778×, waste 2.6834 named
separately) and **`C-75`** covers D11-C′ (predicted 3.2, actual 3.0337, ratio 0.948×, waste
0.0). **Appending a row for a records action would double-count nine arms in the ledger.**

The precedent is this family's own and is explicit — `EXPERTISE_CURRICULUM.md` Amendment 1
§A1.4: *"Zero compute: a records action at 0.000 core-min, so no calibration row is owed."*

**The nine-arm rollup, for the supervisor's convenience and NOT as a new ledger row:**
predicted **17.45**, actual **8.4173**, **0.482×**, **$0.007197 DERIVED, not measured**.

**THE WASTE, RESTATED BECAUSE IT IS THE HEADLINE AND MUST NOT BE ABSORBED INTO THAT RATIO**
(`COMPUTE_BUDGET_CHARTER.md` §6): **2.6834 core-min — 31.9 % of the nine-arm spend — produced
no graded quantity, and all of it was the prior lane's own instrument defects**: D10 **0.4167**
(plant on an initial field a converged steady solve ignores by construction); D11 **0.7166**
(`MRFProperties` in OpenFOAM's named-zone layout when `IOMRFZoneListDF` wants a single
top-level `MRF` sub-dictionary); D11-D′ **0.8334** (the 300 rad/s stall); D11-O′ **0.7167**
(`argparse` reading `-1.0e-3` as an option flag).

**Contention is NOT claimed to be zero.** Peer lanes were live throughout and **no uncontended
control was run**, so residual contention in these figures is **UNMEASURED**. All arms carried
`--bind-to none` via a before-first-compute amendment, which avoided the measured 3.99× CPU-0
collision — avoiding a known mechanism is not the same as measuring the residual.

---

## 9. THE THREE TRANSFERABLE LESSONS

1. **A DISTINCT EXIT CODE BESIDE A CLUSTER OF OTHERS IS A DISTINCT FINDING.** `fdm` exited
   **`2`** while its four siblings exited **`1`**, in **all three** D11 attempts. `rc=1` is
   DAFoam's `AnalysisError`; `rc=2` is `argparse`. That distinct code sat unexamined beside the
   cluster and was read as part of the same failure — **surviving two further re-buys and
   costing 1.5501 of the 2.6834 core-min of waste.** The most expensive single mistake in the
   campaign was **not a defect but a triage failure.**
2. **A GATE WHOSE ANTECEDENT CAN BE TRIPPED BY THE INSTRUMENT THAT TESTS IT IS NOT MEASURING
   WHAT ITS LABEL SAYS.** D11's frozen §4 mapped *"`MRFProperties` rejected → `BLOCKED`
   (capability absent from this build)"*. The antecedent fired — for a reason the mapping never
   contemplated. **Reporting `BLOCKED` would have been FALSE**, and would have told D11's
   costing that this box cannot do MRF adjoints when the capability had never been reached and
   so had never been shown absent. **`BLOCKED` requires reaching a capability and finding it
   gone.** Every D11 successor now carries: *a fatal originating in this lane's own files is
   `NOT A RESULT`, never `BLOCKED`.*
3. **A PREDICTION ANCHORED ON THE SAME STAGES OF THE SAME CASE ON THE SAME BOX LANDS WITHIN
   ~30 %, AND USUALLY WITHIN 12 %.** The four re-buy predictions were *measured* rather than
   guessed — ratios **0.926 / 0.694 / 0.717 / 0.883 / 0.911 / 0.948**. The two guessed
   predictions were the outliers — D10 **0.167×**, D12 **0.213×**. **Corollary from D11-C′:
   a mesh-build figure carried across probes is the least transferable line in a DAFoam
   per-stage prediction** (predicted 0.22, measured 0.0167 — essentially the whole 5.2 % gap),
   **while the per-container solver figures transferred to 1.6 %.**

---

## 10. WHAT I COULD NOT VERIFY

- **I did not re-run any solve.** Every physical measurement in §2–§4 and §6 is read from the
  nine committed `RESULTS.md` and their `ledger.txt`. **I verified the artifacts exist, that
  the cost arithmetic reconciles, and that the toolchain hash resolves** (§5) — **I did not
  independently reproduce a single gradient, plant response or convergence claim.**
- **δ_repeat on D12's time-average: NOT MEASURED**, by this lane or any prior one.
- **D12's memory envelope: OPEN.** Not 32 GiB, and not shown flat.
- **Residual contention: UNMEASURED** — no uncontended control exists.
- **`check_grader_self_blindness.py` clean is not proof of correctness**, and it is blind to
  `pathlib` and f-strings.
- **The §7(b) charter reading is unsettled** and is the supervisor's to make.

**SUBMISSIONS ARE PARKED. Nothing in this file has been sent, filed, uploaded, registered,
posted or commented, and sending is Sanaa's decision alone.**
