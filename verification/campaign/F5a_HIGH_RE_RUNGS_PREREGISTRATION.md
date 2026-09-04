# F5a HIGH-Re RUNGS (Re 5000, Re 10 000) — PRE-REGISTRATION

**Status: DRAFT, NOT FROZEN. No compute may be launched under this document until it is
committed by cfd-supervisor (check 4, non-delegable). This lane drafted it and did not freeze it.**

| | |
| --- | --- |
| team | cfd |
| campaign | F5a — unsteady 2D cylinder Reynolds ladder |
| rungs registered | **Re 5000** and **Re 10 000**, in that order |
| classification | **NEW registration, SUCCESSOR to F5a's stop-ruling.** Not an amendment. See §1. |
| parent record | `verification/campaign/F5a_cylinder_reynolds_ladder.md` — **FROZEN EVIDENCE, untouched by this document** |
| drafted at HEAD | `f996344ffa3db2997886580e8887ccece430c029` |
| drafted | 2026-09-04T0137Z |
| compute spent under this document to date | **ZERO** |

---

## 1. Classification: why this is a NEW registration and not an amendment

Three findings decide it, each measured rather than assumed.

**(a) There is no prior frozen gate for these rungs to amend.** `F5a_cylinder_reynolds_ladder.md`
carries frozen gates for Re 1000, Re 2000 and Re 3900. For Re 5000 and Re 10 000 it carries **no
gate, no threshold, no cap and no label** — only a cost range (line 1226) and a reasoned
recommendation not to run (lines 1327–1371). An amendment needs an existing gate to amend; there
is none.

**(b) The parent record is frozen evidence and cannot receive the gate.** It is cited as evidence
**E6** in the **frozen** `verification/campaign/F5b_PHYSICS_PREREGISTRATION.md:112` by md5
`8348d1f7b27df90a5107d3f3bd28afb3`. This lane verified that hash **on disk and at HEAD — both
match**. Under rule 6 the file is never edited; writing a gate into it would break a frozen
registration's own evidence hash. The gate must therefore live in a separate document.

**(c) It is a SUCCESSOR, not a fresh start, because it must answer F5a's stop-ruling.** F5a
recommends: *"do not climb to Re 5000 or Re 10,000 next"* (line 1344), on two independently
established reasons. This document supersedes **one** of them and **explicitly does not supersede
the other**:

| F5a reason | status now | how established |
| --- | --- | --- |
| **Reason 2 — reference availability.** *"The rung above buys a weaker gate than the rung just completed."* | **STANDS, UNCHANGED.** Not superseded. | Re-checked by this lane 2026-09-04: no Dong, Karniadakis, Norberg or Williamson paper exists anywhere under `docs/papers/`. F5a's Unpaywall result (`is_oa: false` on both DOIs) has not changed and cannot be changed from inside the box (rules 7/8). **The literature point gate is therefore registered BLOCKED — see §4, G2.** |
| **Reason 1 — prioritisation.** *"The informative next step is the 3D rung, not a higher-Re 2D rung"* (line 1359). | **SPENT.** The stated alternative has been executed. | F5a's own operational record, lines 476–490: the Re 1000 3D `pilot` **completed** 2026-07-30 10:14:01 UTC, 44,102 s ClockTime, 8 ranks, reaching `endTime = 90.0` in full. F5a's recommendation was *"do not climb **next**"* — a sequencing call against a specific alternative. That alternative has been run. |

**This is the whole of the supersession, and it is deliberately narrow.** F5a's ruling was a
prioritisation between two candidate next steps; the step it preferred has been taken. Nothing in
this document reopens its reference-availability finding, and no threshold anywhere below depends
on a reference the lab does not hold. **No gate is widened to make these rungs passable** — the
opposite: §4 G3 pre-declares one of the ladder's four standing quantities **ungatable**, with the
measurement that forces it.

---

## 2. The registered ladder, established from disk

**Re 1000 → 2000 → 3900 → 5000 → 10 000 → 1e5 → 1e6.** Two independent on-disk sources, neither a
relay:

- `verification/campaign/F5a_cylinder_reynolds_ladder.md:3` — *"Ladder: Re 1000 -> 2000 -> 3900 -> 5000 -> 10,000 -> 1e5 -> 1e6. Each rung must pass its gate before the next starts."*
- `verification/runs/F5_runs/cylinder_ladder.py:3` (module docstring) — the identical sequence.

⚠ **The claim that "F5a spans Re 100–180" is REFUTED and must not be resurrected.** Re 100–180 is
the *prior work* this module reuses (`cylinder_ladder.py:8–9`: the O-grid generator validated
*"St within 0.7% of Roshko at Re=100-180"*). It is the provenance of the mesh generator, not the
span of this ladder.

### 2a. State of every rung, measured on disk 2026-09-04

Run artifacts live **outside git** at `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/`. The
git-tracked tree `verification/runs/F5_runs/` is a **harvested mirror** holding logs, `record.json`
and case inputs only. Reading the mirror alone misclassifies rungs — see §3.

| rung | mesh | solve | `record.json` | on-convention? | state |
| --- | --- | --- | --- | --- | --- |
| Re 1000 | 22,400 cells | complete | yes | yes (`first_cell` 0.00447) | **gated** (GATE REACHED, point) |
| Re 1000 coarsespacing | 22,400 cells | complete, **4 ranks** | yes | no — deliberate spacing control | spacing control |
| Re 2000 | 27,360 cells | **complete** | **NO — see §3** | yes (bit-exact) | **gated, banded** |
| Re 3900 | 44,000 cells | complete | yes | **NO** — `first_cell` 0.0035167, the kOmegaSST y+~1 value | superseded by its twin |
| Re 3900 corrected | 44,000 cells | complete | yes | yes (bit-exact) | **gated** (GATE REACHED, PROVISIONAL) |
| **Re 5000** | **not staged** | never | no | n/a | **NEVER RUN — registered below** |
| **Re 10 000** | **84,100 cells, staged 2026-07-29 23:23** | **never** | no | **yes (bit-exact)** | **NEVER RUN — registered below** |
| Re 1e5, Re 1e6 | no tree | never | no | n/a | out of scope here |

### 2b. Both rungs are registered, in ladder order — and why Re 5000 cannot be skipped

The ladder's own rule (`F5a:3–4`) is *"Each rung must pass its gate before the next starts."*
Re 5000 sits between Re 3900 and Re 10 000 and **has never been staged**. Registering Re 10 000
alone would skip a registered rung.

**Freezing this document commits to both rungs, in order.** Re 5000 first, Re 10 000 only after
Re 5000 grades. If the supervisor wants Re 10 000 without Re 5000, that requires an **explicit
waiver of the ladder's sequencing rule** and is a different document — this lane will not waive it
implicitly. Three reasons Re 5000 belongs in scope rather than being waived:

1. It is the ladder's own next rung.
2. It is cheap — **259.8–325.0 core-min** (§5), roughly a third of Re 10 000.
3. The primary gate (§4, G1) is a **trend** gate, and a trend gate is strictly stronger with the
   intermediate point than without it. Skipping Re 5000 would leave a 2.56× Re jump from the last
   measured rung.

---

## 3. ⚠ Re 2000 is NOT an abandoned rung — the census finding is corrected here

The census (`verification/campaign/CFD_NEVER_RUN_CENSUS_2026-09-04.tsv`) classified
`verification/runs/F5_runs/re2000` as meshed-and-abandoned. **Measured on disk, that is wrong**,
and this document corrects it rather than carrying it forward.

`/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re2000` holds a **completed solve**:

| evidence | measured |
| --- | --- |
| time directory | `90/` present, holding `U p phi uniform yPlus` |
| force history | `postProcessing/forceCoeffs1/0/coefficient.dat` — **10,191 data rows**, first `t=0.0044802867`, **last `t=90` exactly == `endTime`** |
| age guard | `0/U` 2026-07-29 02:16:07 → `90/U` 2026-07-29 03:22:51 — fields newer than the datum, guard **passes** |
| staged params | `first_cell` 0.00316227766016837939 — **bit-identical** to the laminar convention `0.01·sqrt(200/Re)`; `turbulence: laminar`; 27,360 cells |

