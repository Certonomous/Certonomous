# A2 MACH tutorial wing — the 96-shape-DV per-component table: RESULTS

**2026-08-22, Lane C (Opus). ZERO COMPUTE: no container was started, no solver was run, no
`check_totals` was re-executed.** Every number below is read out of a log already on disk, at the
line number given, by a script whose path is in §1. Nothing filed, sent, uploaded or pushed. Filing
stays NOT APPROVED and is Sanaa's alone.

**No pre-registration, and the reason is the same one `../grading_confirmation/RESULTS.md` gives:
this item buys no compute.** There is no arm to register, no ceiling to commit to and no falsifier
that a launch could trip. What replaces a pre-registration here is an *integrity gate* stated before
any number was extracted (§2) and applied to every candidate copy, including the ones it rejected.

---

## HEADLINE — four findings, one of which changes a grade

1. **The table exists now, and it is not clean.** `CD` wrt `dvs.shape`, SHIPPED: aggregate
   **1.7138% PASS**, **zero sign flips**, but **79 of 96 components within 5%**, **89 within 15%**,
   and **7 components beyond 15%**, the worst reading **−360.75%** at **idx18**. `CL` wrt
   `dvs.shape`, SHIPPED: aggregate **1.1652%**, zero flips, **88/96 within 5%**, one component at
   **−80.20%** (idx15).
2. **The PATCHED toolchain has a SIGN FLIP that the record says does not exist.**
   `../grading_confirmation/RESULTS.md` §1 states: *"All six are ≤5% and **no component is flagged** —
   the record reports no sign flip anywhere in A2, at either toolchain."* **At `CD` wrt `dvs.shape`,
   idx46, the patched analytic is `+2.27367571e-06` against an FD of `−2.52460969e-06`.** That is a
   sign flip, it is on the *patched* image, and it is the A5-idx16 situation on a different case.
3. **The FD is bit-identical shipped vs patched, and this is now proved per component, not asserted.**
   `CL` wrt `shape`: **96 of 96 components bit-identical**. `CD` wrt `shape`: 31 of 96 survive the log
   damage bit-identical, and the remaining 65 are established indirectly and decisively — pairing the
   patched analytic with the *stock* FD reproduces the **patched log's own printed relative error to
   eight significant figures** (§4).
4. **A log-integrity defect nobody had noticed: most printed copies of these tables are silently
   corrupt.** OpenMDAO's `check_totals` under MPI prints each derivative block **once per rank**, and
   the four ranks interleave on one stdout, splicing arrays **mid-number**. Of the four printed copies
   of `CD wrt shape` in the published log, **one is usable**; of the four copies of `CL wrt shape`,
   **none is**. A naive extractor reading the first copy it finds gets numbers that are wrong and
   carry no error (§2.2).

---

## 1. What was extracted, from where, and with what

| item | value |
|---|---|
| extraction script | `/home/ubuntu/certonomous-runs/P3-a2-percomponent/extract_per_component.py` (parser + integrity classifier) |
| table builder | `/home/ubuntu/certonomous-runs/P3-a2-percomponent/build_tables.py` |
| full machine output | `/home/ubuntu/certonomous-runs/P3-a2-percomponent/tables.txt` (all three logs, all 96 rows each), `out_*.txt` (per-log census) |
| SHIPPED, published | `/home/ubuntu/certonomous-runs/A2-mach-wing/check_totals_run1.log` (2026-07-28) |
| SHIPPED, re-measured | `/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_stock_checktotals.log` (2026-08-02) |
| PATCHED (rotation fix on `PYTHONPATH`) | `/home/ubuntu/certonomous-runs/W4-a2-provenance/a2_ao_patched_checktotals.log` (2026-08-02) |
| case | 38,304 cells, `DARhoSimpleFoam`, np=4, `runScript_AeroOnly.py`, `check_totals` central FD `step=1e-3 step_calc=abs`, 105 DVs (96 shape + 7 twist + 2 patchV) |
| grading band | `../../A_stepsize_study.md:91-93` — PASS ≤5% with zero flagged components; CONDITIONAL 5–15%; **>15% or any flagged component → FAIL pending investigation** |

## 2. The integrity gate — stated before the numbers, and it rejected most of the data

### 2.1 The gate

A candidate `(Jfor, Jfd)` pair is **ACCEPTED** only if the norms **reconstructed from the extracted
components** reproduce, to the seven significant figures OpenMDAO prints, all three of that block's
own printed scalars:

```
‖Jfor‖ == Analytic Magnitude      ‖Jfd‖ == Fd Magnitude
‖Jfor − Jfd‖ / ‖Jfd‖ == Relative Error (Jan - Jfd) / Jfd
```

**This is a three-way check that a corrupted array cannot pass by accident**, and it is the only
reason the tables below can be trusted: the corruption in these logs is *silent*, produces
well-formed floating-point text, and is invisible to any check that does not recompute the norms.

### 2.2 What the gate found — the census

