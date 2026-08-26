# T1b results: fully developed turbulent pipe against the disagreement between two correlations

Campaign T, tier 1, rung T1b, attempt 2. Written 2026-08-20, completed
2026-08-21 after the §6 extension reported. Run tree
`verification/runs/T-family/T1_runs/`, 19 cases.
Comparator `analyse_t1b.py`, frozen at commit `08732fd6` (2026-08-19 19:10:04 Z)
before any case solved (Charter §2d), verified byte-identical at analysis time:
sha256 `647d7412...`. Band read from `T1b_band.json`, committed before any case
directory existed. Attempt 1 was NOT A RESULT (D437, radial grading reversed,
`T1b_ATTEMPT1_MESH_FAULT.md`); nothing in it is graded here.

**Rung verdict: PASS, as returned by the frozen comparator, on all four Nu rows
— and every one of the four grid triples is DIVERGENT or STAGNANT, so none of
the four is a mesh-converged value; under the amendment candidate in section 8
all four rows read NOT A RESULT — 4 graded rows, 0 GATE FAIL, 0 NOT A RESULT.**
Analysed 2026-08-21 16:36 Z, after the §6 extension. Docket D440.

---

## 1. The rows

Reference at each `Re` is the midpoint of Dittus–Boelter and Gnielinski, the
band their half-spread. Station `80 D`, plateau check at 60/70/80 D (spread
below 0.2 x band). The value graded is the **finest** level of the three-level
ladder; the grid triple is computed beside it.

| row | `Re` | quantity | value | reference | band | deviation | grid triple | observed `p` | verdict |
| --- | ---: | --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| B0 | 1e4 | `Nu` | 31.619 | 30.907 | 2.84 % | 2.305 % | **DIVERGENT** | −0.219 | **PASS** |
| B1 | 1e4 | `f` | 0.03106 | 0.031480 | — | 1.34 % | — | — | REPORTED |
| B2 | 3e4 | `Nu` | 72.480 | 73.684 | 3.89 % | 1.635 % | **DIVERGENT** | −0.150 | **PASS** |
| B3 | 3e4 | `f` | 0.02290 | 0.023639 | — | 3.11 % | — | — | REPORTED |
| B4 | 1e5 | `Nu` | 185.771 | 190.398 | 5.33 % | 2.430 % | **DIVERGENT** | −0.059 | **PASS** |
| B5 | 1e5 | `f` | 0.01733 | 0.017992 | — | 3.69 % | — | — | REPORTED |
| B6 | 3e5 | `Nu` | 449.255 | 456.723 | 5.75 % | 1.635 % | **STAGNANT** | +0.010 | **PASS** |
| B7 | 3e5 | `f` | 0.01389 | 0.014435 | — | 3.77 % | — | — | REPORTED |

Row tags follow the comparator's counter: a NOT A RESULT `Nu` row consumes one
tag and emits no friction row, so the pre-extension output (§6.1) carried B0–B4.

| `Re` | coarse | medium | fine | `y+` c / m / f | station spread, fine |
| ---: | ---: | ---: | ---: | --- | ---: |
| 1e4 | 30.119 | 30.831 | 31.619 | 1.55 / 0.98 / 0.62 | 0.004 |
| 3e4 | 69.103 | 70.732 | 72.480 | 1.53 / 0.97 / 0.61 | 0.010 |
| 1e5 | 177.506 | 181.582 | 185.771 | 1.53 / 0.97 / 0.61 | 0.025 |
| 3e5 | 430.220 | 439.761 | 449.255 | 1.53 / 0.97 / 0.61 | 0.067 |

**A PASS here means consistent with the canon's midpoint to within the canon's
own disagreement. It is not verification to that tolerance** (T1 §3.2), and at
no `Re` is it a mesh-converged value (§8).

## 2. Friction and attribution

