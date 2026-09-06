# SANAA-DIRECT — "everything approved" (2026-09-06, ~02:30Z)

Captured verbatim from the chief session.

## Sanaa's words, verbatim

> ëverything approved

## Context (chief's reading, not her words) — the asks this answers

Her approval answers the enumerated desk list as it stood at the moment of
her message:

1. **Paper retrieval — APPROVED, seven papers**: Smirnov & Menter 2009,
   Wallin & Johansson 2000, Xiao et al. 2020, Weatheritt & Sandberg 2016,
   Speziale 1987 (closure's register), Vogel & Eaton 1985 (T3 ladder's
   blocked reference), Blay 1992 (K0d). Inbound fetch only; L-144
   title-page verification on arrival; nothing leaves the box (rule 7/8
   untouched).
2. **Closure sequencing — the SEQUENCING reading is adopted**: closure
   solves begin when the F6 separated-flow cases come online, behind
   M6/CRM, per her 0910b664 note — no further word needed at that point.
   The stand-down reading is retired.
3. **VMFRT005 — BOTH decisions approved**: procure the gas-phase nC12H26
   mechanism (inbound), and the run cost (~2,500-4,000 core-h,
   $128-205 derived) is approved. Runs through standing law: its own
   pre-registration, rule-12 costing, caps.
4. **Machine-readable freeze pin — APPROVED**: each pre-registration
   records its own freeze sha in a fixed field at freeze time;
   verification lands the clause and the convention.
5. **Rule 4 `phi` addition — APPROVED**: the constitution's field list
   gains phi, aligning it with its enforcing instrument (mark_done_t3.py).
6. **Ling arm 2 GPU run — APPROVED** (re-affirming her earlier YES at the
   frozen 40 GPU-h cap). One dependency approval cannot substitute:
   B1/B3 need HER CONSOLE SESSION (the instance's shutdown attribute —
   stop vs terminate — and a current price read) BEFORE power-on. The
   lab proceeds to the ready-to-power state (B2 amendment, drafted row)
   and then asks her for the console facts and the power-on.

Standing constraints unchanged: SUBMISSIONS PARKED, permanent privacy,
no permission laundering, all work through the lab's law.

## ADDENDUM (2026-09-06, ~21:00Z) — m0 box-wide-kill: repair, not retire

## Sanaa's words, verbatim

> yes agreed lets do 1

(In answer to the chief's two options for the run_r2_m0.sh box-wide kill:
option 1 = repair the pkill scope; option 2 = retire the m0 driver.)

## Context (chief's reading, not her words)

- **Option 1 chosen**: repair `run_r2_m0.sh`'s EXIT-trap `pkill -f
  "rhoSimpleFoam -parallel"` (:83,85) to a `-case $ROOT`-scoped kill,
  matching the already-safe sibling `run_r2_m1.sh`. m0's landed GATE FAIL
  verdict is untouched; the driver is not retired.
- **Route**: cfd owns the file (committee-grids); the driver is FROZEN
  (committed, worktree==HEAD sha256 cb810bb5...), so the in-place edit is a
  rule-6/§2d.1 amendment that VERIFICATION rules, not a lane edit.
- **Forced-repair test (§2av)**: the correct scoping is forced — one right
  answer exists (the sibling's `-case $ROOT` form) — so it has no degrees of
  freedom pointing at any verdict, which is the ground on which the amendment
  is grantable. m0 already reached first compute (it ran and graded), so
  §2ax does NOT apply and this is a genuine post-compute §2d.1 amendment, not
  a pre-compute one — the burden is the full four conditions, and the repair
  must not touch any gate, threshold, cap, label, or the graded verdict.
- **The census fact that motivates it**: the box-wide idiom FIRED once
  (2026-09-06 09:09Z, daemon-run), foreign blast radius unmeasured and
  unknowable; the repair closes it for good and protects the pattern from
  being copied unscoped.
