"""Ingest raw interval-read exports from substation gateways."""
from __future__ import annotations

import csv
import logging
from datetime import datetime
from pathlib import Path

from acme.models import RawMeterRead

logger = logging.getLogger(__name__)

_ALT_TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M"


def _parse_timestamp(value: str) -> str:
    """Normalize a gateway timestamp to ISO 8601.

    Most gateways emit ISO 8601 already, which pydantic parses directly.
    A couple of substations (GW-04, GW-11) emit `DD/MM/YYYY HH:MM`
    instead; this coerces that alternate format to ISO 8601 so it
    validates the same way.
    """
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value
    except ValueError:
        parsed = datetime.strptime(value, _ALT_TIMESTAMP_FORMAT)
        return parsed.isoformat()


def parse_gateway_export(path: Path) -> list[RawMeterRead]:
    """Parse one gateway export CSV into a list of `RawMeterRead`.

    Gateway exports are plain CSV with columns:
    `meter_id, gateway_id, read_at, kwh`.

    A row that fails to parse (bad numeric value, missing column, ...) is
    skipped and logged rather than aborting the whole file - one bad row
    from a flaky gateway should not cost us the rest of the day's reads.
    """
    reads: list[RawMeterRead] = []
    with path.open(newline="") as fh:
        reader = csv.DictReader(fh)
        for line_no, row in enumerate(reader, start=2):  # header is line 1
            try:
                reads.append(
                    RawMeterRead(
                        meter_id=row["meter_id"],
                        gateway_id=row["gateway_id"],
                        read_at=_parse_timestamp(row["read_at"]),
                        kwh=float(row["kwh"]),
                    )
                )
            except (KeyError, ValueError, TypeError) as exc:
                logger.warning(
                    "skipping malformed row %s:%d (%s): %s", path.name, line_no, row, exc
                )
    return reads


def load_gateway_exports(export_dir: Path) -> list[RawMeterRead]:
    """Parse every `.csv` export found directly under `export_dir`."""
    reads: list[RawMeterRead] = []
    for csv_path in sorted(export_dir.glob("*.csv")):
        reads.extend(parse_gateway_export(csv_path))
    return reads


def fetch_with_retry(download_fn, gateway_id: str, max_attempts: int = 3):
    """Call `download_fn()` with retries, for flaky gateway connections.

    `download_fn` takes no arguments and either returns the downloaded
    payload or raises. Retries up to `max_attempts` times with a short
    linear backoff between attempts, then re-raises the last error.
    """
    import time

    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return download_fn()
        except Exception as exc:  # noqa: BLE001 - deliberately broad, network layer varies
            last_exc = exc
            logger.warning(
                "download from %s failed (attempt %d/%d): %s",
                gateway_id,
                attempt,
                max_attempts,
                exc,
            )
            if attempt < max_attempts:
                time.sleep(0.5 * attempt)
    logger.error("giving up on %s after %d attempts", gateway_id, max_attempts)
    assert last_exc is not None
    raise last_exc
