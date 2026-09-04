# Closure-correction library — ARCHITECTURE

**STATUS: DRAFT v0.2, 2026-09-04. PRE-INGEST. ZERO COMPUTE — this document registers a DOCUMENT
STRUCTURE, not a run, and no solver has been launched under it. Nothing in this file is a
verdict.** v0.2 folds in two read-only survey lanes: the install surface is now MEASURED
(§2.1-2.4) and v0.1's open flow-class question is RESOLVED (§3). The gap register, the retrieval
priorities and the recommendation on which case should earn the first certified result live in the
companion `INGEST_PLAN.md`. Filed rather than kept in scratch because L-186 forbids the scratchpad
as a handoff channel and this frame change must survive a session kill.

**Authority:** Sanaa verbatim at `0910b664`,
`etc/sessions/2026-09-04T1510Z_sanaa_model_form_closure_ladder.md` — the closure line returns as
the TOP RUNG of a validation ladder and as OWNER of this library. Provenance verified at HEAD by
this supervisor: the commit is in HEAD's history and the file on disk is byte-identical to its
HEAD blob `e2089d0a`. **Execution is SEQUENCED behind M6/CRM's first rungs and builds as the
separated-flow cases (F6 hump, periodic hills, duct) come online; no closure solve runs before
that sequencing point.**

## 0. What this library is, and the failure it is built against

Sanaa's word is **installable**: "installable, provenance-tagged closure options, each mapped to
the flow class it addresses and its own validation case." An entry that cites a paper and stops
is a bibliography. This library's unit is not a citation — it is **an applicable model-form
modification with a demonstrated install path and a licence to be believed.**

The failure this architecture exists to prevent is precise, and it is the one that would destroy
her named product. At rung 3 a lane applies correction X to a hard case and X does not fix it.
Two explanations are then indistinguishable:

  (i) the correction genuinely does not help this flow class;
  (ii) we implemented the correction wrongly.

Without a structural separation of those two, the exhaustion result Sanaa calls "rare and
valuable" — *all known closures fail this flow at these numbers* — **collapses**, because it is
equally consistent with *the lab implemented eleven corrections incorrectly.* A ladder record
that cannot exclude (ii) is not a certificate; it is a confession with the wrong title.

Hence the load-bearing rule of the whole design, which is this line's own bright line
(`CLOSURE_MODELLING_CHARTER` §22.2 — corrections live inside the solved equations, re-solve, not
post-hoc) applied to the library itself:

> **An entry is licensed as ladder evidence only after it has reproduced its own paper's claimed
> improvement, on its own paper's validation case, through the registered path, against the same
> reference.** Until then it may be TRIED, but a negative result from it is NOT evidence about the
> correction — only about our implementation.

## 1. Where it lives

Sanaa's wording is "into the docs and lessons". `docs/LESSONS.md` is a narrative record of things
learned; it is the wrong container for 30-60 structured, queryable, diffable entries. Split:

```
docs/closure/correction_library/
  SCHEMA.md              # the frozen entry schema (this doc's §2)
  LIBRARY_MANIFEST.md    # the roll; an exhaustion claim pins THIS by sha
  library.json           # machine mirror, generated, never hand-edited
  INGEST_PLAN.md         # ordered ingest queue with per-item status
  entries/<family>_<name>_<author><year>.md
  LADDER_RECORD_FORM.md  # §4, coordinated with verification
```

`docs/LESSONS.md` gets **one** lesson block: the doctrine and the traps (§0 above, §5 below), with
a pointer to the library. Doctrine in lessons, data in the library. That satisfies "docs and
lessons" without turning LESSONS.md into a database it cannot be queried as.

**Filing question to route:** a schema checker belongs in `scripts/` per `FILING_CHARTER`, which is
outside closure's folder scope. Adding a NEW file to a shared directory is not patching another
team's instrument, but I will not assume it — chief to route, or it lands under
`cases/RANS_LES_closure_models/_common/`.

## 2. The entry schema — every field mandatory, "none" written rather than omitted