Friction is the attribution lever registered in T1 §3.3 and T1b_DESIGN §2: **a
friction error is a solver or mesh fault; a Nusselt error with correct friction
is the thermal closure.** It found attempt 1, where `Nu` and `f` failed
together by nearly the same amount at every `Re` (D437). It is measured from
the pressure drop between 50 D and 80 D and is independent of the thermal
field. Rows B1/B3/B5/B7 above: **`f` is BELOW Petukhov on every fine level, by
1.34 / 3.11 / 3.69 / 3.77 % at 1e4 / 3e4 / 1e5 / 3e5, the shortfall growing
with `Re`, and the friction triples are DIVERGENT (§8). By the attribution rule
this rung registered, a friction error is a solver or mesh fault: the thermal
closure is therefore NOT cleanly attributable here, because the momentum
solution is not itself grid-converged. The `P_*` cases return `f` identical to
their `R_*_f` partners to five figures at every `Re` (0.03106, 0.02290,
0.01733, 0.01389) while `Nu` differs by 7.4–10.0 %: `Pr_t` moves `Nu` and not
`f`, which is the separation the lever exists to make.**

The `P_*` cases return `f` = 0.03106 / 0.02290 / 0.01733 / 0.01389 at
1e4 / 3e4 / 1e5 / 3e5, each the same five figures as its `R_*_f` partner,
while their `Nu` differ by 7.38 / 8.50 / 9.40 / 10.02 %. Pre-extension only the
1e4 pair could be read (`R_10k_f` and `P_10k`, both 0.03106, `Nu` apart by
7.4 %); the extension added the other three and none broke the pattern: a
change to `Pr_t` alone moves `Nu` and leaves `f` where it is, which is exactly
the separation the lever is built to make.

## 3. The Prt discrimination (T1 §7.1)

Registered prediction: `Pr_t` 0.85 → 1.0 moves `Nu` by order 15 %, 2.6–5.3
times the band, and the rung must separate the two at every swept `Re` or it is
too blunt to grade a thermal closure.

| `Re` | `Nu`, Prt 0.85 (fine) | `Nu`, Prt 1.0 (`P_*`) | separation | band | verdict |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1e4 | 31.619 | 29.285 | 7.38 % | 2.84 % | **SEPARATED** |
| 3e4 | 72.480 | 66.317 | 8.50 % | 3.89 % | **SEPARATED** |
| 1e5 | 185.771 | 168.317 | 9.40 % | 5.33 % | **SEPARATED** |
| 3e5 | 449.255 | 404.261 | 10.02 % | 5.75 % | **SEPARATED** |

**SEPARATED at all four `Re`: 7.38 / 8.50 / 9.40 / 10.02 % against bands of
2.84 / 3.89 / 5.33 / 5.75 %, the separation growing with `Re`.** Pre-extension
only the `Re = 1e4` pair existed (31.619 vs 29.285, 7.38 % against 2.84 %) and
it has not moved. The shift is half to two-thirds of the registered order of
15 %; the prediction was an order-of-magnitude estimate from `Nu ~ 1/Pr_t`, and
the test it registers is separation against the band, not the size of the
shift.

## 4. The wall-treatment comparison

Registered prediction (T1b_DESIGN §1): the two wall treatments differ by MORE
than the armed band, in which case no "does OpenFOAM match Dittus–Boelter"
claim is meaningful without naming the wall treatment. The `alphaEff` factor
is read from the written `alphat` field, not assumed; a wall-function case
below `y+ = 30` is REPORTED, not graded (T1b_DESIGN §4.2).

| `Re` | `Nu`, resolved fine | `Nu`, wall function | `y+` achieved | `alphaEff` factor | difference | band | exceeds band | inside validity |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 1e5 | 185.771 | 157.561 | 48.1 | 2.559 | 15.19 % | 5.33 % | yes | yes (y+ 48.1) |
| 3e5 | 449.255 | 474.083 | 48.4 | 3.222 | 5.53 % | 5.75 % | no | yes (y+ 48.4) |

Prediction: **met at 1e5 and NOT met at 3e5. At 1e5 the wall-function arm is
15.19 % below the resolved value against a 5.33 % band (and 17.2 % below the
reference, which on its own would be a GATE FAIL); at 3e5 it is 5.53 % ABOVE
the resolved value against a 5.75 % band — inside it by 0.22 pp — and 3.8 %
above the reference. The sign flips between the two Reynolds numbers. Both
`y+` values (48.1, 48.4) are inside the wall function's validity, so both rows
are graded comparisons, not reports. The registered consequence applies at 1e5
and is unresolved at 3e5: a "does OpenFOAM match Dittus–Boelter" claim at 1e5
is meaningless without naming the wall treatment.**

