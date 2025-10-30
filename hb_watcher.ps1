# HB Watcher: triggers hb_file.py on .txt create/change/rename and via polling fallback.

# --- Config ---
$folderPath    = "[REDACTED_FILE_PATH]"
$pythonScript  = "[REDACTED_FILE_PATH]"
$processedFiles = @{}
$pollSeconds   = 15
$debounceMs    = 750

# --- Process existing .txt files ---
Write-Host "Checking for existing TXT files in: $folderPath"
Get-ChildItem -Path $folderPath -Filter "*.txt" | ForEach-Object {
    $filePath = $_.FullName
    if (-not $processedFiles.ContainsKey($filePath)) {
        Write-Host "Processing existing TXT file: $filePath"
        Start-Sleep -Milliseconds $debounceMs
        python $pythonScript -i $filePath
        $processedFiles[$filePath] = $true
    }
}

# --- FileSystemWatcher ---
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.Filter = "*.txt"
$watcher.IncludeSubdirectories = $false
$watcher.NotifyFilter = [IO.NotifyFilters]'FileName,LastWrite,Size'
$watcher.EnableRaisingEvents = $true

$action = {
    $filePath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    Write-Host "Event triggered: $changeType on $filePath"
    Start-Sleep -Milliseconds $debounceMs
    if (Test-Path $filePath -and (-not $processedFiles.ContainsKey($filePath))) {
        Write-Host "Processing new TXT: $filePath"
        python $pythonScript -i $filePath
        $processedFiles[$filePath] = $true
    }
}

Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action

# --- Polling fallback ---
Write-Host "Monitoring folder: $folderPath (poll every $pollSeconds seconds). Press Ctrl+C to exit."
while ($true) {
    $currentFiles = Get-ChildItem -Path $folderPath -Filter "*.txt" -File -ErrorAction SilentlyContinue
    foreach ($file in $currentFiles) {
        $filePath = $file.FullName
        if (-not $processedFiles.ContainsKey($filePath)) {
            Write-Host "Polling detected new file: $filePath"
            Start-Sleep -Milliseconds $debounceMs
            python $pythonScript -i $filePath
            $processedFiles[$filePath] = $true
        }
    }
    Start-Sleep -Seconds $pollSeconds
}
