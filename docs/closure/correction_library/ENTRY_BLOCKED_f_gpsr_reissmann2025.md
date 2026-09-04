# ENTRY BLOCKED — GPSR / semantic backpropagation (closure-challenge leaderboard rank 1)

**VERDICT: BLOCKED.** This is a blocker record, **not a library entry**. It is filed
here, one level above `entries/`, deliberately: `build_correction_library.py` globs
`entries/*.md`, so a file placed there is parsed as an entry, and this item must not be
parsed as one. Nothing here has been run. **ZERO COMPUTE.**

Drafted by closure lab-lane (laneC), 2026-09-04, under a tasking brief that asked for a
`REGISTERED` entry for this correction. **The entry could not be written honestly. This
record says why, and exactly what would unblock it.**

---

## 1. What was asked for

A `status: REGISTERED` entry for the rank-1 closure-challenge submission — GPSR /
semantic backpropagation, Reissmann, Fang, Ooi & Sandberg — citing
`docs/papers/data_driven_rans/reissmann_fang_ooi_sandberg_gpem2025_2409.07369.pdf`,
family (f).

## 2. Title-page verification: the paper IS what its filename says

Read personally, page 1 only, `pdftotext -f 1 -l 1`, 2026-09-04 (L-144). Verbatim:

> "Constraining Genetic Symbolic Regression via Semantic Backpropagation /
> Maximilian Reissmann(1*), Yuan Fang(1), Andrew S. H. Ooi(1), Richard D. Sandberg(1) /
> arXiv:2409.07369v2 [math.OC] 17 Nov 2024 / (1*) Department of Mechanical Engineering,
> University of Melbourne, Grattan Street, Melbourne, 3010, Victoria, Australia."

So `provenance.title_page_verified` would legitimately be `yes`, with a real quote. The
retrieval is correct. **That is not the problem.**

## 3. The problem: the held paper contains no turbulence closure

The paper is a genetic-programming methods paper. Its stated application is physics
equation discovery from the Feynman lectures — page 1, verbatim: *"This framework is
applied to discover physical equations from the Feynman lectures."* Its section
headings are Symbolic Regression, Consideration of a Dimensional Constraint, Structural
Homogeneity, Semantic Backpropagation, Benchmark, Hyperparameter Setup, Evaluation.

