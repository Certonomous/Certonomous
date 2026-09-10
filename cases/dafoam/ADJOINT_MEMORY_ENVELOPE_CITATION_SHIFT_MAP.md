# ADJOINT_MEMORY_ENVELOPE.md — CITATION SHIFT MAP

**What this is.** `cases/dafoam/ADJOINT_MEMORY_ENVELOPE.md` is a frozen record
that other records cite **by line**. On 2026-09-09, commit `fa124d95` appended a
correction to its foot — legal — **and also inserted two lines into its body**,
which is not. Every body line from old L65 downwards moved by **+2**, and the
`lines whose number changed above this section: 0` assertion that `CLAUDE.md`
rule 6 requires was neither made nor makeable.

**The damage cannot be undone by moving lines again.** Un-inserting the marker
would shift every number a second time and break the citations written since.
What makes the defect harmless is a **published translation**, and this file is
it. Any reader holding a citation written before 2026-09-09 can convert it
mechanically here.

**This document renames nothing, renumbers nothing and edits no frozen record.**
It is a lookup table plus a census. Filed beside the file it maps, in dafoam
territory; nothing outside `cases/dafoam/` was touched to produce it.

**Author:** dafoam `lab-lane`. **Date:** 2026-09-10. **Zero compute:** no solver,
no container, no `mpirun`. Every figure below is read from git or from the file
on disk.

---

## 1. THE SHIFT, MEASURED FROM GIT

### 1.1 The commit that caused it

`fa124d95aee5950253a90a0edd0cf0ce4a71deb8`, **2026-09-09T21:14:23Z**,
*"ADJOINT_MEMORY_ENVELOPE correction 2026-09-09 …"*, **66 insertions, 0
deletions**. Pre-image blob `e4d1ac20`, **635 lines**; post-image blob
`d28d729c`, **701 lines**.

Its two hunks, read at `-U0` (this is the measurement, not a summary of it):

| hunk | what it did | verdict |
|---|---|---|
| `@@ -64,0 +65,2 @@` | inserted 2 lines into the **body**, immediately after old L64 | **NOT LEGAL under rule 6** |
| `@@ -635,0 +638,64 @@` | appended 64 lines at the **foot** (old EOF was L635) | legal |

The two inserted lines occupy **new L65** — the
`> [SUPERSEDED — see CORRECTION 2026-09-09 at the foot: …]` marker — and **new
L66**, its blank line. Old L64 was itself blank and is still L64.

**A correction of wording on the file's own face.** Amendment 2 §D (at L827-828)
describes the insertion as *"at position 63"*. The measured insertion point is
**after old line 64**; the new lines are L65 and L66. §D's next clause —
*"Every body line below L64 therefore moved down by two"* — is exactly right, and
its *"the marker now at L65"* is exactly right. Only the phrase "position 63" is
wrong, and it is corrected here rather than by editing that frozen section.

### 1.2 THE TRANSLATION RULE

> **OLD ≤ 64 → NEW = OLD (unchanged).**
> **OLD ≥ 65 → NEW = OLD + 2.**

Uniform. There is no second displacement anywhere in the file, no deletion, and
no reflow. A citation written against the pre-2026-09-09 numbering is converted
by adding 2 if and only if its number is 65 or greater; a **range** has both
endpoints converted.

| old | new | | old | new |
|---|---|---|---|---|
| 48–63 | 48–63 | | 423–427 | **425–429** |
| 64 | 64 | | 432 | **434** |
| 65 | 67 | | 608–635 | **610–637** |
| 141–168 | **143–170** | | 611 | **613** |
| 200–205 | **202–207** | | 622 | **624** |
| 261–273 | **263–275** | | 625–626 | **627–628** |

Every row of that table was checked by reading the same text out of both blobs,
not by arithmetic alone: for each range, the **first and last line** of the old
range and of the shifted new range were compared and found identical.

### 1.3 The later amendment shifted NOTHING — verified, not assumed

`335fd464c3c2de6b425e9a740289af54853834cd`, **2026-09-10T04:17:45Z**, Amendment 2
(v1.2), **174 insertions, 0 deletions**. Single hunk `@@ -701,0 +702,174 @@` — a
pure append at the foot.

**Test performed, with the value of N stated because that is the whole content of
the check:** `head -n 701` of the HEAD blob (701 = the full line count of the
`fa124d95` post-image) was compared byte-for-byte against the whole `fa124d95`
blob. **IDENTICAL.** Equivalently and independently, the first **43,236 bytes**
(the byte length of the `fa124d95` blob) of the HEAD blob match it exactly, and
both prefixes carry sha256
`1f3778cd046f1cf86d45df0caf8ef06baa1a1a8699583486201d0a72da3b1a07`.

