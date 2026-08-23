#!/usr/bin/env bash
# b3_rss_watch.sh -- TRUE peak-RSS instrument for one NAMED docker container.
#
# Registered in PREREGISTRATION.md in this directory, section 4, and frozen at that
# commit. Nothing in this file is sent, filed or uploaded.
#
# WHY THIS FILE EXISTS. cases/dafoam/ladder-b/B3/decomposition_np4/RESULTS.md:132
# says of the 6.156 GiB figure it carries: "a `docker stats` sample taken during the
# linear solve, not a true peak -- no per-arm high-water mark was recorded". This
# instrument records the high-water mark.
#
# WHAT IT SAMPLES, every CADENCE seconds, for the named container only:
#   memory.peak    -- cgroup v2 kernel high-water of memory.current. MONOTONE
#                     NON-DECREASING, so the last reading before teardown IS the
#                     true peak up to that instant. Includes page cache and kernel
#                     memory: it is the quantity --memory=12g is enforced against.
#   memory.current -- instantaneous, for the trajectory.
#   tree RSS       -- sum of VmRSS over every pid in the container cgroup. Resident
#                     process memory only, no page cache.
#   per-pid VmHWM  -- kernel per-process high-water. Answers "which process", which
#                     a container-level number cannot.
#
# THE TWO NUMBERS ARE NOT THE SAME QUANTITY and the grader reports both. Neither is
# `docker stats` MemUsage (= memory.current - inactive_file), the instrument every
# earlier B3 figure came from -- and whose field-3 parse bug is on the record at
# cases/dafoam/ladder-a/A6/rung_n16_np1/RESULTS.md:377. This file parses no
# human-formatted size string at all; every number is raw bytes from sysfs or kB
# from /proc/<pid>/status.
#
# ATTRIBUTION. adjoint_unblock_reproduce/RESULTS.md:292: "A peak-RSS number from a
# shared-box watcher is a claim about a named container or it is not a measurement."
# That lane's raw watcher maximum, 9.786 GiB, belonged to ANOTHER LANE's container.
# This instrument resolves the container by name to a container id to a cgroup path
# and reads only that cgroup. It cannot see a peer lane's container and it REFUSES
# if it cannot resolve the one it was given.
#
# HOST-MEMORY FLOOR. Structure and ordering follow the peer W4 lane's
# w4_m1m2_memguard.sh (L-239: a registered stop with nothing wired to it is not a
# guard). The kill decision is taken FIRST, before any sampling that can block.
#
# usage: b3_rss_watch.sh <container-name> <out-log> <max-ticks> <hard_floor_kib>
#        b3_rss_watch.sh --selftest <out-dir>
#
# exit 0 = container finished, no breach   exit 9 = host floor breached, kill issued
# exit 2 = refusal (cannot resolve, cannot read, self-test could not see the plant)
set -uo pipefail

CADENCE=2                       # seconds; the registered requirement is <= 5
PLANT_GIB=2                     # self-test allocation
PLANT_LO=2.00                   # self-test acceptance band, GiB, tree RSS
PLANT_HI=2.60
PEAK_LO=2.00                    # self-test acceptance band, GiB, memory.peak
PEAK_HI=3.50
IMG=dafoam-subpclu:v2           # the plant runs in the SAME image as the graded arms

now() { date -u +%FT%TZ; }
refuse() { echo "b3_rss_watch: REFUSE: $*" >&2; exit 2; }
memavail_kib() { awk '/^MemAvailable:/{print $2}' /proc/meminfo; }

# Resolve a container NAME to its cgroup v2 directory. Empty output = not resolvable.
cgdir_of() {
    local name="$1" id d
    id=$(timeout 5 sudo -n docker inspect -f '{{.Id}}' "$name" 2>/dev/null) || return 0
    [ -n "$id" ] || return 0
    for d in "/sys/fs/cgroup/system.slice/docker-${id}.scope" \
             "/sys/fs/cgroup/docker/${id}"; do
        [ -r "$d/memory.peak" ] && { echo "$d"; return 0; }
    done
    return 0
}

