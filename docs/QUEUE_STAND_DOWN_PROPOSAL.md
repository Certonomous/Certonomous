# PROPOSAL — NOT ADOPTED — a per-team stand-down gate for the queue daemon, and the honesty repair of `SKIP_DIRS`

**Status:** PROPOSAL. Nothing here is in force and nothing here has been executed.
**No line of `scripts/queue_runner.py` was modified by this document's author.** The
daemon is live (pid 1664) and the restart that would adopt any of this is Sanaa's,
held by the chief.

**Filing note.** `docs/<TOPIC>_PROPOSAL.md` is the lab's established location for an
infrastructure proposal — eight precedents on disk `[MEASURED, ls docs/*_PROPOSAL.md,
this document excluded]`, and `check_filing.py` R2 (`docs/*.md` is `UPPER_SNAKE`).
`docs/proposals/` does not exist and is registered in no filing rule;
`BOARD_MIGRATION_PROPOSAL.md` and `BOARD_BASE_RULE_PROPOSAL.md` both declined to
create it and this document follows that precedent.

**Author:** cfd (lab-lane, for cfd-supervisor). **Solver compute: 0 core-min, $0.00.**
**Gates · thresholds · bands · caps · labels changed: 0 · 0 · 0 · 0 · 0.**

---

## 1. The defect, measured

All line numbers are against `scripts/queue_runner.py` at HEAD as read
2026-09-03T20:48Z (2,002 lines).

### 1.1 There is no per-team gate anywhere on the launch path

`list_entries(root)` — **`:434-442`** — is the whole of the daemon's admission
enumeration:

```python
def list_entries(root: Path) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for team in TEAMS:                                    # :436
        d = root / team
        if not d.is_dir():
            continue
        files = sorted((p for p in d.glob("*.json")), key=lambda p: p.stat().st_mtime)
        out[team] = files
    return out
```

`TEAMS = tuple(qec.TEAMS)` at **`:113`** is iterated **unconditionally**. The only
`continue` is `not d.is_dir()` — a team is skipped if and only if its directory does
not exist. **There is no per-team gate of any kind on this path.** A team that has
stood down is therefore protected by exactly one thing: its queue directory being
empty of top-level `.json`.

`[MEASURED 2026-09-03T20:48Z]` top-level `.json` counts per team directory under
`verification/queue/`: `ansys-verification` 0, `cfd` 1, `closure` 0, `dafoam` 1,
`heat-transfer` 0, `verification` 0. closure is stood down and is holding at 0 — by
emptiness, not by any control.

**Consequence.** One `.json` placed at the top level of a stood-down team's queue
directory — by any agent, by a stale editor, by a recovery script replaying a row —
is admitted on the next tick, with no agent alive to watch the run it starts.

### 1.2 Killing the daemon is not a control

`[MEASURED]` `crontab -l` carries `* * * * * /bin/bash
/home/ubuntu/Certonomous/scripts/queue_runner.sh` alongside an `@reboot` line. A
minute-resolution keepalive restarts the daemon, so "kill it" is not a stand-down
mechanism; it is a one-minute pause.

### 1.3 `SKIP_DIRS` is dead code, and that is the more serious half

**`:114`** — `SKIP_DIRS = ("launched", "refused")`.

`[MEASURED]` `grep -c SKIP_DIRS scripts/queue_runner.py` returns **1**. `grep -n`
returns exactly one line: **`:114`, its own definition.** The name is bound and never
read. It is dead code.

`launched/` and `refused/` are in fact excluded from enumeration — but by
**`d.glob("*.json")` at `:440` being non-recursive**, which excludes every
subdirectory equally and by accident of the glob's semantics. The exclusion is
**incidental, not protective**: it is a property of the pattern, not a decision the
code takes, and nothing anywhere tests that those two directories in particular are
skipped.