| log | row | printed copies | usable |
|---|---|---|---|
| published (shipped) | `CD` wrt `shape` | 4 (lines 49513, 50300, 52556, 52640) | **1** — line **50300** |
| published (shipped) | `CL` wrt `shape` | 4 (lines 49751, 50393, 52733, 52819) | **0** |
| re-measured (shipped) | `CD` wrt `shape` | 4 (51691, 51775, 52179, 52835) | **2** — lines **51775**, **52835**, mutually identical |
| re-measured (shipped) | `CL` wrt `shape` | 4 (51868, 52102, 52498, 52928) | **1** — line **52928** |
| patched | `CD` wrt `shape` | 4 (51895, 52291, 52539, 52665) | **0** (all four have a damaged FD column) |
| patched | `CL` wrt `shape` | 4 (52214, 52462, 52800, 52886) | **1** — line **52886** |

**Two examples of what the gate caught, both of which would have been reported as fact by a
`grep`-based extractor:**

* Published log, `CD wrt shape`, copy at line **52640**: 96 well-formed values in each column, no
  parse error. Reconstructed `‖Jfd‖` = **3.47614670e+03** against a printed `Fd Magnitude` of
  **4.858158e-02**. One component, idx31, reads `3476.1467` where the intact copy reads
  `3.54761467e-04` — a rank's output spliced into the exponent field.
* Published log, `CL wrt shape`, copy at line **52819**: again 96 clean-looking values per column;
  reconstructed relative error **1.64039614e-02** against the printed **1.1651630e-02**. A 41% error
  in the headline number, from a file that looks perfectly ordinary.

**The corruption has structure.** In both the stock and the patched log, the `CD wrt shape` FD array
is severed at **exactly the same place** — immediately after component **30**, `3.05777580e-04` —
which is a stdout write-boundary effect, not a numerical one.

**Consequence for the lab, not for this item:** `../grading_confirmation/RESULTS.md` §5.4 recorded
that *"the `Raw Analytic Derivative (Jfor)` / `Raw FD Derivative (Jfd)` rows needed to do it **are**
present in the logs"*. That is **true but incomplete**: they are present, and **most printed copies
of them are corrupt**. The follow-up was free, as §5.4 said; it was not as simple as §5.4 implied.

## 3. `CD` wrt `dvs.shape` — the 96-component table

**Both shipped columns are the same numbers.** The published 2026-07-28 run and the re-measured
2026-08-02 run agree **on every one of the 96 analytic components and every one of the 96 FD
components, to every printed digit**. `../grading_confirmation/RESULTS.md` §2's *"18 of 18 rows
identical to every printed digit"* now holds **at component level**, which is a materially stronger
statement than agreement of six norms.

| | SHIPPED | PATCHED |
|---|---|---|
| aggregate `‖Jan−Jfd‖/‖Jfd‖` (printed, and reconstructed) | **1.7138%** (`1.7137910e-02` / `1.71379136e-02`) | **0.0506%** (`5.0591140e-04` / `5.05911495e-04`) |
| `‖Jan‖` | `4.8016250e-02` | `4.8569680e-02` |
| `‖Jfd‖` | `4.858158e-02` | `4.858158e-02` — **identical** |
| **sign flips** | **0 of 96** | **1 of 96 — idx46** |
| within 5% | **79 / 96** | **95 / 96** |
| within 15% | **89 / 96** | **95 / 96** |
| **beyond 15%** | **7** — idx18, 46, 17, 19, 39, 20, 16 | **1** — idx46 |
| **max component** | **idx18, −360.75%** (`−1.03225641e-04` vs `−2.24038028e-05`) | **idx46, +190.06%** (`+2.27367571e-06` vs `−2.52460969e-06`) |

### 3.1 Every component outside ±5%, SHIPPED — with its weight

`|Jfd|/max|Jfd|` is the component's share of the largest FD entry; it is printed because **every
out-of-band component is a small one**, and that is the whole reason a 1.71% aggregate could hide them.

| idx | `Jan` | `Jfd` | rel. err | \|Jfd\|/max |
|---|---|---|---|---|
| **18** | `−1.03225641e-04` | `−2.24038028e-05` | **−360.75%** | 0.0016 |
| **46** | `−1.07582947e-05` | `−2.52460969e-06` | **−326.14%** | 0.0002 |
| **17** | `+3.39261625e-05` | `+1.22838538e-04` | **−72.38%** | 0.0085 |
| **19** | `+3.46833017e-05` | `+1.18329562e-04` | **−70.69%** | 0.0082 |
| **39** | `−9.23682642e-05` | `−7.58402828e-05` | **−21.79%** | 0.0053 |
| **20** | `+3.90667665e-04` | `+4.74106076e-04` | **−17.60%** | 0.0329 |
| **16** | `+4.04840645e-04` | `+4.79549681e-04` | **−15.58%** | 0.0333 |
| 29 | `−1.55967844e-04` | `−1.80662697e-04` | +13.67% | 0.0126 |
| 24 | `−5.10666470e-04` | `−5.71548378e-04` | +10.65% | 0.0397 |
| 38 | `−2.76182603e-04` | `−2.52827326e-04` | −9.24% | 0.0176 |
| 21 | `+7.21026962e-04` | `+7.91265408e-04` | −8.88% | 0.0550 |
| 25 | `−1.15005818e-03` | `−1.23548124e-03` | +6.91% | 0.0858 |
| 47 | `+1.65542610e-04` | `+1.77187120e-04` | −6.57% | 0.0123 |
| 28 | `−7.28341688e-04` | `−7.77367694e-04` | +6.31% | 0.0540 |
| 37 | `−4.65986783e-04` | `−4.39992213e-04` | −5.91% | 0.0306 |
| 26 | `−1.28574885e-03` | `−1.36372164e-03` | +5.72% | 0.0948 |
| 27 | `−1.20787748e-03` | `−1.27757111e-03` | +5.46% | 0.0888 |