**So the total shift, from any pre-2026-09-09 citation to HEAD, is +2 and only
+2.** HEAD blob is **875 lines**.

`335fd464` also correctly declined to un-insert the marker, and said so on the
file's face (L843-848). That refusal is right and this document endorses it: a
second renumbering would break every citation written between the two commits.

---

## 2. THE CENSUS — EVERY CITATION FOUND, AND WHETHER IT RESOLVES

**Method, in two passes, both controlled.**

1. **Tracked tree** — `git grep -n 'ADJOINT_MEMORY_ENVELOPE'`. Reading taken
   **2026-09-10T04:38Z at HEAD `cf82a349`**: **61 hit-lines** across 36 files.
2. **Untracked, non-ignored text files** — 2,262 files matching
   `.md .py .sh .json .tsv .txt .csv .yaml .yml .tex .rst`, swept with a
   **planted positive control** (a temporary file carrying
   `ADJOINT_MEMORY_ENVELOPE.md:432`) added to the file list. **The control was
   seen.** Result: **zero** untracked citations, other than this document itself.
   A zero from a reader shown able to see a plant is evidence; the plant was
   removed afterwards.

Hits were then classified by hand into line citations, section citations and
name-only mentions, and every line citation was resolved by reading the cited
text out of the pre-shift blob and the HEAD blob.

**Both counts are a reading at an instant, not a constant.** Peers commit
continuously; `docs/LAB_STATE.md` in particular was being rewritten while this
sweep ran, and its own line numbers moved between two passes half an hour apart.
**Re-derive rather than quote** — the classification below is what is durable,
not the totals.

**A false zero was hit on the way, and is recorded here because rule 3's
principle applies to sweeps as well as to comparators.** A first attempt,
`grep -rn --no-ignore 'ADJOINT_MEMORY_ENVELOPE' .`, returned **0**. A single-file
control on `docs/MEMORY_ARCHITECTURE.md` returned **2** on the same tool
(`/usr/bin/grep` is **ugrep 7.8.4** on this box). The zero was the reader, not
the tree. **A sweep that has not been shown able to see a known hit is not a
census** — every count above comes from a reader demonstrated non-blind.

### 2.1 LINE CITATIONS — these are the ones that move

`R` = resolves to the intended content at HEAD.

| # | citing file : line | cites | intended content | R? | **corrected** |
|---|---|---|---|---|---|
| 1 | `cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:233` | `:427` | the power law `1.2125 x cells^0.8485` | **NO** — and **already wrong before the shift**, see §3 | **`:434`** |
| 2 | `cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:320` | `:427` | same power law | **NO** — same pre-existing error | **`:434`** |
| 3 | `cases/dafoam/ladder-a/A3/original_memory_plan/PREREGISTRATION.md:33` | `:423-427` | the agg-peak-RSS table carrying **5,876.6 MiB** at 21,840 cells | **NO** — correct until `fa124d95` | **`:425-429`** |
| 4 | `…/original_memory_plan/PREREGISTRATION.md:33` | `:608-635` | the 2026-08-08 annotation that `transonicPCOption 2` is **dead code** | **NO** — correct until `fa124d95` | **`:610-637`** |
| 5 | `…/original_memory_plan/PREREGISTRATION.md:88` | `:432` | the power law (`R²=0.9992`) | **NO** — correct until `fa124d95` | **`:434`** |
| 6 | `…/original_memory_plan/PREREGISTRATION.md:155` | `:200-205` | *"the lab's only working cut: −29.6%"* — the `maxResConLv4JacPCMat` row and its result paragraph | **NO** — correct until `fa124d95` | **`:202-207`** |
| 7 | `…/original_memory_plan/PREREGISTRATION.md:162` | `:141-168` | the `adjUseColoring=False` FATAL coloring-validation block | **NO** — correct until `fa124d95` | **`:143-170`** |
| 8 | `…/original_memory_plan/PREREGISTRATION.md:265` | `:608-635` | *"fitted entirely on `transonicPCOption 2` runs"* | **NO** — correct until `fa124d95` | **`:610-637`** |
| 9 | `…/original_memory_plan/PREREGISTRATION.md:270` | `:261-273` | the 1,613–1,615 MiB vs 2,185.216 MiB accounting discrepancy | **NO** — correct until `fa124d95` | **`:263-275`** |
| 10 | `docs/MEMORY_ARCHITECTURE.md:51` | `:625-626` | *"died with it — they are **unreconstructible**"* | **NO** — correct until `fa124d95` | **`:627-628`** |
| 11 | `verification/campaign/COLD_START_TEST_2026-08-11.md:245` | `:622` | the same *"unreconstructible"* quote | **NO** — and **already wrong before the shift**, see §3 | mechanically **`:624`**; content-correct **`:627-628`** |
| 12 | `verification/campaign/DEAD_LEVER_AUDIT_ROUND5_2026-08-14.md:81` | `:611` | *"the retroactive note R1 said was owed"* — the transonic-PC dead-lever annotation | **NO** — correct until `fa124d95` | **`:613`**; the annotation's heading is **`:610`** and its item 1 spans **`:612-621`** |

