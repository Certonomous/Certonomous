# Ownership boundaries as a defect class — the zone register and the owner's worklist

**Swept 2026-08-15 at HEAD `1360a5a9`.** Docket **D145**. This document landed at
`a3342d9a`. The instance that named the class is **D140** (commit `09234034`), repaired at
`be0a0c5d`.

**Two concurrency facts are recorded here rather than tidied away, because both are the
shared working tree behaving exactly as the register above predicts.** (1) The row was
written as **D143** and renumbered to **D145** on discovering that a concurrent dispatch had
claimed D143 and D144 in the seconds between the free-ID check and the write. (2) **The
D145 row itself is not carried by this dispatch's commit.** It was staged in the shared
working tree and swept into a concurrent dispatch's commit **`60073572`** before this one
ran, so `git log -- docs/DOCKET.md` attributes it to an author who did not write it. **That
is this document's own subject in miniature: a shared surface with no per-writer boundary at
all, where the pathspec that protects your file cannot protect your line.**

**No scoring call was made; the ledger stands at 6. Nothing was fetched, sent, uploaded,
filed or registered. The scoring pin `deb91557` was not moved. No solver ran.**

---

## 0. The claim this document exists to make

D140 named the class as: *an ownership boundary that a sweep must not cross is a place
where wrong copies survive corrections.* **Measured, that statement is half right, and the
half it gets wrong is the half that matters.**

Of the five zones carrying live wrong claims, **four were already detected, in writing, by
name, before this pass began**. `dist/` is failing a check *right now* — and its four bad
copies were found and written down by **three separate earlier passes** (§2.7), one of which
recorded its reason for stopping as *"Reported, not repaired — `dist/` has a designated
owner."* `LADDER_V_*` was detected and filed as D140. `latex/` was detected and filed as
D115. `LAPTOP_SHOOT.md` was detected and filed as **A3**. **Not one of them survived because
nobody looked.** They survived because:

1. **a detection with no named owner has nobody to hand to**, and
2. **nothing in this lab schedules any check at all** (`scripts/lab_check.py`, D64: *"no
   CI, no Makefile, no pytest config, no installed git hook, no Claude hook"*), and
3. in the worst case a check **crossed the boundary, read the wrong text, and returned a
   PASS on it** — see §2.1, which is the single worst finding in this document.

So the durable fix is not a better sweep. **The sweeps are adequate and in one case already
red.** The durable fix is that a boundary must resolve to a name, and a detection must
resolve to a task. §5.

**And a name alone is not enough either — that is what `LAPTOP_SHOOT.md` proves.** It is the
one zone in the register whose owner is stated plainly and personally (*"It is Katie's file"*),
and it carries four live wrong claims two weeks old, in a script written to be read aloud on
camera. **A named owner with no cadence and no worklist is a boundary that fails politely
instead of silently.** The fix is a name *and* a cadence *and* a list — §3 is the list.

---

## 1. The zone register — what is in force, who owns it, what sweeps it

Established by grepping the docket, the charters, `docs/USING_THIS_LAB.md`, the campaign
briefs and the sweep scripts themselves for ownership language. **Frames stated per row in
§3.**

| Zone | Where it is declared | Owner | Swept by | Can any check read its contents? |
|---|---|---|---|---|
| `dist/certonomous-demo.zip` (tracked) and `dist/certonomous-demo/` (gitignored, `.gitignore:72`) | `docs/DOCKET.md` D80, D112, D115, D118, D135, D136, D140; `campaign/LADDER_V_TRIPLE_VERIFICATION.md:992` *"`dist/` and the public pages belong to their owners"* | **UNOWNED.** Called *"the designated owner"* six times across six rows and **never once given a name** | `self_audit.py::check_bundle_drift` (currently **FAIL**) and `::check_rank_claim_surfaces` (currently a **false PASS**, §2.1) | **Zip: YES.** `self_audit.py:1060-1079` opens every member via `zipfile.ZipFile`. **PDF-inside-zip: no** — `_surface_text` drops anything that fails UTF-8 decode |
| `demo-output/website/latex/*` — `.tex` **and** the compiled `.pdf` | `docs/DOCKET.md` D71, D115 (*"`latex/*` has a designated owner and no PDF was modified or opened for writing"*) | **UNOWNED.** Same generic formula | `.tex`: `docket_citation_guard.py` (in `TEXT_SUFFIXES`). `.pdf`: **NOTHING** | **PDF: NO**, and the lab says so in its own generated output — `self_audit.py:5948` prints *"nothing in this file opens a PDF, so a claim that exists only in a compiled report is invisible while its `.tex` source is not."* `docket_citation_guard.py:150-152` excludes `.pdf` by suffix |
| `demo-output/website/campaign/LADDER_V_*` round documents | `docs/DOCKET.md` D140; `LADDER_V_V13_CLOSEOUT.md:851` (*"§8 is not edited"*) | **UNOWNED.** D140's disposition says only *"owner of `LADDER_V_*`"* | Later `LADDER_V_V15_ROUND*` / `V16_GRADE*` rounds re-audit each other; `check_rank_claim_surfaces` reads them as lab records | Text — fully readable |
| `LAPTOP_SHOOT.md` | `docs/DOCKET.md` A3: *"It is Katie's file; the fleet does not edit it."* | **NAMED — Katie** | Cited by campaign docs; **nothing checks it for freshness**, and A3's staleness finding is still open | Text — readable |
| `docs/charters/*` | `docs/charters/CUSTODY_PROPOSAL.md:19-54`; `docs/MEMORY_ARCHITECTURE.md` §2.2: ***"Only three files say who writes them. Nine of twelve charters do not."*** | **UNOWNED for 9 of 12.** Named: `SUPERVISOR_RULINGS.md` → chief (outward-facing excluded); `RESULT_PRIORITY_CHARTER.md` → Katie; `CASE_SELECTION_CHARTER.md` §1 → Katie | Nothing — governance, not swept | Text — readable |
| `demo-output/website/dafoam/ladder-b/` | `docs/DOCKET.md` D80a: *"a barred directory for this agent"* | **UNOWNED** | generic corpus sweeps only | Text — readable |
| `scripts/self_audit.py`, `sdk/tests/test_rank_claim_surfaces.py`, `campaign/V16_*` | dispatch briefs and `agenda/proposals/naca-report-1191-*.json:22` *"other agents hold those"* | **UNOWNED** — "other agents", never a name | it *is* the sweep | — |
| `/usr/local/bin/` (installed `auto-stop.sh`) | `docs/USING_THIS_LAB.md:118-119`; `docs/DOCKET.md` D65 | **NAMED — Katie / Sanaa** | `scripts/installed_registry.py`, with a dated waiver expiring 2026-08-21 | shell — readable |
| Outward-facing acts / submissions | `GOALS_AND_PROPOSALS_CHARTER.md` §8 via `docs/USING_THIS_LAB.md:334-341`; `SUPERVISOR_RULINGS.md` R9 *"carries the company's name and stays hers"* | **NAMED — Katie** | a send/no-send gate, not a content sweep | — |
| `motorbike-video/`, `FILMING_COMMANDS.md`, `closure.html`, `docs/PRODUCT_LIST.md`, `docs/USING_THIS_LAB.md`, `ACTIVE_RESEARCH.md`, `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md`, `.autostop-hold`, `sdk/chief_engineer/` | **no standing declaration found** — these appear on individual dispatch briefs' do-not-touch lists, which are per-dispatch and expire with the dispatch | n/a — not standing zones | ordinary sweeps read them | text — readable |

### 1.1 The asymmetry, which is the register's own finding

**Every zone this lab invented for itself is anonymous. Every zone that touches Katie
personally or the outside world is named.** `LAPTOP_SHOOT.md`, `/usr/local/bin/` and
submissions resolve to Katie or Katie/Sanaa. `dist/`, `latex/`, `LADDER_V_*`,
`dafoam/ladder-b/`, `self_audit.py` and nine of twelve charters resolve to *"the designated
owner"*, *"whoever owns X"*, *"other agents"* — **a role with no occupant.**

The only machine-readable ownership in the repo is `sdk/chief_engineer/exec_bits.py:346-363`,
an `OWNERS` prefix table mapping paths to **families, not people**, used for exec-bit waiver
attribution and nothing else.

---

## 2. Per-zone hit classification

### 2.1 `dist/` — 4 LIVE AND WRONG, and a check that reads them and passes them

The shipped `dist/certonomous-demo.zip` and the unpacked `dist/certonomous-demo/` are
**byte-identical** (md5 over all 90 members). Both carry four live copies of withdrawn
claims. The live sources they were copied from **are already repaired**, strike-and-keep.

| Member | Line | What it says | What it should say | Class |
|---|---|---|---|---|
| `site/benchmarks.html` | 148-149 | *"the 0.0029 margin over the published leader carries a truth-free seed-uncertainty bound of comparable size (0.0024)"* | margin is `0.001365` over **Yang** on the six-entry board; the `0.002419` bound is **177% of it — it exceeds the margin** | **LIVE AND WRONG** |
| `site/closure.html` | 366-368 | *"0.0566 is the best overall number on the board — 0.0029 below the published leader … the margin carries a seed-uncertainty bound of comparable size"* | `0.001365` below **Yang**; the bound exceeds the margin | **LIVE AND WRONG** |
| `site/closure.html` | 411 | *"a truth-free bound cannot rule out movement up to 0.0024 — comparable to the 0.0029 margin over the published leader"* | 0.0024 is 177% of the `0.001365` margin over Yang | **LIVE AND WRONG** |
| `site/closure.html` | 502-503 | *"rank 1 of 5 is our local scoring at a pinned benchmark commit, with a seed-uncertainty bound comparable to its margin"* | **rank 1 of 7** on the six-entry board; bound **larger than** its margin | **LIVE AND WRONG — two withdrawn claims in one sentence** |

Repaired in the source at `demo-output/website/benchmarks.html:156` (`cc906ec9`) and
`demo-output/website/closure.html:404,562-563` (`7a0419f7`). The bundle was last built at
`bd3da3a1`, **2026-08-14 21:17:35 — before both repairs.**

**THE FINDING. A check crosses this boundary, reads exactly these bytes, and returns a
PASS.** `self_audit.py::check_rank_claim_surfaces` opens the zip and grades every member.
Run at `1360a5a9` it reports:

> `WARN — every travelling surface complies; 26 lab record(s) claim rank 1 without what V8 requires`

Verified directly: line **502** of `certonomous-demo/site/closure.html` **inside the zip**
is read and is recognised as a rank claim (`_rank_claim_lines` returns
`[95, 96, 108, 112, 139, 141, 366, 370, 375, 391, 391, 502]`) — **and it passes.** It passes
because the check grades **claim FORM** — does this sentence carry P(rank 1), its interval
and the token *"not statistically decided"* — and **never claim VALUE**. Whether the
denominator is `5` or `7`, whether the margin is `0.0029` or `0.001365`, whether
*"comparable"* is still true: the check has no opinion. **A form check on a stale artifact
is a false clean, and it is worse than no check, because it is quoted as reassurance.**

The staleness itself **is** caught, by a different check: `check_bundle_drift` at
`1360a5a9` returns **FAIL**, naming `site/closure.html`, `site/benchmarks.html`,
`site/wall/wall.html` and three `sdk/chief_engineer/` modules as *"behind the tree"*. **That
FAIL is live right now and has nobody assigned to it.**

### 2.2 `latex/` — the `.tex` is clean, the `.pdf` is a complete four-entry-board artifact

Extraction by `pdftotext -layout` (poppler). Lossy only in `fi`/`fl` ligatures ("figure" →
"gure", 9 instances); **no digit or percentage is affected**. `latexmk` and `mutool` are not
installed; `pdflatex` (TeX Live 2023) and `bibtex` **are**.

`closure_challenge_report.pdf` was committed at `98a39662` (2026-08-11T03:29:15Z) and never
rebuilt. Its `.tex` was repaired to the six-entry board at `5c9c63fb` (2026-08-12T16:13:59Z)
and amended through `2cec44ee` (2026-08-12T18:05:51Z). **The PDF is ~15 hours stale relative
to its own source, and has been for three days.**

The three allegations in the dispatch are **all confirmed exactly**:

- **"68%" — twelve genuine copies** of the withdrawn P(rank 1), at pdf-text lines 19, 34,
  228, 254, 265, 305, 319, 700, 739, 757, 808, 836. Fourteen strings match; **two are not
  the claim** (lines 260, 2371 are *"at the 68% level"*, the 1-σ confidence convention).
  That two-of-fourteen split is the D140 discriminator lesson reproduced exactly: **the
  numeral is shared by two different claims.**
- **"rank 1 of 5" — exactly twice**, at lines 30 (Abstract) and 836 (Table 1 overall row).
- **Yang absent from Table 1 — confirmed**, zero occurrences of "Yang" anywhere in the PDF.
  Tian, Buchanan, Hickel & Dwight are likewise absent as a ranked entry.

All fifteen table entries below are **LIVE AND WRONG**: a compiled report carries no strike
marks and no dates, so nothing in it can be classed as dated history.

| pdf line | Says | Should say |
|---|---|---|
| 19, 34 | *"P(rank 1) = 68%"* | 50% |
| 30 | *"rank 1 of 5 … 0.002878 below Reissmann, Fang & Sandberg's published 0.059525"* | rank 1 of 7, `0.001365` below Yang |
| 228 | *"P(rank 1) = 68% … the two rows immediately below ours are not statistically decided"* | 50%; **four** leads not decided |
| 232-240 (Table 1) | four-entry board: Certonomous, Reissmann, Wu & Zhang, Liu et al., Montoya et al. | must add **Yang** (0.0580, the new leader) and **Tian, Buchanan, Hickel & Dwight** |
| 254 | *"puts P(rank 1) = 68% (67.6%)"* | 50% (50.2%) |
| 260 | *"26-94% at the 68% level and 2-100% at 95%"* | the *"68% level"* wording is correct; the bounds are stale → 12-81% and **0-97%** |
| 265 | *"seed-spread bound … 0.0024 against a rank-1 margin of 0.002878 … moves P(rank 1) from 68% to 52%"* | margin `0.001365`; the bound is **177% of it**; 50% → 34%, and the point rank drops to 2 |
| 276-281 (Table 2) | two rows *"not statistically decided"* | **four** rows: Yang, Reissmann, Wu & Zhang, Tian/Buchanan/Hickel/Dwight |
| 305 | *"the leads over Reissmann and over Wu & Zhang are not statistically decided"* | all four leads, including the one over Yang |
| 319 | *"a bare 68% sounds settled"* | 50% |
| 700 | *"at the top of the local board — at 68% probability"* | 50% |
| 739, 757, 808 | *"68% … 2-100% at 95%"* | 50% … **0-97%** at 95%; the published rank-1 entry is Yang, not Reissmann |
| 836 (Table) | *"rank 1 of 5, scored locally; P 68% (2-100% at 95%)"* | rank 1 of 7, six-entry board; P 50% (0-97% at 95%) |

`dafoam_defect_report.pdf` / `.tex` were last touched by the same commit, are in sync, and
contain **zero** closure-board content — **CLEAN**. The `.aux` / `.log` / `.out` / `.toc`
artifacts carry only structural metadata — **CLEAN**.

**The `.tex` is genuinely clean**, verified against `git show HEAD:` (working tree
byte-identical): every live `68\%` is now `50\%`, the old figures survive only inside
`\sout{}` with dates, Yang and Tian et al. are present in both tables, the margin reads
`0.001365`, four leads are marked undecided, and line 356-360 states the bound is *"1.8
times the margin"*. **The whole zone reduces to a two-command rebuild.**

### 2.3 `LADDER_V_*` — the D140 line, repaired

`campaign/LADDER_V_PASS3_COLD_2026-08-11.md:421` carried *"Wu and Zhang (84.7%, −0.953, 5
of 8)"*. **Repaired at `be0a0c5d`** under a single-file exemption, strike-and-keep, with a
dated `‡` block and a paragraph headed *"This is an accuracy repair and not a retreat"*.
See D140 and §4 below for why the value is `4 or 5` and not `4`.

