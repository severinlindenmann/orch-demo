"""Real orch operations on a virtual timeline (R5). Human steps only from the user's terminal (R4) or a temp copy."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

import seed_proc as sp
from seed_specs import REFRESH, SPRINTS, TICKETS, TicketSpec

from orch.core.events import Actor
from orch.core.ops import Ops

HUMAN = Actor("human", "you", "tty", None)
MIN_WINDOW = timedelta(hours=6)


def agent_actor(spec: TicketSpec) -> Actor:
    session = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{sp.repo_url(sp.HARNESS_REPO)}#{spec.key}"))
    return Actor("agent", spec.harness, "cli", session)


class Refs:
    def __init__(self, data: dict):
        self.data = data

    def issue(self, slug: str) -> str:
        try:
            return f"GH-{self.data['issues'][slug]}"
        except KeyError:
            raise sp.SeedError(f"issue {slug} is not in out/github.json; run seed.py issues --apply first") from None

    def pr(self, repo: str, branch: str) -> str:
        try:
            return self.data["prs"][f"{repo}:{branch}"]["url"]
        except KeyError:
            raise sp.SeedError(f"PR {repo}:{branch} is not in out/github.json; run seed.py prs --apply first") from None


class _Clock:
    def __init__(self, t: datetime):
        self.t = t

    def now(self) -> datetime:
        return self.t

    def advance(self, minutes: float) -> None:
        self.t += timedelta(minutes=minutes)

    def set(self, t: datetime) -> None:
        self.t = max(self.t, t)  # never backwards: events stay in time order


@contextmanager
def virtual_clock(start: datetime):
    import orch.clock
    import orch.core.ops
    clock = _Clock(start)
    with mock.patch.object(orch.clock, "now", clock.now), mock.patch.object(orch.core.ops, "now", clock.now):
        yield clock


def raw_set(ws, human_ops: Ops, tid: str, **meta) -> None:
    from orch.core import store
    from orch.core.model import render_ticket
    path, t = store.load(ws, tid)
    t.meta.update(meta)
    human_ops.replace_raw(tid, render_ticket(t), expected_mtime_ns=path.stat().st_mtime_ns)


def migrate_external(ws, human_ops: Ops) -> list[str]:
    from orch.core import store
    from orch.core.trackers import external_ref
    trackers = ws.config["external_trackers"]
    if not any(t.get("pattern") == "GH-(?P<id>\\d+)" for t in trackers):
        raise sp.SeedError("orchestrator/config.json still has the bare tracker; switch it to GH-(?P<id>\\d+) first")
    changed = []
    for e in store.scan(ws):
        exts = (e.meta or {}).get("external") or []
        if not any(str(x.get("key", "")).isdigit() for x in exts):
            continue
        new = [external_ref(trackers, f"GH-{x['key']}") if str(x.get("key", "")).isdigit() else x for x in exts]
        raw_set(ws, human_ops, e.id, external=new)
        changed.append(e.id)
    return changed


def _ticket(ws, tid: str):
    from orch.core import store
    return store.load(ws, tid)[1]


def seen_gate_hash(ws, tid: str, gate: str, delegate: dict | None = None) -> str:
    """The hash of what a human reads before approving `gate` of `tid`, computed by orch itself: the gate hash
    (text, size, type and the sha256 of every artifact image the text shows), or for an epic the charter's
    content hash over the epic and its open children."""
    from orch.core import epics
    from orch.core.gates import gate_hash
    t = _ticket(ws, tid)
    if t.meta.get("type") == "epic":
        return epics.charter(ws, t, delegate, tickets=epics.open_children(ws, t))["content_hash"]
    return gate_hash(t, gate)


def seen_question_hash(ws, tid: str, qid: str) -> str:
    from orch.core.questions import find_question, question_hash
    return question_hash(find_question(_ticket(ws, tid), qid))


def seen_verdict_hash(ws, tid: str) -> str:
    """The hash of the criteria and the evidence (Verification, with its pinned images) a verdict accepts."""
    from orch.core import epics, store
    t = _ticket(ws, tid)
    if t.meta.get("type") == "epic":
        return epics.verdict_hash(epics.open_children(ws, t), ws)
    return epics.verdict_hash([t], ws)


def _attach(ag: Ops, tid: str, a: dict, refs: "Refs", link: bool = False) -> None:
    """An agent attaches a file (`orch artifact add`, bytes from seed_artifacts) or a link to a ticket."""
    extra = {k: a[k] for k in ("label", "kind", "task", "ac") if k in a}
    if link:
        ag.artifact_link(tid, refs.pr(a["repo"], a["branch"]) + a.get("suffix", ""), **extra)
        return
    import seed_artifacts
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / a["name"]
        src.write_bytes(seed_artifacts.FILES[a["name"]])
        ag.artifact_add(tid, src, a["name"], inline=a.get("inline", False), **extra)


def _apply(ws, spec: TicketSpec, step: tuple, ag: Ops, hu: Ops, refs: Refs) -> None:
    kind, *a = step
    tid = spec.key
    if kind == "sections":
        for name, text in a[0].items():
            ag.set_section(tid, name, text)
    elif kind == "edit":
        ag.set_section(tid, a[0], a[1])
    elif kind == "approve":  # an epic's approval may carry {"delegate": {...}}: the charter, signed as the human's
        opts = a[1] if len(a) > 1 else {}
        hu.approve(tid, a[0], expected_hash=seen_gate_hash(ws, tid, a[0], opts.get("delegate")), **opts)
    elif kind == "pause":
        hu.epic_pause(tid)
    elif kind == "auto_approve":  # the agent, under the epic's signed delegation
        ag.epic_auto_approve(tid)
    elif kind == "sprint":
        ag.link(tid, sprint=a[0])
    elif kind == "changes":
        hu.request_changes(tid, a[0], a[1], expected_hash=seen_gate_hash(ws, tid, a[0]))
    elif kind == "claim":
        ag.claim(tid)
    elif kind == "tasks":
        ag.task_add(tid, a[0])
    elif kind == "start":
        ag.task_start(tid, a[0])
    elif kind == "done":
        ag.task_done(tid, a[0], a[1])
    elif kind == "skip":
        ag.task_skip(tid, a[0], a[1])
    elif kind == "ask":
        ag.ask(tid, a[0])
    elif kind == "answer":
        hu.answer(tid, a[0], a[1], a[2], expected_hash=seen_question_hash(ws, tid, a[0]))
    elif kind == "move":
        ag.move(tid, a[0])
    elif kind == "verdict":
        hu.verdict(tid, a[0], a[1], expected_hash=seen_verdict_hash(ws, tid))
    elif kind == "link":
        ag.link(tid, repo=a[0], branch=a[1], pr=refs.pr(a[0], a[1]) if a[2] else None)
    elif kind == "raw":
        raw_set(ws, hu, tid, **a[0])
    elif kind == "artifact":
        _attach(ag, tid, a[0], refs)
    elif kind == "artifact_link":
        _attach(ag, tid, a[0], refs, link=True)
    elif kind == "log":
        ag.log(tid, a[0])
    elif kind == "state":
        ag.set_state(tid, a[0])
    else:
        raise sp.SeedError(f"unknown recipe step {kind!r} in {tid}")


def segments(specs) -> list[tuple[float, TicketSpec, list]]:
    """Each recipe split at its ("at", x) steps into (at, spec, steps), in timeline order (stable for equal at)."""
    out = []
    for s in specs:
        at, batch = s.at, []
        for step in s.steps:
            if step[0] == "at":
                out.append((at, s, batch))
                at, batch = step[1], []
            else:
                batch.append(step)
        out.append((at, s, batch))
    first = {}
    for at, spec, _ in out:
        if spec.late:
            first.setdefault(spec.key, at)
    if sorted(first, key=lambda k: first[k]) != sorted(first):
        raise sp.SeedError("late tickets must start in key order on the timeline")
    return sorted(out, key=lambda o: o[0])


def sprint_dates(today) -> list[dict]:
    """Two two-week sprints: the one containing `today` (from its Monday) and the next."""
    monday = today - timedelta(days=today.weekday())
    out = []
    for n in range(2):
        start = monday + timedelta(days=14 * n)
        out.append({"id": f"S{n + 1}", "name": f"Sprint {n + 1}" + (" · gateway hardening" if n == 0 else ""),
                    "start": start.strftime("%Y-%m-%d"), "end": (start + timedelta(days=13)).strftime("%Y-%m-%d")})
    return out


def ensure_sprints(ws, today):
    """Write the two demo sprints into orchestrator/config.json when it defines none (and into the open
    workspace's config, which is read when a workspace opens)."""
    if ws.config.get("sprints"):
        return ws
    path = ws.home / "config.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    cfg["sprints"] = sprint_dates(today)
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ws.config["sprints"] = cfg["sprints"]
    return ws


def _next_number(ws) -> int:
    return int(json.loads((ws.state_dir / "counter.json").read_text(encoding="utf-8"))["next"])


def build(ws, refs: Refs, *, human: Actor, start: datetime, end: datetime, specs=TICKETS) -> dict[str, str]:
    from orch.core import store
    existing = {(e.meta or {}).get("title"): e.id for e in store.scan(ws)}
    for s in specs:
        if s.title in existing and existing[s.title] != s.key:
            raise sp.SeedError(f"{s.title!r} exists as {existing[s.title]}, expected {s.key}")
    missing = [s for s in specs if s.title not in existing]
    if not missing:
        return {s.title: existing[s.title] for s in specs}
    if len(missing) != len(specs):
        raise sp.SeedError("only some demo tickets exist (an interrupted run?). Restore orchestrator/ from git "
                           "(`git restore --source=HEAD --staged --worktree orchestrator`) and run again")
    first = int(specs[0].key.split("-")[1])
    if _next_number(ws) != first:
        raise sp.SeedError(f"the next ticket would be DEMO-{_next_number(ws):04d}, not {specs[0].key}; "
                           f"commits, PRs and wiki pages cite DEMO-{first:04d}..; nothing was changed")
    if end - start < MIN_WINDOW:
        raise sp.SeedError(f"the timeline window is {(end - start)} but needs 6 h so stale claims are stale; "
                           "run again later")
    late = [s for s in specs if s.late]
    if [s.key for s in specs[len(specs) - len(late):]] != [s.key for s in late]:
        raise sp.SeedError("late tickets must be the last keys")  # their IDs are allocated after all the others
    ids: dict[str, str] = {}

    def create(s: TicketSpec) -> None:
        ext = refs.issue(s.issue) if s.issue else None
        t = Ops(ws, agent_actor(s)).new(s.title, type=s.type, priority=s.priority, size=s.size, ask=s.ask,
                                        external=ext, from_ref=s.from_key, epic=s.epic)
        if t.id != s.key:
            raise sp.SeedError(f"{s.title!r} became {t.id}, expected {s.key}")
        ids[s.title] = t.id

    with virtual_clock(start) as clock:
        for s in specs:  # phase A: create in key order so IDs are DEMO-0016..; late tickets come in phase B
            if not s.late:
                create(s)
                clock.advance(2)
        slot0, usable = start + timedelta(minutes=40), (end - start) - timedelta(minutes=80)
        for at, s, steps in segments(specs):  # phase B: the work, spread over the window
            clock.set(slot0 + usable * at)
            if s.late and s.title not in ids:
                create(s)
                clock.advance(2)
            ag, hu = Ops(ws, agent_actor(s)), Ops(ws, human)
            for step in steps:
                _apply(ws, s, step, ag, hu, refs)
                clock.advance(2)
        by_key = {s.key: s for s in specs}
        for sprint, keys in SPRINTS.items():  # planning: the agents put their tickets into the sprints
            for key in keys:
                if key in by_key:
                    _apply(ws, by_key[key], ("sprint", sprint), Ops(ws, agent_actor(by_key[key])), None, refs)
                    clock.advance(1)
    return ids


BASELINE_LINKS = (  # evidence the first demo tickets already cite in their Log: linked so Artifacts shows it
    ("DEMO-0001", f"{sp.repo_url(sp.HARNESS_REPO)}/pull/19/checks", {"kind": "build", "label": "CI run on PR #19: green"}),
)


def link_baseline_evidence(ws) -> list[str]:
    from orch.core import store
    done = []
    for key, url, extra in BASELINE_LINKS:
        if not any(e.id == key and e.meta is not None for e in store.scan(ws)):
            continue
        session = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{sp.repo_url(sp.HARNESS_REPO)}#{key}"))
        Ops(ws, Actor("agent", "claude-code", "cli", session)).artifact_link(key, url, **extra)
        done.append(key)
    return done


def refresh_claims(ws, keys=REFRESH) -> list[str]:
    from orch.core import store
    present = {e.id for e in store.scan(ws) if e.meta is not None}
    done = []
    for key in (k for k in keys if k in present):  # DEMO-0016.. exist only after `tickets --apply`
        _, t = store.load(ws, key)
        claim = t.meta.get("claim") or {}
        if t.status not in ("open", "in-progress") or not claim.get("session"):
            continue
        Ops(ws, Actor("agent", claim.get("harness") or "claude-code", "cli", claim["session"])).claim(key)
        done.append(key)
    return done


def unsigned_on(ws, keys=REFRESH) -> dict[str, list[str]]:
    """Decisions on the existing tickets among `keys` that the ledger on this machine does not hold. orch lets an
    agent (re)claim only on signed decisions, so these need `orch ledger adopt` by the human first."""
    from orch.core import ledger, store
    out: dict[str, list[str]] = {}
    present = {e.id for e in store.scan(ws) if e.meta is not None}
    for key in keys:
        if key not in present:
            continue
        _, t = store.load(ws, key)
        for item in ledger.unsigned_items(ws, [t]):
            out.setdefault(key, []).append(f"{item['kind']} {item.get('gate') or item.get('qid') or ''}".rstrip())
    return out


def adopt_hint(missing: dict[str, list[str]]) -> str:
    listed = "; ".join(f"{k}: {', '.join(v)}" for k, v in missing.items())
    return (f"not in your approval ledger: {listed}. Review and sign them in your own terminal with "
            "`uv run --project <orch-core plugin> orch ledger adopt --workspace` (from the demo root), then run again")


def last_timeline_at(ws) -> datetime | None:
    """The time of the last event that belongs to the demo's own story. `ledger.adopted` events are bookkeeping:
    `orch ledger adopt` stamps them with the real time of the signing, so counting them would start the timeline at
    "now" and the 6 h window the stale claims need could never open right after an adopt. orch reads events by seq
    only (events.py validates seq, not `at`; the stale-claim and activity views take per-event times), so new events
    stamped before those adopt lines are valid, just not in time order with them."""
    from orch.clock import parse_stamp
    for line in reversed((ws.state_dir / "events.jsonl").read_text(encoding="utf-8").strip().splitlines()):
        event = json.loads(line)
        if event.get("kind") != "ledger.adopted":
            return parse_stamp(event["at"])
    return None


def timeline_window(ws, now: datetime) -> tuple[datetime, datetime]:
    last = last_timeline_at(ws)
    return (last + timedelta(minutes=1) if last else now - timedelta(days=2)), now


def run_all(ws, refs: Refs, *, sign_earlier: bool = False) -> dict[str, str]:
    """Migration and build on one timeline, then the fresh claims at real time: events stay in time order.

    The human steps go through Ops with a human actor, so orch signs them into the ledger of whoever runs this.
    `sign_earlier` (scratch copies and tests only, see seed_scratch) also adopts the decisions made before the
    ledger existed into the throwaway scratch ledger; on the real demo the human adopts them with `orch ledger adopt`."""
    from orch.core.maintenance import build_index
    start, end = timeline_window(ws, datetime.now(timezone.utc))  # before any write
    ws = ensure_sprints(ws, end.date())
    with virtual_clock(start):
        migrated = migrate_external(ws, Ops(ws, HUMAN))
    ids = build(ws, refs, human=HUMAN, start=start + timedelta(minutes=5), end=end)
    with virtual_clock(max(start, (last_timeline_at(ws) or start) + timedelta(minutes=1))):
        link_baseline_evidence(ws)
    if sign_earlier:
        import seed_scratch
        seed_scratch.check_scratch(ws.root)
        seed_scratch.sign_unsigned(ws, HUMAN)
    refreshed = refresh_claims(ws)
    build_index(ws)
    print(f"migrated {len(migrated)} ticket(s) to GH- keys; {len(ids)} demo tickets; refreshed {len(refreshed)} claim(s)")
    return ids


def _copy_ignore(src, names):
    skip = {".venv", "__pycache__", ".work", ".pytest_cache"}
    if Path(src).name == ".state":
        skip |= {"locks", "addons"}  # runtime locks and addon caches are never part of the demo state
    return [n for n in names if n in skip]


def rehearse(refs: Refs, dst: Path | None = None) -> tuple[Path, list[str]]:
    """Run everything in a full copy of the harness (sub-repos included, so task refs and commit checks are real),
    in a child process with its own throwaway orch user dir and ledger (seed_scratch). Returns the copy and the
    checklist problems found in it."""
    import seed_scratch
    root = Path(dst) if dst else Path(tempfile.mkdtemp(prefix="orch-demo-rehearsal-")) / sp.HARNESS_NAME
    shutil.copytree(sp.HARNESS, root, symlinks=True, ignore=_copy_ignore)
    return root, seed_scratch.run_rehearsal(root, refs.data)


def cmd_tickets(args) -> int:
    from orch.core.workspace import Workspace
    if args.apply:  # refuse inside an agent before anything else, even the rehearsal
        from orch.actor import require_human_terminal
        from orch.errors import OrchError
        try:
            require_human_terminal("seeding the demo tickets", hint="run `seed.py tickets --apply` in your own terminal")
        except OrchError as e:
            raise sp.SeedError(f"{e.message}; {e.hint}") from e
        missing = unsigned_on(Workspace.open(sp.HARNESS))
        if missing:  # the fresh claims at the end would be refused: stop before anything is written
            raise sp.SeedError(adopt_hint(missing))
    refs = Refs(sp.load_out())
    copy, problems = rehearse(refs)
    print(f"rehearsal in {copy}: " + ("all ticket states present" if not problems else "; ".join(problems)))
    if problems or not args.apply:
        return 1 if problems else 0
    typed = input("This records approvals, answers and verdicts as you in the demo. Type DEMO to confirm: ").strip()
    if typed != "DEMO":
        raise sp.SeedError("not confirmed; nothing changed")
    run_all(Workspace.open(sp.HARNESS), refs)
    return 0


def cmd_refresh(args) -> int:
    from orch.core.workspace import Workspace
    ws = Workspace.open(sp.HARNESS)
    from orch.core import store
    missing = unsigned_on(ws)
    present = {e.id for e in store.scan(ws) if e.meta is not None}
    keys = [k for k in REFRESH if k not in missing and k in present]
    if not args.apply:
        print("PLAN re-claim " + (", ".join(keys) or "nothing") + " with their own agent sessions (where claimed)")
        if missing:
            print("SKIP " + adopt_hint(missing))
        return 0
    print("refreshed " + (", ".join(refresh_claims(ws, keys)) or "nothing"))
    if missing:
        print("error: skipped " + ", ".join(missing) + "; " + adopt_hint(missing), file=sys.stderr)
        return 1
    return 0
