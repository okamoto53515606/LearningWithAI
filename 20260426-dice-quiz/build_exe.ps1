# build_exe.ps1 - Build 5 game exes with PyInstaller
# Usage: .\build_exe.ps1

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot
Set-Location $proj
$env:VIRTUAL_ENV = $null

Remove-Item -Recurse -Force "build","dist" -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Filter "*.spec" -ErrorAction SilentlyContinue | Remove-Item -Force

$games = @(
    @{ name="01_machigai_sagashi";  file="main.py" },
    @{ name="02_kanji_quiz";         file="kanji.py" },
    @{ name="03_kisetsu_quiz";       file="kisetsu.py" },
    @{ name="04_time_attack";        file="timeattack.py" },
    @{ name="05_gekimuzu";           file="gekimuzu.py" }
)

foreach ($g in $games) {
    Write-Host ("=== Building " + $g.name + " ===") -ForegroundColor Cyan
    uv run --project $proj pyinstaller `
        --onefile --windowed --noconfirm `
        --name $g.name `
        $g.file
}

Write-Host ""
Write-Host "=== ALL DONE ===" -ForegroundColor Green
Get-ChildItem dist\*.exe | ForEach-Object {
    $mb = [math]::Round($_.Length/1MB, 1)
    $line = '  ' + $_.Name + ' - ' + $mb + ' MiB'
    Write-Host $line
}
