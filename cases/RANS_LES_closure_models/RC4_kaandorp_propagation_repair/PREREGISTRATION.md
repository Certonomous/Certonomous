# RC4 — KAANDORP A-POSTERIORI PROPAGATION REPAIR: THE `kDeficit ≡ 0` SETUP DEFECT, REGISTERED AND TESTED

> # STATUS: **DRAFT / UNFROZEN.**
>
> **NOTHING MAY RUN AGAINST THIS DOCUMENT.** No solve, no extraction, no scoring
> pass, no queue entry, no staging into a run root. This registration is **NOT
> FROZEN**: its gates, thresholds, cap and label are **OPEN** and amendable in
> place under standing rule 2's pre-compute clause.
>
> **THE FREEZE IS THE SUPERVISOR'S ACT, NOT A LANE'S.** It happens only after the
> closure-supervisor's **personal** `SUPERVISION_CHARTER.md` §3 check-1 — the
> measurement instruments read as measurement scripts, as diffs, personally, not
> relayed — and §3 check-4 (pre-registration **committed** before compute).
> Standing rule 2 fixes the grading path **at the pre-registration commit**, and
> **this item's instruments do not exist yet**, so the freeze is the later commit
> that carries **this document AND its instruments together**. Any run before that
> commit is unregistered and its output is **NOT A RESULT**.
>
> **THIS COMMIT IS NOT THE FREEZE.** It lands the draft so it is reviewable.
>
> **Zero solver compute produced this document.** Nothing has been sent, filed,
> uploaded, registered, posted or commented (standing rules 2, 7). No frozen file
> was edited (standing rule 6). **No RC2 file was read for write, edited, or
> depended upon.** No sha is pinned by this document.

Predecessor: `Kaandorp2020_TBRF/aposteriori` — `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/RESULTS.md`, **NOT A RESULT** (registered §5 cascade: the H0 truth-injection gate required a ≥30% cut in `U_rms` and measured a **+62.0%** rise on T1 / **+57.0%** on T2, so H1–H3 are void).

**Rung:** `RC4_kaandorp_propagation_repair`
**Team:** closure
**Class:** **SETUP-REPAIR REGISTRATION** — the product is a repaired propagation
configuration and a pre-registered statement of what a repaired propagation must
demonstrate. It is **not** a model finding and takes **no** verdict on the TBRF.
**Label:** `RC4` (closure; Kaandorp2020 TBRF a-posteriori chain; propagation-path
setup repair)
**Status:** **DRAFT / UNFROZEN.** `prereg_commit:` = `PENDING_SUPERVISOR_FREEZE`.
**Drafted:** 2026-09-10, by a closure lane on the closure-supervisor's dispatch.
**Discharges:** the `Kaandorp-aposteriori` **NEEDS-SUCCESSOR** row owed by
`docs/closure/CLOSURE_2BC_EXHAUSTION_REAUDIT.md` (commit `3c6eb5da`), Row 4.

---

## 0. DISJOINTNESS FROM RC2 — stated first, because it is a precondition of this item existing

`cases/RANS_LES_closure_models/RC2_kaandorp_divergence_repair/` was **FROZEN on
2026-09-10** and is running. RC2 and RC4 share a case directory and nothing else.

| | **RC2** (frozen, running) | **RC4** (this draft) |
|---|---|---|
| **object** | the `diverged` **flag reader** — `run_lane.py:175`, an unanchored substring that matches OpenFOAM's `trapFpe:` safety banner on line 18 of every log, so `diverged` is a constant `True` and not a measurement | the **solver setup** — the registered choice `kDeficit ≡ 0` at `aposteriori/PREREGISTRATION.md:97` and `setup_case.py:128` |
| **kind of defect** | a **bookkeeping** defect in an instrument | a **physical configuration** defect in the experiment |
| **what moves** | a convergence/divergence label on 16 preserved rows | the `U_rms` and `k` budget of the truth-injection ceiling |
| **compute** | **ZERO solver compute** — a re-grade from preserved artifacts | **NEW solves required** (§9) |
| **files it creates** | `rc2_divergence.py`, `regrade_rc2.py` | new modules under `RC4_.../` only (§10) |
| **files it edits** | none — `run_lane.py` is NOT edited | none — `run_lane.py`, `setup_case.py`, `frozen_R.py`, `aposteriori/PREREGISTRATION.md` are NOT edited, and **no RC2 file is edited or written** |
| **question answered** | which recorded verdicts move once the flag is repaired | whether the H0 ceiling propagates once the k-equation correction `R` is supplied |

**Non-contradiction clause, registered.** RC2 may relabel convergence states on the
preserved Kaandorp rows. **RC4 does not depend on those labels.** Its defect is
re-derived from `U_rms` and `k/k_LES` — physics fields — and Sanaa's universal rule
of 2026-08-26 governs: *bookkeeping never voids physics.* Where RC2 publishes a
re-graded convergence label for a row RC4 also cites, **RC4 takes RC2's label as
authoritative and does not recompute it**; RC4's own convergence determinations
apply **only** to the new runs RC4 launches, under §8's completion clause. RC4
asserts nothing about the `diverged` flag, on any row, ever.

