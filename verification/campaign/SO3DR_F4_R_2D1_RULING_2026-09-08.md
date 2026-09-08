# SO3DR-F4-R — §2d.1 RULING: GRANTED. The F6 sample-path defect is a value-invariant, invocation-only repair; re-grade with `--sample` at the REGISTERED with-R file recovers a clean RECORD (NOT A RESULT | HIGH-CONFOUNDED), not a different answer.

**Date:** 2026-09-08. **Author:** verification-supervisor (personal §2d.1 ruling; cross-team gate audit).
**Provenance:** chief routing 2026-09-08 (internal relay, not Sanaa's words) — dafoam's SO3DR-F4-R
disposition. **Cost:** 0 solver core-min, $0.00 (re-grade only; the value-invariance re-run read
existing leg dirs, output to scratch).
**Evidence:** verification lab-lane gather + zero-re-solve re-run, verified by me; scratch artifacts at
`…/scratchpad/so3dr_regrade/` (not a repository handoff — cited here as this session's evidence only).

## The case, and why it is the LAWFUL vehicle V-127 prescribed

SO3DR-F4-R (`cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2_R/`) is the **fresh successor** V-127
mandated when I ruled the ORIGINAL Stage-2 F4 defect §2d.1-UNAVAILABLE (the grader had refused, so no
value existed to hold invariant). The successor RAN CLEAN (36 legs) but its frozen grader
`so3dr_stage2R_grade.py` then refused at a **different** step — **F6, a sample-presence control** —
because of a filename defect. That F6 refusal is what this ruling disposes of.

## Facts verified at source (by the lane, checked by me)

1. **Grader `--sample` default** (`so3dr_stage2R_grade.py:402-403`) resolves the **no-R basename**
   `so3dr_stage2_registered_sample.json` against the `_R` dir. **`SAMPLE_MD5 = 55bf8e2d…`** (`:50`);
   F6 refuses on absence/mismatch (`:261-262`).
2. **FREEZE marker** (`so3dr_stage2_FREEZE.marker`) REGISTERS the **with-R** sample
   `so3dr_stage2R_registered_sample.json` md5 `55bf8e2d` — but its PRESCRIBED grade command omits
   `--sample` (relying on the broken default). *The freeze is internally inconsistent: it registers
   the with-R file yet prescribes a command that cannot reach it.*
3. **On disk:** the no-R default file is **ABSENT**; the with-R registered file is **PRESENT**, md5
   `55bf8e2d` = SAMPLE_MD5, and is the ONLY sample json in the `_R` dir.
4. **Frozen grader byte-UNCHANGED** — blob `8f7ca638…` (V-127 pin), md5 `2d32ec9b…` (marker + prereg
   §7 pin). Gate/threshold/reader all byte-identical: `HIGH_THRESH=0.50`, `LOW_THRESH=0.10`,
   `F3_SUCC_CONFOUND=0.10`, the six-token discrim map (`:275-311`), the F6 reader (`:258-268`).

## The §2d.1 four conditions — all met

1. **Real, confirmed grading-path defect — demonstrable by FILE EXISTENCE.** The default points at a
   file that never existed; the registered/md5-pinned file exists. Met.
2. **VALUE-INVARIANT, verified on EVIDENCE not assertion.** Zero-re-solve re-run:
   - marker-prescribed default (no `--sample`): **rc=2**, reproduces the F6 refusal exactly.
   - repair (`--sample` = registered with-R file): **rc=0**, reaches and passes the gate; verdict
     **`NOT A RESULT` | `HIGH-CONFOUNDED`** = the **registered prediction**. `r_sa=0.8889` (32/36);
     `legs_completed=36`; F3 confound `r_succ_stratum=0.6667` (8/12) > 0.10 → HIGH downgraded to
     NOT A RESULT (F3-borne). Planted control fires (`--selftest` rc=0 under python3 and -O; blinded
     reader caught both). Met.
3. **Frozen file edited only via a dated addendum — here NOT edited at all.** The repair is
   INVOCATION-ONLY; the grader blob is unchanged. Stronger than F27 R2 (which needed a v1.1 in-place
   re-pin). Met.
4. **No gate/threshold/band/cap/label/reader altered.** Byte-identity of the whole grader proves it.
   Met.

## The anti-gaming test (§2av) — satisfied by the freeze's OWN guard

The repair has **zero degrees of freedom to affect the answer**: F6 checks the sample against the
FROZEN `SAMPLE_MD5 = 55bf8e2d`, so **only a file matching that md5 passes** — any other `--sample`
target is REFUSED. The one admissible target is doubly pinned (marker registration + the grader's own
frozen md5 constant). A defect with exactly one correct repair cannot be aimed at an answer.

## The V-127 distinction, honored

V-127's SO3DR-F4 refused at a **grading** step because a required input genuinely DID NOT EXIST (the
primal failed) → no referent, and the proposed fix altered logic (dropped F4's md5 arm) as an
untracked monkeypatch. SO3DR-F4-R refuses at a **sample-presence** control on a wrong PATH STRING,
while the input EXISTS and is md5-pinned; the fix alters no logic and the grader is byte-frozen. This
is F27-R2-shaped (a wrong default-arg to an existing, uniquely-determined target), NOT
V-127-SO3DR-F4-shaped.

## RULING

**§2d.1 GRANTED.** Re-grade SO3DR-F4-R with `--sample` pointed at the REGISTERED with-R file
(`so3dr_stage2R_registered_sample.json`, md5 55bf8e2d); **zero re-solve**. The recorded verdict is
**`NOT A RESULT` | `HIGH-CONFOUNDED` (F3-borne)** — the repair recovers a clean RECORD, not a different
answer.

### Condition on the grant (dafoam to execute; the vehicle by which the corrected invocation becomes the frozen grading path)

A **dated §2d.1 addendum** to the FREEZE marker / prereg, written by dafoam, that: (i) records the
defect (marker registered the with-R file md5 55bf8e2d; prescribed command relied on a default
resolving to a nonexistent no-R path — an internal freeze inconsistency); (ii) corrects the prescribed
grade command to pass `--sample so3dr_stage2R_registered_sample.json` explicitly (keeping the grader
byte-frozen — do NOT edit the grader's default, which would move its blob and need a re-pin); (iii)
asserts value-invariance citing this ruling and the re-run; (iv) alters no gate/threshold/band/cap/
label, and carries the "lines whose number changed above this section: 0" assertion if it appends to a
frozen document. The verdict is then recorded for SO3DR-F4-R.

## Caveats (disclosed, not gating for a NOT A RESULT)

- The verdict is a **NOT A RESULT (a non-credential)**, so it certifies nothing — it records that the
  result is confounded. It therefore does **not** rest on independent re-verification of the 36 legs'
  strict rule-4 completion; that completion is ATTESTED by the grader (`legs_incomplete=[]`, and F4
  requires all legs passed) and was not re-derived by me. Were this a PASS, that independent check
  would be load-bearing; for a NOT A RESULT it is not.
- The ~74.87 core-min cost and the primary V-127 record were not independently re-read (seen as
  dafoam's rendering); neither bears on the §2d.1 disposition.

## Downstream substance (unchanged from V-127)

The `NOT A RESULT | HIGH-CONFOUNDED` is **F3-borne** (SUCCEEDED-stratum r_succ 8/12 = 66.7% ≫ 10%) —
an upstream fact independent of the F6 defect. A successor buys a clean F4 RECORD, not a different
answer. Whether to pursue the F3 confound further is dafoam's + the chief's compute call, not a
verification gate.
