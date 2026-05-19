"""
Core orchestrator — Robin deploys all traps, waits, watches.
"""

import threading
import yaml
from pathlib import Path

from robin import display
from robin.services import ssh_trap, http_trap, ftp_trap


DEFAULT_CFG = {
    "host":     "0.0.0.0",
    "ssh_port":  2222,
    "http_port": 8080,
    "ftp_port":  2121,
    "timeout":   10,
}


def load_config(path: str = "config/config.yaml") -> dict:
    cfg_path = Path(path)
    if cfg_path.exists():
        with open(cfg_path) as f:
            user_cfg = yaml.safe_load(f) or {}
        return {**DEFAULT_CFG, **user_cfg}
    return DEFAULT_CFG.copy()


def run(cfg: dict):
    stop_event = threading.Event()

    services_meta = [
        {"name": "SSH",  "port": cfg["ssh_port"]},
        {"name": "HTTP", "port": cfg["http_port"]},
        {"name": "FTP",  "port": cfg["ftp_port"]},
    ]

    display.print_banner()
    display.mission_start(services_meta)

    threads = [
        threading.Thread(target=ssh_trap.start,  args=(cfg, stop_event), daemon=True),
        threading.Thread(target=http_trap.start, args=(cfg, stop_event), daemon=True),
        threading.Thread(target=ftp_trap.start,  args=(cfg, stop_event), daemon=True),
    ]
    for t in threads:
        t.start()

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        display.warn("Signal reçu — Robin abandonne le terrain proprement.")
        stop_event.set()
        for t in threads:
            t.join(timeout=3)

        from robin import logger, analyzer
        logger.flush_now()
        display.print_summary(logger.get_stats())
        analyzer.print_live_analysis()
