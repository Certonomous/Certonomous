# T9a-R1b (`W1b`) row R1 — COMPANION RECORD, 2026-09-03

**THE CELL `"verdict": "PASS"` IN `gate_t9aR1b.json` IS SUPERSEDED. THE ROW READS
`NOT A RESULT` ON ITS ROACHE LIMB.**

**Nothing in `gate_t9aR1b.json` is edited.** That file is a graded artifact
written by a frozen comparator on 2026-08-27T16:48Z; standing rule 6 is absolute
and a graded artifact is not rewritten to match a later ruling. This companion
record sits beside it in the same run directory so that the artifact and the
ruling that supersedes its verdict cell are read together.

Written by a heat-transfer lane on the heat-transfer supervisor's ruling,
2026-09-03. **No compute was run for it and no instrument was written**: it is a
record, not a comparator, and no grading script reads this file.

---

## 1. The artifact, named

| what | where |
|---|---|
| the graded artifact | `verification/runs/T-family/T9aR1b_runs/gate_t9aR1b.json` |
| the superseded cell | its top-level `"verdict"` key, whose value is `"PASS"` |
| the comparator stdout | `verification/runs/T-family/T9aR1b_runs/log.analyse_t9aR1b.20260827T164837Z.txt` |
| the registration | `verification/runs/T-family/T9aR1b_runs/T9aR1b_registered.json`, prose twin `docs/campaigns/T-family/T9aR1b_PREREGISTRATION.md` |
| the rung's results record | `docs/campaigns/T-family/T9aR1b_RESULTS.md` (amended the same day, §5 and §7 of that file) |

`gate_t9aR1b.json` also carries, in its own bytes and unaltered:

    "triple": { "state": "EXACT", "order": null,
                "e21": -2.8421709430404007e-13,
                "e32":  3.240074875066057e-12,
                "GCI_abs": null },
    "deviation_K": 2.8990143619012088e-12,
    "band_K": 1e-06

## 2. The ruling, quoted by its charter line

`docs/charters/VERIFICATION_CHARTER.md` **§2g**, landed as **Amendment v1.16,
2026-08-27** (`:2590`), ruled on this exact row. The ruling, verbatim at
**`VERIFICATION_CHARTER.md:2606-2607`**:

> **A pre-registration fixes the gate, threshold, cap and label FOR ITS CASE. It has no power to
> disapply a standing rule, and an exception to one is void however early it was frozen.**

and the remedy it prescribes, verbatim at **`VERIFICATION_CHARTER.md:2643-2647`**:

> - The row reads **`NOT A RESULT` on its Roache limb** — rule 5 unexcepted.
> - **The measurement is REPORTED beside it, not discarded**: 2.899e-12 K against a 1e-06 K floor,
>   the three levels' agreement, and the 900× improvement on the band it replaces. **D534 already
>   established `REPORTED` as a row class** for exactly this — a quantity the record carries and no
>   gate scores.

**The ground is `CLAUDE.md` standing rule 5's own last sentence** — *"The gate can
only turn a `PASS` or `GATE FAIL` **into** `NOT A RESULT`, never the reverse."*
Clause (2) of that rule names `EXACT` among the triple states that make a row
`NOT A RESULT` **whatever the value**. The pre-registered floor exception, frozen
at `3c39d08d` on 2026-08-26T21:18Z — **before** first compute at
2026-08-27T08:54:19Z, so **standing rule 2 is clean and is not in question** —
ran that gate backwards, and §2g refused it on that sentence.

**This record does not re-open the ruling and does not argue with it.** It
executes it.

## 3. The superseded cell, stated exactly

| limb | what the artifact says | what stands after §2g |
|---|---|---|
| **R1 Roache limb** (`T_i1`, grid triple c/m/f) | `"verdict": "PASS"` | **`NOT A RESULT`** |

**One cell moves and nothing else does.** §2g.3 is explicit that rule 5 *"refuses
to compute an ORDER from nothing. It does not say the VALUE is worthless."*
Accordingly:

- the **value** `T_i1` and its deviation are **unchanged and are reported below**;
- the **completion** finding is unchanged (three of three arms complete, rc 0);
- the **controls** are unchanged (`C_CONV`, `C_MAP`, `C_SCHEME`, `C_REF`, `C_PZ` —
  the planted-zero control passed at a demonstrated floor of 1e-07 K);
