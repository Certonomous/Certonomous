# T4d — impinging round jet, H/D = 2, Re = 23 000: the COST-RECALIBRATION successor of T4c that changes only the caps/timeouts — pre-registration (FROZEN)

> **STATUS AT THIS COMMIT: FROZEN, BEFORE ANY SOLVER HAS ITERATED ON ANY `T4d_IJ_*` CASE.**
> NOT BUILT. NOT ENQUEUED. NOT LAUNCHED. **Zero solver core-minutes have been spent on this rung.**
>
> **The grading path is fixed by sha in §12 below** (the five-file freeze set, computed with
> `git hash-object` and sha256 on the exact committed files; the frozen comparator verifies at
> runtime by hashing each file against its committed blob). The heat-transfer supervisor's
> non-delegable §3 checks are complete (2026-09-07): the four T4d scripts are PURE RENAMES of their
> T4c ancestors (reverse-swap byte-identical), and `T4d_registered.json` differs from
> `T4c_registered.json` ONLY in the per-level caps/timeouts/POINT/CEILING/rate plus the
> parent/lineage/cost prose — every band, threshold, reference, floor, control and prediction
> byte-identical. **The build (`blockMesh`/`checkMesh` birth certificate) and the queue entries
> remain WITHHELD** — the fire order is the supervisor's, a separate STAGED phase (coarse+medium
> first; the fine gated on the medium clearing C6.3 < 2e-04) after verifying this freeze commit
> exists. Nothing here authorises a launch or a send (rule 7: SUBMISSIONS REMAIN PARKED).

**Predecessor: T4c** (`docs/campaigns/T-family/T4c_PREREGISTRATION.md`; grade record: T4c
graded **`NOT A RESULT`** by non-completion, 2026-09-07 — coarse FINISHED CLEAN
(`STATUS.T4c_IJ_c`, rc=0, 22.1 core-min, under its 30.2 core-min POINT), medium and fine
supervisor-stopped by targeted SIGTERM before their caps because the caps could not be reached in
time — `STATUS.T4c_IJ_{m,f}` in `verification/runs/T-family/T4c_runs/`). T4d is that record's
successor the way T4c is T4b's and T3f is T3e's — the predecessor is named here on a line-leading
`Predecessor:` field, in the recognised K0g/T4b form, so the §2ay / completion-enforcement check
sees the chain **T4 → T4b → T4c → T4d**. **T4d carries over every band, reference, threshold,
floor, control, prediction and PHYSICS/DESIGN of T4c UNCHANGED** (T25 ruling: a band, threshold or
reference is never widened to manufacture a pass). **What changes is ONLY the per-level cost caps
and timeouts** — the three things the T4c run measured to be too small — and nothing else. This is a
cost recalibration, not a physics change.

Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED / GATE FAIL / NOT A RESULT /
BLOCKED / PENDING.**

---

## 0. Why a successor, and why it is a COST RECALIBRATION and not a diagnosis

T4c returned `NOT A RESULT` (2026-09-07). **The physics and design were right.** The registered
changes against T4b (Change A `nrj = 3N/2`, Change B under-relaxation 0.7→0.6, Change C `endTime`
schedule 30000/60000/64000 with `writeInterval` pinned 2000/3000/4000) all stood, and **the coarse
level COMPLETED CLEAN** under them: `STATUS.T4c_IJ_c` reads `rc=0`, `wall_s=1326`, `core_min=22.100`,
`capped=no`, `note=clean` — **inside** its 30.2 core-min POINT and well inside its 65 core-min cap.

**The cost model did not.** The T4c caps were sized (rule 12) from **T4b's** measured per-cell rates
(`T4b_RESULTS.md` §7: c 6.994e-06, m 7.135e-06, f 9.754e-06 core-s/cell-it). On the finer T4c mesh
those rates under-predicted the true cost badly: the medium ran at **2.60e-05** core-s/cell-it
(**3.65×** the T4b basis) and the fine at **3.67e-05** (**3.76×**) — measured and recorded in
`STATUS.T4c_IJ_m` / `STATUS.T4c_IJ_f` (`per_cell_core_s`, `ratio_to_T4b_basis`, `last_iteration`
1890 / 335). At those settled rates neither the medium (cap 500 core-min) nor the fine (cap 2880
core-min) could reach `endTime` within cap; the supervisor stopped both by targeted SIGTERM before
the caps rather than waste compute running to a guaranteed cap-stop (rule 12), and graded the rung
`NOT A RESULT` by non-completion.

