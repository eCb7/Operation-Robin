"""
Tactical analysis — Robin reads the battlefield in real time.
"""

import json
import re
from pathlib import Path
from collections import Counter

from robin import display

REPORT_PATH = Path("logs/robin_report.json")

# Known brute-force user agents / payloads
KNOWN_TOOLS = {
    "hydra":       r"hydra",
    "nmap":        r"nmap|masscan",
    "sqlmap":      r"sqlmap",
    "metasploit":  r"msfconsole|Metasploit",
    "nikto":       r"nikto",
    "dirbuster":   r"dirbuster|gobuster|ffuf|wfuzz",
}


def fingerprint_tool(payload: str) -> str | None:
    lower = payload.lower()
    for tool, pattern in KNOWN_TOOLS.items():
        if re.search(pattern, lower):
            return tool
    return None


def load_report() -> dict:
    if not REPORT_PATH.exists():
        return {}
    with open(REPORT_PATH) as f:
        return json.load(f)


def print_live_analysis():
    report = load_report()
    if not report:
        display.warn("Aucun rapport disponible — démarrez d'abord le honeypot.")
        return

    display.print_summary({
        "total_connections": report.get("total_connections", 0),
        "by_service":        report.get("by_service", {}),
        "top_ips":           report.get("top_ips", []),
    })

    events = report.get("events", [])
    tool_hits: Counter = Counter()
    for ev in events:
        tool = fingerprint_tool(ev.get("payload_preview", ""))
        if tool:
            tool_hits[tool] += 1

    if tool_hits:
        display.warn("Outils détectés dans les payloads :")
        for tool, count in tool_hits.most_common():
            print(f"    {tool:<15} {count} occurrence(s)")
