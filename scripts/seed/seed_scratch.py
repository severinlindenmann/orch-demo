"""Scratch copies of the demo: an isolated orch user dir, and the test hook that lets the seed's human steps run there.

orch signs every human decision (approve, answer, verdict, close, adopt) into a per-user ledger in the orch config
dir, and refuses a human action when any ancestor process is an agent harness. The real seed (`tickets --apply`)
runs in the human's own terminal and goes through those checks unchanged.

A scratch copy (the `tickets` rehearsal, `shots`, a screenshot/demo server) runs with its own temporary
ORCH_STATE_DIR and XDG_CONFIG_HOME, so its ledger key and ledger are throwaway files. There, and only there,
`scratch_human` replaces `orch.actor.process_chain` with an empty chain: the same stub orch-core's own test suite
uses (tests/conftest.py, orch.testing.pytest_plugin), so a scratch process started from an agent session can still
record the seed's human steps into its throwaway ledger. It refuses unless `isolate_env` ran in this process and the
workspace lies inside that scratch dir; it is never used on the real demo.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import seed_proc as sp

SCRATCH_MARK = "ORCH_DEMO_SCRATCH"
# Every variable by which orch (or orch-core's tests) recognises an agent harness, plus orch's own session vars.
AGENT_VARS = ("ORCH_HOME", "CLAUDECODE", "CLAUDE_CODE_SESSION_ID", "ORCH_HARNESS", "ORCH_SESSION", "ORCH_MODEL",
              "CLAUDE_CODE_ENTRYPOINT", "AI_AGENT", "CODEX_SANDBOX", "CODEX_SANDBOX_NETWORK_DISABLED", "GEMINI_CLI")


def real_config_dir() -> Path:
    return Path.home() / ".config" / "orch"


def isolate_env(tmp: Path) -> dict:
    """Point this process's orch user dir and XDG config at `tmp` (keeping the gh login) and drop agent markers."""
    tmp = Path(tmp).resolve()
    real_gh = Path(os.environ.get("HOME", str(Path.home()))) / ".config" / "gh"
    env = {"ORCH_STATE_DIR": str(tmp / "orch-user"), "XDG_CONFIG_HOME": str(tmp / "xdg"), "GH_CONFIG_DIR": str(real_gh),
           SCRATCH_MARK: str(tmp)}
    Path(env["XDG_CONFIG_HOME"]).mkdir(parents=True, exist_ok=True)
    link = Path(env["XDG_CONFIG_HOME"]) / "gh"
    if real_gh.exists() and not link.exists():
        link.symlink_to(real_gh, target_is_directory=True)  # gh and git's gh credential helper keep the login
    for var in AGENT_VARS:
        os.environ.pop(var, None)
    os.environ.update(env)
    return env


