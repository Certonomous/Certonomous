# MP-A1 INSTRUMENT MD5 TABLE (DRAFT -- NOT FROZEN)

Existence is asserted BEFORE any md5 (DAFOAM_CHARTER section 18.3): existence and
md5-agreement are different questions and the second cannot be inferred from the
first.  Each row: the MP-A1 instrument, its md5, and its SO-3 parent's md5 (the
file it was derived from).  Where the two md5s AGREE the file is a pure identity-
preserving carry (no SO3/so3 token and no content change); where they differ the
*_DELTAS_from_so3.diff beside it is the exact change.  SUBMISSIONS PARKED.

| instrument | EXISTS | md5 (MP-A1) | md5 (SO-3 parent) | carry/changed |
|---|---|---|---|---|
| `mpa1_runScript.py` | yes | `6cef4ad56b3b9d053d464c9dbeb7123f` | `0c026d72047b605099125258e3152f93` | changed (see diff) |
| `mpa1_grade.py` | yes | `7050d38e8fe4165677c0842c5dd4b5b9` | `0ac111ef144a62111e36f676e8114af1` | changed (see diff) |
| `mpa1_xf.py` | yes | `8036ca85d502276dc172c626becd11d5` | `58fd0e2600ce6836ddd039beb8677477` | changed (see diff) |
| `mpa1_stall.py` | yes | `5d112800fc34dc729c80c584d873eec7` | `c0719b7fad530a34391280139fe7aa6c` | changed (see diff) |
| `mpa1_age_guard.py` | yes | `7fe4352d36b7b48a5bb2885e225e455a` | `1bcbe57cb708d8e6a7a89ceb2235a35c` | changed (see diff) |
| `mpa1_aggregate_memory.py` | yes | `709ab0b98ef0302a3a3a318588f9493f` | `709ab0b98ef0302a3a3a318588f9493f` | pure carry |
| `mpa1_stop_marker.sh` | yes | `5063f90b227eb3a7341d18c6ca7b7824` | `4809ff569def1927e516685bb218e7bc` | changed (see diff) |
| `mpa1_run_arm.sh` | yes | `f884672c32738b549ee79f4f400660ff` | `e8839a2fb445239609718feed9b0aeed` | changed (see diff) |
| `mpa1_chain_driver.sh` | yes | `1e7ac6b752b4e3385df1fb9191588452` | `22850e62a28aacef5187620c92feeed7` | changed (see diff) |
| `mpa1_decomposeParDict` | yes | `e6f1b0060944bc86d6dff56480ad2bd4` | `e6f1b0060944bc86d6dff56480ad2bd4` | pure carry |

Toolchain identity (by digest, carried from SO-3 section 7, unchanged):
- PATCHED `dafoam-idwarp-rot:v1` sha256:2927768a...f6d35, libidwarp.so md5 85f59e87253e0a71a813f64ca6e4c425
- SHIPPED `dafoam/opt-packages:latest` sha256:9d45679d...f07fc, libidwarp.so md5 f0fcb488e0e98156575cd19548e91663

The grading path is `mpa1_grade.py`; `mpa1_chain_driver.sh` asserts its md5 with
`md5sum -c` before staging any arm (carried from SO-3).
