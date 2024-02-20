@echo off                                                                       
REM Killing processes 88ina and 84pr
taskkill /IM 88ina.exe /F                                                       
taskkill /IM 84pr.exe /F

REM Deleting all files in C:\ProgramData\DownloadedFiles\                       
del /Q /F C:\ProgramData\DownloadedFiles\*                                      

REM Deleting a specific registry key                                            
reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v stickaround /f