def _inside(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def check_scratch(root: Path) -> Path:
    """The scratch dir, after making sure `root` and the orch user dir are inside it and the real ones are not."""
    mark = os.environ.get(SCRATCH_MARK)
    if not mark:
        raise sp.SeedError("the scratch human hook needs isolate_env() in this process first; "
                           "the real demo is seeded only from your own terminal")
    tmp = Path(mark).resolve()
    state = Path(os.environ.get("ORCH_STATE_DIR") or "/nonexistent").resolve()
    root = Path(root).resolve()
    if not _inside(state, tmp):
        raise sp.SeedError(f"ORCH_STATE_DIR {state} is not inside the scratch dir {tmp}")
    if not _inside(root, tmp) or root == sp.HARNESS.resolve():
        raise sp.SeedError(f"{root} is not a scratch copy inside {tmp}")
    if _inside(state, real_config_dir().resolve()):
        raise sp.SeedError("ORCH_STATE_DIR points at the real ~/.config/orch")
    return tmp


@contextmanager
def scratch_human(root: Path):
    """Inside an isolated scratch copy only: let human Ops run although an agent harness is an ancestor (the
    process_chain stub of orch-core's tests). The throwaway ledger key in the scratch dir signs the decisions."""
    check_scratch(root)
    if any(os.environ.get(v) for v in AGENT_VARS):
        raise sp.SeedError("agent markers are still set in the scratch process; isolate_env() removes them")
    import orch.actor
    with mock.patch.object(orch.actor, "process_chain", lambda: []):
        yield


def sign_unsigned(ws, human) -> tuple[list[str], list[str]]:
    """Adopt every decision the (scratch) ledger lacks through orch's own Ops.ledger_adopt. Returns the adopted
    items and the ones orch refuses to adopt (e.g. a gate changed since its approval), as "TICKET kind what"."""
    from orch.core import ledger, store
    from orch.core.ops import Ops
    from orch.errors import OrchError
    tickets = [store.load(ws, e.id)[1] for e in store.scan(ws) if e.meta is not None]
    adopted, refused = [], []
    for item in ledger.unsigned_items(ws, tickets):
        label = f"{item['ticket']} {item['kind']} {item.get('gate') or item.get('qid') or ''}".rstrip()
        try:
            Ops(ws, human).ledger_adopt(item, item["id"])
            adopted.append(label)
        except OrchError as e:
            refused.append(f"{label} ({e.message})")
    return adopted, refused


def carry_rehearsal_ledger(source: Path | None) -> bool:
    """When `source` is a `tickets` rehearsal copy, copy its throwaway ledger (and key) into this scratch user dir:
    epic charters, delegations and pauses cannot be adopted afterwards, so a copy served without them would show
    the epic children as approved on their own. Only a rehearsal's own scratch dir is read, never ~/.config/orch."""
    import shutil
    if source is None:
        return False
    src_dir = Path(source).resolve().parent
    user = src_dir / "orch-user"
    if not (src_dir / "rehearsal-report.json").exists() or not (user / "ledger.key").exists():
        return False
    if _inside(user.resolve(), real_config_dir().resolve()):
        raise sp.SeedError("refusing to read a ledger from the real ~/.config/orch")
    dst = Path(os.environ["ORCH_STATE_DIR"])
    if (dst / "ledger.key").exists():
        return False  # this scratch dir has its own key already
    dst.mkdir(parents=True, exist_ok=True)
    for name in ("ledger.key", "ledger.jsonl"):
        if (user / name).exists():
            shutil.copy2(user / name, dst / name)
    return True


def prepare(root: Path, source: Path | None = None) -> dict:
    """Make a scratch copy demo-ready: carry a rehearsal's ledger over (see carry_rehearsal_ledger), sign the
    copy's remaining earlier decisions into the scratch ledger, then retake the fresh claims (agent actions, which
    orch allows only on signed decisions)."""
    import seed_tickets as st
    from orch.core.workspace import Workspace
    check_scratch(root)
    carried = carry_rehearsal_ledger(source)
    with scratch_human(root):
        ws = Workspace.open(root)
        adopted, refused = sign_unsigned(ws, st.HUMAN)
        refreshed = st.refresh_claims(ws)
    return {"carried": carried, "adopted": adopted, "not_adopted": refused, "refreshed": refreshed}


# -- the `tickets` rehearsal: a child process with its own scratch env ------------------------------------------

def rehearse_child(root: Path, refs_path: Path, report: Path) -> int:
    import seed_checklist as cl
    import seed_tickets as st
    from orch.core.workspace import Workspace
    root = Path(root)
    with scratch_human(root):
        ws = Workspace.open(root)
        st.run_all(ws, st.Refs(json.loads(Path(refs_path).read_text(encoding="utf-8"))), sign_earlier=True)
    ws = Workspace.open(root)
    problems = cl.ticket_problems(ws) + cl.check_problems(ws)
    Path(report).write_text(json.dumps({"root": str(root), "problems": problems}), encoding="utf-8")
    return 0


def run_rehearsal(root: Path, refs_data: dict) -> list[str]:
    """Run the full rebuild in `root` (a copy inside a fresh temp dir) in a child process with isolated user config."""
    tmp = Path(root).resolve().parent
    refs_path, report = tmp / "refs.json", tmp / "rehearsal-report.json"
    refs_path.write_text(json.dumps(refs_data), encoding="utf-8")
    env = {k: v for k, v in os.environ.items() if k not in AGENT_VARS}
    env.update({"ORCH_STATE_DIR": str(tmp / "orch-user"), "XDG_CONFIG_HOME": str(tmp / "xdg")})
    r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "rehearse", str(root), str(refs_path),
                        str(report), str(tmp)], env=env, text=True)
    if r.returncode != 0 or not report.exists():
        raise sp.SeedError(f"the rehearsal in {root} failed (exit {r.returncode}); nothing was changed in the demo")
    return json.loads(report.read_text(encoding="utf-8"))["problems"]


def _main(argv: list[str]) -> int:
    if len(argv) == 5 and argv[0] == "rehearse":
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        isolate_env(Path(argv[4]))
        from orch.errors import OrchError
        try:
            return rehearse_child(Path(argv[1]), Path(argv[2]), Path(argv[3]))
        except (sp.SeedError, OrchError) as e:
            print(f"rehearsal failed: {getattr(e, 'message', e)}", file=sys.stderr)
            return 2
    print("usage: seed_scratch.py rehearse <root> <refs.json> <report.json> <scratch dir>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
