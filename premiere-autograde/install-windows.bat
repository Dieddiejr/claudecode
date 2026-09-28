@echo off
rem Installe le panneau Claude AutoGrade dans Premiere Pro (Windows).
setlocal
set "SRC=%~dp0"
set "DEST=%APPDATA%\Adobe\CEP\extensions\claude-autograde"

rem Autorise les extensions non signees (mode developpeur CEP), pour toutes les versions recentes.
for %%v in (9 10 11 12 13) do reg add "HKCU\Software\Adobe\CSXS.%%v" /v PlayerDebugMode /t REG_SZ /d 1 /f >nul

robocopy "%SRC%." "%DEST%" /E /PURGE /XD tests /XF install-*.* >nul
if %ERRORLEVEL% GEQ 8 (
  echo La copie a echoue.
  pause
  exit /b 1
)

echo.
echo Claude AutoGrade est installe dans :
echo   %DEST%
echo.
echo Redemarre Premiere Pro, puis ouvre Fenetre ^> Extensions ^> Claude AutoGrade.
pause
