# T3. Heated backward-facing step against Vogel and Eaton 1985: pre-registration

Campaign T, rung T3 (a HARD rung, `T_FAMILY_INDEX.md` section 2). Written
2026-08-21, **before any case directory existed** (checked: `ls
verification/runs/T-family/T3_runs/` held only `T3_CONTRACT.md` and this
rung's scripts at the time of the commit that carries this file; no
`constant/polyMesh` and no time directory anywhere under it). Run tree
`verification/runs/T-family/T3_runs/`. Machine contract `T3_CONTRACT.md` in
the run tree; comparator `analyse_t3.py`, frozen in the same commit.

**Status of the reference, stated first because it decides what this rung can
be: the primary is NOT OBTAINED. The gate rows of this rung are BLOCKED by
construction until it is held, and nothing below pretends otherwise. The
feasibility and physics stages run now; the gate stage cannot.**

---

## 1. The rung in one paragraph

Air at `Re_H = 28 000` separates over a single-sided backward-facing step of
expansion ratio 1.25 and reattaches about `6.7 H` downstream; the wall behind
the step carries a constant heat flux. The quantity the literature grades is
the local Stanton number `St(x/H)` on that wall, which peaks a little upstream
of reattachment and recovers slowly toward a flat-plate value. It is the first
thermal rung in this lab with **separated flow**, and it is the entry to T4 and
T5. What the rung can test, once its reference is held, is whether a steady
`kOmegaSST` solution with a resolved thermal wall reproduces the measured
Stanton distribution **at the grid limit** — not on the finest mesh built
(T1b, D440). What it can test today, without the reference, is everything
about the solution except its agreement with experiment.

## 2. The reference: `NOT OBTAINED`, in the four fields Charter 6b requires

**What is missing.** Vogel, J. C. and Eaton, J. K. (1985), *Combined Heat
Transfer and Fluid Dynamic Measurements Downstream of a Backward-Facing Step*,
ASME J. Heat Transfer 107(4), 922–929, DOI 10.1115/1.3247522: the full text,
its `St(x/H)` data (table or figure), and **the authors' stated measurement
uncertainty on `St`**, which is the only band this rung may arm (an
experiment's band is its stated uncertainty; T1's two-correlation mechanism
does not apply because no correlation describes a reattaching flow). The
companion report, Vogel and Eaton, Stanford Thermosciences Division Report
MD-44 (August 1984, 191 pp., NSF grant MEA-81-08189), would serve equally.

**Which rows it blocks.** G1–G4 of section 7 (peak `St`, its location, `St`
at `x/H = 10` and `20`). It does not block the momentum row M1, the
discrimination rows, the controls, the grid ladder, the heat balance or the
cost science, all of which are measured and reported in this rung regardless.

**Why it was not obtained, with the checks named and dated (all 2026-08-21
unless stated).** Unpaywall on the DOI: `is_oa: false`, no OA location
(2026-08-17, K0d record). Semantic Scholar graph API on the DOI:
`openAccessPdf.status = CLOSED`, 409 citations. ERCOFTAC Classic Collection
(`cfd.mace.manchester.ac.uk/ercoftac`, reached over plain HTTP; HTTPS refuses
connections): the backward-facing-step holdings are case030 Driver and
Seegmiller 1985, case031 Le and Moin 1992 DNS, case053 Makiola and Ruck 1992,
case056 Tsai and Yang 1994 — **none heated; Vogel and Eaton is not held.**
NASA NTRS API: 49 backward-facing-step records, no Vogel, no Eaton, no heated
step (the MD series was NSF-funded, not NASA). Stanford SearchWorks: MD-44 is
a physical holding at SAL3 with no PURL and no digital copy. OSTI: the 1983
conference abstract only. DTIC: bot-walled to every tool here. CORE, Google
Books, HathiTrust, the Stanford group pages: nothing. A whole-issue scan on a
file-sharing site exists and **was not downloaded or used**. Two sub-agents,
about forty minutes of search in total.

