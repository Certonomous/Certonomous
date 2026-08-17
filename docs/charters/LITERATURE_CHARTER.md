# Certonomous Literature Review Charter

Version 1.3, dated 2026-08-17. Governs every reading the lab does: overnight
reading programs, no-compute review tasks, a single paper fetched to settle an
argument, and any citation that reaches a record, a certificate, a proposal or
a camera surface.

Version 1.1 adds the in-sample reproduction clause to section 7 and the gate
that enforces it to section 8. A reading is where a scored benchmark case gets
proposed as a training case, so the rule has to sit here as well as in the
verification charter. Nothing in 1.0 was weakened.

Version 1.2 records P-2.1's tier half as a landed review aid rather than a
proposal: section 8 now names `sdk/scripts/citation_tier_audit.py`, the two
rules it adopted, the third it measured and did not adopt, and the 2026-08-05
abstract-tier defect all three were written from. Nothing in the tier table
itself changed, and the fourth tier the records use is reported rather than
blessed.

## 1. The line

> **Zero fabricated citations. The record stands at zero and the tolerance is
> zero.**

There is no acceptable rate. A wrong number is a defect and gets corrected. A
citation to something that was never read, or never existed, is a different
kind of event: it means the lab's record cannot be checked by inspection, and
checking by inspection is the only thing that separates this lab from a
confident writer. L-22 already made this point one level up, about attribution
rather than sources, and its conclusion transfers exactly. A register whose
entries are not individually checkable is not a register, it is a rumor with
formatting.

Fabrication includes all of these, not only the invented paper:

- A title, author list, year, venue, DOI or page number that was not read off
  the artifact.
- A number attributed to a paper that the paper does not state, including a
  number correctly recalled from memory but not located in the text this
  session.
- A claim credited to a source that supports something adjacent to it.
- A citation carried forward from another of our own documents without
  re-checking that the original said it. Copying a citation copies its
  reassurance along with its error, which is L-26's corollary about code
  comments applied to bibliography.

## 2. Provenance tiers, and every citation carries one

The lab already runs this discipline. It is written down here because it
worked. `demo-output/website/campaign/LITERATURE_REPRODUCTION_REVIEW.md`
states it in its own header and applies it to every source it names.

| Tier | What it means | What may be asserted from it |
| --- | --- | --- |
| **READ IN FULL** | Full text fetched and read this session. | Anything the text states, quoted or paraphrased, with the location. |
| **PAYWALLED, abstract-only** | Only the public abstract or a search-result excerpt was seen. | Nothing beyond what that abstract literally states. The tier is printed next to the claim, not hidden in a footnote. |
| **INTERNAL, already read** | A prior session in this lab read the full text and reproduced its tables in our own record. | What our record already extracted, with attribution to the session that read it and to the file holding the extraction. |

A source that fits none of these tiers is not a source. There is no fourth
tier for "well known", "standard result" or "widely reported".

**Availability checks are reported, never assumed.** If Unpaywall or a DOI
resolution was attempted and failed, that attempt is part of the record. The
literature review does this explicitly and it is the reason a reader can tell
a paywall from a shortcut.

**Figures count as text.** Where a paper's prose does not carry the number and
the figure does, the figure is fetched and read directly, and the record says
the number came from a figure. A digitised figure value carries the reading
uncertainty of the digitisation, which is usually the limiting uncertainty of
any comparison built on it, and L-28 forbids claiming a difference below a
detector's own increment. The same arithmetic applies to a literature
recollection carrying two significant figures: F2's transonic gate asserted a
third decimal place against exactly that, and the claim did not survive.

## 3. The claim to source to where-it-applies format

Every reading that feeds a lab decision produces rows in this shape. Prose
around them is optional. The rows are not.

| Claim | Source and tier | Where it applies | Where it does not |
| --- | --- | --- | --- |
| The one thing being carried forward, stated as a sentence with its number. | Author, year, venue, and the provenance tier from section 2. Page, table or figure. | The regime, geometry class, Reynolds or Mach range, and mesh class in which we may use it. | The nearest place we might be tempted to use it and must not. |

The fourth column is the one that does work. A claim with no stated domain
gets used outside its domain, and the lab has already paid for this twice:

- L-23. A discharge-coefficient correlation with no stated beta limit was used
  as a sweep objective, and the optimiser walked straight to the edge where the
  correlation has no valid limit at all. The fix was one line of algebra at the
  physical extremes, and it was a stronger statement than 1.35 core-hours of
  CFD.
- The Cappelli and Mansour hump paper reads carefully on every axis and never
  states a convergence criterion, which our own review records as its single
  largest reproducibility gap. That absence is a finding about the domain in
  which its numbers can be reproduced, and it belongs in the fourth column.

**An omission is a finding.** Where a paper withholds a quantity needed to
rebuild its result, that omission is recorded as the outcome of the reading. It
is not smoothed over, and it is not filled in from a similar paper.

## 4. Sources allowed

Allowed, in the order the lab prefers them:

