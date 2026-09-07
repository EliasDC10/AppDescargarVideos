"""Comprueba que el Python de desarrollo puede crear la interfaz."""

import sys


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Se requiere Python 3.10 o posterior.")
    try:
        import tkinter
    except ImportError as error:
        raise SystemExit(
            "Falta Tkinter. En macOS con Homebrew ejecuta: brew install python-tk@3.14\n"
            "También puedes instalar Python desde https://python.org, que ya lo incluye."
        ) from error
    print(f"Python {sys.version.split()[0]} y Tk {tkinter.TkVersion}: listos.")


if __name__ == "__main__":
    main()
