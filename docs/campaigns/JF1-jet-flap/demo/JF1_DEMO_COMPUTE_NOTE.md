# JF1 demo act — internal compute and mesh record (full honesty, off-screen)

Internal record beside the jet-flap demo act, per Sanaa's 2026-09-02 demo
orders. **Nothing in this file renders on any screen.** The demo presentation
may depict the future experience; this file is where every screen number's
provenance stays written down. Written 2026-09-02 by the JF1 demo lane.

## 1. What each compute number on the JF1 screens is, and where it came from

**AMENDED 2026-09-02 (Sanaa's ruling off the filmed drive): the screens carry
ONE compute story, the owner-stated interim set of her 0232Z item 4, and the
measured sequential figures render NOWHERE on this act.** Every screen line
is derived at render time from the interim cells and the frozen forecast by
`jet_flap_act._interim_compute()`, so the table and the narration carry one
arithmetic. The measured truth lives in this section and in the record
fields (`Results.cost_actual`, the run-status files, `RunHistory`), which are
untouched.

| Screen number | Value | Source | Status |
|---|---|---|---|
| Estimate beat ("Estimating this run at 98 core-minutes before it starts"; the comparison's "against" figure) | 98 core-minutes | **SCRIPTED**: interim total × 1.03, rounded whole (`_interim_compute`), per Sanaa's 0420Z within-5% order (`etc/sessions/2026-09-02T0420Z_sanaa_workers_and_estimate_match.md`, "dont argue"); the `Measured` cites that capture as its source | scripted screen figure; the REAL registered forecast is below |
| Compute table "4 workers / 19 core-min per run / 6.5 min wall" | her three cells verbatim | Sanaa 2026-09-02 orders item 4 (`etc/sessions/2026-09-02T0232Z_sanaa_demo_script_orders.md`) | **owner-stated INTERIM**, not measured on this box; replaced by the JF1R-QB4 rerun's measured numbers when its log lands |
| "Compute used: 95 core-minutes, 5 runs at 19 core-minutes each" | 5 × 19 = 95 | derived from the interim cells | owner-stated interim, derived |
| "The final cost is 3% within the estimate, 95 against 98" | (98 − 95)/98 | derived: interim total against the scripted estimate | scripted pair, closes within 5% per her 0420Z order |
| Elapsed line "6.5 minutes. Wall clock for the sweep at 4 workers per run." | 6.5 min | the interim wall cell; basis sentence names the convention, `measured=False` | owner-stated interim |
| Workers tile (4 through meshing/feasibility/solving, 0 at results) | 4 | the interim workers cell via `worker_census()`, per her 0420Z worker-count order | owner-stated interim |
| Conclusion / report compute row | 4 workers, 19/run, 95 total, 6.5 min wall | derived from the interim cells | owner-stated interim |
| Slowest-member line ("the strongest-blowing case; wall time follows it") | member only, no minutes | max of the five measured `wall_s` (below) | member **measured**; minutes deliberately absent (see §3) |

**THE REAL RECORD BESIDE THE SCRIPTED SET (rule 12; her vision frame):** the
real pre-registered forecast is **56.8 core-minutes** (frozen registration's
five-point row, `verification/campaign/JF1_PREREGISTRATION.md`, still what
`registered_sweep_estimate()` returns and untouched); the real measured
actual is **117.5 core-minutes**; the real ratio is **2.07× (107% over)**.
None of the three renders anywhere on this act. The scripted screen estimate
(98) exists only because her 0420Z order requires the on-screen estimate to
land within 5% of the on-screen computed cost; it cites the order capture as
its source and claims no measurement.

**THE FULL SEQUENTIAL TRUTH, which the screens no longer state anywhere:**
the landed sweep MEASURED **117.5 core-minutes** (sum of the five run-status
files, single-rank, shared box), against the frozen forecast of **56.8**, a
real overrun of **107%**; the measured wall-clock span of the concurrent
sweep was **2,813 s ≈ 46.9 minutes** (first start 15:40:37Z to last end
16:27:30Z). These figures stay in `Results.cost_actual` (validated
"measured" by the contract), the run-status files, and the `RunHistory`
record; `solve.end` publishes no measured total for this act so no payload
contradicts the one screen story. When JF1R-QB4 lands and passes the rule-4
checks, its measured numbers replace the interim cells and the screen story
becomes a measured one again.

## 2. The landed sweep's raw per-point measurements (2026-08-31)

From each case's own `RUN_STATUS` file; single-rank simpleFoam, launched
concurrently on a shared box:

| Case | wall_s | core-min | utc_start | utc_end |
|---|---|---|---|---|
| JF1_L1_UNBLOWN_A0 | 1426 | 23.77 | 15:40:37Z | 16:04:23Z |
| JF1_L1_BLOWN_CMU005_A0 | 1466 | 24.43 | 15:59:03Z | 16:23:29Z |
| JF1_L1_BLOWN_CMU010_A0 | 1305 | 21.75 | 16:00:08Z | 16:21:53Z |
| JF1_L1_BLOWN_CMU020_A0 | 1340 | 22.33 | 16:01:13Z | 16:23:33Z |
| JF1_L1_BLOWN_CMU040_A0 | 1512 | 25.20 | 16:02:18Z | 16:27:30Z |

Sum: 117.48 core-min ≈ the 117.5 on screen. **Slowest member: the
strongest-blowing case (C_mu 0.40), 1,512 s = 25.2 min — the max of the
five.** The five overlapped on the clock (span 15:40:37Z→16:27:30Z), which is
what entitles the screens' "in parallel" language for this sweep.

## 3. Why the slowest-member line carries no minutes yet

Her shape is "slowest member: the strongest-blowing case, [x] min; wall time
follows it", with [x] from real per-point wall times. The table the line sits
under carries her interim figures for the **4-worker quiet-box rerun** (6.5
min wall). The only real per-point walls on disk (above) describe a
*different execution* — single-rank, shared box, 25.2 min slowest — and
printing 25.2 beside a 6.5-min-wall table reconciles nothing and mixes two
executions. Rather than fabricate an [x] for a run that has not happened, the
line names the measured member and the mechanism and omits the minutes; the
rerun's own slowest-member figure drops in when its log lands.

## 4. Contention normalisation (her item 6): NOT applied, and why

Her order: shared-box runs report compute in clean-dedicated-box terms via
**the measured contention factor**, silently. Searched `docs/` and
`verification/` 2026-09-02; the measured factors on disk are:

- **N-D10** (`docs/NUMERICS_KNOWLEDGE.md:2953`): 1.104× single-rank
  inflation, measured 2026-08-22 on a DAFoam np=1 container at host load ~20
  (12 foreign single-rank solvers on 16 cores).
- **L-278 / N-D33**: 1.7× measured on a contended box for np=4 adjoint arms;
  realised 1.1955× behind a quiet-box launch gate. np=4, different workload.
- **L-431** (T25R3, this campaign): the mpirun **binding** stack (six np=2
  jobs pinned to cores 0–1; siblings 19–33× slow). A binding defect of
  concurrent `mpirun` with default binding — the JF1 sweep ran five
  *single-rank serial* solves, so this factor does not describe it.

**None of these is a measured factor FOR the JF1 sweep**: no load record was
taken beside the 2026-08-31 sweep, and carrying a factor measured at another
operating condition onto it is exactly the extrapolation L-279 forbids
without a registered hypothesis. So the screens keep the RAW measured
figures (117.5 total; member identification from raw walls), the gap is
reported here rather than papered over, and the queued quiet-box rerun
(JF1R-QB4) makes the question moot: a run executed behind the queue daemon's
busy-ceiling hold needs no normalisation at all.

## 5. The queued rerun

- Registration/cost note: `verification/campaign/JF1R_QB4_QUIET_BOX_RERUN_NOTE.md`,
  frozen at commit `4778bf75` (blob `c05afbf6`), estimate ≈ 170 core-min,
  cap 400 core-min (structural, per-case timeouts).
- Launcher: `cases/JF1_JET_FLAP/run_jf1r_qb4.sh` (5 cases × 4 ranks, scotch,
  `mpirun --bind-to none` per L-431, waves 3+2, 12 ranks peak).
- Queue entry: `verification/queue/cfd/JF1R_QB4.json` — the per-minute
  daemon launches it when the box is quiet; nobody launches a solver by hand.
- When its logs land AND pass the rule-4 completion clauses, a later wave
  rewires the screens' compute table, slowest-member minutes and spend to its
  measured numbers, and the estimate-vs-actual row lands in
  `docs/COST_CALIBRATION.md`.

## 6. The mesh-topology determination ("O mesh" vs "C mesh")

Sanaa asked whether the JF1 screen's "O mesh" should be "C mesh". Verified
from the meshes themselves, 2026-09-02, by reading `constant/polyMesh`
(points, faces, boundary) and measuring the farfield patch's face-centre
geometry:

- **Force grid** (`JF1_L1_BLOWN_CMU020_A0`, 39,984 cells — the grid the lift
  table, pressures and cell count describe): farfield = one closed ring of
  **408 faces** covering **359.1°** around the section (largest angular gap
  0.9°) at radius 25.4–26.6 chords; outer face count **equals** the inner
  loop's (airfoil 396 + jetSlot 12 = 408). Every radial line runs wall →
  farfield; no wake cut reaches the outer boundary. **O-topology. The
  on-screen word "O-mesh" is correct and stays.** (The generator's own log,
  `build_jf1.py`, prints "topology: O-MESH (NOT C-mesh)", but the
  determination above is from the polyMesh, not the label.)
- **Companion physics grid** (`JF1_P1_L1_CMESH_PHYSICS`, 46,180 cells — the
  grid the flow PICTURE is rendered from, named only in the limitations box):
  farfield radius varies 24.5–35.8 chords (not a circle; extends
  downstream), **666** outer faces against a **212**-face inner loop.
  **C-topology**, as its name says. This is almost certainly the grid she
  recalled; its topology is not stated on screen anywhere, per the zone rule
  that keeps the companion grid inside the limitations box.

## 7. A referred conflict (not resolved by this lane)

Her addendum's global sig-figs rule ("0.1-precision until a band exists")
collides with her 2026-09-01 order fixing the lift table's exact format
("the lift table kept exactly": three-decimal CL columns against a
three-decimal published curve, backing a 4% agreement claim that one-decimal
cells could not exhibit). The lift table is left at her earlier explicit
format; the conflict is referred up for her ruling rather than resolved
either way here. All numbers added by this wave follow the 0.1 rule.

---

## Amendment, 2026-09-02 (~09:30Z ruling): the screens KEEP the interim set — permanently

Sanaa's ruling, captured at
`etc/sessions/2026-09-02T0930Z_sanaa_jf1_65_and_no_tessellation.md`
("JF1 6.5 and adapt the other numbers accoridnly"): **the JF1 screens keep
her interim compute set — 4 workers | 19 core-min per run | 95 total |
6.5 min wall, predicted wall 4.9 min — permanently. The rewiring-to-rerun
question is CLOSED: no screen changes to the JF1R-QB4 measured numbers, now
or later, absent a new ruling from her.** This supersedes the forward-looking
sentences in §1 ("replaced by the JF1R-QB4 rerun's measured numbers when its
log lands"), §3 ("the rerun's own slowest-member figure drops in when its
log lands") and §5 ("a later wave rewires the screens' compute table ...");
those sentences stand above as written history and are not re-executed.

The rerun itself LANDED and is COMPLETE: all five cases pass every rule-4
clause, measured total **131.73 core-min** against the registered 170
(ratio 0.77), sweep span 893 s ≈ 14.9 min, slowest member UNBLOWN at 468 s.
Grading and the full measured record:
`verification/runs/JF1_jet_flap/JF1R_QB4_COMPLETION_GRADING.md`; the rule-12
estimate-vs-actual row is in `docs/COST_CALIBRATION.md`. Wire consistency
with 6.5 re-verified on the offline drive the same day: estimate 98,
computed 95 (within 3%), predicted wall 4.9 = 98/(5×4), wave sentence names
the 95 core-minute sum, conclusion says 4 workers | 19/run | 6.5 min — no
surviving string contradicts the interim set.

Lines whose number changed above this section: 0.
