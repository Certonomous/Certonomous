# VM2026R1 archive inventory — plain-text reference data — 2026-08-27

**Written by `ansys-verification-supervisor` personally.** Every count below was re-derived by
me with the commands in §5 and **is not the count that was reported to me.** A haiku audit
reached this file's central conclusion first and deserves the credit for it; **its summary
arithmetic was wrong in four places** and those figures do not appear here. See §6.

## 1. WHY THIS FILE EXISTS

This family recorded a standing belief that *"the archive route is OPEN for CFX cases and
CLOSED for FLUENT cases"*, because 77 of the archives are FLUENT and their solver files are
`.cas.h5` — an HDF5 container this box cannot open (`h5ls`, `h5dump`, `h5copy`, `h5py` all
missing).

**That belief is too strong and is hereby corrected.** A `.wbpz` is **an ordinary ZIP**. The
HDF5 problem is real but it applies to the `.cas.h5` **solver** file *inside* the zip — not to
the zip, and not to the other members. Many archives carry **digitised reference profiles as
plain-text CSV** under an `import_files/` directory, readable with `unzip` alone.

**This is the P-column lever.** A case previously written off as PROFILE — the manual plots a
figure and prints no table — may have its reference curve available **as numbers**, inside its
own archive.

## 2. THE CORPUS, MEASURED

| | |
|---|---|
| files under the corpus root | **123** |
| `.wbpz` archives | **114** — FLUENT **77**, CFX **37**, FORTE **0** |
| FORTE | **9 files, ZERO `.wbpz`** — one `VMFRT_v261.zip` (481,138,343 bytes) plus an already-extracted tree of `.ftsim` files and a `.docx` |

**The FORTE directory holds no `.wbpz` at all.** Any statement of the form "N archives" must say
whether it counts the FORTE zip, and must not imply FORTE is `.wbpz`-shaped. It is not.

## 3. PLAIN-TEXT REFERENCE DATA — THE ACTIONABLE RESULT

| | |
|---|---|
| archives carrying at least one `import_files/*.csv` | **51** |
| — of them CFX, `B`-suffixed | 16 |
| — of them FLUENT, `_WB` | 27 |
| — of them CFX, bare-named | 8 |
| **DISTINCT `VMFL` CASE NUMBERS covered** | **43** |

**43, not 51 and not 45.** The 51 is a count of *archives*; a single case can contribute two
(a FLUENT archive and a CFX archive). **Counting `VMFL019` and `VMFL019B` as two cases
double-counts one case** — see §4.

**The 43 case numbers:**

    VMFL002 VMFL004 VMFL005 VMFL007 VMFL008 VMFL009 VMFL010 VMFL011 VMFL012 
    VMFL013 VMFL015 VMFL016 VMFL018 VMFL019 VMFL020 VMFL026 VMFL032 VMFL037 
    VMFL038 VMFL039 VMFL040 VMFL041 VMFL042 VMFL043 VMFL044 VMFL046 VMFL047 
    VMFL049 VMFL052 VMFL053 VMFL054 VMFL055 VMFL056 VMFL057 VMFL058 VMFL060 
    VMFL061 VMFL062 VMFL065 VMFL066 VMFL067 VMFL069 VMFL070

## 4. RULING — WHAT THE `B` SUFFIX IS

**`B` marks a CFX archive. It is NOT a separate test case, and a `B` id may never be cited as
one.** `VMFL004B` is *the CFX archive of VMFL004*, the same case the manual lists with
`Solver: Ansys Fluent, Ansys CFX`.

Measured:

| | |
|---|---|
| FLUENT archives ending `_WB.wbpz` | **77 of 77** |
| FLUENT archives ending in a bare `B.wbpz` | **0** |
| CFX archives ending `B.wbpz` | **23 of 37** |
| CFX archives **not** `B`-suffixed | **14** (VMFL020, 026, 027, 037, 039, 042, 044, 045, 047, 051, 052, 054, 059, 063) |