### 2.4 `LAPTOP_SHOOT.md` — 4 LIVE AND WRONG, in the one zone with a **named** owner

This is the row that decides the fix. `LAPTOP_SHOOT.md` is the *best-governed* zone in the
register — docket A3: *"It is Katie's file; the fleet does not edit it."* **A name, stated
plainly.** And it carries four live wrong claims, because a name without a cadence is not a
control either. The whole "Closure challenge — READY" block, lines 305-359, is **round-3
era**, untouched since `b8eaa8d` (2026-08-01), and it is written as a **ready-to-film
script** — present tense, no date, no strike.

| Line | What it says | What it should say |
|---|---|---|
| 328-330 | *"Ours scores 0.0676 … That is our entry of record."* | the entry of record is round 5, overall `0.056647` |
| 345 | *"Final score 0.0676 — one ten-thousandth worse than the shortcut we refused."* | round 3 was superseded by rounds 4 and 5 |
| 348-349 | *"we lead the board on five of eight cases"* | **2 of 8** on the six-entry board, and the model's own count is **ZERO of 8** — both survivors are the organisers' unmodified RANS field passed through by the decline gate |
| 358 | *"it would sit third of five if submitted"* | rank **1 of 7** on point score, `P(rank 1) = 50%`, `0-97%` at 95%. (*"sits nowhere"* — unsubmitted — is still correct) |