---

## 1. The defect, re-derived AT SOURCE at drafting — not quoted from the board

The re-audit is **not** the authority for anything in this section.

### 1.1 The registered choice that broke the ceiling

`cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md`,
§2.3, lines **97–98**, verbatim:

> *"`R = 0` therefore, everywhere, in every configuration **including the
> truth-injection ceiling**."*

and §2.4, lines **103–112**, which sets the other half of the mechanism:

> *"`kOmegaSSTCorrected` is stock SST plus corrections: both transport equations
> are solved every iteration, with the production augmented by
> `Gextra = -2 k bScale (bijDelta : grad U)` in the `k` equation …"* (`:106–108`),
> closing at `:112` with *"Freezing is not run."*

Implemented at `aposteriori/setup_case.py:10` — the build docstring, verbatim,
`kDeficit  = 0            (registered: the TBRF predicts b only)` — and written to
disk at `aposteriori/setup_case.py:128`.

### 1.2 The mechanism, in one line

Injecting `b^Delta` changes the `k`-equation production term `Gextra` with
**nothing on the other side of the budget to balance it**, because `R` (the
`kDeficit` field) is identically zero. The transported `k` therefore collapses,
and the modelled stress `tau = 2k(b_linear + b^Delta)` is scaled by a wrong `k`
however good the anisotropy is.

### 1.3 The measured consequence — `aposteriori/RESULTS.md` §2 table, corroborated against the JSON on disk

| case | row | `U_rms` | vs BASE | `k_mean` | `k/k_base` | `k/k_LES` |
|---|---|---|---|---|---|---|
| `AR_1_Ret_360` | shipped BASE | 0.1985 | — | 26.679 | 1.000 | 0.615 |
| `AR_1_Ret_360` | NULL | 0.19874 | +0.1% | 26.712 | 1.001 | 0.615 |
| `AR_1_Ret_360` | **TRUTH** | **0.32151** | **+62.0%** | **8.740** | **0.328** | **0.201** |
| `AR_3_Ret_360` | shipped BASE | 0.1846 | — | 29.238 | 1.000 | 0.594 |
| `AR_3_Ret_360` | **TRUTH** | **0.28980** | **+57.0%** | **10.504** | **0.359** | **0.213** |

Corroborated to full precision against
`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json`:
`AR_1_Ret_360__TRUTH` `U_rms` = **0.32151472485167976** against
`AR_1_Ret_360__NULL` `U_rms` = **0.19873618541903595** (a **+61.8%** rise measured
against NULL; the **+62.0%** in `RESULTS.md` is measured against the shipped BASE
0.1985 — both denominators are quoted here so neither is hidden);
`AR_3_Ret_360__TRUTH` = **0.2897951941371819** against
`AR_3_Ret_360__NULL` = **0.18652118516596**; `CBFS13700__TRUTH` =
**0.08413142594037305** against `CBFS13700__NULL` = **0.05155374750771284**
(**+63.2%**).

The H0 gate that these rows failed is registered at
`aposteriori/PREREGISTRATION.md:192–193`: *"NOT A RESULT for the entire lane if
`TRUTH` fails to reduce `U_rms` on T1 by ≥ 30% relative to the SST gate 0.1985."*

**Injecting the truth made the answer worse. On every case.**

### 1.4 The controlling counter-evidence — the SAME solver, the SAME path, with `R` supplied

`/home/ubuntu/closure-data/aposteriori/kaandorp/frozen_R_AR_1_Ret_360.json`,
`propagate` block, run directory `AR_1_Ret_360__TRUTHR` (on disk):

- `U_rms` = **0.003406514937336865** — against NULL 0.19873618541903595, a
  **98.3% cut**
- `k_rms` = 0.0035758325158110472; `b_rms_total` = **0.0022509857005574446**
- in-plane secondary flow = **1.4962988765646739 %** of bulk against the DNS
  **1.5081349205678083 %** — i.e. **99.2%** of the true secondary-flow magnitude,
  from a linear model's structural zero
- 383 iterations, `wall_s` = **7.4**, `rc` = 0

And on a second case, `frozen_R_PHLL10595.json`, run directory
`PHLL10595__TRUTHR`: `U_rms` = **0.009319036382277986**, `unrealisable_frac` =
**0.0**, `"converged": true` at `converged_iteration` **3368** of 3450 — the
cleanest two-channel truth-injection row on disk.

**Same solver (`kOmegaSSTCorrected`, `sdk/openfoam/sparta`). Same injection path.
Same meshes. One field different: `kDeficit`.** The propagation path is not
broken. The **registered setup** is.

### 1.5 Why this is a SETUP defect and not a model finding

§2.3's reasoning — *"The TBRF predicts `b` and nothing else … inventing one would
be fitting a second model"* — is **correct for the ML row**. A model
configuration must carry only what the model predicts.

