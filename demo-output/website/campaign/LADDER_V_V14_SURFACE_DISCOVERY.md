# Ladder V — rung V14 (A14): mechanical surface discovery

**Executed 2026-08-10.** Owner: an agent that has written to none of the surfaces
below. **Read-only except this file.** No fix was applied to any surface; every
stale surface is reported to its owner. Zero scoring calls. Nothing sent.

**What this rung replaces.** V10's cross-surface sweep walked a hand-maintained
list of surfaces. The ladder's first full run then found three stale claims on
surfaces that list had never contained — a tracked shipping archive, a live audit
guard, and a public page carrying a struck sentence. **This rung is a search, not
a list**, and it fails if its method is a list. What follows is the search, its
frames, its proven reach, and its stated blind spots.

**Method summary.** Four literal families (`0.0741`, `0.0676`, `0.0654`,
`0.0566`/`0.056647`) plus every case-level value read out of the round-5 record
(not guessed — sourced from `closure_challenge_round5_qcr.json`
`official_test_harness_result` and `CLOSURE_CHALLENGE_STATUS.md` §0f), plus the
struck prior-art sentence and its distinctive fragments, run across six frames:
the whole working tree as text, the gzip frame, the tracked shipping archive
opened, the PDF frame extracted, the git-history frame, and the image frame
(named, partly closed).

---

## 1. The literals, and where they came from

Sourced, not guessed. `demo-output/website/closure_challenge_round5_qcr.json`
→ `official_test_harness_result`, cross-read against
`demo-output/website/CLOSURE_CHALLENGE_STATUS.md` §0f (lines 475–485).

| Round | Overall (4 dp) | Overall (full) |
|---|---|---|
| 2 | 0.0741 | — |
| 3 | 0.0676 | — |
| 4 | 0.0654 | 0.06543140783850523 |
| **5 (entry of record)** | **0.0566** | **0.056647191704213645** |

Round-5 per-case, 4 dp and full precision:

| Case | 4 dp | full |
|---|---|---|
| `alpha_15_13929_4048` | 0.0501 | 0.05010529499681675 |
| `alpha_15_13929_2024` | 0.1011 | 0.10111218200472648 |
| `alpha_05_4071_4048` | 0.0461 | 0.04610779144551565 |
| `alpha_05_4071_2024` | 0.0719 | 0.07186293244687289 |
| `AR_1_Ret_360` | 0.0455 | 0.04547044480564218 |
| `AR_3_Ret_360` | 0.0400 | 0.039982156323801255 |
| `AR_14_Ret_180` | 0.0353 | 0.035338619029087186 |
| `NASA_2DWMH` | 0.0632 | 0.0631981125812468 |

Superseded per-case values also searched, because a stale surface carries *those*:
round-4 ducts `0.0811` / `0.0775` / `0.0325`; round-3 ducts `0.0303` / `0.0919` /
`0.0862`; the accept bar `0.065438` / `0.06543`; Reissmann's published `0.059525`.

**The struck prior-art sentence**, recovered from the record rather than
paraphrased. It was struck on 2026-08-05 and the correction landed on
`closure.html` in Pass 2 (`92562841`, 2026-08-10). `git show 92562841 --
demo-output/website/closure.html` gives the removed lines verbatim:

> *"A classifier that reads only the uncorrected solve and controls where a
> data-driven correction is allowed to act has been published repeatedly —
> Ling and Templeton in 2015, Wu, Wang, Xiao and Ling in 2017, Steiner, Dwight
> and Viré in 2022, Buchanan, Lăcătuş, West and Dwight in 2025."*

Why it is wrong: Ling & Templeton and Wu et al. **identify** where the baseline
is unreliable and control nothing; only Steiner et al. and Buchanan et al.
**control** a correction with a classifier. Rolling all four into one list credits
two author groups with a mechanism they never reported — to a readership that
includes two of the benchmark's own authors.

Fragments searched (any one of which catches the sentence or a near-variant):
`published repeatedly`, `controls where a data-driven correction`, `Templeton`,
`Steiner, Dwight`, `L.c.tu` (Lăcătuş, encoding-tolerant).

---

## 2. Frames, reach proofs, and counts

