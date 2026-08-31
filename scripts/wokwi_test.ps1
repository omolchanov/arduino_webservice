param(
    [string]$Fqbn = "arduino:avr:uno",
    [int]$TimeoutMs = 45000
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ArduinoDir = Join-Path $RepoRoot "arduino"
$ArduinoTestsDir = Join-Path $RepoRoot "arduino-tests"
$IncludeFlag = "-I$ArduinoDir"

function Require-Command {
    param([string]$Name, [string]$InstallHint)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "$Name not found on PATH. $InstallHint"
    }
}

function Require-WokwiToken {
    if (-not $env:WOKWI_CLI_TOKEN) {
        Write-Error "WOKWI_CLI_TOKEN is not set. Create a token at https://wokwi.com/dashboard/ci and set `$env:WOKWI_CLI_TOKEN."
    }
}

Require-Command "arduino-cli" "Install from https://arduino.github.io/arduino-cli/"
Require-Command "wokwi-cli" "Install from https://docs.wokwi.com/wokwi-ci/cli-installation"
Require-WokwiToken

$coreList = & arduino-cli core list 2>&1
if ($coreList -notmatch "arduino:avr") {
    Write-Host "Installing arduino:avr core..."
    & arduino-cli core update-index
    & arduino-cli core install arduino:avr
}

Write-Host "Installing AUnit library..."
& arduino-cli lib install "AUnit"
if ($LASTEXITCODE -ne 0) {
    Write-Warning "AUnit install returned exit code $LASTEXITCODE (may already be installed)"
}

$testProjects = Get-ChildItem -Path $ArduinoTestsDir -Directory -Filter "test_*" | Sort-Object Name
$failed = @()

foreach ($project in $testProjects) {
    $name = $project.Name
    $buildDir = Join-Path $project.FullName "build"
    Write-Host "==== $name ===="
    Write-Host "Compiling $name..."
    & arduino-cli compile -b $Fqbn $project.FullName `
        --build-property "compiler.cpp.extra_flags=$IncludeFlag" `
        --output-dir $buildDir
    if ($LASTEXITCODE -ne 0) {
        $failed += "$name (compile)"
        continue
    }

    Write-Host "Running Wokwi simulation for $name..."
    Push-Location $project.FullName
    try {
        & wokwi-cli . --scenario aunit.test.yaml --timeout $TimeoutMs
        if ($LASTEXITCODE -ne 0) {
            $failed += "$name (wokwi)"
        } else {
            Write-Host "PASS: $name"
        }
    } finally {
        Pop-Location
    }
}

if ($failed.Count -gt 0) {
    Write-Error "Wokwi tests failed: $($failed -join ', ')"
}

Write-Host "All Wokwi AUnit tests passed."
