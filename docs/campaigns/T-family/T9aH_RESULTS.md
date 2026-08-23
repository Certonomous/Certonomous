# T9a-H results: the composite wall and fin re-graded under `Gauss harmonic`

Campaign T, tier 4, rung **T9aH**. Pre-registration
`docs/campaigns/T-family/T9aH_PREREGISTRATION.md`, §§1–10 frozen at
`0078fe9c25ac58e7ef1fda0cd97bab8884d4c5d2` (2026-08-23), addenda A.1–A.8 at
`1908bb7c` and `a66232c1`. Run tree
`verification/runs/T-family/T9aH_runs/`. Graded 2026-08-23.

**The grading path is SPLIT, exactly as §1 registered, and the two halves are
never merged.** Rows FR0–FR4 and controls C1–C3 are the output of the **frozen
T9a comparator, byte-identical**; rows H1–H6 and controls HC1–HC4 are the
output of the **new instrument** `analyse_t9aH.py`. Neither re-grades the
other. **No T9a number moved and no frozen file was edited.**

---

## 1. The rows — FROZEN path, FR0–FR4

`verification/runs/T-family/T9aH_runs/analyse_t9a.py`, sha256
`dd2d6bf0ac690fdcca90719cb6586168763d311ea3b5a7ad937fdf054ecac9da`, the byte
copy of the blob committed at `239ed2b8`. Output
`verification/runs/T-family/T9aH_runs/gate_t9a.json`. **Exit code 1.** Values
are the finest level; the three levels and the triple state are printed beside
each row, per §5.1.

| row | quantity | reference | c | m | f | triple | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| FR0 | wall `q″` [W/m²] | 19.5026820 | 19.50268162 | 19.50268162 | 19.50268162 | **OSCILLATORY** | **NOT A RESULT** |
| FR1 | wall `T` interface 1 [K] | 348.7810820 | 348.78108240 | 348.78108240 | 348.78108240 | **OSCILLATORY** | **NOT A RESULT** |
| FR2 | wall `T` interface 2 [K] | 300.0243780 | 300.02437835 | 300.02437835 | 300.02437835 | **DIVERGENT** | **NOT A RESULT** |
| FR3 | fin efficiency `η` | 0.8332367 | 0.83314553 | 0.83316576 | 0.83317371 | CONVERGING, order 1.9901780603156476 | **GATE REACHED** |
| FR4 | fin tip ratio | 0.7523781 | 0.75239885 | 0.75239616 | 0.75239511 | CONVERGING, order 1.996906346447679 | **GATE REACHED** |

FR0–FR2 arm **no band** — `gate_t9a.json` records `band_pct: null` and
`why: "grid triple is OSCILLATORY/DIVERGENT; no band can be armed"`. FR3's band
is 0.0007695579145997664 % and FR4's is 0.00011215531036092926 %, both below
the registered 0.025 % fin one-dimensionality floor, so both are **reported,
not graded** (deviations would have been 0.0076 % and 0.0023 %).

**§4.1 registered this outcome before the run, and it is unfavourable to this
rung's own hypothesis.** The registered prediction was: *"The most likely single
outcome is OSCILLATORY → NOT A RESULT"*, with FR3/FR4 GATE REACHED. That is
what the frozen rule returned. **The verdicts are published exactly as
returned. They are not re-labelled, softened or repaired**, and nothing in §2
below re-grades them.

**The order the frozen rule printed for FR2 (`-1.3757918549751695`) is the
frozen instrument's own output and is NOT adopted as a rung claim about
order.** §5.2's collapse floor (1.0e-06 K on wall temperature levels,
1.0e-06 relative on `q″`) fired on every wall triple — the three level errors
of §2 are 1e-11 K and below — so **the rung quotes no observed order, no
Richardson extrapolate and no GCI derived from any wall triple.** FR3/FR4's
orders are quoted because the fin level errors (~1e-4) sit far above that
floor.

## 2. The rows — NEW instrument, H1–H6

`verification/runs/T-family/T9aH_runs/analyse_t9aH.py`, sha256
`8107ed38578fcade0196c6458cb2e8e0f3d1af620c1a4d2c1dd444cea97f2870` (frozen in
Addendum A.2 before any case existed). Output
`verification/runs/T-family/T9aH_runs/gate_t9aH.json`. **Exit code 0.**
**This instrument arms no band and quotes no GCI.** Errors are absolute
distances from the full-precision closed form of §3, at **every** level.

