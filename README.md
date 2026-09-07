# Descargador de Videos

Aplicación de escritorio para descargar un video por vez en macOS o Windows. El usuario final no necesita instalar Python, yt-dlp ni FFmpeg.

## Funciones

- Descarga desde YouTube y los sitios compatibles con yt-dlp.
- Calidad automática, 1080p, 720p, 480p o 360p.
- Progreso, velocidad, tiempo restante y cancelación.
- Descargas reanudables e historial para no duplicar videos.
- Cookies opcionales de Chrome, Edge, Firefox, Brave, Opera o Vivaldi.
- Botón **Revisar y actualizar**: actualiza yt-dlp e instala FFmpeg si falta, sin permisos de administrador.
- Binarios independientes para macOS y Windows.

Usa esta aplicación únicamente para contenido propio o que tengas permiso legal de descargar. Algunos servicios prohíben las descargas en sus condiciones de uso.

## Ejecutar el código

```bash
python -m venv .venv
```

Comprueba primero que el Python de desarrollo incluye la interfaz gráfica:

```bash
python scripts/check_environment.py
```

macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Crear la aplicación instalable

Desde el sistema para el que quieras compilar:

```bash
python scripts/prepare_build.py
pyinstaller --clean --noconfirm UniversalVideoDownloader.spec
```

El resultado queda en `dist/`. PyInstaller no permite generar un `.exe` de Windows desde macOS; por eso el workflow de GitHub Actions compila ambos sistemas en máquinas separadas.

En una PC Windows también puedes hacer doble clic en `CREAR_WINDOWS.bat`. El asistente instala Python mediante Winget si hace falta y crea `dist\DescargadorVideos-Windows.zip` automáticamente.

## Publicar macOS y Windows automáticamente

Sube el proyecto a GitHub y ejecuta **Actions → Compilar macOS y Windows → Run workflow**. También se ejecuta al crear una etiqueta como `v2.0.0`. Al terminar, descarga los artefactos de macOS y Windows desde la ejecución.

### Nota de distribución

Para compartir públicamente sin advertencias del sistema, firma el `.exe` con un certificado de firma de código y firma/notariza la app de macOS con una cuenta de Apple Developer. La compilación funciona sin esas credenciales, pero macOS Gatekeeper y Windows SmartScreen pueden mostrar una advertencia.
