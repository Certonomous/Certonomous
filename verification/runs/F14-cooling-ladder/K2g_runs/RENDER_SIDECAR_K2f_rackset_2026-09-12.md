# K2f rack-set ParaView renders — sidecar, 2026-09-12

**THE FIELDS IN THESE FIGURES ARE NOT RULE-4 COMPLETE, CARRY NO GRADED VERDICT,
AND WERE REFUSED BY THEIR OWN FROZEN COMPARATOR AT EXIT 2 — `NOT A RESULT`.**

That sentence is in this file, in the same file as the paths, deliberately: the
paths and the caveat must not be separable. Every figure also carries
`NOT A RESULT` burned into its own stamp, and that is enforced mechanically —
`scripts/demo3d_render_common.py` records `allowed_verdicts = {"NOT A RESULT"}`
for both cases and `assert_stamp` refuses a stamp carrying `PASS` or
`GATE REACHED` **before a single pixel is rendered**.

---

## What was produced, and from where

| figure | source case | what it shows |
|---|---|---|
| `K2f_L1_coarse_mesh.png` (425,768 B) | `K2f_runs/K2f_L1`, **58,368 cells** | the **COARSE** level's mesh, 30,304 of 58,368 cells in the cut |
| `K2f_L3_temperature_field.png` (125,986 B) | `K2g_runs/K2f_L3`, **664,848 cells**, **t = 803** | fine-level *T*, range 289.00–301.00 K |
| `K2f_L3_recirculation.png` (150,015 B) | same | fine-level streamlines, 6,504 points |

**Directory:** `docs/campaigns/F14-cooling-ladder/demo/figures_K2f_rackset/`
(701,769 bytes total). **Renderer:**
`docs/campaigns/F14-cooling-ladder/demo/render_K2f_rackset_paraview/render_k2f_rackset.py`,
ParaView 5.11.

**Where the images live and why:** the images sit under the committed
`docs/campaigns/F14-cooling-ladder/demo/` figures convention, beside
`figures_K2bU3R3/`, rather than inside the run tree — `FILING_CHARTER` keeps run
outputs in `verification/runs/` and figures with the campaign prose. **This
sidecar is what sits beside the run**, so a reader standing in the run directory
finds the paths and the caveat together.

## Sanaa's directive, and how each half was satisfied

> *"whenever a run completes, i want the paraview visualization of its mesh
> saved. (when the run is complete). The paraview should show the coarse mesh
> (or meidum mesh if the coarse isnt converged). But all fields should be stored
> as the fine mesh result fields (whenever we have it)."*

**Coarse mesh, and the choice is a MEASUREMENT rather than a default.** Her
parenthetical allows medium *"if the coarse isnt converged"*. `K2f_L1` **is**
converged: final-300 per-iteration residual peak-to-peak **5.05e-11** on `Ux`,
and `DP_module` monotone across all six checkpoints — **0 sign changes, p2p
3.11e-04 m²/s²**.

**`K2f_L2` would have been the wrong choice, on the same evidence, and it is
recorded here so nobody reaches for it later.** L2 limit-cycles at a 1e-4
residual floor (`Ux` 8 sign changes over the final 300, p2p 6.69e-05) and its
`DP_module` **turns** — 1 sign change, p2p 3.70e-03 m²/s². Both readings are in
`docs/campaigns/F14-cooling-ladder/K2h_PREREGISTRATION.md` §2.

**Fields from the finest completed level.** That is `K2f_L3` at **t = 803**, the
only reconstructed time it has; `processor*/` carries the full 25-interval
series from 500 to 803.

**NOTHING IS INTERPOLATED BETWEEN THE TWO.** 58,368 and 664,848 cells are
different meshes. A single image claiming to be the coarse mesh carrying the fine
fields would require resampling one onto the other, **manufacturing values no
solver wrote**. The mesh picture is L1's own mesh; the field pictures are L3's
own fields; each is rendered from the case that produced it and every caption
says which.

## The caveat, in full

1. **These fields are from a level that is not rule-4 complete and carries no
   graded verdict.** `mark_done_k2f.py` (frozen, unedited) returned **NOT DONE**:
   *clause 3 — last written time 803 != endTime 2000*; *clause 5 — 803
   `ExecutionTime` lines, expected round(2000/1) = 2000*. Recorded in
   `K2g_runs/autograde.K2f_L3.out`.
2. **The Δp number is evidence of an unsteady quantity, not a converged result.**
   `DP_module` = 28.0521393 m²/s² at iteration 803 (`MONITOR.K2f_L3.tsv`, col 15)
   does lie inside the registered band [27.9699, 28.0901] — **and that is exactly
   what makes this render dangerous.** The level never plateaued: stop rule
   **R4** ended it on coherent oscillation, 7 sign changes over 300 iterations
   with peak-to-peak **0.02802 m²/s² = 2.85× the registered `PLATEAU_TOL` of
   1.0e-02**. The frozen comparator `analyse_k2g.py` **REFUSED at exit 2** and
   graded nothing.
3. **The run that will produce the graded number is the transient successor
   `K2h_L3`**, registered and frozen at `db523d06a` with a pre-compute amendment
   at `d603a3b0a`, validator-ACCEPTED and queued. It is held behind a full box
   (4 requested ranks + 13 live > 16 cores) — a transient condition, not a defect.

**No observed order and no GCI may be quoted from these figures, and they are not
a Roache triple of one discretisation.** K2h §3: L1 and L2 are steady `DP_module`
and L3 would be time-averaged, which are two different quantities on one axis;
and L2's steady value is itself a time-slice of a non-stationary state.

## What the render did not touch

No solver ran. Fields were read through a scratch case of symlinks, and **both
graded trees were fingerprinted before and PROVED unchanged after** —
`K2f_runs/K2f_L1` and `K2g_runs/K2f_L3`, asserted by
`demo3d_render_common.assert_run_tree_untouched`.

**One honest blemish:** `pvpython` printed `X Error … GLXBadContext` at process
teardown, **after** all three images were written and after both
run-tree-unchanged assertions had passed. It is an X context cleanup error on
exit, it corrupted nothing, and it is recorded rather than omitted.

*Nothing here is sent, filed, uploaded, registered, posted or commented outside
this box (rule 7).*
