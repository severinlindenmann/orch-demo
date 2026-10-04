"""Read-only checklist: every state the demo must show. Exit 1 lists what is missing."""
from __future__ import annotations

import json
from collections import defaultdict

import seed_proc as sp

WANT = {
    "type": {"feature", "bug", "chore", "spike", "investigation", "epic"},
    "status": {"backlog", "open", "in-progress", "waiting", "testing", "done"},
    "priority": {"low", "normal", "high", "urgent"},
    "size": {"xs", "s", "m", "l"},
    "requirements": {"pending", "approved", "invalidated", "changes_requested"},
    "plan": {"pending", "approved", "invalidated", "skipped", "changes_requested"},
    "verdict": {"pending", "follow-up", "done"},
    "question": {"blocking", "non-blocking", "answered"},
    "claim": {"fresh", "stale"},
    "shape": {"multi-repo", "follow-up", "pr", "docs-label"},
    "external": {"GH"},
    "tasks": {"todo", "doing", "done", "skipped", "blocked", "human-owned", "added-after-approval"},
    "epic-child": {"covered", "changed", "delegated"},  # orch.core.epics.child_state
    "delegation": {"active", "paused"},
    "sprint": {"current", "next"},
}


def chain_depth(meta_by_id: dict) -> int:
    memo: dict[str, int] = {}

    def depth(tid: str, seen: frozenset) -> int:
        if tid in memo:
            return memo[tid]
        if tid not in meta_by_id or tid in seen:
            return 0
        below = [depth(str(b).upper(), seen | {tid}) for b in meta_by_id[tid].get("blocked_by") or []]
        memo[tid] = 1 + max(below, default=0)
        return memo[tid]

    return max((depth(t, frozenset()) for t in meta_by_id if meta_by_id[t].get("blocked_by")), default=0)


def ticket_problems(ws) -> list[str]:
    from orch.core import store
    from orch.core import tasks as tk
    from orch.core.gates import changes_pending, gate_state, plan_required
    from orch.core.ops import claim_expired

    ttl = float(ws.config["claims"]["ttl_hours"])
    seen: dict[str, set] = defaultdict(set)
    metas = {}
    for e in store.scan(ws):
        if e.meta is None:
            continue
        _, t = store.load(ws, e.id)
        m = t.meta
        metas[t.id.upper()] = m
        for key in ("type", "priority", "size"):
            seen[key].add(m.get(key))
        seen["status"].add(t.status)
        seen["requirements"].add(gate_state(t, "requirements"))
        if changes_pending(t, "requirements"):
            seen["requirements"].add("changes_requested")
        if t.status != "backlog":
            seen["plan"].add(gate_state(t, "plan") if plan_required(ws, t) else "skipped")
            if changes_pending(t, "plan"):
                seen["plan"].add("changes_requested")
        if t.status == "testing":
            seen["verdict"].add("pending")
        verdict = ((m.get("gates") or {}).get("verify") or {}).get("verdict")
        if verdict:
            seen["verdict"].add(verdict)
        for q in m.get("questions") or []:
            if q.get("answer") not in (None, ""):
                seen["question"].add("answered")
            else:
                seen["question"].add("blocking" if q.get("blocking", True) else "non-blocking")
        claim = m.get("claim") or {}
        if claim.get("session"):
            seen["claim"].add("stale" if claim_expired(claim, ttl) else "fresh")
        if len(m.get("repos") or []) >= 2:
            seen["shape"].add("multi-repo")
        if m.get("parent"):
            seen["shape"].add("follow-up")
        if m.get("prs"):
            seen["shape"].add("pr")
        if "docs" in (m.get("labels") or []):
            seen["shape"].add("docs-label")
        for x in m.get("external") or []:
            key = str((x or {}).get("key", ""))
            seen["external"].add("GH" if key.upper().startswith("GH-") else "bare" if key.isdigit() else "other")
        try:
            items = tk.ticket_tasks(t)
        except tk.TaskParseError:
            seen["tasks"].add("broken")
            items = []
        for task in items:
            seen["tasks"].add(task.state)
            if task.owner == "human":
                seen["tasks"].add("human-owned")
            if task.added and "after plan approval" in task.added:
                seen["tasks"].add("added-after-approval")
    _epic_states(ws, seen)
    problems = [f"{k}: missing {', '.join(sorted(v - seen[k]))}" for k, v in WANT.items() if v - seen[k]]
    if "bare" in seen["external"]:
        problems.append("external: bare-number keys are left; run the GH- migration (seed.py tickets)")
    if "broken" in seen["tasks"]:
        problems.append("tasks: a Tasks section does not parse")
    depth = chain_depth(metas)
    if depth < 3:
        problems.append(f"blocked_by: longest chain is {depth}, want 3")
    return problems


