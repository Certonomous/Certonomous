# PRE-REGISTRATION — VMFL034-R2: Particle Aggregation inside a Turbulent Stirred Tank

**DRAFT — NOT YET FROZEN.** Successor to the struck registration **VMFL034**
(freeze `f4f80b53`), which is **ungradeable** for three measured defects (`§R`).
The struck bytes are **NOT edited and NOT reverted** (CLAUDE.md rule 6, rule 10);
`f4f80b53` stands in history as a registration that could not produce a verdict.
This is a **new registration** that repairs the three defects while reusing the
struck case's **settled, forward-derived physics unchanged** (`§R.6`).

Drafted by `ansys-lane-opus48`, 2026-09-04 (`date -u` in the drafting invocation:
`Fri Sep  4 18:29:26 UTC 2026`). **This lane has frozen nothing, committed nothing,
run no graded solver, and touched no archive copy.** The supervisor performs
`SUPERVISION_CHARTER` §3 check 4 and freezes (the commit is the freeze).

---

## §R. WHAT R2 REPAIRS — the three struck defects, and the fix for each

The supervisor measured three defects in `f4f80b53` (struck). Each is repaired here.

**D1 — the registered triple could not be built from frozen material.** The struck
gate was a three-level size-group triple, but the freeze committed **only one**
instance (35 groups); the Wheeler-quadrature + Kumar–Ramkrishna feed generator that
would build the other two levels lived **only in scratch** — uncommitted, unpinned,
unhashable. Synthesising the missing levels from uncommitted code would put
gate-relevant feed inputs on an **unfrozen grading path** (rule 2).
**Fix:** R2 registers the **r = 2 (`N_g / 2N_g / 4N_g`) triple 16/32/64**, commits
the generator `gen_sizegroups.py` (pinned, `§D`) and the two templates it fills, and
commits **all three** grid+feed instances outright under `grids/{S1,S2,S3}/`. The
driver **stages those frozen instances**; nothing is generated at grade time.

**D2 — the comparator hardwired the wrong refinement ratio.** The struck comparator
carried `math.log(2.0)` and `rref = 2.0`, while the drifted spread it actually
graded (the 25-35-50 group spread) had ratios **1.4000 and 1.4286** — neither 2 nor
even constant, so every GCI it printed was invalid.
**Fix:** in `analyse_vmfl034_r2.py` the refinement ratio is a **parameter asserted
against the registered level list at grade time** — `assert_ratio()` reads the three
grids' class counts and **REFUSES (exit 2)** unless they give a *constant* ratio
equal to `RREF = 2`; `roache_triple` and `gci` take `rref` and use `log(rref)`. On
the registered 16/32/64 the ratio is exactly 2 and the GCI is valid.

**D3 — the frozen document contradicted itself about its own triple, and the feed
was unguarded.** The struck `§7` (its rule-5 statement) declared **`r = 2` on class
count, `N_g / 2N_g / 4N_g`**, while its `§B.4`/`§C.E` declared the non-constant
25-35-50 spread — an open gate question inside a freeze commit (`§11.2` forbids it).
And its comparator's `_assert_grid` checked only the diameters `d_i`, **never the
feed `value_i`** — a wrong feed would grade silently.
**Fix:** R2 honours `§7`'s own `r = 2` design (see `§7` below) and carries **exactly
one** triple, `16/32/64`, throughout. And the comparator gains a **feed-moment
guard** (`feed_moment_guard`): it reads the `value_i` from each grid's
`phaseProperties`, reconstructs the feed diameter moments, and **REFUSES** unless
they reproduce the archive feed (`§R.5`).

### §R.1 The triple decision — a real choice, defended with measured feed reconstructions

