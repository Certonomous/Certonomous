# T5 results — PARTIAL, 2026-08-26T21:17Z: `T5_CUBE_c` and `H_c` DONE; the ladder is still running; no row graded

**Rung verdict: `PENDING`** — `verification/queue/heat-transfer/T5_CUBE_m_v2.json` … (M, P_m, L_m, F queued; `S_m` not enqueued). The frozen comparator wrote no verdict, verbatim (rc 0, `T5_runs/log.analyse_t5.20260826T211657Z.txt`):

```
T5_CUBE_c: done=True -- all clauses hold
T5_CUBE_m: done=False -- no STATUS file: nothing ran, or the launcher died before writing one
T5_CUBE_f: done=False -- no STATUS file: nothing ran, or the launcher died before writing one

No case has run: no rows are graded and no verdict is written.
```

No V, G or P row was printed, and the planted-zero control was not reached — the comparator stops before the plant when the triple is incomplete. Nothing is quoted here as a graded value. (The comparator's closing sentence "No case has run" is its fixed wording for an incomplete ladder; `T5_CUBE_c` has run, as its own first line says.)

Pre-registration `docs/campaigns/T-family/T5_PREREGISTRATION.md` (v1.7; AMENDMENTS 1–8; graded launches under AMENDMENT 6(b)/8(d), `run_one_t5.sh --no-detach` via the queue runner). Run tree `verification/runs/T-family/T5_runs/`. Written by a lab lane on the heat-transfer supervisor's order `[lab-attributed]`.

## 1. Frozen instruments, hashed before use

| instrument | freeze | `git hash-object` on disk | match |
|---|---|---|---|
| `T5_runs/analyse_t5.py` | blob `9c2c1d44` at `503a9a13` (supervisor's row; §16.9 sha256 `17703b78dad5`) | `9c2c1d44` | SAME |
| `T5_runs/mark_done_t5.py` | blob `a74ce20d` at `503a9a13` | `a74ce20d` | SAME |

`mark_done_t5.py --selftest`: 5 arms, 0 FAILED. `analyse_t5.py --selftest`: 16 arms, 0 FAILED; the one-way gate refusal fires under `-O`.

## 2. Completion — the strict rule, two of six graded cases

| case | wall s | ExecutionTime s | `Time =` lines / last | End | core-min | POINT (§11.1 Model B, AMENDMENT 2) | ratio | timeout s |
|---|---:|---:|---|---|---:|---:|---:|---:|
| T5_CUBE_c | 965 | 929.68 | 5000 / 5000 == endTime | yes | 16.083 | 45.6 | 0.353 | 8 208 |
| H_c | 994 | 958.66 | 5000 / 5000 | yes | 16.567 | 45.6 | 0.363 | 8 208 |

`mark_done_t5.py --root T5_runs T5_CUBE_c`, `H_c`: each `DONE` (rc 0); marker: `DONE T5_CUBE_c under the strict rule (rc=0, End, endTime, fields, age guard) at 2026-08-26T21:16:56Z`. In-wrapper `STATUS.T5_CUBE_c` / `STATUS.H_c`: `rc=0 … capped=0 checkMesh_rc=0 note=clean`, ranks 1.

## 3. FINDING — the `H_c` control is blind by construction (a registration defect, stated, not amended)

**What the pre-registration says `H_c` tests** (§5.6, verbatim): *"`H_c` runs the coarse level with `Gauss linear` on the solid laplacian, everything else identical, and the difference in the `h` and `T_sur` rows is REPORTED. … If `H_c` moves a graded row by more than its band, the scheme choice becomes a named uncertainty of this rung rather than a settled input"*; §16.5 (INTERPRETATION 12, ADOPTED): *"the `H_c` interface scheme is TESTED, not carried … Registered as an `H_c` twin at $0.04 derived — the best value in the rung: $0.04 to test rather than assume."*

**What was measured.** The only difference between the two cases' inputs is `system/epoxy/fvSchemes` lines 16–17: `laplacian(alpha,e|h) Gauss harmonic corrected` (T5_CUBE_c) vs `Gauss linear corrected` (H_c); `diff -rq` of `system/` shows no other file differing. At `5000/` the fields are **byte-identical** (md5, first 12 hex): `air/T` `c2cac072781e` = `c2cac072781e`; `air/U` `9981db36ef36` = `9981db36ef36`; `epoxy/T` `0b03589276e9` = `0b03589276e9`; `air/p_rgh` `b9dcf6142730` = `b9dcf6142730`. The supervisor's own measurement of `air/T` (md5 `c2cac072…`) is reproduced and extended to `epoxy/T` and `air/U`.

**Why, and what it means.** The edited scheme is the solid region's laplacian interpolation of `alpha` (thermal diffusivity). The epoxy is a single material with uniform `alpha`; the harmonic and linear interpolations of a uniform field are the same number at every face, so the solver assembles the identical matrix, and the identical iteration history follows to the last bit. The scheme that §5.6 meant to test — the interface treatment under a 9:1 conductivity jump — lives in the coupled boundary condition and in the **fluid**-side `alphaEff` laplacian, neither of which `H_c` varies. **The control as registered cannot fire, whatever the answer; its result is not a PASS and not evidence that the scheme choice is settled.** Under `CLAUDE.md` rule 2 nothing is amended post-compute: the defect is recorded here, and any re-designed control is a new registration, not a rewrite of §5.6/§16.5. The 16.567 core-min bought a measurement of the control's blindness, which is named as such and not netted off.

## 4. Cost so far — rule 12

- Predicted (AMENDMENT 2 table, Model B): 45.6 core-min each; $0.0390 derived each.
- Measured: 16.083 + 16.567 = **32.650 core-min** (wall 965 + 994 s × 1 rank ÷ 60), gross = cleaned (no row over 3 600 s); contention present, not limiting: ExecutionTime/ClockTime 96.3 % / 96.4 % (box at 14–16 of 16 cores). Ratios **0.353 / 0.363**: misprediction of the per-cell-iteration rate on a 5.4e4-cell conjugate case (Model B carried T9a-D's rate). **$0.0279 DERIVED, NOT MEASURED** at $0.0513/core-h. Waste 0.000 core-min on these two cases; the 17:41Z `T5_C` crash (0 core-min, `crash_1741Z/`) is AMENDMENT 8's record. Ledger row: `docs/COST_CALIBRATION.md`, id assigned at commit; the rung's full row follows at completion.

## 5. What remains

`T5_CUBE_m`, `P_m`, `L_m`, `T5_CUBE_f` are queued (`_v2` entries); `S_m` refuses without `M`'s surface T. When all markers exist: `analyse_t5.py --root T5_runs` (P rows BLOCKED under §7.5(3) until the reference is on disk and digitised; V/G rows gradeable), then this file is rewritten with every row.

---

# APPENDED 2026-08-26T22:14Z — `T5_CUBE_m` DONE under the strict rule; the frozen comparator still writes NO verdict; `X_2d` is UNGRADED BY REGISTRATION; `S_m` cannot be enqueued

**Lines whose number changed above this section: 0** (appended to a copy of the
HEAD blob, verified byte-identical to the worktree copy before the append).
**Rung verdict: still `PENDING`.** Written by a lab lane on the heat-transfer
supervisor's standing order `[lab-attributed]`.

## 6. Frozen instruments, hashed on disk BEFORE this session's comparator runs

| instrument | registered blob | `git hash-object` on disk at 22:13Z | match |
|---|---|---|---|
| `T5_runs/mark_done_t5.py` | `a74ce20dfea675c7865742976cf6467287a2ed78` (§16 / `503a9a13`) | `a74ce20d…` | **SAME** |
| `T5_runs/analyse_t5.py` | `9c2c1d44cfebe6b3baaebc0ad53036b87d1f07d9` (AMENDMENT 3, in force; §16.9's original row reads `17703b78dad5`) | `9c2c1d44…` | **SAME** |
| `T5_runs/run_one_t5.sh` | `313df45c85b3de916ccf75a1ae38398656b7baa9` (§16.9) | `313df45c…` | **SAME** |

Prereg blob verified present: `git cat-file -e 299296a2:docs/campaigns/T-family/T5_PREREGISTRATION.md` → exists.

**A freeze-set mismatch IS on record and is reported, not worked around**:
§16.9 registers `T5_runs/digitise_t5.py` at blob `e55d6208c511`. HEAD carries
`e55d6208` — the frozen bytes are intact — but the **worktree copy on disk hashes
`ea789ea6`** (`git diff HEAD --numstat`: **+929 / −1**), and a third variant
`digitise_t5.A7_PROPOSED.py` (`001d81bc`) sits beside it. No grade in this
section reads the digitiser, so nothing here is refused by it. Inspected, never
reverted (rule 10); raised for a landing decision.

## 7. Completion — the strict rule, `T5_CUBE_m`

`STATUS.T5_CUBE_m` (written in-wrapper by the frozen `run_one_t5.sh`, ranks 1):
`rc=0 wall_s=4539 core_min=75.650 timeout_s=95472 capped=0 checkMesh_rc=0 note=clean`.

| case | wall s | ExecutionTime s | `Time =` / `ExecutionTime` lines | last time | endTime | End | fields at 5000 | age guard | core-min | POINT | ratio | timeout s |
|---|---:|---:|---:|---|---|---|---|---|---:|---:|---:|---:|
| `T5_CUBE_m` | 4 539 | 4 490.88 | 5 000 / 5 000 | 5000 | 5000 | yes (1) | `air/{T,U,alphat,k,nut,omega,p,p_rgh,phi,rho}`, `epoxy/{T,p}` | `5000/air/T` 22:13:02Z **newer than** `0/air/T` 20:57:21Z | **75.650** | 530.4 | **0.1426** | 95 472 |

`python3 mark_done_t5.py T5_CUBE_m` → `DONE      T5_CUBE_m`, **rc 0**; marker
`DONE.T5_CUBE_m` written. Cap not approached (4 539 / 95 472 = 4.8 %);
`capped=0`.

## 8. The frozen comparator, run exactly as registered — it writes NO verdict, recorded verbatim

`python3 analyse_t5.py --root .` (blob `9c2c1d44`), rc **0**, log
`T5_runs/log.analyse_t5.20260826T221331Z.txt`, printed in full:

```
T5_CUBE_c: done=True -- all clauses hold
T5_CUBE_m: done=True -- all clauses hold
T5_CUBE_f: done=False -- no STATUS file: nothing ran, or the launcher died before writing one

No case has run: no rows are graded and no verdict is written.
```

**This is the expected finding on a partial C/M/F triple and it is recorded as
printed, not argued with.** No V, G or P row exists; the planted-zero control
(§9, `PLANT = 1.234e-03`) was not reached — the comparator stops before the plant
while the triple is incomplete; **no number from this rung is quoted anywhere as
a graded value.** The closing sentence *"No case has run"* is the frozen file's
fixed wording for an incomplete ladder and is now false of two of the three
levels, as its own first two lines say; the substantive claim it carries — *no
rows are graded and no verdict is written* — is correct and is what governs.
Nothing is amended (rule 6).

Two of the three graded levels now hold. `T5_CUBE_f` has never launched: its
queue entry `T5_F_v2.json` is still held by the queue runner's box-busy ceiling.

## 9. `X_2d` — UNGRADED BY REGISTRATION; no precursor check exists in the frozen comparator

**The check asked for.** Whether the frozen `analyse_t5.py` (`9c2c1d44`) exposes
a precursor check for `X_2d` — a Re_θ crossing or station-selection arm.

**The answer, measured.** **It does not.** A case-insensitive grep of the whole
frozen file for `x_2d|x2d|re_theta|station|precursor|inflow` returns **0
matches**; `LEVELS = ("c", "m", "f")` (l.26) and `main()` (l.393–412) accepts
only `--selftest`, `--drive-oneway-violation` and `--root`, and under `--root`
loops over `T5_CUBE_{c,m,f}` and nothing else. **There is no precursor arm to
run, so none was run and no grade is invented.**

The Re_θ crossing and station selection DO exist as arithmetic — but in
`map_inflow_t5.py`, which AMENDMENT 6(a) states in terms is **NOT in the §16.9
freeze set** ("an owed instrument"). Its executed iteration is on record in
`T5_runs/T5_INFLOW_LOG.md` (Re_θ = 660 crossed at `x/H` 63.790 → plane
`x_p/H` 55.790 → mapped station `x/H` 56 at Re_θ 592.1). **A non-frozen
instrument's output is not a grade**, and it is cited here as provenance for the
inlet map only.

**`X_2d` therefore stands as AMENDMENT 1 registered it: UNGRADED.** Its
strict-rule numbers, and nothing more:

| case | rc | wall s | ranks | core-min | POINT (AMENDMENT 2) | ratio | timeout s | marker |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `X_2d` | 0 | 313 | 1 | **5.217** | 26.4 | **0.198** | 4 752 | `DONE.X_2d` — "under the strict rule (rc=0, End, endTime, fields, age guard) at 2026-08-26T16:58:41Z" |

The age datum for `X_2d` is `0/**/U`, not `0/**/T` (AMENDMENT 1: a `simpleFoam`
precursor carries no `T`). The runner-written `X_2d/STATUS.T5_X_2d` remains
AMENDMENT 1's false bookkeeping file, excluded from every completion judgement
and left in place undeleted.

## 10. `S_m` — the queue entry CANNOT be dropped; added core-min = 0

§8 (DS) registers `S_m` and AMENDMENT 8(d) states *"`S_m` is NOT enqueued: its
launcher refuses without `M`'s surface T."* With `M` now DONE that clause is
satisfied — **and the case still cannot be enqueued, for a second reason the
amendment does not name.** `build_t5.py` refuses `S_m` **twice**:

1. l.575 — `"%s (constant-T arm) needs --s-m-tsurf = area-averaged conjugate
   surface T from T5_CUBE_m (S8 DS); it is not built before T5_CUBE_m has run"`.
   This one is now satisfiable: `M` is DONE and its conjugate surface `T` is on
   disk at `T5_CUBE_m/5000/epoxy/T` and `5000/air/T`.
2. l.624 — `"S_m fluid-only meshing (remove epoxy cells) is not implemented
   until T5_CUBE_m has run"`. **This is a NOT-IMPLEMENTED branch, not a
   precondition**: the `else` arm of the conjugate `splitMeshRegions` step has no
   fluid-only meshing path at all. `M` having run does not supply one.

**Consequence, measured rather than asserted.** A drafted entry was validated and
**REFUSED**, verbatim:

```
REFUSED verification/runs/T-family/T5_runs/queue_drafts/T5_S_m_BLOCKED.json
    AGE-GUARD: cwd /home/ubuntu/Certonomous/verification/runs/T-family/T5_runs/S_m does not exist as a directory, so it cannot be shown free of a prior answer.

1 of 1 entry REFUSED.
```
(`python3 scripts/queue_entry_check.py`, rc 2.)

The draft is retained, **NOT enqueued**, at
`verification/runs/T-family/T5_runs/queue_drafts/T5_S_m_BLOCKED.json` — costs per
AMENDMENT 2 (`cost_core_min_estimate` 489.0, `cap_core_min_registered` 1467.0,
`--timeout 88020`), argv in AMENDMENT 6(b)'s `--no-detach` form, `prereg_commit`
`299296a29b30def2c9fec910b66a554b4f4f11cd`. **Core-minutes added to the
heat-transfer queue by this section: 0.0.** Building `S_m` needs a fluid-only
meshing path written into `build_t5.py` — a builder change outside the §16.9
freeze set, and the supervisor's call, not this lane's.

## 11. Cost — rule 12, `T5_CUBE_m`

- **Predicted:** 530.4 core-min (AMENDMENT 2 table, Model B `T5_CUBE_m` 8.84
  core-h × 60 at ranks 1); $0.4535 derived.
- **Measured:** **75.650 core-min** = 4 539 wall s × 1 rank ÷ 60
  (`STATUS.T5_CUBE_m`). **Gross = cleaned.** The 4 539 s row is over the
  3 600 s stall figure by the letter and **is not a stall**: `Time =` advanced
  monotonically to 5000 == `endTime` with 5 000 `ExecutionTime` lines and one
  `End`, and ExecutionTime 4 490.88 s = **98.94 %** of ClockTime.
- **Ratio 0.1426.** **$0.0647 DERIVED, NOT MEASURED** at $0.0513/core-h,
  c7a.4xlarge, reported-by-owner (`COMPUTE_BUDGET_CHARTER.md` §5).
- **Gap attribution — MISPREDICTION OF THE MESH SCALING, not contention and not
  waste.** Contention was present but not limiting (1.06 % ClockTime excess at
  ~14 of 16 cores). Model B priced c → m as **×11.63** (45.6 → 530.4 core-min)
  where the mesh grows **×4.04** (53 553 → 216 214 cells, air + epoxy from
  `log.checkMesh`); the box delivered **×4.70** (16.083 → 75.650). Per
  cell-iteration: **3.47e-06 s at 53 553 cells → 4.15e-06 s at 216 214 cells**,
  a 20 % cache-shaped rise — the same direction K0f measured (C-137) and an
  order of magnitude short of Model B's assumed super-linearity.
- **WASTE: 0.000 core-min on this case**, named separately
  (`COMPUTE_BUDGET_CHARTER.md` §6).
- **Carry forward:** price serial `chtMultiRegionSimpleFoam` on this box at
  **≈ 3.5e-06 s per cell-iteration below ~60 k cells and ≈ 4.2e-06 at ~220 k**;
  on that basis `T5_CUBE_f` (registered POINT 2 308.2 core-min) should land near
  **300–350 core-min**, which is a prediction this rung will score.

Ledger row for this case: `docs/COST_CALIBRATION.md`, id re-derived from the HEAD
blob at commit time (rule 11). C-140 covers `T5_CUBE_c` and `H_c`.

## 12. What remains

`P_m` was at `Time = 3597`/5000 at 22:13:46Z (ETA ≈ 22:33Z). `L_m` and
`T5_CUBE_f` are queued and held by the runner's box-busy ceiling. `S_m` is
blocked on a builder that cannot mesh it (§10). When the C/M/F triple is
complete, `analyse_t5.py --root T5_runs` grades the V and G rows; the P rows stay
BLOCKED under §7.5(3) until the digitised reference is on disk, and §10's
freeze-set drift on `digitise_t5.py` must be resolved before that reference is
believed.
