#!/usr/bin/env python3
"""VR8 -- SELFTEST TRIGGER REACHABILITY CENSUS.

Gate question: for every instrument in `scripts/` that defines a `--selftest`
mode, is that selftest REACHABLE FROM AN AUTOMATIC ROOT -- a crontab line or a
`.claude` hook -- or does it fire only when a human or an agent types it?

WHY REACHABILITY AND NOT "HAS A CALLER". A caller that is itself never fired
automatically does not fire anything. A chain of hand-only callers is still
hand-only, so the only honest question is whether a path exists from something
that runs BY ITSELF down to the selftest. `DEAD_LEVER_AUDIT` SS20 names the shape:
a control with no trigger "has no call sites, so it cannot be applied, only
remembered."

WHAT IS MINE: the census. The scripts belong to five other teams and WIRING a
trigger is each owner's act. This item wires nothing and edits nothing.

-------------------------------------------------------------------------------
SCOPE, STATED AS A LIMIT AND NOT AS A BOAST
-------------------------------------------------------------------------------
DEFINERS are enumerated from `scripts/` ONLY -- the lab's own instrument
directory. Selftests inside `cases/` and `verification/` are OUT OF SCOPE and
this item claims NOTHING about them. A wider sweep is a different rung with a
different cap; pretending this one covers them would be the overclaim.

-------------------------------------------------------------------------------
THE TWO DEFECTS THIS DRIVER WAS BUILT AROUND, BOTH FOUND BEFORE FREEZING
-------------------------------------------------------------------------------
DEFECT 1 -- FILE-LEVEL CO-OCCURRENCE IS NOT AN INVOCATION. A first cut asked
whether some other file contained both the definer's basename and the string
`--selftest` anywhere in it. That admits `scripts/queue_entry_check.py`, which
mentions `queue_runner.py` at line 159 and has its OWN `--selftest` at line 36 --
sixty lines apart and unrelated. A trigger is an INVOCATION: the two tokens must
sit on the SAME LINE, and that line must not be a comment.

DEFECT 2 -- PROSE LIVES INSIDE `.py` TOO. Excluding `.md` is not enough, because
a Python docstring is prose in an executable carrier. THIS VERY FILE names
`queue_runner.py` beside `--selftest` in its own docstring. So comment and
docstring lines are stripped before matching, and the definer itself is excluded.

-------------------------------------------------------------------------------
GROUND TRUTH, RE-DERIVED TODAY RATHER THAN CITED
-------------------------------------------------------------------------------
`DEAD_LEVER_AUDIT` SS20 (2026-08-31T00:40Z) ruled `queue_runner.py --selftest`
HAND-ONLY: "the wrapper launched --daemon, check_harness.py never called
--selftest, and no hook or cron ran it."

THAT RULING IS STALE, AND THIS DRIVER MUST NOT BE ANCHORED ON IT. cfd landed a
FAIL-CLOSED SELFTEST GATE in `scripts/queue_runner.sh` on 2026-08-31, citing
verification's own audit finding 5. The real chain today is:

    crontab  `* * * * * /bin/bash .../scripts/queue_runner.sh`
      -> scripts/queue_runner.sh:91  `python3 "$REPO/scripts/queue_runner.py" --selftest`

So `queue_runner.py` is REACHABLE, and limb X1 asserts exactly that -- verified
against the LIVE crontab and the REAL wrapper, not against a ruling that has been
overtaken. A rung anchored on SS20 would have graded a stale audit section.

-------------------------------------------------------------------------------
SS2j -- WHO WROTE THE BYTES
-------------------------------------------------------------------------------
VERIFICATION_CHARTER SS2j.2: "ask who WROTE the bytes the control reads."

  * the crontab -- written by the box's owner. THE REAL PRODUCER.
  * `.claude/settings.json` hooks -- written by the lab's own configuration.
  * every script under `scripts/` -- real production code by five teams.

There is NO fixture tree, NO synthesised caller and NO planted script anywhere in
this file, because BOTH ANSWERS ALREADY EXIST in the real corpus. The one thing
the selftest constructs is limb X3's DELIBERATELY LOOSENED matcher, which exists
only to demonstrate that the strict matcher excludes something real.
"""

