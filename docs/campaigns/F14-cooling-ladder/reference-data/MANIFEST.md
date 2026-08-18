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

---

## `wibron_2018_digitized/` (added 2026-08-17, F14 rung K2c-A)

**These files are DIGITIZED, not tabulated, and they are the only files in this
directory that are.** Everything under `betts_bokhari/` is a byte-identical copy
of a published data file; everything here is a reading taken off a figure.

| Field | Value |
| --- | --- |
| Source | Wibron, E., Ljung, A.-L., Lundström, T.S. (2018). Computational Fluid Dynamics Modeling and Validating Experiments of Airflow in a Data Center. *Energies* 11(3), 644. DOI `10.3390/en11030644`, CC-BY |
| Copy read | `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf`, SHA-256 `4de4798ed5eed60feda123c7a2398674a6a9177f44906175847d90f5227d7b77` |
| Figures read | 6a, 6b (per-rack temperatures) and 7a to 7e (velocity profiles). Figures 3 and 8 were read for controls only and are not written here |
| Method | Vector path extraction from the figures' PDF Form XObjects, calibrated on the axis tick marks. Not pixel digitization |
| Produced by | `../digitize_wibron2018.py --write`, which re-verifies the SHA-256 before reading |
| Digitization increments | temperature plus or minus 0.03 K, velocity plus or minus 0.007 m/s, height plus or minus 0.005 m, each derived from a control and restated in every file header |
| Controls and recovery errors | `../K2c_DIGITIZATION_ADDENDUM.md` §3. Seven controls; three recover values the paper states in its own prose |
| Files | `fig6_rack_temperatures.dat`, `fig7_velocity_profiles.dat` |

`NODATUM` in `fig6_rack_temperatures.dat` means the paper plots no experimental
bar for that rack and face, which is a property of the reference and not of the
extraction. It is R5 and R6 on the front, and R1, R5 and R6 on the back.


---

## Paper-library forwarding note — appended 2026-08-18

**Nothing above this line was edited.** The `docs/papers/` paths cited above were
correct when the sentences carrying them were written. Commit `5c0d2483`
(2026-08-18) refiled the paper library into topic subdirectories and renamed most
of its files, and `4323d7e3` lowercased two of the new names afterwards. Those
citations were left exactly as they stood, because each records where a file was
at the moment its statement was made; rewriting one would have changed what this
record says happened.

Each pair below was resolved by **git blob identity** — the old path's blob hash
matched to the path carrying the identical hash — and not by name similarity, and
each destination was then confirmed against the filesystem at commit `4323d7e3`.

| as cited above | the same bytes, as of `4323d7e3` |
| --- | --- |
| `docs/papers/wibron_ljung_lundstrom_2018_en11030644.pdf` | `docs/papers/data_center_indoor_airflow/wibron_ljung_lundstrom_2018_en11030644.pdf` |

The whole 87-path table was appended to `docs/papers/README.md` in the same
commit. `python3 scripts/check_paper_citations.py` re-derives the rows above and
exits non-zero if any destination stops resolving.
