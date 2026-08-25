"""PLANTED CONTROL on section 5 clause 1's rc PROXY.  Out of band: builds synthetic
trees in scratch and grades them with the FROZEN reader's own check_completion.
The running case is never touched, read or written."""
import importlib.util, json, os, shutil, sys, tempfile, time

R = "/home/ubuntu/Certonomous/verification/runs/F5b_runs/analyse_f5b_physics.py"
spec = importlib.util.spec_from_file_location("f5b", R)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print("frozen reader graded by this control: %s" % R)
print("its blob: %s" % os.popen("git hash-object " + R).read().strip())
print()

tmp = tempfile.mkdtemp(prefix="f5b_rcproxy_")
def clause1(root):
    c = m.check_completion(root)
    for n, name, ok, detail in c.clauses:
        if n == 1:
            return ok, detail
    return None, "clause 1 not present"

rows = []
# ---- N: the NEGATIVE arm -- a clean tree the proxy must PASS -------------
root = m._synthetic_run(os.path.join(tmp, "N_clean"))
ok, _ = clause1(root); rows.append(("N  clean synthetic tree", True, ok))

# ---- P1: DRIVER FAILED -- run_case raised, so NO record.json (D-2 path) --
root = m._synthetic_run(os.path.join(tmp, "P1_no_record"))
os.remove(os.path.join(root, "record.json"))
ok, d1 = clause1(root); rows.append(("P1 record.json ABSENT (driver raised)", False, ok))

# ---- P2: a prelude log MISSING entirely ---------------------------------
root = m._synthetic_run(os.path.join(tmp, "P2_no_prelude"))
os.remove(os.path.join(root, "case", "log.potentialFoam"))
ok, _ = clause1(root); rows.append(("P2 log.potentialFoam MISSING", False, ok))

# ---- P3: a prelude log present but WITHOUT End (crashed prelude) --------
root = m._synthetic_run(os.path.join(tmp, "P3_prelude_no_end"))
open(os.path.join(root, "case", "log.blockMesh"), "w").write("...\nFOAM FATAL ERROR\n")
ok, _ = clause1(root); rows.append(("P3 log.blockMesh has NO End", False, ok))

# ---- P4: record.json WRITTEN, THEN the driver dies ----------------------
# The supervisor's second planted case.  record.json and the preludes are all fine;
# the solver log is truncated.  Clause 1 CANNOT see this -- and that is the point.
root = m._synthetic_run(os.path.join(tmp, "P4_died_after_record"))
p = os.path.join(root, "case", "log.pimpleFoam")
txt = open(p).read().replace("\nEnd\n", "\n")
open(p, "w").write(txt)
ok, _ = clause1(root)
comp = m.check_completion(root)
caught = [n for n, _, o, _ in comp.clauses if not o]
rows.append(("P4 record.json OK, solver died after it", None, ok))

print("=" * 78)
print("PLANTED CONTROL -- can the rc PROXY see a non-zero?")
print("=" * 78)
allgood = True
for label, want, got in rows:
    if want is None:
        print("  %-42s clause1=%-5s  (see note below)" % (label, got)); continue
    verdict = "OK" if got == want else "*** DID NOT FIRE ***"
    if got != want: allgood = False
    print("  %-42s clause1=%-5s expected %-5s  %s" % (label, got, want, verdict))
print()
print("P4 NOTE: clause 1 PASSES on a run that wrote record.json and then died.")
print("  The proxy shows the driver REACHED ITS FINAL WRITE, not that it EXITED CLEANLY.")
print("  The conjunctive rule caught it anyway -- failing clauses: %s" % caught)
print()
print("P1 detail, the independent half of the proxy, verbatim from the frozen reader:")
for line in d1.splitlines(): print("    " + line)
shutil.rmtree(tmp, ignore_errors=True)
print()
print("RESULT: %s" % ("PROXY SHOWN ABLE TO SEE A FAILURE on every arm it claims to cover"
                     if allgood else "PROXY FAILED TO FIRE -- ground 2 bites, row is NOT A RESULT"))
sys.exit(0 if allgood else 2)
