# T5f — the unequal region refinement ratio ruling, owed by `T5f_PREREGISTRATION.md` §3.1

**Team: heat-transfer. Ruling by the heat-transfer supervisor, `[lab-attributed]`.**
**Dated 2026-09-12. Issued BEFORE any T5f solver has run.**

> **NOT SENT, NOT FILED.** `CLAUDE.md` rule 7. Nothing here leaves the box.
> **No verdict from rule 1's vocabulary is assigned by this document.** It is a
> ruling about how a future triple may be graded, not a grade.

---

## 0. WHY THIS DOCUMENT EXISTS, AND WHY IT IS DATED TODAY

`T5f_PREREGISTRATION.md` §3.1, frozen, says:

> "The two regions refine at different ratios and the heat-transfer supervisor
> holds an open ruling on whether a conjugate triple whose regions refine
> differently is three geometrically similar meshes. **That ruling is owed BEFORE
> any T5f triple is graded** and this registration does not pre-empt it."

**It is issued now, before any T5f case has produced a value, so that it cannot be
shaped by T5f's answer.** At the time of writing `T5F_CUBE_{c,m,f}` exist as built
meshes with **no `log.solve` and no time directories**. No T5f has run.

**Rule 2 analysis, stated so a later reader can check it rather than trust it.**
This document does **not** amend `T5f_PREREGISTRATION.md` and does not alter any
gate, threshold, cap or label in it. §3.1 reserved this ruling to the supervisor
and explicitly declined to pre-empt it. T5f §4 names only `analyse_t5e.py`
(limb A) and `t5f_convergence_gate.py` (limb B); **no triple comparator is
registered for T5f at all.** So what follows binds the *registration of that
future comparator*, and it can only make a row harder to grade — the one-way
direction rule 5 permits. No frozen file is edited by this document.

---

## 1. THE EVIDENCE THIS RULING RESTS ON

A `lab-lane` was briefed **to refute the supervisor's draft, not to support it**,
at **zero solver core-minutes**. Instrument and outputs:

- `verification/runs/T-family/T5f_runs/t5f_region_ratio_audit.py` — 17 controls,
  every one driven both directions; calls `scripts/roache_triple.py` rather than
  reimplementing it.
- `verification/runs/T-family/T5f_runs/T5F_REGION_RATIO_AUDIT.txt`
- `verification/runs/T-family/T5f_runs/T5F_REGION_RATIO_SENSITIVITY.json`

**It refuted the draft. The draft is not issued.** What follows is the corrected
ruling, and §3 records what was wrong with the original in the supervisor's own
name rather than quietly shipping a better version.

### 1.1 The registration's arithmetic is CONFIRMED — nothing to correct

Per-region cell counts recovered by two routes sharing no code (`polyMesh/owner`
`nCells:` headers; summing `nx·ny·nz` over the 74 `hex … <zone>` lines of each
`system/blockMeshDict`) agree **exactly**, with `log.checkMesh` as a third route.

| | registered | measured | \|Δ\| |
|---|---|---|---|
| air `r32` | 1.5929 | 1.592921 | 2.08e-05 |
| air `r21` | 1.6060 | 1.605978 | 2.16e-05 |
| epoxy `r32` | 1.5557 | 1.555719 | 1.91e-05 |
| epoxy `r21` | 1.6428 | 1.642813 | 1.29e-05 |

End-to-end agreement **+0.0955 %** against the registered 0.095 %; per-step
divergence **−2.3354 % / +2.2936 %** against the registered −2.34 / +2.29. **All
three of §3.1's claims confirmed.** *Precision note, not a defect: the two steps
are not exactly equal and opposite — their first-order sum is −0.0419 pp.
"Equal and opposite" is a fair description, not an identity.*

### 1.2 Integer rounding is the WHOLE explanation — residual exactly zero

With exact fractional divisions (`base · 1.6^lvl`, no rounding) both regions give
`r32 = r21 = 1.6000000000` to machine precision. With `round()`, the recipe
reproduces the meshes on disk with a residual of **+0 cells at all six
region/level combinations.** Rounding accounts for 100 %.

### 1.3 The interface is CONFORMAL, and the supervisor verified this himself

Coupled patches `cube_front`, `cube_rear`, `cube_top`, `cube_side_n` carry
**identical face counts on the air side and the epoxy side at every level** —
**469 / 1,144 / 3,078** — read directly from each region's
`constant/<region>/polyMesh/boundary`. **Tangentially there is no air-versus-epoxy
choice to bound.** The in-surface pair is one unambiguous measurement, `dim = 2`:
**`r21 = 1.640292`, `r32 = 1.561804`.**

### 1.4 Wall-normally there ARE two meshes, and they diverge 2.7× more than §3.1's figures

- **Air** first-layer thickness, from each case's own `CASE.txt`: 1.28e-4 / 8e-5 /
  5e-5 m → **`r21 = 1.600000`, `r32 = 1.600000`** — exactly.
