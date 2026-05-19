# Opération Robin — Honeypot Tactique

> *"Je surveille tout. Les criminels tombent toujours dans mon piège."*

---

## Présentation

**Opération Robin** est un honeypot multi-services écrit en Python.  
Il simule des services réseau vulnérables (SSH, HTTP, FTP) pour attirer, enregistrer et analyser le comportement des attaquants.

Projet réalisé dans le cadre du **Bachelor 3 Cybersécurité, Systèmes & Réseaux** — pilier *détection d'intrusion & analyse comportementale réseau*.

---

## Architecture

```
Operation-Robin/
├── main.py                    # Point d'entrée
├── config/
│   └── config.yaml            # Ports, timeouts, interface d'écoute
├── robin/
│   ├── honeypot.py            # Orchestrateur — déploie tous les pièges
│   ├── logger.py              # Enregistrement structuré (texte + JSON)
│   ├── analyzer.py            # Fingerprinting d'outils d'attaque
│   ├── display.py             # Interface terminal (couleurs, bannière)
│   └── services/
│       ├── ssh_trap.py        # Faux serveur SSH (banner + brute-force logging)
│       ├── http_trap.py       # Faux panneau admin HTTP
│       └── ftp_trap.py        # Faux serveur FTP
├── logs/
│   ├── robin_tactical.log     # Journal texte horodaté (rotation automatique 5 Mo)
│   └── robin_report.json      # Rapport JSON mis à jour toutes les 10 connexions
└── tests/
    ├── test_analyzer.py
    └── test_logger.py
```

---

## Installation

```bash
# Cloner le dépôt
git clone https://github.com/ecb7/operation-robin.git
cd operation-robin

# Environnement virtuel (recommandé)
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Dépendances
pip install -r requirements.txt
```

---

## Utilisation

### 1. Lancer le honeypot (Terminal 1)

```bash
python main.py
```

> **Comportement normal :** une fois les 3 pièges affichés, le programme se bloque en attente.  
> C'est voulu — il écoute comme un vrai serveur. **Ne pas fermer ce terminal.**

```
[09:51:18] ══ OPÉRATION ROBIN — DÉMARRAGE ══
  [+] Piège actif   : SSH          → port 2222
  [+] Piège actif   : HTTP         → port 8080
  [+] Piège actif   : FTP          → port 2121
  ...
  Surveillance en cours… En attente des intrus.
```

Les pièges actifs :

| Service | Port par défaut | Ce qu'il capture |
|---------|-----------------|------------------|
| SSH     | 2222            | Bannière exchange, tentatives d'auth |
| HTTP    | 8080            | Scan de paths, credential stuffing |
| FTP     | 2121            | Séquences USER/PASS, commandes FTP |

---

### 2. Tester les pièges (Terminal 2)

Ouvrir un **second terminal** dans le même répertoire et envoyer des connexions de test.

#### Linux / macOS

```bash
# Piège HTTP — scan de paths
curl http://localhost:8080/wp-admin
curl http://localhost:8080/admin

# Piège SSH — tentative de connexion
nc localhost 2222

# Piège FTP — séquence login
ftp localhost 2121
# Puis entrer :  USER admin   →  PASS motdepasse
```

#### Windows (PowerShell)

```powershell
# Piège HTTP
Invoke-WebRequest http://localhost:8080/wp-admin
Invoke-WebRequest http://localhost:8080/admin

# Piège SSH — vérification de port
Test-NetConnection localhost -Port 2222

# Piège FTP
ftp localhost 2121
# Puis entrer :  USER admin   →  PASS motdepasse
```

Chaque connexion déclenche une **alerte rouge en temps réel** dans le Terminal 1 :

```
[09:52:41] !! ALERTE — HTTP — intrus depuis 127.0.0.1:54321
           payload : GET /wp-admin HTTP/1.1
```

---

### 3. Arrêter et lire le rapport final

Depuis le Terminal 1, appuyer sur **`Ctrl+C`**.

Robin arrête proprement tous les services et affiche le bilan :

