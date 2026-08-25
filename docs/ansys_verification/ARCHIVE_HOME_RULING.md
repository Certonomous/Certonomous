# D-6 RULING — the canonical home of the Ansys VM2026R1 archive set

**NOT FILED ANYWHERE. Nothing in this document leaves this box** (CLAUDE.md
rules 7, 8). The manual is proprietary Ansys documentation and the archives are
Ansys project files, uploaded by Sanaa for this lab's private use.

**Status: RULING — in force.** Issued by the `ansys-verification-supervisor` on
2026-08-24 under `ANSYS_VERIFICATION_CHARTER.md` §9, which reserves this ruling
to the supervisor and forbids any lane from moving, deleting, renaming or
git-adding either archive copy until it is made. Drafted to the supervisor's
dictation by `ansys-lane-opus`; the wording of §1 is the supervisor's, recorded
in substance as dictated. Inputs: the charter's §9 read-only inspection of
2026-08-24 and the verification team's memo `docs/VM2026R1_FILING_ANALYSIS.md`
(option A recommended). Sanaa's approval of D-6 is recorded in D496.

---

## 1. The ruling

> **RULING (ansys-verification-supervisor, 2026-08-24, docket D-6, Sanaa's
> approval of D-6 recorded in D496):**
>
> **(a)** The canonical home of the Ansys VM2026R1 archive set is
> **`/home/ubuntu/ansys-vm2026r1/`** — outside git, beside `closure-data/` and
> `certonomous-runs/`, the lab's existing big-data pattern (option A of
> `docs/VM2026R1_FILING_ANALYSIS.md`; charter §9 recommendation).
>
> **(b)** The repository-root copy `VM2026R1_Fluids/` (123 files, 2.5 GB) is the
> **AUTHORITATIVE** source and is **MOVED, not copied**, to that home by a haiku
> lane, with sha256 of every file taken before and re-verified after the move;
> the manifest is committed at
> `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`.
>
> **(c)** The partial copy `docs/papers/verification_validation/VM2026R1_Fluids/`
> (10 CFX files, 26 MB) is a **dead transfer, not a strict subset**: 9 files
> byte-identical to the authoritative copy, `VMFL011B.wbpz` truncated at 327,680
> of 670,152 bytes. Its disposition: **DELETE**, because every one of its 9
> intact files is a byte-identical duplicate of a file in the canonical home
> (verified by sha256 in the manifest) and the 10th is an unreadable fragment of
> a file the canonical home holds complete — **nothing unique is lost**. The
> deletion is executed **only after** the haiku lane's post-move hash
> verification reports **123/123 matches**, and is recorded as done by a dated
> line in this file.
>
> **(d)** The extracted FORTE duplicate inside the set (`VMFRT_v261.zip`, 481 MB,
> plus its extraction) is **kept as-is for now**; dedup is a later, separate
> ruling.
>
> **(e)** `.gitignore` gains entries `VM2026R1_Fluids/` and
> `cases/ansys_verification/**/archive_extract/` so no rule-10 pathspec sweep can
> ever commit archives or an extraction.
>
> **(f)** The manual PDF + sidecar stay tracked where they are; the R8 basename
> question (memo §4) is **NOT ruled here** — that directory belongs to the
> verification team.
>
> **(g)** Pre-registrations cite archive paths under `/home/ubuntu/ansys-vm2026r1/`
> **only**.

---

## 2. What each clause binds

| clause | binds | consequence if broken |
|---|---|---|
| (a) | every path in every record of this team | a record citing the repository-root path after this ruling cites a path that no longer resolves; the verdict that rests on it is `NOT A RESULT` until re-pathed |
| (b) | the move: one move, hashes both sides | a copy instead of a move leaves two divergent 2.5 GB trees and no authority between them |
| (c) | the partial copy's deletion, gated on 123/123 | deleting before the verification would destroy the only remaining copy of any file the move damaged |
| (d) | the Forte duplicate | dedup is deferred, so nobody deletes 481 MB on their own reading |
| (e) | `.gitignore` | a rule-10 pathspec sweep (L-12: 1,187 files, 25M insertions, twice) cannot reach 2.5 GB of archives |
| (f) | scope | this ruling does not touch the verification team's directory |
| (g) | pre-registrations | a frozen pre-registration must name paths that are still true when the verdict cites them (VERIFICATION_CHARTER §1, §9) |

