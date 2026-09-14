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

🔴 **`SIDECAR.md` carries a preliminary observation that must be read before any of
these figures is shown**: the β = 0 symmetry check passes at 1e-08 against a 1e-4
threshold, but the side force at the other six points is about 25× below Roddy's
line and of the sign §4.2 registered in advance as evidence of an inverted
bookkeeping or solve. A candidate mechanism — the `slip` lateral boundary — is named
and measured there. It is escalated, not graded.
