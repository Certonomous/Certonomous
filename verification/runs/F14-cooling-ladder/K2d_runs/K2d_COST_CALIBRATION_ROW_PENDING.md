# K2d cost-calibration row — **PENDING**, composed and NOT LANDED

**Status: `PENDING`** (display/queue state, `VERIFICATION_CHARTER.md` §9 —
*not* a softened `GATE FAIL`). The row below is complete and ready. It is not
in `docs/COST_CALIBRATION.md` because **the ledger currently refuses every
team's append at exit 7**, for a cause that is not this rung's and not this
team's to rule on.

**This file exists because the scratchpad is not a handoff channel (L-186).**
It lives beside the rung it belongs to so the row survives the session. Land it
unchanged the moment the block below clears.

---

## THE BLOCK — a lab-wide rule-12 block, third occurrence, already ruled once

`scripts/append_record.py` audits **HEAD's whole blob** before appending
(clause 1b). One line fails the audit:

- `HEAD:docs/COST_CALIBRATION.md:522`, id `C-20260910T230023.521144Z-mrfr1a1`
- landed by **cfd** in commit `6af542b6d` (MRF_R1 verdict row, 2026-09-10)
- the body `mrfr1a1` is **7 characters and non-hex**, so it fails
  `TOOL_ID_BODY`; no id pattern parses it, yet it matches the id-bearing
  candidate shape — so the shape audit refuses.

**Measured, 2026-09-11:** `python3 scripts/append_record.py --path
docs/COST_CALIBRATION.md --rows <row> --allocate-id --rev HEAD --dry-run`
returns **exit 7**, writes nothing, and the worktree ledger is unchanged.
**Every team's `COST_CALIBRATION` append is blocked until this clears.**

**It has happened twice before and was ruled then.** `scripts/append_record.py`
already carries literal exclusions for `…-w4reanc` (dafoam) and
`…-vmfl046r5` (ansys) at `:724` and `:725`, whose comment records the identical
diagnosis — *"clause 1b … refused EVERY team's future COST_CALIBRATION append
at exit 7: a lab-wide rule-12 block"* — and the identical prevention:
**"a tool-form id is MINTED by `--allocate-id`, never hand-typed."** The cfd
row bypassed `--allocate-id` and hand-typed its id.

**WHY THIS LANE DID NOT FIX IT.** The 2026-09-07 precedent was **RULED BY
VERIFICATION**, not by the team that hit the block. The fix is an edit to
`scripts/append_record.py` — a shared gating instrument outside heat-transfer's
territory — and the register's own comment warns that an over-broad exclusion
"would silently admit FUTURE bad ids and hollow the smuggle guard". Choosing
between the two register edits is a judgement about another team's record.
**Surfaced, not taken** (standing rule 9).

**The narrow fix the precedent points to**, for whoever is entitled to make it:
one literal line in `KNOWN_EXCLUDED["docs/COST_CALIBRATION.md"]`, in the exact
form of its two neighbours —
`r"^\|[ \t]*C-20260910T230023\.521144Z-mrfr1a1[ \t]*\|"` — after measuring that
it matches exactly one line. cfd may then append a correction row re-issuing a
valid id via `--allocate-id`. **This lane asserts neither; it measured the
block and stopped.**

## WHAT WAS AND WAS NOT VALIDATED ON THE ROW BELOW

The refusal fires in the shape audit, **before** the row itself is fully
validated, so the row carries only these checks: it is **one line**, it has
**exactly 10 cells** matching the header's 10 columns, it contains no embedded
pipe or newline, and the tool **did** mint it an id
(`C-20260911T154345.221242Z-af162fbe`) on the dry run. **Full format validation
did not run.** Re-run `--allocate-id` when landing — do not paste the minted id
above, which was a dry-run reading and is not reserved.

---

## THE ROW

