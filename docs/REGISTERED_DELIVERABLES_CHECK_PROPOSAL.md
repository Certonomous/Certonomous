# Registered-deliverables close-out check — proposal (verification team, 2026-08-23)

**Routed by the chief from the closure supervisor's R4 finding:** R4's frozen
pre-registration §7 registered a deliverable (`COVERAGE.md`, *"ships with
`MODEL.md`"*, `PREREGISTRATION.md:199-201`) that was never delivered and never
disclosed among the rung's thirteen dated departures. The failure mode —
**registered deliverable absent and undisclosed at close-out** — escaped every
existing control, because a prose-registered deliverable is not a gate, so no
gate row ever counted it, and the departure discipline only catches departures
somebody noticed. The R4 instance's repair (dated departure addendum + lesson)
is closure's and is already dispatched; **nothing here touches it.**

## 1. Evaluation: yes to an executable check; the binding clause is Sanaa's

The class is checkable by construction: a frozen pre-registration is on disk,
the artefacts it names either exist at close-out or do not, and a departure
section either names an absent one or does not. That is the shape of a check,
not of a review habit. A charter sentence alone would be the "paragraph written
twice" pattern the lab already rejected (CLAUDE.md rule 14's provenance): a
defect class that has bitten gets an assert, not prose.

Two constraints from the lab's own law bound the design:

- **Charter §5 (archive replay):** a new detection rule is replayed against the
  archive before adoption, with its fire count published, and a rule that
  cannot discriminate its own motivating case is withdrawn. The motivating
  case here is R4 §7: **the check must fire on it.**
- **Charter §17a (over-reach):** old pre-registrations never promised a
  machine-readable deliverables list, and prose parsing over them will have
  false reads. So the check is **binding prospectively, report-only
  retrospectively** until the replay's fire rate is measured and published.

## 2. The check's spec — `scripts/check_registered_deliverables.py`

**Unit of analysis:** one rung = one frozen `*PREREGISTRATION*.md` plus the
close-out record (`RESULTS.md` or the record the prereg names) in the same
directory.

**Two modes:**

1. **Declared mode (binding, prospective).** A pre-registration MAY carry a
   fenced block headed `## REGISTERED DELIVERABLES` — one repo-relative path
   per line, optionally with a one-line description. If the block exists:
   every listed path must, at close-out, be either PRESENT on disk (and, where
   the block says `committed`, present in the close-out commit) or named in a
   dated departure/disclosure section of the close-out record. Any listed path
   ABSENT-UNDISCLOSED → **refuse close-out, exit 2**. The block is frozen with
   the prereg; the check hashes the prereg against its committed blob first
   (rule 2's own verification, reused).
2. **Heuristic mode (report-only, retrospective).** Where no block exists:
   extract candidate deliverables from the prereg prose — backtick-quoted
   tokens matching artefact shapes (`*.md`, `*.json`, `*.py`, `*.csv`,
   `artefacts/*`) in sentences containing a commitment verb (ships, is
   written, is committed, lands, is recorded), excluding paths inside code
   fences and paths that are inputs rather than products (already exist at
   prereg commit time — checkable against the prereg's own commit). Classify
   each: PRESENT / ABSENT-DISCLOSED / ABSENT-UNDISCLOSED / CANNOT-PARSE.
   Report; never exit nonzero on heuristic findings until adoption is ruled.

**Planted controls (`--selftest`), all four required:**
- a prereg naming an existing file → silent;
- a prereg naming a missing file that the results' departure section names →
  ABSENT-DISCLOSED, silent;
- a prereg naming a missing, undisclosed file → **must fire**;
- the planted-zero principle: a prereg that visibly names a deliverable on
  which extraction returns zero candidates → **CANNOT-PARSE, refuse**, never a
  clean pass over an empty population.

**Adoption sequence (charter §5, none skippable):**
1. Implement with selftest.
2. Fire on the motivating case: R4 §7 `COVERAGE.md` → ABSENT (disclosure state
   read from the record as it stands after closure's repair lands:
   ABSENT-DISCLOSED then, ABSENT-UNDISCLOSED against the pre-repair record —
   both runs recorded).
3. Archive replay over every `*PREREGISTRATION*.md` in the repo; publish the
   fire count, the per-finding classification, and the false-positive reading.
4. Only then: the binding question goes to Sanaa (§3 below). Until her ruling
   the checker runs report-only everywhere and binding nowhere.

## 3. Charter clause — DRAFT for Sanaa's ratification, not in force

> **Proposed VERIFICATION_CHARTER addendum (would be appended at the foot,
> lines above unmoved):** *An artefact a pre-registration promises is a
> registered deliverable of the rung. Close-out states, for every registered
> deliverable, PRESENT or a dated departure; a registered deliverable absent
> and undisclosed at close-out is a §9 evidence-record violation. New
> pre-registrations enumerate their deliverables in a machine-readable
> `REGISTERED DELIVERABLES` block; `scripts/check_registered_deliverables.py`
> is the binding artifact and refuses close-out in declared mode.*

Ratifying this — and the choice of whether heuristic-mode findings on
pre-2026-08-23 rungs ever become binding — is **Sanaa's**, per the standing
rule that retiring or adding a standard is reserved to her. This document and
the implemented checker land on her desk together with the replay numbers.

## 4. Cost

Zero solver compute. Implementation + selftest + archive replay is one lane at
reads-and-greps cost.