Every count below states the frame it was measured in. **Every negative carries a
positive control run in the same frame.**

### Frame A — the working tree as text

`/bin/grep -rIn --exclude-dir=.git` over the repo root. `/bin/grep` used
explicitly throughout: this lab's shell `grep` is a wrapper, and the single
highest-exposure stale surface found by this rung
(`dist/certonomous-demo/`) is **gitignored at `.gitignore:72`** — exactly the
class a `.gitignore`-honouring search is built to skip.

| Measure | Value |
|---|---|
| Files present in frame (excl. `.git`) | 48,654 |
| Tracked files | 20,493 |
| Untracked or ignored entries | 28,629 |
| Repo size searched (excl. `.git`) | 15 GB |
| Overall-literal hit lines | **178,262** across **4,383 files** |
| Case-level-literal hit lines | **325,437** |
| Prior-art fragment hit lines | **100** |
| Timeouts | 0 (each sweep completed; exit 0 recorded) |

**Reach proof — untracked trees are inside the frame**, with a positive control
in each:

| Tree | Tracked files | Files present | Sweep hit lines | Positive control |
|---|---|---|---|---|
| `mission-output/` | 0 | 8,625 | 5,079 | 1,454 files match a known token |
| `demo-output/website/solve_registry/` | 0 | 297 | 4,156 | 288 files readable as text |
| `sdk/chief-engineer-runs/` | 0 | 1,568 | 5 | — |
| `chief-engineer-runs/` (repo root) | 0 | 3 | 0 | 1 file readable as text — **the null is a real absence, not an unreachable tree** |
| `dist/certonomous-demo/` | 0 (**gitignored**) | 82 | 7 | struck sentence found at lines 254–256 |

### Frame B — the gzip frame

529 `.gz` files, searched with `zgrep` via `find -print0 | xargs -0`.

- **136 files carry a score literal. All 136 are numeric coincidence** — solver
  residuals, force coefficients, `bounding epsilon` lines, `polyMesh/points`,
  `U`/`p`/`phi` fields. Verified by decompressing and reading matched lines, e.g.
  `MODEL_FORM_runs/N_a0_kEpsilon/log.simpleFoam.gz`:
  `Initial residual = 0.05667097726`, `Cd(r): -0.07419835508`,
  `bounding epsilon … average: 0.06545661788`.
- **Zero prior-art hits.** Positive control for that null: `zgrep -c "Time = "` on
  `W1_runs/fine/log.simpleFoam.gz` returns **34,000** — zgrep reaches inside these
  files; the prior-art null is an absence, not a broken pipe.
- The `xargs` invocation exits 123 because `zgrep` returns 1 on non-matching
  files. **That is not a truncated sweep** — the per-file results are complete and
  the positive control proves it.

### Frame C — the tracked shipping archive, opened

`dist/certonomous-demo.zip` — **tracked** (`git ls-files dist/` returns exactly
this one path), 1,425,076 bytes, committed `c83c7240` on 2026-08-01. Extracted to
scratch and searched. **85 files.** No nested archives (`unzip -l` shows no
`.zip`/`.gz`/`.tar`/`.whl` members), so no second layer to open.

**10 score-literal hits in 3 files, and the struck prior-art sentence in 1.**
Positive control: `Closure` found in `site/closure.html` in the same pass.

`dist/certonomous-demo/` is the **untracked, gitignored staging mirror** of the
same bundle. `diff -rq` against the extracted zip: identical except a
`__pycache__` directory and `site/wall/wall.html`. **Both copies carry the same
stale claims.**

### Frame D — the PDF frame (binary; `grep -I` skips it)

**68 PDFs**, all extracted with `pdftotext`, **68 non-empty, 0 extraction
failures, 0 empty (no image-only PDFs)**. Positive control: `Certonomous` found in
2 extracted files.

- **21 score hits, all in `demo-output/website/latex/closure_challenge_report.pdf`.**
  It is **CURRENT** — carries `0.056647` as the entry of record, with rounds 2–4
  labelled superseded. Built from `closure_challenge_report.tex`; both files share
  mtime `2026-08-10 16:22`, and the PDF's last two commits (`15f2921a`,
  `170b3426`) are the round-5 catch-up and the P(rank 1) addition. In sync.
