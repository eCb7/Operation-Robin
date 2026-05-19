"""
HTTP Trap — fake admin panel, captures credential stuffing & path scanning.
"""

import socket
import threading
from robin import display, logger

_LOGIN_PAGE = b"""\
HTTP/1.1 200 OK\r
Content-Type: text/html; charset=utf-8\r
Server: Apache/2.4.57 (Ubuntu)\r
Connection: close\r
\r
<!DOCTYPE html>
<html>
<head><title>Admin Login</title></head>
<body>
  <h2>Administration Panel</h2>
  <form method="POST" action="/admin/login">
    <input type="text"     name="username" placeholder="Username" /><br/>
    <input type="password" name="password" placeholder="Password" /><br/>
    <button type="submit">Login</button>
  </form>
</body>
</html>
"""

_UNAUTH = b"""\
HTTP/1.1 401 Unauthorized\r
Content-Type: text/plain\r
WWW-Authenticate: Basic realm="Admin"\r
Connection: close\r
\r
401 Unauthorized\r
"""

_NOT_FOUND = b"""\
HTTP/1.1 404 Not Found\r
Content-Type: text/plain\r
Connection: close\r
\r
404 Not Found\r
"""


def _respond(path: str, method: str) -> bytes:
    if path in ("/", "/admin", "/admin/", "/login", "/wp-admin", "/phpmyadmin"):
        return _LOGIN_PAGE
    if path in ("/admin/login",) and method == "POST":
        return _UNAUTH
    return _NOT_FOUND


def _parse_request(raw: str) -> tuple[str, str]:
    lines = raw.splitlines()
    if not lines:
        return "GET", "/"
    parts = lines[0].split()
    method = parts[0] if len(parts) > 0 else "GET"
    path   = parts[1] if len(parts) > 1 else "/"
    return method, path


def _handle(conn: socket.socket, addr: tuple, cfg: dict):
    ip, port = addr[0], addr[1]
    payload = ""
    try:
        conn.settimeout(cfg.get("timeout", 10))
        data = conn.recv(4096)
        payload = data.decode(errors="replace") if data else ""
        method, path = _parse_request(payload)
        conn.sendall(_respond(path, method))
    except (OSError, socket.timeout):
        pass
    finally:
        conn.close()

    display.alert_connection("HTTP", ip, port, payload)
    logger.record("HTTP", ip, port, payload, extra={"path": _parse_request(payload)[1]})


def start(cfg: dict, stop_event: threading.Event):
    host = cfg.get("host", "0.0.0.0")
    port = cfg.get("http_port", 8080)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(50)
    srv.settimeout(1)

    display.info(f"HTTP trap listening on {host}:{port}")

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