# ------------------------------------------------------------------ self-test --
# THE PLANTED CONTROL (standing rule 3). A watcher that reports a peak is not
# evidence until it has been shown able to see a KNOWN peak it did not choose.
# Plants PLANT_GIB of genuinely-touched anonymous memory in a container of the
# graded image and REFUSES unless both instruments read it back inside the bands.
if [ "${1:-}" = "--selftest" ]; then
    OUT="${2:?selftest needs an output directory}"
    mkdir -p "$OUT" || refuse "cannot create $OUT"
    SLOG="$OUT/selftest_watch.log"
    CNAME=b3rss_plant_$$

    # (a) trigger path: a hard floor of MemTotal can never be satisfied, so the kill
    #     path must fire on the first sample. The kill is redirected at a sentinel,
    #     so the wiring is proved without touching docker.
    SENT="$OUT/.selftest_kill_fired"; rm -f "$SENT"
    MT=$(awk '/^MemTotal:/{print $2}' /proc/meminfo)
    B3RSS_KILLCMD="touch $SENT" "$0" no-such-container-$$ "$OUT/selftest_trigger.log" 5 "$MT"
    trc=$?
    [ "$trc" = "9" ] && [ -f "$SENT" ] || {
        echo "b3_rss_watch selftest: TRIGGER PATH FAILED (exit=$trc sentinel=$([ -f "$SENT" ] && echo PRESENT || echo ABSENT))"
        exit 2; }
    echo "b3_rss_watch selftest: trigger path PASS (exit 9, kill command executed)"

    # (b) the plant. Hard floor 1 kB: this arm must never kill.
    rm -f "$SLOG"
    "$0" "$CNAME" "$SLOG" 150 1 &
    WPID=$!
    # This is the FIRST container of the chain and it runs the graded image, so it
    # also carries the image content assertion registered in PREREGISTRATION.md 2.2:
    # a tag is not an identity, the md5 of the patched source file is.
    timeout 300 sudo -n docker run --rm --name "$CNAME" --cpuset-cpus 0-3 --memory=6g \
        "$IMG" bash -lc \
        "md5sum /home/dafoamuser/dafoam/repos/dafoam/src/adjoint/DALinearEqn/DALinearEqn.C
source /home/dafoamuser/dafoam/loadDAFoam.sh
python -c \"import time
b=bytearray(${PLANT_GIB}*1024**3)
for i in range(0,len(b),4096): b[i]=1
time.sleep(25)\"" >> "$OUT/selftest_plant.log" 2>&1
    prc=$?
    wait $WPID 2>/dev/null
    [ "$prc" = "0" ] || refuse "plant container exited rc=$prc (see $OUT/selftest_plant.log)"

    # NB: the log emits "KEY= value" as two whitespace fields on purpose, so the
    # value is $(i+1) under the default field separator. Do NOT split on "=".
    read -r seen_rss seen_peak < <(awk '
        {for(i=1;i<=NF;i++){
            if($i=="TREE_RSS_KB="){r=$(i+1)+0; if(r>mr)mr=r}
            if($i=="MEM_PEAK_B="){p=$(i+1)+0; if(p>mp)mp=p}}}
        END{printf "%.4f %.4f\n", mr/1048576.0, mp/1073741824.0}' "$SLOG")

    echo "b3_rss_watch selftest: planted ${PLANT_GIB}.00 GiB; tree RSS read back ${seen_rss} GiB (band ${PLANT_LO}-${PLANT_HI}); memory.peak read back ${seen_peak} GiB (band ${PEAK_LO}-${PEAK_HI})"
    awk -v r="$seen_rss" -v p="$seen_peak" -v rl="$PLANT_LO" -v rh="$PLANT_HI" \
        -v pl="$PEAK_LO" -v ph="$PEAK_HI" \
        'BEGIN{exit !(r>=rl && r<=rh && p>=pl && p<=ph)}' || {
        echo "b3_rss_watch selftest: FAILED -- the instrument cannot see a plant it was given."
        echo "b3_rss_watch selftest: FAILED" >> "$OUT/selftest_verdict.txt"
        exit 2; }
    echo "b3_rss_watch selftest: PASS plant_gib=${PLANT_GIB} tree_rss_gib=${seen_rss} mem_peak_gib=${seen_peak} utc=$(now)" \
        | tee "$OUT/selftest_verdict.txt"
    exit 0
fi

# --------------------------------------------------------------------- normal --
CNAME="${1:?container name}"
LOG="${2:?output log path}"
MAXTICKS="${3:?max ticks}"
HARD_KIB="${4:?host MemAvailable hard floor, kB}"
KILLCMD="${B3RSS_KILLCMD:-sudo -n docker kill $CNAME}"
case "$MAXTICKS$HARD_KIB" in *[!0-9]*) refuse "max-ticks and floor must be integers";; esac

