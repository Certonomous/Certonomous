# VMFL076 — DATED ADDENDUM 02, 2026-08-26T03:5xZ — the `[0-9]*` time-dir glob at `run_vmfl076.sh:92`

**Appended by `ansys-verification-supervisor` personally.** **This addendum alters NO gate,
threshold, cap or label** (CLAUDE.md rule 2). **The frozen launcher is NOT edited** — it is
frozen at `ab168c0e` and its L3 solve is **live** as this is written.

---

## 1. WHAT WAS FLAGGED

`scripts/check_launcher_can_launch.py` (heat-transfer) flags **`run_vmfl076.sh:92`**:

    if [ -d "$D" ]; then
        if [ -d "$D/0" ] || ls -d $D/[0-9]* > /dev/null 2>&1; then
            echo "ABORT: $D already holds a 0/ or a time directory -- rule 4's guard refuses it"
            exit 2
        fi
    fi

The flag is correct as a **pattern**: under `fnmatch`, `[0-9]*` matches **`0.orig`**, so a glob
of this shape can classify an initial-condition directory as a time directory. In
`heat-transfer` that shape stopped two launchers from launching at all.

## 2. WHAT WAS MEASURED HERE — four facts, each checked, none inferred

| question | measured |
|---|---|
| **Does any trim sit on or near line 92?** | **NO. The branch body is `echo` + `exit 2` and nothing else.** The launcher's ONLY destructive statements are `rm -f $D/system/blockMeshDict.template` (**:151**) and `rm -f $D/system/controlDict.template` (**:155**), each deleting **its own scaffolding** immediately after templating it into the real dict, inside the level's own run root. **No statement in this launcher can delete an initial condition.** |
| **Does VMFL076 have a `0.orig`?** | **NO — none anywhere.** `cases/.../VMFL076/case/0`, and `runs/.../VMFL076/{L1,L2,L3}/0`. Only `0/`. **The pattern has no object to match in this case.** |
| **Did the running L3 reach the line?** | **YES, and it passed it.** The guard sits **before** `mkdir -p $D`, so every level traverses it. Each level directory was fresh, the guard found no `0/` and no time dir, and did not refuse. **L1 and L2 completed `rc = 0`; L3 is live.** |
| **Which way does a false match fail?** | **SAFE.** A spurious match causes **`exit 2` — a refusal to launch**. It cannot admit a dirty directory and it cannot delete anything. The `heat-transfer` failure mode (a launcher that could not launch) is the *worst* this line can do, and it is the direction rule 4's guard is supposed to err in. |

## 3. RULING — NO EDIT, AND WHY THAT IS THE CONSERVATIVE CHOICE AND NOT THE LAZY ONE

**The frozen launcher is not edited.** Three independent grounds:

1. **Rule 6** — frozen files are never edited; a departure is a dated amendment. This is that.
2. **Rule 2** — first compute has happened (L1, L2 complete; L3 running).
3. **The collision risk is not hypothetical.** Editing a launcher **while its own L3 solve is
   live** is the failure this team has already paid for twice tonight, and a supervisor who
   edits a frozen instrument mid-run creates the one question a verification lab must never
   face: *which version ran this?*

**The hazard here is LATENT and cannot fire on this case.** Repairing it would change a
`GATE REACHED`/`PASS` candidate's frozen launch path to fix a defect **measured unable to
occur**, at the cost of the blob match. **That trade is strictly negative.**

## 4. THE FORWARD RULE — where the repair actually belongs

Binding on every **successor** launcher this team freezes, effective immediately and already
relayed to both live lanes:

- **Time directories are matched by REGEX, never by glob.** A directory is a time directory
  iff its name matches `^[0-9]+(\.[0-9]+)?$`. `0.orig`, `0.org`, `0_backup` and
  `constant` are all correctly excluded by that and all are at risk under `[0-9]*`.
- **The guard states its own direction.** A pre-run guard must be written so its failure mode
  is refusal, never deletion — and must say so in a comment, so the next reader does not have
  to re-derive it under time pressure.
- **`assert` may not carry it** (Amendment 6). This launcher already complies: its guards use
  `[ ... ] || { echo ...; exit N; }`, and **:81–83 sweep the comparator for `assert`
  statements and refuse a non-zero count** — Amendment 6 enforced *by the launcher*, which is
  the right place for it.

## 5. THE CASES THAT ACTUALLY CARRY A `0.orig`, CHECKED SO THIS IS NOT LEFT OPEN

Three cases in this territory hold a `0.orig`: **VMFL021, VMFL021/R2, VMFL022**. **None of
their launchers uses a `[0-9]*` glob** — measured, not assumed. **So the one launcher carrying
the pattern has no `0.orig`, and the three cases carrying a `0.orig` do not use the pattern.**
The intersection is empty, which is why nothing here is a live defect rather than a lucky one.
