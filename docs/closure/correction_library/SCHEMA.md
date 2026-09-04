# Closure-correction library — ENTRY SCHEMA v1.0 (FROZEN 2026-09-04)

**FROZEN.** This file is not edited. A departure is a dated amendment appended at the foot with a
version bump and the assertion `lines whose number changed above this section: 0` (CLAUDE.md
rule 6). `ARCHITECTURE.md` carries the reasoning; this file carries only the contract, so that a
checker and a lane can both be held to it.

**Zero compute.** Nothing here has been run. Freezing a schema is not a run and needs no gate.

---

## 1. File form

One entry per file, `entries/<family>_<name>_<author><year>.md`, opening with a fenced YAML block
delimited by `---`, followed by free prose. **The YAML block is the entry; the prose is commentary
and is never parsed.** `library.json` is GENERATED from the YAML blocks and is never hand-edited.

## 2. Fields — every one REQUIRED. Write `none` with a reason; never omit a key

| key | type | contract |
|---|---|---|
| `id` | string, `^[a-z0-9_]+$` | stable; ladder records cite this, so it survives a file rename |
| `family` | one of `a`..`f` | a=algebraic-stress, b=nonlinear-EVM, c=curvature-rotation, d=separation-specific, e=data-informed, f=closure-challenge |
| `flow_class` | list, from §3 vocabulary | what the correction claims to address; **the rung-3 filter reads this** |
| `validation_cases` | list of case ids | concrete artifacts, §3 |
| `equation_form` | string | the modification at equation level, with the SOURCE EQUATION NUMBER and page |
| `provenance.path` | path under `docs/papers/` | the PDF |
| `provenance.title_page_verified` | `yes` / `no` | **`yes` requires `provenance.title_page_quote` to be non-empty** |
| `provenance.title_page_quote` | string | verbatim printed title read off page 1, with who read it and when |
| `provenance.equations` | string | equation numbers and pages the `equation_form` was transcribed from |
| `claimed_effect` | string | the paper's OWN claim, QUOTED, with its magnitude and its reference data |
| `install_class` | one of §4 | how it is applied here |
| `install_stanza` | string | literal `constant/turbulenceProperties` content |
| `model_type_name` | string or `none` | the string typed into `RASModel`; checkable against `nm -DC` |
| `libs_required` | list | `.so` basenames as in `FOAM_USER_LIBBIN` |
| `libs_route` | `ensure_libs` / `assert_only` / `replace_with_assert` | §5 |
| `libs_route_justification` | string or `none` | **REQUIRED non-`none` when `libs_route: replace_with_assert`** |
| `failure_mode` | `loud` / `silent` | what happens if the library does not load; **governs `libs_route`, §5** |
| `contraindications` | string | where it is known to make things WORSE. **`none known` must be ARGUED, never defaulted** |
| `what_it_cannot_see` | string | charter §16 |
| `band_interaction` | `acts_on_k_magnitude` / `does_not` / `unknown` | §22.4 item 2 |
| `status` | one of §6 | the licence |
| `cost_estimate_core_min` | number or `none` | rule 12; the reproduction run's cost |

## 3. Controlled vocabularies

**`flow_class`** — PROMOTED from `docs/closure/CLOSURE_METHOD_CLASSES_INVENTORY.md` §3.8, the
lab's only existing flow-class list. **Recorded as a promotion: that table was written as a
per-method assessment and was never declared a controlled vocabulary.**
`square_duct_secondary_flow` · `separation_2d` · `geometry_transfer_fixed_Re` ·
`Re_extrapolation` · `unsteady_rans` · `complex_3d`

**`validation_cases`** — the case ids already used by `R4_sparta_build/MODEL.json` and by the
benchmark on disk: `PH_Breuer` · `Parm_PH_29` · `DUCT` · `CBFS` · `NASA_2DWMH`, optionally with a
sub-id (`AR_3_Ret_360`, `PHLL10595`, `CBFS13700`).

## 4. `install_class` — and the pairing the checker REFUSES

`dictionary-model` · `dictionary-coefficients` · `field-input` · `fvOptions-source` ·
`compiled-library`

**REFUSED COMBINATION:** `install_class: fvOptions-source` on an entry whose `equation_form`
modifies the Reynolds-stress / anisotropy tensor. `fvOptions` adds sources and **cannot modify the
momentum equation's Reynolds-stress term**, so an anisotropy correction (the SpaRTA and TBNN shape)
must be `compiled-library`. An entry claiming otherwise is wrong on its face.

**`field-input` carries an extra duty.** `GEKO` with `machineLearning true;` reads its correction
fields `READ_IF_PRESENT`: a missing or misnamed field **silently becomes zero and the run completes
looking like a plausible baseline.** Every `field-input` entry MUST plant a non-zero correction
field, read it back, and demonstrate the solve moves, before any result from it is believed
(CLAUDE.md rule 3).

## 5. `libs_route` is governed by `failure_mode`, not by convenience

| `failure_mode` | permitted `libs_route` |
|---|---|
| `silent` | **`ensure_libs` ONLY** |
| `loud` | `ensure_libs` or `assert_only` |
| any | `replace_with_assert` only with a non-`none` justification naming an ABSENT library |

A `grep -q '<lib>'` assert is **not** sufficient on its own: a second top-level `libs` entry is a
**duplicate dictionary key, not a longer list**, and passes that check while the library may fail
to load. `scripts/foam_libs.py`'s `ensure_libs` refuses on that condition.

## 6. `status` — the licence, and what each state may be used for

| `status` | meaning | may it be cited as ladder evidence? |
|---|---|---|
| `REGISTERED` | schema complete, provenance title-page verified. Not implemented | **NO** |
| `IMPLEMENTED` | install path demonstrated to run in this toolchain | **NO** |
| `REPRODUCED` | reproduced ITS OWN paper's claimed improvement on ITS OWN paper's validation case, registered path, same reference | **YES — the only licensed state** |
| `REFUTED-IN-REPRODUCTION` | implemented; the paper's own claim did NOT reproduce on the paper's own case | **NO** as evidence *for* the correction; **YES** as evidence *about* it. A finding, never a discard |

**An entry may NOT be `REGISTERED` on capability alone.** Several corrections are installable on
this box today whose defining papers we do not hold (`ShihQuadraticKE`, `LienCubicKE`). Capability
without provenance is not an entry: `provenance.title_page_verified: yes` is a precondition of
`REGISTERED`, and a `yes` with an empty `title_page_quote` is a schema violation — **that exact
defect was found in this corpus's own manifest on 2026-09-04** (Addendum 3 asserted "title page
below" with nothing below).

## 7. Structural exclusions — the checker refuses these outright

1. **A band is not a correction.** No entry may describe an uncertainty envelope (shelf-D
   eigenspace perturbation and its kin). §22.4 item 2, L-219/L-220, D446.
2. **A post-hoc field correction is not a closure model.** Entries modify the solved equations and
   are re-solved. §22.2.
3. **Per-case switching is not a model.** §22.1. A ladder-derived per-case correction may never be
   assembled into a benchmark submission as if it were one model — that is the round-5
   heterogeneous entry, which is internal R&D and NOT SENT.

## 8. Exhaustion claims

A rung-3 exhaustion claim is legal only when every entry with `status: REPRODUCED` whose
`flow_class` matches the case was applied and gated, **at a pinned `LIBRARY_MANIFEST.md` sha**, with
every flow-class match that was excluded **named with its reason**. The claim reads *"all known
closures in the library at manifest sha S"* — never *"all known closures"*. Entries at
`REGISTERED` or `IMPLEMENTED` in a matching flow class are listed as **untried**.
