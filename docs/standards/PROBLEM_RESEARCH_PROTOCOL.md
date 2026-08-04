# Problem Research Protocol

Version 0.1, dated 2026-08-04. Written from the first pass it governs
(`demo-output/website/dafoam/LIAISON_RESEARCH_adjoint_conditioning.md`), under
Katie's standing directive of the same date: when something breaks, the liaison
researches the problem online — and records how, so the next pass starts here
instead of from scratch. This document is expected to be edited every time it
is used. Citation rules are LITERATURE_CHARTER.md's and are not restated, only
applied.

## 1. Source tiers, in the order they pay off

1. **Upstream issue tracker AND discussions.** Issues via
   `api.github.com/search/issues?q=repo:OWNER/REPO+<term>`. **Trap learned on
   pass 1: the REST issue search does not index GitHub Discussions**, and
   projects like DAFoam keep nearly all traffic there. Cover discussions
   separately: `github.com/search?q=repo:OWNER/REPO+<terms>&type=discussions`
   (fetchable) plus a plain web search with the repo name. A zero-hit issue
   search proves nothing until discussions were swept too.
2. **Upstream source, at the exact deployed version.** Fetch raw files
   (`raw.githubusercontent.com/OWNER/REPO/<sha-or-tag>/path`) or shallow-clone
   to grep. Two non-negotiables: (a) pin every source claim to a sha/tag and
   date it; (b) **before proposing a fix, check whether the deployed copy
   already contains it** — diff the deployed file against main, and walk the
   file's commit history (`/commits?path=...`). Pass 1's example: the "obvious"
   PETSc ILU shift fix has been hard-coded in DAFoam since 2022; a docket item
   to "try the shift" would have burned a run on a no-op.
3. **Official docs AND the tutorials/examples repo.** For research codes the
   tutorials' run scripts are the de-facto option documentation and encode the
   maintainer's actual recommended settings; the prose docs lag. Read the
   class, not the dictionary entry (charter §4.3 / L-20, L-26).
4. **Library mailing lists.** petsc-users is archived and searchable at
   mail-archive.com; developer replies (named individuals) there are
   authoritative for what an error code means and what the sanctioned
   workarounds are.
5. **Forums** (CFD-Online, StackExchange): leads and symptom-matching only —
   anything found here gets re-verified at tier 2 or 4 before it is cited.
6. **Papers**, per LITERATURE_CHARTER.md tiers. A paper claim that contradicts
   a lab measurement is charter §6 trigger 3 and forces a proposal.

## 2. Constructing search terms from an error signature

Work outward in three rings, and run all three before concluding "unreported":

1. **The literal machine string**: `DIVERGED_NANORINF`, `KSPConvergedReason
   -9`, the exact exception text. Highest precision, hits the people with the
   identical failure.
2. **The words a maintainer would use**: "adjoint diverged", "zero pivot",
   "shift", "not converging". This is where the fix-thread usually lives,
   because maintainers answer in mechanism words, not error codes.
3. **The mechanism we measured**: "ILU no pivoting singular", "block Jacobi
   number of processes", "matrix ordering zero pivot". This ring finds the
   library-level literature even when the application (DAFoam) has no thread
   at all.

Record every query that returned nothing, with where it was run. A recorded
negative ("0 hits for NANORINF in repo issues, 2026-08-04, REST search —
discussions swept separately") is what later justifies "this appears
unreported upstream", which is itself a docket-grade finding.

## 3. Recording findings

Every finding is one row: **claim → source URL + tier + date fetched → where
it applies → where it does not** (LITERATURE_CHARTER §3). Source-code claims
additionally carry file, line, and sha. Zero fabricated citations: a URL that
was not actually fetched this session does not appear, full stop. Findings go
in a dated memo under the investigation's own directory; ranked, with the
cheapest discriminating action attached to each lead — a lead without a
runnable next action is a summary, and summaries are what §4 exists to
prevent.

## 4. When a finding MUST produce a docket proposal

Mapped from LITERATURE_CHARTER §6; if any fires, the research pass does not
close on a memo alone:

1. **A concrete, settable, untried option exists** for the live blocker →
   proposal to try it, cheapest-first ladder, cost estimates attached.
2. **The fix already exists upstream** in a newer version/commit → proposal to
   upgrade or backport, citing the sha.
3. **An upstream claim contradicts a lab measurement** → proposal for the
   discriminating experiment (their limitation, our defect, or different
   measurand — name which one it decides).
4. **A pinned mechanism is unreported upstream** → proposal to file/report
   upstream. Drafts only: **the liaison is read-only on the web — never post,
   comment, or create accounts. Anything outbound awaits Katie's call.**

## 5. What pass 1 would do differently (fold in on the next edit)

- **Deployed-source check first, not last.** The single highest-leverage read
  of the whole pass was three lines of the shipped C file; it should be step
  zero whenever the blocker names a code path.
- `gh` is not installed on this host; `curl api.github.com` covers search,
  commits, file listings, and issue reads unauthenticated (rate limit ~60/hr —
  batch queries).
- Web-search summaries are leads, not sources: click through and fetch the
  page before citing anything from it.