| Field | What it carries | Why it is mandatory |
|---|---|---|
| `id` | stable identifier, cited by ladder records | a ladder record must survive a renamed file |
| `family` | one of (a)-(f), §3 | free text makes the rung-3 filter unrunnable |
| `flow_class` | one or more from the fixed vocabulary, §3 | this is the mapping Sanaa named |
| `equation_form` | the modification AT EQUATION LEVEL, transcribed with source equation number and page | a correction described in prose is not installable |
| `provenance` | paper path in `docs/papers/closure/`, title-page verification state per **L-144**, equation numbers, pages | §15: cite only from a title-verified PDF |
| `claimed_effect` | the paper's own claim, QUOTED, with its magnitude and its reference data | separates their claim from our result |
| `validation_case` | the paper's own demonstration case + whether we hold that reference data, and where | the reproduction gate needs a target |
| `install_class` | **exactly one of** `dictionary-model` / `dictionary-coefficients` / `field-input` / `fvOptions-source` / `compiled-library`. See §2.2 | prevents an entry claiming "coefficients only" that **silently does nothing**: an unrecognised key in a `<model>Coeffs` sub-dict is ignored without error |
| `install_stanza` | the literal `constant/turbulenceProperties` content — `RAS { RASModel <name>; turbulence on; }` | **measured correction: this installation is ESI api 2606 and uses `turbulenceProperties`. `momentumTransport` is the OpenFOAM.org name and DOES NOT EXIST here — an entry drafted against it will not run** |
| `model_type_name` | the string typed into `RASModel` | **checkable at zero compute against the library's symbol table (`nm -DC lib.so \| grep RASModels::`)** — see §2.3 |
| `libs_required` / `libs_route` | `.so` basenames as they appear in `FOAM_USER_LIBBIN`; route is one of **three** values — see §2.5 | rule 14, L-221/L-222: `libs` entries are INSERTED WITH AN ASSERT, never replaced. The lab's machinery is `scripts/foam_libs.py` (`ensure_libs`/`assert_libs`, depth-aware, idempotent, refuses on two top-level entries) |
| `failure_mode` | **`loud`** or **`silent`** — what happens if the library does NOT load | this field, not convenience, decides which `libs_route` is legal (§2.5) |
| `contraindications` | where it is known or measured to make things WORSE | a correction library without contraindications is a footgun; "none known" must be argued, never defaulted |
| `what_it_cannot_see` | inherited from charter §16, which makes this a mandatory section | the lab's standing honesty clause |
| `band_interaction` | does this correction act on the `k`-magnitude axis the shelf-D band does not perturb? | §22.4 item 2 — where a band and such a model appear together, the overlap in what NEITHER sees is stated; this field pre-computes it |
| `status` | the licence, §2.1 | the whole point |
| `cost_estimate` | core-minutes for its reproduction run, rule 12 | a proposal with no cost is disqualified |

### 2.1 The licence states — an entry's own ladder

- `REGISTERED` — schema complete, provenance title-page verified. Not implemented. **Not evidence.**
- `IMPLEMENTED` — install path demonstrated to run in this toolchain on any case. **Not yet evidence.**
- `REPRODUCED` — reproduced its paper's claimed improvement on its paper's own validation case,
  registered path, same reference. **LICENSED as rung-3 evidence.**
- `REFUTED-IN-REPRODUCTION` — implemented, and the paper's own claim did NOT reproduce on the
  paper's own case. **This is a finding and a certified result in its own right, not a discard.**
  It is disclosed, kept, and it disqualifies the entry from being cited as ladder evidence *for*
  the correction — while remaining fully citable as evidence *about* it.

An exhaustion claim counts only `REPRODUCED` entries. `REGISTERED` and `IMPLEMENTED` entries in a
matching flow class are **named as untried** on the ladder record — an exhaustion claim with
unnamed gaps is not an exhaustion claim.

