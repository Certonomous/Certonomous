# LESSONS_DRAFT — proposed lesson rows from D460 phase 1

> **DRAFT. NOT APPENDED.** This lane does not write `docs/LESSONS.md`. Every real append goes
> through `python3 scripts/append_record.py`, with `python3 scripts/check_record_reconciliation.py`
> run **before**, and numbers assigned **at commit, from the tail — the maximum existing number,
> never a count** (`CLAUDE.md` rule 11). That is the supervisor's job.
>
> Re-derived 2026-08-23 for context only, and **stale the moment a peer commits**:
> `grep -oE '^## L-[0-9]+' docs/LESSONS.md | grep -oE '[0-9]+' | sort -n | tail -1` → **248**.
> **Do not hard-code 249.** Re-derive in the same shell invocation as the append.

---

## Proposed lesson A — a novelty sweep that stops at the application's tracker misses the layer where the defect actually lives

**The rule.** When the finding is in a *build* of a library — an AD build, a patched build, a
vendored fork — sweep **the fork's own issue tracker**, not only the application's. Enumerate the
publishing organisation's repositories (`api.github.com/orgs/<org>/repos`) and read the small
trackers **in full**; a two-issue tracker is a complete read for the price of one request, and it is
a stronger negative than any number of term guesses against a large one.

**Why.** The application's tracker is where *users* post. The fork's tracker is where the
*maintainer* records what he already knows is broken, and he does not cross-post.

**The incident.** D460's partial sweep — 39 searches, 4 venues, 2026-08-22 — concluded *"No prior
art was found for either finding."* The full sweep of 2026-08-23 (101 searches, 13 venues,
`cases/dafoam/LIAISON_NOVELTY_SWEEP_adf_primal_nonreproduction.md`) found the prior art in
**`DAFoam/OpenFOAM-AD`**, the AD-patched OpenFOAM distribution DAFoam v5 migrated to. That tracker
holds **exactly two issues**, both open, both by the lead maintainer, and one of them —
**#2, 2026-01-25, `"PBiCGStab/DILU fvSolution generated wrong flow results"`** — states that *"both
ADR and ADF flow solvers generate wrong results (flow variables blow up rapidly)"* as a function of
the `fvSolution` linear solver. That is D460's defect family, reported seven months earlier. The
venue was not merely unswept: it was **not on the candidate's own list of unswept venues**. Cost of
finding it: one `orgs/<org>/repos` call and two issue reads.

**The second half of the lesson, which is the more valuable half.** The find did not only correct a
novelty claim — **it corrected the next experiment before it was run.** D460 §7 registered sweep 1
as "switch `p` from `GAMG` to `PBiCGStab`/`DIC`, and read NaN-persists as AD correctness". Upstream
#2 reports PBiCGStab/DILU as independently breaking AD builds, so that arm would have been
**confounded** and its headline reading wrong. The sweep was scheduled as a filing-readiness
formality and paid for itself as **experimental design**. **Run the novelty sweep before the
characterisation run, not after it.**

---

## Proposed lesson B — a nonsense-token control has to be run on *every* search surface, because each one fails differently

**The rule.** L-234 requires a nonsense-token control before any hit count is read. Extend it: the
control must be run **per surface**, and its *failure mode* recorded, because the surfaces do not
fail alike. Also run the **positive** direction — a query known to return many hits — so the reader
is shown able to see a presence, not only an absence.

**Measured 2026-08-23, three surfaces, three different behaviours:**

| surface | nonsense token returns | reading rule |
|---|---|---|
| GitHub REST `search/issues` | **0** | count is literal |
| GitHub Discussions HTML | **1** — a pinned thread, on every query | effective = threads − 1 |
| WebSearch (US index) | **8 topically-plausible on-target links** | **counts are worthless; only on-point content counts** |

**Why the third row matters most.** The web engine **discarded the nonsense token and answered the
topic**: `zzzqqxnonsensetoken12345 dafoam adjoint forward AD primal` returned DAFoam's DAOPTION
doxygen page, its verifications overview and the AIAA-J paper. So a web-venue disposition of *"the
search returned the project's own docs, nothing on point"* is **exactly what a query with no
meaning returns**, and it is not evidence that the venue was searched. Every web-venue row must be
recorded as *"no page whose content is on point"* and never as a hit count.

**Corollary on instrument choice.** Where a deterministic reader exists, prefer it to a summarizing
one. Asked to count threads on the same fetched page, the summarizing fetch reported *"0 distinct
threads"* while describing a thread link on that page; `curl` plus a regex over
`/<owner>/<repo>/discussions/[0-9]+` gave an exact, auditable, re-runnable thread-number list.
Print the numbers so the count can be checked without the HTML.

---

## Proposed lesson C — a NaN detector written as `\bn?an\b` matches the English word "an"

**The rule.** A sentinel-value detector gets a planted control in **both** directions before it is
trusted: it must fire on a file where the sentinel was planted, **and stay silent on a file known
not to contain it.** A one-directional plant catches a blind reader and misses a screaming one.

**The incident.** The D460 sweep-1 comparator
(`cases/dafoam/d460_sweep1_solver_family/analyse_sweep1.py`) first matched NaN with
`re.compile(r"\bn?an\b|-nan|\bNaN\b", re.I)`. The alternation `n?an` matches **`an`** — an ordinary
English word present in essentially every solver log ever written. The false positive was caught
before first compute by running the detector against the plain-build reference `patched.log`, which
is known NaN-free. Under the frozen decision rule that false positive would have driven **every**
arm to `GATE FAIL / AD CORRECTNESS`, the most serious verdict on the table, on every future run.
Fixed to `(?<![A-Za-z0-9_])-?nan(?![A-Za-z0-9_])`, then re-verified in both directions on real
files: `patched.log` → `False`, `s1b.log` → `True`.

---

## Proposed lesson D — register the field list the case actually has, not the family's boilerplate

**The rule.** The strict completion rule's "fields present" clause is **per family**. Copying
another family's list into a pre-registration registers a clause that can only ever fail.

**The incident.** `CLAUDE.md` rule 4 states the field list `T U p_rgh alphat nut k omega` **for the
thermal family**. The D460 sweep-1 arms are compressible external aero on `DARhoSimpleCFoam` with
Spalart-Allmaras: the fields are `T U p nut nuTilda alphat`. There is no `p_rgh`, no `k`, no
`omega` — the case has never written them. Registering the thermal list would have produced a
guaranteed `NOT A RESULT` on a healthy run, and the failure would have looked like a solver problem.
Caught while writing the pre-registration, before compute.

---

## Proposed protocol edit (not a lesson; `docs/standards/PROBLEM_RESEARCH_PROTOCOL.md` §1a)

Two statements in §1a are stale as of 2026-08-23 and were measured this pass. **Editing that file is
not this lane's call**; it is recorded here so the supervisor can dispatch it.

1. §1a: *"Plain `curl` to `github.com` HTML **hangs from this host**."* **No longer true.**
   `curl -sSL -A "Mozilla/5.0" "https://github.com/<owner>/<repo>/discussions?discussions_q=<q>"`
   returned a 260 KB page in under a second, 22 consecutive times.
2. §1a: *"A discussions search page that comes back with a 'There was an error while loading'
   banner is NOT a clean negative — retry it."* The literal string is present in the page
   **template on every fetch**, so a `grep` for it fires 22 times out of 22. The test must key on an
   **empty results region**, not on the banner string.
