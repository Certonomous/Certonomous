# Independent control on the P3 fatal clause. GRADES NOTHING.
import re
from pathlib import Path
PAT = re.compile(r"FOAM FATAL|Floating point exception|signal")
roots = [Path("/home/ubuntu/certonomous-runs"), Path("/home/ubuntu/Certonomous/verification/runs"),
         Path("/home/ubuntu/closure-data")]
logs = []
for r in roots:
    if r.is_dir():
        logs += list(r.rglob("log.run"))[:300]
logs = logs[:300]
fired = notfired = ended_and_fired = banner_only = 0
nf = []
for p in logs:
    try:
        sz = p.stat().st_size
        with p.open("rb") as fh:
            head = fh.read(65536).decode("utf-8", "replace")
            if sz > 131072:
                fh.seek(-65536, 2); tail = fh.read().decode("utf-8", "replace")
            else:
                tail = ""
    except Exception:
        continue
    t = head + "\n" + tail
    lines = [ln for ln in t.split("\n") if PAT.search(ln)]
    ended = bool(re.search(r"(?m)^End\s*$", t))
    if lines:
        fired += 1
        if ended: ended_and_fired += 1
        if all(("trapping enabled" in ln) or ("trapFpe" in ln) for ln in lines): banner_only += 1
    else:
        notfired += 1
        if len(nf) < 3: nf.append(str(p))
print("logs examined (head+tail 64KB each)      : %d" % len(logs))
print("clause FIRED (reports fatal)             : %d" % fired)
print("clause did NOT fire                      : %d" % notfired)
print("FIRED *and* log carries a clean End line : %d" % ended_and_fired)
print("FIRED where EVERY hit is the trapFpe banner: %d" % banner_only)
print("did-not-fire examples: %r" % nf)
