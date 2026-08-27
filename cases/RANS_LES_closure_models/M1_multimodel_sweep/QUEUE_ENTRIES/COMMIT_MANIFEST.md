# M1_multimodel_sweep / QUEUE_ENTRIES -- COMMIT MANIFEST

Written by the closure verification lane, 2026-08-27, as the >50-file commit manifest
Sanaa's section 1 rule requires. **UNTRACKED when written; the closure-supervisor
commits it.** This lane committed nothing and copied nothing into
`verification/queue/closure/` -- a copy there LAUNCHES (D535 / L-348).

## Freeze

Every entry carries `prereg_commit = 73cd5ac578c4916a07ae05a9618e166832fdef75` (**M1 AMENDMENT 1**, pre-compute) and
`prereg_path = cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md`.
`PREREGISTRATION.md` on disk sha256 `e15d0df3ee960b907b50a978db864cd1a112cd4723274f7bd2876df643d87572`, byte-equal to
`git show 73cd5ac5:cases/RANS_LES_closure_models/M1_multimodel_sweep/PREREGISTRATION.md`.

The set was first cut against `7b00b3ec` and re-cut after the amendment: only
`prereg_commit` and `enqueued_by` moved, on all 78 and on no other key. Verified
here rather than relayed: the amendment is a **single diff hunk at line 1249**,
appended at the foot (1,253 lines -> 1,321), with **no line above it moved**. The
section 2.3 table (line 163) and the section 9.2 clauses (lines 911, 914) are
byte-unchanged, so every cost figure below still cites the clause it names.
`make_queue_entries_m1.py`, `run_m1.sh` and `grade_m1.py` are byte-identical at
`7b00b3ec` and `73cd5ac5`; only `PREREGISTRATION.md` and `stage_m1.py` changed.

## Provenance

All 78 `.json` were produced by re-running the FROZEN generator
`make_queue_entries_m1.py` (blob byte-identical on disk, at `73cd5ac5` and at HEAD)
with `--prereg-commit 73cd5ac578c4916a07ae05a9618e166832fdef75` and the `--enqueued-by`
string recording the supervisor's personal check. The generator was not edited
(standing rule 6). Cell counts are read live from each case's
`constant/polyMesh/owner` and all 39 match the frozen section 2.3 table (590,026
cells).

**Every value in `enqueued_by` is mechanically checkable.** It carries the full
40-character `prereg_commit` and the full 64-character pre-registration sha256, with
no abbreviation and no ellipsis, so an auditor hashes the document and compares in
one command rather than reconstructing what was elided and trusting the elision. An
earlier draft carried an abbreviated digest; it was corrected before filing on the
same principle VERIFICATION_CHARTER v1.12 records for freeze shas -- a provenance
field carries a verifiable value or it carries nothing. The digest it carries is the
**post-amendment** one; the pre-amendment digest is stale and appears nowhere in the
78 entries.

`README.md` is NOT the generator's output. The frozen generator emits a README that
still opens `# DRAFT -- NOT FROZEN, NOT COMMITTED, NO COMPUTE AUTHORISED` and claims
`prereg_commit` is `PENDING_SUPERVISOR_FREEZE`, whatever sha it is given -- false of
these 78 entries. The generator was not edited; its emitted copy was superseded by a
README written here, and the defect is disclosed in that file. Same class measured
independently at `G1_grid_triple/grade_g1.py:611` (prints "DRAFT, NOT FROZEN" while
frozen at `03be2015`) and a third time in the pre-registration's own closing line,
struck by AMENDMENT 1.

## Validation

`scripts/queue_entry_check.py --selftest` was run FIRST and passed (18 controls
fired, each shown able to fail), then `--dir` over this directory: **78 ACCEPTED, 0
REFUSED**, rc 0. Acceptance is a mechanical guard only; SUPERVISION_CHARTER sec.3
check 4 was performed personally by the closure-supervisor and is recorded verbatim
in every entry's `enqueued_by`.

**`host` is omitted on all 78.** `queue_entry_check.py` does not validate that field
at all, and `queue_runner.py:461` reads `entry.get("host", "local")`, so omission
means THIS BOX by default rather than by declaration.

## Totals

