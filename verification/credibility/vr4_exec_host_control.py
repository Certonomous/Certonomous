#!/usr/bin/env python3
"""VR4 -- the exec_host control: EXEC must be NOT MEASURED across hosts.

Frozen gate: verification/campaign/VR4_PREREGISTRATION.md, commit ffe5ded7.
The code change to scripts/queue_entry_check.py is cfd's; this is the SPEC's
control, written first so their repair has something to be checked against.
"""
import os, socket, sys, json, tempfile

LOCAL = socket.gethostname()

def exec_verdict(entry, local=LOCAL):
    """The specified behaviour. G1: across hosts the clause is NOT MEASURED."""
    cwd = entry.get('cwd')
    host = entry.get('exec_host') or entry.get('host')
    if host and host != local:
        return ('NOT MEASURED',
                "EXEC not evaluated: entry executes on %r, this validator ran on %r; "
                "a path that resolves here is not a statement about there (L-394)" % (host, local))
    if not cwd or not os.path.isdir(cwd):
        return ('REFUSE', "EXEC: cwd %r does not exist on %s, the executing host" % (cwd, local))
    return ('PASS', "EXEC: cwd exists on %s, the executing host" % local)

def main():
    print("VR4 -- exec_host control (frozen: VR4_PREREGISTRATION.md @ ffe5ded7)")
    fails = []
    d = tempfile.mkdtemp(prefix='vr4_')
    # G3 limb 1: local host, ABSENT cwd -> must still REFUSE (EXEC retained where meaningful)
    v, _ = exec_verdict({'cwd': os.path.join(d, 'nope'), 'exec_host': LOCAL})
    if v != 'REFUSE': fails.append("G3a: local+absent cwd gave %s, wanted REFUSE" % v)
    # G3 limb 2: remote host, PRESENT cwd -> must be NOT MEASURED, never PASS
    v, _ = exec_verdict({'cwd': d, 'exec_host': 'ip-172-31-44-162'})
    if v != 'NOT MEASURED': fails.append("G3b: remote+present cwd gave %s, wanted NOT MEASURED" % v)
    # local host, present cwd -> PASS
    v, _ = exec_verdict({'cwd': d, 'exec_host': LOCAL})
    if v != 'PASS': fails.append("G3c: local+present cwd gave %s, wanted PASS" % v)
    for f in fails: print("  " + f)
    if fails:
        print("VERDICT: GATE FAIL -- %d control limb(s) misbehaved" % len(fails))
        return 1
    print("  control: local/absent REFUSE, remote/present NOT MEASURED, local/present PASS")
    # G4 -- the two live GPU entries, re-validated under the spec
    print("  G4 -- live GPU entries under the spec:")
    n = 0
    for f in ('VMFLGPU001.json', 'VMFLGPU001-R2.json'):
        p = os.path.join('verification/queue/ansys-verification/held', f)
        if not os.path.isfile(p): continue
        e = json.load(open(p)); v, why = exec_verdict(e); n += 1
        print("    %-22s %-12s %s" % (e.get('case_id'), v, why))
    if n == 0:
        print("VERDICT: NOT A RESULT -- G4 read no live entry")
        return 2
    print("VERDICT: PASS -- all control limbs behaved and %d live entr(y/ies) classified" % n)
    return 0

if __name__ == '__main__':
    sys.exit(main())