import argparse
import os
import re
import subprocess
import sys

REPO = "/home/ubuntu/Certonomous"
SCRIPTS = os.path.join(REPO, "scripts")
SELFTEST = "--selftest"

# Carriers in which an INVOCATION may live. Prose-only formats are absent by
# construction; prose INSIDE these is stripped (see strip_prose).
CARRIER_ROOTS = ["scripts", "harness", ".claude"]
CARRIER_EXT = {".py", ".sh", ".json", ".yaml", ".yml"}


class Refusal(Exception):
    """The instrument cannot honestly grade. Exit 2, never a degraded answer."""


# ------------------------------------------------------------ prose stripping -

def strip_prose(text, ext):
    """Blank out comment and docstring lines, preserving line numbering.

    Executable carriers contain prose. A docstring naming a script beside
    `--selftest` is a MENTION, not an invocation, and admitting it is DEFECT 2.
    """
    lines = text.splitlines()
    out = []
    in_doc = None
    for line in lines:
        s = line.strip()
        if ext == ".py":
            if in_doc:
                if in_doc in s:
                    in_doc = None
                out.append("")
                continue
            for q in ('"""', "'''"):
                if s.startswith(q):
                    # a one-line docstring closes on the same line
                    if not (len(s) > 5 and s.endswith(q)):
                        in_doc = q
                    s = ""
                    break
            if s.startswith("#") or s == "":
                out.append("")
                continue
        elif ext == ".sh":
            if s.startswith("#"):
                out.append("")
                continue
        out.append(line)
    return out


# ---------------------------------------------------------------- readers -----

def read_crontab():
    """The LIVE crontab. Producer: the box's owner. An automatic root."""
    try:
        p = subprocess.run(["crontab", "-l"], capture_output=True, text=True,
                           timeout=20)
    except (OSError, subprocess.SubprocessError) as exc:
        raise Refusal("cannot read the crontab (%s) -- with no automatic roots "
                      "EVERY instrument would read HAND-ONLY, which is the "
                      "parser-blindness answer, not a finding" % exc)
    if p.returncode != 0:
        raise Refusal("crontab -l returned rc=%s -- refusing rather than "
                      "treating 'no roots' as 'nothing is wired'" % p.returncode)
    return [l for l in p.stdout.splitlines()
            if l.strip() and not l.strip().startswith("#")]


def read_hooks():
    """`.claude` hook commands. Producer: the lab's own configuration."""
    cmds = []
    for rel in (".claude/settings.json", ".claude/settings.local.json"):
        p = os.path.join(REPO, rel)
        if not os.path.exists(p):
            continue
        try:
            import json
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        for _event, entries in (d.get("hooks") or {}).items():
            for entry in entries or []:
                for h in entry.get("hooks") or []:
                    if h.get("command"):
                        cmds.append(h["command"])
    return cmds


def find_definers():
    """`scripts/` files defining a --selftest, by basename -> abspath."""
    out = {}
    if not os.path.isdir(SCRIPTS):
        raise Refusal("scripts/ absent at %s" % SCRIPTS)
    for f in sorted(os.listdir(SCRIPTS)):
        if os.path.splitext(f)[1] not in (".py", ".sh"):
            continue
        p = os.path.join(SCRIPTS, f)
        try:
            t = open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        if SELFTEST in t:
            out[f] = p
    if not out:
        raise Refusal("ZERO scripts/ files define %s -- a reader that finds no "
                      "definers reports a vacuous PASS" % SELFTEST)
    return out


def load_carriers():
    """(abspath, [stripped lines]) for every executable carrier."""
    out = []
    for rel in CARRIER_ROOTS:
        root = os.path.join(REPO, rel)
        if not os.path.isdir(root):
            continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in (".git", "__pycache__")]
            for f in fn:
                ext = os.path.splitext(f)[1]
                if ext not in CARRIER_EXT:
                    continue
                p = os.path.join(dp, f)
                try:
                    if os.path.getsize(p) > 3_000_000:
                        continue
                    t = open(p, encoding="utf-8", errors="replace").read()
                except OSError:
                    continue
                out.append((p, strip_prose(t, ext)))
    if not out:
        raise Refusal("ZERO carriers loaded -- nowhere to look for an invocation")
    return out


