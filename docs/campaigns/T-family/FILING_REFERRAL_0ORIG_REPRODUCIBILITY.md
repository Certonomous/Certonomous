# FILING REFERRAL — `0.orig/` AND T-FAMILY REPRODUCIBILITY

**Date:** 2026-08-31
**From:** heat-transfer
**To:** the chief, **for routing** — FILING_CHARTER is not heat-transfer's to amend
**Type:** REFERRAL. This document decides nothing and proposes no edit to any file.
**Source:** `docs/campaigns/T-family/AGE_GUARD_REFERENT_AUDIT.md`, committed at
`aadc7bcf`; its §9 ruling committed at `7673c393`.

---

## 0. Why this is referred rather than decided

The age-guard audit was commissioned to answer a narrow question about the mtime
referent `0/T`. That question is now **closed by ruling** (audit §9, commit `7673c393`):
run-tree `0/` is **not** to be tracked, because git carries content and the guard reads
mtime, so tracking it would not restore what a `git clean` destroys.

The audit uncovered something **larger than the question it was asked**, and that larger
thing is not heat-transfer's to rule on:

> Of the T-family run cases carrying a thermal age-guard referent, a **majority have no
> tracked `0.orig/` either** — so those cases **cannot be regenerated from git at all.**

That is a **reproducibility gap**, not an mtime subtlety. And `0.orig/` is **case
definition rather than run output**, so the FILING_CHARTER reasoning that keeps `0/` out
of version control does not obviously reach it. Deciding it means reading — and possibly
amending — FILING_CHARTER R6, which belongs to whoever owns that charter, not to the
family that would benefit from the answer.

**Scope, stated once and binding on this whole document: this referral asks about
`0.orig/` ONLY. It does not reopen `0/`, which heat-transfer has ruled on.**

---

## 1. The counts, re-verified

Every figure below was **re-derived independently** for this referral at HEAD
`62ceaac0`, by the method the audit's §2 states — walk `verification/runs/T-family/`;
a directory is a **case** if it holds `system/` or `constant/` or a `log.solve*`, and a
**run case** if it holds a `log.*`, a `STATUS*`/`DONE*` marker, or more than one numeric
time directory; tracking resolved against a single `git ls-tree -r HEAD` snapshot
(2,763 tracked files under the tree). The four commits that landed while this referral
was being written were checked and **none touched `verification/runs/T-family/`**, so the
census is not stale.

| Population | Re-verified | Audit §2 |
|---|---:|---:|
| Run cases under `verification/runs/T-family/` | **263** | 259 |
| — with a thermal age-guard referent (`0/T` or `0/<region>/T`) | **212** | 213 |
| — — referent **UNTRACKED** at HEAD | **208** (98.1%) | 209 (98.1%) |
| — — referent **TRACKED** at HEAD | **4** | 4 |
| — with `0/` but **no `T`** inside it (referent does not apply) | **45** | 45 |
| — with **no `0/`** at all | **6** | 1 |

Of the **212** referent-bearing run cases, the state of `0.orig/`:

| `0.orig/` state | Re-verified | Audit §2 |
|---|---:|---:|
| present and **TRACKED** | **85** | 85 |
| present and **UNTRACKED** | **127** | 127 |
| **absent entirely** | **0** | 1 |

**The headline for this referral: 127 run cases have NEITHER a tracked age-guard
referent NOR a tracked `0.orig/`.** For those cases the rebuild source is untracked, so
the case cannot be regenerated from git at all — let alone re-verified. (The audit's
figure was 128; the difference is the single T5 case discussed at §3 below.)

The four tracked referents are all in `T11_runs`, all flat `0/T` — `T11_PW_c`,
`T11_PW_f`, `T11_PW_f_CT`, `T11_PW_m` — and their tracking is incidental rather than
policy, since no other rung shows it.

---

## 2. The exclusions, stated honestly rather than absorbed

**45 run cases have a `0/` that holds no `T`.** The age guard's referent does not apply
to them and they are excluded from the 212 denominator. Their shapes, counted:

- **34** hold **`viewFactorField` only** — all in `T10aVF_runs/cases/`;
- **10** hold **`U` and `p` only**;
- **1** holds **`U k nut omega p`** — `T5_runs/X_2d`.

*Correction to a figure circulated with this task:* the last two lines are **10 and 1**,
not "11 U/p-only". `X_2d` is a turbulent isothermal case, not a `U`/`p` case, and it is
the same directory that produces the T5 discrepancy at §3. The distinction is small but
it is the whole of that discrepancy, so it is stated rather than rounded.

**6 run cases have no `0/` at all.** Five are **built but never solved** — they hold
`0.orig/`, `constant/`, `system/` and a `log.blockMesh`, and qualify as "run" cases only
because `log.blockMesh` matches the audit's `log.*` test:
`T19_runs/{P_q_f, P_q_m, P_Ts_f, P_Ts_m}` (built 2026-08-27) and
`T25_MODULE_runs/T25_MOD_L1` (built 2026-08-31 22:23). The sixth,
`T1_runs/P_10k.attempt1_stale`, declares itself stale in its own name.

