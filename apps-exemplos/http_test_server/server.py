#!/usr/bin/env python3
import argparse
import json
import mimetypes
import os
import secrets
from datetime import datetime, timezone
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
MAX_BODY = 2 * 1024 * 1024


def json_bytes(data):
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


def status_phrase(code):
    try:
        return HTTPStatus(code).phrase
    except ValueError:
        return "Status personalizado"


class TestHandler(BaseHTTPRequestHandler):
    server_version = "HTTPStudyServer/1.0"

    def log_message(self, fmt, *args):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {self.client_address[0]} - {fmt % args}")

    # ---------- helpers ----------
    def _send_bytes(self, body, status=200, content_type="application/json; charset=utf-8", extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Lab-Server", "HTTPServer")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, data, status=200, extra_headers=None):
        self._send_bytes(json_bytes(data), status, extra_headers=extra_headers)

    def _read_body(self):
        raw_len = self.headers.get("Content-Length")
        if not raw_len:
            return b""
        try:
            length = int(raw_len)
        except ValueError:
            return b""
        if length > MAX_BODY:
            raise ValueError("Corpo maior que 2 MiB")
        return self.rfile.read(length)

    def _parsed_body(self, body):
        ctype = self.headers.get("Content-Type", "")
        text = body.decode("utf-8", errors="replace")
        parsed = None
        if "application/json" in ctype and text:
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError:
                parsed = "JSON inválido"
        elif "application/x-www-form-urlencoded" in ctype:
            parsed = {k: v for k, v in parse_qs(text, keep_blank_values=True).items()}
        return text, parsed

    def _cookies(self):
        raw = self.headers.get("Cookie", "")
        cookie = SimpleCookie()
        try:
            cookie.load(raw)
        except Exception:
            return {}
        return {k: morsel.value for k, morsel in cookie.items()}

    def _request_snapshot(self, body=b""):
        parsed = urlparse(self.path)
        text, parsed_body = self._parsed_body(body)
        return {
            "method": self.command,
            "path": parsed.path,
            "query_string": parsed.query,
            "query": parse_qs(parsed.query, keep_blank_values=True),
            "http_version": self.request_version,
            "client": {"ip": self.client_address[0], "port": self.client_address[1]},
            "headers": dict(self.headers.items()),
            "cookies": self._cookies(),
            "body": text,
            "parsed_body": parsed_body,
            "received_at": datetime.now(timezone.utc).isoformat(),
        }

    def _serve_static(self, route):
        if route == "/":
            file_path = WEB_DIR / "index.html"
        else:
            relative = route.removeprefix("/web/")
            if ".." in Path(relative).parts:
                self.send_error(403)
                return
            file_path = WEB_DIR / relative

        if not file_path.is_file():
            self.send_error(404)
            return

        content = file_path.read_bytes()
        ctype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in {"application/javascript", "application/json"}:
            ctype += "; charset=utf-8"
        self._send_bytes(content, 200, ctype)

    # ---------- routes ----------
    def _route(self):
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/" or route.startswith("/web/"):
            self._serve_static(route)
            return

        if route == "/api/inspect":
            try:
                body = self._read_body()
            except ValueError as exc:
                self._send_json({"error": str(exc)}, 413)
                return
            self._send_json({
                "message": "Requisição recebida com sucesso.",
                "request": self._request_snapshot(body),
                "response": {
                    "status": 200,
                    "headers": {
                        "Content-Type": "application/json; charset=utf-8",
                        "Cache-Control": "no-store",
                        "X-Lab-Server": "HTTPServer",
                    },
                },
            })
            return

        if route.startswith("/api/status/"):
            try:
                code = int(route.rsplit("/", 1)[1])
            except ValueError:
                self._send_json({"error": "Código inválido"}, 400)
                return
            if code < 100 or code > 599:
                self._send_json({"error": "Use um código entre 100 e 599"}, 400)
                return
            # 1xx não são adequados como resposta final no BaseHTTPRequestHandler.
            if code < 200:
                self._send_json({"error": "Para este laboratório, escolha um status final entre 200 e 599."}, 400)
                return
            payload = {
                "status": code,
                "phrase": status_phrase(code),
                "explanation": f"O servidor respondeu deliberadamente com HTTP {code}.",
            }
            # 204, 205 e 304 não devem carregar corpo de resposta.
            if code in {204, 205, 304}:
                self._send_bytes(b"", code)
            else:
                self._send_json(payload, code)
            return

        if route == "/api/cookies/set":
            query = parse_qs(parsed.query, keep_blank_values=True)
            name = query.get("name", ["lab_cookie"])[0].strip() or "lab_cookie"
            value = query.get("value", [secrets.token_hex(4)])[0]
            max_age = query.get("max_age", ["3600"])[0]
            cookie = SimpleCookie()
            cookie[name] = value
            cookie[name]["path"] = "/"
            if max_age.isdigit():
                cookie[name]["max-age"] = max_age
            cookie[name]["samesite"] = "Lax"
            header_value = cookie.output(header="").strip()
            self._send_json({
                "message": "Cookie enviado ao navegador via Set-Cookie.",
                "cookie": {"name": name, "value": value, "max_age": max_age},
            }, extra_headers={"Set-Cookie": header_value})
            return

        if route == "/api/cookies/delete":
            query = parse_qs(parsed.query, keep_blank_values=True)
            name = query.get("name", ["lab_cookie"])[0].strip() or "lab_cookie"
            expired = f"{name}=; Path=/; Max-Age=0; SameSite=Lax"
            self._send_json({"message": f"Solicitada exclusão do cookie '{name}'."}, extra_headers={"Set-Cookie": expired})
            return

        if route == "/api/cookies/read":
            self._send_json({
                "cookie_header": self.headers.get("Cookie", ""),
                "cookies": self._cookies(),
            })
            return

        if route == "/api/redirect":
            query = parse_qs(parsed.query, keep_blank_values=True)
            target = query.get("to", ["/"])[0] or "/"
            try:
                code = int(query.get("code", ["302"])[0])
            except ValueError:
                code = 302
            if code not in {301, 302, 303, 307, 308}:
                code = 302
            body = json_bytes({"message": "Redirecionamento", "status": code, "location": target})
            self._send_bytes(body, code, extra_headers={"Location": target})
            return

        if route == "/api/headers":
            query = parse_qs(parsed.query, keep_blank_values=True)
            demo_headers = {
                "X-Demo-Header": query.get("x_demo", ["Olá do servidor"])[0],
                "X-Request-Method": self.command,
                "Content-Language": "pt-BR",
            }
            self._send_json({
                "message": "Observe os cabeçalhos da resposta nas DevTools.",
                "response_headers": demo_headers,
            }, extra_headers=demo_headers)
            return

        self._send_json({
            "error": "Endpoint não encontrado",
            "path": route,
            "available": [
                "/api/inspect",
                "/api/status/<200-599>",
                "/api/cookies/set",
                "/api/cookies/read",
                "/api/cookies/delete",
                "/api/redirect",
                "/api/headers",
            ],
        }, 404)

    def do_GET(self):
        self._route()

    def do_POST(self):
        self._route()

    def do_PUT(self):
        self._route()

    def do_PATCH(self):
        self._route()

    def do_DELETE(self):
        self._route()

    def do_OPTIONS(self):
        if urlparse(self.path).path == "/api/inspect":
            body = json_bytes({"message": "Métodos permitidos", "allow": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]})
            self._send_bytes(body, 200, extra_headers={"Allow": "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD"})
        else:
            self._route()

    def do_HEAD(self):
        self._route()


def main():
    parser = argparse.ArgumentParser(description="Laboratório HTTP didático usando HTTPServer")
    parser.add_argument("--host", default=os.getenv("HTTP_LAB_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("HTTP_LAB_PORT", "8000")))
    args = parser.parse_args()

    server = HTTPServer((args.host, args.port), TestHandler)
    print("=" * 64)
    print(" Laboratório HTTP - HTTPServer")
    print(f" Acesse: http://{args.host}:{args.port}")
    print(" CTRL+C para encerrar")
    print("=" * 64)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
