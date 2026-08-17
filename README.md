# Certonomous

An autonomous CFD laboratory. State an engineering objective in plain language.
The lab interprets it, forms a team of agents, runs real OpenFOAM solves, and
reports every result with a trust tier and a confidence envelope, bounding its
own trust rather than overclaiming.

This document is for a reader who knows CFD but not this lab. Every number below
traces to a file or to the command that produced it, and each section names its
source. Counts over the corpus are readings at a stated commit frame, not
constants: the tree moves several times an hour while the lab is working, so
re-derive rather than quote. The frame for every count on this page is
`8cefb4e9`.

---

## 1. What the lab produces

| Product | Where it lives |
|---|---|
| An entry to an external turbulence-closure benchmark, scored locally | `demo-output/website/CLOSURE_*.md`, `closure_challenge_*` |
| Verification and validation records: ladders, rungs, gate verdicts | `demo-output/website/campaign/` |
| Solve case trees (OpenFOAM, DAFoam, VSPAERO) | `/home/ubuntu/certonomous-runs/`, outside the repository |
| Sealed one-page PDF certificates carrying a SHA-256 evidence seal | `demo-output/website/certificates/` |
| A control-room server and the SDK behind it | `sdk/chief_engineer/` |
| The lab's own instrument corpus: checks, guards, sweeps | `scripts/`, `sdk/tests/` |

What it does with them:

- **Geometry studies.** Take any watertight STL or OBJ through surface check,
  meshing, a steady solve, and a force reported with its settling envelope.
- **A validation wall.** Canonical bodies (sphere, cylinder, cube, Ahmed, NACA
  wings) graded against published experiment, each with its trust tier and, where
  the solve lands in a different regime than the reference, an explicit reference
  regime mismatch diagnosis.
- **Ask the lab.** Record-grounded question answering over missions, the
  knowledge base, lessons, and the validation wall, with an optional LLM layer
  that reasons over the grounded facts. With no key it falls back to a
  deterministic listing.
- **Aircraft L/D optimization.** Search a wing design space against stated
  mission requirements (passengers, range, take-off and landing speeds),
  reported as a conceptual-design trade.
- **A sealed certificate per mission.** A one-page PDF carrying the result, the
  envelope, the trust tier, the three V&V channels, and a SHA-256 evidence seal.

---

## 2. The headline result

The lab's closure-benchmark entry, scored locally at benchmark commit
`deb91557`. Per-case scores are read from
`demo-output/website/closure_challenge_round5_qcr.json`; board figures are
derived by joining that record to the `LIVE_BOARD` table in
`sdk/scripts/probability_of_rank.py`.

| Quantity | Value | Source |
|---|---|---|
| Overall score, round 5 | 0.056647 | `closure_challenge_round5_qcr.json` |
| Its predecessor, round 4 | 0.065431 | same record |
| Board | 6 entrants plus this entry, 7 positions | `probability_of_rank.py`, board fetched 2026-08-11T23:33Z |
| Overall rank on that board | 1 of 7, with P(rank 1) 50.2% on a 0.2-96.9% at 95% interval, and not statistically decided against 4 of the 6 | derived |
| Margin over Yang, the board leader | 0.001365 | derived |
| P(rank 1) | 50.2% | `probability_of_rank.py`, B = 400,000 |
| Its interval, 95% double bootstrap | 0.2-96.9% at 95% | same, 2,000 outer by 4,000 inner |
| Pairs not statistically decided | 4 of 6, Yang among them | same |
| Best-on-board individual cases | 2 of 8 | derived |
| Of those, earned by this lab's trained model | 0 of 8 | derived; both are cases where a gate declined and the organisers' own RANS field was submitted unmodified |

The rule that governs every restatement of this result, internal or outward
(`docs/PRODUCT_LIST.md` section 4B): no surface may print "rank 1" without the
interval, the count of not-decided pairs, and the board named by entrant count
and retrieval date. A commit anchor is not an admissible board identifier.
`deb91557` scores; it does not rank.

**Submissions are PARKED.** Nothing has been sent, uploaded, registered or filed
outward. This is a local score, not an official placement.

---

## 3. Where things are

