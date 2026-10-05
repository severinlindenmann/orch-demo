"""Push the demo pages to the harness wiki. Pages without the seed marker are never overwritten."""
from __future__ import annotations

import sys
from pathlib import Path

import seed_proc as sp

PAGES_DIR = sp.HERE / "wiki_pages"
MARKER = f"<!-- seeded by {sp.HARNESS_NAME}/scripts/seed/wiki_pages; edit the source there -->"
WIKI_REPO = f"{sp.HARNESS_REPO}.wiki"  # cloned with `gh repo clone` (https; no SSH key needed)


def clone_dir() -> Path:
    return sp.WORK / "wiki"


def parse(path: Path):
    addon = Path(__import__("orch").__file__).resolve().parents[2] / "addons" / "wiki"
    if str(addon) not in sys.path:
        sys.path.insert(0, str(addon))
    from orch_wiki.markdown import parse_page
    return parse_page(path.stem, path.read_text(encoding="utf-8"), local_prefix="DEMO", pad=4, tracker_prefixes=("GH",))


def _sync_clone() -> Path:
    d = clone_dir()
    if (d / ".git").exists():
        sp.run(["git", "-C", d, "pull", "--ff-only"])  # local scratch clone; a read from GitHub
    else:
        d.parent.mkdir(parents=True, exist_ok=True)
        sp.run(["gh", "repo", "clone", WIKI_REPO, d])
    return d


def ensure_wiki(w: sp.Writer) -> list[str]:
    d = _sync_clone()
    changed = []
    for src in sorted(PAGES_DIR.glob("*.md")):
        text = src.read_text(encoding="utf-8")
        dest = d / src.name
        if dest.exists():
            current = dest.read_text(encoding="utf-8")
            if current == text:
                continue
            if MARKER not in current:
                print(f"SKIP {src.name}: the wiki has this page and the seed did not write it")
                continue
        changed.append(src.name)
        if w.apply:
            dest.write_text(text, encoding="utf-8")
        else:
            print(f"PLAN write {src.name}")
    if changed:
        w(["git", "-C", d, "add", "--", *changed])
        w(["git", "-C", d, *sp.GIT_ID, "commit", "-m", "Add the demo wiki pages",
           "-m", "What: Architecture, runbooks, data model, onboarding and two ADRs with documents: front matter.\n"
                 "Why: Related pages and 'may need an update' on tickets need real pages.\nRisk: None; demo wiki."])
    ahead = sp.out(["git", "-C", d, "rev-list", "--count", "@{u}..HEAD"], ok=(0, 128))
    if changed or ahead not in ("", "0"):  # also finishes a run whose push failed after the commit
        w(["git", "-C", d, "push", "origin", "HEAD"])
    return changed


def cmd_wiki(args) -> int:
    ensure_wiki(sp.Writer(apply=args.apply))
    return 0
