# F4 — STATE REPORT BEFORE ANY CONVERSION DOCUMENT IS WRITTEN

**Written 2026-08-25T21:10:19Z. Team: cfd. Lane: lab-lane under cfd-supervisor.**
**Zero compute. No solver launched, no mesh built, no case directory created.**

**Why this report exists, stated first.** The brief that preceded this one
(commit `1251a015`) tasked a lane to *fire* the F3 and F11 conversions; both were
already fired, graded and closed, and firing either would have overwritten a
graded artifact and broken a freeze. The lane refused and showed the disk. This
lane was therefore instructed to **establish F4's state from HEAD before writing
anything**, and this document is that establishment. It writes no gate, no band,
no threshold and no cap. It is not a pre-registration and must not be cited as
one.

**Reading frame.** Every fact below is read from a git object, never from the
worktree and never from `git status`. The shared index stages ~1,266 paths
differing from HEAD, so `git status` reports committed files as untracked;
`git ls-files --others --exclude-standard` is equally unusable here. The read
commit is `ed726454103307486f98d8fe74319c1a3c8169ef` ("F1 te-study SWEEP"). HEAD
moved past it during this lane's work (peers commit constantly); nothing below
depends on a file a later commit touched, and the commit landing this report
re-captures HEAD in its own shell invocation per standing rule 10.

---

## 0. Staleness check on the frozen F4 documents — ALL FOUR ARE CLEAN

Eight tracked `.md` under `verification/` and `docs/` are known to be strict
prefixes of their HEAD blob — appended amendments that landed in a commit and
never landed on disk. A grading decision taken against such a worktree copy is
taken against withdrawn text. **Every F4 document was therefore `cmp`'d against
its HEAD blob before being read**, and the result is recorded here rather than
asserted:

| document | HEAD bytes | disk bytes | `cmp` vs HEAD blob |
|---|---:|---:|---|
| `verification/campaign/F4_hypersonic_blunt_body.md` | 88 604 | 88 604 | **IDENTICAL** |
| `verification/campaign/F4_hypersonic_blunt_body.json` | 228 928 | 228 928 | **IDENTICAL** |
| `verification/campaign/F4_SIGFPE_STEP01_PREREGISTRATION.md` | 107 242 | 107 242 | **IDENTICAL** |
| `verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` | 45 021 | 45 021 | **IDENTICAL** |

**None of the four F4 documents is stale.** F4 is not among the eight. The
instruments were checked the same way and are also identical to HEAD (§5).

---

## 1. F4's current recorded verdict, and where it lives

**F4 carries TWO recorded `PASS` verdicts, both in
`verification/campaign/F4_hypersonic_blunt_body.md`, both dated 2026-07-28
(repo @ `b23138d`), and a third gate recorded "Not run".**

| gate | where | reference | fine-mesh result | recorded verdict |
|---|---|---|---|---|
| **1 — shock standoff at stagnation** | `F4_hypersonic_blunt_body.md` §4 (heading at line 97), verdict sentence at the foot of §4; Summary table row 1 (§ "Summary", heading line 339) | Billig (1967) δ/R = 0.386·exp(4.67/M²) | M=6 δ/R = **0.4485 ± 0.0017** (dev **+2.06 %**); M=7 **0.4345 ± 0.0017** (**+2.33 %**); M=8 **0.4181 ± 0.0033** (**+0.70 %**) | **PASS** |
| **2 — windward Cp distribution** | same file §5 (heading line 143), verdict sentence in §5; Summary row 2 | modified Newtonian (Lees), Cp_max via Rayleigh–Pitot | RMS = **3.91 %**, **3.91 %**, **3.87 %** of Cp_max at M = 6, 7, 8 | **PASS** |
| **3 — SWBLI stretch (compression ramp / cyl-flare)** | same file §7 (line 183), §7a (line 187); Summary row 3 | Kussoy & Horstman M=7.05 cyl–flare, NASA TM 101075 | — | **"Not run"** |

