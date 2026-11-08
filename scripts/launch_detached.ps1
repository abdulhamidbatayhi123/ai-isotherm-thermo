# Start a batch file as a process outside this shell's job (Win32_Process.Create), so it
# survives the end of the terminal or agent session that launched it (the Paper 3A tuning
# workers were killed once when the launching session ended). The batch file holds the whole
# command, which avoids cmd.exe's quote stripping on paths with spaces.
# Usage: powershell -NoProfile -File scripts/launch_detached.ps1 scripts/launch/worker_a.cmd
param([string]$Batch)
$repo = Split-Path -Parent $PSScriptRoot
$path = (Resolve-Path $Batch).Path
# cmd.exe started through WMI did not run a quoted path with spaces; the 8.3 short path has none
$short = (New-Object -ComObject Scripting.FileSystemObject).GetFile($path).ShortPath
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = "cmd.exe /c $short"; CurrentDirectory = $repo }
"{0}: pid {1} (return {2})" -f (Split-Path -Leaf $path), $r.ProcessId, $r.ReturnValue
