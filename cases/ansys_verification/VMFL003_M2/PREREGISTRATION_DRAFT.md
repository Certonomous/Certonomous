# VMFL003-M2 — "Try Other Models": PRE-REGISTRATION **DRAFT** (NOT FROZEN)

**NOT FILED ANYWHERE.** Nothing in this document or the case it registers is sent,
emailed, uploaded, filed, posted, registered or commented outside this box (CLAUDE.md
rules 7 and 8; `ANSYS_VERIFICATION_CHARTER.md` §8). **SUBMISSIONS PARKED.**

**THIS IS A DRAFT. IT IS NOT FROZEN, IT IS NOT YET THE GRADING PATH, AND IT AUTHORISES
NO COMPUTE.** Written by `ansys-lane-opus48` (Opus 4.8), 2026-08-25, for the
`ansys-verification-supervisor` to correct, and — only by the supervisor personally,
after the four `SUPERVISION_CHARTER` §3 checks — to freeze and to unlock compute. **No
agent message is Sanaa's consent** (rule 9). This revision folds in the supervisor's
rulings of 2026-08-25 (three on the first pass, plus Sanaa's V/P ruling relayed the same
day); it does not restart.

**ZERO SOLVER/MESH COMPUTE HAS RUN FOR VMFL003-M2.** Checked in the drafting invocation:
`verification/runs/ansys_verification/VMFL003_M2/` does not exist. What HAS executed,
with **zero solver/mesh compute**: the two M2 comparators' `--selftest` (§4), on
in-memory fixtures, no mesh, no `simpleFoam`. HEAD at this revision recorded in the
committing invocation.

**Directive.** Sanaa, 2026-08-25, byte-exact: *"VMFL051 and VMFL003 try other models"*
and *"When a model doesnt work, try the other ones"* (spelling hers). The supervisor's
binding guard: each attempt is a separately-frozen registration with the turbulence
model as the registered variable; **every attempt is recorded whatever its verdict**;
the full slate is declared up front in fixed order and **all declared attempts are run
and reported regardless of what the first returns**; each model's "wrong" is defined in
advance; nothing but the model changes, or a coupled change is declared with its cost to
interpretation. Cycling models until one clears the gate would poison every credential
this register holds; this draft is built to make that structurally impossible.

**Run 1 (`kEpsilon` + `nutkWallFunction`) is not touched.** Its frozen
`PREREGISTRATION.md`, comparator and `RESULTS.md`, and all its run-tree artifacts, are
neither edited, cleared nor re-labelled. VMFL003-M2 is a NEW case id with its own tree,
comparators and register rows, and cites run 1 rather than revising it.

---

## 0. WHAT RUN 1 ESTABLISHED — two SEPARATE defects, and a review of its registration

**Defect A — the MODEL-LEVEL miss (substantive).** Δp = 20800.82 Pa is **−4.34 %** vs
the manual target 21744 Pa and **−4.55 %** vs closed-form Colebrook 21792.88 Pa — nearly
identical, so not a chart-read artefact of the target. Developed-region f_dev = 0.027147
is **−4.63 %** vs Colebrook, free of entrance/BC effects: **this lab's `kEpsilon` +
`nutkWallFunction` genuinely under-predicts developed turbulent pipe friction by ~4.6 %
at Re = 1.37×10⁴.** Δp is converged to **7.8 ppm** (L2→L3 = 0.161 Pa) while the wall
ladder (N_r = 3/4/5/6) moves it **1.7356 %** — the model/wall channel is ~2200× the axial
channel. This is the defect "try other models" targets.

**Defect B — the ITERATIVE-CONVERGENCE miss (procedural, SEPARATE).** All three levels
failed the residual leg (final initial residuals of p, Ux, k, ε each < 1e−8): L1/L2 4 of
4; L3 on **ε alone** (2.523e−8, by 2.5×). This is *why* the verdict was `NOT A RESULT`,
not `GATE FAIL`. It is a consequence of run 1's iteration counts (6000/8000/12000) being
too short (its own §4.5 declared them ESTIMATES; §7c/§11-item-5 registered the repair:
re-run longer as a NEW RUNG). **Fixing B does not fix A** — run 1's RESULTS states a
converged kEpsilon would return `GATE FAIL`, not `PASS`. §7 shows why fixing B is not a
confound.

