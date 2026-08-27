Set-Location $PSScriptRoot
Start-Process "http://localhost:8081"
py -m http.server 8081