```
══════════════ RAPPORT FINAL — ROBIN ══════════════
  Connexions totales interceptées : 7
  SSH          ███ 3
  HTTP         ████ 4
  FTP          0

  Top attaquants :
    127.0.0.1            7 tentatives
═══════════════════════════════════════════════════
```

Le rapport complet est également disponible dans `logs/robin_report.json`.

---

### Analyser sans relancer

```bash
python main.py --analyze
```

Affiche le rapport du dernier run sans relancer le honeypot : top IPs, répartition par service, outils détectés.

---

### Configuration personnalisée

```bash
python main.py --config mon_config.yaml
```

Exemple de `config/config.yaml` :

```yaml
host:      "0.0.0.0"
ssh_port:  2222       # 22 en production (nécessite sudo / admin)
http_port: 8080       # 80 en production (nécessite sudo / admin)
ftp_port:  2121       # 21 en production (nécessite sudo / admin)
timeout:   10         # secondes avant fermeture d'une connexion inactive
```

> **Ports standards en production :** utiliser les ports 22, 80, 21 nécessite des droits élevés.  
> Linux/macOS : `sudo python main.py`  
> Windows : lancer le terminal en **Administrateur**

---

## Logs

Deux fichiers sont générés dans `logs/` :

| Fichier | Format | Contenu |
|---------|--------|---------|
| `robin_tactical.log` | Texte | Une ligne par connexion, horodatée — rotation automatique à 5 Mo (3 fichiers max) |
| `robin_report.json` | JSON | Rapport global mis à jour toutes les 10 connexions : top IPs, stats par service, 200 derniers événements |

---

## Tests

Les tests ne nécessitent pas de lancer le honeypot.

```bash
# Linux / macOS
python3 -m pytest tests/ -v

# Windows
python -m pytest tests/ -v
```

Résultat attendu :

```
tests/test_analyzer.py::test_fingerprint_tool[...hydra]       PASSED
tests/test_analyzer.py::test_fingerprint_tool[...sqlmap]      PASSED
tests/test_analyzer.py::test_fingerprint_tool[...nmap]        PASSED
tests/test_analyzer.py::test_fingerprint_tool[...dirbuster]   PASSED
tests/test_analyzer.py::test_fingerprint_tool[hello world]    PASSED
tests/test_analyzer.py::test_fingerprint_tool[vide]           PASSED
tests/test_logger.py::test_record_increments_stats            PASSED
tests/test_logger.py::test_json_report_written                PASSED

8 passed
```

---

## Résolution de problèmes

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Address already in use` | Un autre processus utilise le port | Changer le port dans `config.yaml` ou arrêter le processus conflictuel |
| `Permission denied` | Port < 1024 sans droits élevés | Utiliser `sudo` (Linux) ou terminal Administrateur (Windows) |
| `ModuleNotFoundError: colorama` | Dépendances non installées | Relancer `pip install -r requirements.txt` |
| Aucune alerte après connexion | Firewall local bloquant | Vérifier que le firewall autorise les ports configurés |

---

## Lien avec la formation

| Compétence Bachelor/Master | Couverture dans ce projet |
|----------------------------|---------------------------|
| Administration d'infrastructures réseau | Déploiement multi-services sur sockets TCP |
| Détection d'intrusion | Capture et classification des connexions suspectes |
| Analyse comportementale réseau | Fingerprinting d'outils (Hydra, Nmap, SQLmap…) |
| Journalisation & traçabilité | Logs structurés texte + JSON avec rotation |
| Politique de sécurité | Configuration des services leurres |

---

## Avertissement légal

Ce honeypot est destiné à un usage **éducatif et défensif uniquement**.  
Ne pas déployer sur une infrastructure sans autorisation explicite du responsable système.  
L'utilisation en environnement de production doit respecter la réglementation locale (RGPD, loi informatique et libertés).

---

> *"Être le chef, c'est savoir avant que ça arrive."* — Robin

---

*Projet développé avec assistance IA.*
