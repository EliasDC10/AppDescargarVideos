"""Ventana principal."""

import os
import subprocess
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from src.components import component_status, repair_components
from src.config import APPEARANCE_MODE, APP_NAME, BROWSERS, COLOR_THEME, WINDOW_HEIGHT, WINDOW_WIDTH
from src.engine import Downloader
from src.widgets import Widgets

ctk.set_appearance_mode(APPEARANCE_MODE)
ctk.set_default_color_theme(COLOR_THEME)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(780, 680)
        self.browser = ctk.StringVar(value=BROWSERS[0])
        self.quality = ctk.StringVar(value="Mejor calidad")
        Widgets(self).crear()
        self.downloader = Downloader(self)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.after(250, self.mostrar_componentes)

    def examinar(self):
        carpeta = filedialog.askdirectory(initialdir=self.entry_destino.get() or str(Path.home()))
        if carpeta:
            self.entry_destino.delete(0, "end")
            self.entry_destino.insert(0, carpeta)

    def descargar(self):
        self.downloader.iniciar()

    def cancelar(self):
        self.downloader.cancelar()

    def escribir(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", str(texto) + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def limpiar_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")

    def actualizar_progreso(self, value, velocidad="-", eta="-"):
        self.progress.set(max(0, min(value, 1)))
        self.lbl_estado.configure(text=f"Estado: Descargando... {value:.0%}")
        self.lbl_velocidad.configure(text=f"Velocidad: {velocidad or '-'}")
        self.lbl_eta.configure(text=f"Tiempo restante: {eta or '-'}")

    def preparar_descarga(self, activa):
        self.btn_descargar.configure(state="disabled" if activa else "normal")
        self.btn_cancelar.configure(state="normal" if activa else "disabled")
        if activa:
            self.progress.set(0)

    def mostrar_componentes(self):
        states = component_status()
        summary = "  •  ".join(f"{name}: {'listo' if ok else 'falta'}" for name, ok, _ in states)
        self.lbl_componentes.configure(text=summary)

    def reparar(self):
        if self.downloader.esta_descargando():
            messagebox.showwarning(APP_NAME, "Espera a que termine o cancela la descarga actual.")
            return
        self.btn_actualizar.configure(state="disabled", text="Actualizando...")
        self.lbl_estado.configure(text="Estado: Revisando componentes...")

        def log(message):
            self.after(0, lambda: self.escribir(message))

        def progress(value):
            self.after(0, lambda: self.progress.set(value))

        def work():
            try:
                messages = repair_components(log=log, progress=progress)
                for message in messages:
                    log(message)
                self.after(0, lambda: self.lbl_estado.configure(text="Estado: Componentes listos"))
                self.after(0, lambda: messagebox.showinfo(APP_NAME, "Todos los componentes están listos."))
            except Exception as error:
                error_message = str(error)
                log(f"ERROR AL ACTUALIZAR: {error_message}")
                self.after(0, lambda: self.lbl_estado.configure(text="Estado: Error de actualización"))
                self.after(0, lambda message=error_message: messagebox.showerror(APP_NAME, f"No fue posible actualizar:\n\n{message}"))
            finally:
                self.after(0, self.mostrar_componentes)
                self.after(0, lambda: self.btn_actualizar.configure(state="normal", text="↻ Revisar y actualizar"))

        threading.Thread(target=work, daemon=True).start()

    def abrir_destino(self):
        destination = Path(self.entry_destino.get().strip())
        if not destination.is_dir():
            messagebox.showwarning(APP_NAME, "Selecciona primero una carpeta válida.")
            return
        if sys.platform == "win32":
            os.startfile(destination)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(destination)])
        else:
            subprocess.Popen(["xdg-open", str(destination)])

    def cerrar(self):
        if self.downloader.esta_descargando():
            if not messagebox.askyesno(APP_NAME, "Hay una descarga activa. ¿Deseas cancelarla y salir?"):
                return
            self.downloader.cancelar()
        self.destroy()
