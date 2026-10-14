@echo off
REM ==== Chay cac kich ban JMeter o che do Non-GUI va sinh HTML Dashboard ====
REM Dat bien moi truong JMETER_HOME tro toi thu muc cai JMeter tren may ban,
REM vi du: set JMETER_HOME=C:\apache-jmeter-5.6.3
REM Neu khong dat, script dung lenh "jmeter" co san trong PATH.
if "%JMETER_HOME%"=="" (set JM=jmeter) else (set JM=%JMETER_HOME%\bin\jmeter.bat)
cd /d %~dp0

REM 1) Web - BlazeDemo (20 users, ramp-up 10s, 5 vong)
call :run 01_BlazeDemo_Web web 20 5

REM 2) API - JSONPlaceholder (30 users, ramp-up 10s, 5 vong)
call :run 02_JSONPlaceholder_API api 30 5

REM 3) So sanh tai - Web voi 10 / 50 / 100 users (3 vong)
call :run 01_BlazeDemo_Web load-10 10 3
call :run 01_BlazeDemo_Web load-50 50 3
call :run 01_BlazeDemo_Web load-100 100 3
goto :eof

REM %1 = ten file jmx, %2 = ten ket qua, %3 = so users, %4 = so vong lap
:run
if exist results\%2-report rmdir /s /q results\%2-report
if exist results\%2.jtl del results\%2.jtl
call "%JM%" -n -t test-plans\%1.jmx -Jthreads=%3 -Jrampup=10 -Jloops=%4 -l results\%2.jtl -e -o results\%2-report -Jjmeter.reportgenerator.overall_granularity=1000
goto :eof
