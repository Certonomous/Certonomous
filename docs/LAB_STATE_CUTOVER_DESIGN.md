# LAB_STATE board-source cutover (V-119) — design + apply procedure

**Owner-approved** 2026-09-10 (via chief). **Infra/dispatch, not a gate/standard change.**
**Author:** verification-supervisor. **Cost: instrument-only, 0 solver core-min, $0.00.**

## The problem
`docs/LAB_STATE.md` was one ~41k-line monolith all six teams wrote to concurrently.
It bloated into 13k-token megalines (a single section header nearly blocked a supervisor
from reading its own handoff channel) and, because every writer staged the WHOLE file
under the rule-10 private-index protocol, a commit could sweep another team's in-flight
edit.

## The architecture (after cutover)
- Each team's section is its OWN source file under `docs/lab_state/`:
  `00_preamble.md` (the title + `## CHIEF` directives), then `10_closure.md`,
  `20_dafoam.md`, `30_heat-transfer.md`, `40_cfd.md`, `50_verification.md`,
  `60_ansys-verification.md`. The numeric prefix fixes assembly order and (via the
  strict `[0-9][0-9]_*.md` glob) excludes README/design docs living alongside.
- `docs/LAB_STATE.md` becomes a GENERATED artifact = a one-line BANNER + the **byte
  concatenation** of the sources in sorted-filename order. Assembly inserts no
  separators, so `scripts/split_lab_state.py` is an exact inverse: `concat(sources)`
  reproduces the pre-cutover board byte-for-byte. The ONLY delta the cutover makes to
  `docs/LAB_STATE.md`'s content is the banner prepended at the top.
- Instruments: `scripts/assemble_lab_state.py` (assemble / `--check` drift / `--no-banner`
  / `--selftest`) and `scripts/split_lab_state.py` (one-shot migration + `--selftest`).

## Why this ends the clobber + bloat
- Each team commits ONLY its own source file → no team's committed work can be clobbered
  by another team, and no single shared megaline sink exists.
- `docs/LAB_STATE.md` is derived; if a stale copy is ever committed it self-heals on the
  next assembly, and `assemble_lab_state.py --check` (exit 2 on drift) catches a source
  edited without reassembly or the generated file edited directly.

## Write protocol (in force after apply)
A team: (1) edits ONLY its `docs/lab_state/<NN>_<team>.md`; (2) runs
`python3 scripts/assemble_lab_state.py` to regenerate `docs/LAB_STATE.md`;
(3) commits BOTH its source and `docs/LAB_STATE.md` via the rule-10 private-index
protocol (explicit paths, CAS, post-commit verify). Readers still read
`docs/LAB_STATE.md` unchanged (FIRST-ACTION rule needs no change). A one-line note for
`CLAUDE.md` rule 13 / `FILING_CHARTER` documenting the source dir is DRAFTED for
chief/Sanaa to apply (a `CLAUDE.md` edit is not an agent's to make — rule 9); it is not
required for correctness because the banner in the generated file states the protocol.

## Losslessness proof (Phase 1, run in scratch — no live mutation)
Copy the live `docs/LAB_STATE.md` to a scratch tree; `split_lab_state.py --out-dir
<scratch>` (its internal reconstruction identity asserts `concat(sources)==input`);
`assemble_lab_state.py --repo <scratch> --no-banner --stdout` must equal the scratch
copy byte-for-byte (md5 match). Both scripts' `--selftest` (planted-content readback;
a mutated source must flip the readback; malformed board must REFUSE) must pass, and
identically under `python -O` (L-332). Verified by the verification-supervisor as a §3
check-1 (diff-read + plant driven personally), never a lane's PASS.

## Atomic apply (Phase 2)
The switch is a SINGLE private-index commit adding the seven `docs/lab_state/` sources
and the regenerated `docs/LAB_STATE.md` (= banner + byte-identical body) together, so a
mid-apply credit/fleet death leaves the OLD board FULLY intact (all-or-nothing at the
git layer) — never half-migrated. Before committing, assert `assemble --no-banner ==
the pre-apply board bytes` so the body is provably unchanged. Working-tree writes are
whole-file (never half-written), so even an un-committed dirty tree stays a valid board.

**Coordination:** safest with a brief board-write quiesce across teams (no LAB_STATE
writes) so nothing lands mid-apply. It is *also* clobber-safe without a quiesce IF the
apply reads the CURRENT working-tree board, re-reads on any CAS-retry, and commits
atomically — the residual is that a peer's un-committed monolith edit present on disk at
apply time is carried into the sources (captured, not lost). During a quiescent
(idle-monitoring) window there are no such in-flight edits, so the apply is clean.

**HARD RULE honored:** never commit a broken/partial board. Either the board ends this
session cleanly cut over (atomic apply committed, body byte-verified) OR unchanged and
intact with this design + the scripts committed for the next session to finish.
