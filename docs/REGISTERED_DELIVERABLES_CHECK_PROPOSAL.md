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

---

# APPENDIX A, dated 2026-08-23 — implementation, planted controls, motivating-case fire, and the archive replay (D473)

**Appended at the foot. Nothing above this line is altered; lines whose number
changed above this section: 0.** The binding clause in §3 remains a DRAFT and is
untouched. Nothing in this appendix wires the check into a gate, into CI, or into
any charter; adoption is Sanaa's alone. Every number below is **CANDIDATE** until
the verification supervisor has read the instrument in full.

## A.1 What was implemented

`scripts/check_registered_deliverables.py`, to the §2 spec: declared mode
(binding, prospective) over a fenced `## REGISTERED DELIVERABLES` block with the
prereg hashed against its committed blob first; heuristic mode (report-only,
retrospective) over prose. Exit 0 clean / 1 usage / 2 refusal. `--strict` is the
switch a ratification would flip and is **off**; `--report-only` prints every
refusal and exits 0, naming the count it suppressed.

Three tightenings were taken against the literal §2 wording, each **lowering**
the fire rate and each named in the script's own docstring: the commitment-verb
list is exactly §2's five lemmas and is not extended; `ship` must be verbal
(`the shipped baseline`, `A6's shipped runScript.py` are adjectival); `land`
must carry a preposition. Two further readings were forced by the archive and
are recorded in A.4.

## A.2 Planted controls — the four §2 requires, plus four

`--selftest` builds a throwaway git repository of synthetic rungs, so the freeze
hash, the close-out commit and the input-exclusion tree are exercised for real
rather than stubbed. **`--selftest` exits 0 with all eight controls green.**

| control | plants | verdict | exit |
|---|---|---|---|
| **C1** (§2) | a prereg naming an existing file | `PRESENT` | 0, silent |
| **C2** (§2) | a missing file the dated departure section names | `ABSENT-DISCLOSED` | 0, silent |
| **C3** (§2) | a missing, undisclosed file | `ABSENT-UNDISCLOSED` | **2, fires** |
| **C4** (§2) | a deliverable visibly named, on which extraction returns zero candidates | `CANNOT-PARSE` | **2, refuses** |
| C5 (extra) | a `REGISTERED DELIVERABLES` heading whose fenced block is missing | `CANNOT-PARSE` | 2 |
| C6 (extra) | a declared block whose prereg no longer matches its committed blob | freeze mismatch | 2 |
| H1 (extra) | heuristic prose `written to \`MODEL.md\``, delivered | `PRESENT` | 0 |
| H2 (extra) | heuristic prose naming a file that predates the freeze | `INPUT-EXCLUDED` | 0 |

C4 is the planted zero (CLAUDE.md rule 3). A **second, independent** reader —
the backstop — scans commitment sentences with every backticked span removed
first, so it sees only what the primary extractor structurally cannot. Primary
empty + backstop non-empty is `CANNOT-PARSE` and a refusal, never a clean pass
over an empty population.

**Mutation evidence — each of the four was shown able to fire.** A scratch copy
of the script was mutated at one reader, `__pycache__` cleared, `--selftest`
re-run, then restored; pristine copy exits 0 before and after.

| mutation | reader broken | `--selftest` exit | controls that failed |
|---|---|---|---|
| M1 | presence reader blinded | 1 | C1, C6, H1 |
| M2 | disclosure reader blinded | 1 | C2 |
| M3 | disclosure reader stuck open | 1 | C3 |
| M4 | independent backstop blinded | 1 | C4 |

## A.3 The motivating case — R4 §7, both runs recorded (§2 adoption step 2)

Pre-repair state read from commit `cb185d97` (the commit before `918e8fe7`, the
D-14 addendum), with `--at`, so no working-tree file was touched:

```
python3 scripts/check_registered_deliverables.py \
  --prereg cases/RANS_LES_closure_models/R4_sparta_build/PREREGISTRATION.md \
  --at cb185d97
```

→ **`ABSENT-UNDISCLOSED  COVERAGE.md  <- FIRE`**, resolved to
`cases/RANS_LES_closure_models/R4_sparta_build/COVERAGE.md`, named at
`PREREGISTRATION.md:201`, "named in no departure or disclosure section". Exit 0
(heuristic is report-only); the same invocation with `--strict` **exits 2**.
The rung's other two prose candidates read correctly beside it: `MODEL.md`
`PRESENT`, and `_common/uq_eigenspace/UQ_EIGENSPACE.md` `INPUT-EXCLUDED`
(it predates the freeze commit `b36daf06`, so it is an input, not a product).

Post-repair state, working tree, same invocation without `--at`: **`PRESENT`**,
exit 0. §2 anticipated `ABSENT-DISCLOSED` here; the record diverged because
closure's repair **delivered the file late** rather than only disclosing the
non-delivery. Both runs are recorded, as §2 requires, and the divergence is
noted rather than tidied.

