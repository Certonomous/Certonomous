# VMFL076-R2 — Forced Convection over a Flat Plate, Low-Prandtl: `GATE REACHED`

## VERDICT: `GATE REACHED` — both frozen gates met at the finest level, on a `CONVERGING` triple

VMFL076-R2 is the re-registration of VMFL076 (register **row #27**, `NOT A RESULT`) under
`ANSYS_VERIFICATION_CHARTER` §6. Row #27's physics met **both** frozen gates at its finest level
but was `NOT A RESULT` because CLAUDE.md **rule 5** turns a non-`CONVERGING` triple into
`NOT A RESULT` whatever the value. The **only** change for R2 is a **coarser** three-level family
(600 / 2 400 / 9 600 cells at endTime 2000 every level) chosen to sit inside the asymptotic
range; the gate scalars, both bands, the tier ceiling, the Sparrow & Gregg similarity reference,
the controls and the verdict path are carried **byte-identical** from the R1 comparator blob
(`git hash-object` of `grade_vmfl076.py` on disk == committed `42c8945544721e60a41fbe1a01513405b64d5f3c`).
Graded independently by `ansys-lane-opus48` (lane B), 2026-08-27.

### The numbers, exactly (frozen comparator `grade_vmfl076.py`, blob `42c89455`)

| level | cells | I_lab (m) | rel vs I_ref | max&#124;ΔΘ&#124; |
|---|---|---|---|---|
| L1 | 600 | 6.307703446455e-02 | +2.879004 % | 2.2904e-02 |
| L2 | 2 400 | 6.114355687567e-02 | −0.274509 % | 8.1364e-03 |
| L3 | 9 600 | 6.080627762560e-02 | **−0.824613 %** | **6.3258e-03** |

- Reference `I_ref = 6.131186321895e-02 m` from the Sparrow & Gregg similarity solution the lab
  derives and evaluates itself (`theta'(0) = 0.029370785745`), gate station x = 0.75 m, 201 fixed
  sample points.
- **Roache triple: `CONVERGING`, R = 0.174442, p_obs = 2.5192, GCI_fine = 1.4651e-03 (0.1465 %)**
  — monotone (I_lab falls 0.06308 → 0.06114 → 0.06081), so the triple is not gated to
  `NOT A RESULT` and the GCI is quotable. **This is the repair working:** R1's finer triple was
  non-`CONVERGING`; the coarser R2 family lands inside the asymptotic range.
- **GATE A** `|I_lab − I_ref| / I_ref = 0.824613 %` against the frozen **3.00 %** band — **met**.
- **GATE B** `max|ΔΘ| = 6.325785e-03` against the frozen **1.00e-02** band — **met**.
- **Tier ceiling `GATE REACHED`** (frozen; the comparator cannot print `PASS`). Both gates met on
  a `CONVERGING` triple ⇒ **`GATE REACHED`**.

### Controls fired (CLAUDE.md rule 3, rule 4)

The comparator's pre-read controls all fired before the real grade: the planted/mutation probes
refuse (exit 2) on dead series, short windows, an `rc = 1` record, an out-of-vocabulary verdict,
a too-short gate line and an off-grid sample y — the reader is shown able to refuse a non-answer,
so its `GATE REACHED` is evidence. `--selftest` 10/10 controls PASSED, exit 0. Strict completion
(rule 4) holds at all three levels: `RUN_RC.txt` rc = 0 each, an `End` line, last time ==
endTime 2000, fields present, age guard met.

### Cost

Total **0.6666 core-min** measured (L1 0.0333 + L2 0.1000 + L3 0.5333, wall 2 + 6 + 32 s × 1 rank
÷ 60), against the pre-registered **0.6 core-min** estimate — ratio **1.111×**. Per-level cap
10 core-min, family ceiling 30 — never bit. **$0.00057 derived** at $0.0513/core-h, derived not
measured (the box cannot read its own billing). No stall, no waste.

### Provenance

- Prereg freeze: **`8667be7257b6223a4d6b922998a374c768bedd87`** (2026-08-26T22:46:15Z; blob
  `65b8829aae070ef99c8b84b49be7682d89d41cbc`, disk == HEAD).
- Comparator: **`42c8945544721e60a41fbe1a01513405b64d5f3c`** (`grade_vmfl076.py`; disk == HEAD).
- Run artifacts: `verification/runs/ansys_verification/VMFL076-R2/` (L1, L2, L3; `RUN_RC.txt`
  rc = 0 each; `STATUS.VMFL076-R2`).
- Cites the superseded R1 row #27; R1's tree, prereg and comparator are preserved
  (VERIFICATION_CHARTER §6: a re-run is a new row citing the old one).

**GATE REACHED is a positive verdict but NOT a PASS credential** — only `PASS` rows are
credentials (charter §6). It is recorded honestly with its numbers.

### Charter / doc update line (Amendment 1.4 Clause C)

**NONE** — the R2 outcome confirms the R1 `RESULTS.md` §7 repair prediction (a coarser triple
inside the asymptotic range) exactly; no new numerics fact, lesson or charter change is
established that the record does not already carry.
