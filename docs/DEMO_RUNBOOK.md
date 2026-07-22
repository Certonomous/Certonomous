# Certonomous demo-day runbook

Every scenario below runs **real OpenFOAM solves on this machine**. Which
workflow runs is decided by the request; no number, plot, envelope, or residual
is scripted. Timings are measured, not estimated.

Working directory for every command: `Jango-AGI/sdk`
Artifacts land in: `Jango-AGI/mission-output/<workflow>/`

## The only surface — the control room

Everything runs from one prompt box. Start the server and drive it all from
the browser:

```powershell
cd C:\Users\mouza\github-cleanup\Jango-AGI\sdk
$env:CHIEF_ADAPTER = "openfoam"
$env:OPENFOAM_RUN_PREFIX = "wsl -d Ubuntu -- openfoam2606"
python -m chief_engineer.server
```

Open **http://127.0.0.1:8765** and type the request. The Chief Engineer reads
it, shows its interpretation under the prompt box, and runs the matching
workflow: the workspace becomes the on-record transcript (role-coloured,
citations inline) beside a live gallery where every envelope plot appears as
it is produced. Compute audit and uncertainty verdicts render on the right.

### What to type for each scenario

| Scenario | Prompt |
|---|---|
| Shape optimization | `Minimize drag on the cylinder body, keeping every solve converged inside the validated regime.` |
| Time constraint, closure approved | `Give me drag for the cylinder at Re 20 within 5 minutes.` |
| Time constraint, closure refused | `Give me drag for the cylinder at Re 100 within 5 minutes.` |
| Unfamiliar geometry | `What drag should I expect for an airfoil at Re 500000? We have never run this geometry.` |
| Uncertainty reduction | `How confident are we in that drag number? Tighten the error bars.` |

To force the scarcity branch during a shape-optimization run, occupy the
machine first with `make_busy.sh 12` (see below).

The terminal commands below remain valid and produce identical artifacts —
use them as the fallback if the browser misbehaves on demo day.

---

## Preflight checklist (run T-30 min)

```bash
cd C:/Users/mouza/github-cleanup/Jango-AGI/sdk

# 1. Compute node alive, OpenFOAM responding
wsl -d Ubuntu -u foam -- openfoam2606 simpleFoam -help | head -3

# 2. No stray load (should print 0)
wsl -d Ubuntu -u foam -- bash -c "pgrep -c -f '[c]ertonomous-load' || echo 0"

# 3. Audit reads healthy — expect YES with ~11-12 cores free
python -c "import sys;sys.path.insert(0,'.');from chief_engineer.compute_audit import audit;print(audit(8).headline())"

# 4. Disk space (each workflow writes < 200 MB; motorBike case ~2 GB)
wsl -d Ubuntu -u foam -- df -h /home | tail -1

# 5. Test suite green (36+ tests)
python -m unittest discover -s tests -p "test_*.py" 2>&1 | tail -3

# 6. SMTP configured for the closing email
python -m workflows.email_report --check

# 7. Warm the solver cache — first solve of a session pays WSL start-up
python -m workflows.unseen_geometry > NUL
```

Browser tabs to pre-open: `http://127.0.0.1:8765` (control room, if the
server is used).

**Cached geometry**: the motorBike case stays staged at
`~/certonomous-runs/motorbike` inside WSL (mesh already built, 353,578 cells).
Do not delete it before the demo — remeshing costs ~5 minutes.

---

## Scenario 1 — Uncertainty reduction *(priority 1, ~75 s)*

**Trigger**
```bash
python -m workflows.uncertainty_reduction
```

**Expected on screen**: compute audit YES → Run A (5 samples, ~10 s) reports an
envelope near 3% → Chief cites **L-001 by name** and orders more samples → Run B
(40 samples, ~60 s) reports ~0.8% → verdict separates the shrinking estimator
error from the irreducible physical spread. Three PNGs, ending with
`uncertainty_ab_panel.png` (side-by-side A vs B).

**Measured**: 45 real solves, 3.3% → 0.8% (75% tighter), 70 s total.

