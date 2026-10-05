"""The harness repo's own GitHub history that the baseline tickets DEMO-0001..0015 cite: labels, the Sprint 41-43
milestones, issues #1-#15, PRs #16-#24 (two merged, one closed) and the DEMO-0005 commit on main.

The baseline tickets in orchestrator/ link these by number (GH-7, .../pull/16), so they must get exactly those numbers:
run this first, on a harness repo with no issues or PRs yet, before `seed.py issues`. Data: baseline_github.json.

The work happens in a scratch clone (scripts/seed/.work/harness), never in your checkout: `git pull` afterwards.
A merged PR is merged by pushing its branch to main (a fast-forward), so no `gh pr merge` is needed; the one closed
PR (#24) is closed with `gh pr close`, which only this command's writer allows.
"""
from __future__ import annotations

import json
from pathlib import Path

import seed_proc as sp
from seed_repos import commit_body, remote_has, write_tree

R = sp.HARNESS_REPO
DATA = sp.HERE / "baseline_github.json"
ALLOW = (("pr", "close"),)


def load() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


def clone_dir() -> Path:
    return sp.WORK / "harness"


def _sync_clone() -> Path:
    d = clone_dir()
    if (d / ".git").exists():
        sp.run(["git", "-C", d, "fetch", "origin"])
        sp.run(["git", "-C", d, "switch", "main"])
        sp.run(["git", "-C", d, "merge", "--ff-only", "origin/main"])
    else:
        d.parent.mkdir(parents=True, exist_ok=True)
        sp.run(["gh", "repo", "clone", R, d])  # https via gh; no SSH key needed
    return d


def numbered() -> dict[int, dict]:
    """Every issue and PR on the harness by number (the issues API lists both)."""
    rows = sp.jout(["gh", "api", f"repos/{R}/issues?state=all&per_page=100"]) or []
    return {r["number"]: r for r in rows}


def _check_slot(n: int, title: str, have: dict[int, dict]) -> bool:
    """True when #n already is this item. Refuses when #n is something else, or when creating now would not get #n."""
    if n in have:
        if have[n]["title"] != title:
            raise sp.SeedError(f"{R}#{n} is {have[n]['title']!r}, expected {title!r}; the baseline needs an empty repo")
        return True
    if max(have, default=0) != n - 1:
        raise sp.SeedError(f"the next number on {R} is not #{n} (highest is #{max(have, default=0)}); the baseline "
                           "tickets cite #1-#24, so run `seed.py baseline` on a repo with no issues or PRs")
    return False


def _number_of(url: str, n: int) -> int:
    got = int(url.strip().rsplit("/", 1)[1])
    if got != n:
        raise sp.SeedError(f"GitHub gave #{got}, expected #{n}; stop and check {R}")
    return got


def ensure_labels(w: sp.Writer, data: dict) -> None:
    have = {r["name"] for r in sp.jout(["gh", "label", "list", "-R", R, "--limit", "200", "--json", "name"]) or []}
    for lb in data["labels"]:
        if lb["name"] not in have:
            argv = ["gh", "label", "create", lb["name"], "-R", R, "--color", lb["color"]]
            w(argv + (["--description", lb["description"]] if lb["description"] else []))


def _milestones() -> dict[str, dict]:
    return {m["title"]: m for m in sp.jout(["gh", "api", f"repos/{R}/milestones?state=all&per_page=100"]) or []}


def ensure_milestones(w: sp.Writer, data: dict) -> None:
    """Created open: `gh issue create --milestone` only finds open milestones. close_milestones runs after the issues."""
    have = _milestones()
    for m in data["milestones"]:
        if m["title"] not in have:
            w(["gh", "api", "-X", "POST", f"repos/{R}/milestones", "-f", f"title={m['title']}"])


def close_milestones(w: sp.Writer, data: dict) -> None:
    have = _milestones()
    for m in data["milestones"]:
        found = have.get(m["title"])
        if m["state"] == "closed" and (found is None or found.get("state") == "open"):
            if found is None:
                print(f"PLAN close milestone {m['title']} after its issues")
            else:
                w(["gh", "api", "-X", "PATCH", f"repos/{R}/milestones/{found['number']}", "-f", "state=closed"])


def _comments(kind: str, n: int) -> int:
    return len((sp.jout(["gh", kind, "view", str(n), "-R", R, "--json", "comments"]) or {}).get("comments") or [])