**It is not correct for the TRUTH row.** The ceiling configuration is not a model
configuration; it is the apparatus's calibration reference, and its only job is to
establish *whether the path can express a correction at all* — that is the
definition the sibling lane registered at
`Wu2018_PIML_RF/aposteriori/PREREGISTRATION.md:126` (*"the **ceiling**: the best
any perfect anisotropy predictor could do through this injection path"*). Supplying
a frozen-RANS-extracted `R` alongside the truth `b` **in the ceiling row only**
measures the apparatus. It fits nothing, predicts nothing, and grades nothing.

The predecessor lane applied the model's information budget to the apparatus's
reference row, and so recorded a **physical property of b-only closures** (the
`k`-budget collapse) as **"broken propagation"**. That is the defect RC4 repairs,
and the repair is a configuration change, not a model change.

### 1.6 The repair already exists as an UNREGISTERED diagnostic — which is exactly the gap

`aposteriori/frozen_R.py:2`, verbatim: *"POST-HOC diagnostic (decided AFTER the
preregistered H0 gate failed)."* and at `:16`: *"NOT a preregistered
configuration. Carries no verdict."*

So the numbers in §1.4 are real, on disk, and **carry no verdict**, by their own
author's registration. **RC4 is what registers the configuration in advance and
states, before compute, what a repaired propagation must demonstrate.** Without
that, §1.4 is an after-the-fact rescue, which is the shape standing rule 2 exists
to forbid.

### 1.7 A defect in the extraction that no predecessor gated on — found at drafting

The frozen-RANS extraction has a **self-check that nobody made a gate**. Every
preserved extraction log at
`/home/ubuntu/closure-data/aposteriori/kaandorp/*__FROZENEXTRACT/` prints the
relative L2 drift of the recovered `k` from `k_data` for both sign conventions:

| case | `RScale = +1` drift | `RScale = −1` drift | printed ratio (−1/+1) |
|---|---|---|---|
| `AR_1_Ret_360` | **3.62632e-05** | 0.993315 | 27391.8 |
| `CBFS13700` | **4.85518438281052e-07** | 0.974810497433794 | 2007772.35337354 |
| `PHLL10595` | **0.065849156661484** | 0.998788240427244 | 15.1678212913461 |

The `+1` branch reproduces `k_data` to 3.6e-05 on `AR_1_Ret_360` and 4.9e-07 on
`CBFS13700`, **but only to 6.6e-02 on `PHLL10595`** — a factor 1,800 worse than
`AR_1`. An extracted `R` that cannot reproduce the `k` it was extracted from is not
a usable reference, and **nothing in the predecessor gates on this number.** RC4
makes it gate **P-1**, and it is evaluated at **zero compute** from the preserved
logs before any solve is launched.

Also recorded, and flagged rather than explained: `kDeficit_rms` on
`AR_1_Ret_360` is **36961887.15656184**, against **0.006807668685535144** on
`CBFS13700` and **0.05882908684166042** on `PHLL10595` — nine orders of magnitude
apart. This lane did **not** determine whether that is a units/normalisation
artefact or a real pathology; §11 states so.

**No `__FROZENEXTRACT` directory exists for `AR_3_Ret_360`.** That extraction has
never been run and RC4 must run it (§9 costs it).

---

## 2. What RC4 is, as ONE capped item

**One product: a repaired truth-injection configuration for the Kaandorp
a-posteriori case, registered in advance, together with a pre-registered statement
of what a repaired propagation must demonstrate before any closure can be graded
through it.**

Two things it is **not**:
- It is **not** a re-grade of the TBRF. No H1/H2/H3 verdict is taken. The forest's
  rows are not rescored by this item.
- It is **not** a licence to grade b-only ML rows against a two-channel ceiling.
  §5's **P3** forbids that explicitly.

---

## 3. Configurations, fixed here

Cases: `AR_1_Ret_360`, `AR_3_Ret_360`, `CBFS13700` — the three in-scope cases of
the predecessor. `BFS5100` (Kaandorp Table 4) remains **BLOCKED**: no such case is
on disk, as the predecessor established. `PHLL10595` is **out of scope** for the
graded ladder and appears only as §1.4/§1.7 evidence.

| tag | `b^Delta` | `kDeficit` (`R`) | purpose |
|---|---|---|---|
| **N NULL** | 0 | 0 | the reference every cut is measured against |
| **T-b** | `b_LES − b_RANS` | **0** | the predecessor's TRUTH row, reproduced so the two ceilings sit side by side |
| **T-bR** | `b_LES − b_RANS` | **frozen-RANS extracted `R`** | **the repaired ceiling** |

`bScale` = **1.0** in every scored configuration — no blending, no clipping —
carried from `aposteriori/PREREGISTRATION.md` §2.5 unchanged, so T-b is
comparable to the predecessor row it reproduces.

