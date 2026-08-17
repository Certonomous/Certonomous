# Mission geometry

Surfaces the control-room viewport can render. `chief_engineer.geometry` reads
both OBJ and STL, in binary or ASCII, and decimates large meshes server-side
before they reach the browser.

**This is a run-time staging area, not a source of truth.**
`/api/geometry/upload` writes here under the client's own filename, so an upload
named `b52.stl` overwrites the staged `b52.stl`. Copy demo surfaces to a laptop
from `demo-surfaces/` instead: it holds byte-identical copies and is git-tracked.

Every file in this directory is committed at frame `8cefb4e9`, including the
three largest, `crm_wingbody.stl`, `nasa_hump.stl` and `onera_m6_wing.stl`:

| Enumeration at `8cefb4e9` | Files | Command |
|---|---|---|
| Tracked here | 24 | `git ls-files sdk/geometry/` |
| Untracked, not ignored | 0 | `git ls-files --others --exclude-standard sdk/geometry/` |
| Gitignored | 0 | `git ls-files --others --ignored --exclude-standard sdk/geometry/` |

**An upload is still destructive, and being tracked is what makes it
recoverable.** Check before assuming: a surface that arrives here untracked and
is then overwritten is gone.

Regenerate or drop in as needed. The motorBike surface comes from the OpenFOAM
installation inside WSL:

```bash
wsl -d Ubuntu -u foam -- bash -c \
  "gunzip -c /usr/lib/openfoam/openfoam2606/tutorials/resources/geometry/motorBike.obj.gz" \
  > motorBike.obj
```

To use a new surface, copy the `.stl` or `.obj` into this directory. The viewport
loads it at `/api/geometry?name=<filename>`.