| quantity | measured over this set | registered in PREREGISTRATION.md |
|---|---|---|
| entries | 78 (39 cases x 2 arms) | 78 |
| sum `cost_core_min_estimate` | **1298.058 core-min** | **1,298.1** core-min (section 9.2) |
| `kOmegaSST_null` arm (planted control) | 39 entries, est 649.029 core-min | **649.029** measured vs 649.0 registered |
| `kOmega` arm | 39 entries, est 649.029 core-min | **649.029** measured vs 649.0 registered |
| sum `cap_core_min_registered` | **1892.780 core-min** | section 2.3 cap column x 2 arms |
| `ranks` | 1 on all 78 | section 9.4 |
| `memory_floor_gb` | 1.0 on all 78, ESTIMATED not measured | section 10 |

**Which cap figure the entries carry:** the entries carry the **section 2.3
per-entry cap column**, summing to **1892.780 core-min**. Section 9.2's headline
registered cap is **1,900.0 core-min** -- a **0.38 % round-UP** of the same figure.
Section 9.2 line 914 is the clause that binds `cap_core_min_registered` to the
section 2.3 column, so the entries follow the binding clause, and they sum BELOW the
headline, i.e. the discrepancy is conservative in the safe direction. The estimate
sum 1298.058 differs from the registered 1,298.1 by 0.042 core-min, from the section
2.3 table rounding `AR_5_Ret_180` to 12.150 where the generator writes 12.149.
AMENDMENT 1 touched no gate, threshold, cap or label, and none of these figures moved.

Dollar figures are DERIVED at the owner-stated $0.0513/core-h and are NOT measured:
this box cannot read its own billing (COMPUTE_BUDGET_CHARTER section 5).
Estimate 21.63 core-h = $1.11 DERIVED; cap 31.55 core-h = $1.62 DERIVED.

## Age guard, re-measured after the amendment

All 78 `cwd` paths EXIST, 0 absent; **0 contain a time directory** (including `0/`),
0 contain bare field files, and all 78 carry `0.orig/`. No compute has occurred on
any of the 78 run roots. This was re-measured after AMENDMENT 1 landed, not carried
forward from the earlier reading.

## Files