---

## 3. The audit's unresolved discrepancy — stated, not hidden

The audit's §8 discloses that **an independent enumeration by a different method
(`find` for `system/controlDict`, then filtering on a `log.*`) returned 263 run cases
against the audit's 259, and the 4-case gap was NOT resolved.**

**It is still not resolved, and this referral's re-derivation lands on 263** — the
higher of the two figures. What can now be said about the gap:

- The re-derivation finds **5 more no-`0/` cases** than the audit (6 against 1). Four of
  them are the built-but-unsolved `T19_runs` cases of §2, which existed on 2026-08-27
  and should have been within the audit's reach; the fifth, `T25_MOD_L1`, was built at
  22:23 on the audit's own evening and may simply postdate its walk.
- The re-derivation finds **one fewer referent-bearing case** (212 against 213), and the
  entire difference is in **`T5_runs`**: the audit tallies 8 untracked referents there,
  the re-derivation finds 7. `T5_runs` holds exactly seven cases with a `T`-bearing `0/`
  (`H_c`, `L_m`, `P_m`, `S_m`, `T5_CUBE_c`, `T5_CUBE_f`, `T5_CUBE_m`). The eighth
  directory, `X_2d`, has `0/` = `U k nut omega p` with **no `T` anywhere beneath it**,
  and is already counted among the 45.
- Correspondingly the audit's **"`0.orig/` absent entirely: 1"** does not reproduce:
  **no referent-bearing case lacks `0.orig/`.** 38 cases lack `0.orig/` on disk, and all
  38 are `viewFactorField`-only or under `T10aVF_runs/reproducer/` — none referent-bearing.
- Net: **+5 − 1 = +4**, which is exactly §8's unexplained gap. The arithmetic is
  consistent, but **that is a reconciliation of the totals, not a demonstration of the
  cause**, and it is not offered as one.

**Nothing in this referral's argument turns on 263 versus 259, nor on 127 versus 128.**
The gap is real at either figure, and it is disclosed here so that whoever routes this
is not later surprised by it. The audit's §2 was **not** rewritten to match; the
divergence is recorded as an appended amendment at its §9.6.

---

## 4. The `.gitignore` finding — and the zero is evidence

**No `.gitignore` rule causes `0/` or `0.orig/` to be ignored anywhere under
`verification/runs/T-family/`.** There is no `.gitignore` file anywhere under that tree.

Established authoritatively rather than by pattern-reading: `git check-ignore --stdin -v`
was run over **all 208 untracked referent paths** and returned **zero matches**
(exit 1, no output).

**Planted control (rule 3) — re-run for this referral.** A zero from a reader not shown
able to see a non-zero is not evidence. The **identical invocation**, with two
known-ignored paths spliced into the same stdin list, returned **both**, each with its
matching rule cited:

| planted path | matched by |
|---|---|
| `verification/runs/R4_runs/processor0/PLANT` | `verification/runs/R4_runs/.gitignore:4:processor*/` |
| `verification/runs/D5_rsm_runs/anycase/0/T` | `.gitignore:59:verification/runs/*_runs/*/[0-9]*/` |

The reader is therefore **proven able to see a non-zero in the same call that returned
the zero**, and the zero over the 208 real paths is evidence.

### 4.1 Why the existing rules do not reach the T-family

The second planted path is the instructive one. `.gitignore:59`
(`verification/runs/*_runs/*/[0-9]*/`) **does** ignore a `0/` — but only where the first
segment under `verification/runs/` is itself `*_runs`. T-family paths are
`verification/runs/T-family/<rung>_runs/<case>/0/…`: the campaign segment `T-family`
intervenes, and a `*` glob does not cross `/`.

That is not an accident, and the file says so in its own words. `.gitignore:148-151` and
`:235-242` record that the `*_runs`/`*_work` spelling was chosen **deliberately** so the
rules would **not** reach campaign-segmented trees — `:238-241` warns that a
`verification/runs/**` spelling *"would therefore reach the F14 cooling-ladder lane's
run trees the moment R25 lands … and it would do it silently, to another lane's next
solver log."*

**So the T-family's untracked `0.orig/` is not the product of any rule. No rule reaches
it.**

### 4.2 The repository's own written policy is SPLIT — and on `0.orig/` it is not

Both halves are quoted, because presenting only one would misrepresent the file:

- **`.gitignore:160-161`** (K2b block) — *"`0.orig/` is case INPUT and must travel, `0/`
  and every solved time directory are OUTPUT."*
- **`.gitignore:183-185`** (BATCH 2 block, citing `MOVE_MAP_2026-08-16.md` §7.2) —
  *"Case dictionaries (`system/`, `constant/`) and initial conditions (`0/`, `0.orig/`)
  are source -- they regenerate the run -- while solver time directories and solver logs
  are output, rebuilt by re-running it."*

