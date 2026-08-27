# Commit-size guard — pre-registration

**Owner:** cfd-supervisor (tooling). **Build item:** Sanaa's standing directives
2026-08-27T16:54Z §1, *"pre-commit guard blocks >50 files or >5 MB without a manifest"* and
*"logs and attempt dirs stay out of git"*. **Artifact:** `scripts/check_commit_size.py`.
**This document is the frozen behaviour spec; it is written BEFORE the guard, so the guard
cannot be shaped to pass its own test.** Every clause ships an L-314 planted-failure proof.

**Named instance this exists to catch:** heat-transfer's `05241ab2` — 172 files, 3.2 M lines
of `log.solve`, landed with no manifest. Not a rebuke; it is the measurement that sized the
thresholds.

## 1. What it does

Reads a **tree** (a private-index `write-tree` result, or `HEAD` vs a candidate tree) and
**REPORTS** its verdict. It never kills, never deletes, never touches git, never writes into
the index. Exit codes: **0** accept, **2** refuse. It is invoked by the committer before
`commit-tree`; the caller MUST test the exit code.

## 2. Refusal clauses — each independent, each separately named in the output

| clause | refuses when | rationale |
|---|---|---|
| `COUNT` | > **50** files added or modified | Sanaa §1 |
| `BYTES` | > **5 MB** total added bytes | Sanaa §1 |
| `LOGS` | any path matching `log.*`, `*/log.*`, `*.log` | logs stay out of git (§1) |
| `ATTEMPT` | any path matching `attempt*/`, `*_attempt*/`, `scratch/`, `__pycache__/` | attempt dirs stay out of git (§1) |

**The manifest exemption applies to `COUNT` and `BYTES` ONLY.** A commit may exceed either
threshold if it carries a manifest — a tracked file in the same tree naming what is being
landed and why, one line per group, with a total. **`LOGS` and `ATTEMPT` are NOT
exemptible by manifest**: a manifest explains bulk, it does not make a solver log a
repository artifact. Bulk evidence is filed by digest outside git
(`/home/ubuntu/certonomous-runs/`), per `docs/LOCATIONS.md`.

## 3. What it must NOT do

Never infer intent, never auto-generate the manifest, never rewrite paths, never `git add`,
never delete. A guard that fixes its own finding cannot be trusted to report it.

## 4. Selftest and L-314 planted-failure proof

A guard that reports on ITSELF is not a guard: **plant a failure and prove it refuses**, exactly
as a comparator plants a perturbation to prove a reader can see.

| control | tree | expected |
|---|---|---|
| 1 | 50 files, 4.9 MB, no manifest | **accept**, rc 0 — the boundary is inclusive |
| 2 | 51 files, no manifest | refuse `COUNT`, rc 2 |
| 3 | 5 MB + 1 byte, no manifest | refuse `BYTES`, rc 2 |
| 4 | 51 files **with** manifest | **accept**, rc 0 |
| 5 | one `verification/runs/X/log.solve` | refuse `LOGS`, rc 2 |
| 6 | one `log.solve` **with** manifest | refuse `LOGS` anyway, rc 2 — proves the exemption is scoped |
| 7 | one `attempt3/` path | refuse `ATTEMPT`, rc 2 |
| 8 | `05241ab2`'s real tree, replayed | refuse `COUNT` + `LOGS`, rc 2 — the named instance |

**Planted failures — each must FLIP a control, proving the clause is reachable, not merely present:**
- disable `COUNT` → control 2 accepts; disable `BYTES` → control 3 accepts;
- disable `LOGS` → controls 5 and 6 accept;
- widen the manifest exemption to `LOGS` → **control 6 accepts, which is the defect this spec
  forbids**; the selftest must show it can be reintroduced and caught.

**L-314 Instance 1, and cfd paid for it again today:** `set -e` is NOT in force in the agent
Bash context — an assertion inside a `python3` heredoc raises and **the surrounding shell
continues**. At `da7e1477` a cfd assertion aborted and the commit landed anyway. Therefore
control 9: **a caller that ignores `set -e` must still detect the refusal**, i.e. the guard's
rc is explicitly tested and its refusal line is greppable. A guard whose failure is only
printed is not a gate.

## 5. Rollout

Advisory for one working session (refusals reported, commits proceed), so its false-positive
rate is measured on real traffic before it blocks anyone. The measured rate is boarded. It
becomes blocking only after that, and never by an agent's own say-so.
