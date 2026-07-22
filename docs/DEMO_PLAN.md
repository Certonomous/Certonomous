# Certonomous demo plan

Working document — Sanaa's demo vision, organized. Edit freely; this is the
contract for what the demo must show.

## The organization (who exists)

| Role | Mandate | Status |
|---|---|---|
| **Head Engineer** (Chief Engineer) | Executes end-to-end: geometry intake → clean → mesh → solve → postprocess → report. Owns the worker fleet and the mission loop. | Kernel exists (`chief_engineer/`); STL pipeline in `head_engineer.py` (phase 1) |
| **Monitoring sub-agent** | Watches solver logs live: NaNs, suspicious residual growth, bounds violations — and, on never-before-seen cases, flags *novel* behaviors as candidate knowledge for the lessons file. | Phase 1 in `head_engineer.py` (`LogMonitor`) |
| **Chief Researcher** | Governs approximations: approves/rejects closure-model use, selects the most informative runs when compute is scarce, decides interpolation strategy for unseen geometry. | To build — role + approval protocol |
| **Numericist** | PhD-in-numerics agent: innovates on discretizations/solvers/speed, absorbs the repo's numerics knowledge + foundational papers Sanaa provides, proposes faster/more accurate ways. | Scaffolded (`introspection/recipe/agents/numericist.yaml`); awaiting papers |

Shared doctrine (must be *visible* in every demo): the chiefs continuously
economize compute, maximize accuracy and reliability, and treat uncertainty as
work-to-be-done — see LESSONS L-001: high uncertainty → spend samples until
only irreducible uncertainty remains.

## Demo Part 1 — Shape optimization under abundance

Aircraft case (OpenVSP adapter), starting geometry given, objective: minimize
drag in a multi-constraint space.

Script beats:
1. Chief Engineer receives the task and **audits compute first**: other jobs
   running? how many workers fit? Can the whole sweep run in one go?
2. **If capacity is sufficient** → launch the parallel sweep, find the optimal
   design.
3. **If not** → Chief Researcher joins, selects the most informative subset of
   runs (active-learning style), then Chief Engineer runs a reduced-order
   model ensemble over the rest.
4. The sweep doubles as the sample pool for **Monte-Carlo/GP uncertainty**:
   final geometry appears **with uncertainty estimates**.
5. Close with a bullet-point next-steps report to the user.

Needs built: compute-audit step (worker/job census before planning), Chief
Researcher run-selection, ROM ensemble fallback, final report generator.

## Demo Part 2 — Simulation under time constraints

Deadline forces a coarser-than-ideal mesh.

Script beats:
1. Chief Researcher is asked to **approve using an existing closure model**
   for the case.
2. Approved → Chief Engineer runs with the closure.
3. Rejected → Chief Engineer runs the coarse simulation and **emphasizes the
   uncertainty**, then runs the appropriate diagnostics (grid-sensitivity
   probe, residual/oscillation analysis) to alleviate it for the user.

Needs built: closure-model registry + approval protocol, coarse-run
uncertainty inflation (mesh term), diagnostics battery.

## Demo Part 3 — Unseen/complicated geometry

Chief Researcher and Chief Engineer **discuss** and interpolate from
experience: nearest seen geometries, what transfers, what doesn't, explicit
confidence discount for extrapolation.

Needs built: case-memory (what have we run before, with outcomes), similarity
reasoning, dialogue surface in the control room.

## Capability checklist the demo must prove

1. Full orchestration end to end (goal → fleet → decision)
2. Full diagnostics and reports end to end
3. Uncertainty quantification — **every result carries its confidence
   envelope, on the plot itself, not just the number**
4. Learning/self-learning + research initiative — lessons applied and written,
   compute economized visibly, chiefs proposing improvements unprompted

## Standing decisions

- Platform name: **Certonomous** (renamed from Jango, 2026-07-20).
- Results presentation: curve + shaded confidence envelope, always.
- Uncertainty doctrine: reduce with samples until irreducible (L-001);
  targeted reduction methods (fidelity, mesh, model) to be added.

## Build status (2026-07-20)

| Piece | State | Evidence |
|---|---|---|
| Head Engineer STL pipeline | **done** | motorBike: 353,578 cells, Cd 0.4167 ± 0.0013 |
| Monitoring sub-agent | **done** | NaN/FPE, residual-spike, bounding, novel capture |
| Compute audit + `make_busy.sh` | **done** | idle → YES (11 free); busy → NO (0 free, 12 jobs) |
| Chief Researcher (both decisions) | **done** | run selection + closure approval, cited |
| Learning beat (L-001, two live runs) | **done** | 3.3% → 0.8%, 45 real solves, 70 s |
| Part 1 both branches | **done** | parallel wave, and ROM branch (0.3% surrogate error) |
| Part 2 both paths | **done** | closure recovers the fine-mesh answer from a coarse run |
| Part 3 chiefs' dialogue | **done** | real retrieval over case memory, no invented numbers |
| Email closing beat | **wired** | needs Sanaa's `CERTONOMOUS_SMTP_*` + one test send |
| Numericist knowledge base | **done** | 7 measured facts + 5 open references indexed |
| Demo runbook | **done** | `docs/DEMO_RUNBOOK.md`, measured timings |

Remaining: one real email delivery test; airplane STL when supplied (drops into
the Head Engineer pipeline as a geometry swap); paywalled papers via MIT library.
