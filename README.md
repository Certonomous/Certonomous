# Certonomous

An autonomous CFD laboratory. State an engineering objective in plain language;
the lab interprets it, forms a team of agents, runs **real OpenFOAM solves**, and
reports every result with a trust tier and a confidence envelope — bounding its
own trust rather than overclaiming.

This repository holds the lab's software, its research record, and its
self-verification apparatus. **Roughly 80 GB of output cannot live in a git
repository**; everything too large to commit is enumerated by exact location in
**[`LOCATIONS.md`](LOCATIONS.md)**, so nothing is invisible merely because it is
big.

---

## Where things are

| Section | Path | What it holds |
|---|---|---|
| **Closure challenge** | `demo-output/website/CLOSURE_*.md`, `closure_challenge_*`, `closure.html`, `benchmarks.*`, `wall/`, `closure_eval/`, `closure_challenge_submission_round*/` | The benchmark entry: status, submission drafts, evaluation protocol, per-case error decomposition, round-4 and round-5 packages |
| **Verification ladder** | `demo-output/website/campaign/` | Ladder V rungs V1–V16, every grading record, and the run archives (`F5_runs/`, `F8_runs/`) — 13,994 tracked files |
| **DAFoam** | `demo-output/website/dafoam/` | Adjoint optimisation work: `work_wing/`, `work_sail/`, NACA4412 families |
| **OpenFOAM cases** | `demo-output/website/tmr*/`, `unsteady-cylinder/`, `valve/`, `committee-grids/`, `mega-batch/`, `race*/`, `hlpw6/`, `optimization/` | Turbulence-model resource cases, canonical bodies, grid studies |
| **Charters and governance** | `docs/charters/`, `docs/standards/`, `docs/aws/` | The rules the lab is bound by, including the reporting and verification charters |
| **Docket** | `docs/DOCKET.md` | The lab's finding ledger — every open question, ruling and defect, append-only |
| **Lab software** | `sdk/`, `scripts/` | The chief-engineer server, mission workflows, and the self-audit / check apparatus |
| **Research notes** | `docs/`, `docs/papers/`, `docs/research/` | Operating notes, numerics knowledge, prior art |
| **Validation curriculum** | `models/curriculum/` | Parametric bodies and their experimental references |
| **Demo and filming** | `demo-output/plots/`, `gui-proof/`, `acts/`, `dist/`, `mission-output/` | The demo bundle, plots, and control-room evidence |

**Start here** if you are new: [`docs/USING_THIS_LAB.md`](docs/USING_THIS_LAB.md)
— every command in it was executed before it was written down.

---

## Principles

- **Real numbers only.** Every coefficient, field, and mesh count comes from an
  actual solve. Hardcode the path, never the result.
- **The lab bounds its own trust.** No result is called VALIDATED without an
  experimental comparison (ASME V&V 20). Everything else is TREND ONLY, and the
  reason is stated in measured terms.
- **Honest uncertainty.** Envelopes on every plotted quantity; a GP envelope is a
  floor, not a bound; a two-mesh probe is a "grid difference," not a verified
  numerical uncertainty.
- **A claim of absence needs a live control.** A sweep that finds nothing has two
  indistinguishable causes — nothing is there, or the search was broken. Only a
  planted control, confirmed by readback in the same run, separates them.
- **Durable records are not revised.** A withdrawn figure is struck and kept, so
  the record shows what was claimed and what replaced it.

---

## What it does

- **Geometry studies** — take any watertight STL/OBJ through surface check,
  meshing, a steady solve, and a force reported with its settling envelope.
- **A validation wall** — canonical bodies (sphere, cylinder, cube, Ahmed, NACA
  wings) graded against published experiment, each with its trust tier and, where
  the solve lands in a different regime than the reference, an explicit
  *reference regime mismatch* diagnosis.
- **Ask the lab** — record-grounded question answering over missions, the
  knowledge base, lessons, and the validation wall, with an optional LLM layer
  that reasons over the grounded facts (falls back to a deterministic listing
  with no key).
- **Aircraft L/D optimization** — search a wing design space against stated
  mission requirements (passengers, range, take-off/landing speeds), reported as
  a conceptual-design trade.
- **A sealed certificate** per mission — a one-page PDF with the result,
  envelope, trust tier, the three V&V channels, and a SHA-256 evidence seal.

---

## The verification apparatus

The lab checks itself, and the checks are part of the deliverable. `lab_check.py`
is the enumerated runner everything reports through; its exit contract is a
**severity ladder, not a taxonomy** — `{0: PASS, 1: FAIL, 2: FAIL, 3: UNKNOWN}`,
with 4 meaning a blocking UNKNOWN.

```bash
python3 scripts/lab_check.py          # the standing run
python3 scripts/self_audit.py         # the claim-surface audit
```

Individual guards live in `scripts/check_*.py`. Each states, in its own output,
the frame it can and cannot see — a check that cannot say what it failed to look
at is not trusted here.

---

## Running the lab

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

Optional LLM answer-synthesis reads `ANTHROPIC_API_KEY` from the environment
only — never committed. Without it, the lab answers deterministically from its
record.

## Tests

```bash
cd sdk && python -m unittest discover tests
```

---

## Reading the record

Three conventions will save a new reader time:

1. **Anchors, not paths.** Durable claims cite the commit that established them.
   A commit anchor stays true; a `file:line` locator is only true at the frame it
   was measured in, and several records carry locators that were correct when
   written and moved afterwards.
2. **Strike-and-keep.** `~~text~~`, `<s>` and LaTeX `\sout{}` mark a withdrawn
   claim that is deliberately still visible. **A PDF cannot be graded from its
   text layer** — a struck figure sits in the text stream exactly as a live one
   does, so PDFs must be rendered and read visually.
3. **Say which arm you swept.** The corpus has four (tracked, untracked,
   gitignored, run tree) and no single command reaches all of them. See
   [`LOCATIONS.md`](LOCATIONS.md) §5 for the reach limits, including the 26
   tracked files no `git grep` mode can reach.
