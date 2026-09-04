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

---

## Addendum 1, 2026-09-04 — v1.0 → v1.1. FIVE GAPS FOUND BY THE FIRST IMPLEMENTATION, NOT BY REVIEW

**Lines whose number changed above this section: 0.** Nothing above is edited. v1.0's clauses all
stand; this addendum ADDS the fields v1.0 required a checker to enforce without giving an entry any
way to state them. **The gaps were found by building the checker, which is the only way this class
of gap is ever found** — a schema is not testable by reading it.

**1. The `structural.*` declarations — v1.0 refused four pairings that no v1.0 field could express.**
§4 refuses `fvOptions-source` on an anisotropy correction and §7 refuses bands, post-hoc field
corrections and per-case switching — but every one of those is a *physics* property, and v1.0 gave
the entry no key to declare it. **REQUIRED, added:** `structural.modifies_anisotropy_tensor`
(`yes`/`no`), `structural.is_uncertainty_band`, `structural.is_post_hoc_field_correction`,
`structural.is_per_case_switching`, `structural.planted_zero_verdict` (`PASS`/`FAIL`/`none`).
**Declared by the author, never inferred by regex.** A pattern over `equation_form` cannot tell
*"adds a term to b_ij"* from *"does not modify b_ij"* — the same tokens appear in both and a
negation inverts the meaning. **A checker that gets physics silently wrong is ARCHITECTURE §0's
failure (ii) wearing a green tick.** Declared, a wrong assertion is attributable, diffable and
falsifiable; inferred, it is a hidden heuristic nobody audits.

**2. `family` may be a LIST.** v1.0 said "one of `a`..`f`", singular, and the very first entries
refute it: SpaRTA is **a+e**, SST-QCRC is **f+b**. A scalar or a list of the same vocabulary is
valid; every member is checked.

**3. `validation_cases` is SPLIT, because dropping a paper's own guard case makes an entry look
better than it is.** v1.0 conflated *"case ids on disk"* with *"what the paper validated on"*.
SpaRTA's converging-diverging channel and SST-QCRC's **ZPG flat plate** have no id in the §3
vocabulary, and the flat plate is precisely the **generalisation guard** — the case showing the
correction does not break attached flow. Dropping it silently flatters the entry.
- `validation_cases` — **on-disk artifact ids only**, §3 vocabulary. What backs a claim here.
- `paper_validation_cases` — **free text**, REQUIRED: everything the paper validated on, including
  cases this lab does not hold. **No id is ever coined for a case we do not have.**

**4. `evidence_about_correction` is retained.** §6 makes `REFUTED-IN-REPRODUCTION` *"NO as evidence
FOR, YES as evidence ABOUT"*, which one boolean cannot carry. The generator emits both; both are
computed from `status` and neither is readable from an entry.

**5. "Schema complete" in §6 is DEFINED.** It was the ambiguity that blocked the first entry.
`equation_form` must cite an **equation number AND a page**, or carry the literal token
`UNVERIFIED`. `UNVERIFIED` **blocks `REPRODUCED`** and surfaces as `equation_form_unverified: true`
in `library.json`. **An entry that admits a gap outranks one that overstates**, and all three
Phase-1 entries carry that flag honestly today.

**Enforced by** `cases/RANS_LES_closure_models/_common/build_correction_library.py` (57 selftest
arms, every rule asserted twice — a valid entry it must PASS and that one rule mutated, which it
must REFUSE — plus two planted IO controls: `library.json` is not written when any entry is
invalid, **and the same writer is shown to write for a valid set**, because a refusal-to-write that
cannot be shown to write is not evidence). **Suite run by the supervisor, not relayed: 57/57, rc 0.**
Its first run was 37/55 and found a real defect in itself: a `_missing=object()` default argument
bound a different object than the module-level sentinel, so **every absent key read as present** and
the missing-key rule was dead. That is what the arms are for.

## Addendum 2, 2026-09-04 — v1.1 → v1.2. `model_type_name` NAMES THIS ENTRY'S PAPER'S MODEL, OR IT IS `none`

**Lines whose number changed above this section: 0.**

**Occasioned by a defect the supervisor found in the first Phase-1 set, in an entry that was
otherwise honest.** The SpaRTA entry declared `model_type_name: kOmegaSSTSparta` — a model that
genuinely is built on this box and whose symbol genuinely resolves — while its own
`contraindications` correctly warned that the built library carries **this lab's R4-discovered
coefficients** (`R4_sparta_build/MODEL.json`), **not Schmelzer's published ones**.

**The warning was true, and it was in the wrong place.** It lived in prose; `model_type_name` is a
**machine** field, and the rung-3 candidate filter reads `library.json`, not the commentary. The
record therefore said *run `kOmegaSSTSparta`* to every reader that matters, and a lane doing exactly
that would have produced a Schmelzer verdict from a model Schmelzer never published —
**ARCHITECTURE §0's failure (ii), reached with no bug anywhere, purely by a plausible name match.**

> **THE RULE: `model_type_name` names the model that implements THIS ENTRY'S PAPER. If the only
> built model with a matching name implements different equations or different coefficients,
> `model_type_name` is `none` and the near miss is recorded in `near_miss_built_model` (new,
> optional) and argued in `contraindications`. The symbol table proves a model is LOADABLE; it
> proves NOTHING about WHICH model it is.**

**This is the same trap in two other places, and both were already handled correctly:**
`kOmegaSSTQCR` is built but implements the constitutive relation only — **not the field-inversion ω
correction that is the "C" in QCRC** — so the SST-QCRC entry carries `none`; and TBRF has no
compiled model at all.

**A prose caveat is not a control.** Where an entry's honest warning and its machine field
disagree, **the machine field is what the lab will act on**, and the schema must not permit the
disagreement.
