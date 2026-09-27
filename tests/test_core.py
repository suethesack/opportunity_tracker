"""
Tests for the parts of the pipeline that don't need live network access
or a real Groq API key: dedupe logic and response parsing.
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from fetch_opportunities import Opportunity, _load_seen_links, _save_seen_links
from ai_evaluator import _parse_json_response
from report_writer import write_report
from ai_evaluator import Evaluation


def test_seen_links_roundtrip(tmp_path, monkeypatch):
    seen_file = tmp_path / "seen.json"
    monkeypatch.setattr(config, "SEEN_FILE", seen_file)
    monkeypatch.setattr("fetch_opportunities.SEEN_FILE", seen_file)

    assert _load_seen_links() == set()
    _save_seen_links({"https://example.com/a", "https://example.com/b"})
    assert _load_seen_links() == {"https://example.com/a", "https://example.com/b"}


def test_parse_json_response_handles_markdown_fence():
    raw = '```json\n{"relevant": true, "score": 8, "reason": "matches embedded systems"}\n```'
    parsed = _parse_json_response(raw)
    assert parsed["relevant"] is True
    assert parsed["score"] == 8


def test_parse_json_response_plain():
    raw = '{"relevant": false, "score": 2, "reason": "not related"}'
    parsed = _parse_json_response(raw)
    assert parsed["relevant"] is False


def test_write_report_filters_by_min_score(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "REPORTS_DIR", tmp_path)
    monkeypatch.setattr("report_writer.REPORTS_DIR", tmp_path)

    opp_high = Opportunity(title="IoT Hackathon", link="https://x.test/1", summary="", source="Devpost")
    opp_low = Opportunity(title="Poetry Contest", link="https://x.test/2", summary="", source="Devpost")

    evaluations = [
        Evaluation(opportunity=opp_high, relevant=True, score=9, reason="great fit"),
        Evaluation(opportunity=opp_low, relevant=False, score=1, reason="unrelated"),
    ]

    report_path = write_report(evaluations, min_score=5)
    content = report_path.read_text()

    assert "IoT Hackathon" in content
    assert "Poetry Contest" not in content


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