### 2.2 SECTION / `L`-STYLE REFERENCES — checked, and these all still resolve

Every one of these points at the stale `-5`-everywhere table and paragraph, which
lives entirely **above** the insertion point and therefore did not move.

| citing file | cites | R? |
|---|---|---|
| `docs/LAB_STATE.md` — 5 hit-lines, carrying 4 range references: **two** `(L48-60)` and **two** `:50-58` | the stale `-5` table and paragraph | **YES**, all four unchanged |
| `ADJOINT_MEMORY_ENVELOPE.md` itself, Amendment 2 §B (L735) and §E (L865) | `L48–L63` | **YES**, unchanged |

`docs/LAB_STATE.md` is deliberately **not cited by line here**: it is the board,
it is rewritten every session, and its line numbers moved twice during this
sweep. Locate those four references by their text, not by a number.

Amendment 2's own internal citations were written **after** the shift and against
the post-shift numbering, and all resolve: `L610` (annotations heading), `L641`
(the `CORRECTION 2026-09-09` heading), `L612-621` (annotation item 1). **No
number inside Amendment 2 needs translating.**

### 2.3 NAME-ONLY MENTIONS — no line number, nothing to translate

Of the 61 tracked hit-lines, 11 carry the 12 line citations of §2.1, 5 are the
`docs/LAB_STATE.md` block of §2.2, and 1 is this document's own sibling
reference in `ACTD_PARAVIEW_RENDER_PASS_PREREGISTRATION.md`. **The remaining 44**
name the file (or `ADJOINT_MEMORY_ENVELOPE.json`,
a **different artifact that this shift does not touch**) without a line number —
by Option (`A3_SUBLU_PREREGISTRATION.md:88`, `A3_SUBLU_SWEEP_PREREGISTRATION.md:17`,
`R5_ADJOINT_CONDITIONING.md:4,66`), by §
(`ladder-a/A6/curriculum_D8/PREREGISTRATION.md:64`,
`curriculum_D17_cone_supersonic/PREREGISTRATION.md:67`,
`docs/dafoam/PRIOR_WORK_INVENTORY.md:978`), or in prose
(`docs/dafoam/GPU_SCOPE_MEMO.md:77`, `cases/dafoam/INDEX.md:145`,
`EXPERTISE_CURRICULUM.md:65`, `A3_SUBLU_RESULT.md:144`,
`ladder-a/A6/README.md:12`, `A6/adjoint_feasibility/*`,
`verification/campaign/DEAD_LEVER_AUDIT_2026-08-08.md:63,126,131,206,368`,
`LITERATURE_REPRODUCTION_REVIEW.md:398,404,811`,
`NOT_PASSING_REGISTER.md:273,326,327`, `MOVE_MAP_BATCH6/7_EXECUTION_*.md`,
`research/agenda/*`, `scripts/add_proposals_supervisor_review_2026_08_07.py:858`,
`sdk/tests/fixtures/absolute_claims_labelled.json:201`,
`cases/hlpw6/FEASIBILITY_PROBE.{md,json}`, `docs/PHASE2_MOVE_MAP.tsv:15176-15177`).
**None is affected.**

**A separate, pre-existing defect visible in that list and NOT repaired here:**
several of those cite the **pre-move path** `demo-output/website/dafoam/ADJOINT_MEMORY_ENVELOPE.md`
(`docs/MEMORY_ARCHITECTURE.md:51,178`, `scripts/self_audit.py:7995`,
`sdk/tests/fixtures/absolute_claims_labelled.json:201`,
`research/agenda/docket.json:4670`,
`research/agenda/proposals/a3-m6-vcoarse-adjoint-sub-lu-arm.json:20`,
`verification/campaign/DEAD_LEVER_AUDIT_2026-08-08.md:206`,
`NOT_PASSING_REGISTER.md:327`). That is a **path** defect from the 2026-08-18
batch-6 move, not a line shift, and it is out of this document's scope. It is
named so nobody mistakes it for shift damage.