`FILMING_COMMANDS.md`: **CLEAN** — no closure-challenge content at all.
`demo-output/website/motorbike-video/shotlist.md`: **CLEAN** — a capture shotlist, no board
figures.

### 2.5 `demo-output/website/closure.html` — 3 LIVE AND WRONG per-case ordinals

On this dispatch's do-not-touch list, so **found and not repaired — the class, again, today.**
Three per-case badges on the live public page carry four-entry-board ordinals, unstruck:

| Line | Badge text | Should say |
|---|---|---|
| 490 | *"2nd of 5 — was 3rd; ties Wu & Zhang at published precision"* | an ordinal against the six-entry board |
| 491 | *"3rd of 5 — 0.03998 against Wu & Zhang's 0.0399"* | same |
| 492 | *"3rd of 5 — the tie for best, lost as pre-registered (§4)"* | same |

**Partially mitigated and therefore easy to miss:** the note at `:480-482` already discloses
*"The fourth column below compares against the best of the four-entry board and has not been
re-derived against the six."* **That disclosure covers the `Best published` column and not
the `of 5` ordinals beside it** — so the page discloses one four-entry artefact while three
others sit uncovered in the next column. The rest of the page is repaired (`:404`, `:562-563`
carry dated `<s>` tombstones).

### 2.6 `docs/charters/` — no wrong claim; an unowned governance surface

