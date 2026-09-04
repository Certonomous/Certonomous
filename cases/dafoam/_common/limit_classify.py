#!/usr/bin/env python3
"""Classify every registered budget limit under cases/dafoam as
ENFORCED / ENFORCED-WATCHER / REPORTS ONLY / DEAD.

    usage:  python3 cases/dafoam/_common/limit_classify.py [dump_path]
            (run from the repository root; ROOT below is repo-relative)

WHY THIS EXISTS
---------------
SO3aF2 registered an item ceiling of 9.0 core-min at
`ladder-a/A1/feasibility_SO3a_multipoint/so3af2_run_arm.sh:131`, echoed it into
every ledger row at `:517`, and compared it to NOTHING anywhere in its case
directory.  The item spent 9.2833 core-min -- 3.15 % over -- and nothing noticed,
because nothing could.  The item's own record names the defect at
`FEASIBILITY_PREREGISTRATION.md` sections A16.5 and A17.3.  That is CLAUDE.md
rule 14's shape ("a lesson is not applied until EVERY call site asserts it") and
this family's "dead lever" class: a registered number that is written, displayed,
and read by nothing.

This instrument answers the POPULATION question -- how many such levers exist --
rather than the one-item question.  First full sweep, 2026-09-04:

    735 script files scanned;  377 registered budget limits in 181 files
      ENFORCED           164   prospective guard, or a timeout/--memory/ulimit
                               runtime sink; fires with no agent alive
      ENFORCED-WATCHER    41   concurrent host poll loop -> `docker stop`;
                               STOPS the run, but only while the host process
                               lives.  This family has MEASURED one failing to
                               fire (so3af2_run_arm.sh:115-120).
      REPORTS ONLY       161   reaches a print/log/ledger/verdict field, or a
                               comparison with no abort, or a comparison after
                               the last irreversible step
      DEAD                11   assigned and never read at all

    Not counted as limits: 28 dead FLAG assignments (`CEILING_HIT=yes` in 25
    launchers) -- dead variables, but the branch they sit on does issue
    `docker stop`, so they are cosmetic, not dead levers; and 7 `sed` lines
    inside pin-selftests that poison a COPY of a launcher.

THE THREE READER DEFECTS THIS REFUSED ON, AND WHY THEY MATTER TO YOUR VERSION
-----------------------------------------------------------------------------
The planted controls below made this classifier refuse three times before any
number it printed was worth reading.  Each refusal was a genuine blindness, and
each is a failure mode the NEXT person's classifier will have too:

  1. CASE-ARM INVISIBILITY.  Shell assigns mid-line -- `MESH) CAP="$CAP_MESH" ;;`
     inside a `case`, after `;`, `&&`, `then`, `do`.  An assignment regex anchored
     at `^` cannot see them, and the known-ENFORCED control came back ABSENT.
  2. MISSING TRANSITIVE DEF-USE.  A limit can reach enforcement only THROUGH a
     derived variable: SO3aF2's CAP -> DEADLINE_S (`:272`) -> `timeout -k
     $KILL_AFTER $DEADLINE_S` (`:480`).  Without a def-use graph the live guard
     read as a report.
  3. FILENAME-MENTION LAUNCH DETECTION.  A loose "irreversible step" regex matched
     an md5 comment NAMING `so3af2_runScript.py` and treated it as a launch, which
     pushed real pre-launch guards past the post-hoc line and demoted them.

A fourth correction came from hand-verification rather than a control, and is
worth the same warning: `return 9` is this family's refusal idiom inside
`run_stage()`.  An abort vocabulary without it hides real prospective guards
(`d12r_stage_and_run.sh:192-194` CAP_CORE_MIN, `:196-198` CAP_S8).

A CLASSIFIER THAT HAS ONLY EVER PRINTED "DEAD" IS NOT EVIDENCE THAT A LIMIT IS
DEAD (CLAUDE.md rule 3).  The four planted controls below and the `exit 2`
refusal are the reason these numbers are worth anything.  DO NOT STRIP THEM: a
successor without them has a classifier that cannot be caught being wrong.

STATED LIMITS OF THIS INSTRUMENT -- read before quoting any count
-----------------------------------------------------------------
  * INTRA-FILE def-use only.  This is regex plus a per-file def-use graph, NOT an
    interpreter.  It cannot see CROSS-FILE enforcement -- a limit exported by a
    driver and enforced in the launcher it calls.  Therefore ENFORCED is a LOWER
    bound and REPORTS ONLY an UPPER bound.  DEAD is the robust class: each DEAD
    row is a sole textual occurrence in its own file.
  * On the 2026-09-04 sweep, 57 REPORTS ONLY sites carried a comparison (the
    false-negative risk set).  52 are `*_grade.py` graders, where a post-hoc
    report is the CORRECT classification.  The 5 that are not graders were
    classified BY NAME AND NOT READ: so2a/so3a/so3ar/so3ar2_groot5_selftest.sh
    (CAPSUM, GCEIL), maaoa_chain_driver.sh (LOOP_BOUND_S), so3_run_arm.sh
    (CAP_MIN_TMO_S), d14m_driver.sh (CAP_CORE_MIN), d6ra2_guard_selftest.py
    (REGISTERED_CAP).
  * WATCHER SURVIVAL WAS ESTABLISHED FOR 1 OF 41.  Only D6's driver was checked
    for detachment (`d6_run_arm.sh:337-339` cites a setsid nohup driver).  The
    other 40 are unverified, and this is the class to trust least.
  * Never use a multi-file grep reduction to check any of this.  `grep` on this
    box is a shell function over ugrep and emits per-file as parallel workers
    finish, so `grep ... | head`/`tail` has NO defined ordering.  This
    instrument reads every file individually, and so should its successor.

THE REPAIR TEMPLATE, for whoever acts on the output
---------------------------------------------------
`ladder-a/A2/curriculum_D6RF/d6rf_chain_driver.sh:155-170` is the only correct
cumulative item-ceiling guard in the family (with its D6RF2 twin): sum ledger
spend, add THIS arm's cap, refuse BEFORE the arm if the projection crosses the
ceiling.  Its own comment states the mechanism: "a per-arm cap alone cannot see
an item walking past its own ceiling one arm at a time."  On 2026-09-04, 2 of 42
chain drivers carried it.

Provenance: dafoam lab-lane for dafoam-supervisor, 2026-09-04.  Zero compute.
"""
import os, re, sys, json, collections

