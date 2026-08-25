# VMFL051 — Isentropic Expansion of Supersonic Flow Over a Convex Corner: RESULTS

**NOT FILED ANYWHERE. Nothing in this document or the case it records is sent,
emailed, uploaded, filed, posted, registered or commented outside this box**
(CLAUDE.md rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). The manual is
proprietary Ansys documentation. **SUBMISSIONS PARKED.**

**This record does NOT revise the pre-registration.** `PREREGISTRATION.md` is frozen
and is not edited by this file (CLAUDE.md rule 6). Every gate, threshold, cap and
label quoted below is read *out of* that freeze, never back into it.

**Written 2026-08-25 by `ansys-lane-opus` (Opus 5) for the `ansys-verification`
team.** Run 1 of VMFL051. Manual: Ansys Fluid Dynamics Verification Manual, Release
2026 R1, **pp. 165–166** (title page verified against the PDF beside the sidecar per
CLAUDE.md rule 15 — PDF p. 1 and the `.txt` sidecar both read *"Ansys Fluid Dynamics
Verification Manual … Release 2026 R1, March 2026"*).

---

## 1. THE VERDICT

# `NOT A RESULT`

**Cost: 23.3167 core-minutes** (1399 wall s × 1 rank ÷ 60) of a frozen **28
core-minute** cap — 83.27 % used, cap never reached. **$0.019936 DERIVED, NOT
MEASURED**, at the owner-stated $0.0513/core-h (c7a.4xlarge); the box cannot read its
own billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**Two independent clauses of CLAUDE.md rule 5 each produce this verdict on its own.**
Either alone would be sufficient; both fired.

| # | clause | what fired |
|---|---|---|
| **1** | **rule 5 step 1** — any level not plateaued ⇒ `NOT A RESULT` | **L1 AND L2 both fail the frozen plateau clause.** Peak-to-peak of the `volAverage(Ma)` gate series over each level's last 20 % of rows: **L1 6.240e−03** (6.24× the frozen 1.000e−03 tolerance, over its last 339 of 1693 rows) and **L2 3.535e−03** (3.54×, over its last 673 of 3365 rows). Only **L3** plateaus, at **8.549e−04** (0.85× the tolerance, over its last 1343 of 6714 rows) |
| **2** | **rule 5 step 2** — triple `DIVERGENT`/`STAGNANT`/`OSCILLATORY`/`EXACT` ⇒ `NOT A RESULT` | The Roache triple is **`OSCILLATORY`**: R = **−1.348600**, negative because the level-to-level increments change sign (d32 = **+4.517908e−03**, d21 = **−6.092849e−03**). **No observed order exists and NO GCI IS QUOTED** — correctly, the three values are not monotone |

**The verdict is not softened, and no re-run is proposed in this document.** The
pre-registration fixed this order before any solver started (`PREREGISTRATION.md`
§6), and Amendment 1's reading table assigns this outcome to its row **(d)**: *"triple
not `CONVERGING` … Rule 5 step 2 already governs: `NOT A RESULT`, no GCI quoted, and
none of the readings above is available at all."* Readings (a), (b) and (c) — the
VMFL001-R2 pattern, the VMFL005 pattern, and indeterminate — are **unavailable** here
and none is claimed. `triple.f_extrapolated` and `triple.gci_fine` are both `null` in
the grading JSON, so ρ and dev_extrap are **not computable** and are not stated.

---

## 2. THE NUMBERS

All read from `verification/runs/ansys_verification/VMFL051/GRADING_VMFL051.json`
(and its human-readable twin `GRADING_VMFL051.stdout.txt`), at full precision, not
retyped from any brief.

### 2.1 The gate quantity, per level

Post-expansion Mach number, `volAverage(Ma)` over the frozen `gateZone` cellZone at
`endTime` = 7e−3 s, at all three levels of the refinement-2 family:

| level | cells | zone cells | **Ma** | dev vs manual target 3.2370 | dev vs closed-form exact | plateau ptp | plateau verdict |
|---|---|---|---|---|---|---|---|
| **L1** 120×52 | 6 240 | 112 | **3.2278606097** | −0.282341 % | −0.237380 % | **6.240e−03** | **FAIL** (6.24× tol) |
| **L2** 240×104 | 24 960 | 455 | **3.2233427020** | −0.421912 % | −0.377014 % | **3.535e−03** | **FAIL** (3.54× tol) |
| **L3** 480×208 | 99 840 | 1 816 | **3.2294355513** | **−0.233687 %** | −0.188704 % | **8.549e−04** | pass (0.85× tol) |

### 2.2 The gate as it would have read, had rule 5 permitted a gate reading

**It does not, and this section is bookkeeping, not a verdict.**

- **Gate value (L3, finest): `Ma = 3.2294355513`**
- **Reference: 3.2370** — the manual's printed target, Table .51.1, p. 166 (analytic
  Prandtl-Meyer)
