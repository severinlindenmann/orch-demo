"""Screenshots of every Mission Control page against a scratch copy with scratch user config (R9). Read-only."""
from __future__ import annotations

import json
import secrets
import shutil
import tempfile
import threading
import time
from pathlib import Path

import seed_proc as sp
import seed_scratch

PAGES = [
    ("today", "/", "Checks failing"),  # "Review requested" needs a second account (B2 ruling)
    ("board", "/board?group=none", "DEMO-0021"),  # the grouping is remembered per workspace: set it every time
    ("board-epic", "/board?group=epic", "DEMO-0031"),
    ("board-sprint", "/board?group=sprint", "Sprint 1"),
    ("board-list", "/board?view=list&group=none", "DEMO-0030"),
    ("board-external", "/board?view=external", "Import"),
    ("activity", "/activity", "DEMO-00"),
    ("reports", "/reports", None),
    ("workspace", "/workspace", "GitHub code reviews"),
    ("code-reviews", "/addons/github-reviews/", "One ticket, several repos"),  # repo cards use the git.repos names
    ("databricks", "/addons/databricks/", "simulated"),
    ("wiki", "/addons/wiki/", "Runbook"),
]
TICKET_SHOTS = {
    "DEMO-0016": "backlog · requirements pending · non-blocking question",
    "DEMO-0017": "backlog · requirements changes requested",
    "DEMO-0018": "open · requirements changed after approval",
    "DEMO-0023": "open · blocked by DEMO-0022 → DEMO-0021",
    "DEMO-0021": "in progress · tasks doing/skipped · failing checks",
    "DEMO-0020": "in progress · fix failing checks",
    "DEMO-0024": "in progress · plan changes requested",
    "DEMO-0025": "in progress · plan changed · stale claim",
    "DEMO-0019": "in progress · multi-repo · human task",
    "DEMO-0026": "waiting · blocking question · blocked task",
    "DEMO-0027": "testing · xs plan skipped · verdict pending · docs may need update · issue closed",
    "DEMO-0028": "in progress · sent back · task added after approval · conflict",
    "DEMO-0029": "done · follow-up DEMO-0030",
    "DEMO-0030": "backlog · follow-up · docs label",
    "DEMO-0031": "epic · children covered / changed since approval / auto-approved · delegation active",
    "DEMO-0034": "epic · delegation paused",
    "DEMO-0036": "open · auto-approved under the epic's delegation",
    "DEMO-0010": "open · issue closed on GitHub (out of sync)",
    "DEMO-0005": "waiting · xs · conflicting PR",
}
DEFAULT_ADDONS = ("github-reviews", "github-issues", "databricks", "wiki")
SETTLE_S = 30  # after every addon has its first cache file, give the other scopes one more scheduler round
isolate_env = seed_scratch.isolate_env  # scratch user config + the scratch marker the human test hook checks