**Review of run 1's frozen registration (reported, NOT edited):** (1) the y+ clause bound
only the AVERAGE — L3 minimum was 23.812, below the [25,65] floor, disclosed but unbound;
corrected in §8. (2) The Roache triple cannot yield a trustworthy order for this quantity
(predicted 6–45 Pa differences, actual 0.16/2.01 Pa → implausible p=3.64); this carries
forward and is pre-declared in §6/§9. (3) **The run-1 cost multiplier of 1.6 was wrong
against a measured ~2.66 and is confounded by a small-mesh overhead floor** — recorded
here because it feeds M2's cost estimate, which instead uses run 1's measured aggregate
rate 5.806e−6 s/(cell·iter) (§12).

## 1. THE INSTALLED MODEL SLATE — read from the library, not recalled

Selectable incompressible RAS models were read from `/usr/lib/openfoam/openfoam2606/src/
TurbulenceModels/` (the `makeRASModel(...)` instantiations compiled into the library
`simpleFoam` links), not from memory: `SpalartAllmaras`, `kEpsilon`, `RNGkEpsilon`,
`realizableKE`, `LaunderSharmaKE`, `kEpsilonPhitF`, `kOmega`, `kOmegaSST`, `kOmegaSSTSAS`,
`kOmegaSSTLM`, `LRR`, `SSG`, `EBRSM`, `GEKO`; incompressible-only nonlinear (self-
registering) `LienCubicKE`, `kkLOmega`, `ShihQuadraticKE`, `LienLeschziner`,
`LamBremhorstKE`, `qZeta`. Wall functions present: `nutkWallFunction` (run 1),
`nutUSpaldingWallFunction`, `nutUWallFunction`, `nutLowReWallFunction`, `nutkRoughWallFunction`,
and `epsilonWallFunction` / `omegaWallFunction` / `kqRWallFunction`.

## 2. THE KIND OF REFERENCE THE MANUAL GIVES — the V/P classification (Sanaa's ruling)

**Sanaa's ruling, 2026-08-25, byte-exact and unnormalised (typos and the doubled "for"
preserved, per the supervisor's instruction to reproduce it this way wherever cited):**

> *"a. Uphold b. Yes ansys manual is a public primary source, and it's fine that itll
> reach gate reach at best. Anything gate reached for for that team means we reached
> ansys, which is good enough."*

**What it settles.** (a) An exact/analytic reference scores **V** (code verification),
never **P**. (b) **The Ansys manual is a public primary source** — the proprietary
objection is closed; where a case's reference is genuinely **measured/experimental**, **P
can be green**. And **`GATE REACHED` is a DECLARED SUCCESS CONDITION for this team, not a
shortfall** — "reaching it means we reached ansys, which is good enough"; recorded here as
the campaign's stated acceptable ceiling.

**The reference taxonomy — the FOUR kinds, of which categories 2 and 4 are the
SUPERVISOR'S OPEN QUESTIONS arising from her ruling, NOT Sanaa's own words. No future
reader should mistake the supervisor's classification for hers.**