1. **Peer-reviewed archival papers and reports**, read at the tiers above.
   Sandia, NASA NTRS, AIAA, JCP, JFM and their equivalents.
2. **Standards and their published test cases.** ASME V&V 20-2009, ISO 5167,
   the NASA Turbulence Modeling Resource, the Drag Prediction Workshop and
   Aeroelastic Prediction Workshop case definitions. These are reference
   identities and stay on camera under the demo discretion charter.
3. **Solver source code and its documentation**, when the question is what the
   software does rather than what the physics is. Read the class, not the
   dictionary entry, and not the comment. L-20 and L-26 are both this failure.
4. **Textbook results and closed-form theory**, cited to a specific edition and
   section.
5. **The lab's own campaign records**, cited by file and section, and only for
   what they measured.

Not allowed as the basis of any claim: a title, an abstract used beyond its own
sentences, a citation count, a preprint's press coverage, an encyclopedia
entry, or another paper's characterisation of a third paper. The last one is
the most tempting and the most common way a wrong number propagates.

**Preprints are allowed and are labelled as preprints.** The random-matrix
framework the lab implemented in full comes from an arXiv preprint, was
verified against fifteen of the paper's own stated properties with zero
failures, and produced a negative result the lab published. That is the correct
handling: a preprint can be reproduced, and reproduction is what upgrades it.

## 5. Citation discipline on the record and on camera

**On the record.** Every number carries its source at the point of use, not in
a bibliography at the end. A reader must be able to check any single line
without reading the document.

**On camera.** The demo discretion charter governs, and its rule is that a
cited standard is a reference identity and stays. "Graded against the standard
acceptance band, per published mesh-quality guidance" keeps the identity of
what we were graded against. What comes out is the recipe, never the reference.
Nothing in this charter may be used to remove a reference identity from a
camera surface, and nothing in the demo charter may be used to remove a
citation from a record.

**Links render as the word "source" and never as a raw URL.** That is an
existing product rule and it survives here unchanged.

## 6. When a reading MUST produce a proposal

A reading that ends in a summary has cost core-minutes and bought nothing the
lab can run. Four triggers make a proposal mandatory rather than optional. If
any of them fires, the reading does not close until a proposal JSON exists in
the agenda inbox.

1. **The paper states a number on a case we can build.** Geometry, conditions
   and a graded quantity are all present. That is a reference the wall can use,
   so it becomes a proposal to run it. This is the trigger that fired on the
   hump, the periodic hill and the cylinder ladder.
2. **The paper describes a method whose admissibility could be written as
   thresholds.** `docs/standards/INNOVATION_STANDARD.md` stage 3 says
   admissibility becomes numbers in `docs/physics_rules.yaml` and never
   constants in workflow code. A reading that could produce those numbers must
   propose them.
3. **The paper disagrees with one of our results.** A disagreement between a
   published number and ours is either their limitation, our defect, or a
   difference in what was measured, and all three are worth one experiment. The
   proposal names which of the three the experiment would distinguish.
4. **The paper's own limit case is checkable at zero compute.** L-23. Write the
   correlation at both ends of the design range by hand and state what it does
   there, before anything is scheduled.

A reading closes with a summary only when it fires none of these, and the
record says which trigger was checked and why it did not fire. "Interesting but
not actionable" is not an acceptable closing line. Name the trigger.

## 7. NEVER

- Assert anything from an abstract that the abstract does not literally say.
- Upgrade a tier without re-reading. An INTERNAL citation does not become READ
  IN FULL because someone is confident.
- Reproduce a paper's number to more significant figures than the paper printed.
- Attribute a mechanism to a source that reported a correlation.
- Let a sub-agent inherit the reading constraints implicitly. L-18: a no-compute
  literature brief that was not restated to a spawned fork ended with that fork
  launching a 57 minute solve producing negative drag on a wing. Every brief
  restates the no-compute status, the budget and the citation discipline,
  however obvious they seem.
- Cite this lab's own document as evidence for a claim that document itself
  attributed to someone else. Go to the original.
- Reproduce a paper's method on a case this lab is scored on, and report the
  result as generalization. A reading is where this one enters: a paper names
  the case it inverted on or trained on, the case is available in our benchmark
  clone, and reproducing it there is the obvious next step. If that case is
  scored, the reproduction is in-sample by construction however faithfully the
  method was copied. `NASA_2DWMH` is the live instance: it is one of the
  closure challenge's eight scored test cases and it carries published
  experimental skin friction, so it reads as an invitation. A proposal arising
  from a reading names the cases its method would fit on, and names them
  against the scored list, before it is filed. Verification charter section 11
  carries the rule; this is the intake side of it.

## 8. Enforcement

There is no script for the citation discipline itself, and saying so is more
useful than implying there is.

What exists:

- The provenance tiers are self-enforcing in review, because a citation without
  a tier is visible at a glance.
- `sdk/scripts/closure_in_sample_gate.py` covers the last NEVER above. It reads
  every training, fitting, inversion and calibration set declared in the repo
  and fails on any that contains a benchmark case this lab is scored on, with
  the scored list derived from the benchmark's own README rather than retyped.
  It does not read intent, only declarations, so a proposal that has not been
  written down yet is still on the reader.