def config_snapshot(path: Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {}
    return {str(p.relative_to(path)): (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(path.rglob("*")) if p.is_file()}


def scratch_copy(dst: Path, src: Path | None = None) -> Path:
    shutil.copytree(Path(src) if src else sp.HARNESS, dst, symlinks=True,
                    ignore=shutil.ignore_patterns(".venv", "__pycache__", ".work", "locks", "addons", ".pytest_cache"))
    return dst


def enable_addons(root: Path, settings: dict) -> None:
    from orch.addons import userfiles
    for name, values in settings.items():
        userfiles.set_enabled(root, name, True)
        if values:
            userfiles.save_addon_config(root, name, values)


def serve(root: Path, token: str, port: int):
    import uvicorn
    from orch.core.workspace import Workspace
    from orch.dashboard.app import create_app
    ws = Workspace.open(root)
    app = create_app(ws, token)  # no port: never registers in the switcher's workspaces.json
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    sp.wait_for(lambda: server.started, "the dashboard to start", timeout=30, every=0.2)
    return ws, server, thread


def wait_for_caches(ws, timeout: float = 300, scheduler=None) -> None:
    """The scheduler only fetches while a live stream is connected or after a Refresh: ask for one until the caches exist."""
    def ready():
        if scheduler is not None:
            scheduler.request_refresh()
        return all(any((ws.state_dir / "addons" / n).glob("*.json")) for n in DEFAULT_ADDONS)
    sp.wait_for(ready, "a first cache file from every default addon", timeout=timeout, every=3)
    if scheduler is not None:
        scheduler.request_refresh()  # the scopes found by the first round get their first fetch too
    time.sleep(SETTLE_S)


def shoot(base: str, token: str, out_dir: Path, targets: list) -> list[str]:
    from playwright.sync_api import sync_playwright
    problems = []
    out_dir.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for theme in ("light", "dark"):
            for width, height in ((1440, 900), (390, 844)):
                ctx = browser.new_context(viewport={"width": width, "height": height}, color_scheme=theme)
                ctx.add_cookies([{"name": "orch_theme", "value": theme, "url": base}])
                page = ctx.new_page()
                page.route("**/*", lambda route: route.continue_()
                           if route.request.method == "GET" and route.request.url.startswith(base) else route.abort())
                page.goto(f"{base}/?token={token}")
                for name, path, marker in targets:
                    resp = page.goto(base + path, wait_until="load")
                    page.wait_for_timeout(400)
                    where = f"{name} {theme} {width}"
                    if resp is None or resp.status != 200:
                        problems.append(f"{where}: HTTP {resp.status if resp else 'none'}")
                    text = page.inner_text("body")
                    if marker and marker not in text:
                        problems.append(f"{where}: missing {marker!r}")
                    if "Traceback" in text or "Internal Server Error" in text:
                        problems.append(f"{where}: server error on the page")
                    if page.evaluate("document.documentElement.scrollWidth - window.innerWidth") > 1:
                        problems.append(f"{where}: horizontal scroll")
                    page.screenshot(path=str(out_dir / f"{name}-{theme}-{width}.png"), full_page=True)
                ctx.close()
        browser.close()
    return problems


def cmd_shots(args) -> int:
    real_config = Path.home() / ".config" / "orch"
    before = config_snapshot(real_config)
    tmp = Path(tempfile.mkdtemp(prefix="orch-demo-shots-"))
    isolate_env(tmp)
    source = getattr(args, "source", None)
    root = scratch_copy(tmp / sp.HARNESS_NAME, source)
    # in the copy only: sign its decisions into the scratch ledger and retake the fresh claims for the shots
    prepared = seed_scratch.prepare(root, source)
    print(f"scratch ledger: adopted {len(prepared['adopted'])}, refreshed {', '.join(prepared['refreshed'])}", flush=True)
    settings = json.loads((sp.HERE / "addon_settings.json").read_text(encoding="utf-8"))
    enable_addons(root, {k: v for k, v in settings.items() if k in DEFAULT_ADDONS})
    token = secrets.token_urlsafe(16)
    targets = PAGES + [(f"ticket-{k}", f"/t/{k}", k) for k in TICKET_SHOTS]
    out_dir = Path(args.out) if getattr(args, "out", None) else sp.WORK / "shots" / time.strftime("%Y%m%d-%H%M%S")
    print(f"serving {root} on 127.0.0.1:{args.port}", flush=True)
    ws, server, thread = serve(root, token, args.port)
    try:
        wait_for_caches(ws, scheduler=server.config.app.state.scheduler)
        problems = shoot(f"http://127.0.0.1:{args.port}", token, out_dir, targets)
    finally:
        server.should_exit = True
        thread.join(timeout=10)
    if config_snapshot(real_config) != before:
        problems.append("~/.config/orch changed during the run")
    (out_dir / "summary.json").write_text(json.dumps({"targets": [t[0] for t in targets], "states": TICKET_SHOTS,
                                                      "problems": problems}, indent=2), encoding="utf-8")
    print(f"{len(targets) * 4} screenshots in {out_dir}")
    for p in problems:
        print("PROBLEM", p)
    return 1 if problems else 0