| kind | what it is | what it buys | example |
|---|---|---|---|
| **1 — CLOSED-FORM / EXACT** | analytic solution of the governing equations | **V** | VMFL005 Hagen–Poiseuille; VMFL045 oblique-shock relations |
| **2 — CORRELATION / EMPIRICAL FIT** | a curve fitted to experiment (Colebrook, Moody chart) | **SUPERVISOR'S OPEN QUESTION** (V or P) | **VMFL003 — THIS CASE** |
| **3 — MEASURED / EXPERIMENTAL** | a direct measurement | **P** (Sanaa's ruling b) | — |
| **4 — MANUAL'S OWN CODE OUTPUT** | a Fluent/CFX number with no independent reference | **NEITHER** (code-to-code) | VMFL010, next tranche |

**VMFL003's reference is category 2.** The manual (p. 19) derives the target Δp from a
friction factor *"determined … from Moody chart"* — the smooth-pipe Colebrook / Prandtl–
von Kármán correlation, a curve fitted to Nikuradse/Colebrook experiments. It is **not**
a closed-form solution of the RANS equations (so not cleanly category 1) and **not** a
measurement of this specific pipe (so not category 3).

**My reasoning on what category 2 buys, offered for the supervisor to rule and NOT
decided here.** My lean is **V**: (i) the manual frames it as a *calculation* from a
chart, not an experiment; (ii) it is not a measurement of this configuration, so a match
does not validate the model against nature directly; (iii) reproducing an accepted
engineering correlation is closer to verifying the solver+model against a reference than
to physical validation. **The honest counter** is that a correlation *encodes*
experiment, so run 1's measured −4.6 % miss is partly a physical-fidelity statement,
which leans P. **This is above my authority; it is the supervisor's open question, and if
it needs Sanaa it goes to her.** Category 4 (Fluent/CFX output) is likewise the
supervisor's open question and is flagged now because VMFL010 in the next tranche has
exactly that kind of reference — a row that quietly counted it P would rest on a false
sentence. **VMFL003's gate does not use the Fluent/CFX numbers (they are context only),
so category 4 does not touch this case; VMFL003's reference-kind field is category 2.**

**Consequence for VMFL003's attainable columns.** Because the reference is category 2
(not measured), **P is not available for VMFL003 regardless of the model** — Sanaa's
ruling (b) opens P only for measured references. **V may be buyable (open question).**
**HOLDS is moot (see §6).** The best attainable outcome for any model in this slate is
therefore **`GATE REACHED`**, which is Sanaa's declared acceptable ceiling.

## 3. THE DECLARED SLATE, IN FIXED ORDER — ALL RUN, WHATEVER EACH RETURNS

Fixed now, before any M2 number exists. **Every model is run and recorded; none is
dropped after seeing a number.**

| # | rung id | RASModel | 2nd var | wall fn | comparator | change vs run-1 config |
|---|---|---|---|---|---|---|
| **M2-A** | `VMFL003_M2_A_kEpsilon` | `kEpsilon` | ε | `nutkWallFunction` | `grade_vmfl003_m2.py` | **only endTime** (converge; baseline control, NEW RUNG per run-1 §7c) |
| **M2-B** | `VMFL003_M2_B_realizableKE` | `realizableKE` | ε | `nutkWallFunction` | `grade_vmfl003_m2.py` | **only the RASModel keyword** |
| **M2-C** | `VMFL003_M2_C_RNGkEpsilon` | `RNGkEpsilon` | ε | `nutkWallFunction` | `grade_vmfl003_m2.py` | **only the RASModel keyword** |
| **M2-D** | `VMFL003_M2_D_kOmegaSST` | `kOmegaSST` | **ω** | `nutkWallFunction` + `omegaWallFunction` | `grade_vmfl003_m2_omega.py` | RASModel **+ coupled ε→ω** (declared confound, §4) |

**CORRECTION to the first draft, surfaced explicitly.** The first draft claimed M2-B/C
reuse the frozen run-1 comparator byte-identical. **That was wrong.** The supervisor's
Ruling 1 (GATE REACHED ceiling), Ruling 3 (y+ minimum clause) and the endTime bump apply
to **all four** models, so all four are graded by a **new M2 comparator**
(`grade_vmfl003_m2.py`), not by run 1's frozen file. The run-1 comparator is cited as the
parent and is diffed against, never reused. This is the honest structure.

**Justification per model:** A `kEpsilon` — the same model as run 1, re-run only to clear
Defect B; the **control** that discharges the convergence defect and gives a clean
converged baseline so B/C/D are compared at the same converged state. B `realizableKE` —
variable C_μ and a realizable ε source; the usual next step when standard k-ε mispredicts.
C `RNGkEpsilon` — the strain-dependent R term in the ε equation. D `kOmegaSST` — the other
workhorse and the model most able to move wall friction (ω-based near-wall + eddy-viscosity
limiter); the strongest physical test of whether the deficit is a wall-treatment artefact,
included **despite** its coupled change precisely because dropping the most informative
model to dodge a comparator variant would be answer-directed.

**Considered and DEACTIVATED FROM THE COMMITTED SLATE, reasons stated so nothing is
silently dropped:** low-Re / integrate-to-the-wall models (`LaunderSharmaKE`,
`LamBremhorstKE`, `kkLOmega`, `nutLowReWallFunction`) need a viscous-sublayer mesh
(N_r~40–80, no wall function) — a mesh+wall confound, deferred to a separate `VMFL003_M3`
low-Re family; `SpalartAllmaras` (transports nuTilda, different wall approach) deferred;
RSM (`LRR`/`SSG`/`EBRSM`), `GEKO`, SAS/LM, nonlinear eddy-viscosity — larger confounds or
tuned/transition models outside the "standard model" reading, deferred. **The committed
slate is exactly {A,B,C,D}; extending it is a freeze-time supervisor decision, never a
lane decision after a number.**

## 4. THE TWO M2 COMPARATORS — built, selftested, ZERO COMPUTE (supervisor Ruling 2)

Both were built in this drafting phase and pass `--selftest` on in-memory fixtures with
**zero solver/mesh compute**. Neither is frozen; the supervisor reads each as a diff
(§3 check 1) and freezes.

- **`grade_vmfl003_m2.py`** (epsilon family: A/B/C). A **disclosed, itemized** derivation
  from run 1's frozen `grade_vmfl003.py`, with four deltas, all in the file's own header:
  (1) endTimes 6000/8000/12000 → **15000/18000/22000**, ladder → 18000 (DATA, fixes
  Defect B); (2) the **y+ MINIMUM clause** `min y+ ≥ YPLUS_MIN_FLOOR = 11.06` (§8);
  (3) the **GATE REACHED ceiling** — `gate_verdict()` returns `GATE REACHED` in-band, and
  the GCI is emitted as an axial-channel diagnostic explicitly labelled *not a
  certification* (§6); (4) the **repo-root class fix** (below). **The grading LOGIC —
  readers, `roache()`, the three planted-zero controls, the verdict ORDER — is unchanged.**
  `--selftest`: **63 checks, 0 failures** (run-1's 60 plus 3 new y+-floor checks, incl. a
  negative control that a face at y+ = 10 is caught and a check that run-1's L3 min 23.812
  *clears* the floor — proving the min clause is a tightening, not answer-fitted).
- **`grade_vmfl003_m2_omega.py`** (omega family: D). A **field-name-only** diff against
  `grade_vmfl003_m2.py`: **20 changed lines, of which 6 are the `epsilon`→`omega`
  substitution** (`FIELDS_REQUIRED`, the residual-leg `gated` list, the reason-string
  tuple, the `RESID_TOL` comment, the `check_residuals` docstring) and the remainder are
  self-identification (docstring family line, `case` label, `rel` path, selftest banner).
  **No grading-logic line changed;** gate, band, reference, all three plants, completion
  clauses and verdict order are byte-identical. `--selftest`: **63 checks, 0 failures.**

**The repo-root class fix (Ruling 2), applied here as the "next comparator fixes the
class" instance.** Run 1's `verify_frozen()` derived the repo root as
`dirname(dirname(dirname(__file__)))`, which resolves to `.../cases`, **not** the repo
root — it worked in run 1 only because `git rev-parse <commit>:<repo-relative-path>` walks
up to `.git` regardless of cwd, so the wrong cwd was still inside the repo. Both M2
comparators instead derive the root robustly: `git rev-parse --show-toplevel` from the
file's own directory. **The four existing frozen comparators still carry the latent fault;
it is disclosed, not edited (they are frozen), and this comparator fixes the class going
forward** (L-221/L-222 posture).

## 5. THE GATE, BAND AND DIAGNOSTICS — PROPOSED **UNCHANGED** FROM RUN 1

> **G-VMFL003-M2 (per model, at `L3_1000x5`): |Δp_lab − 21744| / 21744 ≤ 0.025 (2.5 %).**
> Δp_lab = ρ·(areaAverage(p)_inlet − areaAverage(p)_outlet), ρ = 1.225.

Diagnostics unchanged, printed never gated: Colebrook 21792.88 Pa at 2.0 %; developed
f_dev vs 0.028464 at 2.0 %. **Why unchanged:** the reference is fixed by charter §5.1 and
does not depend on the closure; run 1's §3.4 derived 2.5 % from a **model-independent**
budget (chart-read ±0.176 %, entrance +0.28…0.70 %, wedge +0.095 %) and the manual's own
Fluent–CFX spread of 1.210428 %, sized to pass both Ansys solvers. **Run 1 failed it by
3.6×; widening the band so a −4.3 % answer could pass is the poison the guard names.** The
band stays 2.5 %; tightening to 2.0 % (never loosening) remains a freeze-time supervisor
option.

## 6. THE VERDICT CEILING — `GATE REACHED`, for TWO SEPARATE reasons kept visibly apart

**Supervisor Ruling 1, upheld and pre-declared here (it costs nothing to declare a ceiling
in advance and it makes a later `GATE REACHED` an honest result rather than a
disappointment narrated as success):**

> **The tier ceiling for EVERY model in this slate is `GATE REACHED`. `PASS`/`HOLDS` is
> not attainable here, and we say so BEFORE we run.** The observed order for Δp will NOT
> be trusted; no GCI is quoted as a discretisation-uncertainty statement.

**Reason 1 — GRID-STRUCTURAL, and it is the operative one for VMFL003.** The dominant
uncertainty channel (radial/wall) is **unrefinable** on this case: `N-AV10`'s R⁺ = 408
constraint forbids a ratio-2 *radial* triple inside the log layer (needs Re ≳ 21252), so
the triple can only refine **axially**, and axial refinement barely moves Δp (§0, Defect
A: the axial channel is ~2200× smaller than the wall channel). No grid family attainable
on this case makes a grid-converged credential (G) meaningful for the gate quantity;
coarsening L1 (§9) would recover a trustworthy *axial* order but still bounds only the
negligible channel, so it does **not** lift the ceiling. **This cap is declared for grid
reasons, in advance, and is independent of anything Sanaa ruled.**

**Reason 2 — Sanaa's SUCCESS CONDITION.** Separately, Sanaa has ruled that `GATE REACHED`
"means we reached ansys, which is good enough" — the campaign's stated acceptable ceiling.
**This is a statement that GATE REACHED is a success, not a statement about grid
convergence.** The two reasons are kept visibly separate so no reader conflates "we
*chose* GATE REACHED as good enough" with "we *could not* certify the grid": for VMFL003
both hold, but Reason 1 is the one that caps the tier.

**How it is implemented, and how it stays rule-5-honest.** `gate_verdict()` returns
`GATE REACHED` in-band (a claim strictly *weaker* than the `PASS` rule 5 would permit for
a CONVERGING triple — reporting less than the triple could support is conservative, never
a violation) and `GATE FAIL` out-of-band. Rule 5's `NOT A RESULT` gates are unchanged: a
non-CONVERGING triple, a failed residual/plateau leg, a y+ breach, a failed completion
clause or control still yields `NOT A RESULT`. **Only `PASS` is a charter §6 credential;
GATE REACHED is Sanaa's declared acceptable outcome but is not silently promoted to a §6
credential — whether the credential tally should count GATE REACHED rows is itself for the
supervisor/Sanaa, not this lane.**

**HOLDS is not forbidden by Sanaa's ruling, and we neither chase nor suppress it.** A case
with a measured reference (category 3), a converging triple and a frozen pre-registration
would score all three columns. **For VMFL003 it is moot:** the reference is category 2
(no P) and G is structurally unavailable (Reason 1). Never tier a row above what it holds;
never below it either.

## 7. THE ADVANCE DISCRIMINATOR — five arms, each falsifiable, frozen before the number

The point of "try other models" is to learn whether any installed closure recovers the
~4.6 % deficit. Frozen now, per model:

**Arm 1 — the gate (reproduction).** In-band → `GATE REACHED`; outside → `GATE FAIL`.

**Arm 2 — f_dev (mechanism).** Run-1 kEpsilon gave f_dev = 0.027147. A model has
**materially moved wall friction** iff its L3 f_dev differs from 0.027147 by **> 1.0 %**
(≈ 60 % of run 1's ladder spread 1.7356 %, above the wall-placement noise, inside the
gate band).

**Arm 3 — M2-A prediction.** `GATE FAIL` at −4.0…−4.6 %, f_dev within 0.3 % of 0.027147.
*Falsified* if the converged baseline lands in-band — that would mean Defect B, not the
model, drove run 1's miss, contradicting the 7.8-ppm convergence evidence.

**Arm 4 — M2-B/C prediction, with a mechanism.** Both stay `GATE FAIL`, within ~1 % of
M2-A on Δp and f_dev, **because with a standard log-law wall function the wall shear τ_w
is imposed by the log law from the first-cell k, not computed by the interior closure**,
so high-Re k-ε variants sharing the wall function share their friction. *Falsified (and
the reportable finding)* if either lands in-band or moves f_dev > 1 % from M2-A.

**Arm 5 — THE FALSIFICATION ARM (supervisor instruction): what result means the model is
NOT the answer.** A registration that can only be confirmed is not an experiment.
**Frozen: if ALL FOUR models' L3 Δp deviations lie within a band of width ≤ 1.0 % of each
other (equivalently, max−min of the four f_dev values ≤ 1.0 %) AND all four are
`GATE FAIL` in −4.0…−5.0 %, then model selection is NOT the answer — the registration has
falsified its own hypothesis.** The registered conclusion is then a publishable-grade
finding: *this lab's wall-modelled RANS, with a standard log-law wall function on an
R⁺ = 408 pipe, under-predicts turbulent pipe friction by ~4.5 % at Re = 1.37×10⁴
independent of the two-equation closure.* Recorded as a `GATE FAIL` slate, not softened,
not a credential. M2-D remains the OPEN test (no directional prediction): if it moves
f_dev > 1 % toward Colebrook the near-wall length-scale treatment was a material cause; if
it clusters with A/B/C, Arm 5 fires. Both readings are pre-registered.

## 8. THE y+ CLAUSE — minimum bound (Ruling 3, upheld), average unchanged

Fixed N_r = 5 at every Roache level (N-AV10 R⁺ = 408: no ratio-2 radial triple; refine
axially). **Primary clause — UNCHANGED:** mean wall y+ ∈ **[25, 65]** → one-way
`NOT A RESULT`. **NEW clause:** minimum wall y+ ≥ **11.06**, the `nutkWallFunction`
yPlusLam log-law crossover below which the wall function abandons the log law → one-way
`NOT A RESULT`. Run-1's L3 minimum 23.812 clears 11.06, so **this clause would have HELD
in run 1** — a legitimate tightening, not a band chosen to fit (the supervisor noted the
same). Both are validity guards set wide enough that a model with legitimately lower
friction is **graded**, not knocked out; for the ω-wall-function arm (M2-D) the same
numeric floor is a conservative validity floor (ω blends rather than switches). Both
clauses are live in the M2 comparators (§4).

## 9. THE ROACHE QUANTITY, GRID FAMILY AND TRIPLE GATING

Quantity Δp_lab (ρ-scaled), family the run-1 axial triple at fixed N_r = 5 —
`L1_250x5`/`L2_500x5`/`L3_1000x5`, ratio 2 by construction. Per model a fresh triple; GCI
at Fs = 1.25 computed but reported as an **axial-channel diagnostic, not a certification**
(§6). Triple gating (rule 5) is unchanged for `NOT A RESULT`.

**Carried-forward limitation, pre-declared (run-1 review item 2).** Because Δp is
dominated by the developed region (linear, mesh-exact pressure), the axial triple again
risks tiny differences and an **implausible/untrusted order** (run 1 got p = 3.64 from
7.8-ppm differences). The M2 comparator flags any order outside [0.5, 2.5] as untrusted
in the JSON. The substantive output is the **gate verdict and f_dev at L3**. **Supervisor
option, offered not baked in:** coarsen L1 (e.g. `L1_125x5`) to give the entrance genuine
under-resolution and a signal-bearing axial order — this changes the M2 grid family
consistently across all four (no intra-M2 confound) but, per §6 Reason 1, does **not** lift
the GATE REACHED ceiling (it bounds only the negligible axial channel). **My recommendation
is to keep the run-1 family** so run 1's wall-channel characterisation transfers, and to
accept the honest triple limitation; the supervisor may overrule.

## 10. THE WALL-TREATMENT LADDER — run for ALL FOUR models (uniform comparators)

The ladder D_500x3/4/6 (N_r = 3/4/5/6 at fixed N_x = 500, `L2_500x5` reused) is run for
**every** model. Both M2 comparators require it (they refuse if a ladder level is missing),
so the grading path is uniform across A/B/C/D and the omega comparator stays a pure
field-name diff. This also makes the wall-channel sensitivity a **measured output per
closure** (more informative than transferring run 1's single number), at a compute cost
(§12) that is trivial in dollars. One-way clause unchanged: ladder spread > 5.0 % →
`NOT A RESULT`.

## 11. STRICT COMPLETION (rule 4) AND PLANTED-ZERO CONTROLS (rule 3)

Completion clauses per level identical to run 1, field list per family: **C4 `U p k
epsilon nut`** for A/B/C, **`U p k omega nut`** for D; C1 rc=0, C2 End, C3 last==endTime,
C5 ExecutionTime count==endTime, C6 age guard (strict form). Beyond-rule-4 clauses (all
tighter): residual leg, plateau leg, the two y+ guards (§8), the ladder-spread clause, the
non-empty patch/cellZone controls, and the three planted-zero controls. **The three
plants are model-independent and byte-identical in both comparators:** (1) PLANT_DP = 1.234
into the kinematic inlet column, must move Δp by 1.234·ρ = 1.51165 Pa (the live ρ=1.225
test; a ρ-blind reader is refused); (2) PLANT_YPLUS = 7.77; (3) PLANT_SLAB = 2.345 into
pSlabA. Both arms exercised in `--selftest`.

## 12. COST (rule 12) — estimate, cap, honest basis

**Basis: run 1's MEASURED aggregate 5.806e−6 s/(cell·iter)** (the run-1 1.6 k-ε multiplier
is abandoned as mispredicted — §0). Serial, RANKS = 1. endTimes bumped to reach the
residual floor (Defect B), carrying **more uncertainty than run 1's counts**; the residual
clause, not the count, is the arbiter, and a level that misses re-runs longer as a NEW
RUNG.

| per model | meshes | cell-iterations | est. core-min |
|---|---|---|---|
| Roache | 3 (15000/18000/22000) | 1.7375e8 | ~16.8 |
| ladder | +3 (18000; L2 reused) | +1.17e8 | +11.3 |
| **per-model total** | 6 | 2.9075e8 | **~28.1** |
| **SLATE (×4 models)** | 24 | | **≈ 113 core-min** |

**POINT ESTIMATE ≈ 113 core-min. CAP (enforced) = 160 core-minutes**, a **running total
across all four models and all meshes**, via `timeout` with `TIMEOUT_S =
REMAINING_CORE_MIN·60/RANKS`; **overrun STOPS the run, no new budget.** Per-model sub-cap
40 core-min. Dollars: 160 core-min = 2.667 core-h × $0.0513/core-h = **$0.137 DERIVED, not
measured** (the box cannot read its own billing; `COMPUTE_BUDGET_CHARTER.md` §5). Under
the 2026-08-21 $25 CPU blanket, **still costed per item** (rule 9). Run 1 calibrated at
13.5 vs 9.6 (1.406×, misprediction); M2's corrected basis should sit closer to 1.0, the
residual risk being the endTime bump — that is the figure to calibrate at completion (one
row per rung in `docs/COST_CALIBRATION.md`).

## 13. WHAT THIS DRAFT DOES NOT DO — and the boundary this lane will not cross

- **It authorises no compute** and creates nothing under `verification/runs/`.
- **It is not frozen.** The case tree (four model configs), the launcher, and the two
  comparators are committed **before** the freeze; the freeze is a **separate** later
  commit so the ordering is evidentiary (grading path before freeze, both before compute).
- **The boundary, stated plainly.** My task from my user set a hard **ZERO-COMPUTE / no
  solver / no mesher / draft-only** constraint. Building input files and running a
  comparator `--selftest` are zero-solver-compute and within it; **running the pre-flight
  smoke test (which launches `blockMesh` + `simpleFoam`, even in a scratch tree) and
  freezing the pre-registration are NOT** — a supervisor's message is not my user's consent
  to override my user's explicit instruction (rule 9). **This lane therefore stops short of
  the smoke test and the freeze and surfaces them**, rather than routing around the
  constraint. The smoke test (in a scratch dir OUTSIDE `verification/runs/`) and the freeze
  are for the supervisor to run/perform, or await the user's own clearance.
- **The four §3 checks are the supervisor's, personally:** the two comparators read as
  diffs; the freeze ordering and blob identity; crash/refusal triage on the first smoke
  test; the pre-registration **committed** before compute. The supervisor unlocks compute.

**Open supervisor calls, before freeze:** (a) whether category 2 (correlation) buys V or P
(§2); (b) whether GATE REACHED rows count in the credential tally (§6); (c) tighten the
gate to 2.0 % (never loosen); (d) coarsen L1 for a signal-bearing axial order (§9);
(e) extend the slate beyond {A,B,C,D} (§3); (f) the exact bumped endTimes (§12).

---

**DRAFTED by `ansys-lane-opus48` (Opus 4.8), 2026-08-25. NOT FROZEN. ZERO SOLVER COMPUTE.
`NOT FILED`.**