The Summary also records **"Rung reached: GATE (fine mesh), both primary gates,
all three Mach numbers."** Total recorded compute for the nine CFD runs:
**14.66 core-minutes** (§6, "Evidence record").

**Where the verdict lives, cross-checked.** `verification/campaign/` is the
verdict location, and the run tree carries only measurements:
`verification/runs/F4_runs/cyl/M{6.0,7.0,8.0}/{coarse,medium,fine}/result.json`
hold per-case values and **no band and no verdict**. Independently,
`verification/campaign/F_FAMILY_TRIPLE_CROWN_SURVEY.md` line 152 enters F4 on
the triple-crown map as **`GATE REACHED`, missing G and P**, and line 576 records
that F3 and F4 are *"entered as `GATE REACHED`"* rather than at a higher tier
precisely because their V-greens rest on comparisons made before any
pre-registration existed.

**Nothing in the F4 corpus uses the token `HOLD`.** A `grep` over the whole
88 KB record returns **0** occurrences of `HOLD`, `GATE REACHED`, `GATE FAIL`,
`NOT A RESULT`, `BLOCKED` and `PENDING`, and **14** of `PASS`.

---

## 2. What a conversion would convert — and it is owed, on grounds that do not
   need the withdrawn text

### 2.1 The defect, established from artifacts

**Both 2026-07-28 `PASS` verdicts were graded against bands written after their
numbers were known. There is no pre-registration for either gate.** The only F4
pre-registration at HEAD is `F4_SIGFPE_STEP01_PREREGISTRATION.md`, which is a
**SIGFPE crash diagnostic on a different case tree** and whose §0 explicitly
forbids issuing any `PASS`, `GATE REACHED` or `GATE FAIL` from it — so it does
not pre-register Gate 1 or Gate 2 and cannot be read as doing so.
`F_FAMILY_TRIPLE_CROWN_SURVEY.md` classifies it the same way at line 440: *"a
**SIGFPE crash diagnostic** — **neither** — not a V/G/P rung."*

This is the identical defect class the F3 conversion exists to repair. Quoting
`F3_CONVERSION_PREREGISTRATION.md` §1 (HEAD blob), which states the principle in
general terms: *"Under standing rule 2 the freeze is the evidentiary content of a
pre-registration: it proves the gate could not have been chosen to fit the answer.
A band written afterwards proves nothing about the band, whatever it proves about
the solver."*

And F4's own §4 verdict line carries the same shape of softened `PASS` that the
F3 conversion was written for. F4 §4 reads **"Verdict: PASS, with the above
caveats stated plainly rather than buried"** — and the caveats are not cosmetic:
§4 records that **M=8 fine is not resolved above its own noise floor**
(deviation +0.70 % against a snapshot scatter of 0.8 %), and that **standoff does
not converge monotonically with refinement** (M=6: −0.33 → −0.60 → **+2.06 %**;
M=8: +6.62 → −1.69 → **+0.70 %**, coarse→medium→fine). Under standing rule 5 a
non-monotone triple cannot carry a GCI at all, and a `PASS` issued over one was
issued without the gate rule 5 requires. **That is the substantive reason a
conversion is owed, and it is visible in the record's own numbers.**

### 2.2 Two independent lab records already name this as an open blocker

- `verification/campaign/F_FAMILY_TRIPLE_CROWN_SURVEY.md` lines 262–263:
  *"**Blocker that is not compute:** **no F4 conversion pre-registration has been
  written.**"* Line 647 repeats it in the survey's own status table.
