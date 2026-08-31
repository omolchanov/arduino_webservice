param(
    [string]$Fqbn = "arduino:avr:uno",
    [string]$Port = "",
    [switch]$CompileOnly
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$ArduinoDir = Join-Path $RepoRoot "arduino"
$ArduinoTestsDir = Join-Path $RepoRoot "arduino-tests"
$IncludeFlag = "-I$ArduinoDir"

function Require-ArduinoCli {
    if (-not (Get-Command arduino-cli -ErrorAction SilentlyContinue)) {
        Write-Error "arduino-cli not found on PATH. Install from https://arduino.github.io/arduino-cli/"
    }
}

function Invoke-ArduinoCompile {
    param(
        [string]$SketchPath,
        [string]$Label
    )
    Write-Host "Compiling $Label..."
    & arduino-cli compile -b $Fqbn $SketchPath --build-property "compiler.cpp.extra_flags=$IncludeFlag"
    if ($LASTEXITCODE -ne 0) {
        throw "Compile failed: $Label"
    }
}

Require-ArduinoCli

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

$productionSketches = @(
    @{ Path = (Join-Path $ArduinoDir "valves"); Label = "valves" },
    @{ Path = (Join-Path $ArduinoDir "simple01"); Label = "simple01" },
    @{ Path = (Join-Path $ArduinoDir "sensors"); Label = "sensors" }
)

foreach ($sketch in $productionSketches) {
    Invoke-ArduinoCompile -SketchPath $sketch.Path -Label $sketch.Label
}

$testProjects = Get-ChildItem -Path $ArduinoTestsDir -Directory -Filter "test_*"
foreach ($project in $testProjects) {
    Invoke-ArduinoCompile -SketchPath $project.FullName -Label $project.Name
}

if ($CompileOnly) {
    Write-Host "Compile-only mode: all sketches compiled successfully."
    exit 0
}

if (-not $Port) {
    Write-Host "Compile-only complete. Pass -Port COM8 to upload AUnit tests and verify serial output."
    exit 0
}

Write-Host "Running AUnit tests on $Port (close Serial Monitor first)..."
$testRunner = Join-Path $RepoRoot "scripts\read_aunit_serial.py"
foreach ($project in $testProjects) {
    Write-Host "Uploading $($project.Name)..."
    & arduino-cli compile -b $Fqbn -p $Port -u $project.FullName --build-property "compiler.cpp.extra_flags=$IncludeFlag"
    if ($LASTEXITCODE -ne 0) {
        throw "Upload failed: $($project.Name)"
    }
    python $testRunner $Port 45
    if ($LASTEXITCODE -ne 0) {
        throw "AUnit tests failed: $($project.Name)"
    }
}

Write-Host "All compile and test steps passed."
