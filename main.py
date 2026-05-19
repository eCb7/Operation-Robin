#!/usr/bin/env python3
"""
Opération Robin — Point d'entrée.

Usage:
    python main.py              # Lance tous les pièges
    python main.py --analyze    # Analyse le dernier rapport sans lancer le honeypot
    python main.py --config <fichier.yaml>
"""

import argparse
import sys

from robin.honeypot import load_config, run
from robin.analyzer import print_live_analysis


def main():
    parser = argparse.ArgumentParser(
        prog="operation-robin",
        description="Honeypot tactique — Opération Robin",
    )
    parser.add_argument(
        "--config", default="config/config.yaml",
        help="Chemin vers le fichier de configuration YAML"
    )
    parser.add_argument(
        "--analyze", action="store_true",
        help="Affiche l'analyse du dernier rapport sans démarrer le honeypot"
    )
    args = parser.parse_args()

    if args.analyze:
        print_live_analysis()
        sys.exit(0)

    cfg = load_config(args.config)
    run(cfg)


if __name__ == "__main__":
    main()
