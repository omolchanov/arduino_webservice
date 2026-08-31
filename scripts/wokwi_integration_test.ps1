param(
    [string]$Fqbn = "arduino:avr:uno",
    [int]$TimeoutMs = 120000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ArduinoDir = Join-Path $RepoRoot "arduino"
$IncludeFlag = "-I$ArduinoDir"

function Require-Command {
    param([string]$Name, [string]$InstallHint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "$Name not found on PATH. $InstallHint"
    }
}

function Require-WokwiToken {
    if (-not $env:WOKWI_CLI_TOKEN) {
        Write-Error "WOKWI_CLI_TOKEN is not set. Create a token at https://wokwi.com/dashboard/ci"
    }
}

Require-Command "arduino-cli" "Install from https://arduino.github.io/arduino-cli/"
Require-Command "wokwi-cli" "Install from https://docs.wokwi.com/wokwi-ci/cli-installation"
Require-WokwiToken

$coreList = & arduino-cli core list 2>&1
if ($coreList -notmatch "arduino:avr") {
    & arduino-cli core update-index
    & arduino-cli core install arduino:avr
}

$failed = @()

Get-ChildItem -Path $ArduinoDir -Directory | ForEach-Object {
    $sketchDir = $_.FullName
    $name = $_.Name
    $wokwiToml = Join-Path $sketchDir "wokwi.toml"
    if (-not (Test-Path $wokwiToml)) {
        return
    }

    $scenario = Get-ChildItem -Path $sketchDir -Filter "*.integration.yaml" -File |
        Select-Object -First 1
    if (-not $scenario) {
        Write-Host "SKIP: $name (no *.integration.yaml)"
        return
    }

    $buildDir = Join-Path $sketchDir "build"
    $logFile = Join-Path $sketchDir "wokwi-report.log"
    Write-Host "==== $name ===="
    Write-Host "Compiling $name..."
    & arduino-cli compile -b $Fqbn $sketchDir `
        --build-property "compiler.cpp.extra_flags=$IncludeFlag" `
        --output-dir $buildDir
    if ($LASTEXITCODE -ne 0) {
        $failed += "$name (compile)"
        return
    }

    Write-Host "Validating diagram.json..."
    Push-Location $sketchDir
    try {
        & wokwi-cli lint
        if ($LASTEXITCODE -ne 0) {
            $failed += "$name (diagram lint)"
            return
        }

        Write-Host "Uploading diagram.json and firmware to Wokwi Simulation API..."
        & wokwi-cli . --scenario $scenario.Name --timeout $TimeoutMs --serial-log-file wokwi-report.log
        if ($LASTEXITCODE -ne 0) {
            $failed += "$name (wokwi)"
            Write-Host "FAIL: $name (see $logFile)"
        } else {
            Write-Host "PASS: $name (report: $logFile)"
        }
    } finally {
        Pop-Location
    }
}

if ($failed.Count -gt 0) {
    Write-Error "Wokwi integration tests failed: $($failed -join ', ')"
}

Write-Host "All Wokwi integration tests passed."
