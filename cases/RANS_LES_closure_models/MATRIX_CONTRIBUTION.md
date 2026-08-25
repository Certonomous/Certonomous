# MATRIX_CONTRIBUTION — the closure family's rows for the lab coverage matrix

**What this file is.** The closure line's offered rows for the lab coverage matrix the
**verification** team is building at `docs/COVERAGE_MATRIX.md`. That file is **not
closure's**, does not exist at the time of writing, and **is not created, written to or
touched by this contribution**. This is a contribution handed to its owner; the owner
re-maps, renames, merges or rejects any row here without asking.

Written 2026-08-24 by a closure lane at the closure supervisor's direction. **Zero
compute.** Every figure below is quoted from a landed record or from a named artefact on
disk; nothing was re-run and nothing was re-derived. Verdict words are the fixed rule-1
vocabulary (`PASS` / `GATE REACHED` / `GATE FAIL` / `NOT A RESULT` / `BLOCKED` /
`PENDING`), and `PENDING` is used only in its charter meaning — a display/queue state for
"not yet run", never a softened `GATE FAIL`.

**Submissions are parked.** Nothing here is filed, sent or registered anywhere.

---

## 0. Closure's reading of V / G / P — OUR expansion, offered for the owner to re-map

**This is a proposal, not a standard.** The matrix owner has not published a V/G/P
definition. Rather than guess silently and hand over columns whose meaning is private to
us, closure states the expansion it used, so that a re-mapping is a mechanical relabel
rather than a re-audit. **If the owner's definitions differ, the evidence clauses in each
cell are the durable part and the YES/NO/PARTIAL letters should be recomputed from them.**

| letter | closure's expansion |
|---|---|
| **V** | A **verification instrument exists and was demonstrated able to fail** — a planted-zero control read back from disk, an identity test, or an independent re-derivation. Mere presence of a check is not V; the check must have been shown to catch something. |
| **G** | A **pre-registered NUMERIC gate exists that could have failed**, frozen by sha **before** the run. A quantity that is reported but carries no registered threshold is not G. |
| **P** | A **pre-registered PREDICTION was made before the run** and is graded. |

Two honest caveats on our own expansion:

1. **The lab does not grade in HIT/MISS.** The brief for this file asked for P graded as
   HIT or MISS. This lab's records grade in the rule-1 verdict vocabulary, and no closure
   record contains the words HIT or MISS as grades. Where a row says P = YES it means the
   registered claim was graded in the rule-1 vocabulary; the HIT/MISS mapping is the
   owner's to define, and closure has not applied it.
2. **V, G and P are not a ladder.** A row can be strong on V and empty on G (the FS2
   audit), or fire a numeric gate while its verification instrument is out of resolution
   (the a-posteriori G0a). The letters are three independent questions.

**Tier vocabulary** is Sanaa's five words, used exactly: `HOLDS` / `GATE REACHED` /
`SURVEYED` / `NOT HELD` / `NEVER RUN`. The tier grades the **class**, not any one run.

---

## 1. The six rows

### Row 1 — a-priori model fit

