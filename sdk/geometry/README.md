# Mission geometry

Surfaces the control-room viewport can render. OBJ and STL (binary or ASCII)
are both read by `chief_engineer.geometry`; large meshes are decimated
server-side before they reach the browser.

Files here are **not committed** — they are large binary assets. Regenerate or
drop in as needed:

```bash
# motorBike, from the OpenFOAM installation inside WSL
wsl -d Ubuntu -u foam -- bash -c \
  "gunzip -c /usr/lib/openfoam/openfoam2606/tutorials/resources/geometry/motorBike.obj.gz" \
  > motorBike.obj
```

To use a new surface, copy the `.stl` or `.obj` into this directory; the
viewport loads it at `/api/geometry?name=<filename>`.
