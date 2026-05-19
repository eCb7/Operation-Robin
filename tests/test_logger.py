"""Tests for the logger stats accumulation."""

import importlib
import sys


def _fresh_logger():
    """Reload logger module to reset in-memory stats."""
    if "robin.logger" in sys.modules:
        del sys.modules["robin.logger"]
    import robin.logger as lg
    return lg


def test_record_increments_stats(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "logs").mkdir()
    lg = _fresh_logger()

    lg.record("SSH",  "1.2.3.4", 12345, "SSH-2.0")
    lg.record("HTTP", "1.2.3.4", 54321, "GET /")
    lg.record("SSH",  "5.6.7.8", 22222, "")

    stats = lg.get_stats()
    assert stats["total_connections"] == 3
    assert stats["by_service"]["SSH"] == 2
    assert stats["by_service"]["HTTP"] == 1
    assert stats["top_ips"][0][0] == "1.2.3.4"


def test_json_report_written(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "logs").mkdir()
    lg = _fresh_logger()

    lg.record("FTP", "9.9.9.9", 9999, "USER admin")
    lg.flush_now()  # flush is buffered every 10 events; force it in tests

    import json
    report_path = tmp_path / "logs" / "robin_report.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert data["total_connections"] == 1
    assert data["events"][0]["src_ip"] == "9.9.9.9"