| row | quantity | threshold | c | m | f | worst | verdict |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| **H1** | \|`T_i1` − 348.7810823988298\| [K], 400× | ≤ 1.0e-08 | 0.0 | 3.183231456205249e-12 | 2.9558577807620168e-12 | **3.18e-12 K** (m) | **PASS** |
| **H2** | \|`q″` − 19.502681618722573\|/`q″` , 400× | ≤ 1.0e-08 | 9.38570758890478e-12 | 6.434081711859108e-12 | 2.484899921384454e-11 | **2.48e-11** (f) | **PASS** |
| **H3** | \|`T_i2` − 300.0243783520234\| [K], 400× | ≤ 1.0e-08 | 5.684341886080802e-14 | 6.821210263296962e-13 | 1.8758328224066645e-12 | **1.88e-12 K** (f) | **PASS** |
| **H4** | `H40_f` (40×): \|`T_i1` − 340.0398406374502\| **and** drop | ≤ 1.0e-08 K **and** > 1.0e+06 | — | — | 2.5011104298755527e-12 K | drop **2.5986089707855840e+10** | **PASS** |
| **H5a** | `H4000_f` (4000×): \|`T_i1` − 349.8753179392549\| [K] | ≤ 1.0e-08 | — | — | 4.206412995699793e-12 | **4.21e-12 K** | **PASS** |
| **H5b** | `H4000_f`: \|`q″` − 1.9949129719216\|/`q″` | ≤ 1.0e-08 | — | — | 1.1406578348527318e-11 | **1.14e-11** | **PASS** |
| **H6** | fin `η` and tip ratio vs T9a published, all levels | ≤ 1.0e-09 | 0.0 | 0.0 | 0.0 | **0.0** | **PASS** |

Measured values: `T_i1` = 348.7810823988298 / 348.78108239882664 /
348.78108239882687 K at c/m/f; `q″` = 19.50268161890562 / 19.502681618848055 /
19.502681619207195 W/m²; `T_i2` = 300.02437835202346 / 300.0243783520241 /
300.0243783520253 K; `H40_f` `T_i1` = 340.0398406374477 K; `H4000_f` `T_i1` =
349.8753179392507 K and `q″` = 1.994912971898845 W/m². All from
`gate_t9aH.json` → `rows`.

**H4's drop clause was checked against the baseline read from
`T9a_runs/gate_t9aD.json`**, `e1(D_C_f)` = −64.99408 mK, **not re-solved**;
the measured drop is 2.60e+10 against the registered minimum of 1.0e+06.
Addendum A.4 disclosed before the run that the absolute bar, not the drop
clause, is the binding one at these numbers, and that is what happened.

**H6 is a specificity row, close to an identity, and counts toward nothing.**
`gate_t9aH.json` carries `counted_toward_hypothesis: false` on it. The fin
values under harmonic are **bit-identical** to T9a's published values — all six
deviations are exactly 0.0 — which is evidence about the build and about the
scheme doing nothing where it must do nothing, and is **not** evidence that
harmonic is correct. **Five rows, H1–H5, are counted toward the hypothesis.**

**The instrument's own summary, verbatim:**

```
  6 registered rows, 6 PASS, 0 GATE FAIL; 5 counted toward the hypothesis (H6 is a specificity row and counts toward nothing)
  4 controls, 0 NOT MET
  THIS INSTRUMENT ARMS NO BAND AND QUOTES NO GCI.  The frozen comparator's own verdicts (FR0-FR4, C1-C3) are whatever it printed, and are NOT re-graded here.
```

## 3. Controls

### 3.1 The frozen controls, and the registered consequence of a missing band

| control | measured | band | result |
| --- | ---: | ---: | --- |
| C1 arithmetic-mean conductivity | `q″` 19.5027 vs `k̄ΔT/L` 1650.9804 → deviation **98.81872118458483 %** | none armed | **NOT MET** |
| C2 perfect fin | `η` 0.833174 vs 1.0 → **16.68262943643002 %** | 0.0007695579145997664 % | **MET** (fails, as it must) |
| C3 uniform wall, solved | `q″` 100.000 %, `T_i1` 0.349 %, `T_i2` 16.657 % | none armed | **NOT MET** |
| C3 uniform fin, synthetic | `η` 100.000 %, tip 32.912 % | 0.0007695579145997664 % / 0.00011215531036092926 % | **MET** (both fail, as they must) |