**The arm does not exist at `Re` = 1e4 and 3e4, and that is arithmetic, not a
build failure** (T1b_DESIGN §4.1a). A `y+ = 50` first cell has height
`2·50·nu/u_tau`: against `R = 0.1 m` that is 3.19e-02 m at 1e4 (**31.9 % of
`R`, 3 cells across the radius**), 1.23e-02 m at 3e4 (12.3 %, 8 cells),
4.22e-03 m at 1e5 (4.2 %, 23 cells), 1.57e-03 m at 3e5 (1.6 %, 63 cells). At
`Re = 1e4` the first cell would be a third of the pipe; no tuning fixes it. The
comparison is two points and says nothing below 1e5.

## 5. The `C_lam` control

Charter §2c trivial baseline, registered before the rung was built: the same
case with turbulence off must FAIL the `Re = 1e4` row, because a row a laminar
solution passes grades nothing (D433).

| control | `Nu` | reference | deviation | band | must | verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `C_lam` | **6.636** | 30.907 | **78.5 %** | 2.84 % | FAIL | **MET (fails, as it must)** |

Iteratively converged (max `T` change 0.0 K, 18000 → 20000); independent of
the extension. Its `Nu` sits above the fully developed laminar 3.657 the design
quoted because at `Re·Pr = 7100` the laminar thermal entry `0.05·Re·Pr·D` is
355 D and 80 D is inside it. The control is asked only to fail; it fails by 4.7x.

## 6. Iterative convergence and the extension

The gate carried from T1c: **no grid claim from a triple containing a level
still moving between its last two checkpoints.** The instrument is the written
`T` field compared between the last two time directories, not the residual.

**6.1 Pre-extension state, analysed 2026-08-20 18:37 Z (`gate_t1b.json`,
endTime 20000 on every case).** Coarse and medium levels at every `Re`, `P_10k`
and `C_lam` were bit-identical or within 2e-09 K between 18000 and 20000
(`R_10k_f`: 1.8e-07 K, CONVERGED). The three other fine levels were not:

| case | max `T` change, 18000 → 20000 | state | consequence |
| --- | ---: | --- | --- |
| **R_30k_f** | **2.74e-03 K** | NOT_CONVERGED | row B2 **NOT A RESULT** |
| **R_100k_f** | **1.58e-03 K** | NOT_CONVERGED | row B3 **NOT A RESULT** |
| **R_300k_f** | **5.93e-04 K** | NOT_CONVERGED | row B4 **NOT A RESULT** |

Pre-extension rows, as the frozen comparator printed them at 18:37 Z:

| row | `Re` | value | deviation | band | grid triple | verdict |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| B0 | 1e4 | `Nu` **31.619** | 2.305 % | 2.844 % | **DIVERGENT, p = −0.219** (30.119 → 30.831 → 31.619) | **PASS** |
| B1 | 1e4 | `f` 0.03106 | 1.34 % | — | — | REPORTED |
| B2–B4 | 3e4, 1e5, 3e5 | — | — | — | — | NOT A RESULT, fine level not converged |

`P_30k`, `P_100k`, `P_300k`, `W_100k`, `W_300k` were never measured
pre-extension: the comparator leaves a `Re` block at its NOT A RESULT row.

**6.2 The extension — a disclosed continuation, not a new attempt.** Six cases
were resumed from 20000 by `run_one_ext1.sh`, each serial (nProcs 1), all six
started together at **18:44:52 Z, 2026-08-20**, solving from `latestTime` to a
raised `endTime`, appending to a new `log.solve.ext1` (`log.solve` untouched)
and writing `STATUS3.<case>` beside the original `STATUS2.<case>`. They ran
concurrently with one another, with the parabolic-inlet diagnostic (D441) and
with another team's training jobs on the same box; the wall column includes
that contention.

