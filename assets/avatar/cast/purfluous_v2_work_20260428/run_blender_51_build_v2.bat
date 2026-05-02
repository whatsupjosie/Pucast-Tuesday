@echo off
setlocal
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
set "SCRIPT_DIR=%~dp0"
set "SCRIPT=%SCRIPT_DIR%build_sir_purfluous_v2_actor.py"

if not exist "%BLENDER_EXE%" (
  echo Blender 5.1 was not found at:
  echo %BLENDER_EXE%
  exit /b 1
)

if not exist "%SCRIPT%" (
  echo Build script not found:
  echo %SCRIPT%
  exit /b 1
)

"%BLENDER_EXE%" --background --python "%SCRIPT%"
exit /b %ERRORLEVEL%
