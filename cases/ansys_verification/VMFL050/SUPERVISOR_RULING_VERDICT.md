# VMFL050 — `PASS`, tier `GATE REACHED`, and the tier is capped by a clause frozen BEFORE the run

**Author:** `ansys-verification-supervisor`, personally, 2026-08-25.
**SUPERVISION_CHARTER §3 check 3** — a conclusion large enough to change this family's
direction (a new credential) gets my own code sweep and an independent diagnostic before it
is repeated upward. Zero compute: the run was already on disk.

**NOT FILED ANYWHERE** (CLAUDE.md rules 7, 8).

---

## How this was found

`VMFL050` was carried in `CASE_MAP.md` as **`NEVER RUN`**. It is not. All three levels have
run, all three carry `DONE.flag` and `RUN_RC.txt`, and
`verification/runs/ansys_verification/VMFL050/GRADING_VMFL050.json` holds a completed
grading with a verdict in it. **It was never entered in the register** — `grep -c VMFL050`
against `ANSYS_VALIDATION_REGISTER.md` returns **0**. A graded result that never reached the
register is compute this lab paid for and did not bank.

## The gate — met, and by a wide margin

Frozen band (§5 of the pre-registration): on the temperature **rise** (T − 293 K), at the
finest level, **both** probes, `|rise_lab − rise_manual| / |rise_manual| ≤ 0.01`.

| quantity | lab (L3) | manual | relative deviation on the rise | inside 1 % band |
|---|---|---|---|---|
| wall T | 392.9773033924 K | 393.0 K | **2.2697e-4** (0.0227 %) | yes |
| T at 150 mm | 318.401437549 K | 318.4 K | **5.6596e-5** (0.0057 %) | yes |

Against the **analytic** value rather than the manual's rounded print, the agreement is
better still: 393.02659961 K exact vs 392.97730339 lab, and 318.40595772 exact vs
318.40143755 lab.

**Ansys's own Fluent numbers (392.95 K, 318.41 K) are CONTEXT ONLY and are not the gate** —
the pre-registration says so at §4, and the reference is Incropera's closed-form solution.

## Every control is satisfied, and I checked each rather than trusting the summary

- **Strict completion (rule 4), per level:** `rc = 0` **evidenced on disk** in `RUN_RC.txt`;
  `n_exec` == `expect_steps` at all three levels (60/60, 120/120, 240/240); `endTime` 120.0
  reached; **age guard passed** — `T` newer than `0/T` at every level. This is the rung where
  the `rc` clause is actually evaluable, in contrast to `VMFL003_M2` where no launcher wrote
  an exit code at all.
- **Planted-zero (rule 3):** the comparator planted **1.234 K** into both gate quantities and
  read back a delta of **1.2339999999999804** off disk. **The reader was shown able to see a
  non-zero before its zeros were believed.**
- **Comparator freeze (rule 2):** the pre-registration names blob
  `22e7c758d117fe23c4b549bbc18512c73d6a2023` as the grading path, fixed at the freeze.
- **Rule 5 is implemented correctly in the comparator, and I read it as code, not as output.**
  `grade_vmfl050.py:336–339` gates on `tw["state"] == "CONVERGING" and tp["state"] ==
  "CONVERGING"` and assigns `NOT A RESULT` with the reason *"grid triple not CONVERGING …
  (rule 5)"* otherwise; the verdict is asserted into the fixed six-word vocabulary at line
  346. The gate can only turn a result **into** `NOT A RESULT`, which is the correct
  direction.

## THE VERDICT: `PASS`. Both triples are `CONVERGING` and both are monotone.

| | wall T | T at 150 mm |
|---|---|---|
| coarse → med → fine | 392.8632 → 392.9336 → 392.9773 | 318.4169 → 318.4018 → 318.4014 |
| monotone | yes (increasing) | yes (decreasing) |
| state | `CONVERGING` | `CONVERGING` |
| observed order p | **0.6883** | **5.5982** |
| GCI_fine (Fs = 1.25) | 2.2724e-4 | **2.5860e-08** |

## THE TIER IS `GATE REACHED`, NOT `HOLDS` — and this was frozen in advance

The pre-registration's **§9** declared the ceiling **before any number existed**:

> *"**HOLDS** is reachable … If the triple is `CONVERGING` but the observed order is
> untrustworthy (noise-floor), the ceiling drops to `GATE REACHED`, declared here as the
> fallback."*

**That fallback fires, and it fires on the `p150` triple.**

Space and time are refined **together at ratio 2** (§6), with `laplacianFoam` on an implicit
Euler time integration. Time is first-order, so the **combined formal order is ≈ 1**, and it
cannot exceed 2 under any reading. Measured:

- **`wallT`: p = 0.6883.** Slightly under 1 — entirely plausible for a first-order-dominated
  scheme that is not yet fully asymptotic. **Trustworthy.**
- **`p150`: p = 5.5982.** Roughly **5.6× the formal order.** This team's own
  `PREREG_TEMPLATE.md` line 10 requires that an observed order exceeding the formal order be
  declared **"SUSPICIOUSLY HIGH" — a warning, not a win.**

**The mechanism is visible in the differences and it is a noise floor, not superconvergence.**
`d21 = 3.125e-4` on a value of 318.4 — a relative separation of **9.8e-7**. The fine and
medium levels agree to seven significant figures, so the ratio `d32/d21` that produces `p` is
computed from a difference at the level of probe-interpolation and write-precision. The
resulting **`GCI_fine = 2.586e-08`, i.e. 2.6e-6 %**, is not a credible estimate of
discretisation error on a transient conduction solve; it is a fit to noise.

**The decisive evidence is internal disagreement.** The same case, the same three meshes, the
same refinement ratio, the same solve, yields **p = 0.688 for one quantity and p = 5.598 for
the other.** A genuinely asymptotic grid family does not do that. **At least one of these two
quantities is not in the asymptotic range**, and the one carrying the physically implausible
order is the one whose levels have collapsed to noise.

**So: `PASS` on the gate — a credential — with the tier honestly capped at `GATE REACHED`,
by the case's own frozen clause rather than by a caveat I invented after seeing the numbers.**
That distinction is the entire evidentiary content of pre-registration. Had §9 not been
frozen, capping the tier here would be indistinguishable from moving a goalpost, and banking
`HOLDS` would have been indistinguishable from flattery. **The register carries verdict and
tier side by side, and the tier never flatters the verdict.**

## What must NOT be concluded

**A GCI of 2.6e-6 % must never be quoted as this case's discretisation uncertainty.** It is a
noise-floor artefact. If a number is needed for an error budget, the `wallT` limb's
**2.27e-4** is the defensible one, and even that rests on p = 0.688 rather than a clean
asymptotic order.

## Actions

1. **Land the register row** — verdict `PASS`, tier `GATE REACHED`, with the numbers above,
   the prereg blob, cost and date. **Derive the credential count from the HEAD blob at append
   time; do not carry a remembered figure.** Only `PASS` rows are credentials, so this row
   moves both numerator and denominator.
2. **Correct `CASE_MAP.md`**, which carries VMFL050 as `NEVER RUN`. **By dated amendment,
   never an in-place edit.** A map that says never-run about a graded case sends the next lane
   to re-run compute this lab has already bought — which is precisely the waste Sanaa's
   throughput directive is aimed at.
3. **Land the calibration row** (rule 12): registered cap 8 core-min against the measured
   actual, with the ratio and its attribution.
