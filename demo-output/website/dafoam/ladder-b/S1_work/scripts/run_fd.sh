cd ramp_kw
mkdir -p fdlogs
python - <<'PY' > fdjobs.txt
import json
p=json.load(open("fdpts/fd_plan.json"))
for j in p["jobs"]: print(j["name"], j["file"])
PY
while read name file; do
  if [ -s "fdlogs/$name.log" ] && grep -q "OBJ UFieldVar" "fdlogs/$name.log"; then echo "skip $name"; continue; fi
  rm -rf c1/processor* c1/[1-9]*
  mpirun -np 4 python runScript_S1.py -task run_model -case c1 -ncells 5000 \
     -betafile "$file" > "fdlogs/$name.log" 2>&1 < /dev/null
  echo "$name -> $(grep 'OBJ UFieldVar' fdlogs/$name.log | tail -1)"
done < fdjobs.txt
echo "=== FD SWEEP DONE ==="
