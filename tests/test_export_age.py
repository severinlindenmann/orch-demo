from __future__ import annotations

from datetime import datetime, timezone

import pytest

from acme.config import PipelineConfig
from acme.ingest import ExportTooLateError, check_export_age


def test_on_time_export_is_not_late():
    config = PipelineConfig()
    export_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    run_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    assert check_export_age(export_date, run_date, config) is False


def test_late_but_allowed_export_is_accepted():
    config = PipelineConfig(allowed_late_days=3)
    export_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    run_date = datetime(2026, 9, 3, tzinfo=timezone.utc)
    assert check_export_age(export_date, run_date, config) is True


def test_too_late_export_is_rejected():
    config = PipelineConfig(allowed_late_days=3)
    export_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    run_date = datetime(2026, 9, 10, tzinfo=timezone.utc)
    with pytest.raises(ExportTooLateError):
        check_export_age(export_date, run_date, config)
