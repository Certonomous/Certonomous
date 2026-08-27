#!/bin/bash
# ---------------------------------------------------------------------------
# CONTENTION TIME-SERIES SAMPLER.
#
# PROVENANCE, and why this file has this name.  This program was found in the
# working tree on 2026-08-27 OVERWRITING `contention_sampler.sh`, whose
# committed form (`8a45cd7b`) is a DIFFERENT INSTRUMENT that is still in use.
# It is NOT a stale copy: its mtime (2026-08-25T17:42:59Z) is ~15 h AFTER the
# commit it appeared to revert, so it is forward work, and it matches no
# ancestor blob.  It was preserved here, under its own name, by the
# ansys-verification supervisor rather than committed over the other one.
#
# THE COLLISION THIS NAME EXISTS TO PREVENT.  The two programs take FOUR
# ARGUMENTS EACH AND MEAN ENTIRELY DIFFERENT THINGS BY THEM:
#     contention_sampler.sh            <CONTENTION.txt> <solver.log> <threshold_simtime> <label>
#     contention_timeseries_sampler.sh <session_id>     <out_file>   <peer_pid>          <peer_name>
# A caller holding the first interface and reaching the second would pass a
# FILENAME where a session id is expected; `kill -0` on it simply fails, the
# while loop never runs, and the caller gets a header line, an "ended" line and
# NO SAMPLES -- with no error and a zero exit.  THE FAILURE IS SILENT, which is
# why one filename may never carry two measurement programs.
#
# WHAT EACH ONE IS FOR.  `contention_sampler.sh` is a ONE-SHOT MIDPOINT sampler:
# it waits for the solver's own SIMULATION time to cross a threshold, emits a
# single self-dating sample, and records MISSED (exit 1) if the run ends first --
# it refuses to reconstruct a missed sample from a later load average.  THIS one
# is a CONTINUOUS series: it polls every 30 s for as long as a session lives.
# They are complements, not versions.  Neither supersedes the other.
#
# ONE MEASURED PROPERTY WORTH KEEPING, and it is why this file was not discarded:
# `pgrep -c -f` matches the FULL COMMAND LINE, so it does not suffer the
# truncation that `ps -o comm` does (comm cuts at 15 chars, so
# buoyantBoussinesqSimpleFoam reads "buoyantBoussine" and a grep for "Foam"
# MISSES IT -- measured by this team 2026-08-25 and recorded in the sibling
# script's comments).
#
# NO RECORD ON DISK IS IN THIS PROGRAM'S FORMAT.  The `CONTENTION.csv` files
# under VMFL019 and VMFL050 have a THIRD header
# (utc,loadavg1,run_slash_total,*_procs,top_pcpu) and came from neither of these
# two scripts.  So nothing that has been graded rests on this program, and
# nothing was corrupted by the shadowing.
#
# Preserved verbatim below -- NOT re-authored.  Supervisor ruling
# [lab-attributed], 2026-08-27.  Read-only: it observes and writes its own log.
# ---------------------------------------------------------------------------
# OS-level contention SAMPLER (read-only; it can only observe and write its own log).
# Armed BEFORE launch so the contention record rests on samples on disk, not on a
# promise to look later -- a lane is not a watcher and dies when its turn ends.
set -u
SID="$1"; OUT="$2"; PEER_PID="$3"; PEER_NAME="$4"
echo "# utc load1 load5 load15 nproc peer_${PEER_NAME}_pid${PEER_PID}_alive n_solver_procs" > "$OUT"
while kill -0 "$SID" 2>/dev/null; do
  L=$(cut -d' ' -f1-3 /proc/loadavg)
  if kill -0 "$PEER_PID" 2>/dev/null; then P=1; else P=0; fi
  N=$(pgrep -c -f 'simpleFoam|laplacianFoam|blockMesh|postProcess' 2>/dev/null || echo 0)
  echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $L $(nproc) $P $N" >> "$OUT"
  sleep 30
done
echo "# sampler ended $(date -u +%Y-%m-%dT%H:%M:%SZ) (watched session $SID gone)" >> "$OUT"