`§7` of the struck document (the section that exists to satisfy rule 5, made *up
front*) declared the triple as **`r = 2` on class count, `S1 = N_g`, `S2 = 2N_g`,
`S3 = 4N_g`**, precisely so Roache's observed order and GCI are **valid**. The
25-35-50 spread was a later drift *away* from that design (a ±10-group spread about
35, ratios 1.40 and 1.4286). **R2 restores `§7`'s constant-ratio design** and
selects the base by a measured a-priori check that consumed **no gate target** — the
Kumar–Ramkrishna reconstruction of the **archive feed moments** (inputs, not the
manual's outlet targets) on each `r = 2` family, classified by the actual Roache
classifier (`gen_sizegroups.py --selftest`):

| `r = 2` family (`N_g`-`2N_g`-`4N_g`) | feed-reconstruction Roache class (gated feed-shape limbs m1,m2,m4,m5) | triple cost (N²-anchored, medium 32 gr ≈ 8.4 core-h) | verdict |
|---|---|---|---|
| base 12 (12-24-48) | m4, m5 **DIVERGENT** (medium ≈ coarse, then fine drops) | ~24.7 core-h | **REJECTED** — would grade m4/m5 NOT A RESULT |
| base 10 (10-20-40) | all CONVERGING, orders scatter 1.7–3.8; coarse m5 residual +22 % | ~17.1 core-h | works, but coarse level marginally asymptotic |
| **base 16 (16/32/64)** | **all CONVERGING, observed order ≈ 2.0 uniformly** | **~43.9 core-h** | **CHOSEN** |
| base 20 (20-40-80) | all CONVERGING, m5 order 0.9 (marginal) | ~68.6 core-h | works, marginal order |
| base 25 (25-50-100) | all CONVERGING, order ≈ 2.3 | ~107 core-h | most robust, most expensive |

**Chosen: `16/32/64`.** Its feed reconstruction is CONVERGING on **all four**
gated feed-shape moments with a uniform observed order ≈ 2.0 — the cleanest
asymptotic signature of any candidate, meaning the coarse level (16) sits solidly in
the asymptotic range and the GCI will be trustworthy. The base-12 family (the
cheapest constant-ratio family) is **rejected on measurement**: its m4/m5 feed
reconstruction is DIVERGENT (a grid-alignment artifact where the medium level barely
differs from the coarse, then the fine drops hard). The base-10 family (the one `§7`
named for illustration) works but its coarse level is marginally asymptotic (order
scatter 1.7–3.8, +22 % coarse residual). This is a design choice, not a
transcription. (The non-chosen families are written in hyphen form deliberately, so
this document declares exactly ONE slash-triple level-set family, `16/32/64`, and one
refinement ratio, `r = 2` — the single-family/single-ratio self-consistency the
struck document violated with two incompatible triples at five separate lines.)

**The alternative that was declined: keep the struck 25-35-50 spread.** Cost
~35.5 core-h — comparable to `16/32/64` — but its ratios are **non-constant**, so
**no valid GCI exists**; the registration would have to DECLINE the triple with a
defended statement (as `VMFL072-R2` did, `VMFL024 §7` precedent) and report only the
finest level with an unbounded grid error. For a case whose entire value is a
**defensible discretisation verdict**, a valid GCI is worth the marginal cost. The
declined path is therefore rejected: it costs about the same and produces no
convergence bound.

### §R.6 WHAT SURVIVES INTACT — the settled physics, reused byte-for-byte

R2 changes **only** the size-group triple (D1/D3), the comparator's ratio assertion
and feed guard (D2/D3), the driver's environment sourcing, and the committed
generator. **Every physics input is byte-identical to the struck case's settled,
forward-derived setup** — the U/p/alpha/k/epsilon/T fields, the mesh
(`blockMeshDict`, `topoSetDict`), `fvSchemes`, `fvSolution`, `controlDict` (rescaled
`endTime = 25 s`, `deltaT = 1e-4`), the thermophysical and turbulence properties,
and every non-`sizeGroups` line of `phaseProperties` (β₀_OF = 2000, α₂ = 1e-2,
SchillerNaumann drag, single shared `velocityGroup`). These were copied from
`cases/ansys_verification/VMFL034/` at build time (reading the struck case, never
modifying it). The settled physics — verified twice by the supervisor and reused
without re-derivation — is documented in the struck registration and cited here by
path:

- **β₀ = 1 (m³/s) and feed moments `(1, 1.108, 1.39, 1.91, 2.8210001, 4.4229999)`**
  read independently from the shipped archive's plain-ASCII members
  (`cases/ansys_verification/VMFL034/PREREGISTRATION.md §5a`), **not** back-calculated
  from the target. Two forward a-priori checks (consuming no target): **m3 conserved
  exact** (feed 1.91 = target 1.910) and **m0 closes** (`50 m0² + m0 − 1 = 0` →
  0.131774 vs 0.132, −0.171 %).
- **τ = 100 s** from the manual's own `V = 0.01 m³`, `Q = 1e-4 m³/s` (`§5`).
- **The kernel convention is the source-verified net `−½β₀n²`** (`§B.5`,
  `populationBalanceModel.C:671`, death `:334-341`, birth `:274-286`).
- **The dictionary kernel `β₀_OF = β₀_ref/α₂`** (declared unit conversion; OF's
  sectional number density `N = α₂ f/(κ d³)` is α₂-scaled); `Da = β₀·m0_feed·τ = 100`
  from archive + manual inputs only (`§C.A`).
- **m0 is DEMOTED to a calibration limb** because choosing β₀_OF to set Da *sets* m0
  by construction; the gate is **m1, m2, m3, m4, m5** (`§C.B`). Retained verbatim in
  the comparator (`GATE_LIMBS = [1,2,3,4,5]`, `EXPECT_M0 = 0.131774`, refuse > 3 %).
- **The similarity rescale** (walls 6.06/6.00, inlet 0.10, τ → 5 s, β₀ → 2000,
  `endTime` 25 s) with **Da preserved exactly** and **well-mixedness MEASURED**
  (`CoV(m0) ≤ 0.10`, comparator refuses) (`§C.C`).
- **The frozen-flow departure closed by construction** (dilute α₂, constant drag
  diameter, single shared `velocityGroup`) (`§3a`, `§C.D`).
- **Nominal, not SI units** — size range O(1) over [0.45, 22.0] (`§B.4`, Ruling 4).

### §R.7 UNMEASURED-INPUT MAGNITUDES AND THE FINE-LEVEL RISK — named before the freeze

The supervisor's resume noted that VMFL072-R2 graded NOT A RESULT because an
**off-equilibrium inlet perturbation of ±30 % had been chosen for plausibility with
no stability argument**, and that both VMFL046-R2 and VMFL072-R2 died at their
**finest level** for instabilities the coarse levels suppressed. Both bear on R2 and
are addressed here rather than discovered at 66 % of a clock.

**(a) R2 carries NO off-equilibrium perturbation.** The inlet is a **steady feed** at
the rescaled operating point; there is no ±X % perturbation, no relaxation factor
chosen for plausibility, and no initial patch beyond the feed composition itself
(`internalField = value_i`, the domain initialised at the feed — a benign,
equilibrium-consistent state). The VMFL072-R2 failure mode has **no analogue** in
this setup.

**(b) The one magnitude that IS a pre-compute estimate, named:** the well-mixedness
threshold **`CoV(m0) ≤ 0.10`** (`§C.C`, comparator `WELLMIXED_COV_MAX`). It is a
pre-compute estimate of when the rescaled box is "mixed enough" to be a CMSMPR at 300
recirculations/residence. It is a **run-time refusal gate, not a gate the verdict can
be tuned against**: if the box proves only marginally mixed, the successor **raises
`U_w/U_in`** (more recirculations, more steps) and **never relaxes the threshold**
(`§C.C` condition 4). Named as an unmeasured input; contained by refusal, not by
adjustment.

**(c) The fine-level (S3 = 64 groups) failure-mode question, answered as far as it
can be.** There is **no thin-film-style floor to collapse** here — the VMFL046-R2 /
VMFL072-R2 deaths were a film `h_min → h₀` diagonal collapse, a mechanism absent from
a volume-fraction sectional population balance. The coalescence source's stiffness is
set by the reaction time `1/(β₀_OF·N) = 1/(2000·1e-2) = 0.05 s ≫ Δt = 1e-4 s`
(`§C.D`), which is **independent of the group count** (β₀_OF and total number are
fixed by the rescale, not by `N_g`), and the tail-truncation break
(`populationBalanceModel.C:673`, at `d_max = 22`) is identical across levels. **What
DOES grow with `N_g` is the size of the coupled scalar system** (64 transported
`f<i>` fields at S3 vs 16 at S1), so a slower or stalling fine-level solve cannot be
excluded a-priori. **This residual risk is CONTAINED, not waived:** the per-level cap
`S3 = 4014 core-min` (2× estimate) stops a fine-level stall at rc 124 → the level
grades **NOT A RESULT** (rule 12/rule 5), and the strict-completion + well-mixedness
refusals catch a partial or pathological fine solve — the campaign is bounded by the
level cap, exactly as the supervisor directed. If S3 grades NOT A RESULT for a stall,
the honest completion state is NOT A RESULT with the fine-level cost reported, not a
verdict read off S1/S2 alone (rule 5 forbids reading the gate below the finest
CONVERGING level).

---

## §0. CLEAN-SLATE ASSERTION (CLAUDE.md rule 2 — the condition, and how it was checked)

**NOT YET RUN. NO VMFL034-R2 SOLVER HAS EVER STARTED.** Every band, ratio, cap,
criterion and label below was fixed with no VMFL034-R2 number in existence. Checked
in the drafting invocation, 2026-09-04T18:29:26Z:

| condition | check | result |
|---|---|---|
| the run root does not exist | `test -e verification/runs/ansys_verification/VMFL034-R2` | **RUN ABSENT** |
| the register carries no VMFL034-R2 row | `grep -c VMFL034-R2 verification/credentials/ansys/ANSYS_VALIDATION_REGISTER.md` | **0** |
| no VMFL034-R2 graded run exists | `find verification/runs -iname '*VMFL034-R2*'` | **0 hits** |

Before first compute, amendments to this file are legal and must state the condition
and how it was checked, naming the run directory
`verification/runs/ansys_verification/VMFL034-R2/` that **does not exist**. After
first compute, dated addenda only (rule 2).

---

## §1. SOURCE (unchanged from the struck registration; CLAUDE.md rule 15)

Ansys Fluid Dynamics Verification Manual, Release 2026 R1, **printed pages 121–122**
(PDF pages 135–136), verified against the PDF at
`docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf`
in the struck registration (`cases/ansys_verification/VMFL034/PREREGISTRATION.md §1`).
The gate reference is the **analytical** Target column of Table .34.1:

| Moment | Target (analytical) | band (relative) |
|---|---|---|
| m0 | 0.132 | ± 0.76 % (CALIBRATION, Ruling B) |
| m1 | 0.225 | ± 0.76 % |
| m2 | 0.547 | ± 0.76 % |
| m3 | 1.910 | ± 0.76 % |
| m4 | 9.073 | ± 0.76 % |
| m5 | 53.797 | ± 0.76 % |

The Ansys Fluent (QMOM) column is context, **not** the gate. This is a
discretisation-vs-exact comparison (the struck `§2`, `§3`; supervisor ruled `SAME`,
PASS-capable, message `affe9dd93ab43580b`).

---

## §4. THE GATE (band and verdict rule — unchanged from the struck registration)

### §4.2 The band — relative, uniform ± 0.76 %

`tol = q + d`, both relative: `q = 0.379 %` (the reference's honest uniform relative
quantisation, `0.0005/0.132`) and `d = 0.379 %` (numerical allowance, set equal to
`q`, never larger). `tol = 0.758 % ≈ ± 0.76 %` on every gated moment. Derivation and
its "not fitted to pass" proof are in the struck `§4.3` and are unchanged. The band
was fixed with no VMFL034-R2 number in existence (`§0`).

### §4.4 The verdict rule (rule-5 ordered)

1. Strict completion (`§9`) fails on any level → **NOT A RESULT**.
2. Well-mixedness (`§C.C`) not met → **NOT A RESULT** (comparator refuses, exit 2).
3. Planted control (`§10`) or feed-moment guard (`§R.5`) does not fire → **NOT A
   RESULT** (no number produced; comparator refuses).
4. Any gated moment's size-group triple not `CONVERGING` → that moment **NOT A
   RESULT**; if any of m1–m5 is NOT A RESULT the case is **NOT A RESULT** (rule 5).
5. Otherwise, on the CONVERGING finest-level (S3 = 64 groups) values: **all five
   gated moments** m1,m2,m3,m4,m5 inside ± 0.76 % → **PASS** (GCI printed per moment);
   **any** outside → **GATE FAIL**. m0 is reported beside the gate against its
   a-priori value 0.131774; a miss > 3 % REFUSES, never licenses a PASS.

---

## §7. THE ROACHE TRIPLE REFINES THE SIZE GROUPS — `r = 2` on class count

> **THE GATED QUANTITIES' DOMINANT DISCRETISATION ERROR IS SIZE-GROUP TRUNCATION.
> THE ROACHE TRIPLE REFINES THE NUMBER OF SIZE CLASSES `N_g` AT A CONSTANT RATIO
> `r = 2`, THE SPATIAL MESH HELD FIXED.** This is the design the struck `§7`
> declared; R2 carries it with a single, self-consistent level family.

| level | class count | role |
|---|---|---|
| **S1** | `N_g` = 16 (coarse) | triple |
| **S2** | `2·N_g` = 32 (medium) | triple |
| **S3** | `4·N_g` = 64 (fine) | triple — the gate is read here |

The concrete family is **`16/32/64`** (r = 2 exactly on class count; `§R.1` defends
the base). The size range `[0.45, 22.0]` (nominal, Ruling 4) is held fixed across
levels. Per moment, at `Fs = 1.25` (rule 5): a triple that is not monotone gets no
GCI; a triple that is `DIVERGENT`, `STAGNANT`, `OSCILLATORY` or `EXACT` grades **NOT
A RESULT**; only `CONVERGING` moments are gate-eligible, read at S3 with GCI printed.
**The comparator asserts the ratio against the actual class counts (D2) and REFUSES a
non-constant triple.**

---

## §9. STRICT COMPLETION (CLAUDE.md rule 4) + AGE GUARD

Binding on every level (S1, S2, S3); comparator **refuses, exit 2**, on any failed
clause. `rc = 0` (captured **inside** the detached wrapper); a standalone `End` in
the **solver** log (`log.reactingTwoPhaseEulerFoam`, never `log.blockMesh`); last
written time == `endTime` (25); `alpha.air`, `U.air`, `p` and every
`f<i>.air.bubbles` present at `endTime`; and every `endTime` field **newer** than the
case's own `0/alpha.air` launch marker (the driver touches `0/alpha.air` **last** and
asserts it newest; refuses a pre-existing `0/` or time dir).