**Failure signature**: `no successful samples produced 'Cd'` (WSL unreachable),
or a run exceeding ~3 min (cores held by a stray job — check preflight #2).

**Fallback**: `mission-output/uncertainty-reduction/` from the validated run of this same
workflow — same code, same machine, real numbers. Show `uncertainty_ab_panel.png`.

---

## Scenario 2 — Shape optimization *(priority 2, ~90 s idle / ~70 s scarce)*

**Trigger (abundance branch — audit YES)**
```bash
python -m workflows.shape_optimization
```

**Trigger (scarcity branch — audit NO, Chief Researcher + ROM)**
```bash
# make the machine genuinely busy first
wsl -d Ubuntu -u foam -- bash /mnt/c/Users/mouza/github-cleanup/Jango-AGI/sdk/scripts/make_busy.sh 12
python -m workflows.shape_optimization
wsl -d Ubuntu -u foam -- bash /mnt/c/Users/mouza/github-cleanup/Jango-AGI/sdk/scripts/make_busy.sh stop
```
`--scarce` forces the staged branch without occupying cores, if the clock is
tight.

**Expected on screen**: contract with constraints → audit verdict → either one
parallel wave of 8 solves, or Chief Researcher naming its anchor runs with
rationale, a quadratic surrogate proposing an optimum, and a **confirmation
solve** validating the prediction → constraint screening → real Monte-Carlo
envelope on the winner → bullet report with next steps.

**Measured (staged branch)**: surrogate predicted Cd 1.874 at D = 1.4 m,
confirmation solve returned 1.868 — 0.3% surrogate error; winner
Cd = 1.84 ± 0.031, +14.8% versus baseline; 17 real solves.

**Failure signature**: `No feasible design` (constraints excluded everything —
means a solve diverged); surrogate error > 5% (anchors too clustered).

**Fallback**: `mission-output/shape-optimization/` transcript + `winner_uncertainty.png`.

---

## Scenario 3 — Closure approval under a deadline *(priority 3, ~20 s / ~35 s)*

**Trigger (approved path)**
```bash
python -m workflows.time_constrained
```
**Trigger (rejected path)**
```bash
python -m workflows.time_constrained --reject
```

**Expected on screen**: the deadline forces a coarse mesh → Chief Researcher
rules on the closure → the two verdicts use *visibly different* uncertainty
language:
- approved → `VALIDATED CLOSURE — the coarse mesh costs speed, not trust`
- rejected → `UNVALIDATED REGIME — treat magnitudes as indicative, trend only`,
  followed by the ordered diagnostics.

**Measured**: approved path corrected 600-cell Cd 2.191 → **2.156**, which is
the 21600-cell grid-converged value — the closure recovers the fine-mesh answer
from a coarse run. Rejected path measured a 6.0% discretization shift with the
grid probe rather than guessing it.

**Failure signature**: closure approved when it should be rejected (check the Re
passed in); probe solve timing out.

**Fallback**: `mission-output/time-constrained/`
transcripts, shown side by side.

---

## Scenario 4 — Chiefs on unfamiliar geometry *(priority 5, instant)*

**Trigger**
```bash
python -m workflows.unseen_geometry            # streamlined airfoil
python -m workflows.unseen_geometry --sphere   # sphere at Re 200
```

**Expected on screen**: retrieval of the three real case-memory records with
scores and citations → Chief Researcher separating what transfers (methodology,
regime warnings) from what does not (magnitudes) → explicit refusal to
interpolate a coefficient → the single cheapest run that closes the largest gap.

**No solver runs**: this scenario is pure retrieval + reasoning and cannot fail on
compute. Every cited case is real.

**Failure signature**: none material (no I/O beyond file reads).

---

## Scenario 5 — Email closing *(priority 4, ~5 s)*

**Trigger**
```bash
python -m workflows.email_report                 # emails the most recent mission
python -m workflows.email_report uncertainty-reduction  # or a named workflow
```

**Expected**: "Report for <beat> emailed to <you> (N rows, M plot(s)
attached)." Then show the phone/inbox: an HTML table of the chiefs' decisions
with the envelope plots attached.