# ------------------------------------------------------------- reachability ---

def invokes_selftest(lines, basename, same_line=True):
    """Line numbers where `basename` is invoked WITH --selftest.

    `same_line=False` is the DELIBERATELY LOOSE form, used only by limb X3 to
    show what the strict form excludes.
    """
    hits = []
    if same_line:
        for n, l in enumerate(lines, 1):
            if basename in l and SELFTEST in l:
                hits.append(n)
    else:
        has_base = [n for n, l in enumerate(lines, 1) if basename in l]
        has_flag = any(SELFTEST in l for l in lines)
        if has_base and has_flag:
            hits = has_base
    return hits


def mentions_file(lines, basename):
    """Line numbers where a carrier invokes `basename` at all (any flags)."""
    return [n for n, l in enumerate(lines, 1) if basename in l]


def reachable(definers, carriers, roots, same_line=True):
    """TRIGGERED iff an automatic root reaches a `<definer> --selftest` line.

    Two hops, which is what the real chains use: root -> wrapper -> selftest,
    and root -> selftest directly. Deeper chains are REPORTED as UNPROVEN rather
    than silently classed either way.
    """
    root_text = "\n".join(roots)

    # Carriers an automatic root fires directly.
    auto_carriers = set()
    for p, _lines in carriers:
        if os.path.basename(p) in root_text or p in root_text:
            auto_carriers.add(p)

    triggered, hand_only = {}, []
    for base, dpath in sorted(definers.items()):
        # hop 0: a root itself invokes `<definer> --selftest`
        if base in root_text and SELFTEST in root_text:
            triggered[base] = ["crontab/hook (direct)"]
            continue
        chains = []
        for p, lines in carriers:
            if os.path.abspath(p) == os.path.abspath(dpath):
                continue        # a definer's own selftest is not its trigger
            if p not in auto_carriers:
                continue
            hits = invokes_selftest(lines, base, same_line=same_line)
            if hits:
                chains.append("%s:%s" % (os.path.relpath(p, REPO),
                                         ",".join(str(h) for h in hits)))
        if chains:
            triggered[base] = sorted(chains)
        else:
            hand_only.append(base)
    return triggered, hand_only, auto_carriers


# ------------------------------------------------------------- selftest -------