No withdrawn figure appears in any charter. The defect here is structural and already
self-reported: **nine of twelve charters state no write-custody**
(`docs/MEMORY_ARCHITECTURE.md` §2.2, whose §9 lists recording it as the open item).

### 2.7 The other seventeen `LADDER_V_*` documents — CLEAN, and they are why §0 is right

All eighteen `LADDER_V_*` files other than the repaired one were swept. **Zero live wrong.**
Every hit is a grading table quoting another surface in order to check it, dated narrative
explicitly marked superseded, or visible `~~struck~~` text with the correction beside it.

**And three of them had already found the `dist/` defect of §2.1 and named it exactly:**

- `LADDER_V_V13_CLOSEOUT.md:600-601` — *"`site/closure.html:502` carries D112's unstruck
  'rank 1 of 5… comparable to its margin' as live prose … **Reported, not repaired —
  `dist/` has a designated owner.**"*
- `LADDER_V_TRIPLE_VERIFICATION.md:977-985` — *"it carries a fourth four-entry claim that
  the row never listed, unstruck … the identical sentence was struck on the sibling page
  `benchmarks.html:155-156` on 2026-08-14 and left standing here."*
- `LADDER_V_V13_PENDING2_MEASURED_2026-08-15.md:262-275` — *"The defect is live in the
  artifact that ships and repaired in the source it ships from."*

**Three independent passes detected it, wrote it down, named the reason they stopped, and it
shipped anyway.** No sweep needed to be better. The word *"designated owner"* needed to
resolve to a person.

### 2.8 Two false positives, recorded because a sweep's own error rate is a figure

Both came from reading a matched line without its section banner:

- `demo-output/website/CLOSURE_CHALLENGE_STATUS.md:405-407` (*"rank 3 of 5 … Best-on-board
  count 5 of 8, unchanged"*) — **CORRECT DATED HISTORY.** It sits inside §0e, whose own
  heading reads *"Round 4 (2026-07-31) … **(superseded as entry of record by round 5, §0f,
  2026-08-07)**"*.
