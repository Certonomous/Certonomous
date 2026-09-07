# K2b-U3-R3 — recalibrated successor to the build-infeasible K2bU3R2: the un-confounded Test D at the NEAREST builder-feasible uniform mesh. Pre-registration

Predecessor: **K2b**

*(The line-leading edge above is the machine-recognised §2ay lineage field
[`scripts/check_completion_enforcement.py:_find_lineage_successor`, keyed on the
line-leading `Predecessor:` naming the superseded case]; `CASE_ID_RE.search`
returns `K2b`, discharging the same K2b flag `[NOT A RESULT] K2b`
("UNDECIDABLE AT THIS PRICE, Test D never run") that the now build-infeasible
K2bU3R2 targeted and could not reach. **Human-readable chain:** K2bU3R3 ←
K2bU3R2 (frozen `0cc9dc89`, build-infeasible pre-compute, no answer) ← K2b-U3
(graded RECORD, outcome P3, `K2bU3_RESULTS.md`) ← K2b. See §7 for an open
question on whether the supervisor wants an explicit `K2bU3R2` supersession
edge in addition.)*

**STATUS: DRAFT — NOT FROZEN, NOT COMMITTED, NO COMPUTE RUN.** This file is a
lane draft awaiting the heat-transfer-supervisor's §3 checks and freeze. It
alters NO gate, threshold, band, label or outcome-meaning — only the mesh
resolution (the infeasible 60 mm → the nearest builder-feasible uniform size)
and the recalibrated cost/cap that resolution implies. Nothing here has been
sent, filed, submitted, uploaded, registered or posted outside this box
(`CLAUDE.md` rule 7). The comparator `analyse_k2bU3R3.py` and the thin build
wrapper are **TO BE WRITTEN before freeze** (§5.3, §2.4) — this draft writes
neither.

---

## 0. What this document is, and what it is NOT

**IS.** A recalibrated re-registration of the exact experiment K2bU3R2 froze —
the un-confounded Test D (3D transient, N = 4 racks, open row ends, 70 %
provisioning, 80 s) that the frozen `K2b_3D_UNSTEADINESS_PREREGISTRATION.md`
§4/§5 named — moved off the mesh size that the frozen builder's own
even-division guard rejects (60 mm) and onto the **nearest uniform size the
same guard accepts (59 mm)**, with the cost and cap re-derived for that size.

**IS NOT.** A new gate, threshold, aliasing/stationarity criterion, band or
outcome-to-meaning. Every one of those is re-used unchanged and cited from the
frozen predecessor comparator `analyse_k2bU3.py` (blob
`d1500a5f113c10c8547b47906474f318fbc93319`) exactly as K2bU3R2 reused them. It
does not move, widen or retract any K2b-U3 verdict (P3 stands, Control M
`DAMPS` stands, O1 stands). It creates ONE new gate — the 59 mm Test D,
currently **PENDING** — and nothing more.

---

## 1. The blocker this fixes, and why the fix is a resolution change and nothing else

K2bU3R2 (frozen `0cc9dc89`) registered a **60 mm uniform** mesh for Test D. The
run reuses the frozen builder `build_k2bU3.py`, whose `mesh3d(h)` calls
`divs(edges, h)` (`build_k2bU3.py:77-83`) — a guard that, for every geometry
interval, rounds `L/h` to an integer cell count `n` and **asserts**
`|L/n − h| < 0.02·h`. At `h = 0.060` the guard **fails on the 2.00→2.70 m
edge** (the 0.70 m rack-top→ceiling gap): `0.70/0.060 = 11.67 → 12` cells →
0.058333 m, deviation 0.001667 m > tolerance 0.001200 m. Confirmed live:
`U.mesh3d(0.06)` raises `AssertionError: cell size 0.06 does not divide interval
2.0-2.7 evenly`. This is a **CONFIG/BUILD infeasibility, triaged pre-compute —
no solver ran, there is no answer to void** (`bookkeeping-never-voids-physics`
does not apply; nothing was measured).

The fix does not loosen the guard and does not edit the frozen builder (both
forbidden). It moves the mesh to the **nearest uniform cell size the frozen
guard accepts on every interval**, proven in §2. That is a change to the mesh
resolution only; §3/§4 re-use every graded quantity, gate and threshold
unchanged.