`k` and `omega` are **TRANSPORTED**, not frozen, in all three configurations,
carried from §2.4 unchanged. **Freezing `k` is deliberately NOT part of this
repair** — that is the sibling chain's variable (`Wu2018_PIML_RF/aposteriori_frozenk`,
and the calibration item RC3 that succeeds it), and mixing it in here would move
two things at once and violate the one-change-per-run rule.

---

## 4. Metrics — unchanged from the predecessor, so the rows stay comparable

Per `_common/BASELINES.md` §1, on the same cells: `U_rms`, `U_mae`, `k_mean`,
`k/k_base`, `k/k_LES`, `b_rms` of the total modelled anisotropy, unrealisable
fraction, `divU_rms_over_gradscale`, in-plane % of bulk (ducts), `x_reatt`
(CBFS).

**Continuity, and both readings reported.** The predecessor's registered bar is
H5, RMS `div(U)` / gradient scale **< 1e-3**
(`aposteriori/PREREGISTRATION.md` §5, H5). **That bar is carried forward
unchanged** so RC4's rows are comparable to the rows they succeed. The sibling Wu
chain's stricter **≤ 1e-4** criterion (`Wu2018_PIML_RF/aposteriori/PREREGISTRATION.md`
§4) is **reported beside every row as a second reading**, so a reader can apply
either and neither threshold is hidden. Disclosed now, before compute, because it
already bites on preserved rows: `AR_1_Ret_360__TRUTHR` measured
`divU_rms_over_gradscale` = **1.703775237339125e-04** — inside 1e-3, outside 1e-4;
`CBFS13700__TRUTHR` measured **0.3219275282624856** and `PHLL10595__TRUTHR`
**0.09202039655862047**, both outside **both** bars.

---

## 5. GATES AND THRESHOLDS — what a repaired propagation must demonstrate

Stated **in advance**, which is the entire point of this item.

### P-1 — R-EXTRACTION VALIDITY. Runs FIRST. Zero compute for the three preserved cases.

> **The frozen-RANS extraction must reproduce the `k` it was extracted from:
> relative L2 drift of recovered `k` from `k_data` ≤ 0.05, on the sign branch the
> extraction actually used.**

Read from the extraction log, not recomputed. Measured today at zero compute
(§1.7): `AR_1_Ret_360` **3.62632e-05** ✓, `CBFS13700` **4.85518e-07** ✓,
`PHLL10595` **0.0658** ✗ (out of scope). `AR_3_Ret_360` **has no extraction on
disk** and must be run and gated the same way.

**Registered consequence:** a case failing P-1 is **`BLOCKED`** — its T-bR row is
not run, and its number is never quoted as a ceiling. **If fewer than 2 of the 3
in-scope cases survive P-1, RC4 as a whole returns `BLOCKED`** — it does **not**
rescale the denominator and report a PASS on one case.

### P0 — THE REPAIRED CEILING PROPAGATES. The headline gate.

> **T-bR must cut `U_rms` by ≥ 80% relative to N NULL, on ≥ 2 of the 3 in-scope
> cases.**

**Threshold provenance, from a measurement already on disk and not from anything
this campaign will produce:** `AR_1_Ret_360__TRUTHR` `U_rms` =
0.003406514937336865 against `AR_1_Ret_360__NULL` 0.19873618541903595 = a **98.3%**
cut. The 80% bar carries **18.3 percentage points of margin below a measured
value**. It is registered now and **it is never moved.**

### P1 — THE REPAIR IS ATTRIBUTABLE TO `R` AND TO NOTHING ELSE.

> **The T-bR case directory must differ from the T-b case directory in exactly
> one field file: `kDeficit`. Every other file — `system/`, `constant/`,
> `fvSchemes`, `fvSolution`, `controlDict`, BCs, `0/` fields, mesh — must be
> byte-identical.**

Verified by a registered recursive directory comparison whose **only** permitted
difference is `<time>/kDeficit`. **Any other difference: the instrument refuses,
`sys.exit(2)`, and the row is `NOT A RESULT`.** This is
`NONCONVERGENCE_STANDARD.md` §2.0's *one change per run* made executable: an arm
that moves two things answers no question.

### P2 — THE NAMED MECHANISM IS THE THING THAT MOVED.

> **`k/k_LES` on the T-bR row must lie in `[0.9, 1.1]`.**

Against the predecessor's measured T-b values of **0.201** (`AR_1_Ret_360`) and
**0.213** (`AR_3_Ret_360`), and against the one prior measurement of the repaired
configuration, `k_rms` consistent with `k/k_LES` ≈ 1 on `AR_1_Ret_360__TRUTHR`.
**A repair that improves `U_rms` without restoring the `k` budget has not
demonstrated the mechanism it claims**, and P2 is what stops RC4 from being right
for the wrong reason.

### P3 — THE TWO CEILINGS ARE PUBLISHED SIDE BY SIDE AND NEVER SUBSTITUTED.

> **The repaired (two-channel) ceiling does NOT retroactively grade the TBRF's ML
> rows.** The TBRF supplies no `R`; a b-only model is graded against the **b-only**
> ceiling (the T-b row), which is republished as a measured number beside the
> repaired one. **Reporting the T-bR ceiling as "the ceiling" for a b-only model is
> forbidden by this registration.**

