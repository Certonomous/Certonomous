#!/usr/bin/env bash
# D14-M SELFTEST -- drives every refusal in the driver's guard block and both python
# instruments, against sacrificial objects only (rule 3).  Never touches the registered
# run root (asserted absent before and after), the baseline reference, or any live
# container.  Legs:
#   S0  bash -n on driver/selftest; python -m py_compile on the two instruments
#   S1  G14-0 clean generator -> PASS (rc 0); --plant -> planted refinement REFUSED (rc 0 = control fired)
#   S1b G14-0 on a copy with s0 halved -> rc 2 (the refusal itself, driven directly)
#   S2  grader selftest under python3 AND python3 -O -> 14/14 both; ast.Assert = 0 in both instruments
#   S3  driver guard block on a sacrificial root: clear -> exit 40 (guards passed, bogus image, nothing staged)
#   S4  G-ROOT.5 (a): sacrificial RUNNING d14m_ container -> rc 3
#   S5  G-ROOT.5 (b): sacrificial live pid, cwd = sacrificial root, in d14m_driver.pid -> rc 3
#   S5b stale pidfile does not block -> exit 40
#   S6  G-ROOT.3: a ledger carrying another ITEM -> rc 3;  S7 G-ROOT.4 ALREADY_BOUGHT row -> rc 3
#   S8  G-ROOT.1: a non-sacrificial selftest root -> rc 3;  S9 usage -> 64
#   S10 registered run root absent before and after; no d14m_ container survives
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; D="$HERE/d14m_driver.sh"; C="$HERE/d14m_contaminant_check.py"; G="$HERE/d14m_grade.py"
REGROOT=/home/ubuntu/certonomous-runs/CURRICULUM-D14M-a2-wing-remesh
REF=/home/ubuntu/certonomous-runs/A2-mach-wing; IMG=dafoam/opt-packages:latest
STAMP=$(date -u +%Y%m%dT%H%M%SZ); SR="/home/ubuntu/certonomous-runs/_d14m_selftest_$STAMP"
PASS=0; FAIL=0; ok(){ echo "  [OK ] $1"; PASS=$((PASS+1)); }; bad(){ echo "  [BAD] $1"; FAIL=$((FAIL+1)); }
echo "D14M SELFTEST $(date -u +%Y-%m-%dT%H:%M:%SZ) driver_md5=$(md5sum "$D"|cut -d' ' -f1) contam_md5=$(md5sum "$C"|cut -d' ' -f1) grader_md5=$(md5sum "$G"|cut -d' ' -f1) sacrificial_root=$SR"
[ -e "$REGROOT" ] && { bad "registered run root EXISTS before the selftest: $REGROOT"; exit 2; } || ok "S10 registered run root absent before: $REGROOT"
mkdir -p "$SR"
# S0
bash -n "$D" && bash -n "$0" && python3 -m py_compile "$C" "$G" && ok "S0 bash -n and py_compile clean" || bad "S0 syntax"
# S1 / S1b
python3 "$C" "$REF/genWingMesh.py" > "$SR/g0_clean.out" 2>&1; r1=$?
python3 "$C" "$REF/genWingMesh.py" --plant > "$SR/g0_plant.out" 2>&1; r2=$?
[ $r1 -eq 0 ] && [ $r2 -eq 0 ] && grep -q "PLANTED CONTROL FIRED" "$SR/g0_plant.out" && ok "S1 G14-0 clean generator PASS (rc 0); planted refinement (N 39->78, s0 1e-3->5e-4) REFUSED by the same reader" || bad "S1 rc_clean=$r1 rc_plant=$r2"
sed 's/"s0": 1.0e-3,/"s0": 5.0e-4,/' "$REF/genWingMesh.py" > "$SR/gen_halved.py"
python3 "$C" "$SR/gen_halved.py" > "$SR/g0_halved.out" 2>&1; r3=$?
[ $r3 -eq 2 ] && grep -q "s0 = 0.0005 differs from registered 0.001" "$SR/g0_halved.out" && grep -q "md5 .* != registered" "$SR/g0_halved.out" && ok "S1b s0 halved -> rc 2, both the md5 and the s0 reason named" || bad "S1b rc=$r3"
# S2
python3 "$G" --selftest --tmpdir "$SR" > "$SR/grader_plain.out" 2>&1; r4=$?
python3 -O "$G" --selftest --tmpdir "$SR" > "$SR/grader_O.out" 2>&1; r5=$?
NA=$(python3 -c "import ast,sys; print(sum(sum(1 for n in ast.walk(ast.parse(open(p).read())) if isinstance(n, ast.Assert)) for p in sys.argv[1:]))" "$C" "$G")
[ $r4 -eq 0 ] && [ $r5 -eq 0 ] && grep -q "SELFTEST PASS 14/14" "$SR/grader_plain.out" && grep -q "SELFTEST PASS 14/14" "$SR/grader_O.out" && grep -q "python_O=True" "$SR/grader_O.out" && [ "$NA" = "0" ] && ok "S2 grader selftest 14/14 under python3 and python3 -O; ast.Assert count over both instruments = 0" || bad "S2 rc=$r4/$r5 asserts=$NA"
# S3 clear
R3="$SR/root_clear"; mkdir -p "$R3"
( cd "$HERE" && D14M_SELFTEST_ROOT="$R3" bash "$D" MESH ) > "$SR/s3.out" 2>&1; rc=$?
[ $rc -eq 40 ] && grep -q "D14M_G_ROOT5_PASS" "$SR/s3.out" && grep -q "D14M_G14_0_PASS planted_control=fired" "$SR/s3.out" && grep -q "D14M_MD5_PASS" "$SR/s3.out" && [ ! -e "$R3/MESH" ] && ok "S3 guard block clear -> exit 40 after G-ROOT.1-.5, G14-0 (+planted control) and md5s; nothing staged" || bad "S3 rc=$rc: $(tail -2 "$SR/s3.out")"
# S4 live container
CN="d14m_selftest_${STAMP}"
if sudo -n docker run -d --name "$CN" --cpus=0.1 --cpuset-cpus=14 --memory=64m --memory-swap=64m "$IMG" bash -c "sleep 120" >/dev/null 2>&1; then
  ( cd "$HERE" && D14M_SELFTEST_ROOT="$R3" bash "$D" MESH ) > "$SR/s4.out" 2>&1; rc=$?
  [ $rc -eq 3 ] && grep -q "ABORT G-ROOT.5 a RUNNING container already carries this item's prefix: \[$CN" "$SR/s4.out" && ok "S4 G-ROOT.5(a) live container $CN -> rc 3" || bad "S4 rc=$rc"
  sudo -n docker rm -f "$CN" >/dev/null 2>&1