- **Zero prior-art fragment hits in any PDF.**

### Frame E — the git-history frame

94 commits touch `0.0654` by content; 34 commit messages carry a score literal.
**All NOT-A-CLAIM by construction** — a commit message is an immutable dated
record of what was true when written, and rewriting history to "fix" one would be
strictly worse than the stale number.

### Frame F — the image frame (named, partly closed)

**No text search can read a number rendered into a PNG.** 955 PNGs in the repo; 25
have closure/benchmark/wall/score in their path. There are **0 SVGs** (an SVG would
have been text and inside Frame A).

Spot-closed by reading one: **`demo-output/website/closure_eval/metric_vs_physics.png`
plots the round-4 per-case scores** (duct points at ≈0.081 / ≈0.078 / ≈0.033). Its
own subtitle names its source — *"scores:
closure_challenge_trained_entry_round4_duct.json"* — so it is **HISTORICAL, correctly
labelled, and must not be "fixed"**. But it demonstrates the frame is not empty:
superseded numbers do live in images here, and 24 further closure PNGs were **not**
opened. See §6.

---

## 3. Hit table — every claim-carrying surface, classified

Frames A + C + D reduce to **227 hit lines in claim-carrying file types**
(`.md .html .tex .py .txt`) plus the claim-carrying JSON/CSV. Everything else in
the 178,262 is Frame-A numeric data — see §5.

Classification key: **CURRENT** = round-5 number with its caveats · **STALE** = an
old number presented as current · **HISTORICAL** = an old number correctly
labelled as history, **correct and must not be changed** · **NOT-A-CLAIM** =
fixture, changelog, commit message, or numeric coincidence.

### 3.1 STALE

| # | Path | Line | Literal | Evidence |
|---|---|---|---|---|
| 1 | `dist/certonomous-demo.zip` → `certonomous-demo/site/closure.html` | 99 | `0.0654` | hero KPI, `our entry of record` — round 4 presented as current |
| 2 | ″ | 100 | `0.0676` | `was 0.0676 until the duct fix below` |
| 3 | ″ | 110 | `0.0654` | `0.0654 means we are about 6.5% wrong` |
| 4 | ″ | 186 | `0.0654` | standings row `— · Certonomous 0.0654 · UNSUBMITTED · NO RANK` |
| 5 | ″ | **254–256** | *(prior art)* | **the struck sentence, verbatim** — `controls where a data-driven correction is allowed to act has been published repeatedly — Ling and Templeton in 2015, Wu, Wang, Xiao and Ling in 2017, Steiner, Dwight and Viré in 2022, Buchanan, Lăcătuş, West and Dwight in 2025` |
| 6 | `dist/certonomous-demo.zip` → `certonomous-demo/site/benchmarks.html` | 69 | `0.0676` | KPI `overall score` — round 3 presented as current |
| 7 | `dist/certonomous-demo.zip` → `certonomous-demo/snapshot/lab_stats.json` | 55–56 | `0.0676` | `"our_score": 0.0676`; `our_entry` text also says `across fou[r]` scoring calls — the record documents six |
| 8–14 | `dist/certonomous-demo/site/closure.html`, `site/benchmarks.html`, `snapshot/lab_stats.json` | same | same | **untracked, gitignored** staging mirror carrying items 1–7 identically |
| 15 | `LAPTOP_SHOOT.md` | 328 | `0.0676` | spoken track: *"Ours scores 0.0676, about 35% closer to reality. **That is our entry of record.**"* |
| 16 | ″ | 345 | `0.0676` | *"Final score 0.0676 — one ten-thousandth worse than the shortcut we refused"* |
| 17 | ″ | 317 | `0.0676` | *"the round-3 mean reproduces 0.0676 exactly … They are right."* — true of round 3, but the doc uses it as the current verification |
| 18 | `demo-output/website/CLOSURE_RANK1_CAMPAIGN.md` | 25, 38, 60 | `0.065438` | *"Our entry of record is round 4, 0.065438."* Present tense, no dated supersession note |
| 19 | `demo-output/website/closure_eval/closure_eval_master_table.md` | 17 | `0.0654` + full round-4 per-case row | row `ours, round 4 (recorded, not submitted)` in a doc titled *master statistics table*, no supersession note. Companion `closure_eval_master_table.json` same row |
| 20 | `sdk/scripts/export_closure_submission_csvs.py` | 6 | `0.0676` | docstring: *"The lab's **round-3 entry of record** (overall 0.0676…)"* — present-tense status on a superseded round, in a live script |
| 21 | `sdk/scripts/closure_round4_manifest.py` | 116 | `0.0654` | writes *"round 4 (**the entry of record**, overall 0.0654)"* into the generated manifest; the string is on disk in `closure_challenge_submission_round4/MANIFEST.json` |
| 22 | `demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md` | 380 | `0.0654` | *"nothing here changes **the recorded** 0.0654"* — definite article pins round 4 as the record |
| 23 | `docs/NUMERICS_KNOWLEDGE.md` | 560 | `0.0741` | *"beats our **current** 0.0741 on the PH-only sub-score"* — `current` pins round 2 |
| 24 | `demo-output/website/closure_challenge_C2_error_decomposition.md` | 136 | `0.0741` | standings table row `**ours (unsubmitted)** | **0.0741**` with **no round label**; §1 scopes the doc to round 2 but this table does not |
| 25 | `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md` | 249 | `0.0654` | *"citable wherever the lab explains what 0.0654 means"* — minor, illustrative |

