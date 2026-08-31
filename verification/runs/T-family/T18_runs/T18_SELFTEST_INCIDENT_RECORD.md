# T18 SELFTEST INCIDENT RECORD

**Status:** record of an artifact, not a verdict. No number in this file is a T18 result.
**Written:** 2026-08-31, heat-transfer lab-lane, on the heat-transfer-supervisor's
preservation instruction [lab-attributed].
**Subject artifact:** `T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.json`
(5186 bytes, md5 `bba51110b76b6f0763a46e68c2c170ba`, sha256
`335bbec520a20ff461398c0b7135e451b994459a7bc7f1dfdd63700afdd7e099`), with its sealed
companion `T18_SELFTEST_SIDE_EFFECT_NOT_A_GRADE_20260831T151045Z.txt`.

This record exists because the artifact was untracked, `/tmp` did not survive the
2026-08-31T14:35Z reboot, and one `git clean` would have erased it. It is committed
here so that it survives **with an accurate label**.

---

## 1. What the selftest arm does

`analyse_t18.py` selftest unit (v), at `analyse_t18.py:509`:

```
grade(HERE, os.path.join(tempfile.gettempdir(), "t18_never.json"), reg)
```

`HERE` (`analyse_t18.py:38`) is the live `T18_runs` directory, hardcoded; the call
ignores `--root`. The unit asserts that grading a tree whose DONE-marker set is
incomplete raises `SystemExit(EXIT_REFUSE)`. To assert that, it must really call
`grade()` with the live tree as its **read root**.

Reading the live tree is the arm's design. Writing to `/tmp` is correct behaviour.
The arm is a read, and its output was directed away from the run tree on purpose.

## 2. NO WRITE INTO THE LIVE TREE EVER HAPPENED

The framing under which this artifact was nearly relayed upward — that it is "the
only evidence the live-tree write happened" — is **false**. There was no live-tree
write. Three independent measurements, all taken 2026-08-31 for this record:

**(a) The file in this directory is a copy, not a write.** The artifact and
`/tmp/t18_never.json` were both 5186 bytes with mtime
`2026-08-31 15:06:21.565360460 +0000` — **identical to the nanosecond** — and
identical in content (`sha256 335bbec5…`, `md5 bba51110…` on both). Two independent
writes cannot land on the same nanosecond. That signature is `cp -p`. The sealed
companion `.txt` states the same origin at its `Origin:` line and records that the
md5s were compared in one shell invocation at copy time.

**(b) `grade()` has exactly one write site and it honours its argument.**
`grade()` spans `analyse_t18.py:265-357`. Its sole write is `:354`,
`json.dump(out, open(json_out, "w"), indent=2)`, to the `json_out` parameter and
nowhere else. Unit (v) passed `/tmp/t18_never.json`. The only other writes reachable
from `grade()` are inside `planted_zero_control` (`:168-221`), which copies the case
into a `mkdtemp` first, **refuses** if that copy resolves inside the case tree
(`:178-179`), plants and restores only within the copy, and removes the copy in a
`finally`.

**(c) The tree carries no mark from it.** Of the **196** files under `T18_CU_c`,
`T18_CU_m`, `T18_CU_f` and `T18_CU_f_CT`, **zero** have an mtime later than the
DONE markers at 2026-08-31T14:57:46Z. The newest file anywhere in the four trees is
`T18_CU_f_CT/STATUS.T18_CU_f_CT` at 2026-08-31T01:20:21.39Z. A full read-and-grade
left no mark at all.

*Planted control on (c), per standing rule 3:* the same reader, asked for files newer
than 2026-08-31T00:00:00Z, returns **56 of 196**. The zero in (c) comes from a reader
demonstrated able to return a non-zero on this exact tree, not from a blind glob.

## 3. THE REGISTERED VERDICT IS NOT CONTAMINATED

`gate_t18.json` has mtime `2026-08-31 15:11:44.670072566 +0000` — **323.105 s
later** than the artifact, not nanosecond-shared with it, so it was written, not
copied. `T18_GRADE_OUTPUT_20260831T151113Z.txt` has mtime
`15:11:44.683219608 +0000`, **13.147 ms after** the gate JSON, and its line 14 reads
`wrote /home/ubuntu/Certonomous/verification/runs/T-family/T18_runs/gate_t18.json`
— it names by absolute path the file it follows. A copy cannot manufacture a fresh
stdout log that names the JSON written 13 ms before it. The registered verdict is a
genuine later grade.

**A discrimination hazard, recorded because it is not obvious.** `gate_t18.json` is
byte-identical to the artifact — same 5186 bytes, same sha256 `335bbec5…`. That is
expected of a deterministic comparator run twice against an unchanged tree, and it
independently corroborates that the artifact is a real grade. It also means
**content alone cannot tell the two apart.** Only provenance can: mtime, and the
stdout log. Anyone re-checking this must use §2 and §3, never a diff of the values.