ROOT = 'cases/dafoam'
DEFAULT_DUMP = 'limit_classify_dump.txt'

# ---------------------------------------------------------------------------
# The limit vocabulary was DERIVED FROM THE FILES, not from a brief: an
# assignment scan over all 735 scripts returned 185 candidate identifiers, then
# narrowed to names that bound a RESOURCE (compute spend, wall/deadline, memory,
# poll bounds, iteration caps).  EXCLUDE removes statistical/physics floors
# (SIGN_FLOOR, PLANT_FLOOR_REL, HARNESS_FLOOR_LO, noise_floor) and plotting
# artefacts (capstyle, xlimits, CAPTIONS), which are not budget limits.
# ---------------------------------------------------------------------------
INCLUDE = re.compile(r'''(
 ^CAP(_|$)|(_|^)CAP$|CAP_CORE_MIN|CAP_S8|CAP_WALL_S|CAP_SUM|CAPSUM|CAP_MARGIN_S|CAP_MIN_TMO_S|CAP_KILL_GRACE_S|
 CEILING|CEIL_REG|GCEIL|RSS_CEIL|CEILINGS|
 MEM_LIMIT|MEM_CAP|MEMCAP|MEM_FLOOR|MEMAVAIL_FLOOR|H5_FLOOR_GIB|HOST_FLOOR|HARD_FLOOR_KIB|FLOOR_KB|MEM_NEED_GB|AGG_CEILING_GIB|
 DEADLINE|TIMEOUT|KILL_AFTER|POLL_BOUND_S|LOOP_BOUND_S|MEM_WAIT_BOUND_S|AGG_WAIT_MAX_S|MEM_POLL_S|
 MAX_ITER|MAXITER|ENDTIME_CAP|
 BUDGET_FACTOR|ITEM_CAP_MIN|ARM_CAP|REGISTERED_CAP|REG_CAPS|SOLVER_CORE_MIN_CAP|
 COST_CEILING|COST_PER_START_CEILING|CAP_BYTES|CAP_TO_TMO|CAP_FIXTURE|CAP_EXITS
)''', re.X)
EXCLUDE = re.compile(r'capture|caption|capstyle|xlimit|escape|CAPTURE_FMT|CAPLINE|CAP_ROW|CAPL$|CAPS$|^caps$|'
                     r'^cap_stopped|^capstop|^capfail|^capped|^hit_cap|^below_cap|^row_capped|^rCAP$|^oCAP$|^ACAP$|'
                     r'CREASE|REVEAL|NEAR_CAP|WALL_CAP', re.I)

