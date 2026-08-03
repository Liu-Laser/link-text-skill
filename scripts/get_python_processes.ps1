# 获取所有Python进程的信息
Get-WmiObject Win32_Process | Where-Object {$_.Name -eq 'python.exe'} | ForEach-Object {
    Write-Host "PID: $($_.ProcessId)"
    Write-Host "Path: $($_.ExecutablePath)"
    Write-Host "Command: $($_.CommandLine)"
    Write-Host "---"
}