# VMFL023 — INTERIM STATUS — **`PENDING`**

**As at 2026-08-25T22:25:51Z.** `PENDING` is used here in its charter sense — a
**display/queue state** for "not yet finished" (`VERIFICATION_CHARTER.md` §9).
**It is not a softened `GATE FAIL` and it is not a result.**

This file exists so the case's state survives a dropped lane. **`RESULTS.md` will
be written once, when the triple exists**, so that no partial number is ever
filed as though it were a verdict.

## Frozen and committed BEFORE any compute

| | |
|---|---|
| Pre-registration | `754f4f66` — run root ABSENT at the freeze timestamp on line 1 |
| Addendum 01 | `2e0dd6a5` — geometry-read-back and budget-starvation instructions |
| Addendum 02 | `591f659e` — the §2d.1 comparator repair |
| Gate | `\|St − 0.165\|/0.165 ≤ 0.03` at the finest level |
| Tier ceiling | **`GATE REACHED`** — the reference is a CORRELATION, which buys V, never P |

## The consistency check — reported whichever way it fell

**The page is INTERNALLY CONSISTENT**, the opposite finding to VMFL036. From the
manual's own stated properties, `Re = ρUD/μ = 1×1×2/0.02 = 100.0`, and the page
itself states Re = 100 in its text and in both result tables. The target
St = 0.165 sits inside the published correlation spread **[0.16434, 0.16706]**
(Williamson 1988, Roshko 1954, Fey 1998, Williamson & Brown 1998), 0.4% from the
mid-spread. **No repair arm is needed.** Both facts are wired into the comparator
as an executable control that REFUSES if either ever fails, and the launcher
carries the same assert so a wrong viscosity would die at launch.

**A correction to the relation this lane was handed:** the supplied form
`St ≈ 0.1644 − 1.5619/Re` gives **0.1488** at Re = 100 and does **not** match
0.165 — it would have read as a failed check. The accepted Williamson (1988)
parabolic fit is `St = −3.3265/Re + 0.1816 + 1.6e−4·Re` = **0.16434**. The check
was re-derived from the literature form; all four correlations agree.

## Level state

| Level | Cells | State | wall s | core-min | Level cap |
|---|---|---|---|---|---|
| L1_96x32 | 3 072 | **complete, rc = 0** | 488 | 8.13 | 20 |
| L2_192x64 | 12 288 | **complete, rc = 0** | 1 945 | 32.42 | 70 |
| L3_384x128 | 49 152 | **RUNNING** — ~18% of 60 000 steps | — | — | 260 |

**L3 projects to ~194 core-min against its 260 cap** (measured 5.15 steps/s on a
drained box), so it is expected to complete inside budget. **All three levels were
launched as SEPARATE invocations, so each level's budget is its own cap alone and
cross-level starvation is structurally impossible in this run.**

**L1 machinery verified on the real completed level:** 60 000/60 000 steps,
Co_max = 0.1392 (registration requires < 1), **SETTLED to 0.006% against the 5%
stationarity tolerance**, 10 upward zero-crossings in the sampling window, and
both planted controls firing (a sinusoid planted at St = 0.165 read back as
0.165000; a flat lift series REFUSED, not reported as some St).

**No St value is quoted here, at any level.** The verdict needs the converging
triple, and a single level is not a result.

## Measured finding already on the record

**The manual's own method cannot resolve this lab's band.** The page specifies an
FFT of the lift coefficient. An FFT resolves one bin, `Δf = 1/T_record`; over
this case's 120 s sampling window that is **ΔSt = 0.01667 — 10.1% of the target
0.165**. Measured, not asserted: the comparator's selftest runs an FFT on a
synthetic series built at St = 0.165 exactly and recovers **0.16667**, off by
exactly one bin, while the frozen zero-crossing regression recovers **0.165000**.
Offered as a prediction, not a conclusion: Fluent's printed 0.178 is 0.165 + 0.013,
**within one bin width**, and the manual's own CFX note says that record length
*"was chosen to accommodate FFT calculations"* — the one solver whose record was
sized for the FFT is the one that landed at ratio 1.01.