- **Frozen band: ± 0.5000 % relative, at the finest level** (`PREREGISTRATION.md` §3.1)
- **Deviation: −0.233687 %** — **inside the band**, by a factor of 2.14

### 2.3 The closed-form exact value — DIAGNOSTIC ONLY, NEVER THE GATE

Declared as a diagnostic in `PREREGISTRATION.md` §3.2 before any compute, and it stays
one here:

- **Exact `M₂ = 3.2355411372251854`**, Prandtl-Meyer at **γ = 1.3990093734749485**,
  derived from the manual's **own** Cp = 1006.43 J/kg-K and MW = 28.966 — **not** the
  textbook 1.4 (at γ = 1.4 the exact value is 3.2368431056638847)
- **Deviation of the L3 value: −0.188704 %**, against a frozen diagnostic band of
  **± 0.25 %** — **inside**
- R_specific = 287.0423968275029 J/kg-K, from R_universal = 8314.47006650545

### 2.4 The Roache triple (ratio 2.0, Fs 1.25)

| quantity | value |
|---|---|
| coarse (L1) | **3.2278606097** |
| medium (L2) | **3.2233427020** |
| fine (L3) | **3.2294355513** |
| d32 (coarse − medium) | **+4.517908e−03** |
| d21 (medium − fine) | **−6.092849e−03** |
| **R** | **−1.348600** |
| **state** | **`OSCILLATORY`** |
| observed order p | **none — not defined for a non-monotone triple** |
| **GCI** | **NOT QUOTED**, and correctly so — the three values are not monotone |
| Richardson extrapolate | **`null`** — not computed, not quoted |

### 2.5 Controls — all three planted-zero controls FIRED (CLAUDE.md rule 3)

| id | reader under test | plant | read back | fired |
|---|---|---|---|---|
| **PZ-1** | gated `.dat` reader | +1.234e−03 Mach | 1.2339999999997353e−03 | **yes** |
| **PZ-2** | `Ma` **field** reader on disk | +7.77e−02 Mach | 7.770000000000010e−02 | **yes** |
| **PZ-3** | the reference computation itself | +5° turn | ΔM₂ = 0.30002701584152813 | **yes** |

**PZ-2 is the one this case most needed** and it is the one that fired on the real
99 840-cell `Ma` field: the field is **not uniform** (min 2.49999805, max 3.396358576,
mean 2.7006549026427984), which is what an expansion fan must look like and what a
false zero could not have produced. PZ-3's identity check returned the turn angle as
**14.999999999999972°** against the required 15°, so the root finder is solving, not
returning a constant. The run tree was **never modified** — every plant went into a
temporary copy.

### 2.6 Ansys's own reported values — CONTEXT ONLY, NEVER THE GATE

Fluent **3.2316** (ratio 0.9980); CFX **3.2354** (ratio 0.9995). **This box has no
Fluent and no CFX. Nothing in this record is a statement about Ansys**
(`ANSYS_VERIFICATION_CHARTER.md` §2); `VMFL051_FLUENT.cas` and `VMFL051_CFX.def` were
never opened or run.

### 2.7 Completion — strict, and it HELD at all three levels

All three levels satisfy CLAUDE.md rule 4 as the freeze's §8 states it, with its two
declared departures:

