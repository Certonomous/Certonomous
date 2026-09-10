# RC3 — WU-FROZENK CEILING-GATE VALIDATION: MAKING THE CEILING GATE AN INSTRUMENT THAT CAN PASS THE TRUTH

> # STATUS: **DRAFT / UNFROZEN.**
>
> **NOTHING MAY RUN AGAINST THIS DOCUMENT.** No solve, no scoring pass, no queue
> entry, no staging into a run root. This registration is **NOT FROZEN**: its
> gates, thresholds, cap and label are **OPEN** and amendable in place under
> standing rule 2's pre-compute clause.
>
> **THE FREEZE IS THE SUPERVISOR'S ACT, NOT A LANE'S.** It happens only after the
> closure-supervisor's **personal** `SUPERVISION_CHARTER.md` §3 check-1 — the
> measurement instruments read as measurement scripts, as diffs, personally, not
> relayed — and §3 check-4 (pre-registration **committed** before compute). Standing
> rule 2 fixes the grading path **at the pre-registration commit**, and **this
> item's instruments do not exist yet**, so the freeze is the later commit that
> carries **this document AND its instruments together**. Any run before that
> commit is unregistered and its output is **NOT A RESULT**.
>
> **THIS COMMIT IS NOT THE FREEZE.** It lands the draft so it is reviewable.
>
> **Zero solver compute produced this document.** Nothing has been sent, filed,
> uploaded, registered, posted or commented (standing rules 2, 7). No frozen file
> was edited (standing rule 6). No sha is pinned by this document.

Predecessor: `Wu2018_PIML_RF/aposteriori_frozenk` — `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md`, **NOT A RESULT** (ceiling gate failed on both arms and all three cases; registered falsifier fired). Its predecessor in turn is `Wu2018_PIML_RF/aposteriori` (**NOT A RESULT**, ceiling gate failed on all three cases).

**Rung:** `RC3_wu_ceiling_gate_validation`
**Team:** closure
**Class:** **GATE-VALIDATION REGISTRATION** — the product is a *calibrated instrument*, not a model score.
**Label:** `RC3` (closure; Wu2018 PIML-RF a-posteriori chain; instrument calibration)
**Status:** **DRAFT / UNFROZEN.** `prereg_commit:` = `PENDING_SUPERVISOR_FREEZE`.
**Drafted:** 2026-09-10, by a closure lane on the closure-supervisor's dispatch.
**Discharges:** the `Wu-frozenk` **NEEDS-SUCCESSOR** row owed by
`docs/closure/CLOSURE_2BC_EXHAUSTION_REAUDIT.md` (commit `3c6eb5da`), Row 6.

---

## 1. The defect, re-derived AT SOURCE at drafting — not quoted from the board

The re-audit is **not** the authority for anything in this section. Every claim
below was re-derived by reading the case files themselves, and each names its
file, its line and its number.

### 1.1 The ceiling is DEFINED as the apparatus maximum

`cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori/PREREGISTRATION.md:126`,
verbatim, in the configuration table:

> `| **TRUTH** | `b_LES - b_RANS` from the shipped `tauij_LES`, `k_LES` | the **ceiling**: the best any perfect anisotropy predictor could do through this injection path |`

So the TRUTH row is, by its own registration, **the maximum this apparatus can
attain**. Nothing in the experiment can beat it.

### 1.2 The gate criterion is a FIXED ABSOLUTE BAR applied to that maximum

Two lanes registered two bars, both as fixed percentages, neither derived from a
measurement of the apparatus:

- `aposteriori/PREREGISTRATION.md:134` — *"If TRUTH does not cut `U_rms` by at
  least **50%** relative to BASE on a case, that case is reported NOT A RESULT"*,
  and at **`:138`**, the whole of the threshold's provenance: *"The 50% figure is
  registered now."* No derivation, no attainability measurement.
- `aposteriori_frozenk/PREREGISTRATION.md:110` — *"**Registered: TRUTH must cut
  `U_rms` by >= 30% relative to NULL.**"* The lowering to 30% is argued at
  `:111–117` **by analogy** to Schmelzer's two-correction result
  (`eps(U)/eps(U_0) = 0.0017`), i.e. from a *different* configuration on a
  *different* case. It is not a measurement of what the b-only path can attain
  here.

### 1.3 The measured consequence: the bar sits ABOVE the attainable maximum

`aposteriori_frozenk/RESULTS.md:20–25`, the H0 table — **six of six TRUTH rows
FAIL**:

| case | arm | NULL `U_rms` | TRUTH `U_rms` | change | 30% gate | 50% gate | source line |
|---|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | S | 0.1991 | 0.2109 | **+5.9%** | FAIL | FAIL | `RESULTS.md:20` |
| `AR_1_Ret_360` | L | 0.3686 | 0.2869 | **−22.2%** | FAIL | FAIL | `RESULTS.md:21` |
| `AR_3_Ret_360` | S | 0.1880 | 0.1941 | **+3.2%** | FAIL | FAIL | `RESULTS.md:22` |
| `AR_3_Ret_360` | L | 0.3556 | 0.2530 | **−28.9%** | FAIL | FAIL | `RESULTS.md:23` |
| `CBFS13700` | S | 0.0516 | 0.1085 | **+110.2%** | FAIL | FAIL | `RESULTS.md:24` |
| `CBFS13700` | L | 0.0498 | 0.1179 | **+136.6%** | FAIL | FAIL | `RESULTS.md:25` |

**The load-bearing number is −28.9%** (`RESULTS.md:23`, `AR_3_Ret_360` arm L).
Arm L freezes `k` at `k_LES`, so that row carries LES truth in **two** channels —
the injected anisotropy *and* the turbulent kinetic energy — and is therefore the
most oracular configuration the frozenk lane ever built. Its best achievement is
a **28.9%** cut against a bar of **30%**: the registered criterion sits **1.1
percentage points above the most favourable row the apparatus has ever
produced**.