**The frozen comparator's closing lines, reproduced verbatim as §4.1 registered
they would be, and NOT explained away:**

```
  5 registered rows: 0 PASS, 0 GATE FAIL, 3 NOT A RESULT, 2 GATE REACHED (reported, not graded)
  4 controls, 2 NOT MET -- the rung is unsound: C1_arithmetic_mean_conductivity, C3_uniform_wall_solved
```

**This is the mechanical consequence registered in advance at §4.1**:
`analyse_t9a.py:541` forms `c1_met = b0 is not None and c1_dev > b0`, and lines
570–575 do the same for C3-wall, so a wall row that arms no band makes C1 and
C3-wall `NOT MET` **whatever the deviation is** — and the deviations are
98.82 % and 100.000 %, i.e. the controls' substance fails exactly as it must.
**No frozen threshold was changed to avoid this.** The substance is re-graded
against absolute thresholds in §3.2.

### 3.2 The new controls, each of which MUST fail — all four MET

| control | realisation | must | measured | result |
| --- | --- | --- | ---: | --- |
| **HC1** wrong resistance rule | finest wall `q″` against `k̄ΔT/L` | FAIL H2's 1.0e-08 bar | fails it | **MET** |
| **HC2** perfect fin | finest `η` against `η` = 1 | FAIL H6's 1.0e-09 bar | fails it | **MET** |
| **HC3** trivial baseline (Charter §2c) | solved uniform solid `W_C3` through the identical pipeline | FAIL H1, H2 and H3 | fails all three | **MET** |
| **HC4** the hypothesis's null arm (Charter §2c) | **`RL_f`** — same mesh, same `k`, `Gauss linear` | FAIL H1, H2 and H3 | `H1` **−2.4091842789175644e-03 K**, `H2` **1.806464886613582e-02**, `H3` **−5.066098354404858e-04 K** | **MET** |

**HC4 is the discrimination test and it is what makes H1–H3 evidence.** The
null arm — the identical case with `Gauss linear` instead of `Gauss harmonic` —
misses H1's 1.0e-08 K bar by **2.41e+05 ×**, and `gate_t9aH.json` records
`rows_not_counted: []`: **the set of rows the hypothesis passes that its
absence also passes is empty.** The null arm's H1 error, −2.4091842789e-03 K,
reproduces T9a's published 2.41 mK miss, which is the quantity this rung exists
to remove.

## 4. The refusal channels, including the two planted zeros

Every channel §6 registered was armed and returned. **None refused**, and a
refusal would have been a finding, not an error to fix.

| channel | what it proves | reading |
| --- | --- | --- |
| **RC1** frozen-file hashes | the grading path is the frozen one | all eight files hash their §1/A.1 values; `T9a_runs/gate_t9a.json` still `7c4c6826…b3a5f4f8` and `gate_t9aD.json` still `96e0dce0…0dc19993`, i.e. **`T9a_runs/` was read-only and nothing moved** |
| **RC2** `fvSchemes` read back off disk | the scheme is not silently ignored | nine cases read `Gauss harmonic corrected`, `RL_f` reads `Gauss linear corrected` — the single registered change, verified from the case's own dictionary |
| **RC3** replica / builder as a controlled variable | the single-change claim is a measurement, not a statement about a new builder | `RL_f` reproduces the frozen `W_f` of `T9a_runs/gate_t9a.json` to **0.0 K on `T_i1`, 0.0 K on `T_i2`, 0.0 W/m² on `q″`** — bit-identical, against tolerances of 1e-9 K and 1e-7 W/m² |
| **RC4** strict completion rule | no case is graded that did not finish | all ten cases pass the six tests including the age guard |
| **RC5** planted convergence reader | a convergence zero is a reader that can see a non-zero | +1.234e-03 K planted into `900/T` of scratch copies of `W_f` and `H40_f`: the frozen `iterative_convergence` returns `max_change` **1.2340000000108375e-03 K** and state **NOT_CONVERGED** on both |
| **RC6** planted **measurement** reader — the load-bearing one | the near-zero H-row errors are evidence | +1.234e-03 K into the cell adjacent to interface 1 of a scratch copy of `W_f` (cell 25, x = 0.04903846153846154 m) moves `T_i1` from 348.78108239882687 K to 348.78225871413395 K, a shift of **1.1763153070774024e-03 K** against a registered floor of 1.0e-05 K |

