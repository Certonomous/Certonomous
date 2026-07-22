# Certonomous

An autonomous CFD laboratory. State an engineering objective in plain language;
the lab interprets it, forms a team of agents, runs **real OpenFOAM solves**, and
reports every result with a trust tier and a confidence envelope — bounding its
own trust rather than overclaiming.

## Principles

- **Real numbers only.** Every coefficient, field, and mesh count comes from an
  actual solve. Hardcode the path, never the result.
- **The lab bounds its own trust.** No result is called VALIDATED without an
  experimental comparison (ASME V&V 20). Everything else is TREND ONLY, and the
  reason is stated in measured terms.
- **Honest uncertainty.** Envelopes on every plotted quantity; a GP envelope is a
  floor, not a bound; a two-mesh probe is a "grid difference," not a verified
  numerical uncertainty.

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

## Running it

Requires OpenFOAM reachable from the host (this project runs it via WSL). From
`sdk/`:

```bash
CHIEF_ADAPTER=openfoam \
OPENFOAM_RUN_PREFIX="wsl -d Ubuntu -- openfoam2606" \
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

## Layout

- `sdk/chief_engineer/` — the lab: server, OpenFOAM adapter, the lab model
  (trust tiers, compute ledger, V&V channels), certificate, Ask-the-lab.
- `sdk/workflows/` — the mission workflows (geometry study, optimization,
  time-constrained, uncertainty reduction, aircraft L/D).
- `models/curriculum/` — the validation ladder: parametric bodies and their
  experimental references.
- `docs/` — operating notes, numerics knowledge, and the demo runbook.
