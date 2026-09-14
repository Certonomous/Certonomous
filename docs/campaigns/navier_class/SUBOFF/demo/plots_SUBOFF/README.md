# SUBOFF drift sweep — demo plot folder

Built 2026-09-13 from the A1h full-domain drift sweep with **zero solver compute**,
under plot library **v2**. Regenerate with `python3 build_plots.py` and
`xvfb-run -a pvpython render_field_panels.py`.

**🔴 THE ACT IS GRADED `NOT A RESULT`** — `L1M_GRADE/A1H_L1M_GRADE.json`,
2026-09-14T00:18:03Z. All seven β points fail the strict completion rule (`rc=1`, no
`End` line, no `endTime` directory, six fields missing), stopping between 2671 and
2881 of a registered 3000. The comparator's own rule-3 plants all PASS, so this is a
working instrument refusing. **Every figure here is a picture of an incomplete solve
and none of them is a result.**

**No derivative, no fit line and no neutral point.** The comparator refused to fit —
that refusal *is* the verdict — and §10 of the registration forbids a neutral point
for this act outright. `SIDECAR.md` lists the five items of the approved figure list
that the frozen registration excludes, and what was drawn instead.

| File | What |
|---|---|
| `suboff_yprime_history.png`, `suboff_nprime_history.png` | all seven points against iteration |
| `suboff_yprime_vs_beta.png`, `suboff_nprime_vs_beta.png` | preliminary window means against β, Roddy's line and its ±4 % band |
| `suboff_residuals.png`, `_f10`–`_f75` | the residual-evolution series, one set of axes |
| `suboff_l2_corner.png` | the L2 zero-incidence corner, complete at 3000 |
| `suboff_mesh_l1m.png` | the L1 mirror's own mesh |
| `suboff_mesh_sail_cut.png` | a cut through the sail showing its cells and wall layers |
| `suboff_p_side_b*`, `suboff_p_top_b*` | surface pressure at β = 0, ±8, ±12, one shared window |
| `suboff_umag_mid_b*` | mid-depth `\|U\|` at the same five angles |
| `suboff_wake_stern_b*`, `suboff_wake_sail_bp12` | wake cross-sections aft of the stern and the sail |
| `suboff_streamlines_bp12`, `suboff_q_bp12` | streamlines over the sail and the Q-criterion iso-surface, at +12 |
| `suboff_history_b*`, `suboff_residuals_b*` | per-point histories and per-point residual-evolution frames |

🔴 **`SIDECAR.md` also records the guard that stopped two blank panels being shipped**,
and the clauses now closing that hole in every driver in this repository.

🔴 **`NOT A RESULT` TWICE OVER — read `SIDECAR.md` before showing any of these.**
The seven points were **stopped on the owner's order** to free ranks, healthy, after a
convergence check — a deliberate stop, not a crash — so they fail the completion rule.
And separately the fitted **`Y_v' = +1.327616e-03` against Roddy's `−0.023008`** is
inverted in sign and ~17× low, which §4.2 pre-declared *before any number existed* as
evidence that the convention or the solve is wrong. **The mechanism is measured and
inside the freeze**: the `farfield` boundary is registered `slip` on a domain reaching
±2.99 m around a 4.356 m body — a closed duct that cannot pass the injected cross-flow.

**What is clean is worth saying too**: the mesh is genuinely full (`symm` nFaces 0), the
β = 0 symmetry check passes at `|Y'| = 1.45e-09` against a 1e-4 gate, and the `k`
bounding is benign — 0 cells at the bound out of 6,537,226. **The inversion is not
noise and not the mirror seam.** An act built on this sweep is showing a well-executed
refusal, not a measurement.
