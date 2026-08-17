# Stop uvicorn and release COM8 (Arduino serial port)
$ErrorActionPreference = "SilentlyContinue"

$AppPort = 8000
$ComPort = "COM8"

function Get-UvicornProcessIds {
    $ids = @()
    foreach ($proc in Get-CimInstance Win32_Process -Filter "Name='python.exe'") {
        $cmd = $proc.CommandLine
        if (-not $cmd) { continue }
        if (
            $cmd -match "uvicorn" -or
            $cmd -match "main:app" -or
            $cmd -match "multiprocessing\.spawn"
        ) {
            $ids += $proc.ProcessId
        }
    }
    return @($ids | Select-Object -Unique)
}

function Get-PortProcessIds {
    param([int]$Port)

    $ids = @()
    foreach ($conn in Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue) {
        $procId = $conn.OwningProcess
        if ($procId -gt 0 -and (Get-Process -Id $procId -ErrorAction SilentlyContinue)) {
            $ids += $procId
        }
    }
    return @($ids | Select-Object -Unique)
}

function Stop-ProcessIds {
    param([int[]]$ProcessIds)

    $stopped = @()
    foreach ($procId in ($ProcessIds | Select-Object -Unique)) {
        if ($procId -le 0) { continue }
        $proc = Get-Process -Id $procId -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "Stopping $($proc.ProcessName) (PID $procId)..."
        } else {
            Write-Host "Stopping PID $procId..."
        }
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        taskkill /F /PID $procId 2>$null | Out-Null
        $stopped += $procId
    }
    return $stopped
}

function Test-PortListening {
    param([int]$Port)

    $listeners = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.OwningProcess -gt 0 }
    foreach ($conn in $listeners) {
        if (Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue) {
            return $true
        }
    }
    return $false
}

Write-Host "Stopping uvicorn (port $AppPort) and releasing $ComPort..."

$targetIds = @(
    (Get-PortProcessIds -Port $AppPort) +
    (Get-UvicornProcessIds)
) | Select-Object -Unique

if ($targetIds.Count -eq 0) {
    Write-Host "No uvicorn/python server process found."
} else {
    Stop-ProcessIds -ProcessIds $targetIds | Out-Null
    Start-Sleep -Seconds 2
}

if (Test-PortListening -Port $AppPort) {
    Write-Host "Port $AppPort still listening; retrying..."
    $retryIds = @(
        (Get-PortProcessIds -Port $AppPort) +
        (Get-UvicornProcessIds)
    ) | Select-Object -Unique
    Stop-ProcessIds -ProcessIds $retryIds | Out-Null
    Start-Sleep -Seconds 2
}

if (Test-PortListening -Port $AppPort) {
    Write-Warning "Port $AppPort is still listening."
    exit 1
}

Write-Host "Port $AppPort is free."

$remaining = Get-UvicornProcessIds
if ($remaining.Count -gt 0) {
    Write-Warning "Uvicorn worker still running (PIDs: $($remaining -join ', '))."
    exit 1
}

Start-Sleep -Seconds 1
Write-Host "$ComPort should be released (close Arduino Serial Monitor if upload still fails)."