---

## 2. MESH FEASIBILITY PROOF (the crux)

### 2.1 Every interval the frozen builder divides

`build_3d()` → `mesh3d(h)` (`build_k2bU3.py:86-129`) divides three edge arrays
(`build_k2bU3.py:45-47`, geometry constants from `build_k2b.py:127-132`:
`D_R=1.10, H_R=2.00, W_CA=1.20, W_HA=1.20, H_ROOM=2.70`):

| axis | edges (m) | interval lengths divided (m) |
|---|---|---|
| XS | 0.0 0.6 1.2 1.8 2.4 3.0 3.6 | 0.60 ×6 |
| YS | 0.0 0.6 1.20 2.30 2.60 3.20 3.50 | 0.60, 0.60, 1.10, 0.30, 0.60, 0.30 |
| ZS | 0.0 2.00 2.70 | 2.00, 0.70 |

**Distinct interval set the guard must pass on: {0.30, 0.60, 0.70, 1.10, 2.00} m.**

### 2.2 The nearest-to-60 mm uniform size that passes ALL intervals: **59 mm (0.059 m)**

A scan of every uniform size in [0.030, 0.100] m against the FROZEN `divs()`
guard (imported unedited from `build_k2bU3.py`; guard exercised, not
re-implemented) finds the feasible set
{0.030, 0.033, 0.034, 0.037, 0.043, 0.050, 0.051, **0.059**, 0.099, 0.100} m.
The member nearest 0.060 is **0.059 m** (1 mm finer than the registered target;
sub-mm spot checks confirm the open interval (0.059, 0.060) fails — e.g. 0.0595
fails the 1.10 m edge, dev 0.00161 > tol 0.00119). **The supervisor's suggested
50 mm is feasible but NOT nearest — it is 10 mm from target and costs ≈2× (§6).**

**Per-interval proof at h = 0.059 m** (tolerance 0.02·h = 0.001180 m):

| interval L (m) | cells n | realized L/n (m) | deviation (m) | verdict |
|---|---|---|---|---|
| 0.30 | 5 | 0.060000 | 1.000e-03 | PASS |
| 0.60 | 10 | 0.060000 | 1.000e-03 | PASS |
| 0.70 | 12 | 0.058333 | 6.667e-04 | PASS |
| 1.10 | 19 | 0.057895 | 1.105e-03 | PASS |
| 2.00 | 34 | 0.058824 | 1.765e-04 | PASS |

All five pass. The two tightest (0.30 at 85 % of tolerance, 1.10 at 94 %) still
pass; the guard is deterministic, so a computed pass is a definite pass, not a
probabilistic one. See §7 for the open question on accepting a tight margin.

