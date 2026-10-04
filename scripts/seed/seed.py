#!/usr/bin/env python3
"""Rebuild the orch-demo data. Every writing command is a dry run unless --apply is given.

  baseline        the harness's own issues #1-15 and PRs #16-24 the first 15 tickets cite (run before issues)
  repos           the three sub-repos: create if missing, scaffold main with CI, clone, protect main
  prs             branches, conflict commits and PRs in the sub-repos (writes out/github.json)
  issues          labels, sprint due dates and issues on the harness repo (writes out/github.json)
  wiki            the demo pages in the harness wiki
  tickets         GH- key migration, DEMO-0016..0036 (incl. epics) and sprints; --apply only in your own terminal
  refresh-claims  re-take the fresh demo claims (agent actions), e.g. right before a demo
  checklist       read-only: every state the demo must show, plus orch check
  shots           read-only: Playwright screenshots of every page against a scratch copy

Run from the demo root:  uv run --project <orch-core plugin> python scripts/seed/seed.py <command> [--apply]
"""
from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import seed_proc as sp  # noqa: E402


def _cmd(module: str, func: str):
    def call(args):
        return getattr(importlib.import_module(module), func)(args)
    return call


COMMANDS = {
    "checklist": _cmd("seed_checklist", "cmd_checklist"),
    "baseline": _cmd("seed_baseline", "cmd_baseline"),
    "repos": _cmd("seed_repos", "cmd_repos"),
    "prs": _cmd("seed_prs", "cmd_prs"),
    "issues": _cmd("seed_issues", "cmd_issues"),
    "wiki": _cmd("seed_wiki", "cmd_wiki"),
    "tickets": _cmd("seed_tickets", "cmd_tickets"),
    "refresh-claims": _cmd("seed_tickets", "cmd_refresh"),
    "shots": _cmd("seed_shots", "cmd_shots"),
}
WRITING = ("baseline", "repos", "prs", "issues", "wiki", "tickets", "refresh-claims")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="seed.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in WRITING:
        sub.add_parser(name).add_argument("--apply", action="store_true", help="really write (default: dry run)")
    sub.add_parser("checklist")
    shots = sub.add_parser("shots")
    shots.add_argument("--port", type=int, default=8899)
    shots.add_argument("--source", type=Path, help="screenshot this copy (e.g. a rehearsal) instead of the demo")
    shots.add_argument("--out", type=Path, help="where the PNGs go (default: scripts/seed/.work/shots/<stamp>)")
    args = p.parse_args(argv)
    if args.cmd not in COMMANDS:
        print(f"{args.cmd} is not implemented yet", file=sys.stderr)
        return 2
    from orch.errors import OrchError
    try:
        return COMMANDS[args.cmd](args)
    except sp.SeedError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except OrchError as e:  # an orch rule refused a step: show it, never a traceback
        print(f"orch refused: {e.message}" + (f" ({e.hint})" if e.hint else ""), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
