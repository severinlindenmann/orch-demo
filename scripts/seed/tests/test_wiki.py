import json
import re

import pytest

import seed_proc as sp
import seed_wiki as sw

PAGES = sorted(sw.PAGES_DIR.glob("*.md"))
REPOS = set(json.loads((sp.HARNESS / "orchestrator" / "config.json").read_text())["git"]["repos"])


def test_six_to_eight_pages():
    assert 6 <= len(PAGES) <= 8
    assert not {"Home.md", "Test.md"} & {p.name for p in PAGES}


@pytest.mark.parametrize("page", PAGES, ids=lambda p: p.stem)
def test_page_parses_with_the_wiki_addon(page):
    parsed = sw.parse(page)
    assert parsed.problems == ()
    assert parsed.documents, "documents: front matter"
    assert any(k.startswith("DEMO-") for k in parsed.keys), "ticket-key mentions"
    for glob in parsed.documents:
        repo, sep, _ = glob.partition(":")
        assert sep and repo in REPOS, glob
    assert page.read_text().rstrip().endswith(sw.MARKER)


def test_cited_keys_are_planned_tickets():
    keys = {k for p in PAGES for k in sw.parse(p).keys if k.startswith("DEMO-")}
    assert all(1 <= int(k[5:]) <= 30 for k in keys)


def test_page_without_marker_is_never_overwritten(tmp_path, monkeypatch, fake_run):
    clone = tmp_path / "wiki"
    (clone / ".git").mkdir(parents=True)
    (clone / PAGES[0].name).write_text("# Someone's own page\n")
    monkeypatch.setattr(sw, "clone_dir", lambda: clone)
    written = sw.ensure_wiki(sp.Writer(apply=True))
    assert PAGES[0].name not in written
    assert (clone / PAGES[0].name).read_text() == "# Someone's own page\n"


def _clone_with_all_pages(tmp_path, monkeypatch):
    clone = tmp_path / "wiki"
    (clone / ".git").mkdir(parents=True)
    for p in PAGES:
        (clone / p.name).write_text(p.read_text())
    (clone / "Home.md").write_text("# Home\n")
    monkeypatch.setattr(sw, "clone_dir", lambda: clone)
    return clone


def test_second_run_writes_nothing(tmp_path, monkeypatch, fake_run):
    clone = _clone_with_all_pages(tmp_path, monkeypatch)
    fake_run.answer(["git", "-C", str(clone), "rev-list"], "0")
    assert sw.ensure_wiki(sp.Writer(apply=True)) == []
    assert fake_run.writes() == []
    assert (clone / "Home.md").read_text() == "# Home\n"


def test_a_commit_left_unpushed_is_pushed(tmp_path, monkeypatch, fake_run):
    clone = _clone_with_all_pages(tmp_path, monkeypatch)
    fake_run.answer(["git", "-C", str(clone), "rev-list"], "1")
    sw.ensure_wiki(sp.Writer(apply=True))
    assert fake_run.writes() == [["git", "-C", str(clone), "push", "origin", "HEAD"]]