# Flags hold yes/no, not a budget value.  Counting them as limits inflated the
# DEAD class by 28 (CEILING_HIT in 25 launchers) -- and the branch those sit on
# DOES issue `docker stop`, so calling them dead levers would be an over-claim.
FLAG = re.compile(r'CEILING_HIT|CAP_REPORTED|CEILING_REASON|VERDICT_CEILING|CAP_EXITS|CAP_FIXTURE|CAP_TO_TMO')

# A pin-selftest POISONS a limit inside a COPY of a launcher, to prove the guard
# fires (so3af2_pin_selftest.sh:233-234 sets MEM_FLOOR_GIB=999999.0 and
# POLL_BOUND_S=0).  That is a planted control in the lab's own code and is the
# right pattern -- but the `sed` expression is not itself a registered limit, and
# counting it inflates DEAD by 4 and ENFORCED by 3.
SEDLINE = re.compile(r'\bsed\b|^\s*-e\s')

# READER DEFECT 1: shell assigns mid-line -- inside a `case` arm, after `;`,
# `&&`, `then`, `do`.  Anchoring at ^ made the known-ENFORCED control ABSENT.
ASSIGN_SH = re.compile(r'(?:^|[;&|)]|\bthen\b|\bdo\b|\belse\b)\s*'
                       r'(?:export\s+|local\s+|readonly\s+|declare\s+-\w+\s+)?'
                       r'([A-Za-z_][A-Za-z0-9_]*)=(?!=)')
ASSIGN_PY = re.compile(r'(?:^|[;:]|\bglobal\b)\s*([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*[^=]+)?=\s*[^=]')

CMP_OPS_SH = re.compile(r'-gt\b|-lt\b|-ge\b|-le\b|-eq\b|-ne\b|[<>]=?|==|!=')
# `return 9` is this family's refusal idiom inside run_stage(); omitting it hid
# real prospective guards (d12r_stage_and_run.sh:192-194, :196-198).
# "NOT LAUNCHED" / "BLOCKED" is the same refusal written as prose.
ABORT_SH = re.compile(r'\bexit\s+[1-9]|\bexit\s+"?\$|nolaunch|\bdie\b|ABORT|\brefuse|REFUSE|'
                      r'\bfail\b.*exit|exit\s*\$\{?rc|\breturn\s+[1-9]|NOT[ _]LAUNCHED|\bBLOCKED\b')
ABORT_PY = re.compile(r'sys\.exit\s*\(\s*[^0)]|raise\b|SystemExit|os\._exit\s*\(\s*[^0)]|REFUSE|exit\(2\)|exit\(1\)')
PRINT_SH = re.compile(r'^\s*(echo|printf)\b|\becho\b|\bprintf\b|>>\s*"?\$')
PRINT_PY = re.compile(r'\bprint\s*\(|\.write\s*\(|f"|f\'|\.format\(|json\.dump')