- `docs/DEMO_DISCRETION_CHARTER.md` section 4 already forbids a comparison
  against an unnamed reference on camera, and `scripts/audit_transcripts.sh`
  runs over the camera surfaces.

**P-2.1's tier half, CARRIED OUT 2026-08-05 as a review aid at WARN, under
the standing charter-iteration directive.**
`sdk/scripts/citation_tier_audit.py` runs over the charters, the standards,
the docket and the website records. It reports and never repairs, its exit
status stays 0 unless `--strict` is given, and a block carrying its own dated
correction is not reported again.

Two rules are adopted, and each reads a clause of this charter:

- **A quantity asserted beside a tier below READ IN FULL.** Section 2's table
  and section 7's first NEVER. The checker cannot read the abstract, so it
  cannot know whether the assertion is literal; what it sees is the shape the
  defect takes, a number standing beside a tier that licenses no numbers.
- **A tier this charter does not define.** Section 2 says there is no fourth
  tier, and SEARCH-EXCERPT is one. It was coined in a liaison memo and reads
  as narrower than PAYWALLED. Reported, not rewritten: whether this charter
  gains the tier or the records lose it is the owner's call.

**A third rule was measured and NOT adopted**, which is charter 1
disqualifier 10 applied to this file's own checker. The original proposal's
"citation-shaped string with no tier in the same block" fires on 24 blocks of
the 392 records, 19 in one file, 15 of them rows of published
reference-comparison tables. That is the false-positive family P-2.1's own
entry predicted and the shape of the withdrawn S7. It ships behind
`--untiered`, off by default, with the replay recorded in the module's own
docstring.

**The incident that motivated the adopted rules, on the record.** The DAFoam
journal paper was cited at abstract tier for "average adjoint derivative
error under 0.1 percent at up to 1536 cores", and the full read on 2026-08-05
found the abstract joining two disjoint experiments: the 1536 cores is a
runtime-only scaling measurement on a 10.1M-cell mesh, the under-0.1 percent
an accuracy study on 102,912 cells at an unstated core count, both belonging
to an architecture the lab's measurement did not touch. An upstream bug
report's framing had been built on the join.
`demo-output/website/dafoam/DAFOAM_PAPERS_VERIFICATION_PROTOCOLS.md` section
5 carries the corrections, commit `bf6ac53b`. Every one of them was found by
a person reading the paper; nothing mechanical looked at the tier.

## Related

- `demo-output/website/campaign/LITERATURE_REPRODUCTION_REVIEW.md`. The reading
  this charter is written from.
- `docs/standards/INNOVATION_STANDARD.md`. Stage 1 requires a literature basis
  on the record before a method is admitted at all.
- `docs/charters/VERIFICATION_CHARTER.md`. Section 11 carries the in-sample
  rule in full; section 12 carries the gate.
- `docs/charters/GOALS_AND_PROPOSALS_CHARTER.md`. What a proposal has to
  contain once a reading triggers one.
- `LESSONS.md` L-18, L-20, L-22, L-23, L-26, L-28.

## Amendment record

**Version 1.3, dated 2026-08-17. A style amendment, measured at frame `101079fd`.**
The sections above were brought to the owner's standard for a durable
record: em dashes and en dashes replaced by ordinary punctuation, and the
result of each replacement read back against the clause it sits in.

| what the amendment did | figure |
| --- | --- |
| em dashes replaced in the live sections | 0 |
| en dashes replaced in the live sections | 0 |
| em dashes left standing inside dated records | 0 |
| en dashes left standing inside dated records | 0 |
| clauses opened and declined, listed below | 1 |
| lines whose number changed above this section | 0 |

**No clause was added, removed, widened or narrowed, and no modal, scope or
tense inside a clause was altered.** Both the counts above and the gates were
taken in a detached worktree held at frame `101079fd`, so that a peer's
concurrent commit could not be read as part of this batch. The gates run either
side of the edit were `scripts/check_verdict_cells.py` with and without
`--selftest`, `scripts/check_absolutes.py`,
`scripts/check_normative_clauses.py`, `scripts/withdrawal_sweep.py`,
`scripts/self_audit.py` and `scripts/lab_check.py --no-tests`; the `sdk/tests`
suite was run either side in the live checkout. No gate moved its verdict. `check_absolutes.py` moved its verdict
COUNTS and not its verdict, and the movement was traced to the
sentences of this record rather than to the sections above.

**The line numbering above this section was held fixed on purpose.** Other
records cite this directory by line, and one of those citations sits inside an
executable check. An amendment that inserted its own changelog at the head of
the file would have moved the cited lines below it, so this record was appended
at the foot instead. The version-history entries above stand unedited, because their
figures describe the versions and the dates they name.

**What was opened and left alone.**
1. The measured counts for this file at frame `101079fd` stood at 0 em dashes, 0 en dashes, 0 personal names as actors and 0 sites of the framing this standard removes, so the amendment reached the version line and stopped there.
