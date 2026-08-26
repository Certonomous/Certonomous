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

# 6. ADDENDUM 2b (D4S-GRADER-DEF-2): arm-kind-aware completion.  Every unit
#    below first makes its condition OCCUR (a mutation applied, then removed)
#    so none can pass vacuously; the decisive rows are the REAL arm bytes.
REAL_BASE = "/home/ubuntu/certonomous-runs/CURRICULUM-D4-SHIPPED-a2-wing-cdmin"
LAUNCHER = os.path.join(HERE, "d4s_run_arm.sh")
real_rows = g.read_ledger(os.path.join(REAL_BASE, "ledger.txt"))
# 6a. kinds READ OUT OF THE LAUNCHER agree with the registered table; ACC is a
#     SOLVER by its own command (:323 == :322, `-task compute_totals`)
kinds = g.parse_arm_kinds(LAUNCHER)
res["6a_kinds_read_from_launcher_match_registered_table"] = (kinds == g.ARM_KIND)
res["6a_ACC_is_SOLVER_by_its_own_command_not_SCRIPT"] = (kinds.get("ACC") == "SOLVER")
res["6a_absent_launcher_REFUSES"] = refuses(
    lambda: g.parse_arm_kinds(os.path.join(d, "no_such_launcher.sh")), "launcher_absent")
mut = os.path.join(d, "mutated_launcher.sh")
src = open(LAUNCHER, errors="replace").read()
import re as _re
mut_src = _re.sub(r'(?m)^  ACC\) CMD=".*$', '  ACC) CMD="decomposePar -force ; echo no-solver-here" ;;', src, count=1)
res["6a_launcher_mutation_APPLIED"] = (mut_src != src)
open(mut, "w").write(mut_src)
res["6a_launcher_table_DISAGREEMENT_REFUSES"] = refuses(
    lambda: g.assert_arm_kinds(mut), "arm_kind_disagreement")
open(mut, "w").write("#!/bin/bash\necho nothing\n")
res["6a_unparseable_launcher_REFUSES"] = refuses(lambda: g.parse_arm_kinds(mut), "launcher_unparseable")
# 6b. REAL P1 bytes (kind SCRIPT, 0 terminal statements in its log): PASS on
#     rc=0 + marker + 6 artefacts newer than P1's own datum; the terminal
#     statement is REPORTED false and NOT composed
r = g.g_completion(os.path.join(REAL_BASE, "O"), REAL_BASE, real_rows, ["P1"], launcher=LAUNCHER)
p1 = r["arms"]["P1"]
res["6b_P1_REAL_BYTES_PASS_script_rule"] = (
    r["pass"] is True and p1["arm_kind"] == "SCRIPT"
    and p1["terminal_detail"]["n_artefacts_checked"] == 6
    and p1["terminal_detail"]["all_artefacts_present_and_newer"] is True
    and len(p1["terminal_detail"]["bookkeeping_marker_present_NOT_SUCCESS"]) == 1
    and p1["terminal_detail"]["terminal_statement_INFORMATIONAL_not_composed"]["terminal_ok_POSITIONAL"] is False
    and r.get("arm_kinds_from_launcher") == g.ARM_KIND)
# 6c. REAL P2 and O bytes: SOLVER rule unchanged, strict, PASS
r = g.g_completion(os.path.join(REAL_BASE, "O"), REAL_BASE, real_rows, ["P2"], launcher=LAUNCHER)
res["6c_P2_REAL_BYTES_PASS_solver_rule"] = (r["pass"] is True and r["arms"]["P2"]["arm_kind"] == "SOLVER")
# 6d. REAL ACC bytes (rc=137, OOMKilled true, log ends on the mpirun abort):
#     kind SOLVER; rc clause FAILS; terminal clause FAILS; the script
#     relaxation does NOT reach it
r = g.g_completion(os.path.join(REAL_BASE, "O"), REAL_BASE, real_rows, ["ACC"], launcher=LAUNCHER)
acc = r["arms"]["ACC"]
res["6d_ACC_REAL_BYTES_rc137_OOM_FAILS_both_clauses_as_SOLVER"] = (
    acc["arm_kind"] == "SOLVER" and acc["rc_clause_pass"] is False
    and acc["terminal_clause_pass"] is False and r["pass"] is False
    and acc["oomkilled"] == "true")
# 6e. SCRIPT fixture: with every artefact -> PASS; one artefact REMOVED ->
#     FAILS; restored -> PASS; artefact OLDER than the datum -> FAILS; marker
#     removed -> FAILS
p1dir = os.path.join(d, "P1")
os.makedirs(p1dir)
open(os.path.join(p1dir, ".d4_age_datum"), "w").write(str(datum - 100))
for f in g.SCRIPT_ARTEFACTS["P1"]:
    open(os.path.join(p1dir, f), "w").write("{}")
