# T3d — the `R_ff` CONTINUATION (`R_fx`): drive the fourth level to iterative convergence, the one thing standing between T3c's four `NOT A RESULT` rows and gradeable numbers

> **STATUS AT THIS COMMIT: FROZEN BY THIS COMMIT AND NOT ONE MINUTE EARLIER.
> NOT ENQUEUED TO THE LIVE DROP PATH. NOT LAUNCHED. NOT GRADED.**
>
> At the moment of freezing, `verification/runs/T-family/T3_runs/R_fx/` holds
> `0.orig/`, `constant/`, `system/` and `CASE.txt` and **NO `0/`, no numeric
> time directory, no `STATUS.R_fx` and no `DONE.R_fx`** — verified on disk in the
> same shell invocation that produced the hashes in §6. **The freeze provably
> precedes compute.**
>
> **The queue entry is staged in `verification/queue/heat-transfer/held/`, which
> the runner's `glob` does not scan.** It is NOT in the live drop path.
> `SUPERVISION_CHARTER.md` §3 check 4 is the supervisor's, is not delegable to
> this lane, and — because that directory is a launch button on a one-minute tick
> (`verification/queue/heat-transfer/README.md`, the 2026-08-27 correction) —
> **must be discharged BEFORE the file is moved, never after.**

Written 2026-09-03 by a heat-transfer `lab-lane`. Repository HEAD at drafting:
`5b7a9163`.

---

## 1. What T3d is, and the one thing it is not

`T3c` graded the triple `(R_m, R_f, R_ff)` on 2026-09-03 and returned
**`NOT A RESULT` × 4** (`gate_t3c.json`, commit `d5a8b651`). Every row failed on
the same clause and the same level:

> `level f not iteratively converged`

`R_ff` sits at relative change **4.343e-06** against tolerance **1e-06** — a
factor of **4.34** — at its final checkpoint pair 116 000 → 118 000. **Nothing
else in the ladder stops those rows.** Five of the six triples are `CONVERGING`.

**T3d continues `R_ff` on the IDENTICAL MESH.** `R_fx` is not a fifth level: it
is 602 128 cells, the same `constant/polyMesh` bytes, seeded from `R_ff/118000/`.
**A continuation is not a mesh study, and this document does not claim one.**

**WHY A NEW CASE DIRECTORY, AND THE SUBSTRATE FINDING BEHIND IT.** `R_ff` holds
`0/` and two numeric time directories, so both the queue validator's `AGE-GUARD`
(`scripts/queue_entry_check.py:326`) and the launcher's own G3 guard refuse it —
**correctly**, under standing rule 4. **The lab's queue substrate has no route
for an in-place continuation.** That is reported to the supervisor as a finding
about the substrate and is **not worked around**: `R_fx` is a fresh case whose
`0.orig/` *is* `R_ff`'s final state, so the age guard is satisfied honestly.

## 2. THE PREDICTION — registered under Sanaa's 2026-09-03 ~21:00Z rule, and it can lose

> *"A pre-registration mismatch never prevents a launch. It's recorded as a
> prediction, the run launches under the monitor, and the outcome is compared to
> the prediction on the certificate."*

**PREDICTION P-1 — `R_fx` reaches iterative convergence (relative change
≤ 1e-06 in `T` between its last two checkpoints) within 24 000 additional
iterations.**

**Basis, measured from `R_ff/log.solve` and not assumed.** The `T` initial
residual is **descending monotonically** over the final ~22 000 iterations,
sampled at 2 000-iteration intervals: `1.465e-07 → 3.182e-08`, a factor
**0.2172**, i.e. **×0.8704 per 2 000 iterations**. To close the remaining factor
of 4.343 requires `ln(4.343) / −ln(0.8704) = 10.58` intervals = **21 160
iterations**. **24 000 is that figure with 13 % margin.**

Sanaa's monitor taxonomy classes this trajectory **descending → extend bounded
and booked**, not plateaued and not diverging.

**PREDICTION P-2 — the restart produces a residual spike that decays within
2 000 iterations.** Seeding `0/` from written fields re-initialises the SIMPLE
loop; a transient at restart is expected and benign. **If it does not decay, P-2
has lost** and the run is reported as such.

**REGISTERED FALSIFIERS — each can lose, and losing is reported, not explained
away:**