---

## 3. TWO CITATIONS THAT WERE ALREADY WRONG BEFORE THE SHIFT

Rows 1, 2 and 11 are **not** `fa124d95`'s fault, and saying so matters: applying
`+2` to them produces a number that is still wrong.

**Rows 1–2 — `A2_GC_…:233` and `:320` cite `:427` for the power law, which has
never been at line 427.** Measured across every commit that touched the file:
the sentence `**memory (MiB) = 1.2125 x cells^0.8485**, R² = 0.9992` has sat at
**L432** continuously since `5a2e49c6` (2026-07-29) and moved to **L434** at
`fa124d95`. Line 427 in the pre-shift file was the table row
`| 79,560 | 17,603.8 |`. `A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md` was frozen
2026-09-01 (`82ea0468`), so the error was **−5 at the moment it was written** and
is now **−7**. **Correct target: `:434`.**

**Row 11 — `COLD_START_TEST_2026-08-11.md:245` cites `:622` for the
*"unreconstructible"* quote, which was at `:626` pre-shift.** This was already
recorded elsewhere: `docs/MEMORY_ARCHITECTURE.md:51` says in its own words
*"at `:625-626` on 2026-08-11, cited as `:622` when this row was written"*. Line
622 pre-shift was *"logs for Option 1 (`adjUseColoring=False`, incl. the
quoted"* — inside the right block, but not the quoted sentence. **Mechanical
translation gives `:624`; the content-correct citation is `:627-628`.**

**A correction to Amendment 2 §D's third bullet (at L838-839).** It reads
*"cites `:622` for the lost-logs block, which now begins at **L623**"*. **L623 is
the true position of the block's heading** (*"2. Options 1–2 lost their solver
logs …"*), so the sentence is not false — but a reader will take `622 → 623` for
the shift, and **the shift is +2, not +1**. Stated unambiguously here:
`:622` → `:624` mechanically; heading at `:623`; the quoted sentence at
`:627-628`.

---

## 4. THE EXECUTABLE CHECK — VERIFIED HERE, NOT REPEATED ON TRUST

`scripts/self_audit.py:4392`, `check_memory_scaling_law()`, is the one executable
check that reads this document. **The claim that it survives the shift was
checked by reading its source and by running its own two matchers over both
blobs, not by repeating the claim.**

It locates its inputs by **content regex only** — `re.search(r"memory \(MiB\) =
([0-9.]+) x cells\^([0-9.]+)\*\*, R.? = ([0-9.]+)", text)` for the published law,
and `re.findall(r"^\| ([0-9,]{4,}) \| ([0-9,]+\.[0-9]+) \|$", text, re.M)` for
the measurement rows. **There is no line number anywhere in the check.**

Both matchers were executed against the pre-`fa124d95` blob and the HEAD blob:

| | pre-shift blob | HEAD blob |
|---|---|---|
| law matched | `1.2125`, `0.8485`, `0.9992` | `1.2125`, `0.8485`, `0.9992` |
| rows matched | **3** | **3** |
| points | (21840, 5876.6), (42120, 9991.9), (79560, 17603.8) | identical |
| refit | coef 1.2125, exponent 0.8485, R² 0.9992 | identical |

**CONFIRMED: the check is unaffected, and its verdict is unchanged.** The reader
returned a **non-empty** match set on both blobs, so this is not a zero from a
blind reader.

**And a real hazard that this test — not the claim — is what closes.** The row
regex scans the **whole text**, so any *appended* section containing a
`| <digits> | <float> |` row would silently enter the fit and could flip the
check to `FAIL` without touching a single line number. Amendment 2 states it
avoided that deliberately; the table above is the measurement that it did.
**Any future amendment to `ADJOINT_MEMORY_ENVELOPE.md` must not introduce a
two-column `| cells | MiB |` row or a second power-law sentence.**

---

## 5. WHAT NEEDS ROUTING — AND WHY THIS LANE DID NOT TOUCH IT

**Nothing outside `cases/dafoam/` was written to produce this file.** The citing
documents are **not** silently rewritten, for two separate reasons: some belong
to other teams, and the dafoam-owned ones are **themselves frozen**.