### P4 — READER CONTROL. §6. A failed control makes the whole item `NOT A RESULT`.

### 5.1 The verdict ladder — fixed vocabulary only

- **PASS** — P-1 admits ≥2 cases, **and** P0 holds, **and** P1 holds on every
  scored row, **and** P2 holds on the P0-passing cases, **and** P4 holds. The
  propagation path is demonstrated repaired, the repair is attributable to
  `kDeficit` alone, and the named mechanism is confirmed.
- **GATE REACHED** — P0 and P1 hold, but P2 fails (`k/k_LES` outside `[0.9,1.1]`).
  Propagation is repaired; the `k`-budget mechanism is **not** confirmed as the
  sole channel, and that is reported as the open question rather than smoothed
  over.
- **GATE FAIL** — P-1 admits ≥2 cases and P1 holds, but **P0 fails**: supplying
  `R` does **not** restore the ceiling. The premise of this item is then wrong and
  the headline finding is that the Kaandorp a-posteriori `NOT A RESULT` has a
  cause other than `R ≡ 0`.
- **NOT A RESULT** — P1 fails (more than one thing differs between T-b and T-bR);
  or P4's control fails in either direction; or any scored row fails §8's
  strict-completion clause.
- **BLOCKED** — fewer than 2 in-scope cases survive P-1; or `BFS5100`, which is
  not on disk; or a case whose benchmark fields are absent at run time.
- **PENDING** — the display state until the item runs. **Never** used to soften a
  `GATE FAIL`.

---

## 6. The planted-zero control — standing rule 3, two directions, on REAL fields

**A zero from a reader not shown able to see a non-zero is not evidence.** RC4's
scorer refuses to produce a number until it has demonstrated both directions **on
a field written by `simpleFoam` on this box** — never on a string literal, because
*a control defined in terms of the thing it controls is not a control*.

**Direction A — can the reader SEE a non-zero?** Copy a real converged `U` field
from a scored case directory. Add `PLANT = 1.234e-03` to the value at cell index
`0` and at cell index `n // 2`. Write it to disk. Re-read through the **same**
reader the scorer uses (`_common/of_read.read_field`) and recompute `U_rms`. **It
must differ from the unplanted value by more than `1e-12`.** Otherwise:
`sys.exit(2)`.

**Direction B — does the reader see a genuine zero AS zero?** Re-read the
unmodified copy through the same reader. **`U_rms` must be bitwise identical to the
original.** Otherwise: `sys.exit(2)`.

**A second plant, on the field this item is actually about.** Because RC4's whole
claim rests on `kDeficit` being non-zero in T-bR and zero in T-b, the instrument
additionally plants `PLANT = 1.234e-03` into a copy of a real `kDeficit` field,
reads it back, and **requires the P1 directory comparator to report that file as
differing**. If the comparator cannot see a planted difference in the one file it
exists to watch, it is blind: `sys.exit(2)`.

**All three controls run on every scoring pass, not only under `--selftest`.**

### 6.1 NO `ast.Assert` CARRIES ANY REFUSAL, GUARD, CONTROL OR GATE

**Binding on every instrument RC4 specifies** (L-332 / D476 §31.3): `assert`
statements are removed by `python3 -O`, so a guard written as an `assert` is a
guard that is absent in half the ways the file can be run.

- **Every refusal, guard, control and gate in RC4's instruments is a
  `sys.exit(2)` or a `raise`.** Not one is an `assert`.
- **`--selftest` must exit 0 under `python3` AND under `python3 -O`**, with
  `__pycache__` cleared before each invocation — a stale `.pyc` inverts mutation
  tests (the clean control fails and the mutated case passes), and
  `PYTHONDONTWRITEBYTECODE` does **not** fix it.
- **The selftest plants a violation of each gate and requires each to be caught**,
  under both interpreter modes.

**The defect is present in the predecessor and is re-derived at source here, so
the replacement is concrete, not theoretical.** `assert` statements carrying
guards exist at `aposteriori/frozen_R.py:79`
(`assert "libspartaTurbulenceModels" in s, "libs insert failed: " + cd` — the
L-221 libs guard; under `-O` it vanishes and the solve runs **without the model**,
silently), `aposteriori/setup_case.py:115`, `aposteriori/setup_case.py:124`,
`aposteriori/run_lane.py:153`, `aposteriori/run_lane.py:273`. **RC4 reuses none of
these call sites.** Its own builder re-implements every one of them, including the
`libs` insert-or-replace check at **every** call site (L-221/L-222: a lesson is not
applied until every call site checks), as `sys.exit(2)`.

---

## 7. THE REGISTERED FALSIFIER