| field | value |
|---|---|
| **Tier** | **GATE REACHED** |
| **V** | **YES** — the a-priori `b_rms` scorer carries a planted-zero control that was read back from disk. `Ling2016_TBNN/gpu/RESULTS.md` §8 G0: plant `1.234e-03` recovered at **1.6e-14** relative, identical on the GPU node and on the lab box; the barycentric flag fired on a planted `diag(1,1,-2)` (min barycentric **−5.0**). Demonstrated able to fail on the selection side too: R4's planted-zero control returned **PASS** on both propagated term sets and **GATE FAIL** on the `R`/T1–T4 set, where a selected term scored **−322.2** on held-out permutation importance — worse than a planted zero (`R4_sparta_build/RESULTS.md` §4; `artefacts/fs3.json`). |
| **G** | **YES** — numeric bars frozen by sha before the fits. `R4_sparta_build/PREREGISTRATION.md` (sha256 `058444309f87a9e1f6faccca2086bf16364df7a06bb7702d155c35b1fcacbbe8`, never edited) registered **≥ 3 of 4 training families** below the train-mean `b_rms`; measured **2 of 4** → **GATE FAIL** (`RESULTS.md` §6). `Ling2016_TBNN` registered **≥ 6 of 8** against SST, against `b = 0` and against the train-mean constant. `Ling2016_TBNN/gpu/PREREGISTRATION.md` (frozen alone at `e8309b6c`, sha256 `61b2097f63a38f320aeb98275f4a7aaba8454880fe2389398ee59678d4d81d97`) registered the same band with a **≤ 3, or failure to beat `b = 0` anywhere → NOT A RESULT** branch, which fired. |
| **P** | **YES** — predictions registered before the runs and graded as written. `Ling2016_TBNN`'s registered falsifier (*"if the plain MLP equals or beats the TBNN on the held-out ducts, the paper's central claim is not reproduced"*) **did not fire** — the TBNN wins all three ducts by 0.020–0.056, every margin beyond its seed spread (`Ling2016_TBNN/RESULTS.md` verdict block). R4's registered a-priori claim graded **GATE FAIL** at 2 of 4. Graded in the rule-1 vocabulary, not HIT/MISS (see §0 caveat 1). |
| **Records** | `cases/RANS_LES_closure_models/Wu2018_PIML_RF/RESULTS.md` — **PASS** (a-priori, labelled); `cases/RANS_LES_closure_models/Ling2016_TBNN/RESULTS.md` — **GATE REACHED**; `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/RESULTS.md` — **GATE FAIL**; `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §6 G1 — **GATE FAIL**; baseline definition at `cases/RANS_LES_closure_models/_common/BASELINES.md` §6.4. |
| **Artefacts (out-of-repo where the numbers live)** | `/home/ubuntu/closure-data/tbnn/ckpt/pred_TBNN_s{0..4}.npy`; `/home/ubuntu/closure-data/kaandorp_tbrf/results.json`; `cases/RANS_LES_closure_models/R4_sparta_build/artefacts/apriori.json`, `artefacts/apriori_realisability.json`, `artefacts/fs3.json`. |
| **Last-changed sha (`git log -1 --format=%H -- <path>`)** | `Wu2018_PIML_RF/RESULTS.md` → **fd3aa735bd32391ab316efe6067fdccba1795c5d**; `Ling2016_TBNN/RESULTS.md` → **fd3aa735bd32391ab316efe6067fdccba1795c5d**; `Kaandorp2020_TBRF/RESULTS.md` → **20666e9702f4a27b3c294b1e8007ee1e0b9e1c5a**; `R4_sparta_build/RESULTS.md` → **918e8fe7e2cb9834badea50e0481382f9d50619d**; `_common/BASELINES.md` → **e4dee8595ae118ce64b1a799aa77d9c3bd43d566**. |

**Why GATE REACHED and not higher.** Registered a-priori thresholds were met on two
records — `Wu2018_PIML_RF` at **7 of 8** against a band of ≥ 6, `Ling2016_TBNN` at 7 of 8
on criteria (i) and (ii) — and the full ladder is not answered on either, because neither
propagated. Charter §2 is the binding reason the tier cannot be `HOLDS`: **an a-priori
score alone is NOT A RESULT for any claim that a closure improves a flow.**

**The honest state of this row, stated as a defensible position, not softened.**

* **The bar these fits clear is low by measurement, not by opinion.** The train-mean
  constant tensor — fitted to nothing beyond an arithmetic mean — beats k-omega SST on
  **8 of 8** strict TEST cases: pooled over 152,520 cells, train-mean **0.3183**, SST
  **0.4138**, `b = 0` **0.4234** (`_common/BASELINES.md` §6.4; charter §3). The Wu 2018
  forest beats that constant on **7 of 8**, the same 7 (`Wu2018_PIML_RF/RESULTS.md` §3.1).
* **No learned model in this family has beaten the harness's own frozen-field ceiling.**
  Across every landed closure record read for this contribution, the ceiling has never
  been beaten by a learned model: R4's discovered model **diverged on all twelve**
  training propagations while the ceiling converged; Kaandorp's a-posteriori ML rows are
  `NOT A RESULT` and, had H0 held, would have graded **within 2×** the ceiling and no
  better (H3 shape, mean 0.15426 against 2 × 0.084131 = 0.16826); the GPU arm's
  a-posteriori gate G4 never ran. **This is a survey of the landed records, not an
  executed sweep** — see §2.
* **None has passed realisability at scale.** TBNN **6.5–15.3 %** of TEST cells outside
  the barycentric triangle against a truth rate of **0.79 %** and SST **0.10 %**
  (`Ling2016_TBNN/RESULTS.md`); TBRF **10.2 / 11.4 / 10.6 %** over three seeds and
  **9.66 %** on the 17-feature arm (same record); the GPU arm's ARM-A TBNN **3.10–5.34 %**
  with `max ‖b‖_F` **7.8e9–2.1e10**, ARM-B **4.30–14.44 %** with **5.6e6–9.4e8**, against
  a registered bar of **2.374 %** and `1.633` — every seed of both models fails both
  clauses (`Ling2016_TBNN/gpu/RESULTS.md` §8 G3); R4's discovered model unrealisable on
  **4.4–6.8 %** of every duct cell and **19.1 %** of `CBFS13700`, `max ‖b^Δ‖_F` **7.559**
  against the realisable bound near **0.8165** (`R4_sparta_build/RESULTS.md` §11.3(b)).
  The linear EVM violates on **no cell of any case**.
* **A registered gate that cannot fail is recorded as such, not repaired after the fact.**
  R4's §6 registers **no threshold on realisability** — G4 is "reported, no gate" — the
  same omission Charter §4 was written to stop after `Ling2016_TBNN`
  (`R4_sparta_build/RESULTS.md` §6, §7).
* **R4's GATE FAIL rests on both registered halves independently**, and the record says so
  in one sentence: G1 a-priori at **2 of 4** families against a registered **3**, and G2
  a-posteriori **diverged on all twelve** at iterations **5 to 18**, every one with a
  floating-point exception inside `kOmegaSSTSparta::updateCorrections`
  (`R4_sparta_build/RESULTS.md` §11.3(a): *"Both registered halves of the GATE FAIL fired
  independently."*).
* **The `xi = 0.1` and R-only arms are DIAGNOSTICS, NOT MODELS.** *"Neither was
  preregistered, neither is graded, and a converged number from either is not a claim that
  the model works at that scaling"* (`R4_sparta_build/RESULTS.md` §7). **No number from
  either arm may be reported in the matrix as a model result.**
* **A registered deliverable of this row was never delivered and the non-delivery went
  undisclosed through thirteen departures.** `R4_sparta_build/RESULTS.md` §12.1, departure
  D-14, docket **D475**. See Row 5.

---

### Row 2 — a-posteriori propagation

| field | value |
|---|---|
| **Tier** | **NOT HELD** |
| **V** | **YES**, with its resolution defect named in the same breath. `G0a` solver identity: `kOmegaSSTCorrected(0,0)` against stock `kOmegaSST` at the same 200 iterations returns **0.0 exactly** on a byte-identical `600/U`; the planted perturbation `1.234e-03` was read back off disk at **4.002936e-07**, so the reader is demonstrated able to see a non-zero. **The defect:** at `writePrecision 6` the reader's one-ulp floor **is** 4.002936e-07, so the registered `1e-10` sits **4,003× below the instrument's resolution** — the third clause in that one pre-registration its instrument cannot serve (L-269). Recorded, not repaired: the verdict cell now reads `0.0 (floor 4.0e-07; registered 1e-10 unresolvable at writePrecision 6)` and **PASS stands as frozen with the limitation disclosed against the lane's own favour**. |
| **G** | **PARTIAL** — the propagation gates are numeric, frozen before any solve, and **did** fail: H0 required `TRUTH` to cut `U_rms` by ≥ 30 % and it rose; H5 continuity `< 1e-3` on the registered `U_bulk/L` normalisation returned **GATE FAIL ×6** at 0.262–13.67, the `NULL` control itself at **262×** the threshold. **PARTIAL** because G0a's identity threshold could not have failed as written (above), and because two §4/§5 metrics — realisability and `x_reatt` — carry **no registered band** and therefore carry no verdict. |
| **P** | **YES** — `PREREGISTRATION.md` §5 froze the cascade before any solve: *"If H0 fails, H1–H3 are reported as NOT A RESULT, not as failures of the model — a broken propagation path cannot grade a closure."* That clause is why the ML numbers are printed and not graded. |
| **Records** | `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/RESULTS.md` — **NOT A RESULT** for the whole lane, all three registered cases; pre-registration `cases/RANS_LES_closure_models/Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md` (one commit ever; blob == HEAD == disk). Siblings, same finding independently: `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori/RESULTS.md` — **NOT A RESULT**; `cases/RANS_LES_closure_models/Wu2018_PIML_RF/aposteriori_frozenk/RESULTS.md` — **NOT A RESULT** (`k` frozen, the `k`-collapse explanation was incomplete). |
| **Artefacts** | `/home/ubuntu/closure-data/aposteriori/kaandorp/results.json` (every number below was read from it, not from the driver log); `/home/ubuntu/closure-data/aposteriori/kaandorp/lane5.log`; `/home/ubuntu/closure-data/kaandorp_tbrf/features_nodurbin.npz`; `/home/ubuntu/closure-data/aposteriori_frozenk/wu2018/scores.json`. |
| **Last-changed sha** | `Kaandorp2020_TBRF/aposteriori/RESULTS.md` → **8322b7b2eb9e069d095319400f03dd4b65d31cc8**; `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md` → **0ebc9d5351545b6fdc3864d24e3e5a2664af048a**. |

**Why NOT HELD.** Not "did not converge", not "inconclusive": **truth injection made the
velocity field worse on every registered case, so the propagation path cannot carry a
closure at all** — and that is a finding about the b-only injection form, not a failure of
any model.

* **The ceiling inverts on all three cases.** `TRUTH` `U_rms` against the SST gate:
  `CBFS13700` **0.084131** against **0.0516** = **+63.05 %** (the 30 % bar was ≤ 0.03612,
  the 50 % bar ≤ 0.02580 — both fail the same way); `AR_1_Ret_360` **0.321515** = **+61.97
  %**; `AR_3_Ret_360` **0.289795** = **+56.99 %** (`aposteriori/RESULTS.md` H0 table).
* **It is not a duct artefact.** `CBFS13700` is a separated flow on a curved wall — the
  paper's own case C1, a different mesh, a different flow class, a different metric family
  — **and it inverts the ceiling by the largest margin of the three**.
* **Every b-only injection moves reattachment the wrong way.** `x_reatt`: shipped SST
  **5.891**, `NULL` **5.8950**, `TRUTH` **6.9117**, `MEANB` **7.9480**, `ML0/1/2`
  **8.7807 / 11.1672 / 14.4603** — against the LES **4.241**. *"Every configuration moves
  `x_reatt` away from the LES 4.241, in the same direction the b-only injection moves
  `U_rms`."* `x_reatt` carries **no registered band** and therefore **no verdict**.
* **Had H0 held, the constant would still have won.** `CBFS13700` ML seeds 0.15883 /
  0.15107 / 0.15289, mean **0.15426**, mean + 2sd **0.16238**, above `MEANB` **0.13965** —
  *"the constant tensor with no inputs propagates better than the forest."* **Not graded**:
  the H0 cascade voids H1–H3. Printed here only because the shape is what the cascade would
  otherwise hide.
* **Two cells that are not measurements.** `AR_3_Ret_360__MEANB` carries `nan` for
  `unrealisable_frac` / `b_rms_total` after `k` collapsed to an empty mask — **not
  measured, not zero**. `AR_3_Ret_360__ML0/1/2` are **BLOCKED** (no block in
  `features_nodurbin.npz`); no metric was written. Kaandorp **Table 4 (BFS5100)** is
  **BLOCKED-ON-DATA** — no such case on disk.
* **Two freeze limbs disclosed rather than assumed.** The six `CBFS13700` rows are
  frozen-by-commit; the ten pre-relaunch duct rows carry logs whose mtimes (17:27–17:44Z,
  2026-08-21) precede the 18:52:18Z freeze commit, so those rows **stand with the §2d label
  "freeze self-attested, no commit witness"** after a negative search for any out-of-git
  posting record.
* **Cost, calibration row C-18:** 388.8 core-min registered against **219.571 core-min
  measured** = 3.6595 core-h, ratio **0.565×**, **zero waste**; $0.1877 **derived, not
  measured** at the recorded rate.

---

### Row 3 — frozen-field ceiling

| field | value |
|---|---|
| **Tier** | **HOLDS** — the one thing in this family that does. |
| **V** | **YES**, on three independent legs. (1) **Byte-identical reproduction of an independent record**: the extraction operator returns `PHLL10595` and `CBFS13700` byte-identical to the W2 record — inputs and outputs — at its own settle iterations **1492** and **354** (`R4_sparta_build/RESULTS.md` §2.1). (2) **Independent re-derivation**: `ic1_check.py` evaluates the same frozen term sets from the same `0/` fields in Python, independently of the solver; worst relative L2 over all 12 cases is **3.969e-12** on `kDeficit` and **5.078e-13** on `bijDelta` — the ascii round-trip floor — which is what rules out component-ordering, exponent-mapping, `2k`-factor and `I2`-sign slips between the two implementations (§4.7, `artefacts/ic1_discovered.json`). (3) **Planted controls demonstrated able to fail**: R5C's three comparators all saw `PLANT = 1.234e-03` to **2.4e-10** relative and are registered to **refuse (exit 2)** otherwise; R5C's G2 re-matched **14 of 14** field sha256 at settle 1492/354. |
| **G** | **YES** — a numeric gate that could have fired and did not. `R4_sparta_build/PREREGISTRATION.md` (sha256 `058444…cbbe8`) registered a **NOT A RESULT branch** firing *if the per-case frozen-field ceiling fails to beat NULL by 30 %*. And a sibling numeric gate on the same rows **did** fire: G3 continuity `≤ 1e-4` put `AR_1_Ret_180` CEILING at **1.0628e-04** → **NOT CONVERGED**, recorded against the ceiling's own favour with the note that the threshold is dimensional. |
| **P** | **YES** — the branch was registered before the run and graded as written: **does NOT fire**. |
| **Records** | `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §5, §6, §11.2, §12.2; `cases/RANS_LES_closure_models/R5C_omega_repair/RESULTS.md` (the ceiling's own instrument repair, **GATE FAIL**); `docs/closure/R5_DECISION_MEMO.md`, `docs/closure/R5_CONSTRAINTS_DISCHARGE_RECORD.md`. |
| **Artefacts** | `cases/RANS_LES_closure_models/R4_sparta_build/artefacts/aposteriori.json`, `artefacts/ic1_discovered.json`, `artefacts/frozen_inventory.json`, `artefacts/frozen_build_manifest.json`; `/home/ubuntu/closure-data/r4/dataset/`. |
| **Last-changed sha** | `R4_sparta_build/RESULTS.md` → **918e8fe7e2cb9834badea50e0481382f9d50619d**; `R5C_omega_repair/RESULTS.md` → **0ac76ec2c5fe455cd359019942a44079cef1dae1**. |

**What the ceiling measured.**

* **It beats doing nothing by a wide margin.** `eps(U)_CEILING / eps(U)_NULL` =
  **0.003523** on `PHLL10595` (**99.6 %** better than NULL), **0.398057** on `CBFS13700`
  (**60.2 %**), and **0.000140** on `AR_5_Ret_180` (**99.99 %**). It clears the registered
  30 % bar on **all eleven** cases where it converged (`RESULTS.md` §11.2;
  `artefacts/aposteriori.json`).
* **It reproduces an independent record to four significant figures.** `CBFS13700`'s
  ceiling is **0.3975** against the W2 campaign's independently obtained **0.39753** — from
  a rebuilt case, a rebuilt harness and a different session.
* **It makes structure a linear model cannot make.** Duct secondary flow: **the corrected
  range is 0.09–0.61 % of the DNS value, not 0.4–0.6 %.** `RESULTS.md` **§12.2** is a dated
  addendum headed *"Correction of record — the duct vortex recovery is 0.09–0.61 %, not
  0.4–0.6 %"*; it corrects lines 678–679 and 1128 of the v1.0 body, which are superseded.
  Per aspect ratio: `AR_1_Ret_180` **0.6126 %**, `AR_3_Ret_180` **0.3878 %**,
  `AR_5_Ret_180` **0.3283 %**, `AR_10_Ret_180` **0.0899 %**. The stated interval is wrong
  for **three of the four** aspect ratios and **the error ran in the ceiling's favour**; no
  verdict moves, because gate **G5 carries no registered bar**. The linear EVM gives
  **exactly zero** secondary flow on every one of them.

**And what a ceiling is, stated in the same row so no reader can lift the number out of
it.** A frozen-field ceiling reads `bijDelta` and `kDeficit` **extracted from the truth**
and injects them as static fields. **It predicts nothing. It is not a model. It is an upper
bound available only when the answer is already known**, and no sentence anywhere may
present it as a closure model (`R4_sparta_build/RESULTS.md` §11.2, the record's own
wording). The sentence that carries this row and the one above it is R4's:
**the harness carries the truth; the model does not.**

**The ceiling's own instrument was repaired and the repair GATE FAILed — both halves are
stated, and neither excuses the other.**

* **The gate.** R5C **GATE FAIL** on its identity gate: `kDeficit` rel L2 **1.1848e-04** on
  `alpha_10_12000_4048` against a registered **1e-6**, and 3 of the 12 not CONVERGED under
  G3 (`R5C_omega_repair/RESULTS.md` §3.1 ladder; pre-registration sha256
  `a1cfae5a…1277a`, committed alone at `f364cf2d`). Eleven of the twelve R4 targets
  reproduce at the **identical settle iteration** to 1e-7–1e-11.
* **The engineering.** The Patankar split **removes the clipping**: `bound(omega)` events
  at **zero on 22 of 27** cases (five at 5, 7, 17, 18, 29) against R4's baseline, and
  **10 of the 15 hills are COMPLETE under the strict six-condition rule against 0 of 15 in
  R4**. That 10 is explicitly *"the number that is not the gate but is the finding"*; the
  registered gate G4 counts **M = 1 of 15** and reached **GATE REACHED**, **overridden by
  G1** under §3.1. The same damping makes the change-based settle criterion stop one target
  **37.4 %** early — **a change criterion cannot tell convergence from damping (L-243)**.
* **The registered consequence was applied, not negotiated:** R4's 12 targets stand, the 15
  hills remain INCOMPLETE, the 27 R5C targets are used for nothing.

---

### Row 4 — feature-library gate FS2 (degeneracy)

| field | value |
|---|---|
| **Tier** | **SURVEYED** |
| **V** | **PARTIAL** — a real identity instrument exists on one axis and none on the other. The **invariance check** (charter §6) re-applies a Galilean boost `c = [0.3057, −0.1735, 0.1074]` and a rigid rotation of 0.7 rad to the raw fields and recomputes every feature and every normaliser at tolerance `1e-12`; it **did** separate signal from artefact — 3 rotation exceedances at max relative change **6.939e-06**, all three triaged (two are algebraically-zero features dividing roundoff by roundoff, one at 3.3e-12 for an O(1) feature) — and it **caught a real failure**: **58 of 110 features are NOT Galilean invariant**, max relative change **2.000e+00**. The report is regenerable and re-running reproduces it. **But the rank / dead-feature branch of `fs2_audit.py` carries no planted control of its own**; the planted control that exists in that file (`planted_control`) was added by the D476 repair and plants into the FS5 companion column, not into the rank census. |
| **G** | **NO** — FS2 as written is a standing **audit**, not a gate with a number. Charter §22.5 requires that *"anything algebraically zero or near-constant is flagged BEFORE training"* — a flag, not a threshold. `FS2_DEGENERACY_REPORT.md` states plainly **"No model was trained"**, and the report registers no numeric bar that could fail. |
| **P** | **NO** — no pre-registered prediction. The report is generated from the data, not predicted in advance of it. |
| **Records** | `cases/RANS_LES_closure_models/_common/features/FS2_DEGENERACY_REPORT.md`; library definition `cases/RANS_LES_closure_models/_common/features/FEATURE_LIBRARY.md` (v1.1, Amendment 1 appended at the foot); generators `build_features.py`, `fs2_audit.py`, `make_fs2_report.py`, `invariance_check.py` in the same directory. |
| **Artefacts** | `/home/ubuntu/closure-data/features/fs2_audit.json`, `/home/ubuntu/closure-data/features/manifest.json`, the 40 per-case `.npz` under `/home/ubuntu/closure-data/features/`; `/home/ubuntu/closure-data/features/invariance_check.json`; per-case tensor-basis rank in `/home/ubuntu/closure-data/kaandorp_tbrf/results.json` under `baselines.<case>.basis_rank_mean`. |
| **Last-changed sha** | `_common/features/FS2_DEGENERACY_REPORT.md` → **fd3aa735bd32391ab316efe6067fdccba1795c5d** (a dated correction; the report was originally generated at `8a380cb9`, which also wrote the `fs2_audit.json` baseline). `_common/features/FEATURE_LIBRARY.md` → **7e973ba8349141ffe9eb8ee21bc6d78db38ec16d**. |

**Why SURVEYED and not a gate tier.** The degeneracy is **measured, per family, and
reproduces** — but nothing in it can fail, so it cannot be `HOLDS`, `GATE REACHED` or
`NOT HELD`. This is a standing gate in the charter's sense (**permanently re-armed rather
than closed**, §22.5) whose armed state has never carried a number.

