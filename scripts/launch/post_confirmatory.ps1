# Waits until the four confirmatory shards (python PIDs given as arguments) have exited, then
# starts the H2 confirmatory shards (h2conf_0/1) and the sensitivity shards (sens_0/1), each as a
# hidden cmd on its 8.3 path. Started detached so the chain survives the session.
param([string]$PidList)
$Pids = $PidList -split ',' | ForEach-Object { [int]$_ }
$root = "C:\Users\abdulhamid batayhi\Desktop\ai-isotherm-thermo"
$log = Join-Path $root "logs\post_chain.log"
"$(Get-Date -Format s) waiting for PIDs $($Pids -join ',')" | Add-Content $log
while ((Get-Process -Id $Pids -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0) { Start-Sleep 300 }
"$(Get-Date -Format s) confirmatory shards exited" | Add-Content $log
$fso = New-Object -ComObject Scripting.FileSystemObject
foreach ($n in "h2conf_0", "h2conf_1", "sens_0", "sens_1") {
  $f = $fso.GetFile((Join-Path $root "scripts\launch\$n.cmd")).ShortPath
  $p = Start-Process -FilePath "cmd.exe" -ArgumentList "/c $f" -WindowStyle Hidden -PassThru
  "$(Get-Date -Format s) started $n (cmd PID $($p.Id))" | Add-Content $log
}