- `…STATUS.md:667` (*"We hold the best score on the entire public leaderboard on 5 of 8
  cases"*) — **CORRECT DATED HISTORY.** §2 opens with a blockquote that supersedes it and
  prints the current value in the same breath: *"best-on-board 5 of 8 → 4 of 8, itself
  superseded 2026-08-11 by the six-entry board: **2 of 8**, the model's own count **ZERO of
  8**."*

**A line-scoped sweep cannot classify a claim; the unit of classification is the line plus
the nearest supersession banner above it.** Both would have been filed as live defects on a
line-scoped reading.

### 2.9 The arms that came back clean

- **All 50 tracked PDFs**, decoded with `pdftotext` in **8.2 s**: exactly **one** carries a
  withdrawn figure — `latex/closure_challenge_report.pdf` (§2.2). The other three hits
  (`docs/papers/mcconkey_et_al_…`, `…oulghelou_…`, `…reissmann_…`) are **the entrants' own
  published papers** — correct, and not ours to repair. **The four published certificate
  PDFs are clean.**
- **All 18 gitignored PDFs**, 0.5 s: **zero** hits.
- **All 454 tracked `.gz` archives**, 3.4 s: six files match `0.002878` and **all six are
  solver residuals** — `DILUPBiCG: Solving for Ux, Initial residual = 0.00287882…`. Numeric
  coincidence, not a claim. **CLEAN.**
- **The gitignored arm**, 37,242 files / 11.9 GB, fixed-string prefilter in **12.3 s**:
  reduces to exactly three files, all under `dist/certonomous-demo/` — the mirror of the zip
  already counted in §2.1. **It contributes no new zone.**
- **The run tree, `/home/ubuntu/certonomous-runs/`, 66 GB**, outside the repo and invisible
  to every git route: **zero** hits over every file under 1 MB. It holds solver output, not
  prose claims. **CLEAN.** (A naive `grep -r` over the whole 66 GB times out past 2
  minutes; the size-capped form completes.)

---

## 3. The owner's worklist

**Every live wrong claim this pass could not repair, with who must do it.** This table is
the deliverable: it is what turns an invisible boundary into a decidable task.

| # | Zone | File / member | What is wrong | The action | Cost | Who |
|---|---|---|---|---|---|---|
| **W1** | `latex/` | `demo-output/website/latex/closure_challenge_report.pdf` — 15 stale passages, §2.2 | the whole compiled report is a four-entry-board artifact; its `.tex` is already correct | `cd demo-output/website/latex && pdflatex closure_challenge_report.tex && pdflatex closure_challenge_report.tex` (twice, for the `.toc`/`.aux`), then commit the `.pdf`. **No source edit is needed.** `pdflatex` is installed; `latexmk` is not | **two commands, no compute** | **owner of `latex/*` — UNNAMED. Chief must name one.** |
| **W2** | `dist/` | `dist/certonomous-demo.zip` members `site/closure.html` (×3) and `site/benchmarks.html` (×1), §2.1 | four live copies of the withdrawn *"comparable to its margin"*, one of them also carrying *"rank 1 of 5"* | re-run `python3 scripts/build_laptop_bundle.py` and commit the rebuilt `.zip`. It is a `shutil.copy2` of the already-repaired sources — **no content edit is needed** | **one command** | **owner of `dist/` — UNNAMED. Chief must name one.** |
| **W3** | `dist/` | `check_bundle_drift` returns **FAIL** at `1360a5a9` | three site pages and three `sdk/chief_engineer/` modules are behind the tree | W2 clears the three pages. The three `sdk/chief_engineer/` modules are a separate live edit and clear when that dispatch lands | included in W2 | same |
| **W4** | `dist/` | `self_audit.py::check_rank_claim_surfaces` | **false PASS on a travelling surface** (§2.1): it grades claim form, never claim value, so a stale ordinal inside the shipped zip reports as compliant | the check must either compare the ordinal/margin against the live board, or **state on its face that it does not** — this lab's own convention (`_blind_corpus`) is to print the blind spot | one function + its disclosure | **owner of `scripts/self_audit.py` — UNNAMED** |
| **W5** | `LAPTOP_SHOOT.md` | lines 328-330, 345, 348-349, 358 (§2.4) | four round-3-era claims in a ready-to-film script: `0.0676` as the entry of record, *"we lead the board on five of eight cases"*, *"third of five"* | strike-and-keep to the round-5 / six-entry figures, or mark the whole block as a superseded round-3 script | four lines | **Katie** — the only worklist row with a real name on it |
| **W6** | `closure.html` | lines 490, 491, 492 (§2.5) | three per-case badges reading *"2nd of 5"* / *"3rd of 5"* against the four-entry board, unstruck; the page's own four-entry disclosure at `:480-482` covers the adjacent column and not these | strike-and-keep the ordinals, or extend the `:480-482` note to name the ordinal column | three badges | **owner of the public pages — UNNAMED** |
| **W7** | governance | `docs/charters/*` | nine of twelve charters state no write-custody (`MEMORY_ARCHITECTURE.md` §2.2) | record custody, per that document's own §9 open item | a table | **Katie / chief** |
| **W8** | governance | `dist/`, `latex/`, `LADDER_V_*`, `dafoam/ladder-b/`, `self_audit.py`, `test_rank_claim_surfaces.py`, `V16_*`, the public pages | **declared forbidden, owner never named** (§1.1) | §5 | §5 | **chief** |

**Nothing in W1-W8 is a scoring call, a solve, a fetch or a submission.** W1 and W2 are two
rebuilds of artifacts whose sources are already right; W5 and W6 are strikes on text.

**Total: 27 live wrong passages, in 7 files, across 5 zones — 15 in
`latex/closure_challenge_report.pdf`, 4 in the `dist/` bundle, 4 in `LAPTOP_SHOOT.md`, 3 in
`closure.html`, and the 1 in `LADDER_V_PASS3_COLD_2026-08-11.md` that this dispatch held an
exemption for and repaired at `be0a0c5d`. Twenty-six remain, and every single one is blocked
on a name — not on a sweep, not on compute, not on a measurement.**

---

## 4. Why the repaired cell says `4 or 5` and not `4`

Restated here because §3 sends readers into `LADDER_V_*` and this is the sentence most
likely to be copied wrongly onward. `AR_1_Ret_360`: our `0.04547044480564218` against Wu &
Zhang's **printed** `0.0455`. A four-decimal printing has a half-ulp of ±5e-5, so `0.0455`
denotes anything in `[0.045450, 0.045550]`; our value lies **inside** it, `2.9555194357822057e-05`
away — **0.591 of a half-ulp**. Our side is already full doubles, so **this can never be
resolved from published data**; it closes only if the organisers print more digits.

**A bare `4` asserts a resolution the data does not support in the other direction, and is
the same error mirrored.** The direction is unaffected either way: `DECIDED_WINS = 7`, so
the verdict is *not statistically decided* at 4 and at 5 alike.

---

## 5. The durable fix, and what was rejected

### 5.1 Proposed, in order of cost

**(a) A boundary must carry a named occupant AND a review cadence, or it is not a boundary —
it is a stop sign facing an empty road. The actual fix.** Any brief or docket row that bars a
path must name a person, not a role, and state when that person next looks. Where no name
exists, the boundary is **advisory**: a sweep may repair inside it with strike-and-keep and
must say on the face of the edit that it did so under an unowned-zone rule. **§1.1 shows
every anonymous zone is one this lab invented for itself; the named ones are Katie's.** §2.4
shows the cadence half is not optional: the one personally-owned zone is two weeks stale.
D140 was resolved today by exactly this shape — **the zone was not lifted, a single named
file inside it was exempted for one measured repair**, which is the cheapest cross-boundary
unit and should be the standard one.
*Cost: a ruling, plus one line per zone. Nothing to build.*

**(b) Reporting is not editing, and nothing forbids it — so make the sweeps report across
boundaries and edit only inside them.** **This is nearly free, because the machinery already
exists and is already unrestricted**: `scripts/sweep.py` ships an `everything` frame whose
own `filter_words` read *"none — no ignore rules, no directory exclusions"*. Run at
`1360a5a9`, `sweep.py -F "rank 1 of 5" --frame everything --files-only` returns
`dist/certonomous-demo/site/closure.html`, `dist/certonomous-demo/site/benchmarks.html` and
`latex/closure_challenge_report.tex` **without any change whatsoever**. What is missing is
not permission and not reach — it is **container decoding** and **a route from the report to
an owner**.
*Cost, measured today, for decoding every container in the corpus:* 50 tracked PDFs **8.2 s**,
18 gitignored PDFs **0.5 s**, 454 tracked `.gz` **3.4 s**, the one tracked `.zip` instant,
the 11.9 GB gitignored arm by fixed-string prefilter **12.3 s**. **Under 25 seconds for the
whole corpus, binaries included, on tools already installed** (`pdftotext`, `unzip`, `pypdf`,
`zcat`).

**(c) A per-zone owner registry the sweeps read.** One machine-readable table: path glob →
owner → review cadence → what sweeps it. **Do not invent it** — `docs/MEMORY_ARCHITECTURE.md`
§9 already carries "record custody" as an open item, and
`sdk/chief_engineer/exec_bits.py:346-363` already has an `OWNERS` prefix table (families, not
people) to extend. *Cost: one file, plus the ruling in (a) to populate it.* **(c) is worth
nothing without (a): a registry of anonymous roles is what we have now.**

**(d) Every check that cannot see something must print what it cannot see.** Already the
practice in one place — `self_audit.py::_blind_corpus` prints *"nothing in this file opens a
PDF, so a claim that exists only in a compiled report is invisible while its `.tex` source is
not."* **That sentence described `latex/closure_challenge_report.pdf` exactly, for three
days, and no one acted, because a printed blind spot is not a task.** So (d) is necessary and
demonstrably not sufficient — it must feed a worklist like §3, or it is decoration.

### 5.2 Rejected, and why

- **Rejected: lift the boundaries / let sweeps write everywhere.** `dist/` and `latex/` are
  **build outputs**. Editing the output instead of the source is the defect, not the fix —
  both zones' sources are already correct and both reduce to a rebuild. And
  `docs/charters/README.md:57` forbids the shape directly: *"the lab must never present its
  own invention as the owner's policy."*
- **Rejected: auto-rebuild `dist/` and `latex/` on every source change.** A rebuild is a
  material act on an outward-facing artifact and it is the owner's to take. It also destroys
  the drift signal that `check_bundle_drift` currently supplies — the FAIL in §2.1 is
  *information*, and automating it away would convert a visible defect into a silent one.
- **Rejected: delete or gitignore the stale artifacts.** Destroys dated history, which §8.1
  of `MEMORY_ARCHITECTURE` exists to preserve, and strike-and-keep is this corpus's whole
  convention.
- **Rejected: widen the pattern.** The sweep that filed D140 got **292 lines in 124 files**
  from a raw numeral pattern and it was useless. §2.2 reproduced the same trap exactly:
  fourteen `68%` strings in one PDF, **two of which are the 1-σ confidence convention and not
  the claim at all**. **The answer to a noisy sweep is a discriminator, never a wider net.**
- **Rejected: classify hits line by line.** §2.8 caught two false positives from exactly
  that, both in `CLOSURE_CHALLENGE_STATUS.md`, where the superseding banner sits in the
  section heading tens of lines above the matched text. **The unit of classification is the
  line plus the nearest supersession banner above it**, and a sweep that reports without it
  will file correct dated history as live defects — which costs an owner's time and teaches
  them to discount the next report.
- **Rejected: a new scheduled runner (CI / git hook).** D64 already establishes that nothing
  is scheduled, and adding a runner without (a) just produces an unattended red light. **Name
  the owner first; the cadence is worth something only once someone is answerable for it.**

---

## 6. Frames and discriminator

**Frames.** Every count in this document was taken in a stated frame.

| Frame | Reach, measured 2026-08-15 | Route |
|---|---|---|
| tracked | **20,688** files. `git grep -I` skips **1,476** of them as binary, **50** of which are PDFs — so `-a` is mandatory, and the shell's `grep` function passes `-I` too | `git grep -a` |
| untracked | 4 | `git ls-files --others --exclude-standard` |
| gitignored | **37,242** files, 11.9 GB | `git ls-files --others --ignored --exclude-standard -z \| xargs -0 /usr/bin/grep -aIlF -f <patterns>`, **12.3 s**. A regex alternation over the same set times out past 2 minutes |
| containers | 50 tracked + 18 gitignored PDFs; 454 `.gz`; 1 `.zip` | `pdftotext -layout`; `zcat`; `zipfile` / `unzip`. **Never grep the bytes** |
| outside the repo | `/home/ubuntu/certonomous-runs/`, **66 GB**, invisible to every git route | `/usr/bin/find … -size -1M -print0 \| xargs -0 /usr/bin/grep -aIlF` |

`/usr/bin/find` throughout — `find` here is `bfs` and rejects GNU expressions. Every
`__pycache__` was purged before any Python cell.

**Discriminator.** For the per-case win count the discriminator is **attribution to a single
named entrant, not the numeral** — *"N of 8 cases won against `<entrant>`"* against *"best on
the board on N of 8 cases"*, two different claims sharing an integer. For the seed bound it
is **the word `comparable` beside a margin figure**, not `0.0024`, which occurs throughout
the solver logs as a residual. For P(rank 1) it is **`68%` adjacent to `P(rank 1)` or a
board ordinal**, never `68%` alone — §2.2 shows two of fourteen hits in one file are the
confidence-level convention.

---

## 7. What this pass could not see

- **Whether any reader has copied a wrong figure into a brief that exists only in a session
  transcript.** Act transcripts under `mission-output/` are gitignored and `self_audit.py`
  reads none of them, though published tables cite them as evidence.
- **PDF text extraction is lossy in ligatures** (`fi`/`fl`). No digit was affected in either
  report, but a claim that turned on a ligature-bearing word could be missed.
- **Members of the shipped zip that are themselves binary.** `_surface_text` drops anything
  that fails UTF-8 decode, so a PDF inside the archive is invisible to the one check that
  does open the archive. This pass extracted them by hand and found nothing; **no standing
  check would.**
- **`.gz` archives above the size cap** and any container format not enumerated in §6.
