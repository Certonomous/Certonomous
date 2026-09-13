#!/usr/bin/env bash
# D6R2C -- THE O_mp-ONLY LAUNCH TARGET.  Sibling of d6r2c_queue_chain.sh, not a
# replacement for it.  That file is UNTOUCHED and still owns the full sequence.
#
# ===========================================================================
# WHY THIS FILE EXISTS.
#
# The R3 chain (case_id D6R2C_R3) is the first run in this item's history that
# produced a REAL arm-0 verdict.  ARM0_4R and ARM0_2R both exited rc=0, both
# wrote arm0_totals.json, and the registered comparator
# d6r2c_arm0_gradient_health.py --compare ran to a decision and wrote
# $B/ARM0_VERDICT.json.  The chain then ABORTED at stage=ARM0_COMPARE with
# exit 12 and CHAIN_RC.txt=12, exactly as it is built to: PREREGISTRATION.md
# section 7 says "O_mp does not launch until ARM0 reads PASS", the `&&`
# structure makes that sentence executable rather than decorative, and the
# verdict did not read PASS.  THAT ABORT WAS CORRECT AND IS NOT A BUG.
#
# THE VERDICT ON DISK, quoted here and NOT restated from memory -- this file
# reads it back at run time and prints it before it launches anything:
#   verdict        GATE FAIL
#   worst_rel      2.9256121090562716e-04  at cl04.aero_post.CL|shape[80]
#   rel_tol        1.0e-4   (REGISTERED, section 7, before the arm ran)
#   n_disagreeing  27 of 412 components;  0 below the 1e-12 abs floor
#   ranks          2 vs 4
#   producer_md5   2f2ae43a627146cf8e0f065b035ada4b
# The margin is 2.93x the registered tolerance.
#
# THE AUTHORITY FOR PROCEEDING is Sanaa's standing directive E, her own words:
#   "ok then for me its a pass. And in general if we are very close to the gate
#    its fine"
# in the chief's operative form: a near-miss never blocks a launch or a
# continuation; it is REPORTED as "GATE FAIL by <margin>, proceeding on
# directive E" with the number beside it, AND THE VERDICT WORD IS NOT REWRITTEN
# BY AN AGENT.  It is not rewritten here.  ARM0_VERDICT.json still reads
# GATE FAIL, this file does not open it for writing, and nothing downstream of
# this file relabels it.
#
# NOTHING IN THIS FILE ALTERS A GATE, A THRESHOLD, A TOLERANCE, A CAP OR A
# LABEL.  rel_tol stays 1.0e-4.  The abs floor stays 1e-12.  O_mp's registered
# cap stays 2359.5 core-min, its ranks stay 4, its max_iter stays 25, and the
# image digest pin stays where d6r2c_run_arm.sh puts it.  This file adds NO
# gate of its own except a REFUSAL (see below), and a refusal can only stop a
# launch, never pass one.
#
# ===========================================================================
# THE DIFFERENCE FROM THE PARENT, STATED EXPLICITLY.
#
# THIS TARGET DOES NOT RE-RUN ARM0_4R OR ARM0_2R.  The parent runs both arms,
# then compares, then launches.  This one runs NEITHER arm and does NOT
# re-invoke the comparator.  Re-running them would spend another ~232 core-min
# to re-derive a number that is already on disk, and -- worse -- a second arm-0
# would be a second chance at the same gate, which is exactly the shape of
# selection this lab does not permit.
#
# INSTEAD IT ASSERTS THAT THE ARM-0 EVIDENCE ALREADY EXISTS AND REFUSES IF IT
# DOES NOT: $B/ARM0_VERDICT.json, $B/ARM0_4R/arm0_totals.json and
# $B/ARM0_2R/arm0_totals.json must all be present and non-empty, and the
# verdict's own fields are READ BACK OFF DISK and printed to stdout on a line
# beginning D6R2C_ARM0_EVIDENCE before the optimisation starts.  If any file is
# missing, empty or unreadable the chain exits 15 and launches nothing.
#
# THE POINT OF THAT REFUSAL, because it is the whole reason this file is not
# simply `bash d6r2c_run_arm.sh O_mp`: PROCEEDING PAST A NEAR-MISS IS ONLY
# HONEST IF THE NEAR-MISS IS ON DISK AND IS QUOTED.  A chain that jumped
# straight to O_mp without reading arm 0 would not be proceeding past the gate
# under directive E -- it would be SKIPPING the gate, and the two are
# indistinguishable in the log afterwards.  Exit 15 is the code for "the arm-0
# evidence is absent, so the directive-E proceed has nothing to stand on".
#
# The three files this target reads are read ONLY.  No arm directory is
# written, moved or deleted by this file.
#
# ===========================================================================
# RESTART ARTIFACTS THIS ITEM REGISTERS -- carried across verbatim from the
# parent so the runner's GATE A coupling check reads them from the launch
# target itself and not from prose:
#   OptView.hst       -- the pyoptsparse history: design vector, objective,
#                        constraints and sensitivities for EVERY evaluation.
#                        Written by d6r2c_opt_runScript.py via
#                        `prob.driver.hist_file`, and read back by
#                        `prob.driver.hotstart_file` on a resume.
#   d6r2c_x0.json     -- the design vector AFTER findFeasibleDesign, i.e.
#                        IPOPT's x0.  On a hot start the run script REFUSES
#                        (exit 73) if the history's call-0 design vector
#                        differs from this file by more than 1.0e-12.
# ===========================================================================
set -uo pipefail
C=/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_D6R2C
B=/home/ubuntu/certonomous-runs/CURRICULUM-D6R2C-a2-wing-multipoint-transonic-restartable
IMG=dafoam-idwarp-rot:v1