**Adjacent finding, same class, not a score literal.** The mechanical sweep also
surfaced the *"INTERNAL ONLY; the 68% figure never appears in an external claim"*
gate on P(rank 1) still live in `CLOSURE_CHALLENGE_STATUS.md` §0f (≈544–545) and
`agenda/CHALLENGE_LANDSCAPE.md` (§5 block). The V8 amendment of 2026-08-11
**withdrew** that internal/external split — the figure now travels with the entry.
Reported to those files' owners; outside this rung's literal set, recorded because
a search found it and a list would not have.

### 3.2 HISTORICAL — correct, and must not be "fixed"

These carry superseded numbers **with the label that makes them true**. Changing
any of them would destroy the record this lab's supersession convention exists to
keep.

| Path | Why it is correct |
|---|---|
| `demo-output/website/CLOSURE_CHALLENGE_STATUS.md` (31 hits) | header states both updates; §0e titled *"…is now 0.0654 (superseded as entry of record by round 5, §0f)"*; §2/§3/§5 carry dated superseded blocks. The convention is stated in the file itself |
| `demo-output/website/closure.html` (19 hits) | hero `0.0566`, rounds table `0.0741 → 0.0676 → 0.0654 → 0.0566` explicitly per-round. **CURRENT + HISTORICAL**. Prior-art paragraph is the corrected two-part split |
| `demo-output/website/benchmarks.html` | `0.0566`, rank-1-local caveat. **CURRENT** |
| `demo-output/website/wall/wall.json`, `benchmarks.json` | `"our_score": 0.0566`, six scoring calls. **CURRENT** |
| `demo-output/website/latex/closure_challenge_report.tex` + `.pdf` | `0.056647` throughout; rounds 3/4 rows labelled *superseded*. **CURRENT** |
| `demo-output/website/ACTIVE_RESEARCH.md` (14 hits) | round-5 header; `0.0654`/`0.0676` appear only in dated log entries, incl. line 834 which states *"0.0654 when this was written; 0.0566 since round 5 superseded it on 2026-08-07"* |
| `demo-output/website/agenda/CHALLENGE_LANDSCAPE.md` | §5 carries an explicit dated supersession block and scopes the `0.0654` bullets as *"this sweep's dated 2026-08-02 record"*, with its own rule that the superseded numbers may not be used |
| `demo-output/website/closure_challenge_stability_physicality_audit.md` | the `0.0654` sits in §0, a **pre-stated-thresholds section frozen before the runs**. Editing it would forge a pre-registration |
| `campaign/R5_PREREGISTRATION.md`, `campaign/R5_RULE_FREEZE.md`, `closure_challenge_R5_ALPHA05_REGIME_PREREGISTRATION.md` | frozen pre-registrations; `0.065438` is the accept bar, correctly |
| `CLOSURE_METHODS_COMPARISON.md` §1.1, `closure_challenge_C6_hump_decision.md`, `CLOSURE_METHOD_PRIORITY_REVIEW.md` | dated evidence records, round explicitly named |
| `CLOSURE_CHALLENGE_SUBMISSION_DRAFT.md` (16 hits) | the `0.0654` cover-email text is quoted **as a recorded Pass-2 defect**, and §10 is a dated round-5 addendum |
| `campaign/LADDER_V_PASS1/2/3_*`, `LADDER_V_RUNGS_*`, `PROBABILITY_OF_RANK_*`, `DEAD_LEVER_AUDIT_*`, `EIG_RANKING_LOOKBACK_*` | verification records; superseded numbers appear as findings |
| `campaign/reports/MORNING_REPORT_2026-08-04.md`, `_2026-08-07.md` | dated reports |
| `scripts/self_audit.py:274, 313` | comments recording the **past** mis-pin. The guard now reads `closure_challenge_round5_qcr.json` — **the round-3 pin found by Pass 2 is fixed**, and this rung re-confirms it |
| `sdk/scripts/build_benchmarks.py:85, 102, 126` | round 5, `0.0566`, six calls, rank-1-local caveat. **CURRENT** |
| `sdk/tests/test_mega_batch.py:247–254` | asserts `our_score == 0.0566`. **CURRENT** test fixture |
| `sdk/scripts/apply_closure_ph_gate.py:6` | *"round 2 scored 0.0741"*, labelled |
| `docs/charters/RESULT_PRIORITY_CHARTER.md:150` | cites the 0.0741-vs-0.0676 drift **as the worked example of the violation** |
| `docs/standards/INFRA_FAMILY_SUPERVISION_GUIDELINES.md:336` | findings record of the stale round-3 test pin, marked fixed |
| `docs/PRODUCT_LIST.md` (8 hits) | §4B is a strikethrough chain `~~0.0741~~ → ~~round 4, 0.0654~~ → **ROUND 5, 0.056647**`; the rest are dated changelog lines |
| `demo-output/website/agenda/docket.json` (8 hits) | dated docket outcomes |
| `demo-output/website/dafoam/ladder-b/B1_reproduction_plans.md` | dated 2026-07-28, cites `…round2.json` by name |
| `closure_challenge_trained_entry_round2/3/4*.json`, `closure_challenge_submission{,_round4}/` CSVs + MANIFESTs | round-scoped artifacts; their whole purpose is to hold the superseded numbers |
| `closure_eval/metric_vs_physics.png` | round-4 per-case scores, but the figure **names `…round4_duct.json` in its own subtitle** |

