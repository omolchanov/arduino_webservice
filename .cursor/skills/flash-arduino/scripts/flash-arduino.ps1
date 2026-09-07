param(
    [Parameter(Mandatory = $true)]
    [string]$Sketch,
    [string]$Port = "COM8",
    [string]$Fqbn = "arduino:avr:uno"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")
$ArduinoDir = Join-Path $RepoRoot "arduino"
$IncludeFlag = "-I$ArduinoDir"

function Require-ArduinoCli {
    if (-not (Get-Command arduino-cli -ErrorAction SilentlyContinue)) {
        Write-Error "arduino-cli not found on PATH. Install from https://arduino.github.io/arduino-cli/"
    }
}

function Resolve-SketchPath {
    param([string]$SketchName)

    $absolutePaths = @()
    foreach ($candidate in @($SketchName, (Join-Path $RepoRoot $SketchName))) {
        if (Test-Path $candidate) {
            $absolutePaths += (Resolve-Path $candidate).Path
        }
    }

    foreach ($path in ($absolutePaths | Select-Object -Unique)) {
        if (Test-Path $path -PathType Leaf) {
            if ($path -match '\.ino$') {
                return (Resolve-Path (Split-Path $path -Parent)).Path
            }
            continue
        }
        if (Test-Path (Join-Path $path "*.ino")) {
            return (Resolve-Path $path).Path
        }
    }

    $normalized = ($SketchName -replace '[/\\]$', '' -replace '\.ino$', '')
    $leaf = Split-Path $normalized -Leaf
    $candidates = @(
        (Join-Path $ArduinoDir $leaf),
        (Join-Path $ArduinoDir $normalized),
        (Join-Path $RepoRoot $normalized),
        (Join-Path $RepoRoot "arduino\$leaf")
    )

    foreach ($path in ($candidates | Select-Object -Unique)) {
        if (-not (Test-Path $path)) {
            continue
        }
        if (Test-Path (Join-Path $path "*.ino")) {
            return (Resolve-Path $path).Path
        }
    }

    $known = (Get-ChildItem -Path $ArduinoDir -Directory | ForEach-Object { $_.Name }) -join ", "
    throw "Sketch not found: $SketchName. Known sketches under arduino/: $known"
}

Require-ArduinoCli

$coreList = & arduino-cli core list 2>&1
if ($coreList -notmatch "arduino:avr") {
    Write-Host "Installing arduino:avr core..."
    & arduino-cli core update-index
    & arduino-cli core install arduino:avr
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install arduino:avr core"
    }
}

$stopScript = Join-Path $RepoRoot ".cursor\skills\stop-app\scripts\stop-app.ps1"
if (Test-Path $stopScript) {
    Write-Host "Stopping uvicorn and releasing $Port..."
    & powershell -ExecutionPolicy Bypass -File $stopScript
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "stop-app reported issues; continuing with upload."
    }
} else {
    Write-Warning "stop-app script not found; close Serial Monitor and uvicorn manually."
}

$sketchPath = Resolve-SketchPath -SketchName $Sketch
$label = Split-Path $sketchPath -Leaf

Write-Host "Compiling and uploading $label to $Port..."
& arduino-cli compile -b $Fqbn -p $Port -u $sketchPath --build-property "compiler.cpp.extra_flags=$IncludeFlag"
if ($LASTEXITCODE -ne 0) {
    throw "Upload failed: $label"
}

Write-Host "Upload complete: $label -> $Port"
