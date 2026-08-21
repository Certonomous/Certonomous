# ERCOFTAC Classic Collection case025 data files: normally-impinging jet from a circular nozzle

Retrieved 2026-08-21 from
http://cfd.mace.manchester.ac.uk/ercoftac/doku.php?id=cases:case025 (bulk
archive lib/exe/fetch.php?media=cdata:case025:ij-allfiles.zip, sha256
6d324a86d68123a275d0c2d826c6a922ef4ca2f03beeeb7a80e3dfa3c27ff0d8, 88 files,
reached over plain HTTP; the host refuses HTTPS). Site licence footer:
CC BY-NC-SA 4.0. Experiments of Cooper, Jackson, Launder and Liao (IJHMT 36,
1993, flow field) and Baughn et al. (Nusselt files). Re = 23000 and 70000,
H/D = 2 and 6, fully developed pipe exit.

- Flow-field uncertainty, stated verbatim on the case page: mean velocity
  within +/- 2 percent of bulk; u' +/- 4, v' +/- 6, uv about +/- 9 percent
  except near impingement.
- The four Nusselt files (ij2lr, ij2hr, ij6lr, ij6hr -nuss.dat) carry NO
  stated uncertainty on the page or in the headers; a 2.4 percent figure for
  Baughn and Shimizu is quoted by the ERCOFTAC KB Wiki UFR 3-09 page and is
  SECOND-HAND, unverified against the closed primary.
- CAUTION, verified 2026-08-21: the header of ij6lr-nuss.dat is mislabeled
  "H/D=2, Re=70000"; the filename and the distinct values indicate H/D=6,
  low Re. Do not trust the in-file header for that file.

Kept for rung T4 (impinging jet). A gate against the Nusselt data needs the
closed Baughn primaries for the in-paper uncertainty; until then the files
support report-only comparisons.
