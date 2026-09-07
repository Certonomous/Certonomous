# DMR POSITIVITY-LIMITED SUCCESSOR — a new numerics family — pre-registration (AUTHORISED)

> **AUTHORISED — FROZEN — CHECK-4 TAKEN.**
> The cfd supervisor took **check 4 PERSONALLY AND UNDELEGATED** (`SUPERVISION_CHARTER.md`
> §3), 2026-09-07, **PASS**. The supervisor read the successor driver
> `run_dmr_positivity_successor.sh` (sha256
> `9d8635e2c3b27f7b826d9164361b191e30fa7558bb8542131c6a9be4232ff7a3`), the generator
> `make_case_successor.py` (sha256
> `5e19df5b5d966e90135a21000bee857dfe4b1cf0a4d9c95e4e0756156c2d156a`) diff vs the parent
> `make_case.py` (confirmed **EXACTLY** the registered levers `maxCo` 0.2->0.1 and
> `reconstruct` rho/U/T vanLeer/vanLeerV->Minmod/MinmodV, nothing else), and confirmed the
> frozen method-agnostic grader `dmr_locator_v2.py` (blob `52aacf9669…`, hashed at grade
> time by the driver, refuses on mismatch). **§2ay state-(b):** the method is changed, Gate
> V' tol 0.0231 and all bands are **HELD EXACTLY** at the frozen parent's values and **NOT
> widened**, the total 60.0 core-min hard cap stops the run on breach (rule 12), and the
> successor may honestly **GATE FAIL on accuracy** (Minmod's diffusivity) — a real result,
> not a failure of the process. Run roots **ABSENT** (gates open) when taken. **AUTHORISED.**
> No queue row placed — placement is the chief's routing act (rule 9); approval of this item
> is approval of **ITS 60 core-min cap, not a new ceiling**.

**§2ay classification of the parent.** Parent verdict: **DMR R3 NOT A RESULT** with
**Gate T BLOCKED** — `verification/campaign/DMR_R3_RESULTS.md:12-14`. `rhoCentralFoam`
crashed at t = 0.10863175 of endTime 0.2 (54 %) with **rc 136 = SIGFPE**, a negative
argument to `sqrt` in the speed-of-sound evaluation — i.e. a **locally negative
temperature** — at h = 1/240. The census flagged it as a standing violation: a landed
NOT A RESULT with **no active dated fix-successor** (`:96` leaves "a positivity-
limited variant graded as its own family, or a 1/180 rung at r = 1.5" to the
supervisor and takes neither). This draft opens the positivity-limited variant. It is
**not** a capability gap (state a): the mechanism is understood (`:76-83`) — the
Kurganov central-upwind flux with `vanLeer` reconstruction carries **no positivity-
preserving limiter**, and at Mach 10 the reconstructed states in a strong expansion
can produce a negative internal energy that sharpens with the grid. A more robust
reconstruction is a standard, available our-side fix.

---

## 1. WHY THIS MUST BE A NEW FAMILY, NOT A RE-RUN OF R3

The frozen parent (`DMR_R3_TRIPLE_PREREGISTRATION.md`) names as a **disqualifier**
"any difference in scheme, constants, boundary conditions, `maxCo`, write times or
rank count between R3 and the two existing rungs — the triple requires one numerics
family and a difference invalidates it rather than being corrected for" (parent
`:91-93`). Therefore **the numerics change cannot be dropped into the R1/R2/R3
triple**: it would produce a rung that runs and a triple that means nothing.

**The successor is a fresh, self-contained three-level family** run end-to-end with
the positivity-limited numerics — R1' (1/60, 240×60), R2' (1/120, 480×120), R3'
(1/240, 960×240), nested exactly 2:1 — graded as **its own** Gate V and its own
grid-convergence triple. The existing DMR two-rung pair (R1, R2, Gate V PASS on the
2026-08-07 record) is **untouched and unaffected** (`:16-19`), exactly as the parent
preserved it.

---

## 2. WHAT FAILED, MEASURED

From `DMR_R3_RESULTS.md`:
- `rhoCentralFoam` reached t = 0.10863175, died rc 136 (SIGFPE), deepest named frame
  `Foam::sqrt(...)` via the speed-of-sound field → **locally negative temperature**
  (`:34-42`), a **trapped** exception (`trapFpe` on), not a silent NaN (`:44-46`).
- **Not a time-step runaway:** `deltaT` constant at 4.32e−05, max Courant steady at
  0.1998 against `maxCo` 0.2 right up to the fault (`:48-58`).
- **The last written field (t = 0.10) is completely healthy:** over all 230,400
  cells, T min = 1.000000, rho min = 1.4, p min = 1, **zero negatives** (`:60-63`).