**RC6 is the channel this rung actually needs.** Its headline is a set of
zeros; the floor it had to clear is **1000× above H1's own 1.0e-08 K
threshold**, so the reader that reported 3.18e-12 K is demonstrably a reader
that could have seen a failure. **Both plants were made on scratch copies
outside the run tree; no case directory was touched.**

## 5. Iterative convergence and heat balance

From `gate_t9a.json` → `iterative_convergence` and `cases[*].heat_balance_closure`:

| case | state | relative (900 → 1000) | heat-balance closure |
| --- | --- | ---: | ---: |
| `W_c` | CONVERGED | 0.0 | 1.865e-11 |
| `W_m` | CONVERGED | 0.0 | 6.036e-12 |
| `W_f` | CONVERGED | 0.0 | 4.361e-11 |
| `W_C3` | **NOT_CONVERGED** | 0.3695652173913043 | 1.922e+00 |
| `F_c` | CONVERGED | 1.33e-12 | 4.262e-11 |
| `F_m` | CONVERGED | 1.80e-11 | 8.394e-11 |
| `F_f` | CONVERGED | 2.75e-12 | 3.660e-11 |

**`W_C3`'s NOT_CONVERGED is reproduced from T9a and is not new here.**
`T9a_runs/gate_t9a.json` publishes the identical state for the identical case
(relative 0.9090909090909091). The cause is arithmetic, not physical: a uniform
350 K solid has `field_range` 5.229594535194337e-12 K, so a `max_change` of
1.9326762412674725e-12 K divides to 0.370 against a 1e-6 tolerance. **It is
reported, not repaired, and no threshold was moved for it.** `W_C3` feeds only
the C3 and HC3 controls; both returned the verdicts registered for them.

## 6. Mesh

`check_t9a_mesh.py` (byte-identical, sha256 `cb7fa05a…c86688bc`) over the seven
frozen cases: **rc = 0, `ALL MESHES VERIFIED`**, refinement ratios read from the
meshes 1.600/1.600/1.600 (`W_c`→`W_m`), 1.625/1.594/1.625 (`W_m`→`W_f`),
1.600/1.600 and 1.600/1.625 for the fin, against a nominal 1.6.

`check_t9aH_mesh.py` over `RL_f`, `H40_f`, `H4000_f`: **rc = 0, `ALL EXTRA
T9aH MESHES VERIFIED`** — 26/51/13 cells per layer, uniformity spread ≤ 6.7e-13,
**90/90 cells carrying the registered `k` of their layer** at each contrast,
`0/T` hot 350.0 K cold 300.0 K, with the layer-`k` map overridden in memory and
its restoration asserted. Every geometric constant read from
`constant/polyMesh/points`.

**`check_t9aH_mesh.py` has still not been read by the supervisor** (Addendum
A.8). Its output is therefore **provenance, not evidence**. It grades nothing —
it is a Charter §2c GUARD whose failure withdraws the run, never the hypothesis
— and no row above depends on it.

OpenFOAM `checkMesh` ran inside the per-case wrapper **before every solve**:
`checkMesh_rc=0` in all ten `STATUS.*` files.

## 7. Provenance, the freeze and the grading path