| Section | Path | What it holds |
|---|---|---|
| Closure challenge | `demo-output/website/CLOSURE_*.md`, `closure_challenge_*`, `closure.html`, `benchmarks.*`, `wall/`, `closure_eval/`, `closure_challenge_submission_round*/` | The benchmark entry: status, submission drafts, evaluation protocol, per-case error decomposition, the round-4 and round-5 packages |
| Verification ladder | `demo-output/website/campaign/` | Ladder V rungs V1 to V16, every grading record, and the run archives (`F5_runs/`, `F8_runs/`) |
| DAFoam | `demo-output/website/dafoam/` | Adjoint optimisation work: `work_wing/`, `work_sail/`, NACA4412 families |
| OpenFOAM cases | `demo-output/website/tmr*/`, `unsteady-cylinder/`, `valve/`, `committee-grids/`, `mega-batch/`, `race*/`, `hlpw6/`, `optimization/` | Turbulence-model resource cases, canonical bodies, grid studies |
| Charters and governance | `docs/charters/`, `docs/standards/`, `docs/aws/` | The rules the lab is bound by, including the reporting and verification charters |
| Docket | `docs/DOCKET.md` | The lab's finding ledger: every open question, ruling and defect, append-only |
| Lab software | `sdk/`, `scripts/` | The chief-engineer server, mission workflows, and the self-audit and check apparatus |
| Research notes | `docs/`, `docs/papers/`, `docs/research/` | Operating notes, numerics knowledge, prior art |
| Validation curriculum | `models/curriculum/` | Parametric bodies and their experimental references |
| Demo and filming | `demo-output/plots/`, `demo-output/gui-proof/`, `demo-output/acts/`, `dist/`, `mission-output/` | The demo bundle, plots, and control-room evidence |

Every path in the table above was checked to exist at `8cefb4e9`. Sizes of the
principal bodies:

| Body | Files | Size | How to re-derive |
|---|---|---|---|
| Tracked in this repository | 20,764 | 1.82 GiB packed | `git ls-files \| wc -l` |
| Verification ladder, tracked | 14,014 | | `git ls-files demo-output/website/campaign/ \| wc -l` |
| Solve run tree, outside the repository | 132,049 regular files | 69.36 GB | `/usr/bin/find /home/ubuntu/certonomous-runs -type f \| wc -l` |

Most of the lab's output cannot live in a git repository. At `8cefb4e9` that is
**90.66 GB apparent, or 84.24 GB once hardlinks are deduplicated.** Every part of
it is enumerated by exact location in [`LOCATIONS.md`](LOCATIONS.md), so nothing
is invisible merely because it is large.

**Start here** if you are new: [`docs/USING_THIS_LAB.md`](docs/USING_THIS_LAB.md).
Every command in it was executed before it was written down.

---

## 4. Principles

- **Real numbers only.** Every coefficient, field, and mesh count comes from an
  actual solve. Hardcode the path, never the result.
- **The lab bounds its own trust.** No result is called VALIDATED without an
  experimental comparison (ASME V&V 20). Everything else is TREND ONLY, and the
  reason is stated in measured terms.
- **Honest uncertainty.** Envelopes on every plotted quantity. A GP envelope is a
  floor, not a bound. A two-mesh probe is a grid difference, not a verified
  numerical uncertainty.
- **A claim of absence needs a live control.** A sweep that finds nothing has two
  indistinguishable causes: nothing is there, or the search was broken. Only a
  planted control, confirmed by readback in the same run, separates them.
- **Durable records are not revised.** A withdrawn figure is struck and kept, so
  the record shows what was claimed and what replaced it.

---

## 5. Running the lab

Requires OpenFOAM reachable from the host. From `sdk/`:

```bash
CHIEF_ADAPTER=openfoam \
OPENFOAM_RUN_PREFIX="<your openfoam launcher>" \
python -m chief_engineer.server
```

Then open the control room at `http://127.0.0.1:8765`.

Ask the lab from the terminal:

```bash
python -m chief_engineer.ask_cli "what have we validated?"
```

Optional LLM answer synthesis reads `ANTHROPIC_API_KEY` from the environment
only, and it is never committed. Without it, the lab answers deterministically
from its record.

Tests:

```bash
cd sdk && python -m unittest discover tests
```

---

## 6. The verification apparatus

