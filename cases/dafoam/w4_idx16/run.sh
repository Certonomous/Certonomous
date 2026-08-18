#!/usr/bin/env bash
# W4 2026-08-02, docket item `w4-idx16-is-the-whole-remaining-residual`.
#
# THE QUESTION. Under the patched IDWarp, A5's OBJ.val wrt shapexUpper is in
# band on 26 of 27 components. idx16 is the exception and it is the ONLY entry
# in either the A1 or A5 record that the patch moves the WRONG WAY:
#     stock    analytic -3.77483865   FD -4.30296296   12.2735%
#     patched  analytic -5.04787848   FD -4.30296296   17.3117%
# The FD is bit-identical between the runs -- the primal never sees the patch,
# which only supplies a warpDeriv term -- so the analytic side moved away from
# a fixed target, and it OVERSHOT it rather than drifting from it. The whole
# vector's absolute error is 7.474091e-01 and idx16's share of it is 7.449e-01:
# idx16 IS the remaining residual.
#     evidence: demo-output/website/dafoam/W5_GRADIENT_REGRADE.md sections 7.2-7.4
#               /home/ubuntu/certonomous-runs/W5-regrade/a5pl_patched_checktotals.log
#
# WHAT IS ALREADY REFUTED, WITHOUT COMPUTE.
#   * Decomposition, the lab's first discriminator. W4-a5-decomp ran A5's
#     compute_totals at fixed np=4 under scotch against simple 4x1x1 WITH THE
#     PATCH MOUNTED, and idx16 reads -5.04787848 vs -5.04971724, a relative
#     difference of 3.6e-04. idx16 is decomposition-invariant.
#   * The FD moving. It is identical to every printed digit between the stock
#     and patched runs.
#
# WHAT THIS PROBE TESTS, PRE-REGISTERED BEFORE IT RUNS.
# H1 (kink): shapexUpper[16] sits at a point where the objective is not
#     differentiable, so the CENTRAL difference at step 1e-4 averages two
#     different one-sided slopes and lands between them. Then the patched
#     analytic is one of those one-sided slopes and the FD target is an
#     artefact of the formula, not a reference.
#     PREDICTS: forward and backward slopes at idx16 differ by roughly the
#     2 x (analytic - FD) = 1.49 that would be needed to average to -4.303,
#     i.e. one side near -5.05 and the other near -3.56, and the split does
#     NOT shrink as the step shrinks.
# H2 (noise): the FD at idx16 is simply under-resolved.
#     PREDICTS: the central difference moves toward the analytic as the step
#     grows, and the forward/backward split shrinks with the step.
# H3 (neither): forward, backward and central all agree near -4.303 at every
#     step, and the patched analytic is wrong on its own.
#
# CONTROL. idx15 is the immediate neighbour and the largest component in the
# vector (analytic -24.25642805, FD -24.27272214, 0.067% apart). Whatever the
# probe reads at idx16 must NOT be read at idx15, or the effect is the harness.
#
# METHOD. runScript.py -task probe perturbs shapexUpper[idx] by a delta, runs
# the PRIMAL ONLY to primalMinResTol 1e-8, and prints OBJ.val to 15 digits.
# The primal does not touch warpDeriv, so this measurement is independent of
# whether the patch is mounted; the patch is mounted anyway so the container is
# byte-identical to the one that produced the disputed table.
set -uo pipefail
BASE=/home/ubuntu/certonomous-runs/W4-idx16
CASE="$BASE/case"
IDX="$1"; DELTA="$2"; TAG="$3"; TASK="${4:-probe}"
# DAFoam's renameSolution refuses to overwrite a solution directory left by a
# previous probe ("... already exists, moving failed"), so each probe starts
# from the same on-disk state. This is the same `rm -rf processor*` the lab's
# own idx0 probe driver used (W5-regrade/a5pl_patched/probe_driver.sh).
sudo rm -rf "$CASE"/processor* "$CASE"/[1-9]* 2>/dev/null
sudo docker run --rm --cpus=4 --memory=8g \
    -v "$BASE":/mnt -v /home/ubuntu/certonomous-runs/W5-patch:/patch -w /mnt/case \
    dafoam/opt-packages:latest bash -lc \
    "source /home/dafoamuser/dafoam/loadDAFoam.sh && export PYTHONPATH=/patch/idwarp:\$PYTHONPATH && mpirun --allow-run-as-root -np 4 -x PYTHONPATH python runScript.py -task $TASK -probeIdx $IDX -probeDelta=$DELTA" \
    > "$BASE/probe_${TAG}.log" 2>&1
rc=$?
sudo chown -R ubuntu:ubuntu "$BASE" 2>/dev/null || true
echo "== idx=$IDX delta=$DELTA rc=$rc $(date -u +%FT%TZ)"
grep -aE "PROBE_RESULT|WARM_BASE|WARM_RESULT|SEQ_" "$BASE/probe_${TAG}.log" | tail -1
