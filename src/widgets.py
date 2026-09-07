"""Controles de la interfaz."""

from pathlib import Path
from tkinter.scrolledtext import ScrolledText

import customtkinter as ctk

from src.config import APP_NAME, APP_VERSION, BROWSERS, QUALITY


class Widgets:
    def __init__(self, app):
        self.app = app

    def crear(self):
        ctk.CTkLabel(self.app, text=APP_NAME, font=("Arial", 28, "bold")).pack(pady=(18, 2))
        ctk.CTkLabel(self.app, text=f"Versión {APP_VERSION} · macOS y Windows", text_color="gray60").pack(pady=(0, 14))
        form = ctk.CTkFrame(self.app)
        form.pack(fill="x", padx=20, pady=(0, 10))
        ctk.CTkLabel(form, text="Enlace del video").pack(anchor="w", padx=15, pady=(12, 0))
        self.app.entry_url = ctk.CTkEntry(form, height=38, placeholder_text="https://...")
        self.app.entry_url.pack(fill="x", padx=15, pady=(4, 10))
        ctk.CTkLabel(form, text="Guardar en").pack(anchor="w", padx=15)
        destination = ctk.CTkFrame(form, fg_color="transparent")
        destination.pack(fill="x", padx=15, pady=(4, 10))
        self.app.entry_destino = ctk.CTkEntry(destination)
        self.app.entry_destino.insert(0, str(Path.home() / "Downloads"))
        self.app.entry_destino.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(destination, text="Examinar", width=100, command=self.app.examinar).pack(side="left")
        ctk.CTkButton(destination, text="Abrir", width=75, fg_color="gray35", command=self.app.abrir_destino).pack(side="left", padx=(8, 0))
        choices = ctk.CTkFrame(form, fg_color="transparent")
        choices.pack(fill="x", padx=15, pady=(0, 12))
        quality = ctk.CTkFrame(choices, fg_color="transparent")
        quality.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkLabel(quality, text="Calidad").pack(anchor="w")
        ctk.CTkComboBox(quality, values=list(QUALITY), variable=self.app.quality, state="readonly").pack(fill="x", pady=(4, 0))
        browser = ctk.CTkFrame(choices, fg_color="transparent")
        browser.pack(side="left", fill="x", expand=True, padx=(8, 0))
        ctk.CTkLabel(browser, text="Cookies (solo si el sitio las necesita)").pack(anchor="w")
        ctk.CTkComboBox(browser, values=BROWSERS, variable=self.app.browser, state="readonly").pack(fill="x", pady=(4, 0))
        buttons = ctk.CTkFrame(self.app, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=5)
        self.app.btn_descargar = ctk.CTkButton(buttons, text="⬇ Descargar", width=170, height=40, command=self.app.descargar)
        self.app.btn_descargar.pack(side="left", padx=(0, 8))
        self.app.btn_cancelar = ctk.CTkButton(buttons, text="Cancelar", width=110, height=40, state="disabled", fg_color="#9b2c2c", command=self.app.cancelar)
        self.app.btn_cancelar.pack(side="left", padx=(0, 8))
        self.app.btn_actualizar = ctk.CTkButton(buttons, text="↻ Revisar y actualizar", width=190, height=40, fg_color="#2f6f4e", command=self.app.reparar)
        self.app.btn_actualizar.pack(side="left")
        ctk.CTkButton(buttons, text="Limpiar", width=85, height=40, fg_color="gray35", command=self.app.limpiar_log).pack(side="right")
        self.app.progress = ctk.CTkProgressBar(self.app)
        self.app.progress.set(0)
        self.app.progress.pack(fill="x", padx=20, pady=(8, 5))
        self.app.lbl_estado = ctk.CTkLabel(self.app, text="Estado: Esperando...")
        self.app.lbl_estado.pack(anchor="w", padx=20)
        info = ctk.CTkFrame(self.app, fg_color="transparent")
        info.pack(fill="x", padx=20)
        self.app.lbl_velocidad = ctk.CTkLabel(info, text="Velocidad: -")
        self.app.lbl_velocidad.pack(side="left")
        self.app.lbl_eta = ctk.CTkLabel(info, text="Tiempo restante: -")
        self.app.lbl_eta.pack(side="left", padx=30)
        self.app.lbl_componentes = ctk.CTkLabel(self.app, text="Comprobando componentes...", text_color="gray60")
        self.app.lbl_componentes.pack(anchor="w", padx=20, pady=(2, 5))
        self.app.log = ScrolledText(self.app, height=10, bg="#171717", fg="#e8e8e8", insertbackground="white", relief="flat", font=("Menlo", 11), state="disabled")
        self.app.log.pack(fill="both", expand=True, padx=20, pady=(0, 18))