| case | endTime | first ext1 `Time` | max `T` change, last two checkpoints | state | extension wall |
| --- | ---: | ---: | ---: | --- | ---: |
| R_30k_f | 20000 → 40000 | 20001 | 0.0 K (38000 → 40000) | CONVERGED | 17 951 s |
| R_100k_f | 20000 → 58000 | 20001 | 0.0 K (56000 → 58000) | CONVERGED | 26 867 s |
| R_300k_f | 20000 → 68000 | 20001 | 0.0 K (66000 → 68000) | CONVERGED | 27 399 s |
| P_30k | 20000 → 30000 | 20001 | 0.0 K (28000 → 30000) | CONVERGED | 8 947 s |
| P_100k | 20000 → 50000 | 20001 | 0.0 K (48000 → 50000) | CONVERGED | 22 123 s |
| P_300k | 20000 → 60000 | 20001 | 0.0 K (58000 → 60000) | CONVERGED | 23 775 s |

The original `mark_done_t1b.py`, run first as the procedure required, reported
the six extended cases NOT DONE on test 5 alone ("20000 ExecutionTime lines,
expected 30000..68000"), tests 1–4 and 6 now passing; `mark_done_t1b_ext1.py`
reported 19/19. After extension all six fine levels are CONVERGED with 0.0 K
change between their last two checkpoints (`gate_t1b.json`,
`cases[*].iterative_convergence`, `max_change` 0.0, `relative` 0.0). The
extension therefore changed the `Nu` rows at 3e4, 1e5 and 3e5 — B2/B4/B6 in
the final numbering, B2–B4 pre-extension — from NOT A RESULT to graded rows,
and changed nothing at 1e4: B0, B1 and the 1e4 discrimination read today
exactly as they did at 18:37 Z on 2026-08-20.

**The decision to extend was taken before the comparator was re-run and is
independent of anything it could return.** The rule "no grid claim from a
triple with an unconverged level" was already in force; the extension gives it
more iterations to judge, nothing else. No `endTime` was chosen with a `Nu` in
view: the rows concerned had no `Nu`, only a NOT A RESULT. Band, reference,
station, comparator and hash are those of 08732fd6. Same class as T1c §3
(6000 → 30000 on the same measurement), disclosed under Charter §2d: added,
iterations; when, 18:44:52 Z; readable then, the tables above; resting on it,
B2–B7 and the Prt and wall-treatment comparisons at 3e4, 1e5, 3e5. B0, B1,
the 1e4 discrimination and `C_lam` do not.

## 7. The marking-tool amendment

The frozen comparator refuses unless `DONE.<case>` exists for all 19 cases.
Markers are written by `mark_done_t1b.py` under six tests: rc = 0; an `End`
line; last time = endTime; every needed field present; ExecutionTime count =
endTime; every field newer than the case's own `0/T` (the D438 stray-write
guard). **The original tool cannot judge an extended case and never retracts a
marker.** Test 5 counts `^ExecutionTime` lines in `log.solve` alone, which for
an extended case holds exactly 20000 lines for ever against an endTime of
30000–68000; and `main()` only writes markers, so the six `DONE` files written
when those cases met the rule at 20000 would have stood, certifying a
superseded state, and the comparator asks only whether the file exists.

`mark_done_t1b_ext1.py` applies the same six tests across both segments: STATUS2
and STATUS3 both rc = 0; `End` in both logs; last time = the raised endTime;
fields present; ExecutionTime(log.solve) + ExecutionTime(ext1) = endTime **and
the first `Time =` of ext1 is exactly 20001**; every field at endTime newer
than `0/T` **and newer than `STATUS2.<case>`**, the file that dated the end of
the original segment. An extended case that fails has any pre-existing marker
**removed**, reasons printed; a case without an ext1 log is judged by the
original tool, untouched. Written while all six extensions were running, before
any STATUS3 existed; dry-run at **20:26 Z** it removed the six stale markers,
leaving 13, so the frozen comparator correctly refused for as long as the
extensions ran. **An amendment to the marking tool, not to the grading path**
(Charter §2d): it cannot move a number; it decides only whether the comparator
may read a case at all, and only in the direction of refusing more.

## 8. A flaw in the frozen comparator: every row passes on a triple that is not converging

**`analyse_t1b.py` grades the fine-level `Nu` against the band and records the
grid triple beside it without gating on it.** Lines 189–197:

```python
g = T1C.gci(lv["c"]["Nu"], lv["m"]["Nu"], lv["f"]["Nu"])
val = lv["f"]["Nu"]
dev = 100.0 * abs(val - Rf) / Rf
bpct = 100.0 * Bd / Rf
verdict = "PASS" if dev <= bpct else "GATE FAIL"      # ... grid=g, verdict=verdict
```

