# Phase-2 repo professionalization — proposed target tree and MOVE_MAP

> ## ⛔ SUPERSEDED IN KIND — DO NOT EXECUTE ANY ROW OF THIS PROPOSAL
>
> **Marked 2026-08-16 at `b0ab070d`. Struck and kept, not deleted: the
> reasoning below was sound against the tree it was drawn for, and the
> measurements it carries were re-used by the map that replaced it.**
>
> The owner's target tree, recorded at **`330faa32`** in
> `campaign/MOVE_MAP_2026-08-16.md` and filed as docket **D331**, overrules this
> document in three load-bearing places. This is **not a re-frame of stale
> counts** — the destinations themselves were reversed:
>
> | | this document | the owner's tree |
> |---|---|---|
> | the webroot | `demo-output/website/**` → `web/site/**` **wholesale** | `/web/` serves **site files only**; everything else moves out |
> | `scripts/` | renamed wholesale → `ops/` | `/scripts/` **retained**; `/ops/` takes launchers only |
> | `cases/` | `models/` + `demo-surfaces/` | **one folder per physics family**; `models/` unchanged |
>
> §5's veto item **V8** offered *"records to `docs/campaign/`"* as the
> alternative to keeping records under the served root, and recorded the
> default as **records stay**. **The owner took the alternative**, which
> inverts §2's stage-3 rule rather than adjusting it.
>
> `docs/PHASE2_MOVE_MAP.tsv` was generated from that inverted rule and is
> superseded with this document. Its generator, `scripts/phase2_move_map.py`,
> **was made to refuse to write** at `b0ab070d` rather than left runnable,
> because a banner in a docstring is not read by whoever types the command.
>
> **What survives and was carried forward** rather than re-derived: §3.5's
> eight hard-breaking runtime consumers, §3.4's guard-layer census, §4's
> `.gitignore`-edit-blinds-live-greps constraint, and the out-of-tree checklist
> (crontab, `/usr/local/bin/auto-stop.sh`, the served-root `--directory` flag).

**PROPOSAL ONLY — AWAITING SANAA'S VETO. No file was moved in preparing this
document.** Filed 2026-08-14 as docket item **F1**; drafted against commit
`975f3a8b` (tree measurements individually anchored below, because the tree
moved twice during drafting — see §4.4). Execution remains gated on all four of
section F's release conditions, first among them **Ladder V's confirmed green**,
and on **Sanaa's walk of the tree** (the taste gate, hers, not delegable).

