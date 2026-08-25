# VMFL045-R2 — opus-4.8 lane RUN REPORT OF RECORD (v3, FINAL for the run)

**Channel:** lane→supervisor `SendMessage` is one-way; this committed file is the
reliable channel. The run is **complete and graded**; the **tier and the credential
landing are HELD for the supervisor** (§4).

## 0. Authority
Chief withdrew its earlier grade-nothing instruction; my supervisor's authorisation
governs in-territory. I ran the frozen comparator (mechanical) and recorded what it
prints; I did **not** issue a tier.

## 1. Result — the frozen comparator, unmodified
- `--verify-frozen HEAD` exit 0 (grading path `382ff497`).
- **VERDICT: `PASS`.** L3 M₂ = **1.874779041082**, deviation **+0.041571 %** vs manual
  target **1.874** (band ±1 %) — inside by ~24×.
- Roache triple (r=2, Fs=1.25): coarse 1.871975737 / medium 1.874534336 / fine
  1.874779041; R=0.095640; state **CONVERGING**; GCI_fine 0.0017 %; Richardson 1.8748049198.
- Three planted-zero controls (PZ-1/2/3) **FIRED**. `GRADING_VMFL045_R2.json`, `.stdout.txt`.

## 2. THE SUSPICIOUS ORDER — surfaced, not stamped
**Observed order p = 3.3862** — far above expected p≈1 and beyond the p≈2 the supervisor
**pre-declared suspicious**. Super-convergence: d21 (−2.45e−4) is ~10× smaller than d32
(−2.56e−3); the triple is very likely **not in the asymptotic range**, so GCI_fine
probably **understates** discretisation uncertainty. This is the "suspiciously good order
is the failure mode nobody reports." **The rule-1 verdict is still PASS** (the frozen
rule-5 classifier makes the triple CONVERGING and the value is inside band); the concern
is the **P limb / tier**, which is the supervisor's.

## 3. Strict completion (rule 4) and cost
- rc=0, one `End`, fields present (Ma T U p rho), **age guard PASS** at all three levels.
  `adjustTimeStep yes` → last written time ~0.0069998 s (not literally endTime 0.007);
  the frozen comparator reads the last time dir and accepted it (exit 0).
- **Cost 26.6667 core-min measured** (L1 0.3667 + L2 2.6667 + L3 23.6333; wall 1600 s,
  serial) of a 48 cap (55.6 %). Predicted 20.4 → **ratio 1.307×**. Under-prediction of
  L3, **zero waste, zero contention charge** (VMFL003 co-resident, load ~3–4/16, LIGHT;
  a serial job there is not core-starved). Calibration **C-58** landed.

## 4. What I LANDED vs what I HELD
**Landed (measured / instrument output / authorised):**
- Run evidence, 27 files by explicit path — commit `c80c7188`.
- `RESULTS.md` (verdict PASS recorded, p=3.39 surfaced, tier deferred) — blob
  `77f0a271`, commit `913ff5ce`.
- Cost-calibration **C-58** — commit `5703f2c3` (append_record.py merge; append_guards
  --selftest 7/7 inside the invocation).
- Contention terminal sample (SAMPLE 3 AT END) in `CONTENTION.txt`; the supervisor's
  OS-level sampler wrote the authoritative mid-L3 (SAMPLE 2) at 02:42:40Z. I removed my
  own redundant watcher so it could not write into the sampler's block.

**HELD for the supervisor's tier ruling (the credential pronouncement):**
- The **validation-register row** (with its tier inline) and the **credential tally**.
- **CASE_MAP.md**'s campaign fraction and the VMFL045 tier cell.
Why held: a tier is the supervisor's ruling; there is no supervisor default tier for a
`PASS`; and p=3.39 is the pre-declared suspicious trigger. Landing a PASS row would
auto-increment the credential count — a credential pronouncement I must not make over a
suspicious P limb.

## 5. When the supervisor rules the tier — the landing sequence (three parents, ONE invocation)
Note **VMFL003 already landed** (commit `288a5862`, NOT A RESULT), so the register
tally and CASE_MAP fraction have moved since; **re-derive every count from the files at
commit time.** Use `verification/runs/ansys_verification/append_guards.py`
(`check_aggregates_moved` is exactly the parent-must-move guard; pins heat-transfer's
`safe_append.py` v1.1 `6c8035a3`); run its `--selftest` inside the committing
invocation. The three parents that must move together:
1. **Register**: append the VMFL045-R2 row with **tier inline (the supervisor's ruling)**
   + update the credential tally "N PASS of M run" (re-derived from PASS rows).
2. **CASE_MAP**: campaign fraction (distinct cases run — a re-run of VMFL045 does **not**
   add a distinct case) + the VMFL045 tier cell (pattern "NOT HELD (run 1) → <tier> (R2)").
3. **Leave the register's #1–#4 foot addendum scope untouched** (this row carries its
   tier inline; it does not join the back-fill).
The register row cites `RESULTS.md` (`77f0a271`), the evidence commit `c80c7188`, prereg
`592e872b`, comparator `382ff497`, and C-58.

## 6. Carried forward, unchanged
Fluent 1.902 would **GATE FAIL** at +1.494 %; CFX 1.871 passes at −0.160 %. A near-Fluent
value is a `GATE FAIL`, never narrated as agreement with Ansys. The `"(h|e)"` fix is
confirmed by the run (smoke rc=0; run-1 `Entry 'e' not found` gone; `e` solved cleanly).

_Last updated 2026-08-25T03:04:35Z._

---

## CLOSE-OUT COMPLETE — 2026-08-25T03:18:07Z
The supervisor read the grading JSON and **ruled the tier ** (not HOLDS),
naming the **G column** as the limb held back: observed order p=3.3862 is measured but
not trusted (above the scheme's formal order), d21 (−2.447e−4) is ~3× L3's plateau floor,
so GCI_fine 0.0017 % is not a discretisation-uncertainty statement (`N-AV7` second form);
V is strong (exact matched to 0.0106 %). Verdict `PASS` unchanged (comparator's,
mechanical); order not re-run, verdict not softened. **First compressible PASS, third credential.**

**Landed after the ruling:**
- RESULTS.md tier updated DEFERRED → `GATE REACHED` (G named) — commit `f4332fe3`.
- **THREE PARENTS in one invocation** — commit `96535662`: register **row #7**
  (`PASS`, tier `GATE REACHED` inline) + credential tally **2→3 PASS of 6→7 run**;
  CASE_MAP VMFL045 ladder tier cell **NOT HELD (run 1) → GATE REACHED (R2)** and the
  now-false "re-run pending" clause corrected; campaign fraction re-derived, unchanged at
  **5 of 73** (a re-run adds no distinct case). Guards: `check_anchor_is_last` (row #6
  VMFL003 was last), `check_aggregates_moved` on both parents, `append_guards --selftest`
  inside the invocation.
- Calibration **C-58** (measured contention ClockTime/ExecutionTime 1.021/1.004/1.000 —
  L3 idle-wait 0.0 %; VMFL003 co-resident but not core-starved) — commit `5703f2c3`.
- `reaudit_landed_blocks.py`: **19 blocks intact** at HEAD.

**Flagged for the supervisor, NOT touched (not this lane's records):** the CASE_MAP
"cases run and their tiers" glance table (~line 138) is missing VMFL003's row and its
header still reads "four cases run"; it needs VMFL003 + a standalone VMFL045-R2 entry and
a header refresh. Left to VMFL003's/the supervisor's hand.

_Case CLOSED at HEAD `96535662`._