**Setup (Sanaa, once, never committed)**: set `CERTONOMOUS_SMTP_HOST`,
`CERTONOMOUS_SMTP_PORT`, `CERTONOMOUS_SMTP_USER`, `CERTONOMOUS_SMTP_PASSWORD`
(app password), `CERTONOMOUS_SMTP_TO`. Verify with `--check` **before demo
day** — one real delivery must be tested.

**Failure signature**: `SMTP NOT CONFIGURED` (env vars missing);
`SMTPAuthenticationError` (needs an app password, not the account password).

**Fallback**: show the previously delivered email in the inbox.

---

## New beats (2026-07-21)

These land on `main`. Each is trigger / expected / failure signature / fallback.
Timings are measured on this machine.

### A — Validation wall (the standing credential)
- **Trigger**: open the control room; the dormant centrepiece is the *Lab
  credentials* wall. Also reachable via the **Lab credentials** tab or
  `?view=credentials`.
- **Expected**: 8 Tier-0 bodies — 4 VALIDATED (cube, ahmed_25, flat_plate,
  naca4412) with measured-vs-reference + source, 2 REFERENCE REGIME MISMATCH
  (sphere, cylinder, blue badge, supercritical-branch diagnosis), 2 TREND ONLY
  (ahmed_35, naca0012) with the honest one-line reason. Header reads "4 of 8
  validated against published experiment."
- **Failure signature**: empty wall → `models/curriculum/results/*.json` missing.
- **Fallback**: `cd models/curriculum && python run_suite.py` regenerates them
  (~23 min full; already committed, so the wall is populated out of the box).

### B — Regime self-diagnosis (sphere / cylinder)
- **Trigger**: point at the sphere or cylinder card on the wall.
- **Expected**: "measured Cd 0.095 matches the supercritical (post-drag-crisis)
  regime … not the subcritical reference 0.47; steady fully-turbulent RANS
  reproduces the post-drag-crisis wake." The lab names *why* the book value does
  not apply — a feature, not a miss.
- **Failure signature**: sphere shows TREND ONLY instead of REGIME MISMATCH →
  the regime `alternates` block is missing from `sphere/reference.yaml`.
- **Fallback**: the reasons are stored in the result JSON; read the card text.

### C — The Certonomous Certificate
- **Trigger**: run any geometry-study mission to completion; a *Sealed
  certificate (PDF)* link appears atop the Report tab, and it is attached to the
  report email.
- **Expected**: one-page PDF — geometry, objective, result + envelope, tier
  badge, three V&V-20 channels, compute, and a SHA-256 evidence seal. A
  curriculum body (e.g. cube) shows the VALIDATED tier on the certificate.
- **Failure signature**: transcript prints "(Certificate could not be issued: …)"
  — the solve is unharmed; the certificate is best-effort.
- **Fallback**: `GET /api/certificate/geometry-study` serves the last one.

### D — Ask the lab (deterministic)
- **Trigger**: the **Ask the lab** tab (or `?view=ask`). Type a question.
- **Expected**: record-grounded answers with display-title citations — "what
  have we validated?", "what do we know about the sphere?" ground on the wall;
  out-of-record questions get an honest "I could not ground an answer … broader
  interpretation comes online with the interpreter." No LLM required.
- **Failure signature**: every answer ungrounded → `models/curriculum/results/`
  or `case_memory`/`lessons` unreadable.
- **Fallback**: `POST /api/ask {"question": …}` returns the same payload.

### E — Live worker-kill recovery
- **Trigger**: during a shape-optimization / sweep mission, run
  `scripts/kill_worker.sh 2` on camera.
- **Expected**: the transcript and present bar report "Worker 2 lost —
  reprovisioning" then "Fresh worker took over slot 2"; the mission completes
  with the **same numbers** as an unsabotaged run (verified by test).
- **Failure signature**: no kill event → the marker dir disagrees; set
  `CERTONOMOUS_SABOTAGE_DIR` the same for the script and the server.