**All seventeen out-of-band components lie in `idx 16–47`**, and **none** lies in `idx 0–15` or
`idx 48–95`. The largest FD entry in the out-of-band set is 9.5% of the vector's largest entry, and
the two worst are 0.16% and 0.02% of it. **The error is concentrated in the low-sensitivity block of
the design vector.** This is an observation about *where*, not a mechanism; naming the mechanism would
require the FFD index map, which this zero-compute item did not open.

### 3.2 The patched sign flip at idx46, stated plainly

```
idx 46   Jfd (shared)  −2.52460969e-06
         Jan SHIPPED   −1.07582947e-05     rel −326.14%   (right sign, 4.3× too large)
         Jan PATCHED   +2.27367571e-06     rel +190.06%   SIGN FLIP
```

**The patch fixes the magnitude and breaks the sign.** Shipped is 4.3× too large but points the right
way; patched is the right size and points the wrong way. This component carries **0.02% of the FD
vector's largest entry**, which is why it is invisible in a 0.0506% aggregate and why it was never
seen.

**It is the third instance of the same pattern in this lab**: A1's `idx6` (640.37% and flipped,
shipped), A5's `idx16`, and now A2's `idx46` — **a near-zero component whose sign the toolchain does
not resolve**, hidden inside a passing vector norm. **This one is on the PATCHED image**, so it is not
the rotation defect being cured; whatever it is survives the rotation fix, exactly as A1's idx6 did at
1.19% and A5's idx16 did at 0.90%.

**What it is not.** It is **not** established that this is a defect rather than a reference problem.
The A5 precedent (`../../W4_IDX16_IS_THE_REFERENCE.md`) found that at idx16 it was `check_totals`' own
FD that was unreproducible, not the adjoint. **Settling idx46 the same way requires a step-size sweep
at that component, which is compute this item did not buy.** It is reported as an open flag, not as a
defect.

### 3.3 The full 96-component table

SHIPPED analytic and the shared FD from `a2_ao_stock_checktotals.log:51775` (bit-identical to
the published `check_totals_run1.log:50300`); PATCHED analytic from
`a2_ao_patched_checktotals.log:51895`. Bold marks |rel. err| > 15%.

