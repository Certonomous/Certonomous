# Act A module unblock — handover note for the cfd team

**Status: PROPOSAL. NOT APPLIED.** Nothing was written under `sdk/`. The
control-room server (pid 848778) was neither restarted nor signalled. All
verification was done in a throwaway `git archive HEAD` copy.

Prepared by the heat-transfer team, 2026-09-01. `sdk/` is cfd territory; the
patch is yours to apply.

- Patch: `/home/ubuntu/Certonomous/docs/campaigns/T-family/demo/PROPOSED_actA_module_unblock.patch`
- Target: `sdk/workflows/thermal_display.py`, one file, blob
  `ee1abe7fb0a3c01a59539a789772b8e2ea9e4413` (HEAD's version at `617a5800`).
- `git apply --check` passes against the real tree.

## Why one patch covers four ordered items

`_normalise_act_a` did `out = dict(b)` and then assigned over the result
**unconditionally**. Strings written as fallbacks for a bundle that carried
nothing were outranking values the producer had since measured. A fallback
that outranks a measurement is not a fallback.

## Hunks, by line range in the pre-patch file

| Hunk | Lines | What it does | Item |
|---|---|---|---|
| 1 | 52–57 | `import re` | — |
| 2 | 135–144 | A8 not-available row gets `satisfied_by="actA_assumptions"`; reason text rewritten so it is true in the only case it is ever shown. **The row is not deleted** — the existing mechanism retires it. | 7 |
| 3 | 160–165 | `figures_extra` on the Act A spec, carrying `actA_assumptions`. The frozen `figures` tuple above is untouched. | 7 |
| 4 | 333–338 | New helpers: `_display_spec` (reads the bundle's `display_precision`), `_columns_table` (a table from a column description, every cell through `_fmt`), `_ACT_A_COLUMNS`. | 1, 4 |
| 5 | 449–463 | `source_case`, `reader`, `mesh` become `b.get(...) or <fallback>`; `mesh` merges **per key**, not per dict. | 6 |
| 6 | 468–499 | `provenance_extra` same discipline; `result_table` comes from the bundle (`result_table`, else `result_table_columns`, else the act default). The default now carries **both** solid peaks. | 1 |
| 7 | 502–519 | Displayed temperatures read the bundle's precision. The monitor row is **exempted** and stays at full precision. | 4 |
| 8 | 525–531 | `quantity_rows` same discipline. | — |
| 9 | 540–547, 561–567, 602–611 | The same three guards in `_normalise_act_c`. Act C's bundle carries none of these keys, so that act does not change. | — |
| 10 | 602–611 | `_figure_list`: spec tuple + `figures_extra` + the bundle's own `extra_figures`. | 7 |
| 11 | 714–720 | `_present` iterates `_figure_list(spec, bundle)`. One line. | 7 |

## Verification

Driving `thermal_display.main()` in a throwaway copy with the live demo
assets. The real tree was never patched.

| Arm | Before | After |
|---|---|---|
| Act A | rc 0, 7 plots, 6 tables, 1 report | rc 0, **8 plots**, 6 tables, 1 report |
| Act C | rc 0, 5 plots, 5 tables, 1 report | rc 0, 5 plots, 5 tables, 1 report |
| Refusal, Act C, **both** bundles stripped | rc 2, 0 plots, 0 reports | rc 2, 0 plots, 0 reports |
| Refusal, Act A, controls stripped | rc 2, 0 plots, 0 reports | rc 2, 0 plots, 0 reports |

Act C's screen output is **byte-identical** before and after, apart from the
output directory path.

**The refusal arm carries its own planted control.** With only
`actc_screen_data.json` stripped and `actc_step_independence.json` left
intact, the patched module returns rc 0 with 5 plots — so the rc 2 above is a
refusal this test can distinguish from a stuck value. Act C's three control
blocks are split two-and-one across the two bundles; both must be stripped or
a working guard reads as broken.

Item by item, Act A after the patch:

- **Item 6** — the phrase "not recorded in this bundle" appears **5 times**
  in the baseline Act A output and **0 times** after. Reader is the bundle's
  real sentence, `Mesh cells: 39,680`, Geometry guard is the real sha256
  byte-identity sentence. No fallback fires.
- **Item 1** — headers over all 16 rows: Power W | Airspeed m/s | **Peak core
  temperature, C** | **Peak housing temperature, C** | Rise above inlet K |
  Margin to the 200 C limit K | Uncertainty. First row: 80, 10, 39.2, 38.1,
  24.4, 160.8. Checked in the bundle first: all 16 rows carry both keys,
  `peak_T_degC` equals `peak_core_T_degC` exactly in every row,
  `peak_T_region` is `core` in every row, and core ≥ housing in every row —
  so naming the existing column "core" is a true rename, not a relabel.
- **Item 7** — an eighth plot goes up, "What this run assumes, and what it
  does not resolve", rendered from `actA_assumptions.pdf`. The not-available
  table falls from 6 rows to 5 and the A8 row is gone, retired rather than
  deleted.
- **Item 4** — temperatures at 0.1, from the bundle's
  `display_precision.temperatures_in_figures`. Hottest 107.7 C, coolest
  24.7 C, smallest margin 92.3 K. The monitor-versus-cells offset stays at
  0.015011 K and the anchor residuals at 3.736e-05 K: the bundle's own
  `not_applied_to` exempts instrument evidence, and 0.1 K precision would
  print that offset as 0.0 K.

Nothing weakens the refusal: no hunk touches `_instrument_rows` or the refusal
block, and the figure list is consulted after the refusal returns. Nothing
fabricates a value: every new cell goes through `_fmt`, which takes no numeric
default, and a grep of the patched file for a numeric second argument to
`dict.get` returns nothing.

## Restart scope — batch this into the coordinated bounce

**The bundle and figure work needs no restart. This module change does.**
`_load_bundle` is called from the mission body, not at import, so bundle JSON
and figure files are re-read on every mission run. This patch is Python inside
a module the control-room server imports, so it does not take effect until the
server restarts. Batch it into the single coordinated restart rather than
bouncing a server Sanaa is sitting in.

After this patch, a bundle-supplied `extra_figures` or `result_table_columns`
is data-only too — a further sheet or a further column then lands with no
bounce at all.

## Relationship to the other pending proposal

`PROPOSED_actA_figure_standard.patch` is a separate pending proposal against
the same file and the same base blob. The two touch **disjoint line ranges**.
Measured: both apply cleanly **in either order**, the combined file parses,
and the combined module gives Act A rc 0 / 8 plots / 6 tables / 1 report with
the banned phrase 0 times, both peak columns present and the assumptions sheet
up; Act C rc 0 / 5 / 5 / 1; refusal rc 2 / 0 plots / 0 reports.

`PROPOSED_thermal_intent.patch` remains stale and must not be applied.

## An index hazard found while preparing this — inspected, not reverted

The shared index stages the **deletion** of
`docs/campaigns/T-family/demo/figures_actA/actA_assumptions.pdf` and `.svg` —
the artifact item 7 needs. Both are present in HEAD and on disk, but absent
from the index, so they read as untracked in the worktree and as staged
deletions against HEAD. A bare `git commit` by anybody would remove the
assumptions box from HEAD, and this patch would then report it as a missing
LANDED figure. The index also holds a stale copy of `actA_screen_data.json`;
HEAD and the worktree agree with each other and disagree with the index. The
index is chief's call, so this is reported and not touched.
