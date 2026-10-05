from __future__ import annotations

import pytest

from acme.ingest import fetch_with_retry


def test_fetch_with_retry_succeeds_after_transient_failures():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise TimeoutError("gateway timeout")
        return "payload"

    result = fetch_with_retry(flaky, gateway_id="GW-03", max_attempts=3)
    assert result == "payload"
    assert calls["n"] == 3


def test_fetch_with_retry_reraises_after_exhausting_attempts():
    def always_fails():
        raise TimeoutError("gateway timeout")

    with pytest.raises(TimeoutError):
        fetch_with_retry(always_fails, gateway_id="GW-03", max_attempts=2)