**What it found, on 110 features over 40 cases, 641,652 cells, zero non-finite values.**

* **No family reaches full rank.** `cbfs` **100/110**, `duct` **96/110**, `hill`
  **100/110**, `hill_breuer` **100/110**, `hump` **100/110**, `POOLED` **100/110**. The
  ducts are worst: **48 algebraically-zero features** and a condition number of
  **1.17e+33**. *"Any method that inverts or regularises this matrix on duct data is
  working in a space 14 dimensions smaller than it thinks."*
* **12 of 110 features are algebraically zero on all pooled data**, every one a high-order
  invariant containing a product of three or more of `S`, `Omega`, `A_p`, `A_k`, listed in
  full with their pooled `max|v|` (5.2e-18 to 5.9e-13). They vanish because every case in
  this benchmark is a statistically two-dimensional mean flow — **the same collapse that
  takes Pope's ten-tensor basis to rank 3**.
* **The tensor-basis rank is measured per case: case means run 3.006 to 3.987, mean of case
  means 3.738** (§4). This is the standing measurement that replaced the pooled **3.24**
  figure whose provenance pointer resolved nowhere (charter §5(b), §20). **Do not quote
  3.24.**
* **The Galilean finding is a property of steady-state implementation, not an error in the
  source paper**: 53 of the 58 contain `A_p`, whose Wu-Xiao-Paterson normaliser
  `rho |DU/Dt|` is boost-invariant only through the unsteady term a steady RANS field does
  not have; the remaining 5 use raw `U`.
* **`singular_value_ratio_first_to_last` is NOT quoted as a number anywhere in this
  contribution**, by standing closure ruling — see Row 5.

---

### Row 5 — feature-library gate FS5 (extrapolation coverage)

| field | value |
|---|---|
| **Tier** | **SURVEYED** |
| **V** | **YES**, and this is the strongest verification instrument in the closure family. Gate **A1** plants a value strictly above every training companion value into a copy of a TEST case's companion column, writes it to a temporary `.npz`, and reads it back through the same path the audit itself uses: case `AR_14_Ret_180`, cell 31818, planted **83.4855** (1.5 × the training max 55.657); flagged cells **0 → 1**; maximum read back 83.4855. **The refusal path was proven live, not merely present**: two reader mutations were run as subprocesses and their exit status checked — unmutated **rc 0**, `clipped_reader` (the D476 defect itself) **rc 2**, `ignores_disk` **rc 2** — both exiting with refusal text naming the planted value, the cell, and the expected-versus-observed counts. *"A control that cannot fail is not a control; this one fails when the reader is blinded in exactly the way the defect blinded it."* |
| **G** | **PARTIAL** — two different things, and they must not be conflated. The **instrument repair** carried four gates frozen before any code was touched (`FS5_D476_CLIP_REPAIR_PREREGISTRATION.md`, commit `bf4956bc`, blob `8fac067cf4a2c19a205df529db6c79bd48e31f3d`, freeze re-verified three ways): **A1 PASS, A2 PASS, A4 PASS, A3 GATE FAIL** — so numeric gates existed and one fired. But **FS5's own standing gate carries no number**: its *"declared factor"* **has never been declared by any build — stated three times, met zero times**, and `COVERAGE.md` §5 explicitly refuses to invent one post-hoc (rule 2). |
| **P** | **PARTIAL** — the repair pre-registration made and graded a prediction (A2's bit-exactness held at 40/40; A3's exact-identity prediction failed and the failure was **diagnosed, not absorbed**). The FS5 **coverage sweep itself** makes no pre-registered prediction: it reports a range comparison against a factor nobody has declared. |
| **Records** | `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md`; `cases/RANS_LES_closure_models/_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md`; `cases/RANS_LES_closure_models/R4_sparta_build/COVERAGE.md` (the per-build discharge, late); `cases/RANS_LES_closure_models/R4_sparta_build/RESULTS.md` §12.1 (departure D-14). |
| **Artefacts** | `/home/ubuntu/closure-data/features/fs2_audit.json` (block `coverage.q1_wallRe_unclipped_companion`); the 40 regenerated `.npz` with keys `['D','F','diag_names','names']` under `/home/ubuntu/closure-data/features/`; pre-repair state preserved at `/home/ubuntu/closure-data/features_backup_pre_D476/`, including `A2_before.json` taken **before any code was edited**; `cases/RANS_LES_closure_models/R4_sparta_build/artefacts/coverage.json`. |
| **Last-changed sha** | `_common/features/FS5_D476_CLIP_REPAIR_RESULTS.md` → **4177489919b155f982a2006cb77e34611f23f0cd**; `_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md` → **7e973ba8349141ffe9eb8ee21bc6d78db38ec16d**; `R4_sparta_build/COVERAGE.md` → **9f0210dd38a951382df2b7779206e21e8b09b33c**. |

**FS5 is a STANDING GATE, permanently re-armed rather than closed** (charter §22.5).

**Three things this row must record, none of them softened.**

1. **FS5's per-build discharge for R4 WAS NOT MET.** Docket **D475**. R4's frozen
   `PREREGISTRATION.md` §7 registered `COVERAGE.md` to ship with `MODEL.md` on 2026-08-22.
   **It was never written.** The strings `FS5` and `coverage` appear **zero times** in the
   1,313-line `RESULTS.md` (control: `FS2` appears six times under the same grep); **none
   of departures D-1…D-13 discloses it**; it is not among §7's ten "cannot see" bullets.
   Found 2026-08-23 by the R5 discharge-record lane and verified personally by the closure
   supervisor the same day. The supervisor's ruling, quoted: *"FS5's per-build discharge
   for R4 WAS NOT MET — the standing gate re-arms. The late delivery discharges the
   deliverable, not the disclosure duty, which stays on record as breached."*
   **Late delivery discharged the deliverable, not the disclosure duty.** What the late
   delivery then showed, on the realised 12-case training set and the frozen fields the
   regression actually fitted: `{T1,T2,T3}` is **rank 3 in 172,106 of 172,106 fitted
   cells**; leave-one-family-out coverage on the six selected columns loses only
   **0.0011 % / 0.0905 % / 0.0000 % / 0.2238 %** of held-out cells (hills / ducts /
   `PHLL10595` / `CBFS13700`) — **so R4's GATE FAIL was not a training-set coverage
   failure**: one candidate explanation removed, none established. Independent reproduction
   of the fit mask returns **172,106 of 172,171, 65 dropped, all hills**. Delivery cost
   **30.6 core-seconds** against a 0.1 core-h cap.
2. **The D476/FS5 instrument-repair adoption block is LIFTED, and its condition is MET.**
   The lift was ruled conditional (docket **D491**, record Addendum 2 v1.1 at
   `41774899`); the condition — verification's supervisor confirming cross-team audit pass
   6 as its own verdict, every load-bearing limb re-derived with its own code — was **MET
   at `f536b114`** (2026-08-24T16:15:20Z), which released the §7 adoption block. **Scope
   is unchanged by the lift:** the unclipped `q1_wallRe_raw` companion is an **audit-side
   diagnostic ONLY** — never in `F`, never a feature, never a correction — **A3 stays GATE
   FAIL**, no thread pinning was adopted, `singular_value_ratio_first_to_last` is **not
   quoted as a number in any closure record** until a registered instrument decision
   adopts verification's recommendation, and **no standing verdict moves.**
3. **What the repaired instrument measured on first reading.** Training companion range
   over 32 training cases (484,034 cells, 0 non-finite): min 3.68e-10, p50 **2.994**, p99
   **32.88**, max **55.657** — *the median unclipped value is already above the clip of
   2.0.* Seven of eight test cases sit inside the training envelope on this axis. **The
   NASA hump does not: `NASA_2DWMH` has 4,954 of 51,626 cells — 9.596 % — above the
   training maximum, the worst excursion at +5.1111 training spans, case max 340.1 =
   6.11× the training max.** The clipped instrument reported that case as in-range by
   construction, since every value on both sides was pinned at 2.0 — **that is the
   blindness D476 recorded, now measured.** And the size of the blindness:
   **`q1_wallRe` sits exactly on the clip in 57.84 % of all 641,652 pooled cells** — the
   clip is not a rare guard, it is the modal value of the column. **No verdict moves from
   any of this**; it is instrument information reported beside the standing verdicts, and
   **R4 does not use `q1_wallRe`.**

**Why A3 failed, recorded because it is the interesting half.** `fs2_audit.json`
new-vs-old differs in exactly six values, all the same statistic, on a matrix every family
of which is rank-deficient — so `s[-1]` is analytically zero and its computed value is
rounding noise at ~1e-15 against `s[0]` ~ 7.5e+02. The cause was located, not guessed: the
inputs are byte-identical (A2), the baseline is code-fair, repeat runs are bit-identical,
and **the statistic moves with the OpenBLAS thread count** — on `hump`, input matrix held
fixed, `s[0]` agrees to 15 significant digits and the rank is 100 at every thread count
while the ratio spans **1.75e+17 to 3.31e+18**; the baseline is the 4-thread value and the
new run the 16-thread value. Re-running pinned to `OPENBLAS_NUM_THREADS=4` gives **exactly
zero differences**. **No thread pinning has been adopted**: *"Pinning would convert this
gate from failed to passed by changing how the instrument is run, which is not registered
and would be engineering a pass."* The delivered `fs2_audit.json` is the unpinned run.
Both instrument-standard questions are referred to verification, unruled here.