| file | sha256 | what it is |
|---|---|---|
| `M1_kOmegaSST_null__AR_10_Ret_180.json` | `f7ecf28818acfb97446f188ef082a7fbcc826a565afe48efa54e8a4e9237cfb8` | queue entry, arm `kOmegaSST_null`, case `AR_10_Ret_180`, 22090 cells, ranks 1, est 24.299 core-min, cap 35.432 core-min |
| `M1_kOmegaSST_null__AR_14_Ret_180.json` | `bec4139dbb2c82621a6b7eecc93f4950ae512da9013106b4ab975244e330ec33` | queue entry, arm `kOmegaSST_null`, case `AR_14_Ret_180`, 31819 cells, ranks 1, est 35.001 core-min, cap 51.038 core-min |
| `M1_kOmegaSST_null__AR_1_Ret_180.json` | `591f4c5c9fac53783b8ab2e94df21ff490b2d6eb61ee235c4009910404479669` | queue entry, arm `kOmegaSST_null`, case `AR_1_Ret_180`, 2209 cells, ranks 1, est 2.430 core-min, cap 3.543 core-min |
| `M1_kOmegaSST_null__AR_1_Ret_360.json` | `f4d8eb1ad59ed55c2e235b59e9c3069425c37fe6d55f17b4af6253b4965ff624` | queue entry, arm `kOmegaSST_null`, case `AR_1_Ret_360`, 3025 cells, ranks 1, est 3.328 core-min, cap 4.852 core-min |
| `M1_kOmegaSST_null__AR_3_Ret_180.json` | `91b7e6a815df42b70d36c3efe6a0e825a051bbd3a609563372eeb106510c6ca3` | queue entry, arm `kOmegaSST_null`, case `AR_3_Ret_180`, 6627 cells, ranks 1, est 7.290 core-min, cap 10.630 core-min |
| `M1_kOmegaSST_null__AR_3_Ret_360.json` | `40c1f7a2327b9f4947b705f5db21ce4fd252640e8842004c8f3d9ae0ec461683` | queue entry, arm `kOmegaSST_null`, case `AR_3_Ret_360`, 8748 cells, ranks 1, est 9.623 core-min, cap 14.032 core-min |
| `M1_kOmegaSST_null__AR_5_Ret_180.json` | `a96ffb9e333b12971583d5c2cf25b815ccd75bf6981a93339ce8d8001212ae5c` | queue entry, arm `kOmegaSST_null`, case `AR_5_Ret_180`, 11045 cells, ranks 1, est 12.149 core-min, cap 17.716 core-min |
| `M1_kOmegaSST_null__AR_7_Ret_180.json` | `b19b4fc67b0464069493f761f557476f68dbfb9e7f991bbcb036f09992729dba` | queue entry, arm `kOmegaSST_null`, case `AR_7_Ret_180`, 15463 cells, ranks 1, est 17.009 core-min, cap 24.803 core-min |
| `M1_kOmegaSST_null__CBFS.json` | `326a39a3a3cbeb3e810174705ed9084c51f8264b08ac043603353a8aadb787b8` | queue entry, arm `kOmegaSST_null`, case `CBFS`, 21000 cells, ranks 1, est 23.100 core-min, cap 33.684 core-min |
| `M1_kOmegaSST_null__PH_Breuer.json` | `ddfc930a5d18968bc7eb6926be160c80b31e8862b1b6682306a1a043b79e9a11` | queue entry, arm `kOmegaSST_null`, case `PH_Breuer`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_10071_2024.json` | `ca0483ad44dd05f2ec8d9b25f61ba360c6ac15ef5a975403975585f4b9438ba7` | queue entry, arm `kOmegaSST_null`, case `alpha_05_10071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_10071_3036.json` | `fb24aeb660ed19be00bfa62c4004ca9c4a0aa0eb5364b2984eb6dc72c8abd706` | queue entry, arm `kOmegaSST_null`, case `alpha_05_10071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_10071_4048.json` | `3ad20e3f87a165306651070262430630706f4e0b65462981ce544e358c1e8dae` | queue entry, arm `kOmegaSST_null`, case `alpha_05_10071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_4071_2024.json` | `06d575ba09b38ee4cc5604b262fcecd59bc3b71044f7ed2a831102d0ad20e30d` | queue entry, arm `kOmegaSST_null`, case `alpha_05_4071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_4071_3036.json` | `93773db68f8f0bd3cdc48988eee5859c1f7c433a881cf86e4fed3ee5765997ad` | queue entry, arm `kOmegaSST_null`, case `alpha_05_4071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_4071_4048.json` | `57896677689d135ecc2d5546388ad37ba0315d8adf4d701704d2ead03cf6a45a` | queue entry, arm `kOmegaSST_null`, case `alpha_05_4071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_7071_2024.json` | `6f9e2aca0f20fd819da08701e86054ad292ec5f50fd97e7bd2a8a122a49a34f7` | queue entry, arm `kOmegaSST_null`, case `alpha_05_7071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_7071_3036.json` | `b578c64af4b12674fe47cb5008a032f5c1c639016e7ac32e441a3b4bf5dff05e` | queue entry, arm `kOmegaSST_null`, case `alpha_05_7071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_05_7071_4048.json` | `58a800e88c586b5ae36dc80de8dfca4f7291e42964630d111502e65cef0011ad` | queue entry, arm `kOmegaSST_null`, case `alpha_05_7071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_075.json` | `47401ae76f5bed01c479264a5847ca579d1237a708d5e41cd34082c85809ac75` | queue entry, arm `kOmegaSST_null`, case `alpha_075`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_12000_2024.json` | `1ff445a1810a0ca01bd6a7c53e2b23a4cecf7a6fbc761c4bbdf9cc1c63f3148f` | queue entry, arm `kOmegaSST_null`, case `alpha_10_12000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_12000_3036.json` | `db1d0c18a0d062e6223796ac080925961d609c9ede6b9fc1026cc2e4d38c2473` | queue entry, arm `kOmegaSST_null`, case `alpha_10_12000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_12000_4048.json` | `5343dc6ce8030d1ee05fa0bceb31999aab42ee2466f32de147a6bb72fa55435b` | queue entry, arm `kOmegaSST_null`, case `alpha_10_12000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_6000_2024.json` | `4411ddcab6d416c50b15eeac96c68d4170a0bac7f5777ace9485cc163e6dc57d` | queue entry, arm `kOmegaSST_null`, case `alpha_10_6000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_6000_3036.json` | `45807c47d6a5102b3c0f6596a5e3ec2dfe572de5ccdbf4ce4d3446d087ee1fa7` | queue entry, arm `kOmegaSST_null`, case `alpha_10_6000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_6000_4048.json` | `55f857c40cdb057ad5628ca688ec6b1d09c766e7633de7f588ae87b7d0392fc0` | queue entry, arm `kOmegaSST_null`, case `alpha_10_6000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_9000_2024.json` | `63f93a5e362602bc7eadb1d0680d3e631c4b1142f827294c583eef8f08d9c491` | queue entry, arm `kOmegaSST_null`, case `alpha_10_9000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_9000_3036.json` | `9e0c6b3316050168b515d053fc4f2224c8983c6c3a864c14d45a8aea9fa88a5e` | queue entry, arm `kOmegaSST_null`, case `alpha_10_9000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_10_9000_4048.json` | `7e07f55a8c71b085c3050c791f1db3617a5751e69be6927ca964ebcf67eb2069` | queue entry, arm `kOmegaSST_null`, case `alpha_10_9000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_125.json` | `f4b04a4021c5399af43e80e0d7e530973d500e99b0b7f3a21c50e226c3d4b9fb` | queue entry, arm `kOmegaSST_null`, case `alpha_125`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_10929_2024.json` | `b940a80bc3f7abb18a430f7f47347ff43e9b0e78c1eb786b35c4c29a791534be` | queue entry, arm `kOmegaSST_null`, case `alpha_15_10929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_10929_3036.json` | `f94a5ec9804365ed44b55c0f6d0cff8d9d513e3cdd8897d60f84bdfb22dea1c6` | queue entry, arm `kOmegaSST_null`, case `alpha_15_10929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_10929_4048.json` | `86d69e6d2d68ce93d9ba9389062f38e52f6dff8084eafa5f4a8d70c413503e08` | queue entry, arm `kOmegaSST_null`, case `alpha_15_10929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_13929_2024.json` | `5f2eae3f757baa446bcdb8c18ad802fe4e364591415940153bd09b3af444f6fa` | queue entry, arm `kOmegaSST_null`, case `alpha_15_13929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_13929_3036.json` | `cf0941d0ca85877e6416b4165a68bb28a4317e5f6e2f5c786574c81a1bb18c60` | queue entry, arm `kOmegaSST_null`, case `alpha_15_13929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_13929_4048.json` | `7c1760a220d089745ed6c7233fbea6ed3d45eb84d13edbbc16a66ee1b3f66c79` | queue entry, arm `kOmegaSST_null`, case `alpha_15_13929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_7929_2024.json` | `6b404036dda4faba8cc4db7d370cdcd0ecd0eae40da281489334f4c577b40d96` | queue entry, arm `kOmegaSST_null`, case `alpha_15_7929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_7929_3036.json` | `2ec1b0b96d70fa363f2abec2e714313f092d145fd36a3c204d6b2e08675fecbd` | queue entry, arm `kOmegaSST_null`, case `alpha_15_7929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmegaSST_null__alpha_15_7929_4048.json` | `da7f8b573aeef2f2b2c974276a68a3915bfe94ecb4f0e7843c08799bb8c41a81` | queue entry, arm `kOmegaSST_null`, case `alpha_15_7929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__AR_10_Ret_180.json` | `8567e935cb107528ac3f5052853a3ff78e5e1cec4a95c7edf0fdf2939cabf905` | queue entry, arm `kOmega`, case `AR_10_Ret_180`, 22090 cells, ranks 1, est 24.299 core-min, cap 35.432 core-min |
| `M1_kOmega__AR_14_Ret_180.json` | `414036dd06f0fbd7262f532735c08c311e7b728794b0c1e088772552c36242f9` | queue entry, arm `kOmega`, case `AR_14_Ret_180`, 31819 cells, ranks 1, est 35.001 core-min, cap 51.038 core-min |
| `M1_kOmega__AR_1_Ret_180.json` | `a763f61b96b4ecce0ef64ba72df2babd24b8c3aa7c9041b2f8f6928404d8582b` | queue entry, arm `kOmega`, case `AR_1_Ret_180`, 2209 cells, ranks 1, est 2.430 core-min, cap 3.543 core-min |
| `M1_kOmega__AR_1_Ret_360.json` | `be1131303137735a024bb84c1af7447f097dbbde2bb64c74869709865b11bfcf` | queue entry, arm `kOmega`, case `AR_1_Ret_360`, 3025 cells, ranks 1, est 3.328 core-min, cap 4.852 core-min |
| `M1_kOmega__AR_3_Ret_180.json` | `4118fdf4a7a93cf9e340be9c7f32e02fa6941b1624c83388a7c87e388f16e6c8` | queue entry, arm `kOmega`, case `AR_3_Ret_180`, 6627 cells, ranks 1, est 7.290 core-min, cap 10.630 core-min |
| `M1_kOmega__AR_3_Ret_360.json` | `e3114f9193856da0b6ae3bd20032a4f13a0ee818721d8d7395efed5282e43e6d` | queue entry, arm `kOmega`, case `AR_3_Ret_360`, 8748 cells, ranks 1, est 9.623 core-min, cap 14.032 core-min |
| `M1_kOmega__AR_5_Ret_180.json` | `6ecd9ead355eaa76280635ea187c5569fab50cd191002d7df03028ba2cd20287` | queue entry, arm `kOmega`, case `AR_5_Ret_180`, 11045 cells, ranks 1, est 12.149 core-min, cap 17.716 core-min |
| `M1_kOmega__AR_7_Ret_180.json` | `5d7232be70a59afb663de757e06fe0a7cb227f3058487415d601151da3e21016` | queue entry, arm `kOmega`, case `AR_7_Ret_180`, 15463 cells, ranks 1, est 17.009 core-min, cap 24.803 core-min |
| `M1_kOmega__CBFS.json` | `dd11f104e45d8b514c8ab1c4e1403a609f219bf8550d128f977d0058cbece593` | queue entry, arm `kOmega`, case `CBFS`, 21000 cells, ranks 1, est 23.100 core-min, cap 33.684 core-min |
| `M1_kOmega__PH_Breuer.json` | `116cc514cf2be227f22ad6065e313b8b035407f026b6bae216ceda2bc2cb7834` | queue entry, arm `kOmega`, case `PH_Breuer`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_10071_2024.json` | `0b958779a429a361f0ec8eb8c08e6db74b9411f67a57fa2cb099f335c2cd967b` | queue entry, arm `kOmega`, case `alpha_05_10071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_10071_3036.json` | `cd4ea84abaff77c3ffd3f918f9053e85ce1e7da72d64765efdaed1d0d5f377d2` | queue entry, arm `kOmega`, case `alpha_05_10071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_10071_4048.json` | `2b2c8b7de5c00bdaa8346da1ad7df7610cc5f7913c651ac40d28705d1c99b606` | queue entry, arm `kOmega`, case `alpha_05_10071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_4071_2024.json` | `a02becff05bd6bb2fb781488337a185dcf0fa80b11f81a95ed3a954d876418be` | queue entry, arm `kOmega`, case `alpha_05_4071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_4071_3036.json` | `7ef46291d0604ec3bb2a9db57a3e89b795d3bb35d51e7aebade98882d753d7e9` | queue entry, arm `kOmega`, case `alpha_05_4071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_4071_4048.json` | `74b75388dc9872a4e47641fb607745afa86483568b94a2b704caf0979f13e19e` | queue entry, arm `kOmega`, case `alpha_05_4071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_7071_2024.json` | `a1f7c74f267025daae8365b6dfe2feec81a0e555ce79d2800e77cf8dbc57bbb9` | queue entry, arm `kOmega`, case `alpha_05_7071_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_7071_3036.json` | `32806afba9fb9850d0cce73073e33563810d501f4bd5419279d43e3a2bee9e82` | queue entry, arm `kOmega`, case `alpha_05_7071_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_05_7071_4048.json` | `0c00a72db748a4eedb916614865ce08857d41188a6e55cfd1859a7b399e43d68` | queue entry, arm `kOmega`, case `alpha_05_7071_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_075.json` | `57f5c61dd80ce062052656e2da87648d97b6fcffa4bd88d459241b4dd5562955` | queue entry, arm `kOmega`, case `alpha_075`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_12000_2024.json` | `8fde8f636e861371c86a2088f884b296e60c920a24a2156c8f12f8fd4939ba3b` | queue entry, arm `kOmega`, case `alpha_10_12000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_12000_3036.json` | `2972259cf6bae4bdae77b42b164c089f4e9ce1acec5d4845e939bfe0ea52e390` | queue entry, arm `kOmega`, case `alpha_10_12000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_12000_4048.json` | `7baeb01a680953c75531325da80781a5f1b983561981296ddaf173cea7d813a1` | queue entry, arm `kOmega`, case `alpha_10_12000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_6000_2024.json` | `ac3d23a359b776b463884797266ab5ba280d06fabe541a331235c0b30a069969` | queue entry, arm `kOmega`, case `alpha_10_6000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_6000_3036.json` | `2fd6151a523e086290da7a305126767c7e7a756c1caf3f776f8065f1eafb4502` | queue entry, arm `kOmega`, case `alpha_10_6000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_6000_4048.json` | `d16765653ad3ce965703f876f3edcabe72985c87a96c891c8361ef47b283c43a` | queue entry, arm `kOmega`, case `alpha_10_6000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_9000_2024.json` | `3906a2b5ab514368d56271e14c0a0c5b1a948d237f44bf6c46d2977b65c1237a` | queue entry, arm `kOmega`, case `alpha_10_9000_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_9000_3036.json` | `8a9582b83937d86fa20a09154ce24339170ab0ef18b4832ca1df281464319631` | queue entry, arm `kOmega`, case `alpha_10_9000_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_10_9000_4048.json` | `6c4a837d63e1ea168c544d90f5ddf5495c77769fee1a68249650f5234fa64f07` | queue entry, arm `kOmega`, case `alpha_10_9000_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_125.json` | `73045a625edd2e027de9a70d99bf93cc2508f5f281b78fe5d3afdfc77eea858b` | queue entry, arm `kOmega`, case `alpha_125`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_10929_2024.json` | `09358118558c79250cc75827e56542af84ca9a227c9ff323b0123d6b016e8c53` | queue entry, arm `kOmega`, case `alpha_15_10929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_10929_3036.json` | `c3267707e6dff202e0ba06902add3e7ed3270f19acc83b39f332885b193b4f71` | queue entry, arm `kOmega`, case `alpha_15_10929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_10929_4048.json` | `f941e8273194295a293e268ab4fd33564e0566aecd31eff9ec2274b99a8c47e3` | queue entry, arm `kOmega`, case `alpha_15_10929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_13929_2024.json` | `2d16dfa6e4c658dcce913873b334bcc5876aeec253ed13138c644b9eee9a4fd2` | queue entry, arm `kOmega`, case `alpha_15_13929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_13929_3036.json` | `7582b8f85af837065f438c0ee432019f9c7abec9d430949eb6440036c585d889` | queue entry, arm `kOmega`, case `alpha_15_13929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_13929_4048.json` | `b1ebcec84a8f16410b688cf1c18f747c744fc7409c07b313ea4f0b9c689ec69c` | queue entry, arm `kOmega`, case `alpha_15_13929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_7929_2024.json` | `e96e9b0912796aec78d785ada5d8a7d9892e8288ecf4bc02849c7785a8d360e1` | queue entry, arm `kOmega`, case `alpha_15_7929_2024`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_7929_3036.json` | `101855c9588a80f30419ea1594b1455ac93bc6dabdbeacc708f675934cf4df5d` | queue entry, arm `kOmega`, case `alpha_15_7929_3036`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `M1_kOmega__alpha_15_7929_4048.json` | `9281dadb3201836a82a322c0470d4c0e6d67636f9222b591690adf35a1bcb848` | queue entry, arm `kOmega`, case `alpha_15_7929_4048`, 15600 cells, ranks 1, est 17.160 core-min, cap 25.022 core-min |
| `README.md` | `132482a7c360ef90367a99da2d4a7bd10238d13fbfdefcdf73fc4ecf17de2378` | README written by this lane, superseding the frozen generator's stale DRAFT-banner template (see Provenance) |

79 files listed (78 entries + 1 README). This manifest is the 80th file in
the directory and is not listed above.