- **rc = 0** at all three (`RUN_RC.txt` per level)
- **exactly one `End` line** in each `log.rhoCentralFoam`
- **last time vs endTime** — DEPARTURE 1 as declared (`adjustTimeStep yes`): L1
  0.0070015301, L2 0.0069997882, L3 0.0069999107, all within maxDeltaT = 1e−5 of the
  7e−3 endTime
- **fields present** — this case's own declared list `T U p rho Ma`
- **`ExecutionTime` count == `Time` count**, both > 0 — DEPARTURE 2 as declared (the
  literal clause is a steady-iteration clause and cannot hold for an adaptive-step
  transient solver): 1693 / 3365 / 6714 steps
- **age guard**, STRICTER than the rule: dated from the latest mtime anywhere in the
  level's own `0/`, every endTime field strictly newer

**Both departures are declared on the face of the frozen pre-registration (§8), both
are tighter-or-equal rather than looser, and both were declared before the answer was
known.** Neither is a repair invented after the number existed.

**The declared inner-zone clause also passed** and is recorded because a failure would
have been a third independent route to this same verdict: at L3, |⟨Ma⟩_gate −
⟨Ma⟩_inner| / ⟨Ma⟩_gate = **2.284871e−04 = 0.0228 %**, against the frozen 1e−2 —
inside by a factor of 43.8. The gate zone and the inner zone agree, so the value is
not an artefact of where the zone edge was drawn.

---

## 3. THE MECHANISM — a diagnosis, stated as the leading candidate and NOT as established

**What is established:** the two coarse levels have not reached a steady plateau in
the sampling zone at endTime = 7e−3 s. That is measured, it is the frozen clause, and
it is clause 1 of §1 above.

**What is a candidate and is NOT claimed:** that this unplateaued state is the
**origin of the non-monotone triple**.

**The arithmetic that supports it.** The Roache triple asks whether the level-to-level
differences are discretisation error. Compare each difference against the residual
unsteadiness of the levels that produced it:

| | value | vs L1 ptp 6.240e−03 | vs L2 ptp 3.535e−03 | vs L3 ptp 8.549e−04 |
|---|---|---|---|---|
| **\|d32\|** (from L1, L2) | 4.518e−03 | **0.72×** | **1.28×** | — |
| **\|d21\|** (from L2, L3) | 6.093e−03 | — | **1.72×** | 7.13× |

**The level-to-level differences are the same order of magnitude as the coarse
levels' own residual unsteadiness** — d32 is smaller than L1's peak-to-peak and only
1.28× L2's; d21 is 1.72× L2's. A difference that does not exceed the wobble of the
signals it is differencing cannot be cleanly attributed to grid refinement. **On that
arithmetic, the triple is plausibly measuring transient noise rather than
discretisation error, and that is the leading candidate for the `OSCILLATORY`
classification.**

**Why it is not established, stated plainly:**

- The arithmetic is a **consistency argument, not a demonstration**. Differences of
  the same order as the noise are *consistent with* noise dominating; they do not
  prove it. A genuinely non-monotone discretisation error of this size would produce
  the same table.
- **L2 is the outlier, not L1** — the sequence runs 3.2279 (L1), 3.2233 (L2), 3.2294
  (L3), so the medium level dips **below both** its neighbours. Nothing here explains
  *why the middle level specifically*, and no mechanism for that is offered.
- **No time-refinement study was run**, and none was pre-registered. The frozen family
  refines space at fixed physical endTime (`PREREGISTRATION.md` §4.3). Whether a
  longer endTime would plateau L1 and L2 and restore monotonicity is **untested**, and
  this record does not assert that it would.
- **L3, which does plateau, is also the level closest to the exact value** (−0.1887 %
  against L1's −0.2374 % and L2's −0.3770 %). That is *suggestive* and it is not
  evidence — one level is not a trend.

**No re-run is proposed here and no endTime is recommended.** What a re-run would have
to establish, and what its pre-registration would have to freeze in advance, is the
supervisor's call, not this lane's.

---

## 4. THE DISCIPLINE WORKING AS DESIGNED — worth saying plainly