**The acquisition path, with its price.** (i) ASME Digital Collection
single-article purchase of DOI 10.1115/1.3247522 — list price to be read at
checkout; historically a pay-per-view article from this publisher has been of
the order of 25–40 USD, and **that figure is recollection, not a quotation**.
(ii) Stanford Libraries scan-on-demand or inter-library loan of MD-44 (191
pages; fee unknown; days to weeks). (iii) Any institutional subscription to
the ASME journals that a member of the lab holds. **Each is a spend or an
access decision outside the compute authorisation, and it goes to Sanaa as a
decision, not an assumption.** The file this comparator will read when the
primary is held is `T3_runs/T3_reference_primary.json`; its schema is in
section 7.3 and it does not exist today.

### 2.1 What IS held: an open secondary, and exactly what it is allowed to do

Smirnov, Smirnovsky, Schur, Zaitsev and Smirnov (2016), *Numerical simulation
of turbulent heat transfer past a backward-facing step: 2D/3D RANS versus
IDDES solutions*, J. Phys.: Conf. Ser. 745, 032016, DOI
10.1088/1742-6596/745/3/032016, CC-BY 3.0. Title and author list verified by
the supervisor from the printed pages 1–2 of the PDF (L-144) — both retrieval
sub-agents had reported a wrong author list, one also a wrong title — sha256
`020a09f14c638a8f6b5dbcb3830f3af03274c904b78b01f078bde0885cb1b237`. Its
section 2 states the experimental conditions verbatim and its Figure 9 plots
the Vogel and Eaton `St` and `C_f` symbols against `x/H` from 0 to 20.

**It states no experimental uncertainty, no step height in metres, no
tabulated values.** It is therefore a **SECONDARY referent**, handled as
Charter 6b's table handles F5a and F7: the held artifact is a digitisation
(`T3_runs/T3_secondary_digitisation.json`, committed before any case exists,
with its symbol-radius increment recorded), and **every comparison against it
is REPORTED, never graded.** No verdict in this rung rests on it. It exists so
that the physics stage can say how far the solution sits from the best
available reproduction of the data, with the provenance on its face, and so
that the comparator's reporting path is exercised before the primary arrives.
**A reader who sees a T3 number "against experiment" in this rung is seeing a
secondary digitisation and the record says so at every row.**

### 2.2 The conditions this design reproduces, and where each comes from

| item | value | source |
| --- | --- | --- |
| `Re_H` | "approximately 28,000", on `H` and the core velocity at `x = -3.3 H` | secondary, section 2, verbatim |
| upstream channel height | `4 H`; expansion ratio 1.25 | secondary |
| aspect ratio | 11.4 (span / `H`); side-wall layers removed by suction 12 H upstream | secondary — justifies a 2D design, see section 10 |
| boundary layer at `x = -3.8 H` | about `1.07 H` on both the step wall and the upper wall | secondary |
| fluid | air, `Pr = 0.71` | secondary |
| heating | constant flux on the lower wall downstream of the step, `q_w = 270 W m-2`; all other walls adiabatic | secondary |
| `St`, `C_f` definition | on the core velocity at `x = -3.3 H` and the inlet temperature | secondary, section 4 |
| reattachment | `x_R / H = 6.67` | Jardine, Iacovides, Craft and Cioncolini, UKHTC 2021 P-2-1, Table 1, attributed to Vogel and Eaton; secondary |
| `H` in metres | 0.038 m | **a scale choice of this design**; the recollected 38 mm is not from any held source and the solution in Boussinesq form with `beta = 0` depends only on `Re_H`, `Pr` and the geometry ratios |

## 3. The design, with the reason for each decision

**Solver and equations.** `buoyantBoussinesqSimpleFoam`, `g = (0 0 0)`,
`beta = 0`: the lab's forced-convection-with-temperature solver
(`NUMERICS_KNOWLEDGE.md`, K0c C1 precedent; T1b, T1c). Temperature is a
passive scalar; the magnitude of the wall flux cannot move `St`, so the
gradient is set to a round `1.0e4 K/m` (about `10 K` of wall rise at
`St ~ 0.003`) rather than to the experiment's `270 W m-2`, and the
Boussinesq-validity question of `NUMERICS_KNOWLEDGE` does not arise.

**Closure and wall treatment.** `kOmegaSST`, wall-resolved, first-cell-centre
`y+` targets 1.6 / 1.0 / 0.625 across the ladder, the same three targets as
T1b so that the two rungs' grid behaviour is comparable. **T1b measured that
the wall treatment moves `Nu` by 15 % at `Re = 1e5`** and that its ladder's
drift tracked the near-wall resolution of the low-Re treatment; this rung
inherits both findings and builds one wall-function arm (`W_m`) beside the
resolved ladder so the difference is measured rather than assumed.
`Pr_t = 0.85` everywhere except the `P_m` arm (1.0); never tuned.