`g["state"]` is stored and printed; the verdict does not read it. The only
gates ahead of it (lines 172–187) are iterative convergence and the station
plateau. `analyse_t1c.py`, from which this comparator imports `gci`, does gate
(lines 438–444):

```python
if conv["state"] != "CONVERGING":
    out["rows"].append(dict(..., verdict="NOT A RESULT",
                            why=f"grid triple is {conv['state']}; "
                                "no band can be armed"))
```

T1c's gate exists because its band IS the GCI: no converging triple, no band.
T1b's band comes from the correlations, so the comparator had a band
regardless, and the triple gate was not carried across. The omission is in the
frozen instrument and became visible only when every triple came back
DIVERGENT or STAGNANT under a passing fine value.

**What the four rows are, exactly.** The frozen comparator returns **PASS on
every `Nu` row** — 31.619 against 30.907 (2.305 % inside 2.844 %), 72.480
against 73.684 (1.635 % inside 3.885 %), 185.771 against 190.398 (2.430 %
inside 5.334 %), 449.255 against 456.723 (1.635 % inside 5.749 %) — and beside
each PASS a triple that is not converging: **30.119 → 30.831 → 31.619
(DIVERGENT, p = −0.219), 69.103 → 70.732 → 72.480 (DIVERGENT, p = −0.150),
177.506 → 181.582 → 185.771 (DIVERGENT, p = −0.059), 430.220 → 439.761 →
449.255 (STAGNANT, p = +0.010).** Every level is iteratively converged and
plateaued across the three stations; the triples are monotone. `Nu` rises by a
near-constant step per 1.6x refinement at every `Re` — **+0.71 / +0.79,
+1.63 / +1.75, +4.08 / +4.19, +9.54 / +9.49** — and the fine deviations
(**2.305 / 1.635 / 2.430 / 1.635 %**) are all smaller than the coarse-to-fine
drift (**4.98 / 4.89 / 4.66 / 4.42 %**), so each PASS is a statement about the
finest mesh built, not about a limit. The direction against the reference
differs: at 1e4 the triple moves **AWAY** from 30.907, the fine level already
above it (the coarse level was 2.55 % off, the medium 0.25 % off, the fine
2.31 % off on the other side); at 3e4, 1e5 and 3e5 it moves **TOWARD** the
reference from below and has not reached it (coarse 6.22 / 6.77 / 5.80 % off,
medium 4.01 / 4.63 / 3.71 %, fine 1.64 / 2.43 / 1.64 %). Whether a fourth
level would pass by less, pass by more or fail is not something any of the four
triples can say. **The rows are reported as the frozen comparator returns
them, with the divergence printed beside each; the verdict column is not
edited.**

**The friction triples are divergent in the same way.** `f` = 0.02960 /
0.03028 / 0.03106 at 1e4 (p = −0.307), 0.02181 / 0.02233 / 0.02290 at 3e4
(p = −0.233), 0.01652 / 0.01691 / 0.01733 at 1e5 (p = −0.132), 0.01327 /
0.01358 / 0.01389 at 3e5 (p = −0.057), every one DIVERGENT by the comparator's
own `gci`, and rising toward Petukhov by a near-constant step exactly as `Nu`
rises toward (or past) the midpoint. The first-cell `y+` runs 1.53 → 0.97 →
0.61 across the ladder, so the step is tied to the near-wall resolution of the
low-Re treatment rather than to an asymptotic range: what the three levels
measure is how far the `kOmegaSST` wall treatment has got into the viscous
sublayer, not where it ends up. **A fourth level at `y+` ≈ 0.38 is the
instrument the next rung needs, and it is proposed, not run.**

**Why it is not repaired now.** Charter §2b(2): after first compute the gate is
closed; a gate later found defective is a finding that lands as a dated
addendum and a docket entry, never as a quiet edit to the bar. §2d.1's repair
exception covers a repair that cannot change a number — a path that resolves
or refuses — and this one can: a gate that turns a PASS into NOT A RESULT moves
a verdict. It belongs before the next rung's first solve.

**Amendment candidate for the next rung's comparator (Charter §2b addendum,
dated 2026-08-20):** *a `Nu` row whose grid triple is not CONVERGING reports
NOT A RESULT, as T1c does; the fine value and the triple are printed beside
it.* Docket entry: D440. Under that rule rows B0, B2, B4 and B6 would all read
NOT A RESULT and the graded-row count would drop from four to zero.

