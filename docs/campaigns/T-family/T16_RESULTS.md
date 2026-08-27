# T16 results — developing laminar mixed convection in a vertical channel — PARTIAL, 2026-08-27T18:45Z: `T16_MC_c` landed COMPLETE but is **BLOCKED**; the frozen marker refuses every real OpenFOAM log

**Document version 1.0.** Rung `T16`, pre-registration
`docs/campaigns/T-family/T16_PREREGISTRATION.md` frozen at commit
**`ae20d137`** (2026-08-27T17:12:13Z). Drafted by a heat-transfer grading lane.

**Rung verdict at this writing: `PENDING`.** One of three levels has landed.
No Roache triple exists, so no row can be gated under rule 5 whatever any
single level says.

**Case verdict, `T16_MC_c`: `BLOCKED`.** The run satisfies all six limbs of the
strict completion rule on a direct reading of its artifacts, and the rung's own
registered marker — the only instrument entitled to write its DONE — **refuses
it (exit 2) on a false-positive crash token.** The block is an instrument
defect, not a property of the run. It is recorded in §4 and docketed.

---

## 1. Freeze verification — done in the same invocation that graded (`VERIFICATION_CHARTER` §2d)

All seven grading-path files were hashed on disk with `git hash-object` and
compared **both** against the blob table the pre-registration declares at §11
**and** against `git rev-parse ae20d137:<path>`. A verification taken in an
earlier invocation would not have discharged this and none was relied on.

| file | declared @ `ae20d137` | on disk | |
|---|---|---|---|
| `exact_t16.py` | `f1591a44…` | `f1591a44…` | MATCH |
| `exact_t16_REPAIR.diff` | `3b6f2803…` | `3b6f2803…` | MATCH |
| `build_t16.py` | `e7ed305e…` | `e7ed305e…` | MATCH |
| `T16_registered.json` | `32816560…` | `32816560…` | MATCH |
| `analyse_t16.py` | `9054d452…` | `9054d452…` | MATCH |
| `mark_done_t16.py` | `2ae1605c…` | `2ae1605c…` | MATCH |
| `run_one_t16.sh` | `a16b9a41…` | `a16b9a41…` | MATCH |

**7 of 7 MATCH.** The files that ran are the files that were frozen. Nothing in
this record rests on a file that drifted.

**Pre-registration preceded compute.** `ae20d137` is timestamped
2026-08-27T17:12:13Z; `T16_MC_c`'s solver banner records `Time : 17:30:06` and
`STATUS.T16_MC_c` records `started_utc=2026-08-27T17:30:06Z` — **18 minutes
after the freeze.** Rule 2 is met by the clock, not by assertion.

---

## 2. Completion — the strict rule (rule 4), read limb by limb from artifacts

`endTime` is `10000`, read from the case's own `system/controlDict`. The
registered field tuple is **`T U p_rgh phi`** — this rung's own, declared at
`mark_done_t16.py:76` (`NEEDED`), **not** the thermal-family tuple quoted in
`CLAUDE.md` rule 4, which is per-rung and is not lab-wide.