**Inlet.** A **uniform** inlet at `x = -48 H`, `U_in = 10.35 m/s`,
`I = 2 %`, `omega` from `l = 0.07 x 4H`. The boundary layer then grows
naturally along the 4H channel; the power-law estimate
`delta = 0.37 x Re_x^-0.2` gives `1.06 H` at `x = -3.8 H`, against the
experiment's 1.07 H. **Why not a prescribed profile at `-3.8 H`:** a
hand-written `k`/`omega` profile is an assumption the comparator cannot
check, and a precursor channel solve is a second case whose own convergence
and mapping would need their own guards; a single mesh whose inlet layer is
**measured** (`delta_99 / H` at `-3.8 H`, reported per case) is the cheaper
and more legible instrument. The core velocity at `-3.3 H` is likewise
**measured**, not set: the displacement of two 1.07 H layers in a 4H channel
accelerates the core by about 7 %, so `U_in` is chosen below `11.05 m/s` and
the achieved `Re_H` is a reported number with a registered tolerance (section
8). `St` and `C_f` are formed with the **measured** `U_ref`, as the
experiment defines them.

**Outlet.** `x = +30 H`, ten step heights beyond the last station, with a
`45 H` arm (`O_m`) to measure outlet independence (section 4).

**Mesh.** Three blocks (upstream `[-48H, 0] x [H, 5H]`, lower downstream
`[0, 30H] x [0, H]`, upper downstream `[0, 30H] x [H, 5H]`), blockMesh,
two-sided geometric grading to every wall and to the step lip with **the
reciprocal written by hand for the second half of each direction** (the
K0cS form; L-142), first `x` cell `0.03 H` at the step on both sides. Counts
per level (coarse / medium / fine): upstream `100 / 160 / 256` by
`80 / 128 / 204`; downstream `200 / 320 / 512` by `60 / 96 / 154` (lower) and
`80 / 128 / 204` (upper). Design totals **36 000 / 92 160 / 235 520** cells;
effective refinement ratios from the totals `1.600` and `1.599`, and the
comparator computes them from `constant/polyMesh/owner`, never from this
paragraph. First wall cells `1.1213e-4 / 7.0083e-5 / 4.3802e-5 m` from
`2 y+ nu / u_tau`, `u_tau = U_ref sqrt(C_f / 2)`, `C_f = 0.003`, and the
**achieved** `y+` is read from the solution on every heated-wall face.
**Every mesh is read from `constant/polyMesh/points` before any solve**
(`check_t3_mesh.py`, section 9): the heated-wall cell must equal the design
value AND be the smallest wall-normal cell in its block, the step `x` cell
must be the smallest on its side, the cells must sum to the block heights,
and each graded half must be geometric to `1e-6`. T1b attempt 1 lost 57
core-hours to a grading direction nobody read from disk; this rung reads it.

**Cases (8, all serial, all 2D).** `R_c`, `R_m`, `R_f` the ladder; `P_m`
(`Pr_t = 1.0`); `C_lam_m` (laminar, the Charter 2c baseline); `W_m` (wall
functions, first cell `2.10e-3 m`, `y+` about 30 where the flow is
attached, wall-normal counts 16 / 48 — the contract's first-written 40 / 96
could not fill the blocks at a ratio of one or more with that wall cell, and
the builder refused rather than invert the grading; amended before any case
existed); `D_m` (upstream length `10 H`, a deliberately thin inlet layer,
predicted `delta_99 / H` about 0.30); `O_m` (outlet at `45 H`). Every
non-ladder arm sits on the medium level so that each comparison is like
against like.

## 4. Stations, chosen by a development analysis and not by convenience (L-141; T1c's station lesson)

Four things were checked before a station was named, and each is a number
that contains no solved quantity.