- So the failure is **sudden and local**: from an everywhere-positive field to a
  negative temperature in ~200 steps. *Where* it first appears was not determined
  (fields at the failing step were never written) — a hypothesis, not a finding
  (`:68-73`).

---

## 3. THE SPECIFIC NUMERICS CHANGE, AND WHY IT SHOULD RECOVER

`rhoCentralFoam` (Kurganov–Tadmor central-upwind) has no built-in positivity limiter;
robustness is controlled through the **reconstruction (interpolation) limiter** and,
secondarily, the Courant number. The change, applied uniformly to **all three
levels** so the family is self-consistent:

1. **reconstruction limiter `vanLeer` → `Minmod`** — the most diffusive of the
   standard TVD limiters, the canonical robust choice for strong-shock Euler runs; it
   clips the reconstructed left/right states more aggressively, suppressing the
   negative-internal-energy overshoot in the strong expansion behind the Mach stem;
2. **`maxCo` 0.2 → 0.1** (secondary lever) — halves the reconstructed-state
   excursion per step, further margin against a locally negative state;
**NOT part of this freeze — a NON-registered future lever, recorded only for transparency:**
were 1–2 insufficient at 1/240, a further change — `Gauss Minmod` on the energy/velocity
reconstruction with the interpolation applied to primitive rather than conservative variables
(documented `rhoCentralFoam` robustness practice) — would be a SEPARATE successor carrying its
own pre-registration and freeze. It is **NOT applied here**: the frozen method changes **exactly
levers 1–2** and the `div(tauMC)` scheme, the Kurganov flux and the Euler `ddt` all remain the
parent's. A frozen method must be deterministic; a contingent "if insufficient" lever cannot sit
inside it, so it is demoted out of the registered set (cfd `lab-lane`, 2026-09-07, pre-freeze;
changes no gate, threshold, cap or label).

**Why it should recover:** the crash is a reconstruction-overshoot into a non-
physical state; a more dissipative limiter and a smaller Courant number directly
reduce that overshoot. The frozen family "survives at 1/60 and 1/120 and does not
survive at 1/240" (`:80-83`), consistent with a robustness ceiling the limiter change
raises.

**Honest caveat, stated before the run (rule 2):** `Minmod` is **more diffusive** than
`vanLeer`. The successor may **run to completion and then GATE FAIL on accuracy** —
the shock position could smear enough to exceed the Gate V tolerance, or the grid-
convergence triple could stagnate because added numerical diffusion masks the formal
order. That would be a **legitimate accuracy/robustness trade-off finding**, still
state (b), NOT a widening of the gate: the tolerance is held (§4) and the family is
honestly graded. Research anchor: this is the standard central-scheme robustness-vs-
accuracy trade; the successor *measures* where it lands rather than assuming.

---

## 4. THE GATES, AND NO THRESHOLD IS WIDENED

**Gate V' (kinematics vs exact theory) — IDENTICAL form and tolerance to the parent
Gate V** (parent `:126-133`): **PASS** iff `|x_measured − x_exact_at_row| ≤ 0.0231`
(1.0 % of the exact incident-shock travel 2.30940 at t = 0.2, row nearest y = 0.9).
Applied at each of R1', R2', R3'. **Not widened by a digit** — the whole point is to
test whether the robust family clears the *same* bar.

**Gate T' (grid-convergence triple) — rule 5 in full.** The self-convergence triple
of the Gate V position error across R1'/R2'/R3' (the parent's no-exact-solution
Roache form, `:86-100`, exact 2:1 nesting so restriction is an exact conservative
block average). A non-CONVERGING triple is **NOT A RESULT**; a CONVERGING triple is
graded against its band; no GCI on a non-monotone triple. **No band is loosened.**

The parent's controls carry over and are re-used: the planted 7-whole-cell density
displacement (integer roll is exact → front must move exactly 7·dx, `:185-189`), the
planted-absence control (`:189-193`), and the regression that reproduces the
2026-08-07 recorded Gate V positions on R1/R2 (`:195`).

---

## 5. GRADING PATH — FIXED AT THE FREEZE, PLANTED-ZERO CONTROL

