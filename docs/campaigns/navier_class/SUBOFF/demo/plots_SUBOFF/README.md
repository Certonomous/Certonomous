# SUBOFF drift sweep — demo plot folder

Built 2026-09-13 from the A1h full-domain drift sweep with **zero solver compute**,
under plot library **v2**. Regenerate with `python3 build_plots.py` and
`xvfb-run -a pvpython render_field_panels.py`.

**EVERYTHING HERE IS `PENDING`.** All seven β points were still running (about 2,450
to 2,640 of a registered 3000) and the two `CASE_FACTS` rows own only the word
`PENDING`, so no other verdict can reach a figure.

**No derivative and no neutral point is computed**, and neither will be until all
seven points land: `Y_v'` and `N_v'` are least-squares slopes over `|β| ≤ 8` and a
slope fitted to unfinished points changes under its own feet.

| File | What |
|---|---|
| `suboff_yprime_history.png`, `suboff_nprime_history.png` | all seven points against iteration |
| `suboff_yprime_vs_beta.png`, `suboff_nprime_vs_beta.png` | preliminary window means against β, Roddy's line and its ±4 % band |
| `suboff_residuals.png`, `_f10`–`_f75` | the residual-evolution series, one set of axes |
| `suboff_l2_corner.png` | the L2 zero-incidence corner, complete at 3000 |
| `suboff_mesh_l1m.png` | the L1 mirror's own mesh |
| the three field panels | **NOT PRODUCIBLE YET.** With `purgeWrite 2` nothing is reconstructed, and ParaView's decomposed reader exposes only `t = 0` — so a "latest time" panel would show the INITIAL CONDITION. Blank attempts were refused by the guard and deleted, not shipped. They are rendered for the first time when the sweep lands |

🔴 **`SIDECAR.md` also records the guard that stopped two blank panels being shipped**,
and the clauses now closing that hole in every driver in this repository.

🔴 **`SIDECAR.md` carries a preliminary observation that must be read before any of
these figures is shown**: the β = 0 symmetry check passes at 1e-08 against a 1e-4
threshold, but the side force at the other six points is about 25× below Roddy's
line and of the sign §4.2 registered in advance as evidence of an inverted
bookkeeping or solve. A candidate mechanism — the `slip` lateral boundary — is named
and measured there. It is escalated, not graded.
