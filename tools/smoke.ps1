# Runs the built exe as "Scrollfold.exe --smoke <folder>" from an empty temp folder. The app does a small piece of its
# real work there and returns exit code 0. On failure it can write the reason to <folder>\smoke.log.
# A windowed exe that fails on startup shows a dialog and waits forever, so a time limit turns that into a failure.
param([int]$TimeoutSeconds = 60)
$ErrorActionPreference = "Stop"
$root =Split-Path -Parent $PSScriptRoot
$work = Join-Path $env:TEMP ("Scrollfold_smoke_" + (Get-Random))
New-Item -ItemType Directory -Force $work | Out-Null
Copy-Item "$root\dist\Scrollfold.exe" $work
$p = Start-Process "$work\Scrollfold.exe" -WorkingDirectory $work -ArgumentList "--smoke", "`"$work`"" -PassThru
$code = 1
if ($p.WaitForExit($TimeoutSeconds * 1000)) {
    $code = $p.ExitCode
    if ($code -eq 0) {
        "Smoke test passed"
    } else {
        "Smoke test FAILED: exit code $code"
        if (Test-Path "$work\smoke.log") { Get-Content "$work\smoke.log" -Encoding UTF8 }
    }
} else {
    "Smoke test FAILED: no exit after $TimeoutSeconds seconds. The exe is probably showing a startup error."
    taskkill /T /F /PID $p.Id | Out-Null
}
Start-Sleep -Seconds 1  # a onefile exe needs a moment to release its file
Remove-Item -Recurse -Force $work -ErrorAction SilentlyContinue
exit $code
