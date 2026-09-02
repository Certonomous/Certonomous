# SANAA-DIRECT — final cosmetic touches, all acts (2026-09-02, ~11:00Z)

## Sanaa's words, verbatim

> JF1: did u confirm is was O mesh? also it says this on top of the final
> plot: Surface loaded: airfoil_blown_slot.stl, 1,716 triangles. The
> rendered view arrives with the run. remove it. Three last touches, all
> cosmetic:
> Predicted wall 4.9 vs actual 6.5 min goes unreconciled — the core-min line
> gets its "within 3%" sentence but the wall miss (+33%) gets none. One
> clause after the slowest-member line closes it: "predicted 4.9; the
> strongest-blowing case ran long, and the wall clock followed it." all acts
> have a Surface loaded: t23_solved_geometry.stl, 1,800 triangles. The
> rendered view arrives with the run. or smth similar on the plot, it
> shouldnt say that. No where should it say 'reference geometry '. Dafoam;
> change the 'where the adjoint says to go 'or smth like that to gradient
> descent and remove No sealed certificate is attached to this run also dofr
> dafoam i want to add in the prompt dont run convergence study also nd the
> ruling ("80 core-minutes, 20.0 minutes wall at 4 ranks") should appear as
> the standard table (Workers | Core-min total | Wall) in the act, matching
> the page. and check/ incorporate Colour bar present? The coloured views
> (whole wing + inboard zoom) need the millimetre scale beside them — a
> field-coloured surface with no scale is the one thing left that could read
> as decoration. The transcript's "colour window fixed across every frame,
> −309 to 303 mm" line implies it exists; confirm it renders.
> The inboard zoom crops the surface at the frame edge (bottom-right runs
> out of view). Pull the camera back a touch so the patch sits inside the
> frame — cropped geometry reads as a viewport bug.
> The zoom view is all warm tones — consistent with the upper surface moving
> outward, fine — but make sure the caption on screen says which quantity
> the colour is (outward normal motion, mm), since without the red/blue
> contrast of the full map a viewer can't infer it. everything else for
> these two runs is good to go. Motor: same issue with the 'surface
> rendered...' on top of the plot. Needs to go. and: The wall-clock
> prediction now exposes the wave problem instead of the slowest-member line
> resolving it: "Predicted wall clock: 560 core-minutes over 12 workers,
> about 47 minutes" — but actual is 86. The 47 assumed perfect packing
> (560/12); 16 runs on 12 workers is two waves, so the honest prediction is
> ~2 × 36 ≈ 72–80 min, and the actual-vs-predicted line plus the two-wave
> sentence must both appear. As pasted, the act predicts 47, delivers 86,
> and never explains — that's a 83% miss left hanging. Fix both ends:
> predictor states waves ("16 runs on 12 workers: two waves, predicted ≈ 75
> min wall"), and the slowest-member two-wave sentence (from the earlier
> order) closes the loop after the table. (If the dump just truncated before
> the conclusion, confirm the sentence survives there.). And still the max
> temp plots still has the titles overlapping. No need to have the label W
> on top of each of them, just have an x axis at the bottom of that plot
> that shows the W values that way the values dont overlap on the
> plot.battery also shouldnt say Surface loaded: battery_module_8cell.stl,
> 1,944 triangles. The rendered view arrives with the run. needs to go. else
> this run is green. Just for all acts still condense the sentences. Anythin
> else i did not mention here stays as is