---

### Row 6 — GPU training

| field | value |
|---|---|
| **Tier** | **NOT HELD** — nothing is established. Arm 2, which is the arm that would settle the question, is **NEVER RUN**. |
| **V** | **YES** — gate **G0** planted-zero: plant `1.234e-03` recovered as `1.234000000e-03` at **1.6e-14** relative error, **identical on the GPU node and on the lab box**, with a planted `diag(1,1,-2)` flagged at min barycentric **−5.0**. The comparator's own sha256 (`4f9eda16…6aac`), the driver's (`1bac03bd…0ed3`) and the launcher's (`5b9c68eb…6fad`) all equal the frozen F.4 table and the `11f93da6` blobs, and the driver copy on the node hashes the same. **VERIFY:** the record registers a **refusal** branch (*"refusal → NOT A RESULT"*) but this lane found no record that the refusal path was exercised **live** on this arm, as FS5's A1 was; do not credit it as demonstrated until someone checks. |
| **G** | **YES** — numeric thresholds frozen alone before any compute in `Ling2016_TBNN/gpu/PREREGISTRATION.md` (sha256 `61b2097f63a38f320aeb98275f4a7aaba8454880fe2389398ee59678d4d81d97`), re-verified equal to the committed blob **and to the copy the node ran from**. They fired: **G1 NOT A RESULT** on its own "failure to beat `b = 0` anywhere" branch, **G2 GATE FAIL**, **G3 NOT A RESULT** on both TBNN models. |
| **P** | **PARTIAL** — a prediction was registered before the run and graded, **but it was registered on the wrong question**, and the record says so under its own verdict. Arm 1's falsifier fired as written and **does not settle departure D3**: the frozen design's *"full batch by construction"* ran **~3.4e5× fewer updates per epoch** than Ling's per-point SGD — the paper updated after each training point, **342,014 updates per epoch** on this training set, against arm 1's one. **A rate is not an optimiser (L-267).** |
| **Records** | `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/RESULTS.md` — **VERDICT: NOT A RESULT** (arm 1, graded personally by the closure supervisor, 2026-08-24T16:07:25Z); `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/PREREGISTRATION.md` (arm 1, frozen alone); `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md` (arm 2, **FROZEN and UNLAUNCHED**). Docket **D490**; lessons **L-267**, **L-268**; numerics **N-B40–N-B42**; calibration row **C-16**. |
| **Artefacts** | `cases/RANS_LES_closure_models/Ling2016_TBNN/gpu/artefacts/grading_witness.json` (committed — it witnesses the grading JSON's sha256 and the comparator that produced it, because the JSON records no comparator sha; a defect a peer supervisor caught, D-5); `/home/ubuntu/closure-data/tbnn_gpu/grading_gpu_ling.json` (NOT committed, bulk-data rule); `/home/ubuntu/closure-data/tbnn_gpu/out/` (6 `status_*.json`, `spend.json`, 15 `pred_*.npz`, 15 `hist_*.csv`, 10 `ck_*.pt`, `armb_optuna.db`; 89,609,821 B, byte-identical to the node); `/home/ubuntu/closure-data/tbnn_gpu/node_root/`; `/home/ubuntu/closure-data/tbnn_gpu/run_window.json`. All present on disk at the time of writing. |
| **Last-changed sha** | `Ling2016_TBNN/gpu/RESULTS.md` → **0263e66930b7e6a50f345a1582b0ac63b41c845e** (Correction 2; the grading commit was `353925c7`). `Ling2016_TBNN/gpu/PREREGISTRATION.md` → **e8309b6ca19bc209b9f8f4110e7af296e575ce0a** (the sole freeze commit). `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md` → **77f064a867246167fc324a390bc87021464608bb** — see the note below, because this is **not** the freeze sha. |

**Arm 1 — CLOSED, NOT A RESULT.** The lab's first GPU run, on `gpu1` (`g6.xlarge`, NVIDIA
L4), the registered class, under Sanaa's verbatim GPU cost approval.

* **G1 NOT A RESULT:** the ARM-A TBNN at Ling's SGD 2.5e-7 × 200,000 full-batch epochs
  beats SST on **0 of 8**, `b = 0` on **0 of 8** and the train-mean on **0 of 8**.
* **G2 GATE FAIL:** TBNN pooled test `b_rms` **3.90e7** (spread 3.46e7) against the plain
  MLP's **0.3604** (spread 0.091).
* **G3 NOT A RESULT on both TBNN models:** violation **3.10–5.34 %** and **4.30–14.44 %**
  against a registered **2.374 %**, `max ‖b‖_F` to **2.1e10** against a registered
  **1.633**.
* **G4 not run**, as registered, because G3 fired.
* **Under the verdict, not softening it:** ARM-B beats all baselines on **7 of 8** (ducts
  0.11–0.12 against train-mean 0.39–0.42) **and violates realisability on up to 46 % of
  duct cells while scoring its best RMSE there** — the axis RMSE cannot see, which is why
  Charter §4 is a gate.
* **The search re-selected the CPU recipe:** a 9×77 network at batch 8192 and Adam
  1.02e-3, beating the CPU lane's 8×30 on validation by **0.005**, inside the **0.0073**
  seed spread.
* **Cost, calibration row C-16: 10.7054 GPU-h = $8.62 derived** at $0.8048/GPU-h from the
  published price list (`docs/GPU_CAPABILITY_STATE.md` §9, commit `112b61b8`) — **derived,
  not measured**; 0.97× the P0 projection and **below** the registered 12–52 floor, because
  measured throughput was 42–80× against an assumed 5–20×. **Waste 7.88 GPU-h = $6.34
  derived**, the node idling after the overnight fleet kill (L-268). Waste is named
  separately and is not absorbed into the ratio.

**Arm 2 — FROZEN AND UNLAUNCHED. Verdict `PENDING`, in the rule-1 display/queue sense: not
yet run. It is not a softened `GATE FAIL`, and nothing about arm 2 has been graded.**

* Pre-registration **frozen and committed ALONE before any compute at `f36fbdd9`**
  (2026-08-24T16:27:45Z); the code whose sha256s the frozen file fixes — driver, comparator,
  launcher — committed at **`f9be7f40`**; the instance was **STOPPED at freeze**.
* **Correction to the sha this lane was handed.** `git log -1 --format=%H` on
  `arm2/PREREGISTRATION.md` returns **`77f064a8`**, not `f36fbdd9`, because **three
  amendments landed before first compute** — `84bf079d` (Amendment 1), `1563a6b2`
  (Amendment 2, gate-neutral), `77f064a8` (Amendment 3, v1.2 → v1.3, the conjunction count
  `n_all` governing G1 on a supervisor ruling, the stricter reading). Amendments before
  first compute are legal under rule 2; the row therefore carries **both**: last-changed
  **`77f064a8`**, original freeze **`f36fbdd9`**. A matrix cell showing only the freeze sha
  would not resolve to the file that will run.
* Registered cost: **3–32 GPU-h = $2.41–$25.75 derived**, cap **40 GPU-h = $32.19
  derived**; overrun stops the run. **GPU spend is outside the 2026-08-21 CPU blanket.**
* **No GPU node is running. Nothing here proposes launching one** — that is Sanaa's, per
  item, with a console-read `cost_basis`.

---

## 2. What these rows cannot see

Mandatory under `CLOSURE_MODELLING_CHARTER.md` §16 — *"the part of the record that stops a
reader inferring a claim the work does not support."*

* **They cannot see generalisation.** Every R4 number is a **training-family** number and
  no TEST case was opened by that lane — asserted in code at five entry points
  (`r4_lib.assert_no_test_case`), not promised in prose. The a-priori TEST scores in Row 1
  are a different lane's and a different split's; nothing in this contribution licenses
  reading them as one experiment.
* **They cannot see a working closure.** Not one row here reports a learned model that
  improved a flow. Rows 1–3 taken together say: the fits clear a bar a constant tensor also
  clears, the propagation path inverts under the truth itself, and the only thing that
  works is a ceiling that already knows the answer.
* **They cannot see whether the ceiling generalises past the extraction.** The ceiling
  `HOLDS` on the twelve cases that completed. **15 of 27 hills never completed** under the
  strict rule in R4; R5C brought 10 of those 15 to COMPLETE and **still GATE FAILed its
  identity gate**, so those targets feed nothing. Whether a positivity-preserving
  discretisation of the frozen `omega` source would converge is **not measured**.
* **They cannot see three-dimensional flow.** Every case in this benchmark is a
  statistically two-dimensional mean flow. That is why 12 features are algebraically zero
  (Row 4) and why Pope's ten-tensor basis collapses to rank ~3 — so `g^(5..10)` are
  unconstrained by the training data and multiply non-zero `T^(5..10)` the moment a
  three-dimensional flow is presented. **A benchmark of 2-D flows cannot test the claim
  that ten tensors are what these methods need.**
* **They cannot see a declared FS5 factor.** FS5 names a *"declared factor"* beyond which
  the response is retrain-coverage expansion or explicit documented acceptance. **No build
  has ever declared one.** Row 5's coverage numbers are therefore a measurement without a
  bar, and `COVERAGE.md` refuses to invent one after the fact.
* **They cannot see uncertainty on the truth.** No closure row here propagates a data
  uncertainty band, and the truth itself is unrealisable on **0.79 %** of the scored TEST
  cells (0.8–1.6 % on the Wu split). A model scored against it inherits that.
* **They cannot see the two asymptotic tests.** Charter §5(c) requires that a closure
  switch off in laminar flow and switch off at DNS resolution. Both are free to run; **no
  paper in the 33-work corpus reports either**, and **no row above reports either**.
* **They cannot see cost as money.** Every dollar figure in these rows is **derived** at a
  recorded rate and labelled so. **The box cannot read its own billing**
  (`COMPUTE_BUDGET_CHARTER.md` §5), so no cost here is measured in dollars; core-minutes
  and GPU-hours are.
* **They cannot see whether the V/G/P letters mean what the matrix owner means.** §0 is a
  proposal. If the owner's expansion differs, **the letters are wrong and the evidence
  clauses are still right** — recompute from the clauses.
* **They cannot see anything closure has not landed.** This is a survey of records that
  exist at HEAD on 2026-08-24. The claim in Row 1 that no learned model has beaten the
  ceiling is a reading of those records; **it is not an executed sweep across the tree**,
  and a row that says VERIFY says so because this lane did not verify it.

---

## 3. Items marked VERIFY

Listed once, so the owner does not have to hunt them.

| item | row | why |
|---|---|---|
| Whether the GPU arm-1 comparator's registered **refusal** branch was exercised live (as FS5's A1 refusal was, with mutated readers exiting rc 2) | Row 6, V | The plant is recorded and passed; this lane found no record of the refusal path being run. Do not credit it as demonstrated until checked. |

**Nothing else in this file is marked VERIFY.** Every other figure was read from the record
or artefact cited beside it.

---

## 4. Provenance of this contribution

Written by a closure `lab-lane` under the closure supervisor, 2026-08-24, zero compute, no
solver, no training. Sources read: `CLAUDE.md`; `docs/charters/CLOSURE_MODELLING_CHARTER.md`
§§1–5, §12, §16, §19, §20, §22.5; the `## closure` section of `docs/LAB_STATE.md` **read
from HEAD** (`git show HEAD:docs/LAB_STATE.md`), the worktree copy lagging by design; and
each record and artefact cited in the rows above. Commit shas in the "Last-changed" cells
were derived with `git log -1 --format=%H -- <path>`; **no sha in this file was guessed.**

