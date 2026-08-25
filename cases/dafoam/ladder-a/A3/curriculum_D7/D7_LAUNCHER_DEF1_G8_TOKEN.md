# `D7-LAUNCHER-DEF-1` — `.d7_g8_pass` has a READER AND NO WRITER. Arm `O` cannot launch.

**Date:** 2026-08-25. **Lane:** dafoam `lab-lane`, curriculum item D7.
**Verdict: `BLOCKED`** — arm `O`, and consequently arms `F-S`/`F-P`, cannot launch from the frozen
launcher as committed at `0e229a0a`.
**Found by RUNNING it, not by reading it.** The freeze audit read this launcher and did not catch it.

## 1. The defect

`d7_run_arm.sh:214-216` gates the colouring-cache inheritance on a token file:

```
stage_coloring() {
  test -f "$BASE/.d7_g8_pass" || { echo "ABORT colouring inheritance requires G8 to have PASSED (sec.5); $BASE/.d7_g8_pass absent"; exit 5; }
```

and its own comment at `:213` states the token is written by arm `P1`:

> *"the launcher refuses to stage it until arm P1 has written `.d7_g8_pass`."*

**Nothing writes it.** `grep -n 'd7_g8_pass' d7_run_arm.sh` returns **three** hits and **all three
are the comment and the `test -f` read**. There is no `touch`, no redirect, no write anywhere in
the file, in either instrument, or in the producer.

`stage_coloring` is called from **two** sites: `:246` in the `O)` branch and `:252` in the
`F-S|F-P)` branch. **Arm `O` therefore aborts at exit 5 unconditionally**, and the two FD arms
would too.

## 2. Measured, not inferred

Arm `P1` ran and returned **rc=0** at `2026-08-25T21:36:40Z`, wall 4 s, **0.267 core-min** against
a registered cap of 8.0. Its ledger row records `inspect(exit,oomkilled)=[0 false]`.

* `ls -la /home/ubuntu/certonomous-runs/CURRICULUM-D7-a3-m6-cdmin/.d7_g8_pass` → **absent**.
* The arm that the comment says writes it **completed successfully and did not write it.**

**And `P1` did the work correctly** — this is a launcher handshake defect, not a failed test:

```
DECOMP_A {"processor0": 10635, "processor1": 10506, "processor2": 10538, "processor3": 10441}
DECOMP_B {"processor0": 10635, "processor1": 10506, "processor2": 10538, "processor3": 10441}
```

**Identical across all four subdomains** — the decomposition determinism G8 exists to demonstrate,
demonstrated. `P1` also wrote `d7_decomp_A.json`, `d7_decomp_B.json` and four
`d7_placement_rank*.json` into `P1/`. Rank affinity from its own log: rank 0 → core 2, rank 1 → 3,
rank 2 → 4, rank 3 → 6 — **four distinct single cores, exactly the registered cpuset `2,3,4,6`.**

## 3. The grader does NOT depend on the token — which localises the defect precisely

`d7_grade.py:570-571` computes G8 by reading the artifacts directly:

```
a = read_json(os.path.join(work, "d7_decomp_A.json"), "G8")
b = read_json(os.path.join(work, "d7_decomp_B.json"), "G8")
```

**G8's verdict is therefore independent of the token.** `.d7_g8_pass` is a purely launcher-internal
handshake, and it is the handshake that is broken — not the gate, not the evidence, not the grading
path. Both artifacts it would be derived from are on disk and readable.

## 4. WHAT THIS LANE DID NOT DO, and why

**The token was not hand-written, and the launcher was not edited.**

Writing `.d7_g8_pass` by hand is available, trivial, and would unblock the ladder in one command —
and it is **exactly the antipattern the standing instruction names**: *a guard that refuses is the
guard working; do not disable it, do not edit it, do not delete a stage to get past it.* The token
is the artifact the guard checks. Manufacturing it from this lane's own reading of `P1`'s log
**substitutes a lane's judgment for the instrument's**, and certifies a gate outside the instrument
that owns it. The fact that the underlying evidence genuinely passes makes that **more** tempting
and no more legitimate.

Editing the launcher is barred by `CLAUDE.md` rule 6 — it is frozen and committed at `0e229a0a`,
and its md5 `c55b2cdeaf8a0975641b491b24912d63` is registered in `PREREGISTRATION.md` Addendum 1
§A1.2 and **re-asserted by the launcher against its own staged copy on every launch**. Any edit
would break that assertion by construction.

**The repair is the dafoam-supervisor's call under `VERIFICATION_CHARTER.md` §2d.1**, as they ruled
for `D4-DEF-4`. This note records the finding and stops.

## 5. Consequence for the run in flight, stated plainly

* `P1` — **complete, rc=0**, evidence on disk.
* `P2` — **running** at the time of writing; it builds the colouring cache and measures the
  baseline primal. It does **not** call `stage_coloring` and is **not** affected.
* `O` — **will abort at exit 5** the moment the chain reaches it. **Cost of that abort: zero
  core-minutes** — the guard refuses *before* any rank is claimed. The chain driver halts on the
  first non-zero rc and will not cascade.
* `F-S`, `F-P` — already `BLOCKED` on the separate and independent `D7-DEF-4` units defect
  (`D7_DEF4_SCALER_BLOCKER.md`). **They now carry two independent blockers.**

## 6. What a repair would need, if the supervisor rules one (NOT implemented here)

The minimal repair is for arm `P1` to write the token **on the launcher's own G8 evidence**, not on
anybody's reading of it: after `P1` completes, compare `d7_decomp_A.json` against
`d7_decomp_B.json` in the launcher and `touch .d7_g8_pass` **only if they match**, so the token
means what `stage_coloring` reads it as meaning. **The token must never be written unconditionally**
— an unconditional `touch` would convert a real gate into a no-op and would be worse than the
current defect, which at least fails closed.

**This defect fails CLOSED**, and that is the one good thing about it: a launcher that wrongly
*granted* colouring inheritance would have produced a full ladder of numbers with an unverified
partition underneath them.