> **If P-1 admits ≥ 2 in-scope cases and P1 holds, and the repaired ceiling T-bR
> nevertheless fails to cut `U_rms` by ≥ 80% relative to NULL on ≥ 2 of the 3
> in-scope cases, then RC4's premise — that `kDeficit ≡ 0` is the propagation
> defect — is FALSIFIED.**
>
> **RC4 is then reported `GATE FAIL` and WITHDRAWN as a propagation repair.**
>
> **The 80% threshold is NOT lowered. No additional channel is added to reach it —
> not frozen `k`, not frozen `omega`, not a `bScale` ladder, not a different `R`
> extraction convention. No case is dropped from the denominator to improve the
> ratio.** The finding recorded is that the Kaandorp a-posteriori `NOT A RESULT`
> has a cause other than the registered `R ≡ 0`, and the search for that cause is a
> **new** registration, not an extension of this one.

**Second falsifier — attributability.** If P1's one-change comparison finds any
file other than `<time>/kDeficit` differing between T-b and T-bR, the row is
`NOT A RESULT` and is **not re-scored as it stands**. The case is rebuilt from the
read-only benchmark clone and re-run **once**. A second P1 failure **withdraws the
item**: a repair that cannot be built as a single change cannot be attributed, and
an unattributable improvement is not evidence.

**Third falsifier — the control.** If the `kDeficit` plant of §6 does not make the
P1 comparator report a difference, the comparator is blind to the only file this
item changes, and every P1 `PASS` it has ever emitted is void. The item returns
`NOT A RESULT`.

---

## 8. Strict completion — standing rule 4, adapted and stated in full

These are incompressible closure cases with no `T`, so the thermal family's field
list does not apply. **The adapted clause, registered here.** A scored run is
**COMPLETE** only if **all** of the following hold; any one failing makes the row
`NOT A RESULT`, and the instrument **refuses (`sys.exit(2)`) rather than
degrading**.

1. **`rc = 0`** from the solver invocation.
2. An **`End`** line in the solver log.
3. **Termination is registered:** either the last written time equals the
   registered `endTime`, **or** the log carries OpenFOAM's `residualControl`
   convergence line and the last written time equals the iteration it names.
   Both branches are registered now, before compute, because these cases stop on
   `residualControl`.
4. **Fields present at the last written time:** `U`, `p`, `k`, `omega`, `nut`,
   `phi`, **and `kDeficit`** — the last because it is the field this item exists to
   change, and a T-bR row without it on disk did not run the configuration it
   claims.
5. **Iteration accounting:** the count of `ExecutionTime` lines equals the number
   of steps the log reports having taken.
6. **AGE GUARD — every field at the last written time is NEWER than the case's own
   `0/U`.** `0/U` is touched last at case build, so it dates the run that was
   allowed to produce the answer.
7. **The build guard refuses a case directory in which `0` or any numeric time
   directory already exists.**
8. **Continuity** reported under both bars per §4; a row outside the carried-forward
   **1e-3** bar is NOT CONVERGED whatever its `U_rms`.

**Registered, so it is not a surprise:** the predecessor's own artifacts show
`"resumed": true` and `"wall_s": -1.0` on all thirteen duct rows in
`results.json`. **RC4's runs are built fresh under clause 7 and are never
resumed**, so `wall_s` is a real measurement on every RC4 row and the rule-12
calibration at §9.3 has something honest to compare against.

---

## 9. COST — standing rule 12

**Unit: core-minutes = wall seconds × ranks ÷ 60.** Ranks = **1**: the predecessor
launcher `aposteriori/run_lane.py:157` invokes
`timeout {WALL_S} simpleFoam -case .` directly, with no `mpirun`, no
`decomposePar` and no `-parallel` token anywhere in the file. Serial. So
core-minutes = wall s ÷ 60.

### 9.1 Derivation, from wall times MEASURED on this box

Iteration rates from the predecessor campaigns' own recorded `wall_s`
(`/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/scores.json` for the ducts,
`/home/ubuntu/closure-data/aposteriori/kaandorp/results.json` for CBFS):
`AR_1_Ret_360` **95.6 it/s** (200,000 it in 2,093 s); `AR_3_Ret_360` **34.2 it/s**
(123,096 it in 3,600 s); `CBFS13700` **12.8 it/s** (884 it in 69.3 s).

| block | derivation | wall s |
|---|---|---|
| **P-1** on the three preserved extractions | read from preserved logs — **zero compute** | **0** |
| new `__FROZENEXTRACT` for `AR_3_Ret_360` | measured extractions: `AR_1` 6.0 s, `CBFS` 40.5 s, `PHLL` 29.0 s; budgeted for the larger duct | **60** |
| **N NULL** ×3, capped at 30,000 iterations | 30000/95.6 = 314; 30000/34.2 = 877; 30000/12.8 = 2,351 | **3,542** |
| **T-b** ×3 | 528 it → 5.5; 3,052 it → 89; CBFS **measured 1,701.6** | **1,796** |
| **T-bR** ×3 | `AR_1` **measured 7.4**; `CBFS` **measured 2,181.6**; `AR_3` no precedent, budgeted at 3× its own T-b (267) | **2,456** |
| scoring, three-way planted control, P1 directory comparison, `--selftest` ×2 (`python3`, `python3 -O`), report assembly | | **300** |
| | **total** | **8,154 s** |

