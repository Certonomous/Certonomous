# HEAVY ARTEFACT MANIFEST — `K0cG_runs`

**These paths are ON DISK and NOT AT HEAD.** They are filed here, by digest, so that a
later reader can prove the copy on disk is the copy the grade read — a gitignored path is
not a filed path, and this file is what makes the difference (`CLAUDE.md` WHERE THINGS
LIVE: *"Nothing is invisible merely because it is big"*).

Written 2026-08-27T16:28:04Z by a heat-transfer lane while landing the `K0cG_runs` evidence chain, under the
heat-transfer supervisor's ruling of 2026-08-27 amending item 5 of that lane's brief.
**No solver ran, no gate was graded and no verdict moved to write this file.**

## Why these are not at HEAD

Two different reasons, and they are not interchangeable:

- **`constant/polyMesh/`** — excluded **repo-wide, by standing policy**, at
  `.gitignore:66` (`**/constant/polyMesh/`). This lane did not choose that and did not
  change it. Regenerable from the case's tracked `build_cases.*` + `system/blockMeshDict`.
- **Numeric time directories** — excluded **by the supervisor's ruling** as reproducible
  bulk. The values a gate reads are not taken from these directories: they come from
  `postProcessing/` and `log.solve`, both of which ARE at HEAD.

## What IS at HEAD, so the chain is complete

Every `log.*`, `STATUS.*`, `DONE.*`, `ALL_DONE`, `*.out`, all of `system/`, all of
`postProcessing/`, the non-`polyMesh` `constant/` dictionaries, and `0/` + `0.orig/`.
The comparator (`analyse_*.py`), the gate (`gate_*.json`), `PREREG_TIMESTAMP.txt` and the
`RESULTS` record were already at HEAD before this landing.

## Digest method

For each directory: every file under it, recursively, is hashed with SHA-256; the lines
`<sha256>  <path relative to that directory>` are **sorted**; and the digest below is the
SHA-256 of those sorted lines joined by newline, with a trailing newline. Reproduce it
with the `digest()` function described in this paragraph — the ordering and the trailing
newline are both load-bearing.

## Manifest

| Directory | Bytes | Files | SHA-256 directory digest | Why not at HEAD |
| --- | ---: | ---: | --- | --- |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/38000` | 22,995,096 | 12 | `dd8893ec0034733bbdc1e21debf3aad8259111560fe95d5607b676191c0b6759` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/40000` | 33,854,182 | 16 | `92e7986388e2691582118e2d5ad7056f93c3c2f04320566757c0021e3f818a47` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_KE_x/constant/polyMesh` | 22,631,845 | 5 | `19e5f24a813e0915e4bba1c91e934a3cf82fe8dcc3017478e1046b4abcf6a704` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/38000` | 22,712,997 | 12 | `e62373a3a9924345b93be2c4c417b00a20184406cd4f4c671015a290e9c95074` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/40000` | 33,571,522 | 16 | `c92114f811a59de2b1443986f738a52de8c5f08a6ea17227d0c54c79db8ddf6c` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cG_runs/S_SST_x/constant/polyMesh` | 22,631,845 | 5 | `19e5f24a813e0915e4bba1c91e934a3cf82fe8dcc3017478e1046b4abcf6a704` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |

**Total: 158,397,487 bytes across 66 files in 6 directories.**

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*
