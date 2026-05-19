"""
Terminal display engine — Robin style.
Tactical. Precise. Always watching.
"""

from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

ROBIN_BANNER = r"""
██████╗  ██████╗ ██████╗ ██╗███╗   ██╗
██╔══██╗██╔═══██╗██╔══██╗██║████╗  ██║
██████╔╝██║   ██║██████╔╝██║██╔██╗ ██║
██╔══██╗██║   ██║██╔══██╗██║██║╚██╗██║
██║  ██║╚██████╔╝██████╔╝██║██║ ╚████║
╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝

         ░█████╗░██████╗░███████╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
         ██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
         ██║  ██║██████╔╝█████╗  ██████╔╝███████║   ██║   ██║██║   ██║██╔██╗ ██║
         ██║  ██║██╔═══╝ ██╔══╝  ██╔══██╗██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
         ╚█████╔╝██║     ███████╗██║  ██║██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
          ╚════╝ ╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
"""

ROBIN_QUOTES = [
    "Je surveille tout. Les criminels tombent toujours dans mon piège.",
    "J'ai toujours un plan de secours. Toujours.",
    "Un bon détective anticipe — il ne réagit pas.",
    "Chaque connexion laisse une trace. Je les lis toutes.",
    "Ce réseau est MON terrain. Et j'ai tout prévu.",
    "Être le chef, c'est savoir avant que ça arrive.",
    "Les données ne mentent pas. Les attaquants, si.",
    "Stratégie, tactique, exécution — dans cet ordre.",
]

RED    = Fore.RED
GREEN  = Fore.GREEN
YELLOW = Fore.YELLOW
CYAN   = Fore.CYAN
WHITE  = Fore.WHITE
BOLD   = Style.BRIGHT
DIM    = Style.DIM
RESET  = Style.RESET_ALL


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def print_banner():
    print(RED + BOLD + ROBIN_BANNER + RESET)
    print(CYAN + "  « " + ROBIN_QUOTES[0] + " »" + RESET)
    print()


def mission_start(services: list[dict]):
    print(GREEN + BOLD + f"[{_ts()}] ══ OPÉRATION ROBIN — DÉMARRAGE ══" + RESET)
    for svc in services:
        print(GREEN + f"  [+] Piège actif   : {svc['name']:<12} → port {svc['port']}" + RESET)
    print(YELLOW + f"  [i] Fichier log   : logs/robin_tactical.log" + RESET)
    print(YELLOW + f"  [i] Rapport JSON  : logs/robin_report.json" + RESET)
    print(RED + BOLD + "\n  Surveillance en cours… En attente des intrus.\n" + RESET)


def alert_connection(service: str, ip: str, port: int, data: str = ""):
    print(
        RED + BOLD + f"[{_ts()}] !! ALERTE" + RESET +
        f" — {CYAN}{service}{RESET} — intrus depuis " +
        BOLD + f"{ip}:{port}" + RESET
    )
    if data:
        preview = data[:120].replace("\n", "\\n").replace("\r", "")
        print(DIM + f"           payload : {preview}" + RESET)


def info(msg: str):
    print(GREEN + f"[{_ts()}]  ·  {msg}" + RESET)


def warn(msg: str):
    print(YELLOW + f"[{_ts()}]  ⚠  {msg}" + RESET)


def print_summary(stats: dict):
    print()
    print(RED + BOLD + "══════════════ RAPPORT FINAL — ROBIN ══════════════" + RESET)
    total = stats.get("total_connections", 0)
    print(WHITE + BOLD + f"  Connexions totales interceptées : {total}" + RESET)
    by_service = stats.get("by_service", {})
    for svc, count in by_service.items():
        bar = "█" * min(count, 40)
        print(f"  {CYAN}{svc:<12}{RESET} {bar} {count}")
    top_ips = stats.get("top_ips", [])
    if top_ips:
        print(YELLOW + "\n  Top attaquants :" + RESET)
        for ip, count in top_ips[:5]:
            print(f"    {ip:<20} {count} tentatives")
    print(RED + "═══════════════════════════════════════════════════" + RESET)
    import random
    print(CYAN + f"\n  « {random.choice(ROBIN_QUOTES)} »\n" + RESET)
