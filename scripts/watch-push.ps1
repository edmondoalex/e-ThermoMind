$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $repoRoot

Write-Host "Watching repo for changes. Press Ctrl+C to stop."

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $repoRoot
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true
$watcher.NotifyFilter = [System.IO.NotifyFilters]'FileName, LastWrite, DirectoryName'

$handler = {
    Start-Sleep -Milliseconds 300
    $status = git status --porcelain
    if ($status) {
        Write-Host "`nChanges detected."
        $ans = Read-Host "Commit+push now? (y/N)"
        if ($ans -match '^[Yy]$') {
            $msg = Read-Host "Commit message"
            if (-not $msg) { $msg = "Update" }
            git add -A | Out-Null
            git commit -m $msg | Out-Null
            git push | Out-Null
            Write-Host "Pushed."
        }
    }
}

$created = Register-ObjectEvent $watcher Created -Action $handler
$changed = Register-ObjectEvent $watcher Changed -Action $handler
$deleted = Register-ObjectEvent $watcher Deleted -Action $handler
$renamed = Register-ObjectEvent $watcher Renamed -Action $handler

try {
    while ($true) { Start-Sleep -Seconds 1 }
}
finally {
    Unregister-Event -SourceIdentifier $created.Name
    Unregister-Event -SourceIdentifier $changed.Name
    Unregister-Event -SourceIdentifier $deleted.Name
    Unregister-Event -SourceIdentifier $renamed.Name
    $watcher.Dispose()
}