: > "$LOG" || refuse "cannot write $LOG"
echo "$(now) START container=$CNAME cadence_s=$CADENCE max_ticks=$MAXTICKS hard_floor_kib=$HARD_KIB baseline_memavail_kib=$(memavail_kib) killcmd='$KILLCMD'" >> "$LOG"

CG=""; seen_running=0; tick=0
while [ "$tick" -lt "$MAXTICKS" ]; do
    tick=$((tick + 1))

    # --- kill decision FIRST, before anything that can block (peer lane's ordering)
    m=$(memavail_kib)
    if [ -n "$m" ] && [ "$m" -lt "$HARD_KIB" ]; then
        echo "$(now) ABORT reason=HOST_HARD_FLOOR memavail_kib=$m floor_kib=$HARD_KIB" >> "$LOG"
        eval "$KILLCMD" >> "$LOG" 2>&1
        echo "$(now) KILL_ISSUED rc=$? -- this run is a MEMORY-ABORT and is NOT A RESULT about convergence" >> "$LOG"
        exit 9
    fi

    # --- resolve the cgroup once the container appears; only ever this container
    [ -n "$CG" ] || CG=$(cgdir_of "$CNAME")

    if [ -n "$CG" ] && [ -r "$CG/memory.peak" ]; then
        seen_running=1
        peak=$(cat "$CG/memory.peak" 2>/dev/null); cur=$(cat "$CG/memory.current" 2>/dev/null)
        rss_sum=0; npids=0; procs=""
        while read -r p; do
            [ -r "/proc/$p/status" ] || continue
            read -r pname prss phwm < <(awk '/^Name:/{n=$2}/^VmRSS:/{r=$2}/^VmHWM:/{h=$2}END{print n" "(r+0)" "(h+0)}' "/proc/$p/status" 2>/dev/null)
            [ -n "${prss:-}" ] || continue
            rss_sum=$((rss_sum + prss)); npids=$((npids + 1))
            procs="$procs ${pname}:${p}:rss${prss}:hwm${phwm}"
        done < "$CG/cgroup.procs"
        echo "$(now) SAMPLE MEM_PEAK_B= ${peak:-0} MEM_CURRENT_B= ${cur:-0} TREE_RSS_KB= $rss_sum NPIDS= $npids MEMAVAIL_KB= ${m:-0} PROCS=[$procs ]" >> "$LOG"
    else
        if [ "$seen_running" = "1" ]; then
            echo "$(now) DONE container_gone ticks=$tick" >> "$LOG"
            exit 0
        fi
        echo "$(now) WAIT container=$CNAME not yet resolvable memavail_kib=${m:-?}" >> "$LOG"
    fi
    sleep "$CADENCE"
done
echo "$(now) DONE max_ticks_reached ticks=$tick seen_running=$seen_running" >> "$LOG"
[ "$seen_running" = "1" ] || refuse "never resolved container $CNAME -- no measurement was taken"
exit 0
