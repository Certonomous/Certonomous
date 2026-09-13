# DRAFT — two rule-6 addenda: the case-writer sha256 pin is stale in two frozen registrations

**DRAFTED BY A cfd `lab-lane`, NOT APPLIED. Team: cfd. 2026-09-13.**
**Neither frozen registration is edited by this lane** (rule 6). The `cfd-supervisor` lands both.
**Filed here, beside the documents they amend, and not in scratch** (L-186).

**No gate, threshold, cap or label is altered by either block. No regrade is implied.**

---

## Why these are needed

Commit **`e7702536125743b22b485074cfb5e253f7952ca5`** (2026-09-13 18:43:14 +0000) changed
`cases/navier_class/DRIVAER/mesh/write_solver_case.py` — the nut wall treatment became a required
argument with no default. **Two frozen registrations pin that file by sha256 against a live path**,
so a verifier re-checking either against the filesystem now gets **DRIFTED**, on runs already
complete.

**Everything asserted in the two blocks below was verified by this lane**, not taken on relay:

| fact | how checked |
|---|---|
| R1 Stage A frozen at **`903dc88d1`**, 2026-09-11 00:22:45 +0000 | `git log --diff-filter=A` |
| R2b frozen at **`ed67a279c`**, 2026-09-12 03:23:55 +0000 | same |
| writer at **each** of those commits hashes to **`b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f`** | `git show <commit>:<path> \| sha256sum`, run for both commits |
| the file has exactly **two** commits in its history: `903dc88d1` and `e77025361` | `git log -- <path>` |
| live file now **`498f5b10054a996fe2d32b7bbb5acf2a4cea73642519aed12f88838bb9ba2a71`** | `sha256sum` |
| last activity in each run root **precedes** the edit by ≥ 25 h — `r1_fine` 2026-09-11 16:29, `r2_medium` 2026-09-12 05:26, `r2_coarse` 2026-09-12 17:30, against the edit at 2026-09-13 18:43 | newest-file mtime per run root |

🔴 **ONE THING THIS LANE COULD NOT VERIFY, STATED RATHER THAN GLOSSED:** `r1_fine` has **no
`RUN_RC`**. The ordering claim below is therefore made on **last file activity**, which is what was
measured, and **not** on a completion verdict. **Neither block asserts that R1's run completed.**

🔴 **AND A DEPARTURE FROM THE INSTRUCTION, DISCLOSED:** the instruction said *version bump*.
**Neither document carries a version field** — checked, no `v1.x` line in either. The blocks
therefore carry their own dated addendum number and **no version line is invented**. If the
supervisor wants one, it is his to add.

## How to land each block

Append verbatim at the foot. Because it is a pure append, `lines whose number changed above this
section: 0` holds by construction — **prove it, do not assert it**:

```bash
PRE=$(git show HEAD:<file> | wc -c)          # BEFORE appending
# ... append the block ...
cmp -n "$PRE" <(git show HEAD:<file>) <file>  # must report no difference
```

---
---

## BLOCK 1 — APPEND EXACTLY THIS TO `verification/campaign/DRIVAER_R1_STAGE_A_PREREGISTRATION.md`

*(its A-series stands at A2, so this is A3)*

```markdown

---

## ADDENDUM A3 — 2026-09-13 — **THE CASE-WRITER sha256 PINNED AT §258 IS STALE AGAINST THE LIVE PATH, AND THAT IS EXPECTED**

**lines whose number changed above this section: 0.** No gate, threshold, cap, label or band is
altered. **No regrade is implied and no verdict of this registration is affected.**

**The pin at line 258 reads `b1b67ae1249636ce` against
`cases/navier_class/DRIVAER/mesh/write_solver_case.py`.** That file was changed on 2026-09-13 at
commit `e7702536125743b22b485074cfb5e253f7952ca5` and now hashes to
`498f5b10054a996fe2d32b7bbb5acf2a4cea73642519aed12f88838bb9ba2a71`.

**1. THE PINNED HASH IS RESOLVED THROUGH GIT, NEVER FROM DISK.** The canonical form is:

```
git show 903dc88d1e5c85cf688816f1ef75a965479d81ba:cases/navier_class/DRIVAER/mesh/write_solver_case.py | sha256sum
  -> b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f