**This file creates, writes to and touches nothing in `docs/`.** `docs/COVERAGE_MATRIX.md`
is the verification team's and was not opened, created or modified.

---

## 5. ADDENDUM 1 — 2026-08-25 — re-score under the chief's stated V / G / P definitions

**Version: v1.0 → v1.1.** This section is **appended**. **Lines whose number changed
above this section: 0.** Proof, run in one shell invocation immediately before and
immediately after the append, on the prefix alone (`head -n 471`):

| what | value |
|---|---|
| prefix line count, before and after | **471** |
| `sha256(head -n 471 MATRIX_CONTRIBUTION.md)` **before** the append | `4c2183ba0c0ee06331c2d3b2bfa1ae2c686798a991e8a650cdfda7c9b9e2b4d2` |
| `sha256(head -n 471 MATRIX_CONTRIBUTION.md)` **after** the append | `4c2183ba0c0ee06331c2d3b2bfa1ae2c686798a991e8a650cdfda7c9b9e2b4d2` |
| `sha256` of the whole file at HEAD `a42fd634`, and on disk, before the append | `4c2183ba0c0ee06331c2d3b2bfa1ae2c686798a991e8a650cdfda7c9b9e2b4d2` (disk == HEAD) |

**No existing line was edited.** Every letter and tier in §1 stands as written; this
addendum states what those cells become under a definition set that did not exist when
§1 was written, and §0's own invitation is what licenses it: *"If the owner's definitions
differ, the evidence clauses in each cell are the durable part and the YES/NO/PARTIAL
letters should be recomputed from them."* The evidence clauses are unchanged and are
still the durable part.

**Dating, stated because the clock rolled over mid-pass.** Every sweep reported below was
run on **2026-08-24**; this addendum was written and appended as the box's clock turned to
**2026-08-25**, and is dated by the day it lands. The §1 body it is appended to is dated
2026-08-24 and is unchanged.

**Zero compute.** No solver, no training, no GPU. Every finding below is a read of a
record, a source file or a disk sweep.

---

### 5(a) The definitions this re-score uses, quoted as received

These reached the closure supervisor from the chief this session. **They are labelled by
the chief as the CHIEF'S RECONSTRUCTION of Sanaa's brief and NOT her verbatim words, and
that label travels with them everywhere they are used, including here.** Verbatim as
received:

> V = code verification: exact solution, manufactured solution or correlation.
> G = a CONVERGING Roache triple with GCI and an observed order.
> P = validation against a public primary source with a pre-registration on disk.
>
> Tier vocabulary, exactly these five and no synonyms: HOLDS (V+G+P all green under
> frozen prereqs) / GATE REACHED (missing one of V/G/P — name which) / SURVEYED
> (breadth evidence, ungated) / NOT HELD (an honest FAIL or a blocker) / NEVER RUN.

**These are materially narrower than §0's closure-private expansion**, on all three
axes:

* §0's **V** credited a planted-zero control, an identity test or an independent
  re-derivation. The chief's V credits none of those by name; it names three instruments
  closure does not have.
* §0's **G** credited *any* pre-registered numeric gate that could have failed. The
  chief's G is a grid-refinement construct and nothing else.
* §0's **P** credited *any* pre-registered prediction, graded. The chief's P additionally
  requires the comparison target to be a **public primary source**.

Verdict words below are rule-1 vocabulary only. Tier words are the five above only.

---

### 5(b) The G sweep — the load-bearing finding

**Result: NO grid-convergence triple exists anywhere in closure territory. Not one.**
No `CONVERGING` classification, no GCI, no observed order, no refinement ratio, no
coarse/medium/fine family. The closure family has never run a grid-refinement study.

**Methods, both run, because one of them is blind by design.**

1. **`grep -r` over `cases/RANS_LES_closure_models/` and `docs/closure/`.** In this
   environment `grep -r` is `ugrep --ignore-files` and **cannot see gitignored
   archives**, so it was never trusted alone. *It also produced a false-positive class
   worth recording: the pattern `roache`, case-insensitive, matches the substring in
   **app-roache-s**. Five of its hits were the word "approaches".*
2. **`find` + `/bin/grep` on explicit absolute paths**, which honours no ignore file:
   over `/home/ubuntu/Certonomous/cases/RANS_LES_closure_models`,
   `/home/ubuntu/Certonomous/docs/closure`, `/home/ubuntu/closure-data` and
   `/home/ubuntu/closure-challenge-benchmark`. Pattern:
   `[Rr]oache|\bGCI\b|grid.?converg|observed order|order of accuracy|refinement ratio|h-refinement|mesh triple|[Rr]ichardson`,
   plus a separate pass for `extrapolat`, and a filename sweep for
   `*coarse* *medium* *fine* *gci* *roache* *refine* *mesh* *grid*`.
3. **A tracked-vs-disk reconciliation**, because the shared index shows phantom rows:
   `git ls-tree -r HEAD --name-only cases/RANS_LES_closure_models/` returns **148**
   files; `find` returns **174** on disk. The 26 extra are **22 `__pycache__/*.pyc`** and
   **four untracked drafts** (`Bae2022_SciMARL_GPU/PREREGISTRATION_DRAFT.md`,
   `R4b_pair_control/PREREGISTRATION.md`, `Sirignano2020_DPM_GPU/PREREGISTRATION_DRAFT.md`,
   `Ling2016_TBNN/gpu/arm2/LAUNCH_CHECKLIST.md`). **Nothing tracked at HEAD is missing
   from disk.** All four untracked drafts were opened and searched.

**What the sweep found, and what each hit actually is.**

| hit | what it is |
|---|---|
| `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:314` | closure's own written disclaimer, in the frozen pre-registration: *"no `Re` sweep, no mesh-refinement study. A converged answer on one mesh is not a grid-converged answer."* **This is the family admitting the gap in advance, in a frozen file.** |
| `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md:786` | a citation of rule 5's **one-way direction principle** as an analogy for an amendment's direction argument. No triple, no mesh, no refinement. `grep` for `refin|mesh|grid` in that whole file returns **zero** lines. |
| `R4b_pair_control/PREREGISTRATION.md:308` (untracked draft) | *"the grid `G = {0.01, 0.02, ... 1.00}` — twelve values"*. This is a **parameter grid over the scaling `xi`**, not a spatial mesh. Explicitly *"fixed here, not refined afterwards"*. |
| `docs/closure/PAPER_CATALOGUE.md`, `CLOSURE_METHOD_CLASSES_INVENTORY.md`, `FOUNDATIONAL_MODELS_INVENTORY.md`, `_common/FEASIBILITY.md` | **other people's papers**, catalogued. Larsson et al. 2016's demand that WMLES show grid convergence; Lozano-Durán's non-monotonic grid convergence; Spalart's supersonic flat-plate study. **Closure catalogued the requirement and never met it.** |
| `/home/ubuntu/closure-data/kaandorp_tbrf/results.json`, `/home/ubuntu/closure-data/supervisor/msg_xiao.txt` | the word *extrapolation* / *extrapolated*, in the feature-coverage sense. Not Richardson extrapolation. |

**The one candidate that looked like a refinement family, and why it is not.** The R5C
and R4 case names carry a four-digit suffix — `alpha_10_9000_2024`,
`alpha_10_9000_3036`, `alpha_10_9000_4048` — reading like `20×24`, `30×36`, `40×48`.
It was checked rather than assumed. **All three carry `nCells: 15600`, identical**, read
from the `note` header of `constant/polyMesh/owner` under
`/home/ubuntu/closure-data/r5c/frozen/<case>/`. The suffix is the public benchmark's
own PHLL29 parametric-variation label (`closure-challenge-benchmark/README.md:73`),
a geometry/parameter index, **not a grid level**. Same mesh size, different hill.
**No refinement family exists in the R5C 27 or the R4 12.**

**Corroborating structural evidence.** The lab's Roache machinery is
`scripts/roache_triple.py` and `verification/campaign/LADDER_V_TRIPLE_VERIFICATION.md`.
A whole-repo sweep for the triple-classification vocabulary (`CONVERGING`,
`OSCILLATORY`, `STAGNANT`) returns the T-family, the F14 cooling ladder, the ansys
verification cases, one dafoam A3 rung, and the charters — and, in closure territory,
**exactly one file: `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md`, at the single line
above.** No closure file imports or invokes `scripts/roache_triple.py`; the sweep for
`roache_triple|p_obs|apparent order|gci_fine|gci_coarse|Fs *= *1.25` across closure
territory returns **nothing**.

**What this null result proves, and what it does not.** It proves that **no closure
record, script, artefact or out-of-repo data file names a grid triple, a GCI or an
observed order**, under two search methods one of which reads the raw disk and honours
no ignore file. It does **not** prove that no such calculation was ever performed and
left unrecorded — an unrecorded calculation carries no evidentiary weight under rule 2, so
that residue cannot move a letter. It also does **not** cover binary artefacts
(`.npz`, `.pt`, `.pkl`, `.db`), which were not text-searched; a triple hidden in a binary
with no accompanying record would likewise not be a result. **The supervisor's working
hypothesis is CONFIRMED: no closure row can be HOLDS, because G is categorically absent
family-wide.**

**One structural objection, raised here rather than used as an excuse.** The chief's G
is a mesh construct. Rows 4 and 5 are **feature-library audits with no PDE solve and no
mesh** — G is not merely absent there, it is inapplicable, and the five tier words carry
no "not applicable". Rows 2 and 3 are solver rows where G is squarely applicable and
squarely absent, and Rows 1 and 6 are training rows whose claims are about propagated
flows, so the absence bites there too. **This is referred to the supervisor as a
definitional question; it changes no letter below, where G is scored NO throughout.**

---

### 5(c) The V sweep under the chief's definition

**Result: closure has NO code verification in the chief's sense, on any row.** A
`find` + `/bin/grep` sweep over every `.md` and `.py` under
`cases/RANS_LES_closure_models/` for
`manufactured solution|MMS|method of manufactured|exact solution|analytic(al)? solution|closed-form solution|Blasius|Moody|Dittus|Colebrook|Poiseuille|Couette`
returns **zero hits**. The only hits anywhere in closure territory are in
`docs/closure/PAPER_CATALOGUE.md` — other people's papers again.

Per-row classification into the chief's three categories, or out of them:

| row | instrument | classification |
|---|---|---|
| 1 a-priori | GPU G0 planted-zero on the `b_rms` scorer; R4's planted-zero on term selection | **planted-zero control — NOT one of the three** |
| 2 a-posteriori | G0a solver identity `kOmegaSSTCorrected(0,0)` vs stock `kOmegaSST`; the `4.002936e-07` read-back | **identity test — see the ruling below** |
| 3 ceiling | (1) byte-identical reproduction of the internal W2 record; (2) `ic1_check.py` Python re-derivation; (3) R5C's three planted comparators | (1) **internal regression test — NOT one of the three**; (2) **see the ruling below**; (3) **planted-zero control — NOT one of the three** |
| 4 FS2 | Galilean/rotational invariance check at `1e-12`, which caught 58 of 110 features non-invariant | **an identity/symmetry test — NOT one of the three** |
| 5 FS5 | gate A1: plant written to a temporary `.npz`, read back through the audit's own path, **two mutated readers run as subprocesses, rc 0 / rc 2 / rc 2** | **planted-zero control with a proven refusal — NOT one of the three** |
| 6 GPU | G0 plant `1.234e-03` recovered at 1.6e-14 relative | **planted-zero control — NOT one of the three; and see 5(f)** |

