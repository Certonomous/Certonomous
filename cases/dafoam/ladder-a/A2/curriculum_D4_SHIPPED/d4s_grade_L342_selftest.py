"""ADDENDUM 2 (L-342) grader selftest.  Drives d4s_grade.py on fixtures:
  1. an ABSENT INFRASTRUCTURE field (memavail_post_GiB=NOT_MEASURED) -> the row
     PARSES, the field reads None and is DISCLOSED, and G1 PROCEEDS;
  2. an ABSENT PHYSICS field (no inspect(exit,oomkilled) value) -> REFUSES;
     present-but-garbage (inspect exit "zz") -> REFUSES (absent != garbage);
  3. kernel exit 1 -> the G1 rc clause FAILS (verdict limb NOT A RESULT);
     harness 0 vs kernel 1 -> REFUSES (rc_disagreement);
  4. the D4S_ string: G9 PASSES on the REAL container line and FAILS on the
     old D4_ form, and reads kernel-held text too;
  5. the kernel-record row: pure function driven with exit 0/1 on the REAL
     timestamps of d4_O_20260826T040414Z_3177545; wall/core-min arithmetic;
     terminal clause positional on the text form; running container refuses;
     G10's frozen clause reads within_cap False for 731.667 > 620.0.
Run under `python3` AND `python3 -O`: there is no bare assert anywhere, every
check is an explicit comparison collected into a dict, so -O cannot silence
one.  Exit 0 only if every check holds."""
import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("g", os.path.join(HERE, "d4s_grade.py"))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

d = tempfile.mkdtemp(prefix="d4s_l342_")
work = os.path.join(d, "O")
os.makedirs(os.path.join(work, "0"))
open(os.path.join(work, "0", "U"), "w").write("x")
datum = int(os.path.getmtime(os.path.join(work, "0", "U")))
open(os.path.join(work, ".d4_age_datum"), "w").write(str(datum))
REAL_LINE = "D4S_IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663"
open(os.path.join(d, "good.log"), "w").write("stuff\n" + REAL_LINE + "\nFinalising parallel run\n")
open(os.path.join(d, "old.log"), "w").write("D4_IDWARP_SO_MD5: f0fcb488e0e98156575cd19548e91663\nFinalising parallel run\n")


def row(rc, insp, mempost="26.59", log="good.log"):
    return ("ARM=O ROW=SHIPPED IMG=dafoam/opt-packages:latest DIGEST=sha256:9d45 rc=%d "
            "wall_s=10975 ranks=4 core_min=731.667 cap_core_min=620.0 enforced_wall_s=9300 "
            "enforced_core_min=620.000000 memory=12g inspect(exit,oomkilled)=[%s] "
            "memavail_pre_GiB=26.01 memavail_post_GiB=%s cpuset=5,6,7,9 "
            "delivered_cores_mean=[NOT_MEASURED] siblings_pre=[NOT_MEASURED] "
            "siblings_post=[NOT_MEASURED] log=%s\n") % (rc, insp, mempost, log)


def ledger(text):
    p = os.path.join(d, "ledger.txt")
    open(p, "w").write("ITEM=D4-SHIPPED\n" + text)
    return p


def refuses(fn, needle):
    try:
        fn()
        return False
    except g.Refuse as exc:
        return needle in str(exc)


res = {}
# 1. absent INFRA field
rows = g.read_ledger(ledger(row(0, "0 false", mempost="NOT_MEASURED")))
res["1_infra_absent_row_PARSES"] = (len(rows) == 1 and rows[0]["ARM"] == "O")
res["1_infra_absent_reads_None_and_is_DISCLOSED"] = (
    rows[0]["memavail_post_GiB"] is None
    and "memavail_post_GiB" in rows[0]["infra_not_measured"]
    and "delivered" in rows[0]["infra_not_measured"])
r = g.g_completion(work, d, rows, ["O"])
res["1_G1_PROCEEDS_and_passes_on_physics_fields"] = (
    r["pass"] is True
    and r["arms"]["O"]["infrastructure_not_measured"] == rows[0]["infra_not_measured"])
# 2. absent PHYSICS field refuses; present-but-garbage refuses
res["2_physics_absent_REFUSES"] = refuses(
    lambda: g.g_completion(work, d, g.read_ledger(ledger(row(0, ""))), ["O"]),
    "kernel_exit_absent")