Sanaa's law: **the only acceptable terminal fail is a measured OpenFOAM capability gap; everything
else is fixed until it runs.** A cap that was too small is not a capability gap — the coupled solver
runs; it is dearer than T4b predicted on the finer mesh. T4d fixes it the way rule 12 mandates: it
sizes the caps from the **predecessor-on-the-identical-mesh MEASURED rate** (the C-155 correction,
T13 — exactly what T4c did against T4b, now with T4c's own measured numbers), and changes nothing
else. **The physics/design freeze of T4c is inherited byte-identical** (§2).

## 1. The case — inherited from T4c §1 (and thus T4b §1) UNCHANGED

Normally-impinging round air jet from a fully developed pipe (recycling `mapped` inlet), H/D = 2,
Re_D = 23 000, D = 0.02 m, ν = 1.5e-05 m²/s, U_bulk = 17.25 m/s, Pr/Pr_t = 0.71/0.85, plate at
1000 W/m², jet 293.15 K; `buoyantBoussinesqSimpleFoam` (β = 0, passive T), `kOmegaSST`, steady,
axisymmetric 2.5° wedge, wall-resolved on every level. **All boundary conditions per field per
patch, `transportProperties`, `turbulenceProperties`, `g` and `fvSchemes` are the frozen
`build_t4.fields()` / `constant_files()` / `system_files()` output, unchanged** — the same writers
T4c and T4b called. Reference: ERCOFTAC Classic Collection case025 `ij2lr`, HELD at
`docs/campaigns/T-family/reference-data/ercoftac_case025/`, re-read at every run.

## 2. The ONE registered change against T4c, and NOTHING else

**Change (cost only) — the per-level cap and timeout are re-sized from the T4c MEASURED per-cell
rates** (`STATUS.T4c_IJ_*`), so every level can COMPLETE to its `endTime` with margin. The medium
and fine caps rise ~3.7× from T4c's under-prediction; the coarse cap tightens to 2× its now-measured
POINT. See §9 for the arithmetic and the sized values.

**Carried over from T4c BYTE-IDENTICAL — the entire physics and design (rule 6, frozen files never
edited; T4d instruments are new files by copy+rename, no logic change):**

- **Change A (mesh):** jet-core/pipe radial `nrj = 3N/2`, `r = 2` preserved in every direction,
  cells **3.75 N²** — coarse **8 640**, medium **34 560**, fine **138 240** (T4c §2 table).
- **Change B (relaxation):** under-relaxation of U, T, k, ω = **0.6** (p_rgh 0.3 unchanged),
  family-wide, IN the design (T4c §2, heat-transfer supervisor's §3 ruling 2026-09-07).
- **Change C (schedule):** `endTime` **30 000 / 60 000 / 64 000**; `writeInterval` **PINNED
  2 000 / 3 000 / 4 000**; `purgeWrite 2` unchanged — so C6.3 measures a change over the identical
  iteration window (§3; the reconsideration below KEEPS these). The pin is unchanged so the fine and
  medium C6.3 windows are byte-identical to T4c's design.
- **Every BC, scheme, transport property, the wedge, the three graded stations G1/G2/G3, all bands,
  references, controls C1–C6 with their thresholds and floors, every planted-zero control, and every
  prediction P1–P9** — carried from T4c unchanged (§6, §7).

`build_t4d.py` is therefore a **pure rename** of `build_t4c.py` (identical `nrj = 3N/2`, relaxation
0.6, `endTime` 30000/60000/64000, `writeInterval` pin logic, each behind its refuse guard); only the
`CASE_PREFIX = "T4d_IJ_"`, the registered-JSON filename and the docstring differ. The cap/timeout
values live in **`T4d_registered.json`** (and, if `launch_t4d.sh` carries per-case timeouts rather
than reading them from the JSON, there too — the supervisor's §3 diff confirms which). This is the
one substantive change in the whole freeze set.

## 3. The `endTime` schedule — RECONSIDERED against the C6.3 decay arithmetic, and KEPT

Task item 2 asks whether the fine (and medium) `endTime` genuinely NEEDS its full window for the
predicted C6.3 to clear the 2e-04 floor with margin, or whether a shorter window clears it and saves
a large fraction of the ~3.8-day fine leg. **Verdict: KEEP 64 000 (fine) and 60 000 (medium). A
shorter window is NOT defensible, on the arithmetic and on the evidence.**

**The reconsideration produced NO new decay data.** T4c was SIGTERM-stopped at `last_iteration`
**335** (fine) and **1890** (medium) — both *before the first checkpoint* (fine `writeInterval` 4000,
medium 3000), so T4c measured **only the per-cell compute rate, nothing about the convergence rate.**
The C6.3 sizing therefore still rests on the same T4b-measured clean decay it did in T4c §3 (fine
ρ ≈ 0.44 per 4 000-it, 2nd-half log-regression; T4c P9/§5.4), with no update available.

**The fine arithmetic (start 8.170e-04 @ T4b endTime 40 000, W = 4 000, target ≤ 1e-04 = 2× below
the 2e-04 floor):**

| endTime | blocks past 40 000 | predicted C6.3 @ measured ρ = 0.44 | predicted C6.3 @ pessimistic ρ = 0.75 |
|---:|---:|---:|---:|
| 52 000 | 3 | 6.96e-05 | **3.45e-04 — FAILS the floor** |
| 56 000 | 4 | 3.06e-05 | **2.59e-04 — FAILS the floor** |
| 60 000 | 5 | 1.35e-05 | 1.94e-04 (bare — no 2× margin) |
| **64 000** | **6** | **5.93e-06** | **1.45e-04 — clears the floor even pessimistically** |

Only **64 000** keeps the C6.3-clears-2e-04 prediction honest under the pessimistic ρ = 0.75. Every
shorter window clears the floor **only if** the T4d decay is as fast as T4b's ρ = 0.44 — and T4d has
**less** confidence in that, not more: the mesh is finer (×1.43 cells vs T4b) and the relaxation
lower (0.7→0.6), both slowing convergence, and the measured **3.65–3.76× per-cell compute slowdown**
is consistent with a stiffer, slower-settling system. Shortening the window would rest the prediction
on the optimistic rate alone and delete exactly the disclosed safety margin §3 was built to hold.
**That is shortening the window to game C6.3, which the T4c discipline and the task forbid.** The
same reasoning keeps the **medium at 60 000** (its window is sized for the Change-B limit-cycle break,
also unmeasured post-SIGTERM). The `writeInterval`/`purgeWrite` pin is unchanged so C6.3 measures the
identical window. The ~3.8-day fine leg (§9) is the honest cost of an at-risk C6.3 prediction, not
slack to be trimmed.

| level | measured tail behaviour (from T4b; no T4c update) | endTime | predicted C6.3 | margin to floor |
|---|---|---:|---:|---:|
| c | already fully settled by ~4 000 it; coarse failures were C2 + C6.1 (mesh, not time) | **30 000** | ~1e-09 | settled |
| m | limit-cycle plateau — Change B breaks it; ×2 iterations let the damped decay reach the floor | **60 000** | **≤ 1e-04** (thin — P5) | ≥ 2× |
| f | clean decaying transient, ρ ≈ 0.44 per 4 000-it | **64 000** | **≤ 8e-05** | ≥ 2.5× |

## 4. Completion rule and controls — carried over from T4c UNCHANGED

`mark_done_t4d.py` is `mark_done_t4c.py` (itself `mark_done_t4b.py`) with only the rung id and case
names changed: the strict all-or-nothing rule (rule 4) stands — `rc = 0`, an `End` line, last time
== `endTime`, fields **`T U p_rgh alphat nut k omega phi`** present at `endTime`, `ExecutionTime`
count == `endTime`, and every field NEWER than the case's own `0/T` (the age guard); infrastructure
fields disclosed if absent, `capped` never a completion conjunct, absent `STATUS` → REFUSE `exit 2`.
**Because T4d re-runs all three levels fresh into new `T4d_IJ_*` case directories, the age guard is
satisfiable** (a guard refuses a case where `0` or a time dir already exists — the T4c coarse dirs
are a different rung and are not touched).

## 5. THE EVIDENCE — the T4c run STATUS files the recalibration is built on

Read-only analysis of the T4c STATUS files; no compute launched, nothing written to the T4c run tree.

- **`STATUS.T4c_IJ_c`** (coarse, FINISHED): `rc=0`, `wall_s=1326`, `ranks=1`, `core_min=22.100`,
  `capped=no`, `checkmesh_rc=0`, `note=clean`. Implied per-cell rate 22.100 core-min ×60 ÷
  (8 640 × 30 000) = **5.12e-06** core-s/cell-it — **0.74×** the T4b basis 6.994e-06 (the coarse ran
  *cheaper* than T4b predicted; its cap can shrink).
- **`STATUS.T4c_IJ_m`** (medium, SIGTERM at it 1890): `per_cell_core_s=2.60e-05`,
  `ratio_to_T4b_basis=3.65`. Cumulative rate peaked ~1.25 it/s then declined to ~1.10 it/s — getting
  dearer, not clearing a transient; a cap-stop before `endTime` 60 000 was guaranteed under the 500
  core-min cap.
- **`STATUS.T4c_IJ_f`** (fine, SIGTERM at it 335): `per_cell_core_s=3.67e-05`,
  `ratio_to_T4b_basis=3.76`, settled flat ~0.19 it/s; a cap-stop before `endTime` 64 000 was
  guaranteed under the 2 880 core-min cap; running to cap would waste ~48 core-h (rule 12).

These three measured rates — **c 5.12e-06, m 2.60e-05, f 3.67e-05 core-s/cell-it (ranks = 1)** — are
the authoritative rule-12 basis for the T4d caps (§9): the predecessor's own measured rate on the
identical mesh.

## 6. Controls — every one carried over from T4c (and T4b) UNCHANGED, byte-identical readers

`analyse_t4d.py` is `analyse_t4c.py` with only the rung id, the registered-JSON filename and the
case-name prefix changed; **no reader, threshold, band, floor, gate order or planted control is
touched.** It imports the frozen `analyse_t4.py` unchanged, as T4c and T4b did. Carried over:

- **C1 / C1b** plate / pipe-wall `y+_max < 1.0` via the solver's own `-postProcess -func yPlus`
  reader, **with the y+ scaling control** (U ×4 → y+ ×2.000000000 exactly, on plate AND pipeWall,
  and the blind generic reader returning 0 beside it — the blind reader shown blind is what makes the
  seeing reader's zero evidence).
- **C2** nozzle-exit `U_c/U_bulk` within ±3 % of 1.2245; planted control aimed at the profile's max.
- **C3** global mass conservation `|Σφ|/|φ_inlet| < 1e-3`; planted control `φ_in ×1.01`.
- **C4** planted-zero controls (rule 3), both arms, on EVERY reader on the grading path — G-row
  profile (`PLANT = 1.234e-03`), y+, exit-line, flux.
- **C5** strict completion + age guard (`mark_done_t4d.py`, §4).
- **C6.1** every `p_rgh` initial residual over the last 2 000 iterations ≤ 1e-06; **C6.2** directional
  growth ratio ≤ 1.05; **C6.3** max G1/G2/G3 peak `U/U_bulk` change between the last two checkpoints
  ≤ 2e-04.
- **Roache floors** `STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05` imported from `scripts/roache_triple.py`;
  gate order per rule 5.

**Graded rows (carried over, references re-read from the held file):** G1 r/D = 1.0, ref 1.0890,
band [1.0690, 1.1090]; G2 r/D = 2.0, ref 0.7888, band [0.7688, 0.8088]; G3 r/D = 3.0, ref 0.4632,
band [0.4432, 0.4832]. Nu rows remain REPORT-ONLY / **BLOCKED** (T4 §2.1). A PASS on G1–G3 is a joint
code-plus-closure statement; no eigenspace band is armed.

## 7. Predictions — carried over from T4c UNCHANGED (to land in `T4d_registered.json`)

The physics and design are byte-identical to T4c, so every prediction is carried over verbatim; none
is loosened. (P1 plate y+ ~0.69/0.35/0.18; P1b pipeWall y+ ~0.40/0.20/0.10, < 1 all levels;
P2 coarse `U_c/U_bulk` 1.191, ≥ 1.1878 — THIN; P2m/P2f 1.20/1.21; P3 mass imbalance ~1e-05;
P4 coarse C6.1 floor 5e-07, < 1e-06 — a prediction; P5 medium C6.3 8e-05, ≤ 1e-04 — THINNEST, with
the WITHOUT-relaxation extrapolation ≈ 2.14e-04 recorded; P6 fine C6.3 3e-05, ≤ 8e-05; P7 G1/G2/G3
fine ≈ 1.085/0.812/0.537 CONVERGING; P8 all three triples CONVERGING; P9 fine limit-cycle
contingency, remedied by 0.6→0.5 not a re-diagnosis.) The full P1–P9 table with grounds is T4c §7;
it is copied into `T4d_registered.json` unchanged. **The two disclosed thin margins remain P2
(coarse C2) and P5 (medium C6.3).** The pre-identified contingencies (P2 → `nrj = 2N`; P5/P9 →
under-relaxation 0.6→0.5) are carried unchanged — sequenced next steps on a measured finding, not
band moves, and none can alter a gate, band, threshold or floor.

## 8. Instruments and the measurement-script changes, as diffs (for the supervisor's §3 read)

The freeze set will live in `verification/runs/T-family/T4d_runs/`: `build_t4d.py`, `analyse_t4d.py`,
`mark_done_t4d.py`, `launch_t4d.sh`, `T4d_registered.json`, and the three case dictionaries after the
build. Every change from the T4c instrument is a diff to be read by the supervisor before belief
(`SUPERVISION_CHARTER` §3). In summary:

- **`build_t4d.py`** — **pure rename from `build_t4c.py`**: `CASE_PREFIX = "T4d_IJ_"`, registered-JSON
  filename, docstring ONLY. `nrj = (3*N)//2`, the four `0.6` relaxation factors, the `endTime`
  30000/60000/64000 schedule, the `writeInterval` 2000/3000/4000 pin (with its exact-count and
  `endTime % writeInterval == 0` refuse guards), and the `residualControl` removal are all
  **unchanged** — the physics/design is inherited byte-identical.
- **`analyse_t4d.py`**, **`mark_done_t4d.py`**, **`launch_t4d.sh`** — rung-id / path / case-name
  renames ONLY; no reader, threshold, band, floor, gate, completion clause or launch guard changed.
  The frozen `analyse_t4.py` is imported unchanged.
- **`T4d_registered.json`** — the ONE substantive change: the per-level `cap` (core-min) and
  `timeout` (s) values re-sized to §9 (cap: coarse 45, medium 1800, fine 10824; timeout:
  2700 / 108000 / 649440). Bands, thresholds, floors, `endTime`, `writeInterval` and predictions
  P1–P9 are copied from `T4c_registered.json` unchanged.

The verbatim unified diffs and the selftest evidence belong in the lane's build/freeze-phase hand-off
to the supervisor, **not in this draft** — this document is pre-build. **No frozen T4/T4b/T4c file is
modified** (rule 6): T4d is new files by copy+rename.

## 9. Cost — rule 12, from T4c's OWN MEASURED per-cell-iteration rates (the recalibration)

**Rate basis.** T4c measured `core-s per cell-iteration` **c 5.12e-06, m 2.60e-05, f 3.67e-05**
(`STATUS.T4c_IJ_{c,m,f}`; §5). Using the predecessor's own measured per-level rates on the identical
mesh is the C-155 correction (T13) — the same discipline T4c applied against T4b, now with T4c's
measured numbers, which is exactly what T4c's under-prediction (medium 3.65×, fine 3.76×) proved was
needed. CEILING = 1.5× POINT and cap = 2× POINT preserve T4c's structure; `timeout_s` = cap_core_min
× 60 (ranks = 1), matching T4c's coarse 65 cm → 3 900 s, medium 500 → 30 000, fine 2 880 → 172 800.

| level | cells | iterations | measured rate (core-s/cell-it) | **POINT core-min** | CEILING (1.5×) | **cap (2×) core-min** | `timeout` s | wall @ POINT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `T4d_IJ_c` | 8 640 | 30 000 | 5.12e-06 | **22.1** | 33.2 | **45** | 2 700 | 0.37 h |
| `T4d_IJ_m` | 34 560 | 60 000 | 2.60e-05 | **898.6** | 1 347.8 | **1 800** | 108 000 | 14.98 h |
| `T4d_IJ_f` | 138 240 | 64 000 | 3.67e-05 | **5 411.6** | 8 117.4 | **10 824** | 649 440 | **90.19 h ≈ 3.76 d** |
| **total** | | | | **6 332.3** (105.5 core-h) | 9 498.5 (158.3 core-h) | **12 669** (211.1 core-h) | | |

**Arithmetic (POINT = cells × iterations × rate ÷ 60):**
- coarse 8 640 × 30 000 × 5.12e-06 = 1 327.1 core-s = **22.1 core-min** (matches the T4c measured
  22.100 core-min exactly — the rate is derived from that completion).
- medium 34 560 × 60 000 × 2.60e-05 = 53 913.6 core-s = **898.6 core-min**.
- fine 138 240 × 64 000 × 3.67e-05 = 324 698.1 core-s = **5 411.6 core-min**.

**Change vs T4c:** coarse cap 65 → **45** core-min (the measured 5.12e-06 is 0.74× the T4b basis, so
the cap tightens toward the measured POINT while keeping the 2× margin — the coarse already completed
at 22.1 core-min under this cap with 2× headroom); medium cap 500 → **1 800** (×3.60, tracking the
3.65× rate miss); fine cap 2 880 → **10 824** (×3.76, tracking the 3.76× rate miss).

**FINE-LEG WALL TIME, FLAGGED (task item 1).** At the measured rate the fine leg is **90.19 h ≈ 3.76
days** at POINT (ranks = 1), and **180.4 h ≈ 7.52 days** at the 2× cap — **by far the single longest
run this ladder has scheduled** (T4c's estimate was ~24 h; the measured rate is ~3.76× dearer). Ranks
stay 1 on every level (F15 decomposition-confound ruling: a ladder differs only in mesh). An overrun
stops the run at its cap (`capped=yes` → `NOT A RESULT`, not re-launched larger).

**USD, DERIVED not measured**, reported-by-owner rate $0.0513/core-h (`COMPUTE_BUDGET_CHARTER` §5;
the box cannot read its own billing): **POINT $5.41, CEILING $8.12, cap $10.83** for the whole rung.
Per run (rule 12's $25 pre-authorised unit), the dearest is the fine at cap: 180.4 core-h × 0.0513 =
**$9.25** — inside the $25 band; the whole rung is still well inside Sanaa's 2026-08-21 blanket, and
still costed here per rule 12. Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at
completion (rule 12).

## 10. Re-running all three levels fresh under one consistent registration (task item 4)

The T4c coarse already completed clean (22.1 core-min, `STATUS.T4c_IJ_c`). **T4d nonetheless re-runs
all three levels fresh** into new `T4d_IJ_{c,m,f}` case directories, for three reasons: (1) the age
guard (rule 4) refuses a case whose `0` or a time dir already exists, so re-using the T4c coarse
output is not admissible under one consistent T4d registration; (2) a single registration grading all
three levels against the same frozen path is cleaner and auditable than mixing a T4c-graded coarse
with T4d medium/fine; (3) the coarse is cheap — 22.1 core-min (~$0.019 derived), a negligible
fraction of the 105.5 core-h rung. There is no case for carrying the coarse over.

## 11. What this rung cannot see

- No Nu row is graded (BLOCKED, T4 §2.1); a PASS on G1–G3 is a joint code-plus-closure statement.
- A different mesh family from T4b (3.75 N² vs 2.625 N²): no cross-rung triple; T4b/T4c numbers are
  context, never a level.
- **The refined-mesh + relaxation-0.6 DECAY rate is still unmeasured** — T4c was SIGTERM-stopped
  before its first checkpoint (§3, §5), so it measured the compute rate, not the convergence rate.
  §3 sizes `endTime` conservatively against the T4b ρ; if a level's C6.3 still exceeds 2e-04 at
  `endTime`, that is a measured finding for the §7 contingency (0.6→0.5), not a terminal fail.
- The wedge is one 2.5° sector: nothing about azimuthal structure.
- Nothing here authorises a launch or a send (rule 7: SUBMISSIONS REMAIN PARKED). No frozen
  T4/T4b/T4c file is modified.

## 12. The freeze set — committed in the same commit as this document

Git blobs computed with `git hash-object` on the exact files committed; sha256 first 16. The frozen
comparator prints its own `sha256_of()` provenance at runtime (`analyse_t4d.py` `grade()`); verify the
frozen file **is** the file that ran by hashing it against the committed blob below. No self-reference:
this freeze table lives in the `.md`, so the `.md` itself is not among the hashed files.

| file | git blob | sha256₁₆ | lines / note |
|---|---|---|---:|
| `verification/runs/T-family/T4d_runs/analyse_t4d.py` | **`d616754e`** | `0e9b13f796014631` | 753; AST 0; selftest 20/20 (`python3` and `-O`); PURE RENAME from `analyse_t4c.py` (frozen `analyse_t4.py` imported unchanged) |
| `verification/runs/T-family/T4d_runs/mark_done_t4d.py` | **`8a281d72`** | `1d488c37134246af` | 256; AST 0; selftest PASS both interpreters; PURE RENAME from `mark_done_t4c.py` |
| `verification/runs/T-family/T4d_runs/build_t4d.py` | **`f3da0fe2`** | `7e7e954f394a0ff6` | 282; AST 0; PURE RENAME from `build_t4c.py` (physics/design byte-identical: nrj 3N/2, relaxation 0.6, endTimes, writeInterval pin, all refuse guards) |
| `verification/runs/T-family/T4d_runs/launch_t4d.sh` | **`5ec16224`** | `dba66ed8b3942491` | 185; `bash -n` clean; PURE RENAME from `launch_t4c.sh`; rc-capture verbatim; reads the cap from `T4d_registered.json` |
| `verification/runs/T-family/T4d_runs/T4d_registered.json` | **`820bd11c`** | `2ad1fea29dc4c534` | 284; the ONE substantive change — §9 cap/timeout/POINT/CEILING/rate values; bands, thresholds, floors, `endTime`, `writeInterval` and predictions P1–P9 copied from `T4c_registered.json` |

Frozen inherited instruments, unchanged in the worktree at this freeze (imported, never copied):
`analyse_t4.py` (its readers, `classify`, `gci`, `planted_zero_control`, `sample_profile`, `peak_of`),
`build_t4.py` (`header`, `grading_ratio`, `system_files`, `constant_files`, `fields`),
`scripts/roache_triple.py` (`STAGNANT_FLOOR`, `P_MIN`), `scripts/check_case_provenance.py`,
`scripts/check_launcher_can_launch.py`.

**Still WITHHELD until the supervisor's separate STAGED launch phase:** the build (`blockMesh`/
`checkMesh` birth certificate) and the queue entries. The launch is coarse+medium first, with the
fine's ~3.76-day run gated on the medium completing and clearing C6.3 < 2e-04 (the medium is the
limit-cycle level that tests whether relaxation-0.6 damped it).