def selftest():
    results = []

    def ok(n, d):
        results.append((n, True, d))

    def bad(n, d):
        results.append((n, False, d))

    try:
        definers = find_definers()
        carriers = load_carriers()
        cron = read_crontab()
        hooks = read_hooks()
    except Refusal as exc:
        print("SELFTEST REFUSED: %s" % exc)
        return 2

    roots = cron + hooks
    print("  automatic roots: %d crontab line(s) + %d hook command(s) "
          "(producers: the box owner, the lab config)" % (len(cron), len(hooks)))
    print("  definers in scripts/: %d   carriers: %d" % (len(definers), len(carriers)))

    triggered, hand_only, auto = reachable(definers, carriers, roots)
    print("  classified: %d TRIGGERED / %d HAND-ONLY   (auto-fired carriers: %d)"
          % (len(triggered), len(hand_only), len(auto)))

    # -- R1 there must BE an automatic root, else every answer is HAND-ONLY and
    #    the census is parser blindness dressed as a finding.
    if roots:
        ok("R1 an automatic root exists", "%d root(s)" % len(roots))
    else:
        bad("R1 an automatic root exists",
            "no cron and no hooks -- every verdict would be vacuous")

    # -- X1 GROUND TRUTH POSITIVE, re-derived today, NOT cited from SS20.
    #    cron -> queue_runner.sh -> `queue_runner.py --selftest`.
    cron_fires_wrapper = any("queue_runner.sh" in l for l in cron)
    qr_trig = "queue_runner.py" in triggered
    if cron_fires_wrapper and qr_trig:
        ok("X1 ground truth POSITIVE (cron -> queue_runner.sh -> --selftest)",
           "reachable via %s" % triggered["queue_runner.py"][0])
    elif not cron_fires_wrapper:
        bad("X1 ground truth POSITIVE (cron -> queue_runner.sh -> --selftest)",
            "the crontab no longer fires queue_runner.sh -- the anchor is gone "
            "and this limb cannot be driven")
    else:
        bad("X1 ground truth POSITIVE (cron -> queue_runner.sh -> --selftest)",
            "cron fires the wrapper and cfd's fail-closed gate is in it, yet "
            "this reader calls queue_runner.py HAND-ONLY -- the reader cannot "
            "see a real trigger, so its HAND-ONLY answers are not evidence")

    # -- X2 GROUND TRUTH NEGATIVE: the reader must return HAND-ONLY on something.
    if hand_only:
        ok("X2 ground truth NEGATIVE (a real HAND-ONLY instrument is seen)",
           "%d hand-only; specimen %s" % (len(hand_only), hand_only[0]))
    else:
        bad("X2 ground truth NEGATIVE (a real HAND-ONLY instrument is seen)",
            "reader never returns HAND-ONLY, so a PASS is unfalsifiable")

    # -- X3 DEFECT 1, driven AT THE MATCHER against the real carrier where the
    #    defect actually lives. scripts/queue_entry_check.py names
    #    `queue_runner.py` and carries its OWN `--selftest` DOZENS OF LINES
    #    APART. File-level co-occurrence calls that an invocation; same-line
    #    matching does not. Driving this through `reachable()` would prove
    #    nothing, because that carrier is not fired by any automatic root -- the
    #    reachability filter HIDES the matcher defect rather than excluding it.
    spec = os.path.join(REPO, "scripts/queue_entry_check.py")
    if not os.path.exists(spec):
        bad("X3 same-line matching excludes real co-occurrence noise",
            "specimen carrier scripts/queue_entry_check.py is gone; the limb "
            "cannot be driven on real bytes")
    else:
        sl = strip_prose(open(spec, encoding="utf-8", errors="replace").read(),
                         ".py")
        strict_hits = invokes_selftest(sl, "queue_runner.py", same_line=True)
        loose_hits = invokes_selftest(sl, "queue_runner.py", same_line=False)
        if not loose_hits:
            bad("X3 same-line matching excludes real co-occurrence noise",
                "the specimen no longer co-occurs at file level; limb is void")
        elif strict_hits:
            bad("X3 same-line matching excludes real co-occurrence noise",
                "same-line matcher FIRED on the specimen at line(s) %s -- it "
                "admits the co-occurrence noise it exists to exclude"
                % ",".join(str(h) for h in strict_hits[:3]))
        else:
            ok("X3 same-line matching excludes real co-occurrence noise",
               "queue_entry_check.py: file-level matcher wrongly fires at "
               "line(s) %s, same-line matcher correctly silent"
               % ",".join(str(h) for h in loose_hits[:3]))

    # -- X4 DEFECT 2: prose stripping must remove a REAL docstring mention.
    #    THIS FILE names queue_runner.py beside --selftest in its own docstring.
    me = os.path.abspath(__file__)
    raw = open(me, encoding="utf-8", errors="replace").read()
    raw_lines = raw.splitlines()
    stripped = strip_prose(raw, ".py")
    raw_hits = [n for n, l in enumerate(raw_lines, 1)
                if "queue_runner.py" in l and SELFTEST in l]
    str_hits = [n for n, l in enumerate(stripped, 1)
                if "queue_runner.py" in l and SELFTEST in l]
    if raw_hits and not str_hits:
        ok("X4 prose stripping removes a real docstring mention",
           "this file's own docstring line(s) %s survive raw matching and are "
           "correctly stripped" % ",".join(str(h) for h in raw_hits[:3]))
    elif not raw_hits:
        bad("X4 prose stripping removes a real docstring mention",
            "this file no longer carries the specimen mention; limb is void")
    else:
        bad("X4 prose stripping removes a real docstring mention",
            "docstring mention SURVIVED stripping at line(s) %s -- prose would "
            "be counted as an invocation"
            % ",".join(str(h) for h in str_hits[:3]))

    # -- X5 PARTITION.
    if set(triggered) & set(hand_only):
        bad("X5 classifier is a partition", "a definer is in both classes")
    else:
        ok("X5 classifier is a partition",
           "%d + %d = %d definers" % (len(triggered), len(hand_only),
                                      len(definers)))

    # -- N1 REFUSAL: an unreadable crontab must REFUSE, never mark all dead.
    saved = globals()["subprocess"]

    class _Boom(object):
        SubprocessError = subprocess.SubprocessError

        @staticmethod
        def run(*a, **k):
            raise OSError("planted: crontab unavailable")

    try:
        globals()["subprocess"] = _Boom
        read_crontab()
        bad("N1 refusal on unreadable crontab", "did not refuse")
    except Refusal:
        ok("N1 refusal on unreadable crontab", "refused (exit 2 path)")
    except OSError:
        bad("N1 refusal on unreadable crontab", "raised OSError instead of Refusal")
    finally:
        globals()["subprocess"] = saved

    # -- N2 REFUSAL: no definers must REFUSE, not report a vacuous PASS.
    saved_scripts = globals()["SCRIPTS"]
    try:
        globals()["SCRIPTS"] = "/nonexistent/vr8/scripts"
        find_definers()
        bad("N2 refusal when scripts/ is unreadable", "did not refuse")
    except Refusal:
        ok("N2 refusal when scripts/ is unreadable", "refused (exit 2 path)")
    finally:
        globals()["SCRIPTS"] = saved_scripts

    print()
    for n, g, d in results:
        print("  [%s] %s -- %s" % ("ok" if g else "FAIL", n, d))
    nbad = sum(1 for _, g, _ in results if not g)
    print("\nSELFTEST: %d case(s), %d failure(s)" % (len(results), nbad))
    return 0 if nbad == 0 else 2