- **Fallback**: `python -m unittest tests.test_worker_recovery` proves it green.

### F — Presentation mode
- **Trigger**: the **PRESENT** toggle (or `P`), or launch with `?present=1`.
- **Expected**: type scales up, config rails and telemetry hide, viewport and
  transcript enlarge, and one large current-action line pins above everything,
  driven by the live transcript.
- **Failure signature**: layout looks cramped dormant → expected; presentation
  mode is for a *running* mission (the hero take).
- **Fallback**: run without the toggle; every panel is still readable.

### G — Autonomy counter
- **Trigger**: launch any mission.
- **Expected**: masthead reads "HUMAN TOUCHPOINTS · 1" (the objective) and stays
  at 1 for an autonomous run; each mid-mission steer increments it.

### Curriculum missions (optional, unattended)
- **Trigger**: `cd models/curriculum && python run_suite.py` (resumable; skips
  finished bodies; `--only <body>` for one).
- **Expected**: each body meshes, solves, and grades against its reference; the
  wall and Ask-the-lab pick up the new credentials. Unattended-operation
  evidence: started once, walks the whole ladder with no human in the loop.
- **Measured**: cube ~1.3 min, sphere/cylinder ~0.6–1.9 min each, full ladder
  ~23 min at refinement 2.

---

## Rehearsal script — full sequence

| # | Scenario | Prompt or command | Time | Cumulative |
|---|---|---|---|---|
| 0 | Preflight | checklist above | 3 min | — |
| 1 | Validation wall | open control room (dormant centrepiece) | 3 s | 0:03 |
| 2 | Regime self-diagnosis | point at sphere / cylinder card | 5 s | 0:08 |
| 3 | Uncertainty reduction | `python -m workflows.uncertainty_reduction` | 75 s | 1:23 |
| 4 | Shape optimization | `python -m workflows.shape_optimization` | 90 s | 2:53 |
| 5 | Worker-kill on cue | `scripts/kill_worker.sh 2` mid-sweep | 5 s | 2:58 |
| 6 | Scarcity on cue | `make_busy.sh 12` then re-run shape optimization | 80 s | 4:18 |
| 7 | Release load | `make_busy.sh stop` | 2 s | 4:20 |
| 8 | Closure approved | `python -m workflows.time_constrained` | 20 s | 4:40 |
| 9 | Closure refused | `python -m workflows.time_constrained --reject` | 35 s | 5:15 |
| 10 | Unfamiliar geometry | `What drag for a body we've never solved?` | 2 s | 5:17 |
| 11 | Certificate + email | finish a geometry study; `python -m workflows.email_report` | 5 s | 5:22 |
| 12 | Ask the lab | Ask tab: "what have we validated?" | 5 s | 5:27 |

Total live compute ≈ 5.5 minutes. For a tighter cut, run 1, 2, 4, 5, 9, 12 (the
credential wall, self-diagnosis, a live sweep with a sabotage save, the
honest-uncertainty verdict, and the lab answering for itself). Toggle **PRESENT**
before the take.

### Narration anchors (what to say over each beat)

- **Uncertainty reduction**: "It doesn't just report uncertainty — it acts on it. That's a
  lesson it wrote for itself, cited by ID, and the envelope shrinks live."
- **Shape optimization / scarcity**: "It checked whether the compute existed before promising the
  sweep. When it didn't, a researcher picked the runs worth paying for and a
  surrogate covered the rest — then a real solve confirmed the surrogate."
- **Closure approved vs refused**: "Same deadline, two different regimes, two different verdicts.
  It knows where its own calibration is valid."
- **Unfamiliar geometry**: "Asked about a geometry it's never seen, it refuses to guess a
  number and tells you the cheapest experiment instead."

---

## Recording the fallbacks

Keep every `mission-output/<workflow>/` directory intact — those transcripts
and PNGs *are* the fallbacks (real runs of the same workflow on the same
machine). Screen-record the uncertainty-reduction and shape-optimization
scenarios once they pass, since those carry live compute that a noisy demo-day
machine could disturb.
