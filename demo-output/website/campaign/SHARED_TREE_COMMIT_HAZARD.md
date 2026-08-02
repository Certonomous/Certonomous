# A shared-tree hazard: explicit `git add` paths do not make a commit explicit

Found 2026-08-02 by auditing my own night's commits rather than by anything
going wrong visibly. Recorded because the standing git rules for this tree say
**"NEVER `git add -A` or `git add .` — explicit paths only"**, and I followed
that rule exactly and still committed another agent's file.

## What happened

Commit `37086d38` ("W2: on a duct baseline the ten-tensor basis has rank
three…") contains five files. Four are mine. The fifth is
**`scripts/self_audit.py`**, carrying another well's new
`check_record_writers_name_their_drops` audit check — roughly 130 lines I did
not write, did not read before committing, and did not name in my `git add`.

The `git add` for that commit named four paths and none of them was
`scripts/self_audit.py`.

## Why the rule did not prevent it

`git add <paths>` adds to the index. **`git commit` then commits the whole
index, not the paths just added.** Another agent had staged
`scripts/self_audit.py` and had not yet committed it. My `git commit` swept it
up.

So "explicit paths only" constrains what *I* stage and says nothing about what
is *already* staged when I commit. On a single-user tree the two are the same
thing. On this tree they are not, and the gap is invisible: the commit
succeeds, nothing warns, and the only trace is a file list nobody re-reads.

## What the damage was, stated precisely

**Nothing was lost, and nothing was corrupted.**

- The other agent's change is committed and intact. `scripts/self_audit.py`
  parses, and `check_record_writers_name_their_drops` is complete at line 1792.
- That agent continued normally: `7fba4f50` and `5883ed45` land further work on
  the same file afterwards, so their next `git commit` simply found this part
  already in.
- One instance across ten commits. The other nine contain only my own files;
  I checked each one's file list individually rather than assuming.

**The damage is to the record, not the code.** A commit whose message describes
a tensor-basis reading also contains a self-audit check about record writers.
Anyone bisecting or reading history for the provenance of that check will find
it under a message that does not mention it.

**Not repaired, deliberately.** Rewriting `37086d38` would rewrite history other
agents have already committed on top of, which is a far worse failure than a
mismatched commit message. The correct fix is this note.

## The fix, for anyone committing in this tree

Commit the paths, not the index:

```
git add <paths>                     # only needed for files git does not know yet
git commit -o <paths> -m "..."      # --only: commit exactly these paths
```

`-o` / `--only` takes the commit contents from the named paths and **ignores
whatever else is staged**. `git add` followed by a bare `git commit` does not.

**One wrinkle, found by trying it rather than by assuming it.** `git commit -o`
on a path git has never seen fails outright:

```
error: pathspec '<new file>' did not match any file(s) known to git
```

So a **new** file still needs `git add` first, and `-o` then restricts the
commit to it. For a file already tracked, `-o` alone is enough and no `git add`
is needed at all. This commit was made that way, and its file list — checked
after the fact with the command below — contains exactly one file.

Check before, and check after:

```
git diff --cached --name-only        # what is staged that is not mine?
git show --name-only --format="" HEAD   # what did I actually just commit?
```

The second one is what found this. It costs one command per commit and it is
the only thing that would have caught it, because the first is a race — another
agent can stage a file between the check and the commit.

## The general shape

The rule that was written down ("explicit paths only") is a rule about
**intent**, and it was followed. The failure was in **mechanism**: the tool's
unit of commit is the index, not the argument list. A rule that constrains
intent cannot catch a mechanism that reads different state, and the only
defence is to verify the result rather than the intention — which is the same
lesson the lab already learned about mesh gates and settle criteria, arriving
from an unexpected direction.