```
| {{ALLOCATE_ID}} | 2026-09-11 | heat-transfer | **K2d RETIRED — the three-level rack-row ladder (F14 DC-cooling spine), realising the owner-approved K2a module.** Prereg FROZEN `e7979e29b706c1f4b91404c04731f29a80f128bd`; grading path pinned by blob in its §9 and all four pins verified byte-exact on disk at retirement. Levels built at 58,368 / 196,992 / 664,848 cells (r = 1.5 in three directions). **RUNG VERDICT `BLOCKED` on a defective frozen grading path; every registered quantity `G1`–`G4` at ALL THREE LEVELS `NOT A RESULT`; `K2d_L3` `NOT A RESULT`** (rule 4 fails on five of six conjuncts). **THIS ROW IS A COMPLETED PROCESS ONLY IN THE SENSE THAT THE RUNG IS CLOSED — NO RESULT WAS BOUGHT.** Two blockers, both on the pinned path and both independent of the timeout that triggered the triage: (1) the frozen document registers `T_in,max` and `U_ha` as in-pass function-object output at `:290` and `:413`, and `build_k2d.py` emits **no function objects** — `grep -c functions` = 0 on all three built `system/controlDict`, no `postProcessing/` anywhere under `K2d_runs/`, so `G-CYCLE` had no input at any level and the series cannot be reconstructed (fields written only at `endTime`); (2) `analyse_k2d.py:613-619` is a two-branch stub — `--selftest` or a hardcoded `EXIT_REFUSE` — whose `main()` never reads a case directory, with 31 green selftest arms wired to nothing. §2d.1 repair DECLINED: plausibly satisfiable, buys nothing, every level reruns regardless. | **§7.1 POINT ladder 1,100 core-min**; carried bracket **1,150–1,650**; cap **1,650**. **Addendum 3 §16.2 re-derived the ladder to 247.0 core-min** from L1's rate and that re-derivation is what the L3 hang guard was sized on. Per level, §7.1 POINT / §16.2 re-derived: L1 **33** / 15.667-measured; L2 **167** / **52.9**; L3 **900** / **178.5**. | **689.734 core-min, MEASURED** from `STATUS.K2d_L*` (wall s × ranks ÷ 60, all 4 ranks): failed launch **0.067** (1 s), L1 **15.667** (235 s), L2 **138.400** (2,076 s), L3 **535.600** (8,034 s). **$0.590 DERIVED** at $0.0513/core-h, c7a.4xlarge, reported-by-owner — **derived, never measured**; the box cannot read its own billing (`COMPUTE_BUDGET_CHARTER.md` §5). | **154.134 core-min** — charter §2's cleaned definition, the 3600-s stall rule removing L3's 8,034 s row. **$0.132 derived.** Stated for format compliance only and it is NOT the useful figure here: see the waste line in gap attribution, because cleaning removes what was never solver cost while **every** core-minute in this row was solver cost that bought nothing. | **NOT COMPUTABLE — a ladder/predicted ratio would be a false efficiency.** 689.734/1,100 = 0.627× reads as 'came in under budget' and the rung produced no gradeable row and ran only 33.17 % of L3's registered iterations. Per-level ratios, which ARE computable and are the calibration content: **L1 0.475×** vs §7.1; **L2 0.829× vs §7.1 but 2.617× vs §16.2's re-derivation**; **L3 1.79× vs §7.1 and 9.05× vs §16.2** on the completed-run figure implied by its own measured rate (535.600 for 33.17 % → **1,615 core-min** projected complete — a PROJECTION, not a measurement). | **WASTE: 689.734 core-min — ALL OF IT — named separately and NOT absorbed into any ratio (`COMPUTE_BUDGET_CHARTER.md` §6).** Not merely L3's 535.600: L1 and L2 completed (L1 rule-4 DONE, L2 3,000 iterations with an `End` line) and bought solves that **no instrument on the frozen path can grade**, so their 154.067 core-min is waste on the same ground. **MISPREDICTION, measured and separate from waste: the cost model was linear in cells and the rate is not.** `ExecutionTime` basis, contention removed: L1 **187,700** / L2 **93,986** / L3 **37,051** cell-iter/core-s — cost per iteration scales as **N^1.6–N^1.77**, not N^1.0. **CONTENTION, stated separately: 1.003 / 1.320 / 1.775** (`ClockTime`/`ExecutionTime`); L3 launched 02:36:58Z while L2 was still running to 02:48:02Z alongside T4e and a seven-rank `simpleFoam` job on 16 vCPUs. **THE CALIBRATION LESSON, and it is the L2 row: the miss was on disk before the expensive level launched and nobody read it.** §16.2 predicted 52.9 core-min for L2; `STATUS.K2d_L2` recorded 138.400 at 02:48:02Z — a **2.617×** miss written **eleven minutes after** L3 launched on a guard sized from that same falsified basis (178.5 ÷ 4 ranks = 2,678 s × 3 = **8,034 s**, hand-passed at `RETIRED_2026-09-11/watch_l3.sh:46-47`; `launch_k2d.sh:7` computes no guard and asserts nothing about the one it is handed). §7.3 registers L3 at **8 ranks / 20,250 s**; it ran at **4 ranks / 8,034 s**, while **L1 used §7.3's registered 1,485 s exactly** — so the departure is from a value the launcher had been using correctly one level earlier. **`note=HANG_GUARD_TRIPPED` in `STATUS.K2d_L3` is FACTUALLY WRONG** — written mechanically by `launch_k2d.sh:45` on any `rc=124`; the solver ran its last 194 iterations at 5.610 `ExecutionTime` s/it and died mid-iteration 995. A budget stop wearing a hang guard's name. **FORWARD CORRECTION, registered into the successor `K2f`:** cost model at N^1.6–N^1.77 with contention stated separately; ranks and guard from one registered table with the launcher asserting the handed value against the registered row and refusing otherwise; `writeInterval` well below `endTime` so a trip leaves a restart point (`writeInterval 3000` with `endTime 3000` is why 535.600 core-min vanished leaving zero fields). | Retirement recorded as **ADDENDUM 4 (§17)** at the foot of `docs/campaigns/F14-cooling-ladder/K2d_PREREGISTRATION.md`, appended under standing rule 6 with the 1,262-line prefix hash asserted identical before and after. Figures read from `verification/runs/F14-cooling-ladder/K2d_runs/STATUS.K2d_L1`, `STATUS.K2d_L2`, and `RETIRED_2026-09-11/STATUS.K2d_L3`; rates and contention from the `ExecutionTime`/`ClockTime` lines of each level's `log.solve`. `K2d_L3` and its `STATUS` were **MOVED, never deleted**, to `verification/runs/F14-cooling-ladder/K2d_runs/RETIRED_2026-09-11/` (log.solve sha256 `2731e614ab63019fcae12ef5085213e2501991aa5a7ca8515c8e686075eb55b0`, byte-identical across the move). Prior partial calibration for L1 only at Addendum 3 §16.5; this row supersedes nothing and corrects no existing row. |
```