def _epic_states(ws, seen) -> None:
    from orch.core import epics, sprints, store
    entries = [e for e in store.scan(ws) if e.meta is not None]
    for e in entries:
        if not epics.is_epic(e.meta):
            continue
        _, epic = store.load(ws, e.id)
        d = epics.delegation(ws, epic)
        if d is not None:
            seen["delegation"].add("paused" if d["paused"] else "active")
        for c in epics.children(ws, epic.id, entries):
            _, child = store.load(ws, c.id)
            seen["epic-child"].add(epics.child_state(ws, epic, child))
    cur = sprints.current(ws)
    ids = [s["id"] for s in sprints.all_sprints(ws)]
    used = {str(e.meta.get("sprint")) for e in entries if e.meta.get("sprint")}
    if cur and cur["id"] in used:
        seen["sprint"].add("current")
    if cur and cur["id"] in ids and ids.index(cur["id"]) + 1 < len(ids) and ids[ids.index(cur["id"]) + 1] in used:
        seen["sprint"].add("next")


def check_problems(ws) -> list[str]:
    from orch.core.check import run_checks
    expected = json.loads((sp.HERE / "expected_findings.json").read_text(encoding="utf-8"))
    problems = []
    for f in run_checks(ws, emit_events=False):
        allowed = expected.get(f.code, {}).get("tickets")
        if allowed == "*" or (isinstance(allowed, list) and f.ticket in allowed):
            continue
        problems.append(f"unexpected orch check finding: {f.level} {f.ticket or '-'} {f.code} {f.message}")
    return problems


class Allowed(str):
    """A finding the demo accepts (printed as ALLOWED, never fails the checklist), e.g. a state a policy blocks."""


def _checks_of(rollup) -> dict:
    import sys
    from pathlib import Path
    addon = Path(__import__("orch").__file__).resolve().parents[2] / "addons" / "github-reviews"
    if str(addon) not in sys.path:
        sys.path.insert(0, str(addon))
    from github_reviews.github import checks_of
    return checks_of(rollup)


def pr_state(pr: dict, login: str) -> set[str]:
    states = set()
    decision = pr.get("reviewDecision")
    if pr.get("isDraft"):
        states.add("draft")
    if decision == "APPROVED":
        states.add("approved")
    if decision == "CHANGES_REQUESTED":
        states.add("changes_requested")
    if any((r or {}).get("login") == login for r in pr.get("reviewRequests") or []):
        states.add("review_requested")
    if pr.get("mergeable") == "CONFLICTING":
        states.add("conflict")
    if not pr.get("isDraft") and decision not in ("APPROVED", "CHANGES_REQUESTED") and pr.get("mergeable") != "CONFLICTING":
        states.add("open")  # open, ready, no review decision yet
    checks = _checks_of(pr.get("statusCheckRollup"))["state"]
    states.add("failing" if checks == "failed" else "passing" if checks == "passed" else f"checks-{checks}")
    return states