res["2_physics_garbage_REFUSES_not_treated_as_absent"] = refuses(
    lambda: g.g_completion(work, d, g.read_ledger(ledger(row(0, "zz false"))), ["O"]),
    "kernel_exit_unparseable")
# 3. rc = 1
r = g.g_completion(work, d, g.read_ledger(ledger(row(1, "1 false"))), ["O"])
res["3_kernel_exit_1_rc_clause_FAILS"] = (r["rc_clause_pass"] is False and r["pass"] is False)
res["3_rc_disagreement_REFUSES"] = refuses(
    lambda: g.g_completion(work, d, g.read_ledger(ledger(row(0, "1 false"))), ["O"]),
    "rc_disagreement")
# 4. D4S_ string
rows = g.read_ledger(ledger(row(0, "0 false")))
t_good = g.g_toolchain(rows, work, [os.path.join(d, "good.log")])
res["4_G9_PASSES_on_real_D4S_line"] = (
    t_good["idwarp_so_md5_distinct"] == ["f0fcb488e0e98156575cd19548e91663"]
    and t_good["pass"] is True)
res["4_G9_FAILS_on_old_D4_line"] = (
    g.g_toolchain(rows, work, [os.path.join(d, "old.log")])["pass"] is False)
res["4_G9_reads_kernel_held_text_too"] = (
    g.g_toolchain(rows, work, [], extra_texts={"docker_logs:x": REAL_LINE + "\n"})["pass"] is True)


# 5. kernel-record row
def insp(ex, oom=False, running=False):
    return {"Image": "sha256:9d45679d55fd47f5ca7afd99cabb86c7c2729cf2acf34c438eb33af5290f07fc",
            "Config": {"Image": "dafoam/opt-packages:latest"},
            "State": {"Running": running, "ExitCode": ex, "OOMKilled": oom,
                      "StartedAt": "2026-08-26T04:04:14.841346421Z",
                      "FinishedAt": "2026-08-26T07:07:09.642351339Z"},
            "HostConfig": {"Memory": 12884901888, "CpusetCpus": "5,6,7,9"}}


good = g.kernel_record_row("O", "d4_O_fixture", insp(0), "x\nFinalising parallel run\n", 620.0)
res["5_kernel_record_wall_10975_core_min_731_667"] = (
    good["wall_s"] == 10975 and good["core_min"] == 731.667
    and good["delivered"] == g.NOT_MEASURED and good["memavail_post_GiB"] is None)
res["5_kernel_record_sources_named_per_physics_field"] = all(
    k in good["field_sources"] for k in ("rc", "oomkilled", "wall_s", "terminal_statement"))
r = g.g_completion(work, d, [good], ["O"])
res["5_G1_PASSES_on_kernel_record_exit_0_terminal_positional"] = (
    r["pass"] is True and r["arms"]["O"]["source"] == "kernel_record"
    and r["arms"]["O"]["terminal_detail"]["source"] == "kernel_record")
r = g.g_completion(work, d, [g.kernel_record_row("O", "f", insp(1), "x\nFinalising parallel run\n", 620.0)], ["O"])
res["5_G1_rc_clause_FAILS_on_kernel_record_exit_1"] = (r["rc_clause_pass"] is False)
r = g.g_completion(work, d, [g.kernel_record_row("O", "f", insp(0), "Finalising parallel run\nmpirun noticed abort\n", 620.0)], ["O"])
res["5_terminal_clause_FAILS_when_not_last_line"] = (r["terminal_clause_pass"] is False)
res["5_running_container_REFUSES"] = refuses(
    lambda: g.kernel_record_row("O", "f", insp(0, running=True), "", 620.0), "still_running")
res["5_G10_frozen_clause_within_cap_False_for_731_667"] = (
    [x for x in g.g_caps([good])["rows"] if x["arm"] == "O"][0]["within_cap"] is False)
res["5_G11_oomkilled_reads_false"] = (good["oomkilled"] == "false")

mode = "python3" if __debug__ else "python3 -O"
for k, v in res.items():
    print("  [%s] %s" % ("OK " if v else "BAD", k))
npass = sum(1 for v in res.values() if v)
print("L342_SELFTEST mode=%s pass=%d fail=%d" % (mode, npass, len(res) - npass))
sys.exit(0 if npass == len(res) else 1)
