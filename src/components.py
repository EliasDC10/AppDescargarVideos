"""Localiza y repara los componentes externos usados por la aplicación."""

from __future__ import annotations

import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from src.config import APP_NAME


def app_data_dir() -> Path:
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    path = root / APP_NAME.replace(" ", "")
    path.mkdir(parents=True, exist_ok=True)
    return path


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))


def executable_name(name: str) -> str:
    return f"{name}.exe" if sys.platform == "win32" else name


def find_ffmpeg() -> Path | None:
    name = executable_name("ffmpeg")
    candidates = [app_data_dir() / "tools" / name, resource_dir() / "ffmpeg" / name]
    system = shutil.which("ffmpeg")
    if system:
        candidates.append(Path(system))
    return next((p for p in candidates if p.is_file()), None)


def find_ytdlp() -> Path | None:
    name = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp"
    candidates = [app_data_dir() / "tools" / name, resource_dir() / "tools" / name]
    system = shutil.which("yt-dlp")
    if system:
        candidates.append(Path(system))
    return next((p for p in candidates if p.is_file()), None)


def executable_works(path: Path | None, version_flag: str = "--version") -> bool:
    if not path:
        return False
    try:
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        result = subprocess.run(
            [str(path), version_flag], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=10, creationflags=creationflags,
        )
        return result.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def component_status() -> list[tuple[str, bool, str]]:
    ffmpeg = find_ffmpeg()
    ytdlp = find_ytdlp()
    return [
        ("yt-dlp", executable_works(ytdlp) if ytdlp else True, str(ytdlp) if ytdlp else "motor integrado"),
        ("FFmpeg", executable_works(ffmpeg, "-version"), str(ffmpeg) if ffmpeg else "no instalado"),
    ]


def _download(url: str, destination: Path, progress=None) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "DescargadorVideos/2.0"})
    with urllib.request.urlopen(request, timeout=45) as response, destination.open("wb") as output:
        total = int(response.headers.get("Content-Length", 0))
        received = 0
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            output.write(chunk)
            received += len(chunk)
            if progress and total:
                progress(min(received / total, 1.0))


def _make_executable(path: Path) -> None:
    if sys.platform != "win32":
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _install_ytdlp(tools: Path, progress=None) -> Path:
    if sys.platform == "win32":
        asset, name = "yt-dlp.exe", "yt-dlp.exe"
    elif sys.platform == "darwin":
        asset, name = "yt-dlp_macos", "yt-dlp"
    else:
        asset, name = "yt-dlp", "yt-dlp"
    target = tools / name
    temporary = target.with_suffix(target.suffix + ".download")
    try:
        _download(f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{asset}", temporary, progress)
        _make_executable(temporary)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def _install_ffmpeg(tools: Path, progress=None) -> Path:
    if sys.platform == "darwin":
        url = "https://evermeet.cx/ffmpeg/getrelease/zip"
    elif sys.platform == "win32":
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    else:
        raise RuntimeError("En Linux instala FFmpeg con el gestor de paquetes del sistema.")

    with tempfile.TemporaryDirectory(prefix="video-downloader-") as temp_name:
        archive = Path(temp_name) / "ffmpeg.zip"
        _download(url, archive, progress)
        with zipfile.ZipFile(archive) as package:
            wanted = executable_name("ffmpeg")
            member = next((m for m in package.namelist() if Path(m).name.lower() == wanted.lower()), None)
            if not member:
                raise RuntimeError("El paquete descargado no contiene FFmpeg.")
            target = tools / wanted
            temporary = target.with_suffix(target.suffix + ".download")
            try:
                with package.open(member) as source, temporary.open("wb") as output:
                    shutil.copyfileobj(source, output)
                _make_executable(temporary)
                os.replace(temporary, target)
            finally:
                temporary.unlink(missing_ok=True)
            return target


def repair_components(log=None, progress=None) -> list[str]:
    """Actualiza yt-dlp e instala FFmpeg cuando no está disponible."""
    if sys.platform not in {"darwin", "win32", "linux"}:
        raise RuntimeError(f"Sistema no compatible: {platform.system()}")
    tools = app_data_dir() / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    messages: list[str] = []
    if log:
        log("Actualizando el motor yt-dlp...")
    ytdlp = _install_ytdlp(tools, progress)
    messages.append(f"yt-dlp listo: {ytdlp}")
    ffmpeg = find_ffmpeg()
    if executable_works(ffmpeg, "-version"):
        messages.append(f"FFmpeg listo: {ffmpeg}")
    else:
        if log:
            log("FFmpeg no está instalado; descargándolo...")
        ffmpeg = _install_ffmpeg(tools, progress)
        messages.append(f"FFmpeg instalado: {ffmpeg}")
    return messages