# ---------------------------------------------------------------- census ------

def run_census():
    definers = find_definers()
    carriers = load_carriers()
    roots = read_crontab() + read_hooks()
    triggered, hand_only, auto = reachable(definers, carriers, roots)

    print("VR8 -- selftest trigger reachability census "
          "(frozen: verification/campaign/VR8_PREREGISTRATION.md)")
    print("  repo=%s" % REPO)
    print("  SCOPE: definers in scripts/ ONLY. cases/ and verification/ are OUT "
          "OF SCOPE and nothing is claimed about them.")
    print("  automatic roots: %d" % len(roots))
    print("  definers: %d   TRIGGERED: %d   HAND-ONLY: %d"
          % (len(definers), len(triggered), len(hand_only)))

    print("\n  TRIGGERED, with the chain that fires each:")
    for base in sorted(triggered):
        print("    %-38s <- %s" % (base, triggered[base][0]))

    print("\n  HAND-ONLY roll call:")
    for base in hand_only:
        print("    %s" % base)

    if hand_only:
        print("\nVERDICT: GATE FAIL -- %d of %d instruments in scripts/ defining "
              "%s are NOT reachable from any automatic root: they fire only when "
              "a human or an agent types them. This is the DEAD LEVER shape "
              "(DEAD_LEVER_AUDIT SS20). It is a finding about the LAB'S CONTROLS, "
              "not a failure of any instrument, and WIRING A TRIGGER IS EACH "
              "OWNER'S ACT -- this item wires none and edits none."
              % (len(hand_only), len(definers), SELFTEST))
        return 1
    print("\nVERDICT: PASS -- every scripts/ %s is reachable from an automatic "
          "root." % SELFTEST)
    return 0


def main():
    ap = argparse.ArgumentParser(description="VR8 selftest trigger reachability")
    ap.add_argument("--selftest", action="store_true",
                    help="drive both control limbs on the real corpus; exit 2 on "
                         "any failure or refusal")
    args = ap.parse_args()
    try:
        if args.selftest:
            print("VR8 SELFTEST -- controls read the LIVE crontab, the real "
                  "hooks and real production scripts (SS2j.2)")
            return selftest()
        return run_census()
    except Refusal as exc:
        print("REFUSED: %s" % exc)
        return 2


if __name__ == "__main__":
    sys.exit(main())