**⚠ The hazard is not primarily the launch. It is that `SKIP_DIRS` documents a
protection that does not exist.** A reader of this file — and a reader is exactly who
would be asked whether a stand-down is safe — would reasonably conclude the
enumerator consults a skip list. It does not. Changing the glob to `rglob`, or adding
a legitimate third directory to `SKIP_DIRS`, would in both cases produce behaviour
flatly contradicting the source as it reads today, and no test would fail.

This is the third instance of that shape recorded in cfd's territory on 2026-09-03;
see `docs/LESSONS.md` L-478, which this section is the live instance of. The other
two are already repaired: `cases/committee-grids/ugrid_to_foam.py` (L-475) and
`scripts/check_converter_copies.py:455-483`, whose own repaired docstring names the
pattern as "the SECOND instance of that shape in this converter's story".

### 1.4 The running daemon is already behind its own source

`[MEASURED]` pid 1664 started **2026-09-03 15:35:14 UTC** (`ps -o lstart`); the box
is UTC. **Four** commits have landed on `scripts/queue_runner.py` since:
`0ac4eb42` (16:13:39Z), `d2005e7c` (17:29:27Z), `1c81275b` (17:37:18Z),
`26361970` (19:02:01Z). The process is running none of them. This is context for §4,
not a defect of its own.

---

## 2. Two candidate fixes, and what each actually solves

They are **independent**. They fix different things. Neither substitutes for the
other, and the recommendation is that **both** land.

### (a) A per-team stand-down marker the enumerator honours — THIS is the stand-down switch

A marker file in a team's queue directory whose presence removes that team from
admission for as long as it exists.

```python
def list_entries(root: Path) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = {}
    for team in TEAMS:
        d = root / team
        if not d.is_dir():
            continue
        if (d / STAND_DOWN_MARKER).exists():      # fail-closed: present => no admission
            out[team] = []
            continue
        files = sorted((p for p in d.glob("*.json")), key=lambda p: p.stat().st_mtime)
        out[team] = files
    return out
```

**Solves:** the actual hazard. A stood-down team stops depending on its directory
staying empty. The switch is a file, so it survives the daemon restart, the cron
keepalive, and the death of every agent — which is precisely the failure mode, since
a stand-down is the state in which no agent is alive to notice.

**⚠ Do not name the marker `HOLD`.** `[MEASURED]` `HOLD` is already a live verdict
string in this file's GPU-gating vocabulary at `:315`, `:329`, `:335`, `:339`,
`:356`, `:957`, `:1490`, `:1516`, `:1536`, where it means *"the caller waits; it does
not refuse"* — a per-tick, self-clearing device condition. A stand-down is the
opposite: operator-set, persistent, and cleared only by hand. Reusing the token would
put two unrelated meanings on one word in one file. Proposed name:
**`STAND_DOWN`** (a marker file `verification/queue/<team>/STAND_DOWN`), with its
content read and echoed into the tick log as the stated reason, and an absent-but-
unreadable marker treated as present (fail-closed).

**Scope — the gate belongs on admission only.** `list_entries` is the right and only
place. The other `launched/` scans — **`:288`** (live-launch detection feeding the
GPU clause) and **`:683`** (cap-watch flag maintenance) — are **supervision of runs
that are already live**, and they must keep running for a held team: a team can be
stood down while a long solve it launched an hour ago is still going, and that solve
must stay watched and stay capped. Gating those loops on the marker would silently
un-watch live runs, converting a safety control into a hazard. **The hold gates
admission, never supervision.**

### (b) Making `list_entries` consult `SKIP_DIRS`

**Solves:** the honesty defect in §1.3, and only that. It converts an incidental
exclusion into an intentional one, so that the source stops asserting a protection it
does not implement and so that a future `rglob` or a third skip directory behaves the
way the file reads.

**⚠ (b) alone does NOT give a stand-down switch, and must not be presented as one.**
`SKIP_DIRS` is a list of *subdirectory names* excluded from enumeration within every
team. It has no per-team dimension and cannot acquire one without becoming a
different thing. Landing (b) and calling the stand-down question closed would be a
strictly worse outcome than landing nothing, because it would leave a repaired-looking
file with the original hazard intact.

