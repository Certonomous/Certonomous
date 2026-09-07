# T10a-VF2 DRIVEN SWEEP — freezing VF-3', VF-6' and the §2 signal-to-background admissibility rule by showing the 0.20 constant NON-LOAD-BEARING

> **FROZEN.** Freeze pin: this document's freezing commit carries
> `FREEZE-PIN: docs/campaigns/T-family/T10aVF2_DRIVEN_SWEEP_PREREGISTRATION.md`
> (`VERIFICATION_CHARTER.md` §2au — the commit is the pin; it is NOT the rule-2
> anchor). **NOTHING RUN** in this arm: this freeze precedes first compute (rule 2).
> The grading path is fixed at this commit; its byte-identity is the rule-2 anchor.
> The §3 measurement-script diff-read and the freeze were performed personally by
> the supervisor and never delegated (`SUPERVISION_CHARTER.md` §3). All four open
> questions O-1–O-4 (§9) are RULED — see the dated freeze appendix at the foot.
>
> *(Superseding the prior DRAFT header. The body below is the prediction-first
> registered content, unchanged: `S(case) = min` was registered BEFORE any sweep
> ran, so no signal was chosen to fit an answer.)*

**Predecessor / lineage:** `T10a-VF2`
(`docs/campaigns/T-family/T10aVF2_PREREGISTRATION.md`, PARTIAL FREEZE
`c4d1e30a`), which itself is the dated fix-successor to `T10a-VF`. This arm is the
**driven-sweep successor** required by verification's **V-121** ruling
(`7db1df83`, recorded in `docs/LAB_STATE.md`, verification-supervisor,
2026-09-07). It does **not** re-open, re-grade or re-hash the parent freeze
(`c4d1e30a`): VF-4' (Limb A/B), VF-7', their controls and the frozen comparator
`analyse_t10avf2.py` (blob `ebe19800f0a338664e74f40a89f9c2f35f0d2e05`) stand
untouched. This arm adds the three elements the parent **DEFERRED**: **VF-3'**,
**VF-6'**, and the **§2 signal-to-background 0.20 admissibility rule**.

Verdict vocabulary fixed by `CLAUDE.md` rule 1:
**PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED / PENDING.**

---

## 0. Why this arm exists — the V-121 binding condition, verbatim in force

V-121 admitted the VF-4' control-measured floor `B_ctrl` (independent control
channel, frozen formula, afix-identity + `p≥1.5` guards) and let VF-4'/VF-7'
freeze now. It **withheld** the 0.20 admissibility constant and the two gates that
depend on it (VF-3', VF-6') under one condition, quoted from the ruling
(`docs/LAB_STATE.md`, V-121):

> **0.20** (VF-3'/VF-6' admissibility only, deferrable): admissible **ONLY IF
> frozen + shown NON-LOAD-BEARING by a driven sweep across `[0.05,0.25]`** (the
> D393 standard) — a "round 5×" rationale is not enough. VF-4' may freeze now;
> VF-3'/VF-6' after the sweep.

The parent's own §4a flag conceded the point: the 0.20 constant is *"the one
element that is a registered judgment call rather than a derivation"* and, *"If
the supervisor judges it pass-fitting, the correct action is to leave
VF-3'/VF-6' FLAGGED and NOT widened."* This arm removes the judgment call by
**measurement**: it drives the admissibility threshold `τ` across the whole
`[0.05, 0.25]` range on the successor's **own fresh controls** and shows,
pass/fail, that the admissible-level set and the VF-3'/VF-6' verdicts do not
depend on where in that range `τ` sits. If they do depend on it, 0.20 is
load-bearing and this arm **GATE FAILs** — VF-3'/VF-6' stay deferred/flagged, not
widened. That is the D393 non-load-bearing discipline: the constant is defensible
only when the answer is shown independent of it, never by asserting robustness.

**This arm changes no verdict in the parent and re-grades nothing.** It measures
whether one deferred constant may freeze, and if so freezes VF-3'/VF-6' against
thresholds carried **verbatim and prediction-first** from the parent §4.

---

## 1. Toolchain and the observable — unchanged, re-asserted

