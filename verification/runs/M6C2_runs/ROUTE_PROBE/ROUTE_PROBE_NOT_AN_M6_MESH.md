# ROUTE_PROBE — NOT AN M6 MESH — THE BODY IS WRONG

**Anything produced in this directory is a ROUTE PROBE. It is NOT an ONERA M6 mesh and
must never be graded as one.** It is built on dafoam's A3 surface, whose body **departs
from AR-138**: the trailing-edge thickness is held constant in ABSOLUTE terms
(0.0011366 m at every station) where AR-138's conical loft requires `t_TE/c` constant.

| z (m) | t_TE/c | vs AR-138 1.4104e-03 |
|---:|---:|---:|
| 0.0000 | 1.410400e-03 | 1.0000x |
| 0.2883 | 1.576832e-03 | 1.1180x |
| 0.5745 | 1.786119e-03 | 1.2664x |
| 0.8459 | 2.043197e-03 | 1.4487x |
| 1.1631 | 2.456634e-03 | **1.7418x** |

**It matches the source to seven digits at the ROOT and departs monotonically outboard,
so a root-station spot check passes it.** Outboard the trailing edge is up to **74 %
thicker** than the source specifies.

**THE ONE QUESTION THIS PROBE ANSWERS:** does pyHyp, given a capped multi-patch surface,
produce a volume that clears openness, face pyramids, boundary closure,
non-orthogonality and skewness? **Five mesh-quality numbers about a METHOD.**

**NO Cp. NO forces. NO solve. NO M6 claim of any kind.** Written BEFORE the mesh.
