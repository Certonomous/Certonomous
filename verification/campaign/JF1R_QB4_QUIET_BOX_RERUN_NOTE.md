# JF1R-QB4 — quiet-box 4-rank parallel rerun of the frozen JF1 L1 sweep

**Label: FEASIBILITY / TIMING RERUN. NO GATE, NO THRESHOLD, NO VERDICT of the
fixed vocabulary (PASS / GATE REACHED / GATE FAIL / NOT A RESULT / BLOCKED /
PENDING) attaches to any run this note registers.** It scores nothing and
counts toward no result column. Sanaa's SANAA-DIRECT of 2026-08-31 (commit
927924f1): feasibility/physics rungs need no freeze. This note is nonetheless
committed BEFORE the entry is enqueued, so the entry can pin it by sha and the
cost is registered before compute (CLAUDE.md rule 12).

## 1. What this run is, and on whose order

Sanaa, 2026-09-02 ~02:32Z demo orders, verbatim (captured at
`etc/sessions/2026-09-02T0232Z_sanaa_demo_script_orders.md`):

> The quiet-box parallel rerun proceeds in the background; when its log
> lands, screens silently update to its numbers.

and item 4 fixes the interim screen figures it will replace:
"JF1 until the rerun log lands: 4 workers | 19 core-min per run | 6.5 min
wall."

So: **re-solve the frozen JF1 L1 five-point sweep — unblown reference plus
C_mu_jet in {0.05, 0.1, 0.2, 0.4} — with 4 MPI ranks per case ("4 workers"
per run), on a quiet box, and measure per-case wall time, per-case
core-minutes, and the sweep's wall-clock span.** The demo screens' compute
table and slowest-member line take the measured numbers from this run's logs
when they land; until then they carry her interim figures, recorded as
owner-stated interim in
`docs/campaigns/JF1-jet-flap/demo/JF1_DEMO_COMPUTE_NOTE.md`.

The physics is IDENTICAL to the landed sweep: same frozen section 5.2 jet
constants (reproduced from the registered formulae inside the launcher, as
`run_jf1_blown.sh` does), same mesh generator and level
(`cases/JF1_JET_FLAP/build_jf1.py --level L1`), same schemes, same
`endTime 8000`. Only the decomposition (scotch, 4 subdomains per case) and
the concurrency (waves of at most 3 concurrent cases, 12 ranks peak, `mpirun
--bind-to none` per L-431) differ, and both exist to measure time, not
physics.

## 2. What is measured, and the one physics cross-check

Registered quantities (all read from the runs' own artifacts, never typed):

- per-case `wall_s`, `ranks` (= 4) and `core_min_MEASURED` in each case's
  `RUN_STATUS.<case>.txt`;
- the sweep's wall-clock span, first start to last end, in
  `RUN_STATUS.JF1R_QB4_SWEEP.txt`;
- the slowest member by measured `wall_s` (the landed sweep's slowest was the
  strongest-blowing case, 1,512 s; this run measures its own).

**Physics cross-check (a consistency check, not a gate):** each blown case's
settled `CL_total` (surface + jet reaction, from the tail of its own
`coefficient.dat`) is compared against the landed serial sweep's value for
the same `C_mu_jet`. Expected agreement: within 1% (decomposition changes
the iteration path, not the settled answer). A larger gap is REPORTED as a
finding beside the timing numbers; it does not grade anything, and under no
reading do this run's numbers replace the landed sweep's lift table on
screen — only the compute numbers are taken.

Completion per CLAUDE.md rule 4 applies per case: solver rc 0, an `End`
line, last `Time = 8000`, fields present at 8000, every 8000-field newer
than the case's own `0/` (0 is touched last before launch). A case failing
any clause is reported as incomplete and its timing numbers are not used.

## 3. Cost (registered BEFORE compute, rule 12)

- **Basis (derived, not measured):** the landed serial sweep measured
  1,305–1,512 wall s per case at 1 rank on a shared box
  (`verification/runs/JF1_jet_flap/JF1_L1_*/RUN_STATUS.*.txt`, 2026-08-31;
  sum 117.5 core-min). Assuming 4-rank parallel efficiency 0.55–0.85 on this
  39,984-cell 2-D case, per-case wall ≈ 410–650 s, per-case core-min ≈
  27–43, sweep total ≈ **135–215 core-min**, point estimate **≈ 170
  core-min** including meshing/decomposition overhead. Waves of 3 + 2 cases
  give a projected wall span of ≈ 15–25 min.
- **CAP: 400 core-min total, enforced structurally**: each case runs under
  `timeout 1200 s`; 5 cases × 4 ranks × 1,200 s / 60 = 400 core-min is the
  worst the launcher can spend. The cap is never raised; a timeout stops the
  case (rule 12).
- Dollars, derived at the owner-stated $0.0513/core-h (reported-by-owner;
  the box cannot read its own billing, COMPUTE_BUDGET_CHARTER §5): estimate
  ≈ $0.15, ≈ $0.34 at cap. Under the pre-authorised $25 blanket.
- Estimate-versus-actual comparison lands in `docs/COST_CALIBRATION.md` at
  completion, per rule 12.

## 4. Where things land

- Run roots: `verification/runs/JF1_jet_flap/JF1R_QB4_<TAG>/` — the launcher
  REFUSES any pre-existing run root (age guard).
- Launcher: `cases/JF1_JET_FLAP/run_jf1r_qb4.sh` (queue-daemon launched;
  never run by hand while the daemon is live).
- Queue entry: `verification/queue/cfd/JF1R_QB4.json`, launched by
  `scripts/queue_runner.py --daemon`, which holds it until the box is quiet
  (busy ceiling + core-fraction holds) — that hold IS the "quiet-box"
  mechanism.
- The demo screens' rewiring to this run's numbers is a LATER wave's item,
  taken only after the logs land and complete.