| idx | `Jfd` (shared) | `Jan` SHIPPED | rel. SHIPPED | `Jan` PATCHED | rel. PATCHED | \|Jfd\|/max |
|---|---|---|---|---|---|---|
| 0 | `+3.14578661e-03` | `+3.04674517e-03` | -3.15% | `+3.14693101e-03` | +0.04% | 0.2186 |
| 1 | `+5.36661742e-03` | `+5.26634114e-03` | -1.87% | `+5.36530282e-03` | -0.02% | 0.3729 |
| 2 | `+5.64859026e-03` | `+5.57319668e-03` | -1.33% | `+5.63655929e-03` | -0.21% | 0.3925 |
| 3 | `+5.75527067e-03` | `+5.71841471e-03` | -0.64% | `+5.74993675e-03` | -0.09% | 0.3999 |
| 4 | `+5.00851446e-03` | `+5.01066168e-03` | +0.04% | `+5.00696121e-03` | -0.03% | 0.3480 |
| 5 | `+3.77012612e-03` | `+3.79163381e-03` | +0.57% | `+3.76199492e-03` | -0.22% | 0.2620 |
| 6 | `+2.72047696e-03` | `+2.75587583e-03` | +1.30% | `+2.71468479e-03` | -0.21% | 0.1890 |
| 7 | `+1.09718464e-03` | `+1.11632636e-03` | +1.74% | `+1.09708831e-03` | -0.01% | 0.0762 |
| 8 | `+4.07136970e-03` | `+4.18434822e-03` | +2.77% | `+4.07224056e-03` | +0.02% | 0.2829 |
| 9 | `+5.93760703e-03` | `+6.06041954e-03` | +2.07% | `+5.93820466e-03` | +0.01% | 0.4125 |
| 10 | `+5.67234082e-03` | `+5.77283367e-03` | +1.77% | `+5.66783699e-03` | -0.08% | 0.3941 |
| 11 | `+5.44426602e-03` | `+5.54680901e-03` | +1.88% | `+5.44276869e-03` | -0.03% | 0.3783 |
| 12 | `+4.61287791e-03` | `+4.71285891e-03` | +2.17% | `+4.61157359e-03` | -0.03% | 0.3205 |
| 13 | `+3.49216354e-03` | `+3.57417930e-03` | +2.35% | `+3.48676201e-03` | -0.15% | 0.2426 |
| 14 | `+2.60515175e-03` | `+2.66408393e-03` | +2.26% | `+2.60112947e-03` | -0.15% | 0.1810 |
| 15 | `+1.11923899e-03` | `+1.13579619e-03` | +1.48% | `+1.11914253e-03` | -0.01% | 0.0778 |
| 16 | `+4.79549681e-04` | `+4.04840645e-04` | **-15.58%** | `+4.78869011e-04` | -0.14% | 0.0333 |
| 17 | `+1.22838538e-04` | `+3.39261625e-05` | **-72.38%** | `+1.19795642e-04` | -2.48% | 0.0085 |
| 18 | `-2.24038028e-05` | `-1.03225641e-04` | **-360.75%** | `-2.16809445e-05` | +3.23% | 0.0016 |
| 19 | `+1.18329562e-04` | `+3.46833017e-05` | **-70.69%** | `+1.19319529e-04` | +0.84% | 0.0082 |
| 20 | `+4.74106076e-04` | `+3.90667665e-04` | **-17.60%** | `+4.74502228e-04` | +0.08% | 0.0329 |
| 21 | `+7.91265408e-04` | `+7.21026962e-04` | -8.88% | `+7.90603088e-04` | -0.08% | 0.0550 |
| 22 | `+9.89638485e-04` | `+9.42317928e-04` | -4.78% | `+9.88909107e-04` | -0.07% | 0.0688 |
| 23 | `+5.39577904e-04` | `+5.21235285e-04` | -3.40% | `+5.39394497e-04` | -0.03% | 0.0375 |
| 24 | `-5.71548378e-04` | `-5.10666470e-04` | +10.65% | `-5.72799574e-04` | -0.22% | 0.0397 |
| 25 | `-1.23548124e-03` | `-1.15005818e-03` | +6.91% | `-1.24174634e-03` | -0.51% | 0.0858 |
| 26 | `-1.36372164e-03` | `-1.28574885e-03` | +5.72% | `-1.36494577e-03` | -0.09% | 0.0948 |
| 27 | `-1.27757111e-03` | `-1.20787748e-03` | +5.46% | `-1.27634325e-03` | +0.10% | 0.0888 |
| 28 | `-7.77367694e-04` | `-7.28341688e-04` | +6.31% | `-7.74801248e-04` | +0.33% | 0.0540 |
| 29 | `-1.80662697e-04` | `-1.55967844e-04` | +13.67% | `-1.79166261e-04` | +0.83% | 0.0126 |
| 30 | `+3.05777580e-04` | `+3.12151983e-04` | +2.08% | `+3.06534684e-04` | +0.25% | 0.0212 |
| 31 | `+3.54761467e-04` | `+3.45355308e-04` | -2.65% | `+3.54615975e-04` | -0.04% | 0.0246 |
| 32 | `-5.26800099e-04` | `-5.38188209e-04` | -2.16% | `-5.26398329e-04` | +0.08% | 0.0366 |
| 33 | `-8.27598467e-04` | `-8.40634657e-04` | -1.58% | `-8.28125216e-04` | -0.06% | 0.0575 |
| 34 | `-8.40495450e-04` | `-8.55958674e-04` | -1.84% | `-8.39969990e-04` | +0.06% | 0.0584 |
| 35 | `-8.29737242e-04` | `-8.50179091e-04` | -2.46% | `-8.28757362e-04` | +0.12% | 0.0577 |
| 36 | `-6.66297778e-04` | `-6.93228703e-04` | -4.04% | `-6.67277673e-04` | -0.15% | 0.0463 |
| 37 | `-4.39992213e-04` | `-4.65986783e-04` | -5.91% | `-4.38304159e-04` | +0.38% | 0.0306 |
| 38 | `-2.52827326e-04` | `-2.76182603e-04` | -9.24% | `-2.50689754e-04` | +0.85% | 0.0176 |
| 39 | `-7.58402828e-05` | `-9.23682642e-05` | **-21.79%** | `-7.58151998e-05` | +0.03% | 0.0053 |
| 40 | `+4.95797338e-04` | `+4.94902780e-04` | -0.18% | `+4.96835129e-04` | +0.21% | 0.0344 |
| 41 | `+3.26027806e-04` | `+3.27960326e-04` | +0.59% | `+3.24305664e-04` | -0.53% | 0.0227 |
| 42 | `+1.00062227e-05` | `+1.01012573e-05` | +0.95% | `+9.75170498e-06` | -2.54% | 0.0007 |
| 43 | `-1.96607349e-04` | `-1.97391230e-04` | -0.40% | `-1.94303140e-04` | +1.17% | 0.0137 |
| 44 | `-2.77271253e-04` | `-2.83397886e-04` | -2.21% | `-2.75722369e-04` | +0.56% | 0.0193 |
| 45 | `-1.97144256e-04` | `-2.04881451e-04` | -3.92% | `-1.93050077e-04` | +2.08% | 0.0137 |
| 46 | `-2.52460969e-06` | `-1.07582947e-05` | **-326.14%** | `+2.27367571e-06` | +190.06% **FLIP** | 0.0002 |
| 47 | `+1.77187120e-04` | `+1.65542610e-04` | -6.57% | `+1.77462391e-04` | +0.16% | 0.0123 |
| 48 | `+2.43087924e-03` | `+2.42422778e-03` | -0.27% | `+2.43132948e-03` | +0.02% | 0.1689 |
| 49 | `+2.89679218e-03` | `+2.88276936e-03` | -0.48% | `+2.89752639e-03` | +0.03% | 0.2013 |
| 50 | `+2.45170278e-03` | `+2.43334201e-03` | -0.75% | `+2.45190656e-03` | +0.01% | 0.1703 |
| 51 | `+2.29596130e-03` | `+2.27079836e-03` | -1.10% | `+2.29434677e-03` | -0.07% | 0.1595 |
| 52 | `+2.14775630e-03` | `+2.12256285e-03` | -1.17% | `+2.14677561e-03` | -0.05% | 0.1492 |
| 53 | `+2.00413041e-03` | `+1.98677897e-03` | -0.87% | `+2.00587420e-03` | +0.09% | 0.1392 |
| 54 | `+2.02693817e-03` | `+2.01857714e-03` | -0.41% | `+2.02801965e-03` | +0.05% | 0.1408 |
| 55 | `+1.26680641e-03` | `+1.26099855e-03` | -0.46% | `+1.26670114e-03` | -0.01% | 0.0880 |
| 56 | `+3.51514766e-03` | `+3.48896423e-03` | -0.74% | `+3.51463985e-03` | -0.01% | 0.2442 |
| 57 | `+4.10260390e-03` | `+4.06049153e-03` | -1.03% | `+4.10317733e-03` | +0.01% | 0.2851 |
| 58 | `+3.46538871e-03` | `+3.42093246e-03` | -1.28% | `+3.46634204e-03` | +0.03% | 0.2408 |
| 59 | `+3.23097538e-03` | `+3.18018631e-03` | -1.57% | `+3.22942012e-03` | -0.05% | 0.2245 |
| 60 | `+2.95749704e-03` | `+2.90896085e-03` | -1.64% | `+2.95527723e-03` | -0.08% | 0.2055 |
| 61 | `+2.69886076e-03` | `+2.66622773e-03` | -1.21% | `+2.70224352e-03` | +0.13% | 0.1875 |
| 62 | `+2.69308360e-03` | `+2.67377696e-03` | -0.72% | `+2.69512481e-03` | +0.08% | 0.1871 |
| 63 | `+1.72972526e-03` | `+1.72022337e-03` | -0.55% | `+1.72990584e-03` | +0.01% | 0.1202 |
| 64 | `+4.97357127e-03` | `+4.90780783e-03` | -1.32% | `+4.97235818e-03` | -0.02% | 0.3456 |
| 65 | `+5.06099678e-03` | `+4.93669496e-03` | -2.46% | `+5.05988356e-03` | -0.02% | 0.3516 |
| 66 | `+3.97403231e-03` | `+3.83234967e-03` | -3.57% | `+3.97308567e-03` | -0.02% | 0.2761 |
| 67 | `+3.43702294e-03` | `+3.28664511e-03` | -4.38% | `+3.43591098e-03` | -0.03% | 0.2388 |
| 68 | `+2.88035055e-03` | `+2.75287723e-03` | -4.43% | `+2.88116164e-03` | +0.03% | 0.2001 |
| 69 | `+2.32734543e-03` | `+2.24055293e-03` | -3.73% | `+2.32807589e-03` | +0.03% | 0.1617 |
| 70 | `+1.98848827e-03` | `+1.94031981e-03` | -2.42% | `+1.98838460e-03` | -0.01% | 0.1382 |
| 71 | `+1.12978281e-03` | `+1.11543969e-03` | -1.27% | `+1.12953791e-03` | -0.02% | 0.0785 |
| 72 | `+5.79513528e-03` | `+5.71655765e-03` | -1.36% | `+5.79435743e-03` | -0.01% | 0.4027 |
| 73 | `+5.82124417e-03` | `+5.67508121e-03` | -2.51% | `+5.82097076e-03` | -0.00% | 0.4045 |
| 74 | `+4.56132195e-03` | `+4.39436692e-03` | -3.66% | `+4.56004346e-03` | -0.03% | 0.3169 |
| 75 | `+3.99725855e-03` | `+3.81799522e-03` | -4.48% | `+3.99386167e-03` | -0.08% | 0.2777 |
| 76 | `+3.44687916e-03` | `+3.29445783e-03` | -4.42% | `+3.44638644e-03` | -0.01% | 0.2395 |
| 77 | `+2.87680933e-03` | `+2.77252844e-03` | -3.62% | `+2.87663484e-03` | -0.01% | 0.1999 |
| 78 | `+2.56665920e-03` | `+2.50930184e-03` | -2.23% | `+2.56607815e-03` | -0.02% | 0.1783 |
| 79 | `+1.53702016e-03` | `+1.52147470e-03` | -1.01% | `+1.53700099e-03` | -0.00% | 0.1068 |
| 80 | `-1.26227658e-02` | `-1.25242650e-02` | +0.78% | `-1.26194305e-02` | +0.03% | 0.8770 |
| 81 | `-1.43924854e-02` | `-1.42073670e-02` | +1.29% | `-1.43883745e-02` | +0.03% | 1.0000 |
| 82 | `-1.22416878e-02` | `-1.20375963e-02` | +1.67% | `-1.22389413e-02` | +0.02% | 0.8506 |
| 83 | `-1.14191872e-02` | `-1.12071018e-02` | +1.86% | `-1.14172288e-02` | +0.02% | 0.7934 |
| 84 | `-1.03254248e-02` | `-1.01468943e-02` | +1.73% | `-1.03240074e-02` | +0.01% | 0.7174 |
| 85 | `-8.95985202e-03` | `-8.83897364e-03` | +1.35% | `-8.95939273e-03` | +0.01% | 0.6225 |
| 86 | `-8.20038427e-03` | `-8.13460126e-03` | +0.80% | `-8.20001169e-03` | +0.00% | 0.5698 |
| 87 | `-4.48256037e-03` | `-4.47125394e-03` | +0.25% | `-4.48209414e-03` | +0.01% | 0.3115 |
| 88 | `-1.13158171e-02` | `-1.12353751e-02` | +0.71% | `-1.13131876e-02` | +0.02% | 0.7862 |
| 89 | `-1.31595164e-02` | `-1.30115680e-02` | +1.12% | `-1.31557993e-02` | +0.03% | 0.9143 |
| 90 | `-1.12873802e-02` | `-1.11261955e-02` | +1.43% | `-1.12849902e-02` | +0.02% | 0.7843 |
| 91 | `-1.05597130e-02` | `-1.03912860e-02` | +1.59% | `-1.05579031e-02` | +0.02% | 0.7337 |
| 92 | `-9.52047733e-03` | `-9.37668085e-03` | +1.51% | `-9.51917871e-03` | +0.01% | 0.6615 |
| 93 | `-8.23491365e-03` | `-8.13535570e-03` | +1.21% | `-8.23444543e-03` | +0.01% | 0.5722 |
| 94 | `-7.52190494e-03` | `-7.46563136e-03` | +0.75% | `-7.52156006e-03` | +0.00% | 0.5226 |
| 95 | `-4.11877150e-03` | `-4.10831810e-03` | +0.25% | `-4.11819051e-03` | +0.01% | 0.2862 |

