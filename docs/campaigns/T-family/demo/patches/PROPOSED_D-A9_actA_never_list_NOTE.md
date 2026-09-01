# D-A9 — the never-list patch for Act A. PREPARED, NOT APPLIED.

**Patch:** `PROPOSED_D-A9_actA_never_list.patch` (11 hunks, two files).
**Target tree:** `sdk/` — **cfd's**, not ours. This lane does not edit it.
**Dry run:** `git apply --check` passes against HEAD. It has **not** been applied.

    git apply docs/campaigns/T-family/demo/patches/PROPOSED_D-A9_actA_never_list.patch

Authority: Sanaa's shooting protocol, `etc/sessions/2026-09-01T1900Z…` and
`…T2030Z_sanaa_demo_shooting_protocol.md` (`cfcf766f`). Her never-list:
*prior runs, replay, agreements, paths, ids, tiers, "not recorded", "no solver",
"already finished"*, with physics facts preserved and phrased as the platform's
next automatic step rather than as an apology.

This is the **last correctness gate on Act A** (checklist box 9). Three of the
`thermal_display.py` sites render **unconditionally, on every take**.

## The rule applied, per site

Resolution **(a) record the value** wherever the value exists on disk — that
makes the screen better rather than quieter. Resolution **(b) the platform's
next automatic step** only where it genuinely does not exist.

### `sdk/workflows/thermal_display.py`

| Site | Quantity | Fires | Res. | What the patch does |
|---|---|---|---|---|
| 274 | `NOT_RECORDED` constant | — | (b) | → `"the platform adds this automatically"`. **One edit fixes every sentinel-driven cell** (328, 390–392, 401, 431) because those sites compare against the *symbol*, not the literal — so behaviour is unchanged and only the rendered words move. |
| 280 | comment | no | — | reworded so the acceptance check below can be a clean zero rather than a zero-with-an-exception |
| 362 | joined descriptor parts | conditional | (b) | literal → the `NOT_RECORDED` symbol |
| 396 | magnitude with no unit | conditional | (b) | → `"{mag}, unit added on the next pass"` |
| **454** | source case | no | **(a), in words** | ⛔ the recorded value is a **filesystem path**, and *"paths"* is itself on the never-list, so recording it verbatim would swap one banned thing for another. → `"16 operating points, four powers by four airspeeds"` |
| **455** | reader | **yes, always** | **(a)** | → the reader description from the screen record, with script names and paths stripped |
| **458** | mesh cell count | **yes, always** | **(a)** | reads `bundle["mesh"]["n_mesh_cells"]` — the value is **39,680**, in `T23_T24_MESH_FACTS.json` |
| **459** | geometry guard | **yes, always** | **(a)** | → *"All sixteen cases were confirmed identical in the air, the housing and the core before any temperature was read."* |
| 527 | uncertainty envelope | conditional | (a) | → Screen 8's form: *"The grid convergence study for this case is running."* |
| 659–664 | four table fallbacks | conditional | (b) | literals → the `NOT_RECORDED` symbol |

### `sdk/workflows/motor_thermal_act.py` — **not in the original brief; found in this audit**

| Site | Term | Fires | What the patch does |
|---|---|---|---|
| 138 | `"not recorded"` — `_cell()` fallback | conditional | → `"the platform adds this automatically"` |
| 550–551 | `"not recorded"` ×3 on the **mesh resolution table** (Screen 5) | not on today's data | same. Dead today because `T23_GRADE.json.yplus` carries all four keys — but one missing key from putting a banned phrase on the table Screen 5 requires |
| 391 | **id** — `run_id=PRIMARY.name` | — | kept (internal) with a comment that it must never be rendered |
| 400 | **id + replay** — `"presentation of run T23_P305_U20"` | — | → `"the motor in its cooling duct"` |
| 734 | **agreement** | renders | → *"There is no measured data for this configuration, so the temperatures are shown as solved."* — **her own preserved wording**; the physics fact is kept, the banned word goes |

## Acceptance check

    grep -c 'not recorded' sdk/workflows/thermal_display.py sdk/workflows/motor_thermal_act.py   # 0 and 0
    grep -c 'presentation of run\|no agreement' sdk/workflows/motor_thermal_act.py               # 0

Both patched files were byte-compiled before the diff was cut.

## ⛔ What this patch does NOT fix, and must not be read as fixing

`thermal_display.py:790–810` is a **route problem, not a wording problem** (spec
§9.4.2). Its narration — *"a body this lab has already run"*, *"No solver starts
on this request"*, *"the screens come from that run's own fields"*, *"neither
meshed nor solved"* — exists solely to narrate the current state of the lab,
which her preamble bans outright, and it contradicts Screen 1 by announcing the
uploaded file is not used. **Rewriting those four sentences would leave a route
whose purpose is the thing the protocol forbids.** The standing recommendation
(D-A10) is that Act A is not shot through `thermal-display` at all; it is shot
through the registered `motor-thermal` act, which narrates none of this. This
patch deliberately leaves that block alone so the two decisions stay separable.

## Boxes 2 and 3 are NOT in this patch, and cannot be act-side

I was asked to wire the acknowledgement geometry table and the USER-DEFINED vs
LAB-DEFINED assumptions table into the act module. **Measured: there is nowhere
to put them.** The contract's frozen dataclasses in `sdk/workflows/demo_mode.py`
carry:

- `Restatement`: `restatement`, `confidence`, `cost_estimate` — three fields, no
  table slot.
- `GeometryMatch`: `quantity`, `solved`, `supplied`, `tolerance`, `relative` —
  a per-quantity comparison, not a features-found summary.

There is no field for a geometry summary table, for an expert-discussion block,
or for a USER/LAB assumptions split. Adding them is a **contract change in
`demo_mode.py`**, which is cfd's file and is the same class of change as D-A7.
The *content* for both is drafted and ready at spec §9.2 and §9.3; it cannot be
wired without the fields. **Reported rather than worked around** — inventing a
place to put it inside the act would be an act reordering the contract, which
the contract forbids.