8,154 wall s × 1 rank ÷ 60 = **135.9 core-minutes**.

### 9.2 The registered figures

**REGISTERED ESTIMATE: 140 core-minutes.**
Derived: 140 ÷ 60 = 2.333 core-h × **$0.0513/core-h** = **$0.120 — DERIVED at the
owner-stated rate, NOT MEASURED.** This box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5); the rate is owner-stated (2026-08-21/22) and
corroborated at `Xiao2016_EnKF/PREREGISTRATION.md:197`.

**REGISTERED CAP: 350 core-minutes.**
Derived: 350 ÷ 60 = 5.833 core-h × $0.0513 = **$0.299 — DERIVED, NOT MEASURED.**
Under the $25 pre-authorisation. **An overrun STOPS the campaign; it does not get a
new budget.**

**The 2.5× cap ratio is justified, not rounded.** Three named risks:
1. **Two of the three duct wall-times in the predecessor are unrecorded.** All
   thirteen duct rows in `results.json` carry `"wall_s": -1.0` with
   `"resumed": true`, so the duct estimates rest on a rate proxy taken from a
   **different campaign** on the same meshes. That is an assumption, and it is
   labelled one.
2. **CBFS is the case that caps.** `CBFS13700__TRUTHR` is a **measured** 2,181.6 s
   at the full 30,000 iterations, and 4 of 6 CBFS rows in the predecessor ran to
   the cap at 1,700–3,400 s.
3. **The repaired configuration has exactly one short precedent** (`AR_1`, 383
   iterations, 7.4 s) and **none at all on `AR_3_Ret_360`**, whose extraction has
   never been run.

**Enforcement, registered:** per-solve `timeout 3600` (the existing
`run_lane.py:157` precedent), **plus** a campaign-level wall accumulator that stops
the campaign at **21,000 wall s at ranks 1** (= 350 core-min), checked before each
solve launches. The accumulator is the binding control: 9 solves plus an
extraction at 3,600 s of per-solve timeout would otherwise permit 36,000 s.

### 9.3 Rule-12 calibration obligation, registered now

At RC4's completion the estimate above is compared against the actual incurred
core-minutes read from the run logs; the ratio actual/predicted is stated; the gap
is attributed (contention / waste / misprediction, with waste named separately per
`COMPUTE_BUDGET_CHARTER.md` §6 and **never absorbed into the ratio**); and a row
lands in **`docs/COST_CALIBRATION.md`** under that file's append rules and the
rule-10 private-index protocol. A completion report without this comparison is
incomplete.

---

## 10. ANTI-GAMING REGISTER — `docs/standards/NONCONVERGENCE_STANDARD.md`, the L0–L7 ladder

Sanaa's clause, verbatim from §1 of that standard:

> *"ANTI-GAMING (absolute): convergence aids (L1-L5) tune freely, disclosed.
> Answer-changing choices (model, scheme class, formulation) are never selected by
> agreement with the reference. Converged-but-wrong = NOT HELD with diagnosis,
> never a parameter hunt. Frozen gates never edited post-compute."*

**FIXED HERE, BEFORE COMPUTE, AND NEVER SELECTED BY AGREEMENT WITH THE
REFERENCE:**

| what | fixed value | ladder level |
|---|---|---|
| turbulence model | `kOmegaSSTCorrected`, `sdk/openfoam/sparta` — the predecessor's solver; **no new solver is written** | **L6 — answer-changing, FIXED** |
| formulation | steady, `simpleFoam`, serial (ranks = 1); `k` and `omega` **transported**, never frozen | **L7 — answer-changing, FIXED** |
| scheme class | the shipped benchmark `fvSchemes` per case, unmodified | **L3 class — answer-changing, FIXED** |
| `bScale` | **1.0**, no blending, no clipping, every scored configuration | **answer-changing, FIXED** |
| the configuration set | **N, T-b, T-bR** exactly as §3 defines them — no configuration added, dropped or re-tagged after compute begins | fixed |
| the `R` source | the frozen-RANS `kCorrectiveFrozenFoam` extraction, **one** sign convention chosen by the P-1 drift criterion **before** any propagation run, and recorded | fixed |
| the P0 threshold | **80%**, derived §5 from a measurement already on disk | fixed |
| the P2 band | **`[0.9, 1.1]`** on `k/k_LES` | fixed |
| the case set | `AR_1_Ret_360`, `AR_3_Ret_360`, `CBFS13700` | fixed |

**MAY TUNE FREELY, AND EVERY CHANGE IS DISCLOSED IN THE RUN RECORD (L1–L5,
convergence aids only):** under-relaxation factors; linear-solver and
preconditioner choice; linear-solver tolerances **provided no channel is ordered
tighter than its siblings without a stated reason**; initialisation and
continuation (potential start, BC ramps) **provided the final state is at the
registered BCs and the registered Re**.