---

## §10. THE PLANTED CONTROL (CLAUDE.md rule 3) — designed against the reduction

The moment reduction is a weighted **sum over all N bins**, so a plant over the
**whole** reduction set cancels identically (a measured past failure). The comparator
therefore perturbs a **PROPER SUBSET** of bins (`PLANT_SUBSET = [8, 9]`, `PLANT =
3.21e-4`) in the outlet `f<i>` and requires the measured moment response to equal the
response computed from the frozen geometry the comparator holds
(`Δm_k = (α₂/κ)·PLANT·Σ_{i∈S} d_i^{k−3}`). `--selftest` proves three mutated readers
REFUSED (drop κ; wrong power `d²`; wrong moment power `d^{k+1}`), and the plant runs
on the **real** reader before any zero is trusted. **Refusal is exit 2 and writes no
grading number.**

---

## §R.5 THE FEED-MOMENT GUARD (D3) — the struck comparator never checked the feed

The comparator reads the sizeGroup `value_i` from each level's `phaseProperties`,
reconstructs the feed diameter moments (`n_i = value_i/(κ d_i³)`, `m_k = Σ n_i d_i^k`
normalised to `m0 = 1`), and **REFUSES (exit 2)** unless the feed reproduces the
archive moments, to these **registered tolerances**:

