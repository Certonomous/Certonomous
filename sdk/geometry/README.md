# Mission geometry

Surfaces the control-room viewport can render. OBJ and STL (binary or ASCII)
are both read by `chief_engineer.geometry`; large meshes are decimated
server-side before they reach the browser.

This is a **run-time staging area, not a source of truth**. `/api/geometry/upload`
writes here under the client's own filename, so an upload named `b52.stl`
overwrites the staged `b52.stl`. Copy demo surfaces to a laptop from
`demo-surfaces/` instead — it holds byte-identical copies and is git-tracked.

Most files here ARE committed (the exceptions today are the three largest:
`crm_wingbody.stl`, `nasa_hump.stl`, `onera_m6_wing.stl` — untracked, so an
overwrite is unrecoverable). Regenerate or drop in as needed:

```bash
# motorBike, from the OpenFOAM installation inside WSL
wsl -d Ubuntu -u foam -- bash -c \
  "gunzip -c /usr/lib/openfoam/openfoam2606/tutorials/resources/geometry/motorBike.obj.gz" \
  > motorBike.obj
```

To use a new surface, copy the `.stl` or `.obj` into this directory; the
viewport loads it at `/api/geometry?name=<filename>`.
