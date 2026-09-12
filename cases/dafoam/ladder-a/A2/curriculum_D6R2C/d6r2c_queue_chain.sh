#!/usr/bin/env bash
# D6R2C -- the single launch target the runner invokes for the O_mp item.
#
# WHY THIS FILE EXISTS AT ALL, stated plainly so no successor deletes it as a
# wrapper-around-a-wrapper.  The entry originally carried
# `["bash","-lc","<chain>"]`.  Run against the runner's OWN gate code, that
# argv makes `qec.launch_target` return kind='shell-code' -- "'bash' runs
# INLINE CODE via '-lc'; the following element is program text, not a path" --
# and GATE A limb (iii) then REFUSES, because it cannot resolve the entry's
# restart claim to any artifact that would have to honour it.  That refusal is
# CORRECT: a restart claim nothing on disk carries is not a declaration.  The
# fix is to give the gate a real file to read, which is this one.
#
# The sequence and its separators are REGISTERED (PREREGISTRATION.md section 7,
# and PARKED_QUEUE_ROW.D6R2C_Omp.json launch_cmd_note): `&&`, because
# "O_mp does not launch until ARM0 reads PASS" and the arm-0 comparator exits
# non-zero on anything but PASS.  That is what makes the sentence executable
# instead of decorative.
#
# RESTART ARTIFACTS THIS ITEM REGISTERS, named here so the gate's coupling
# check reads them from the launch target itself and not from prose:
#   OptView.hst       -- the pyoptsparse history: design vector, objective,
#                        constraints and sensitivities for EVERY evaluation.
#                        Written by d6r2c_opt_runScript.py via
#                        `prob.driver.hist_file`, and read back by
#                        `prob.driver.hotstart_file` on a resume.
#   d6r2c_x0.json     -- the design vector AFTER findFeasibleDesign, i.e.
#                        IPOPT's x0.  On a hot start the run script REFUSES
#                        (exit 73) if the history's call-0 design vector
#                        differs from this file by more than 1.0e-12.
set -uo pipefail
C=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
B=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable
IMG=dafoam-idwarp-rot:v1

bash "$C/d6r2c_run_arm.sh" ARM0_4R "$IMG" || { echo "D6R2C_CHAIN_ABORT stage=ARM0_4R rc=$?"; exit 10; }
bash "$C/d6r2c_run_arm.sh" ARM0_2R "$IMG" || { echo "D6R2C_CHAIN_ABORT stage=ARM0_2R rc=$?"; exit 11; }

# ARM 0 IS A PRECONDITION, NOT A DIAGNOSTIC.  O_mp does not launch unless the
# multipoint gradient agrees between 2 and 4 ranks to the tolerance registered
# BEFORE the arm ran (1.0e-4 relative, PREREGISTRATION.md section 7).
python3 "$C/d6r2c_arm0_gradient_health.py" \
    --compare "$B/ARM0_4R/arm0_totals.json" "$B/ARM0_2R/arm0_totals.json" \
    --json-out "$B/ARM0_VERDICT.json" \
  || { echo "D6R2C_CHAIN_ABORT stage=ARM0_COMPARE rc=$? -- the gradient did not agree between 2 and 4 ranks to the registered tolerance, so the optimisation does not start"; exit 12; }

bash "$C/d6r2c_run_arm.sh" O_mp "$IMG" || { echo "D6R2C_CHAIN_ABORT stage=O_mp rc=$?"; exit 13; }

# The restart artifacts are ASSERTED PRESENT after the run, by the names the
# entry registers.  An optimisation that finished without writing the state a
# restart needs has not satisfied her item 2, whatever its objective did.
for f in OptView.hst d6r2c_x0.json; do
  test -s "$B/O_mp/$f" || { echo "D6R2C_CHAIN_ABORT stage=RESTART_ARTIFACTS missing_or_empty=$B/O_mp/$f"; exit 14; }
done
echo "D6R2C_CHAIN_OK restart_artifacts_present=OptView.hst,d6r2c_x0.json"