**The two items the supervisor asked to be judged on their merits, not dismissed. The
argument on each side is stated; the supervisor rules, not this lane.**

**(a) `R4_sparta_build/ic1_check.py` — worst relative L2 `3.969e-12` on `kDeficit`,
`5.078e-13` on `bijDelta`, over all 12 cases (`RESULTS.md` §4.7,
`artefacts/ic1_discovered.json`).**

*For calling it code verification:* the reference it checks against is **known in closed
form**. `MODEL.json`'s frozen term sets are an algebraic expression; evaluating that
expression at given inputs has an exact answer, and `ic1_check.py` computes it in a
second language, from the same `0/` fields, **independently of the solver**. Agreement at
the ascii round-trip floor is therefore agreement with an exactly-known target, which is
the shape of an exact-solution code verification for the term-evaluation routine. The
file's own docstring names the four specific defect classes it rules out — component
ordering, exponent mapping, the `2k` factor, the `I2` sign — and those are precisely
implementation errors an exact-solution test is for.

*Against:* it verifies **one subroutine's arithmetic**, not the solver, not the
discretisation and not the PDE. It compares two implementations of the same formula
against each other with **no external truth**; a shared misreading of `MODEL.md` would
pass. And the independence is partial — `ic1_check.py` imports
`assemble_dataset.basis`, `sym_to_full` and `of_read.read_field` from
`cases/RANS_LES_closure_models/_common/`, i.e. it shares the tensor-basis and
field-reading code with the harness that built the training data. It is independent of
the **solver**, not of the **lab's own library**.

**This lane's reading: a cross-implementation regression test, not code verification** —
because the target is the lab's own frozen expression rather than an externally-known
solution, and because a shared-library defect survives it. It is a strong instrument and
its evidence clause stands verbatim; it is not V under the chief's definition.

**(b) The Kaandorp a-posteriori G0a solver identity —
`kOmegaSSTCorrected(0,0)` vs stock `kOmegaSST`, `0.0 exactly`, two byte-identical
`600/U` files, `md5 ff95ccb5c5b3f146ac4c364c006352b5` on both
(`aposteriori/RESULTS.md` §G0).**

*For:* it is a **known-answer test on the solver itself**. The correct answer is
analytically zero, known in advance, admitting no tuning; it runs the full discretisation
over 3,025 cells and 200 iterations; and it is the gate the whole lane was registered to
stop on. That is closer to code verification than anything else in the family.

*Against:* the identity verifies that **the correction path vanishes when switched off** —
it says the new code reduces to the old code, not that either is right. Both branches
share the same discretisation, so **a discretisation error common to both is invisible to
it by construction**. The chief's three named instruments all supply an *external*
reference; this one supplies an *internal* one. And the record's own disclosed defect
sharpens the point: at `writePrecision 6` the reader's one-ulp floor **is 4.002936e-07**,
so the registered `1e-10` sits **4,003× below the instrument's resolution** and what the
gate actually establishes is agreement to better than `4.0e-07` relative.

**This lane's reading: an analytic identity the code must satisfy, and a genuine
known-answer test — but a code-to-code identity, not an exact solution of a problem
whose answer is independently known.** Not V under the chief's definition. **The
supervisor rules; if the supervisor rules that a known-answer identity on the full
solver is code verification, Row 2's V returns to YES and Row 2's tier is unaffected,
because G is still NO.**

**A correction closure owes against its own favour, found during this sweep.** §1 Row 1's
V cell says the GPU a-priori `b_rms` scorer *"carries a planted-zero control that was
read back from disk."* **The disk half of that sentence is not supported by the source.**
In `Ling2016_TBNN/gpu/score_gpu_ling.py`, `b_LES` is loaded once from
`/home/ubuntu/closure-data/tbnn/dataset.npz` at line 184; the plant is then applied to an
**in-memory copy** at lines 85–88 (`b_plant = b_clean.copy()`), and the reference
`pred = np.zeros_like(b_clean)` is synthesised in memory, not read from disk. **The plant
never round-trips through a file.** Contrast rule 3's cited exemplar, `T3_runs/analyse_t3.py`'s
`plant_into_T()`, which writes into the field file, and FS5's A1, which writes a temporary
`.npz` and reads it back. **The arm-1 record itself does not make the disk claim** —
`Ling2016_TBNN/gpu/RESULTS.md:21` says only *"plant `1.234e-03` read back within 1e-9
relative"*, which is accurate. **The overstatement is this contribution's, in §1 Row 1,
and it is corrected here rather than left standing.** What the arm-1 control establishes
is that the **scorer arithmetic** responds to a known perturbation; it does not establish
that the **disk reader** can see one.

---

### 5(d) The P sweep under the chief's definition

Public primary source, and the pre-registration path, verified present **both** at HEAD
(`git ls-tree -r HEAD --name-only`) **and** on disk (`find`), each of the six rows:

| row | public primary source | pre-registration path | at HEAD | on disk |
|---|---|---|---|---|
| 1 a-priori | **Ling, Kurzawski & Templeton 2016**, *J. Fluid Mech.* 807:155–166 (on-disk copy is Sandia unlimited release `SAND2016-7345J`; `gpu/PREREGISTRATION.md:34-36` records **no arXiv id**); **Wu, Xiao & Paterson 2018**, *Phys. Rev. Fluids* 3:074602, arXiv:1801.02762v4; **Kaandorp & Dwight 2020**, arXiv:1810.08794v2; **Schmelzer, Dwight & Cinnella 2020**, arXiv:1905.07510v2 | `Ling2016_TBNN/PREREGISTRATION.md`, `Wu2018_PIML_RF/PREREGISTRATION.md`, `Kaandorp2020_TBRF/PREREGISTRATION.md`, `R4_sparta_build/PREREGISTRATION.md` | **yes, all four** | **yes, all four** |
| 2 a-posteriori | **Kaandorp & Dwight 2020**, plus the public benchmark LES/DNS truth fields | `Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md` | **yes** | **yes** |
| 3 ceiling | **contested — see below** | `R4_sparta_build/PREREGISTRATION.md`; instrument repair `R5C_omega_repair/PREREGISTRATION.md` | **yes, both** | **yes, both** |
| 4 FS2 | **none** — the report is generated from the data, not predicted against a source | **NO PRE-REGISTRATION EXISTS.** §1 Row 4 already says so | n/a | n/a |
| 5 FS5 | **none — an internal instrument repair.** The gates A1–A4 predict the behaviour of closure's own audit code, not any published quantity | `_common/features/FS5_D476_CLIP_REPAIR_PREREGISTRATION.md` | **yes** | **yes** |
| 6 GPU | **Ling, Kurzawski & Templeton 2016** | `Ling2016_TBNN/gpu/PREREGISTRATION.md`; arm 2 `Ling2016_TBNN/gpu/arm2/PREREGISTRATION.md` | **yes, both** | **yes, both** |

Every PDF named above is present as a title-page-verified pair under
`docs/papers/closure/` — `Ling2016_tbnn_embedded_invariance.{pdf,txt}`,
`Wu2018_physics_augmenting.{pdf,txt}`, `Kaandorp2020_random_forests.{pdf,txt}`,
`Schmelzer2020_algebraic_reynolds.{pdf,txt}`.

**Row 3's P is the contested one and it is contested against the ceiling's favour.** A
frozen-field ceiling **reads `bijDelta` and `kDeficit` extracted from the truth** and
injects them. Scoring that construction against the same truth field is **not validation
of a prediction** — the row's own §1 text says it: *"It predicts nothing. It is not a
model. It is an upper bound available only when the answer is already known."* And the
row's headline corroboration — `CBFS13700`'s ceiling **0.3975** against the W2 campaign's
**0.39753** — is agreement with **an internal Certonomous record**, not with a public
primary source. **This lane's reading: Row 3's P is NO.** The registered branch that was
graded (does the ceiling beat NULL by 30 %) is an **internal** comparison between two of
closure's own configurations. **The supervisor rules.**

**Two rows registered a prediction against no public primary source, and say so:** Row 4
(no pre-registration at all) and Row 5 (a pre-registration on disk, frozen at commit
`bf4956bc`, blob `8fac067cf4a2c19a205df529db6c79bd48e31f3d`, gating **closure's own
instrument**, not a published result).

---

### 5(e) The re-score table

**OLD** = §1 as written, under §0's closure-private expansion. **NEW** = under the
chief's reconstruction quoted in 5(a).

| row | OLD tier | OLD V/G/P | **NEW tier** | **NEW V/G/P** | evidence for each changed cell |
|---|---|---|---|---|---|
| **1** a-priori model fit | GATE REACHED | YES / YES / YES | **NOT HELD** | **NO / NO / YES** | **V→NO:** the instrument is a planted-zero control, and for the GPU arm it is an in-memory one (`Ling2016_TBNN/gpu/score_gpu_ling.py:85-88`); no exact, manufactured or correlation reference exists — the sweep over every `.md`/`.py` in `cases/RANS_LES_closure_models/` returns zero hits. **G→NO:** no triple anywhere (5(b)). **P stays YES:** Ling 2016 and Wu 2018 are public primary sources and the pre-registrations are at HEAD. **Tier:** two of the row's four records are honest `GATE FAIL` — `Kaandorp2020_TBRF/RESULTS.md` and `R4_sparta_build/RESULTS.md` §6 G1 at 2 of 4 families against a registered 3. |
| **2** a-posteriori propagation | NOT HELD | YES / PARTIAL / YES | **NOT HELD** | **NO / NO / YES** | **Tier unchanged.** **V→NO:** G0a is a code-to-code identity, not one of the three (5(c)(b)); its registered `1e-10` is 4,003× below the instrument's `4.002936e-07` floor (`aposteriori/RESULTS.md` §G0). **G→NO:** the row's own frozen pre-registration says it at `aposteriori/PREREGISTRATION.md:314`. **P stays YES:** Kaandorp & Dwight 2020, pre-registration at HEAD, one commit ever. |
| **3** frozen-field ceiling | **HOLDS** | YES / YES / YES | **NOT HELD** — *this cell was OVERTURNED by the supervisor; see Ruling 2 in 5(k)* | **NO / NO / NO** — *V by Ruling 3, P by Ruling 5* | **See 5(f). This row drops and the drop is not softened.** **G→NO:** no triple; the `2024/3036/4048` suffixes are one mesh at `nCells 15600` (5(b)). **P→NO:** a ceiling built from the truth and scored against the truth is not validation, and its corroborating record (W2, `0.39753`) is internal. **V contested:** `ic1_check.py` at `3.969e-12` / `5.078e-13` — this lane reads it as a cross-implementation regression test (5(c)(a)). **If the supervisor rules V=NO and P=NO, this row is missing two of three and GATE REACHED no longer fits — see the vocabulary gap in 5(h).** |
| **4** FS2 degeneracy | SURVEYED | PARTIAL / NO / NO | **SURVEYED** | **NO / NO / NO** | **Tier CONFIRMED, not dropped** — SURVEYED is exactly "breadth evidence, ungated", and the row already said nothing in it can fail. **V→NO:** the Galilean/rotation invariance check at `1e-12` is a symmetry identity, not exact/manufactured/correlation — though it is the instrument that **caught 58 of 110 features non-Galilean at max relative change 2.000e+00** (`FS2_DEGENERACY_REPORT.md`). G and P were already NO. |
| **5** FS5 extrapolation coverage | SURVEYED | YES / PARTIAL / PARTIAL | **SURVEYED** | **NO / NO / NO** | **Tier CONFIRMED, not dropped.** **V→NO:** A1 is the family's strongest instrument — plant `83.4855` into `AR_14_Ret_180` cell 31818, flagged cells 0→1, and **two mutated readers run live as subprocesses, `clipped_reader` rc 2 and `ignores_disk` rc 2** — and it is still a planted-zero control, not one of the chief's three. **G→NO:** the repair's four gates are not a triple; FS5's own standing gate has **no declared factor, stated three times, met zero times**. **P→NO:** an internal instrument repair, no public primary source. |
| **6** GPU training | NOT HELD | YES / YES / PARTIAL | **NOT HELD** | **NO / NO / PARTIAL** | **Tier unchanged.** **V→NO:** planted-zero control, in-memory (5(c)); and the VERIFY item is now settled negatively — see 5(g). **G→NO:** no triple. **P stays PARTIAL:** Ling 2016 is a public primary source with a frozen pre-registration at HEAD, **but the prediction was registered on the wrong question** — the design's *"full batch by construction"* ran **~3.4e5× fewer updates per epoch** than Ling's per-point SGD (342,014 updates per epoch against one). **A rate is not an optimiser (L-267).** |