1. **Bulk temperature rise against wall rise.** With constant flux the bulk
   rises linearly: at `x = 20 H`, `dT_bulk / (T_w - T_in) = 5 St_mean` about
   `0.014` for `St_mean` about 0.0028. The experiment's reference
   temperature is the **inlet** temperature, so `St` as defined already
   carries this 1.4 % and the design reproduces the definition rather than
   correcting it; the comparator reports the ratio per case. It is not a
   saturation problem — the driving difference does not decay — but it is
   the closest analogue of T1c's check and it is written down.
2. **The corner region `x/H < 1.5` is excluded from graded stations.** The
   secondary's own 3D RANS shows side-wall effects confined to `0 < x/H <
   1.5` and 2D/3D `St` differing by about 4 % there; the corner eddy
   (positive `C_f` for `x/H < 1`) is the least 2D and least steady part of
   the flow. Stations begin at `x/H = 2` for profile reporting and the peak
   is searched for at `x/H >= 1.5`.
3. **Outlet independence is measured, not assumed.** `O_m` moves the outlet
   from `30 H` to `45 H` on the medium mesh. **Registered criterion: if
   `St(20 H)` differs between `R_m` and `O_m` by more than 1.0 %, row G4
   (`St` at `20 H`) is NOT A RESULT.** The 1 % is a fixed number chosen now
   because no band exists yet to scale it; when the primary arrives the
   criterion will be restated as a fraction of the band by addendum and the
   stricter of the two applies.
4. **Inlet development is measured.** `delta_99 / H` at `x = -3.8 H` on the
   floor and the top wall, and `U_ref` at `-3.3 H`, are read from every case.
   **Registered tolerance: `delta_99 / H` within `[0.80, 1.35]` and
   `Re_H,achieved` within `[26 600, 29 400]` (±5 %) on the ladder cases**,
   else the thermal rows carry a flag "inlet condition outside the registered
   window" and are REPORTED, not graded, when the primary arrives. `D_m` is
   outside by design and is a discrimination arm, not a ladder member.

Graded quantities and why these four: **G1** the peak `St` (the number every
RANS study of this flow reports); **G2** its location `x_peak / H` (the
thermal analogue of reattachment, independent of the `St` magnitude);
**G3** `St` at `x/H = 10` (early recovery, where closures disagree most);
**G4** `St` at `x/H = 20` (late recovery, the station closest to a
flat-plate state and the one most exposed to the outlet). Profile values at
`x/H = 2 … 20` are reported for the record. The momentum lever **M1** is
`x_R / H` from the last negative-to-positive crossing of the wall shear
(ignoring `x/H < 0.5`), REPORTED beside the thermal rows as T1b reported
friction: **a momentum error is a mesh or solver fault; a Stanton error with
correct momentum is the thermal closure.**

## 5. Convergence, durability, and what is NOT the criterion

`endTime 20000`, `deltaT 1`, `writeInterval 2000`, `purgeWrite 2`:
`writeInterval` is strictly less than `endTime` because that line is a
durability property (L-140) and because the convergence gate needs two
checkpoints. **`residualControl` is not written.** Not because this is a
wedge — it is not — but because in both prior rungs the residual was not the
instrument (T1c: a genuinely unconverged case at residual `4e-05`; L-141),
and the test that worked is the one used here: **the written `T` field
compared between the last two checkpoints; any ladder level still moving is
NOT CONVERGED and no grid claim is made from a triple containing it.** The
zero is verified by a live planted control (`1.234e-03 K` written to a copy
and read back from disk) before the comparator reads anything. A case that
has not converged at 20 000 may be **extended** from `latestTime` under the
T1b section 6 disclosure rule (new log, new STATUS, first extension `Time`
exactly `endTime + 1`, marker re-judged across both segments); the decision
to extend is taken on the convergence state alone and never with a `St` in
view.

The laminar control at `Re_H = 28 000` may never reach a steady state. That
is anticipated: it is run to `endTime`, its state is reported, and if it is
NOT CONVERGED the discrimination row it serves is UNMEASURED, not satisfied
(Charter 2c, boundary clause 1).

## 6. Heat-balance closure: a GUARD on every case

Kinematic units (W per `rho c_p`), face areas from `points`/`faces`. `Q_wall`
= sum over heated-wall faces of `alpha_eff (dT/dn) A`, with `alpha_eff = nu /
Pr + alphat_w` and `alphat_w` **read from the written patch** (T1b: dropping
it reports only the molecular part on a wall-function wall). `Q_adv` = sum
over inlet and outlet faces of `phi_f (T_f - T_in)` from the written `phi`;
boundary conduction at inlet and outlet from the face-to-cell gradient.
Closure residual `(Q_wall - Q_adv - Q_cond) / Q_wall`, reported beside
`imbalance % = 100 |sum Q| / sum (Q > 0)` against the governed `0.5 %`
(`physics_rules.yaml`), with mass in/out and the outlet bulk rise. The inlet
is at `300 K` against a datum of `300 K`, so the inlet advective term is
identically zero **by the definition of the datum** — this is the open-case
shape where the ratio is well defined because the outlet term carries the
whole wall input; the datum sensitivity is reported through the mass
imbalance. It is a GUARD row under Charter 2c: it withdraws the run, never
the hypothesis, and is counted in no tally.

## 7. Rows, verdicts, and the rule that is new in this rung

### 7.1 The triple gate is binding

**A graded row whose grid triple is not CONVERGING returns NOT A RESULT with
the fine value and the triple printed beside it. It cannot return PASS.**
This is D440's amendment candidate made binding before this rung's first
solve, as T1b section 8 said it must be: T1b's frozen comparator returned
four PASSes on four DIVERGENT or STAGNANT triples because it graded the finest
mesh and stored the triple without reading it. `analyse_t3.py` reads it
first. The order of evaluation for every graded row: (1) any ladder level
NOT CONVERGED → NOT A RESULT; (2) triple not CONVERGING → NOT A RESULT; (3)
no primary reference file → **BLOCKED**, with the fine value, triple, GCI
and the deviation from the secondary digitisation printed as REPORTED
information; (4) primary held → PASS if the fine value lies within the stated
uncertainty of the reference value, else GATE FAIL. The `--selftest` mode
proves each branch on synthetic triples, including that a DIVERGENT,
STAGNANT or OSCILLATORY triple with a value **inside** the band still returns
NOT A RESULT, and that with a CONVERGING triple the verdict is reachable both
ways by moving the fine value (the mutation control).

Observed order and GCI (`Fs = 1.25`) use the **effective** ratios from the
cell counts with the unequal-ratio fixed-point form; the comparator asserts
that it reproduces T1c's `gci()` when the ratios are equal.

### 7.2 The rows

| row | quantity | kind | verdict today | verdict when the primary is held |
| --- | --- | --- | --- | --- |
| G1 | `St_peak`, fine level | GRADE | BLOCKED (or NOT A RESULT by 7.1) | PASS / GATE FAIL / NOT A RESULT |
| G2 | `x_peak / H` | GRADE | BLOCKED (or NOT A RESULT) | as G1 |
| G3 | `St(10 H)` | GRADE | BLOCKED (or NOT A RESULT) | as G1 |
| G4 | `St(20 H)` | GRADE | BLOCKED (or NOT A RESULT); NOT A RESULT if the `O_m` criterion fails | as G1 |
| M1 | `x_R / H` | lever | REPORTED with triple | REPORTED |
| DP | `Pr_t` 0.85 vs 1.0, `St_peak` and `St(10 H)` | discrimination | SEPARATED / NOT SEPARATED against the provisional floor 3 %, labelled PROVISIONAL | against the band |
| DC | laminar baseline vs `R_m`, `St_peak` | Charter 2c | MET if it differs by more than 25 %; UNMEASURED if `C_lam_m` is not converged | same |
| DW | wall functions vs resolved, `St_peak`, `St(10 H)`, `St(20 H)`; achieved `y+` and the fraction of faces below 30 | comparison | REPORTED | REPORTED |
| DD | thin inlet layer: `delta_99 / H`, `St_peak` shift | comparison | REPORTED against the registered direction | REPORTED |
| DO | outlet: `St(20 H)`, `x_R` vs `R_m` | guard for G4 | 1 % criterion | restated as a band fraction by addendum |
| HB | heat balance, every case | GUARD | REPORTED against 0.5 % | REPORTED |

**The `N of M` tally of this rung is `0 of 4` graded rows until the primary
is held, and that is the honest count.** A rung with no graded row is not a
capability (index section 4).

### 7.3 The reference slot

`T3_runs/T3_reference_primary.json`, absent today:

```
{"provenance": {"citation": "...", "page_or_table": "...", "sha256": "...",
                "title_verified_page1": true, "digitised": false},
 "rows": {"G1": {"value": 0.0, "uncertainty": 0.0, "units": "St"},
          "G2": {"value": 0.0, "uncertainty": 0.0, "units": "x/H"},
          "G3": {"value": 0.0, "uncertainty": 0.0, "units": "St"},
          "G4": {"value": 0.0, "uncertainty": 0.0, "units": "St"}}}
