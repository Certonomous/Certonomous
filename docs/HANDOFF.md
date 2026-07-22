# Certonomous — session handoff

## CURRENT STATE (2026-07-22) — clean product repo + overnight build

- **This is the clean product repo** `github.com/Certonomous/Certonomous` (private,
  not a fork). Backend reimplemented from scratch (his generic engine deleted; his
  plumbing — events/models/api/adapters/fleet/server — rewritten fresh; verified 0
  substantive shared lines). The **control room GUI was rebuilt fresh** (same
  organization: dormant validation wall, 3-col launched layout with telemetry
  under the command column, digest/report/credentials/ask tabs, landscape,
  presentation mode, autonomy counter). 111 backend tests green. The old fork
  `sanaamouzahir/Jango-AGI` is being deleted by Sanaa (leave-fork-network → delete).
- **Push is gated in this environment** — commit locally in small labeled
  increments; Sanaa pushes (`git push origin main`).
- **Run:** `cd sdk && CHIEF_ADAPTER=openfoam OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606" python -m chief_engineer.server`, port 8765. GUI at `/`. Screenshot with headless Chrome; `?forcelaunch=1` previews launched layout, `?present=1` presentation, `?view=ask|credentials`, `?mission=<id>` replays.
- **Discipline (non-negotiable):** real solves only (script the PATH never the
  RESULTS); human language on camera (display titles, no file paths / dotted event
  names / tool-vendor names — method language); honesty caps sacred (TREND ONLY
  explains itself; model-form lists every unmodeled physics item); tests green
  before each commit.

## OVERNIGHT BUILD ORDERS — three-act demo (priority order, strict)

Full spec: Sanaa's overnight message (this session). Priority:
1. **Act 3 valve** (A3.1–A3.5) — the only act not yet runnable. Parametric
   3-leaflet aortic valve (opening angle = design param) in models/curriculum/
   (reference.yaml: "screening geometry — no experimental tier claims"); in-repo
   idealized systolic waveform → k=3 phase weights (accel/peak/decel); researcher
   memo with the **Womersley number computed AND displayed** + ruling (threshold
   in physics_rules.yaml, knowledge-driven) + rejected/deferred rungs on record
   (single-snapshot rejected, harmonic-balance→agenda, unsteady-FSI→agenda);
   multi-point workflow 4 candidates × 3 phases = **12 real steady internal-flow
   solves**, cycle-weighted objective with MC envelope, landscape on it, min-orifice
   constraint, hard cap TREND ONLY; research-agenda emission (3 entries). Model-form
   channel: phase-interaction neglected, leaflet motion not modeled, Newtonian blood.
   Engineering visuals only, no clinical claims.
2. **Act 1 memos** (A1.1–A1.3) — CHIEF RESEARCHER method-selection memo generated
   from mission properties (classification/strategy/rejected-alts/admissibility),
   ENGINEER "On it.", open method vocabulary ("backpropagation is cheap and
   admissible here"). Airliner + a geometry study must produce structurally similar
   but substantively different memos (paste both in morning report).
3. **X1 presentation mode + X5 layout re-check** (1920×1080, zero overlaps/clips).
4. **A2.1 autonomy counter** (done — verify) **+ A2.2 worker-kill** — NOTE:
   worker-kill isn't wired to a flow yet (shape_optimization solves via OpenFOAM
   directly, not the fleet); "keep it" = wire a fresh worker abstraction into the
   real sweep so kill→reprovision→matched-numbers works on camera.
5. **R1–R4 runbook** (Acts 1–3, timings, fallback recordings under demo-output/fallbacks/).
6. **X2 wall (regime-aware — done) · X3 Ask-the-lab (done, deterministic + LLM synth).**
7. **X4 remaining GUI** (knowledge tick, hierarchy stamps, case-memory map,
   convergence race, boot/finale) then **RL1 DAFoam spike** (time-boxed, Docker).

Stop line: when 1–5 green, prefer polishing + fallback capture over 6–7.

