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
    param([string]$Name)

    $normalized = $Name.Trim().TrimEnd('.', '/', '\')
    if ($normalized.EndsWith(".ino")) {
        $normalized = Split-Path $normalized -Parent
    }
    $normalized = $normalized -replace "\\", "/"

    if ($normalized -match "^arduino/") {
        $candidate = Join-Path $RepoRoot ($normalized -replace "/", [IO.Path]::DirectorySeparatorChar)
    }
    elseif ($normalized -match "^arduino-tests/") {
        $candidate = Join-Path $RepoRoot ($normalized -replace "/", [IO.Path]::DirectorySeparatorChar)
    }
    else {
        $candidate = Join-Path $ArduinoDir $normalized
    }

    if (-not (Test-Path $candidate)) {
        $known = @(
            "valves",
            "simple01",
            "sensors",
            "mulie_function",
            "mux"
        ) -join ", "
        Write-Error "Sketch not found: $candidate. Known production sketches: $known"
    }

    $ino = Get-ChildItem -Path $candidate -Filter "*.ino" -File | Select-Object -First 1
    if (-not $ino) {
        Write-Error "No .ino file in sketch folder: $candidate"
    }

    return $candidate
}

Require-ArduinoCli
$sketchPath = Resolve-SketchPath -Name $Sketch
$sketchLabel = Split-Path $sketchPath -Leaf

Write-Host "Flashing $sketchLabel to $Port ($Fqbn)..."
Write-Host "Sketch path: $sketchPath"

& arduino-cli compile -b $Fqbn -p $Port -u $sketchPath --build-property "compiler.cpp.extra_flags=$IncludeFlag"
if ($LASTEXITCODE -ne 0) {
    throw "Upload failed: $sketchLabel"
}

Write-Host "Upload complete: $sketchLabel -> $Port"