- the **`R0` `REPORTED` row** (`q_hot`) is unchanged; it was never a graded row
  (D534) and no gate ever scored it.

## 4. THE MEASUREMENT, PRESERVED BESIDE THE REFUSAL — a NOT A RESULT hides no measurement

**These numbers are read from `gate_t9aR1b.json` itself and are reported, not
discarded.** They carry no verdict and are scored by no gate.

| quantity | value | source key |
|---|---:|---|
| reference `T_i1` (derived, cross-checked against T9a) | **348.7810823988298 K** | `reference_T_i1` |
| solved `T_i1`, coarse (35 cells) | **348.7810823988299 K** | `values.c` |
| solved `T_i1`, medium (56 cells) | **348.78108239882664 K** | `values.m` |
| solved `T_i1`, fine (90 cells) | **348.7810823988269 K** | `values.f` |
| **deviation from the referent** | **2.899e-12 K** | `deviation_K` |
| **registered floor** | **1.000e-06 K** | `band_K` |
| level difference `e21` | −2.842e-13 K | `triple.e21` |
| level difference `e32` | +3.240e-12 K | `triple.e32` |
| observed order `p` | **null — refused, and correctly** | `triple.order` |
| GCI | **null — refused, and correctly** | `triple.GCI_abs` |

**The deviation is 2.899e-12 K against a registered floor of 1.000e-06 K — five
and a half orders of magnitude inside it.** The three levels agree to 12
significant figures across a 35 → 56 → 90 cell refinement.

**Why the order and the GCI are null, and why that is the instrument working
rather than failing.** `p = ln|e32/e21| / ln r` on two differences that are both
round-off is noise divided by noise (§2g.3). The comparator computed no order and
quoted no GCI. **Standing rule 5's own instruction — never quote a GCI when the
three values are not monotone — was obeyed by the frozen instrument.** The
refusal is not a defect in this run.

**The physical reason the triple is `EXACT`**, restated from the rung's own record
(`T9aR1b_RESULTS.md` §5): with the **harmonic** interface conductivity, the
discrete interface temperature in layered 1-D conduction is mesh-independent by
construction. **A grid-refinement study cannot show convergence in a quantity
that has nothing to converge from.** That is why §2g.3 diagnoses *"the wrong
instrument was registered"* rather than a bad answer.

## 5. What is therefore true of this rung, and what is not

**TRUE, and supported by the artifact:** on this case, at three refinement
levels, the harmonic-interface discrete `T_i1` reproduces its cross-checked
referent to 2.899e-12 K, and the three levels agree with one another to
round-off.

**NOT TRUE, and no reader may take it from here:** that T9a-R1b demonstrates
grid convergence, carries an observed order, or supports a GCI. It does not.
`T9aR1b_RESULTS.md` §9 already disclosed this in its own words —
*"this rung provides **no grid-convergence evidence**"* — and §2g makes the row
label match that disclosure.

**The remedy §2g names is a successor, not a re-grade.** §2g.3: *"The successor
registers a FLOOR DEMONSTRATION with its own gate … and that gate CAN `PASS`."*
That successor is `T9aR1c` (`docs/campaigns/T-family/T9aR1c_PREREGISTRATION.md`),
and `VERIFICATION_CHARTER.md:2800` records the ruling that **`PASS` is available
to T9a-R1c's floor limb** on §2g.3's express authority. **T9aR1c carries no
`*_RESULTS.md` at this writing** and therefore carries no rung verdict; nothing
in this record supplies one.

## 6. Scope of this record

- **No frozen file was edited** (standing rule 6). `gate_t9aR1b.json`,
  `analyse_t9aR1b.py`, `build_t9aR1b.py`, `mark_done_t9aR1b.py`,
  `run_one_t9aR1b.sh` and `T9aR1b_registered.json` are untouched.
- **No instrument was written and no sidecar was created that any comparator
  reads.** This file is prose; nothing parses it.
- **No compute was run.**
- **Nothing was sent, filed, uploaded, posted or registered outside this box**
  (standing rule 7).
- The two other paths a reader can take to this number carry the same correction:
  `docs/campaigns/T-family/T9aR1b_RESULTS.md` (amendment of 2026-09-03) and the
  `T9aR1b` row of `docs/campaigns/T-family/T_FAMILY_INDEX.md`.
