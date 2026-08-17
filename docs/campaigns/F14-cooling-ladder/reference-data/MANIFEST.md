# Reference data manifest, campaign F14 gate K0c

## betts_bokhari/

Primary experimental data for the K0c turbulent rung. Subset of the ERCOFTAC
Classic Collection Case 079 archive, "Turbulent Natural Convection in an Enclosed
Tall Cavity, Experiments by Betts and Bokhari".

| Field | Value |
| --- | --- |
| Fetched | 2026-08-17 |
| Source page | `http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case079` |
| Full archive URL | `http://cfd.mace.manchester.ac.uk/ercoftac/lib/exe/fetch.php?media=cdata:case079:nctc-allfiles.zip` |
| Full archive SHA-256 | `4cd931c0c13a0ed5f898c39d94ea9f3b2ccd5dfc9cec75c00e37a818d7906dde` |
| Full archive contents | 236 data files in `Low-Ra/` and `High-Ra/` |
| Kept here | 22 files: the ones the K0c gate names, byte-identical copies |
| Publication of record | Betts, P.L., Bokhari, I.H. (2000). Experiments on turbulent natural convection in an enclosed tall cavity. Int. J. Heat and Fluid Flow, Vol. 21, pp. 675-683 (citation as printed on the case page; paper itself paywalled, Unpaywall `is_oa: false`, checked 2026-08-17) |

File naming, as used by the database: `m` mean, `f` fluctuation (rms); `t`
temperature, `v` vertical velocity; `z0` mid-span plane; the two-digit field is
y/H x 100; `rt`/`rb` are the top and bottom rubber-wall temperature profiles;
suffix `lo` is Ra = 0.86e6 (dT = 19.6 C), `hi` is Ra = 1.43e6 (dT = 39.9 C).
Units per file headers: x in mm, T in deg C, V in m/s.

Kept files:

- `mt_z0_{05,30,40,50,60,70,95}_{lo,hi}.dat` mean temperature profiles
- `mv_z0_50_{lo,hi}.dat` mean vertical velocity at mid-height
- `fvv_z0_50_{lo,hi}.dat` rms vertical velocity fluctuation at mid-height
- `mt_rt_z0_{lo,hi}.dat`, `mt_rb_z0_{lo,hi}.dat` top and bottom wall temperature
  profiles, the boundary conditions to impose on the partially conducting walls

Derived gate metrics are recomputed from these files by
`../compute_reference_metrics.py`; the gate spec quotes no derived number that the
script does not print.
