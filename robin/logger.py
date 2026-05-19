"""
Tactical logger — every byte recorded, every move traced.
"""

import json
import logging
import logging.handlers
import os
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from threading import Lock


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

_file_lock = Lock()

# Rotating file handler: 5 MB max, 3 backup files kept
_handler = logging.handlers.RotatingFileHandler(
    LOG_DIR / "robin_tactical.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8",
)
_handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))
_log = logging.getLogger("robin")
_log.setLevel(logging.INFO)
_log.addHandler(_handler)
_log.propagate = False

_FLUSH_EVERY = 10  # write JSON report every N connections

# In-memory stats
_stats: dict = {
    "total_connections": 0,
    "by_service": defaultdict(int),
    "ip_counter": Counter(),
    "events": [],
}


def record(service: str, ip: str, port: int, payload: str = "", extra: dict | None = None):
    """Record one honeypot interaction."""
    with _file_lock:
        _stats["total_connections"] += 1
        _stats["by_service"][service] += 1
        _stats["ip_counter"][ip] += 1

        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": service,
            "src_ip": ip,
            "src_port": port,
            "payload_preview": payload[:512] if payload else "",
        }
        if extra:
            event.update(extra)

        _stats["events"].append(event)
        _log.info(
            "service=%-8s ip=%-20s port=%-5d payload=%r",
            service, ip, port, payload[:120]
        )
        if _stats["total_connections"] % _FLUSH_EVERY == 0:
            _flush_json()


def _flush_json():
    report_path = LOG_DIR / "robin_report.json"
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_connections": _stats["total_connections"],
        "by_service": dict(_stats["by_service"]),
        "top_ips": _stats["ip_counter"].most_common(10),
        "events": _stats["events"][-200:],   # keep last 200 events in report
    }
    tmp = str(report_path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(report, f, indent=2)
    os.replace(tmp, report_path)


def flush_now():
    """Force an immediate JSON report write — call on shutdown."""
    with _file_lock:
        _flush_json()


def get_stats() -> dict:
    with _file_lock:
        return {
            "total_connections": _stats["total_connections"],
            "by_service": dict(_stats["by_service"]),
            "top_ips": _stats["ip_counter"].most_common(10),
        }