**Why (c) is a deletion and not a quarantine.** The disposition rests on a
property, not a preference: *nothing unique is lost.* The 9 intact files are
byte-identical duplicates by sha256, and the 10th is 327,680 of 670,152 bytes of
a file the canonical home holds whole — an unreadable fragment, not a variant.
A half-copied tree read as a corpus is a measurement of nothing, and leaving it
on disk beside the manual invites exactly that reading.

**What the ruling deliberately does not decide.** The R8 basename of the manual
(memo §4), the Forte dedup (clause d), and whether any archive is ever extracted
inside the repository at all — clause (e) only guarantees that if one is, git
cannot swallow it.

---

## 3. Execution — status, with the readings that support it

Read-only observations taken by `ansys-lane-opus` at **2026-08-24T17:18Z**, in
the same invocation as this file's drafting. These are readings, not constants;
re-derive with `find … -type f | wc -l`, `du -sh`, `sha256sum`.

| step | state at 17:18Z | reading |
|---|---|---|
| (b) move to `/home/ubuntu/ansys-vm2026r1/` | **done** | `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/` holds **123 files, 2.5 GB**; the repository-root `VM2026R1_Fluids/` **no longer exists** |
| (b) manifest | **written, not yet committed at this file's commit** | `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`, **123 lines**, paths relative as `./VM2026R1_Fluids/…` |
| (b) post-move re-verification, 123/123 | **NOT recorded here yet** | the haiku lane's report is the authority; this file carries no 123/123 claim until it lands |
| (c) deletion of the partial copy | **NOT DONE** | `docs/papers/verification_validation/VM2026R1_Fluids/` still holds **10 files** |
| (e) `.gitignore` entries | **done in this file's commit** | the two entries of clause (e) |

**The deletion of clause (c) has not been executed and is not authorised by this
line.** It is authorised by clause (c) itself and gated on the 123/123 report;
when it is done, it is recorded here as a dated line under §4 and nowhere else.

---

## 4. Dated execution lines (append-only)

*(One line per executed step, dated UTC, naming the agent and the reading that
justified it. Nothing is recorded here that was not read from disk.)*

- 2026-08-24T17:18Z — `ansys-lane-opus`: ruling recorded; `.gitignore` guards of
  clause (e) landed; charter amendment 1.1 and the `docs/LOCATIONS.md` sub-note
  landed in the same commit. **Zero compute; no archive touched by this commit.**

- 2026-08-25T21:2xZ — **`ansys-verification-supervisor`, personally: THE RECORD ABOVE IS
  STALE. §3 states clause (c) `NOT DONE` and clause (b) `NOT recorded here yet`. The disk
  says clause (c) IS DONE, and clause (b) is half-done. Recorded here as a dated note
  rather than by editing §3, because a record that says "never done" about a thing that
  was done is itself the defect, and overwriting it would hide that it ever diverged.**

  **Measured by the supervisor at 2026-08-25T21:17Z, read from disk, zero compute:**

  | what §3 says | what the disk shows | which is right |
  |---|---|---|
  | (c) `docs/papers/verification_validation/VM2026R1_Fluids/` "still holds **10 files**" | **ABSENT** — the path does not exist | **the disk.** Clause (c) has been executed; the dead partial copy is gone |
  | (implied) a copy at the repository root | **ABSENT** — `/home/ubuntu/Certonomous/VM2026R1_Fluids` does not exist | **the disk.** The move of clause (a) completed |
  | (b) post-move re-verification "NOT recorded" | **file-count half CONFIRMED**, sha half **still not run** | **§3, in part** — see below |

  **The canonical home holds the complete set:** `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/`
  — **123 files, 2.5 GB**, split **CFX 37 / FLUENT 77 / FORTE 9**, exactly the composition
  the charter's §9 inspection recorded for the pre-move copy.

  **`VMFL011B.wbpz` is 670,152 bytes — its FULL size.** The charter recorded it TRUNCATED
  at 327,680 of 670,152 bytes. That truncation was a property of the **dead partial copy**,
  which is now deleted; **the surviving archive is intact.** The truncation hazard is
  retired.

  **What is still genuinely outstanding, and is NOT closed by this note:** the **sha256
  re-verification of all 123 files against the committed manifest**
  (`docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`, 123 lines) has **never been
  run**. A file count is not an integrity check — 123 files of the right names can still
  be 123 corrupted files. It is dispatched to a reading lane with a **planted-corruption
  positive control**, because a clean result from a reader not shown able to see dirt is
  not evidence (CLAUDE.md rule 3). **Until that reports 123/123 OK with its control
  firing, clause (b) stays open and no one may write that the move is verified.**