The grading path is the frozen DMR Gate V / triple grader (parent's, blob at this
successor's fresh registration commit), re-used unchanged so R1'/R2'/R3' are graded
by the identical instrument. **The run driver is authored and on disk:**
`verification/runs/DMR_runs/run_dmr_positivity_successor.sh` — sha256
`9d8635e2c3b27f7b826d9164361b191e30fa7558bb8542131c6a9be4232ff7a3`. (Location choice,
recorded here because this §5 designated no driver path: the driver sits alongside
`run_r3.sh` and the successor generator in `verification/runs/DMR_runs/`, named to mark
it a successor; its RUN OUTPUT goes to the fresh successor roots of §5.1(a), never to
the parent `res240`.) It mirrors `run_r3.sh`'s proven idioms exactly and changes only
what the three-level successor requires: it iterates the three registered levels R1'
(N=60, 240×60), R2' (N=120, 480×120), R3' (N=240, 960×240) nested exactly 2:1;
generates each with `make_case_successor.py` (**not** the parent `make_case.py`); writes
each to its own root `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/{R1p,R2p,R3p}`;
carries **rc captured inside the wrapper at every step** (L-"setsid parent returns
zero"), the rule-4 **ABSENT guard per level** (refuse if that level's run dir already
exists), and the parent's step sequence (blockMesh, checkMesh, setExprFields,
decomposePar, `rhoCentralFoam -parallel` on 4 ranks, reconstructPar, writeCellCentres).
Before grading each level it hashes `dmr_locator_v2.py` against its frozen blob
`52aacf9669bcf23e88a0bf7984b299fa8aaf286e` and refuses if it differs, then grades with
it (grade-path integrity, rule 2).

**Cap wiring — the ONE registered hard cap.** The §6 table registers a SINGLE hard cap:
**total 60 core-min**. Its per-level figures (R1' ~0.25, R2' ~1.9, R3' ~33, overhead
~1.5) are **estimates** ("MEASURED-ANCHORED" / "ESTIMATED"), not registered per-level
caps — only "HARD CAP 60 core-min" carries the word cap. The driver therefore enforces
that one registered cap as a single core-second accumulator carried across all steps of
all three levels — mirroring `run_r3.sh`'s single-accumulator design — that **stops the
run and writes a `CAP_BREACH` file** on breach, with no new budget (rule 12). The §6
per-level estimates are printed by the driver as advisory rule-12 calibration
watermarks only and **never** trigger a breach; **no per-level hard cap was invented**
(CLAUDE.md rule 2/12). The **planted-zero controls of §4 are mandated** and must pass before any
verdict: a located shock front is evidence only from a reader shown able to see the
planted 7·dx displacement and the planted absence. Grading is zero-new-compute after
the solves.

---

**AUTHORING NOTE — cfd `lab-lane`, 2026-09-07 (pre-freeze; changes no gate, threshold, cap or label).**
A prior lane correctly refused this freeze because two rule-2 essentials were on disk only as prose.
They are now authored:

- **(d) changed-method artifact — the successor generator — authored.** §5 named "the driver mirrors
  `run_r3.sh`" but was silent on HOW the changed-method case is built, since the DMR case is generated by
  `make_case.py`, not by committed scheme files. The concrete mechanism is now on disk:
  `verification/runs/DMR_runs/make_case_successor.py` — sha256
  `5e19df5b5d966e90135a21000bee857dfe4b1cf0a4d9c95e4e0756156c2d156a`. It is derived from the frozen parent
  generator `make_case.py` (HEAD blob `c6a7addad3c9a8360c6656467c5858bb2ebca5b6`) and its generated case
  OUTPUT is byte-identical to the parent's EXCEPT the registered levers: `reconstruct(rho)` `vanLeer`→`Minmod`,
  `reconstruct(U)` `vanLeerV`→`MinmodV`, `reconstruct(T)` `vanLeer`→`Minmod` (lever 1) and controlDict
  `maxCo` `0.2`→`0.1` (lever 2). A recursive diff of the two generators' output at N=60 shows exactly those
  four lines across the whole case tree (0/, constant/, system/) and no other. The `Gauss Minmod` div lever
  is NON-registered (§3) and is not present. The successor's run driver mirrors `run_r3.sh` unchanged in
  form — it carries NO method levers (the method lives entirely in the generator) — parameterised over the
  three levels below and calling `make_case_successor.py` in place of `make_case.py`.

- **(a) distinct fresh self-contained run roots declared:**
  `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R1p` (1/60, 240×60),
  `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R2p` (1/120, 480×120),
  `verification/runs/DMR_R3_POSITIVITY_SUCCESSOR_runs/R3p` (1/240, 960×240) — nested exactly 2:1, each its
  OWN root, none shared with the parent `verification/runs/DMR_runs`. All three confirmed ABSENT on disk at
  authoring (the parent root exists and is untouched).

- **guard c and Gate V' re-confirmed after these edits.** The successor is graded by the frozen
  `verification/runs/DMR_runs/dmr_locator_v2.py` (blob `52aacf9669bcf23e88a0bf7984b299fa8aaf286e`, unchanged
  since its establishing commit `4590ba56`) — a reader that grades the shock POSITION (`Cx`, `Cy`, `rho` at
  t = 0.2) and reads NO scheme file, so it is method-agnostic and needs no change to grade the Minmod family.
  `GATEV_TOL = 0.0231` (`dmr_locator_v2.py:69`) is byte-identical to the parent frozen Gate V tolerance
  (`DMR_R3_TRIPLE_PREREGISTRATION.md:130`) and to this successor's §4. Nothing in this session touched the
  grader. *(The board-70-era grader sha `a062778d` does not resolve as any object in the current repo; the
  verifiable identity is the blob/commit cited here.)*