---

### 5(f) Every row that DROPS, stated plainly. Row 3 first.

**ROW 3 DROPS FROM `HOLDS`. It is not `HOLDS` and it was never entitled to be under the
chief's definitions.** The reason is not a judgement call and not a matter of degree:
**`HOLDS` requires V+G+P all green, G requires a CONVERGING Roache triple with a GCI and
an observed order, and no closure row — including this one — has ever run a grid
refinement of any kind.** The ceiling's twelve cases are twelve different flows on twelve
different meshes, one mesh each. §1 called this row *"the one thing in this family that
does"* hold. **Under the owner's definitions it does not, and the sentence in §1 is
superseded by this addendum.** Beyond G, the row's P is a comparison of a
truth-constructed field against the truth, and its V rests on instruments this lane reads
as regression and planted-zero controls. **A row that claims more than its verdict is
exactly the failure this matrix exists to prevent, and this row claimed the most.**

Nothing in the ceiling's *measurements* is withdrawn. `eps(U)_CEILING / eps(U)_NULL` is
still `0.003523` on `PHLL10595`, `0.398057` on `CBFS13700`, `0.000140` on
`AR_5_Ret_180`; the duct vortex recovery is still 0.09–0.61 % where a linear EVM gives
exactly zero. **What is withdrawn is the tier, not the numbers.**

**ROW 1 DROPS FROM `GATE REACHED` TO `NOT HELD`.** Under §0's expansion it held all three
letters. Under the chief's it holds one. Its class contains two honest `GATE FAIL`
records, and closure's own Charter §2 already forbade the tier going higher: **an
a-priori score alone is `NOT A RESULT` for any claim that a closure improves a flow.**

**ROWS 2 AND 6 DO NOT DROP IN TIER — they were already `NOT HELD` — but their letters
drop from YES/PARTIAL/YES and YES/YES/PARTIAL to NO/NO/YES and NO/NO/PARTIAL.** A tier
that was already at the floor cannot fall further; the letters that supported it can and
do.

**ROWS 4 AND 5 DO NOT DROP AT ALL IN TIER.** `SURVEYED` is confirmed by the narrower
definitions, because `SURVEYED` is the one tier that asks for no gate. Their V letters
drop to NO.

**Nothing goes UP.** This lane looked for a row the narrower definitions would raise and
found none. The nearest candidate is Row 5: **its A1 gate is the only instrument in the
closure family whose refusal path was proven live**, with two deliberately broken readers
exiting rc 2 and naming the planted value, the cell and the expected-versus-observed
counts. Under the chief's V that instrument scores **NO**, because a planted-zero control
is not an exact solution, a manufactured solution or a correlation. **That is recorded as
a place where the definition may be too narrow for a feature-library audit that has no
PDE — a question for the owner, not a licence for closure to score itself higher.**

---

### 5(g) The one VERIFY item — SETTLED, and settled negatively

§3 carried one item: *whether the GPU arm-1 comparator's registered **refusal** branch
was exercised live, as FS5's A1 refusal was.* **It is settled by reading the record and
the comparator source. It was NOT exercised live.** Three independent legs, all cheap:

1. **The source.** `Ling2016_TBNN/gpu/score_gpu_ling.py` contains two refusal branches —
   G0a at lines 106–109 and G0b at lines 117–119, both `sys.exit(2)` with refusal text.
   **Both are present and reachable. Nothing in the file, in `run_all_gpu.sh`, or in
   `train_gpu_ling.py` runs a mutated reader or checks a return code.** Contrast FS5's
   repair, which runs `clipped_reader` and `ignores_disk` as subprocesses and asserts
   rc 2 on each.
2. **The artefacts.** A `find` + `/bin/grep` sweep for `REFUSAL|mutat` across every
   `.json`, `.log`, `.txt` and `.csv` under `/home/ubuntu/closure-data/tbnn_gpu/` returns
   **nothing**.
3. **The record's own words.** `Ling2016_TBNN/gpu/RESULTS.md:197`: the run's timestamps
   are continuous 21:21:32Z → 08:03:58Z and *"no BLOCKED or REFUSED state was"* entered.

**Settlement: the arm-1 refusal branch is PRESENT and READABLE but NOT DEMONSTRATED.**
Under rule 3's principle — *a zero from a reader not shown able to see a non-zero is not
evidence* — the G0a plant does show the **scorer** responding to a non-zero, so the gate
is not empty. But the refusal path itself is unexercised, and per 5(c) the plant is
applied in memory rather than round-tripped through disk, so **the arm-1 control is
weaker than FS5's A1 on both counts**. §3's VERIFY row is discharged by this finding, not
by a confirmation. **This does not move the arm-1 verdict**, which is `NOT A RESULT` on
G1/G3 and `GATE FAIL` on G2 and stands unchanged.

**Arm 2's comparator inherits the same shape.** `arm2/score_gpu_ling_v2.py` carries the
same two refusal branches at lines 128 and 139. **Nothing here is a recommendation to
change arm 2's frozen code — it is frozen and unlaunched, and this is an observation for
the owner, not an amendment.**

---

### 5(h) The four closed verdicts as the anchor, and the tier check against them

The four verdicts that are closed, restated as the ceiling the tiers may not exceed:

| verdict | record |
|---|---|
| **Ling2016 GPU arm 1 — `NOT A RESULT`** | `Ling2016_TBNN/gpu/RESULTS.md`, graded personally by the closure supervisor 2026-08-24T16:07:25Z |
| **Kaandorp a-posteriori — `NOT A RESULT`** | `Kaandorp2020_TBRF/aposteriori/RESULTS.md`, whole lane, all three registered cases |
| **R5C — `GATE FAIL`** | `R5C_omega_repair/RESULTS.md` §3.1; `kDeficit` rel L2 `1.1848e-04` on `alpha_10_12000_4048` against a registered `1e-6` |
| **R4 — `GATE FAIL`** | `R4_sparta_build/RESULTS.md`; both registered halves fired independently |

Row-by-row check, **and one row is flagged**:

* **Row 6 vs arm 1 `NOT A RESULT`** — tier `NOT HELD`. Does not read richer. **OK.**
* **Row 2 vs Kaandorp `NOT A RESULT`** — tier `NOT HELD`. Does not read richer. **OK.**
* **Row 1 vs R4 `GATE FAIL`** — tier `NOT HELD`. Does not read richer. **OK.**
* **Row 4, Row 5 vs nothing closed** — tier `SURVEYED`, ungated by construction. **OK.**
* **ROW 3 IS FLAGGED.** Its tier, even after dropping to `GATE REACHED`, rests on
  **two records whose own verdicts are `GATE FAIL`**: the ceiling was measured inside the
  R4 lane, whose verdict is `GATE FAIL`, and its instrument repair R5C is a `GATE FAIL`
  on its identity gate with **3 of the 12 not CONVERGED under G3**. The ceiling is a
  sub-arm that met its own registered branch, and §1 says so — but **a reader who sees
  `GATE REACHED` on Row 3 and `GATE FAIL` on both of its underlying records is entitled
  to ask which is the row's verdict.** This lane's answer: **the row's tier must not be
  read as a verdict on R4 or R5C, and R4's `GATE FAIL` and R5C's `GATE FAIL` stand
  untouched by anything in this addendum.** Whether `GATE REACHED` is a defensible tier
  for a sub-arm of a `GATE FAIL` lane is **referred to the supervisor**, and if the answer
  is no, Row 3 falls to `NOT HELD`.

