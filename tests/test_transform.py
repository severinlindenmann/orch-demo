from __future__ import annotations

from acme.transform import dedupe_reads, normalize_reads


def test_normalize_reads_flags_suspect_values(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    suspects = [r for r in normalized if r.is_suspect]
    assert len(suspects) == 1
    assert suspects[0].meter_id == "MTR-002"


def test_normalize_reads_preserves_count(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    assert len(normalized) == len(raw_reads)


def test_dedupe_reads_drops_repeats(raw_reads, config):
    normalized = normalize_reads(raw_reads, config)
    doubled = normalized + normalized
    deduped = dedupe_reads(doubled)
    assert len(deduped) == len(normalized)