**Contrast at h = 0.060 m** (the infeasible registered size): 0.30/0.60/1.10/2.00
all PASS, only the 0.70 m gap FAILS (dev 0.001667 > tol 0.001200). So 59 mm
succeeds precisely because it redistributes the rounding error off the 0.70 m
edge; it is the same nominally-uniform ~60 mm mesh with per-block sizes
0.0579–0.0600 m (vs 60 mm's would-be 0.0583–0.0611 m) — within the guard's own
2 % of the registered resolution.

### 2.3 Proof the builder actually builds it

Running the FROZEN mesh generator directly (no files written — `mesh3d` returns
the blockMeshDict text and the cell count, it does not touch a case dir):

- `U.mesh3d(0.10)` → **28 740 cells** (matches the recorded `K2bU3_D` 100 mm
  cell count, `K2bU3_D/CASE.txt`: `cells 28740`) — confirms the import path is
  the real builder.
- `U.mesh3d(0.059)` → **137 000 cells**, blockMeshDict emitted OK, `divs()`
  raised no assertion on any interval.
- `U.mesh3d(0.06)` → `AssertionError` on the 2.0–2.7 interval (confirms 60 mm
  infeasible).

**Age guard (rule 4):** `mesh3d()` writes nothing. The full build (the thin
wrapper of §2.4) must run into a NEW, empty case root with no `0/` and no time
dir present, so the age guard is satisfiable — identical to K2bU3R2 §5.3 item 2.

### 2.4 The build path — a thin wrapper, TO BE WRITTEN before freeze (no frozen file edited)

`build_3d()` hard-codes `mesh3d(H_CELL)` with `H_CELL = 0.1`, and K2bU3R2 built
60 mm by calling the parameterised `mesh3d(h)` from a thin successor wrapper
(the same reason `U.mesh3d(0.06)` was reachable to assert). K2bU3R3's build
wrapper does the same at `h = 0.059`: it **imports** `build_k2bU3` and calls the
frozen `mesh3d(0.059)` plus the frozen field/BC/controlDict/provisioning steps
of `build_3d()` (70 % tile provisioning, tile-turbulence follow, PIMPLE 2/2,
Euler, endTime 80 s, maxCo 2.0, monitor 0.2 s) UNCHANGED. **No frozen file is
edited** (rule 6); the wrapper is a new script under the K2b_runs tree, its
sha256 pinned at freeze alongside the case dir. This draft does NOT write it.

---

## 3. The run, and the numbers fixed before it starts

One case only: the un-confounded Test D at **59 mm**. No new Control M is run
(K2bU3R2 §1: at the spec's own coarse resolution the answer is a statement about
the spec's 3D module, not "about nothing", so the 100 mm confound does not
arise; 59 mm is within 1.7 % of that spec resolution). The 100 mm `K2bU3_D`
tree is not touched. A NEW case dir is built fresh, age guard satisfied.

| | Test D at 59 mm (this run) | source (unchanged) |
|---|---|---|
| solver | `buoyantBoussinesqPimpleFoam`, Euler ddt, PIMPLE 2 outer / 2 inner | predecessor §3 |
| provisioning | 70 % tile provisioning, BCs of `K2bP_under`, uniform start at T_sup | predecessor §3 |
| geometry | full module, N = 4 racks, open row ends | predecessor §3 |
| **mesh** | full module, **h = 0.059 m — 137 000 cells** (nearest builder-feasible to the registered 60 mm; §2) | **RECALIBRATED (only change)** |
| endTime | 80 s | predecessor §3/§4 |
| maxCo | 2.0 | predecessor §3 |
| monitor interval | 0.2 s, `weightedAverage(rack{0..3}_in) of T`, mass-flow-weighted, per-rack alongside | predecessor §3/§3.3 |

Graded quantity unchanged: the mass-flow-weighted mean of T_in over all four
rack front faces, per-rack values reported alongside.

---

## 4. Gates, thresholds and outcome-meaning — REUSED UNCHANGED, CITED, NOT RE-AUTHORED

**No gate, threshold, band, aliasing/stationarity criterion or outcome-to-meaning
changes.** All are imported from the frozen comparator `analyse_k2bU3.py` (blob
`d1500a5f113c10c8547b47906474f318fbc93319`) exactly as K2bU3R2 imported them:

- **Aliasing guard (predecessor §3.1):** ≥ 20 time steps AND ≥ 10 monitor samples
  per 6.000 s period, measured whatever happens; fewer than the floor → REFUSED →
  P3. At 59 mm, maxCo 2.0 gives dt ≈ 0.098 s → ≈ 61 steps and 30 samples per
  period (floors 20 and 10) — expected to pass with margin, figures reported as
  measured regardless.
- **Windows / stationarity (predecessor §3.2):** discard first 40 s; grade final
  20 s (60–80 s) against preceding 20 s (40–60 s).
- **Thresholds (predecessor §3.3; `analyse_k2bU3.py:15-16`):**
  `P_SURV, P_DAMP, R_SURV, R_DAMP = 0.30, 0.10, 0.8, 0.5`; floors 20/10. Final-window
  p2p ≥ 0.30 K AND ratio ≥ 0.8 → **SURVIVES**; p2p ≤ 0.10 K OR ratio ≤ 0.5 →
  **DAMPS**; else **UNDECIDABLE**.
- **Outcome-meaning (predecessor §4):** SURVIVES → P1; DAMPS → P2;
  (REFUSED | UNDECIDABLE) → P3. Consequences verbatim as K2bU3R2 §3 (P1: the
  cycle is not a 2D artefact, transient formulation carries to the 3D module,
  §9 steady estimate stays void; P2: three-dimensionality damps it, the 2D
  finding stands as true of the 2D slice, §9 estimate becomes revivable-but-
  not-revived; P3: stated as the answer, module held, §9 estimate void). The
  gate can only turn a SURVIVES or DAMPS **into** P3 (via a guard failure), never
  the reverse (`CLAUDE.md` rule 5 order).

**The comparator for this run** would be `analyse_k2bU3R3.py`, imported —
NOT re-implemented — from the frozen `analyse_k2bU3.py` (reader `series()`,
grader `grade()`, all constants), adding ONLY the §5.1 planted-zero control,
exactly as `analyse_k2bU3R2.py` (blob `120464450cecf8ed13816df5c9a3d640ab4b38d9`)
did, re-pointed to the 59 mm case dir. **TO BE WRITTEN before freeze — this
draft does NOT write it.**

---

## 5. Controls this run MUST carry (standing rules, not optional)

### 5.1 Planted-zero control — REQUIRED (rule 3)

A `DAMPS` verdict is a near-zero p2p; a zero from a reader not shown able to see
a non-zero is not evidence (`CLAUDE.md` rule 3;
`a-zero-needs-a-live-planted-control`). The frozen predecessor `analyse_k2bU3.py`
carries no such control; the successor comparator MUST, before grading the true
series: (1) plant a known non-zero p2p `PLANT` into a COPY of the on-disk monitor
log AFTER reading it, re-read it back THROUGH the imported `series()` reader, and
**refuse (exit 2)** if the reader cannot recover `PLANT`; (2) only then grade the
true series. Identical in mechanism to `analyse_k2bU3R2.py` §5.1.

### 5.2 Strict completion rule — REQUIRED (rule 4)

The run is `done` only if ALL hold: `rc = 0`; an `End` line; **last time ==
endTime (80.0)**; fields present (`T U p_rgh alphat nut k omega phi` — thermal
family); `ExecutionTime` count == endTime; and **every field at endTime NEWER
than the case's own `0/T`** (the age guard). The guard **refuses** a case where
`0` or a time dir already exists. Any failing clause → `NOT A RESULT`, never
"roughly done". Completion-guard instrument (`mark_done_t3.py` reused, or an F14
equivalent enforcing the identical clause set) is a freeze-time pin (§5.3).

### 5.3 Grading-path freeze plan — pins to be cut AT freeze by the supervisor (rules 2, 6)

At freeze the supervisor cuts and records, hashing each frozen file against its
committed blob (rule 2):
1. **This pre-registration** — frozen by sha at commit; grading path fixed there;
   post-compute changes land only as struck/dated addenda that cannot alter a
   gate, threshold, cap or label.
2. **The 59 mm case directory** — a NEW tree, e.g.
   `verification/runs/F14-cooling-ladder/K2b_runs/K2bU3R3_D59/`; pin sha256 of
   `system/`, `constant/`, `0.orig/` of the case built with `0`/time dirs absent
   so the age guard is satisfiable.
3. **The build wrapper** (§2.4) and **the comparator `analyse_k2bU3R3.py`** (§4) —
   both TO BE WRITTEN before freeze; pin each sha256 at freeze. Comparator reuses
   the §4 constants unchanged and carries the §5.1 plant.

No comparator, wrapper or case has been written or modified by this draft.

---

## 6. Cost — recalibrated, costed before the run (rule 12)

**Measured basis:** the rung's measured 3D transient rate **4.26e4 cell·steps/(core·s)**
(`K2b_3D_UNSTEADINESS_PREREGISTRATION.md` §4; the same rate the frozen builder
uses, `build_k2bU3.py:330` = 46400·1978/1780/1.21 = 42 613 cell·steps/core·s),
multiplied by the **builder-measured** 59 mm cell count and the maxCo-2.0 step
count. Cell count 137 000 is read from the FROZEN `mesh3d(0.059)` (§2.3), not
scaled. dt = 2·0.059/1.2 = 0.0983 s (< maxDeltaT 0.25) → 80/0.0983 ≈ 814 steps.

**POINT = 43.6 core-min** = 814 steps × 137 000 cells / 42 613 / 60. This is
**1.04× the frozen 60 mm estimate of 42 core-min** — the 59 mm mesh is only
1.7 % finer, so the cost barely moves.

**CAP = 66 core-min (1.5× the point, rounded up).** An overrun **stops the run**
(rule 12); it does not get a new budget. Reaching the cap without satisfying §5.2
→ `BLOCKED` (over-cap), not a graded outcome.

*Note:* this cap (66) exceeds K2bU3R2's cap (63) by 3 core-min, solely because
59 mm is 1.7 % finer than the infeasible 60 mm. It is R3's OWN pre-registered
cap, set before compute; it is not bound to R2's (R2 is a distinct, infeasible
registration). Setting it is a costing act (rule 12), not a gate/threshold change.

