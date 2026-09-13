# PROPOSED — `write_solver_case.py`: state the wall treatment, never default it

**DRAFTED, NOT APPLIED.** Team: cfd. Lane: `lab-lane` under `cfd-supervisor`. 2026-09-13.

**Filed here and not in scratch: the scratchpad is never a handoff channel (L-186), and a draft
another agent must read lives under the case directory it belongs to.**

🔴 **THE SUPERVISOR READS THIS AS A DIFF.** It changes a script that determines the conditions of a
measurement, so `SUPERVISION_CHARTER` §3 check 1 binds and it is **not taken on relay**. This lane
has **not** applied it: `git diff -- cases/navier_class/DRIVAER/mesh/write_solver_case.py` is empty.

## Why

`DRIVAER_R5_..._PREREGISTRATION_DRAFT.md` §3 registers **`nutUSpaldingWallFunction`** on the `".*"`
vehicle block. The case R5 stages from (`r2_medium`, per `build_r5.sh` `SRC=$D/r2_medium`) carries
**`nutkWallFunction`**, and `write_solver_case.py` emits `nutkWallFunction` at **`:137`** and
**`:138`**. **Nothing converts it** — exhaustively traced, with controls, in
`docs/PUBLISHED_SETUP_COMPARISON_2026-09-13.md` §7.3.

**The case conforms to the registration, not the reverse.** Once gates are closed the only legal
direction is making reality match a registered value; leaving the writer emitting `nutk` would mean
running a case that contradicts its own registration.

**Three reasons this REMOVES the default rather than flipping it** (the supervisor's, recorded):

1. **Other arms legitimately use `nutk`** — the baseline does, and `floorNoSlip` should keep it. A
   hardcoded Spalding would create the mirror-image defect for the next arm.
2. **The value was hardcoded twice**, at `:137` and `:138` — **L-607's shape: one quantity in more
   than one place, and the one you did not rewrite is the one that wins.**
3. **A default is what let this happen.** The R2c arm got Spalding as a registered one-change; every
   arm after inherited `nutk` in silence. **No default means no silent inheritance.**

## Timing — the window is narrow and open

🔴 **`r5_wallfunction`'s mesh build was RUNNING when this was drafted** (`mpirun -np 16
snappyHexMesh`, log 25 s old at 18:26:30 UTC). **Nothing in that run root is touched.** When it
finishes, `write_solver_case.py` is the next step against it — and that command is what closes the
window. **Neither R5 root has `0.orig` or `0` yet, so applying this BEFORE that step leaves nothing
to reconcile and no before-image to keep.** The script also refuses to overwrite an existing
`0.orig` (`:58-59`) or `0` (`:62-63`), so it cannot silently rewrite a case that already exists.

## Verified on the proposed file, in scratch, never in the repo

- `python3 -m py_compile` — **COMPILES OK**.
- Invoked without the new arguments it **REFUSES**:
  `error: the following arguments are required: --nut-wall-vehicle, --nut-wall-floor`.
- **Not verified:** that it writes a correct case end-to-end — that needs a built mesh, and the only
  R5 mesh is mid-build. **Stated rather than claimed.**

## The diff

```diff
--- a/cases/navier_class/DRIVAER/mesh/write_solver_case.py
+++ b/cases/navier_class/DRIVAER/mesh/write_solver_case.py
@@ -50,6 +50,22 @@
     ap.add_argument("--root", required=True)
     ap.add_argument("--reference", required=True)
     ap.add_argument("--end-time", type=int, default=3000)
+    # WALL TREATMENT IS STATED, NEVER DEFAULTED.  A default is what let R5 stage
+    # from a case carrying nutkWallFunction while its registration said
+    # nutUSpaldingWallFunction: the R2c arm got Spalding as a registered
+    # one-change and every arm after it inherited nutk in silence.  These two
+    # are `required=True` with NO default, so this script REFUSES to write a
+    # case whose wall treatment nobody stated.  The value lived in two places
+    # (the floor block and the ".*" default) and one of them always won -- that
+    # is L-607's shape, so both now come from one decision each.
+    ap.add_argument("--nut-wall-vehicle", required=True,
+                    choices=("nutkWallFunction", "nutUSpaldingWallFunction"),
+                    help="nut wall function on the \".*\" vehicle block. "
+                         "The registration names it; this script does not guess.")
+    ap.add_argument("--nut-wall-floor", required=True,
+                    choices=("nutkWallFunction", "nutUSpaldingWallFunction"),
+                    help="nut wall function on floorNoSlip. Stated separately "
+                         "because it legitimately differs from the vehicle.")
     ap.add_argument("--write-interval", type=int, default=1000)
     a = ap.parse_args()
     root = Path(a.root)
@@ -134,8 +150,27 @@
         [("inlet", blk("type            calculated;", f"value           uniform {nut_in:.8g};")),
          ("outlet", blk("type            calculated;", f"value           uniform {nut_in:.8g};")),
          (f'"({slip})"', blk("type            slip;")),
-         ("floorNoSlip", blk("type            nutkWallFunction;", "value           uniform 0;"))],
-        blk("type            nutkWallFunction;", "value           uniform 0;")))
+         ("floorNoSlip", blk(f"type            {a.nut_wall_floor};",
+                             "value           uniform 0;"))],
+        blk(f"type            {a.nut_wall_vehicle};", "value           uniform 0;")))
+
+    # READ IT BACK FROM DISK.  An argument that was accepted is not evidence
+    # that the file carries it (rule 3): assert against the written bytes, and
+    # assert the OTHER treatment is absent so a stale literal cannot survive.
+    _nut = (root / "0.orig" / "nut").read_text()
+    _other = {"nutkWallFunction": "nutUSpaldingWallFunction",
+              "nutUSpaldingWallFunction": "nutkWallFunction"}
+    for _want, _where in ((a.nut_wall_vehicle, "vehicle"), (a.nut_wall_floor, "floorNoSlip")):
+        if _want not in _nut:
+            raise SystemExit(f"REFUSE: wrote 0.orig/nut but the {_where} treatment "
+                             f"{_want} is not in the file on disk.")
+    if a.nut_wall_vehicle == a.nut_wall_floor and _other[a.nut_wall_vehicle] in _nut:
+        raise SystemExit(f"REFUSE: 0.orig/nut still carries "
+                         f"{_other[a.nut_wall_vehicle]}, which nobody asked for.")
+    (root / "WALL_TREATMENT_AS_REQUESTED.txt").write_text(
+        f"nut_wall_vehicle={a.nut_wall_vehicle}\n"
+        f"nut_wall_floor={a.nut_wall_floor}\n"
+        "stated on the command line; no default exists in this script\n")
 
     (root / "constant" / "transportProperties").write_text(
         head("dictionary", "transportProperties", "constant") +
```

## What this does NOT do

- **It does not choose the values.** It forces them to be stated. R5's registration names
  `nutUSpaldingWallFunction` for the vehicle; `floorNoSlip` is a separate decision and this lane
  does not make it.
- **It does not move a gate, threshold, cap or label**, and it does not edit any frozen file.
- **It reads the file back from disk and asserts** (rule 3): an argument that was accepted is not
  evidence the bytes carry it, so it checks the written `0.orig/nut`, refuses if the requested
  treatment is absent, and refuses if the other treatment survives where it was not asked for.
- **It writes `WALL_TREATMENT_AS_REQUESTED.txt`** into the run root, so the case records what it was
  asked for rather than only what it contains.
