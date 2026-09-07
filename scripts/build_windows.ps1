$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host "Preparando Descargador de Videos para Windows..." -ForegroundColor Cyan

$pythonCommand = $null
$pythonPrefix = @()

if (Get-Command py.exe -ErrorAction SilentlyContinue) {
    try {
        & py.exe -3.13 -c "import sys; assert sys.version_info >= (3, 10)"
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = "py.exe"
            $pythonPrefix = @("-3.13")
        }
    } catch {}
}

if (-not $pythonCommand -and (Get-Command python.exe -ErrorAction SilentlyContinue)) {
    try {
        & python.exe -c "import sys; assert sys.version_info >= (3, 10)"
        if ($LASTEXITCODE -eq 0) { $pythonCommand = "python.exe" }
    } catch {}
}

if (-not $pythonCommand) {
    if (-not (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        throw "Faltan Python 3.10 o posterior y Winget. Instala Python desde https://python.org y vuelve a ejecutar este archivo."
    }
    Write-Host "Python no esta instalado. Instalando Python 3.13..." -ForegroundColor Yellow
    & winget.exe install --id Python.Python.3.13 --exact --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "Winget no pudo instalar Python." }
    $installedPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python313\python.exe"
    if (-not (Test-Path $installedPython)) { throw "Python se instalo, pero no se encontro. Reinicia esta ventana y prueba otra vez." }
    $pythonCommand = $installedPython
}

Write-Host "Creando entorno de compilacion..."
& $pythonCommand @pythonPrefix -m venv .build-windows
$venvPython = Join-Path $PWD ".build-windows\Scripts\python.exe"
$pyinstaller = Join-Path $PWD ".build-windows\Scripts\pyinstaller.exe"

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt
& $venvPython scripts\prepare_build.py
& $pyinstaller --clean --noconfirm UniversalVideoDownloader.spec

$zip = Join-Path $PWD "dist\DescargadorVideos-Windows.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "dist\Descargador de Videos\*" -DestinationPath $zip

Write-Host ""
Write-Host "LISTO: $zip" -ForegroundColor Green
Write-Host "Descomprime el ZIP antes de abrir Descargador de Videos.exe."
