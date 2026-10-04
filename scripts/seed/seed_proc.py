"""Process helpers for the demo seed: argv-only gh/git calls and a dry-run Writer that refuses destructive argv."""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS = HERE.parents[1]
# The one place that names the GitHub account and the repos: every repo name, URL and test derives from these.
# Override with ORCH_DEMO_OWNER to seed a copy under another account (then also replace the owner in
# orchestrator/config.json, AGENTS.md, wiki_pages/ and the baseline tickets, which are data, not code).
OWNER = os.environ.get("ORCH_DEMO_OWNER") or "severinlindenmann"
HARNESS_NAME = "orch-demo"
HARNESS_REPO = f"{OWNER}/{HARNESS_NAME}"
SUBREPO_NAMES = ("ingest", "dbt", "infra")
# Who the seeded commits are by (never the global git config, which may hold a work address).
GIT_NAME = os.environ.get("ORCH_DEMO_GIT_NAME") or "Severin Lindenmann"
GIT_EMAIL = os.environ.get("ORCH_DEMO_GIT_EMAIL") or f"{OWNER}@users.noreply.github.com"
GIT_ID = ("-c", f"user.name={GIT_NAME}", "-c", f"user.email={GIT_EMAIL}")


def subrepo(name: str) -> str:
    """owner/repo of a sub-repo: ingest -> severinlindenmann/orch-demo-ingest."""
    return f"{OWNER}/{HARNESS_NAME}-{name}"


def repo_url(full: str) -> str:
    return f"https://github.com/{full}"
OUT = HERE / "out" / "github.json"
WORK = HERE / ".work"


class SeedError(RuntimeError):
    pass


def run(argv, cwd=None, input=None, ok=(0,)):
    argv = [str(a) for a in argv]
    r = subprocess.run(argv, cwd=cwd, input=input, text=True, capture_output=True)
    if r.returncode not in ok:
        raise SeedError(f"{shlex.join(argv)} failed ({r.returncode}): {r.stderr.strip()[-800:]}")
    return r


def out(argv, cwd=None, ok=(0,)) -> str:
    return run(argv, cwd, ok=ok).stdout.strip()


def jout(argv, cwd=None):
    text = run(argv, cwd).stdout
    return json.loads(text) if text.strip() else None


_PUSH_BAD = ("--force", "-f", "--force-with-lease", "--force-if-includes", "--mirror", "--delete", "-d", "--prune")


def _git_sub(a: list[str]) -> tuple[str | None, list[str]]:
    i = 1
    while i < len(a):
        if a[i] in ("-C", "-c"):
            i += 2
        elif a[i].startswith("-"):
            i += 1
        else:
            return a[i], a[i + 1:]
    return None, []


def refuse_reason(argv, allow=()) -> str | None:
    """Why the seed must never run `argv`, or None. `allow` lists gh subcommands a caller may run anyway, e.g.
    ("pr", "close") for the baseline's one closed PR."""
    a = [str(x) for x in argv]
    if not a:
        return "empty argv"
    if a[0] == "git":
        sub, rest = _git_sub(a)
        if sub == "push":
            if any(x in _PUSH_BAD or x.startswith("--force") for x in rest):
                return "force or delete pushes are never allowed"
            if any(x.startswith(("+", ":")) for x in rest):
                return "forced or deleting refspecs are never allowed"
        if sub == "branch" and any(x in ("-D", "-d", "--delete") for x in rest):
            return "deleting branches is never allowed"
        if sub == "reset" and "--hard" in rest:
            return "hard resets are never allowed"
        if sub in ("clean", "update-ref"):
            return f"git {sub} is never allowed"
    if a[0] == "gh":
        if tuple(a[1:3]) in allow:
            return None
        if a[1:3] in (["repo", "delete"], ["issue", "delete"], ["label", "delete"], ["pr", "merge"], ["pr", "close"]):
            return f"gh {' '.join(a[1:3])} is never allowed"
        if a[1:2] == ["api"]:
            for flag in ("-X", "--method"):
                if flag in a and a.index(flag) + 1 < len(a) and a[a.index(flag) + 1].upper() == "DELETE":
                    return "DELETE API calls are never allowed"
    return None


@dataclass
class Writer:
    """Every GitHub/remote write goes through here. Dry run (the default) prints; --apply runs."""
    apply: bool
    log: list = field(default_factory=list)
    allow: tuple = ()  # gh subcommands refuse_reason lets through for this writer only, e.g. (("pr", "close"),)

    def __call__(self, argv, cwd=None, input=None):
        argv = [str(a) for a in argv]
        why = refuse_reason(argv, self.allow)
        if why:
            raise SeedError(f"refused {shlex.join(argv)}: {why}")
        self.log.append(argv)
        print(("RUN  " if self.apply else "PLAN ") + shlex.join(argv) + (f"   # in {cwd}" if cwd else ""), flush=True)
        return run(argv, cwd, input) if self.apply else None


def wait_for(probe, what: str, timeout: float = 180, every: float = 5):
    end = time.monotonic() + timeout
    while True:
        value = probe()
        if value:
            return value
        if time.monotonic() > end:
            raise SeedError(f"timed out after {timeout:.0f} s waiting for {what}")
        time.sleep(every)


def me() -> str:
    return out(["gh", "api", "user", "--jq", ".login"])


def require_admin(login: str) -> None:
    perms = jout(["gh", "api", f"repos/{HARNESS_REPO}", "--jq", ".permissions"]) or {}
    if not perms.get("admin"):
        raise SeedError(f"gh account {login} is not admin on {HARNESS_REPO}; `gh auth switch` to the {OWNER} account")


def load_out() -> dict:
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"prs": {}, "issues": {}}


def save_out(data: dict) -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