## 9. What this rung cannot see

From the comparator's own docstring, and extended:

- **Whether either correlation is right.** The reference is their midpoint and
  the band their disagreement. Inside the band means consistent with the
  canon, not verified to that tolerance.
- **Nothing about the correlations' own accuracy** against experiment; the band
  is narrower than either correlation's quoted uncertainty at every `Re`, by
  construction.
- **Roughness, variable properties, entrance effects, buoyancy** — excluded by
  the design.
- **Anything at a Reynolds number where the wall-function arm was not built**:
  the wall-treatment finding is two points, 1e5 and 3e5.
- **A mesh-converged `Nu` at any `Re`.** Every triple is DIVERGENT or STAGNANT;
  at each of the four Reynolds numbers the rung reports a fine-mesh value and a
  direction, not a limit (§8).
- **Whether the thermal closure or the mesh is responsible for the 1.6–2.4 %
  `Nu` deviations**, because the friction rows — the attribution lever — are
  themselves off by 1.3–3.8 % and not grid-converged.
- **`Pr_t` at any value other than 0.85 and 1.0**, and aspect-ratio damage
  (up to 3189, T1b_DESIGN §4a) except through the observed order and the
  friction row.

## 10. Cost

`nProcs = 1` on every case; core-hours = wall seconds (STATUS2 + STATUS3) /
3600; 0.0513 USD per core-hour.

| segment | cases | wall, s | core-hours | USD |
| --- | ---: | ---: | ---: | ---: |
| attempt 2, original (endTime 20000) | 19 | 217 442 | 60.40 | 3.10 |
| extension ext1 | 6 | 127 062 | 35.30 | 1.81 |
| **attempt 2 total** | 19 | 344 504 | **95.70** | **4.91** |
| attempt 1, discarded (D437) | 19 | — | 56.6 | 2.90 |
| **T1b grand total including attempt 1** | — | — | **152.3** | **7.81** |

T1b grand total including attempt 1: 152.3 core-hours, 7.81 USD.

Original-segment wall, s: R_10k c/m/f 1804/6271/22900; R_30k 1904/6641/23533;
R_100k 1669/6156/22163; R_300k 1665/5783/20734; P_10k 22683, P_30k 23419,
P_100k 22237, P_300k 20890; W_100k 703, W_300k 2175; C_lam 4112. Extension wall
per case: §6.2 table. The six extensions, each serial, ran concurrently with
one another, with the parabolic-inlet diagnostic (D441) and with another team's
training jobs on the same box; their wall, and so the 35.30 core-hours billed
for them, includes that contention and is an upper bound on the solver time.

## 11. Rung verdict

**PASS, as returned by the frozen comparator, on all four Nu rows — and every
one of the four grid triples is DIVERGENT or STAGNANT, so none of the four is a
mesh-converged value; under the amendment candidate in section 8 all four rows
read NOT A RESULT — 4 graded `Nu` rows, 0 GATE FAIL, 0 NOT A RESULT; Prt
discrimination SEPARATED at all four `Re`: 7.38 / 8.50 / 9.40 / 10.02 % against
bands of 2.84 / 3.89 / 5.33 / 5.75 %, the separation growing with `Re`; wall
treatment differs from resolved by 15.19 % at 1e5 (exceeds the band) and
5.53 % at 3e5 (inside by 0.22 pp), opposite signs; `C_lam` MET; rows B0, B2,
B4 and B6 PASS on DIVERGENT or STAGNANT triples, reported as returned and
flagged in §8.**

---

## 12. Addendum 2026-08-26 — L4 extension (EXT2) graded `[lab-attributed]`

Dated addendum under the numbering of this file, the location
`T1b_L4_AMENDMENT.md` §7 registers for the L4 analysis sequence. **Lines whose
number changed above this section: 0.** Assembled 2026-08-26T16:11:10Z by a lab-lane on the
heat-transfer supervisor's brief. Pre-registration
`T1b_L4_EXT2_PREREGISTRATION.md` (HEAD blob `9d4beec4`); gates, bands and
labels are those of `T1b_L4_AMENDMENT.md` (`ad7208b5`) and `T1b_band.json`,
untouched. Graded artifact: `verification/runs/T-family/T1_runs/gate_t1b_L4.json`.