**What is genuinely missing is `log.pimpleFoam`.** Consequences, stated exactly:

- Rule 4 **cannot be certified**: no rc, no `End` line, no `ExecutionTime`-count identity. The run
  cannot be called strictly complete.
- Under Sanaa's universal ruling (2026-08-26) that **bookkeeping never voids physics**, the loss is
  *infrastructure*, not physics. The `90/` fields and the force history are intact and the last
  time is exactly `endTime`.
- Re 2000's existing F5a gate — **GATED, BANDED, LOWER CONFIDENCE** — stands. It is not re-opened
  by this document.

**Registered disposition for Re 2000: NO COMPUTE. It needs a log-loss disclosure, not a run.** The
census's ~113 core-min estimate is moot; the rung already cost a measured **66.09 core-min**
(3,965.11 s serial).

⚠ **HAZARD — Re 2000 must NEVER be re-staged.** `run_rung.py:58` in `stage()` executes
`shutil.rmtree(remote_dir, ignore_errors=True)` **before** rebuilding. Pointing `stage` at `re2000`
would destroy the only surviving copy of a completed, gated rung whose log is already lost. This is
registered as a **hard prohibition**, not a caution.

> **HANDED UP, NOT ACTED ON.** Regenerating `re2000/record.json` from the surviving
> `postProcessing/` is zero-compute but **impossible with the current harvester**: `run_rung.py:90–91`
> raises `"no log.pimpleFoam ... solve did not run"` before it reads anything else. Repairing that
> means changing a script that produces a measured number, so this lane **stopped and did not touch
> it** (supervisor's standing instruction). A successor harvester at a new path is the rule-6-clean
> shape; the decision is the supervisor's.

*Minor, disclosed rather than smoothed:* F5a records re2000's history as **"10,204 rows"**; the file
holds **10,204 total lines, 13 of them `#` headers, so 10,191 data rows**. The prose figure is a
line count. No data defect; noted so a re-derivation is not mistaken for a change.

---

## 4. THE GATE — frozen before any run

Four quantities are in scope. **Three are gated, one is pre-declared ungatable, one is pre-declared
inapplicable.** Every threshold below is computed from lab measurements already committed to disk,
and no Re 5000 or Re 10 000 solve exists — so none of them can have been chosen to fit an answer.

### 4a. Which quantities may be gated, and the measurement that decides it

The Re 3900 matched pair (`re3900` vs `re3900_corrected`, a **55% first-cell change**, both
complete) is the lab's own direct measurement of which quantities are mesh-robust at the top of
this ladder (`F5a:1086–1096`):

| quantity | original | twin | change | gatable? |
| --- | --- | --- | --- | --- |
| Cd_mean | 1.7011 | 1.5806 | **−7.1%** | **YES** |
| −Cpb | 2.038 | 1.8967 | **−6.9%** | **YES** |
| Cl_rms | 1.3740 | 1.3292 | **−3.3%** | **YES** |
| **St** | 0.2409 | **0.1564** | **−35.1%, sign of the error FLIPPED** | **NO — see G3** |
| L_rec/D | none | none | unchanged | **inapplicable — see G4** |

### 4b. The convention-consistent series the gate is built on

⚠ **The trend is built on `re3900_corrected`, NOT `re3900`.** Only the corrected twin sits on the
laminar first-cell convention `0.01·sqrt(200/Re)`; the original carries the kOmegaSST-derived
spacing (`F5a:1030–1036`). Verified bit-exact by this lane:

| Re | staged `first_cell` | convention value | match |
| --- | --- | --- | --- |
| 1000 | 0.00447 | 0.00447213595499957976 | yes (record rounds) |
| 2000 | 0.00316227766016837939 | 0.00316227766016837939 | **exact** |
| 3900 (orig) | 0.00351667717684800646 | — | **OFF-CONVENTION** |
| 3900 (corrected) | 0.00226455406828919180 | 0.00226455406828919180 | **exact** |
| **10 000 (staged)** | **0.00141421356237309503** | **0.00141421356237309503** | **exact** |

Series values, all on the ladder's default `t ≥ 45` window, read from each rung's own `record.json`:

| Re | Cd_mean | −Cpb | Cl_rms |
| --- | --- | --- | --- |
| 1000 | 1.4651 | 1.6080 | 0.9666 |
| 2000 | 1.5879 | 1.8630 | 1.1837 |
| 3900 (corrected) | 1.5806 | 1.8967 | 1.3292 |

### G1 — PRIMARY GATE: internal trend continuation (no external reference)

The series shows the force quantities **decelerating sharply** between the last two rungs. Per Re
doubling: Cd went ×1.0838 then **×0.9952**; −Cpb ×1.1586 then **×1.0188**; Cl_rms ×1.2246 then
×1.1279. Two hypotheses are therefore distinguishable, and Re 3900 → 10 000 is **1.3585 doublings**:

| quantity | **H_plateau** (late rate continues) | **H_diverge** (early rate resumes) | **DISCRIMINATOR** (midpoint) |
| --- | --- | --- | --- |
| Cd_mean | **1.570** | **1.763** | **1.667** |
| −Cpb | **1.945** | **2.317** | **2.131** |
| Cl_rms | **1.565** | **1.750** | **1.658** |

**Frozen decision rule.** For each of the three quantities, at Re 10 000:
`value < discriminator` → **PLATEAU**; `value > discriminator` → **DIVERGENT**. Reported as a
3-tuple. Re 5000's values are recorded on the same axes and used to check the trend is smooth; the
Re 5000 discriminators are computed by the same formula at 0.3585 doublings **at grading time from
this frozen rule**, not re-chosen.

**Threshold for the verdict itself:**
- **GATE REACHED** — the run satisfies §6 completion in full, **and** Cd drift ≤ **10%** (the
  ladder's own standing stationarity gate, `run_rung.py:150`), **and** all three quantities are
  produced on the `t ≥ 45` window. The PLATEAU/DIVERGENT classification is then reported.
- **GATE FAIL** — run completes but Cd drift > **10%**: no trend statement is possible.
- **NOT A RESULT** — any §6 completion clause fails.

*Why this is falsifiable in both directions:* a plateau result says the 2D-laminar model's force
quantities saturate in the same Re range the real subcritical flow does (offset but structurally
parallel); a divergent result says the model departs from the real flow's own structure. Neither
outcome is the "good" one, so the gate cannot be satisfied by wishing.

### G2 — SECONDARY GATE: literature band — **BLOCKED for a point gate, BANDED and LOWER CONFIDENCE otherwise**

- **Point gate: BLOCKED — reference access.** Dong & Karniadakis (2005) DOI
  `10.1016/j.jfluidstructs.2005.02.004` and Dong et al. (2006) DOI `10.1017/S0022112006002606` are
  the correct Re 10 000 sources and are paywalled (`is_oa: false`, F5a:1335). **Verified by this
  lane 2026-09-04: neither is on the box, nor is Norberg or Williamson.** Obtaining them is
  outside the box and is **Sanaa's decision alone** (rules 7/8). This is a desk item, not a lab fix.
- **Band gate, registered as the weaker instrument it is.** Zdravkovich's subcritical band
  (**Cd ≈ 1.0–1.2**, **St ≈ 0.19–0.21**), via the same Lupi (2014) Fig. 3.3 / Zdravkovich (1990)
  chain F5a used at Re 2000, and whose stated range extends to Re ≈ 2–4×10⁴, so Re 5000 and
  Re 10 000 both sit inside it.
  **Pre-registered expectation, written now: Cd_2D over-predicts the band by +30% to +90%**,
  bracketing Re 2000's measured +32–59% and Re 3900's +54–109%. A result inside that bracket
  continues the established pattern; outside it is a finding.
  **Label, fixed: BANDED, LOWER CONFIDENCE — a model-deviation measurement, NOT a solver
  validation.** Identical in kind to Re 2000's and Re 3900's, and it is reported as no stronger.
- ⚠ **Registered caveat:** Williamson (1996) places Re 10 000 in the **shear-layer transition
  regime** (St gradually decreasing, base suction increasing), which is finer structure than a flat
  subcritical band resolves. The band is therefore used as a **coarse bound only**, and the St half
  of it is not used at all (G3).

### G3 — St is **NOT GATED**, pre-declared, with the measurement that forces it

**No threshold is registered for Strouhal number at either rung.** The Re 3900 matched pair
measured St moving **0.2409 → 0.1564 (−35.1%) under a 55% first-cell change, flipping the sign of
the error** against the 3D reference — confirmed independently by a Hann-windowed FFT as well as
the period detector (`F5a:1105–1126`). A quantity the ladder has measured to be non-reproducible
under its own mesh convention cannot carry a defensible threshold, and inventing a loose band to
accommodate it would be exactly the gate-widening this document is forbidden to do.

**St will be measured and reported at both rungs, with both estimators (period detector and
Hann-windowed FFT band), carrying NO PASS/FAIL.** Registered in advance so a later reader does not
mistake its absence from the verdict for an oversight.

### G4 — L_rec/D is **NOT APPLICABLE**, pre-declared, with its falsifier

At Re 3900 the mean recirculation bubble is absent on **both** meshes, and F5a established this as
physics rather than a spacing artifact (it survives the 55% first-cell change, `F5a:1072–1080`).

- **If absent again:** the registered label is **NOT MEASURABLE BY THIS METRIC ON THIS FLOW** —
  F5a's own established wording. **It is NOT a GATE FAIL.** An inapplicable gate and a missed gate
  are different outcomes and conflating them misleads (`F5a:748–752`).
- **Registered falsifier, stated now:** if a mean bubble **reappears** at Re 5000 or Re 10 000, the
  monotone-collapse reading (0.397 → 0.254 → none) is falsified and must be reported as such, not
  absorbed.

### Verdict labels, fixed

| outcome | label |
| --- | --- |
| §6 complete, drift ≤ 10%, three quantities produced | **GATE REACHED** — 2D-model deviation measurement, BANDED reference, LOWER CONFIDENCE. **NOT a solver validation.** |
| §6 complete, Cd drift > 10% | **GATE FAIL** (non-stationary) |
| any §6 clause fails | **NOT A RESULT** |
| literature point comparison | **BLOCKED — reference access** (standing, until Sanaa rules) |
| L_rec/D absent | **NOT MEASURABLE BY THIS METRIC ON THIS FLOW** |

---

## 5. COST — rule 12, mandatory

**Unit: core-minutes = wall seconds × ranks ÷ 60.** Dollars are **DERIVED at $0.0513/core-h**
(owner-stated) and are **DERIVED, NOT MEASURED** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER` §5).

### 5a. Measured anchors (all read from logs on disk by this lane, none relayed)

| rung | cells | steps | `ExecutionTime` s | ranks | **core-min** | µs/cell-step |
| --- | --- | --- | --- | --- | --- | --- |
| re1000 | 22,400 | 8,511 | 2,417.17 | 1 | **40.29** | 12.68 |
| re1000_coarsespacing | 22,400 | 8,276 | 706.35 | **4** | **47.09** | 15.24/rank |
| re2000 | 27,360 | 10,191 | 3,965.11 | 1 | **66.09** | 14.22 |
| re3900 | 44,000 | 13,838 | 10,899.37 | 1 | **181.66** | 17.90 |
| re3900_corrected | 44,000 | 14,446 | 11,625.02 | 1 | **193.75** | 18.29 |

The supervisor's anchor (re3900 → 181.7 core-min, serial) is **reproduced exactly**.

### 5b. Parallel efficiency — measured in-family, not borrowed

`re1000` (serial) vs `re1000_coarsespacing` (4 ranks, scotch), same 22,400 cells, same Re, same
solver: **0.284005 vs 0.085349 s/step → speedup 3.3276×, efficiency 83.2%**.
*Honest caveat:* the two cases differ in near-wall spacing (`first_cell` 0.00447 vs 0.0069416), so
per-step work is not bit-identical. This is still far better evidence than the 3D pilot's 75%
(measured on a 1.34M-cell 3D case inside its transient) and is the only 2D in-family parallel
measurement the ladder holds.

⚠ **Decomposing raises core-minutes while lowering wall time** — 40.29 → 47.09 core-min for the same
physics (+16.9%). Registered explicitly because core-minutes is the budgeted unit, so decomposition
is a real cost, paid deliberately to clear the wall-time and timeout problems in §5e.

### 5c. Projection — two independent methods, agreeing

**Method A — F5a's own mandated range.** F5a:1223–1225 instructs that remaining rungs be quoted as
a **range spanning n = 0.7 to 1.6** (cost ~ Re^n), because its exponent was measured non-monotonic
(0.985 → 0.714 → 1.515). From the re3900 anchor:

| rung | serial band (n=0.7 … 1.6) | 4-rank wall | **core-min** | $ derived |
| --- | --- | --- | --- | --- |
| Re 5000 | 12,970 … 16,220 s (3.6–4.5 h) | 3,898 … 4,874 s | **259.8 … 325.0** | $0.222 … $0.278 |
| Re 10 000 | 21,070 … 49,170 s (5.9–13.7 h) | 6,332 … 14,776 s | **422.1 … 985.1** | $0.361 … $0.842 |

*This reproduces F5a:1226–1227 ("Re 5000 ~13,000-16,000 s; Re 10,000 ~21,000-49,000 s") exactly —
an independent confirmation of the parent record, derived rather than copied.*

**Method B — mechanistic, fitted on the measured rungs.** Steps ~ Re^0.3571 (8,511 → 19,370 at
Re 10 000) and µs/cell-step ~ Re^0.2534 (12.68 → 22.73; the per-step cost genuinely rises with Re as
the pressure solve stiffens). With the staged 84,100 cells:
**84,100 × 19,370 × 22.73 µs = 37,020 s serial (10.28 h)** → at 4 ranks **11,125 s wall (3.09 h)**
= **741.7 core-min, $0.634 derived.**

Method B sits inside Method A's band, upper-middle. **Registered central estimate for Re 10 000:
741.7 core-min.**

⚠ **The census's ~347 core-min for Re 10 000 is the very bottom of the band** (it corresponds to
20,820 s serial ≈ the n=0.7 edge). It was correctly labelled a floor, and it is one — the central
estimate is **2.1× larger**. Registered so the cap is not set from the floor.

### 5d. Registered caps — an overrun STOPS the run

Caps are set at the **n = 1.6 upper bound plus a 15% contention allowance**, because the box is
measurably oversubscribed (§5e):

| rung | central | **CAP (core-min)** | cap $ derived |
| --- | --- | --- | --- |
| Re 5000 | ~292 | **400** | $0.342 |
| Re 10 000 | 741.7 | **1,150** | $0.983 |
| **total** | **~1,034** | **1,550** | **$1.325** |

Both rungs are far under the $25 pre-authorisation. **They are costed anyway** — a blanket is not a
per-item reading (rule 9).

**Rule 12 calibration is mandatory at completion of each rung**: actual core-min from the log
against the estimate above, ratio actual/predicted, gap attributed (contention / waste /
misprediction, waste named separately), landing as a row in `docs/COST_CALIBRATION.md`. A
completion report without it is incomplete.

### 5e. Decomposition — registered rank count, and why not more

**Registered: 4 ranks, `scotch`, `decomposePar`.**

- ⚠ **The brief's "8 of 16 vCPUs busy" is REFUTED by measurement.** At 2026-09-04T0132Z the box
  carried **load average 21.37 / 23.64 / 23.66 on 16 vCPUs** — already **~134–148% oversubscribed**.
  The consumer is a foreign 8-rank `buoyantBoussinesqSimpleFoam` on
  `verification/runs/T-family/T3_runs/R_fx` (mpirun pid 342265, 8 workers at ~99.5% each, ~7.5 h
  elapsed). Memory is not a constraint: 27 GB of 30 GB available.
- **4 ranks, not 8.** 8 would take every nominally-free core, collide with the T-family job the
  moment it rebalances, and land ~10,500 cells/rank where communication starts to dominate a 2D
  case. 4 ranks gives ~21,000 cells/rank and is the count for which this ladder has a **measured**
  efficiency.
- 4 ranks is also the rank count `cylinder_ladder.py:14` names for the larger meshes
  (*"MPI-parallel staging capped at 4 ranks"*). ⚠ **That cap is a docstring claim only — `--ranks`
  defaults to 1 and nothing in the code enforces it.** Registered as an assertion to be checked at
  launch, not relied on (rule 14: a lesson is not applied until every call site asserts it).
- ⚠ **Contention will inflate core-minutes.** The 83.2% efficiency was measured on a quieter box.
  Any gap is attributed to **contention** in the §5d calibration row and is **not** absorbed into
  the misprediction term.

### 5f. ⚠ Two wall-time traps, registered rather than discovered

1. **`solver_timeout` defaults to 28,800 s** (`cylinder_ladder.py:576`). The Re 10 000 **serial**
   central estimate is **37,020 s — the default timeout would kill the run before it finished.** At
   4 ranks (11,125 s) it fits comfortably. **Registered: 4 ranks is required, and `--solver-timeout`
   must be set explicitly to 20,000 s** (≥ the n=1.6 4-rank bound of 14,776 s, with margin).
2. **Both rungs exceed rule 12's 3,600 s stall threshold at every rank count this box can offer** —
   Re 10 000 at 4 ranks is ~11,125 s wall, and even a hypothetical perfect 8× would be 4,628 s.
   **This is pre-declared: a >3,600 s row for these rungs is EXPECTED, not a stall.** Registering
   the expected wall time in advance is what prevents a false stall finding at grading.

---

## 6. GUARDS — pre-existing state, age guard, completion

### 6a. Pre-existing-state guard — both directories already hold a mesh

Rule 4's guard refuses a case where `0/` or a time directory already exists. Both registered
directories currently hold `0/` (`U`, `p`) and a `constant/polyMesh`, staged **2026-07-29**.
Measured state of `re10000`: `0/U` and `0/p` at 23:23:38, `polyMesh/points` at 23:23:39,
`log.checkMesh` at 23:23:41, **no time directories other than `0`, no `processor*` directories, no
`log.pimpleFoam`.**

**Registered handling: Re 10 000 MUST be re-staged, never launched in place.**

- `run_rung.py` `stage()` line 58 executes `shutil.rmtree(remote_dir, ignore_errors=True)` **before**
  rebuilding. Re-staging is therefore **destructive and complete**: it deletes the whole run
  directory and rebuilds `0/`, `constant/`, `system/` and the mesh from scratch. The rebuilt case has
  a fresh `0/` and **no** time directories, satisfying rule 4's guard **by construction** rather than
  by inspection.
- Re 5000 has no directory at all and is simply staged.

**Pre-stage assertion (zero cost, and it is F5a's own lesson at lines 1310–1320 —
*"comparing the staged `stage_params.json` against the rung's own convention before launch, which
costs nothing"*):** the existing `stage_params.json` must be compared against the registered
parameters **before** anything is deleted. **This lane has already run that check on Re 10 000 and
it PASSES:**

| param | staged | registered | |
| --- | --- | --- | --- |
| `reynolds` | 10000.0 | 10000.0 | ok |
| `nu` | 0.0001 | 0.0001 | ok |
| `turbulence` | **laminar** | laminar | ok — **no kOmegaSST fork** (the L-11 trap that caught Re 3900) |
| `first_cell` | 0.00141421356237309503 | 0.01·sqrt(200/10000) | **bit-exact** |
| `cells` | 84,100 | 145 × 145 × 4 | ok |
| `n_radial` / `n_tangential` | 145 / 145 | 145 / 145 | ok |
| `farfield_diameters` | 20.0 | 20.0 | ok |
| `end_time` / `dt0` / `max_co` | 90.0 / 0.001 / 1.5 | 90.0 / 0.001 / 1.5 | ok |

**The existing Re 10 000 mesh is clean and on-convention.** It was staged at 23:23 on 2026-07-29,
*after* the Re 3900 spacing defect was found, and it does **not** carry the defective
kOmegaSST-derived `first_cell`. The re-stage is therefore for **freshness and provenance, not
correction** — it is expected to reproduce an identical mesh, and the post-stage assertion is that
it does (`cells == 84100`, params equal to the table above).

### 6b. Age guard — which file dates the run

**This family has no `0/T`.** It is incompressible laminar `pimpleFoam` with `U` and `p` only. The
thermal-family datum does not exist and must not be looked for.

**Registered datum: `case/0/U`, with `case/0/p` as the check-twin.**

- `stage()` rewrites `case/0/` on every stage, so `0/U`'s mtime **is** the stage time, and the mesh
  is rebuilt in the same call — mesh and datum share one timestamp, so there is no old-mesh /
  new-fields mismatch.
- Registered assertion: **`mtime(90/U) > mtime(0/U) > mtime(freeze commit of this document)`.**
- ⚠ **The third clause is the load-bearing one.** The first two are satisfied *trivially* if the run
  is launched against the 2026-07-29 mesh in place: `0/U` would be dated 2026-07-29, any `90/`
  written today would be newer, and the guard would pass while proving nothing. **The age guard is
  a freshness test, not a provenance test.** Requiring `0/U` to postdate the freeze commit is what
  ties the artifacts to this frozen document and defeats a silent regrade against 2026-07-29
  material. Re-staging is what makes the guard informative at all.
- *Worked precedent:* Re 2000's own guard passes (`0/U` 02:16:07 → `90/U` 03:22:51) — and its `0/U`
  postdates its first staging because the 02:16 relaunch re-staged. Same mechanism.

### 6c. Completion — rule 4, all-or-nothing, spelled out for this family

A rung is complete only if **every** clause holds:

1. **rc = 0**, captured **inside** the detached wrapper — ⚠ never around the `setsid` line, which
   returns 0 for every outcome.
2. **`End` line** present in `log.pimpleFoam`.
3. **last `Time =` == `endTime` == 90.0.**
4. **Fields present in `90/`: `U p phi uniform`** — this family's set. **Not** the thermal
   `T U p_rgh alphat nut k omega`.
5. **`ExecutionTime` line count == step count** (~19,370 at Re 10 000).
6. **Age guard** per §6b, all three clauses.
7. **`log.pimpleFoam` copied back to the git mirror BEFORE any cleanup.** ⚠ This is the exact clause
   Re 2000 failed (§3), and `run_rung.py:90–91` refuses to harvest without it. Losing the log costs
   the rung its rule-4 certification even when the physics is intact.

⚠ **Registered defect in the harvester, disclosed not repaired:** `run_rung.py:126–130` takes the
**last** `ExecutionTime` in the log *"regardless of how many restarts contributed"* — so a restarted
run is silently absorbed and its wall time under-reported. **These rungs are registered as
single-shot: no restart. If one is restarted, the run is `NOT A RESULT` under this document** and a
successor registration is required. This lane did **not** modify the harvester (supervisor's
standing instruction on measured-number scripts).

### 6d. Planted-zero control (rule 3)

The three gated quantities are read from `postProcessing/forceCoeffs1/0/coefficient.dat` via
`parse_coefficient_history`. **Registered requirement: before grading, plant a known perturbation
into a copy of the coefficient history, read it back through the same path, and refuse if the
reader cannot see it.** A zero — or a null `Lr/D` (§4 G4) — from a reader not shown able to see a
non-zero is not evidence. ⚠ **The ladder's current harvest path carries no planted-zero control**;
building one is a comparator change and is **handed up, not taken** by this lane.

---

## 7. Instrument gaps found while drafting — handed up, not acted on

Each of these touches a script that produces or grades a measured number. **This lane stopped at
every one of them** per the supervisor's standing instruction.

| # | gap | where | consequence |
| --- | --- | --- | --- |
| 1 | Harvester refuses without `log.pimpleFoam` | `run_rung.py:90–91` | Re 2000's `record.json` cannot be regenerated from intact artifacts (§3) |
| 2 | **`Cl_rms` is not stored in `record.json`** | `run_rung.py:133–152` | G1 gates on Cl_rms, but the record carries `cl_band` (peak-to-trough envelope) instead. **A comparator must compute Cl_rms, and one must exist before grading.** |
| 3 | Restart absorption | `run_rung.py:126–130` | wall time under-reported after a restart; §6c registers single-shot to avoid it |
| 4 | 4-rank cap is a docstring, not an assert | `cylinder_ladder.py:14` vs `:574` | nothing prevents a 16-rank launch on an oversubscribed box |
| 5 | No planted-zero control on the force-history reader | harvest path | §6d |

⚠ **Gap 2 is on the critical path.** G1's primary gate cannot be graded until a comparator that
computes `Cl_rms` on the `t ≥ 45` window exists and is itself frozen. **This document registers the
gate; it does not supply the instrument.**

---

## 8. What this document does NOT claim

- It does **not** overturn F5a's reference-availability finding. The Re 10 000 point gate stays
  **BLOCKED**.
- It does **not** claim these rungs validate the solver. Both are **model-deviation measurements**
  against a **banded** reference, **LOWER CONFIDENCE**, and are labelled so in advance.
- It does **not** gate St, and says why with the measurement (§4 G3).
- It does **not** assert the 2D-laminar model is adequate at Re 10 000. `cylinder_ladder.py:11–13`
  records the opposite view — *"a laminar solve is not defensible up there"* for Re ≥ 3900. The
  ladder runs laminar deliberately, to hold one variable per rung; that choice makes these rungs a
  **measurement of model inadequacy**, which is what the gate is written to capture.
- It does **not** freeze itself. Freezing is the supervisor's check 4.

---

## 9. Ready-to-freeze checklist

| item | state |
| --- | --- |
| Ladder established from disk, not relay | §2 — two independent on-disk sources |
| "Re 100–180" claim refuted | §2 |
| Classification decided with evidence | §1 — new registration, successor; parent md5 verified on disk **and** at HEAD |
| Gate, thresholds, cap, label all fixed before any run | §4, §5d |
| No gate widened; one quantity pre-declared ungatable | §4 G3 |
| Cost in core-minutes, re-derived from the anchor | §5 — two methods agreeing |
| Dollars labelled derived, not measured | §5 |
| Decomposition registered with measured efficiency | §5b, §5e |
| Pre-existing mesh handled | §6a — re-stage, destructive by construction; params verified bit-exact |
| Age guard datum named and its weakness closed | §6b — `0/U`, plus the postdates-freeze clause |
| Completion clauses enumerated for this family | §6c |
| Census correction recorded | §3 — Re 2000 is not abandoned |
| Blocking instrument gap flagged | §7 gap 2 |
| **G1's anchor sourced, the series put on ONE definition** | **§10 (Amendment 1)** — was the open blocker |

---

## 10. AMENDMENT 1 — 2026-09-04, cfd lab-lane. THE G1 ANCHOR IS SOURCED, AND §4b's SERIES IS ON THREE DIFFERENT DEFINITIONS

**Legality, stated with the condition and how it was checked (rule 2, pre-compute clause).** This
document is **not frozen** (its own line 3 says so) and **no compute has been spent under it**.
The condition was checked by naming the run directories that do not exist:
`/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re10000/90` — **absent**, the tree holds only
`0/ constant/ system/ log.blockMesh log.checkMesh` and no `log.pimpleFoam`, no `postProcessing/`;
and `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re5000` — **the directory does not exist at
all**. Both verified on disk 2026-09-04T15:0xZ by this lane. Amendments are therefore legal, and
this one changes a threshold — after first compute it would not be.

**This amendment does not widen any gate.** It corrects an input the gate is computed *from*, and
the correction moves the Cl_rms discriminator by **+0.13%**.

### 10.1 ⚠ 1.3292 IS SOURCED. It is not the statistic §4a's column header says it is

The supervisor withheld the freeze because §4b's Re 3900-corrected anchor **1.3292** could not be
reproduced from the surviving artifact under any definition swept, the closest being **1.337205**
(−0.59%). **It is reproducible.** Measured by this lane two ways that agree:

| route | value | vs 1.3292 |
| --- | --- | --- |
| this lane's own independent computation from `re3900_correctedspacing/postProcessing/forceCoeffs1/0/coefficient.dat` (14,446 rows), trapezoid time-weighted, **about ZERO**, `t ≥ 45` | **1.329197** | **−0.0002%** |
| `verification/runs/F5_runs/analyse_f5a_cl_rms.py --census`, column `rms\|zero,time` | **1.329177** | −0.0017% |

**1.3292 is the trapezoid TIME-WEIGHTED RAW root-mean-square of `Cl` ABOUT ZERO on `t ≥ 45`.**
It is *not* the fluctuation rms about the mean, and *not* the sample-weighted rms. The
supervisor's 1.337205 is the **`about=mean, weighting=sample`** cell of the same census — a real
statistic, correctly computed, and a different one. Nothing was fitted to an answer; two of the
four definitions simply differ by 0.6% on this rung, because `cl_mean = 0.0696` is not zero.

### 10.2 ⚠ THE DEFECT THIS EXPOSED: §4b's four numbers use THREE DIFFERENT DEFINITIONS

Each of §4a/§4b's quoted values was matched against all four self-consistent definitions on the
`t ≥ 45` window. **No single definition produces all of them.**

| rung | §4b quotes | definition it actually is | error |
| --- | --- | --- | --- |
| Re 1000 | 0.9666 | `about=mean, weighting=sample` (0.966578) | −0.002% |
| Re 2000 | 1.1837 | `about=zero, weighting=sample` (1.183735) | +0.003% |
| Re 3900 orig | 1.3740 | `about=zero, weighting=time` (1.373980) | −0.001% |
| Re 3900 corrected | 1.3292 | `about=zero, weighting=time` (1.329177) | −0.002% |

Every one matches *something* to within 0.003% — so these are transcriptions of correctly computed
numbers, not arithmetic errors. **But G1 is a TREND gate, and a trend computed across a series
whose members are three different statistics is not a trend.** That is the real defect, and it is
larger than the one that stopped the freeze.

### 10.3 REGISTERED: ONE definition, named, and the series restated on it

**Registered grading definition: `--about zero --weighting time`.** Chosen on two grounds fixed
before any Re 5000 or Re 10 000 value exists:

1. It is the definition that **reproduces the ladder's own last anchor** (§10.1), so the
   registration and the parent record stay on one axis.
2. It matches the weighting of **every other statistic this ladder reports** — `cd_mean`,
   `cl_mean`, `cd_band`, `cpb` all come from `time_weighted_stats`, trapezoidal, because the time
   step is adaptive. A sample-weighted rms silently over-weights the small steps.

**§4b's Cl_rms column is STRUCK and replaced by this one** (Cd_mean and −Cpb are unaffected: they
were already time-weighted and this lane reproduced §4's discriminators for both — Cd 1.6668
against the quoted 1.667, −Cpb 2.1309 against 2.131):

| Re | Cl_rms (`zero,time`, `t ≥ 45`) | §4b had |
| --- | --- | --- |
| 1000 | **0.964543** | 0.9666 |
| 2000 | **1.181602** | 1.1837 |
| 3900 (corrected) | **1.329177** | 1.3292 |

### 10.4 G1's Cl_rms row, RE-DERIVED — the change is +0.13%

By §4's own frozen formula (ratios per Re doubling; 1000→2000 = 1 doubling, 2000→3900 = 0.96347,
3900→10 000 = 1.35845), unchanged:

| quantity | H_plateau | H_diverge | **DISCRIMINATOR** |
| --- | --- | --- | --- |
| Cd_mean (unchanged) | 1.570 | 1.763 | **1.667** |
| −Cpb (unchanged) | 1.945 | 2.317 | **2.131** |
| **Cl_rms — STRUCK 1.565 / 1.750 / 1.658** | **1.5691** | **1.7512** | **1.6601** |

**The Cl_rms discriminator moves 1.658 → 1.6601, +0.13%.** The decision rule itself is
**unchanged**: `value < discriminator` → PLATEAU, `value > discriminator` → DIVERGENT.

### 10.5 REGISTERED: the definition-sensitivity check, because 1.27% is not zero

Computed under all four definitions the Cl_rms discriminator spans **1.6572 … 1.6784** — a spread
of **1.27%**, against a H_plateau→H_diverge gap of **±5.48%**. So the definition choice cannot
invert the classification *unless the measured value lands within ~1.1% of the discriminator*.

**Registered now, before any value exists:** at grading, the Cl_rms classification is computed
under **all four** definitions. If all four agree, the classification is reported. **If they do not
all agree, that axis reports `INDETERMINATE — DEFINITION-SENSITIVE`, with all four values and all
four discriminators printed beside it.** This is not a widened gate: it adds no way to pass, it
removes a way to report a classification the evidence does not support. Cd_mean and −Cpb are
single-definition quantities and are unaffected.

### 10.6 The instrument for gap 2 EXISTS — and it closes the instrument half only

`verification/runs/F5_runs/analyse_f5a_cl_rms.py` (741 lines, sha256 `788d70c00adda1f9…`, git blob
`8dd000160d950e868d726c3cf0bb4d32af182254`, **UNTRACKED at the time of this amendment**) computes
Cl_rms on the `t ≥ 45` window and **refuses (rc 2) unless both `--about` and `--weighting` are
given** — precisely because the registration did not fix them. Run by this lane 2026-09-04:

- `--selftest` → **rc 0, "ALL CONTROLS GREEN"**: 16 planted controls, including an analytic
  sinusoid recovering `A/√2`, a square wave (where `band/rms = 2`, not `2√2`), pre-window garbage
  in every plant, and **two mutations that correctly drive the suite red** — substituting the
  `cl_band` envelope, and ignoring the `about` axis.
- `--census` → reproduces the ladder's stored `cl_band` for all five rungs beside all four rms
  definitions.

**With §10.3 naming the pair, the comparator's refusal is satisfied and §7 gap 2 is closed as an
instrument gap.** ⚠ It is **NOT closed as a registration item until the file is committed and this
document pins it by blob sha** — rule 2 fixes the grading path at the pre-registration commit and
requires the frozen file to be hashed against the committed blob. **Committing and pinning it is
part of check 4 and is the supervisor's, not this lane's.**

### 10.7 Re-measured facts that supersede or confirm earlier readings

| item | §-reference | re-measured 2026-09-04 | disposition |
| --- | --- | --- | --- |
| `re10000` is staged-and-never-solved | §2a | `0/U`, `0/p`, `constant/polyMesh`, `system/`, `log.blockMesh`, `log.checkMesh`, **84,100 cells**; **no `90/`, no `log.pimpleFoam`, no `postProcessing/`**; birth certificate `verdict: clean`, max aspect ratio 3.917, max non-orthogonality 6.16e-06, max skewness 0.0132 | **CONFIRMED** |
| box load 21.37 / 23.64 / 23.66 | §5e | superseded. `journalctl --list-boots`, read by this lane: boot −1 ended **2026-09-04 07:45:19 UTC**, boot 0 began **14:50:22 UTC** — an outage of **7 h 05 m 03 s**, independently confirming the supervisor's reading (the *"34 minutes idle"* trigger is his and was **not** re-derived here). At 15:13Z load was 38.69/22.13/10.86 on 16 vCPUs, **dominated by this lane's own numpy analysis**; **no OpenFOAM process was running.** | **§5e's figure is STALE in BOTH directions. The rank count must be re-justified against a load reading taken at launch, not against §5e's and not against this one.** |
| estimate ≤ its own cap (supervisor's standing ruling) | §5c/§5d | Re 5000 central ~292 ≤ cap 400; its n=1.6 upper bound 325.0 ≤ 400. Re 10 000 central 741.7 ≤ cap 1,150; its n=1.6 upper bound 985.1 ≤ 1,150. Total central ~1,034 ≤ 1,550. | **PASSES — no row is barred from launching by that ruling** |
| re3900 cost anchor | §5a | `log.pimpleFoam` holds **13,838** `ExecutionTime` lines and an `End`; 10,899.37 s ÷ 60 = **181.656 core-min serial** | **CONFIRMED** |
| §5b parallel efficiency | §5b | re-derived independently: 2,417.17/8,511 = 0.284005 s/step serial vs 706.35/8,276 = 0.085349 s/step at 4 ranks → speedup **3.3276**, efficiency **83.19%** | **CONFIRMED to 5 s.f.** |
| µs/cell-step anchors | §5a | re-derived from `ExecutionTime ÷ (cells × steps)`: 12.679 / 14.221 / 17.901 µs at Re 1000 / 2000 / 3900 | **CONFIRMED** |
| Method B central estimate 741.7 core-min | §5c | independently re-fitted: steps ~ Re^**0.3565** (§5c says 0.3571), µs/cell-step ~ Re^**0.2529** (§5c says 0.2534) → 18,920 steps, 22.249 µs, **35,403 s serial**, 10,638 s at 4 ranks, **709.2 core-min** | **§5c's 741.7 is 4.6% HIGHER than an independent re-derivation — conservative, in the safe direction, and well inside the 1,150 cap. NOT changed.** |

### 10.8 ⚠ A DUPLICATE `re10000` TREE EXISTS IN GIT, AND IT IS NOT THE LAUNCH TARGET

`verification/runs/F5_runs/re10000/` holds `log.blockMesh`, `log.checkMesh`, `stage_params.json`
and **`case/0/{U,p}`, `case/constant/`, `case/system/` — physics one level down, under `case/`.**
It carries the **same 84,100-cell** checkMesh. It has **no `constant/polyMesh`**, so it is not
runnable; the runnable mesh is the out-of-git one. `stage_params.json` names
`"remote_dir": "/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re10000"`, so `stage()`'s
`shutil.rmtree` targets the **out-of-git** path. **Registered: the launch target is the out-of-git
directory; the git mirror is never a stage target.**

**The `case/`-one-level-down shape is the exact shape that defeated the obvious wiring of
`scripts/solve_evidence_guard.py` on F5c** — `find_solve_evidence()` scans only `target` itself,
`target/processor*` and `target/postProcessing`, and **does not recurse into `target/case/`**.
This lane therefore **ran the guard rather than reasoning about it**, on all seven candidate F5a
targets:

| target | guard on the target | guard on `target/case/` |
| --- | --- | --- |
| out-of-git `re10000` | reports SAFE | no `case/` subdir |
| out-of-git `re2000` | **REFUSES — 3 evidence items** | no `case/` subdir |
| out-of-git `re3900_correctedspacing` | **REFUSES — 3 evidence items** | no `case/` subdir |
| git `F5_runs/re10000` and `/case` | reports SAFE | safe |
| git `F5_runs/re2000` and `/case` | reports SAFE | safe |

**Measured conclusion: the guard's known non-recursion defect does NOT bite on F5a**, because the
git mirrors hold no physics at any depth and the out-of-git trees are flat. The guard correctly
refuses on both completed rungs, including §3's hazard case `re2000`. **This is a measurement, not
an assumption, and it does not repair the guard for other families.**

### 10.9 What THIS AMENDMENT could not verify

- **`re5000` is unverifiable by inspection because it does not exist.** Everything registered for
  it is projection from the other rungs.
- **The 1.27% definitional spread is measured on three rungs only.** Whether it stays that small at
  Re 10 000 cannot be known before the run; §10.5 is written so it does not need to be.
- **This lane did not commit the comparator and did not freeze this document.** Both are check 4.
- **§5b's 83.2% was re-derived and confirms**, but the caveat §5b itself states is untouched: the
  two cases behind it differ in near-wall spacing (0.00447 vs 0.0069416), so per-step work is not
  bit-identical and the figure is an in-family estimate, not a controlled scaling measurement.
- **No launch-time load reading exists.** §10.7 supersedes §5e's figure but does not replace it;
  the 4-rank justification must be re-checked against the box at the moment of launch.
- **No claim is made that `about=zero` is the physically better statistic.** It is registered
  because it reproduces the ladder's own anchor and matches the ladder's own weighting. A lab that
  preferred the fluctuation rms would register `about=mean, weighting=time` and get a
  discriminator of 1.6572; that choice is the supervisor's and either is defensible, **but it must
  be made before the run, not after.**

---

## 11. AMENDMENT 2 — 2026-09-04T15:44Z, cfd lab-lane. THE GRADING PATH IS PINNED BY BLOB SHA — and §1(b)'s parent-record hash has MOVED since drafting

**Legality, stated with the condition and how it was checked (rule 2, pre-compute clause).** This
document is **still not frozen** (line 3) and **still no compute has been spent under it**. The
condition was re-checked by this lane at **2026-09-04T15:44:11Z**, by naming the run directories
that do not exist — not by relaying §10's earlier check:

- `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re5000` — **the directory does not exist at all.**
- `/home/ubuntu/certonomous-runs/f5a-cylinder-ladder/re10000` — holds exactly
  `0/ constant/ system/ log.blockMesh log.checkMesh`. **No `90/`, no `log.pimpleFoam`, no
  `postProcessing/`.**

Amendments are therefore legal. **This one changes no gate, no threshold, no cap and no label.**
It fixes a grading path, restates a stale hash, and records two obligations that remain open.

### 11.1 REGISTERED: the grading path for G1's Cl_rms axis, pinned

Rule 2 fixes the grading path at the pre-registration commit and requires the frozen file to be
verifiable **by hashing it against its committed blob**. §10.6 left this open because the
comparator was untracked and an untracked file has no committed blob to hash against. It now has one.

| | |
| --- | --- |
| grading path | `verification/runs/F5_runs/analyse_f5a_cl_rms.py` |
| **git blob sha (THE PIN)** | **`8dd000160d950e868d726c3cf0bb4d32af182254`** |
| sha256 | `788d70c00adda1f9b7309107a25b523282dd2a4577b1de29b776a9119f1f4c0c` |
| size / lines | 33,117 bytes / 741 lines |
| commit | **`91cc2bfc1f9defd773b97c293a30491e90876ab5`** — the comparator alone, 741 insertions, **0 deletions, 1 path** |
| invocation fixed by §10.3 | `--grade --about zero --weighting time` |

**Registered verification, to be executed before grading and again at grading:**
`git rev-parse HEAD:verification/runs/F5_runs/analyse_f5a_cl_rms.py` **must equal
`8dd000160d950e868d726c3cf0bb4d32af182254`.** If it does not, the file that ran is not the file
that was pinned, and the run is **NOT A RESULT** under this document until a dated addendum
discloses what changed. This was executed against the committed tree at authorship of this
amendment and **returns the pinned sha**.

⚠ **The blob sha was verified at commit time, not assumed from §10.6's note.** §10.6 recorded
`8dd0001…` while the file was untracked; this lane re-hashed the file **before** committing, and
again **after** exercising it, and it was bit-identical both times. A changed instrument between
the note and the commit is exactly the failure pinning exists to catch, so it was checked rather
than carried forward.

### 11.2 The instrument was re-exercised by this lane, not relayed

Committing an instrument makes the committing lane its sponsor, so all 741 lines were read and the
comparator was run rather than believed:

| control | result |
| --- | --- |
| `--selftest` | **rc 0, "ALL CONTROLS GREEN"** — 3 analytic plants × 4 definitions, pre-window-garbage control (C-P4), envelope control (C-P3, the only one that can catch a `cl_band` substitution), 2 mutations that **correctly drive the suite red** (C-M1 envelope substitution, C-M2 `about` axis ignored), and `-O` parity (C-O1) |
| `--grade` with no `--about`/`--weighting` | **rc 2 — the registered refusal fires** |
| `--census` | reproduces the ladder's own anchors independently: `zero,time` = **0.964543 / 1.181602 / 1.329177**, and `mean,sample` at Re 3900-corrected = **1.337205** — i.e. **both** numbers in the disagreement §10.1 resolved are recovered here |
| bare `assert` count | **0** (L-332/L-475: `python3 -O` deletes every one) |

### 11.3 `scripts/check_comparator_freeze.py` — it APPLIES, and it returns NO VERDICT on this file

Run by this lane over the whole repository (203 graders in the population):

- The comparator **is in the walk population** — it sits under `verification/` and matches the
  `analyse_*.py` pattern; it appeared as **row 500** even while untracked, because the tool walks
  the disk.
- Its row is **`NO-MARKERS`** — *"no completion marker in this tree — out of evidence reach"*.
  `verification/runs/F5_runs/` carries **zero `DONE.*` completion markers** (measured), so the tool
  **cannot compare a commit date against a completion date and gives this comparator no freeze
  verdict at all.** Committing it does **not** turn that row `FROZEN`.
- The run's repository-wide `VERDICT: FAIL` (rc 3) is driven by **12 UNFROZEN + 4 AMENDED_AFTER**
  graders **elsewhere in the repository** — chiefly the T-family trees. **F5a contributes a
  `NO-MARKERS` row, not a violation.** ⚠ It is recorded here so that a later reader does not read
  that FAIL as F5a's, and does not read a green from this tool as certifying F5a either.

**Consequence, stated plainly: the blob pin in §11.1 is the ONLY instrument that fixes this grading
path.** The freeze checker is out of evidence reach here and cannot substitute for it.

### 11.4 The §10.4 re-derivation moves the discriminator by ARITHMETIC ALONE — verified, with a control

This was checked rather than accepted, because "the correction is small" is exactly how a widened
gate would be described. **§4's own formula** (ratios per Re doubling; 2000→3900 = 0.96347
doublings, 3900→10 000 = 1.35845) was re-implemented independently and pointed first at the
quantities the amendment claims are **unaffected** — those are the control:

| quantity | series used | this lane re-derives | §4 / §10 states | |
| --- | --- | --- | --- | --- |
| Cd_mean (control) | §4b, unchanged | **1.666816** | 1.667 / 1.6668 | reproduces |
| −Cpb (control) | §4b, unchanged | **2.130868** | 2.131 / 2.1309 | reproduces |
| Cl_rms, OLD mixed-definition series | §4b's 0.9666 / 1.1837 / 1.3292 | **1.657798** | §4's 1.658 | reproduces |
| Cl_rms, NEW `zero,time` series | §10.3's 0.964543 / 1.181602 / 1.329177 | **1.660133** | §10.4's 1.6601 | reproduces |

**The same formula, unchanged, reproduces §4's own three frozen discriminators from §4's own
inputs, and §10.4's from §10.3's.** The only thing that changed is the input series.
**NO TOLERANCE, BAND, THRESHOLD OR DECISION RULE WAS TOUCHED**, and none may be. H_plateau and
H_diverge re-derive as **1.569090 / 1.751177**, matching §10.4's 1.5691 / 1.7512.

*Two rounding disclosures, made rather than smoothed:*
- §10.4's **"+0.13%"** is computed against §4's **rounded** 1.658. Against the **unrounded**
  1.657798 the move is **+0.1409%**. Both are correct statements of the same arithmetic; the
  direction and the order of magnitude are unaffected, and neither figure enters a gate.
- §10.5's **"1.27%"** definitional spread: the endpoints **1.657176 … 1.678411** reproduce exactly.
  The spread is **1.281%** of the low end and **1.265%** of the high end. §10.5's conclusion is
  unchanged — the spread remains far inside the **±5.484%** H_plateau→H_diverge gap, so the
  definition choice can invert the classification only within ~1.1% of the discriminator, which is
  precisely the case §10.5 already routes to `INDETERMINATE — DEFINITION-SENSITIVE`.

### 11.5 🔴 §1(b)'s parent-record md5 IS STALE, and §1(b) also calls F5b "frozen" when it is NOT

§1(b) asserts the parent record `F5a_cylinder_reynolds_ladder.md` carries md5
`8348d1f7b27df90a5107d3f3bd28afb3` and that *"this lane verified that hash on disk and at HEAD —
both match"*. **That was TRUE when written and is FALSE now.** Measured by this lane:

| reading | md5 |
| --- | --- |
| at the drafting HEAD `f996344f` (§'s own "drafted at HEAD") | `8348d1f7b27df90a5107d3f3bd28afb3` — §1(b) was correct at authorship |
| on disk today, and at today's HEAD | **`a9c3d124644ca4e33413c18406794ba8`** |

**Cause, established rather than guessed.** Commit **`09cf6854`** (*"cfd BLOCKING FIX: the only
sanctioned repair for a lost solver log was the call that DELETED the physics"*) modified the parent
record between the drafting HEAD and now. Its shape was measured:

- `git diff --numstat` → **`116  0`** — **116 insertions, ZERO deletions.**
- The hunk header is **`@@ -1371,0 +1372,116 @@`** — a pure append at the foot, after the old last line.
- **`head -1371` of the file today md5s to `8348d1f7b27df90a5107d3f3bd28afb3`** — bit-identical to
  the whole of the pre-edit file.

**Disposition, and it is deliberately narrow:**

1. **Rule 6 was HONOURED.** The parent was extended by an appended amendment, not rewritten.
2. **Every line-numbered citation in this document still resolves to the same text** — 476–490,
   1030–1036, 1072–1080, 1086–1096, 1105–1126, 1223–1227, 1310–1320, 1327–1371, 1344, 1359 all sit
   inside the untouched 1–1371 prefix, spot-verified at 1344 and 1359. **No argument in §1, §2, §3
   or §5 is disturbed.**
3. ⚠ **But §1(b)'s sentence is now false as written, and freezing it would freeze a false
   verification claim.** **REGISTERED CORRECTION: the parent record's md5 at the freeze of this
   document is `a9c3d124644ca4e33413c18406794ba8`; the md5 `8348d1f7b27df90a5107d3f3bd28afb3`
   is the md5 of its first 1,371 lines**, which is what F5b pinned and what §1(b) verified.
4. 🔴 **SECOND ERROR IN THE SAME SENTENCE, and it is not a hash question.** §1(b) calls
   `F5b_PHYSICS_PREREGISTRATION.md` **"frozen"**. **It is not.** Its own line 3 reads
   *"Status: `PENDING` — DRAFT, NOT FROZEN, NOTHING LAUNCHED, supervisor read required before
   freeze."* §1(b)'s argument does not depend on F5b being frozen — the parent is frozen **evidence**
   on its own footing — but the word is wrong and must not be frozen into this document.
5. **HANDED UP, NOT ACTED ON:** `F5b_PHYSICS_PREREGISTRATION.md:112` pins E6 by
   `8348d1f7b27df90a5107d3f3bd28afb3`, which **no longer matches the whole file it names**. Because
   the change was append-only the pinned *content* is intact, but the pin as written cannot be
   verified by hashing the named file. **That is F5b's defect, in another document, and this lane
   did not touch it.**

### 11.6 REGISTERED: the rank count is decided by a LAUNCH-TIME load reading, not by any figure in this document

§5e's *"load average 21.37 / 23.64 / 23.66"* and §10.7's *"38.69 / 22.13 / 10.86"* are **both
stale and neither governs.** §10.7 established a **7 h 05 m 03 s** outage (boot −1 ended
2026-09-04 07:45:19Z, boot 0 began 14:50:22Z) that invalidates any reading spanning it.

**Registered pre-launch assertion, zero cost, and it is a hard precondition of launching either
rung:** immediately before `decomposePar`, a **fresh** load reading is taken and **recorded in the
run's own record**, and the rank count is justified against **that** reading. **4 ranks remains the
registered default** (§5e: the only rank count for which this ladder holds a *measured* 83.2%
efficiency, and the count §5f requires to keep the run under the 20,000 s `--solver-timeout`).
**Departing from 4 ranks requires a dated addendum naming the reading that forced it.** No figure
already written in this document may be used as that reading.

### 11.7 ⚠ §6d's planted-zero requirement is CLOSED FOR Cl_rms ONLY — it remains OPEN for Cd_mean, −Cpb and Lr/D

This is measured, not assumed. Of the seven Python modules under `verification/runs/F5_runs/`,
**exactly one contains a planted control: `analyse_f5a_cl_rms.py`**, the file pinned in §11.1. The
harvest path that produces `cd_mean` and `cpb` (`run_rung.py`, `gate.py`) plants nothing.

| §4 quantity | planted-zero control | state |
| --- | --- | --- |
| **Cl_rms** | `analyse_f5a_cl_rms.py`, C-P1…C-P5 + C-M1/C-M2, verified rc 0 by this lane | **CLOSED** |
| **Cd_mean** | none on the harvest path | **OPEN** |
| **−Cpb** | none on the harvest path | **OPEN** |
| **Lr/D (G4)** | none | **OPEN — and this one is the sharpest**, because G4's registered outcome is a **NULL** (*"NOT MEASURABLE BY THIS METRIC ON THIS FLOW"*), and rule 3 says a null from a reader not shown able to see a non-null is not evidence. §6d says so in its own words. |

**Registered:** §6d is a **grading-time** requirement, so it does not by itself bar the freeze — but
**two of G1's three gated quantities and the whole of G4 cannot be reported under rule 3 until a
planted control exists for them.** Building it is a comparator change; this lane **stopped and did
not take it**, exactly as §6d and §7 already direct. It is recorded here so the freeze is taken with
this open, not in ignorance of it.

### 11.8 §9's checklist, restated — what this amendment moves

| item | state after this amendment |
| --- | --- |
| G1's Cl_rms grading path fixed at the pre-registration commit and hashable against its committed blob (rule 2) | **CLOSED** — §11.1, blob `8dd0001…`, commit `91cc2bfc` |
| §7 gap 2 (no Cl_rms instrument) | **CLOSED** — instrument exists, is committed, is pinned, and was re-exercised by a second lane |
| §1(b)'s parent-record hash claim | **CORRECTED** — §11.5; the argument survives, the sentence did not |
| §5e's rank justification | **DEFERRED TO LAUNCH BY REGISTRATION** — §11.6 |
| §6d planted-zero, Cd_mean / −Cpb / Lr/D | **OPEN** — §11.7 |
| §7 gaps 1, 3, 4, 5 | **OPEN, handed up** — unchanged by this amendment |

### 11.9 What THIS AMENDMENT could not verify

- **Nothing about Re 5000 or Re 10 000 was verified**, because neither has run. Every projected
  number in §5 remains a projection.
- **The pin proves identity, not correctness.** `8dd0001…` guarantees the file that grades is the
  file that was registered. It does **not** guarantee the statistic is the physically preferred one
  — §10.9 already says the lab could defensibly have registered `about=mean, weighting=time` and
  got 1.657176 instead. That choice is the supervisor's and it is made at the freeze.
- **`check_comparator_freeze.py` gives this comparator NO verdict** (§11.3). Its silence here is
  out-of-reach, not a pass, and it is counted as such.
- **This lane did not verify the 116 appended lines of the parent record.** It verified only that
  they are appended and that the 1,371-line prefix is untouched. Whether that appended amendment
  says anything bearing on these rungs was **not** read, and is not claimed either way.
- **This lane did not freeze this document.** Freezing is check 4 and it is the supervisor's.
