# A6 CRM wing-alone — adjoint feasibility: DECISION AND VERDICT

**2026-08-21, Lane A. Zero solver core-minutes were spent on the full-size question.** This file
records the decision taken against `PREREGISTRATION.md` in this directory. Nothing filed upstream.

---

## 1. Verdict row — full-size A6

| case | cells | arm | image | predicted | measured | verdict |
|---|---|---|---|---|---|---|
| A6 CRM wing-alone | **579,072** | adjoint (any objective, any DV) | — | peak RSS **95–116 GiB** vs a 30 GiB box | **not run, deliberately** | **BLOCKED (memory), and independently BLOCKED (conditioning)** |

**This verdict is recorded from prediction, not from an OOM, and that is the point.** The
pre-registration priced the demonstration run at ~$0.10 and recommended against it: it would have
driven host `MemAvailable` toward the 6 GB safety floor on a box Lane B is sharing, in order to
observe something two existing measurements already bracket. **The supervisor's decision is to leave
it unrun.**

### The four memory models, and the fifth that was rejected

Source data: `../../ADJOINT_MEMORY_ENVELOPE.json` option 5 (status **PARTIAL — cross-case envelope
only**; two of its five points censored at a container cap). A6 is `DARhoSimpleCFoam`, so the
compressible points govern.

| model | basis | rate | predicted peak at 579,072 cells |
|---|---|---|---|
| **M1** average rate, compressible uncensored | 18,421.76 MiB / 99,840 cells | 0.18451 MiB/cell | **104.3 GiB** |
| **M2** affine, 2,048 MiB fixed overhead | (18,421.76 − 2,048)/99,840 | 0.16400 MiB/cell marginal | **94.7 GiB** |
| **M3** average rate, censored upper variant | 20,480 / 99,840 | 0.20513 MiB/cell | **116.0 GiB** |
| **M4** affine on the censored upper variant | (20,480 − 2,048)/99,840 | 0.18462 MiB/cell marginal | **106.4 GiB** |
| M5 adjoint-state count (family-independent cross-check) | A6 = 579,072×6 + 1,770,408 faces = **5,244,840** states exactly; A3-coarse ≈ 899,040 ⇒ ratio 5.83 | — | **105.0 GiB** |
| ~~M6~~ naive small-case rate | 0.542–0.555 MiB/cell from the 4–5k-cell points | — | ~~307–314 GiB~~ **REJECTED** — folds fixed overhead into a per-cell rate; the envelope itself notes those two points give a nonphysical negative intercept |

**Five independent constructions land in a 94.7–116.0 GiB band.** M2 was validated against a point
it was not fitted on — A3 rung 3, 79,560 cells, measured peak **11.65 GiB**, against a model value
of 14.7 GiB — so the model **overpredicts by 1.27×**, the conservative direction. De-biasing the
full-size figure by that factor still leaves **74.6 GiB against a 30 GiB machine.**

### Two corroborations that need no extrapolation

1. A3's fine mesh **OOM'd at 399,360 cells at both a 12g and an 18g cap**, twice, at the same
   pipeline step. **A6 is 1.45× larger**, same solver family.
2. A3's coarse mesh needed **≥18.4–20.5 GiB at 99,840 cells** with every memory lever applied.
   **A6 is 5.80× larger.**

### The second, independent blocker

Even with unlimited memory, `DARhoSimpleCFoam` — **the same solver** — stagnates at **79,560 cells**
with memory comfortable (11.65 of 22 GiB), `PetscConvergedReason: -3` after a 1.31× residual
reduction over 4,000 iterations (`../../A3_RUNG3_N52_RESULT.md`). Full-size A6 is **7.3×** the
largest rung that converges and **7.28×** the rung that stagnates. **Memory is not the only blocker
and is arguably not the first one.**

## 2. Decision taken

**Option A6-2b is bought: one extra `cgns_utils coarsen` pass + pyHyp `N=16` → 41,760 cells, plus
the stock-vs-patched pair.** Options A6-2a (22,272 cells) and A6-2c (77,952 cells) are **not**
bought at this time; A6-1 (full size) is **not run**.

The rung is pre-registered at `../rung_n16_np1/PREREGISTRATION.md` and its results are at
`../rung_n16_np1/RESULTS.md`.

**A6-2c remains the only option on the original list that could return a surprise** — if CRM
converges at ~78k cells where ONERA M6 stagnates at ~79.5k, the "structural wall" that has been
projected from A3 onto A6 since 2026-07-28 is a property of the M6 case and not of the solver. It
is left costed and unbought (130 core-min, $0.111).

## 3. What this decision record cannot see

1. **The envelope is PARTIAL by its own status field**, with options 3 and 4 never run and two of
   its five points censored at a container cap. §1's validation against A3 rung 3 is the only
   out-of-sample check in existence.
2. **No CRM-specific memory point exists at any size** — every number in §1 is transferred from
   ONERA M6 and NACA0012/U-bend. **The 41,760-cell rung will produce the first one**, which is a
   further reason to prefer it over an argument.
3. **A prediction is not a measurement.** The BLOCKED verdict above is the strongest statement the
   evidence supports at zero risk to a shared box; it is not the same object as an observed OOM, and
   is labelled accordingly.

## 4. Ledger

| item | value |
|---|---|
| solver core-minutes spent on the full-size question | **0.00** |
| dollars | **$0.00** |
| containers started | 0 |
| frozen files edited | 0 |
| filed upstream | nothing |
