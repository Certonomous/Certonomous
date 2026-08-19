# Retiring the velocity-peak location rows, and the tag instability that retiring them exposed

Campaign F14, gate K0c. Written 2026-08-19. Zero compute, zero solver writes.
**No case was re-run and no measurement changed.**

---

## 1. The rows, and why they grade nothing

Charter §2c: **a graded row must separate the hypothesis from a registered
trivial baseline.** Four rows did not.

**K0cT / K0cX, tall cavity, W = 76 mm, band ±5 mm on the peak's location.** The
peak sits **4–6 mm from a wall**, so **the tolerance is as large as the
measurand.** Read off the meshes on disk rather than argued:

| band | admits | of the half-width |
| --- | --- | --- |
| hi-Ra downward, [0.0, 10.0] mm | **13 of 20 cells** (coarse), 21 of 32 (fine) | the wall itself is the lower edge |
| lo-Ra upward, [66.2, 76.2] mm | 13 of 20 (coarse) | **upper edge is OUTSIDE the 76.0 mm cavity** |

**All nine K0cT cases pass both rows** — three turbulence models, both Rayleigh
rungs, the adiabatic variant, the seed perturbation, the Rayleigh perturbation,
and **`C1_hi_c_laminar`, a laminar solution of a turbulent flow, at 68.765 /
7.235 mm.** Total spread across all nine is **3.46 mm against a 10 mm-wide
band.**

**K0cS, square cavity, row G9 (`Vpeak_X`).** Band ±0.005 m about a reference
0.00667 m from the wall — **75 % of the measurand.** `C1_laminar` deviates
0.00025 m and passes. All ten cases pass.
`scripts/check_row_discrimination.py` had already been reporting G9 as
**D1-HOLLOW-PASS on every arm.** **It was reported and not acted on; this
record acts on it.**

**K0cX** retired its equivalents (R3, R7, R9) earlier. **K0cR** already carried
`pass_carries_evidence: false` with `in_band_control: true` on its `Vpeak_X`
rows and needed no change.

---

## 2. Two mechanisms, deliberately different

**K0cT — moved out of the tally.** Its `graded_rows` is read by no comparator,
so the four rows were moved to `reported_never_graded`, values and bands intact.
**18 → 14 graded rows; the 14 survivors are field-for-field EQUAL and every one
keeps its verdict; FAIL stays at 8; the rung stays GATE FAIL.** The pass rate
**falls**, 10/18 to 6/14.

**K0cS — flagged in place.** Its `graded_rows` is a **published interface**:
`analyse_k0cg`, `analyse_k0cr` and `analyse_k0cp` each build their
reference-and-band dictionary from it, and **`analyse_k0cr` grades its own
`Vpeak_X` row against the entry found there.** Those three comparators are
**frozen and belong to rungs that have already reported.** Removing the row
would silently change what a frozen comparator reads; **adding a key cannot**,
because each copies the fields it names. G9 therefore stays where its consumers
look, carries `discriminating=False`, and is excluded from this rung's tally:
**20 rows preserved byte-identical apart from the new flag, 20 → 18 graded,
`kOmegaSST` 8 of 9 and `kEpsilon` 6 of 9.**

**Verified, not asserted: `gate_k0cr.json`, `gate_k0cp.json` and
`gate_k0cq.json` were regenerated after the change and are BYTE-IDENTICAL.**

---

## 3. The instrument defect the retirement exposed, which matters more

`scripts/check_row_discrimination.py` derived K0cT's row tags from their
**position** — `f"R{i}"` over `graded_rows`. **A positional tag is not an
identifier.** Removing four rows renumbered every row after them, and this was
checked rather than supposed:

| tag | before | after the naive retirement |
| --- | --- | --- |
| R11 | hi, peak upward velocity **(location)** | hi, mid-width temperature at y/H = 0.50 |
| R13 | hi, peak downward velocity **(location)** | hi, antisymmetry defect of the two peaks |

**Every historical citation of a K0cT row would have come to name a different
quantity, silently** — and the checker's own summary line would have kept
printing familiar tags for unfamiliar rows. **K0cS never had this exposure
because it tags its rows G1–G10 at creation.**

**Fixed at both ends.** `analyse_k0ct.py` now assigns `row = R{i}` **over the
full list, in build order, before the split**, which reproduces the original
numbering exactly and freezes it against every future retirement; and the
checker **prefers a row's own tag**, falling back to the positional form only
for a document that carries none. **All 18 original tags resolve and none
changed meaning.**

**The consequence for reading the record: K0cT-hi's two remaining hollow rows
are R15 and R17** — the mid-width temperature at y/H = 0.50 and the antisymmetry
defect. **Retiring the location rows did not fix K0cT's discrimination problem;
it revealed two more hollow rows underneath.** Those are physically meaningful
quantities with over-wide bands and want **re-banding, not retirement**. **NOT
DONE HERE**, and a defensible band needs the reference's own reported
uncertainty rather than a number chosen to fit.
