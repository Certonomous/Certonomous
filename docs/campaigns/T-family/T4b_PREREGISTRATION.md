# T4b — impinging round jet, H/D = 2, Re = 23 000, wall-resolved successor of T4: pre-registration (FROZEN, BUILT, NOT FIRED)

**Document v1.0. FROZEN ON COMMIT, BEFORE ANY SOLVER HAS ITERATED ON ANY
`T4b_IJ_*` CASE.** Campaign T, rung **T4b**, the successor the heat-transfer
supervisor ordered on the T4 grade record (`7422591b`, `NOT A RESULT` ×3;
`docs/LAB_STATE.md` §10 ruling: *"T4b, registered fresh — coarse level
first-layer sized so y+ < 1 on `c`, the three controls as readers INSIDE the
frozen comparator, same ERCOFTAC case025 reference (held). No paper can block
it."*). Verdict vocabulary fixed by `CLAUDE.md` rule 1: **PASS / GATE REACHED /
GATE FAIL / NOT A RESULT / BLOCKED / PENDING.** Nothing here authorises a
launch: **the fire order is the heat-transfer supervisor's**, after the personal
checks of `SUPERVISION_CHARTER.md` §3; the queue entries are prepared in the
registering lane's scratchpad and are dropped by the supervisor, never by the
lane (`QUEUE_ENTRY_STANDARD.md` §1).

**Condition (`CLAUDE.md` rule 2), and how it was checked.** At the moment this
file is committed, `verification/runs/T-family/T4b_runs/` holds the five
instruments of §11, `T4b_registered.json`, and three case directories
`T4b_IJ_c`, `T4b_IJ_m`, `T4b_IJ_f`, each holding `0.orig/ constant/ system/
BUILD.txt CASE.txt log.blockMesh log.checkMesh.build` and **no `0/`, no
numeric time directory, no `log.solve`, no `log.launch`, no `processor*`**;
the run root holds **no `STATUS.T4b_IJ_*`, no `DONE.T4b_IJ_*` and no
`gate_t4b.json`** (checked with `ls` and `find -regex` immediately before the
commit; the launcher, `mark_done_t4b.py` and the queue validator's age guard
all refuse on any of them, and `mark_done_t4b.py` and `analyse_t4b.py` both
**refuse on the live tree today**, `exit 2`). **Zero solver core-minutes have
been spent on this rung.** What did run, disclosed: `blockMesh` and `checkMesh`
on the three cases (the birth certificate, §4; 0.07–1.4 s each), and **one
one-iteration smoke of the coarse case in a scratch root outside the
repository** (§8: `check_launcher_can_launch.py` ARM 2's form, real solver,
`endTime 1`, **rc 0, reached `Time = 1`, 0.18 s wall**), whose fields were
used only to exercise the comparator's live reader controls (§6.2) and are
not in the run tree.

**Provenance of the build.** A previous lane built the cases and drafted the
instruments and `T4b_registered.json`, then died on a usage limit before
writing this document. This lane read every file, ran every selftest under
`python3` and `python3 -O`, diffed each instrument against its T4 parent (§7,
the supervisor's check-1 table), verified the built dictionaries against the
mandate, and repaired exactly what §7.3 lists — before anything was committed
and before anything ran.

---

## 0. Why a successor, in one paragraph

T4 (`T4_PREREGISTRATION.md`, `T4_RESULTS_2026-08-26.md`) returned
`NOT A RESULT` ×3: gate (1) fired because levels `c` and `f` failed the
directional C2 not-growing residual test on residual floors of 5.5e-09 /
9.0e-10 (a test that fired on a 1.0001 window ratio, i.e. on noise, on a
19 000-iteration plateau); the triples were DIVERGENT / OSCILLATORY /
OSCILLATORY; **control C1 fired on `c` (plate y+_max 1.2480 > 1.0)** exactly
as T4 AMENDMENT 2 §A2.4 had registered as a risk; and the frozen comparator
**carried no y+ / C2 / C3 reader at all** — §9's controls were named in the
registration and absent from the grading path, so the lane's y+ numbers were a
measurement outside the frozen path. Two instrument facts came out of it:
generic `postProcess -func yPlus` returns 0 on every patch here (no turbulence
model in the database) and only the solver's own `-postProcess` mode sees y+;
and the pipe wall sat at y+ 30 / 20 / 13 under `nutLowReWallFunction` because
T4's jet-core radial grading put its **coarsest** cell on the pipe wall, a
registration gap C1 did not cover. T4b is that record's successor: **no
threshold relaxed, no band moved**; the coarse first layer halved so C1 can
pass on `c`; the pipe wall resolved and gated (C1b); every control a reader
inside the frozen comparator with its own planted control; the not-growing
test given the noise tolerance T4's own plateaus measured; `residualControl`
removed so the run length is the registered `endTime` (L-141).

## 1. The case — inherited from T4 §1–§3 unchanged

Normally-impinging round air jet from a fully developed pipe (recycling
`mapped` inlet sampling 5 D upstream), H/D = 2, Re_D = 23 000, D = 0.02 m,
ν = 1.5e-05 m²/s, U_bulk = 17.25 m/s, Pr/Pr_t = 0.71/0.85, plate at constant
heat flux 1000 W/m², jet 293.15 K; `buoyantBoussinesqSimpleFoam` with β = 0
(passive T), `kOmegaSST`, steady, axisymmetric wedge 2.5°, wall-resolved on
every level. **Boundary conditions per field per patch are T4 AMENDMENT 2
§A2.2's table, produced by the frozen `build_t4.fields()` and
`constant_files()` called unchanged** (blob `ff032f3e`): measured with `diff`
before the freeze, `0.orig/{U,p_rgh,T,alphat,nut,k,omega}`,
`constant/{g,transportProperties,turbulenceProperties}`, `system/fvSchemes`
and `system/controlDict` of `T4b_IJ_c` are **byte-identical to `T4_IJ_c`'s**
(likewise `m`/`f`). `system/fvSolution` differs in **exactly one block**:
the `residualControl { p_rgh 1e-7; U 1e-7; T 1e-7; k 1e-7; omega 1e-7; }`
line of T4's frozen writer is **removed** (L-141; §3). `system/blockMeshDict`
is new (§2).

## 2. The mesh family — three levels, r = 2 exactly, two registered changes from T4

Built by `build_t4b.py` (§11), which imports the frozen `build_t4.py` and
reuses its `header()`, `grading_ratio()`, `system_files()`, `constant_files()`
and `fields()`; only `block_mesh_dict()` is new. Same three-block wedge
topology as T4 (collapsed axis edge). **The two mesh changes, stated:**

1. **First-cell height halved at every level** — 1.2e-05 / 6.0e-06 / 3.0e-06 m
   (T4: 2.4e-05 / 1.2e-05 / 6.0e-06). Ground: T4 measured plate y+_max 1.2480
   / 0.6466 / 0.3383 at first-cell **centres** 1.2e-05 / 6e-06 / 3e-06 m,
   i.e. u_τ,max = 1.560 / 1.617 / 1.692 m/s; at T4b's coarse centre 6.0e-06 m
   that is y+ 0.62 at T4's coarse u_τ and 0.71 at an extrapolated 1.78 m/s;
   C1 fires on `c` only above u_τ,max = 2.5 m/s. r = 2 is kept exactly.
2. **The jet-core/pipe radial grading is inverted** so the fine cell sits on the
   pipe wall / nozzle lip at the same first-cell height as the plate (T4's
   `simpleGrading(g_pipew …)` with g > 1 along axis→r0 put the **coarsest**
   cell, 1.7e-03 m at `c`, on the pipe wall — hence y+ 30/20/13). To keep the
   jet-core cell-to-cell growth below 1.15 (it would be 1.249 at N/2) the
   jet-core/pipe radial division is **3N/4** instead of N/2; cells are
   therefore **2.625 N²** (T4: 2.25 N²).

| level | `N` | **cells** (`log.checkMesh.build`) | first cell (m), plate AND pipe wall | first-cell centre y_p (m) | jet-core radial growth q | `endTime` | `writeInterval` |
|---|---:|---:|---:|---:|---:|---:|---:|
| `T4b_IJ_c` | 48 | **6 048** | 1.2e-05 | 6.0e-06 | 1.1421 | 20 000 | 2 000 |
| `T4b_IJ_m` | 96 | **24 192** | 6.0e-06 | 3.0e-06 | 1.0680 | 30 000 | 3 000 |
| `T4b_IJ_f` | 192 | **96 768** | 3.0e-06 | 1.5e-06 | 1.0333 | 40 000 | 4 000 |

Divisions (`CASE.txt`): jet-core/pipe radial 36/72/144, wall-jet radial
72/144/288, axial 48/96/192, pipe axial 24/48/96; gradings plate 399.8 /
410.0 / 415.3, jet-core radial 0.009566 / 0.009335 / 0.009222 (< 1: fine at
r0), wall-jet 366.7 / 372.8 / 375.8, pipe axial 8. `r21 = r32 = 2` in every
direction by construction. `purgeWrite 2`. **T4b is a different mesh family
from T4** (2.625 N² vs 2.25 N², inverted core grading); no triple is ever
formed across the two rungs.

## 3. `endTime`, no `residualControl`, and the completion rule

`endTime` 20 000 / 30 000 / 40 000 as T4 (T4 reached every one with rc 0, and
its residuals plateaued by iteration 562 / 1 208 / 3 472). **`residualControl`
is removed** (L-141): the run length is the registered `endTime`, so the strict
rule's "last time == `endTime`" clause is decidable and convergence is judged
by the comparator from the residual history and the written checkpoints,
never by the solver. `deltaT 1`, steady SIMPLE.

**Completion rule (rule 4), strict and all-or-nothing, `mark_done_t4b.py`
(§11), field classes per L-342** (`d4d0c29d`; `mark_done_t3_rff.py` is the
applied pattern): **physics-critical** — solver `rc = 0` read from the
in-wrapper `STATUS.T4b_IJ_*` (written by `launch_t4b.sh` in the run root,
never by a poller); an `End` line in `log.solve`; last time == `endTime`;
fields `T U p_rgh alphat nut k omega phi` present at that time (`phi` because
C3 reads it); `ExecutionTime` count == `endTime`; **every field at `endTime`
NEWER than the case's own `0/T`** (touched last at launch — the age guard).
Any failure → `NOT DONE`, no marker; **an absent `STATUS` is a REFUSAL
(`exit 2`)**, never an inference from an `End` line. **Infrastructure** —
`wall_s timeout_s ranks core_min capped checkmesh_rc started_utc ended_utc
solver_path note`: absent → `NOT MEASURED`, disclosed in the marker line,
**grade proceeds**. **`capped` is NOT a completion conjunct** (the T4/T11
defect the L-342 audit found CONFLATING, rows 30/46); it only labels a
non-zero rc as CAPPED (wall_s ≥ timeout_s: rule 12, the run stopped at its
cap, `NOT A RESULT`, never re-launched larger) or CRASH (a finding until
triage). The queue runner writes its own `STATUS.<case_id>` **inside the case
directory** (`QUEUE_RUNNER.md` step 4); that file is the launch argv's exit
status, an infrastructure record, and `mark_done_t4b.py` never reads it.

## 4. Birth certificate — issued before the freeze

`blockMesh` rc 0 and `checkMesh` rc 0 on all three (`BUILD.txt`,
`log.checkMesh.build`, sha256 `0d9ac885…` / `d187838c…` / `2b1676a2…`):

| level | cells | faces | max aspect ratio (cells flagged) | max skewness | non-orthogonality | min volume (m³) |
|---|---:|---:|---:|---:|---:|---:|
| `c` | 6 048 | 24 300 | 1 627.44 (14) | 0.3308 | 0 | 1.26e-13 |
| `m` | 24 192 | 96 984 | 1 639.08 (52) | 0.3308 | 0 | 3.14e-14 |
| `f` | 96 768 | 387 504 | 1 644.76 (192) | 0.3308 | 0 | 7.86e-15 |

`checkMesh` prints `Failed 1 mesh checks` on every level — the high-aspect-ratio
check, the same class and the same numbers as T4's 1 626 / 1 639 / 1 645
(T4 §5 disclosed them as near-wall clustering on a wall-resolved mesh);
skewness and non-orthogonality are identical across levels, the
geometric-similarity check T4 §5 used. `scripts/check_case_provenance.py
--case T4b_IJ_c`: **clean** (no compressible-family token) — and the launcher
now runs that check itself before arming (§8). `polyMesh` is **not committed**
(the family's convention: T4 committed no case files; T3 `R_ff` committed
dictionaries and the certificate log); it is regenerated by `blockMesh` from
the committed `blockMeshDict` and the certificate is the log.

## 5. Gates — T4 §4's rows and bands, unchanged; the rule-5 order with the shared floors

**Graded rows** (`T4b_registered.json` `graded_rows`, the reference value
re-read from the held file at every run): **G1** `U_max/U_bulk` at r/D = 1.0,
`ij2lr-10-sw-mu.dat`, ref 1.0890, band **[1.0690, 1.1090]**; **G2** r/D = 2.0,
`ij2lr-20-sw-mu.dat`, 0.7888, **[0.7688, 0.8088]**; **G3** r/D = 3.0,
`ij2lr-30-sw-mu.dat`, 0.4632, **[0.4432, 0.4832]**. Band ±0.02 in U/U_bulk at
every station (ERCOFTAC: mean velocity within ±2 % of bulk), **identical to
T4 §4; T4's registration named no reason to move them and none is moved.**
Reference: ERCOFTAC Classic Collection case025 `ij2lr`, HELD at
`docs/campaigns/T-family/reference-data/ercoftac_case025/` (archive sha256
`6d324a86…f0d8`, T4 §2). Nu rows remain REPORT-ONLY / **BLOCKED** (T4 §2.1,
§8: no first-hand Nu uncertainty; closed primaries NOT OBTAINED) and no
eigenspace band is armed (T4 §11 stands). A PASS is a joint code-plus-closure
statement, never a code-verification claim (T4 §4).

**Rule 5, in `analyse_t4b.py:apply_gate` — the only function that writes a
verdict:** (1) any level failing C1 / C1b / C2 / C3 / C6 → `NOT A RESULT`;
(2) triple `EXACT`, `STAGNANT`, `OSCILLATORY`, `DIVERGENT` or `DEGENERATE` →
`NOT A RESULT`, value, triple and state printed, **no GCI**; (3) `CONVERGING`
→ `PASS` inside the band else `GATE FAIL`, GCI at Fs = 1.25 printed. The gate
can only turn a PASS or GATE FAIL into NOT A RESULT (structural: (1) and (2)
return before the band is read; selftest-driven).

**The observed-order floors — the SHARED names (`MESH_STANDARD.md` §10.5,
chief ruling `01967a7b`).** `analyse_t4b.py` **imports `STAGNANT_FLOOR` and
`P_MIN` from `scripts/roache_triple.py`** (blob `78e56a3b`) and defines
neither: `0 < p < STAGNANT_FLOOR = 0.5` → `STAGNANT`, `|p| < P_MIN = 0.05` →
`DEGENERATE` (e21 ≈ e32, the fitted order is rounding residual). The
registered JSON carries the same two numbers and the comparator **refuses if
import and registration disagree**; the selftest shows `classify()` names the
same state as `roache_triple.gci_equal` on eight synthetic triples. **Ground
for the stagnant floor, rung-specific as this family rules it (T11 AMENDMENT
1 at `352aef0d`, `[lab-attributed]`):** p_expected = 1.5 at r = 2 for the
bounded second-order schemes on a max-of-profile reader; 1.5/3 = 0.5; below
it adjacent-level errors differ by < 2^0.5 = 1.41×, the "levels too close to
resolve an order" state T3 measured. **Verdict-equivalent to the family's
per-comparator `P_MIN = 0.5`** (`analyse_t3_rff`, `analyse_t11`): the same
rows go to `NOT A RESULT`; only the symbol moved. The floor can only move a
row INTO `NOT A RESULT`.

## 6. Controls — every one a READER inside the frozen comparator, each with its planted control

| id | control | reader (in `analyse_t4b.py`) | fires |
|---|---|---|---|
| **C1** | plate `y+_max < 1.0` on **every** level | `yplus_read`: **`buoyantBoussinesqSimpleFoam -postProcess -func yPlus`** on a scratch copy (the working form — T4's instrument fact: generic `postProcess -func yPlus` returns 0 on every patch here) | `NOT A RESULT`, gate (1) |
| **C1b** | pipeWall `y+_max < 1.0` on every level (a gate that names one wall certifies one wall) | same reader | gate (1) |
| **C2** | nozzle-exit `U_c/U_bulk` = max |U|/U_bulk along a 200-point line across y = H (axis → pipe wall), within **±3 %** of the 1/7-power-law value **1.2245** (T4 §9's C2) | `exit_profile` / `exit_read` via OpenFOAM `sets` | gate (1) |
| **C3** | global mass conservation `|Σ_patches φ| / |φ_inlet| < 1e-3` (T4 §9's C3) | `flux_read` via `surfaceFieldValue` sums of the written `phi` over inlet / entrainment / farfield / plate / pipeWall | gate (1) |
| **C4** | planted-zero control, BOTH arms, on **every** reader on the grading path | §6.2 | **REFUSAL `exit 2`** |
| **C5** | strict completion + age guard | `mark_done_t4b.py` (§3) | `NOT DONE` → comparator refuses on the absent `DONE` |
| **C6** | iterative convergence, three parts, every level: **C6.1** every `p_rgh` initial residual (every non-orthogonal corrector) over the **last 2 000** iterations ≤ **1.0e-06**; **C6.2 not growing, directional**: mean over the last 1 000 iterations ÷ mean over the preceding 1 000 ≤ **1.05**; **C6.3** max over G1/G2/G3 of the peak `U/U_bulk` change between the last two written checkpoints ≤ **2.0e-04** (1 % of the band half-width, T4 §9.4) | `residual_history` (streamed), `residual_tests`, frozen `sample_profile`/`peak_of` | gate (1) |

**C6.2 against T4's C2 — a change, and its ground, stated for the supervisor's
check 1.** T4 tested `not (later > earlier)` on 200-sample windows; on `c`'s
19 000-iteration plateau at 6.98e-07 it fired on a 1.0001 ratio and on `f` on
noise around 9e-10 — the test measured noise, not growth. T4b keeps the
**directional** form (later window ÷ earlier window) over 1 000-iteration
windows with a **5 % tolerance**: T4's own three levels measure ratios
1.000 / 0.989 / 0.999 and pass it; a residual growing 5 % per 1 000 iterations
fails it (selftest: 6 %/1 000 → FAIL). C6.1 is **stricter** than T4's (2 000
iterations and every corrector, against 200 and the first). **Registered
risk:** T4's `c` plateau was 6.98e-07 against the 1e-06 floor — a 1.43×
margin (P4).

### 6.2 Planted-zero controls (rule 3), all on the grading path, all measured on the smoke before the freeze

| reader | plant | arms | measured on the 1-iteration smoke (§8) |
|---|---|---|---|
| G-row profile (frozen `analyse_t4.planted_zero_control`, `PLANT = 1.234e-03` m/s, aimed by cell centres at the r/D = 1 peak, descending ladder 1 … 1e-6) | 1.234e-03 m/s | positive: seen; negative: exactly 0 on identical bytes; the registered plant must sit above the demonstrated floor | recovered 6.35e-05, floor 1e-06 |
| y+ (registered solver-mode reader) | `U` × **4.0** in every cell of the scratch copy → `y+_max` must move by exactly ×2.000000000 (nut_w = 0 under `nutLowReWallFunction`), on plate AND pipeWall; **and the blind generic `postProcess -func yPlus` must return exactly 0 on every patch beside it** — the blind reader shown blind is what makes the seeing reader's number evidence | positive ×2 exact; negative identical; blind = 0 | blind 0 on every patch; registered plate max 0.2298 (a 1-iteration number, not physics); ×4 → ×2 exactly |
| exit-line (C2) | 1.234e-03 m/s subtracted from U_y in the cell nearest the line's **current maximum**, visibility judged on the whole 200-point profile in max-norm, the C2 scalar's own change reported beside it; ladder 1 … 1e-6 | positive; negative | recovered 2.35e-05 at the registered plant, floor 1e-06 |
| flux (C3) | inlet `phi` × **1.01** over every inlet face (structural locate) → the imbalance must equal the analytically predicted `|Σφ + 0.01 φ_in| / |1.01 φ_in|` to 1e-9 | positive (analytic); negative | imbalance 1.622e-05 on the smoke; ×1.01 → 0.00988492608 = predicted 0.00988492608 |

**Why the exit-line plant is aimed at the maximum, disclosed as a repair
(§7.3).** The dead lane aimed it at a fixed near-axis cell; on the smoke a
plant of 1.0 m/s there was **invisible** to a max-reader whose maximum sat
elsewhere (|U| 8.7 m/s at the aimed cell against a line maximum of 15.4 m/s)
— the exact T8-class failure T4 §9.1a describes, on a different reader. The
control now aims where the frozen G reader aims: at the reader's own peak.

## 7. Instruments — what was inherited frozen, what changed, and what this lane repaired

### 7.1 Check-1 table: every gate, band, threshold, control and reader of `analyse_t4b.py` / `mark_done_t4b.py` / `launch_t4b.sh` / `build_t4b.py` against the T4 parent

| item | T4 (frozen: `analyse_t4.py` `6f362447`, `mark_done_t4.py`, `run_one_t4.sh`, `build_t4.py` `ff032f3e`) | T4b | class of change |
|---|---|---|---|
| G1/G2/G3 reference, band ±0.02 | as §5 | **identical**; reference re-read from the held file | none |
| Roache order / GCI | `A.classify`, `A.gci` (correct Richardson sign), Fs 1.25, r 2 | **imported unchanged**; `apply_gate` re-implemented to add the floors and fold the controls into gate (1) | none on the arithmetic |
| observed-order floor | none (T4 quoted any p > 0) | `STAGNANT_FLOOR = 0.5` / `P_MIN = 0.05` **imported from `roache_triple.py`** (dead lane had a local `P_MIN = 0.5`) | **verdict-equivalent: STAGNANT below 0.5 / DEGENERATE below 0.05, same as the family's per-comparator 0.5 floor; NEW relative to T4 (T4 had no floor) — can only add NOT A RESULT rows** |
| C1 plate y+ | named in §9, **no reader** | reader inside the comparator, threshold 1.0 **unchanged** | reader added |
| C1b pipe-wall y+ | absent (registration gap) | **new** control, threshold 1.0 | control added; can only add NOT A RESULT |
| C2 nozzle-exit U_c/U_bulk ±3 % of 1.2245 | named, **no reader** | reader inside the comparator, threshold unchanged | reader added |
| C3 mass imbalance < 1e-3 | named, **no reader** | reader inside the comparator, threshold unchanged | reader added |
| C4 planted zero | G reader only (aimed, floor measured) | G reader (frozen, reused) **+** y+ (×4 → ×2, blind reader beside it) **+** exit-line (aimed at the max) **+** flux (analytic) | controls added |
| C6.1 residual floor | last 200 `p_rgh` initial residuals ≤ 1e-6 | last **2 000**, **every** non-orthogonal corrector, ≤ 1e-6 | **stricter** (same threshold) |
| C6.2 not growing | `not (later > earlier)`, 200-sample windows | later/earlier ≤ **1.05**, 1 000-iteration windows | **changed — a 5 % noise tolerance on the directional form; ground §6** |
| C6.3 field change ≤ 2e-4 | at G1 only (`GRADED[0]`) | **max over G1/G2/G3** | **stricter** (same threshold) |
| gate (1) conjuncts | C6 only | C1, C1b, C2, C3, C6 | stricter |
| completion rule | rc, End, last time, 7 fields, count, age; **`capped` absent → NOT DONE** (L-342 audit row 46, CONFLATING); absent STATUS → NOT DONE | rc, End, last time, **8 fields (+ `phi`)**, count, age; **`capped` an infrastructure field, never a conjunct**; **absent STATUS → REFUSE exit 2**; `INFRA` tuple disclosed | L-342 applied |
| launcher form | `launch_t4.sh` → `run_one_t4.sh`, caps hard-coded, `setsid nohup` outer, rc in-wrapper, `capped` witness | `launch_t4b.sh` on the `launch_k0f.sh` / `launch_t3_rff.sh` form: refuses `--ranks ≠ 1`, `--timeout ≠ registered` (read from `T4b_registered.json`), unregistered case, existing `STATUS`, `0/`, time dir, running pid, missing mesh/fields/solver, **failed `check_case_provenance.py`**; `0/T` touched last; `checkMesh` recorded; solver in the foreground under `timeout`, rc captured; `exit "$RC"` | form changed, same discipline |
| mesh | 2.25 N², first cell 2.4e-5/1.2e-5/6e-6, jet-core coarsest cell on the pipe wall | 2.625 N², first cell halved, core grading inverted (§2) | **the mandate's change** |
| `residualControl` | present in the frozen `fvSolution` writer (1e-7 on five fields) | **removed** (L-141) | registered |
| BCs, schemes, transport, `endTime`, `writeInterval` | A2.2 table | **byte-identical** (measured by `diff`) | none |

### 7.2 What the selftests measured (all before the freeze)

`analyse_t4b.py --selftest`: **20/20 under `python3` and 20/20 under
`python3 -O`**; with `--smoke <scratch T4b_IJ_c at Time = 1>`: **24/24** —
the four live reader controls of §6.2 included. Driven refusals (each a
subprocess under both interpreters, rc 2 and `REFUSE` printed): missing
`DONE`; a blind flux reader (mutant that ignores the plant); a y+ plant that
never lands. AST `ast.Assert` count **0** (the counter shown to see a planted
assert). `mark_done_t4b.py --selftest`: **9/9 under both interpreters** —
clean forged case → DONE; rc=1 → NOT DONE (CRASH label); no End; short
`ExecutionTime` count; a missing field; fields older than `0/T`; **absent
STATUS → exit 2**; **every infrastructure field absent (incl. `capped`) →
still DONE with NOT MEASURED disclosed**; AST 0. `build_t4b.py`: AST 0.
`launch_t4b.sh`: `bash -n` clean; `check_launcher_can_launch.py --worktree`
ARM 1: **0 suspect globs**; **eight refusal arms driven on a scratch copy**
(ranks 2; timeout 100; timeout 3000; unregistered case name; existing
`STATUS`; existing `0/`; existing `2000/`; a planted `compressible::` token) —
each **rc 2 before anything was written** (no `STATUS`, no `0/` afterwards).
Both comparator and marker **refuse on the live tree today** (`exit 2`).

### 7.3 Repairs this lane made to the dead lane's files (all pre-first-compute; none moves a band, threshold or cap)

1. `analyse_t4b.py`: the local `P_MIN = 0.5` replaced by the import of the
   shared names (§5) — a symbol change ordered by the supervisor's course
   correction, verdict-equivalent; selftest cases renamed and a
   verdict-equivalence check against `roache_triple.gci_equal` added.
2. `analyse_t4b.py`: the exit-line planted control re-aimed at the line's
   maximum and judged on the whole profile (§6.2) — the dead lane's fixed aim
   was shown blind on the smoke; this is a control repair, it moves no number.
3. `mark_done_t4b.py`: `--root` and a forge-based `--selftest` added (the
   dead lane's marker had none; the mandate requires every refusal driven
   under both interpreters). Clauses and classes unchanged.
4. `launch_t4b.sh`: `--timeout` must now **equal** the registered value (was
   "not exceed"; a narrower one manufactures a cap-stop); an existing
   `STATUS` is refused before anything is written; `check_case_provenance.py`
   runs before arming. All three are refusal arms, exercised in §7.2.
5. `T4b_registered.json`: `roache_floors` block added; per-level POINT /
   CEILING recomputed from T4's measured walls to two decimals (§9; the dead
   lane's 11.84 / 74.63 / 429.65 become 11.84 / 74.65 / 429.41 — rounding of
   the same arithmetic, caps unchanged); C2's description updated to the
   re-aimed control.
   Nothing else in the JSON changed; caps, timeouts, bands, thresholds and
   predictions are the dead lane's, kept because they encode the mandate.

## 8. Launch discipline — `launch_t4b.sh` (§11), the one-iteration arm, and what the queue entry carries

`launch_t4b.sh --case-dir DIR --timeout S --ranks 1 [--no-detach]`: refuses
everything in §7.1's row before writing anything; arms `0/` from `0.orig`
and touches `0/T` **last**; runs `checkMesh` (`log.checkMesh`, infrastructure)
and then `timeout $S buoyantBoussinesqSimpleFoam -case DIR` **in the
foreground** (no `setsid` between them — the measured trap in
`launch_k0f.sh`'s header), captures `RC=$?`, writes `STATUS.<case>` atomically
in the run root with `rc wall_s ranks core_min timeout_s capped checkmesh_rc
solver solver_path note started_utc ended_utc`, and `exit "$RC"`. Without
`--no-detach` it re-execs itself once under `setsid` and returns; **the queue
entries pass `--no-detach`** because the runner detaches (`QUEUE_RUNNER.md`
step 4).

**ARM 2, run before the freeze:** the real solver on a scratch copy of
`T4b_IJ_c` with `endTime 1` — **rc 0, `Time = 1`, `End`, 0.18 s wall**; the
fields fed §6.2's controls and stay outside the repository.

**The launch argv (one per level; the supervisor's fire order and the queue
entries' `launch_cmd`):**
```
/home/ubuntu/Certonomous/verification/runs/T-family/T4b_runs/launch_t4b.sh \
    --case-dir /home/ubuntu/Certonomous/verification/runs/T-family/T4b_runs/T4b_IJ_<c|m|f> \
    --timeout <1500|9000|51600> --ranks 1 --no-detach
```
`ranks = 1` on every level, the three run concurrently (T4 §6; F15's
decomposition-confound ruling: a ladder differs only in mesh).

## 9. Cost — rule 12, from T4's MEASURED per-level rates (C-119 at `93a8b7e6`)

**Rate basis.** T4's POINT was built on T1b's 209 920-cell rate and
over-predicted these 5k–83k-cell meshes 2.3–2.6× (ratio actual/POINT 0.423).
T4b therefore uses **T4's own measured wall per level** —
`STATUS.T4_IJ_{c,m,f}`: 609 / 3 839 / 22 084 s at ranks 1 on 5 184 / 20 736 /
82 944 cells × 20 000 / 30 000 / 40 000 iterations = **5.874e-06 / 6.171e-06 /
6.656e-06 core-s per cell-iteration** — scaled by the new cell counts at the
same iteration counts. CEILING = 1.5 × POINT: the halved first cell (aspect
ratio 1 627–1 645, T4's class) and a box at 12–13 of 16 cores busy can raise
the `p_rgh` GAMG iteration count. Caps ≈ 2.0 × POINT (T4 §12.1's margin
argument; a cap 2.5 % above POINT is a coin-flip, not a guard).

| level | cells | iterations | rate (core-s/cell-it) | **POINT core-min** | CEILING core-min | **cap core-min** | `timeout` s = cap × 60 / 1 | cap/POINT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `T4b_IJ_c` | 6 048 | 20 000 | 5.874e-06 | **11.84** | 17.76 | **25** | **1 500** | 2.11 |
| `T4b_IJ_m` | 24 192 | 30 000 | 6.171e-06 | **74.65** | 111.97 | **150** | **9 000** | 2.01 |
| `T4b_IJ_f` | 96 768 | 40 000 | 6.656e-06 | **429.41** | 644.12 | **860** | **51 600** | 2.00 |
| **total** | | | | **515.90** (8.60 core-h) | 773.85 (12.90 core-h) | **1 035** (17.25 core-h) | | |

Arithmetic, level `c`: 609 s / (5 184 × 20 000) = 5.874e-06; × 6 048 × 20 000
= 710.5 s = 11.84 core-min; likewise `m` 4 478.8 s, `f` 25 764.6 s.
**USD at $0.0513/core-h, derived, not measured, reported-by-owner rate
(`COMPUTE_BUDGET_CHARTER.md` §5): POINT $0.441, CEILING $0.662, cap $0.885.**
Expected wall ≈ 12 min / 75 min / 7.2 h at POINT, all three concurrent.
**Memory floor 2 GB** per entry (K0f measured 128 MB RSS at 50 176 cells on
this solver; `f` at 96 768 cells ≈ 250 MB; the floor is conservative and is
an estimate, not a measurement). An overrun stops the run (the wrapper's
`timeout` at the registered cap; `capped=yes` labels it, `NOT A RESULT`, not
re-launched). Estimate-versus-actual lands in `docs/COST_CALIBRATION.md` at
completion.

## 10. Predictions — registered as numbers before compute (`T4b_registered.json` `predictions`)

| id | quantity | point | interval / verdict predicted | ground |
|---|---|---|---|---|
| **P1** | plate `y+_max` c / m / f | 0.66 / 0.34 / 0.18 | **[0.55, 0.80] / [0.28, 0.42] / [0.14, 0.22]** | T4's u_τ,max 1.560 / 1.617 / 1.692 m/s at T4b's centres 6e-6 / 3e-6 / 1.5e-6 m (next-finer-level u_τ, +5 % for `f`) |
| **P1b** | pipeWall `y+_max` c / m / f | 0.21 / 0.11 / 0.06 | **[0.12, 0.45] / [0.06, 0.25] / [0.03, 0.14]** | T4's pipe y+ 30.09 at a 8.57e-4 m centre → u_τ,pipe 0.527 m/s; widened upward for u_τ up to 1.1 m/s |
| **P2** | `U_c/U_bulk` at the exit | 1.22 | **[1.19, 1.26]** (C2 passes) | 1/7-power law 1.2245 |
| **P3** | mass imbalance | 1e-05 | **[0, 1e-04]** (C3 passes) | steady SIMPLE at plateau |
| **P4** | `p_rgh` plateau on `c` | 7.0e-07 | **[2.0e-07, 1.0e-06]** — C6.1 margin 1.43×, disclosed | T4 `c` 6.98e-07 |
| **P5** | G1 fine value | 1.070 | **[1.055, 1.085]**, triple CONVERGING with p ∈ [0.5, 2.5] → **GATE FAIL** (0.004–0.014 below the band) | T4's (1.00290, 1.03150, 1.06287) was DIVERGENT (growing differences); a CONVERGING G1 looks like (1.030, 1.052, 1.063): p = 1.0, GCI 1.29 % |
| **P6** | G2 fine value | 0.815 | **[0.795, 0.835]** → **GATE FAIL** | T4 fine 0.8176, 0.0088 above the band |
| **P7** | G3 fine value | 0.538 | **[0.515, 0.560]** → **GATE FAIL** | T4 fine 0.5400, 0.0568 above: kOmegaSST over-predicts the decaying wall jet |
| **P8** | triples | — | **all three CONVERGING** (a gate-(2) `NOT A RESULT` is a scored miss) | T4's P4 was WRONG; registered again so the miss is scored |

A `p` below `STAGNANT_FLOOR` on any row is `NOT A RESULT` at gate (2), not a
scored P5–P7 value. **The comfortable outcome is P5–P7 wrong in the passing
direction**; it is recorded as wrong if it happens.

## 11. The freeze set — committed in the same commit as this document

Git blobs computed with `git hash-object` on the exact files committed;
sha256 first 16.

| file | git blob | sha256 | lines / note |
|---|---|---|---:|
| `verification/runs/T-family/T4b_runs/analyse_t4b.py` | **`69abe6e5`** | `06674874d025c11b` | 753; AST 0; selftest 20/20 (`python3` and `-O`), 24/24 with the smoke |
| `verification/runs/T-family/T4b_runs/mark_done_t4b.py` | **`d5411c3f`** | `2d8bdfe91e24138c` | 256; AST 0; selftest 9/9 both interpreters |
| `verification/runs/T-family/T4b_runs/build_t4b.py` | `85f6fe84` | `1728afa3f5cef1d4` | 260; AST 0 |
| `verification/runs/T-family/T4b_runs/launch_t4b.sh` | `1f12792d` | `9d77ea35b82c94f1` | 165; ARM 1 0 globs; 8 arms driven |
| `verification/runs/T-family/T4b_runs/T4b_registered.json` | `0837e95e` | `a4eb13e7eca5435f` | 277; bands, thresholds, caps, floors, predictions |
| `T4b_runs/T4b_IJ_{c,m,f}/system/{blockMeshDict,controlDict,fvSchemes,fvSolution}`, `constant/{g,transportProperties,turbulenceProperties}`, `0.orig/{T,U,alphat,k,nut,omega,p_rgh}`, `CASE.txt`, `BUILD.txt`, `log.blockMesh`, `log.checkMesh.build` | committed | | dictionaries + the birth certificates; `polyMesh` not committed (§4) |

Frozen inherited instruments, by HEAD blob, byte-identical in the worktree at
the freeze: `analyse_t4.py` `6f362447` (imported: `sample_profile`, `peak_of`,
`read_cell_centres`, `parse_internal_vectors`, `planted_zero_control`,
`classify`, `gci`, `load_ref`, `ref_peak`, `latest_time`, `two_latest_times`),
`build_t4.py` `ff032f3e`, `scripts/roache_triple.py` `78e56a3b`
(`STAGNANT_FLOOR`, `P_MIN`), `scripts/check_case_provenance.py` `dd0b8431`,
`scripts/check_launcher_can_launch.py` `0035b098`. Verify the frozen file is
the file that ran by hashing it against the committed blob.

## 12. What this rung cannot see

- **No Nu row is graded** (T4 §2.1): Baughn/Cooper primaries NOT OBTAINED; the
  Nu rows stay BLOCKED; nothing here earns a heat-transfer verdict.
- A PASS on G1–G3 is a **joint code-plus-closure** statement about kOmegaSST on
  this family; not a code-verification claim, and no eigenspace band is armed
  (T4 §11's two grounds stand).
- **A different mesh family from T4**: no cross-rung triple; T4's numbers are
  context, never a level.
- C6.2's 5 % tolerance admits a residual growing slower than 5 % per 1 000
  iterations; C6.1's absolute floor and C6.3's field change bound what that can
  hide (a level whose graded peak moves < 2e-4 between checkpoints).
- The wedge is one 2.5° sector: nothing about azimuthal structure.
- The `y+` reader is the solver's own `-postProcess`; its values are trusted
  through the ×4 → ×2 control and the blind-reader contrast, not independently.
- Nothing here authorises a launch or a send (rule 7: **SUBMISSIONS REMAIN
  PARKED**). No frozen T4 file is modified.

## 13. Status and certificate lines

**Status: PRE-REGISTERED, BUILT, NOT FIRED; queue entries prepared (validator
ACCEPTED, in the registering lane's scratchpad only), NOT dropped — enqueueing
is the supervisor's check 4.**

- `T4b_IJ_c`: built 2026-08-26T16:28:25Z, 6 048 cells, checkMesh rc 0; no `0/`,
  no time dir, no STATUS; POINT 11.84 / cap 25 core-min, timeout 1 500 s.
- `T4b_IJ_m`: built 16:28:26Z, 24 192 cells, checkMesh rc 0; POINT 74.65 / cap
  150, timeout 9 000 s.
- `T4b_IJ_f`: built 16:28:28Z, 96 768 cells, checkMesh rc 0; POINT 429.41 / cap
  860, timeout 51 600 s.
- Solver core-minutes on the rung at the freeze: **0**.

---

## AMENDMENT 1 — 2026-08-26 (PRE-FIRST-COMPUTE): the launcher's cwd-holder guard would refuse its own parent shell under the queue runner's `cd` form — the T10aR2 twin defect, repaired before any launch; guard re-frozen

**Document version 1.0 -> 1.1 (1.0 = the `91614764` freeze; this amendment declares the numbering). Lines whose number changed above this section: 0** (appended to the worktree copy after verifying it byte-identical to the HEAD blob `93df857e`). Ruled by the heat-transfer supervisor `[lab-attributed]` after crash triage on T10aR2 (check 2) and a personal read of the diff; drafted by the T5 lane. **Condition (`CLAUDE.md` rule 2), and how it was checked:** no solver has run on this rung and no launch was attempted — `T4b_IJ_c`, `T4b_IJ_m`, `T4b_IJ_f` hold only `0.orig BUILD.txt CASE.txt constant log.blockMesh log.checkMesh.build system` (`ls` at 17:40Z); no `0/`, no numeric time directory, no `STATUS.*`, no `DONE.*`; `mark_done_t4b.py` refuses `no STATUS.T4b_IJ_c`. The three queue entries were withdrawn from `verification/queue/heat-transfer/` at 17:27Z to `T4b_runs/queue_withdrawn/` before the runner reached them. **Solver core-minutes on the rung: 0.**

**Ground — measured on the sibling, not assumed.** `launch_t4b.sh` (blob `1f12792d`) lines 132–135 are line-for-line the guard of `launch_t10aR2.sh` (`dd58c649`) lines 133–135, which refused all three T10aR2 levels at zero compute under the queue runner (verbatim, `T10aR2_runs/<case>/launcher.queue.out`: `REFUSE: pid 280744 is already running in R2_c`, `REFUSE: pid 284860 is already running in R2_m`, `REFUSE: pid 286906 is already running in R2_f`; runner lines 17:24:17Z / 17:25:22Z / 17:26:27Z). The runner's fixed form `setsid nohup bash -c 'cd <cwd>; <argv> …'` (`docs/standards/QUEUE_RUNNER.md` §4; `scripts/queue_runner.py` line 26) makes the wrapper shell — the launcher's own parent — hold the case directory as cwd; the guard excluded only `$$` and so refuses its own launch by construction.

**The repair — the only change in the file.** The four-line guard is replaced by a lineage-aware one (a `ppid_of()` reader of `/proc/<pid>/stat`, the launcher's ancestor chain `LINEAGE` walked from `$PPID` to pid 1, an `own_lineage()` test that also walks a candidate's ancestors to `$$`, and the same `/proc` scan, which now `continue`s on the launcher's own lineage and still refuses, naming the pid, on any foreign process). Nothing else moves: `--timeout` must still equal the registered cap, `--ranks` 1, the `0/` / time-dir / mesh / field refusals, `check_case_provenance.py` (1b), `0/T` touched last, solver in the foreground under `timeout`, rc in-wrapper, `capped` witness, `exit "$RC"`. **Driven on a scratch copy of `T4b_IJ_c` (`endTime 1`, outside the run tree, deleted afterwards):** (a) a planted foreign `sleep` with cwd = the scratch case dir → `REFUSE: pid 292903 is already running in T4b_IJ_c`, rc 2, the planted pid named; (b) the runner's exact form `bash -c 'cd <scratch case> && launch_t4b.sh --case-dir … --timeout 1500 --ranks 1 --no-detach'` → the guard passed and the launcher stopped at the NEXT check, 1b: `REFUSE: T4b_IJ_c failed check_case_provenance.py` — because the scratch copy resolves `$SELF/../../../../scripts/check_case_provenance.py` outside the repository, not because of the case (no solver started, no STATUS written, as that refusal registers). In the run tree that path resolves; the one-iteration arming smoke of §8 already passed on the built case at the freeze.

**Freeze set, §11 row for the launcher — STRUCK, not deleted:** ~~`launch_t4b.sh` | `1f12792d` | `9d77ea35b82c94f1` | 165~~ → **`launch_t4b.sh` | `8bd93c23` | `9c035b147bd1b4ef` | 185; 0 `assert`; the two guard arms above driven.** Every other row of §11 is unchanged. No gate, band, threshold, floor, control, cap, timeout or cost moves; §9's POINT 515.90 / caps 25 / 150 / 860 stand.

**Status after this amendment: PRE-REGISTERED, BUILT, NOT FIRED; re-enqueued as `T4b_IJ_{c,m,f}_v2.json` citing this amendment's commit.**
