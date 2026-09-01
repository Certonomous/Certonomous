# Shock-reflection display mission: assets and capture order

Built 2026-09-01 by a cfd lane. **Nothing here required new compute**: the
benchmark was solved on 2026-08-07 and both grids are complete on disk.

**Camera state, honestly.** The wired GUI act is a **proposal that has not been
applied and has not been seen in a running control room** (see
`PROPOSED_dmr_intent_NOTE.md`). What is shootable today without any server
restart is the figure and the numbers below, cut in as a result sheet in the
same way Act B's fallback works.

## Capture order

| # | Asset | Path |
|---|---|---|
| 1 | Density contours at the final time, both grids | `docs/campaigns/DMR/demo/figures/dmr_density_contours.pdf` (vector) and `.png` |
| 2 | One-page result sheet | `docs/campaigns/DMR/demo/DMR_SHOCK_REFLECTION_RESULT_SHEET.pdf` |

The sheet is one page and carries the figure, both tables, the verification
statement in three signed role voices, and the caveat box. It is built by
`make_dmr_sheet.py` in the same directory, which substitutes every number from
the graded records; nothing on it is typed by hand. Rebuild it with
`python3 docs/campaigns/DMR/demo/make_dmr_sheet.py`.

The tables below are the act's own on-screen tables, reproduced here so a
caption or a slide can be set from them without re-deriving anything.

## Table 1 — the two grids

| Grid | Cells | Spacing |
| --- | --- | --- |
| Coarse | 14,400 | 1/60 |
| Fine | 57,600 | 1/120 |

## Table 2 — incident shock position at the final time, against the exact solution

| Grid | Solved position | Exact position | Difference | As a share of the distance travelled |
| --- | --- | --- | --- | --- |
| Coarse | 3.0045 | 3.0005 | 0.0040 | 0.17% |
| Fine | 2.9967 | 2.9933 | 0.0034 | 0.15% |

Source, per grid: `verification/runs/DMR_runs/<grid>/locator_result.json`,
field `gateV`. The share is the difference over the distance the shock
travelled in x at fixed height between the start and the final time, which the
exact solution gives as 20 t / sqrt(3) = 2.309401 at t = 0.2.

## Table 3 — compute

| Item | Core-minutes |
| --- | --- |
| Estimated before running | 20 |
| Used | 2.4 |
| Used as a share of the estimate | 0.12 |

Source: `verification/campaign/DMR_RESULTS.md`, cost section. Basis: gross,
wall seconds times four ranks, both solves plus meshing, initialisation and
post-processing. The box cannot read its own billing, so no dollar figure is
quoted here.

## The verification line, in the words the act uses

> Verified against the exact shock-speed solution to within 0.15% of the
> distance the shock travels on the fine grid, and 0.17% on the coarse grid.
> The criterion, one percent, is fixed in writing before the run.

## THE FREEZE, AND THE ONE PART OF IT THAT IS NOT PROVABLE

**Read these two paragraphs together. The second is not a footnote to the first.**

**What IS provable, to the minute.** The gate, its threshold and its tolerance
are frozen at commit `74797a57`, **2026-08-07T22:40:28Z**. The earliest artifact
of either case is **22:43:36Z**, and the first solved write is **22:44:55Z**. The
pre-registration blob is `a08ee245…`, byte-identical today to what was committed
then — the repo move of 2026-08-18 carried it without changing it. **The
criterion could not have been chosen to fit the answer, and that is checkable by
anyone with the repository.**

**What is NOT provable, and must not be claimed.** The pre-registration calls the
measuring script *"the pre-committed detector"*. **That specific claim is not
supported by the repository.** `dmr_locator.py` was first committed at
`84933043`, **2026-08-08T01:56:04Z — about three hours AFTER the runs it
graded.** Its content may well have existed on disk beforehand; git cannot
corroborate it either way. Rule 2 asks that the grading path be fixed at the
pre-registration commit and verified by hashing against the committed blob, and
**for this campaign that verification is not available.**

**This does not overturn the result and nothing is being withdrawn.** The
measured values stand, the freeze of the gate stands, and the numbers are what
they are. What changes is only what may be said: **a claim that cannot be checked
is not repeated as though it had been.** If asked on camera whether the
measurement script was frozen with the gate, the honest answer is that the gate
was and the script's ordering cannot be shown.

**And it does not recur.** The successor reader
`verification/runs/DMR_runs/dmr_locator_v2.py` is committed at `4590ba56`,
**before** the rung it is registered to grade, and it carries a two-sided planted
control that is itself demonstrated able to fail. From here the ordering is
provable.

## The caveat box, in the words the act uses

> The fine structure behind the main shock, the second shock and the wall jet
> under it, is shown in the picture and is NOT among the quantities measured
> here. Read it as a picture, not as a number.
>
> This is an inviscid calculation with no turbulence model in it, so nothing
> here says anything about a turbulence closure.
>
> The comparison is against an exact analytic solution for the shock speed. No
> experimental measurement of this configuration exists to compare the rest of
> the structure against.

## Do not capture

- `verification/runs/DMR_runs/dmr_density_contours_t0p2.png`, the contour
  record retained with the runs. It is a correct scientific figure and its
  captions carry run directory names, the solver and flux-scheme names, a
  record filename and a pointer to an internal file. **Superseded on camera by
  the figure in row 1**, which is drawn from the same fields.
