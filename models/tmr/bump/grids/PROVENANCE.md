# NASA TMR bump-in-channel grids — byte provenance

NASA distributes the bump family two ways; both were used and they agree
byte-for-byte where they overlap. No grid here was regenerated locally.

## Sources

1. **tmbwg.github.io mirror** (GitHub Pages of github.com/TMBWG/turbmodels,
   retrieved 2026-07-31): serves only the two smallest grids as regular files;
   the 353x161 and larger are git-lfs pointers whose media endpoint returns
   404, so they cannot be fetched from the mirror.
2. **NASA's official zip** `https://www.nasa.gov/wp-content/uploads/2026/02/bumpgrids-grids.zip`
   (linked from the mirror's bump_grids.html; retrieved 2026-07-31 UTC;
   166,394,812 bytes, sha256
   `4542e3bd6d2be6f88c6e6e903a2439e2cffe9d1ada2df88cfcab912f11e519d4`),
   containing `u/piyer/nasa_tmr/gitlab/turbmodels/Bump/Grids/*`. The full
   family in every published format comes from here.

## Files held, with sha256 of the decompressed PLOT3D bytes

| file | decompressed sha256 | byte source |
|---|---|---|
| `bump_4levelsdown_89x41.p3dfmt.gz` | `3a325e11b7244dfa46fc0935c30ed4237e4718243b6bd504ad58a87da626ec79` | mirror 2026-07-31; **identical bytes** confirmed inside the NASA zip |
| `bump_3levelsdown_177x81.p2dfmt.gz` | `0f11cf2818516326be73b4523d84b7132f395df354b300aa1caf3971bff16902` | mirror 2026-07-31; **identical bytes** confirmed inside the NASA zip |
| `bump_3levelsdown_177x81.p3dfmt.gz` | (as shipped in zip, gz sha256 `92354bba4429061c8b35de49122251f2feca5b437828ff2ee4ca0bf6e15d5443`) | NASA zip, copied out unmodified |
| `bump_2levelsdown_353x161.p3dfmt.gz` | (gz sha256 `437d4fe0314df090b51453d20fd1d518c3a71d70a745c02a0693d9fa7cadb35c`) | NASA zip, copied out unmodified |
| `bump_1levelsdown_705x321.p3dfmt.gz` | (gz sha256 `24b5eb0640d1e93f9aff0c3ecace7fb4246985ff7a4e9e9f43dd25ab487b7590`) | NASA zip, copied out unmodified |

The 0levelsdown 1409x641 p3dfmt (14.6 MB gz) is in the same zip and was not
copied into the repo: it is far outside any affordable solve on this box
(arithmetic in the w1 campaign record) and can be re-extracted from the zip
by its URL and sha256 above at any time.

## Measured identities (read from the node arrays, 2026-08-01)

- Point-drop: `177x81 == 353x161[::2, ::2]`, `89x41 == 177x81[::2, ::2]`,
  `353x161 == 705x321[::2, ::2]`, all to **max |delta| = 0.0** in both
  coordinates — the family is exact point coarsenings of one grid, one h,
  refinement ratio exactly 2.
- The mirror's `177x81.p2dfmt` equals the zip's `177x81.p3dfmt` i=0 plane to 0.0.
- Axes in the p3dfmt files: i = span (y in [-1, 0], 2 planes, identical in
  the other coordinates to 0.0), j = streamwise (x in [-25, 26.5]),
  k = wall-normal (0 to 5); bump crest 0.05 at x = 0.75.
- First wall-normal spacing at x = 0.75: 8.05762e-06 / 3.97693e-06 /
  1.98201e-06 (89x41 / 177x81 / 353x161) — near-exact halving; at the
  x = -25 symmetry plane NASA relaxes it to 3.21e-3 / 1.60e-3 / 8.00e-4.

Reader used: `/home/ubuntu/certonomous-runs/w1-bump-nasa-grids/read_p3d.py`.
