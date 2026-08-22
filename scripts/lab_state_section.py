#!/usr/bin/env python3
"""Replace ONE team's section of docs/LAB_STATE.md by rebuilding from a committed revision.

docs/LAB_STATE.md is shared by five teams. Committing it from the working tree carries
every other team's uncommitted section edits along (chief's rule, 2026-08-22, after
a6b43ab3 did exactly that). This helper is the same shape as append_record.py:

  1. take the COMMITTED blob at --rev (pass the SAME rev you pass to `commit-tree -p`);
  2. replace only the `## <team>` section (from its heading to the next `## ` heading
     or EOF) with the contents of --section-file;
  3. write the result to --out in SCRATCH -- the shared worktree copy is never written;
     stage it with `B=$(git hash-object -w OUT); git update-index --add --cacheinfo 100644,$B,PATH`;
  4. REFUSE (exit 2) if the bytes outside that section differ from the committed blob
     -- which can only happen if the section file itself contains a `## ` heading.

The caller still does the private-index sequence, the CAS and the post-commit verify.
--selftest plants a foreign edit outside the section and proves it is dropped, and
plants a stray `## ` heading inside the section and proves refusal.
"""
import argparse, os, re, subprocess, sys, tempfile

def committed(repo, rev, path):
    return subprocess.check_output(["git", "-C", repo, "show", f"{rev}:{path}"], text=True)

def split(text, team):
    m = re.search(rf"^## {re.escape(team)}\s*$", text, flags=re.M)
    if not m:
        raise SystemExit(f"REFUSED: no `## {team}` heading in the committed blob")
    start = m.start()
    n = re.search(r"^## ", text[m.end():], flags=re.M)
    end = m.end() + n.start() if n else len(text)
    return text[:start], text[start:end], text[end:]

def build(repo, rev, path, team, section_text):
    base = committed(repo, rev, path)
    head, old, tail = split(base, team)
    if not section_text.startswith(f"## {team}"):
        raise SystemExit(f"REFUSED: section file must begin with `## {team}`")
    if re.search(r"^## ", section_text[3:], flags=re.M):
        raise SystemExit("REFUSED: section file contains a second `## ` heading -- it would swallow a neighbour's section")
    if not section_text.endswith("\n"):
        section_text += "\n"
    new = head + section_text + tail
    h2, _, t2 = split(new, team)
    assert h2 == head and t2 == tail, "internal: bytes outside the section changed"
    return base, old, new

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--path", default="docs/LAB_STATE.md")
    ap.add_argument("--team")
    ap.add_argument("--section-file")
    ap.add_argument("--rev", default="HEAD")
    ap.add_argument("--out", help="write the merged file HERE (scratch), never the shared worktree; stage it with `git hash-object -w` + `git update-index --add --cacheinfo`")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.team or not a.section_file:
        raise SystemExit("--team and --section-file are required")
    sec = open(a.section_file, encoding="utf8").read()
    base, old, new = build(a.repo, a.rev, a.path, a.team, sec)
    print(f"lab_state_section.py -- rebuild from {a.rev}:{a.path}, replace only `## {a.team}`")
    print(f"  committed blob   : {len(base)} bytes; old section {len(old)} bytes; new section {len(sec)} bytes")
    print(f"  outside section  : byte-identical to the committed blob (asserted)")
    if a.dry_run:
        print("  --dry-run: nothing written"); print("VERDICT: OK"); return 0
    if not a.out:
        raise SystemExit("REFUSED: --out is required -- the shared worktree copy is never written (chief's rule, 2026-08-22)")
    with open(a.out, "w", encoding="utf8") as f:
        f.write(new)
    print(f"  written          : {a.out}  (scratch; the worktree {a.path} is untouched)")
    print(f"  next             : B=$(git hash-object -w {a.out}); git update-index --add --cacheinfo 100644,$B,{a.path}")
    print("VERDICT: OK")
    print("CANNOT SEE: any commit -- the private-index sequence, the CAS and the post-commit verification remain the caller's; pass this same --rev to commit-tree -p.")
    return 0

def selftest():
    d = tempfile.mkdtemp()
    subprocess.check_call(["git", "init", "-q", d])
    os.makedirs(f"{d}/docs")
    text = "# board\n\n## closure\nclosure text\n\n## dafoam\nold dafoam\n\n## heat-transfer\nthermal text\n"
    open(f"{d}/docs/LAB_STATE.md", "w").write(text)
    subprocess.check_call(["git", "-C", d, "add", "docs/LAB_STATE.md"])
    subprocess.check_call(["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init"])
    # plant a foreign edit in the worktree (another team's uncommitted change)
    open(f"{d}/docs/LAB_STATE.md", "w").write(text.replace("thermal text", "thermal text PLANTED-FOREIGN-EDIT"))
    base, old, new = build(d, "HEAD", "docs/LAB_STATE.md", "dafoam", "## dafoam\nnew dafoam\n")
    ok1 = "PLANTED-FOREIGN-EDIT" not in new and "new dafoam" in new and "closure text" in new and "thermal text" in new
    print(f"  planted foreign edit outside section -> {'DROPPED (correct)' if ok1 else 'CARRIED (WRONG)'}")
    try:
        build(d, "HEAD", "docs/LAB_STATE.md", "dafoam", "## dafoam\nx\n## heat-transfer\nhijack\n")
        ok2 = False
    except SystemExit as e:
        ok2 = "REFUSED" in str(e)
    print(f"  stray `## ` heading inside section -> {'REFUSED (correct)' if ok2 else 'ACCEPTED (WRONG)'}")
    print("VERDICT: " + ("PASS" if ok1 and ok2 else "FAIL"))
    return 0 if ok1 and ok2 else 1

if __name__ == "__main__":
    sys.exit(main())
