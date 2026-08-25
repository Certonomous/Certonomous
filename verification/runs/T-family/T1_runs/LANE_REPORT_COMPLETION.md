# LANE REPORT — T1b L4: comparator freeze against the pre-registration commit,
# and the planted-zero control built to its frozen specification

**Lane:** `lab-lane`, heat-transfer team. **Date:** 2026-08-25.
**Reported to:** heat-transfer-supervisor. **Delivery:** `SendMessage` to the
supervisor returned *"No agent named 'heat-transfer-supervisor' is reachable"*,
so under the supervisor's own fallback instruction this file is the **report of
record**. It was not sent to the chief (L-306).

**This lane issues NO verdict.** Everything below is evidence.

---

## 1. Charter §2d, CLOSED — the file about to grade the pool IS the file frozen

An earlier report by this lane hashed the comparators against **HEAD**, which is
not the test Charter §2d states: the grading path is fixed **at the
pre-registration commit**. That caveat is now closed.

The L4 pre-registration commit is
**`17209b50a61b981f6b8b9862cfaf9c45db8ca6bb`** (2026-08-21 18:14:22 Z) — the
single commit that introduced `docs/campaigns/T-family/T1b_L4_AMENDMENT.md`,
`analyse_t1b_L4.py` and `mark_done_t1b_L4.py` together.

sha256 of each blob **at that commit**, against HEAD and against the worktree:

| file | sha256 at pre-reg commit | prereg == HEAD == disk |
| --- | --- | --- |
| `analyse_t1b_L4.py` | `9698adb00e80441696efed3870e71792ea505eac070ebdb33c18825d9948e31d` | **YES** |
| `analyse_t1b.py` | `647d74121677e529f3e2ede1402f593c831aace598623d696550dbd849b2241e` | **YES** |
| `analyse_t1c.py` | `60893b28e284127f61b41842c520897a2202cb024d5a4d260272c6ee7e6c5135` | **YES** |
| `mark_done_t1b_L4.py` | `f75f4a819346e538e2326aa684176811984dbca54804c393e98497b48693a06e` | **YES** |
| `T1b_band.json` | `6914ce28a874eb007b29df0ff561bd8b01fa3d12f10c225900785faec36731b9` | **YES** |