- **Epoxy** shell normal divisions, identified from block *geometry* (extent ==
  `DELTA`) rather than assumed: 2 / 3 / 5 → **`r21 = 1.666667`, `r32 = 1.500000`.**
- Divergence **−6.2500 % then +4.1667 %**, against the region-mean −2.3354 /
  +2.2936. ***That is 2.7× and 1.8× larger than the figures §3.1 quotes.***

**And this is not academic: `analyse_t5e.py:238` sets
`GRADED_H = {"G1a": "cube_front", "G2a": "cube_top", "G3a": "cube_rear"}` —
ALL THREE primary graded rows are interface quantities.**

### 1.5 The sensitivity, computed rather than asserted

80 synthetic power-law triples, `p_true` 0.5–4.0 across amplitudes 0.02–5.0, each
graded under both ratio sets by `roache_triple.gci_unequal`. **The relative GCI
spread is amplitude-invariant — it depends only on `p_true`.**

| ratio pair | \|Δp\| | \|ΔGCI\| relative |
|---|---|---|
| region means (the draft's figures) | 0.2133 – 0.2826 | 21.81 – 37.10 % |
| **interface wall-normal (the correct pair)** | **0.5263 – 0.7949** | **44.14 – 61.57 %** |

**There is no GCI magnitude below which the ratio choice stops mattering.** At
every ceiling swept from 0.1 % to 5 % there are triples the choice alone moves
across.

---

## 2. THE RULING

**Prospective. T5f and its successors on this ladder.** A conjugate triple on this
ladder may be graded as a systematically refined family **only** under all four
clauses below. The burden sits on the row, not on the reader.

### (a) NO SINGLE REFINEMENT RATIO MAY BE ASSUMED

Every observed order and every GCI is computed with the **generalised
non-constant-`r` (Celik) fixed point**, on ratios **MEASURED from the built
meshes** — never typed, never inherited from a predecessor, never taken from this
document. `scripts/roache_triple.py:276` already implements the form.

### (b) INTERFACE ROWS CARRY A BOUNDING SENSITIVITY OVER **THREE** MEASURED PAIRS

Not two. The three pairs are §1.3's in-surface pair and §1.4's two wall-normal
pairs:

| pair | `r21` | `r32` | basis |
|---|---|---|---|
| in-surface (conformal, single-valued) | 1.640292 | 1.561804 | coupled-patch face counts, `dim = 2` |
| air wall-normal | 1.600000 | 1.600000 | first-layer thickness |
| epoxy wall-normal | 1.666667 | 1.500000 | shell normal divisions |

`p` and the GCI are recomputed under **each** pair and **all three printed beside
the row.** *The tangential conformality is stated as a measurement, not offered as
a choice.*

### (c) THE BOUND IS EVALUATED ON THE RULE-5 **STATE** FIRST, THE BAND SECOND

**If the three pairs do not agree on the triple's state — `CONVERGING` versus
`DIVERGENT` / `STAGNANT` / `OSCILLATORY` / `EXACT` — the row is `NOT A RESULT`,
whatever any of them says about the value, and no GCI is quotable.** Only if all
three agree `CONVERGING` does the band question arise; and if the band verdict
then differs across the three pairs, the row is **`NOT A RESULT`**.

> **This clause exists because the supervisor's draft did not have it, and its
> absence was the draft's most dangerous defect.** Measured: the ratio choice
> *alone* flips a triple between `STAGNANT` and `CONVERGING` over a contiguous
> `p_true` window of width **0.212** under the region means and **0.445** under
> the interface wall-normal pairs — *and that window sits exactly where a
> conjugate ladder with a harmonic interface is likeliest to land.* The draft
> bounded the GCI and said "if that spread changes the verdict"; read narrowly,
> a state flip escapes that clause entirely, and one region's ratios would grant a
> row a verdict the other denies it. **A clause that bounds the value while the
> state flips underneath it is a gate that cannot fire where it matters most** —
> the fifth such gate this team has found in four days, and the first one the
> supervisor authored himself.

### (d) SCOPE: PROSPECTIVE ONLY

This ruling binds T5f and successors. **It does not re-grade anything.** The
retrospective question is referred, not decided — §4.

---

## 3. WHAT THE SUPERVISOR GOT WRONG, IN HIS OWN NAME

The draft ruling was wrong in three ways and right in one.

1. **It bounded the wrong quantity.** It proposed bounding air's region-mean
   ratios against epoxy's. The tangential interface is **conformal**, so there is
   nothing to bound there; and the real divergence is **wall-normal** and
   **2.7× larger** than the figures the draft would have used. *The draft
   understated the problem roughly twofold while appearing to address it.*
2. **It bounded the value and not the state** — §2(c). Rule 5 orders the state
   ahead of the value, and the draft inverted that in its own clause.
3. **It framed the question as conjugate-specific, and the framing presupposed
   something false** — §4.
4. **Item (a) was correct**, and survives unchanged.

*The draft was put on `docs/LAB_STATE.md` as a draft, before its evidence
arrived, precisely so that this correction would be visible rather than absorbed.*

---

## 4. REFERRED, NOT DECIDED — and it is larger than the question that was asked

***The per-slab local refinement ratios inside `build_t5.py` span 1.5000 to
2.0000*** — the `BASE_Y[1]` slab (y ∈ [0.0005, 0.0015], inside the cube's
j-range) goes 1 / 2 / 3, giving `r32 = 2.0000` and `r21 = 1.5000`. **That is a
31.25 % spread of nominal, an ORDER OF MAGNITUDE larger than the 2.3 %
between-region difference this ruling was asked about.**

***So neither region, taken alone, is a strictly geometrically similar family
either.*** The question as posed — *is a **conjugate** triple with unequal region
ratios three similar meshes?* — presupposes that a single-region triple on this
ladder would be. **It would not be.**

**Eça & Hoekstra (2014), assumption 2, is adverse and is the only primary clause
on non-constant `r` in this box:** grid density must be representable by a single
parameter, which *"requires the grids to be geometrically similar, i.e. **the grid
refinement ratio must be constant in the complete field**."* They name lack of
geometric similarity as a main contributor to noisy data, and recommend **at least
four grids** where scatter is expected. *It is an assumption statement and a
recommendation, not a prohibition — and Celik's unequal-`r` fixed point is the
standard accommodation, already implemented here.*

**THEREFORE REFERRED to the chief and to verification, and NOT settled by this
team:** whether the T5 ladder's intra-region slab non-uniformity invalidates
triples already graded on it. **That would re-grade published records**, which is
not a supervisor's unilateral act — and it reaches beyond the T-family, since the
builder pattern is not unique to it.

---

## 5. TWO INSTRUMENT FINDINGS, REPORTED AND NOT REPAIRED

**5.1 The grading path computes AIR's ratios only, and every primary graded row is
an interface quantity.** `analyse_t5e.py:219` fixes
`CELLS_REGISTERED = {"c": 52684, "m": 212942, "f": 882024}` — air — and the reader
at `:1987` takes the **first** `cells:` match in `log.checkMesh`, which is air.
**`epoxy` appears three times in the whole 124 KB comparator and in none of them as
a cell count or a ratio.** Verified at source by the supervisor. **`analyse_t5e.py`
is FROZEN** (T5f §9, sha256 `c97d355d…`), so this is a finding and not a repair.
*It also means §2(a) currently has no registered instrument to bind — which is why
§2 binds the registration of T5f's future triple comparator instead.*

**5.2 This lab implements Celik's formula without holding Celik's paper.**
Title-page verified by fresh extraction (rule 15, L-144): **Eça & Hoekstra (2014)**,
*J. Comput. Phys.* **262**, 104–130, and **Dowding (2016)**, SAND2016-5342C, are
genuinely present in `docs/papers/verification_validation/`. But **Oberkampf & Roy
(2011) is present only as the 12-page Cambridge frontmatter preview** — §8.6
*"Roache's grid convergence index (GCI)"* exists solely as a table-of-contents
line — and **Roache (1998, 2009) and Celik et al. (2008) are not in this box at
all**, surviving only as references inside Eça & Hoekstra's bibliography.
***Citing Oberkampf & Roy for GCI from this box is a stretched citation and should
be refused.*** **On conjugate or multi-region grid refinement the box contains
nothing**: zero hits across all three sources, and the only "conjugate" hits in
`docs/papers/` are conjugate-*gradient* solvers or conjugate heat transfer as
physics. *An honest "the box does not contain an answer" is worth more than a
stretched citation.*

---

## 6. WHAT THIS RULING CANNOT DO

- **It cannot tell whether real T5f interface quantities land in the state-flip
  window.** That is unknowable before the run. And the sensitivity was computed on
  **perfect power laws**, so if Eça & Hoekstra are right that lost similarity adds
  scatter, ***these spreads are a LOWER BOUND on the real sensitivity.***
- **It does not re-grade, re-open or repair anything** — not T5, not T5b, not T5c,
  not T5d, and not `analyse_t5e.py`.
- **It did not use `T5c_RESULTS.md:15`'s real `G2a` triple**, which was available:
  that GCI is under AMENDMENT 1 of 2026-09-10 which withdraws it, and
  reconstructing it would be re-grading a withdrawn row.
- **It does not touch the physics question** of whether T5's and T5c's runs carry
  the divergence T5e measured on T5b's. That remains open and nothing is claimed.

## 7. COST

**Zero solver core-minutes.** The audit is single-core Python completing in wall
seconds; **it was not separately metered and no figure is presented for it** — an
approximation in a ledger is a number somebody later cites as measured.
