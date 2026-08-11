# What is tracked that should not be — scoping for §7 G5

Chief supervisor, 2026-08-11. Docket item **F** (Katie's §7, G5).

Katie's G5 asks that everything currently tracked which is **generated** — logs, run outputs,
built bundles — either move to a gitignored `evidence/` or leave tracking, with history
untouched and `.gitignore` rebuilt to match the new shape.

**The moves wait for the quiet window. The scoping does not, and this is the scoping.** It
costs no compute and it is the part that makes the window safe: the window is short, the suite
must stay green after every batch, and nobody should be discovering *during* it which files a
published claim depends on.

**This document proposes nothing untracked. It measures.**

---

## 1. Frame, stated before the numbers

Every count below is over **`git ls-files` — tracked files only, not the filesystem** — measured
at commit `6a2b3ea2` on 2026-08-11. It is deliberately not `grep -r`: in this environment `grep`
execs `ugrep --ignore-files`, which honours `.gitignore` and would silently skip the very
archives this exercise is about (L-75).

Regenerate every figure here rather than quoting it:

```
python3 scripts/corpus_figures.py          # the tracked-shape block
```

A number below that disagrees with the generator means the tree moved, and **the generator
wins.** That is L-79's rule applied to this document from the moment it was written.

## 2. The split that matters: source versus output

The naive count is wrong in a specific direction, and the direction is worth naming. A field
file named `U` under `0/` is an **initial condition** — it is source, it is hand-authored, and
untracking it destroys the case. The same filename under a **non-zero** time directory is
**solver output**. Counting them together overstates the generated set by about a thousand
files and would put case setup on the deletion list.

| Population | Files | What it is |
|---|---:|---|
| All tracked | **20,573** | the denominator |
| Under a non-zero time directory | **8,582** | **solver output** — generated |
| `log.*` | **778** | **solver logs** — generated |
| Under `0/` | 965 | initial conditions — **source** |
| Under `constant/` or `system/` | 2,727 | case dictionaries — **source** |
| Under any `*_runs/` directory | 13,345 | mixed; contains all of the above |

**Control on the output count.** Every one of the 208 parent directories of a matched output
file is either a real OpenFOAM case root — confirmed by having a tracked `system/` or
`constant/` beside it, 123 of them — or a `postProcessing/<functionObject>/` directory, 85 of
them. **Zero unexplained.** The regex is not matching directories that merely happen to be
named with digits.

## 3. The safety question, and it is the only one that matters

> **You cannot untrack evidence that a published claim cites.**

So: how many of these generated files does a committed record actually point at?

Method: harvest every `*_runs/`-shaped path token from all **362** tracked markdown files,
then intersect with the tracked file list. 179 distinct path tokens, of which **13 resolve to
an exact tracked file**.

| Population | Cited by **exact path** | Under a cited **directory** |
|---|---:|---:|
| Solver output (8,582 files) | **0** | 2,928 |
| Solver logs (778 files) | **0** | 131 |

**Not one solver-output field file, and not one log file, is cited by path anywhere in the
committed markdown corpus.**

### The positive control, because a zero is only as good as the method that found it

A citation extractor that finds nothing may be broken rather than reporting an absence. This
one finds **13** exact tracked-file citations, and their composition is the finding:

```
F11_runs/cavity_ladder.py            F4_runs/make_swbli_case.py
F11_runs/ladson_reference_note.md    F5_runs/cylinder_ladder_3d.py
F12_runs/reference/decode_tape.py    F7_runs/F7_damBreak_gate_comparison.png
F4_runs/billig_theory.py             F7_runs/F7a_diagnosis.json
F4_runs/build_inlet_profile.py       F7_runs/integrated_front.py
F7_runs/damBreak_.../constant/turbulenceProperties
F7_runs/old_spec_readings.py         F8_runs/s10_replay/s10d_corpus_replay.py
```

Every one is a **script, a reference note, a plot, a JSON summary, or a case dictionary** —
source and summary artifacts. The extractor demonstrably resolves exact file citations when
they exist. It finds thirteen, and finds zero field files and zero logs among them.

That is the shape G5 predicts, now measured instead of assumed: **records cite the code that
produced a result and the summary of it, never the raw field data.**

## 4. What this does and does not license

**It supports:** moving solver output and solver logs out of tracking without breaking a single
path citation in the committed record.

**It does NOT support** — and these are the ways this measurement could still be wrong, stated
because a scoping document that lists only its strengths is not a scoping document:

1. **Citation by description rather than path.** A record saying *"see the run outputs under
   F6b"* is a real dependency my method cannot see. 24 of the 25 `*_runs/` directories are named
   in tracked markdown; only `F5b_runs/` is not. **Directory-level naming is common; file-level
   citation is absent.** Untracking must therefore preserve *reachability of the archive*, which
   is what a gitignored `evidence/` with a README does and what deletion does not.
2. **Non-markdown consumers.** Scripts, tests and JSON records may open these paths. This
   measurement covers markdown only. **That sweep is owed before any move** and it is cheap.
3. **The one-way door.** Untracking is reversible; deleting is not. G5 offers both, and nothing
   here argues for the second.
4. **`F5b_runs/` is the odd one out** — tracked, and named in no committed markdown at all. That
   makes it the safest candidate and the one most deserving of a second look, since a run
   archive nothing references may equally be an orphan or evidence whose record was lost.

## 5. Recommended order when the window opens

1. Sweep the non-markdown consumers (§4.2). Zero-compute, and it closes the last gap.
2. Move solver **logs** first — 778 files, no path citations, and the most obviously regenerable.
3. Then solver **output** — 8,582 files. This is where the size is.
4. Leave `0/`, `constant/`, `system/` and every `.py`/`.json`/`.png`/`.md` under `*_runs/`
   tracked. They are source and summary, and the thirteen real citations all land there.
5. `.gitignore` rebuilt to match, and `evidence/` gets the README G2 requires — stating what
   lives there **and why it is untracked**, because an unexplained gitignored evidence tree is
   how a future cold-start agent concludes the evidence does not exist.

**Nothing in this list executes before Ladder V converges.** That is Katie's sequencing and it
is not mine to relax.
