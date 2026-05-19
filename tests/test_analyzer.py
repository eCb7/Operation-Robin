"""Tests for the payload fingerprinting logic."""

import pytest
from robin.analyzer import fingerprint_tool


@pytest.mark.parametrize("payload,expected", [
    ("User-Agent: Mozilla/5.0 (Hydra)", "hydra"),
    ("GET /admin HTTP/1.1\r\nUser-Agent: sqlmap/1.7", "sqlmap"),
    ("nmap scan v7.94", "nmap"),
    ("User-Agent: DirBuster-1.0", "dirbuster"),
    ("hello world", None),
    ("", None),
])
def test_fingerprint_tool(payload, expected):
    assert fingerprint_tool(payload) == expected