### Recommendation

**Land (a) as the stand-down switch. Land (b) as a separate honesty repair, in its own
commit, with its own message.** Keeping them apart matters: (b) is a no-op on
observable behaviour today (the glob already excludes those directories), and burying
a no-op inside a behavioural change makes both harder to review and makes (b)
untestable — there is no before/after to show. Two commits, two rationales.

---

## 3. The planted-failure test for (a)

CLAUDE.md rule 3 plants a perturbation to prove a **reader** can see a non-zero. This
lab has been correspondingly weak on planting a **failure** to prove a **guard** can
abort. `queue_runner.py`'s own selftest already has the right idiom — `PLANT 1..4` at
`:1470`, `:1482`, `:1511`, `:1530`, each of which *flips a control* to prove the
clause under test is load-bearing rather than incidentally satisfied. The stand-down
gate should be tested the same way and in the same file.

**None of the following has been executed. The live daemon is not ours to experiment
on; these controls run inside `selftest()`, against its `tmp` fixture root
(`:997`, "PRODUCTION'S SHAPE, not a convenient one"), never against
`verification/queue/`.**

**Control H1 — the marker holds.** In the fixture root, create a team directory,
place **one benign, validator-clean entry** at its top level, write `STAND_DOWN` beside
it, run `tick()`. **Assert: the tick returns `HELD` for that team, the entry file is
still at its original path, and no `launched/` record was written.** Assert on the
entry's continued existence, not merely on the return string — a gate that returns the
right word while the entry is consumed is the failure this control exists to catch.

**Control H2 — the same entry launches once the marker is removed.** This is the half
that makes H1 evidence. Delete the marker, leave everything else byte-identical, run
`tick()` again. **Assert: the entry LAUNCHES.** Without H2, H1 is satisfied by an entry
that was never launchable for some unrelated reason — a malformed row, a failed
validator, an empty directory. **H1 alone is a planted zero with no positive control**,
and the lab has three recorded instances of exactly that mistake.

**Control H3 — the marker is what held it (the PLANT, in the file's own idiom).**
Following `PLANT 1` at `:1470`: with the marker present, substitute a mutant gate that
ignores the marker, run `tick()`, and **assert the entry LAUNCHES**. This proves H1's
hold came from the gate and not from an accident of the fixture — the same argument
`PLANT 3` makes at `:1511` ("so fail-closed is what held it, not an accident of the
reading"). Restore the real gate in a `finally:`, as `PLANT 4` does at `:1543`.

**Control H4 — an unreadable marker is treated as present.** Create the marker with
mode `000` (or as a directory), run `tick()`. **Assert: `HELD`.** The fail-closed
direction must be tested, or the `try/except` around the read will silently become a
launch path. A held team whose marker cannot be read is the exact case where guessing
is most expensive.

**H2 is the control that most often gets skipped and is the one that carries the
proof.** A hold that cannot be lifted is indistinguishable from a queue that was never
going to run.

---

## 4. Forward-only; it rides the restart the chief already holds

This proposal is **forward-only**. It changes no past verdict, no launched record and
no queued row, and it is deliberately not applied to the running process.

- **No code change should land ahead of the restart** beyond what is already staged for
  it. `scripts/queue_runner.py` on disk would change behaviour for all six teams the
  moment pid 1664 is replaced, and pid 1664 is already four commits behind its own
  source (§1.4) — so the restart is the single point at which the accumulated change
  set becomes live, and it should be reviewed as one set.
- It should ride that restart **alongside** the `queue_runner` pid-of-dead-parent field
  and the fleet-ceiling telemetry (`26361970`, report-only), which are queued for the
  same event.
- **Until the restart, the stand-down state of a team remains what it is today: an
  empty directory and a convention.** That should be said plainly to anyone who asks
  whether a team is safely stood down, and it is the reason §1.3's naming defect is
  worth repairing rather than tolerating — the next person to answer that question will
  answer it by reading this file.

**Nothing in this document authorises the restart, and no agent may take it.**
