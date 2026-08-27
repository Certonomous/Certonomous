# MDS-1 — MESH DIMENSION SURVEY 1

**Home of the survey named, sized and owned in `docs/standards/MESH_STANDARD.md` §11.5, as
corrected by that file's §12 amendment (v1.7, 2026-08-27).** Owner: the cfd supervisor.

**This directory's existence discharges §11.5's anti-deferral clause.** Before it existed, every
record citing §11 to say *"threshold deferred to MDS-1"* was citing a survey that had not been
started, and §11.5 required such a record to say so in those words.

## What is here

| file | what it is |
|---|---|
| `mds1_survey.py` | the reader; carries its own planted controls (`--selftest`) |
| `MDS1_SURVEY.json` | the distribution, one record per log, plus the census |
| `MDS1_SURVEY_STDOUT.txt` | the survey run's own output, as evidence of the run |
| `MDS1_CONTROLS.txt` | the controls driven, both directions, as evidence |

## What MDS-1 IS, and what it is NOT

**IS:** a collection of the empirical distribution of two quantities across the lab's whole
`log.checkMesh` population — max aspect ratio (§11.3(a)) and whole-mesh cell-volume ratio
(§11.3(b)).

**IS NOT:** a gate. **No threshold is set, none is proposed, and no verdict word is issued** —
not by this reader and not by §11 or §12. There is no gate and no pre-registration behind a
survey. Collecting a survey and setting a gate are different acts; only the first is performed
here. §11.5 lists four requirements a later amendment must meet before any number is set; this
survey satisfies **one** of them.

**Cost: ZERO new compute.** Both quantities are read back from logs already on disk.

## Enumerator, stated — because §11.5's was not, and produced a false zero

```bash
find <root> -path '*/verification/runs/F5b_runs' -prune -o \
     \( -name 'log.checkMesh*' -o -name '*.log.checkMesh*' \) -type f -print
```

**Both filename shapes.** `log.checkMesh` AND the stem-prefixed `<stem>.log.checkMesh`
(`rung6b.log.checkMesh`, `A3-vcoarse-smoke.log.checkMesh`). §11.5's original enumerator saw only
the first and missed 87 logs, 78 of them the whole `verification/runs/MESH_AUDIT_runs/2026-08-08/`
pool. See §12.1.

**Excluded:** `.git/` (object store, not a run record); `verification/runs/F5b_runs/`
(**QUARANTINED** pending Sanaa's ruling on a permission denial — pruned by explicit path test,
counted, **never opened**).

**Roots include the out-of-repository corpus** `/home/ubuntu/certonomous-runs/` and
`/home/ubuntu/closure-data/`, which §11.5's population omitted and which hold 3 of the lab's 5
degenerate meshes (§12.7). **Those roots are READ ONLY**; nothing outside the repository is
written, modified, moved or deleted.

## Behaviour on non-positive minimum volume — fixed BEFORE collection (§12.3)

The cell-volume ratio is undefined precisely where the mesh is worst. A mesh whose minimum cell
volume is **negative, zero or unprinted** is given an explicit status (`MIN_NEGATIVE`, `MIN_ZERO`,
`MIN_VOLUME_LINE_ABSENT`), keeps its negative value and negative-cell count, **is counted in the
census and never dropped**, and is **excluded from ratio percentiles with the exclusion stated as
a number** beside them. A missing aspect field is `ABSENT` — a third label form, never a `null`
and never a number.

## Controls and refusals

Controls are driven on **every** invocation, not only under `--selftest`, each in **both**
directions — the perturbation must FIRE and its unperturbed twin must STAY SILENT. The reader
**refuses (exit 2) rather than degrades**: under `python -O`; if any `assert` statement is found
in its own source (required 0 `ast.Assert` nodes, verified on itself at every run); on unreadable
input; on a missing corpus root; on an unparsable value; and on any control that misbehaves.

## Pointer a reader may need: `MESH_AUDIT_runs` moved (§12.4)

`verification/campaign/MESH_BIRTH_CERTIFICATE_AUDIT_2026-08-08.md:45` cites its 78 retained logs
at `demo-output/website/campaign/MESH_AUDIT_runs/2026-08-08/`. **That path is empty and
`demo-output/` holds no `log.checkMesh` files at all.** The logs are **not lost**: all 78 are at
**`verification/runs/MESH_AUDIT_runs/2026-08-08/`**, moved at commit `a1fbe127` (2026-08-18,
MOVE_MAP batch 7). The audit document is another team's frozen record and is not edited; the
redirection is recorded here and in §12.4 so a reader landing on either finds it.

## The corpus is live — and the filed JSON already disagrees with §12.8 by one log

Every count is a dated snapshot, not a constant.

- §12.1's enumerator comparison was taken at **1005** repository logs.
- §12.8's distribution tables were taken at **1158** total logs (1006 repository + 152
  out-of-repository).
- **`MDS1_SURVEY.json` as filed here reads 1159**, because
  `verification/runs/F17c_runs/medium/log.checkMesh` appeared while this record was being written.
  `verification/runs/F17c_runs/coarse/log.checkMesh` had appeared minutes earlier, between the
  1005 and 1006 enumerations.

**This is the caveat working, not a defect.** Nothing was dropped between the snapshots (the
difference is additions only, verified by set difference), no percentile in §12.8 moves at the
displayed precision, and the census differences are exactly `+1` in `EQUALS_FORM` and `+1` in
`MIN_POSITIVE`. Re-derive with the command above; a later count disagreeing with either figure is
not a defect in either measurement, and a record that quoted one number as permanent would be the
misleading one.
