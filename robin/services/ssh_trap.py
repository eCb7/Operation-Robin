"""
SSH Trap — fake OpenSSH banner, captures credential attempts.
"""

import socket
import threading
from robin import display, logger

SSH_BANNER = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.6\r\n"

# Fake auth-failure messages to lure multi-attempt brute-forcers
AUTH_FAIL = (
    b"Permission denied (publickey,password).\r\n"
)


def _handle(conn: socket.socket, addr: tuple, cfg: dict):
    ip, port = addr[0], addr[1]
    payload = ""
    try:
        conn.settimeout(cfg.get("timeout", 10))
        conn.sendall(SSH_BANNER)
        data = conn.recv(1024)
        payload = data.decode(errors="replace") if data else ""
        conn.sendall(AUTH_FAIL)
    except (OSError, socket.timeout):
        pass
    finally:
        conn.close()

    display.alert_connection("SSH", ip, port, payload)
    logger.record("SSH", ip, port, payload)


def start(cfg: dict, stop_event: threading.Event):
    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("ssh_port", 2222)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(50)
    srv.settimeout(1)

    display.info(f"SSH trap listening on {host}:{port}")

    while not stop_event.is_set():
        try:
            conn, addr = srv.accept()
            t = threading.Thread(target=_handle, args=(conn, addr, cfg), daemon=True)
            t.start()
        except socket.timeout:
            continue
        except OSError:
            break

    srv.close()