Identical to the parent (§1, §0.2): OpenFOAM ESI **v2606**,
`/usr/lib/openfoam/openfoam2606`, utility **`viewFactorsGen`**. The graded
observable is unchanged and needs no reference: for any closed enclosure of opaque
surfaces `sum_j F_ij = 1` exactly, at every resolution; `E ≡ rowSum − 1` is
compared to the exact value 0 and to nothing else. **No band is widened.** All
symbols as the parent: `E` = patch-mean `rowSum − 1`; `n_ev` = patch-mean
mutually-visible edge-sharing neighbour count; `e(a) = −(2 ln a + 3)/(4π)`,
`e(0.21) = +0.0096524`, `e(exp(−3/2)) = 0`; `B_ctrl(case) = max|E|` over that
case's `n_ev = 0` convex/flat control patches (frozen formula, per V-121 and the
parent §2 Step 4).

---

## 2. The quantity the sweep drives: the admissibility ratio and the set `A(τ)`

The parent §2 admissibility rule is:

> a mesh case is **ADMISSIBLE** for a mechanism gate iff
> `B_ctrl(case) ≤ τ · |n_ev · e(0.21)|` on that case (parent uses `τ = 0.20`,
> "signal ≥ 5× background").

Rewrite it as a per-case scalar **ratio** so the threshold is the only free knob:

> **`r(case) ≡ B_ctrl(case) / S(case)`**, where `S(case)` is the case's mechanism
> **signal**. Case is **ADMISSIBLE at threshold `τ`** iff `r(case) ≤ τ`.
> The **admissible set** is `A(τ) = { case : r(case) ≤ τ }`.

**Signal definition `S(case)` (registered now, prediction-first).** The rule must
hold for *every* graded patch a mechanism gate reads, so the signal is taken as
the **weakest** mechanism signal among that case's graded (concave, `n_ev > 0`)
patches — the most conservative choice, giving the **largest** ratio and the
**hardest** admissibility bar:

> **`S(case) = min` over the case's graded concave patches of `|n_ev · e(0.21)|`.**

*(This definition is a REGISTERED CHOICE, not pinned by the parent prereg — see the
open question O-1 in §9. Min-signal is chosen so admissibility can never be gamed
by a single strong patch; the supervisor must ratify it before freeze because it
changes which levels land in `A(τ)` and therefore the sweep numbers.)*

The parent recorded the predecessor family's ratios as `L1 (N=8) ≈ 0.31`,
`L2–L4 ≈ 0.02–0.05` — a wide gap straddling the whole `[0.05, 0.25]` interval.
Those are predecessor numbers; this arm recomputes `r(case)` on the **successor's
own fresh cases**, which is exactly why the sweep must be *driven* and not
asserted.

---

## 3. The driven sweep — design (frozen BEFORE the single run computes)

Two layers, both frozen at the pre-registration commit.

### 3.1 Data layer (mesh-side, `viewFactorsGen`) — one computation

The sweep consumes per-case row-sum measurements over the **S1 SPH mesh family and
the S2 geometry family** — the same cases the parent VF-4' arm defines:

| set | cases | n² per side | what it yields the sweep |
| --- | --- | ---: | --- |
| **S1 — SPH family** | `SPH` at 768 / 1728 / 3072 / 4800 faces (= `L1 / L2 / L3 / L4`) + `_afix` twin of each (8 cases) | `Σn² = 3.6e7` (×2 with afix = 7.2e7) | `B_ctrl`, `E`, `E_afix`, `r(case)` per level → VF-3' (b) admissible-level spread, VF-6' |
| **S2 — geometry** | `BOX`, `SHELL`, `BALL`, `CYL` at 2 res + `_afix` at the finer (12 cases) | `Σn² = 3.4e7` | `E/n_ev` per concave patch → VF-3' (a); VF-6' on admissible un-agglomerated cases |

Every `r(case)` is a **derived scalar** read from these already-computed row sums;
`τ` **does not enter any `viewFactorsGen` run** — the mesh data is computed once
and the threshold is swept in post-processing only. (Accounting for whether these
cases are built by this arm or read read-only from the parent's arm: open
question O-2, §9.)

### 3.2 τ-sweep layer (post-processing) — the driven grid

Frozen threshold grid spanning the V-121 interval, 0.20 included as the nominal:

> **`τ ∈ { 0.05, 0.075, 0.10, 0.125, 0.15, 0.175, 0.20, 0.225, 0.25 }`**
> (9 points, uniform step `Δτ = 0.025`, endpoints inclusive).

At each `τ` the sweep recomputes `A(τ)` and re-evaluates the **full** VF-3' and
VF-6' verdicts against `A(τ)` (their thresholds are §4, unchanged).

**Grid justification, and why grid density is itself non-load-bearing.** `A(τ)` is
a step function of `τ` that changes only where `τ` crosses some case's ratio
`r(case)`. So the sweep also computes the **exact** invariance backbone directly
from the ratios (no discretisation):

> **EXACT-GAP CHECK:** `A(τ)` is invariant across `[0.05, 0.25]` **iff no case
> ratio `r(case)` lies in the half-open interval `(0.05, 0.25]`** — equivalently
> every `r(case)` is either `≤ 0.05` or `> 0.25`.

The 9-point grid is the *driven demonstration* required by V-121 (verdicts
actually recomputed and shown identical at each point); the exact-gap check is the
*proof*, and because it is exact, the choice of grid step is **not load-bearing**
(no infinite regress: a finer grid cannot change the exact answer). `Δτ = 0.025`
is `≥ 8×` finer than the predecessor gap margin (nearest admissible ratio ≈ 0.05
to the endpoint, vs the inadmissible L1 at ≈ 0.31 well above 0.25), so the grid
resolves any partition boundary the exact check flags.

### 3.3 The INVARIANCE gate (VF-ADM) — the pass/fail test that decides 0.20

This is the load-bearing new gate of this arm. It decides whether 0.20 is
non-load-bearing (may freeze) or load-bearing (may not).

| gate | what it tests | PASS threshold | GATE FAIL |
| --- | --- | --- | --- |
| **VF-ADM** — 0.20 non-load-bearing | the admissible set and the two dependent verdicts do not depend on `τ` within `[0.05, 0.25]` | **all three hold:** (i) EXACT-GAP CHECK passes (no `r(case) ∈ (0.05, 0.25]`); **and** (ii) `A(τ)` is the identical case set for all 9 grid `τ`; **and** (iii) the VF-3' verdict label and the VF-6' verdict label are each **identical** across all 9 grid `τ`, AND every graded value they compute is stable to `≤ 1e-6` relative across the grid | any of (i)–(iii) fails: some `r(case) ∈ (0.05, 0.25]`, or `A(τ)` changes, or a dependent verdict label flips, across the range |

