# HEAVY ARTEFACT MANIFEST — `K0cP_runs`

**These paths are ON DISK and NOT AT HEAD.** They are filed here, by digest, so that a
later reader can prove the copy on disk is the copy the grade read — a gitignored path is
not a filed path, and this file is what makes the difference (`CLAUDE.md` WHERE THINGS
LIVE: *"Nothing is invisible merely because it is big"*).

Written 2026-08-27T16:28:06Z by a heat-transfer lane while landing the `K0cP_runs` evidence chain, under the
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
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_c/30000` | 5,223,633 | 16 | `c3e22d9793c2f90a97cf54309518bba5a24a3861e9418478df86788a615f9c29` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_c/constant/polyMesh` | 3,229,207 | 5 | `75111874d8644d44d9212061b54eacf5ec113871fb95f938c12dd09aded14e49` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_f/40000` | 13,274,823 | 16 | `f19e827d2de8fa2ba060d7f175a1395f335d4a0115213049952b13e7ecb51d57` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P021_sq_f/constant/polyMesh` | 8,496,048 | 5 | `1144318b5d0b743e8e3f2355aecb35ca6e499c232b66cb3cba84d0a1cdbb048b` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_c/30000` | 5,245,556 | 16 | `b4989e8f5b2d945d1cf8b37078228b49fac78da05c21b7ee4340fbe9307ea7a5` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_c/constant/polyMesh` | 3,229,207 | 5 | `75111874d8644d44d9212061b54eacf5ec113871fb95f938c12dd09aded14e49` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_f/40000` | 13,330,191 | 16 | `558365ce2fa5ea9406a3c652aae8cdc65ac1564e9aa4312c7aace69539fb318e` | numeric time directory -- solver field output at the final written time |
| `verification/runs/F14-cooling-ladder/K0cP_runs/P102_sq_f/constant/polyMesh` | 8,496,048 | 5 | `1144318b5d0b743e8e3f2355aecb35ca6e499c232b66cb3cba84d0a1cdbb048b` | constant/polyMesh -- gitignored repo-wide by .gitignore:66 '**/constant/polyMesh/' |

**Total: 60,524,713 bytes across 84 files in 8 directories.**

*Nothing here was sent, filed, uploaded, posted or registered outside this box
(`CLAUDE.md` rule 7).*