### 2.2 The install classes, and the one that cannot be written
`fvOptions` adds sources; **it cannot modify the momentum equation's Reynolds-stress term.** So an
anisotropy correction — the `b_ij` / nonlinear-stress shape, which is SpaRTA and TBNN — is **NOT**
installable by that route and requires `compiled-library`. Only scalar-transport corrections (k and
omega source terms) may declare `fvOptions-source`. **An entry pairing an anisotropy correction
with `fvOptions-source` is wrong on its face and the schema checker must refuse it.**

### 2.3 The symbol-table assertion — the cheapest defence against §0 failure (ii)
Every built library on this box registers its model under a name recoverable from `nm -DC`.
Therefore **"does the library actually provide the model this entry claims" is a zero-compute,
mechanically checkable assertion**, and it is checked before any solve. It does not prove the
correction is implemented correctly — nothing static can — but it removes the cheapest and most
embarrassing version of failure (ii): a ladder record reporting that a correction did not help,
when the solver silently ran the baseline because the model name was never registered.

### 2.4 The planted-zero trap that ships INSIDE a stock model
`GEKO` with `machineLearning true;` reads `Ck` and `Comega` as `volScalarField`s from the case time
directory under `READ_IF_PRESENT`. That makes it a spatially-varying data-driven correction
installable with **no compile** — genuinely valuable. **But a missing or misnamed field silently
becomes zero and the run completes looking like a plausible baseline.** This is rule 3's
planted-zero failure built into a shipped model. **Any `field-input` entry MUST plant a non-zero
correction field, read it back, and demonstrate the solve moves — or it is refused.**

### 2.5 `libs_route` — three values, chosen by FAILURE MODE, not by convenience
Settled by reading `docs/closure/LIBS_ASSERT_SWEEP.md` (the L-221 sweep: 8 library-load call
sites, 4 unasserted and one of them a **live** defect). Two facts from it change the field:

1. **A `grep -q '<lib>'` assert is NOT sufficient.** Sweep site #7 records what the naive check
   cannot see: **a second top-level `libs` entry is a DUPLICATE DICTIONARY KEY, not a longer
   list.** A controlDict carrying two of them passes `grep -q` and may still not load the library.
   `foam_libs.ensure_libs` refuses on that condition; a hand-rolled assert does not.
2. **Assert-without-insert is legal in exactly one circumstance, and the sweep names it.** Site #8
   is recorded as *"the one place the law is applied in half"* — assert only, no insert — because
   a missing library there produces an **unknown RAS model**, i.e. a LOUD failure. That is a
   principled exception, not a shortcut.

| `libs_route` | when legal |
|---|---|
| `ensure_libs` | **the default.** Insert-or-replace, re-read from disk, assert. Required whenever `failure_mode: silent` |
| `assert_only` | **only** when `failure_mode: loud` — a missing library makes the solver refuse an unknown `RASModel` name. Never where the solver would fall back to a stock model |
| `replace_with_assert` | the R4 precedent only (`R4_sparta_build/r4_lib.py:100-140`), where the entry being replaced names a library **absent from this machine** so merging would load a non-existent `.so`. Requires `libs_route_justification` naming that condition |

**Why `failure_mode` is a schema field and not a note.** L-221's cost was five eigenspace re-solves
returning `it=0` and the baseline `U_rms` — **the unperturbed field, which looks like a plausible
physical answer.** A correction that fails to load silently is §0's failure (ii) in its purest
form: the ladder records "this correction did not help" when the correction never ran.

**⚠ Carried to the chief, not fixed here:** `lint_foam_libs.py` **excludes
`cases/RANS_LES_closure_models/` by default** (`--include-closure` opts in), and this sweep shows
closure's tree holds **6 of the 8** library-load call sites in the lab. **The tree with the most of
this defect class is the one the linter skips unless asked.** `scripts/` is not closure's.

## 3. Controlled vocabularies

