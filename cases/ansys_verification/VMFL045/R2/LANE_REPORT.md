# VMFL045-R2 — opus-4.8 lane report of record: FREEZE-VERIFY message fix (Ruling item 2)

**Channel note:** lane→supervisor `SendMessage` is one-way and fails (L-306). This
file is the report of record; its commit sha is the handoff.

**Task:** the supervisor's ruling ACCEPTED R2 with one required fix before compute
unlock — the comparator's `--verify-frozen` success line named two different files as
the same thing (`grade_vmfl045.py` while `SELF_REL` is `grade_vmfl045_r2.py`). Fix it
as a CLASS, re-freeze as a pre-compute amendment, re-run the checks, and STOP before
launch. Done. **Compute NOT launched.**

## 1. What I did

1. **Re-verified the pre-compute condition myself** before touching anything:
   `verification/runs/ansys_verification/VMFL045/R2/` **ABSENT**; no R2 solver running
   (the only solver processes visible are two `buoyantBoussinesqSimpleFoam` running
   since Aug21 — unrelated heat-transfer long-runs, not VMFL045). No recent commit
   created an R2 run tree. Checked at `2026-08-25T02:15:10Z`.
2. **Amended the comparator** `cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py`:
   the `--verify-frozen` success line now prints `os.path.basename(SELF_REL)` instead
   of the literal `grade_vmfl045.py`, so the printed name is DERIVED from the path
   constant and cannot go stale on a future retarget (class fix, not instance). The
   four docstring usage lines are corrected to the real R2 filename the same way.
   This is the **FOURTH path-related change** in the R2 comparator (`SELF_REL`,
   `RUN_ROOT`, `OUT_JSON` were the first three).
3. **Committed the comparator** (private-index protocol; base sha captured in the
   committing invocation; HEAD-blob change guard; single-path tree assertion; ref CAS;
   post-commit verify — only my path in `HEAD~1..HEAD`).
4. **Appended a dated pre-compute AMENDMENT 1** at the foot of R2's
   `PREREGISTRATION.md` (freeze v1.0→v1.1; "lines whose number changed above the
   section: 0"), re-checking the run-dir absence with `date -u` in the **same shell
   invocation** as the append (`2026-08-25T02:20:06Z`). The amendment records the
   change and new blob sha, **STRIKES** the §3/head "three path constants" and "only
   these three lines differ" language, states the correct count (four path-related
   changes), and asserts no gate/band/level/`endTime`/solver/zone/Roache
   quantity/plant/classifier/cap/label moves. Committed separately (private index).
5. **Re-ran the checks** against the final HEAD.
6. **STOPPED. Did not launch.**

## 2. What I measured (shas and numbers, no logs)

| item | value |
|---|---|
| OLD comparator blob (pre-fix, at `3467dd25`/`4b3f512e`) | `a282f00d267119f55f3f6a39b69cb693309595e7` |
| **NEW comparator blob (the grading path, re-frozen)** | **`382ff4975801c5911277fb463076d1a14dd813c6`** |
| comparator freeze commit | `946bbf24e955c8601e5b38de3d06a0853e9ccfe1` |
| PREREGISTRATION.md blob after AMENDMENT 1 | `592e872b5738f33cbbbb5eac6440e7174cbed95e` |
| PREREGISTRATION amendment commit (final HEAD) | `ae678955e84491c2251174254713a95cf4eb38f1` |
| comparator on-disk sha256 (first 16) | `8d876e6d447a176c` |
| bare `grade_vmfl045.py` occurrences remaining in comparator | 0 |
| tree-diff at each commit | exactly one path, mine |
| `python3 -m py_compile` | OK |
| `--selftest` (final) | **45 ok, 0 FAIL** |
| `--verify-frozen HEAD` (final) | **exit 0**; success line names `grade_vmfl045_r2.py` on BOTH sides |
| R2 run dir at every check (`02:15:10Z`, `02:20:06Z`, `02:20:42Z`) | ABSENT |

The fixed line now reads (subject correctly identified):
`FREEZE VERIFIED: grade_vmfl045_r2.py is byte-identical to HEAD:cases/ansys_verification/VMFL045/R2/grade_vmfl045_r2.py (sha256 8d876e6d447a176c)`.

## 3. Status / verdict

**PENDING** — VMFL045-R2 is not yet run; zero solver compute. The required fix is
complete and the grading path is re-frozen at blob
`382ff4975801c5911277fb463076d1a14dd813c6` (commit `946bbf24`), recorded by dated
pre-compute AMENDMENT 1 (commit `ae678955`). **Compute is NOT launched.** Per the
ruling, check 4 (personal re-verification of the changed grading path) is the
supervisor's, and a changed grading path re-opens it: I am STOPPED and awaiting the
supervisor's re-verify and compute unlock.

**Cost of this step:** 0.0000 core-minutes — no solver ran; selftest and
verify-frozen are pure Python control checks with no run tree.

## 4. What I could NOT verify

- Everything downstream of a run: mesh build, `topoSet` filling both zones, the live
  `Ma`/`volFieldValue.dat`, per-level plateau within 7.0e-3 s, observed order and
  shock position, and the 1% gate value itself. All remain findings to be measured
  after unlock, whatever they are.
- The supervisor's own check 4 (re-verifying the changed grading path and unlocking
  compute) — that is theirs, not mine, and I have not performed it.
- Nothing in the frozen gate, bands, three levels, `endTime`, solver, zones, Roache
  quantity or the 48-core-min cap changed; the Fluent-would-FAIL declaration and the
  p≈1-expected / p≈2-suspicious statements stand as frozen.