def ensure_issue(spec: dict, w: sp.Writer, have: dict[int, dict]) -> None:
    n = spec["number"]
    exists = _check_slot(n, spec["title"], have)
    if not exists:
        argv = ["gh", "issue", "create", "-R", R, "--title", spec["title"], "--body", spec["body"]]
        for label in spec["labels"]:
            argv += ["--label", label]
        if spec["milestone"]:
            argv += ["--milestone", spec["milestone"]]
        if spec["mine"]:
            argv += ["--assignee", "@me"]
        r = w(argv)
        if r is not None:
            _number_of(r.stdout, n)
        have[n] = {"title": spec["title"], "state": "open"}  # also in a dry run: the next slot is n + 1
    state = have[n].get("state", "open")
    if spec["closed"] and state == "open":
        w(["gh", "issue", "close", str(n), "-R", R, "--reason", "completed", "--comment", spec["comment"]])
    elif spec["comment"] and not spec["closed"] and (not exists or _comments("issue", n) == 0):
        w(["gh", "issue", "comment", str(n), "-R", R, "--body", spec["comment"]])


def ensure_branch(spec: dict, d: Path | None, w: sp.Writer) -> None:
    branch = spec["branch"]
    if d is None or not w.apply:
        print(f"PLAN branch {branch} from main in {R} ({len(spec['files'])} file(s)), then push")
        return
    if remote_has(d, branch):
        return
    w(["git", "-C", d, "switch", "-c", branch, "origin/main"])
    write_tree(d, spec["files"])
    w(["git", "-C", d, "add", "-A"])
    w(["git", "-C", d, *sp.GIT_ID, "commit", "-m", spec["commit"]["subject"], "-m", spec["commit"]["body"]])
    w(["git", "-C", d, "push", "-u", "origin", branch])
    w(["git", "-C", d, "switch", "main"])


def ensure_pr(spec: dict, d: Path | None, w: sp.Writer, have: dict[int, dict]) -> None:
    n = spec["number"]
    if not _check_slot(n, spec["title"], have):
        ensure_branch(spec, d, w)
        argv = ["gh", "pr", "create", "-R", R, "--head", spec["branch"], "--base", "main",
                "--title", spec["title"], "--body", spec["body"]]
        for label in spec["labels"]:
            argv += ["--label", label]
        r = w(argv + (["--draft"] if spec["draft"] else []))
        have[n] = {"title": spec["title"], "state": "open", "pull_request": {}}
        if r is None:
            if spec["comment"] and not spec["close"]:
                print(f"PLAN comment on #{n}")
            if spec["merge"]:
                print(f"PLAN merge #{n} by pushing {spec['branch']} to main (fast-forward)")
            if spec["close"]:
                print(f"PLAN close #{n} with a comment")
            return
        _number_of(r.stdout, n)
    pr = sp.jout(["gh", "pr", "view", str(n), "-R", R, "--json", "state,comments"]) or {}
    if spec["comment"] and not spec["close"] and not pr.get("comments"):
        w(["gh", "pr", "comment", str(n), "-R", R, "--body", spec["comment"]])
    if spec["merge"] and pr.get("state") == "OPEN":
        if d is None:
            print(f"PLAN merge #{n} by pushing {spec['branch']} to main (fast-forward)")
            return
        sp.run(["git", "-C", d, "fetch", "origin"])
        w(["git", "-C", d, "push", "origin", f"origin/{spec['branch']}:refs/heads/main"])
        sp.wait_for(lambda: (sp.jout(["gh", "pr", "view", str(n), "-R", R, "--json", "state"]) or {}).get("state") == "MERGED",
                    f"#{n} to show as merged")
        sp.run(["git", "-C", d, "fetch", "origin"])
        sp.run(["git", "-C", d, "merge", "--ff-only", "origin/main"])
    if spec["close"] and pr.get("state") == "OPEN":
        w(["gh", "pr", "close", str(n), "-R", R, "--comment", spec["comment"]])


def ensure_main_commit(mc: dict, d: Path | None, w: sp.Writer) -> None:
    if d is None or not w.apply:
        print(f"PLAN commit '{mc['subject']}' on main of {R}, then push (fast-forward)")
        return
    if mc["subject"] in sp.out(["git", "-C", d, "log", "origin/main", "--format=%s"]).splitlines():
        return
    w(["git", "-C", d, "switch", "main"])
    w(["git", "-C", d, "merge", "--ff-only", "origin/main"])
    write_tree(d, mc["files"])
    w(["git", "-C", d, *sp.GIT_ID, "commit", "-am", mc["subject"], "-m", mc["body"] or commit_body(mc["subject"], "Demo.")])
    w(["git", "-C", d, "push", "origin", "main"])


def cmd_baseline(args) -> int:
    w = sp.Writer(apply=args.apply, allow=ALLOW)
    sp.require_admin(sp.me())
    data = load()
    ensure_labels(w, data)
    ensure_milestones(w, data)
    have = numbered()
    for spec in data["issues"]:
        ensure_issue(spec, w, have)
    close_milestones(w, data)
    d = _sync_clone() if args.apply else (clone_dir() if (clone_dir() / ".git").exists() else None)
    for spec in data["prs"]:
        ensure_pr(spec, d, w, have)
    for mc in data["main_commits"]:
        ensure_main_commit(mc, d, w)
    if args.apply:
        print(f"done: pull the merged commits into your checkout with `git pull --ff-only` ({R})")
    return 0