| artifact | sha256 / state |
| --- | --- |
| `docs/campaigns/T-family/T9aH_PREREGISTRATION.md` | worktree byte-identical to HEAD, `d28f8970eb3835c82ddeff3ba555ccf5f243903efb1ca577993b0154c08ff4af`; §§1–10 frozen at `0078fe9c` |
| `T9aH_runs/analyse_t9a.py` | `dd2d6bf0…4ecac9da`, blob at `239ed2b8` |
| `T9aH_runs/exact_t9a.py` | `d3f2558c…d017d3d0b8`, blob at `239ed2b8` |
| `T9aH_runs/T9a_registered.json` | `66b03c7d…1edb40ed`, blob at `239ed2b8` |
| `T9aH_runs/check_t9a_mesh.py` | `cb7fa05a…c86688bc` |
| `T9aH_runs/mark_done_t9a.py` | `0feff87e…6a7da669` |
| `T9aH_runs/run_one_t9a.sh` | `163c4345…5f8f2761` |
| `T9aH_runs/run_chain_t9a.sh` | `cbf3b957…34999e7d` |
| `T9aH_runs/build_t9a.py` | `516fee58…4e9a2659e9` |
| `T9aH_runs/analyse_t9aH.py` | `8107ed38…a97f2870`, frozen in A.2 before any case existed |
| `T9aH_runs/build_t9aH.py` | `c7a742f2…787104a4` |
| `T9aH_runs/run_chain_t9aH.sh` | `77c58025…9eac39aade` |
| `T9aH_runs/T9aH_registered.json` | `2a5ee67c…def30151b8` |
| `T9a_runs/gate_t9a.json` | `7c4c6826…b3a5f4f8`, **unmoved** |
| `T9a_runs/gate_t9aD.json` | `96e0dce0…0dc19993`, **unmoved** |

All thirteen instruments were verified byte-identical to their HEAD blobs
before any of them was run. The two transcriptions of §4 — `T9aH_registered.json`
and `analyse_t9aH.py`'s hard-coded `REGH_CODE` — agreed at the run; the
instrument refuses rather than grades on any disagreement.

The exact references were re-derived at the comparator run by the frozen
`exact_t9a.py` along both independent routes and agreed: 400× `q″`
19.502681618722573 W/m², `T_i1` 348.7810823988298 K, `T_i2` 300.0243783520234 K;
40× 159.3625498007968 / 340.0398406374502 / 300.199203187251; 4000×
1.9949129719216 / 349.8753179392549 / 300.0024936412149. All from
`gate_t9aH.json` → `exact_references`, and identical to §3 of the
pre-registration, which was written before any case existed.

Timeline, from artifact mtimes in the run tree:

| step | when (UTC) |
| --- | --- |
| ten case directories written by `build_t9aH.py` | 2026-08-23T20:12:18.060–.064 |
| `blockMesh` ×10 | 20:13:03.725 → 20:13:05.971 |
| chain 1, the seven frozen cases | 20:13:54.114 → `CHAIN_DONE` 20:14:04.132 |
| chain 2, `RL_f` `H40_f` `H4000_f` | 20:14:04.367 → `CHAIN_DONE_H` 20:14:05.264 |
| **launching lane died here** | between 20:14:05 and 20:36 |
| `mark_done_t9a.py` | 20:37:07 |
| `check_t9a_mesh.py`, `check_t9aH_mesh.py` | 20:38:12 → 20:38:15 |
| `analyse_t9a.py` (frozen) | 20:38:23 → 20:38:27 |
| `analyse_t9aH.py` (new) | 20:38:53 → 20:38:54 |

## 8. Disclosures — the lane handover, an ordering divergence, and one finding off the grading path

**8.1 The launching lane died between chain completion and marking (2026-08-23).**
Both chains finished at 20:14:04Z and 20:14:05Z with `CHAIN_DONE`,
`CHAIN_DONE_H` and ten `STATUS.*` files all reporting `rc=0`. Nothing further
had been run: no `DONE.*` marker, no mesh-verifier output, neither comparator,
and no file in the tree was newer than `CHAIN_DONE_H`. **This lane — same
supervisor authority, fresh session — completed the registered remainder of
§9 step 5 and nothing else.** It rebuilt nothing, re-ran no chain, re-solved no
case, and touched no other lane's process. Every instrument it ran was verified
byte-identical to its HEAD blob **before** it was run, and the pre-registration
was verified byte-identical to HEAD. **No gate, threshold, band, cap, reference
or label was touched, and none could be: they were frozen before any case
existed.**

