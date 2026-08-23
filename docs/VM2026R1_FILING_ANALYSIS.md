# VM2026R1_Fluids — filing analysis for Sanaa's D-6 ruling (prepared, not acted on)

**Status: ANALYSIS ONLY.** The chief's D-6 ruling stands — *no agent acts on
it; do not touch either copy* — and nothing here moves, deletes, tracks or
reorganises anything. This memo exists so the ruling costs one read instead of
a re-derivation. Prepared by the verification supervisor, 2026-08-23.

## 1. The facts, read live 2026-08-23T19:37Z (read-only)

| copy | contents | state |
|---|---|---|
| `VM2026R1_Fluids/` (repo root) | 123 files, 2.5 GB — `VM2026R1_FLUENT_ARCHIVES`, `VM2026R1_CFX_ARCHIVES` (+ Forte per the chief's note) | complete per the chief's own 123-file count; untracked; mode 700 |
| `docs/papers/verification_validation/VM2026R1_Fluids/` | 10 files, 26 MB, **nested doubled path** (`VM2026R1_Fluids/VM2026R1_Fluids/`) | **the transfer is DEAD, not in progress**: last write 2026-08-22 17:42:44Z, and no `scp`/`rsync`/`sftp` process was live at the reading. The chief's 08-22 note ("being scp'd right now") described a transfer that has since stopped at 10 of 123 files |
| companion manual | `docs/papers/verification_validation/Ansys_Fluid_Dynamics_Verification_Manual.pdf` + `.txt` | tracked; R8 pair complete as of `090c070c`; title page verified (Release 2026 R1, March 2026) |

## 2. What the charters say

- **R8** (papers) does not fit: the suite is not a paper — it is a set of
  vendor case archives (inputs). The manual (the PDF) is the paper, and it is
  already filed under R8's directory.
- **R6** (cases) fits the *kind*: reference case definitions live under
  `models/` ("reference case *definitions* (inputs)"), never beside the prose
  describing them — which argues against the `docs/papers/…` copy on kind
  alone.
- **CLAUDE.md, WHERE THINGS LIVE**: *"Data too large for git lives outside it —
  `/home/ubuntu/{closure-data, closure-challenge-benchmark,
  certonomous-runs}/`. Nothing is invisible merely because it is big;
  `docs/LOCATIONS.md` enumerates it."* 2.5 GB of vendor archives is squarely
  this class; the lab already runs this pattern three times.
- **VERIFICATION_CHARTER §1**: a verdict cites an artifact still on disk.
  An outside-git home satisfies this the way `closure-data` already does,
  provided sha256 manifests of anything graded are committed.

## 3. The options, with the trade named

| option | what it is | trade |
|---|---|---|
| **A (recommended)** | Canonical home **outside git**: `/home/ubuntu/vm2026r1-fluids/` (sibling of `closure-data`), moved from the repo-root copy; enumerated in `docs/LOCATIONS.md`; sha256 manifest of the 123 files committed before anything is graded; the dead partial copy under `docs/papers/…` deleted | Follows the lab's existing big-data pattern; keeps the repo root clean (FILING R1); costs one `LOCATIONS.md` entry and one manifest. Archives are not diffable, so git adds nothing to them |
| B | Keep at repo root, add to `.gitignore`, enumerate in `LOCATIONS.md`; delete the partial copy | Zero move risk, but violates R1's spirit (a 2.5 GB untracked tree loose at the root) and L-class "gitignored is not filed" |
| C | Track the full 2.5 GB under `models/vm2026r1/` | Charter-cleanest kind-wise, heaviest repo cost; vendor archives never diff, so the 2.5 GB buys no history |

Under every option the **partial nested copy is deleted** (it is 10 stalled
files of a 123-file set — *"a half-copied tree read as a corpus is a
measurement of nothing"*) and the **manual PDF + `.txt` stay tracked where they
are**.

## 4. A second small ruling that can ride along

The manual's basename `Ansys_Fluid_Dynamics_Verification_Manual.{pdf,txt}`
violates R8's `author_year_identifier` pattern and is flagged twice by
`check_filing.py`. The conforming name would be
`ansys_2026_fluid_dynamics_verification_manual.{pdf,txt}`. The rename is a
tracked-file move (cheap here — nothing references the path yet outside the
board and this memo) but it was **not** made, because it sits beside D-6
material: one ruling can cover both.

## 5. What is blocked on the ruling

Grading anything from the suite (the external verification suite the lab
would grade itself against — VMFL001…VMFL036 per the manual's contents list).
No pre-registration will be written against either copy until the canonical
home exists, because a pre-registration must name artifact paths that will
still be true when the verdict cites them.