**Ranks = 1 (serial).** Confirmed from the predecessor: `run_k2b.sh` runs
"single core", and `K2bU3_D/system/` carries no `decomposeParDict`. So
core-min = wall-min; POINT ≈ 44 wall-min serial.

**cost_basis:** REPORTED-BY-OWNER at **$0.0513/core-h** (owner-stated 2026-08-21/22;
the box cannot read its own billing, `COMPUTE_BUDGET_CHARTER.md` §5;
`run_k2b.sh` itself notes "no verified currency rate for this machine"). DERIVED
dollars (NOT measured): POINT 43.6 core-min = 0.727 core-h → **$0.0373**; CAP 66
core-min = 1.100 core-h → **$0.0564**. Both far under the $25/run
pre-authorisation (a blanket is not a per-item read, rule 9). A
`docs/COST_CALIBRATION.md` row is owed at completion (estimate 43.6 core-min vs
actual from the log) and is the supervisor's to land.

**Rejected alternative — 50 mm:** feasible (all intervals pass), but 10 mm from
target and **POINT = 86.3 core-min** (229 920 cells × 960 steps / rate / 60) =
**2.06× the 42 registered — it BREACHES K2bU3R2's 63 cap** (the supervisor's
1.73× was cell-count-only; including the dt reduction the true factor is ≈2.06).
51 mm is similar (83.2 core-min). 59 mm is both nearer to the registered
resolution AND far cheaper.