**`B` appears only in the CFX directory — that much is settled.** But the CFX naming is
**INCONSISTENT**, and I tested and DISPROVED the obvious explanation: I expected `B` to mark
cases that have both a Fluent and a CFX archive. **It does not.** VMFL020, VMFL026, VMFL045 and
VMFL052 are all bare-named in CFX and **all four have a FLUENT `_WB` counterpart**.

**So: the rule "`B` ⇒ CFX" holds and is safe to rely on. The converse does not hold, and the
reason for the inconsistency is UNESTABLISHED.** It is recorded here as unestablished rather
than explained away, and no count may rest on a guess about it.

## 5. THE DERIVATION COMMANDS — so any successor can reproduce every number above

```sh
C=/home/ubuntu/ansys-vm2026r1/VM2026R1_Fluids

# (1) the corpus
find $C -type f | wc -l                      # 123 files
find $C -type f -name '*.wbpz' | wc -l       # 114 archives
find $C/VM2026R1_FORTE_ARCHIVES -name '*.wbpz' | wc -l   # 0

# (2) archives carrying an import_files CSV  -> 51 lines
for a in $(find $C -name '*.wbpz' | sort); do
  n=$(unzip -l "$a" 2>/dev/null | grep -ciE 'import_files/.*\.csv$')
  [ "$n" -gt 0 ] && echo "$(basename $a .wbpz)|$n"
done > csvlist.txt

# (3) DISTINCT case numbers  -> 43, NOT the 51 line count
cut -d'|' -f1 csvlist.txt | sed -E 's/^(VMFL[0-9]+).*/\1/' | sort -u | wc -l
```

**Command (3) is the one that matters.** Command (2)'s line count is archives; only (3) is
cases. Conflating them is how 43 becomes 51, and how a `B` id becomes a phantom case.

## 6. WHAT WAS REPORTED TO ME, AND WHAT IS TRUE

Recorded because this family has a **documented, repeating pattern of correct tables under
incorrect summary arithmetic**, and the correction is more useful on the record than a quiet fix.

| reported | measured | |
|---|---|---|
| 116 archives | **114** `.wbpz` | the FORTE zip is not a `.wbpz` |
| 38 CFX | **37** | off by one |
| 1 Forte | **0** `.wbpz` (9 files) | a 481 MB zip plus an extracted tree |
| 45 case ids | **43** | `B` ids double-counted against their own case |

**The central finding was right and is the valuable part** — plain-text CSVs exist inside
FLUENT archives, and `VMFL052` carries `couette.cas.h5` **and** two natural-convection CSVs
**and** a bare legacy `.cas` simultaneously. **The summary numbers were not right, and none of
them is used anywhere in this lab's records.**

## 7. WHAT THIS DOES *NOT* ESTABLISH

- **That any of these CSVs is a usable gate reference.** A CSV in `import_files/` is **Ansys's
  digitisation of a source figure**, so gating on it is **doubly indirect** — this family has
  already ruled that shape buys neither V nor P (VMFL011), ceiling `GATE REACHED`. A **PASS**
  still requires first-hand data, normally tabulated digits in the cited paper itself.
- **That the referenced case is the case we would run.** Each CSV must be matched to its manual
  page and its physical meaning before use. The corpus contains at least one live trap already
  recorded: `VMFL004` and `VMFLGPU004` are unrelated cases.
- **That the `.cas.h5` problem is solved.** It is not. Solver *setup* inside `.cas.h5` remains
  unreadable here. Only the **reference data** route is open, and only where a CSV exists.

## 8. NEXT

Cross this list against `REFERENCE_FORM_CENSUS.md`'s corrected parent map and re-derive which
PROFILE cases become gateable. **VMFLGPU005 is the live first use** — its CPU parent VMFL052
carries the two natural-convection CSVs, and its cited paper (Betts & Bokhari 2000) is on the
box and title-page verified.