## 4. `CL` wrt `dvs.shape` — 96 components, and the cleaner half of the story

| | SHIPPED | PATCHED |
|---|---|---|
| aggregate (printed / reconstructed) | **1.1652%** (`1.1651630e-02` / `1.16516310e-02`) | **0.0219%** (`2.1894730e-04` / `2.18947333e-04`) |
| `‖Jan‖` | `8.4805820e-01` | `8.5731700e-01` |
| `‖Jfd‖` | `8.5729920e-01` | `8.5729920e-01` — **identical** |
| **sign flips** | **0 of 96** | **0 of 96** |
| within 5% | **88 / 96** | **96 / 96** |
| within 15% | **95 / 96** | **96 / 96** |
| beyond 15% | **1** — idx15 | **0** |
| **max component** | **idx15, −80.20%** | **idx15, +1.25%** |

Every component outside ±5% on the shipped image, with the patched value beside it:

| idx | `Jfd` (shared) | `Jan` SHIPPED | rel. SHIPPED | `Jan` PATCHED | rel. PATCHED | \|Jfd\|/max |
|---|---|---|---|---|---|---|
| **15** | `+1.63807924e-04` | `+3.24306774e-05` | **−80.20%** | `+1.65848968e-04` | +1.25% | 0.0006 |
| 7 | `−6.58230722e-04` | `−7.47988707e-04` | −13.64% | `−6.55871984e-04` | +0.36% | 0.0025 |
| 11 | `−1.03429090e-02` | `−1.10791978e-02` | −7.12% | `−1.03528593e-02` | −0.10% | 0.0391 |
| 14 | `−3.08498437e-03` | `−3.30242141e-03` | −7.05% | `−3.08129771e-03` | +0.12% | 0.0117 |
| 10 | `−1.19478301e-02` | `−1.27629803e-02` | −6.82% | `−1.18965091e-02` | +0.43% | 0.0452 |
| 12 | `−8.04502756e-03` | `−8.56434422e-03` | −6.46% | `−8.06810683e-03` | −0.29% | 0.0304 |
| 9 | `−1.37771974e-02` | `−1.46418767e-02` | −6.28% | `−1.37425499e-02` | +0.25% | 0.0521 |
| 13 | `−5.68513120e-03` | `−6.00761517e-03` | −5.67% | `−5.69202119e-03` | −0.12% | 0.0215 |