| citer | owner | why untouched | route it needs |
|---|---|---|---|
| `docs/MEMORY_ARCHITECTURE.md:51` | not dafoam | outside this lane's write scope | the owning team appends a dated correction, or accepts this map as the translation |
| `verification/campaign/COLD_START_TEST_2026-08-11.md:245` | verification / cfd | outside this lane's write scope | same, plus §3 row 11: the number was wrong before the shift too |
| `verification/campaign/DEAD_LEVER_AUDIT_ROUND5_2026-08-14.md:81` | verification / cfd | outside this lane's write scope | same |
| `docs/LAB_STATE.md:6492,6532,6565` | the chief | board file; not a lane's to edit | **no action needed** — those references still resolve (§2.2) |
| `scripts/self_audit.py:7995` | cfd / verification tooling | outside this lane's write scope; **not** shift damage | stale **path** in the VALUE registry (§2.3), worth a separate item |
| `cases/dafoam/ladder-a/A3/original_memory_plan/PREREGISTRATION.md:33,88,155,162,265,270` | **dafoam** | **FROZEN PRE-REGISTRATION** (`CLAUDE.md` rules 2 and 6). Filed 2026-08-21 before any arm; it carries no `PERMISSION` marker but it is a pre-registration and its body is not editable by this lane | **supervisor's call**: a dated addendum at its foot, in the rule-6 form (version bump + `lines whose number changed above this section: 0`), restating the six citations at their corrected numbers. **Six citations, one document — one addendum, not six edits.** |
| `cases/dafoam/A2_GC_GRID_CONVERGENCE_PREREGISTRATION.md:233,320` | **dafoam** | **FROZEN PRE-REGISTRATION, POST-COMPUTE** — it already carries Amendment 1, Amendment 2 and a Results Addendum, each asserting `Lines whose number changed above this section: 0` | **supervisor's call**: a dated addendum correcting `:427` → `:434` and recording that the error **predates the shift** (§3), so a reader does not attribute it to `fa124d95` |

**No addendum to either pre-registration is drafted or applied here.** The brief
under which this lane worked reserved that decision, and rule 9 is why: an
instruction to publish a map is not an authorisation to append to a frozen gate
document.

---

## 6. WHAT WAS VERIFIED, AND WHAT WAS NOT

**Verified by direct measurement on this box, 2026-09-10:**

- The two hunks of `fa124d95` at `-U0`, and the pre/post line counts (635 → 701).
- The uniform `+2` rule, checked by reading the first and last line of **every**
  cited range out of both blobs and finding them identical.
- That `335fd464` shifted nothing: `head -n 701` (43,236 bytes) byte-identical to
  the `fa124d95` blob, both sha256
  `1f3778cd046f1cf86d45df0caf8ef06baa1a1a8699583486201d0a72da3b1a07`.
- That the power law has occupied L432 since 2026-07-29 and never L427 — walked
  commit by commit through the file's follow-history.
- That `check_memory_scaling_law` matches on content regexes only, and that both
  matchers return the same three points and the same refit on both blobs.
- The census: **61 tracked hit-lines** at 2026-09-10T04:38Z / HEAD `cf82a349`,
  and **zero** untracked citations across 2,262 untracked text files — the latter
  a zero taken with a **planted positive control that the sweep saw**.

**NOT verified, stated plainly:**

- **The census cannot be proven complete.** It finds citations that spell the
  filename. A citation that quotes a line number while naming the document only
  by description — *"the memory envelope, line 432"* — would not be found by any
  string sweep, and none is claimed to have been ruled out.
- **Data outside the repository is not covered.** The untracked pass was bounded
  to text extensions inside the working tree; anything under
  `/home/ubuntu/{closure-data,closure-challenge-benchmark,certonomous-runs}/`,
  and any gitignored binary or archive inside the tree, was **not** swept.
  Citations there, if any, are unknown. A whole-disk `grep -rn` was attempted and
  **abandoned** rather than left running: the box is saturated with two live
  dafoam solves and the sweep's I/O was competing with them.
- **"Intended content" is this lane's reading** of what each citer meant, taken
  from the citing sentence. Where a citer's intent was ambiguous — row 11 is the
  clear case — **both** the mechanical translation and the content-correct target
  are given rather than one being chosen.
- **No citing document has been corrected.** Every row in §2.1 still resolves
  wrong in the file that carries it until its owner acts. **This map makes the
  damage legible; it does not repair it.**

---

*Drafted by a dafoam `lab-lane` under a ZERO-COMPUTE instruction: no solver, no
container and no `mpirun` was invoked. `cases/dafoam/ADJOINT_MEMORY_ENVELOPE.md`
was read and **not modified**; no file outside `cases/dafoam/` was written.*
