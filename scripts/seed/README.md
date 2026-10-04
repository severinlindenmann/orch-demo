# Demo seed

`seed.py` rebuilds the orch-demo data (the harness's own issues and PRs, sub-repos, PRs, issues, wiki, tickets) with
orch-core's real operations. Every writing command is a dry run unless `--apply` is given; `seed.py --help` lists the
commands.

```sh
uv run --project <orch-core>/plugins/orch-core python scripts/seed/seed.py <command> [--apply]
```

## Repos, owner and order

The GitHub account and repo names live in one place, `seed_proc.py`: `OWNER` (default `severinlindenmann`, override
with `ORCH_DEMO_OWNER`), the harness `orch-demo` and the sub-repos `orch-demo-{ingest,dbt,infra}`. Seeded commits are
made as `ORCH_DEMO_GIT_NAME <ORCH_DEMO_GIT_EMAIL>` (default: the owner's `users.noreply.github.com` address), never with
your global git identity. To seed a copy under another account, set `ORCH_DEMO_OWNER` and also replace the owner in
`orchestrator/config.json`, `AGENTS.md`, `wiki_pages/` and the baseline tickets: those are data, not code.

The repository starts with a **baseline**: `orchestrator/` holds DEMO-0001..0015 (the tickets from before the seed
existed, with their gates and events) and the next number is DEMO-0016. `tickets` builds on exactly that state, and
the tests read it from the repository's initial commit. Those tickets cite the harness's own issues #1-#15 and PRs
#16-#24 by number, so `baseline` recreates them first, on a harness with no issues or PRs yet. Order:

1. `baseline --apply` (harness labels, milestones, issues #1-#15, PRs #16-#24; then `git pull --ff-only`)
2. `repos --apply`, `prs --apply`, `issues --apply` (writes `out/github.json`), `wiki --apply` (the wiki needs one
   page created in the browser first: GitHub creates a wiki's git repo only then)
3. `orch ledger adopt --workspace`, then `tickets --apply`, in your own terminal (see below)

## Human decisions and the approval ledger

**Workspace identity.** orch keys every ledger entry by `workspace_id` (sha256 of the config's `customer` and id
prefix) and ticket, and an epic's delegation id is its charter's content hash. Two demos with the same identity
therefore share decisions in one user's ledger: seeding again after an earlier seed of the same identity would read the
old approvals, charters and pauses as this run's (it failed with "the delegation on DEMO-0034 is paused already").
This demo's customer is `Acme Energy (orch demo)`, distinct from the earlier private demo's `Acme Energy`.
`tickets --apply` checks your ledger read-only before the rehearsal (`seed_tickets.ledger_collisions`) and stops with
the colliding tickets; if it does, give `orchestrator/config.json` a `customer` no earlier seed used, adopt the
baseline again and rerun.

orch-core signs every human decision (requirements/plan approvals, answers, verdicts, closes) into a per-user
ledger (`ledger.jsonl` plus the HMAC key `ledger.key` in the orch config dir: `$ORCH_STATE_DIR`, else
`$XDG_CONFIG_HOME/orch`, else `~/.config/orch`). Agents can only claim, start or finish tasks and move to testing
on decisions that are in that ledger, and a human action is refused when any ancestor process is an agent
harness (Claude Code, Codex, ...).

The seed follows those rules instead of working around them:

- **Human steps** (approve, request changes, answer, verdict, ticket-file edits for the GH- key migration) go
  through `Ops` with a human actor in the seed's own process, so orch signs them into the ledger of whoever runs
  it. **Agent steps** (new, sections, claims, tasks, logs, moves, links) use one agent actor per ticket.
- `tickets --apply` and its human steps run only in your own terminal. Inside an agent harness it stops with
  "running inside an agent harness"; that is intended.
- Decisions made before the ledger existed (DEMO-0001..0015) are not in your ledger. `refresh-claims` and
  `tickets --apply` list them and stop; review and sign them yourself with
  `uv run --project <orch-core>/plugins/orch-core orch ledger adopt --workspace` from the demo root, then run again. The seed
  never adopts on the real demo for you.
  You can run again right away: the timeline starts after the last event that is not a `ledger.adopted` line.
  `orch ledger adopt` stamps those lines with the real time of the signing, so counting them would leave no 6 h
  window for the stale claims. orch reads events by seq (it validates seq, not `at`), so the seed's earlier-stamped
  events after the adopt lines are accepted; the Activity timeline merely shows the adopt block between them.
  The adopted tickets' own adopt events count as a sign of life for the dashboard's "stale" view (120 min), so
  DEMO-0003 and DEMO-0014 show as silent only that long after you adopted.
- Dry runs work anywhere, also from an agent: `tickets` (no `--apply`) runs the full rebuild as a rehearsal,
  `refresh-claims` prints its plan and which tickets still need `orch ledger adopt`.

Every human decision is bound to the hash of what the human read: orch refuses an approval, answer or verdict
without one ("an approval needs the hash of what you read"). `seed_tickets._apply` asks orch for that hash right
before each human step (`seen_gate_hash`, `seen_question_hash`, `seen_verdict_hash`, built on orch's `gate_hash`,
`charter(...)["content_hash"]`, `question_hash` and `verdict_hash`) and passes it as `expected_hash`; it never
re-implements the hashing.

## Artifacts

Agent steps `("artifact", {...})` and `("artifact_link", {...})` attach files and links with `orch artifact add` /
`orch artifact link`, optionally tied to a task and an acceptance criterion, so Mission Control's Artifacts panel has
content (`seed_artifacts.py` draws the two screenshots deterministically). DEMO-0023 shows its mock-up inline in the
requirements (`![..](artifact:daily-report-mockup.png)`): the file is attached before the approval, so the gate hash
(v3) pins the image's sha256. DEMO-0028 shows a screenshot inline in its Verification, which the verdict hash pins.

## Epics, delegation and sprints

`tickets` also builds the epic examples (`seed_specs.py`, DEMO-0031..0036) with the same split between human and
agent steps:

| Ticket | What it shows | How |
|---|---|---|
| DEMO-0031 | epic, delegation active (max 3 children, up to size s) | agent writes it; the human approves it with `delegate` (signed charter) |
| DEMO-0032 | child covered by the epic approval, in progress | written before the approval; the agent claims it and starts T1 |
| DEMO-0033 | child "changed since epic approval" | covered, then the agent edits its Requirements |
| DEMO-0036 | child auto-approved under the delegation | the agent adds it after the approval (a late ticket) and runs `epic_auto_approve` |
| DEMO-0034 / 0035 | epic with a paused delegation, one covered child | the human approves with `delegate`, later `epic_pause` (signed) |

A recipe's steps can be split with `("at", x)` so an epic's children are written before the epic approval and
worked after it; a `late` ticket is created when its first batch runs (late tickets are the highest keys).

Sprints: when `orchestrator/config.json` defines none, the seed writes two two-week sprints there, dated around the
day it runs (S1 from this week's Monday, current; S2 the next), and the agents put the tickets in `SPRINTS` into
them. Board → Group by epic / sprint then has content. The checklist requires the epic child states covered,
changed and delegated, an active and a paused delegation, and tickets in the current and the next sprint;
`expected_findings.json` allows DEMO-0033's `gate-invalidated` and DEMO-0036's `delegated-approval` info lines.

## Scratch copies and the test hook

The `tickets` rehearsal, `shots` and screenshot/demo servers (e.g. a `devserve.py` that builds a scratch copy and
serves it) work on a copy of the demo with a throwaway orch user dir:

- `seed_scratch.isolate_env(tmp)` points `ORCH_STATE_DIR` and `XDG_CONFIG_HOME` at `tmp`, removes the agent
  markers from the environment and sets `ORCH_DEMO_SCRATCH=tmp`. The ledger key created there is a temporary one.
- `seed_scratch.scratch_human(root)` then replaces `orch.actor.process_chain` with an empty chain for the block:
  the same stub orch-core's own tests use (`tests/conftest.py`, `orch.testing.pytest_plugin`). A scratch process
  started from an agent session can therefore record human steps, but only into its throwaway ledger. It refuses
  unless `isolate_env` ran in this process, the orch user dir and `root` are inside the scratch dir, `root` is not
  the demo itself, and no agent marker is set.
- `seed_scratch.prepare(root)` uses it to adopt the copy's earlier decisions through orch's `Ops.ledger_adopt`
  and retake the fresh claims (`refresh_claims`, agent actions), so claims in the served copy are live. A
  screenshot server calls `isolate_env` → `scratch_copy` → `prepare` → `serve`.
- Epic charters, delegations and pauses cannot be adopted later (only gates, answers, verdicts and closes can).
  So when the source is a `tickets` rehearsal copy, `prepare(root, source)` first copies that rehearsal's
  throwaway ledger and key (`<rehearsal dir>/orch-user`) into the new scratch dir; it never reads
  `~/.config/orch`. A scratch copy of the real demo starts with an empty ledger, so its epic children show as
  approved on their own there.
- The `tickets` rehearsal runs in a child process (`seed_scratch.py rehearse ...`) with its own scratch env, so the
  stub never exists in the process that applies to the real demo, and the rehearsal's decisions never reach your
  real ledger.

The hook is never used on the real `--apply` paths. The seed's tests (`scripts/seed/tests`) isolate the
environment the same way (temporary `ORCH_STATE_DIR`/`XDG_CONFIG_HOME`, `process_chain` stub):

```sh
uv run --project <orch-core>/plugins/orch-core python -m pytest -q scripts/seed/tests
```
