$ErrorActionPreference = "Stop"

$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $RootDir

$PythonBin = "python"
$PyInstallerBin = "pyinstaller"
if (Test-Path "$RootDir\.venv\Scripts\python.exe") {
    $PythonBin = "$RootDir\.venv\Scripts\python.exe"
}
if (Test-Path "$RootDir\.venv\Scripts\pyinstaller.exe") {
    $PyInstallerBin = "$RootDir\.venv\Scripts\pyinstaller.exe"
}

$Version = & $PythonBin -c "from version import __version__; print(__version__)"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Building PyInstaller bundle for Algoo v$Version..."
& $PyInstallerBin --clean --noconfirm packaging\algoo.spec
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$IsccPath = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $IsccPath)) {
    $IsccCmd = Get-Command iscc -ErrorAction SilentlyContinue
    if ($IsccCmd) {
        $IsccPath = $IsccCmd.Source
    } else {
        throw "Inno Setup 6 (ISCC.exe) not found."
    }
}

Write-Host "Compiling Windows Setup EXE with Inno Setup..."
& $IsccPath "/DAppVersion=$Version" "packaging\windows\algoo.iss"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Write-Host "Created installer: dist\Algoo-Setup-$Version.exe"