### 12.1 Freeze

`analyse_t1b_L4.py` blob `59c345bd` == HEAD; `mark_done_t1b_L4.py` `2055d35b`;
`mark_done_t1b_ext1.py` `eb607a2c`; `planted_zero_control_t1b.py` `16660281` —
all byte-identical to their committed blobs at grading time.
`scripts/check_comparator_freeze.py` (selftest rc=0; whole-tree verdict FAIL,
rc=3) reports `analyse_t1b_L4.py` **UNFROZEN**: its commit
2026-08-21T18:14:22Z postdates the first scoped marker `DONE.R_10k_c` (mtime
2026-08-21T16:35:58Z, MARKER-UNDATED, mtime basis), margin −5 904 s. This is the
standing finding already on record for the pool grade (§8, the 2026-08-25
ruling); the extension changes nothing about it and it is reported, not worked
around. The checker's refusal is a finding of this record.

### 12.2 Strict completion (rule 4, amendment §7 extended form)

`mark_done_t1b_L4.py`: 4/4 x-level cases PASS (3 with ext1 included);
`mark_done_t1b_ext1.py`: 19/19 PASS. Both instruments run without a `--help`
switch and executed on invocation; they rewrote `DONE.R_{10k,100k,300k}_x` at
16:00:23Z on this pass (`DONE.R_10k_x` text now reads "strict rule met,
extension ext1 included"). Clauses re-derived read-only:

| case | `STATUS` rc | `STATUS_ext1` rc / wall s | `End` orig / ext1 | ExecutionTime orig + ext1 = endTime | first ext1 Time | last time dir | fields (7) newer than `0/T` and `STATUS` |
|---|---:|---|---|---|---|---|---|
| `R_10k_x` | 0 | 0 / 52 469 | 1 / 1 | 20000 + 12000 = 32000 | 20001 | 32000 | yes (07:11:13Z vs 08-21 22:37:55Z, 08-23 03:19:42Z) |
| `R_100k_x` | 0 | 0 / 46 325 | 1 / 1 | 80000 + 14000 = 94000 | 80001 | 94000 | yes (05:28:50Z vs 08-21 21:28:41Z, 08-25 07:23:55Z) |
| `R_300k_x` | 0 | 0 / 70 388 | 1 / 1 | 80000 + 30000 = 110000 | 80001 | 110000 | yes (12:09:52Z vs 08-21 21:27:10Z, 08-24 20:11:05Z) |

No cap was reached (caps 1 100 / 1 300 / 2 750 core-min, timeouts 66 000 /
78 000 / 165 000 s; every wall below its timeout).

### 12.3 Planted-zero control (rule 3, external instrument)

`planted_zero_control_t1b.py` on `R_10k_x`, station 80 D, plant 1.234e-03 K:
**PASSED** — arm 1 (`analyse_t1c.iterative_convergence`) negative CONVERGED
between (30000, 32000) unmodified, positive recovered 1.234e-03 exactly and
flipped to NOT_CONVERGED; arm 2 (`analyse_t1b.measure`) negative delta 0.0,
positive moved Nu 32.2665 → 32.1385. Not a rung verdict.

### 12.4 Grade — frozen comparator `analyse_t1b_L4.py`, rc=0

| row | Re | Nu (c, m, f, x) | x state | reference ± band | deviation of x | (c,m,f) state, p | (m,f,x) state, p | GCI | verdict | guard |
|---|---|---|---|---|---|---|---|---|---|---|
| X0 | 1e4 | 30.119, 30.831, 31.619, 32.267 | **NOT_CONVERGED** | 30.907 ± 2.84 % | not computed (gated) | DIVERGENT, −0.219 | STAGNANT, +0.420 | n/a | **NOT A RESULT** | step (1) |
| X1 | 3e4 | 69.103, 70.732, 72.480, 73.904 | CONVERGED | 73.684 ± 3.885 % | 0.299 % | DIVERGENT, −0.150 | STAGNANT, +0.435 | n/a | **NOT A RESULT** | step (2) |
| X3 | 1e5 | 177.506, 181.582, 185.771, 189.207 | CONVERGED | 190.398 ± 5.334 % | 0.626 % | DIVERGENT, −0.059 | STAGNANT, +0.422 | n/a | **NOT A RESULT** | step (2) |
| X5 | 3e5 | 430.220, 439.761, 449.255, 457.078 | CONVERGED | 456.723 ± 5.749 % | 0.078 % | STAGNANT, +0.010 | STAGNANT, +0.412 | n/a | **NOT A RESULT** | step (2) |

Reported rows (never graded): X2 `f_x` 0.02338 vs Petukhov 0.02364 (1.08 %);
X4 0.01767 vs 0.01799 (1.77 %); X6 0.01415 vs 0.01444 (1.96 %); all (m,f,x)
STAGNANT. y+ at x: 0.392 / 0.388 / 0.387 / 0.386. Frozen (c,m,f) verdicts
beside, for the record: PASS at 2.305 / 1.635 / 2.430 / 1.635 % on DIVERGENT /
DIVERGENT / DIVERGENT / STAGNANT triples (§8 flaw, unchanged).
Summary line as printed: "0 graded rows: 0 GATE FAIL, 4 NOT A RESULT".

**What the extension changed:** `R_100k_x` and `R_300k_x` moved from
NOT_CONVERGED (step (1), 2026-08-25) to CONVERGED and now fall at step (2) on a
STAGNANT (m,f,x) triple; `R_10k_x` remains NOT_CONVERGED at 32000 (Nu moved
32.577 → 32.267); `R_30k_x` was not extended. **The board's `NOT A RESULT` × 4
stands. Zero graded rows, zero PASS, zero GATE FAIL, no GCI quotable.**

### 12.5 Predictions of amendment §3, scored

| Re | predicted Nu_x | actual | predicted f_x | actual | predicted y+_x | actual | grid prediction |
|---|---|---|---|---|---|---|---|
| 1e4 | 32.41 (outside band, away) | 32.267 (4.40 %, outside) | 0.03184 | 0.03171 | 0.38–0.39 | 0.392 | four NOT A RESULT — HELD |
| 3e4 | 74.23 (inside, crossed) | 73.904 (inside, crossed) | 0.02348 | 0.02338 | 0.38–0.39 | 0.388 | HELD |
| 1e5 | 189.96 (inside, below) | 189.207 (inside, below) | 0.01774 | 0.01767 | 0.38–0.39 | 0.387 | HELD |
| 3e5 | 458.75 (inside, crossed) | 457.078 (inside, crossed) | 0.01420 | 0.01415 | 0.38–0.39 | 0.386 | HELD |

Every registered prediction held in direction and landing; Nu_x within
0.16–0.44 % of the predicted number at every Re. Under §3's own reading this
is a statement about the ladder's direction, not about a limit.

### 12.6 Cost (rule 12)

Extension segment only, from `STATUS_ext1.<case>` wall × 1 rank ÷ 60:
`R_10k_x` 874.483 (POINT 1 073.6, ratio 0.815), `R_100k_x` 772.083 (671.0,
1.151), `R_300k_x` 1 173.133 (1 121.2, 1.046); **total 2 819.700 core-min
MEASURED against POINT 2 865.8 — ratio 0.9839**; against CEILING 5 071.5,
0.556; cap utilisation 79.5 / 59.4 / 42.7 %. **$2.4108 DERIVED, NOT
MEASURED** at $0.0513/core-h. Realised 4.372 / 3.309 / 2.346 s per iteration
against POINT 5.368 / 2.876 / 2.243. Contention, named: the arms ran beside up
to nine foreign solvers; the 04:14–04:35Z memory incident slowed each by
~1.19–1.22× (`T4_runs/MEMORY_INCIDENT_2026-08-26.md` §1; the supervisor's
brief quotes 1.24–1.30×). Waste 0.000 core-min — nothing re-run, no cap
crossed. Against the amendment's own §5 (registered endTimes, 205.4 core-h for
the whole level): not comparable segment-for-segment; the EXT2 §9 POINT is the
registered basis and is the one calibrated. All three walls exceed the §2
3600-s stall trigger mechanically; each ended on its registered `endTime` with
rc=0 and `End`, so cleaned is stated equal to gross with this departure named.
Calibration row: `docs/COST_CALIBRATION.md`.
