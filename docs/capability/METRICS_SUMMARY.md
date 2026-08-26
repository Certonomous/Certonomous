# Metrics summary for the CAPABILITY GRID — Sanaa's §1–§6, resolved against the lab's standards

**Written 2026-08-26 by a verification-supervisor lane (lane id `metrics`), for the verification
supervisor to fold into `docs/CAPABILITY_GRID.md`.** Taxonomy and wording are Sanaa's
`[SANAA-DIRECT] CAPABILITY GRID` directive, `docs/LAB_STATE.md:1225-1253` at HEAD `33dbe337`.

**The rule this file obeys (Sanaa's):** a summary is written ONLY where an item is ABSENT from
the lab's existing verification/standards files. Where the item already exists, this file gives a
one-line citation — file, section, line range — and nothing else. **Every line range below was
resolved against HEAD `33dbe337` with `git show 33dbe337:<path> | sed -n`.** A summary written
here is labelled `ABSENT from standards — summary written here, not a standard until Sanaa adopts
it`; it binds nobody and moves no threshold.

**ASME V&V 20 itself:** the standard's own text is **NOT** in the repository.
`docs/papers/verification_validation/` holds `dowding_2016_asme_vv.pdf` (Dowding, Sandia
SAND2016-5342C — an *overview* of V&V 20-2009), Oberkampf & Roy 2011, Eça & Hoekstra 2014 and
the Ansys Fluid Dynamics Verification Manual. `docs/NUMERICS_KNOWLEDGE.md:120-123` lists
"ASME V&V 20-2009" as "now supplied", but `git ls-tree -r HEAD | grep -i 'v&v\|vv20\|asme'` returns
only the Dowding overview. Stated so the grid does not imply the standard is on the shelf.

**Predecessor draft:** none at HEAD (`docs/capability/` holds only `dafoam_GRID.md`), on disk or in
the scratchpad root. Nothing was reverted.

---

## §1 Verification metrics (right equations solved right)

**Sanaa's ruling, her words:** *"Your ruling: these score V, never P."* — `docs/LAB_STATE.md:1239`.
The lab's coverage rubric already enforces it: a case scores **V** only against an exact solution,
a manufactured solution or a correlation; **P** only against a public primary source with the
pre-registration on disk — `docs/COVERAGE_MATRIX.md:44-48` (rubric table) and `:95-100` (the
correction that heat-transfer's "V" rows were G rows).

- **Reference versus gate (a correlation yields a deviation, not a verdict, unless banded in
  advance)** — PRESENT: `docs/charters/VERIFICATION_CHARTER.md` §2, lines 62-102. Worked table with
  the Strouhal-vs-Roshko-Williamson row at 0.77 % (`:80-86`). Fixed verdict vocabulary `:96-102`.
- **Observed order versus formal order** — PRESENT: `VERIFICATION_CHARTER.md` §3.1 lines 195-277
  (dimensionality divides p by exactly 1.5), §3.2 lines 278-347 (the two ways an observed order
  lies), §3.4 lines 440-486 (a band is not a demonstrated asymptotic order; order must stop moving).
- **Correlation agreement, % deviation (Colebrook, Dittus-Boelter, Zukauskas)** — the *shape*
  (reference column, % deviation, banded PASS) is PRESENT in §2 `:74-86`; the named correlations
  are not cited by any charter or standard (`git grep -i colebrook\|dittus\|zukauskas` over
  `docs/charters docs/standards` returns nothing).
- **Error norms vs exact/analytic (L2, L∞)** — ABSENT from standards. `git grep` for `L∞`, `L_inf`,
  `Linf`, `L2 norm` over `docs/charters docs/standards CLAUDE.md` returns only two unrelated
  `λ_L2` penalty lines (`VERIFICATION_CHARTER.md:120-121`) and the Ekaterinaris review text.
- **Method of manufactured solutions** — ABSENT from standards. Named only in the coverage rubric
  (`docs/COVERAGE_MATRIX.md:46, 98, 229, 369-371`); no charter defines how an MMS case is graded.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Error norms against an exact solution u_ex on a mesh of N cells with volumes V_i:
`L2 = sqrt( sum_i V_i (u_i - u_ex(x_i))^2 / sum_i V_i )`, `Linf = max_i |u_i - u_ex(x_i)|`,
each stated in the solution's own units and beside its relative form (divided by a named
reference scale). Observed order from two mesh levels with refinement ratio r:
`p_obs = log( E_coarse / E_fine ) / log(r)`; from three levels use the shared instrument
(`scripts/roache_triple.py`, §2 below), never a two-point slope alone. The verification claim is
`p_obs` against the scheme's formal order p_f, reported as a pair `(p_obs, p_f)` with the
dimensionality printed (charter §3.1). MMS: choose a smooth analytic field u_m, compute the
source `S = L(u_m)` symbolically, run the solver with `S` added and u_m as boundary data, and
grade with the L2/Linf norms and `p_obs` exactly as above; a manufactured solution is a code
verification and scores V only. These norms are gate-shaped only when a band was frozen before
the run (charter §2 `:72-74`).

## §2 Grid / numerical convergence

- **Roache triple → GCI + observed order** — PRESENT: `CLAUDE.md` rule 5, lines 58-67 (the gate,
  in order; `Fs = 1.25`; never a GCI on a non-monotone triple); `docs/standards/MESH_STANDARD.md`
  §9.1 lines 448-473 (Sanaa's three-level ruling, verbatim, with the three conditions that stay
  binding); §10.2 lines 586-608 (a GCI at a vortex core bounds MESH error only — disclosure);
  §10.5 lines 623-633 (`STAGNANT_FLOOR = 0.5`, `P_MIN = 0.05` DEGENERATE); the shared instrument
  `scripts/roache_triple.py` lines 1-183 (rule 5 in order `:118-126`, states `:182-183`);
  `docs/UNCERTAINTY-DOCTRINE.md:21-28` (u_num recipe, Eça & Hoekstra least-squares fit, p clamped
  to [0.5, 2.5] for the band). Draw-scatter rule for any claim about the SHAPE of a ladder:
  `VERIFICATION_CHARTER.md` §17 lines 1424-1440.
- **Iterative convergence (residuals)** — PRESENT: `VERIFICATION_CHARTER.md` §4 lines 487-564
  (L-14 Initial-vs-Final residual, 1e-322 underflow `:506-510`, L-15 exit-zero, L-24 "a quantity is
  converged, not a run", iteration cap is a budget `:528-531`); `docs/NUMERICS_KNOWLEDGE.md:856-880`
  (`residualControl` is not a criterion; gate the graded quantity's peak-to-peak over a window).
- **The 10^105 lesson (absolute solution / continuity bounds)** — PRESENT as a numerics fact, not
  as a charter clause: `docs/NUMERICS_KNOWLEDGE.md` **N-AV12**, lines 4226-4293: VMFL007's
  normalised `p` residual sat in [0.157, 0.587] for 9 000 iterations while
  `time step continuity errors : sum local` reached **3.316e+105**; a normalised residual is
  blind to coherent divergence. No L-number carries it (`grep -n 'e+105' docs/LESSONS.md` empty).
- **Partition / round-off reproducibility (the 2.2e-5 finding)** — PRESENT:
  `docs/standards/PARALLEL_GATE_DOCTRINE.md` §2 lines 31-46 (Sanaa's words: "graded quantities
  moved 2.2e-5 across partitions — the answers are stable; the gates aren't"), §3 C1/C3 lines
  53-99 (deterministic decomposition; partition-robustness in gate design), §4.5 lines 184-202
  with the correction at `:194-198` (2.2e-5 = reattachment alone, 2.169e-05; separation moved
  2.857e-07). DAFoam side: `docs/charters/DAFOAM_CHARTER.md` §5 lines 156-198 (serial before
  parallel; every parallel gradient discloses its decomposition); `docs/NUMERICS_KNOWLEDGE.md`
  N-D12 `:3220-3229` (cold-start continuity signature is np-specific). Invariance passing because
  both sides are wrong together: `docs/LESSONS.md` L-38 `:1736`. No L-number carries 2.2e-5.
- **Seed spread** — PRESENT for closure models: `docs/LESSONS.md` L-181 `:8123-8150` ("seed
  spread is an extrapolation detector"); `docs/charters/CLOSURE_MODELLING_CHARTER.md` §4
  `:122-146` (per-seed realisability table). For CFD solves the lab's analogue is the
  partition pair above; there is no seed-spread clause for a deterministic solver.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
An *absolute* iterative-convergence bound, to sit beside the normalised residual: for each
transported field record `max|phi|` and the solver's `time step continuity errors : sum local /
global / cumulative` per iteration; a run is iteratively converged only if the normalised
residual meets its tolerance AND `sum local` is below a frozen absolute ceiling (order 1e-3 for
incompressible cases) AND the graded quantity's peak-to-peak over the frozen window is inside its
band (NUMERICS `:872-880`). Partition reproducibility as a metric: run the gate case at two
decompositions (np pair, pinned method + seed), report `delta_np = |Q(np_a) - Q(np_b)| / |Q|`
per graded quantity, and quote it as the reproducibility floor beneath which no difference is a
result (the lab's measured value on the hump: 2.169e-05 reattachment, 2.857e-07 separation).

## §3 Validation vs experiment — by data type

- **Integral / single-value (Cd, Cl, Nu, f·Re, Δp, St, shock standoff, reattachment) — % error vs
  measurement** — PRESENT: `VERIFICATION_CHARTER.md` §2 `:62-102` (reference column, % deviation,
  banded PASS; hump separation/reattachment row `:82`, Strouhal row `:81`); §5 `:565-648` (detector
  resolution beside every number, L-28 quantised shock position `:568-580`); §6b `:1661-1725`
  (a reference never obtained is recorded in one vocabulary); §2c `:1726-1832` (a row that grades
  a hypothesis must discriminate it from the hypothesis being absent — the K0cS Nusselt row);
  §2d `:1833-1913` (comparator frozen before its cases can answer it).
- **Fields — scaled MAE (the closure-challenge metric)** — PRESENT:
  `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md:239-244` (definition: mean Euclidean error over the
  1000 fixed points divided by the mean magnitude of the truth; overall = plain mean of eight);
  `docs/charters/RESULT_PRIORITY_CHARTER.md:134-138`. Correlation coefficient: Pearson r appears as a
  frozen clause V2 (`r >= 0.85`) in `campaign/R5_PREREGISTRATION.md` via `docs/DOCKET.md:579`
  (D214), not in any charter.
- **Profiles — RMSE/MAE at traverse stations, fraction inside error bars** — ABSENT from standards.
  The lab has graded profiles (F6b Gate Q, scaled MAE of velocity at 9 stations, 12.82 %,
  `docs/VALIDATION_INVENTORY.md:319`) but no charter or standard defines a per-profile RMSE or an
  inside-error-bar fraction (`git grep -i 'error bar\|RMSE\|traverse station'` over
  `docs/charters docs/standards`: only CLOSURE §4 `:146` "regardless of RMSE" and `:315`).
- **Structure / topology (vortex count, separation/reattachment location, stall angle, shock
  position) — "the round-5 lesson: scalar metrics can't see wrong structure"** — PARTLY PRESENT.
  Separation/reattachment *location* and shock position are graded as scalars (charter §2 `:82`,
  §5 `:568-580`). The round-5 record on disk is `docs/DOCKET.md:579-580` (D214: one third of the
  frozen round-5 gate graded fields the entry is not scored on and read PASS on an arm whose graded
  fields never converged; D215). **No L-number or charter clause carrying "scalar metrics cannot
  see wrong structure" was found at HEAD** (`grep -in 'round.5\|wrong structure' docs/LESSONS.md`:
  only L-96 `:4380` and R5 file-path lessons). Explicit structure rows are ABSENT from standards.
- **Statistics (unsteady): means, RMS, spectra peaks, phase averages** — ABSENT from standards.
  Strouhal is the only unsteady statistic a charter grades (`:81`); `git grep -i 'spectr\|phase.averag'`
  over `docs/charters docs/standards` hits only the Ekaterinaris review text.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Profiles: at each published traverse station s with N_s points, `RMSE_s = sqrt( mean_j (u_sim(y_j)
- u_exp(y_j))^2 )`, `MAE_s = mean_j |u_sim - u_exp|`, both divided by a named reference velocity,
plus `f_in,s = (number of j with |u_sim - u_exp| <= sigma_exp(y_j)) / N_s` where `sigma_exp` is
the reference's own stated error bar; the simulated value is interpolated to the experimental
ordinate, never the reverse, and the station list is frozen in the pre-registration. Fields:
scaled MAE as defined in GOALS_AND_PROPOSALS `:239-244`; Pearson r between simulated and truth
fields at the same points, reported beside scaled MAE, never instead of it. Structure: every
structural feature the case exists to show is an explicit row — vortex/bubble count (integer,
detector named), separation and reattachment x/L, stall angle, shock x/c — each with its
detector resolution (charter §5) and its own band; a scalar-metric PASS with a structural row
missing or failed is not a validation of the structure. Unsteady statistics: time-mean and RMS
over a frozen averaging window that starts after a stated transient and spans an integer number
of shedding periods; dominant spectral peak frequency (as St) with the resolution `1/T_window`
printed beside it; phase-averaged quantities only at pre-registered phases. Every unsteady
statistic states its window and its sampling interval or it is not a result.

## §4 The formal standard tying it together — ASME V&V 20 (u_val, E vs u_val)

- **u_val = sqrt(u_num^2 + u_input^2 + u_D^2); comparison error E = S − D judged against u_val**
  — PRESENT: `docs/UNCERTAINTY-DOCTRINE.md` lines 14-40 (the three channel recipes) and
  `:72-108` (combination stated once); `docs/NUMERICS_KNOWLEDGE.md:120-123` (V&V 20 reference),
  `:163-170` (Dowding overview: without an experimental comparison no validation claim can be
  made), `:469-490` (report the three channels separately). Standard's own text: NOT on disk
  (header above).
- **The one use, K0cT** — PRESENT: `docs/campaigns/F14-cooling-ladder/K0cT_NUSSELT_REGRADE.md`
  §2-§3 lines 44-66 at record commit `336a364d`: u_val in quadrature 5.43 % / 5.41 % from Betts &
  Bokhari's stated 5.00 % accuracy, 2.09 % / 2.00 % table inconsistency, 0.28 % / 0.49 % grid
  uncertainty; `E = 100 (Nu_solve - Nu_ref) / Nu_ref` on the fine mesh; verdict by `|E|/u_val`
  (3.09 and 4.57 → GATE FAIL). Every band element external to the solve values (`:44-53`).
- **High_order_grid_convergence.pdf** — PRESENT and RULED OUT as a source:
  `docs/standards/High_order_grid_convergence_PROVENANCE.md:1-30` (the file is Ekaterinaris 2005,
  PAS 41:192-300, a review of high-order schemes; contains no grid-convergence apparatus);
  `MESH_STANDARD.md` §10.1 `:557-585` (prohibition) and §10.2 `:586-608` (the one thing it says).

Nothing is ABSENT in §4 except the standard's own PDF; no summary is written.

## §5 Internal physicality (validity without a reference)

- **Heat balance closure %** — PRESENT: `docs/NUMERICS_KNOWLEDGE.md:881-908` (on a sealed case the
  boundary balance is an identity to 5e-9 %; `scripts/heat_balance.py` stamps
  `closure_is_identity_class`; reported, never counted as evidence on a sealed case); `:1180-1260`
  (open-domain advective enthalpy flux — the closure is convergence-sensitive there);
  `VERIFICATION_CHARTER.md:1947` (K0cS's repair was found by the heat balance).
- **Realisability (b_ij)** — PRESENT as a GATE: `docs/charters/CLOSURE_MODELLING_CHARTER.md` §4
  lines 122-157 (violating-fraction ≤ 3× truth's own, `max||b||_F ≤ 2·sqrt(2/3)`, else NOT A
  RESULT regardless of RMSE); `docs/NUMERICS_KNOWLEDGE.md` N-B3 `:2093-2100` (the `a1` limiter is
  a realisability constraint).
- **Continuity RMS / absolute continuity bound** — PRESENT only as the N-AV12 fact (§2 above,
  `NUMERICS_KNOWLEDGE.md:4226-4293`) and the continuity-error detection-floor lesson L-209
  (`docs/LESSONS.md:8836`); no charter gates on it.
- **Mass balance closure %, boundedness, entropy conditions** — ABSENT from standards
  (`git grep -i 'mass balance\|boundedness\|entropy'` over `docs/charters docs/standards CLAUDE.md`:
  nothing gate-shaped).

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Mass balance: `imbalance_% = 100 · |sum_patches (rho U·n A)| / (0.5 · sum_patches |rho U·n A|)`
over all boundary patches, computed from the solver's own `phi` (never a normal you build,
NUMERICS `:1191-1199`); on a sealed incompressible case this is an identity and is reported, not
counted. Continuity: `sum local` per iteration with its frozen absolute ceiling (§2 summary).
Boundedness: for every physically bounded scalar (alpha in [0,1], T inside its boundary range, k
and omega > 0) report `min/max` over the domain at the graded iteration and the count of cells
outside the bound; a bounded scheme keeping a field inside its bounds is not evidence of accuracy.
Entropy (compressible): `s - s_inf` must be ≥ 0 across a shock and ≈ 0 along an isentropic
streamline; report `max(s_inf - s)` (the largest entropy *decrease*, a discretisation artefact)
beside the shock-position row. Realisability: CLOSURE §4, unchanged.

## §6 Adjoint-specific

- **FD-vs-adjoint relative error per DV** — PRESENT: `docs/charters/VERIFICATION_CHARTER.md` §7
  lines 833-897: PASS ≤ 5 % aggregate with zero flagged components, CONDITIONAL 5-15 % with a
  per-component breakdown, FAIL > 15 % or any sign flip (`:838-847`); five-step reporting protocol
  with the plateau mini-sweep, per-component or cosine-similarity agreement, the 50 %-per-decade
  flag, the 2.5-5 % harness floor, central differences with step 1e-3 to 1e-2 (`:853-868`); three
  table shapes — per-derivative `| derivative | analytic | FD | abs err | rel err |`, per-component
  `| idx | analytic | FD (step) | rel. err % | sign match |`, step sweep `| step | rel err |
  rel err (excl. flagged) | cosine | status |` (`:870-892`). `docs/charters/DAFOAM_CHARTER.md`
  §2 `:41-89` (aggregate named as `‖J_an − J_fd‖ / ‖J_fd‖`; complex-step or forward-AD is the
  reference where reachable `:66-73`), §3 `:90-126` (plateau per component), §4 `:127-155`
  (registered trivial baseline = same probe at a deliberately wrong step), §5 `:156-198`
  (decomposition disclosed), §9 `:331-373` (FD at the final design point, cap-stopped is never
  PASS). A gradient check certifies a contraction, not an operator: `docs/LESSONS.md` L-36 `:1689`.
- **Complex-step** — NAMED but NO STANDARD: `DAFOAM_CHARTER.md:62-73` names it as the preferred
  reference where a build exists and requires a record to state when it did not reach for it;
  `docs/COVERAGE_MATRIX.md:373` records that no complex-step build exists. No build, no procedure,
  no band. `docs/capability/dafoam_GRID.md` census: never performed anywhere in the family.
- **Dot-product / duality test** — NO STANDARD in the lab. `git grep -il 'dot.product\|duality'`
  over `docs/charters docs/standards scripts CLAUDE.md` returns nothing; the only mentions are
  `docs/LESSONS.md` L-29 `:1413` (a random-seed dot-product test as a contraction) and L-36
  `:1689` ("any dot-product/FD test ... at one point"), plus `docs/EXTERNAL_REFERENT_AUDIT.md`.
  `dafoam_GRID.md` census: never performed anywhere in the family.
- **np-invariance** — NO STANDARD as a gradient metric. The nearest clauses are DAFOAM §5
  (disclose the decomposition; serial before parallel), PARALLEL_GATE_DOCTRINE C1/C3 (primal
  reproducibility across a partition pair), N-D12 (a signature is only a signature within one rank
  count) and L-38 (an invariance check can pass with both sides wrong). No clause requires
  `J_adj(np_a)` vs `J_adj(np_b)` agreement or sets a band for it.

**ABSENT from standards — summary written here, not a standard until Sanaa adopts it.**
Dot-product (duality) test: with tangent operator `A` (forward linearisation, `dR/dw · v`) and
adjoint operator `A^T`, for random `v`, `w` compute `<A v, w>` and `<v, A^T w>`; report
`|<Av,w> - <v,A^T w>| / (|<Av,w>| + |<v,A^T w>|)`, pass at machine precision times a stated
condition-number allowance (order 1e-10 in double); one point certifies the operator pair at that
point only (L-36). np-invariance: the same adjoint gradient at two decompositions,
`delta_np = ‖J_adj(np_a) − J_adj(np_b)‖ / ‖J_adj(np_a)‖`, per DV and aggregate, with both partitions
pinned and disclosed (PARALLEL_GATE C1); a band for it must be frozen before the run and cannot
be looser than the FD band it accompanies. Complex-step: `dJ/dx_i = Im[ J(x + i h e_i) ] / h` with
`h ~ 1e-20`, no subtractive cancellation, and it becomes the reference in the §7 table's FD column
"when built" — until a build exists every record says so on its face (DAFOAM §2 `:71-73`).

---

## Census of this file

Items in Sanaa's §1-§6: 26. PRESENT — cited: 17. NAMED but no standard: 3 (complex-step,
dot-product/duality, np-invariance). ABSENT — summary written: 6 classes (L2/L∞ + MMS; absolute
convergence + partition metric; profile RMSE/error-bar fraction, explicit structure rows, unsteady
statistics; mass balance/boundedness/entropy). Not located at HEAD: an L-number for the 10^105
lesson (lives as N-AV12), for the 2.2e-5 finding (lives in PARALLEL_GATE_DOCTRINE §2/§4.5), and
for the "round-5 / scalar metrics can't see wrong structure" sentence (nearest: D214/D215).

## Footer — the planted control: every cited sha, resolved

Run from the repository root; every line must read `ok` (2 distinct shas cited: HEAD of the
citations and the K0cT record):

```
for s in 33dbe337 336a364d; do printf '%s ' "$s"; git cat-file -e "$s^{commit}" 2>/dev/null && echo ok || echo MISSING; done
```

Reading at write time, 2026-08-26: 2 ok, 0 MISSING.