The two blocks **disagree about `0/`**: `:161` calls it output, `:183-185` calls it
source. That disagreement is not this referral's business — heat-transfer's ruling
disposes of `0/` on other grounds entirely.

**They agree completely about `0.orig/`.** Both call it case input / source that must
travel. There is **no** written policy anywhere in the file classing `0.orig/` as output.

And the rules are spelled to match. `.gitignore:243-250` use **`[1-9]*/`** and
**`0.[0-9]*/`**, not `[0-9]*/`; `:213-225` record why, explicitly: *"`[0-9]*/` matches
`0/` and `0.orig/` too -- case INPUT … These two patterns never match `0` or `0.orig` in
the first place."* The stated motive was avoiding a costly re-inclusion (572 files), not
protecting `0.orig/` for its own sake — but the **effect** is deliberate and documented:
the batch-2 rules leave `0.orig/` trackable on purpose.

**Conclusion on the `.gitignore` question: the untracked `0.orig/` under the T-family is
an OVERSIGHT — an omission from the tracking sweep, not an exclusion by it — and the
repository's existing written policy leans toward tracking it.**

---

## 5. Why FILING_CHARTER's reasoning does not obviously settle it

The rule in play is **FILING_CHARTER R6**:

> *"An OpenFOAM case lives under `verification/runs/<CAMPAIGN>/`, `cases/`, or `models/`.
> … `models/` holds reference case **definitions** (inputs); `verification/runs/` holds
> run **outputs**."*

R6 draws a clean binary between input trees and output trees. **`0.orig/` breaks the
binary**: it is unambiguously a case *definition* that lives, by design and by the
launcher's own construction, **inside** the run-output root. The launcher
(`run_one_t20.sh:184-189`) arms `0/` from `0.orig/` and refuses a case that has no
`0.orig/<region>` to arm from (`:145`), so `0.orig/` is the authored artifact and `0/`
is the manufactured one. R6 classifies *trees*; the question here is about a *directory
inside* a tree whose class is the opposite of its parent's.

There is a **precedent in the charter itself, and it cuts toward tracking.**
FILING_CHARTER §3 records that R6's first draft flagged `models/tmr/**` — reference case
definitions living outside a run tree — and that **"the rule was wrong, not the tree"**,
so the rule was corrected rather than the files moved. `0.orig/` is the mirror image:
case definitions living *inside* a run tree. Whether the same correction is owed is
exactly what this referral asks and does not answer.

---

## 6. THE QUESTION, narrowly

1. **Should `0.orig/` be tracked for all cases** — so that a case's authored inputs
   survive a `git clean` and the run can be regenerated from git?
2. **Whose decision is that** — FILING_CHARTER's owner, ruling once for the repository;
   or each family, for its own tree, within a principle the charter states?

Nothing else is asked. In particular this referral does **not** ask for a `.gitignore`
edit, does not ask for any file to be added to git, and does not ask for `0/` to be
reconsidered.

---

## 7. Heat-transfer's interest, disclosed

**Heat-transfer benefits from the answer "yes."** Tracking `0.orig/` would make **127**
of our own run cases regenerable from git that currently are not, and would remove a
known weakness from the family whose ladder this team is graded on.

We therefore **state the question and take no reading on it.** No recommendation is
offered, no preferred answer is implied by the ordering of §4 or §5, and the evidence in
§4.2 that existing policy leans toward tracking is presented because it is what the file
says — not because it is what we would prefer it to say. A family with an interest in
the outcome should not be the one weighing it, which is the reason this is a referral at
all.

---

## 8. What is NOT being asked, and what is already settled

- **`0/` is settled and is not reopened.** Heat-transfer has ruled: not to be tracked,
  because git carries content and the age guard reads mtime (audit §9, commit
  `7673c393`). The measurement behind that ruling — a HEAD blob extracting with the
  extraction time as its mtime, twice, seven minutes apart — is recorded there.
- **No comparator is touched.** All three exercised in the audit fail closed as written
  and are frozen files under rule 6.
- **No file on disk was modified** in producing this referral, and no run tree was
  altered. It is filesystem and static analysis only.
- **Nothing is sent anywhere** (rule 7). This is an internal referral within the box.

---

## 9. Verdict vocabulary and compute

No gate is graded here, so **no verdict from the rule-1 vocabulary is claimed.** The
determinations made are census figures and a `git check-ignore` result, each with its
method stated and its control shown.

*Compute: negligible — no solver launched; one tree walk, one `git ls-tree` snapshot and
two `git check-ignore` invocations, well under 1 core-minute and below the resolution at
which COMPUTE_BUDGET_CHARTER requires a costed row. Rule 12 estimate-versus-actual:
pre-registered negligible, incurred negligible, ratio ~1; no calibration row is opened
for a sub-resolution spend.*
