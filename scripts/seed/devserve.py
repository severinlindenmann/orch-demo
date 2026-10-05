"""Scratch-copy demo server for screenshots and UI checks (the sanctioned path from this README, usable from an agent).

    uv run --project <orch-core>/plugins/orch-core --extra dashboard python scripts/seed/devserve.py PORT [TOKEN]

Copies the demo into a throwaway directory with its own orch user dir (the real ~/.config/orch is never read or
written), adopts the copy's earlier decisions there, enables the demo addons and serves Mission Control on
127.0.0.1:PORT. Prints `READY <url>` once it is up; stop it with Ctrl-C. Pick a free port; do not use 8765/8766/8777.
Set DEVSERVE_WORK to keep the scratch copy somewhere else (default: a fresh temp dir).
"""
from __future__ import annotations

import json
import os
import secrets
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import seed_proc as sp  # noqa: E402
import seed_scratch  # noqa: E402
import seed_shots as sh  # noqa: E402


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    port = int(argv[0])
    token = argv[1] if len(argv) > 1 else secrets.token_urlsafe(16)
    tmp = Path(os.environ.get("DEVSERVE_WORK") or tempfile.mkdtemp(prefix="orch-devserve-"))
    tmp.mkdir(parents=True, exist_ok=True)
    sh.isolate_env(tmp)
    root = sh.scratch_copy(tmp / sp.HARNESS_NAME)
    prep = seed_scratch.prepare(root)
    print("prepared", len(prep["adopted"]), prep["refreshed"], flush=True)
    settings = json.loads((sp.HERE / "addon_settings.json").read_text(encoding="utf-8"))
    sh.enable_addons(root, {**{k: v for k, v in settings.items() if k in sh.DEFAULT_ADDONS}, "terminals": {}, "ticket-usage": {}})
    with seed_scratch.scratch_human(root):
        _ws, _server, thread = sh.serve(root, token, port)
        print(f"READY http://127.0.0.1:{port}/?token={token} root={root}", flush=True)
        try:
            while thread.is_alive():
                time.sleep(5)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