**`CL` wrt `shape` is the row where the patch does what the record says it does, and does it
per component**: 8 components out of band shipped, **zero** patched, worst case improved from
−80.20% to +1.25%, no flip on either image. **The 53.2× aggregate improvement recorded in
`../grading_confirmation/RESULTS.md` §3 is not an average over a mixed picture — it is uniform.**
The one asymmetry worth naming: the patched analytic moved **toward the pre-existing, unchanged FD on
every one of the eight**, which is the direction a genuine fix must move and a comparison-rigging
artifact could not (the same argument A1's re-verification made on its eight components).

## 5. FD bit-identity, shipped vs patched — proved per component

The patch is derivative-only: `vectorUtils.f90` is unchanged and `warpMesh` output is md5-identical
patched vs unpatched (`../../patched_build/idwarp_rot/BUILD.md` §3). The primal, and therefore every
finite difference, must be **unmoved**. That is the control which makes the whole comparison readable,
and it has until now been asserted from six printed norms. Per component:

| row | direct bit-identical components | how the rest are established |
|---|---|---|
| `CL` wrt `shape` | **96 / 96** — every component of `a2_ao_patched_checktotals.log:52886` equals `a2_ao_stock_checktotals.log:52928` exactly | nothing left to establish |
| `CD` wrt `shape` | **31 / 96** — the patched FD array is severed after component 30 in **all four** printed copies (§2.2) | **indirectly and decisively:** pairing the patched **analytic** (96 components, norm-verified against its own printed `Analytic Magnitude`) with the **stock** FD reproduces the patched log's own printed `Relative Error` as **`5.05911495e-04` against the printed `5.0591140e-04`** — agreement to **8 significant figures**. Had any one of the 65 unrecovered FD components differed, that norm could not land on the printed value |
| both rows | printed `Fd Magnitude` | `4.858158e-02` and `8.5729920e-01`, **identical on both images**, in the logs' own headers |

**Verdict on the control: the FD did not move. Confirmed per component where the logs permit, and
confirmed by norm reconstruction where they do not.** The `CD wrt shape` per-component table in §3.3
therefore uses the stock FD column for both images, and says so in its caption rather than presenting
a reconstruction as a reading.

## 6. Does anything flag? — the question the brief asked, answered both ways

**The lab's own definition of "flagged" cannot be evaluated on this data, and that must be said
first.** `../../A_stepsize_study.md:86-87` defines a flagged component as one *"whose FD value
changes sign or moves by >50% of its own magnitude **across one decade of step**"*. **A2 was measured
at one step, `1e-3`, and at one step only.** There is no second decade in any A2 log. **The literal
flagging test is unavailable here, and no amount of re-reading these logs will make it available.**

What *is* available is the operational reading the lab has actually used — `../../A1/reverify_patched_idwarp_np1/RESULTS.md`
§2 grades *"a sign flip is a flagged component"* — and under that reading the answer is yes:

| row | image | flip? | reading under `A_stepsize_study.md:91-93` |
|---|---|---|---|
| `CD` wrt `shape` | SHIPPED | none | aggregate 1.7138% ⇒ **PASS on the aggregate**, with 7 of 96 components beyond 15% |
| `CD` wrt `shape` | **PATCHED** | **YES, idx46** | aggregate 0.0506%, but **"any flagged component → FAIL pending investigation, regardless of the aggregate percentage"** |
| `CL` wrt `shape` | SHIPPED | none | 1.1652% ⇒ **PASS**, with 1 of 96 beyond 15% |
| `CL` wrt `shape` | PATCHED | none | 0.0219%, 96/96 within 5% ⇒ **PASS, unqualified** |

**The recommendation, and it follows the A5 precedent rather than inventing one.** A5's `idx16` was
the identical shape of problem — one out-of-band component inside a passing aggregate — and
`../../A5/reverify_patched_idwarp_np1/RESULTS.md` graded it **"PASS on the aggregate band, with the
per-component caveat in §5"** rather than converting it to a FAIL, precisely because the follow-up
work showed the *reference*, not the adjoint, was the doubtful side. **The same disposition is
recommended here:**

> **A2 `CD` wrt `shape`, PATCHED: PASS on the aggregate band (0.0506%), with a per-component caveat —
> one sign flip at idx46, on a component carrying 0.02% of the FD vector's largest entry, cause
> unestablished.**

**and the aggregate PASS in `../grading_confirmation/RESULTS.md` §3 should carry that caveat rather
than the sentence it currently carries.** The sentence *"no component is flagged — the record reports
no sign flip anywhere in A2, at either toolchain"* (§1) is **factually falsified by this extraction**
and is the specific line that needs amending. **This item does not edit that file** — it is not this
lane's to edit — and the correction is stated here for the supervisor's desk.

**What would settle it, and what it costs.** A step-size mini-sweep at `step ∈ {3e-4, 1e-3, 3e-3}`
restricted to `of=CD, wrt=shape`, on the patched image, reading idx46 and idx18 only. That is the
A_stepsize_study protocol's own step 1, it is the measurement A5's idx16 needed, and on a
38,304-cell case at np=4 with 96 DVs it is **not cheap** — A2 has lost a full `check_totals` sweep
twice, at 207.13 and 238.4 core-min (`../grading_confirmation/RESULTS.md` §5.3). **It is named here
as the unbought measurement, with its price, and not smuggled in as a conclusion.**

## 7. What this extraction cannot see

1. **One step, so no flagging test** (§6) and no plateau confirmation. Every percentage here inherits
   whatever `step=1e-3` truncation and noise the case carries, and that quantity is unmeasured on A2.
2. **It cannot say whether idx46 is an adjoint defect or an FD reference artefact.** A5's idx16 turned
   out to be the reference. That question needs compute.
3. **65 of 96 patched `CD` FD components are not directly readable** — they are established by norm
   reconstruction (§5), which proves the *vector* is identical but does not print the individual
   numbers. If a future item needs those 65 values, it needs a re-run, not a better parser.
4. **No FFD index map was opened**, so §3.1's "all seventeen lie in idx 16–47" is a statement about
   the design-variable ordering and **not** a statement about a region of the wing. Naming the region
   would need `runScript_AeroOnly.py`'s DVGeo local-index layout, which this item did not read.
5. **np=4 throughout, and only np=4.** A2 is separately recorded as decomposition-clean (scotch vs
   simple at ~1e-04), but nothing in *this* extraction tests that, and the whole log-corruption
   problem in §2 exists **because** these are MPI runs.
6. **The limiter axis is untouched.** `../grading_confirmation/RESULTS.md` §5.1 records that A2's
   `fvSchemes` was never audited for `cellLimited`. That is still true; this item read no `fvSchemes`.
7. **This says nothing about the 47-iteration optimisation**, whose gradients were evaluated at
   deformed meshes that no A2 verification has ever examined.

## 8. VERDICTS

| row | image | aggregate | components >15% | sign flips | **verdict** |
|---|---|---|---|---|---|
| `CD` wrt `dvs.shape` (96) | SHIPPED | **1.7138%** | **7** (idx18, 46, 17, 19, 39, 20, 16; worst −360.75%) | **0** | **PASS on the aggregate band, with a per-component caveat** |
| `CD` wrt `dvs.shape` (96) | **PATCHED** | **0.0506%** | **1** (idx46, +190.06%) | **1 — idx46** | **PASS on the aggregate band, with a per-component caveat; a strict reading of `A_stepsize_study.md:91-93` makes it FAIL PENDING INVESTIGATION** |
| `CL` wrt `dvs.shape` (96) | SHIPPED | **1.1652%** | **1** (idx15, −80.20%) | **0** | **PASS on the aggregate band, with a per-component caveat** |
| `CL` wrt `dvs.shape` (96) | PATCHED | **0.0219%** | **0** | **0** | **PASS, unqualified — 96/96 within 5%** |
| FD invariance, shipped vs patched | both | — | — | — | **PASS** — 96/96 bit-identical on `CL`; 31/96 direct + norm-reconstruction to 8 s.f. on `CD` (§5) |
| published vs re-measured shipped | both | — | — | — | **PASS** — identical on all 96 analytic **and** all 96 FD components of both rows |
| log integrity | all three | — | — | — | **DEFECT FOUND** — 2 of 6 (row × image) combinations have **zero** uncorrupted printed copies (§2.2) |

> ### **ITEM VERDICT: the table is extracted, and it is not the clean table the record implied.**
>
> **The aggregates all stand exactly as published — every reconstructed norm reproduces its printed
> value to 7–8 significant figures, so nothing in `../grading_confirmation/RESULTS.md` §1 or §3 is
> numerically wrong.** What changes is what sits underneath them: **seven of 96 shipped `CD`
> components beyond 15%, one shipped `CL` component at −80.20%, and one PATCHED sign flip at idx46
> that the record explicitly says does not exist.** All of them are near-zero components, all of them
> are invisible to a vector norm, and the third of them is the third instance in this lab of the same
> failure shape (A1 idx6, A5 idx16, A2 idx46).
>
> **The free follow-up §5.4 named has now been done, and its value was not the reassurance it was
> expected to give.**

## 9. Ledger

| item | value |
|---|---|
| solver core-minutes | **0** — no container started, no solve run |
| dollars | **$0.00** |
| containers started | 0 |
| processes needing a kill | 0 |
| frozen files edited | **0** |
| files in `cases/` edited | **0** — this file is new; `../grading_confirmation/RESULTS.md` is **not** touched, and its §1 correction is left for the supervisor |
| published case directories written into | 0 |
| filed upstream | **nothing** |

**Verdict vocabulary:** PASS, GATE REACHED, GATE FAIL, NOT A RESULT, BLOCKED, PENDING. Shipped and
patched are separate rows throughout.
