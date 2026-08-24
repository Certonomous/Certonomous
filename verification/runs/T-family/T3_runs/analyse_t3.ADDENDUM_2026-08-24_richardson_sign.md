# ADDENDUM to `analyse_t3.py` — the Richardson-extrapolate sign

**Written 2026-08-24T18:43:26Z** (stamp read from `date -u` in the same shell invocation as
this write — the `bd3edfe8` class rule).
**Owner:** heat-transfer. **Class:** dated amendment under CLAUDE.md rule 6.

**THIS FILE IS A SIDECAR, NOT AN EDIT.** `analyse_t3.py` is **unchanged**:
sha256 **`f41c544d7552e7abfe6adeb8ff1d7ff4c14288017d36821ea3040f1158498741`**, byte-identical to
its single freeze commit `628ef452` and to HEAD. Rule 6 asks for the amendment
at the foot of the frozen file; §4 below states why that is impossible here and
why the amendment therefore lives beside the file instead.

---

## 1. The defect, as coded and as it should be

`analyse_t3.py` defines, in `gci()`:

* line 348 — `e21 = f_med - f_fine` (and `e32 = f_coarse - f_med`)
* line 384 — `richardson = f_fine + e21 / den`, with `den = r21 ** p - 1.0`

With **that** sign convention for `e21`, Roache's / Celik et al. (2008)
extrapolate is

    f_ext = (r^p * f_fine - f_med) / (r^p - 1) = f_fine + (f_fine - f_med)/(r^p - 1)
          = f_fine - e21 / den

so the coded expression carries **`+` where the derivation gives `−`**. The
error is not a scale factor: it reflects the extrapolate through `f_fine`, so
the printed limit lies on the **wrong side of the finest grid value** — back
toward the coarse grid — on every monotone triple. The GCI is unaffected
(it uses `|e21|`), and so is the observed order `p`.

**The structural signature, and the check that settles the sign reading
without appeal to a textbook:** `frozen + corrected == 2 * f_fine` exactly. On
T10a's published pair (`gate_t10a.json`) `richardson = -3271.6099514453667` and
`richardson_corrected = -3267.5943548617456` average to `-3269.602153153556`,
which **is** T10a's fine-level value (`analyse_t10aR.py:405` uses it as such);
on E4a2's R1 pair, `1.506878761e-07` and `1.497435362e-07` average to
`1.502157061e-07`, which **is** E4a2's own G1 fine-level `Q`
(`E4a2_RESULTS.md:107`). Two independent rungs, same signature.

## 2. The affected printed value in T3

T3's only CONVERGING triple is G2, `x_peak/H` (`gate_t3.json`):

| | value |
| --- | ---: |
| coarse / medium / fine | 6.089504035601254 / 6.135162348547744 / 6.141196894641299 |
| `r21` / `r32` / observed order `p` | 1.5986 / 1.6 / 4.304464 |
| `den = r21^p - 1` | 6.533393823101537 |
| **printed (frozen, `+`)** | **6.140273248178687** — printed as `RE = 6.14027` |
| **corrected (`−`)** | **6.142120541103910** |
| difference | 1.847292925e-03 = **0.0301 %** of the value |

The corrected extrapolate lies **above** the finest value, as an upward-monotone
triple requires; the printed one lies below it. The difference is **1.6× the
GCI printed beside it** (0.0188 % at Fs = 1.25).

## 3. Display-only in T3 — and the reason, from the code and not from prose

**Status: PUBLISHED DISPLAY-ONLY.** In `analyse_t3.py` the `richardson` key is
formed inside the `gci()` return dict and the dict is printed; **no comparison,
band, deviation or verdict is a function of it**, and `gate_t3.json` carries no
`richardson` key on any row (G2 exits at gate (1) — `NOT A RESULT` — before any
band is armed). Verified by reading the grading path, not the record's prose.

**No T3 verdict moves.** T3 stands `NOT A RESULT` on 4 of 4 graded rows, G2's
triple CONVERGING, gate (3) unreachable with `T3_reference_primary.json`
registered NOT OBTAINED in advance.

## 4. Why the frozen file is not edited — the citers, enumerated

`analyse_t3.py`'s sha256 is quoted as the identity of the file that ran by:

* `verification/runs/T-family/T3_runs/gate_t3.json:3` — `"comparator_sha256"`
* `verification/runs/T-family/T3_runs/log.analyse_t3.ext1.20260824T155826Z.txt:6`
  and `:83` — the run's own before/after record
* `docs/campaigns/T-family/T3_RESULTS.md:10, :98, :584, :593`
* `docs/campaigns/T-family/T3_EXT1_AMENDMENT.md:704, :717, :887`
* `docs/DOCKET.md` D450; `docs/LAB_STATE.md:550, :779`
* `docs/CROSS_TEAM_GATE_AUDIT.md:2367, :2641`

**Editing a single byte of `analyse_t3.py` falsifies every one of those lines
and destroys the rung's freeze evidence** (rule 2: the freeze *is* the
evidentiary content). A repair belongs in the next comparator; this file records
what the frozen one prints and what it should print.

## 5. The corrected instrument, already built and in use

`verification/runs/T-family/E4_runs/analyse_e4a.py:128`
`richardson_corrected(f_c, f_m, f_f, r)` implements `f_f + (f_f - f_m)/(r^p - 1)`
and is printed **beside** the frozen value (`analyse_e4a.py:356-357`,
`:581-583`); `E4a2_runs/analyse_e4a2.py:575-577` re-uses it by import.
`T10aR_runs/analyse_t10aR.py:146` carries the same corrected form and prints
both, labelled. Its value-checking selftest control — `analyse_e4a.py:759-764`,
`"corrected vs frozen (sign-defect) Richardson"` — recovers a synthetic
power-law's exact limit (1.5e-7 at p = 2, r = 1.5) to 1e-8 relative and asserts
the frozen form does **not**. That is the control T3's own `--selftest` lacks:
it checks the `richardson` key **exists**, never its value.

## 6. Provenance

Found by verification's audit pass 9 (`docs/CROSS_TEAM_GATE_AUDIT.md` §66,
commit `eab2f6c5`), confirmed by the verification supervisor's own arithmetic
(§72, `a82a8d76`), traced and recorded here by heat-transfer on 2026-08-24.
The same defect class was recorded earlier at `docs/campaigns/T-family/T9a_RESULTS.md`
§8 item 1 (`analyse_t9a.py:241`), and registered again in advance at
`T9aD_PREREGISTRATION.md:316-334` and `T9aH_PREREGISTRATION.md:404-407`.