### 3.3 CURRENT

`closure.html` · `benchmarks.html` · `wall/wall.json` · `benchmarks.json` ·
`latex/closure_challenge_report.tex` + `.pdf` · `docs/PRODUCT_LIST.md` §4B ·
`ACTIVE_RESEARCH.md` header · `CLOSURE_CHALLENGE_STATUS.md` §0f ·
`closure_challenge_round5_qcr.json` · `closure_challenge_submission_round5/`
(README, DESCRIPTION_DOCUMENT, MANIFEST, CSVs) · `sdk/scripts/build_benchmarks.py`
· `sdk/tests/test_mega_batch.py` · `scripts/self_audit.py`.

**Every one of these carries `0.0566`/`0.056647` with the local-scoring caveat.**
The five surfaces V10 checked are still consistent; this rung's finding is that
the surfaces V10 did **not** check are where the drift survived.

---

## 4. STALE list ranked by exposure

Public and shipping first. **Reported, not fixed** — other agents own most of
these and several are live.

| Rank | Surface | Exposure | Owner action | What rebuilds it |
|---|---|---|---|---|
| **1** | **`dist/certonomous-demo.zip`** — TRACKED, and it ships. Round-4 hero `0.0654`, round-3 `0.0676` KPI and `lab_stats`, **and the struck prior-art sentence** | **Highest.** A tracked archive is handed to outsiders as-is. It credits two author groups — including authors of the benchmark being entered — with a mechanism they never reported, and announces a superseded score with no caveat | Rebuild the bundle | **`scripts/build_laptop_bundle.py`.** It copies `demo-output/website/{closure.html,benchmarks.html,wall/wall.html}` — **all three are already correct** — and re-snapshots `chief_engineer.lab_stats.lifetime_counters()`. **A plain re-run fixes every item 1–7 with no hand-editing**, provided the live `lab_stats` counter is itself round-5 |
| **2** | **`dist/certonomous-demo/`** — untracked **and gitignored** (`.gitignore:72`) staging mirror, same four defects | Ships if re-zipped; invisible to any `.gitignore`-honouring search | Regenerated by the same rebuild | same script |
| **3** | **`LAPTOP_SHOOT.md`** — the spoken 60-second track says `0.0676` **is** the entry of record | **Public-facing by design.** This is read aloud on camera. It also carries *"we lead the board on five of eight cases"*, the best-on-board claim **this lab withdrew on 2026-08-01** | Katie's — it is her shoot script | Hand-maintained |
| 4 | `demo-output/website/CLOSURE_RANK1_CAMPAIGN.md` | Internal, but it is the campaign plan and its premise (reach rank 1) has since been met | needs a dated supersession note, like §0e got | Hand-maintained |
| 5 | `demo-output/website/closure_eval/closure_eval_master_table.md` + `.json` | Internal; titled *master statistics table*, so a reader takes the `ours` row as current | re-run, or add a supersession note | **`sdk/scripts/closure_eval_battery/build_master_table.py`** — the literal `0.0654` is hard-coded at its line 330 |
| 6 | `sdk/scripts/export_closure_submission_csvs.py:6` | Live script docstring calling round 3 *the entry of record* | one-line docstring fix | Hand-maintained |
| 7 | `sdk/scripts/closure_round4_manifest.py:116` | The string is written **into** `closure_challenge_submission_round4/MANIFEST.json`; the manifest is legitimately round-4, the parenthetical *"the entry of record"* is not | drop the parenthetical | Re-running the script rewrites the manifest |
| 8 | `demo-output/website/CLOSURE_EVALUATION_PROTOCOL.md:380` | Internal protocol doc, definite article | one word | Hand-maintained |
| 9 | `docs/NUMERICS_KNOWLEDGE.md:560` | Internal; `current` pins round 2 | one word | Hand-maintained |
| 10 | `demo-output/website/closure_challenge_C2_error_decomposition.md:136` | Internal; unlabelled `ours (unsubmitted) 0.0741` row | add the round label | Hand-maintained |
| 11 | `demo-output/website/agenda/LIBRARY_ACCESS_LIST.md:249` | Internal, illustrative | lowest priority | Hand-maintained |

