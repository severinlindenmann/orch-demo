"""The three sub-repos: create, clone into the harness, scaffold main, allow the demo bot, protect main."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import seed_proc as sp
from seed_files import MAIN_TREES

SUBREPOS = {name: sp.subrepo(name) for name in sp.SUBREPO_NAMES}
DESCRIPTIONS = {
    "ingest": "orch demo (Acme Energy, fictional): gateway download service",
    "dbt": "orch demo (Acme Energy, fictional): dbt models",
    "infra": "orch demo (Acme Energy, fictional): job and environment definitions, never deployed",
}
PROTECTION = {
    "required_status_checks": None,
    "enforce_admins": False,
    "required_pull_request_reviews": {"required_approving_review_count": 1, "dismiss_stale_reviews": False,
                                      "require_code_owner_reviews": False},
    "restrictions": None,
}
class PolicyError(sp.SeedError):
    """An org or enterprise policy, not this script, blocks a setting; the rest of the seed can still run."""


_POLICY = ("GitHub refused to let Actions create and approve pull requests on {full}. An org or enterprise admin "
           "(or the account owner) must turn on 'Allow GitHub Actions to create and approve pull requests', then rerun `seed.py repos`.")


def clone_dir(name: str) -> Path:
    return sp.HARNESS / name


def commit_body(what: str, why: str) -> str:
    return f"What: {what}\nWhy: {why}\nRisk: None; demo repository."


def write_tree(d: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = Path(d) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")


def remote_has(d: Path, branch: str) -> bool:
    return bool(sp.out(["git", "-C", d, "ls-remote", "--heads", "origin", branch]))


def repo_exists(full: str) -> bool:
    return sp.run(["gh", "repo", "view", full, "--json", "name"], ok=(0, 1)).returncode == 0


def ensure_repo(name: str, w: sp.Writer) -> bool:
    full = SUBREPOS[name]
    if repo_exists(full):
        return True
    w(["gh", "repo", "create", full, "--private", "--disable-wiki", "--description", DESCRIPTIONS[name]])
    return w.apply


def ensure_clone(name: str, w: sp.Writer) -> None:
    d = clone_dir(name)
    if (d / ".git").exists():
        url = sp.out(["git", "-C", d, "remote", "get-url", "origin"])
        if not url.rstrip("/").removesuffix(".git").endswith(SUBREPOS[name]):
            raise sp.SeedError(f"{d} is a clone of {url}, expected {SUBREPOS[name]}")
        w(["git", "-C", d, "fetch", "origin"])
        return
    if d.exists() and any(d.iterdir()):
        raise sp.SeedError(f"{d} exists and is not a git clone; move it away first (nothing was changed)")
    w(["git", "clone", f"git@github.com:{SUBREPOS[name]}.git", d])


def ensure_main(name: str, w: sp.Writer) -> None:
    d = clone_dir(name)
    if remote_has(d, "main"):
        return
    if not w.apply:
        print(f"PLAN scaffold main of {SUBREPOS[name]} with {len(MAIN_TREES[name])} files")
        return
    sp.run(["git", "-C", d, "symbolic-ref", "HEAD", "refs/heads/main"])  # an empty clone has an unborn HEAD
    write_tree(d, MAIN_TREES[name])
    w(["git", "-C", d, "add", "-A"])
    w(["git", "-C", d, *sp.GIT_ID, "commit", "-m", f"Scaffold the {name} demo repo",
       "-m", commit_body("README, sources, deterministic CI and the demo-bot workflow.",
                         "Mission Control's demo needs a sub-repo with PRs in every review state.")])
    w(["git", "-C", d, "push", "-u", "origin", "main"])


def ensure_actions_can_review(full: str, w: sp.Writer) -> None:
    path = f"repos/{full}/actions/permissions/workflow"
    if (sp.jout(["gh", "api", path]) or {}).get("can_approve_pull_request_reviews"):
        return
    try:
        w(["gh", "api", "-X", "PUT", path, "-f", "default_workflow_permissions=read",
           "-F", "can_approve_pull_request_reviews=true"])
    except sp.SeedError as e:
        raise PolicyError(_POLICY.format(full=full) + f" ({e})") from e
    if w.apply and not (sp.jout(["gh", "api", path]) or {}).get("can_approve_pull_request_reviews"):
        raise PolicyError(_POLICY.format(full=full))


def ensure_protection(full: str, w: sp.Writer) -> None:
    if sp.run(["gh", "api", f"repos/{full}/branches/main/protection"], ok=(0, 1)).returncode == 0:
        return
    w(["gh", "api", "-X", "PUT", f"repos/{full}/branches/main/protection", "--input", "-"], input=json.dumps(PROTECTION))


def ensure_subrepo(name: str, w: sp.Writer) -> bool:
    if not ensure_repo(name, w):
        print(f"PLAN (dry run stops here for {name}: the repo does not exist yet)")
        return False
    ensure_clone(name, w)
    if not (clone_dir(name) / ".git").exists():
        return False
    ensure_main(name, w)
    ensure_protection(SUBREPOS[name], w)  # before the Actions setting, so a policy refusal leaves main protected
    ensure_actions_can_review(SUBREPOS[name], w)
    return True


def cmd_repos(args) -> int:
    w = sp.Writer(apply=args.apply)
    sp.require_admin(sp.me())
    blocked = []
    for name in SUBREPOS:
        try:
            ensure_subrepo(name, w)
        except PolicyError as e:
            print(f"BLOCKED {e}", file=sys.stderr)
            blocked.append(SUBREPOS[name])
    if blocked:
        print(f"error: the repos are set up, but Actions may not create or approve PRs on {', '.join(blocked)}; "
              "the demo-bot reviews (seed.py prs) need that setting or a human reviewer", file=sys.stderr)
        return 3
    return 0
