# Closure modelling — start here

The lane's map. **This is a map, not a report**: every number below is a pointer to the
record that owns it. Dated 2026-08-20.

**The standing rules are `docs/charters/CLOSURE_MODELLING_CHARTER.md`.** Read it before
writing code or a preregistration. Its line:

> **A closure is not a result until it has been re-solved, and a score against a baseline a
> constant can beat is not an evaluation.**

---

## 1. What exists, and where

| Document | What it is | Size |
|---|---|---|
| `docs/charters/CLOSURE_MODELLING_CHARTER.md` | **The standing rules.** 19 clauses, each with the incident or paper that earned it. | — |
| `docs/papers/closure/MANIFEST.md` | **The corpus of record.** 33 canonical title-verified works with script-generated hashes, 6 byte-identical duplicates, 30 quarantined wrong retrievals, 16 PENDING-MIT. | 33 PDFs |
| `docs/closure/PAPER_CATALOGUE.md` | One block per work: method, data, cases, headline numbers with page citations, author-stated limitations, and what each cannot see. | 33 blocks |
| `docs/closure/FOUNDATIONAL_MODELS_INVENTORY.md` | The classical closures — equations, constant provenance, failure modes. Boussinesq, SA/QCR, k-eps, k-omega, SST, Pope/EASM, RSM, Smagorinsky, dynamic, WALE, Vreman, sigma, wall models. | 18 sections |
| `docs/closure/CLOSURE_METHOD_CLASSES_INVENTORY.md` | Organised by **method class**, not by paper: inputs and invariance handling, solver coupling, training, a-priori vs a-posteriori validation, failure mechanisms, and a comparison table. | 8 classes |
| `cases/RANS_LES_closure_models/_common/BASELINES.md` | The benchmark inventory and every baseline number. **§6.4 is the train-mean tensor**, the baseline the charter requires. | — |
| `cases/RANS_LES_closure_models/_common/FEASIBILITY.md` | Per-paper: can it be reproduced here, with what data, at what core-hour cost, and the verdict. **§2 bands everything against the 487-core-hour authorisation.** | 29 papers |

**Data lives outside the repo.** Benchmark clone: `/home/ubuntu/closure-challenge-benchmark`
(commit `deb91557184af3cb95f5190494ec52d8f2c6a0d1`). Run outputs: `/home/ubuntu/closure-data/`.
**PDFs are never committed; their `.txt` sidecars are.**

---

## 2. Reading order for a new team member

1. **This file**, then `docs/charters/CLOSURE_MODELLING_CHARTER.md` in full. Nothing else is
   worth reading until you know what a result has to be here.
2. **`_common/BASELINES.md` §6.4.** Twenty lines. It is the single fact that reframes the
   whole lane: a constant tensor beats the shipped RANS closure on 8 of 8 held-out cases.
3. **`_common/FEASIBILITY.md` §2 and §3.** What is affordable, and what the matrix cannot see.
4. **`docs/closure/CLOSURE_METHOD_CLASSES_INVENTORY.md` §0.** The three axes — where invariance
   comes from, how the closure enters the momentum equation, what the training loss can see —
   before any individual paper.
5. **One case directory, end to end.** `Wu2018_PIML_RF/` is the cleanest: preregistration,
   results, verdict, and an explicit "what it cannot see".
6. **`PAPER_CATALOGUE.md` by category**, as needed. Do not read it cold; it is 2,000+ lines.
7. **`FOUNDATIONAL_MODELS_INVENTORY.md`** when you need an equation or a constant's provenance.

---

## 3. Scoreboard — the four reproductions

| Case | Verdict | Headline, with its record |
|---|---|---|
| **`Wu2018_PIML_RF`** | **PASS**, a-priori, with one case failing and one claim untested | RF discrepancy model beats SST on **7 of 8** strict TEST cases (band required ≥6) and **18 of 18** held-out hills. Pooled TEST `b_rms`: **RF 0.2213-0.2225** vs **SST 0.4138** vs **train-mean 0.3183**. Loses on `NASA_2DWMH` (0.3540 vs 0.3318). **Nothing was re-solved — a stated scope decision.** 5 seeds, ~0.3 core-hours. |
| **`Ling2016_TBNN`** | **PENDING** — and the preregistration itself was defective | Criteria (i) and (ii) met at **7 of 8**; criterion (iii), the plain-MLP control, still training. **The prereg required realisability to be reported and never gated on it**, so a model putting **6.47-15.34%** of test cells outside the barycentric triangle (truth 0.79%, SST 0.10%) with `‖b‖_F ≈ 1.48e+07` on the hump was on track for a PASS. Charter §4 exists because of this file. |
| **`Kaandorp2020_TBRF`** | **GATE FAIL on all three preregistered claims** — a documented failure with the cause measured | Faithful FS1/FS2/FS3 VARIANT, trained on 19 group-clean hills + PHLL10595 only, tested on the strictly held-out duct `AR_1_Ret_360`. (i) 16-feature **6.382 ± 2.110** vs 5-feature **3.666 ± 2.299** — the extra features made it *worse*, so F18's central claim **GATE FAIL** (paper: 0.0995 → 0.0521). (ii) vs SST **0.5843** — 10.9× worse, also loses to train-mean 0.4718 and to `b ≡ 0` — **GATE FAIL**. (iii) realisability **0.0752 ± 0.0129** of cells outside the barycentric triangle against a truth of 0.0159 — **GATE FAIL**, so F19 does not transfer. Table 4 (BFS5100) **BLOCKED** — no such case on disk. Cause measured: Pope basis rank **3.09-3.99**, coefficient magnitude p99 3.4e4, and departure D2 (Durbin time-scale bound) active in **71.8%** of duct cells; removing D2 post-hoc gives **0.3160 ± 0.0080**, which would have passed (i) and (ii) but still fails (iii) at 0.1339. 5 seeds, 17.79 core-hours. `RESULTS.md` §1-11; incident record in `INCIDENT_tbrf_overwrite_2026-08-20.md`. |
| **`Schmelzer2020_SpaRTA`** | **PASS** at the ceiling gate and **PASS** on the discovered-model gate | **Reported from an existing lab reproduction, not a new run.** The work was done 2026-08-01 under `verification/campaign/W2_SPARTA_*`, three weeks before this preregistration was written. CBFS `eps(U)/eps(U_0)` **0.39753** against published **0.22703**, inside the factor-two gate. |