**One observation the ranking makes visible.** Items 1, 2 and 5 are **built
artifacts whose sources are already correct**. The stale claim is not in the
prose — it is frozen in an output nobody re-ran. That is the same failure mode as
the round-3 `self_audit.py` pin: a derived surface outliving its source.

---

## 5. NOT-A-CLAIM — the bulk of the hits, and why they are not findings

Of 178,262 Frame-A hit lines, **the overwhelming majority are numeric coincidence
in CFD data**. Four significant figures beginning `0.0` is a common float in a
turbulence solve. Verified by reading matched lines, not assumed:

- `demo-output/website/mega-batch/ledger.jsonl` — 262 hits, all of the form
  `"kinematic_viscosity": 0.06542` / `0.06541` / `0.065436`.
- `demo-surfaces/motorBike.obj`, `campaign/F8_runs/.../blade.stl` — vertex
  coordinates.
- `R4_runs/*/constant/polyMesh/points`, `F7_runs/.../0/C`, `.../U`, `.../phi`,
  `MODEL_FORM_runs/*/log.simpleFoam` — mesh and field data, solver residuals.
- `mission-output/**` field JSONs, `adjoint-optimization/a2_wing_iter_*.json`,
  `W2_sparta_runs/regression/cbfs_discovery_*.json` — solver output.
- All 136 gz hits (Frame B).
- **`demo-output/website/dafoam/ladder-a/A3_onera_m6.md:99`** — `0.0741` is an
  **ONERA M6 C_p RMS deviation**, an entirely different quantity that happens to
  share the digits. The clearest illustration of why a literal search must be
  followed by classification, and why an automated fixer would be dangerous here.
