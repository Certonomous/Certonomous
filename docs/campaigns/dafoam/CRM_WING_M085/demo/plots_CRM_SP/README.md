# CRM wing, Mach 0.85 — demo plot folder

Ten figures, built 2026-09-14 from the run tree with **zero solver compute**, under
plot library **v2**. Regenerate with `python3 build_plots.py`.

**🔴 NO OPTIMISATION RAN — zero design iterations have ever completed.** There is no
CD-versus-design-iteration history, no optimised geometry and no drag reduction, and
nothing here may be described as any of those. Status line for the act: *"baseline
established and verified against the published result; the optimisation has not yet
completed a design iteration."*

| File | Source |
|---|---|
| `crm_cd_history.png`, `crm_cl_history.png` | `P00` verbatim baseline primal, `rc = 0` |
| `crm_residuals.png`, `_f10`–`_f75` | the same log's 21 checkpoints, six equations |
| `crm_trim_cd.png`, `crm_trim_alpha.png` | `MP_R1` at **iteration zero**; the run died in its first adjoint |
| `crm_decomposition.png` | the decomposition sweep, three arms graded `PASS` |

**The headline is a validation, not an optimisation:** our `C_D = 0.02090109066417552`
against DAFoam's published **0.02090** and an independent prior lab run
**0.02090143421526141** — five significant figures, on a mesh rebuilt from the
published recipe.

`SIDECAR.md` carries the full provenance, the trim table, the decomposition finding,
and what is not built (the ParaView panels — C_p, FFD box, mesh — which the material
supports and which are the first thing to add).