The lab checks itself, and the checks are part of the deliverable.
`scripts/lab_check.py` is the enumerated runner everything reports through. It
finds the checks mechanically rather than from a typed list, and it prints its
own frame: how many candidates it found, how many ran, and what it could not run
and why. A green run is therefore readable as the narrow statement it is.

```bash
python3 scripts/lab_check.py          # the standing run
python3 scripts/self_audit.py         # the claim-surface audit
```

Its exit contract is a severity ladder, not a taxonomy. Read from the module's
own contract section:

| Exit code | Meaning | Effect |
|---|---|---|
| 0 | PASS | allowed |
| 1 | FAIL | blocked |
| 2 | FAIL | blocked |
| 3 | UNKNOWN about the runner's reach | warn, do not block |
| 4 | UNKNOWN about a check's output | blocked: the runner does not know what the check found |

A check that dies with a traceback is UNKNOWN, not FAIL. The difference matters.
FAIL is a statement about the lab; UNKNOWN is a statement about the instrument.

Individual guards live in `scripts/check_*.py`. Each states, in its own output,
the frame it can and cannot see. A check that cannot say what it failed to look
at is not trusted here.

---

## 7. Reading the record

Three conventions will save a new reader time.

1. **Anchors, not paths.** Durable claims cite the commit that established them.
   A commit anchor stays true. A `file:line` locator is only true at the frame it
   was measured in, and several records carry locators that were correct when
   written and moved afterwards.
2. **Strike-and-keep.** `~~text~~`, `<s>` and LaTeX `\sout{}` mark a withdrawn
   claim that is deliberately still visible. A PDF cannot be graded from its text
   layer: a struck figure sits in the text stream exactly as a live one does, so
   PDFs must be rendered and read visually.
3. **Say which arm you swept.** The corpus has four arms (tracked, untracked,
   gitignored, run tree) and no single command reaches all of them. See
   [`LOCATIONS.md`](LOCATIONS.md) section 5 for the reach limits.

---

## 8. Limits, in one place

1. **The corpus counts on this page are readings at `8cefb4e9`, not constants.**
   The tracked and gitignored arms move several times an hour while the lab is
   working. Each count above carries the command that reproduces it; run it.

2. **The headline score is local, and the standing is not decided.** The
   one-seed uncertainty on the overall exceeds the margin over Yang, who leads
   the board:

   | Quantity | Value |
   |---|---|
   | Truth-free one-seed bound on the overall | 0.002419 |
   | Margin over Yang, the board leader | 0.001365 |
   | Bound as a fraction of the margin | 177% |
   | Overall under adverse seed loading | 0.059066 |
   | Yang's overall | 0.058013 |

   0.059066 is above 0.058013, so the adverse leg of a seed the lab did not
   control loses the point lead outright. First on the point estimate, and not
   first within noise. Derived from
   `demo-output/website/closure_challenge_seed_sensitivity.json` and
   `closure_challenge_stability_physicality_audit.md` section 1.

3. **No search here reaches the whole corpus.** Measured at `8cefb4e9`:

   | Reach limit | Count | Of |
   |---|---|---|
   | Tracked blobs `git grep -a` can read | 20,738 | 20,764 |
   | Unreachable by `git grep` in any mode | 26 | 17 symlinks and 9 empty blobs |
   | Additionally skipped by `git grep -I` | 1,476 | 981 that `.gitattributes` marks binary, plus 495 git auto-detects from NUL bytes |
   | Of the 981 marked, containing no NUL byte at all | 11 | plain text, including published certificate PDFs |

   The 26-file gap has been stable across every frame measured this week even as
   both totals moved.

4. **Almost nothing here is scheduled.** Re-derived at `8cefb4e9`:

   | Scheduled thing | State |
   |---|---|
   | Root cron | one entry, the five-minute auto-stop gate |
   | User cron | one entry, `@reboot` for the demo servers |
   | Installed git hooks | one, `pre-commit`, the index guard of docket D242 |
   | CI configuration, Makefile, pytest or tox config | none tracked, none present |

   The installed hook lives in `.git/hooks/`, which git does not track, so it is
   local to this box and never travels with a clone. Every check in `scripts/`
   and `sdk/tests/` otherwise runs when a person or an agent types its name, so a
   check being correct is not evidence it has run.

5. **The lab's own records are the evidence for most claims on this page.** No
   third party has re-derived them.