**8.2 Ordering divergence, disclosed and not repaired.** §9 step 5 registers the
order *"build, `blockMesh`, mesh check, the two serial chains, markers, both
comparators."* The two **Python geometry verifiers** had not been run when the
launching lane died, so this lane ran them **after** the chains rather than
before. Both returned rc = 0 (§6). The OpenFOAM `checkMesh` that the wrapper
runs **did** execute before every solve (`checkMesh_rc=0` in all ten
`STATUS.*`), so no case was solved on an unchecked mesh; what ran late is the
registered geometry verifier, which **grades nothing** and is a Charter §2c
GUARD. **It is disclosed here rather than absorbed**, and it changes no verdict:
had either verifier failed, the RUN would have been withdrawn, not the
hypothesis.

**8.3 A staged deletion in the shared git index, inspected and NOT reverted.**
`git diff HEAD --stat` reports `T9aH_runs/check_t9aH_mesh.py` as a 60-line
deletion. The cause is a staged deletion (`D `) in the **shared** index, not a
change on disk: the worktree file hashes
`5c45eb9c89f49d954e2876ef64c762a7cfbaf7d474cd2b8c9bb15d1f2608db4d`, **identical
to its HEAD blob** from `a66232c1`. `T9aH_PREREGISTRATION.md` shows the same
`MM` pattern with its worktree likewise identical to HEAD. The index is
somebody's unfinished work and the chief's call; **it was inspected, never
reverted, and no staged entry was touched.** This record was committed by the
private-index protocol, which reads from HEAD and is therefore immune to it.

**8.4 Not measured.** The wall time of `build_t9aH.py`'s own process was not
recorded by the launching lane and cannot be recovered; only the 4 ms span of
its file writes is on disk. The `blockMesh` figure in §9 is the mtime span from
the first `log.blockMesh` to the last and therefore **excludes the first
invocation's own runtime**. Both are stated as bounds, not measurements.

## 9. Cost, actual against registered

**Unit: core-minutes (wall s × ranks ÷ 60).** `nProcs` 1 on every case, both
chains serial, peak occupancy **1 core of 16**. Four other lanes'
`buoyantBoussinesqSimpleFoam` processes (pids 442445, 450274, 488219, 757934)
were running on this box throughout and were **not touched**; the wall figures
therefore include contention and are **gross**, which is stated rather than
absorbed.

| item | how measured | core-s |
| --- | --- | ---: |
| `build_t9aH.py` case writes | mtime span, 20:12:18.060→.064 (process wall not recorded — see §8.4) | 0.004 |
| `blockMesh` ×10 | `log.blockMesh` mtime span (lower bound, §8.4) | 2.246 |
| chain 1, seven frozen cases | `W_c/0/T` → `CHAIN_DONE` | 10.018 |
| chain 2, three extra cases | `RL_f/0/T` → `CHAIN_DONE_H` | 0.897 |
| `mark_done_t9a.py` | timed at the call | 0.038 |
| `check_t9a_mesh.py` | timed at the call | 1.953 |
| `check_t9aH_mesh.py` | timed at the call | 0.841 |
| `analyse_t9a.py` (frozen comparator) | timed at the call | 3.831 |
| `analyse_t9aH.py` (new instrument) | timed at the call | 1.594 |
| **TOTAL, gross** | | **21.422 core-s = 0.357 core-min = $3.053e-04** |

| | core-s | core-min | $ |
| --- | ---: | ---: | ---: |
| registered prediction (§8) | ≤ 90 | 1.50 | 1.28e-03 |
| **registered CAP (§8)** | **300** | **5.00** | **4.28e-03** |
| **actual, gross** | **21.422** | **0.357** | **3.053e-04** |

**No overrun. 7.1 % of the cap and 23.8 % of the prediction.** The registered
chain-wall-clock line — the figure T9a-D's lesson said to register — predicted
12.5 core-s for the two chains; the measured chains are **10.915 core-s**. The
solver-only sum across the ten `STATUS.*` files is **8.52 core-s**, the largest
row being `F_f` at 5.89 s. **No row exceeded 3600 wall s, so no row is a
stall.**

**Rate: c7a.4xlarge at $0.0513/core-h. `cost_basis`: reported-by-owner, NOT
measured** — the box cannot read its own billing
(`COMPUTE_BUDGET_CHARTER.md` §5). Every dollar figure above is owner-stated and
is not a measurement.

## 10. What this rung cannot show — §7, unchanged

- **It does not make T9a pass and did not try.** T9a's GATE FAIL on R1 stands
  exactly as its frozen comparator returned it. No T9a number moved; both T9a
  gate files still hash what §6.1 registered.