# READER DEFECT 3: the irreversible step is an actual container or solver
# INVOCATION.  Kept tight -- a mere filename mention (an md5 comment naming
# so3af2_runScript.py) is NOT a launch, and treating it as one demoted real
# guards into REPORTS ONLY.  The planted ENFORCED control caught exactly that.
LAUNCH = re.compile(r'\bdocker\s+(run|start|exec|wait)\b|\bmpirun\b|\bmpiexec\b|'
                    r'subprocess\.(run|Popen|call|check_call)\s*\(|'
                    r'\b(simpleFoam|pimpleFoam|buoyantSimpleFoam|rhoSimpleFoam|snappyHexMesh|blockMesh|decomposePar)\b\s*(-|>|\||;|$|")|'
                    r'os\.system\s*\(|\bsetsid\s+\S|\bnohup\s+\S|\bsbatch\b|'
                    r'(bash|python3?|mpirun)\s+\S*runScript')

# A watcher branch that STOPS the container.  Distinguishing this from a
# post-completion check is the whole point: collapsing it into REPORTS ONLY
# mislabels 38 live ceilings; collapsing the other way IS the SO3aF2 defect.
STOPRX = re.compile(r'docker\s+(stop|kill)\b|\bkill\s+-?\w*\s*\$|\bpkill\b|\.terminate\(|\.kill\(')

RUNTIME_SINK_TMPL = (
    r'\btimeout\b[^|]*\$\{{?{v}\b', r'--memory(-swap)?=\$?\{{?{v}\b', r'--cpus=\$?\{{?{v}\b',
    r'\bulimit\b.*\$\{{?{v}\b', r'-k\s+\$\{{?{v}\b', r'timeout\s*=\s*{v}\b',
    r'signal\.alarm\s*\(\s*{v}\b',
)


def strip_comment(line):
    """Drop a trailing shell comment; a '#' inside quotes is not a comment."""
    q = None
    out = []
    for ch in line:
        if q:
            out.append(ch)
            if ch == q:
                q = None
            continue
        if ch in '"\'':
            q = ch
            out.append(ch)
            continue
        if ch == '#':
            break
        out.append(ch)
    return ''.join(out)


def is_runtime_sink(line, var):
    return any(re.search(t.format(v=re.escape(var)), line) for t in RUNTIME_SINK_TMPL)


def files_under(root):
    out = []
    for d, dn, fn in os.walk(root):
        dn[:] = [x for x in dn if x != '__pycache__']
        for f in fn:
            if f.endswith(('.sh', '.py', '.bash')):
                out.append(os.path.join(d, f))
    return sorted(out)


