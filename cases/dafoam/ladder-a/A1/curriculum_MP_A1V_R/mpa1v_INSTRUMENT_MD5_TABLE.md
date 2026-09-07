# MP-A1V-R INSTRUMENT MD5 TABLE — FROZEN 2026-09-07

MP-A1V launcher-repair successor. Instruments CARRIED BYTE-IDENTICAL from frozen MP-A1V
(a5d7691d) — NO prefix rename. Only the launcher (runtime path refs) and driver (new run
root + path-existence fixpoint + MD5_LAUNCHER re-pin) differ. ALL_PINS_MATCH = 1.

| file | md5 | vs MP-A1V |
|---|---|---|
| mpa1v_grade.py | 0a41208ee834df2b413b944938587a67 | byte-identical carry |
| mpa1v_xf.py | ea53c04314f20c438de233101d5ce84d | byte-identical carry |
| mpa1v_runScript.py | bb3ba3a61b19dc8564e247cdb11e9147 | byte-identical carry (staged as mpa1_runScript.py) |
| mpa1v_stall.py | 5d112800fc34dc729c80c584d873eec7 | byte-identical carry |
| mpa1v_age_guard.py | 7fe4352d36b7b48a5bb2885e225e455a | byte-identical carry |
| mpa1v_stop_marker.sh | 5063f90b227eb3a7341d18c6ca7b7824 | byte-identical carry |
| mpa1v_aggregate_memory.py | 709ab0b98ef0302a3a3a318588f9493f | byte-identical carry |
| mpa1v_decomposeParDict | e6f1b0060944bc86d6dff56480ad2bd4 | byte-identical carry |
| mpa1v_run_arm.sh | 342d55c99b184cccf2c82fc9768fb4a6 | CHANGED: runtime path refs age_guard/stall/output/pidfile reconciled mpa1_->mpa1v_; run root |
| mpa1v_chain_driver.sh | d5ec9b970625b0222750ee2ce70eabee | CHANGED: new run root, path-existence fixpoint added, MD5_LAUNCHER re-pinned (UNGUARDED top of chain) |

Driver pins: MD5_LAUNCHER 342d55c9 (mpa1v_run_arm.sh), MD5_GRADER 0a41208e (byte-identical carry),
MD5_RUNSCRIPT bb3ba3a6, MD5_XF ea53c043, + the byte-identical-carry values. ALL_PINS_MATCH=1.
Path-existence fixpoint validated (extracts {mpa1_runScript.py, mpa1v_age_guard.py, mpa1v_stall.py,
mpa1v_xf.py}; catches a missing ref; passes complete). Freeze + launch are the supervisor's acts.