**ONE CHANGE PER RUN.** P1 (§5) is this rule made executable for the one change
this item is about.

**L0 IS MANDATORY AND COMES FIRST.** Any row that does not converge gets a recorded
L0 reading — which of the three shapes (oscillation / growth under flat neighbours
/ plateau), which channel, the balance state, and where in the domain — **before**
any L1 dial is touched.

**Explicitly forbidden, named so it cannot happen by drift:**
- Choosing the `R` sign convention because one of them gives a better `U_rms`.
  **The convention is chosen by P-1's `k`-reproduction drift, before any
  propagation run, and recorded.** That is a criterion about the extraction's
  internal consistency, **not** about agreement with the velocity reference.
- Lowering the 80% bar because a case landed at 78%.
- Widening the `[0.9, 1.1]` `k/k_LES` band to admit a row.
- Freezing `k` "as well", to help T-bR clear P0 — that moves two things and is the
  sibling chain's variable.
- Dropping `CBFS13700` from the denominator because it is the hard case.
- Quoting the T-bR ceiling when grading a b-only model (forbidden by P3).

---

## 11. Instruments — to be built, and to be frozen WITH this document

**These do not exist yet.** The freeze commit must carry them.

| module | job | refusals |
|---|---|---|
| `build_rc4_cases.py` | build N / T-b / T-bR per case from the read-only benchmark clone; write `b^Delta` and `kDeficit`; install the `libs` entry insert-or-replace **with a `sys.exit(2)` check at every call site** | `sys.exit(2)` on: libs entry absent after insertion; a pre-existing time directory; a missing benchmark field |
| `rc4_extract_R.py` | run the frozen-RANS extraction for `AR_3_Ret_360`; read the `k`-reproduction drift for **all** cases from the extraction logs; apply **P-1** | `sys.exit(2)` on: drift line absent from a log; drift > 0.05 on a case being propagated |
| `rc4_onechange.py` | the **P1** recursive directory comparison, with the §6 `kDeficit` plant proving it can see a difference in that file | `sys.exit(2)` on: any difference outside `<time>/kDeficit`; the plant not being detected |
| `rc4_score.py` | run all three planted controls FIRST, then score, apply §8's completion clause, evaluate P0/P2/P3, emit the verdict from the fixed vocabulary | `sys.exit(2)` on: any plant direction failing; any completion clause failing; a continuity violation silently accepted |

**Every module: `--selftest` green under `python3` AND `python3 -O`,
`__pycache__` cleared before each. No `ast.Assert` carries any refusal, guard,
control or gate (§6.1).**

**No RC2 module is imported, called, edited or extended.** No file under
`Kaandorp2020_TBRF/aposteriori/` is edited, at any line, for any reason
(standing rule 6); `setup_case.py` and `frozen_R.py` are **read** for their method
and **re-implemented** here, not modified in place.

---

## 12. What this lane could NOT verify, stated plainly

1. **The `kDeficit_rms` = 3.6961887e+07 on `AR_1_Ret_360`** (§1.7), nine orders
   above `CBFS13700`'s 6.8e-03 and `PHLL10595`'s 5.9e-02. **This lane did not
   determine whether that is a units/normalisation artefact of the duct case or a
   real pathology in the extraction.** It is flagged for the supervisor. It does
   not change any registered threshold here, and P-1 gates the extraction on its
   `k`-reproduction drift rather than on this magnitude — but a reviewer should
   know the number exists.
2. **The `converged` field disagrees between artifacts on the very row §5's
   threshold is derived from.** `frozen_R_AR_1_Ret_360.json` records
   `AR_1_Ret_360__TRUTHR` as `"converged": false`, `"converged_iteration": null`,
   with `res_p_max_last500` = **1.0**, while `aposteriori/RESULTS.md` §2 prints the
   same row as `CONVERGED-residualControl` at 383 iterations. **This lane did not
   resolve that discrepancy and does not claim to.** Convergence-label
   reconciliation on preserved Kaandorp rows is **RC2's territory** (§0), and RC4
   takes RC2's labels as authoritative when they land. The 80% bar is set 18.3
   points below the 98.3% figure partly because its source row is not pristine, and
   **P0 is measured afresh on RC4's own runs under §8's completion clause
   regardless of what the preserved row's label turns out to be.**
3. **`AR_3_Ret_360` has no frozen-RANS extraction on disk**, so P-1's outcome on
   that case is genuinely unknown and its T-bR cost is a budget, not a measurement.
4. **All thirteen duct rows of the predecessor carry `"wall_s": -1.0`
   (`"resumed": true`)**, so no duct wall time from that campaign is a measurement.
   §9's duct rates come from the **frozenk** campaign on the same meshes and are
   labelled as a proxy.

---

*Drafted 2026-09-10 by a closure lane. **DRAFT / UNFROZEN. Nothing may run against
it.** The freeze is the closure-supervisor's act, after a personal §3 check-1.
Zero solver compute produced this document. Nothing sent, filed, uploaded,
registered, posted or commented. No RC2 file was edited or depended upon.*
