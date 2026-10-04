"""Files the seeded agents attach to tickets (`orch artifact add`): a rendered mock-up, a chart, a test log and a CSV.

The two screenshots are drawn here as small deterministic PNGs (no imaging library, no network), so the seed always
produces the same bytes and therefore the same sha256 that orch pins in the gate and verdict hashes."""
from __future__ import annotations

import struct
import zlib

INK, PAPER, GRID = (33, 37, 41), (250, 250, 247), (214, 218, 222)
HEAD, ACCENT, OK, WARN = (226, 232, 240), (234, 120, 40), (60, 150, 90), (200, 60, 60)


def _png(width: int, height: int, pixels: bytearray) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        body = tag + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + bytes(pixels[y * width * 3:(y + 1) * width * 3]) for y in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


class _Canvas:
    def __init__(self, width: int, height: int):
        self.w, self.h = width, height
        self.px = bytearray(bytes(PAPER) * (width * height))

    def rect(self, x: int, y: int, w: int, h: int, color) -> None:
        for yy in range(max(y, 0), min(y + h, self.h)):
            start = (yy * self.w + max(x, 0)) * 3
            n = max(min(x + w, self.w) - max(x, 0), 0)
            self.px[start:start + n * 3] = bytes(color) * n

    def png(self) -> bytes:
        return _png(self.w, self.h, self.px)


def daily_report_mockup() -> bytes:
    """The daily report with the new threshold column (DEMO-0023)."""
    c = _Canvas(640, 300)
    c.rect(0, 0, 640, 44, INK)
    c.rect(20, 16, 160, 12, PAPER)
    cols = (20, 190, 330, 470)  # meter, read, kWh, threshold
    c.rect(0, 60, 640, 30, HEAD)
    for x, w in zip(cols, (90, 70, 60, 120)):
        c.rect(x, 71, w, 8, INK)
    for i in range(6):
        y = 100 + i * 28
        c.rect(0, y + 26, 640, 1, GRID)
        for x, w in zip(cols[:3], (80, 56, 44)):
            c.rect(x, y + 9, w, 8, (120, 126, 134))
        suspect = i in (1, 4)
        c.rect(cols[3], y + 4, 96, 18, ACCENT if suspect else (225, 228, 232))
        c.rect(cols[3] + 8, y + 10, 48, 6, PAPER if suspect else (150, 156, 164))
    c.rect(466, 56, 4, 238, ACCENT)  # the new column is outlined
    return c.png()


def dst_day_chart() -> bytes:
    """Reads per hour on 2026-10-25, the 25-hour day (DEMO-0028)."""
    c = _Canvas(640, 260)
    c.rect(40, 20, 2, 200, INK)
    c.rect(40, 220, 580, 2, INK)
    for hour in range(25):
        x = 52 + hour * 23
        height = 150 + (hour * 37) % 30
        c.rect(x, 220 - height, 16, height, WARN if hour == 3 else OK)  # the repeated 02:00 hour
    return c.png()


TEST_LOG = """\
$ python -m unittest discover -s tests -t .
test_429_without_retry_after_waits_30s ... ok
test_429_with_retry_after_uses_header ... ok
test_503_then_200_loads_the_file ... ok
test_empty_export_returns_no_rows ... ok

Ran 14 tests in 0.412s

OK
"""

EMPTY_EXPORT_LOG = """\
$ python -m unittest discover -s tests -t .
test_empty_export_returns_no_rows ... ok
test_empty_export_logs_a_warning ... ok

Ran 14 tests in 0.388s

OK
"""

COMPUTE_CSV = """\
compute,runs,avg_minutes,avg_cost_chf,cold_start_s
classic,10,11.8,4.62,0
serverless,10,12.4,3.79,40
"""

# name -> bytes (the files that artifact steps in seed_specs refer to)
FILES: dict[str, bytes] = {
    "daily-report-mockup.png": daily_report_mockup(),
    "dst-25h-day.png": dst_day_chart(),
    "429-repro.log": TEST_LOG.encode(),
    "empty-export-tests.log": EMPTY_EXPORT_LOG.encode(),
    "compute-comparison.csv": COMPUTE_CSV.encode(),
}
