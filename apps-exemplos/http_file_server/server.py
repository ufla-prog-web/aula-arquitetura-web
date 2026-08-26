#!/usr/bin/env python3
"""Servidor de arquivos didatico usando apenas a biblioteca padrao do Python.

Recursos:
- Interface web responsiva
- Upload via HTTP PUT
- Listagem via API JSON
- Download via HTTP GET
- Exclusao via HTTP DELETE
- Busca no navegador

Nao e recomendado expor este servidor diretamente na Internet sem adicionar
HTTPS, autenticacao, controle de acesso e outras protecoes de producao.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"
DEFAULT_SHARED_DIR = BASE_DIR / "shared"
DEFAULT_MAX_UPLOAD_MB = 100


class FileServer(HTTPServer):
    """HTTPServer com configuracoes acessiveis pelo handler."""

    def __init__(self, server_address, handler_class, storage_dir: Path, max_upload_bytes: int):
        super().__init__(server_address, handler_class)
        self.storage_dir = storage_dir
        self.max_upload_bytes = max_upload_bytes


class FileServerHandler(BaseHTTPRequestHandler):
    server_version = "FileBoxHTTP/1.0"

    def log_message(self, format: str, *args) -> None:
        now = datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {self.client_address[0]} - {format % args}")

    # ------------------------------
    # Helpers
    # ------------------------------
    def _send_bytes(
        self,
        data: bytes,
        status: int = 200,
        content_type: str = "application/octet-stream",
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, payload, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send_bytes(data, status, "application/json; charset=utf-8")

    def _send_error_json(self, message: str, status: int) -> None:
        self._send_json({"ok": False, "error": message}, status)

    def _serve_static(self, relative_path: str) -> None:
        requested = (WEB_DIR / relative_path).resolve()
        try:
            requested.relative_to(WEB_DIR.resolve())
        except ValueError:
            self._send_error_json("Caminho invalido.", 400)
            return

        if not requested.is_file():
            self._send_error_json("Recurso nao encontrado.", 404)
            return

        mime, _ = mimetypes.guess_type(str(requested))
        self._send_bytes(
            requested.read_bytes(),
            200,
            (mime or "application/octet-stream") + ("; charset=utf-8" if mime and mime.startswith("text/") else ""),
        )

    def _safe_file_path(self, encoded_name: str) -> Path | None:
        name = unquote(encoded_name)
        if not name or name in {".", ".."}:
            return None
        if "/" in name or "\\" in name or Path(name).name != name:
            return None

        target = (self.server.storage_dir / name).resolve()
        try:
            target.relative_to(self.server.storage_dir.resolve())
        except ValueError:
            return None
        return target

    # ------------------------------
    # HTTP methods
    # ------------------------------
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._serve_static("index.html")
            return

        if path == "/style.css":
            self._serve_static("style.css")
            return

        if path == "/app.js":
            self._serve_static("app.js")
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if path == "/api/files":
            self._list_files()
            return

        if path.startswith("/files/"):
            self._download_file(path[len("/files/"):])
            return

        self._send_error_json("Rota nao encontrada.", 404)

    def do_PUT(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/files/"):
            self._upload_file(parsed.path[len("/api/files/"):])
            return
        self._send_error_json("Rota nao encontrada.", 404)

    def do_DELETE(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/files/"):
            self._delete_file(parsed.path[len("/api/files/"):])
            return
        self._send_error_json("Rota nao encontrada.", 404)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Allow", "GET, PUT, DELETE, OPTIONS")
        self.end_headers()

    # ------------------------------
    # API
    # ------------------------------
    def _list_files(self) -> None:
        files = []
        for item in sorted(self.server.storage_dir.iterdir(), key=lambda p: p.name.lower()):
            if not item.is_file() or item.name == ".gitkeep":
                continue
            stat = item.stat()
            files.append(
                {
                    "name": item.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                    "download_url": "/files/" + quote(item.name, safe=""),
                }
            )

        self._send_json(
            {
                "ok": True,
                "files": files,
                "count": len(files),
                "max_upload_bytes": self.server.max_upload_bytes,
            }
        )

    def _upload_file(self, encoded_name: str) -> None:
        target = self._safe_file_path(encoded_name)
        if target is None:
            self._send_error_json("Nome de arquivo invalido.", 400)
            return

        length_header = self.headers.get("Content-Length")
        if length_header is None:
            self._send_error_json("Content-Length obrigatorio.", 411)
            return

        try:
            content_length = int(length_header)
        except ValueError:
            self._send_error_json("Content-Length invalido.", 400)
            return

        if content_length < 0:
            self._send_error_json("Tamanho invalido.", 400)
            return

        if content_length > self.server.max_upload_bytes:
            self._send_error_json("Arquivo excede o limite configurado.", 413)
            return

        existed = target.exists()
        temp_target = target.with_name(target.name + ".uploading")

        remaining = content_length
        try:
            with temp_target.open("wb") as output:
                while remaining > 0:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk:
                        raise ConnectionError("Upload interrompido antes do fim.")
                    output.write(chunk)
                    remaining -= len(chunk)
            os.replace(temp_target, target)
        except Exception as exc:
            if temp_target.exists():
                temp_target.unlink(missing_ok=True)
            self._send_error_json(f"Falha no upload: {exc}", 500)
            return

        self._send_json(
            {
                "ok": True,
                "message": "Arquivo atualizado." if existed else "Arquivo enviado.",
                "name": target.name,
                "size": target.stat().st_size,
            },
            200 if existed else 201,
        )

    def _download_file(self, encoded_name: str) -> None:
        target = self._safe_file_path(encoded_name)
        if target is None or not target.is_file():
            self._send_error_json("Arquivo nao encontrado.", 404)
            return

        mime, _ = mimetypes.guess_type(str(target))
        size = target.stat().st_size

        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Content-Length", str(size))
        self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(target.name, safe='')}")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()

        with target.open("rb") as source:
            while True:
                chunk = source.read(1024 * 1024)
                if not chunk:
                    break
                self.wfile.write(chunk)

    def _delete_file(self, encoded_name: str) -> None:
        target = self._safe_file_path(encoded_name)
        if target is None or not target.is_file():
            self._send_error_json("Arquivo nao encontrado.", 404)
            return

        try:
            target.unlink()
        except OSError as exc:
            self._send_error_json(f"Nao foi possivel excluir o arquivo: {exc}", 500)
            return

        self._send_json({"ok": True, "message": "Arquivo excluido.", "name": target.name})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Servidor de arquivos com interface web usando HTTPServer.")
    parser.add_argument("--host", default="127.0.0.1", help="Endereco para escuta (padrao: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Porta TCP (padrao: 8000)")
    parser.add_argument(
        "--directory",
        type=Path,
        default=DEFAULT_SHARED_DIR,
        help="Diretorio usado para armazenar os arquivos.",
    )
    parser.add_argument(
        "--max-upload-mb",
        type=int,
        default=DEFAULT_MAX_UPLOAD_MB,
        help=f"Tamanho maximo de upload em MB (padrao: {DEFAULT_MAX_UPLOAD_MB}).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    storage_dir = args.directory.expanduser().resolve()
    storage_dir.mkdir(parents=True, exist_ok=True)

    max_upload_bytes = max(1, args.max_upload_mb) * 1024 * 1024
    server = FileServer((args.host, args.port), FileServerHandler, storage_dir, max_upload_bytes)

    print("=" * 62)
    print(" FileBox - servidor de arquivos com HTTPServer")
    print("=" * 62)
    print(f" Interface:  http://{args.host}:{args.port}")
    print(f" Arquivos:   {storage_dir}")
    print(f" Limite:     {args.max_upload_mb} MB por arquivo")
    print(" Pressione Ctrl+C para encerrar.")
    print("=" * 62)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
