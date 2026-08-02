# W3 — replicate meshes at the three rungs the credentials wall publishes

**Meshed and solved 2026-08-02 06:12:51 → 06:18:48 UTC.** Follows
`W3_MESH_NOISE_FLOOR_RESULTS.md` §5, which concluded that the replicate to run
first belongs at the **coarsest** rung, not the finest — and the coarsest rung
that matters is the one a credential is printed from.

Serves `agp-d0b3c7cb6a58` (cube) and `agp-7273e7f80ddc` (NACA 0015 sail), and
adds a third body, the Ahmed 25°, because its row is on the same wall.

---

## 1. Method

For each body: two cases built from that body's own production case, one at the
stored background divisions (**A**, the control — it must reproduce the stored
cell count) and one perturbed (**B**). Everything else byte-identical. Both
solved at **4 MPI ranks**, scotch, so the pair shares a decomposition.

| body | A divisions | B divisions | A cells | B cells | cell Δ |
| --- | --- | --- | --- | --- | --- |
| Ahmed 25° | (60 13 36) | (61 12 37) | **79 439** ✓ | 77 389 | −2.58% |
| cube | (36 60 36) | (37 59 37) | **299 493** ✓ | 329 606 | +10.05% |
| NACA 0015 sail | (60 36 54) | (61 35 55) | **243 929** ✓ | 245 560 | +0.67% |

✓ = reproduces the stored production cell count exactly.

## 2. Results

| body | Cd (A) | Cd (B) | scatter | A's own iterative 2σ | scatter ÷ 2σ | published envelope | scatter ÷ envelope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ahmed 25° | 0.084802548 | 0.088579984 | 3.777 × 10⁻³ | 1.34 × 10⁻⁵ | **283×** | 2.022 × 10⁻² | **0.19×** |
| NACA 0015 sail | 0.010155910 | 0.009624541 | 5.314 × 10⁻⁴ | 3.83 × 10⁻⁶ | **139×** | 7.207 × 10⁻³ | **0.07×** |
| cube | 1.108388909 | 1.093505136 | 1.488 × 10⁻² | 1.469 × 10⁻² | **1.0×** | 7.822 × 10⁻³ | see §4 |

**Controls.** A reproduces the stored production Cd to 9.45 × 10⁻⁶ on the
Ahmed and 2.91 × 10⁻⁶ on the sail, across a change from 6 and 16 ranks to 4.
Both converged on `residualControl` — 155 and 139 iterations. The cube's
control does **not** reproduce, to 4.22 × 10⁻³, and §4 is about why.

## 3. Two rows come out well, and that is worth saying plainly

On the **Ahmed 25°** and the **NACA 0015 sail** the mesh-generation scatter is
283× and 139× each body's own iterative noise — so it is cleanly separable and
it is real — and it is **19% and 7% of the envelope those rows publish.**

Whatever else is wrong with publishing an envelope off a declined ladder — and
that is the open ruling `w3-a-declined-ladder-still-publishes-an-envelope` —
**those two envelopes are not too small for the mesh scatter underneath them.**
They are conservative against it by 5× and 14×. That is a real check that the
wall passed, and it is the first time it has been made.

The sail's margin should be read with its own record in view: its `band_rel`
is 0.70962, so the envelope is 71% of the value it decorates. An envelope that
large will contain almost anything. The Ahmed's 19% is the more meaningful
result of the two.

## 4. The cube, where the replicate found something else

**The cube's production run — the run the credentials wall publishes — never
converged, and neither did any re-solve of it.** No "SIMPLE solution
converged" message appears in the original
`/home/ubuntu/certonomous-runs/study-cube-2904cb/log.simpleFoam`, nor in
either of tonight's; all three ran to the fixed 300-iteration cap.

Final-20%-window statistics from each run's own `coefficient.dat`:

| run | ranks | cells | mean Cd | 2σ | as % of Cd | as % of the published ±0.0078 |
| --- | --- | --- | --- | --- | --- | --- |
| original production | 16 | 299 493 | 1.102404922 | 7.255 × 10⁻³ | 0.66% | **93%** |
| A, re-solve tonight | 4 | 299 493 | 1.108388909 | 1.469 × 10⁻² | 1.32% | **188%** |
| B, replicate mesh | 4 | 329 606 | 1.093505136 | 4.062 × 10⁻³ | 0.37% | 52% |

**So the cube's mesh-scatter number cannot be extracted from this experiment**,
because at 1.488 × 10⁻² it is the same size as run A's own iterative 2σ of
1.469 × 10⁻². That is stated as a failure to measure, not massaged into a
result.

**What the experiment found instead is worse than what it went looking for.**

* The **original** run behind the published credential has an unsettled
  final-window 2σ of **7.255 × 10⁻³**, which is **93% of the ±0.0078 envelope
  printed beside it.** That envelope is offered as a *discretization*
  uncertainty across a three-mesh study. Almost all of it could be accounted
  for by the single solve underneath it not having stopped moving.
* **The same mesh at a different rank count moves the answer by
  5.98 × 10⁻³** — 1.102404922 at 16 ranks against 1.108388909 at 4, on
  byte-identical geometry and dictionaries — which is **76% of the published
  envelope from decomposition alone.**
* Across the three runs the means span **1.488 × 10⁻²**, 1.90× the envelope.

**`agp-d0b3c7cb6a58` asked for a fourth rung on the cube's ladder. A fourth
rung cannot help a body whose third rung has not converged.** The cube's three
stored Cd values are 1.102982, 1.109239, 1.104172 — a total spread of
6.26 × 10⁻³ across a 5.6× change in cells, which is **smaller than the
iterative 2σ of the finest rung and smaller than what changing the rank count
does.** The ladder is reading its own noise.

This is the same defect `w3-run-uq-studies-still-caps-every-rung-at-300`
names, arriving on a third body: `run_uq_studies.ITERATIONS` is the constant
300 for the cube's 53 861-cell coarse rung and its 299 493-cell production
rung alike, and nothing checks whether either settled. `tmr_verification`
fixed exactly this on 2026-07-31 with `iteration_backstop(cells)` and a settle
criterion that drives the run; the curriculum runner never got it.

## 5. What should happen to the cube's row

Not decided here, and deliberately. Three facts are now on the record and the
decision belongs with the open envelope ruling:

1. the run behind the credential did not converge and says so nowhere;
2. its unsettled 2σ is 93% of the envelope it publishes;
3. changing only the rank count moves it 76% of that envelope.

The row should not be quietly retightened or quietly widened tonight. It
should be **re-solved under a settle criterion** — which is a cheap experiment,
about 6 core-minutes at 4 ranks per attempt on tonight's measurement — and the
envelope recomputed from rungs that stopped because they were done.

## 6. Cost

| stage | ranks | ExecutionTime | core-min |
| --- | --- | --- | --- |
| Ahmed 25° A + B | 4 | 43.49 s | 2.90 |
| cube A + B | 4 | 384.90 s | 25.66 |
| NACA 0015 sail A + B | 4 | 144.92 s | 9.66 |
| six meshes | 1 each, 3 concurrent | — | ≈8 |
| **total** | | | **≈46 core-minutes** |

Against `est_core_min` 20.0 each for the two items it serves. Over on the
cube, which took 25.7 core-minutes by itself because it is the one body here
that runs its full 300 iterations every time — which is the finding.