## 4. What the artifact is, and how it must be handled

It is an **UNREGISTERED REAL GRADE computed to a temporary path.** Its numbers are
real — that is precisely the danger, because they could be mistaken for a registered
verdict, and being byte-identical to `gate_t18.json` they would not look wrong. **No
number in it may ever be quoted as a T18 verdict.** The registered verdict lives in
`gate_t18.json` with `T18_GRADE_OUTPUT_20260831T151113Z.txt` and that file's
companion `.NOTE.txt`.

The prior lane that preserved it and relabelled it rather than deleting it did the
right thing, and its sealed companion `.txt` is accurate on every point checked here,
including the `/tmp` origin. The false "live-tree write" framing is **not** in that
note; it entered in relay upward. The sentence most likely to have seeded it is the
note's "grade() runs to completion and writes this JSON", read next to a file
physically sitting in the run tree. The note is left unedited; this record carries the
correction.

## 5. THE DESIGN DEFECT THAT DOES SURVIVE

The arm asserts "live tree with no DONE markers refuses". **Completing the DONE set
removes the arm's own precondition**, and completing it is a precondition of ever
grading. Before 2026-08-31T14:57:46Z: selftest 17/17, grading refuses. After:
grading runs, selftest 16/17. **There is no state in which both the arm and a grade
can hold.** T18's selftest reports this honestly, and it is to be stated this way
everywhere and never as PASS:

    16 ok / 1 FAIL (unit (v), live-tree arm, EXPECTED-INVERTED)

*Source of that string:* the sealed companion `.txt` and the grading run's
`.NOTE.txt`, both filed 2026-08-31. This record verified the **arm's logic** at
source (`:505-512`) but did not re-run the selftest — re-running it would produce a
further side-effect artifact.

**The construction is wider than T18.** Measured by source sweep across
`verification/runs/T-family/` on 2026-08-31, `grade(HERE, …, "<rung>_never.json")`
appears at:

| Comparator | Line |
|---|---|
| `T9aR1b_runs/analyse_t9aR1b.py` | 367 |
| `T9aR1c_runs/analyse_t9aR1c.py` | 934 (variant, `quiet_ref=True`) |
| `T14_runs/analyse_t14.py` | 468 |
| `T15_runs/analyse_t15.py` | 918 |
| `T17_runs/analyse_t17.py` | 616 |
| `T18_runs/analyse_t18.py` | 509 |
| `T19_runs/analyse_t19.py` | 691 |

**Honest limit on that table:** it records where the *construction* is present. It
does **not** establish that each of those arms is currently inverted — inversion
depends on each rung's DONE-marker state, which this record did not measure. Whoever
schedules the repair must measure that per rung.

## 6. The repair, and whose call it is

The repair already exists as **T16c's S8a–S8e apparatus** (`analyse_t16c.py:153-167`):

- **S8a** `_selftest_root_guard` (`:1388-1408`) refuses (exit 2) if a selftest arm's
  grading root is, contains, or is contained by a live root — resolving symlinks.
- **S8b** every forged tree carries a `FORGED_BY_T16C_SELFTEST_NOT_A_RUN` sentinel
  and `_selftest_grade` (`:1410-1420`) refuses without it; S8a alone is a path test
  and a symlink defeats a path test.
- **S8c** a `_RootWatch` records every read under each live root, with its own
  planted control (`:1739`).
- **S8d** a source-level detector counts direct `grade(…)` calls, with a planted
  control source, so every route must go through `_selftest_grade`.
- **S8e** `sys.dont_write_bytecode = True` before import, so no `__pycache__` lands
  in a frozen tree.

Why this repairs the inversion and not merely the side effect: T16c's live-root arm
(`:2182`) goes through `_selftest_grade`, so the refusal it asserts comes from **S8a,
before any read** — a precondition the selftest itself controls — rather than from the
DONE-marker state, which the campaign consumes by succeeding. The assertion therefore
survives the rung being graded.

**Scheduling this repair onto the rungs in §5 is the heat-transfer supervisor's
decision and is NOT taken here.** Standing rule 2 bars editing a frozen comparator;
the repair belongs to a successor registration, not to this record and not to the
run that exposed it.

## 7. What this record did not verify

- The `16 ok / 1 FAIL` count was **cited from the two 2026-08-31 notes, not
  re-measured**; the selftest was deliberately not re-run.
- Per-rung inversion state for the six sibling comparators in §5 — **not measured**.
- `gate_t18.json` is at the time of writing still **untracked** and at the same
  `git clean` risk this record was written to remove. Committing a gate JSON is a
  registration act, so it is flagged to the supervisor here rather than taken by
  this lane.

**Cost:** file inspection and source reading only. No solver ran; no compute beyond
shell inspection was consumed, so there is no core-minute figure to calibrate against
a pre-registered estimate.