- `sdk/tests/fixtures/ledger_slice.jsonl`, `control_room_ahmed_stream.jsonl` —
  test fixtures.
- 34 commit messages and 94 commits by content (Frame E).

---

## 6. What this frame structurally cannot contain

Stated plainly, because a rung whose method is a search owes the boundary of the
search.

1. **Rendered text inside images.** 955 PNGs, 0 SVGs. `grep` cannot read a number
   drawn into a raster. **This is not a hypothetical gap**: I opened
   `closure_eval/metric_vs_physics.png` and it does carry round-4 per-case scores
   (correctly self-labelled, so HISTORICAL). **24 further closure-named PNGs were
   not opened.** A stale number rendered into a plot is invisible to every frame
   in this rung except a human eye or OCR.
2. **Non-extractable binaries.** 339 `.so` (incl. the QCR library), 473 `.stl`
   (ASCII STLs *were* reached and are in Frame A; binary ones were not), 2 `.vtu`
   (base64-encoded VTK payloads inside XML — Frame A reads the file but the
   payload is opaque), 2 third-party `.whl` (numpy, h5py — structurally incapable
   of carrying a lab claim). PDFs are **not** in this list: all 68 were extracted.
3. **Everything outside `/home/ubuntu/Certonomous`.** This is the sharpest limit.
   Present on the box and **not searched**: `/home/ubuntu/certonomous-runs/`
   (448 entries, including `w3-qcr-rank1/`, the round-5 run tree the record
   cites), `/home/ubuntu/closure-challenge-benchmark/`,
   `/home/ubuntu/closure-challenge-pkg/`, `/home/ubuntu/backups/`,
   `certonomous-cache.tar.gz`, `certonomous-git-backup-*.tar.gz`,
   `/home/ubuntu/memory-import/`, and the agent memory under
   `~/.claude/projects/`. The rung scoped itself to the repo; a claim that
   travels could still live in any of these.
4. **Anything already sent or deployed.** A served copy of the site, an emailed
   attachment, a rendered video, a file on Katie's laptop. Nothing is sent from
   this box and the entry is parked, so the population should be empty — but this
   frame cannot demonstrate that, only assert the park.
5. **Git objects for content never in the working tree.** Frame E covers commit
   messages and pickaxe history, not every blob in 2.0 GB of `.git`. A literal
   that existed only in an abandoned branch is out of frame — and out of scope,
   since it is not a surface anyone reads.
6. **Semantic variants of the prior-art sentence that share no searched fragment.**
   A paraphrase avoiding `Templeton`, `published repeatedly`, `Steiner, Dwight`
   *and* `controls where a data-driven correction` would pass. `Templeton` alone
   is a strong net — it caught every prior-art discussion in the repo, including
   `docs/papers/*` third-party PDFs-as-text — but a sentence that mis-credits
   *without naming anyone* is unreachable by literal search.
7. **A stale claim expressed without a number.** *"we lead the board"*,
   *"best on five of eight"*, *"our entry of record"* with no figure. Item 15's
   `five of eight` was caught only because it sat beside a score literal. **This
   is the largest semantic hole in the method** and the natural brief for a
   follow-on rung.

---

## 7. Verdict

**V14: PASS as executed.** The method was a search, not a list, and it found what
a list had missed — including one surface (`dist/certonomous-demo/`) that is
gitignored and therefore structurally invisible to this lab's default `grep`.

**11 stale surfaces across 25 hit lines**, ranked by exposure in §4. The two
highest-exposure are the tracked shipping bundle and its gitignored mirror; both
are rebuilt by `scripts/build_laptop_bundle.py` from sources that are **already
correct**, so the fix is a rebuild rather than an edit. The third is Katie's
shoot script.

**Reported, not fixed.** Nothing on any checked surface was written by this rung;
the only file it wrote is this one.

**Re-derivation note for a later reader.** The counts in §2 are frame-scoped and
time-scoped to 2026-08-10. Re-running the sweeps is cheap; do that rather than
trusting these numbers if the corpus has moved. The classification in §3 is the
part that took judgement, and §3.2 is the part a careless re-run would break: a
changelog saying *"round 4 scored 0.0654"* is **correct** and must survive.