**Families** (Sanaa's own list, made enumerable): (a) analytical / algebraic-stress /
explicit-algebraic; (b) functional / nonlinear eddy-viscosity; (c) curvature and rotation;
(d) separation-specific; (e) data-informed / data-driven; (f) closure-challenge corrections.

**Flow classes — RESOLVED BY MEASUREMENT: no controlled vocabulary exists in this repository**
(searched four file types against four phrase patterns; every hit is prose usage, never a
definition — a negative that is a search result, not a proof of absence). **But two de facto
vocabularies do exist, and the decision is to PROMOTE rather than invent a rival.**

**Two fields, not one — collapsing them is what forces the invention of a rival.**

- **`flow_class`** — promoted from `docs/closure/CLOSURE_METHOD_CLASSES_INVENTORY.md` §3.8, the
  lab's only existing flow-class *list*, already tied to per-class evidence and citations:
  *square duct / secondary flow of the second kind* · *2-D separation (hills, curved step, BFS)* ·
  *geometry transfer at fixed Re* · *Re extrapolation* · *unsteady RANS* · *3-D complex geometry*.
  **Adopting it is a decision to PROMOTE a per-method assessment table into a controlled
  vocabulary, and is recorded as such — it was never declared as one.** It states what an
  exhaustion claim covers.
- **`validation_cases`** — the concrete case ids already used by `R4_sparta_build/MODEL.json` and
  by the benchmark on disk: `PH_Breuer`, `Parm_PH_29`, `DUCT`, `CBFS`, `NASA_2DWMH`, with per-case
  ids of the shape `AR_3_Ret_360`, `PHLL10595`, `CBFS13700`. It says which artifact backs the claim.

*"2-D separation" and `PHLL10595` are not the same kind of thing, and the ladder needs both.*

**`library.json`'s field vocabulary starts from `cases/RANS_LES_closure_models/R4_sparta_build/MODEL.json`**
— the closest existing thing in the lab to a machine library entry, already carrying
`preregistration_sha256`, training cases, symbolic term list, CV error, condition number, seed
agreement and a `planted_zero_verdict`. Adopted rather than rivalled.

## 4. The ladder record form — what makes the exhaustion claim falsifiable

Per rung, against **the same reference at every rung** (her words), each applied and gated
individually through the standard registered path:

1. **Rung 1** — every stock closure tried, each with verdict and deviation. "If none land, register."
2. **Rung 2** — the §0 numerical rule-out, cited to its artifact.
3. **Rung 3** — the candidate set is **DERIVED, NOT CHOSEN**: filter `LIBRARY_MANIFEST.md` by the
   case's flow class **at a pinned manifest sha**. Record: entries selected; entries matching the
   flow class and **excluded, each with its reason named**. An unexplained exclusion is how an
   exhaustion claim gets quietly narrowed until it is true.
4. **Rung 4** — the lab's own GP/SpaRTA research closure.

**The exhaustion claim is time-indexed by construction.** It reads *"all known closures in the
library at manifest sha S fail this flow at these numbers"* — never *"all known closures"*. The
sha is what makes it checkable later, and what stops it silently decaying as the library grows.

## 5. Structural exclusions — what may NEVER enter this library

1. **A band is not a correction** (§22.4 item 2, L-219/L-220, D446). An eigenspace band is a
   statement about what the model cannot see. It is never applied to a prediction, never
   subtracted from an error. The library must not let a band enter as an entry.
2. **A post-hoc field correction is not a closure model** (§22.2). Entries modify the solved
   equations and are re-solved.
3. **Per-case switching is not a model** (§22.1) — and here is a tension I am flagging rather than
   resolving alone, because it is exactly the mistake this charter already records as NOT SENT:
   the ladder applies corrections **per case**, which is in direct tension with §22.1's "one model
   applied uniformly to all eight cases." The two are different products and must not be
   conflated. **A ladder-derived per-case correction may NEVER be assembled into a benchmark
   submission as if it were one model** — that is the round-5 heterogeneous entry, which is
   internal R&D and NOT SENT. The ladder is a validation instrument; the benchmark entry is a
   scored product. This boundary needs to be written into whichever charter lands the ladder.