**That is the defect, stated exactly.** The gate's reject region contains its own
reference. An instrument whose criterion rejects the known-correct input is not
calibrated, and a `NOT A RESULT` it emits carries **no information about any
model** — only about the criterion. The frozenk lane's own conclusion
(`RESULTS.md:11–13`, *"It still fails. The k-collapse explanation was
incomplete"*) is a true statement about `k`-collapse and is **not** withdrawn by
this item; what RC3 says is that the *gate* was never entitled to be the
instrument that established it.

**Honest caveat, registered so it is not discovered later.** Arm L is not an exact
oracle. The solver realises `b_total = b_linear(current iterate) + b^Delta`
(`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:83`, *"not equal to the
forest's `b`. That is the SpaRTA propagation form"*), so injecting
`b_LES − b_RANS` does not reconstruct `b_LES` exactly, and `omega` is frozen at
its SST value so `nu_t` is not the LES eddy viscosity. Arm L is therefore the
**best available** oracle, not the **exact** one. §3's C4 configuration exists
precisely to close that gap.

### 1.4 A second, independent defect: the gate is PROSE-ONLY

`aposteriori_frozenk/score.py` is **180 lines** and contains, by direct count of
the file:

- occurrences of `ceiling`: **0**
- occurrences of `sys.exit`: **0**
- occurrences of `assert`: **0**
- occurrences of `PLANT`: **0**

The script computes `U_rms` and **prints a table**. The 30% comparison is
performed by a human reading `RESULTS.md` against that table. There is therefore
**no executable gate, no executable refusal, and no planted-zero control anywhere
in the scoring path** — standing rule 3 is not satisfied by the predecessor at
all. A ceiling number produced by a reader never shown able to see a non-zero is
not evidence, and this reader was never shown that.

### 1.5 What is NOT claimed

- RC3 does **not** claim the Wu forest is good. No model verdict is taken here.
- RC3 does **not** withdraw the frozenk `NOT A RESULT`. That label stands; RC3
  determines whether it stands for an *instrument* reason or a *physics* reason.
- RC3 does **not** edit `aposteriori/PREREGISTRATION.md`,
  `aposteriori_frozenk/PREREGISTRATION.md`, `score.py`, or any other file in the
  Wu chain, at any line, for any reason (standing rule 6). RC3 is a **successor**,
  and its instruments are new modules in this directory.

---

## 2. What RC3 is, as ONE capped item

**One product: a ceiling gate that has been shown, on this apparatus, to ADMIT a
reference carrying the truth and to REJECT a reference carrying no information.**

That is the two-direction control doctrine (standing rule 3) applied to the gate
itself. A gate validated in only the admitting direction passes everything; a gate
validated in only the rejecting direction is the one the Wu chain already has.

**A gate that cannot pass the truth is FALSIFIED and is WITHDRAWN. It is never
tuned to fit.** This is registered here, before compute, and §7 states it as the
item's falsifier.

---

## 3. The C-ladder — the configurations, fixed here

One case family, five injected configurations plus one planted-negative. All
within the **b-only** family, because b-only is what the Wu forest supplies and
the apparatus under calibration is *"b-only injection into
`kOmegaSSTCorrected`"*. The auxiliary channels (`k`, `omega`) are **apparatus**
channels, not model channels, so giving them oracle information measures the
apparatus, not the model.

| tag | injected `b^Delta` | `k` treatment | purpose | precedent on disk |
|---|---|---|---|---|
| **C0 NULL** | 0 | transported | the reference every cut is measured against | `aposteriori_frozenk` `S_null` / `L_null` |
| **C1** | `b_LES − b_RANS` | transported | the `aposteriori` lane's TRUTH row | `aposteriori/RESULTS.md` TRUTH rows |
| **C2** | `b_LES − b_RANS` | frozen at `k_base` | the frozenk lane's arm S | `aposteriori_frozenk` `S_truth` |
| **C3** | `b_LES − b_RANS` | frozen at `k_LES` | the frozenk lane's arm L — the best oracle built so far | `aposteriori_frozenk` `L_truth` |
| **C4 EXACT-STRESS** | see §3.1 | frozen at `k_LES` | **the strict apparatus maximum** | **none — new** |
| **CX SCRAMBLED** | see §3.2 | frozen at `k_LES` | **the planted negative** | **none — new** |

Cases: `AR_1_Ret_360`, `AR_3_Ret_360`, `CBFS13700`. `NASA_2DWMH` remains
**BLOCKED** on the missing `libfrozenIncompressibleTurbulenceModels.so` /
`AugmentedkOmegaSST`, exactly as established at
`aposteriori/PREREGISTRATION.md` sec. 2; RC3 does not attempt it and does not
substitute a non-comparable baseline for it.

### 3.1 C4 EXACT-STRESS — the configuration that makes the ceiling measurable

The question the ladder must answer is: **if the momentum equation is handed the
exact LES Reynolds stress, does the velocity field become the LES velocity
field?** If yes, the apparatus is sound and any shortfall in C1–C3 is a genuine
physical property of a b-only correction. If no, the apparatus cannot express the
right answer at all and no ceiling gate built on it can certify anything.

Because the solver recomputes `b_linear` from the current strain rate each
iteration, `b^Delta` cannot be set once to reconstruct `b_LES`. **Registered
method:** an outer fixed-point loop. At outer pass *m*, set
`b^Delta_(m) = b_LES − b_linear(U_(m−1))` using `b_linear` read from the previous
pass's converged field, with `k` frozen at `k_LES`, and re-solve.

**Registered stopping and abort, fixed now:**
- **N_outer = 5** passes maximum.
- Contraction criterion: `||b^Delta_(m) − b^Delta_(m−1)||_2 / ||b^Delta_(m−1)||_2`
  must fall monotonically across passes 2..5 and reach **≤ 1e-2**.
- **If it does not, the C4 row is `NOT A RESULT`**, the fact is printed with all
  five ratios, and the ceiling is read from the best of C1–C3 with C4 recorded as
  unavailable. N_outer is **not** raised, and no relaxation of the fixed point is
  introduced to reach it.

### 3.2 CX SCRAMBLED — the planted negative for the gate

`b^Delta` is the C3 field with its **cell values randomly permuted** under a
registered seed (`numpy.random.default_rng(20260910)`, one permutation of the cell
index array, applied identically to all six tensor components so each cell keeps a
physically realisable tensor and only its *location* is destroyed). The
distribution of the injected tensor is preserved **exactly**; its spatial
structure is destroyed **completely**.

This is the planted negative required by §5's V1b. It is not a model, it cannot be
gamed by a modelling choice, and it is generated from the truth field itself, so
it cannot be accused of being a straw comparator.

---

## 4. Metrics — unchanged from the predecessors, so the rows stay comparable

Per `_common/BASELINES.md` §1, on the same cells, computed by the same reader:

- `U_rms` = `sqrt(mean(|U − U_LES|^2)) / mean(|U_LES|)`; `U_mae` likewise.
- RMS `div(U)` normalised by the field's own gradient scale. **Registered, and
  carried over verbatim from `aposteriori/PREREGISTRATION.md` §4: a solved field
  that does not satisfy continuity to ≤ 1e-4 is reported as NOT CONVERGED,
  whatever its `U_rms`.**
- `k/k_base` and `k/k_LES` on every row.
- Realisability of the converged `b_total` as the fraction outside the
  barycentric triangle.
- Ducts: in-plane secondary-flow magnitude as % of bulk (DNS `AR_1_Ret_360`
  **1.508%**, `AR_3_Ret_360` **1.411%**). CBFS: `x_reatt` against LES **4.241**.

---

## 5. GATES, THRESHOLDS AND VERDICTS — the four things rule 2 freezes (1 of 4: the gates)

### V0 — APPARATUS ADMISSIBILITY. Runs FIRST; RC3 stops if it fails.

> **The exact-stress configuration C4 must cut `U_rms` by ≥ 80% relative to C0
> NULL, on ≥ 2 of the 3 in-scope cases.**

**Threshold provenance — derived from an independent prior measurement, NOT from
anything this campaign will produce.** The same solver family
(`kOmegaSSTCorrected`, `sdk/openfoam/sparta`) with a two-channel truth injection
has already been measured on this box at
`/home/ubuntu/closure-data/aposteriori/kaandorp/frozen_R_AR_1_Ret_360.json`:
`U_rms` = **0.003406514937336865** on `AR_1_Ret_360`, against that case's NULL
`U_rms` = **0.19873618541903595** (`.../results.json`, run key
`AR_1_Ret_360__NULL`) — a **98.3%** cut. The 80% bar carries **18.3 percentage
points of margin below a measured value** and is registered now. **It is never
moved.**

### V1 — TWO-DIRECTION GATE VALIDATION. The item's actual product.

The candidate ceiling criterion is the statement *"the ceiling row for a case is
the row that cuts `U_rms` by ≥ 80% relative to NULL"*. It is judged **CALIBRATED**
only if **both** directions hold on the **same** ≥ 2 of 3 cases:

- **V1a ADMISSION.** The criterion returns PASS on the **C4 EXACT-STRESS** row.
- **V1b REJECTION.** The criterion returns FAIL on the **CX SCRAMBLED** row.

Both are required. Either alone is not a validation.

### V2 — CEILING PUBLICATION. Only reached if V0 and V1 both hold.

The **b-only ceiling** is published per case as `max(cut over C1, C2, C3)`, **as a
number with its configuration named**, and the predecessors' fixed 30% and 50%
bars are recorded as **FALSIFIED BY MEASUREMENT** for every case whose measured
b-only ceiling falls below them. No bar is re-fitted; the fixed-percentage form is
replaced by the measured-ceiling form.

### V3 — READER CONTROL. See §6. A failed control makes the whole item `NOT A RESULT`.

### 5.1 Thresholds, in one table (2 of 4: the thresholds)

| gate | threshold | provenance |
|---|---|---|
| **V0** | C4 cut ≥ **80%** vs NULL, on ≥ **2 of 3** cases | 98.3% measured on the same solver family, `frozen_R_AR_1_Ret_360.json` + `results.json` |
| **V1a** | criterion PASSes C4 on those same ≥ 2 of 3 | definitional: the instrument must admit its reference |
| **V1b** | criterion FAILs CX on those same ≥ 2 of 3 | definitional: the instrument must reject a structureless input |
| **C4 fixed point** | contraction ratio ≤ **1e-2** by pass 5, monotone over passes 2–5 | registered §3.1; abort, never extend |
| **continuity** | RMS `div(U)` / gradient scale ≤ **1e-4** or the row is NOT CONVERGED | carried verbatim from `aposteriori/PREREGISTRATION.md` §4 |
| **V3 plant** | recomputed `U_rms` must move by > **1e-12** when `PLANT = 1.234e-03` is written into `U`, and be **bitwise identical** when it is not | standing rule 3; `PLANT` value matches the lab's established comparators |

### 5.2 The verdict ladder — fixed vocabulary only

- **PASS** — V0 holds, V1a and V1b both hold on the same ≥ 2 of 3 cases, V3
  holds. The ceiling gate is a **validated instrument**; V2's measured ceilings
  are published and the Wu chain acquires a gate that can certify.
- **GATE REACHED** — V0 holds and V1a holds, but V1b fails (the criterion also
  admits SCRAMBLED). The apparatus is sound but the *criterion form* does not
  discriminate; the criterion is withdrawn under §7 and the apparatus finding is
  reported on its own.
- **GATE FAIL** — V0 fails: the exact LES Reynolds stress does **not** cut `U_rms`
  by ≥ 80% relative to NULL on ≥ 2 of 3 cases. **The apparatus cannot express the
  correct answer**, the ceiling gate is not repairable by re-registration, and
  that is the headline finding.
- **NOT A RESULT** — V3's control fails in either direction; or any scored row
  fails §8's strict-completion clause; or the C4 fixed point fails to contract on
  ≥ 2 of 3 cases (in which case the item has no reference to validate against).
- **BLOCKED** — `NASA_2DWMH`, per `aposteriori/PREREGISTRATION.md` sec. 2; and any
  case whose benchmark fields are not on disk at run time.
- **PENDING** — the display state until the item runs. It is **never** used to
  soften a `GATE FAIL`.

---

## 6. The planted-zero control — standing rule 3, two directions, on REAL fields

**A zero from a reader not shown able to see a non-zero is not evidence.** The
predecessor's `score.py` has no control at all (§1.4). RC3's scorer refuses to
produce a number until it has demonstrated both directions **on a field written by
`simpleFoam` on this box**, never on a string literal — a control defined in terms
of the thing it controls is not a control.

**Direction A — can the reader SEE a non-zero?**
Copy a real converged `U` field from a scored case directory. Add
`PLANT = 1.234e-03` to the value at cell index `0` and at cell index `n // 2`.
Write it to disk. Re-read it through the **same** reader the scorer uses
(`_common/of_read.read_field`) and recompute `U_rms`. **The recomputed value must
differ from the unplanted value by more than `1e-12`.** If it does not, the
instrument **refuses: `sys.exit(2)`**.

**Direction B — does the reader see a genuine zero AS zero?**
Re-read the unmodified copy through the same reader and recompute `U_rms`. **It
must be bitwise identical to the original.** If it is not, the instrument
**refuses: `sys.exit(2)`**.

**Both directions run on every scoring pass, not only under `--selftest`.** A
control that runs only in the test harness certifies the test harness.

### 6.1 NO `ast.Assert` CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE

**Binding on every instrument RC3 specifies** (L-332 / D476 §31.3): `assert`
statements are removed by `python3 -O`, so a guard written as an `assert` is a
guard that is not there in half the ways the file can be run.

- **Every refusal, guard, control and gate in RC3's instruments is a
  `sys.exit(2)` or a `raise`.** Not one is an `assert`.
- **`--selftest` must exit 0 under `python3` AND under `python3 -O`**, with
  `__pycache__` cleared before each invocation (a stale `.pyc` inverts mutation
  tests: the clean control fails and the mutated case passes, and
  `PYTHONDONTWRITEBYTECODE` does not fix it).
- **The selftest plants a violation of each gate and requires each to be caught**,
  under both interpreter modes.

**This defect is present in the predecessor chain and is re-derived at source
here, so the replacement is not theoretical.** `assert` statements carrying guards
exist at `Kaandorp2020_TBRF/aposteriori/frozen_R.py:79`
(`assert "libspartaTurbulenceModels" in s` — the L-221 libs guard, which vanishes
under `-O` and lets the solve run without the model, silently),
`setup_case.py:115`, `setup_case.py:124`, `run_lane.py:153`, `run_lane.py:273`.
**RC3 reuses none of these call sites and re-implements each guard as
`sys.exit(2)` in its own module.**

---

## 7. THE REGISTERED FALSIFIER (3 of 4: the label is §"Label" above; this is what withdraws the item)

> **If V0 fails — if the exact LES Reynolds stress, supplied to this solver on
> these meshes, does NOT cut `U_rms` by ≥ 80% relative to NULL on ≥ 2 of the 3
> in-scope cases — then the ceiling gate is NOT repairable by re-registration,
> because the apparatus itself cannot express the correct answer.**
>
> **RC3 is then reported `GATE FAIL` and WITHDRAWN as a gate-repair item.**
>
> **The 80% threshold is NOT lowered. No further oracle channel is added to reach
> it. No case is dropped from the denominator. No margin is renegotiated.** The
> finding recorded is that the Wu a-posteriori apparatus is instrument-limited, and
> the Wu chain's standing `NOT A RESULT` labels are then correct for an apparatus
> reason that is finally named.

**Second falsifier — the criterion form.** If V1b fails, i.e. the candidate
criterion **admits the SCRAMBLED-truth row**, then the criterion form is
falsified: a gate that passes a structureless tensor passes anything. The
criterion is **WITHDRAWN**, not re-tuned, and RC3 returns `GATE REACHED` with the
apparatus finding standing alone.

**Third falsifier — the ladder itself.** If the C4 fixed point fails to contract
on ≥ 2 of 3 cases, RC3 has no reference against which to validate anything and
returns `NOT A RESULT`. `N_outer` is not raised above 5.

---

## 8. Strict completion — standing rule 4, adapted and stated in full

The thermal family's field list does not apply: these are incompressible closure
cases with no `T`. **The adapted clause, registered here:**

A scored run is **COMPLETE** only if **all** of the following hold. Any one
failing makes the row `NOT A RESULT`; the instrument **refuses (`sys.exit(2)`)
rather than degrading**.

1. **`rc = 0`** from the solver invocation.
2. An **`End`** line in the solver log.
3. **Termination is registered:** either the last written time equals the
   registered `endTime`, **or** the log carries OpenFOAM's `residualControl`
   convergence line and the last written time equals the iteration it names.
   *(These cases stop on `residualControl`, so the thermal family's bare
   "last time == endTime" does not apply verbatim; both branches are registered
   now, before compute.)*
4. **Fields present at the last written time:** `U`, `p`, `k`, `omega`, `nut`,
   `phi`.
5. **Iteration accounting:** the count of `ExecutionTime` lines equals the number
   of steps the log reports having taken.
6. **AGE GUARD — every field at the last written time is NEWER than the case's own
   `0/U`.** `0/U` is touched last at case build, so it dates the run that was
   allowed to produce the answer. A field older than it came from somewhere else.
7. **The build guard refuses a case directory in which `0` or any numeric time
   directory already exists.** A rebuilt case starts from a clean copy or the item
   stops.
8. **Continuity**: RMS `div(U)` / gradient scale ≤ **1e-4**, else the row is
   reported NOT CONVERGED whatever its `U_rms` (§4).

---

## 9. ANTI-GAMING REGISTER — `docs/standards/NONCONVERGENCE_STANDARD.md`, the L0–L7 ladder

Sanaa's clause, verbatim from §1 of that standard:

> *"ANTI-GAMING (absolute): convergence aids (L1-L5) tune freely, disclosed.
> Answer-changing choices (model, scheme class, formulation) are never selected by
> agreement with the reference. Converged-but-wrong = NOT HELD with diagnosis,
> never a parameter hunt. Frozen gates never edited post-compute."*

**FIXED HERE, BEFORE COMPUTE, AND NEVER SELECTED BY AGREEMENT WITH THE
REFERENCE:**

| what | fixed value | ladder level |
|---|---|---|
| turbulence model | `kOmegaSSTCorrected`, `sdk/openfoam/sparta` — the same solver the predecessors ran; **no new solver is written** | **L6 — answer-changing, FIXED** |
| formulation | steady, `simpleFoam`, serial (ranks = 1) | **L7 — answer-changing, FIXED** |
| scheme class | the shipped benchmark `fvSchemes` for each case, unmodified | **L3 class — answer-changing, FIXED** |
| `bScale` (blending) | **1.0**, no blending, no clipping, in every scored configuration | **answer-changing, FIXED** |
| the C-ladder configuration set | C0, C1, C2, C3, C4, CX exactly as §3 defines them — **no configuration is added, dropped or re-tagged after compute begins** | fixed |
| the V0 threshold | **80%**, derived §5 from an independent prior measurement | fixed |
| the case set | `AR_1_Ret_360`, `AR_3_Ret_360`, `CBFS13700` | fixed |
| the scramble seed | `numpy.random.default_rng(20260910)` | fixed |

**MAY TUNE FREELY, AND EVERY CHANGE IS DISCLOSED IN THE RUN RECORD (L1–L5,
convergence aids only):** under-relaxation factors; linear-solver and
preconditioner choice; linear-solver tolerances **provided no channel is ordered
tighter than its siblings without a stated reason**; initialisation and
continuation (potential start, BC ramps) **provided the final state is at the
registered BCs and the registered Re**.

**ONE CHANGE PER RUN** (§2.0 of the standard). An arm that moves two dials cannot
discriminate and is `NOT A RESULT` for this ladder's purposes.

**L0 IS MANDATORY AND COMES FIRST.** Any row that does not converge gets a
recorded L0 reading — which of the three shapes (oscillation / growth under flat
neighbours / plateau), which channel, the balance state, and where in the domain —
**before** any L1 dial is touched.

**Explicitly forbidden, named so it cannot happen by drift:**
- Lowering the 80% bar because a row landed at 78%.
- Adding a sixth oracle channel because C4 fell short.
- Re-scoring against BASE instead of NULL, or vice versa, because one denominator
  gives a better number.
- Dropping `CBFS13700` from the denominator because it is the hard case.
- Changing the scramble seed because the first permutation was admitted.

---

## 10. COST — standing rule 12 (4 of 4: the cap)

**Unit: core-minutes = wall seconds × ranks ÷ 60.** Ranks = **1**: no `mpirun`,
no `decomposePar`, no `-parallel` token occurs in either predecessor launcher —
`aposteriori_frozenk/run_solves.sh:11` invokes `timeout 3600 simpleFoam` directly
and `Kaandorp2020_TBRF/aposteriori/run_lane.py:157` invokes
`timeout {WALL_S} simpleFoam -case .`. Serial. So core-minutes = wall s ÷ 60.

### 10.1 Derivation, from wall times MEASURED on this box

Rates derived from the predecessor campaign's own recorded `wall_s`
(`/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/scores.json`) and
(`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`):

- `AR_1_Ret_360`: 200,000 iterations in 2,093 s → **95.6 it/s**
- `AR_3_Ret_360`: 123,096 iterations in 3,600 s → **34.2 it/s**
- `CBFS13700`: 884 iterations in 69.3 s → **12.8 it/s**

| block | derivation | wall s |
|---|---|---|
| **C0 NULL** ×3, capped at 30,000 iterations | 30000/95.6 = 314; 30000/34.2 = 877; 30000/12.8 = 2,351 | **3,542** |
| **C1** ×3 (`b` truth, `k` transported) | 528 it → 5.5; 3,052 it → 89; CBFS **measured 1,701.6** | **1,796** |
| **C2** ×3 (arm S) | **measured** 6 + 71 + 308 | **385** |
| **C3** ×3 (arm L) | **measured** 8 + 82 + 336 | **426** |
| **C4** ×3, up to 5 outer passes | budgeted at 5 × C3 | **2,130** |
| **CX SCRAMBLED** ×3 | budgeted at 2 × C3 (structureless stress may converge slowly) | **852** |
| scoring, two-direction control, `--selftest` ×2 (`python3`, `python3 -O`), report assembly | | **300** |
| | **total** | **9,431 s** |

9,431 wall s × 1 rank ÷ 60 = **157.2 core-minutes**.

### 10.2 The registered figures

**REGISTERED ESTIMATE: 160 core-minutes.**
Derived: 160 ÷ 60 = 2.667 core-h × **$0.0513/core-h** = **$0.137 — DERIVED at the
owner-stated rate, NOT MEASURED.** This box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5); the rate is owner-stated (2026-08-21/22) and
corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`.

**REGISTERED CAP: 400 core-minutes.**
Derived: 400 ÷ 60 = 6.667 core-h × $0.0513 = **$0.342 — DERIVED, NOT MEASURED.**
Under the $25 pre-authorisation. **An overrun STOPS the campaign; it does not get a
new budget.**

**The 2.5× cap ratio is justified, not rounded.** Three named risks:
1. **CBFS is the case that caps.** In the predecessor Kaandorp campaign 4 of 6
   CBFS rows ran the full 30,000 iterations at 1,700–3,400 s each
   (`results.json`: `CBFS13700__TRUTH` 1,701.6 s, `__MEANB` 3,411.2 s, `__ML0`
   3,192.6 s, `__ML2` 2,796.0 s).
2. **C4's outer fixed point has no measured precedent on this box.** The 5 × C3
   budget is an assumption, not a measurement, and is labelled as such.
3. **CX injects a spatially incoherent stress field.** Its convergence behaviour
   is unknown; it may run to the per-solve timeout.

**Enforcement, registered:** per-solve `timeout 3600` (matching the existing
`run_solves.sh:11` precedent), **plus** a campaign-level wall accumulator that
stops the campaign at **24,000 wall s at ranks 1** (= 400 core-min). The
accumulator is checked before each solve launches and is the binding control;
18 solves × 3,600 s of per-solve timeout would otherwise permit 64,800 s.

**Rule 12 calibration obligation, registered now:** at RC3's completion the
estimate above is compared against the actual incurred core-minutes read from the
run logs, the ratio actual/predicted is stated, the gap is attributed
(contention / waste / misprediction, with waste named separately and never
absorbed into the ratio), and a row lands in **`docs/COST_CALIBRATION.md`** under
that file's append rules and the rule-10 private-index protocol. A completion
report without this comparison is incomplete.

---

## 11. Instruments — to be built, and to be frozen WITH this document

**These do not exist yet.** The freeze commit must carry them.

| module | job | refusals |
|---|---|---|
| `build_rc3_ladder.py` | build the six configurations per case from the read-only benchmark clone; write `b^Delta`, set the `k` treatment, install the `libs` entry **insert-or-replace with a `sys.exit(2)` check, never `assert`** (L-221/L-222: **every** call site checks) | `sys.exit(2)` on: libs entry absent after insertion; a pre-existing time directory; a missing benchmark field |
| `rc3_ceiling.py` | run the two-direction planted control (§6) FIRST, then score every row, apply the strict-completion clause (§8), evaluate V0/V1a/V1b/V2, emit the verdict from the fixed vocabulary | `sys.exit(2)` on: either plant direction failing; any strict-completion clause failing; a continuity violation being silently accepted |
| `rc3_fixedpoint.py` | drive C4's outer loop, print all five contraction ratios whatever happens | `sys.exit(2)` on N_outer exceeded without contraction |

**Every module: `--selftest` green under `python3` AND `python3 -O`,
`__pycache__` cleared before each. No `ast.Assert` carries any refusal, guard,
control or gate (§6.1).**

---

## 12. Relationship to other live closure items

- **RC2 (`RC2_kaandorp_divergence_repair`, FROZEN 2026-09-10)** — a different
  case (`Kaandorp2020_TBRF`), a different object (the `diverged` flag reader), and
  zero solver compute. **RC3 edits no RC2 file and depends on no RC2 output.**
- **RC4 (`RC4_kaandorp_propagation_repair`, drafted alongside this item)** — the
  Kaandorp propagation-path repair. RC3 and RC4 share a physical mechanism (the
  `k` budget) and are on **different cases with different products**: RC3
  calibrates a *gate criterion* on the Wu chain; RC4 repairs a *setup* on the
  Kaandorp chain. RC3's V0 threshold is *derived from* a Kaandorp measurement
  already on disk; it does not require RC4 to run, and RC4's outcome does not
  change RC3's registered numbers.
- **The frozenk chain** — `Wu2018_PIML_RF/aposteriori` and
  `Wu2018_PIML_RF/aposteriori_frozenk` are **read only**. Not one line of either
  is edited (standing rule 6).

---

## 13. What this lane could NOT verify, stated plainly

1. **`AR_3_Ret_360` arm L's `wall_s` is `None`** in
   `/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/scores.json`, so that
   row's cost contribution is a proxy from the arm-S rate, not a measurement. The
   §10 table says so.
2. **Whether the 30% bar would have been met by a *true* exact-stress oracle is
   unknown** — that is precisely what C4 exists to measure, and RC3 takes no
   position on it in advance.
3. **The `converged` field on several predecessor rows is inconsistent between
   artifacts.** `frozen_R_AR_1_Ret_360.json` records the `AR_1_Ret_360__TRUTHR`
   row as `"converged": false`, `"converged_iteration": null`, with
   `res_p_max_last500` = **1.0**, while
   `Kaandorp2020_TBRF/aposteriori/RESULTS.md` §2 prints it as
   `CONVERGED-residualControl` at 383 iterations. **This lane did not resolve that
   discrepancy and does not claim to.** It is flagged for the supervisor. It is
   noted that the same rows carry `"diverged": true` from the reader defect RC2
   owns, and that convergence-label reconciliation on preserved Kaandorp rows is
   RC2's territory, not RC3's.
4. **`divU_rms_over_gradscale` = 1.7038e-04 on `AR_1_Ret_360__TRUTHR`** exceeds
   the ≤1e-4 continuity criterion this document carries forward at §4. The 98.3%
   figure used to derive V0's 80% bar therefore comes from a row that **marginally
   fails that continuity criterion**. This is disclosed here rather than buried:
   the bar is set 18.3 points below it precisely because the source row is not
   pristine, and V0 is measured afresh under §8's completion clause regardless.

---

*Drafted 2026-09-10 by a closure lane. **DRAFT / UNFROZEN. Nothing may run against
it.** The freeze is the closure-supervisor's act, after a personal §3 check-1.
Zero solver compute produced this document. Nothing sent, filed, uploaded,
registered, posted or commented.*

---

## AMENDMENT A1 — 2026-09-10. PRE-FIRST-COMPUTE. Four supervisor rulings registered into the document.

**Document version: DRAFT v1.1** (was DRAFT v1.0 as landed at commit `4e3c5bc6`).
**lines whose number changed above this section: 0** — this amendment is appended
at the foot and edits no line above it. The assertion is not a claim: it was
proved by hashing the file's first 33,535 bytes (598 lines) before and after the
append inside a single shell invocation, with the whole-file digest shown to move
in the same invocation so the hasher is demonstrably not returning a constant.
The two prefix digests and the two whole-file digests are recorded in the commit
that carries this amendment.

**THIS AMENDMENT IS NOT THE FREEZE.** It changes no gate, no threshold, no cap and
no label. `prereg_commit:` still reads the DRAFT/UNFROZEN token at the Status line
of this document; that token still occurs **exactly once** in this file, and this
amendment deliberately does not write the token string again, so that the
supervisor's single substitution at the freeze clears
`build_rc3_ladder.refuse_if_unfrozen()` in one edit.

### A1.0 Why these resolutions land BEFORE the freeze and not at it

An **ambiguous criterion, once frozen, is a criterion that can be re-read later to
fit the answer** — which is precisely the failure standing rule 2's freeze exists
to prevent. Rule 2's own pre-compute clause makes an amendment legal here and
makes it illegal after the first solve. A resolution that lives only in a module
docstring is *not registered*: the instrument can be rewritten, and the gate is
supposed to live in the document. So the ambiguity is closed here, where it is a
gate, rather than at grading time, where it would be commentary.

### A1.1 The rule-2 condition, and how it was checked — freshly, at this amendment

**Condition: RC3 has had ZERO compute. The run root registered by its own
instrument does not exist.**

Checked at this amendment, by this lane, at zero compute:

| check | result | control that FIRED (same command shape, positive case) |
|---|---|---|
| `/home/ubuntu/closure-data/rc3` — the run root named at `build_rc3_ladder.py:102` (`ROOT = "/home/ubuntu/closure-data/rc3/wu2018"`) | **ABSENT** | `/home/ubuntu/closure-data` **EXISTS**; `/home/ubuntu/closure-data/aposteriori_frozenk` **EXISTS** |
| `/home/ubuntu/closure-data/rc3/wu2018` | **ABSENT** | as above |
| `find /home/ubuntu/closure-data -maxdepth 1 -name 'rc[34]*'` | **no hits** | the same `find` with `-name 'apost*'` returns `aposteriori` and `aposteriori_frozenk` |
| `find .../verification/runs -maxdepth 2 -iname '*rc3*'` | **no hits** | the same `find` with `-iname '*T-family*'` returns `verification/runs/T-family` |
| any `RESULTS.md`, `scores.json` or run artifact beside this registration | **none** — the directory holds `PREREGISTRATION.md`, `build_rc3_ladder.py`, `rc3_ceiling.py`, `rc3_fixedpoint.py` and nothing else | the sibling `Wu2018_PIML_RF/aposteriori_frozenk/` does carry `RESULTS.md`, so the listing is not blind to result files |

Independently, the instruments themselves refuse to run today:
`build_rc3_ladder.refuse_if_unfrozen()` (`build_rc3_ladder.py:152`) reads this
file and exits 2 while the Status line still carries the DRAFT/UNFROZEN token, and
`rc3_fixedpoint.drive()` calls it before any pass. No path through the committed
instruments can start a solver against this registration in its present state.

### A1.2 RULING 1 — §3.1's contraction criterion, read out in full. AMBIGUITY REMOVED; NO BAR MOVED.

§3.1 registers `N_outer = 5`, requires monotonic fall **"across passes 2..5"**, and
requires **all five ratios** to be printed. A ratio needs a predecessor, so five
outer passes taken alone would yield only four ratios. **The reading registered
here — the only one consistent with both §3.1's own "all five ratios" and §10's
"C4 ×3, up to 5 outer passes … budgeted at 5 × C3" — is:**

> **`b^Delta_0` is configuration C3's injected field.** C3 is exactly
> `b_LES − b_RANS` with `k` frozen at `k_LES` (§3 table), which is pass 0 of this
> same iteration and is therefore literally "the previous pass's converged field"
> for pass 1.
>
> **There are therefore FIVE ratios, `r_1 … r_5`, over FIVE outer passes**, with
> `r_m = ||b^Delta_(m) − b^Delta_(m−1)||_2 / ||b^Delta_(m−1)||_2`.
>
> **Monotonicity is required over `r_2 … r_5`**, exactly as §3.1 registers
> ("monotonically across passes 2..5"). **`r_1` is excluded** — it is the first and
> largest step, from the C3 field to the first fixed-point iterate.
>
> **The final ratio `r_5` must be ≤ 1e-2.**
>
> **All five ratios are printed whatever happens**, per §3.1 and §11.

**What this ruling does NOT do, verified clause by clause against the unmodified
text above:**

- **`N_outer = 5` does not move.** §3.1 line 193 is unchanged; `N_OUTER = 5` at
  `rc3_fixedpoint.py:71`.
- **The 1e-2 contraction threshold does not move.** §3.1 line 195 and §5.1 line 279
  are unchanged; `CONTRACTION_MAX = 1e-2` at `rc3_fixedpoint.py:72`.
- **The `NOT A RESULT` branch does not move.** §3.1 lines 196–199, §5.2 line 298 and
  §7's third falsifier (lines 377–379) are unchanged: a non-contracting fixed point
  is `NOT A RESULT`, the ceiling is read from the best of C1–C3 with C4 recorded as
  unavailable, `N_outer` is not raised, and no relaxation is introduced.

The reading was previously stated only in `rc3_fixedpoint.py`'s module docstring
(lines 26–38). **It is registered here so that no future reader has to reconstruct
it from an instrument**, and so that it cannot be re-read after compute.

### A1.3 RULING 2 — §9's model row names the frozen-k model explicitly. NO NEW SOLVER IS WRITTEN.

§9's anti-gaming table (line 429) names `kOmegaSSTCorrected` as the fixed
turbulence model, while §3's C2, C3, C4 and CX all register `k` **frozen**, which
that model cannot do. Freezing `k` is realised by the model
**`kOmegaSSTCorrectedFrozenK`**, in the library **`libwu2018FrozenK.so`**.

**Both libraries pre-date RC3 and neither is built by it. Verified at source by
this lane, at zero compute:**

| library | on-disk mtime | model symbols it defines |
|---|---|---|
| `.../platforms/linux64GccDPInt32Opt/lib/libspartaTurbulenceModels.so` | **2026-08-01 01:09:28 UTC** | `kOmegaSSTCorrected` |
| `.../platforms/linux64GccDPInt32Opt/lib/libwu2018FrozenK.so` | **2026-08-21 18:12:47 UTC** | `kOmegaSSTCorrected`, **`kOmegaSSTCorrectedFrozenK`** |

Both precede this registration's own directory (created **2026-09-10 04:43 UTC**)
by weeks. `libwu2018FrozenK.so` was built by the predecessor frozenk lane
(`Wu2018_PIML_RF/aposteriori_frozenk/src/Make/files:3`,
`build_cases.sh:43`), and RC3's builder consumes it as an existing artifact
(`build_rc3_ladder.py:111–114`: `SPARTA_LIB`, `FROZENK_LIB`, `MODEL_FROZEN_K`).

**Registered clarification of §9's model row — its binding content is unchanged:**

> The fixed model set is **`kOmegaSSTCorrected`** (library
> `libspartaTurbulenceModels.so`) for the `k`-transported configurations C0 and
> C1, and **`kOmegaSSTCorrectedFrozenK`** (library `libwu2018FrozenK.so`) for the
> `k`-frozen configurations C2, C3, C4 and CX, exactly as §3's table registers the
> `k` treatment per configuration.
>
> **§9's binding assertion is and remains: NO NEW SOLVER IS WRITTEN OR COMPILED BY
> RC3.** Both libraries already existed on this box before RC3 existed. The L6
> answer-changing row is FIXED, and it is fixed on a model set that was chosen
> before any RC3 number was seen.

No threshold, cap, band or label is touched by this clarification.

### A1.4 RULING 3 — §10's ILLUSTRATIVE solve count is corrected. THE BINDING CONTROL DOES NOT MOVE.

§10 line 521 reads, verbatim:

> `18 solves × 3,600 s of per-solve timeout would otherwise permit 64,800 s.`

**That sentence is SUPERSEDED and is wrong.** It counted C4 as one solve per case.
Under §3.1 as read out in A1.2, C4 is **five** solves per case. The worst-case
solve count is therefore:

| block | solves |
|---|---|
| C0 NULL ×3 | 3 |
| C1 ×3 | 3 |
| C2 ×3 | 3 |
| C3 ×3 | 3 |
| **C4 ×3 cases × 5 outer passes** | **15** |
| CX ×3 | 3 |
| **total** | **30** |

**Corrected illustrative figure: 30 solves × 3,600 s of per-solve timeout would
otherwise permit 108,000 s.**

**Nothing binding moves, and the correction strengthens rather than weakens the
control:**

- **The campaign-level accumulator remains 24,000 wall s at ranks 1 (= 400
  core-min)**, checked before each solve launches. §10 line 519 already names it
  **the binding control**, and it is unchanged. The gap it must close is simply
  larger than the document said (108,000 s of nominal timeout headroom, not
  64,800 s) — which is the argument *for* the accumulator, not against it.
- **The REGISTERED CAP remains 400 core-minutes** (§10.2, line 502). Unchanged.
- **The REGISTERED ESTIMATE remains 160 core-minutes** (§10.2, line 496).
  Unchanged, and it was never affected: §10.1's C4 row already budgets
  **5 × C3 = 5 × 426 = 2,130 wall s**, i.e. it already assumed five solves per
  case. The estimate's 9,431 s total and its 157.2 core-minutes are arithmetically
  untouched by this correction.
- Per-solve `timeout 3600` is unchanged.

**An illustrative figure that understates is still a wrong record.** It is
corrected here rather than left standing because it is non-binding.

### A1.5 RULING 4 — the builder's FOURTH refusal, registered into §11.

§11's row for `build_rc3_ladder.py` names three refusals. The committed instrument
carries a **fourth**, which the building lane disclosed openly in the function's
own docstring rather than adding silently. **An unregistered refusal is as much a
defect as a missing one** — a reader of §11 would not know it exists — so it is
registered here.

**Registered, as a fourth refusal of `build_rc3_ladder.py`:**

> **`write_bdelta_and_verify()` (`build_rc3_ladder.py:343`) — WRITER READ-BACK.**
> After writing `bijDelta` into a case, the builder reads the file back **through
> the scorer's own reader** (`_common/of_read.read_field`) and compares it to what
> it wrote. It **refuses, `sys.exit(2)`**, if the shape does not match, or if
> `max|read − written|` exceeds a **PLANT-RELATIVE** tolerance:
> `tol = max(1e-12, 8 × eps × max|written|)` — machine epsilon at the field's own
> largest magnitude, floored at 1e-12, **never an absolute 1e-15** (L-508: an
> absolute bar false-refuses on O(1)+ data and cost this team a legitimate
> instrument). The `_writer` argument is injectable so the module's `--selftest`
> can drive a deliberately corrupting writer and show the guard FIRES
> (`build_rc3_ladder.py:700–716`).

**Its provenance and its scope, registered so the scope is not later widened:**

- It was added under **standing rule 3**, which binds whether or not this document
  repeats it: a builder not shown able to put a non-zero on disk has not been shown
  to have built anything. Rule 3 is normally applied to the *reader*; this applies
  it to the *writer*, which is the same argument in the same direction.
- **It can only ever REFUSE.** It has no branch that emits a verdict, a value, a
  band or a label. **It cannot manufacture a `PASS`, and it cannot move a
  threshold, a cap, a band or a label.** Its only effect is to stop a mis-built
  case from ever running.
- It is a `refuse()` → `raise SystemExit(2)` (`build_rc3_ladder.py:145`), **not an
  `assert`**, so it survives `python3 -O` as §6.1 requires.
  `ast.Assert` count in `build_rc3_ladder.py`: **0**.

### A1.6 What did NOT move — the clause-by-clause statement rule 2 requires

Every line above this amendment is byte-identical to the version committed at
`4e3c5bc6`; the prefix hash recorded in the commit message proves it. Named
explicitly, because "nothing moved" is worth more when it is enumerated:

| clause | line | value, unchanged |
|---|---|---|
| V0 threshold | 237, 276 | C4 cut **≥ 80%** vs C0 NULL on **≥ 2 of 3** cases |
| V1a | 257, 277 | criterion PASSes C4 on the same ≥ 2 of 3 |
| V1b | 258, 278 | criterion FAILs CX on the same ≥ 2 of 3 |
| C4 fixed point | 193, 195, 279 | `N_outer = 5`; ratio **≤ 1e-2** by pass 5; monotone over passes 2–5 |
| continuity | 223, 280, 410 | RMS `div(U)` / gradient scale **≤ 1e-4** or NOT CONVERGED |
| V3 plant | 281, 316 | `PLANT = 1.234e-03`; move **> 1e-12** when planted, **bitwise identical** when not |
| verdict ladder | 285–302 | PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING, unchanged |
| falsifiers | 356–379 | all three unchanged; 80% never lowered, no oracle channel added, no case dropped, `N_outer` never raised |
| REGISTERED ESTIMATE | 496 | **160 core-minutes** |
| REGISTERED CAP | 502 | **400 core-minutes** |
| campaign accumulator | 519 | **24,000 wall s at ranks 1** — the binding control |
| per-solve timeout | 517 | `timeout 3600` |
| case set / seed / `bScale` | 432–436 | unchanged |
| Label | header | `RC3`, unchanged |

**No gate, threshold, cap or label is altered by this amendment.**

### A1.7 What this lane could not verify, at this amendment

1. **This lane did not run any instrument.** The `--selftest` claims in §11 and
   §6.1 are the building lane's; this amendment records what the committed source
   *contains* (verified by reading `git show HEAD:` for each file, not the working
   tree alone), not that the selftests pass. Executing them is part of the
   supervisor's §3 check-1, not this amendment.
2. **This lane did not re-derive the physics of the C4 fixed point** — only that
   §3.1's five-ratio reading is the sole reading consistent with §3.1 and §10
   together, and that `rc3_fixedpoint.py:126–142` implements exactly that.

*Amendment A1 appended 2026-09-10 by a closure lane on the closure-supervisor's
ruling. **THIS IS NOT THE FREEZE.** The document remains DRAFT / UNFROZEN and
nothing may run against it. Zero solver compute produced this amendment. Nothing
sent, filed, uploaded, registered, posted or commented.*