`git log --all --full-history` on the three graders shows the only other commit
touching any of them is merge `89231930` (2026-08-22, Sanaa's paper uploads); the
equal hashes prove it carried them through unchanged. **No diff to produce.**
Nothing here changes what the rung is allowed to do next.

---

## 2. The planted-zero control, built to the frozen specification

**Spec:** `docs/campaigns/T-family/T1b_L4_PLANTED_ZERO_CONTROL_PREREGISTRATION.md`,
commit `3ae9e504`, sha256
`303924c1c1088559262996afe5aaf489205f8a07577422063fe3678c862b16f6` (verified
against the blob at HEAD before a line was written).

**File:** `verification/runs/T-family/T1_runs/planted_zero_control_t1b.py`, 510 lines.

Registered constants used exactly as frozen: `PLANT = 1.234e-03`,
`TOL_REL = 1.0e-06`, refusal exit `2`. Both readers are **imported** —
`analyse_t1b.measure` and `analyse_t1c.iterative_convergence` — never
reimplemented. **No frozen file was edited**; all four were re-hashed *after* the
control was written and run and remain byte-identical to their pre-registration
blobs (§1 above). The §2d.1 repair exception was not invoked.

### 2.1 Subject case: `R_10k_x`

Chosen because it is the only completed x case that both satisfies all six
completion criteria **and** carries its recorded marker (`DONE.R_10k_x`,
2026-08-24T15:59:47Z). `R_300k_x` satisfies the criteria equally but its missing
marker is an open supervisor decision, and the control should not carry a
dependency on one. `R_10k_x`'s checkpoints (18000 / 20000) also make it the
cheapest copy in the pool.

### 2.2 Self-test result — PASSED, 21/21

Synthetic scratch data only; no case directory read or written. It proves the two
decision functions (including refusal just outside `TOL_REL`); that the plant
lands **by line index** and is read back **from disk**; that the frozen reader
`analyse_t1c.read_internal` sees it and sees no change in untouched values; and
**both arms end to end on the real imported `iterative_convergence`**.

It carries a **mutation control**: a deliberately blind reader is caught by the
positive arm *while the negative arm stays happy*, and a deliberately noisy
reader is caught by the negative arm. Without it the control would be
unfalsifiable.

`analyse_t1b.measure` **cannot** be exercised on synthetic data — it runs
`postProcess` against a real mesh. The self-test says so rather than implying
coverage it does not have.

### 2.3 Three points the supervisor must see when reading the diff

**(a) A spec reading that needs confirmation.** The negative arm's *"copy the
field and read it back unmodified; the reader MUST report no change"* cannot mean
"run the reader on the case as it stands": the last two checkpoints of any real
case differ by a real physical amount, so "no change" would be unsatisfiable by
construction, while §4 of the spec predicts the control passes. It is implemented
as `analyse_t10a.py`'s own construction — its self-test builds *"two checkpoints,
identical; then the plant"* — by copying the **latest** `T` over the earlier slot
so the two checkpoints the reader compares are byte-identical and a correct
reader must return `max_change` **exactly 0.0**. This also makes **both** arms
exact equalities rather than inequalities. **If the supervisor intended the other
reading, this file must change.**

**(b) The plant for `measure()` had to be aimed, and this is a real trap.**
`measure` computes `Nu = D*grad*aeff / |T_wall - T_bulk|`. A **uniform** shift of
`T` **cancels exactly**, and a plant into a cell at another axial station changes
nothing — either would have reported a **false blindness** in a perfectly sound
reader. The plant therefore goes into the one cell `measure` uses for `T_wall`
(largest-`Cy` cell of the station's set), located from `measure`'s **own**
returned `station_xD` / `D_used` and the `Cx` / `Cy` its own `postProcess` wrote.
Nothing about the reader is reimplemented. A mis-aimed plant can only make the
positive arm **fail**, never pass falsely, and the assertion that `T_wall` shifts
by exactly the planted amount is itself the proof the aim was right. Station is
80 D (`T1B.STATIONS[-1]`), the station whose `Nu` the L4 row uses.

**(c) A hard guard, because two solvers are live.** `measure()` runs
`postProcess` and **writes into whatever directory it is handed**
(`log.writeCellCentres`, `Cx`, `Cy`, `V`). `assert_not_case_tree()` refuses
(exit 2) if the control is ever pointed inside `T1_runs`. Tested: pointing it at
`R_10k_x` exits 2 with *"it copies and never touches. Nothing was written."*

### 2.4 Nothing was touched

The only files written inside any case directory in the twenty minutes covering
this work are `R_100k_x/log.solve` and `R_30k_x/log.solve` at 01:29:00 Z — the two
live solvers' own output. Both pids remained running throughout (450274 at
3-04:00 elapsed, 488219 at 3-03:04). `__pycache__` for the imported modules was
checked read-only and is **valid against source**, so no stale-`.pyc` inversion of
the mutation controls.

---

## 3. Cost

Self-test is sub-second — well inside the frozen spec §6 estimate of *under 1
core-minute*. The **real run has not been made**, so no actual-versus-estimate row
is due yet; at completion it lands in `docs/COST_CALIBRATION.md` under CLAUDE.md
rule 12, in core-minutes, with any dollar figure marked **derived, not measured**.

---

## 4. Status — and what is explicitly NOT done

**PENDING: the supervisor's personal read of the diff.** The control has **not**
been run against `R_10k_x` or any pool case. Per `SUPERVISION_CHARTER.md` §3 that
read is the supervisor's personally and cannot be delegated; **this lane's testing
is evidence, not that read.** No verdict is issued here, and the control's own
passing would not be a rung verdict in any case — per the frozen spec §2 it can
only ever turn a number into `NOT A RESULT`, never into a `PASS`.

Carried forward from this lane's earlier report and **not** this lane's to rule
on: `R_300k_x` satisfies all six completion criteria and lacks only its marker;
`T9aH_runs/run_chain_t9aH.sh:10-11` registers a real 300 core-second cap with no
enforcement instrument at all (actual spend 0.28 core-s, ratio 0.0009 — no
overrun, nothing reportable under rule 12).

**SUBMISSIONS REMAIN PARKED.** Nothing here was sent anywhere.

---

# ADDENDUM — 2026-08-25: THE REAL RUN. Control **PASSED**, exit 0.

Appended after the supervisor discharged the `SUPERVISION_CHARTER.md` §3 check 1
diff read personally, ratified the negative-arm spec reading and the subject
choice, and authorised the run. Nothing above this line was altered; **lines
whose number changed above this section: 0.**

Command: `planted_zero_control_t1b.py` (no arguments; production path, no reader
injected). Subject `R_10k_x`, station 80.0 D. Run 2026-08-25 01:34:41–01:34:54 Z.

## A1. `analyse_t1c.iterative_convergence` — the reader that gates Roache step (1)

| arm | recovered | expected | outcome |
| --- | --- | --- | --- |
| NEGATIVE (two byte-identical checkpoints) | `0.0` exactly | `0.0` | **not noisy** — `state=CONVERGED`, `between=('18000','20000')` |
| POSITIVE (plant read back from disk) | `0.0012340000000108375` | `0.0012340000000108375` | **not blind** — exact equality, `state=NOT_CONVERGED` |

**Planted:** `18000/T` **line 24**, pre-plant value **`299.9999999999995`**
(cell index 0). The state flip `CONVERGED → NOT_CONVERGED` on a single planted
cell is itself informative: the reader is sensitive at the level at which it
gates.

## A2. `analyse_t1b.measure` — supplies Nu, f, u_tau, y+. **First exercise of this arm ever.**

| arm | recovered | expected | outcome |
| --- | --- | --- | --- |
| NEGATIVE (independent unmodified copy) | `0.0` exactly, on both `T_wall` and `Nu` | `0.0` | **not noisy** — `Nu` bit-identical at `32.576755397128444` |
| POSITIVE (aimed plant) | `0.0012340000000108375` | `0.0012340000000108375` | **not blind** — exact equality on `T_wall` |

**Planted:** `20000/T` **line 209738**, cell **209714** of 209920, pre-plant
value **`300.620284378675`**. `Nu` moved
**`32.576755397128444` → `32.44621428379953`** (Δ `-0.13054111332891694`, −0.40 %).

The aim was correct: `T_wall` shifted by *exactly* the planted float change, which
is the assertion that proves the aim rather than assuming it.

## A3. Exit code

**`0`** (`EXIT_OK`). No refusal path was taken. Printed verdict: *"PASSED — both
readers saw the plant and neither invented one."*

**This is not a rung verdict.** Per the frozen pre-registration §2 and §4 the
control arms an existing gate; it does not create one, and it can only ever turn
a number into `NOT A RESULT`, never into a `PASS`. The §4 prediction — that both
readers would see the plant and the negative arms report no change — is
**scored CORRECT**.

## A4. Nothing was written into any case directory

Established by snapshot, not by assertion. All 1053 files under `T1_runs/R_*`
were recorded (path, `mtime_ns`, size) before the run and again after.

- **1053 files before, 1053 after — no file created, none deleted.**
- **The only entries that changed are `R_100k_x/log.solve` and
  `R_30k_x/log.solve`** — the two live solvers' own output, which advances on its
  own while they run.
- The differ was itself given a **planted control** (a one-character change in a
  copy of the pre-snapshot) and detected it, so the short change list is a real
  result and not a blind reader — the same discipline this control exists to
  enforce.
- **Both solvers still running** after the run: pid 450274 at 3-04:06:25 elapsed,
  pid 488219 at 3-03:10:45. Neither was touched, signalled or renice'd.
- The control removed its own scratch: no `t1b_plant_*` directory left behind.
- The three frozen graders re-hashed **after** the run and remain byte-identical
  to their blobs at pre-registration commit `17209b50`.

## A5. Cost — estimate versus actual (CLAUDE.md rule 12)

| | value |
| --- | --- |
| pre-registered estimate (frozen spec §6) | **under 1 core-minute**; $0.0009 derived |
| measured wall | **12.63 s**, single continuous run |
| ranks | **1** (serial Python; `postProcess` is serial, and there is no `decomposeParDict` anywhere in this territory) |
| **actual** | **0.2105 core-minutes** = 0.003508 core-hours |
| **ratio actual / predicted** | **0.21** against the ≤1 core-min ceiling |
| dollars | **$0.00018, DERIVED at $0.0513/core-h, not measured** — the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5) |
| waste | **none.** No stall; no row approaches the 3600-s rule. Gross = cleaned |
| gap attribution | **estimate was a conservative ceiling, not a miss.** Six `postProcess` invocations on a 209,920-cell mesh plus ~340 MB of scratch copying came in at about a fifth of it. The honest lesson for the next estimate is that a copy-and-read control on a 2·10⁵-cell case is a **~0.2 core-minute** item, not a ~1 core-minute one |

Row not appended to `docs/COST_CALIBRATION.md` by this lane: that ledger is
written across teams and the row is the supervisor's to place. Figures above are
ready for it. **The number must be re-derived at commit time** — the maximum
existing `C-` number is **52** while the distinct row count is **7**, exactly the
divergence CLAUDE.md rule 11 warns about, so the next id is `C-53` *only if it is
still 52 when the row lands.*

## A6. What this control still cannot see

Unchanged by the run, and worth keeping beside the PASS:

- **Whether either reader is CORRECT.** It establishes that they are not blind and
  not noisy — that their zeros are real zeros. A reader that sees a difference and
  then computes the wrong `Nu` passes this control.
- **The other fourteen levels.** Only `R_10k_x` was exercised. The control was not
  run against, and says nothing about, the other fifteen cases in the pool.
- **Any grader outside the T1b chain.** The frozen spec §5 list stays **OPEN**, as
  a lead and not a finding.

**The pool was NOT graded.** `R_30k_x` and `R_100k_x` are still solving, the
comparator refuses without all sixteen markers, and the marker decision is the
supervisor's. **SUBMISSIONS REMAIN PARKED.**