def analyse(path, lines, py):
    """Return {limit_name: record} for every budget limit assigned in this file."""
    rx = ASSIGN_PY if py else ASSIGN_SH

    assign = collections.defaultdict(list)
    for i, l in enumerate(lines, 1):
        if l.lstrip().startswith('#'):
            continue
        for m in rx.finditer(l):
            n = m.group(1)
            if EXCLUDE.search(n) or not INCLUDE.search(n):
                continue
            if (i, l.rstrip()) not in assign[n]:
                assign[n].append((i, l.rstrip()))
    if not assign:
        return {}

    launch_lines = [i for i, l in enumerate(lines, 1)
                    if not l.lstrip().startswith('#') and LAUNCH.search(strip_comment(l))]

    # READER DEFECT 2: def-use graph over ALL variables, so a limit that reaches
    # enforcement THROUGH a derived variable (CAP -> DEADLINE_S -> `timeout`) is
    # not miscounted as a report.  The planted ENFORCED control proved this gap.
    defuse = collections.defaultdict(set)
    for i, l in enumerate(lines, 1):
        if l.lstrip().startswith('#'):
            continue
        for m in rx.finditer(l):
            v = m.group(1)
            rhs = l[m.end():]
            if py:
                defuse[v].update(re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', rhs))
            else:
                defuse[v].update(re.findall(r'\$\{?([A-Za-z_][A-Za-z0-9_]*)', rhs))
                # `awk -v x="$Y"` carries Y into the awk program
                defuse[v].update(re.findall(r'-v\s+\w+\s*=\s*"?\$\{?([A-Za-z_][A-Za-z0-9_]*)', rhs))

    out = {}
    for n, asites in assign.items():
        assign_ln = {i for i, _ in asites}
        if py:
            pat = re.compile(r'\b' + re.escape(n) + r'\b')
        else:
            pat = re.compile(r'\$\{?' + re.escape(n) + r'\b|\bv?\s*' + re.escape(n) + r'=\s*"\$')

        reads = []
        for i, l in enumerate(lines, 1):
            if l.lstrip().startswith('#'):
                continue
            code = l
            if i in assign_ln:
                # a self-reference on its own assignment line is a read; the LHS is not
                rhs = l.split('=', 1)[1] if '=' in l else ''
                if not pat.search(rhs):
                    continue
                code = rhs
            if not pat.search(code):
                continue
            reads.append((i, l.rstrip()))

        if not reads:
            out[n] = dict(cls='DEAD', assigns=asites, reads=[], cmp=[], abort=[],
                          runtime=[], via=[], watcher=[], post_hoc=False, launches=launch_lines)
            continue

        cmps, prints = [], []
        for (i, l) in reads:
            is_cmp = False
            if py:
                if re.search(r'^\s*(if|elif|while|assert)\b', l) and CMP_OPS_SH.search(l):
                    is_cmp = True
                if re.search(re.escape(n) + r'\s*(<|>|<=|>=|==|!=)', l) or \
                   re.search(r'(<|>|<=|>=|==|!=)\s*' + re.escape(n), l):
                    is_cmp = True
            else:
                if (re.search(r'\[\[?.*\$\{?' + re.escape(n), l) or re.search(r'^\s*(if|while|until)\b', l)) \
                        and CMP_OPS_SH.search(l):
                    is_cmp = True
                if re.search(r'\btest\b.*\$\{?' + re.escape(n), l) and CMP_OPS_SH.search(l):
                    is_cmp = True
                if 'awk' in l and re.search(r'-v\s+\w+\s*=\s*"?\$\{?' + re.escape(n), l) \
                        and CMP_OPS_SH.search(l):
                    is_cmp = True
                if re.search(r'\(\(.*\$?\{?' + re.escape(n), l) and CMP_OPS_SH.search(l):
                    is_cmp = True
            if is_cmp:
                cmps.append((i, l))
            if (PRINT_PY if py else PRINT_SH).search(l):
                prints.append((i, l))

        AB = ABORT_PY if py else ABORT_SH
        aborts = []
        for (i, _l) in cmps:
            for j in range(i, min(i + 9, len(lines) + 1)):
                if AB.search(lines[j - 1]):
                    aborts.append((i, j, lines[j - 1].rstrip()))
                    break

        # A limit consumed by `timeout N`, `--memory=`, `--cpus=`, `ulimit` is
        # enforced by the OS/runtime even with no in-script comparison, and is
        # prospective by construction.
        runtime_enf = [(i, l) for (i, l) in reads if is_runtime_sink(l, n)]

        # Transitive: does this limit flow into a variable that is itself enforced?
        via = []
        seen, frontier = {n}, [n]
        while frontier:
            cur = frontier.pop()
            for v, srcs in defuse.items():
                if cur in srcs and v not in seen:
                    seen.add(v)
                    frontier.append(v)
        for v in sorted(seen - {n}):
            vpat = (re.compile(r'\b' + re.escape(v) + r'\b') if py
                    else re.compile(r'\$\{?' + re.escape(v) + r'\b'))
            for i, l in enumerate(lines, 1):
                if l.lstrip().startswith('#') or not vpat.search(l):
                    continue
                if is_runtime_sink(l, v):
                    via.append((v, i, l.strip()[:180]))
                elif CMP_OPS_SH.search(l) and re.search(r'^\s*(if|while|until|\[|assert|elif)', l.lstrip()):
                    for j in range(i, min(i + 9, len(lines) + 1)):
                        if AB.search(lines[j - 1]):
                            if not launch_lines or any(L >= i for L in launch_lines):
                                via.append((v, i, lines[j - 1].strip()[:180]))
                            break

        # A concurrent watcher: the comparison's branch STOPS the container.
        watcher = []
        for ci, _l in cmps:
            for j in range(ci, min(ci + 9, len(lines) + 1)):
                if STOPRX.search(lines[j - 1]):
                    watcher.append((ci, j, lines[j - 1].strip()[:180]))
                    break

        # A guard is PROSPECTIVE if some irreversible step still lies AHEAD of it
        # -- not merely if it precedes the FIRST one.  Shell defines functions in
        # text order but runs the guard inside run_stage() ahead of that function's
        # own `docker run`; testing against the first launch anywhere in the file
        # called those live guards reports (d12x/d12y_stage_and_run.sh).
        post_hoc = False
        if aborts and not runtime_enf and not watcher and launch_lines:
            if all(not any(L >= ci for L in launch_lines) for ci, _, _ in aborts):
                post_hoc = True

        if runtime_enf or via or (aborts and not post_hoc):
            cls = 'ENFORCED'
        elif watcher:
            cls = 'ENFORCED-WATCHER'
        else:
            cls = 'REPORTS ONLY'

        out[n] = dict(cls=cls, assigns=asites, reads=reads, cmp=cmps, abort=aborts,
                      runtime=runtime_enf, via=via, watcher=watcher,
                      post_hoc=post_hoc, launches=launch_lines)
    return out


def sweep():
    results = {}
    for p in files_under(ROOT):
        try:
            lines = open(p, errors='replace').read().split('\n')
        except Exception:
            continue
        for n, rec in analyse(p, lines, p.endswith('.py')).items():
            results[(p, n)] = rec
    return results


def controls(results):
    """CLAUDE.md rule 3.  Four planted controls; the classifier REFUSES unless all
    four hold.  Two are real limits whose class is known from hand-reading; two
    are synthetic plants inserted into real bytes, so the DEAD and ENFORCED
    branches are each shown REACHABLE rather than merely never taken."""
    src = 'cases/dafoam/ladder-a/A1/feasibility_SO3a_multipoint/so3af2_run_arm.sh'
    checks = []

    # (a) known ENFORCED: CAP is assigned in a `case` arm and reaches enforcement
    #     only transitively, via DEADLINE_S -> `timeout` inside the container.
    #     Defects 1 and 2 each made this control fail.
    checks.append(('CAP in so3af2_run_arm.sh', 'ENFORCED',
                   results.get((src, 'CAP'), {}).get('cls', 'ABSENT')))
    # (b) known REPORTS ONLY: the 9.0 ceiling reaches the ledger row at :517 and
    #     no comparison anywhere.  NOTE it is REPORTS ONLY, not DEAD -- displayed
    #     is a read, and 11 limits in this corpus are genuinely worse.
    checks.append(('CEILING in so3af2_run_arm.sh', 'REPORTS ONLY',
                   results.get((src, 'CEILING'), {}).get('cls', 'ABSENT')))

    base = open(src, errors='replace').read().split('\n')
    # (c) synthetic DEAD: assigned into real bytes, read by nothing.
    dead_lines = list(base)
    dead_lines.insert(140, 'PLANTED_DEAD_CAP_CORE_MIN=1.234')
    checks.append(('PLANTED_DEAD_CAP_CORE_MIN (synthetic)', 'DEAD',
                   analyse(src + '#PLANT-DEAD', dead_lines, False)
                   .get('PLANTED_DEAD_CAP_CORE_MIN', {}).get('cls', 'ABSENT')))
    # (d) synthetic ENFORCED: the same plant given one comparison and one exit.
    live_lines = list(dead_lines)
    live_lines.insert(141, 'PLANTED_LIVE_CAP_CORE_MIN=2.5')
    live_lines.insert(142, '[ "$(awk -v a=1 -v b="$PLANTED_LIVE_CAP_CORE_MIN" '
                           '\'BEGIN{print (a<b)?1:0}\')" = 1 ] || exit 9')
    checks.append(('PLANTED_LIVE_CAP_CORE_MIN (synthetic)', 'ENFORCED',
                   analyse(src + '#PLANT-LIVE', live_lines, False)
                   .get('PLANTED_LIVE_CAP_CORE_MIN', {}).get('cls', 'ABSENT')))

    ok = True
    for name, want, got in checks:
        print(f"CONTROL  {name}: want={want} got={got}", file=sys.stderr)
        if got != want:
            ok = False
    return ok


def main():
    dump_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_DUMP
    if not os.path.isdir(ROOT):
        print(f"REFUSE: {ROOT} not found -- run from the repository root", file=sys.stderr)
        sys.exit(2)

    results = sweep()

    if not controls(results):
        print("CONTROL FAILED -- classifier REFUSES (CLAUDE.md rule 3).  A zero from a "
              "reader not shown able to see a non-zero is not evidence.", file=sys.stderr)
        sys.exit(2)

    # Flags are not limits, and neither is a selftest's `sed` poison line.
    # Report both separately rather than inflating DEAD.
    def is_sed(rec):
        return bool(rec['assigns']) and all(SEDLINE.search(l) for _, l in rec['assigns'])

    limits, flags, sed_lines = {}, {}, {}
    for k, v in results.items():
        if FLAG.search(k[1]):
            flags[k] = v
        elif is_sed(v):
            sed_lines[k] = v
        else:
            limits[k] = v

    counts = collections.Counter(v['cls'] for v in limits.values())
    risk = [k for k, v in limits.items() if v['cls'] == 'REPORTS ONLY' and v['cmp']]
    print(json.dumps({
        'registered_budget_limits': len(limits),
        'files': len({p for p, _ in limits}),
        'counts': dict(counts),
        'flag_sites_excluded': len(flags),
        'selftest_sed_sites_excluded': len(sed_lines),
        'false_negative_risk_set': len(risk),
        'note': 'ENFORCED is a LOWER bound and REPORTS ONLY an UPPER bound: '
                'intra-file def-use only, no cross-file flows.',
    }, indent=1))

    with open(dump_path, 'w') as fh:
        for (p, n), v in sorted(limits.items()):
            fh.write(f"=== {p} :: {n} :: {v['cls']}\n")
            for i, l in v['assigns']:
                fh.write(f"  ASSIGN {i}: {l[:200]}\n")
            for i, l in v['cmp']:
                fh.write(f"  CMP    {i}: {l.strip()[:200]}\n")
            for ci, ai, l in v['abort']:
                fh.write(f"  ABORT  cmp{ci}->{ai}: {l.strip()[:200]}\n")
            for i, l in v['runtime']:
                fh.write(f"  RUNTIME {i}: {l.strip()[:200]}\n")
            for ci, ai, l in v['watcher'][:3]:
                fh.write(f"  WATCHSTOP cmp{ci}->{ai}: {l}\n")
            for vv, i, l in v['via'][:4]:
                fh.write(f"  VIA {vv} @{i}: {l}\n")
            if v['cls'] == 'REPORTS ONLY':
                for i, l in v['reads'][:6]:
                    fh.write(f"  READ   {i}: {l.strip()[:200]}\n")
    print(f"dump: {dump_path}  (regenerated on demand; not committed)", file=sys.stderr)


if __name__ == '__main__':
    main()