**Consequence, registered in advance:**
- **VF-ADM PASS** → the 0.20 constant is demonstrated non-load-bearing; it and the
  §2 admissibility rule **may freeze** (supervisor's freeze), and the VF-3'/VF-6'
  verdicts computed at the nominal `τ = 0.20` (§4) are **awarded**.
- **VF-ADM GATE FAIL** → 0.20 is load-bearing on the successor's own data; the §2
  admissibility rule and VF-3'/VF-6' **remain deferred/flagged and are NOT
  widened** (parent §4a discipline, V-121). VF-3'/VF-6' are reported **NOT A
  RESULT** (the instrument cannot certify a gate whose admissibility partition is
  threshold-dependent), value and both partitions printed beside them. This
  outcome does **not** touch VF-4'/VF-7' (frozen `c4d1e30a`).

Note the endpoint honesty: the predecessor's `L2–L4` ratios reached ≈ 0.05, i.e.
the low endpoint. If a fresh admissible case lands with `r ∈ (0.05, 0.25]`,
VF-ADM **GATE FAILs by design** — the falsifier bites exactly where the parent's
"any value in `[0.05,0.25]`" claim is most fragile. That is the intended,
non-pass-fitting behaviour. (Whether the V-121 interval is read strictly full-range
or as a neighbourhood of 0.20 is open question O-3, §9; this draft registers the
strict full-range reading, which is the harder test.)

---

## 4. VF-3' and VF-6' — gates carried VERBATIM and prediction-first from the parent §4

These thresholds were registered prediction-first in the parent (`c4d1e30a` §4)
and DEFERRED unfrozen. They are carried here **unchanged** — this arm freezes them,
it does not re-pose them. Their verdicts are awarded **only if VF-ADM PASSes**;
otherwise NOT A RESULT (§3.3).

| gate | what it tests | PASS threshold | GATE FAIL |
| --- | --- | --- | --- |
| **VF-3'** per-pair constant | `E/n_ev` is a constant of `alpha`, not of `h`, measured only where the signal dominates (i.e. on `A(τ)`) | (a) `E/n_ev ∈ [0.0080, 0.0130]` on every concave patch of S1–S2 at `alpha = 0.21`; **and** (b) spread of `E/n_ev` across the **ADMISSIBLE** `SPH` levels `≤ 15 %` | (a) outside the interval on any patch; **or** (b) admissible-level spread `> 15 %` |
| **VF-6'** `alpha`-fix leaves exactly the background | `alpha = exp(−3/2)` removes exactly the mechanism, leaving the converging background | on every **ADMISSIBLE, UN-AGGLOMERATED** case: all patch means `|E_afix − B_ctrl(case)| ≤ max(0.30·B_ctrl(case), 0.003)` | any admissible un-agglomerated patch mean outside |

**Cap / label.** Arm cap **1.00 USD** (parent). Label: **T10a-VF2 driven-sweep
arm** (freezes VF-3', VF-6', §2 admissibility rule). Roache triple gating
(`CLAUDE.md` rule 5) is not invoked: these are `viewFactorsGen` row-sum gates on a
mesh family, not a three-grid GCI observable; no GCI is quoted and no triple is
formed (consistent with the parent, which quotes none for these gates).

### 4a. Principled-vs-pass-fitting self-audit (honest-labelling)

| gate | why it is not pass-fitting | the falsifier that still bites |
| --- | --- | --- |
| **VF-ADM** | the 0.20 constant is decided by measurement across the whole range on fresh controls, not asserted; grid density is proven non-load-bearing by the exact-gap check | any `r(case) ∈ (0.05,0.25]` → GATE FAIL; the constant is then declared load-bearing and VF-3'/VF-6' stay deferred, not widened |
| **VF-3'** | admissible levels are selected by a threshold shown `τ`-independent (VF-ADM), not post-hoc; `h`-independence measured only where measurable | `E/n_ev` drifting with `h` on admissible levels → spread `>15 %` → GATE FAIL; any concave patch outside `[0.0080,0.0130]` → GATE FAIL |
| **VF-6'** | the post-fix residual is graded against the background it should leave (`B_ctrl`), not against 0 | fix leaving more than the background on any admissible un-agglomerated case → GATE FAIL |

---

## 5. Planted-zero controls (`CLAUDE.md` rule 3) — TWO plants, both driven every grading run

Rule 3: a reader not shown able to see a non-zero is not evidence. Two independent
plants, each RED (perturbation seen) then GREEN (clean), refusing (**exit 2**) if
not recovered.

1. **Row-sum plant — carried identical to the parent §5.** `PLANT_ROWSUM =
   3.21e-2`, injected into a **scratch copy** of `constant/F` under the case (never
   the real matrix), streamed through the **same** row-sum reader that produces `E`
   and `B_ctrl`, asserting the designated face's reported `rowSum` rose by
   `PLANT_ROWSUM` to `1e-9`; then the unperturbed copy is read and the designated
   row asserted at its measured value. Read back from disk, never from memory. This
   proves the reader feeding `r(case)` can see a non-unit row sum.

2. **Ratio-partition plant — NEW, load-bearing for THIS arm's gate.** The
   invariance detector (VF-ADM) must be shown able to see a *load-bearing*
   threshold, or a PASS from it is not evidence. `PLANT_RATIO = 0.15` is injected
   as one **synthetic case** with `r = 0.15` (a value inside `(0.05, 0.25]`) into
   the τ-sweep; the sweep must report VF-ADM **GATE FAIL** (exact-gap check trips,
   `A(τ)` changes across the grid). The synthetic case is then removed and the real
   family swept, and VF-ADM must return its real verdict. A detector that cannot
   flip to GATE FAIL on a planted in-range ratio **refuses and grades nothing** — a
   "non-load-bearing" verdict from a detector blind to a load-bearing case is not
   evidence.

Both plants and their RED/GREEN drives are exercised in the comparator's
`--selftest` and in every real grading run.

---

## 6. Strict completion, age guard, comparator freeze (`CLAUDE.md` rules 2, 4)

- **Mesh cases (S1/S2) obey the strict completion rule** exactly as the parent
  arm: `rc = 0`, an `End` line, `last time == endTime`, the `viewFactorsGen`
  outputs present (`constant/F`, `0/viewFactorField`), and the **age guard** — the
  produced fields NEWER than the case's own `0/T`; the builder refuses a case where
  `0` or a time dir already exists (rule 4; parent §3). No solver runs — mesh-side
  preprocessing only (`blockMesh` + `viewFactorsGen`), Charter §2d. `CLAUDE.md`
  rule 4 fields list is the thermal-family list; for this `viewFactorsGen`-only arm
  the "fields present" clause is the utility's own outputs, as in the parent
  (carried, not re-defined here).
- **The τ-sweep post-process is not a solver run**; it produces no time directory.
  Its integrity rests on (a) the two §5 plants, (b) refusal (exit 2) on any missing
  or stale input case, and (c) self-hashing against the committed comparator blob.
- **Comparator freeze plan (rule 2).** The grading path is fixed at the
  pre-registration commit and each scoring script hashes itself against its
  committed blob at run time, refusing on mismatch
  (`scripts/check_comparator_freeze.py`). The frozen `analyse_t10avf2.py`
  (`ebe19800…`) is **read-only input** and is **not modified** (rule 6): this arm's
  comparator re-implements or read-only-imports its readers, exactly as that file
  re-implemented the predecessor's.

---

## 7. Comparator code that would need to be WRITTEN — NOT written in this draft

Per V-121 and the parent §6, this zero-compute draft registers the contract only;
no gate code is written, because the design may change under the §3 check. The
supervisor decides what is written after checking this design.

| path | role | status |
| --- | --- | --- |
| `docs/campaigns/T-family/T10aVF2_DRIVEN_SWEEP_PREREGISTRATION.md` | this file | **drafted (this lane); NOT committed, NOT frozen** |
| `verification/runs/T-family/T10aVF2_runs/analyse_t10avf2_sweep.py` | **NEW comparator**: read-only reuse of `analyse_t10avf2.py` readers (`read_boundary`, `read_faces`, row-sum aggregation, `B_ctrl`, patch classification) **plus** `r(case)`, `A(τ)` over the frozen grid, the exact-gap check, VF-3'/VF-6' evaluation per §4, the VF-ADM invariance gate, the two §5 plants, refusal on missing/stale input, self-hashing, and `--selftest` | **TO BE WRITTEN before freeze — NOT written here** |
| `verification/runs/T-family/T10aVF2_runs/grade_t10avf2_sweep.py` | scorer emitting VF-ADM + VF-3'/VF-6' verdicts and the calibration row | **TO BE WRITTEN before freeze — NOT written here** |

**Do NOT touch** the frozen `analyse_t10avf2.py` (`ebe19800…`) or the predecessor
`analyse_t10avf.py` (`6bb15552…`) — both are read-only input (rule 6).

---

## 8. Cost — core-minutes, honest basis (`CLAUDE.md` rule 12)

`viewFactorsGen` scales `O(n²)`. Rate anchor carried from the parent's **measured**
predecessor actuals: **≈ 2.84e-8 core-min per `n²`** (the rule-12 estimate→actual
calibration feeding forward).

| item | `Σn²` | core-min |
| --- | ---: | ---: |
| S1 SPH family (8 cases incl. afix) | 7.2e7 | ~2.0 |
| S2 geometry (12 cases) | 3.4e7 | ~1.0 |
| `blockMesh` + `checkMesh`, ~20 cases | — | ~1.2 |
| Python: comparator + `B_ctrl` + `r(case)` + 9-point τ-sweep + 2 plants + `--selftest`, over ~20 cases | — | ~6.0 |
| **registered total (independent build)** | ~1.06e8 | **~10.2 core-min** |
| **registered ceiling incl. 3× contingency + reruns** | | **~31 core-min** |

**If the sweep rides on the parent VF-4' arm's already-completed S1/S2 cases**
(read-only), the mesh layer cost is **zero to this arm** and only the ~6 core-min
Python layer is new (ceiling ~18 core-min). Which accounting applies is open
question **O-2** (§9); this draft registers the **full independent-build ceiling**
so the pre-registered cap is never exceeded whichever path the supervisor picks.

Arm cap **1.00 USD**. Registered estimate ~10.2 core-min; **derived** cost
≈ **$0.0087** at $0.0513/core-h. An overrun **stops the run** (rule 12); the cut
order is the parent's — drop `S1 L4` and its afix twin first, then `S2 SHELL`
finer + twin. No cut touches a flow result: **no solver runs in this arm.** Under
$25 pre-authorised (2026-08-18 standing authorisation); this is ~0.03 % of that
per-run ceiling.

> **cost_basis: rate $0.0513/core-h is OWNER-STATED (`CLAUDE.md` rule 12;
> `Xiao2016_EnKF/PREREGISTRATION.md:197`); the box cannot read its own billing
> (`COMPUTE_BUDGET_CHARTER.md` §5), so every dollar figure here is DERIVED at that
> rate, REPORTED-BY-OWNER, NEVER measured. Core-minutes are the measured unit and
> come from per-case `STATUS wall_s` at grade time.**

At process completion (VF-ADM + VF-3'/VF-6' graded) the rule-12 estimate-vs-actual
calibration row lands in `docs/COST_CALIBRATION.md` (actual/predicted ratio, gap
attribution, waste named separately) — the completion report is incomplete without
it.

---

## 9. Open design questions the SUPERVISOR must settle before freeze

These are not resolvable from V-121 or the parent prereg alone; the freeze should
not proceed until they are ruled.

- **O-1 — the signal `S(case)` in the admissibility ratio.** The parent states the
  rule as `B_ctrl ≤ 0.20·|n_ev·e(0.21)|` but does **not** pin whether the signal is
  the min / max / mean / representative concave-patch `|n_ev·e(0.21)|`. This draft
  registers **min over graded concave patches** (most conservative, largest ratio,
  hardest bar). The choice changes the numeric `r(case)` and therefore whether
  VF-ADM passes; it must be ratified (or replaced) before freeze, because after
  first compute it cannot change (rule 2).
- **O-2 — cost accounting / case sharing.** The S1/S2 mesh cases are the **same
  physical cases** the parent VF-4' arm defines. Does this arm (a) read them
  read-only from a completed parent run (Python-only cost, no double-count), or
  (b) build and run its own copies? The age guard (rule 4) and completion rule
  attach to whichever arm actually builds them; the supervisor must decide the
  ownership so the same cases are not costed twice across two preregs.
- **O-3 — interpretation of the V-121 interval near the endpoints.** The
  predecessor's admissible ratios reached ≈ 0.05 (the low endpoint). This draft
  registers the **strict full-range** reading: any `r(case) ∈ (0.05, 0.25]` fails
  VF-ADM. If the supervisor reads V-121 as requiring invariance only in a
  *neighbourhood of 0.20* (not touching the extreme endpoints), the grid and the
  exact-gap interval must be re-registered accordingly. The strict reading is the
  harder, more honest test and is this draft's default.
- **O-4 — GATE FAIL disposition of VF-3'/VF-6'.** This draft registers that a
  VF-ADM GATE FAIL renders VF-3'/VF-6' **NOT A RESULT** (deferred/flagged, not
  widened). The supervisor should confirm this matches V-121's intent versus
  reporting them as GATE FAIL; the distinction matters for the §2ay lineage flag on
  T10a-VF.

---

---

## 10. FREEZE APPENDIX — the O-1–O-4 rulings, dated (2026-09-07, pre-first-compute)

*This appendix records the settlement of §9's four open questions and the two
grading operationalizations, so the frozen registration matches the frozen grading
path byte-for-byte. It is written at freeze time, before any `viewFactorsGen` or
sweep has run for this arm (rule 2: pre-first-compute; no gate, threshold, band,
cap or label is moved from the prediction-first body above).*

- **O-1 (signal `S(case)`) — RULED: `S_MODE = "min"` CONFIRMED.** Ruled by
  verification (**V-124**, LAB_STATE; commit `1cca81ca`), whose §3 plant-drive
  independently exercised the comparator (frozen-reader byte-identity `ebe19800`
  holds `= committed`; `PLANT_RATIO = 0.15` flips VF-ADM → GATE FAIL; AST confirms
  import-reuse / no reimplementation). **`min` is retained on the
  MIN-IS-CONSERVATIVE ground** (largest ratio, hardest bar; admissibility cannot be
  gamed by a single strong patch), **with all three `S(case)` candidates — min,
  max, mean — REPORTED** (the comparator's `S_case_all` / `[A]` block and
  `S_DEPENDENT` manifest). *An earlier "load-bearing sub-condition" framing raised
  at escalation was WITHDRAWN by verification as mis-specified and is superseded by
  this rationale.* This matches the prediction-first body (§2, `S(case) = min`) and
  the comparator constant `S_MODE = "min"` (blob `f3619318`).
- **O-2 (cost accounting) — RULED (supervisor, per V-121): INDEPENDENT BUILD.** The
  registration carries the FULL independent-build ceiling (§8, ~31 core-min) so the
  cap is never exceeded whichever path runs; no case is double-costed across the two
  preregs because this arm's build is the accounted owner of its own cases.
- **O-3 (V-121 interval) — RULED (supervisor, per V-121): STRICT FULL-RANGE.** Any
  `r(case) ∈ (0.05, 0.25]` fails VF-ADM (§3.3 / §4). The harder, more honest test;
  the draft default is ratified.
- **O-4 (VF-3'/VF-6' disposition on VF-ADM GATE FAIL) — RULED (supervisor, per
  V-121): NOT A RESULT.** A VF-ADM GATE FAIL renders VF-3'/VF-6' **NOT A RESULT**,
  deferred/flagged and **NOT widened** (parent §4a discipline, V-121). The draft
  default is ratified; the T10a-VF §2ay flag stays discharged only by the parent's
  landed PASS (`0f0e9b4b`), never by a widening here.

**TWO GRADING OPERATIONALIZATIONS — BLESSED (verification V-124):**

1. **VF-3' (b) admissible-level spread** is computed as: per-SPH-level MEAN of
   `E/n_ev`, then `(max − min) / mean` across the admissible levels, gated at
   `≤ 15 %` (§4).
2. **VF-6' afix twin resolution** is `meta['twin']` when present, else the case
   name with the `"_afix"` suffix; a missing twin → **NOT A RESULT** (never a silent
   pass), as the comparator enforces.

**GRADING PATH (supersedes §7's placeholder scorer).** Scoring is FOLDED INTO the
single self-contained comparator
`verification/runs/T-family/T10aVF2_runs/analyse_t10avf2_sweep.py` (blob
**`f3619318`**), which emits the VF-ADM + VF-3'/VF-6' verdicts, carries the two §5
plants and the `--selftest`, and self-hashes / refuses on frozen-reader mismatch.
There is **no separate `grade_t10avf2_sweep.py`**; the row in §7 registering it is
superseded by this appendix. `EXPECTED_SELF_BLOB` remains `None` (print-only) — a
document cannot contain the sha of the commit that commits it (§2au.2, the
IMPOSSIBLE form); the rule-2 anchor is the on-disk file's byte-identity against its
committed blob at grade time (`scripts/check_comparator_freeze.py`), and the freeze
is recorded by the `FREEZE-PIN` line in this commit's message (§2au.3).

**§3 CHECK-1 (supervisor, non-delegable):** the comparator was diff-read by the
supervisor (imports the frozen `analyse_t10avf2.py` `ebe19800` by path + asserts
its blob at import; AST self-check proves no reader was reimplemented and no
`av2.*` monkeypatch; both rule-3 plants fire RED/GREEN; the blind-invariance
detector is CAUGHT by `PLANT_RATIO = 0.15`; `--selftest` rc 0) and independently
plant-driven by verification (V-124). The on-disk file is byte-identical to the
plant-driven blob `f3619318` at freeze.

*Frozen by the heat-transfer supervisor, 2026-09-07, zero compute. The design was
drafted by a heat-transfer lab-lane; the §3 checks, the O-1–O-4 rulings adopted
here, and this freeze are the supervisor's.*
