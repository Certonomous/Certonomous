# Queue-entry validator — standing rulings

Owner: **cfd-supervisor** (`scripts/queue_entry_check.py`, landed `0d895da0` as queue
substrate 1/3). Rulings here bind the validator's behaviour. Every clause ships a selftest
and an **L-314 planted-failure proof**: a guard that reports on itself is not a guard.

---

## R-AGE-CWD — 2026-08-27, cfd-supervisor, on Sanaa's §1(b) delegation. `[lab-attributed]`

**Question referred.** `check_age_guard()` refuses an entry whose `cwd` does not exist.
ansys's position: an absent run root is the *strongest* proof that no prior answer exists, so
the refusal should be kept only for a cwd that **exists and contains time directories**.
ansys is working around it with `mkdir -p`.

### Finding 1 — ansys's PREMISE is correct, and the current message states the opposite of the truth.

An absent directory is the strongest possible evidence that it holds no prior answer. This is
not a concession; it is how **CLAUDE.md rule 2's pre-compute condition is proven everywhere
else in this lab** — "name the run directory that does not exist", `test -e`, stamped. cfd
discharged exactly that for F25_DUCT3D at 16:23:12Z today.

The current text — *"cwd ... does not exist as a directory, so it cannot be shown free of a
prior answer"* — is **wrong on the merits**. Absence *is* the proof. That wording sent ansys
hunting for a rule-4 problem that does not exist. **The age-guard clause must never refuse on
absence.**

### Finding 2 — ansys's REMEDY is rejected, on measurement, not on preference.

Deleting the refusal would let an entry be ACCEPTED that **cannot launch at all**. Measured by
me, not recalled:

- `scripts/queue_runner.py:286` builds `cd '<cwd>' && <argv> …`
- `scripts/queue_runner.py:293` calls `Popen(..., start_new_session=True, cwd=str(cwd))`
- Driven: `Popen` with an absent cwd raises `FileNotFoundError: [Errno 2]`; `bash -c "cd
  <absent>"` returns **rc 1**.

So an absent `cwd` moves a **filing-time refusal** into a **launch-time death** — and the
runner writes its `LAUNCHED` record *first*. That manufactures precisely the stale-launch-record
class **L-344** was written to kill. Strictly worse than refusing.

### Ruling — SPLIT THE CLAUSE. Both halves are kept; neither is loosened.

1. **`check_age_guard()` applies only to a `cwd` that EXISTS.** Refuse on pre-existing time
   directories exactly as today. An absent `cwd` is **not** an age-guard finding and returns
   clean from this clause.
2. **New `check_cwd_launchable()` refuses an absent `cwd` under its own word, `EXEC`**, never
   `AGE-GUARD`, with a message that names the mechanism and the fix:
   `EXEC: cwd <path> does not exist; queue_runner.py chdirs into it (:286) and Popen(cwd=)
   raises FileNotFoundError (:293), so this entry would be recorded LAUNCHED and die. Fix:
   name an existing directory as cwd — the CASE directory is the lab convention — or mkdir -p
   it before filing.`
3. **`mkdir -p` is a legitimate remedy, not a workaround.** ansys should keep doing it.
4. **The preferred convention is the case directory**, and it already works: **10 of 10**
   launched cfd entries name `cases/<CASE>/`, which always exists; the launcher creates its own
   run root from absolute paths and ignores `cwd`. This needs no code change and is the
   one-line fix for any team blocked today.

**Net effect on queue depth: zero entries that pass today begin failing, and zero entries that
fail today begin passing.** The refusal is re-labelled and correctly attributed, not removed.
Nothing here weakens rule 4.

### Selftest and L-314 planted-failure proof (required before this ruling is believed)

| control | entry | must refuse under | must NOT refuse under |
|---|---|---|---|
| A | `cwd` absent | `EXEC` | `AGE-GUARD` |
| B | `cwd` exists, holds a time directory `0.1/` | `AGE-GUARD` | `EXEC` |
| C | `cwd` exists, clean | — (ACCEPTED) | — |

**Planted failures — each must FLIP a control, proving the clause is load-bearing and
reachable, not merely present:**
- disable `check_cwd_launchable` → **A must be ACCEPTED** (proves A's refusal comes from that
  clause and not incidentally from another);
- disable the time-directory scan → **B must be ACCEPTED**;
- re-point `check_age_guard` at absence → **A must refuse under `AGE-GUARD`**, which is the
  defect this ruling removes; the selftest must show it can be reintroduced and caught.

**L-314 Instance 1 applies to the harness that runs this selftest, and cfd paid for it again
today:** `set -e` is NOT in force in the agent Bash context. An assertion inside a `python3`
heredoc raises and **the surrounding shell continues** — at `da7e1477` a cfd assertion aborted
and the commit landed anyway. The selftest must therefore **return a checked exit code**, and
any caller must test it explicitly; a selftest whose failure is only printed is not a gate.

---

## R-TEAM-BINDING — 2026-08-27, cfd-supervisor. `[lab-attributed]` — **Sanaa may overrule.**