def pr_problems(ws) -> list[str]:
    from seed_files import NEEDS_SECOND_ACCOUNT, PR_SPECS, SECOND_ACCOUNT_HINT
    from seed_repos import SUBREPOS
    login, problems = sp.me(), []
    for name, full in SUBREPOS.items():
        rows = sp.jout(["gh", "pr", "list", "-R", full, "--state", "open", "--limit", "50", "--json",
                        "headRefName,isDraft,reviewDecision,reviewRequests,mergeable,statusCheckRollup"]) or []
        by_branch = {r["headRefName"]: r for r in rows}
        passing = 0
        for spec in (s for s in PR_SPECS if s.repo == name):
            pr = by_branch.get(spec.branch)
            if pr is None:
                problems.append(f"{full}: no open PR for {spec.branch}")
                continue
            states = pr_state(pr, login)
            passing += "passing" in states
            want = {spec.seeded_state} | ({"passing"} if spec.seeded_state == "open" else set())
            if not want <= states:
                problems.append(f"{full}#{spec.branch}: want {sorted(want)}, GitHub shows {sorted(states)}")
        if not passing:
            problems.append(f"{full}: no PR with passing checks")
    for state in sorted(NEEDS_SECOND_ACCOUNT):
        branches = [f"{s.repo}:{s.branch}" for s in PR_SPECS if s.state == state]
        if branches:
            problems.append(Allowed(f"{state}: not seeded, {SECOND_ACCOUNT_HINT}; "
                                    f"open without review instead: {', '.join(branches)}"))
    return problems


def issue_problems(ws) -> list[str]:
    from orch.core import store
    problems, login = [], sp.me()
    ms = sp.jout(["gh", "api", f"repos/{sp.HARNESS_REPO}/milestones?state=all&per_page=100"]) or []
    titles = {m["title"]: m for m in ms}
    for t in ("Sprint 41", "Sprint 42", "Sprint 43"):
        if not (titles.get(t) or {}).get("due_on"):
            problems.append(f"{t}: no due date")
    issues = sp.jout(["gh", "issue", "list", "-R", sp.HARNESS_REPO, "--state", "all", "--limit", "500",
                      "--json", "number,state,assignees"]) or []
    state = {f"GH-{i['number']}": i["state"] for i in issues}
    if not any(i["state"] == "OPEN" and any(a["login"] == login for a in i["assignees"]) for i in issues):
        problems.append("Mine: no open issue assigned to you")
    linked, closed_open, open_done = set(), 0, 0
    for e in store.scan(ws):
        for x in (e.meta or {}).get("external") or []:
            key = str(x.get("key", "")).upper()
            linked.add(key)
            closed_open += state.get(key) == "CLOSED" and e.status != "done"
            open_done += state.get(key) == "OPEN" and e.status == "done"
    if closed_open < 2:
        problems.append(f"out of sync: {closed_open} closed issue(s) with an open ticket, want 2+")
    if open_done < 1:
        problems.append("out of sync: no open issue whose ticket is done")
    if not any(s == "OPEN" and k not in linked for k, s in state.items()):
        problems.append("Import: every open issue is already linked")
    return problems


def wiki_problems(ws) -> list[str]:
    import seed_wiki as sw
    d = sw._sync_clone()
    problems = []
    for src in sorted(sw.PAGES_DIR.glob("*.md")):
        dest = d / src.name
        if not dest.exists() or dest.read_text(encoding="utf-8") != src.read_text(encoding="utf-8"):
            problems.append(f"{src.name} is not on the wiki (or differs)")
    return problems


CHECKS = [ticket_problems, check_problems, pr_problems, issue_problems, wiki_problems]


def cmd_checklist(args) -> int:
    from orch.core.workspace import Workspace
    ws = Workspace.open(sp.HARNESS)
    problems, allowed = [], []
    for check in CHECKS:
        name = check.__name__.removesuffix("_problems")
        for p in check(ws):
            (allowed if isinstance(p, Allowed) else problems).append(f"{name}: {p}")
    for p in allowed:
        print("ALLOWED", p)
    for p in problems:
        print("MISSING", p)
    print("all demo states present" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0