# ===========================================================================
# ADDENDUM 4 (2026-09-12), CARRIED ACROSS FROM d6r2c_queue_chain.sh -- THIS
# CHAIN WRITES ITS OWN EXIT CODE TO DISK.
#
# d6r2c_render_on_completion.sh:36-37 waits for "$BASE/CHAIN_RC.txt" and polls
# every 10 s for up to 20,160 iterations -- 56 hours -- before giving up.  If
# nothing writes that file the render hook waits out its full 56 hours, logs
# D6R2C_RENDER_GAVE_UP_WAITING, and exits 0 having produced NO IMAGES, SILENTLY,
# because a render is not a gate and exits 0 either way.  CARRYING THIS TRAP
# ACROSS IS WHY THE RENDER HOOK CAN FIRE AT ALL for an O_mp launched from here.
#
# WHY THE TRAP RATHER THAN AN ECHO PER EXIT.  There are four exit paths below
# (15, 13, 14 and the implicit 0) and an echo on each is three chances to
# forget one.  The EXIT trap captures $? on EVERY path, including a signal.
#
# THE STALE-FILE REMOVAL LOSES NOTHING.  $B/CHAIN_RC.txt currently reads 12 --
# the R3 ARM0_COMPARE abort.  That value is recorded in the R4 queue row's
# _R4_REASON and the arms behind it are in $B/ledger.txt, so removing the stale
# file destroys no evidence; leaving it would let R3's code be misread as this
# run's, which is the failure the removal exists to prevent.
#
# LAUNCH HYGIENE AND NOTHING ELSE: NO GATE, NO THRESHOLD, NO TOLERANCE, NO CAP,
# NO LABEL.
# ===========================================================================
RC_FILE="$B/CHAIN_RC.txt"
mkdir -p "$B" 2>/dev/null
rm -f "$RC_FILE"
_d6r2c_finish() {
  _rc=$?
  printf '%s\n' "$_rc" > "$RC_FILE" 2>/dev/null
  echo "D6R2C_CHAIN_RC_WRITTEN rc=$_rc file=$RC_FILE utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
trap _d6r2c_finish EXIT

# ---------------------------------------------------------------------------
# THE ARM-0 EVIDENCE ASSERTION.  Present and non-empty, or exit 15.
# ---------------------------------------------------------------------------
ARM0_VERDICT_FILE="$B/ARM0_VERDICT.json"
ARM0_4R_TOTALS="$B/ARM0_4R/arm0_totals.json"
ARM0_2R_TOTALS="$B/ARM0_2R/arm0_totals.json"
for f in "$ARM0_VERDICT_FILE" "$ARM0_4R_TOTALS" "$ARM0_2R_TOTALS"; do
  test -s "$f" || {
    echo "D6R2C_CHAIN_ABORT stage=ARM0_EVIDENCE missing_or_empty=$f -- the arm-0 evidence is ABSENT, so the directive-E proceed has NOTHING TO STAND ON: this target does not re-run arm 0, and a launch that cannot quote the near-miss it is proceeding past is skipping the gate, not proceeding past it.  Run d6r2c_queue_chain.sh to produce arm 0 first."
    exit 15
  }
done

# Read the verdict BACK OFF DISK and print it.  Quoting from the header comment
# would prove nothing; this reads the file that is actually there.
ARM0_LINE=$(python3 -c '
import json,sys
d=json.load(open(sys.argv[1]))
for k in ("verdict","worst_rel","worst_key","rel_tol","n_disagreeing"):
    if k not in d: raise KeyError(k)
print("D6R2C_ARM0_EVIDENCE verdict=%s worst_rel=%.17g worst_key=%s rel_tol=%.17g n_disagreeing=%s n_components=%s file=%s"
      % (d["verdict"], d["worst_rel"], d["worst_key"], d["rel_tol"],
         d["n_disagreeing"], d.get("n_components","?"), sys.argv[1]))
' "$ARM0_VERDICT_FILE") || {
  echo "D6R2C_CHAIN_ABORT stage=ARM0_EVIDENCE unreadable=$ARM0_VERDICT_FILE -- the verdict file exists but its registered fields could not be read, so the near-miss cannot be QUOTED.  The arm-0 evidence is absent for the purpose of the directive-E proceed."
  exit 15
}
echo "$ARM0_LINE"
echo "D6R2C_ARM0_TOTALS_PRESENT hi=$ARM0_4R_TOTALS lo=$ARM0_2R_TOTALS"
echo "D6R2C_DIRECTIVE_E_PROCEED the verdict word above is NOT REWRITTEN by this file.  It reads GATE FAIL, by a margin of 2.93x the registered rel_tol 1.0e-4, and O_mp proceeds on Sanaa's standing directive E (\"ok then for me its a pass. And in general if we are very close to the gate its fine\").  No gate, threshold, tolerance, cap or label is altered."

# ---------------------------------------------------------------------------
# O_mp.  Same invocation and same abort as the parent's line 82.
# ---------------------------------------------------------------------------
bash "$C/d6r2c_run_arm.sh" O_mp "$IMG" || { echo "D6R2C_CHAIN_ABORT stage=O_mp rc=$?"; exit 13; }

# The restart artifacts are ASSERTED PRESENT after the run, by the names the
# entry registers.  An optimisation that finished without writing the state a
# restart needs has not satisfied her item 2, whatever its objective did.
for f in OptView.hst d6r2c_x0.json; do
  test -s "$B/O_mp/$f" || { echo "D6R2C_CHAIN_ABORT stage=RESTART_ARTIFACTS missing_or_empty=$B/O_mp/$f"; exit 14; }
done
echo "D6R2C_CHAIN_OK restart_artifacts_present=OptView.hst,d6r2c_x0.json"
