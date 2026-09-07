"""Motor de descarga con soporte para cancelación y progreso."""

from __future__ import annotations

import re
import subprocess
import sys
import threading
from pathlib import Path

from yt_dlp import YoutubeDL

from src.components import find_ffmpeg, find_ytdlp
from src.config import ARCHIVE_FILE, OUTPUT_TEMPLATE, QUALITY


class _Logger:
    def __init__(self, downloader):
        self.downloader = downloader

    def debug(self, message):
        if not message.startswith("[debug]"):
            self.downloader.ui(self.downloader.app.escribir, message)

    info = debug

    def warning(self, message):
        self.downloader.ui(self.downloader.app.escribir, f"AVISO: {message}")

    def error(self, message):
        self.downloader.ui(self.downloader.app.escribir, f"ERROR: {message}")


class Downloader:
    def __init__(self, app):
        self.app = app
        self.cancelado = False
        self.thread: threading.Thread | None = None
        self.process: subprocess.Popen | None = None

    def iniciar(self):
        if self.esta_descargando():
            return
        url = self.app.entry_url.get().strip()
        carpeta = self.app.entry_destino.get().strip()
        if not url.startswith(("http://", "https://")):
            self.app.escribir("Escribe una URL válida que comience con http:// o https://.")
            return
        if not carpeta:
            self.app.escribir("Selecciona una carpeta de destino.")
            return
        self.cancelado = False
        self.app.preparar_descarga(True)
        self.thread = threading.Thread(
            target=self._descargar,
            args=(url, carpeta, QUALITY[self.app.quality.get()], self.app.browser.get()),
            daemon=True,
        )
        self.thread.start()

    def cancelar(self):
        if not self.esta_descargando():
            return
        self.cancelado = True
        self.ui(self.app.lbl_estado.configure, text="Estado: Cancelando...")
        if self.process and self.process.poll() is None:
            self.process.terminate()

    def ui(self, funcion, *args, **kwargs):
        self.app.after(0, lambda: funcion(*args, **kwargs))

    @staticmethod
    def _format_selector(height, ffmpeg_available=True):
        if not ffmpeg_available:
            limit = f"[height<={height}]" if height else ""
            return f"best{limit}/best"
        if height is None:
            return "bestvideo+bestaudio/best"
        return f"bestvideo[height<={height}]+bestaudio/best[height<={height}]"

    def _common_options(self, carpeta, height, navegador):
        ffmpeg = find_ffmpeg()
        options = {
            "format": self._format_selector(height, ffmpeg is not None),
            "outtmpl": str(Path(carpeta) / OUTPUT_TEMPLATE),
            "download_archive": str(Path(carpeta) / ARCHIVE_FILE),
            "continuedl": True,
            "overwrites": False,
            "noplaylist": True,
            "merge_output_format": "mp4",
            "windowsfilenames": sys.platform == "win32",
        }
        if ffmpeg:
            options["ffmpeg_location"] = str(ffmpeg.parent)
        if navegador != "Ninguno":
            options["cookiesfrombrowser"] = (navegador.lower(),)
        return options

    def _progress(self, data):
        if self.cancelado:
            raise RuntimeError("Descarga cancelada por el usuario.")
        if data.get("status") == "downloading":
            downloaded = data.get("downloaded_bytes", 0)
            total = data.get("total_bytes") or data.get("total_bytes_estimate") or 0
            value = downloaded / total if total else 0
            self.ui(self.app.actualizar_progreso, value, data.get("_speed_str", "-"), data.get("_eta_str", "-"))
        elif data.get("status") == "finished":
            self.ui(self.app.lbl_estado.configure, text="Estado: Procesando archivo...")

    def _descargar_api(self, url, carpeta, height, navegador):
        options = self._common_options(carpeta, height, navegador)
        options.update({"progress_hooks": [self._progress], "logger": _Logger(self), "quiet": True})
        with YoutubeDL(options) as ydl:
            result = ydl.download([url])
        if result:
            raise RuntimeError("El motor de descarga informó un error.")

    def _descargar_cli(self, executable, url, carpeta, height, navegador):
        options = self._common_options(carpeta, height, navegador)
        command = [
            str(executable), "--ignore-config", "--newline", "--no-playlist", "--continue", "--no-overwrites",
            "--format", options["format"], "--merge-output-format", "mp4",
            "--output", options["outtmpl"], "--download-archive", options["download_archive"],
            "--progress-template", "download:%(progress._percent_str)s|%(progress._speed_str)s|%(progress._eta_str)s",
        ]
        if "ffmpeg_location" in options:
            command += ["--ffmpeg-location", options["ffmpeg_location"]]
        if navegador != "Ninguno":
            command += ["--cookies-from-browser", navegador.lower()]
        if sys.platform == "win32":
            command.append("--windows-filenames")
        command.append(url)
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", creationflags=creationflags,
        )
        assert self.process.stdout is not None
        pattern = re.compile(r"^download:\s*([\d.]+)%\|([^|]*)\|(.*)$")
        for line in self.process.stdout:
            line = line.rstrip()
            match = pattern.match(line)
            if match:
                self.ui(self.app.actualizar_progreso, float(match.group(1)) / 100, match.group(2), match.group(3))
            elif line:
                self.ui(self.app.escribir, line)
        code = self.process.wait()
        if self.cancelado:
            raise RuntimeError("Descarga cancelada por el usuario.")
        if code:
            raise RuntimeError(f"yt-dlp terminó con el código {code}.")

    def _descargar(self, url, carpeta, height, navegador):
        try:
            Path(carpeta).mkdir(parents=True, exist_ok=True)
            self.ui(self.app.lbl_estado.configure, text="Estado: Analizando enlace...")
            executable = find_ytdlp()
            if executable:
                self._descargar_cli(executable, url, carpeta, height, navegador)
            else:
                self._descargar_api(url, carpeta, height, navegador)
            self.ui(self.app.progress.set, 1)
            self.ui(self.app.lbl_estado.configure, text="Estado: Finalizado")
            self.ui(self.app.escribir, "Descarga finalizada correctamente.")
        except Exception as error:
            state = "Cancelada" if self.cancelado else "Error"
            self.ui(self.app.lbl_estado.configure, text=f"Estado: {state}")
            self.ui(self.app.escribir, f"{state.upper()}: {error}")
        finally:
            self.process = None
            self.ui(self.app.preparar_descarga, False)

    def esta_descargando(self):
        return bool(self.thread and self.thread.is_alive())