- **It does not establish `Gauss harmonic` is correct for a conjugate rung.** It
  establishes exactness for **piecewise-constant `k` with the interface on a
  mesh face, on a 1-D orthogonal mesh, with fixed-temperature boundaries**, at
  contrasts 40×, 400× and 4000×. T9b's coupled interface, non-orthogonal meshes,
  graded or temperature-dependent `k`, and contact resistance are all outside it.
- **It does not show harmonic is safe to adopt everywhere.** Nothing here
  measures it on any advective term, on any turbulent thermal diffusivity, or on
  any quantity beyond this wall's `q″`, `T_i1`, `T_i2` and the fin's two rows.
- **It measures no fluid, no turbulence model and no thermal closure.** Both
  fluids are boundary conditions.
- **It does not rescue the GCI band.** It steps around it by grading absolute
  distances from an exact reference, which is available **only because this is
  an EXACT-tier rung** and is not a method a rung with a merely experimental
  reference can borrow.
- **H6 is a specificity row, close to an identity, and supports nothing.**
- **It produces no fidelity chip.** The rows grade a solver's discretisation
  against closed-form theory, not physics against the world.

## 11. Rung verdict

**Split by grading path, as §1 registered. The two are reported side by side and
are never merged.**

**FROZEN path — `analyse_t9a.py`, byte-identical, exit 1.**
**FR0 NOT A RESULT. FR1 NOT A RESULT. FR2 NOT A RESULT. FR3 GATE REACHED.
FR4 GATE REACHED.** Four frozen controls, two NOT MET, and the comparator's own
line — *"the rung is unsound: C1_arithmetic_mean_conductivity,
C3_uniform_wall_solved"* — is reproduced in §3.1 verbatim. **This is exactly the
outcome §4.1 registered before the run**, for the reason it registered: under an
exact scheme the differences a Roache band is built from are round-off, so the
frozen rule can arm no band and no wall row can come back PASS.

**NEW instrument — `analyse_t9aH.py`, exit 0.**
**H1 PASS. H2 PASS. H3 PASS. H4 PASS. H5 PASS. H6 PASS (specificity, counted
toward nothing).** **Five rows counted toward the hypothesis.** Four controls,
all MET — each failed as it must — and the null arm misses H1's bar by
2.41e+05 ×, so `rows_not_counted` is empty and the discrimination is real.

**What the rung measured, stated once and plainly:** under
`laplacian(DT,T) Gauss harmonic corrected`, the composite wall reproduces the
full-precision closed form to **3.18e-12 K** at worst on `T_i1`, **2.48e-11**
relative on `q″` and **1.88e-12 K** on `T_i2`, **at every level including the
35-cell coarse mesh**, and at contrasts **40×, 400× and 4000×** — against a
threshold of 1.0e-08 fixed before any case existed, which is 3 333× above the
largest residual T9a-D had measured and 240 918× below the 2.41 mK the rung
exists to remove. The identical case under `Gauss linear` misses that threshold
by five orders of magnitude. **The 2.41 mK T9a interface miss is removed by the
interface scheme, on this geometry and within the limits of §10, and by
nothing else.**

---

**Supervisor close-out note, dated 2026-08-23 (appended after the grade landed
at `359cccfb`).** Addendum A.8's outstanding condition is CLOSED:
`check_t9aH_mesh.py` was read in full, as source, by the T-family supervisor.
Ruled SOUND: the in-memory layer-k override deep-copies both frozen modules'
REG layer lists before mutation, restores them in `finally`, and asserts the
restoration on both; the frozen `T9a_registered.json` is never edited; the
file grades nothing (Charter §2c guard — its failure withdraws the run, never
the hypothesis) and discloses its one `postProcess -func writeCellCentres`
invocation rather than folding it into "zero compute". Its rc=0 output
(`ALL EXTRA T9aH MESHES VERIFIED`) is promoted from provenance to evidence.
§8.2's ordering divergence is reviewed and ACCEPTED: the two Python geometry
verifiers ran after the chains because the launching lane died at
2026-08-23T20:14:05Z before running them; they grade nothing, and
`checkMesh_rc=0` stands in all ten `STATUS.*` files, so no case was solved on
an unchecked mesh. Lines whose number changed above this section: 0.