| moment | checked against | tolerance | why |
|---|---|---|---|
| m0 | archive 1.000 | `1e-6` | number normalisation (KR-conserved, level-independent) |
| m3 | archive 1.910 | `1e-3` relative | **volume conservation** — KR-conserved exactly at every N; a wrong feed breaks this |
| m1, m2, m4, m5 | the comparator's **independent** KR expectation on that grid | `5e-3` relative | fractional volume-moments carry the physical KR residual (level-dependent: +8 % on m5 at 16 groups → +0.2 % at 64); checking them against the archive *directly* would false-refuse a correct coarse feed, so they are checked against the comparator's own KR reconstruction |

`--selftest` proves a correct feed passes and a **mutated feed** (5 % of the volume
shifted one bin larger) is **REFUSED** (it breaks m3 conservation and the m1/m2/m4/m5
shape). This closes the exact gap the brief named: "a wrong feed would sail straight
through."

---

## §12/§C.E COST — the r = 2 triple 16/32/64

- **Method:** N²-anchored on the medium level (32 groups ≈ 8.4 core-h, from the
  struck case's measured 0.24 s/step × ~1.5e5 steps/level, conservative). The
  coalescence loop is ~N², so S1(16) ≈ 2.1, S2(32) ≈ 8.4, S3(64) ≈ 33.4 core-h.
- **Estimate:** **≈ 43.9 core-h** for the triple. **Derived $ = $2.25** at
  $0.0513/core-h (**derived, not measured** — the box cannot read its billing,
  `COMPUTE_BUDGET_CHARTER §5`). Well under the $25 pre-authorised per-run ceiling.
- **Cap:** **88 core-h RUNNING TOTAL** (2× estimate); per-level caps
  S1 = 252, S2 = 1004, S3 = 4014 core-min (2× each). An overrun **STOPS the run**
  (rc 124, rule 12); it does not get a new budget. (Pure-N² over-estimates growth —
  the fixed-cell flow solve does not scale with N — so the estimate is conservative.)
- **Estimate-vs-actual ratio:** PENDING the graded run; filed to
  `docs/COST_CALIBRATION.md` at process completion (rule 12).

---

## §15. THE OUTCOMES, NAMED IN WRITING BEFORE COMPUTE

1. **PASS** — all five gated moments inside ± 0.76 % at S3, all size-group triples
   CONVERGING, `§9`/`§10`/`§R.5`/well-mixedness satisfied. GCI printed per moment.
2. **GATE FAIL** — any of the five converged gated moments outside ± 0.76 % (with GCI).
3. **NOT A RESULT** — completion, well-mixedness, a size-group triple not CONVERGING,
   the plant or the feed guard failing.
4. **NOT A RESULT** (budget) — the `§12` cap fires.
5. **NOT A RESULT** (solver death) — non-zero rc; a non-zero rc is a finding, not a retry.
6. **BLOCKED** — the CLAUSE-B smoke fails for a reason that is not a physics result.

---

## §D. GRADING-PATH PIN — COMPLETED AT THE FREEZE, NOT DEFERRED

`git hash-object` yields a blob sha without committing, and writing it into *this*
file does not change the pinned files' shas. The queue row repeats this list verbatim
so the daemon can verify the pins without trusting this document.

| artifact | path | git blob |
|---|---|---|
| **grading_freeze** (comparator) | `cases/ansys_verification/VMFL034-R2/analyse_vmfl034_r2.py` | `7f2329485c2d33bd7bf053fc546c94191f979895` |
| pinned generator | `cases/ansys_verification/VMFL034-R2/gen_sizegroups.py` | `d5dfff4fdb500bb9911b8051b4bf04bb6f9a5950` |
| pinned template (phaseProperties) | `cases/ansys_verification/VMFL034-R2/templates/phaseProperties.template` | `144b69ef775e82fefdf6d5a25df98fcf8c9ae3a3` |
| pinned template (f field) | `cases/ansys_verification/VMFL034-R2/templates/f.template` | `c10243e0f6f1c64056e2780274b365aed37902cb` |

sha256 of the comparator's disk bytes:
`bbb221a31049c37a6522ceda8a9f204f618dfdccd9f39e0f735c32f25f5691b0`.

The driver `run_vmfl034_r2.sh` verifies these four pins on every launch (before any
compute), and verifies the staged case inputs against the case-inputs freeze commit
`FREEZE_COMMIT`, which the **supervisor sets at freeze** (a graded run REFUSES while
it is the placeholder — the freeze commit cannot exist before the freeze).

### §D.1 DISCLOSED: THE PHASE NAMES ARE TEMPLATE-INHERITED (unchanged from the struck case)

The dispersed phase is named **`air`** and the population balance **`bubbles`**,
inherited from the ESI `bubbleColumnPolydisperse` template. **There is no air and
there are no bubbles in this case** — they label the crystal/particle phase of a
CMSMPR aggregation problem. The field names `f<i>.air.bubbles` and `alpha.air` are
what the solver writes (`sizeGroup.C:46-60`) and what the comparator reads, so they
are load-bearing at the interface and are retained deliberately (renaming would
re-open the `§39.5` interface that struck VMFL072). Any record citing this case must
carry this note so a reader never infers that air was modelled.

---

## §17. FREEZE CLAIM

When the supervisor commits this file it freezes it **before the run, before the
data, and before the reading**: no VMFL034-R2 solver has run (`§0`), no VMFL034-R2
field data exists, and no VMFL034-R2 moment has been read by any comparator. The
grading path is fixed at the pre-registration commit and verified by hashing the
pinned comparator/generator/templates against their committed blobs before grading
(rule 2).