else bad "S4 could not start the sacrificial container"; fi
# S5 live pid in pidfile
( cd "$R3" && exec sleep 120 ) & SPID=$!; echo "$SPID" > "$R3/d14m_driver.pid"
( cd "$HERE" && D14M_SELFTEST_ROOT="$R3" bash "$D" MESH ) > "$SR/s5.out" 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "ABORT G-ROOT.5 driver pidfile $R3/d14m_driver.pid names LIVE pid $SPID" "$SR/s5.out" && ok "S5 G-ROOT.5(b) live pid $SPID cwd=$R3 -> rc 3" || bad "S5 rc=$rc"
kill "$SPID" 2>/dev/null; wait "$SPID" 2>/dev/null
echo 999999 > "$R3/d14m_driver.pid"
( cd "$HERE" && D14M_SELFTEST_ROOT="$R3" bash "$D" MESH ) > "$SR/s5b.out" 2>&1; rc=$?
[ $rc -eq 40 ] && grep -q "driver_pidfile=present_stale_or_ancestor" "$SR/s5b.out" && ok "S5b stale pidfile ignored -> exit 40" || bad "S5b rc=$rc"
rm -f "$R3/d14m_driver.pid"
# S6 / S7
R6="$SR/root_foreign"; mkdir -p "$R6"; echo "ITEM=CURRICULUM-D4-SHIPPED" > "$R6/ledger.txt"
( cd "$HERE" && D14M_SELFTEST_ROOT="$R6" bash "$D" MESH ) > "$SR/s6.out" 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "ABORT G-ROOT.3" "$SR/s6.out" && ok "S6 G-ROOT.3 foreign ITEM in ledger -> rc 3" || bad "S6 rc=$rc"
R7="$SR/root_bought"; mkdir -p "$R7"; printf 'ITEM=CURRICULUM-D14M\nARM=MESH rc=0 oom=false wall_s=40 core_min=0.67 container=x\n' > "$R7/ledger.txt"
( cd "$HERE" && D14M_SELFTEST_ROOT="$R7" bash "$D" MESH ) > "$SR/s7.out" 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "ABORT G-ROOT.4 ALREADY_BOUGHT" "$SR/s7.out" && ok "S7 G-ROOT.4 ALREADY_BOUGHT rc=0 row -> rc 3" || bad "S7 rc=$rc"
# S8 / S9
( cd "$HERE" && D14M_SELFTEST_ROOT="/home/ubuntu/certonomous-runs/A2-mach-wing" bash "$D" MESH ) > "$SR/s8.out" 2>&1; rc=$?
[ $rc -eq 3 ] && grep -q "ABORT G-ROOT.1" "$SR/s8.out" && ok "S8 G-ROOT.1 a non-sacrificial selftest root (the baseline's!) -> rc 3, nothing touched" || bad "S8 rc=$rc"
( cd "$HERE" && bash "$D" ) > /dev/null 2>&1; rc=$?; [ $rc -eq 64 ] && ok "S9 usage -> 64" || bad "S9 rc=$rc"
# S10
rm -f "$HERE"/G14-0_*.json
rm -rf "$SR"; [ ! -e "$SR" ] && ok "sacrificial root removed: $SR" || bad "sacrificial root still present"
[ ! -e "$REGROOT" ] && ok "S10 registered run root still absent after: $REGROOT" || bad "registered run root appeared"
sudo -n docker ps -a --format '{{.Names}}' 2>/dev/null | grep -q "^d14m_" && bad "a d14m_ container survives" || ok "no d14m_ container survives"
echo "D14M SELFTEST pass=$PASS fail=$FAIL $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ "$FAIL" -eq 0 ]
