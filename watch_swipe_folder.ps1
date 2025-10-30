# Set the folder to watch
$folderPath = "[REDACTED_FILE_PATH]"
$pythonScript1 = "[REDACTED_FILE_PATH]"
$pythonScript2 = "[REDACTED_FILE_PATH]"

# Track processed files
$processedFiles = @{}

# Helper to find the most likely updated file
function FindUpdatedFile($originalFilePath) {
    $originalTime = (Get-Item $originalFilePath).LastWriteTime
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($originalFilePath)

    $updatedFiles = Get-ChildItem -Path $folderPath -Filter "*Updated*.csv" | Where-Object {
        $_.LastWriteTime -gt $originalTime -and $_.Name -like "*$baseName*"
    }

    if ($updatedFiles.Count -gt 0) {
        return $updatedFiles | Sort-Object LastWriteTime -Descending | Select-Object -First 1 | ForEach-Object { $_.FullName }
    }

    return $null
}

# Process existing CSV files
Write-Host "Checking for existing CSV files in: $folderPath"
Get-ChildItem -Path $folderPath -Filter "PaymentCard_*.csv" | ForEach-Object {
    $existingFile = $_.FullName
    if (-not $processedFiles.ContainsKey($existingFile)) {
        Write-Host "Processing existing file: $existingFile"
        try {
            python $pythonScript1 $existingFile
            Start-Sleep -Seconds 2
            $updatedFile = FindUpdatedFile $existingFile
            if ($updatedFile -and (Test-Path $updatedFile)) {
                python $pythonScript2 $updatedFile
            } else {
                Write-Host "❌ Updated file not found for: $existingFile"
            }
            $processedFiles[$existingFile] = $true
        } catch {
            Write-Host "⚠️ Error processing existing file: $_"
        }
    }
}

# Create a FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $folderPath
$watcher.Filter = "PaymentCard_*.csv"
$watcher.IncludeSubdirectories = $false
$watcher.EnableRaisingEvents = $true

# Define the action to take when a file is created/changed/renamed
$action = {
    $filePath = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    Write-Host "Event triggered: $changeType on $filePath"
    Start-Sleep -Seconds 2

    if (Test-Path $filePath -and (-not $processedFiles.ContainsKey($filePath))) {
        Write-Host "Processing new CSV: $filePath"
        try {
            python ${using:pythonScript1} $filePath
            Start-Sleep -Seconds 2
            $updatedFile = FindUpdatedFile $filePath
            if ($updatedFile -and (Test-Path $updatedFile)) {
                python ${using:pythonScript2} $updatedFile
            } else {
                Write-Host "❌ Updated file not found for: $filePath"
            }
            $processedFiles[$filePath] = $true
        } catch {
            Write-Host "⚠️ Error running Python scripts: $_"
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
    $currentFiles = Get-ChildItem -Path $folderPath -Filter "PaymentCard_*.csv"
    foreach ($file in $currentFiles) {
        $filePath = $file.FullName
        if (-not $processedFiles.ContainsKey($filePath)) {
            Write-Host "Polling detected new file: $filePath"
            try {
                python $pythonScript1 $filePath
                Start-Sleep -Seconds 2
                $updatedFile = FindUpdatedFile $filePath
                if ($updatedFile -and (Test-Path $updatedFile)) {
                    python $pythonScript2 $updatedFile
                } else {
                    Write-Host "❌ Updated file not found for: $filePath"
                }
                $processedFiles[$filePath] = $true
            } catch {
                Write-Host "⚠️ Error processing file: $_"
            }
        }
    }
    Start-Sleep -Seconds 5
}
