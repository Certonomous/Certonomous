#!/bin/bash
# T10a-R preprocessing (Charter 2d mesh side): blockMesh, checkMesh,
# viewFactorsGen, per case, wall time and peak RSS recorded in <case>/BUILD.txt.
# NO SOLVER IS RUN HERE.  Refuses a case that already holds constant/F.
HERE="$(cd "$(dirname "$0")" && pwd)"
CASE="$1"; CDIR="$HERE/$CASE"
[ -d "$CDIR" ] || { echo "no such case $CASE" >&2; exit 4; }
[ -f "$CDIR/constant/F" ] && { echo "SKIP $CASE: constant/F already present"; exit 1; }
source /usr/lib/openfoam/openfoam2606/etc/bashrc
cd "$CDIR" || exit 4
T0=$(date +%s); nice -n 15 blockMesh > log.blockMesh 2>&1; BM=$?; T1=$(date +%s)
nice -n 15 checkMesh > log.checkMesh.build 2>&1; CM=$?; T2=$(date +%s)
/usr/bin/time -v nice -n 15 viewFactorsGen > log.viewFactorsGen 2>log.vfgen.time; VF=$?; T3=$(date +%s)
RSS=$(awk '/Maximum resident/{print $NF}' log.vfgen.time)
{ echo "case            $CASE"
  echo "date            $(date -u +%FT%TZ)"
  echo "generator       viewFactorsGen"
  echo "blockMesh_rc    $BM   wall $((T1-T0)) s"
  echo "checkMesh_rc    $CM   wall $((T2-T1)) s"
  echo "viewFactorsGen_rc  $VF   wall $((T3-T2)) s   maxRSS_kB $RSS"
  echo "F_size          $(stat -c%s constant/F 2>/dev/null) bytes"
  echo "gFF_size        $(stat -c%s constant/globalFaceFaces 2>/dev/null) bytes"
  echo "F_sha256        $(sha256sum constant/F 2>/dev/null | cut -d' ' -f1)"
} > BUILD.txt
cat BUILD.txt
[ $BM -eq 0 ] && [ $CM -eq 0 ] && [ $VF -eq 0 ]