| # | limb | source read | result |
|---|---|---|---|
| L1 | `rc = 0` | `STATUS.T16_MC_c` (the wrapper's record, not inferred from the log) | `rc=0` **PASS** |
| L2 | exactly one `End` line | `T16_MC_c/log.solve` | 1 **PASS** |
| L3 | last time == `endTime` | last numeric dir `10000` vs `endTime 10000` | **PASS** |
| L4 | registered fields at `endTime` | `10000/` holds `T U alphat p p_rgh phi uniform` | all four present **PASS** |
| L5 | `ExecutionTime` count == `endTime` | 10000 lines vs 10000 | **PASS** |
| L6 | **age guard** — every field at `endTime` newer than the case's own `0/T` | `0/T` 17:30:06; `T U p_rgh phi` all 17:42:30 | all NEWER **PASS** |

**Six of six hold.** Time directories present: `0`, `9000`, `10000`.

**This table is NOT the registered grading path and does not substitute for
it.** Rule 2 fixes the grading path at the pre-registration commit; a hand
reading by a lane is evidence about what the block is hiding, and nothing more.
`T16_MC_c` is **BLOCKED**, not DONE, and no DONE marker was written.

---

## 3. What the case actually is

`T16_MC_c` is the **coarse** level of a three-level ladder. At this writing:

| level | state | evidence |
|---|---|---|
| `T16_MC_c` | landed, complete on a hand reading, **BLOCKED** by the marker | `STATUS.T16_MC_c`, `10000/` |
| `T16_MC_m` | **RUNNING** — not read beyond a directory listing, not touched | last time `2000` of `endTime 20000` |
| `T16_MC_f` | **not launched** — no `0/`, no `STATUS.T16_MC_f` | `T16_MC_f/` holds `0.orig` and mesh logs only |

**No Roache triple exists.** Under rule 5 no row is gated and no GCI is quoted.
The rung is `PENDING` on the triple independently of §4's defect: even a
repaired marker would not produce a gate verdict today.

---

## 4. THE DEFECT — the frozen marker cannot pass ANY real OpenFOAM run

**`mark_done_t16.py` refuses `T16_MC_c` at exit 2 with:**

> `REFUSE: log.solve of T16_MC_c carries crash token(s) 'Floating point exception' -- R-RC forbids inferring success past evidence of a crash (K0d L1), with or without an rc record`

**The token is matched against the OpenFOAM start-up banner, which says the
opposite of what the matcher takes it to mean.** The single occurrence in a
7,029,076-byte log is **line 18**:

> `trapFpe: Floating point exception trapping enabled (FOAM_SIGFPE).`

That line announces that floating-point-exception trapping is **ENABLED**. It
is printed by **every** OpenFOAM 2606 run on this box before the first
iteration, on clean runs and crashed runs alike — verified against three
unrelated real logs (`T16_MC_c`, `T5_runs/L_m`, `T5_runs/T5_CUBE_f`): the
banner line is present in all three, and `FOAM FATAL ERROR` in none.

**Mechanism, cited by line.** `mark_done_t16.py:97-98` declares

```
CRASH_TOKENS = ("FOAM FATAL ERROR", "FOAM FATAL IO ERROR", "Segmentation fault",
                "Floating point exception", "Aborted", "signal ")
```

and `crash_tokens_in_log()` at `:101-113` tests each token with a bare
substring match, `if tok in line`. The refusal at `:141-145` fires **before**
the rc branch and before any physics limb is read, so it is unconditional and
un-appealable. **The consequence is total: no T16 case can ever be marked DONE
through its own registered marker**, and that is all three levels, not one.

**Why the selftest did not catch it, which is the deeper half.** The selftest
passes — 0 failed, under `python3` and `python3 -O` identically, exactly as the
pre-registration's §11 records. It passes because its fixture log is
synthesised at `:234-238` as

```
body = "ExecutionTime = 1 s\n" * n            # + optional FOAM FATAL ERROR + End
```

— **a log with no OpenFOAM banner.** No arm of the selftest ever presents the
reader with a real clean OpenFOAM log, so the one input that breaks it is the
one input it is never given. The fixture is unrealistic in precisely the
dimension the check operates on.

This is standing rule 3's doctrine inverted. Rule 3 says a reader that has not
been shown able to see a non-zero cannot certify a zero. Here a reader that has
never been shown a **real clean log** certifies a crash. The control that was
owed — and is owed by every crash-token reader — is a planted **clean** OpenFOAM
banner that the reader must pass, standing beside the planted crash it must
refuse.

**Scope, measured rather than assumed.** `mark_done_t16.py` is the **only**
marker in the repository carrying a `CRASH_TOKENS` list and the only one
carrying the `Floating point exception` token (`grep -rl` over every
`mark_done_*.py` under `verification/`). No other rung's completion record is
affected by this defect and none is called into question by it.

**NOT REPAIRED HERE.** The file is frozen at `ae20d137` and rule 6 forbids
editing it; a measurement script is additionally read as a diff by the
supervisor personally before its output is believed
(`SUPERVISION_CHARTER` §3 check 1), and that check is not delegable. This lane
changed no frozen file, proposed no patch, and launched no solver. Docketed.

---

## 5. The `ExecutionTime` tension did NOT become load-bearing

`CLAUDE.md` rule 4 lists the `ExecutionTime` count among the strict conjuncts;
the L-342 ruling classes infrastructure fields as never able to refuse a grade
on their own. That contradiction is on Sanaa's desk and is not this lane's to
settle. **It did not have to be settled here:** `T16_MC_c`'s count is 10000
against an `endTime` of 10000 — the limb **passes on either reading**, so
nothing in this record depends on which way the desk rules. For completeness,
this rung's frozen marker takes its own position at `:197-201` (the count is
INFRASTRUCTURE, read and reported, never entering `fails`), and it took that
position **before compute**, at the freeze.

---

## 6. Cost — rule 12, `T16_MC_c`

| | |
|---|---|
| **pre-registered** | POINT **16.611** core-min; ceiling 25.062; cap **40** (`T16_registered.json`, `cases.T16_MC_c`) |
| **actual, MEASURED** | **12.400** core-min — `wall_s=744` × `ranks=1` ÷ 60, from `STATUS.T16_MC_c` |
| gross vs cleaned | **gross == cleaned.** 744 wall s, far under the 3,600-s stall convention; one continuous solve, `ExecutionTime` count 10000 == `endTime` |
| **ratio actual/predicted** | **0.747** |
| dollars | predicted $0.0142; actual **$0.0106** — **DERIVED, NOT MEASURED**, at the owner-stated $0.0513/core-h (`COMPUTE_BUDGET_CHARTER` §5: the box cannot read its own billing) |
| cap | not approached — 31.0 % of the registered 40 core-min |

**Gap attribution: misprediction, favourable, and a small one.** The registered
POINT rate `3.8932e-06` core-s per cell-iteration was measured on a scratch copy
of **this exact case on this box** (prereg §8), which is the strongest basis the
lab has, and it still over-predicted by 34 %. **Contention is not claimed**: no
per-level free-core reading was taken beside the wall time, so it cannot be
separated, and it is not offered as an explanation.

**WASTE: none on this row, and the distinction matters.** The 12.400 core-min
bought a complete converged coarse-level solution which is on disk at
`10000/` and is gradeable the moment the §4 defect is repaired — the marker
reads artifacts, so no re-run is implied. Had the repair required re-running
the case, this row would have become waste in full; it did not, and it is not
named as waste (`COMPUTE_BUDGET_CHARTER` §6).

---

## 7. Planted-zero control (rule 3)

**Not run, and not claimed.** The comparator `analyse_t16.py` — which the
pre-registration names at §11 as the only function that writes a verdict, and
which carries the rung's planted-zero controls — was **not** executed, because
no Roache triple exists (§3) and no row is gradeable. **No zero appears
anywhere in this record**, so no zero rests on a reader whose reach was not
established. When the triple completes, the controls are owed before any row is
believed.

---

## 8. Disclosures

- **`T16_MC_m` was not touched.** It was live throughout this grading; the only
  reads taken against it were a directory listing and its `controlDict`.
- No frozen file was edited (rule 6); no comparator or marker was patched; no
  solver was launched; nothing was placed in `verification/queue/`.
- Nothing was sent, filed, uploaded, posted or registered outside this box
  (rule 7).
- Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit from the tail
  maximum row-opener.
