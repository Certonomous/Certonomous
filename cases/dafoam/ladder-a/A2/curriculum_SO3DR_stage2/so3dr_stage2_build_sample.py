#!/usr/bin/env python3
"""Stage-2 stratified sample builder — host-side reading of the FROZEN D6R log.
Reuses the SO3DR reader's OWN parse_primal_records so the failed/succeeded
partition is byte-identical to the graded Stage-1 census. Deterministic:
fixed seed. Emits the exact registered sample for the pre-registration.
NO SOLVER, NO COMPUTE — this reads one existing log file."""
import sys, json, random, importlib.util, hashlib

READER = "/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_SO3DR/so3dr_replay.py"
LOG = "/home/ubuntu/certonomous-runs/CURRICULUM-D6R-a2-wing-multipoint/O_mp_20260828T162849Z_1898072.log"
SEED = 20260907          # registered seed
N_FAIL = 24              # stratum: cl04 FAILED inside multipoint
N_SUCC = 12              # stratum: cl04 SUCCEEDED inside multipoint
# total N = 36 >= 30 (binomial resolution justified in prereg §2)

spec = importlib.util.spec_from_file_location("so3dr", READER)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
print("log lines:", len(lines))
print("log sha256:", hashlib.sha256(open(LOG,'rb').read()).hexdigest())

records = m.parse_primal_records(lines)
blocks = m.parse_design_vars_blocks(lines)

# map each record to the design block line that precedes it (carries the DV vector)
def block_for(s_line):
    b = None
    for bb in blocks:
        if bb["line"] < s_line:
            b = bb
        else:
            break
    return b

cl04 = [r for r in records if r["scenario"] == "cl04"]
failed = [r for r in cl04 if r["banners"] > 0]
succ   = [r for r in cl04 if r["banners"] == 0]
print("cl04 records:", len(cl04), "failed:", len(failed), "succeeded:", len(succ))

rng = random.Random(SEED)
def draw(pool, n):
    idx = sorted(rng.sample(range(len(pool)), n))
    return [pool[i] for i in idx]

sf = draw(failed, N_FAIL)
ss = draw(succ, N_SUCC)

def dv_block(r):
    b = block_for(r["start_line"])
    return None if b is None else b["line"]

def row(r, stratum):
    bl = dv_block(r)
    aoa_dv = None
    if bl is not None:
        for bb in blocks:
            if bb["line"] == bl:
                aoa_dv = bb["aoa"].get("cl04")
                break
    return {
        "ordinal": r["ordinal"],
        "record_start_line": r["start_line"],
        "dv_block_line": bl,
        "record_aoa": round(r["aoa"], 8) if r["aoa"] is not None else None,
        "cl04_dv_aoa": round(aoa_dv, 8) if aoa_dv is not None else None,
        "multipoint_outcome": stratum,
        "banners": r["banners"],
    }

sample = [row(r, "FAILED") for r in sf] + [row(r, "SUCCEEDED") for r in ss]
sample.sort(key=lambda x: x["dv_block_line"])
out = {
    "seed": SEED, "n_fail": N_FAIL, "n_succ": N_SUCC, "N": N_FAIL + N_SUCC,
    "population_failed": len(failed), "population_succeeded": len(succ),
    "log_sha256": hashlib.sha256(open(LOG,'rb').read()).hexdigest(),
    "sample": sample,
}
json.dump(out, open("/home/ubuntu/Certonomous/cases/dafoam/ladder-a/A2/curriculum_SO3DR_stage2/so3dr_stage2_registered_sample.json","w"), indent=1)
for s in sample:
    print(s)