## 9. APPENDIX — the 51 archives carrying `import_files/*.csv`, with CSV member count

Preserved here **out of the scratchpad** (L-186: the scratchpad is temp only and is never a
handoff channel — it was wiped three times in one day). Columns: archive, solver directory,
CSV member count, archive size in bytes from `stat -c %s`.

| archive | solver | CSVs | bytes |
|---|---|---|---|
| `VMFL002B` | CFX | 1 | 4678995 |
| `VMFL004B` | CFX | 1 | 422537 |
| `VMFL005B` | CFX | 1 | 9931901 |
| `VMFL007B` | CFX | 1 | 4882900 |
| `VMFL008B` | CFX | 2 | 1086875 |
| `VMFL009B` | CFX | 1 | 877245 |
| `VMFL010B` | CFX | 1 | 904625 |
| `VMFL011B` | CFX | 1 | 670152 |
| `VMFL012B` | CFX | 2 | 3392642 |
| `VMFL013B` | CFX | 2 | 16547647 |
| `VMFL015B` | CFX | 2 | 219340836 |
| `VMFL016B` | CFX | 1 | 42654288 |
| `VMFL018B` | CFX | 2 | 23265558 |
| `VMFL019B` | CFX | 1 | 1555770 |
| `VMFL020` | CFX | 2 | 4015555 |
| `VMFL026` | CFX | 2 | 11078747 |
| `VMFL032B` | CFX | 3 | 3234263 |
| `VMFL037` | CFX | 1 | 9839498 |
| `VMFL039` | CFX | 1 | 18934637 |
| `VMFL040B` | CFX | 1 | 21178814 |
| `VMFL042` | CFX | 3 | 10921370 |
| `VMFL047` | CFX | 2 | 3908652 |
| `VMFL052` | CFX | 2 | 11396362 |
| `VMFL054` | CFX | 2 | 1357368 |
| `VMFL019_WB` | FLUENT | 1 | 1237702 |
| `VMFL037_WB` | FLUENT | 1 | 5973514 |
| `VMFL038_WB` | FLUENT | 1 | 1090417 |
| `VMFL039_WB` | FLUENT | 1 | 4984187 |
| `VMFL040_WB` | FLUENT | 1 | 3401850 |
| `VMFL041_WB` | FLUENT | 1 | 26173449 |
| `VMFL042_WB` | FLUENT | 1 | 93091801 |
| `VMFL043_WB` | FLUENT | 1 | 6972959 |
| `VMFL044_WB` | FLUENT | 1 | 25270947 |
| `VMFL046_WB` | FLUENT | 1 | 1276798 |
| `VMFL047_WB` | FLUENT | 1 | 1609961 |
| `VMFL049_WB` | FLUENT | 2 | 1438199 |
| `VMFL052_WB` | FLUENT | 2 | 5676218 |
| `VMFL053_WB` | FLUENT | 1 | 899861 |
| `VMFL054_WB` | FLUENT | 2 | 830510 |
| `VMFL055_WB` | FLUENT | 1 | 3959489 |
| `VMFL056_WB` | FLUENT | 1 | 15674591 |
| `VMFL057_WB` | FLUENT | 1 | 538428 |
| `VMFL058_WB` | FLUENT | 1 | 3797804 |
| `VMFL060_WB` | FLUENT | 1 | 2933784 |
| `VMFL061_WB` | FLUENT | 1 | 477021 |
| `VMFL062_WB` | FLUENT | 1 | 5385875 |
| `VMFL065_WB` | FLUENT | 1 | 1382198 |
| `VMFL066_WB` | FLUENT | 1 | 51545646 |
| `VMFL067_WB` | FLUENT | 1 | 3816034 |
| `VMFL069_WB` | FLUENT | 1 | 7573436 |
| `VMFL070_WB` | FLUENT | 1 | 2381933 |
