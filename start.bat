@echo off
:START
echo Starting index.js...
start /min node index.js

timeout /t 600 >nul

taskkill /f /im node.exe >nul
echo index.js process terminated.
goto START