---

## LANDED 2026-09-11 — this file is now HISTORY, not a pending row

**The row above IS IN `docs/COST_CALIBRATION.md`.** Do not append it again.

- **Allocated id `C-20260911T182256.192404Z-63d7559b`**, minted by
  `scripts/append_record.py --allocate-id`. The `{{ALLOCATE_ID}}` placeholder was
  carried through the tool unchanged and **no id was hand-typed** — hand-typing is
  the mechanism that caused the block this row waited out.
- **Landing commit `f81c5f545347f1320b72c5cc238bc6c3c134010b`.**
- **The block cleared at `bc5588bc7`** (verification), which excluded the exact
  offending id `C-20260910T230023.521144Z-mrfr1a1` from the shape audit. Re-measured
  here before writing anything: `--dry-run --allocate-id` returned **exit 0**.
- **Duplicate check run BEFORE the write and re-derived at commit time:** `K2d` and
  `689.734` — zero hits each over HEAD's blob.
- **The three things that survived the landing, unchanged:** the ladder ratio is
  `NOT COMPUTABLE` and not 0.627×; **all** 689.734 core-min is named as waste, not
  merely L3's 535.600; every dollar figure is **DERIVED, never measured**.

**The status line at the top of this file is superseded by this section**, which is
appended rather than replacing it, so the block it records stays legible.
