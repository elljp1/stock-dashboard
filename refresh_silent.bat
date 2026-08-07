@echo off
REM Silent daily refresh: downloads data, regrades predictions, rebuilds dashboard.
REM Run automatically by Windows Task Scheduler ("Stock Timing Daily Refresh").
cd /d "%~dp0"
echo ==== refresh started %date% %time% ==== >> refresh_log.txt
REM wait for the internet (up to ~3 min) - boot-time runs start before Wi-Fi is up
set tries=0
:netwait
ping -n 1 github.com >nul 2>&1 && goto netok
set /a tries+=1
if %tries% geq 12 (echo no network after 3 min, aborting >> refresh_log.txt & exit /b 1)
timeout /t 15 /nobreak >nul
goto netwait
:netok
echo network OK after %tries% waits >> refresh_log.txt
"C:\Users\micro\AppData\Local\Programs\Python\Python312\python.exe" fetch_data.py >> refresh_log.txt 2>&1
"C:\Users\micro\AppData\Local\Programs\Python\Python312\python.exe" analyze.py >> refresh_log.txt 2>&1
REM PUBLISH DISABLED - the cloud workflow is the single publisher
REM git -C site pull --rebase origin main >> refresh_log.txt 2>&1
copy /Y index.html site\index.html >> refresh_log.txt 2>&1
REM PUBLISH DISABLED - the cloud workflow is the single publisher
REM git -C site add index.html >> refresh_log.txt 2>&1
REM PUBLISH DISABLED - the cloud workflow is the single publisher
REM git -C site -c user.name="dashboard-bot" -c user.email="dashboard-bot@users.noreply.github.com" commit -m "auto data refresh" >> refresh_log.txt 2>&1
REM PUBLISH DISABLED - the cloud workflow is the single publisher
REM git -C site push origin main >> refresh_log.txt 2>&1
"C:\Users\micro\AppData\Local\Programs\Python\Python312\python.exe" publish_if_stale.py >> refresh_log.txt 2>&1
echo ==== refresh finished %date% %time% ==== >> refresh_log.txt