Measured over the sidecar with **`/bin/grep -ci`** (the closure corpus sidecars are
invisible to this box's default `grep` under .gitignore + ugrep — L-486):

| term | Reissmann | Schmelzer | Kaandorp | Wu & Zhang |
|---|---|---|---|---|
| `Reynolds` | **0** | 16 | 47 | 2 |
| `anisotrop` | **0** | 7 | 61 | 0 |
| `eddy visc` | **0** | 9 | 4 | 1 |
| `Navier` | **0** | 1 | 7 | 0 |
| `turbulence model` | **0** | — | — | — |

**The zero is planted-controlled** (CLAUDE.md rule 3): the same reader, the same
patterns, the same invocation returns large non-zero counts on three sibling papers, so
it is demonstrably able to see a non-zero. Reissmann's zero is evidence, not a blind
reader.

*(A naive `grep -ci RANS` on this file returns 22 and means nothing: `RANS` is a
substring of `t`**`rans`**`form`. Every one of those 22 hits is "transformer",
"transformation" or "Transactions". This is recorded because it is exactly the kind of
number that would otherwise be quoted as evidence the paper is about RANS.)*

## 4. Where the closure form actually lives — and it is not on this box

McConkey et al., *The Closure Challenge*
(`docs/papers/data_driven_rans/mcconkey_et_al_closure_challenge_2603.28884.pdf`,
title-page verified by this lane), Table 1, "Leaderboard as of March 2026", lists at
rank 1:

> Reissmann, Fang, and Sandberg **[17, 18]** — Overall 0.0595

Two references, not one:

- **[17]** = the held paper. "Constraining genetic symbolic regression via semantic
  backpropagation." *Genetic Programming and Evolvable Machines*, 26(1):12, 2025. **The
  search method.**
- **[18]** = Jack Weatheritt and Richard Sandberg. "A novel evolutionary algorithm
  applied to algebraic modifications of the RANS stress–strain relationship." *Journal
  of Computational Physics*, 325:22–37, 2016. **The closure form — the modification to
  the stress–strain relationship that the search method searches over.**

**[18] IS NOT HELD.** And the near-miss is worse than a plain absence:

> `docs/papers/closure/_WRONG_RETRIEVALS/Weatheritt2016_evolutionary_rans.pdf`
> is **not** Weatheritt & Sandberg 2016. Page 1, read personally, verbatim:
> *"On the Distinction of Functional and Quality Requirements in Practice / Jonas
> Eckhardt(1), Andreas Vogelsang(2), and Daniel Méndez Fernández(1) /
> arXiv:1611.08830v1 [cs.SE] 27 Nov 2016 / Technical University of Munich ...
> Technische Universität Berlin"*
>
> It is a **software-engineering survey of 103 practitioners about requirements
> engineering.** The filename is right, the author string is right, the year is right,
> and the contents are a different field. It is already correctly quarantined under
> `_WRONG_RETRIEVALS/`; it is cited here because it is the cleanest live instance of
> L-144 in this corpus, and because anyone reaching for [18] by filename will find it.

## 5. Why no defensible `status` exists for this item under SCHEMA v1.0

SCHEMA §6 defines `REGISTERED` as *"schema complete, provenance title-page verified"*.
Provenance is verified. **Schema completeness is not reachable**, and not for one field
but for five, because every one of them requires a paper that describes a turbulence
correction:

| required field | why it cannot be filled |
|---|---|
| `equation_form` | §2 requires "the modification at equation level, with the SOURCE EQUATION NUMBER and page". [17] contains no Reynolds-stress modification at all. The equations it does number are dimensional-transformation rules for expression trees. |
| `validation_cases` | §3 vocabulary is `PH_Breuer`/`Parm_PH_29`/`DUCT`/`CBFS`/`NASA_2DWMH`. [17]'s validation set is the Feynman equation corpus. **No value from the vocabulary is true.** |
| `claimed_effect` | §2 requires "the paper's OWN claim, QUOTED, with its magnitude and its reference data". [17]'s claim is about recovering original equations under noise, not about a flow. |
| `install_stanza`, `model_type_name` | there is no model to install. |

Writing `REGISTERED` here would mean supplying `validation_cases` and `claimed_effect`
from outside the cited paper while the entry asserts they came from it. That is making
the entry fit, and ARCHITECTURE §0 names the cost precisely: an entry that cites a paper
and stops is a bibliography, and a rung-3 negative from a wrongly-implemented correction
is indistinguishable from a correction that genuinely does not help.

**A schema gap, stated plainly:** SCHEMA v1.0 has no state for *"provenance
title-page verified, correction form unsourced."* INGEST_PLAN §2 anticipated exactly
this condition for family (b) — *"we can run the model and cannot yet cite the paper
that defines it"* — and §3 rules on it in the opposite direction (*"An entry may not be
`REGISTERED` on capability alone"*), but neither names a state for the mirror case:
**paper without form.** This is referred, not decided by this lane. See §7.

## 6. What would unblock it, in order of cost

1. **Retrieve [18], Weatheritt & Sandberg 2016, JCP 325:22–37.** This is the single
   blocking artifact. It carries the algebraic stress–strain modification that the
   rank-1 submission searches over, and with it `equation_form`, `install_class` and
   `band_interaction` all become writable. **Institutional pull is Sanaa's; this belongs
   on the retrieval register in INGEST_PLAN §2, and it is not currently on it.**
   *Recommended priority: above the existing Priority 3 items, because it is the only
   absent paper blocking a **rank-1** leaderboard entry we otherwise hold the challenge
   description for.*
2. **Retrieve the challenge submission description for the rank-1 entry**, if one exists
   on the challenge GitHub page. McConkey et al. state (printed p. 5): *"Details from
   each of the early submitters are available on the github page."* We hold exactly such
   a description for the rank-2 entry
   (`wu_zhang_sst_qcrc_challenge_description.pdf`), and it turned out to carry the model
   equations directly. **NOTE: retrieval is not this lane's to perform and nothing is to
   be requested, contacted or fetched from outside this box — SUBMISSIONS AND CONTACT
   ARE PARKED, CLAUDE.md rule 7. This is a note for Sanaa's desk, not an action.**
3. **A related but NOT substitutable holding**, offered so the supervisor knows it
   exists and knows it is not the answer:
   `docs/papers/data_driven_rans/zhao_akolekar_weatheritt_michelassi_sandberg_1902.09075.pdf`,
   page 1 read personally today: *"RANS Turbulence Model Development using CFD-Driven
   Machine Learning / Yaomin Zhao, Harshal D. Akolekar, Jack Weatheritt, Vittorio
   Michelassi, Richard D. Sandberg / Journal of Computational Physics (2020)"*. Same
   group, same GEP lineage, genuinely a RANS closure paper. **It is not [18] and it is
   not the leaderboard entry**, and substituting it would be the same offence in a more
   plausible costume. It could support its *own* entry, which is a separate decision.

## 7. Referred to the supervisor — not decided here

1. **Does SCHEMA v1.0 need a fifth state?** Something like `PROVENANCE-GAP` /
   `BLOCKED-ON-SOURCE`: title-page-verified paper held, correction form unsourced, may
   never be tried and never cited. Alternatively, rule that such items live *only* as
   blocker records like this one and never as entries. Either is defensible; both are
   amendments to a frozen file (CLAUDE.md rule 6) and neither is a lane's call.
2. **If the answer is "write it as an entry with `UNVERIFIED` in `equation_form`"**,
   note that `build_correction_library.py` already supports that path and makes it
   visible rather than silent: an `equation_form` carrying the token `UNVERIFIED` passes
   validation at `REGISTERED`, is refused at `REPRODUCED`, and the generator emits
   `equation_form_unverified: true` into `library.json` so the gap is machine-filterable
   from any exhaustion query. **That path was deliberately not taken here**, because
   `validation_cases` and `claimed_effect` have no such escape and would have had to be
   invented outright. If the supervisor rules that the entry should exist, it can be
   written in minutes against this record.
3. **Rung-3 exhaustion consequence, which is why this matters beyond one file.** Under
   SCHEMA §8 an exhaustion claim counts only `REPRODUCED` entries and must NAME every
   flow-class match excluded, with its reason. This item is a family-(f) correction at
   the **top of the leaderboard**. It must appear by name in the excluded list of any
   duct or hills exhaustion claim, with the reason recorded as: *source paper for the
   correction form (Weatheritt & Sandberg 2016, JCP 325:22–37) not held; cannot be
   implemented, therefore cannot be tried.* An exhaustion claim that silently omits the
   rank-1 entry is the "quietly narrowed until it is true" failure ARCHITECTURE §4 warns
   about.

---

## Readers used, stated so the negative is auditable

- Page 1 of every PDF named above read personally with `pdftotext -f 1 -l 1` and
  transcribed verbatim. Never by filename, file type or hash (L-144) — a rule this
  record exists to demonstrate the value of.
- Every sidecar content search used **`/bin/grep` over explicit globs**, because the
  closure corpus sidecars are invisible to this box's default `grep` (.gitignore +
  ugrep) — L-486. A default-`grep` search here would have returned an empty result set
  that looked like an answer.
- The zero counts in §3 are **planted-controlled**: the same reader returns 16 / 47 / 2
  for `Reynolds` on three sibling papers in the same invocation. A zero from a reader
  not shown able to see a non-zero is not evidence (CLAUDE.md rule 3).
