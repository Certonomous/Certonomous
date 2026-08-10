# Certonomous — Closure Challenge submission package (round 5)

**This package is DRAFT and has not been sent. Submissions are parked.**

Written 2026-08-11 by Ladder V Pass 2, to discharge cold-reproduction defects
D1 (*"the package never says where the benchmark or the scorer is"*), D4
(*"every provenance pointer dangles on receipt"*) and D10 (*"the package does not
name itself"*). Pass 3 reproduced our score bit-for-bit but had to find the
benchmark and the scorer by filesystem search; a recipient would not have that
option. Everything needed to score this package from nothing is below.

## What is in the box

| file | what it is |
|---|---|
| `test/*.csv` | **the submission** — 8 files, one per test case, 1000 rows × 3 columns (`Ux, Uy, Uz`), comma-delimited, no header |
| `DESCRIPTION_DOCUMENT.md` | the disclosure document: method, prior art, every leakage disclosure, the score and what it is worth |
| `MANIFEST.json` | SHA-256 per file, the harness commits, and the pre-score verification record |
| `README.md` | this file |

Two fields in `DESCRIPTION_DOCUMENT.md` are marked `[KATIE TO FILL]` — the author
names and the reference URL. **No value has been invented for either.**

## How to score this package from scratch

Nothing below requires anything from the submitting lab's repository.

```
# 1. the benchmark dataset (evaluation points, meshes, ground truth, README/board)
git clone https://github.com/rmcconke/closure-challenge-benchmark
git -C closure-challenge-benchmark checkout deb91557184af3cb95f5190494ec52d8f2c6a0d1

# 2. the scorer -- a SEPARATE repository from the dataset. This distinction
#    matters: installing the wrong one, or a later commit of the right one,
#    scores you on a different metric (see the note below).
git clone https://github.com/rmcconke/closure-challenge
git -C closure-challenge checkout 1c4e22c8ac6b2e5f978ba6918f4f44b2db66d162
pip install -e closure-challenge

# 3. drop this package's test/ into the benchmark dataset and score it
python -c "import closure_challenge as cc; print(cc.score_from_csv('test'))"
```

Expected result, to full precision: **`0.056647191704213645`**.

Per case: `alpha_15_13929_4048` 0.0501 · `alpha_15_13929_2024` 0.1011 ·
`alpha_05_4071_4048` 0.0461 · `alpha_05_4071_2024` 0.0719 · `AR_1_Ret_360` 0.0455 ·
`AR_3_Ret_360` 0.0400 · `AR_14_Ret_180` 0.0353 · `NASA_2DWMH` 0.0632.

### Version note — read this before installing

The scorer's `__init__.py` reports `__version__ = "0.2.1"` while its
`pyproject.toml` at the pinned commit declares `0.3.1`, whose commit message
reads *"v0.3.1: vector magnitude metric, mean over cases"*. **The version string
is not the metric revision; the commit hash is.** Pin `1c4e22c8` — a `pip install`
of the package by name may resolve to a different metric and give a different
number for the identical CSVs.

## Integrity

Verify the eight files against `MANIFEST.json`:

```
cd test && sha256sum -c <(python - <<'EOF'
import json
m = json.load(open("../MANIFEST.json"))
for case, info in m["files"].items():
    print(f'{info["sha256"]}  {case}.csv')
EOF
)
```

All eight hashes were also frozen in a pre-registration
(commit `e865076b`) **before** the single scoring call that produced the number
above (commit `07a7fe9e`, 12m 59s later). Five of the eight are byte-identical to
our round-4 submission; three (the ducts) are new.

## What produced each file

- **3 duct cases** (`AR_1_Ret_360`, `AR_3_Ret_360`, `AR_14_Ret_180`) — converged
  forward solves of the **untrained** QCR2000 term (`kOmegaSSTQCR`, `Ccr1 = 0.3`,
  Spalart 2000's published constant, nothing fitted), nearest-neighbour
  interpolated to the benchmark's shipped evaluation points.
- **2 declined cases** (`alpha_05_4071_4048`, `alpha_05_4071_2024`) — **the
  supplied RANS field, unmodified.** A train-only gate declined to correct them.
  These are not our model's numbers.
- **3 corrected cases** (`alpha_15_13929_4048`, `alpha_15_13929_2024`,
  `NASA_2DWMH`) — a trained post-hoc velocity-field correction. **These three are
  the only rows an outside reader cannot re-derive from public inputs**, because
  they depend on a fitted model; the disclosure document says so and quantifies
  the seed uncertainty that follows from it.

Full account in `DESCRIPTION_DOCUMENT.md`.
