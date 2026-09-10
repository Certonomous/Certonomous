# VMFL051-R3 — FREEZE RECORD, 2026-09-10

**This file exists BECAUSE the frozen registration must not be edited.** The
pre-registration's §10 blob-sha table is deliberately still BLANK, and it stays blank.
Filling it in after the freeze would change `PREREGISTRATION.md`'s blob, and the driver's
own freeze-pin compares the on-disk prereg against the blob committed at the freeze
commit — so "completing" that table would make `run_vmfl051_r3.sh` REFUSE TO LAUNCH.
The shas therefore live here, outside the frozen file, and rule 6 is satisfied by not
touching it at all. Lines whose number changed in PREREGISTRATION.md: **0**.

## The freeze

- **Freeze commit:** `5b9b086e5e25d4e63bd10ce3745536753d3df566`
- **Filed queue entry:** `verification/queue/ansys-verification/VMFL051-R3.json`, validator **ACCEPTED**

| frozen file | blob at the freeze commit |
|---|---|
| `PREREGISTRATION.md` | `073e27100680592db7eb7c7817b160a6b21c6311` |
| `grade_vmfl051_r3.py` | `fedb1088bfdc6be028743246e0da5b404c6749b2` |
| `run_vmfl051_r3.sh` | `16aa1907193559d60196fc75592b680253368109` |
| `case/system/topoSetDict` | `e96bd15e78ada10a540cc27692958ad9efe83de2` |
| `case/system/controlDict.template` | `9269fde375dbe032e4546ba31521f7d2c0d79c98` |

Verified in the filing invocation: `git hash-object` of the on-disk
`PREREGISTRATION.md` equals its blob at `5b9b086e5e25d4e63bd10ce3745536753d3df566` (`073e2710…`), so the pin holds.

## A correction to my own freeze commit message

That message said the post-L1 `--dryrun-reader` check "must pass before L2/L3".
**It is not mechanically enforced, and I am correcting that rather than leaving a
statement standing that the code does not honour.** `run_vmfl051_r3.sh` defines all
three levels in `LEVELS` at :44 and loops over them at :69 and :86 within a single
invocation; there is no between-level gate for a lane or a supervisor to interpose.

I am launching anyway, and here is the honest reasoning rather than a silent decision:

1. **The exposure is small and bounded.** 9.8 core-min estimated (MEASURED on R2's
   byte-identical solve), 28 core-min capped by `timeout`, so at absolute worst
   ~$0.024 DERIVED at $0.0513/core-h — not measured, the box cannot read its billing.
2. **A reader or format mismatch cannot manufacture a false number.** The comparator
   REFUSES with rc 2 rather than degrading, so the failure mode is a refusal I can see,
   not a value I might believe. That is what makes the ungated run acceptable.
3. The check is therefore run as a **post-L1 diagnostic**, not as a gate.

## What is genuinely unverified until compute happens

Carried from the lane's §11 and not papered over: the mesh build, that `topoSet` yields
exactly one face column per plane, that the `exprField` / `weightField phi` evaluate
live, and that the live `surfaceFieldValue.dat` matches the source-derived reader. Rule 2
forbade the compute that would settle them. Any failure is a refusal and a finding,
repaired by a dated addendum; **no gate, threshold, cap or label moves.**

## Expected outcome, stated before the answer is seen

A repeat `NOT A RESULT` is a **pre-registered legitimate outcome**. R2's gate VALUE would
have passed (L3 deviation −0.233 % inside the 0.5 % band) and only its OSCILLATORY triple
(R = −1.184) blocked it; R2's strictly-inner zone was ALSO non-monotone, so the corner-entropy
floor may simply be irreducible. "PASS-capable" is a ceiling, not a promise.
