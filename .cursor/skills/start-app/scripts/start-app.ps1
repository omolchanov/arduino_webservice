$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..\..")
$patterns = @('main:app', 'multiprocessing\.spawn.*spawn_main')

$running = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object {
    $cmd = $_.CommandLine
    ($patterns | Where-Object { $cmd -match $_ }).Count -gt 0
  }

if ($running) {
  Write-Output "Uvicorn is already running."
  exit 0
}

Start-Process -FilePath "uvicorn" -ArgumentList @("main:app", "--reload") -WorkingDirectory $projectRoot | Out-Null

$deadline = (Get-Date).AddSeconds(15)
do {
  Start-Sleep -Milliseconds 500
  try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/status" -UseBasicParsing -TimeoutSec 2
    if ($response.StatusCode -eq 200) {
      $status = $response.Content | ConvertFrom-Json
      if ($status.serial_connected) {
        Write-Output "Server started at http://127.0.0.1:8000 (COM8 connected)."
      } else {
        Write-Output "Server started at http://127.0.0.1:8000 (COM8 not connected yet)."
      }
      exit 0
    }
  } catch {}
} while ((Get-Date) -lt $deadline)

Write-Output "Uvicorn start requested; server not responding yet on http://127.0.0.1:8000"
exit 1
