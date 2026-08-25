# F11 lid-driven cavity — CONVERSION RESULTS

**Verdict: `NOT A RESULT`, all six gate rows.**

Pre-registration frozen at `53298a45`; graded by `grade_f11.py` blob `01aa54d7`, verified
equal to its committed HEAD blob **before** it graded (rule 2). Run 2026-08-25, cfd.

## What was asked and what came back

The conversion re-runs the 2026-07-30 `GATE REACHED` record — which **had no
pre-registration at all**, so no band existed before the numbers did — against bands frozen
in advance. Six `simpleFoam` laminar solves: Re 100 and Re 1000 at n = 32 / 64 / 128.

**Every band verdict was `PASS`. Every row is nonetheless `NOT A RESULT`**, because the
Roache/plateau gate converted them: the `coarse` level (and `medium` on four of the six
rows) is **not iteratively converged or not plateaued**, so no grid claim can be made from
the triple. This is standing rule 5 operating in the only direction it is permitted to
operate — the gate may turn a PASS into `NOT A RESULT`, never the reverse.

| row | quantity | value | band | triple state | order | GCI | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G-F11-1 | Re 100 `u` @ (0.5, 0.9766) | 0.843419 | [0.80423, 0.87823] | CONVERGING | — | — | **NOT A RESULT** |
| G-F11-2 | Re 100 `v` @ (0.8047, 0.5) | −0.253229 | [−0.25343, −0.23723] | CONVERGING | — | — | **NOT A RESULT** |
| G-F11-3 | Re 100 `u` @ (0.5, 0.5) | −0.20874 | [−0.21361, −0.19801] | CONVERGING | 2.2178 | 0.2238 % | **NOT A RESULT** |
| G-F11-4 | Re 1000 `u` @ (0.5, 0.9766) | 0.663878 | [0.58028, 0.73828] | CONVERGING | 2.8432 | 0.0386 % | **NOT A RESULT** |
| G-F11-5 | Re 1000 `v` @ (0.9063, 0.5) | −0.524586 | [−0.536, −0.494] | CONVERGING | 2.2065 | 0.4286 % | **NOT A RESULT** |
| G-F11-6 | Re 1000 `u` @ (0.5, 0.5) | −0.0618216 | [−0.0748, −0.0468] | CONVERGING | 2.3495 | 0.5177 % | **NOT A RESULT** |

**The GCI figures above are printed because the triples are CONVERGING and monotone. They
do not rescue the rows** — the iterative-convergence limb fails first, and clause order in
rule 5 is not negotiable.

**Why `coarse` fails.** On G-F11-1 and G-F11-3 the coarse plateau is **UNMEASURED**, not
merely bad: no `centerlineSeries` sample exists at least 250 iterations before the converged
iteration 442 (the series on disk holds only `[250]`), so the criterion **cannot be
evaluated — and an unevaluated step is not a passed one.** On the Re 1000 rows the coarse
drift is 1.6e−04 to 4.8e−04 against a 1e−06 threshold, i.e. two to three orders out.

## What the run does NOT establish, stated because a band PASS invites the opposite reading

- **No grid-convergence claim.** That is the whole content of the verdict.
- **Two bands are WEAK BARS and the comparator says so on their face.** G-F11-4 carries
  `B_ref` at **72.2 %** of its half-width — most of the band is the *reference's* own
  resolution, not our mesh — and the comparator prints: *"a materially wrong solve could
  pass this band."* Four rows (G-F11-2, -4, -5) are **wider than the largest deviation
  anywhere in the 2026-07-30 record** (0.01734 lid-speed units), so they are not bars a real
  solve can fail. **The load-bearing content of those rows is the triple, the order and the
  GCI — not the band.**
- **Coverage matrix `P`: `BLOCKED`.** The Ghia, Ghia & Shin (1982) primary is **not on
  disk**, so rule 15's title-page verification cannot be performed. `V`: not earnable by
  this run.
- **Discrimination test: `UNMEASURABLE`, not satisfied** — the hypothesis has no runnable
  null arm, and the row is recorded unmeasured rather than quietly dropped.

## Instrument evidence

- **Selftest 98/98, of which 32 are MUTATION controls** — each proves the grade *changes*
  when the answer does. Value controls at 1e−12 against cases whose answers are known by
  construction, none against a key's mere presence.
- **54 planted-zero controls, all PASSED** (plant 0.001234, read back through the same
  parser that grades).
- **All six solves `rc = 0`, MEASURED** — an integer on disk via
  `setsid bash -c 'CMD; echo $? > RC.txt; sync'`. **No proxy was used or needed.** This is
  the carry-forward registered on F5b one run earlier, applied at the next opportunity.
- A **document defect is recorded, not repaired**: §7 states the per-run caps sum to
  1,296 s where its own six caps sum to 1,355.575 s. Immaterial — both are far above the
  780 s budget, so the clause's conclusion holds a fortiori.

## Cost

**6.0835 core-min actual against 8.0200 predicted (ratio 0.759) and a HARD CAP of 13.0
(0.468 of cap). Cap respected; `stopped_by: null`.** Cleaned == gross; nothing approaches
the 3600-s stall rule. **Waste: ZERO** — no kill, no wall-cap fire, no relaunch — named
separately and never absorbed into the ratio. Gap is **misprediction (over-prediction)**,
essentially in full; **contention is BOUNDED, NOT MEASURED** (loadavg 1.29 at launch, 6.37
terminal, rising because F5b and F3 ran concurrently, with no per-level decomposition to
separate it). **Dollars $0.0052 — DERIVED, NOT MEASURED.** Calibration row: **C-64**.

## Artifacts

`F11_CONVERSION_GRADE.json`, `F11_CONVERSION_RUN_LEDGER.json`, `RC.txt` (rc = 0),
`WATCH_TERMINAL.txt`, `runs/<rung>/<level>/`. Solver logs are gitignored and remain on disk.