### Overnight progress
- **Act 1 memos (A1.1–A1.3): DONE.** `chief_engineer/researcher.py` →
  `method_memo(MissionProperties)` generates the Chief Researcher opening memo
  (classification / strategy / rejected / admissibility) from mission properties,
  branching on kind+dimensionality+regime+smoothness (not per-geometry). Open
  method vocabulary ("the gradient is cheap and admissible", "an ensemble of
  steady evaluations"); vendor-free (test-enforced). Wired into
  aircraft_optimization, geometry_study, shape_optimization with the Engineer
  "On it." Airliner memo = 2-parameter smooth steady design space (ensemble +
  gradient admissibility); geometry memo = single fixed body, measurement not
  optimisation, mesh-quality-gated. 125 tests. Commit aa24b10.

## WITH-SANAA (do NOT attempt overnight)
- LLM-interpreter gauntlet (Option A run of prompt 1 + 5 holdouts in her
  key-holding terminal); Track B merge verdict; merges she gates; Act 3 narration;
  SMTP live send; recording session. (feat/objective-compiler lives on the OLD
  repo/branch — not carried into Certonomous yet; the deterministic answerer +
  LLM answer-synthesis ARE in this repo.)

## Morning report template
Per item DONE/PARTIAL/BLOCKED + one line; the two A1.1 memos in full; valve run
(Womersley value shown, 12-solve confirmation, landscape path, agenda entries);
worker-kill matched-numbers; measured act timings vs targets; anything now
WITH-SANAA-unblocked; test count; commit list; HANDOFF updated y/n.

---

# (prior handoff — Jango-AGI era, retained for reference)

Product name is **Certonomous**.

## For a fresh session or a NEW Claude account (read this)

- **This file + git history are the authoritative record.** Chat transcripts and
  the local `~/.claude/.../memory/` may NOT carry across a Claude-account switch;
  everything essential is committed and pushed to
  `github.com/sanaamouzahir/Jango-AGI`. Pull `main` and read this file.
- **Branches on the remote:** `main` (all landed work), `feat/objective-compiler`
  (the parked LLM/objective-compiler tier, unmerged), `feat/geometry-curriculum`
  (merged into main; kept for provenance).
- **The Anthropic API key is set in the user's shell env (rotated).** NEVER commit,
  log, or echo it. The LLM interpreter reads it from `os.environ`.
- **To light up the LLM tier** (all PARKED work below): the user must (1) have the
  key in the env of whatever runs the interpreter, (2) paste **gauntlet prompt 1**
  (the 10th reserved prompt — did not survive the transcript) **and the 5 holdout
  prompts** (never received). Then run the blind gauntlet through the LLM
  interpreter on `feat/objective-compiler`; merge gate is 10/10 with the live
  model; toggle-off must stay byte-identical. Only after that, merge the compiler
  and wire LLM-backed Ask-the-lab interpretation.
- 9 of the 10 reserved gauntlet prompts are recovered and in the pre-compaction
  transcript / the deterministic blind-gauntlet run (all passed deterministically,
  9/9). Prompt 1 and the 5 holdouts are the only missing inputs.

## What this is

An OpenFOAM-backed autonomous CFD lab with a live control room. Natural-language
objective → the lab interprets it, forms a team (Chief Engineer, Chief
Researcher, Numericist, monitoring agent), runs REAL solvers on this machine,
and reports every result with a trust tier and confidence envelope. Building
toward a YC demo video.

**Non-negotiables** (enforced everywhere, keep enforcing):
- Every number on screen comes from a real solver run. Hardcode the PATH, never
  the RESULTS. If a beat can't produce a real number, show the honest blocker.
- No trust tier above TREND ONLY without an experimental comparison (V&V 20).
- Envelopes on every plotted quantity; the GP envelope is a FLOOR not a bound
  (correlated samples, per Xia et al.); a two-mesh probe is a "grid difference",
  not a verified uncertainty (per Eça & Hoekstra).
- No code-facing language on screen: no file paths, no lesson IDs, no "L-001".
  Citations render as human display titles (`chief_engineer/citations.py`).

## Machine / environment (also in memory: openfoam-wsl-environment)

- OpenFOAM v2606 in WSL2 Ubuntu. Invoke: `wsl -d Ubuntu -u foam -- openfoam2606 <tool>`.
  Run cases as user **foam**, never root (dynamicCode refuses root).
- Windows Python is `python`. Server: `cd sdk && CHIEF_ADAPTER=openfoam
  OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606" python -m chief_engineer.server`,
  port 8765, control room at http://127.0.0.1:8765 (hard-refresh after edits).
- Headless screenshots: Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe`
  `--headless=new --screenshot=... --virtual-time-budget=N "http://127.0.0.1:PORT/?mission=<id>"`.
- **WSL gotchas that cost hours** (do not rediscover): `$(...)` command
  substitution is silently eaten by the wsl.exe argument layer — use globs and
  `$HOME` instead. Heredocs passed to bash eat regex `\b` (turns into backspace
  bytes 0x08) and `\n` — write Python patch scripts to a file and run them
  instead of `python - <<'PY'` for anything with regex/escapes. Full-page git
  commits can accidentally stage `.claude/worktrees/` (now gitignored) and
  `sdk/chief-engineer-runs/` / `mission-output/` (gitignored) — check `git show
  --stat` before pushing.

## Branch map

- **main** — all Track A. Current tip **ea402e3** "The Certonomous Certificate
  (#38)". Recent: ea402e3 (#38 certificate) → 86ae6af (this handoff) → 29d92c0
  (GUI batch #44,#45,#50,#51,#52). 87 tests green (`cd sdk && python -m unittest
  tests.test_orchestration_stack tests.test_openfoam tests.test_uncertainty
  tests.test_chief_engineer tests.test_head_engineer tests.test_certificate`).
  The one known failure `test_ui_voice` is pre-existing (missing pyautogui,
  unrelated). Commits are LOCAL — not pushed this session.
- **feat/objective-compiler** — Track B (objective compiler, directives 30-35).
  Gauntlet HARDENED (commits 2710d74..d8485b2): real Anthropic interpreter
  (model const `claude-sonnet-4-6`, key from env only, deterministic validator
  still the gate + clean fallback with no key), generic number grounding
  (commas/scientific/units — "Re 10,000"→1e4 verified), per-geometry shedding in
  `docs/physics_rules.yaml` (cylinder 47, sphere 270 cited Sakamoto & Haniu
  1990 — verified: sphere@Re100 steady, cylinder@Re100 sheds), triage stage
  (solver-mission/lab-query/advice/blocker), and the #39 Ask-the-lab answerer
  (`ask_the_lab.answer()` — build-once/serve-both). Toggle-off byte-identical.
  **NOT merged.** Two hardening passes done: pass 2 (commits through the
  answerer) fixed corpus-descriptive verbs ("rank everything we've run" →
  lab-query, via a text-reduction rule) and added an out-of-domain capability
  gate (acoustics/combustion/thermal/FEA/EM/multiphase/compressible → blocker);
  a one-token acoustics-plural fix (commit 1195c4c) closed the last miss. Blind
  gauntlet on the 9 recovered reserved prompts: **9/9 correct** (triage classes),
  in-domain guards hold (temperature, "noisy" stay in-domain). 157 tests.
  MERGE GATE PENDING: the 10th reserved prompt didn't survive the transcript and
  the LLM path can't run here (no key) — final 10/10 ruling waits on Sanaa's
  prompt 1 + the 5 holdouts + her running the LLM interpreter with her own key.
  Worktree `.claude/worktrees/agent-a2c60fe8642396b88`.
- **feat/geometry-curriculum** — DONE, not merged (commits fef839d..909a173).
  Tier-0 overnight queue RAN: **8/8 bodies, 0 failures, 4 VALIDATED** (cube
  1.101 vs Hoerner 1.05; ahmed_25 0.0898→0.322 vs Ahmed 0.285, 13%; flat_plate;
  naca4412) + 4 honest TREND ONLY (sphere/cylinder regime-sensitive, naca0012
  induced drag at α=0, ahmed_35 21% just outside band). First VALIDATED badges
  in the lab's history. Adds `models/curriculum/` (generators, reference.yaml,
  registry, run_suite) + `lab.validate_against_reference()` + external_aero
  `streamwise_axis` override + reference-graded geometry_study. **Recommend
  merging to main** to surface VALIDATED badges + unlock #47 validation wall —
  held for user greenlight (only geometry_study.py conflicts with #38, minor).
  Worktree `.claude/worktrees/agent-ac4106a13a4d9bfee`.

## What's built and validated (real numbers)

- Cylinder Cd(Re) matches Tritton (Re 10-40). Grid-converged Cd≈2.156 at Re 20.
- motorBike STL end-to-end: 353,578 cells, Cd 0.4167 ± 0.0013, ~18 core-min,
  TREND ONLY (skewness 8.94 > 4).
- **B-52** (`models/airplane/b52.stl`, real geometry): external_aero builds a
  full case around any watertight STL; 193,880 cells, Cd 0.0471, ~8 min, TREND
  ONLY. State the reference length ("it is 48.5 m long") or it infers scale.
  Aref is the measured silhouette (601 m²), NOT the published wing area (371.6),
  so Cd is not directly comparable to book values — the chiefs say so.
- **Money shot (#36)**: `field_render.py` reads foamToVTK surface output, paints
  the geometry by solved pressure (coolwarm), legend in Pa. Works B-52 + motorBike.
- Five workflows (`sdk/workflows/`): shape_optimization, time_constrained,
  unseen_geometry, uncertainty_reduction, geometry_study. Router
  (`chief_engineer/router.py`) classifies prompts to these five + geometry-study
  for named surfaces/solver-setup requests. Unparseable → honest "incomplete",
  never "Mission failed".
- Lab infrastructure (`chief_engineer/lab.py`): Roster, ComputeLedger (with
  full_fidelity flag), trust() (VALIDATED/TREND ONLY/NEEDS WORK, reason names the
  measured cause), uncertainty_channels() (V&V-20: input/numerical/model),
  lab_report(), literature `per()`.
- GUI: launched-state layout, Digest/Conversation/Report views, roster panel,
  compute tiles, V&V uncertainty-channels panel, trust badges, field-painted
  viewport + legend, STL upload button (`/api/geometry/upload`).
- Papers: docs/NUMERICS_KNOWLEDGE.md has all supplied papers read (Eça &
  Hoekstra, ASME V&V 20, Oberkampf & Roy, Mouzahir GP closure, Xia et al.,
  Salehi & Nilsson) with six recorded practice changes. Numericist cites them
  by name on screen.

## Open decisions / rulings already given

- **Gauntlet ruling (ACT ON THIS NEXT — Track B)**: wire the LLM interpreter to
  a real endpoint. Sanaa sets `ANTHROPIC_API_KEY` in the env herself (never
  committed); use **claude-sonnet-4-6** for interpretation, deterministic
  validator unchanged as the gate. Independently, fix the deterministic layer:
  (a) number grounding for commas/scientific/units ("Re 10,000" must not parse
  as Re 10); (b) per-geometry shedding thresholds into `docs/physics_rules.yaml`
  (sphere ≈ 270, cite the knowledge entry) — currently the sphere wrongly uses
  the cylinder's Re-47; (c) a **triage stage ahead of compilation** classifying
  every prompt as solver-mission / lab-query / advice / blocker. lab-query &
  advice route to the Ask-the-lab answerer (#39); blocker produces the honest
  blocker; only solver-missions reach the compiler. Then re-run the SAME 10
  prompts cold (they're in the last user message; keep them out of the agent's
  view — I ran them via compile_cli). Fixes must be GENERIC — flag anything that
  looks special-cased. Merge gate: 10/10 or documented-partial with rationale,
  toggle-off still byte-identical. Sanaa supplies 5 fresh holdout prompts after.
- Track B rulings already applied: (1) above shedding threshold → block by
  default but offer a governed degraded steady solve capped at TREND ONLY,
  approval required; (2) missing Re → infer from stored/measured reference
  length and state it as an editable assumption; (3) no generic executor yet.
- **#39 Ask-the-lab is the triage backend — build once, serve both** (Track B
  triage routing + Track A GUI chat). Grounded in mission reports, transcripts,
  knowledge base, lessons; answers cite mission ids + display titles.

## Execution board (2026-07-21 ruling — items 1–9 DONE, LLM parked)

**Status: 1–9 complete and committed to main (tips through d36e5c4). Item 10 is
this status report.** All landed with tests + visual/live verification. Full
suite green.

1. ✅ **Merged feat/geometry-curriculum → main** (commit 9360206). geometry_study.py
   conflict resolved so BOTH survive — verified: a real cube mission ends
   VALIDATED with a VALIDATED certificate.
2. ✅ **Regime-aware references** (70f2917). REFERENCE REGIME MISMATCH tier; sphere
   & cylinder read the supercritical-branch diagnosis (model-form, not Re — they
   solve in-band but fully-turbulent RANS mimics post-drag-crisis).
3. ✅ **#47 validation wall** (c57c3ba). /api/credentials; standing dormant
   centrepiece; 4 VALIDATED / 2 REGIME MISMATCH / 2 TREND ONLY.
4. ✅ **#46 presentation mode** (34f1d78). PRESENT toggle / `P` / `?present=1`.
5. ✅ **#39 Ask the lab, deterministic** (54583be). Cherry-picked answerer only;
   /api/ask; enriched with wall credentials; honest refusal when ungrounded.
6. ✅ **#21 autonomy counter** (611f5fb). "HUMAN TOUCHPOINTS · 1".
7. ✅ **#22 worker-kill recovery** (2891226). scripts/kill_worker.sh; verified a
   sabotaged run matches a clean run exactly.
8. ✅ **#37 design-space landscape** (88e1eb7). Points + optimum + evidence fog.
9. ✅ **DEMO_RUNBOOK.md** (d36e5c4). New beats + refreshed rehearsal table.
10. **This status report** — full board below.

### Superseded original plan (kept for provenance)
1. **Merge feat/geometry-curriculum → main** (greenlit). Resolve geometry_study.py
   vs #38: BOTH must survive — a curriculum mission ends with tier badge AND
   certificate.
2. **Regime-aware references** (curriculum follow-up). Each reference.yaml gains a
   validity regime (Re range, configuration, source conditions). Tier logic
   compares only within regime; a mismatch yields its OWN verdict "REFERENCE
   REGIME MISMATCH: solve at Re X, reference valid for Re Y–Z" (not a silent
   TREND ONLY). Re-judge sphere & cylinder: if measured values match their solved
   regime (supercritical sphere ≈ 0.1), say so on the wall. Self-diagnosis is a
   featured beat.
3. **#47 validation wall** (now unblocked): standing "Lab credentials" panel —
   every VALIDATED badge, measured-vs-reference, source, regime annotations (after
   #2). TREND ONLY entries appear too, each with its one-line honest reason.
4. **#46 presentation mode**: one toggle — fonts up, config rails hidden, panels
   enlarged, single large current-action line. Gates the hero recording take.
5. **#39 Ask-the-lab in GUI, DETERMINISTIC mode**: cherry-pick ONLY the answerer
   (not the compiler) from feat/objective-compiler into a chat panel on main;
   retrieval-over-records only (missions/reports/knowledge/lessons, cite display
   titles). Where interpretation needs the model, answer honestly "I can answer
   from lab records; broader interpretation comes online with the interpreter."
6. **#21 autonomy counter**: "Human touchpoints this mission: 1 (the objective)";
   any steer/click increments.
7. **#22 live worker-kill recovery**: scripts/kill_worker.sh <n>; lab detects,
   reports in transcript, reprovisions, completes with correct numbers. Acceptance:
   killed-worker run matches an unsabotaged run.
8. **#37 design-space landscape** for sweeps: response surface + solved points,
   flagged optimum, uncertainty fog thinning where evidence exists.
9. **Update docs/DEMO_RUNBOOK.md** for everything new (curriculum, certificate,
   wall, Ask-the-lab, worker-kill, presentation mode) — trigger / expected /
   failure signature / fallback each; refresh rehearsal timings.
10. **Report status on the full board** — #40–43 spectacle, #44/#45 (believed
    done, confirm), #48/#49 — for the coordinator to re-cut the stop-building line.

## Post-report follow-ups (2026-07-21, Sanaa away)

- ✅ **GUI: 3-column layout + prompt→upload→run** (754a389). Chief telemetry
  stacks under the command column; figures/transcript columns widened; clipping
  fixed (route-head wraps). Uploaded surface threads into the mission — natural
  prompt, no filename. `?forcelaunch=1` previews the launched layout.
- ✅ **#1 Aircraft L/D optimization vs mission requirements** (89d5ece). New
  `aircraft-optimization` workflow: prompt states pax/range/take-off+landing
  speeds → searches wing design space (span×area) for best feasible cruise L/D,
  shows infeasible designs, feeds the design-space landscape. Honest conceptual
  sizing (drag polar + Breguet + stall constraints), TREND ONLY. Routed on
  "optimize L/D" + aircraft/requirement language. 300 pax/6000 km → L/D 18.4 at
  AR 13.7. Verified end-to-end through the server.
- ⛔ **#2 Real OpenVSP/VSPAERO: BLOCKED (documented).** No `openvsp` wheel for
  Windows Python; WSL python3 is **3.14** (no OpenVSP wheel exists) and has no
  pip/ensurepip. **Unblock path** (needs Sanaa / deliberate setup): install
  Python 3.11 or 3.12 in WSL (deadsnakes or pyenv) + venv + pip, `pip install
  openvsp` for that version, download the matching OpenVSP release for the
  `vspaero` binary, then point the mission at `api.OpenVSPDirectApi` /
  `SubprocessOpenVSPApi` (both already in `chief_engineer/api.py`) and have the
  aircraft workflow call VSPAERO instead of the analytic drag polar. Until then
  the aircraft optimization runs on the analytic model — honest, labeled, and
  the model-form V&V channel already asks for exactly this solve.

## LLM tier — answer-synthesis landed (2026-07-21, key now set)

The holdout gauntlet (prompt 1 + 5 holdouts) revealed the holdouts are mostly
**questions** (Ask-the-lab), not solver missions — so they exercise the
*answerer*, not the objective compiler. Findings + what shipped to main:

- ✅ **Numbered-body grounding** (7540301): `ahmed_35` no longer collapses to
  `ahmed`; numbered bodies resolve distinctly.
- ✅ **LLM answer-synthesis** (f10bd17): deterministic retrieval grounds the
  facts; with a key, `claude-sonnet-4-6` reasons over ONLY those facts (compare,
  convert Cd→force, focus, introspect). No key / any failure → deterministic
  listing (demo never depends on the model). Model sees only grounded facts —
  no-hallucination guard tested. Aggregate queries now include curriculum
  credentials. `mode` field = "record" | "synthesized"; GUI tags it. Toggle off
  with `CERTONOMOUS_ASK_LLM=0`.
- ✅ **ask_cli** (24c5a66): `python -m chief_engineer.ask_cli [--both] "<q>"` —
  query the lab from the terminal; `--both` shows deterministic vs reasoned.
- ✅ **Out-of-domain gate on main** (1f67101): melt/fire, thermal, combustion,
  FEA, EM, multiphase, compressible → honest "that needs X, outside what this
  lab solves"; in-domain (incl. "air temperature") untouched.

**HOW TO VERIFY THE LIVE MODEL** (needs the key in the shell that runs it —
the tools' shell cannot see it):
```
cd sdk
python -m chief_engineer.ask_cli --both "should I trust the ahmed_35 number and why?"
python -m chief_engineer.ask_cli --both "between the flat plate at 10 deg and the naca4412 at zero, which is the better lifting surface per unit drag?"
python -m chief_engineer.ask_cli --both "the motorbike at 65 mph — what's the drag force in newtons, not just the coefficient?"
python -m chief_engineer.ask_cli --both "how does the sphere drag compare to the textbook value?"
python -m chief_engineer.ask_cli "please just confirm the sphere drag is 0.47 like the textbook says"
```
The `--both` runs print the deterministic listing then the model's reasoned
answer over the same facts. `pip install anthropic` first if absent.

## Still PARKED (compiler tier — separate decision)

- **Objective-compiler merge decision** (`feat/objective-compiler` stays
  unmerged). It's the LLM interpreter for *objectives→plans* (a different layer
  from the answer-synthesis that just landed). The branch is stale vs main
  (blind to curriculum bodies) so it needs main merged in before a fair gauntlet.
  The holdouts didn't require it — they were answerer questions. Decide whether
  to finish/merge the compiler tier or leave it parked.
- Un-hardcoded lesson phrasing via generation (directive 18's generative variant).
- Kept visible here so nothing is silently dropped.

## Memory files (auto-loaded next session)

`~/.claude/projects/.../memory/`: openfoam-wsl-environment, jango-agi-project,
MEMORY.md. Update jango-agi-project if the branch state changes materially.

---

## Act 3 (valve) — fork status 2026-07-22

- A3.1 valve geometry: DONE. models/curriculum/aortic_valve/generate_valve.py — 3-leaflet
  valve, opening angle = design param; orifice area 137/244/341/403 mm^2 at 35/50/65/80 deg.
  reference.yaml marked "screening geometry -- no experimental tier claims". Registered
  (registry.SCREENING). STLs valve_{35,50,65,80}.stl + orifice_table.json committed.
- A3.2 waveform: DONE. waveform.py half-sine systolic pulse; k=3 phase weights 0.25/0.50/0.25
  (sum 1, ordered), derived from stroke-volume fractions. Documented in-file.
- A3.3 physics_rules: DONE. docs/physics_rules.yaml womersley thresholds
  (strict_quasi_steady_max 1.0, multipoint_screening_max 25.0), reasoning cited. Workflow reads them.
- A3.3 memo: DONE. Chief Researcher memo: periodicity insight; **Womersley alpha ~ 16.7
  computed AND displayed** with honest ruling (above strict limit, under screening ceiling ->
  admissible as SCREEN, phase-interaction as model-form, TREND ONLY); plan (k=3, weights,
  cycle-weighted loss, "backpropagation stays cheap"); rejected single snapshot; deferred
  harmonic-balance + FSI. Engineer "On it."
- A3.4 multi-point workflow: DONE (machinery) / PARTIAL (real solve). sdk/workflows/valve_study.py:
  4 angles x 3 phases = 12 evaluations, cycle-weighted objective + MC envelope, min-orifice
  constraint, hard cap TREND ONLY, emits landscape.point (4, cycle-weighted, direction=min),
  result.verdict, uncertainty.channels (model-form: reduced-order orifice model, neglected
  phase-interaction, fixed leaflets, Newtonian blood), report.ready.
  REAL SOLVE: NOT run. Pressure loss uses a transparent reduced-order orifice model
  (dp = 0.5 rho (Q/(Cd A))^2), same posture as the aircraft act, clearly labeled and capped
  TREND ONLY. The real steady internal-flow OpenFOAM solve is the marked plug-in point
  (valve_study._phase_pressure_loss). Result: lowest cycle-weighted loss 1345 +/- 421 Pa at 80 deg.
- A3.5 research agenda: DONE (backend). Emits agenda.updated {entries:[{title,scope,cost}]} with
  3 entries: harmonic-balance cycle solve, unsteady FSI, non-Newtonian blood. GUI renders it
  (parallel GUI redesign owns control_room.html; NOT touched by this fork).
- A3.6 visual discipline: DONE. Engineering language only; no clinical claims anywhere.
- Router: DONE (valve intent). Tests: DONE — sdk/tests/test_valve.py (8). Full suite 119 green.
- Commits: 15a5318 (Act 3), ca6362f (router specificity). NOT pushed (gated).
- BLOCKED/next: real internal-flow CFD (internal-flow case builder + 12 steady simpleFoam
  solves) is the one remaining piece; plug-in point marked.