| # | prediction | what falsifies it |
|---|---|---|
| **F-1** | convergence within 24 000 its | the last checkpoint pair still reads relative > 1e-06 at `endTime` |
| **F-2** | residual keeps descending | the `T` initial residual plateaus (factor > 0.98 per 2 000 its) or rises over any 6 000-iteration window after the restart transient |
| **F-3** | cost lands within CAP | actual > 16 326 core-min |
| **F-4** | the continuation does not move the physics | `St_peak` at `R_fx` differs from `R_ff`'s 0.00356254 by more than the level's own GCI of 6.0970 % |

**F-4 is the one this lane most expects to be argued about**, and it is stated as
a prediction rather than an assumption: a continuation that changes the graded
value by more than its own grid-uncertainty band would mean the value quoted at
118 000 was not converged in a sense the GCI already claimed to cover.

## 3. THE DISCLOSURE AGAINST THIS DOCUMENT'S OWN INTEREST

**T3d WILL NOT PRODUCE A `PASS`, and nobody should approve it expecting one.**

The frozen ordered gate is: (1) level not CONVERGED → `NOT A RESULT`; (2) triple
not CONVERGING → `NOT A RESULT`; (2b) outlet test; (3) **no primary → `BLOCKED`**;
(4) band. **The primary — Vogel & Eaton (1985) — is NOT OBTAINED** (`primary_present:
false` in `gate_t3c.json`; ASME closed, every open archive named in
`T3_PREREGISTRATION.md` §2).

So if P-1 holds, the expected movement is:

| row | today | expected after T3d | why |
|---|---|---|---|
| G1 `St_peak` | NOT A RESULT | **BLOCKED** | triple CONVERGING, gate (3) fires on the missing primary |
| G3 `St_10H` | NOT A RESULT | **BLOCKED** | same |
| G4 `St_20H` | NOT A RESULT | **BLOCKED** | same |
| G2 `x_peak_H` | NOT A RESULT | **NOT A RESULT** | triple is `OSCILLATORY`; gate (2) fires regardless of convergence |

**Three rows move from `NOT A RESULT` to `BLOCKED`, and one does not move at
all.** That is the honest expected product for 5 442 core-minutes.

**Why heat-transfer judges it worth buying anyway, stated as an argument and not
as a fact:** `NOT A RESULT` says *our ladder did not converge, so the number
means nothing*. `BLOCKED` says *we have a mesh-converged number with a GCI band
and no reference to grade it against*. **The second is a capability statement and
the first is not**, it is quotable into the DC certificate as a REPORTED value
with real uncertainty, and it moves the rung's blocker from something the lab can
fix with compute to something only an archive can fix. **If the supervisor judges
that not worth 5 442 core-min, declining is a reasonable call and this section
exists so it can be made on the numbers.**

## 4. The run

| item | value |
|---|---|
| case | `verification/runs/T-family/T3_runs/R_fx` |
| mesh | **602 128 cells, IDENTICAL bytes to `R_ff`** |
| seed | `R_ff/118000/` → `0.orig/`: `T U p_rgh p alphat nut k omega phi` |
| **not** seeded | `C Cx Cy Cz` (function-object cell centres, not solution state) and `118000/uniform` (time bookkeeping that would contradict a restart at 0) |
| solver | `buoyantBoussinesqSimpleFoam` |
| `endTime` | **24 000 — ADDITIONAL iterations.** The counter restarts at 0 because `startFrom latestTime` will find only `0/` |
| `writeInterval` / `purgeWrite` | 2 000 / 2, unchanged from `R_ff` |
| ranks | **8**, `simple (8 1 1)`, as `R_ff` |
| builder | `build_t3d.py`, refuses if the target exists and never writes into `R_ff` |
| launcher | `launch_t3d.sh` — **four refusal arms driven, all exit 2**: wrong ranks, wrong timeout, wrong case name, absent case; the case tree was verified untouched afterward |

## 5. COST — rule 12 and Sanaa's 2026-09-03 18:00Z cap law, arithmetic shown

**Rate basis: MEASURED, from `R_ff`'s own `STATUS.R_ff`** — 26 757.067 core-min
for 118 000 iterations on this exact mesh at these exact ranks =
**0.226755 core-min per iteration**. This is not an analogy from another case.