- 2026-08-25T21:2xZ — **`ansys-verification-supervisor`: AN ARCHIVE-READABILITY GAP found
  while resolving a missing driving input, recorded here because it bounds what this whole
  corpus can be used for.**

  **No HDF5 tooling exists on this box.** Measured: `h5ls` MISSING, `h5dump` MISSING,
  `h5copy` MISSING, and `python3 -c "import h5py"` fails — **h5py MISSING.**

  **77 of the 123 archives are FLUENT `.cas.h5` files — an HDF5 container format.** With no
  HDF5 reader, **the majority of the corpus cannot be opened by any proper tool on this
  box**; only a `strings` scrape is available, which recovers no structured
  boundary-condition data reliably. The **37 CFX** archives carry text-bearing `.out`
  files and are readable; the **9 FORTE** archives are untested.

  **Consequence for the ladder:** where the manual omits a driving input, the archive is
  the documented resolution route — and **that route is currently open for CFX cases and
  closed for FLUENT cases.** This is an instrument gap, not a case failure. It is recorded
  as a finding rather than worked around, and **no lane may substitute a guessed or
  "typical" value for an input it could not read** — a fabricated driving input produces a
  false gate on a case that then looks verified.

- 2026-08-25T21:2xZ — **`ansys-verification-supervisor`: CLAUSE (b) IS NOW CLOSED, AND WITH
  IT D-6 IN FULL. §3 IS SUPERSEDED.** `[lab-attributed]` under Sanaa's desk-item disposal
  rule.

  The sha256 re-verification that the note above left open **has now been run**, and its
  record is committed at **`9ddd7624`**, file
  `docs/ansys_verification/VM2026R1_SHA_VERIFICATION_2026-08-25.txt`. **The supervisor read
  that file in full before citing it** — its three literal `FAILED` strings are the
  zero-count labels `": FAILED  0"` and `": FAILED open or read  0"` plus the planted
  control's own detection line, not failures.

  | check | result |
  |---|---|
  | files reporting `: OK` | **123** |
  | files reporting `: FAILED` | **0** |
  | files reporting `: FAILED open or read` | **0** |
  | `sha256sum -c` exit code | **0** |
  | lines checked vs manifest | **123 = 123** |
  | **planted-corruption control** | **FIRED** — one manifest hash corrupted, `FAILED` correctly reported |

  **The control is what makes the 123 evidence.** A clean sweep from a reader not shown able
  to see dirt is not a result (CLAUDE.md rule 3); this reader was shown, and it saw.

  **THEREFORE, RULED:**
  1. **Clause (b) is discharged.** The move preserved the corpus byte-for-byte: all 123
     archives match the checksums taken before the move.
  2. **Clause (c) is discharged** (recorded in the note above): both partial copies are
     ABSENT.
  3. **§3's status table is SUPERSEDED** by these two dated notes. **It is not edited** —
     it remains on the record as written, because the divergence between a record saying
     "never done" and a disk saying "done" is itself the finding, and overwriting it would
     erase the evidence that it ever diverged.
  4. **THE STANDING HOLD FROM THIS TEAM'S FIRST DAY IS RETIRED** — *"neither copy is moved
     or deleted until the supervisor rules"*. Both partial copies are already gone, the
     canonical home is verified intact, and **the hold has nothing left to protect.** No
     successor should carry it.
  5. **`VMFL011B.wbpz` is COMPLETE at 670,152 bytes.** The truncation belonged to the
     deleted partial copy; the hazard is retired.

  **D-6 — open since 2026-08-24, the first question this team was created to answer — is
  CLOSED.** Archive paths are cited under `/home/ubuntu/ansys-vm2026r1/` only.

  **One practice worth carrying, earned tonight:** the lane that produced this **wrote its
  result to disk and committed it BEFORE interpreting it.** Three of this team's lanes
  dropped mid-turn in the same hour; that one survived, and its measurement survived with
  it. **Measure, commit, then reason** — in a session that can die between two tool calls,
  interpretation is cheap to redo and a measurement is not.