This document instantiates what docket section F (Katie's §7, 2026-08-11)
already specified; it designs nothing that section F settled. Its additions are
the parts section F required but did not yet contain: the per-file MOVE_MAP
(release condition 4), the breakage census behind it, and the landing sequence
for the deferred `.gitignore` rebuild (H3b).

Companion artifacts:

- `docs/PHASE2_MOVE_MAP.tsv` — the full enumeration, one row per moving path.
- `scripts/phase2_move_map.py` — its generator. **The generator is
  authoritative** (L-79): the TSV carries its commit anchor, and the last
  regeneration before execution is the binding map, because the fleet committed
  five times while this proposal was being drafted.

---

## 1. Proposed target tree

```
/                       README.md, LICENSE (decision pending, Katie),
                        .gitignore, .gitattributes,
                        LESSONS.md            [named exception — veto item V2]
                        uq_batch.err, uq_batch.log  [named exception — V1]
sdk/                    product source, RETAINED under its current name
  chief_engineer/  workflows/  openfoam/  geometry/  scripts/  tests/
ops/                    <- scripts/   launchers, guards, audits, cron registry,
                        laptop_bundle/, installed/
docs/                   the only documentation home (charters/, standards/,
                        research/, aws/, papers/ as today)
  filming/              <- FILMING_COMMANDS.md, LAPTOP_SHOOT.md (from root)
cases/                  inputs and birth certificates, never results
  tmr/  curriculum/  airplane/        <- models/
  demo-surfaces/                      <- demo-surfaces/ (+ deduped Stl_files)
web/
  site/                 <- demo-output/website   (the served root)
  filming/              <- demo-output/{plots, acts, gui-proof, fallbacks,
                           loose .png}
evidence/               GITIGNORED; requires its own README stating what lives
                        there and why it is untracked (G2's rule)
  <mirrored old paths>  <- all tracked solver output and logs, at their old
                           paths verbatim under evidence/
  build-logs/           <- mbc_retry* (10 files, H3b)
  wheels/               <- numpy / h5py .whl (2 files, H3b)
  dist/                 <- dist/certonomous-demo.zip (D56-gated)
```

### Justification of each top-level choice, against how the repo was used

**`sdk/` retained rather than renamed `certonomous/`.** Section F offered
either. Measured at `26a32239`, sdk/ already carried the exact substructure
section F names beneath the product source — `workflows/`, `chief_engineer/`,
`openfoam/`, `geometry/`, `tests/` — so the rename would have repurchased every
import path and launcher line in the fleet for zero structural gain. Retention
is 299 files at zero moves and zero breakage.

**`ops/` <- `scripts/`.** Section F names it, and the census (§3) confirmed the
lab's real usage: agents invoke this layer by literal path from code, cron and
tests, which is precisely why it deserves a directory whose name says
"operational machinery" rather than the generic "scripts". The cost is real and
quantified (§3, ~459 live references under the `scripts/` prefix) and every one
is repaid in the same commits as the moves, per section F's own mechanics.

**`docs/` unchanged as the only documentation home, plus `docs/filming/`.**
docs/ already held charters/, standards/, research/. Reshuffling its interior
was considered and rejected: the interior filenames are cited hundreds of times
from durable records, and the newcomer questions ("where are the charters")
already land correctly. The only change is inbound: the two filming documents
loose at root were documentation and move under docs/.

**`cases/` <- `models/` + `demo-surfaces/`.** Section F: "configs and birth
certificates, never results." models/tmr (150 files) and models/curriculum (50)
are reference grids and curricula — inputs; demo-surfaces/ (6) is demo geometry
with its README. `Stl_files/` dissolves: its single file was byte-identical
(blob `9b3a5a35`) to the demo-surfaces copy — veto item V5.

**`web/` split into `site/` and `filming/`.** The load-bearing fact, from
`scripts/demo_servers.sh:46` (matching `docs/aws/provision.sh`): the website
was served with `--directory demo-output/website`, so **published URLs are
relative to the served root, not to the repo root**. Moving the whole root to
`web/site/` therefore renames only the server configuration — every URL path
below the root, and every `campaign/...`-relative citation in the records,
survives unchanged. What CAN 404 published links is removing files from under
the root, which is why the stage-1 untrack carries its own URL census (§3,
census C). `web/filming/` takes the presentation artifacts (plots, acts,
gui-proof, fallbacks) that were never served but are demo-bound.

**`evidence/` gitignored, mirroring old paths verbatim.** G5's destination.
Mirroring means every historical citation of an old path maps mechanically to
`evidence/<old path>` with no per-file judgment, and reachability of the
archive is preserved — which TRACKED_ARTIFACT_SCOPING.md §4.1 established as
the requirement (records name 24 of 25 `*_runs/` directories even though they
cite almost no file paths). The README is not optional: an unexplained
gitignored evidence tree is how a future cold-start agent concludes the
evidence does not exist.

### The newcomer test, answered honestly

- *What is this?* Root README — kept, rewritten to section F's spec (three
  sentences, 30-second sketch, one-line-per-directory map).
- *How do I run a mission?* README points at sdk/ (the product) and ops/ (the
  launchers). Both are top-level and named for what they do.
- *Where are the charters?* `docs/charters/` — unchanged, already correct.
- *Where is the evidence for claim X?* **This is the tree's one honest
  defect.** Campaign records live under `web/site/campaign/` because they are
  published surfaces — the site serves them, and moving them out would break
  every published URL. A newcomer would look in `evidence/` or `docs/` first.
  Mitigations: the root README's map says so in one line; `evidence/README`
  points back at the records; the records' own `campaign/...` citation
  namespace stays valid against the served root. The trade — publication
  integrity over first-guess discoverability — is put to Sanaa explicitly
  rather than smuggled (veto item V8 offers the alternative).

---

## 2. The MOVE_MAP

Generated at anchor `ab4fc849` (20,633 tracked): **20,195 rows** — every path
that moves, no wildcards. Enumeration was the rule for exactly the reason the
brief names: a blanket `campaign/*` exclusion once cost the accepted entry's
own pre-registration (R5_PREREGISTRATION.md, R5_RULE_FREEZE.md).