open(os.path.join(d, "p1.log"), "w").write("D4S_IDWARP_SO_MD5: x\nno End line, no terminal statement\n")
open(os.path.join(d, "p1.log.ok.stamp"), "w").write("")
rows_p1 = g.read_ledger(ledger(row(0, "0 false", log="p1.log").replace("ARM=O", "ARM=P1")))
r = g.g_completion(work, d, rows_p1, ["P1"])
res["6e_SCRIPT_fixture_all_artefacts_PASS_without_any_terminal_statement"] = (
    r["pass"] is True and r["arms"]["P1"]["terminal_detail"]["n_artefacts_checked"] == 6)
os.remove(os.path.join(p1dir, "d4_decomp_B.json"))
r = g.g_completion(work, d, rows_p1, ["P1"])
res["6e_SCRIPT_fixture_one_artefact_REMOVED_FAILS"] = (r["terminal_clause_pass"] is False and r["pass"] is False)
open(os.path.join(p1dir, "d4_decomp_B.json"), "w").write("{}")
r = g.g_completion(work, d, rows_p1, ["P1"])
res["6e_SCRIPT_fixture_artefact_RESTORED_PASSES_again"] = (r["pass"] is True)
os.utime(os.path.join(p1dir, "d4_decomp_B.json"), (datum - 1000, datum - 1000))
r = g.g_completion(work, d, rows_p1, ["P1"])
res["6e_SCRIPT_fixture_artefact_OLDER_than_datum_FAILS"] = (r["terminal_clause_pass"] is False)
os.utime(os.path.join(p1dir, "d4_decomp_B.json"), None)
os.remove(os.path.join(d, "p1.log.ok.stamp"))
r = g.g_completion(work, d, rows_p1, ["P1"])
res["6e_SCRIPT_fixture_bookkeeping_marker_ABSENT_FAILS"] = (r["terminal_clause_pass"] is False)
open(os.path.join(d, "p1.log.ok.stamp"), "w").write("")
# 6f. SCRIPT arm with rc=1 FAILS on clause 1 even with every artefact present
r = g.g_completion(work, d, g.read_ledger(ledger(row(1, "1 false", log="p1.log").replace("ARM=O", "ARM=P1"))), ["P1"])
res["6f_SCRIPT_fixture_rc_1_FAILS_clause_1_artefacts_do_not_rescue_it"] = (
    r["rc_clause_pass"] is False and r["pass"] is False)
# 6g. SOLVER fixture: WITH the statement PASSES; WITHOUT it FAILS (strict)
r = g.g_completion(work, d, g.read_ledger(ledger(row(0, "0 false", log="good.log").replace("ARM=O", "ARM=P2"))), ["P2"])
res["6g_SOLVER_fixture_with_statement_PASSES"] = (r["pass"] is True and r["arms"]["P2"]["arm_kind"] == "SOLVER")
rows_nostmt = g.read_ledger(ledger(row(0, "0 false", log="old.log").replace("ARM=O", "ARM=P2")))
open(os.path.join(d, "old.log"), "w").write("D4S_IDWARP_SO_MD5: x\nno terminal statement here\n")
r = g.g_completion(work, d, rows_nostmt, ["P2"])
res["6g_SOLVER_fixture_without_statement_FAILS_clause_strict"] = (r["terminal_clause_pass"] is False and r["pass"] is False)
# 6h. an arm absent from the registered table REFUSES; a SCRIPT kind with no
#     registered artefact REFUSES (every kind must present something)
res["6h_unregistered_arm_kind_REFUSES"] = refuses(
    lambda: g.g_completion(work, d, g.read_ledger(ledger(row(0, "0 false").replace("ARM=O", "ARM=ZZ"))), ["ZZ"]), "arm_kind_unregistered")
saved = g.SCRIPT_ARTEFACTS["P1"]
g.SCRIPT_ARTEFACTS["P1"] = []
res["6h_SCRIPT_kind_with_EMPTY_artefact_list_REFUSES"] = refuses(
    lambda: g.g_completion(work, d, rows_p1, ["P1"]), "script_arm_without_registered_artefacts")
g.SCRIPT_ARTEFACTS["P1"] = saved
mode = "python3" if __debug__ else "python3 -O"
for k, v in res.items():
    print("  [%s] %s" % ("OK " if v else "BAD", k))
npass = sum(1 for v in res.values() if v)
print("L342_SELFTEST mode=%s pass=%d fail=%d" % (mode, npass, len(res) - npass))
sys.exit(0 if npass == len(res) else 1)
