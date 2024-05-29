@echo off
cd %~dp0
@REM call gen_static.cmd
@REM call migrate_dev_app.cmd



PUSHD "..\..\BACKEND\api"

setlocal enabledelayedexpansion
set "ENV=..\..\deploy\.env"
set APP_PORT_API=9000
if exist %ENV% (
    :: Read the .env file and set environment variables
    for /f "tokens=* delims=" %%i in (%ENV%) do (
        set "line=%%i"
        echo !line! | findstr /r "^PURPOSE" >nul
        if !errorlevel! equ 0 (
            for /f "tokens=1,2 delims==" %%a in ("!line!") do set "%%a=%%b"
        )
        echo !line! | findstr /r "^APP_PORT_API" >nul
        if !errorlevel! equ 0 (
            for /f "tokens=1,2 delims==" %%a in ("!line!") do set "%%a=%%b"
        )
    )
)

:: Get the current branch name
for /f "delims=" %%i in ('git branch --show-current') do set "branch=%%i"
:: Get the short commit hash
for /f "delims=" %%i in ('git rev-parse --short HEAD') do set "commit=%%i"
:: Combine the branch name and commit hash, and write to the file
echo %branch%%purpose%-%commit% > ..\git-version.txt
:: Display the environment variables to verify
echo BRANCH=%branch%, PURPOSE=%purpose%, commit=%commit%




rem git rev-parse --short HEAD > ..\git-version.txt
echo.
echo Starting FastAPI web server...
set TF_ENABLE_ONEDNN_OPTS=0
poetry run uvicorn main:app --port %APP_PORT_API% --host 0.0.0.0 --reload
ENDLOCAL
POPD