| Stage | Action | Rows | What |
|---|---|---:|---|
| 1 | UNTRACK-MV to `evidence/` | **12,791** | 12,000 solver-output files (whole-time-dir frame), 778 logs, 10 mbc_retry, 2 wheels, 1 dist zip |
| 2 | GIT-MV, low fanout | **257** | scripts/ -> ops/ (46 at that anchor; 51 at `975f3a8b` — regenerate), models/ -> cases/ (202), demo-surfaces/ -> cases/demo-surfaces/ (6), 2 filming docs -> docs/filming/, 1 dedupe |
| 3 | GIT-MV, big rename | **7,147** | demo-output/website -> web/site (remaining tracked source), demo-output/* -> web/filming |
| — | KEEP (not rows) | 438 | root keeps, sdk/, docs/ |

**The two frames, stated rather than hidden.** `scripts/corpus_figures.py`
counts solver output by immediate parent directory: **8,582** at `26a32239`.
A move map cannot use that frame — a time directory moves as a unit
(`0.025/U` cannot go to evidence/ while `0.025/uniform/functionObjects/...`
stays) — so stage 1 classifies by any non-zero numeric path component:
**12,000**. The delta is nested subdirectories of time directories. Both
numbers print in the TSV header on every regeneration.

**Controls the generator enforces (exit nonzero on failure):** zero unmapped
paths; zero destination collisions; and every solver-output case root
explainable as an OpenFOAM case (tracked `constant/` or `system/` sibling) or
`postProcessing`. The control fired once during drafting, on
`postProcessing.feasibility_smoketest/` — the restart-collision rename this
lab has met before — and was taught that form; the catch is recorded here
because a control that never fires is a control nobody has tested.

**Order within stage 1** follows TRACKED_ARTIFACT_SCOPING.md §5: logs first
(778, one known citation — `tmr/runs/naca-a10-medium/log.checkMesh`, cited
from `campaign/C4_naca0012_closure.md`; annotated in the same commit as its
move), then output (the mass). Initial conditions (965), case dictionaries
(2,727) and every `.py/.json/.png/.md` under `*_runs/` stay tracked — they are
source and summary, and all thirteen exact-path citations land there.

---

## 3. Breakage census — what each move costs, measured

Three independent censuses over the tracked corpus (`git grep -F` /
`git ls-files`; never bare `grep -r`, which is ugrep honouring .gitignore,
L-75). "Live" = code, configs, HTML, JSON consumers that must be repaired in
the same commits as the moves (section F's G3 rule). "Records" = .md
append-only surfaces that are NOT edited; they resolve via commit anchors
(W-5), and `evidence/`'s path mirroring keeps their old paths mechanically
mappable.

### 3.1 Stage 2: scripts/ -> ops/ (census B, at `975f3a8b`)

- **~459 live references** under the `scripts/` prefix in total; 220 against
  the 43 individually-censused filenames.
- Worst offender: **`scripts/self_audit.py` — 46 live references** (docket.json
  x10, the two sdk test fixtures x11, itself x4, fail_open_scan x3, ...).
- Next: launch_solve.sh (17), check_absolutes.py (13), cost_calibration.py
  (9), dispatch_queue.py (9).
- Four scripts had **zero references anywhere** (add_proposals_r6/r7/r8,
  add_proposals_w5_flatplate) — they move with the rest; no deletion is
  proposed (nothing load-bearing deleted without its own docket entry, and
  "unreferenced" is not "not load-bearing" — L-75's archives were unreferenced
  too).
- Root files: LESSONS.md **46 live consumers** (corpus_figures.py x7, fixtures,
  docket.json — the measured case for keeping it at root, V2); FILMING docs,
  uq_batch, mbc_retry: **zero live consumers** — their moves are free of code
  repair.

### 3.2 Stage 3: demo-output -> web/ (census B)

- `demo-output/website`: **2,114 live references — the worst offender in the
  entire map.** Composition matters: the bulk is demo-output's own JSON
  (replay_s1_s6.json x834, docket.json x174) which **travels with the tree**;
  the external mass is `sdk/chief_engineer/exec_bits.py` (x200) and the two
  sdk test fixtures (x92+). So the repair surface is concentrated in a handful
  of files, not smeared across two thousand sites.
- `demo-output/plots`: 17 live; acts/gui-proof/fallbacks: 0 live (records
  only).
- Serving config: `scripts/demo_servers.sh:46` and `docs/aws/provision.sh`
  repoint `--directory` in the same commit (and the cron `@reboot` entry in
  `scripts/installed/` — which appeared mid-draft, see §4.4).

### 3.3 Stage 2: models/ -> cases/ (census B)

- `models/curriculum`: **64 live** (docket.json x19, W3_GUARD_SWEEP.json x10,
  self_audit.py x3); `models/tmr`: 14 live; `models/airplane`: 0 live.
- `demo-surfaces`: 8 live (shoot.html, geometry scripts); `Stl_files`:
  **zero references anywhere** — the dedupe is free.
- `dist/certonomous-demo`: 8 live including `sdk/tests/test_bundle_drift_gate.py`
  and self_audit.py — the D56 gate's own instruments; V4 covers sequencing.

### 3.4 The guard layer (census A)

`scripts/self_audit.py` held **~55 distinct code-level path literals** (~70
sites), concentrated in exactly the "own copy of expected locations"
structures the brief predicted:

- `WEB = REPO/"demo-output"/"website"` (L93–96) — one constant feeding ~25
  downstream reads (ledger, wall, closure submissions, dafoam records, F2
  campaign raw data). One repair point, wide blast radius.
- The citation-resolver whitelist `roots` (L2756–57):
  `("demo-output/", "sdk/", "scripts/", "models/", "mission-output/",
  "docs/", "dist/")` — **five of its seven roots are touched by this
  proposal**; rewritten in the same commit as each stage, or
  `check_evidence_paths_exist` starts failing correct citations.
- `_PY_ROOTS` (L3339) for the fail-open/altitude sweeps names `scripts`.
- The bundle-drift guard's own location tables `_BUNDLE_VERBATIM` /
  `_BUNDLE_PAGES` (L4594–4608) pin `scripts/laptop_bundle`, three
  `demo-output/website/*.html` pages, and bundle root `dist/certonomous-demo`.
- The `BASIS` producer pairs (L4824+, enforced L5155–83) pin
  `scripts/gate_table.py`, `sdk/scripts/build_wall.py` and
  `sdk/chief_engineer/uq.py` — enforcement turns a moved producer into a FAIL
  immediately, which is correct and is why repairs land in the move commits.
- Board/probability pins (L313–317, L1066–68) and six checks globbing
  `models/curriculum/uq-studies`.

`scripts/fail_open_scan.py` pinned `CONTROL_COMMIT = "038b36da"` with
`CONTROL_PATH = "scripts/self_audit.py"`. A scripts/ move leaves the scan and
the pinned **positive** control intact (history keeps the old path) but
breaks the **negative** control (it reads the live file) and
`sdk/tests/test_fail_open_scan.py:104` — loudly, by design; the docstring
anticipated exactly this reorg and forbids silent repointing. The repair is an
explicit CONTROL_PATH repoint in the move commit.

Outside the tree entirely: the **live user crontab** carried
`@reboot ... /home/ubuntu/Certonomous/scripts/demo_servers.sh` — it dangles on
scripts -> ops and **no repo sweep can see it**; it goes on the window
checklist by name. `/usr/local/bin/auto-stop.sh` is an installed copy, not a
path dependence, but drifts from its moved source and is re-installed from
ops/ in the window (the `scripts/installed/` registry, which landed mid-draft
at `9806ab1d`, exists for exactly this diff).

Guard-layer per-move totals: **demo-output/website -> web/site: ~125 files,
~680 reference lines — the worst offender by ~3.5x**, dominated by
`sdk/chief_engineer/exec_bits.py`'s ~200-path waiver registry and the two
absolute-claims fixtures; scripts -> ops: ~65 files, ~195 lines, but denser
in load-bearing single points (crontab, negative control, `_PY_ROOTS`, the
BASIS producer pin); models -> cases: ~35 files, ~65 lines; dist: 3 files.

**A finding the census forced into the open (veto item V9):**
`models/curriculum/results` held generated results data under models/ — and
six self_audit checks glob `models/curriculum/uq-studies`. Mapping models/ ->
cases/ wholesale puts results under a directory whose charter reads "never
results." Default taken: move intact (one-prefix guard repairs) and read
section F's "never results" as "never solver fields"; alternative: split
curriculum results out to evidence/ with six glob repairs. Sanaa's call.

### 3.5 The owed non-markdown consumer sweep, and the published-URL surface (census C)

TRACKED_ARTIFACT_SCOPING.md §4.2 said this sweep was owed before any move. It
was performed for this proposal, and **it refuted the unconditional claim**
"outputs and logs can be untracked without breaking a non-markdown consumer."
The markdown-only measurement was right about markdown; the class it could
not see contains **eight hard-breaking runtime consumers**, all tracked, all
reading tracked stage-1 files:

1. `demo-output/website/campaign/F7_runs/old_spec_readings.py` — reads
   `<t>/alpha.water(.gz)` and `<t>/C` for every t>0 across 15 F7 cases (980
   tracked field files), CWD-relative; its own docstring ("PATH DEPENDENCY —
   READ BEFORE MOVING") demands re-pointing in the same commit, no
   autodiscovery. (Section F's pointer list already named this file.)
2. `demo-output/website/dafoam/f6a_nasa_hump/score_our_baseline.py:15` —
   absolute read of `case/1772/U`.
3. `demo-output/website/dafoam/ladder-b/S1_work/scripts/build_ref.py:35` —
   absolute read of `case/1772/wallShearStress`.
4. The three f6d ensemble builders (`build_ensemble.py`, `build_signdemo.py`,
   `f6a_recheck.py`) — read `case_breuer_re10595/10000/{U,k,omega,nut,...}`.
5. `scripts/check_convergence_validate.py` — two of its known-answer targets
   are tracked `log.*` files; the known-answer suite fails after the move.
6. `sdk/scripts/score_s6_partition.py:58` — opens every gated log named in
   `demo-output/website/monitor/replay_s1_s6.json` (196 exact repo-relative
   log paths).
7. `demo-output/website/campaign/4G_runs/bump_iteration_matched/drag_split.py:60`
   — reads three `tmr/runs/bump-*/log.simpleFoam`.
8. `demo-output/website/campaign/W3_runs/setup.sh:19` — greps a tracked
   `log.checkMesh` under `set -eo pipefail`; the log alone vanishing aborts
   the script.

Every one is repairable by path re-pointing in the move commit, and none is
hidden — but a stage 1 executed on the scoping document's markdown-only zero
would have broken all eight silently. **The owed sweep earned its keep.**

Two archive-sweep instruments additionally define their measured corpus as
"everything under demo-output on disk": `sdk/scripts/replay_monitor_rules.py`
(`ARCHIVE_ROOT = REPO/demo-output`, 1,375 run logs content-swept) and
`sdk/tests/test_log_signatures.py` (ArchiveSweepTests rglob with standing
assertions, e.g. `graded > 150`). Because `evidence/` mirrors old paths at
the repo root rather than staying under demo-output/, **both instruments'
roots are re-pointed at `evidence/` in the same commit as the stage-1 move**,
and their standing counts re-derived and re-anchored.

**The published-URL surface came back clean, and this is the number that
makes stage 1 shippable:** 56 tracked HTML pages under the served root, 79
href/src attributes, **zero** pointing at the generated set, at any `*_runs/`
path, or at `log.*` files; no live `fetch()` of such paths. The stage-1
untrack removes nothing any published page links to. The one exact-path
markdown citation (`C4_naca0012_closure.md` -> `log.checkMesh`) remains the
single record-side dependency, annotated in the move commit per §2.

---

## 4. The .gitignore rebuild (H3b) — how it lands without blinding anyone

**Why it was deferred, restated because it is the constraint that shapes the
landing:** `grep` on this box execs `ugrep --ignore-files`, which honours
`.gitignore` at read time. An edit to `.gitignore` while any agent sweeps
**silently changes what that agent's greps can see**, with no error anywhere
(L-75). Ten agents were live while this proposal was drafted; the edit was
therefore not made, and must not be made, outside the window below.

**The landing sequence — the .gitignore edit is the FIRST act of the quiet
window, and the window is verified, not assumed:**

1. **Window entry, verified three ways:** every family drained or checkpointed
   per section F condition 2 (docket claims closed); process-table sweep shows
   no live agent; the auto-stop gate's view agrees. The window is announced in
   the docket BEFORE the first edit, so any agent launched afterward is the
   violation, not the edit.
2. **Commit A (pathspec `.gitignore` only):** the rebuilt file — `evidence/`
   rule; the ten `mbc_retry` names (H3b rule 1); wheel names; retirement of
   per-directory patchwork the evidence/ rule supersedes (current lines 52–53
   already ignored *untracked* time dirs; the 12,000 tracked ones predate
   those rules and tracked files override ignore rules — that inversion is the
   whole point of the rebuild).
3. **Commit B, immediately after, same session, no gap for sweeps:**
   `git rm --cached` batches + `mv` into `evidence/` + `evidence/README.md`,
   with the C4 log-citation annotation in the same commit as the log move.
   Test suite green after every batch (condition on section F's mechanics).
4. **Wheels trap honoured (H3b):** the wheels are untracked at HEAD in this
   window regardless of the history-purge decision, which stays Katie's and
   stays out of scope here (H2: history is untouched).
5. No agent launches until commits A and B have both landed and the suite is
   green. The two commits are back-to-back precisely so no sweep can observe
   the intermediate state.

**Same-commit repairs bound to commit B** (from §3.5): the eight runtime
consumers re-pointed; `ARCHIVE_ROOT` in `sdk/scripts/replay_monitor_rules.py`
and the ArchiveSweepTests root in `sdk/tests/test_log_signatures.py`
re-rooted at `evidence/` and their standing counts re-derived; self_audit's F2
raw read and six uq-studies globs repointed; the C4 log citation annotated.

**The out-of-tree checklist — dependencies no repo sweep can see, verified by
hand in the window:** the live user crontab line invoking
`scripts/demo_servers.sh`; the installed `/usr/local/bin/auto-stop.sh` copy
(re-install from ops/ via the installed-registry diff); the served-root
`--directory` flag; `CLOSURE_BENCHMARK_DIR` / `~/closure-challenge-benchmark`
(external, unaffected, listed so nobody rediscovers it mid-window).

**This document did not touch `.gitignore`, and nothing before Sanaa's veto
may.**

---

## 5. Veto items for Sanaa — each with the default this proposal takes

| # | Item | Default taken | The alternative |
|---|---|---|---|
| V1 | `uq_batch.err/log` loose at root | KEEP at root (cited from docs/HANDOFF-UQ.md as living at the worktree root; GITIGNORE_PROPOSAL.md pinned them) | move to evidence/ + annotate the handoff |
| V2 | `LESSONS.md` loose at root | KEEP at root (H6 standing record; 46 live consumers measured) | docs/LESSONS.md + repair 46 consumers |
| V3 | wheels | untrack to evidence/wheels/ in the window | history purge additionally — Katie's call, separate, H2 |
| V4 | `dist/certonomous-demo.zip` | untrack to evidence/dist/ — but **D56-gated**: no rebuild/re-track until D56's settlement decides the shipping mechanism | keep tracked until D56 settles, then decide |
| V5 | `Stl_files/naca4412_wing.stl` | GIT-RM-DUP (byte-identical to demo-surfaces copy, blob `9b3a5a35`; zero references) | keep both under cases/ |
| V6 | four zero-reference add_proposals scripts | move to ops/ with everything else | separate retirement docket entry |
| V7 | models/ -> cases/ flattening (cases/tmr not cases/models/tmr) | flatten | keep models/ name as cases/models/ (single-prefix repair) |
| V8 | campaign records under web/site/ | records stay with the served root (URL integrity) | records to docs/campaign/ + URL redirect layer — breaks every published URL absent a redirect mechanism the lab does not have |
| V9 | `models/curriculum/results` (+ uq-studies) is generated data headed into cases/, whose charter says "never results" | move intact; read the charter as "never solver fields" (six guard globs keep one-prefix repairs) | split results/ out to evidence/ + six glob repairs in self_audit |

---

## 6. What this proposal explicitly did not do

No file was moved, copied, deleted, untracked or created outside the three new
artifacts (this document, the generator, the TSV) and the docket row F1. No
directory was created or deleted. `.gitignore` was not edited. No submission,
push, or external interaction occurred. The closure-challenge tree and the
adaptive-selection disclosure were not touched. Execution of every row in the
MOVE_MAP waits on Ladder V's confirmed green, the drained fleet, the quiet
window, and Sanaa's veto and walk.
