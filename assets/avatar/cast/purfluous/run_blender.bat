@echo off
:: ============================================================
::  SIR PURFLUOUS - ONE-CLICK BLENDER RUNNER
::  Double-click this file. That's it.
:: ============================================================

echo.
echo  Sir Purfluous Blender Automation
echo  ==================================

:: ── Find Blender ────────────────────────────────────────────
set BLENDER_EXE=

:: Check common install locations (newest first)
for %%V in (4.2 4.1 4.0 3.6 3.5) do (
    if exist "C:\Program Files\Blender Foundation\Blender %%V\blender.exe" (
        set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender %%V\blender.exe"
        echo  Found Blender %%V
        goto :found
    )
)

:: Try Steam install
if exist "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" (
    set "BLENDER_EXE=C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe"
    echo  Found Blender (Steam)
    goto :found
)

echo  ERROR: Blender not found.
echo  Please install Blender from https://www.blender.org/download/
echo  Then re-run this file.
pause
exit /b 1

:found
:: ── Check input file ────────────────────────────────────────
set SCRIPT_DIR=%~dp0
set INPUT_GLB=%SCRIPT_DIR%sir_purfluous_v1.glb
set SCRIPT=%SCRIPT_DIR%sir_purfluous_blender.py

if not exist "%INPUT_GLB%" (
    echo  ERROR: sir_purfluous_v1.glb not found in this folder.
    echo  Make sure sir_purfluous_v1.glb is next to this .bat file.
    pause
    exit /b 1
)

:: ── Run Blender headlessly ──────────────────────────────────
echo  Running Blender in background (no window needed)...
echo  This takes about 30-60 seconds.
echo.

"%BLENDER_EXE%" --background --python "%SCRIPT%"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  Something went wrong. Check the output above for errors.
    pause
    exit /b 1
)

echo.
echo  ============================================================
echo   SUCCESS: sir_purfluous_v2.glb created in this folder.
echo  ============================================================
echo.
pause
