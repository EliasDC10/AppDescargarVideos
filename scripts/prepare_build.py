"""Descarga los componentes correctos para el sistema que realiza la compilación."""

import os
import shutil
import stat
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def download(url, destination):
    print(f"Descargando {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "DescargadorVideos-build/2.0"})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def executable(path):
    if sys.platform != "win32":
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    if sys.platform not in {"darwin", "win32"}:
        raise SystemExit("La distribución oficial se compila en macOS o Windows.")
    ffmpeg_dir = ROOT / "ffmpeg"
    tools_dir = ROOT / "tools"
    ffmpeg_dir.mkdir(exist_ok=True)
    tools_dir.mkdir(exist_ok=True)
    suffix = ".exe" if sys.platform == "win32" else ""
    ytdlp_asset = "yt-dlp.exe" if sys.platform == "win32" else "yt-dlp_macos"
    ytdlp = tools_dir / f"yt-dlp{suffix}"
    download(f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{ytdlp_asset}", ytdlp)
    executable(ytdlp)

    ffmpeg_url = (
        "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        if sys.platform == "win32" else "https://evermeet.cx/ffmpeg/getrelease/zip"
    )
    with tempfile.TemporaryDirectory(prefix="video-build-") as temporary:
        archive = Path(temporary) / "ffmpeg.zip"
        download(ffmpeg_url, archive)
        wanted = f"ffmpeg{suffix}"
        with zipfile.ZipFile(archive) as package:
            member = next(m for m in package.namelist() if Path(m).name.lower() == wanted.lower())
            target = ffmpeg_dir / wanted
            temporary_target = ffmpeg_dir / f"{wanted}.download"
            with package.open(member) as source, temporary_target.open("wb") as output:
                shutil.copyfileobj(source, output)
            executable(temporary_target)
            os.replace(temporary_target, target)
    print("Componentes de compilación listos.")


if __name__ == "__main__":
    main()