**The vocabulary gap, reported rather than filled.** The chief's `GATE REACHED` is defined
as *"missing one of V/G/P — name which"*. **Rows 1, 2 and 6 are missing two; Rows 4 and 5
are missing three; Row 3 is missing at least two on this lane's reading.** The five words
carry no tier for "missing two". This lane refused to coin a sixth word (rule 1's
discipline, applied to the tier vocabulary by the supervisor's instruction) and instead
routed each such row to `NOT HELD` where the class contains an honest FAIL or a blocker,
and to `SURVEYED` where it is ungated breadth. **That routing is this lane's proposal and
is the supervisor's to confirm or overturn. It is the single largest source of
uncertainty in this re-score, and it is named rather than buried.**

---

### 5(i) Arm 2 is untouched

**Arm 2 remains `PENDING` in the rule-1 display/queue sense: not yet run.** Nothing about
arm 2 has been graded, no number exists, and `PENDING` here is not a softened `GATE FAIL`
and must never be read as one. Its pre-registration is **frozen and committed alone
before any compute at `f36fbdd9`** (2026-08-24T16:27:45Z), last-changed `77f064a8` after
three pre-compute amendments, and the instance was **STOPPED at freeze**. **No GPU node is
running and nothing in this addendum proposes launching one** — that is Sanaa's decision,
per item, with a console-read `cost_basis`, and GPU spend sits outside the 2026-08-21 CPU
blanket.

---

### 5(j) Scope, cost, and what this addendum did not do

* **`docs/COVERAGE_MATRIX.md` was not created, opened for writing, read for writing, or
  touched.** It is the verification team's.
* **`docs/LAB_STATE.md` was not touched.** The closure supervisor owns that section.
* **Nothing was committed by the lane that drafted this.** The closure supervisor reads
  the diff personally before anything lands.
* **Nothing was sent, filed, uploaded, registered or posted. Submissions are parked.**
* **Zero compute.** No solver, no training, no GPU, no run directory created. Cost:
  **0.000 core-minutes**; there is no pre-registered estimate to calibrate against because
  no run was pre-registered — this is a documentation pass, not a process completion in
  the rule-12 sense.
* **Tracked state was read with `git ls-tree -r HEAD` and `git cat-file -p HEAD:<path>`**,
  because the shared index shows phantom `D`/`MM` rows in closure territory while disk
  equals HEAD; `MATRIX_CONTRIBUTION.md` was confirmed identical on disk and at HEAD
  (`4c2183ba…b4d2`) before the append. **No `git checkout --`, `git reset`, `git stash` or
  `git clean` was run.**

**End of Addendum 1.**

---

### 5(k) SUPERVISOR'S RULINGS on the questions 5(b)–5(h) referred upward

Written by the **closure supervisor personally**, 2026-08-25, before this addendum was
committed and after reading the whole draft above as a diff. The draft was **uncommitted
and never landed** when these rulings were written, so they are recorded here as part of
Addendum 1 rather than as a later correction of it. **Two cells of the draft above were
edited by the supervisor before landing — both are named in 5(k)(2) and nowhere else —
and every other line of 5(a)–5(j) is the lane's, unedited.**

The independent re-verification the supervisor did **personally, not relayed**: the
append-only claim was re-proved with `git diff --numstat` at HEAD — **441 insertions,
0 deletions** for the lane's draft as it was handed over, and **622 insertions, 0
deletions** for the file as it lands with these rulings appended, still a pure append
because every line of §5 is new at HEAD — and by re-hashing `head -n 471` on disk to
`4c2183ba0c0ee06331c2d3b2bfa1ae2c686798a991e8a650cdfda7c9b9e2b4d2`, **equal to the
whole-file hash at HEAD `a42fd634`**; and the four closed verdicts of 5(h) were re-read
from their own records at HEAD, not from this file (`gpu/RESULTS.md:3`
`# VERDICT: NOT A RESULT`; `aposteriori/RESULTS.md:2-4` H0 GATE FAIL ⇒ H1–H3 NOT A
RESULT; `R5C_omega_repair/RESULTS.md:3` `# VERDICT: GATE FAIL`;
`R4_sparta_build/RESULTS.md:23` `# VERDICT: **GATE FAIL**`).

**RULING 1 — the vocabulary gap. The lane's routing is CONFIRMED, and no sixth word is
coined.** The chief's `GATE REACHED` is defined as *"missing one of V/G/P — name which"*.
A row missing **two or three** is therefore **not eligible for `GATE REACHED` at all** —
the definition is a count, not a direction. The lane routed such rows to `NOT HELD` where
the class contains an honest FAIL or a blocker and to `SURVEYED` where it is ungated
breadth. **That routing is correct and is adopted.** The governing principle when a fixed
vocabulary does not cleanly fit is the one this matrix exists to serve: **the tier must
never read richer than the evidence, so an unfitted row goes DOWN, never up.** The gap
itself — that the five words carry no tier for "missing two" and none for "not
applicable" — is **referred to the matrix owner (verification) through the chief**, as a
question about the vocabulary and not a licence for closure to relabel itself.

**RULING 2 — ROW 3 FALLS TO `NOT HELD`. The draft's `GATE REACHED` is OVERTURNED.** The
lane proposed `GATE REACHED (missing G)` and flagged, correctly and against its own
proposal, that on its own reading the row is missing **two or three**. Two independent
grounds, either sufficient:

* **(i) Arithmetic, under Ruling 1.** The row's P is NO (5(d)) and its V is at best
  contested (5(c)(a)). Missing two, `GATE REACHED` is unavailable by the definition's own
  terms.
* **(ii) The anchor check of 5(h), which the lane raised and referred.** The ceiling was
  measured inside the **R4** lane, whose verdict is **`GATE FAIL`**, and its instrument
  repair **R5C** is a **`GATE FAIL`** on its identity gate at `kDeficit` rel L2
  **1.1848e-04** against a registered **1e-6**. **A sub-arm of a `GATE FAIL` lane may not
  carry a tier that reads richer than the lane's own verdict.** I rule that explicitly,
  because the lane asked: the answer is **no**.

`NOT HELD` — *"an honest FAIL or a blocker"* — is the fitting tier and not merely the
residual one: the row carries **two honest FAILs** (R4, R5C) and **a live blocker** (15 of
27 hills never completed under the strict rule in R4; R5C brought 10 of those to COMPLETE
and still GATE FAILed, so those targets feed nothing, and whether a positivity-preserving
discretisation of the frozen `omega` source would converge is **not measured**).
`SURVEYED` was considered and **rejected**: this row is not ungated breadth — it carried a
registered NOT-A-RESULT branch that did not fire, and its G3 continuity gate **did** fire
`NOT CONVERGED` on `AR_1_Ret_180` at `1.0628e-04`.

**None of the ceiling's measurements is withdrawn, and this ruling withdraws no verdict.**
`eps(U)_CEILING / eps(U)_NULL` stands at `0.003523` / `0.398057` / `0.000140`; the duct
vortex recovery stands at 0.09–0.61 % where a linear EVM gives exactly zero; the
byte-identical W2 reproduction stands. **What is withdrawn is a tier, and it is withdrawn
by two steps — `HOLDS` → `GATE REACHED` → `NOT HELD` — because the family's single
strongest row was also its single largest overstatement.**

**RULING 3 — `ic1_check.py` is NOT code verification. Row 3's V is `NO`, not
`CONTESTED`.** The lane's reading is adopted, on the ground it identified as decisive and
which the supervisor re-checked: the checker **imports `assemble_dataset.basis`,
`sym_to_full` and `of_read.read_field` from `_common/`**, so it is independent of the
**solver** and not of the **lab's own library** — a shared-library defect survives it —
and its target is closure's **own frozen `MODEL.json` expression**, not an externally
known solution. The argument for the other side is real and is preserved verbatim in
5(c)(a); it loses on independence. Row 3's V is therefore **`NO`**, which strengthens
Ruling 2's ground (i) from "at best contested" to "missing two, plainly".

**RULING 4 — the G0a solver identity is NOT code verification. Row 2's V stays `NO`.**
Adopted on the lane's decisive point: **both branches share the discretisation, so an
error common to both is invisible by construction**, and all three of the chief's named
instruments supply an *external* reference where this supplies an *internal* one. It
remains a genuine known-answer test on the full solver and the strongest V-axis
instrument in the family; it is not V under this definition set. **Row 2's tier is
unaffected either way, because G is NO.**

**RULING 5 — Row 3's P is `NO`. Adopted.** A field constructed from the truth and scored
against that same truth is not validation of a prediction, and the row's corroboration
(`0.3975` against W2's `0.39753`) is agreement with **an internal Certonomous record**.
The row's own §1 text already said the substance of it.

**RULING 6 — the in-memory plant is a RULE-3 FINDING, not a typo, and it is recorded as
one.** The lane found, against closure's own favour, that §1 Row 1's *"read back from
disk"* is unsupported: in `Ling2016_TBNN/gpu/score_gpu_ling.py` the plant is applied to an
**in-memory copy** (lines 85–88, `b_plant = b_clean.copy()`) and the reference is
`np.zeros_like`, so **the plant never round-trips a file**. The supervisor's reading goes
further than the correction. **CLAUDE.md rule 3 requires that a comparator *"plants a
known perturbation, reads it back from disk, and refuses if the reader cannot see it."*
The GPU comparator satisfies neither the disk limb (5(c)) nor the refusal limb (5(g),
settled negatively).** Consequences, stated exactly and no wider:

* **No verdict moves.** Arm 1 is already **`NOT A RESULT`**; a weaker control cannot make
  a NOT A RESULT weaker, and the arm-1 record's own wording was accurate — the
  overstatement was this contribution's and is corrected above.
* **What the arm-1 G0 control does establish** is that the **scorer arithmetic** responds
  to a known perturbation. **What it does not establish** is that the **disk reader** can
  see one. Those are different claims and the record now separates them.
* **This is live for arm 2, which is frozen and UNLAUNCHED**, and whose comparator
  `arm2/score_gpu_ling_v2.py` carries the same shape at lines 128 and 139. Amendments
  before first compute are legal (rule 2), so a repair is *available* — and is
  **deliberately NOT made tonight**. Arm 2 cannot launch in any case (its gate is Sanaa's
  own words, her start of the instance and her two console readings), so there is **no
  urgency**, and a change to a frozen instrument written at speed is precisely what
  supervisor check 1 exists to prevent. **Recorded as an OPEN INSTRUMENT QUESTION with the
  supervisor's recommendation: before arm 2 ever runs, its planted-zero control should
  round-trip the plant through a file and its refusal path should be exercised live
  against a deliberately blinded reader, as FS5's A1 does — which would be a fourth
  pre-compute amendment, needing its own stated condition, its own condition check, and
  the supervisor's own diff read.** Nothing is amended by this addendum.

**RULING 7 — G's inapplicability to Rows 4 and 5 changes no letter.** The lane is right
that a feature-library audit with no PDE and no mesh cannot have a Roache triple, and that
the five words carry no "not applicable". **G stays `NO` on those rows** — the honest
record is that the evidence is absent, and inventing an exemption would be the same
failure in the other direction. The definitional question is **referred to the matrix
owner**, with the note that it is closure's rows that would benefit, which is precisely
why closure does not decide it.

---

#### 5(k)(1) The re-score AS RULED — THIS TABLE GOVERNS

It supersedes the "NEW tier" column of 5(e) and the provisional tier language of 5(h)
wherever they differ. Where 5(h) reads *"even after dropping to `GATE REACHED`"* it is
recording the lane's own referred proposal, preserved so the argument is auditable;
**Ruling 2 answered that referral and the answer was no.**

| row | §1 as written | **AS RULED** | **V / G / P as ruled** |
|---|---|---|---|
| **1** a-priori model fit | GATE REACHED | **NOT HELD** | NO / NO / YES |
| **2** a-posteriori propagation | NOT HELD | **NOT HELD** | NO / NO / YES |
| **3** frozen-field ceiling | **HOLDS** | **NOT HELD** *(Ruling 2 — down two steps)* | **NO** *(Ruling 3)* / NO / **NO** *(Ruling 5)* |
| **4** FS2 degeneracy | SURVEYED | **SURVEYED** | NO / NO / NO |
| **5** FS5 extrapolation coverage | SURVEYED | **SURVEYED** | NO / NO / NO |
| **6** GPU training | NOT HELD | **NOT HELD** | NO / NO / PARTIAL |

**Closure offers the matrix owner NO row at `HOLDS` and NO row at `GATE REACHED`.** Four
rows at `NOT HELD`, two at `SURVEYED`, none `NEVER RUN`. **G is `NO` on every row without
exception**, because the closure family has never run a grid-refinement study of any kind
— a null established under two search methods, one of which reads the raw disk and honours
no ignore file, and admitted in advance in closure's own frozen pre-registration
(`Kaandorp2020_TBRF/aposteriori/PREREGISTRATION.md:314`: *"no mesh-refinement study. A
converged answer on one mesh is not a grid-converged answer."*).

**These letters and tiers are closure's OFFER, not a matrix entry.** The owner re-maps,
renames, merges or rejects any row without asking, and `docs/COVERAGE_MATRIX.md` remains
untouched by closure.

#### 5(k)(2) The two cells the supervisor edited in the draft above, named in full

Disclosed so no reader has to diff the draft against what landed. **Exactly ONE line was
edited: the Row 3 line of the 5(e) table.** Its "NEW tier" field went from
`**GATE REACHED** — missing **G**` to `**NOT HELD**` under Ruling 2, and its letters field
from `**CONTESTED / NO / NO**` to `**NO / NO / NO**` under Rulings 3 and 5; both now point
here. **Nothing else in 5(a)–5(j) was touched** — including 5(f)'s Row 3 paragraph, which
needed no edit because it states only that the row drops from `HOLDS`, which is true and
now truer. The lane's reasoning for its own superseded proposal is preserved verbatim
wherever it appears, and the supervisor's overturning of it is recorded here rather than
by deleting it.

#### 5(k)(3) What this addendum did NOT do, restated at the supervisor's level

**No verdict moved.** R4 stays `GATE FAIL`, R5C stays `GATE FAIL`, Kaandorp a-posteriori
stays `NOT A RESULT`, Ling arm 1 stays `NOT A RESULT`, A3 stays `GATE FAIL`. **Arm 2 stays
`PENDING` in the display/queue sense and UNFIRED**; nothing here proposes launching it, no
GPU node is running, and its launch gate is unchanged — **Sanaa's own words, her start of
the instance, and her two console readings; no agent message, the chief's included, is her
consent (rule 9), and GPU spend is outside the 2026-08-21 CPU blanket (rule 12).** **No
frozen file was edited.** **Zero compute: 0.000 core-minutes, 0.000 GPU-hours.** Nothing
was sent, filed, uploaded, registered or posted — **submissions are parked**.

**End of Supervisor's Rulings.**