**An entry's `team` field MUST equal the team directory it sits in.** A mismatch is a
`TEAM-BINDING` validation failure, and therefore — correctly — a `refused/` outcome.

### Why this lands by the RULINGS route and not as an amendment to the standard

**This is a tooling-correctness clause.** It moves no gate, threshold, cap or label. It
refuses **only an entry that contradicts its own declared `team` field** — an entry
inconsistent with itself. It creates **no new gate on lab process**, and the runner already
moves refused entries to `refused/`, so this adds a **refusal reason to a mechanism that
already exists**, not a new mechanism. The `EXEC` clause (R-AGE-CWD above) landed by exactly
this route and is the live precedent.

`docs/standards/QUEUE_ENTRY_STANDARD.md` is **Sanaa's** and is **not edited**: it receives a
dated **cross-reference pointer** at its foot and nothing else. **D539's posture is unchanged
by this ruling** — adding a gate on lab process is reserved to Sanaa, and this is not one; a
measured rate is never an authorisation (`CLAUDE.md` rule 9).

### The defect, measured

`queue_runner.list_entries()` (`:387-395`) iterates **by directory** and never reads `team`;
`tick()` carries that directory's name into the round-robin cursor, the `LAUNCH_LOG.tsv` row
and the `<team>/launched/` destination. `check_schema` (`queue_entry_check.py:154-155`) asks
only whether `team` is one of the six, never **which** one. So an entry declaring one team in
another team's drop path launches and is recorded as the **directory's** — corrupting verdict
ownership and per-team queue depth. **A metric that can be silently wrong is worse than one
that is absent.**

### The two refusals this adds, and there are no others

| clause | refuses | never refuses |
|---|---|---|
| `TEAM-BINDING` | an entry whose `team` differs from its containing team directory | a missing/out-of-roster `team` (SCHEMA's, once); a file outside the six directories |
| `REQUIRE-BINDING` | **only under `--require-binding`:** a file outside the six directories, i.e. one where binding could not be checked | anything when the flag is absent |

`check_team_binding()` has three `return` statements, one of which is a refusal.
`require_binding_clause()` has two, one of which is a refusal. **Those two are the entire
refusal surface of this change** — enumerated from the AST, not read off the source.

### `NOT CHECKED`, not `NOT BOUND`

Outside the six directories the verdict prints a `TEAM-BINDING: NOT CHECKED` block naming
what was not checked and where it will be, in a **different shape** from the one-line
`TEAM-BINDING: bound to <team>/` a bound entry gets. **`NOT BOUND` would describe the
entry's state; `NOT CHECKED` describes the limit of our knowledge**, and the planted-zero
principle is about knowledge. It is not a refusal, because refusing there would force every
lane to copy into the drop path **before** validating — to validate only once the launch is
armed — which inverts the safe order and contradicts check-4-before-the-drop.
`--require-binding` is what makes it bite, and the enqueue procedure runs it **on the queued
copy, in place, after the copy**.

### Controls — C1–C12, spec `docs/standards/QUEUE_ENTRY_TEAM_BINDING.md` (frozen `b23b5638`, v1.1)

| # | control | planted failure it rests on |
|---|---|---|
| C1 | a matching entry draws no `TEAM-BINDING` | — (guards a check that refuses everything) |
| **C2** | **mismatch REFUSED, message naming both sides** | **the plant itself** |
| **C3** | **the clause no-opped → C2 must FLIP to accepted** | **C2 is worthless without it** |
| C4 | `validate()` with no `entry_path` raises loudly | — |
| C5 | the path defaulted → C4 flips, the mismatch validates clean and silently | the silent-skip defect, reproduced |
| C6 | a missing `team` refuses **once**, by SCHEMA | — |
| C7 | a draft outside the queue is accepted **and** says `NOT CHECKED` | — |
| C8 | the note suppressed → C7 flips | proves C7 read the note, not the absence of a refusal |
| C9 | one real `queue_runner.tick()`: moved to `refused/`, clause named, **nothing launched** | asserts the recognised path shape first, so it cannot pass vacuously |
| C10 | zero `ast.Assert` nodes after the change (L-332) | — |
| **C11** | **unbound entry accepted without `--require-binding`, REFUSED with it** | **the flag's plant** |
| **C12** | **the clause no-opped → C11 must FLIP** | **C11 is worthless without it** |

Plus a hygiene control: no control artefact may reach the real drop path — *the drop path is
a launch button, and a test file there is a launch.*

**Measured before the code existed and re-measured at landing:** entries in all six drop
paths carrying a `team` that disagrees with their directory — **zero**, and zero across the
`launched/` records. The clause is **preventive**; it invalidates no existing verdict.

**Known limit, recorded rather than hidden:** the clause recognises the path shape
`.../verification/queue/<team>/`. A runner started with a **non-default `--root`** is
therefore unbound and silently so. Production is unaffected (`DEFAULT_ROOT` is
`<repo>/verification/queue`; cron passes no `--root`). Referred, not fixed here — relaxing
the path shape changes the invariant, not its implementation.
