@echo off
cd /d "%~dp0"
if not exist "dist\ingame-ready\LANCER.cmd" goto missing
call "dist\ingame-ready\LANCER.cmd" %*
exit /b %errorlevel%
:missing
echo Le kit local de test n'est pas encore prepare sur cette machine.
echo Voir docs\maintenance\INGAME_READY.md.
pause
exit /b 1
