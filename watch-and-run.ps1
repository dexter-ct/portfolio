
# Set the folder to watch
$folderPath = "[REDACTED_FILE_PATH]"
$pythonScript = "[REDACTED_FILE_PATH]"

# Track processed files
$processedFiles = @{}

# Process existing CSV files
Write-Host "Checking for existing CSV files in: $folderPath"
Get-ChildItem -Path $folderPath -Filter "*.csv" | ForEach-Object {
    $existingFile = $_.FullName
    if (-not $processedFiles.ContainsKey($existingFile)) {
        Write-Host "Processing existing file: $existingFile"
        try {
            python $pythonScript $existingFile
            $processedFiles[$existingFile] = $true
        } catch {
            Write-Host "Error processing existing file: $_"
        }
    }
}

# Create a FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.Filter = "*.csv"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

# Define the action to take when a file is created/changed/renamed
$action = {
    $filePath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    Write-Host "Event triggered: $changeType on $filePath"
    Start-Sleep -Seconds 2  # Wait for file to finish writing

    if (Test-Path $filePath -and (-not $processedFiles.ContainsKey($filePath))) {
        Write-Host "Processing new CSV: $filePath"
        try {
            python $pythonScript $filePath
            $processedFiles[$filePath] = $true
        } catch {
            Write-Host "Error running Python script: $_"
        }
    }
}

# Register multiple events
Register-ObjectEvent $watcher "Created" -Action $action
Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Renamed" -Action $action

# Polling fallback for OneDrive quirks
Write-Host "Monitoring folder: $folderPath. Press Ctrl+C to exit."
while ($true) {
    $currentFiles = Get-ChildItem -Path $folderPath -Filter "*.csv"
    foreach ($file in $currentFiles) {
        $filePath = $file.FullName
        if (-not $processedFiles.ContainsKey($filePath)) {
            Write-Host "Polling detected new file: $filePath"
            try {
                python $pythonScript $filePath
                $processedFiles[$filePath] = $true
            } catch {
                Write-Host "Error processing file: $_"
            }
        }
    }
    Start-Sleep -Seconds 5
}
