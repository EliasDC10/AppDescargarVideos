"""Configuración de la aplicación."""

APP_NAME = "Descargador de Videos"
APP_VERSION = "2.0.0"
WINDOW_WIDTH = 950
WINDOW_HEIGHT = 760
APPEARANCE_MODE = "dark"
COLOR_THEME = "blue"

BROWSERS = ["Ninguno", "Chrome", "Edge", "Firefox", "Brave", "Opera", "Vivaldi"]

QUALITY = {
    "Mejor calidad": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
    "360p": 360,
}

OUTPUT_TEMPLATE = "%(title).200s_[%(id)s].%(ext)s"
ARCHIVE_FILE = "download_archive.txt"