**The rule discriminates its own motivating case** — the charter §5 clause whose
failure withdraws a rule.

## A.4 Archive replay (charter §5) — the fire rate, published

Every tracked `*PREREGISTRATION*.md` in the repository, heuristic mode,
`--report-only`:

| | |
|---|---|
| pre-registrations found | **111** |
| NOT-CLOSED-OUT / unreadable (not graded) | 32 |
| **records scanned** | **79** |
| declared-mode rungs | 0 (no block exists yet anywhere) |
| `CANNOT-PARSE` refusals | **0** |
| **FIRES (≥1 `ABSENT-UNDISCLOSED`)** | **9** |
| **FIRE RATE** | **9/79 = 11.4%** (10 fired tokens) |

The nine fired pre-registrations: `Wu2018_PIML_RF/aposteriori`,
`ladder-a/A3/rung2_patched_idwarp_np4`, `ladder-a/A6/rung_n16_fixed_reference`,
`ladder-b/S1_CBFS_INVERSION`, `ladder-b/S1_PRIORS`, `ladder-b/S1_WITH_PRIORS`,
`T-family/T5_PREREGISTRATION_DRAFT`, `verification/campaign/CUBE_SAIL_DRAW_SCATTER`,
`verification/campaign/F6a_DIFFUSION`.

**The zero is planted, not assumed** (rule 3). On the same 79 records the
primary extractor saw a candidate in **37** documents and the independent
backstop saw one in **1**; a `CANNOT-PARSE` is backstop-sees-and-extractor-does-not,
so both readers are live on this corpus and the zero is a reading. Honest limit:
one document is a thin corpus-level plant, and the strength of that zero rests
mainly on C4 and its M4 mutation.

**Two readings were forced by the replay and are recorded as measurements, in
the S7 manner** — the tightening, and what it moved:

| resolver / reader | fire rate |
|---|---|
| first implementation | 27/83 = 32.5% |
| + markdown table rows read as independent sentences | 22/83 = 26.5% |
| + possessive `A6's shipped X` read as adjectival | 19/79 = 24.1% |
| + a token resolved to the unique tracked path whose tail matches it | **9/79 = 11.4%** |

Joining markdown table rows into one sentence let a commitment verb in one cell
attach to a path cited in another; a table is a list of independent statements
and is now read as one. A close-out record was also being paired across rungs
(a sibling rung's `RESULTS.md`), which read that rung's departures as this
one's; §2's unit of analysis is one directory and the pairing is now confined to
it, which moved four rungs from graded to NOT-CLOSED-OUT.

### The false-positive reading, and it is the load-bearing half

Reading all ten fired tokens against their naming sentence: **at least eight are
false.**

- **Six are citations, not promises** — `BUILD.md` §7, `mphys_dafoam.py`,
  `cbfs_beta/runScript.py`, `analyse_t5.py`, `birth_certificate.json`,
  `hump_gate_analysis.py`. The commitment verb belongs to a neighbouring clause
  of the same sentence; the path is cited, not registered.
- **At least three shipped OUTSIDE the repository**, where the lab deliberately
  keeps large run data: `fields_report.json` exists at
  `/home/ubuntu/closure-data/aposteriori/wu2018/`, and the ladder-b run ledgers
  at `/home/ubuntu/certonomous-runs/*/ledger.csv`. The checker reads inside the
  repository only, so those read ABSENT. **This is the single largest false-fire
  source in heuristic mode.**
- At most two survive as candidate-true, and both are weak:
  `S1-priors/ledger.csv` (no `S1-priors` run directory exists — plausibly an
  unrun arm rather than an undisclosed non-delivery) and
  `T5_reference_primary.json` (in a **DRAFT** pre-registration, whose rung has
  not run).

**Reading, stated plainly: heuristic mode on this archive is measuring the
population's prose habits and the in-git/out-of-git storage split, not the
defect.** It clears charter §5's withdrawal bar — it discriminates its motivating
case, and 11.4% is far from S7's two-thirds — but its retrospective precision is
poor, and nothing here supports making heuristic findings binding on
pre-2026-08-23 rungs. That is exactly the split §2 already registered, now with
a number behind it.

## A.5 What is on Sanaa's desk, unchanged

The §3 clause, still a DRAFT and still hers alone to ratify or refuse, and with
it the separate question §3 already names: whether heuristic-mode findings on
pre-2026-08-23 rungs ever become binding. The replay's answer to that second
question is **no on this evidence**. Declared mode has never yet run on a real
rung, because **no pre-registration in the repository carries a `REGISTERED
DELIVERABLES` block** — the prospective half is unexercised outside its planted
controls, and its first real exercise would be the first new pre-registration
written after a ratification.

## A.6 Cost

Zero solver compute; zero core-minutes of solver time. Implementation, selftest,
mutation evidence and two archive replays are reads and greps on the head node.
