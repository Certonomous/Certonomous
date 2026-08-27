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