- `docs/LAB_STATE.md` line 4329 (cfd's board): *"**F4 conversion** —
  pre-registration **not yet written**; it does not fire without one."* The same
  board lists "F4 conversion pre-registration" as a next action at lines 4331,
  4474 and 4604.

**So the premise of this lane's brief is CORRECT for F4, unlike for F3 and F11.**
F3's conversion is frozen and (per `1251a015`) fired and closed; F11's likewise.
**F4's is neither written nor fired.**

### 2.3 The attribution that must NOT be cited, recorded here so it cannot be
     re-introduced

The text *"CFD team — Re-run under frozen pre-registrations, <40 core-min each:
F3 (supersonic exact suite), F11 (per capability map), F4 (hypersonic) — the
early PASSes that lack prereqs convert to HOLDS"* is **NOT sourceable to Sanaa.**
Its attribution was withdrawn on `docs/LAB_STATE.md` line 4385 and again, on the
artifact that bore it, in `F3_CONVERSION_PREREGISTRATION.md` **AMENDMENT 1**
(§A1.1). That amendment's own re-run of the source search found the text
reproduced in **exactly one commit message in the entire history — `2bf4915a`,
the F3 pre-registration's own freeze commit** — and in four tracked files, all
four of which are cfd's own documents quoting the paraphrase. **None is a
source.** The cfd supervisor did not hear it said and will not vouch for it.

**Consequences this lane binds itself to:**

1. **The paraphrase is not cited as Sanaa's words anywhere in the F4 work.**
2. **It is not cited as a compute authorisation.** In particular the figure
   "<40 core-min" is a paraphrase's number, not an owner's cap, and no F4 cap
   may be set by reference to it. Any F4 cap must be derived from F4's own
   measured cost basis. (L-309: an attribution authorising spend must carry its
   source when recorded.)
3. **"Convert to HOLDS" does not describe what will be done, and `HOLD` is not
   in the rule-1 vocabulary.** What is owed is narrower and is stated in lab
   terms: **re-run the two gates under a frozen pre-registration so that whatever
   verdict issues is defensible.** The conversion may land `PASS`, `GATE FAIL` or
   `NOT A RESULT`; nothing about it is pre-decided, and this lane records now,
   before writing any band, that **a `NOT A RESULT` on Gate 1 is a live and
   arguably likely outcome** given §4's recorded non-monotonicity.

---

## 3. The step-0/1 headline, and the ruling it is contingent on

**These are a DIFFERENT case, a DIFFERENT solver binary and a DIFFERENT
pre-registration from Gates 1 and 2. Recorded here because the brief requires the
contingency to be located exactly, not because it touches the cylinder gates.**

**The headline** (`verification/campaign/F4_SIGFPE_STEP01_RESULTS.md` §3.1, and
`docs/LAB_STATE.md` line 4500): both steps **COMPLETE** and **SIGFPE-ABSENT**;
Step 0 on event 1 gives S0a = **8.9832 %** (2668 / 29700) at
`t* = 1.8993308e-05`, inside the frozen band **[6 %, 24 %]**, and S0b =
**23.0842 %** (6856 / 29700) at `6.5e-05` → **BASELINE-RECOVERED**; §8.2
**THRESHOLD-ARTIFACT** (99.1103 % of clamped cells in (19.5, 20) K, **0.0000 %**
at T ≤ 10 K); §8.3 **INDETERMINATE**; §8.4 **DEFICIT-NOT-IMPLICATED** (S1a ratio
**1.0000** against a 0.60 threshold). Under prereg §9.1 row 2 this **eliminates
the inlet-face dissipation-deficit variant as mechanism #7**. The §8 labels are
that pre-registration's own vocabulary and are deliberately outside rule 1.

**The contingency.** Verification's audit pass 11 (`25f16019` §83–89; the
verification supervisor's own read at `4267cd94` §90) recommends **`NOT A
RESULT`** for §8.1 and §8.3. The cfd supervisor contests it on mechanism grounds
while conceding the frozen text does not name the event ordinal. **The ruling is
Sanaa's, is cross-family, and is `PENDING`** — recorded as such at
`F4_SIGFPE_STEP01_RESULTS.md` §C1.4 (heading line 489) and on `docs/LAB_STATE.md`
lines 4333, 4476, 4540, 4609. Under verification's reading §9.1 **row 4** applies
and the mechanism-#7 elimination becomes **`NOT A RESULT`**. Both readings are
printed side by side at §3.2; the one-paragraph presentation Sanaa asked for
landed at `2db96bd4`.

**Materiality is confined.** §3.2's own table shows only **§8.1** and **§8.3**
turn on the event choice; **S0b**, **§8.2** and **§8.4** do not. The event-2
column reads: `t*` = 749 = **2.5219 %** (outside the [6, 24] band), window end
2019 = **6.7980 %**, §8.1 → **BASELINE-NOT-RECOVERED**, §8.3 → **E-FIRST**.

### 3.1 Which limbs of an F4 conversion this blocks — and which it does not

| limb | case tree | solver | blocked by the event ruling? |
|---|---|---|---|
| **A — Gates 1 & 2**: standoff vs Billig, windward Cp vs modified Newtonian, M = 6/7/8, 2-D cylinder | `verification/runs/F4_runs/cyl/` | vanilla `rhoCentralFoam`, inviscid | **NO.** Different geometry, different binary, different quantity, different pre-registration. No clause of Gate 1 or Gate 2 reads any BOUND-family diagnostic, and the SIGFPE prereg issues no verdict that either gate consumes. |
| **B — Gate 3**: SWBLI θ = 32.5° / 35° | `verification/runs/F4_runs/swbli_cylflare/` | `rhoCentralFoamBounded*` | **YES — `BLOCKED`.** Recorded as held at `F4_SIGFPE_STEP01_RESULTS.md` §6 row **F4-W1**: the θ=20° warm-up remains not gated and θ=32.5°/35° remain held until the remaining mechanism (§8.6(3) momentum/energy split, or the wedge-face identity) is resolved — and the mechanism headline that would inform it is itself contingent on the unmade ruling. |

**This lane registers limb B as `BLOCKED` and does not make the ruling. Neither
does the cfd supervisor; it is Sanaa's alone.** One honest caveat, stated rather
than glossed: if a limb-A cylinder run were itself to SIGFPE, the mechanism
question would bear on its *triage* — but that is a contingency of a crash that
has never occurred on this case tree (all nine 2026-07-28 runs completed), not a
dependency of either gate.

---

## 4. Rule-2 condition check — the registrable run roots DO NOT EXIST

**Checked by `test -e` in the same shell invocation as this assertion, at
2026-08-25T21:10:19Z, and not recalled:**

| path | result |
|---|---|
| `verification/runs/F4_runs/conversion_2026-08-25` | **ABSENT** |
| `verification/runs/F4_runs/conversion_2026-08-25/runs` | **ABSENT** |
| `verification/runs/F4_runs/conversion` | **ABSENT** |

**No case directory, no `0/`, no time directory and no `log.rhoCentralFoam`
exists beneath any of them. A conversion is UNFIRED.**

### 4.1 One finding the check turned up — an EMPTY, UNTRACKED `conversion_2026-08-24/`

**`verification/runs/F4_runs/conversion_2026-08-24/` EXISTS on disk.** It is
**empty** (`find` returns the directory and nothing else), **untracked at the
read commit** (`git ls-tree -r HEAD` over that path returns 0 entries), and its
mtime is **2026-08-24 19:14**. It holds no case, no script, no `0/`, no time
directory and no log.

**What it is:** a run root a prior lane created on the F3 conversion's date and
never populated — F3's own root is `verification/runs/F3_runs/conversion_2026-08-24/`
and this is the same name under the F4 tree. **It is not a fired conversion and
carries no result.** Nothing is deleted or reverted (rule 10: an unexpected
change is inspected, never reverted); it is reported to the supervisor.

**Operational consequence for any F4 pre-registration:** a launcher that refuses
a run root which already exists would trip on this path. **A conversion must
therefore register `conversion_2026-08-25/` (or later) as its run root**, so the
rule-2 "does not exist" condition is true of the path actually registered, and
must say in the document that `conversion_2026-08-24/` exists and is empty rather
than letting a future reader discover it.

---

## 5. Is there a grader for F4? — **NO. There is a measurement script and a table
   printer, and neither grades.**

All six instruments are tracked and **byte-identical to HEAD** (`cmp` against the
blob, not a hash comparison of a hash):

| file (under `verification/runs/F4_runs/`) | HEAD blob | sha256 (disk == HEAD blob) | `--selftest` | role |
|---|---|---|---|---|
| `run_cylinder_case.py` | `97910088c380422ccadc90f596d1958a5c57399f` | `b8e641ae0f43f3fdcf91918f292d97f09e58fe776ca785d9c31636f6e920cfc3` | **NO** | **the measurement script.** 213 lines. Locates the shock by peak density gradient (`find_shock_r`, line 89), averages standoff over 3 late-time snapshots (lines 137–157), computes Cp RMS against modified Newtonian, and **writes `result.json`** (line 204). |
| `build_report.py` | `2fe9df0df01cb03c924a574c3e60a53715c6b0d1` | `33d1b52ba2b10c949634cd123aba91a13fda9f0267d975d27615fe97cc4350a6` | **NO** | **a 34-line table printer.** It reads `result.json` and formats columns. It applies no band, computes no deviation of its own and issues no verdict. |
| `billig_theory.py` | `8ae1847e8534e32d952b82353c2341e01c3a15e4` | `7078bd4ca1fe08b649bebb69603a964d6c66b27c14c78fd2ea6c2bdb42169ff9` | **NO** | closed-form reference: Billig δ/R and `cp_max_rayleigh_pitot`. |
| `make_cylinder_case.py` | `466a4f55800ce6f039d276e6c170c4e7d6b49276` | `4252c42a6614e7fb2eb61491fcb01f1cb6cae55a4466a92f92953ea807651c39` | **NO** | mesh + case generator. `RES` at line 50, `RADIAL_GRADING = 8.0` at line 56, the `hex` line written at line 131. |
| `make_swbli_case.py` | `62f7a7ef88823860092cc22027cf12d52eac1197` | `67e40fd9458c5136e4a6a5e94ee9f496c87318ba541c3fcaf25e03ad1ea26bca` | **NO** | limb-B only. |
| `build_inlet_profile.py` | `c555430ed04c7d0a80b0e8ebc4c2a04bfaa2c182` | `24d2c9a6c520c2d233eda78e70058115517cdf3f17e30664b139c5705042c147` | **NO** | limb-B only. |

**Stated plainly: F4 has NO instrument that turns fields into a gate verdict.**
No F4 script contains the string `--selftest`; none contains a planted-zero
control; none applies a pre-registered band; none emits a rule-1 token. **A
conversion must therefore write a grader from scratch** — it cannot pin an
existing one — and that grader is a new measurement instrument the supervisor
must read **as a diff** before any core-minute is spent (supervision check 1).

### 5.1 The Roache instrument, and the ladder it would be pointed at

`scripts/roache_triple.py` is present, **byte-identical to HEAD**, HEAD blob
**`8dee0d31e94d3f59d28658f88a4cd6df80ae8e39`**, sha256
**`452f475181c9897000ea530b39a84bd3e7e9927e0a3fd39fe8b1105f538ac051`**. It
**does** carry `--selftest` (documented from line 18: it imports both parents and
cross-checks against them, and §(iii-b) is a value-checking control). Its `form`
parameter is documented at lines 319–341: `"equal"` **REFUSES** when
`|r21 − r32| > equal_tol`, `"auto"` silently falls back to the unequal/Celik
path. **`form="equal"` is the setting that refuses; `"auto"` is the silent
fallback that gives a mis-built ladder a plausible order.**

**The ladder, measured from the WRITTEN blockMeshDicts, not from requested
values** (`MESH_STANDARD.md` §9.2 — *"the requested value is the thing that
lied"*). Read from HEAD, `verification/runs/F4_runs/cyl/M6.0/{coarse,medium,fine}/system/blockMeshDict`,
**line 27** in each:

| level | written `hex` line | cells |
|---|---|---:|
| coarse | `hex (0 1 2 3 4 5 6 7) (50 20 1) simpleGrading (1 8.0 1)` | 1 000 |
| medium | `hex (0 1 2 3 4 5 6 7) (100 40 1) simpleGrading (1 8.0 1)` | 4 000 |
| fine | `hex (0 1 2 3 4 5 6 7) (200 80 1) simpleGrading (1 8.0 1)` | 16 000 |

At `dim = 2`, h ∝ N^(−1/2), so coarse→medium `r = (4000/1000)^(1/2) = 2.000000`
and medium→fine `r = (16000/4000)^(1/2) = 2.000000`; the gap is **0**. **This is
a genuinely equal-ratio ladder and `form="equal"` is admissible on it** — worth
saying, because it is uncommon in this lab and because it is what makes rule 5
gradable here at all.

**Two cautions recorded now, before any band exists, so neither can be presented
as a later discovery:**

1. **`RADIAL_GRADING = 8.0` is held constant while `nr` doubles.** That fixes the
   *total* wall-to-farfield expansion, not the first-cell height. Whether the
   near-wall spacing actually halves per level is a property of the written
   `simpleGrading` and **must be measured from the written dicts**, not assumed
   from the cell counts. If it does not, the triple is not geometrically similar
   and rule 5 refuses it whatever the cell counts say.
2. **Gate 1 is the limb most likely to come back `NOT A RESULT`.** §4's recorded
   values are non-monotone at M=6 and M=8. A non-monotone triple carries no GCI
   (rule 5), and the record's own diagnosis — *"a genuine, resolution-dependent
   systematic bias in the peak-density-gradient detector itself"* — says the
   detector, not the solver, is what moves. Gate 2's values (4.48 → 4.21 →
   3.91 %; 4.08 → 3.89 → 3.87 %) are monotone and are the better-behaved limb.

### 5.2 The instrument this lane is FORBIDDEN to use

**`sdk/workflows/tmr_verification.py` supplies no GCI, observed order or
Richardson value to any F4 document.** Three implementations quote a **negative
GCI (−10.714 %) on a divergent triple** and that file is one of them. Its
geometry helpers may be used; its GCI may not. Grading goes through
`scripts/roache_triple.py` only, pinned by blob **and** sha256, with `dim`,
`fs = 1.25` and `form="equal"` all named in the document.

---

## 6. Determination

| item | finding |
|---|---|
| Is an F4 conversion **already fired**? | **No.** All three registrable run roots are ABSENT (§4). `conversion_2026-08-24/` exists but is empty and untracked (§4.1). |
| Is an F4 conversion **owed**? | **Yes, on limb A.** Two `PASS` verdicts (§1) with no pre-registration for either (§2.1), corroborated as an open blocker by two independent lab records (§2.2). The ground is artifact-based and does **not** rest on the withdrawn paraphrase (§2.3). |
| Is any limb **blocked**? | **Yes — limb B (Gate 3, SWBLI θ=32.5°/35°) is `BLOCKED`**, on F4-W1 and on the event-1/event-2 ruling `PENDING` on Sanaa's desk (§3.1). This lane does not make that ruling. |
| Does a **grader** exist to pin? | **No** (§5). One must be written and read as a diff before compute. |
| Verdict issued by this report | **None.** This is a state establishment, not a grading. No rule-1 token is assigned to Gate 1 or Gate 2 here, and the 2026-07-28 `PASS` verdicts stand undisturbed on the record until a conversion grades them. |

**Cost of this report: 0 core-minutes. Zero compute. No solver launched, no mesh
built, no case directory created, no file under `cyl/` or `swbli_cylflare/`
touched.**

**Assertions.**
- Nothing was sent, filed, uploaded, registered, posted or commented (rule 7).
- No frozen file was edited; this is a new file (rule 6).
- No band, threshold, cap or label is written here (rule 2 is not engaged by this
  document, and it must not be cited as a freeze).
- The shared git index was not touched and nothing was reverted (rule 10).