---

## 7. Lineage, scope, and OPEN QUESTIONS for the supervisor to settle before freeze

**Discharges** the K2b §2ay flag `NOT A RESULT` via the line-leading
`Predecessor: **K2b**` edge (recognised by `_find_lineage_successor`), now that
K2bU3R2 could not reach it. **Does not** alter the K2b-U3 P3 verdict, the
Control M `DAMPS` reading, or O1. **Creates** one new gate (the 59 mm Test D),
currently **PENDING** — it grades only after the run satisfies §5.2 and the
frozen comparator (with the §5.1 plant) returns rc 0.

**Open questions the supervisor must settle (I am not entitled to decide these):**

1. **Resolution vs the frozen "60 mm" wording.** The frozen K2b registration
   names "60 mm" verbatim; 60 mm is infeasible under the frozen builder's own
   guard. I chose 59 mm as the nearest feasible realization (within the guard's
   own 2 % of 60 mm). Is a 1.7 %-finer nominal mesh a supervisor-freezable
   resolution recalibration, or does the departure from the literal registered
   size need Sanaa? My reading: it is a resolution recalibration (rule 2 permits
   the successor to set mesh + cost), but the call is the supervisor's.
2. **Tight-but-passing margin at 59 mm.** Two intervals pass at 85 % (0.30 m) and
   94 % (1.10 m) of the 2 % tolerance. The guard is deterministic so this is a
   definite pass, but if the supervisor prefers more headroom the only feasible
   alternatives are 51 mm/50 mm (roomier, but ≈2× cost and breaching R2's cap) or
   a graded ceiling-gap mesh (a larger departure from the frozen uniform-mesh
   builder — not needed here since 59 mm passes, and offered only if margin is
   judged insufficient).
3. **Lineage edge.** I kept `Predecessor: **K2b**` (R2's proven-working pattern,
   discharging the same K2b flag). If the supervisor wants R3 also recorded as
   explicitly superseding K2bU3R2, that is a second line-leading edge to add at
   freeze; R2 carries no NOT-A-RESULT run row (it never ran), so no separate flag
   currently needs discharging on R2's account.
4. **Cap 66 vs 63.** R3's own cap is 66 core-min (1.5× point). Confirm the
   supervisor is content that R3 registers a cap 3 core-min above R2's, given the
   1.7 %-finer mesh (§6).

**STATUS: DRAFT — awaiting the supervisor's §3 checks and freeze. NOT FROZEN,
NOT COMMITTED, NO COMPUTE RUN.**
