#!/usr/bin/env bash
# package_caches.sh -- tar the warm mesh and solve caches for the demo machine.
#
# Why this is not just a tar command. Cache entries are replaced with
# rmtree-then-copytree (see L-9): between those two calls an entry does not
# exist on disk. Taring while any act is mid-save silently produces an archive
# with an entry missing, and the failure only shows up later as a cold run in
# front of a camera. So this waits for the cache to stop moving first.
#
#   scripts/package_caches.sh [output.tar.gz]
set -euo pipefail

RUNS=/home/ubuntu/certonomous-runs
OUT=${1:-/home/ubuntu/certonomous-cache.tar.gz}
SETTLE_SAMPLES=3      # consecutive identical samples required
SETTLE_INTERVAL=20    # seconds between samples
MAX_WAIT=1800         # give up waiting after 30 min and say so

cd "$RUNS"

fingerprint() {
    # Entry names AND byte totals. Names alone miss an entry being rewritten
    # in place; bytes alone miss one entry swapping for another.
    { ls -1 .mesh-cache 2>/dev/null; ls -1 .solve-cache 2>/dev/null;
      du -sb .mesh-cache .solve-cache 2>/dev/null; } | md5sum | cut -d' ' -f1
}

echo "waiting for the caches to settle ($SETTLE_SAMPLES identical samples, ${SETTLE_INTERVAL}s apart)"
stable=0
prev=""
waited=0
while [ "$stable" -lt "$SETTLE_SAMPLES" ]; do
    cur=$(fingerprint)
    if [ "$cur" = "$prev" ]; then
        stable=$((stable + 1))
    else
        stable=1
    fi
    printf "  %s  mesh=%s solve=%s  stable=%d/%d\n" \
        "$(date -u +%T)" \
        "$(ls -1 .mesh-cache 2>/dev/null | wc -l)" \
        "$(ls -1 .solve-cache 2>/dev/null | wc -l)" \
        "$stable" "$SETTLE_SAMPLES"
    prev=$cur
    [ "$stable" -ge "$SETTLE_SAMPLES" ] && break
    sleep "$SETTLE_INTERVAL"
    waited=$((waited + SETTLE_INTERVAL))
    if [ "$waited" -ge "$MAX_WAIT" ]; then
        echo "STILL MOVING after ${MAX_WAIT}s -- something is actively writing." >&2
        echo "Refusing to package a cache that is mid-write. Stop the running" >&2
        echo "acts, or re-run once they are done." >&2
        exit 2
    fi
done

echo "settled. packaging"
tar czf "$OUT" .mesh-cache .solve-cache

echo
echo "archive:  $OUT"
ls -lh "$OUT" | awk '{print "  size:   " $5}'
echo "  md5:    $(md5sum "$OUT" | cut -d' ' -f1)"
echo "  mesh entries:  $(ls -1 .mesh-cache 2>/dev/null | wc -l)"
echo "  solve entries: $(ls -1 .solve-cache 2>/dev/null | wc -l)"
echo
echo "contents:"
{ ls -1 .mesh-cache 2>/dev/null | sed 's/^/  mesh  /'
  ls -1 .solve-cache 2>/dev/null | sed 's/^/  solve /'; }