| item | value | arithmetic |
|---|---|---|
| **ESTIMATE (POINT)** | **5 442.1 core-min** | `0.226755 × 24 000` |
| **HARD CAP** | **16 326 core-min** | `5 442 → ×3 → 16 326` |
| registered `timeout_s` | **122 445 s** (34.0 h) | `16 326 × 60 ÷ 8 ranks` |
| **FLEET SAFETY CEILING** | **48 978 core-min** | `3 × CAP` (Sanaa 21:00Z: `min(3× cap, remaining box budget)`) |
| USD at POINT | **$4.653** | **DERIVED, NOT MEASURED** — `5442.1 ÷ 60 × $0.0513/core-h` |
| USD at CAP | **$13.96** | **DERIVED, NOT MEASURED** |

The rate is **reported-by-owner, not measured** — this box cannot read its own
billing (`COMPUTE_BUDGET_CHARTER.md` §5).

**CAP ENFORCEMENT, and what actually stops this run.** `scripts/queue_runner.py`
**reports** a cap overrun and does **not** kill. The cap binds only through
`launch_t3d.sh`'s `timeout --signal=TERM --kill-after=120 122445`, and the
launcher **refuses at pre-flight** any `--timeout` not equal to the registered
122 445 and any `--ranks` not equal to 8. **A cap nothing enforces is not a cap**
— a lesson this rung paid for hours earlier, when T3c registered a 0.30 core-min
cap with no instrument and overran it to 0.3965.

**Predicted-versus-actual is OWED to `docs/COST_CALIBRATION.md`** at completion
and is not discharged here. Waste, if any, is named separately and never absorbed
into the ratio. **The $1 000 envelope is the benchmark ladder's (cfd, Rungs 0–3)
and is NOT this rung's funding basis**; T3d runs under the standing blanket and
the cap above.

## 6. THE GRADING PATH, FIXED AT THIS COMMIT — full sha256 of the disk bytes

Recorded as **full** sha256 because `check_comparator_freeze.py`'s
`sha_witness()` greps the full digest and can see neither a git blob sha1 nor a
16-hex truncation (`VERIFICATION_CHARTER.md` §2u).

| file | sha256 |
|---|---|
| `verification/runs/T-family/T3_runs/analyse_t3d.py` | `980ae3b203cb7d75abf3027eea7a9d37c0c4c042dd06216d3f1ebc28a7e77034` |
| `verification/runs/T-family/T3_runs/build_t3d.py` | `bfc5087be17951d9562378891af2e262f6935fdd89e6b95b8c784b02ed635890` |
| `verification/runs/T-family/T3_runs/launch_t3d.sh` | `7d0bbe38344b5b12b9546fd3ec194af0d06f580e81a5b9a771d702f114cec367` |

**`analyse_t3d.py` differs from the frozen `analyse_t3c.py` in FIVE IDENTITY
HUNKS AND NOTHING ELSE**, each reviewable as a diff: the `LADDER` level-f name,
the output filename, the confound wording, the cost key and the rung label.
**No predicate, threshold, gate, band or verdict rule differs**, and the repaired
rule-3 control P-2 (`N_ULP = 32`, LIMB A identity + LIMB B in ulp of the
operands) is carried over byte-identical. `--selftest`: **PASS, 0 failed**,
including arm S-9 and the `DONE.R_fx` refusal at exit 2.

**FREEZE STATUS, STATED SO IT IS NOT MISREAD.** `check_comparator_freeze.py` will
scope `analyse_t3d.py` to `DONE.R_m` and `DONE.R_f` (2026-08-24) and report it
**`UNFROZEN`**. **That is a TRUE POSITIVE for the two coarse levels** — they were
complete and published before this module existed, and this lane proved that same
flag a true positive rather than inheriting a claim to the contrary
(`probe_freeze_flip_t3_rff.py`, commit `5b43399a`). **For the level this rung
actually adds, `R_fx`, the freeze is clean by construction: no `R_fx` marker,
`STATUS` or time directory exists at this commit.**

## 7. What this document does not do

- It does **not** launch. The entry is staged in `held/`, outside the runner's scan.
- It does **not** discharge `SUPERVISION_CHARTER.md` §3 check 4. That is the
  supervisor's, personally, before the file moves.
- It does **not** edit `analyse_t3.py`, `analyse_t3_rff.py` or `analyse_t3c.py`,
  and it does **not** re-grade or withdraw T3c's published `NOT A RESULT` × 4.
- It does **not** move a gate, band, threshold, cap or label of the T3 rung.
- It does **not** claim a fifth mesh level, and does **not** claim the
  continuation will produce a `PASS` — §3 says the opposite.
- It does **not** authorise any send. **SUBMISSIONS REMAIN PARKED** (rule 7).