**The gate value sits inside BOTH bands.** L3's Ma = 3.2294355513 is inside the
frozen ± 0.5000 % gate band against the manual's printed target (−0.233687 %, by a
factor of 2.14) **and** inside the tighter ± 0.25 % diagnostic band against the
closed-form exact value (−0.188704 %). It is also inside the manual's own stated 3 %
accuracy goal (§1.3, p. 5) by a factor of **12.8**. On the number alone, this case
looks like a clean success.

**Rule 5 nevertheless makes it `NOT A RESULT`, and that is the point.** Two of three
levels never settled, so the lab does not know that the number it is holding is a
converged property of the discretisation rather than a snapshot of a still-moving
solution. A value inside its band, produced by a family that cannot demonstrate grid
convergence, is exactly the kind of number the rule exists to refuse — the case where
the answer *looks* right and the evidence for it is absent.

**A gate that could only ever confirm would be worth nothing.** This is the discipline
paying for itself: the pre-registration fixed the plateau tolerance at 1.0e−3 Mach and
the verdict order in rule 5's stated sequence **before** any of these numbers existed,
so neither could be chosen to fit them. Had the order been read the other way — gate
first, convergence second — this row would today be a `PASS`, and it would be
unsupported.

**And the rule's one-way property held.** CLAUDE.md rule 5: the gate can only turn a
`PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse. Here it did exactly
that, and no clause anywhere in the comparator can push in the other direction.

---

## 5. MANUAL DEFECT — the compressibility contradiction

**Recorded on the frozen pre-registration (§1a, Defect 1) BEFORE any compute**, so it
cannot be presented as a discovery that followed a number. Restated here because the
register's audit trail must carry it.

**VMFL051 contradicts itself on compressibility, on a single page.** Its *"Analysis
Assumptions and Modeling Notes"* (p. 165) reads, verbatim:

> *"The flow is steady, inviscid, and **incompressible**. Analytic expressions for
> isentropic expansion can be used to calculate the Mach number downstream of the
> corner."*

Its own *"Physics/Models"* line, **on the same page**, reads:

> *"**Compressible**, inviscid flow"*

The Material Properties line specifies *"Density: Ideal Gas law"*, and the case is a
Mach 2.5 → 3.24 isentropic expansion whose entire content is compressible. **The word
"incompressible" is wrong.**

**How wrong, quantified:** an incompressible treatment produces **no Mach change at
all** across the corner — M stays at 2.5 against a target of 3.2370, a deviation of
**−22.77 %**, failing the frozen 0.5 % gate by a factor of 45. The comparator's
`--selftest` fires exactly this arm. This lane modelled the flow as **compressible**,
per the Physics/Models line and per the case itself.

**Two further defects are on the frozen pre-registration §1a and are not re-derived
here:** Defect 2 (the printed target 3.2370 is not the exact Prandtl-Meyer value at
any γ consistent with the case — it carries ≈ 0.005 % of table-rounding error, and is
consistent with a two-decimal ν lookup) and Defect 3 (Table .51.2's value column is
headed *"Ansys Fluent"* under a *"Results Comparison for Ansys CFX"* section — a
copy-paste error, typographic, no numerical consequence).

**All three are `NOT FILED`.** Contacting Ansys, or anyone, is Sanaa's decision alone
(CLAUDE.md rule 7; `ANSYS_VERIFICATION_CHARTER.md` §8). They are drafted for the
supervisor's read toward `docs/NUMERICS_KNOWLEDGE.md` (family `N-AV`) and are not
appended by this lane.

---

## 6. PROVENANCE — the freeze, and that it is the file that ran

**The freeze was verified by hashing the file against the committed blob** (CLAUDE.md
rule 2), independently in this lane and not taken on report:

| artifact | blob sha | HEAD blob | recorded by the launcher |
|---|---|---|---|
| `PREREGISTRATION.md` | **`7dad56168d7ad7d599f92e05aa249a3014d0dc63`** | identical | identical |
| `grade_vmfl051.py` (the comparator) | **`acad1aff71da4a960045484f9e6f8470f8beccb7`** | identical | identical |

All three columns agree for both files. Each of the three per-level `RUN_RC.txt`
carries both blobs, so the binding is per level and not a single HEAD read.

**Zero compute preceded the freeze.** The pre-registration was frozen at commit
**`22249c82`** (2026-08-25T00:20:33Z); its **before-first-compute Amendment 1** — legal
under CLAUDE.md rule 2, and which altered no gate, threshold, cap or label — landed at
**`54d34542`** (00:25:34Z); the **first mesh was written at 00:25:59Z**. The freeze's
own §2b.1 condition was checked and not asserted: at 00:15:28Z
`verification/runs/ansys_verification/VMFL051/` did not exist and `find` beneath it
returned 0 files.

**The launcher's own guards** (`run_vmfl051.sh`): refuses to start into any
pre-existing level directory (rule 4's guard), refuses unless the pre-registration is
committed at HEAD, refuses if `topoSet` left either sampling zone empty, and enforces
the cap with `timeout`. None fired as a refusal; all three levels started clean.

---

## 7. COST, AND THE ESTIMATE-VERSUS-ACTUAL COMPARISON (CLAUDE.md rule 12)

**The calibration row is `C-50` in `docs/COST_CALIBRATION.md`**, landed in its own
commit. Summary here; the full attribution is in that row.

| | value |
|---|---|
| **pre-registered POINT estimate** | **11.3 core-min** (677 wall s), frozen `PREREGISTRATION.md` §9.1 |
| **pre-registered CEILING (the enforced cap)** | **28 core-min** |
| **ACTUAL, MEASURED** | **23.3167 core-min** — 1399 wall s × 1 rank ÷ 60, from `COST.txt`, corroborated level by level against the three `RUN_RC.txt` (L1 9 s / 0.1500, L2 207 s / 3.4500, L3 1183 s / 19.7167) |
| **ratio actual/predicted** | **2.0634×** |
| cap usage | **83.27 %** — the cap was **never reached** and no `CAP_EXCEEDED.txt` exists |
| **$ DERIVED, NOT MEASURED** | **$0.019936** at $0.0513/core-h, c7a.4xlarge, **reported-by-owner** |

**Attribution, in one line and expanded in `C-50`: the frozen solver estimate was
GOOD, and the 2.06× overrun is very largely CONTENTION, which is named separately and
is netted off neither the ratio nor the actual.**

- **Solver CPU, MEASURED: 534.52 s** (final `ExecutionTime`: L1 7.71 + L2 59.31 + L3
  467.50) against the freeze's combined solver + function-object allowance of 637 s —
  **ratio 0.839×, inside the estimate and in the conservative direction.**
- **CONTENTION: 864.48 s = 14.408 core-min**, the wall-minus-CPU gap, from other
  teams' jobs on a 16-core box. Evidence in
  `verification/runs/ansys_verification/VMFL051/CONTENTION.txt`: loadavg **68.38** at
  00:30:40Z rising to **75.84** at 00:34:52Z on `nproc = 16`, with two
  `buoyantBoussinesq*` at 99.9 % and five `tesseract` at 84–89 % — **none of them this
  case's**, and none touched (standing rule). Measured clock/exec by level: L1 **1.17×**
  (it ran at 00:26 before the load built), L2 **3.49×**, L3 **2.53×**.
- **WASTE: 0.000 core-min**, named separately per `COMPUTE_BUDGET_CHARTER.md` §6 and
  netted off nothing — no level failed, none restarted, none was capped, no re-run of
  any kind, and the comparator returned exit 0 on its first invocation.

### 7.1 INSTRUMENT DEFECT, disclosed — the cap unit and the enforcement unit are not the same unit

**The cap is denominated in CORE-MINUTES; it was enforced as a WALL-CLOCK
`timeout`.** For this run the two coincide **exactly**, and only because the run is
**serial**: at 1 rank, core-min = wall_s × 1 ÷ 60. The coincidence is arithmetic, not
design.

**On any parallel case they would not coincide, and the enforcement would be wrong by
a factor of the rank count** — a `timeout` of `cap_core_min × 60` seconds on an
8-rank job would permit **8× the registered budget** before firing. The correct
conversion is:

    timeout_seconds = cap_core_min * 60 / ranks

**This is recorded here, in the `C-50` calibration row, and in `CONTENTION.txt`
where it was first noticed, so it is fixed before this team runs its first parallel
case.** It changed nothing about this run's cap, verdict or numbers. Referred to the
supervisor; a change to `run_vmfl051.sh`'s cap idiom is not this lane's call.

---

## 8. ARTIFACTS — every number above cites one, and all are on disk and committed

Run root: **`verification/runs/ansys_verification/VMFL051/`**

| artifact | what it carries |
|---|---|
| `GRADING_VMFL051.json` | the machine record — every number in §2, at full precision |
| `GRADING_VMFL051.stdout.txt` | the human-readable grading transcript, same values |
| `COST.txt` | 1399 wall s, 1 rank, 23.3167 core-min, cap 28, point estimate 11.3, 00:49:24Z |
| `CONTENTION.txt` | the live load readings and the instrument note of §7.1 |
| `<level>/RUN_RC.txt` ×3 | rc, wall, ranks, core-min, cells, **and both frozen blobs**, per level |
| `<level>/log.rhoCentralFoam` ×3 | the completion evidence of §2.7 — `End`, step counts, `ExecutionTime` |
| `<level>/log.blockMesh`, `log.checkMesh`, `log.topoSet` ×3 | mesh construction and the non-empty sampling zones |
| `<level>/postProcessing/gateMach/0/volFieldValue.dat` ×3 | **the gate source** — the `volAverage(Ma)` series the value and the plateau clause are read from |
| `<level>/postProcessing/gateMachInner/0/volFieldValue.dat` ×3 | the inner-zone diagnostic series of §2.7 |

**The six `volFieldValue.dat` gate-source files match `.gitignore` and are invisible to
`git add`** — they were filed by explicit path via `git update-index --add`, which does
not consult the ignore rules. **This is `L-300`, encountered again on this case and
handled the same way.**

**What is on disk and deliberately NOT committed:** the OpenFOAM field data (the
per-time-directory `T`, `U`, `p`, `rho`, `Ma` volFields), ~51 MB across the three
levels. The graded numbers do not depend on re-reading them — every value in §2 comes
from the `.dat` series and the logs above, all committed — except **PZ-2**, which read
the L3 `Ma` field directly. PZ-2's firing is recorded in `GRADING_VMFL051.json`, and
the field itself remains on disk but **outside git**; if that run root is cleared,
PZ-2 becomes unreproducible from the repository alone. **Stated rather than glossed.**

Case definition (inputs): **`cases/ansys_verification/VMFL051/`** — `PREREGISTRATION.md`
(frozen, blob `7dad5616…`), `grade_vmfl051.py` (frozen comparator, blob `acad1aff…`),
`run_vmfl051.sh`, `case/` (the templated OpenFOAM tree), `.launch.log`.

---

## 9. WHAT THIS RUNG DOES NOT CLAIM

- **It does not claim a converged Mach number.** The value 3.2294355513 exists, it is
  inside both bands, and the family it came from cannot demonstrate grid convergence.
  It is **not** a lab result and is **not** a credential.
- **It does not claim an observed order of accuracy** for `rhoCentralFoam` on a
  centred expansion fan. The pre-registration said a first-order or fractional order
  would be reported as measured, whatever it was; **no order is measurable from a
  non-monotone triple** and none is stated.
- **It quotes no GCI**, because the three values are not monotone.
- **It makes no statement about Ansys, Fluent or CFX.** This box has neither solver.
- **It does not establish the mechanism** of §3 — that is a candidate with arithmetic
  behind it, and is labelled so.
- **It does not propose or authorise a re-run**, an endTime change, or any change to
  the frozen family. Those are the supervisor's calls.

---

## 10. REGISTER

Recorded as **row #4** of `verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md`,
verdict `NOT A RESULT`. **The register's credential count does not move** — only `PASS`
rows are credentials, and this is not one. It stays on the register honestly, with its
numbers, as a finding.
