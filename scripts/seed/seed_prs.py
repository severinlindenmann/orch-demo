"""Branches (from main's first commit), conflict commits on main and PRs in the sub-repos; writes out/github.json.

Every PR is opened by the user's own gh account. The enterprise forbids GitHub Actions to create or approve PRs, so
there is no bot: the planned review states (seed_files.NEEDS_SECOND_ACCOUNT) are seeded as open PRs without a review,
and the checklist reports them as allowed findings.
"""
from __future__ import annotations

import seed_proc as sp
from seed_files import PR_SPECS, PrSpec
from seed_repos import SUBREPOS, clone_dir, commit_body, remote_has, write_tree


def _local_branch(d, branch) -> bool:
    return sp.run(["git", "-C", d, "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"], ok=(0, 1)).returncode == 0


def base_commit(d) -> str:
    return sp.out(["git", "-C", d, "rev-list", "--max-parents=0", "origin/main"]).splitlines()[0]


def ensure_branch(spec: PrSpec, w: sp.Writer) -> None:
    d = clone_dir(spec.repo)
    if remote_has(d, spec.branch):
        return
    if _local_branch(d, spec.branch):  # committed earlier, push failed: push it, never recreate
        w(["git", "-C", d, "push", "-u", "origin", spec.branch])
        return
    if not w.apply:
        print(f"PLAN branch {spec.branch} in {SUBREPOS[spec.repo]} ({len(spec.files)} file(s)), then push")
        return
    w(["git", "-C", d, "switch", "-c", spec.branch, base_commit(d)])
    write_tree(d, spec.files)
    w(["git", "-C", d, "add", "-A"])
    w(["git", "-C", d, *sp.GIT_ID, "commit", "-m", spec.title.removeprefix("Draft: "),
       "-m", commit_body(spec.body.splitlines()[0].removeprefix("What: "), f"Demo PR state: {spec.seeded_state}.")])
    w(["git", "-C", d, "push", "-u", "origin", spec.branch])
    w(["git", "-C", d, "switch", "main"])


def ensure_main_commit(spec: PrSpec, w: sp.Writer) -> None:
    mc, d = spec.main_commit, clone_dir(spec.repo)
    if mc["subject"] in sp.out(["git", "-C", d, "log", "origin/main", "--format=%s"]).splitlines():
        return
    if not w.apply:
        print(f"PLAN commit '{mc['subject']}' on main of {SUBREPOS[spec.repo]}, then push (fast-forward)")
        return
    w(["git", "-C", d, "switch", "main"])
    w(["git", "-C", d, "merge", "--ff-only", "origin/main"])
    write_tree(d, mc["files"])
    w(["git", "-C", d, *sp.GIT_ID, "commit", "-am", mc["subject"],
       "-m", commit_body(mc["subject"] + ".", f"Moves main so {spec.branch} conflicts (demo).")])
    w(["git", "-C", d, "push", "origin", "main"])


def find_pr(full: str, branch: str) -> dict | None:
    rows = sp.jout(["gh", "pr", "list", "-R", full, "--head", branch, "--state", "all",
                    "--json", "number,url,state,isDraft"]) or []
    return rows[0] if rows else None


def ensure_pr(spec: PrSpec, w: sp.Writer, login: str) -> dict | None:
    """Open the PR as `login` (the gh user). Never requests a review or reviews: one account cannot."""
    full = SUBREPOS[spec.repo]
    pr = find_pr(full, spec.branch)
    if pr is None:
        argv = ["gh", "pr", "create", "-R", full, "--head", spec.branch, "--base", "main",
                "--title", spec.title, "--body", spec.body]
        w(argv + (["--draft"] if spec.seeded_state == "draft" else []))
        if not w.apply:
            return None
        pr = sp.wait_for(lambda: find_pr(full, spec.branch), f"the PR for {spec.branch}")
    return {"number": pr["number"], "url": pr["url"]}


def ensure_prs(name: str, w: sp.Writer, login: str) -> dict[str, dict]:
    if not (clone_dir(name) / ".git").exists():
        print(f"PLAN (skipping {name}: not cloned yet; run seed.py repos --apply)")
        return {}
    sp.run(["git", "-C", clone_dir(name), "fetch", "origin"])
    specs = [s for s in PR_SPECS if s.repo == name]
    for s in specs:  # every branch first: a branch made after the conflict commit would not conflict
        ensure_branch(s, w)
    for s in specs:
        if s.main_commit:
            ensure_main_commit(s, w)
    found = {}
    for s in specs:
        pr = ensure_pr(s, w, login)
        if pr:
            found[f"{s.repo}:{s.branch}"] = pr
    return found


def cmd_prs(args) -> int:
    w = sp.Writer(apply=args.apply)
    login = sp.me()
    sp.require_admin(login)
    data = sp.load_out()
    for name in SUBREPOS:
        data["prs"].update(ensure_prs(name, w, login))
    if args.apply:
        sp.save_out(data)
    return 0
