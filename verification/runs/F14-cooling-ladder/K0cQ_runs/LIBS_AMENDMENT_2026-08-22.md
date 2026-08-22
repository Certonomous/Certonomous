# K0cQ libs amendment, 2026-08-22

**What changed:** `build_cases.sh` line 59 no longer writes the `libs` entry with a
blind `>>` append. It calls `scripts/foam_libs.py ensure`, which merges, writes,
re-reads from disk and asserts. L-221, and Sanaa's H-7: the assert goes at the
call site, not in a report.

**Why this is disclosed rather than done quietly.** K0cQ has already reported
(`K0cQ_RESULTS.md`), and that record's own falsifier names this builder: *"exhibit
a QCR arm, built by `K0cQ_runs/build_cases.sh` from these baselines, whose hot-wall
Nusselt differs from its twin by 1 % or more."* Charter 2d's boundary question is
*could this change move a number that a verdict depends on?* The answer here is no,
and that is shown below rather than asserted — so under 2d it "belongs in the
record with a date on it", which is this file.

## Freeze determination

Checked per the standing test — a file is frozen if a campaign doc records its sha
as frozen:

```
grep -rn "build_cases.sh" docs/campaigns docs/DOCKET.md | grep -i -E "frozen|sha"
```

**No hit. `build_cases.sh` is NOT frozen.** What K0cQ froze and verified by sha is
the **comparator**, `analyse_k0cq.py` (`K0cQ_RESULTS.md` §6, sha256 prefix
`94eddde98f0f61cf`, committed 22:10:06Z with zero completion markers on disk).
Charter 2d and `scripts/check_comparator_freeze.py` govern comparators; the
builder is not one, and no doc records its sha.

## The defect, stated precisely

The append was **not wrong on these six cases**. It was wrong *as a method*: it is
correct only because the K0cS/K0cX baselines happen to carry **no top-level `libs`
entry**. Against a baseline that carries one, `>>` produces **two** top-level
entries — a duplicate dictionary key, not a longer library list. The `grep -q`
guard that had been added ahead of this change does not catch that, because grep
cannot tell one entry from two. The append is a latent defect, not a realised one.

## The six built cases were verified correct

Both facts checked directly on disk, 2026-08-22:

| case | `Selecting RAS turbulence model` | top-level `libs` entries | sub-dict `libs` lines (not counted) |
| --- | --- | ---: | ---: |
| `Q_sq_c` | `kOmegaSSTQCR` | 1 | 8 |
| `Q_sq_f` | `kOmegaSSTQCR` | 1 | 8 |
| `Q_tl_c` | `kOmegaSSTQCR` | 1 | 11 |
| `Q_tl_f` | `kOmegaSSTQCR` | 1 | 11 |
| `Z_sq_c` | `kOmegaSSTQCR` | 1 | 8 |
| `Z_tl_c` | `kOmegaSSTQCR` | 1 | 11 |

The sub-dictionary column is the reason a naive check is useless here: every one of
these `controlDict`s carries 8 to 11 `libs (fieldFunctionObjects);` /
`libs (sampling);` lines inside `functions { }`. Those are function-object loaders,
not the solver's library list. `foam_libs.py` tracks brace depth, so it counts the
one that matters and ignores the rest.

Re-verified by the shared helper, all six `OK`:

```
python3 scripts/foam_libs.py assert <case>/system/controlDict libkOmegaSSTQCRTurbulenceModels.so
```

**No solver was re-run and no case directory was written to.** The solver logs are
the original ones; the library named in each `controlDict` is the library the log
records the solver selecting. No number in `gate_k0cq.json` is touched by this
change.

## The one difference a re-run would produce, disclosed

`ensure_libs` inserts the entry **after the `FoamFile` banner**; the old append put
it **after the closing footer comment**. Both are legal OpenFOAM and load the same
library — the six shipped cases prove the footer position works. But a re-run of
the patched builder therefore yields a `controlDict` that is **byte-different from
the shipped one, in the position of that single line and nothing else**. Verified
by rebuilding one case into a scratch tree and diffing against the case that
actually ran (`Q_sq_c`): the complete difference set is that line moving from line
170 to line 18. Anyone re-deriving these cases byte-for-byte should expect it.

## Also amended, same sitting

`K0cT_runs/continue_cases.sh` and `K0cT_runs/continue_past_residual.sh` — neither
frozen by the same test — each ran three `sed -i` rewrites of `controlDict` with no
post-check. `sed -i` exits 0 when it matched **nothing**, so an unchanged dictionary
and a correctly rewritten one were indistinguishable. Each now asserts the
resulting **state** on disk (`startFrom latestTime`, `endTime`, `writeInterval`) and
REFUSEs with exit 2 on mismatch. The state, not "did sed run": a second
continuation legitimately finds `startFrom` already `latestTime`.

Verified by planting a `controlDict` whose `endTime` spacing defeats the sed — the
script REFUSEs with exit 2 **before** reaching the solver, where previously it would
have continued the run to the wrong `endTime`.