- **(e) run driver — the successor DRIVER — authored (2026-09-07, pre-freeze; changes no gate,
  threshold, cap or label).** §5 previously said only "the driver mirrors `run_r3.sh`". The parent
  `run_r3.sh` is hard-wired — a single root `res240`, a single level N=240, a 35.0 core-min cap, and
  it calls the PARENT `make_case.py` — so it could not be reused for a three-level successor. The
  concrete driver is now on disk: `verification/runs/DMR_runs/run_dmr_positivity_successor.sh` — sha256
  `9d8635e2c3b27f7b826d9164361b191e30fa7558bb8542131c6a9be4232ff7a3`, `bash -n` clean. It iterates the
  three registered levels R1'/R2'/R3' (240×60 / 480×120 / 960×240, nested 2:1), calls
  `make_case_successor.py`, writes to the §5.1(a) successor roots (never `res240`), and mirrors
  `run_r3.sh` idiom-for-idiom: rc captured inside the wrapper per step, the rule-4 ABSENT guard per
  level, and — for the ONE registered §6 hard cap (total 60 core-min) — a single core-second
  accumulator across all three levels that stops the run and writes `CAP_BREACH.txt` on breach. **The
  §6 per-level figures are estimates, not registered caps; no per-level hard cap was invented.** Before
  grading a level the driver hashes `dmr_locator_v2.py` against the frozen blob
  `52aacf9669bcf23e88a0bf7984b299fa8aaf286e` and refuses on mismatch (rule 2 grade-path integrity),
  then grades. **No solver was launched authoring it.**

Because the DMR grader reads position and not schemes, the F27-style method-lock does NOT arise for DMR:
the successor is genuinely buildable and gradeable by the frozen instrument. **STATUS: with the generator,
run roots and grader identity above, this draft is complete and freeze-ready pending the supervisor's
check-4 re-take.**

---

## 6. COST — rule 12 (measured anchors from R1/R2)

Measured (`DMR_RESULTS.md:135-137`, 4 ranks, wall × ranks): R2 (1/120) **1.67
core-min**, R1 (1/60) **0.22 core-min**; the parent priced 1/240 at **~15 core-min**
(8× R2, `:146`). `Minmod` at `maxCo` 0.1 roughly doubles the step count of the finest
level versus `maxCo` 0.2 (a real cost of lever 2) and adds a small per-step limiter
cost:

| rung | h | grid | basis | core-min |
|---|---|---|---|---|
| R1' | 1/60 | 240×60 | 0.22 × ~1.1 (limiter) | ~0.25 MEASURED-ANCHORED |
| R2' | 1/120 | 480×120 | 1.67 × ~1.1 | ~1.9 MEASURED-ANCHORED |
| R3' | 1/240 | 960×240 | ~15 × ~2.2 (maxCo 0.1 + limiter) | ~33 ESTIMATED |
| mesh/init/reconstruct/locator | | | parent < 0.5 × 3 | ~1.5 |
| **estimate total** | | | | **≈ 37 core-min** |
| **HARD CAP** | | | | **60 core-min** |

R3' dominates and its 2.2× factor (chiefly the halved Courant number) is the estimate
carrying most of the uncertainty. An overrun of the 60 cap **stops the run** and does
not get a new budget (rule 12). If R3' at `maxCo 0.1` still crashes, that is a
**measured negative result** (the limiter change was insufficient), reported not
softened. Dollars: 60 core-min = 1.0 core-h × $0.0513 = **$0.0513 — DERIVED, NOT
MEASURED** (reported-by-owner, `COMPUTE_BUDGET_CHARTER.md` §5). Well under the $25
ceiling. Calibration row owed at completion.

---

## 7. WHAT THIS SUCCESSOR CAN AND CANNOT SETTLE

- **Can:** whether a positivity-robust reconstruction (`Minmod`, reduced Courant)
  lets the DMR run reach t = 0.2 at 1/240 and produce a CONVERGING three-level Gate V
  triple; and, whichever way it lands, quantify the robustness-vs-accuracy trade at
  Mach 10.
- **Cannot:** claim anything about the *original* frozen `vanLeer` family's triple —
  that remains a two-rung pair with a measured robustness ceiling between 1/120 and
  1/240 (parent `:127-133`), untouched by this successor.

**Nothing is sent, filed, uploaded, registered or posted (rule 7). Draft handed to
the cfd supervisor for the check-4 freeze.**
