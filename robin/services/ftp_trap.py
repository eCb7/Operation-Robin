"""
FTP Trap — fake FTP server, captures login attempts & command sequences.
"""

import socket
import threading
from robin import display, logger

_BANNER   = b"220 FTP Server Ready\r\n"
_USER_OK  = b"331 Password required for {user}\r\n"
_PASS_FAIL = b"530 Login incorrect.\r\n"
_UNKNOWN  = b"500 Unknown command.\r\n"


def _handle(conn: socket.socket, addr: tuple, cfg: dict):
    ip, port = addr[0], addr[1]
    transcript = []
    try:
        conn.settimeout(cfg.get("timeout", 15))
        conn.sendall(_BANNER)

        for _ in range(20):  # accept up to 20 FTP commands per session
            try:
                data = conn.recv(256)
            except socket.timeout:
                break
            if not data:
                break
            line = data.decode(errors="replace").strip()
            transcript.append(line)
            cmd = line.split()[0].upper() if line.split() else ""

            if cmd == "USER":
                user = line[5:] if len(line) > 5 else "?"
                conn.sendall(_USER_OK.replace(b"{user}", user.encode()))
            elif cmd == "PASS":
                conn.sendall(_PASS_FAIL)
                break
            elif cmd == "QUIT":
                conn.sendall(b"221 Goodbye.\r\n")
                break
            else:
                conn.sendall(_UNKNOWN)
    except (OSError, socket.timeout):
        pass
    finally:
        conn.close()

    payload = " | ".join(transcript)
    display.alert_connection("FTP", ip, port, payload)
    logger.record("FTP", ip, port, payload)


def start(cfg: dict, stop_event: threading.Event):
    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("ftp_port", 2121)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(50)
    srv.settimeout(1)

    display.info(f"FTP  trap listening on {host}:{port}")

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