```

`903dc88d1` is **this registration's own freeze commit**. Verified, not asserted.

**2. THE CHANGE POSTDATES THE RUN.** Last file activity in `r1_fine` is **2026-09-11 16:29**; the
writer changed **2026-09-13 18:43**, more than two days later. **The run this registration governs
was produced by `b1b67ae1…`, and nothing about it is altered.** *(Stated on measured file activity.
`r1_fine` carries no `RUN_RC`, so this addendum makes no claim about its completion status.)*

**3. WHAT CHANGED, IN ONE LINE.** The `nut` wall treatment became a **required argument with no
default** (`--nut-wall-vehicle`, `--nut-wall-floor`), so the writer refuses to write a case whose
wall treatment nobody stated; a count-based readback asserts the written bytes carry exactly the
requested treatments. **The reason: R5 registers `nutUSpaldingWallFunction` while the staged case
carried `nutkWallFunction`, and a silent default is what allowed that divergence.**

**4. 🔴 A `DRIFTED` RESULT AGAINST THE LIVE PATH IS EXPECTED AND IS NOT EVIDENCE OF TAMPERING.** A
verifier re-checking this pin against the filesystem **will** disagree, and that disagreement is
this addendum, not a finding. **Re-check through git at the commit named in item 1.**

**5. THE GENERAL DEFECT, RECORDED BECAUSE IT HAS NOW BITTEN THREE INSTRUMENTS IN ONE NIGHT.** *"A
document pinned as a frozen instrument cannot also be the file that evolves."* Any registration
pinning a script **by disk hash** acquires a landmine the first time that script is **legitimately
improved** — PPTC's comparator, whose whole-file hash every lawful amendment invalidated; CRM's pin,
naming a blob and a commit that never went together; and this. **The fix is the same in all three:
pin by commit, resolve through git, never from the filesystem.**
```

---
---

## BLOCK 2 — APPEND EXACTLY THIS TO `verification/campaign/DRIVAER_R2B_COARSE_SOLVE_PREREGISTRATION.md`

*(it carries no addenda, so this is ADDENDUM 1)*

```markdown

---

## ADDENDUM 1 — 2026-09-13 — **THE CASE-WRITER sha256 PINNED AT §114 IS STALE AGAINST THE LIVE PATH, AND THAT IS EXPECTED**

**lines whose number changed above this section: 0.** No gate, threshold, cap, label or band is
altered. **No regrade is implied and no verdict of this registration is affected.**

**The pin at line 114 reads `b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f`
against `cases/navier_class/DRIVAER/mesh/write_solver_case.py`.** That file was changed on
2026-09-13 at commit `e7702536125743b22b485074cfb5e253f7952ca5` and now hashes to
`498f5b10054a996fe2d32b7bbb5acf2a4cea73642519aed12f88838bb9ba2a71`.

**1. THE PINNED HASH IS RESOLVED THROUGH GIT, NEVER FROM DISK.** The canonical form is:

```
git show ed67a279c416d7a516922b67e6871401f397a04c:cases/navier_class/DRIVAER/mesh/write_solver_case.py | sha256sum
  -> b1b67ae1249636ce4a6ad9246ace236ff05035f87f47031117c68dc81dfe3f1f
```

`ed67a279c` is **this registration's own freeze commit**. Verified, not asserted.

**2. THE CHANGE POSTDATES THE RUNS.** Last file activity is **2026-09-12 05:26** in `r2_medium` and
**2026-09-12 17:30** in `r2_coarse`, both carrying `RUN_RC = 0`; the writer changed **2026-09-13
18:43**. **The runs this registration governs were produced by `b1b67ae1…`, and nothing about them
is altered.**

**3. WHAT CHANGED, IN ONE LINE.** The `nut` wall treatment became a **required argument with no
default** (`--nut-wall-vehicle`, `--nut-wall-floor`), so the writer refuses to write a case whose
wall treatment nobody stated; a count-based readback asserts the written bytes carry exactly the
requested treatments. **The reason: R5 registers `nutUSpaldingWallFunction` while the staged case
carried `nutkWallFunction`, and a silent default is what allowed that divergence.**

**4. 🔴 A `DRIFTED` RESULT AGAINST THE LIVE PATH IS EXPECTED AND IS NOT EVIDENCE OF TAMPERING.** A
verifier re-checking this pin against the filesystem **will** disagree, and that disagreement is
this addendum, not a finding. **Re-check through git at the commit named in item 1.**

**5. THE GENERAL DEFECT, RECORDED BECAUSE IT HAS NOW BITTEN THREE INSTRUMENTS IN ONE NIGHT.** *"A
document pinned as a frozen instrument cannot also be the file that evolves."* Any registration
pinning a script **by disk hash** acquires a landmine the first time that script is **legitimately
improved** — PPTC's comparator, CRM's pin naming a blob and a commit that never went together, and
this. **The fix is the same in all three: pin by commit, resolve through git, never from the
filesystem.**
```

---

## A note this lane owes, since the edit that caused this was its own

**The pins were not searched before the edit was applied.** This lane flagged call sites as the
open risk and named a repository sweep as someone's five-minute item; **the sweep found no caller
but did find these two pins.** A hash pin is a consumer of a file **exactly as a call site is**, and
it is the one that survives `grep` for the script's name — because it cites the **path**, not the
symbol. **Searching for callers is not the same as searching for dependants, and this lane searched
for the first while calling it the second.**