```

The `uncertainty` is the authors' stated figure, in the units of the row; if
the numbers had to be digitised from the primary's figure, `digitised` is
true and the comparator adds the digitisation increment in quadrature. **The
person who fills this file reads it from the printed page (L-144) and writes
the page number.** Nothing in `analyse_t3.py` changes when it appears.

## 8. Registered predictions, written before any solve

These are order-of-magnitude statements whose purpose is to be wrong in a
recorded direction, as T1b section 7.1 was.

1. **`x_R / H` on the fine SST level between 6.0 and 7.5.** Two-equation
   models on this expansion ratio reattach near 6.5–7.2; the experiment's
   6.67 sits inside. Outside that window the momentum lever points at the
   mesh or the inlet before anything thermal is read.
2. **`St_peak` on the fine level within ±15 % of the secondary's digitised
   peak, and `x_peak / H` within ±1.0 of its digitised location.** A larger
   miss is reported as a finding about the setup (inlet layer, 2D-ness,
   closure), not hidden; it grades nothing either way.
3. **`Pr_t` 0.85 → 1.0 moves `St_peak` and `St(10 H)` by 8–12 %**, the T1b
   shift at the same `Re` range (7.4–10.0 %). If it moves them by less than
   the provisional 3 % floor, the rung cannot discriminate a thermal closure
   and says so.
4. **The laminar baseline reads `St_peak` at least 25 % below the SST value,
   or does not converge.** A laminar solution that lands within 25 % of the
   turbulent one makes G1 a row that grades nothing (D433, D411).
5. **The wall-function arm differs from the resolved medium level by more
   than 5 % at `St_peak`** (T1b: 15 % at `1e5`), and a substantial fraction
   of its heated-wall faces sit below `y+ = 30` in the recirculation, where
   the wall function is outside its own validity; that fraction is printed.
6. **The thin-layer arm `D_m` has a higher `St_peak` than `R_m`** — the
   experiment's own finding that a thinner layer at separation raises the
   peak — and a shorter `x_R`.
7. **`delta_99 / H` at `-3.8 H` on the ladder between 0.95 and 1.20**
   (power law 1.06); `Re_H` achieved within ±5 % of 28 000.
8. **The triples.** Honest statement: T1b's `Nu` triples were DIVERGENT or
   STAGNANT at the same `y+` targets because the low-Re wall treatment's
   near-wall behaviour was still changing between 1.6 and 0.625. **The
   prediction is that at least one of G1–G4 comes back not CONVERGING**, in
   which case that row is NOT A RESULT under 7.1 and the record says which.
   A fourth level is proposed in that event, not run.

## 9. Build, verification and launch discipline

- `build_t3.py` writes the eight cases; `check_t3_mesh.py` reads every
  `points` file and refuses on A–F of the contract **before any solver
  runs**; its planted-positive test (an inverted grading) must FIRE.
- `checkMesh` birth certificate per case (Charter 9); high aspect ratio on
  resolved meshes is expected and reported with its number, not hidden.
- Launch via `launch_t3.sh` (atomic `LAUNCH_LOCK`; refusal if any process
  has the case as cwd, identified by `readlink /proc/pid/exe`; refusal if
  any numeric time directory other than `0` exists — L-143) and
  `run_one_t3.sh` detached with `setsid nohup`; **nothing in this rung kills
  a process and nothing needs to**: every case runs to `endTime` and writes
  `STATUS.<case>`.
- Completion: `mark_done_t3.py`'s six tests, including the age guard (every
  final-time field newer than the case's own `0/T`, written at the start of
  the run allowed to produce the answer). The comparator refuses without all
  eight markers.
- Concurrency cap 6 solver processes (the box is shared with the DAFoam and
  closure teams; DAFoam held cores 0–3 at design time).
- **Tooling disclosure.** Before this file was committed, the builder
  sub-agent ran a 200-iteration smoke test of `R_c` **in scratch, outside the
  run tree**, to confirm the dictionaries are accepted, the listed fields are
  written and the post-processing calls execute. Its fields were deleted;
  its numbers are not results and were not read as such. It is disclosed
  here because Charter 2d asks what was readable before the freeze: nothing
  a verdict depends on.

## 10. Cost, predicted

Planning throughput `4.0e5` cell-iterations per core-second (the honest 2D
turbulent figure in `NUMERICS_KNOWLEDGE` is `4.8e5`, and cases above 100 k
cells run about 19 % slower, so `4.0e5` is used for every case), `endTime
20000`, `nProcs 1`, `0.0513 USD` per core-hour.

| case | design cells | predicted core-s | core-h | USD |
| --- | ---: | ---: | ---: | ---: |
| R_c | 36 000 | 1 800 | 0.50 | 0.026 |
| R_m | 92 160 | 4 608 | 1.28 | 0.066 |
| R_f | 235 520 | 11 776 | 3.27 | 0.168 |
| P_m | 92 160 | 4 608 | 1.28 | 0.066 |
| C_lam_m | 92 160 | 4 608 | 1.28 | 0.066 |
| W_m | 28 160 | 1 408 | 0.39 | 0.020 |
| D_m | 79 360 | 3 968 | 1.10 | 0.057 |
| O_m | 128 000 | 6 400 | 1.78 | 0.091 |
| **total** | | **39 176** | **10.88** | **0.56** |

Predicted wall: with six concurrent and a shared box, `R_f` sets the
critical path at **3.3 h uncontended, up to about 5 h contended**; the whole
rung inside one working day. **Measured before the freeze, in the scratch
smoke test (section 9): `1.94e5` cell-iterations per second on `R_c` under a
host load average of 12–13 on 16 cores, half the planning figure.** At that
rate `R_f` takes about 6.7 h and the rung about 1.5 working days; both
figures are registered and the measured wall is printed beside them. The pre-authorised ceiling is 25 USD (487
core-hours); this design uses **2.3 % of it**, and an extension of every case
to 60 000 iterations would still be under 2 USD. Measured wall per case is
read from `STATUS.<case>` and printed beside the prediction.

## 11. What this rung cannot see

- **Agreement with the experiment.** Until the primary is held every thermal
  row is BLOCKED; the deviations printed against the secondary digitisation
  are reported with the digitisation's provenance and increment, and are not
  verdicts.
- **Whether the experiment's `St` data were taken at exactly `Re_H = 28 000`
  and `delta / H = 1.07`.** The primary reports Stanton profiles "as a
  function of Reynolds number and boundary-layer thickness at separation"
  (its abstract); the secondary plots one set at "approximately 28,000". The
  Manchester secondary mentions a heat-transfer run at a channel-height
  Reynolds number of 52 000 (`Re_H` about 13 000). Which run the digitised
  symbols represent is **a question only the primary answers**.
- **Three-dimensionality.** A 2D design on an aspect ratio of 11.4 with
  side-wall suction; the secondary's 3D RANS puts the 2D/3D difference at
  about 4 % in the recirculation and less downstream. This rung cannot
  measure it.
- **Unsteadiness.** A steady RANS of a flow whose shear layer flaps; the
  iterative-convergence gate reports a limit cycle as NOT CONVERGED and the
  rung then says so rather than averaging.
- **Any closure other than `kOmegaSST`**, and `Pr_t` at any value other than
  0.85 and 1.0. `NUMERICS_KNOWLEDGE` K0c-T: "quote two models or quote none"
  — a second closure is the first extension to propose if the rung gates.
- **A mesh-converged `St` if the triples come back not CONVERGING** (section
  8, prediction 8).
- **Whether the inlet layer's internal structure (`k`, `omega` profiles)
  matches the facility's**; only `delta_99` and the core velocity are
  measured against stated values.

## 12. Status

**Reference NOT OBTAINED; gate rows BLOCKED; design registered; no case
built and no compute spent at the time of this commit.** Comparator and
secondary digitisation frozen in the same commit. Builder, mesh check, runner
and marker committed beside them. The costed acquisition list of section 2
goes to Sanaa. Results, when the physics stage reports, land in
`T3_RESULTS.md` beside this file with every row's verdict and what it cannot
see.