**Cross-tree pointers, and the charter requires them (§13).** The SpaRTA line lives in
`verification/campaign/`: `W2_SPARTA_PREREGISTRATION.md`, `W2_SPARTA_FROZEN_CBFS.md`/`.json`,
`W2_SPARTA_REGRESSION_PREREGISTRATION.md`, `W2_SPARTA_REGRESSION.md`/`.json`,
`W2_SPARTA_CBFS_DATA_FORENSICS.md`, and `W5_SPARTA_GATE_STATUS.md` — the last records that the
same completed work was demanded by three separate tasks over nineteen days.

**Two integrity flags on the records above**, both scheduled for correction, neither quoted
from: `Ling2016_TBNN/RESULTS.md` §0 still carries a stale `GATE FAIL` line contradicting its
`PENDING` headline, and disagrees with itself on seed counts. `BASELINES.md` §6.4 states
341,717 training cells where both `RESULTS.md` files state 342,014.

---

## 4. The standing rules, in one screen

Full text and provenance: `docs/charters/CLOSURE_MODELLING_CHARTER.md`.

| § | Rule |
|---|---|
| 2 | A-posteriori validation before any claim. An a-priori score is labelled a-priori and alone is **NOT A RESULT**. |
| 3 | Score against the **train-mean tensor**, not SST. Both columns, same cell mask. Name the baseline in the prereg. |
| 4 | **Realisability is a GATE.** The prereg states the violating-fraction and norm thresholds at which the verdict is NOT A RESULT. |
| 5 | Extrapolation detected three ways: feature-distance statistic, tensor-basis rank, and the laminar / DNS-resolution asymptotic tests. |
| 6 | Invariance verified over the **whole composition** — features, normalisers, basis, output — by a boost+rotation unit test on a frozen field. |
| 7 | Every post-hoc velocity correction reports **RMS div(U)**. Our own published floor is 10.5%. |
| 8 | **≥3 seeds**, mean ± spread; a claimed margin must exceed the spread. |
| 9 | **REPRODUCTION** vs **VARIANT**, labelled, with every departure listed. A variant can never PASS the paper's number. |
| 10 | Disjointness asserted in code. Every score labelled **IN-FAMILY** or **OUT-OF-FAMILY**; never pooled. |
| 11 | Prereg frozen before results. Score the ladder **as written**, even when it is wrong; fix it in the next one. |
| 12 | Verdicts are exactly: `PASS`, `GATE REACHED`, `GATE FAIL`, `NOT A RESULT`, `BLOCKED`, `PENDING`. Only against a **registered** falsifier. |
| 13 | **Prior-art search before any reproduction.** A gate names the artefact that closes it. |
| 14 | Check a shared path is unoccupied before writing. A recovered file carries its recovery chain. |
| 15 | Cite only from a **title-verified** PDF. Duplicates by sha256. Never state a number from memory. |
| 16 | **"What it cannot see"** is a mandatory section of every `RESULTS.md` and catalogue block. |
| 17 | Lesson drafts to scratchpad; the supervisor appends to `LESSONS.md`. Numerics facts to `NUMERICS_KNOWLEDGE.md`. |
| 18 | **Under 487 core-hours pre-authorised**; above it, stop and cost it. Runs bounded and checkpointed — kill is unavailable. |
| 19 | **Submissions parked.** Nothing leaves the machine; sending is Sanaa's alone. |

---

## 5. PENDING-MIT — 16 titles needing institutional access

Full table with DOIs, why each is wanted, and what it blocks: **`docs/papers/closure/MANIFEST.md` §4.**
Every one is `BLOCKED-ON-SOURCE`, and **no number from any of them appears anywhere in the lab's
documents.**

Gatski & Speziale 1993 · Parish & Duraisamy 2016 · Singh & Duraisamy 2016 · Holland et al. 2019 ·
Weatheritt & Sandberg 2016 · Ling & Templeton 2015 · Emory et al. 2013 · Iaccarino et al. 2017 ·
Vreman 2004 · Park & Choi 2021 · Bose & Park 2018 · Yang et al. 2019 · Zanna & Bolton 2020 ·
Edeling et al. 2014 · Germano et al. 1991 · Bardina et al. 1980

**The three that cost the most:**

1. **Holland et al. 2019** — the integrated FIML formulation, the only method the reviews say
   "ensures full consistency between the learning and prediction environments". Category C is
   catalogued from its application, not its foundation.
2. **Emory 2013 + Iaccarino 2017** — eigenspace perturbation. `FEASIBILITY.md` §1.2 prices the
   falsifiable question at **< 1 core-hour on frozen fields, no solve, no ML**. The cheapest
   high-value item in the programme, blocked purely on retrieval.
3. **Ling & Templeton 2015** — the origin of the feature set that **four** on-disk papers use at
   second hand.

**On arrival**: title-verify, add to `MANIFEST.md` §1 with a script-generated hash, remove from
§4, and revisit every document carrying its stub. Two papers took exactly that path on
2026-08-20 and **both changed conclusions in documents already written** (L-163).
