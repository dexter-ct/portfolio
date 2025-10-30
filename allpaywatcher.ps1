$folderPath = "[REDACTED_FILE_PATH]"
$pythonScript = "[REDACTED_FILE_PATH]"
$processedFiles = @{}

# Process existing .txt files
Write-Host "Checking for existing TXT files in: $folderPath"
Get-ChildItem -Path $folderPath -Filter "*.txt" | ForEach-Object {
    $filePath = $_.FullName
    if (-not $processedFiles.ContainsKey($filePath)) {
        Write-Host "Processing existing TXT file: $filePath"
        python $pythonScript $filePath
        $processedFiles[$filePath] = $true
    }
}

# FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.Filter = "*.txt"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

$action = {
    $filePath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    Write-Host "Event triggered: $changeType on $filePath"
    Start-Sleep -Seconds 2
    if (Test-Path $filePath -and (-not $processedFiles.ContainsKey($filePath))) {
        Write-Host "Processing new TXT: $filePath"
        python $pythonScript $filePath
        $processedFiles[$filePath] = $true
    }
}

Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action

# Fallback polling
Write-Host "Monitoring folder: $folderPath. Press Ctrl+C to exit."
while ($true) {
    $currentFiles = Get-ChildItem -Path $folderPath -Filter "*.txt"
    foreach ($file in $currentFiles) {
        $filePath = $file.FullName
        if (-not $processedFiles.ContainsKey($filePath)) {
            Write-Host "Polling detected new file: $filePath"
            python $pythonScript $filePath
            $processedFiles[$filePath] = $true
        }
    }
    Start-Sleep -Seconds 5
}
