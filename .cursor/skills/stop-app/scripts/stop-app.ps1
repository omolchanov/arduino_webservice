$patterns = @('main:app', 'multiprocessing\.spawn.*spawn_main')
$procs = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object {
    $cmd = $_.CommandLine
    ($patterns | Where-Object { $cmd -match $_ }).Count -gt 0
  }

if (-not $procs) {
  Write-Output "No uvicorn processes found."
  exit 0
}

foreach ($proc in $procs) {
  Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
  Write-Output "Stopped PID $($proc.ProcessId)."
}

Start-Sleep -Seconds 2
Write-Output "COM8 should be released."
