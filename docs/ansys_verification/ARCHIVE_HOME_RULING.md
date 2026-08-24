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
- 2026-08-24T17:43Z — `ansys-lane-opus48` (running as **claude-opus-4-8**): **D-6
  EXECUTED — clauses (a), (b) recorded done; (c) retirement ORDERED.** Readings and
  facts relayed from the haiku lane's move report (~17:20Z) and re-checked read-only
  by this lane. **Zero compute; no archive touched by this commit.**
  - **(a)/(b) canonical home:** the set now lives at
    `/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids/{VM2026R1_FLUENT_ARCHIVES,VM2026R1_CFX_ARCHIVES,VM2026R1_FORTE_ARCHIVES}/`
    — the `VM2026R1_Fluids/` level is **retained**, and the manifest's relative paths
    (`./VM2026R1_Fluids/…`) carry it, so `sha256sum -c` must be run from
    `/home/ubuntu/ansys-vm2026r1/`. The haiku lane reports that check **passed
    123 OK / 0 FAILED** (its measurement, not re-run here). Byte total
    **2,650,121,385 before and after** the move. Counts: **FLUENT 77 / CFX 37 /
    FORTE 9 = 123.** The repository-root `VM2026R1_Fluids/` was **removed** (empty
    `rmdir`). No mode-700 files anywhere inside the set.
  - **This lane's own read-only re-check:** `find … -type f | wc -l` at the canonical
    home returns **123**. sha256 over 2.5 GB was **not** re-run here — the 123 OK / 0
    FAILED figure is the haiku lane's.
  - **(c) partial copy** `docs/papers/verification_validation/VM2026R1_Fluids/`
    (10 CFX files): confirmed a dead transfer — **9 basenames sha-identical** to the
    canonical copies, and `VMFL011B.wbpz` truncated at **327,680 of 670,152 bytes**.
    Its retirement under clause (c) is **ordered 2026-08-24, executed by a second
    haiku lane** running in parallel — see the next dated line (the confirming
    execution line is left to the supervisor). Nothing unique is lost.
  - **(d) Forte, correction of record:** the board's "stored twice" is **wrong**. The
    "extraction" `VMFRT_v261/` is a **4 KB stub** sitting beside the **459 MB**
    `VMFRT_v261.zip`; the **zip is the only full Forte copy**. Clause (d) still defers
    Forte dedup, but there is no full duplicate to dedup — only a zip and a stub.
  - **Manifest landed:** `docs/ansys_verification/VM2026R1_SHA256_MANIFEST.txt`,
    **123 lines**, committed as-is in this commit.
  - **Absent-archive notes for the register:** **VMFL068** has **no archive anywhere**
    in the set; all ten **VMFLGPU** archives are absent (recorded in `CASE_MAP.md`).
- 2026-08-24T17:39:17Z — clause (c) executed by haiku lane: partial copy removed
  after re-verification (manifest 123 OK, exit 0; 9 of 10 partial hashes present in
  manifest, VMFL011B.wbpz absent as expected; git ls-files empty for the path);
  manual PDF 8,517,733 B and sidecar 368,949 B intact. Confirmed by the supervisor.
