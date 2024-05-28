@echo off
cd %~dp0
@REM call gen_static.cmd
call migrate_dev_app.cmd
PUSHD "..\"
echo.
echo Starting to check additional libraries...
SETLOCAL
SET "POPPER_BIN=%CD%\LIBS\poppler\Library\bin"
IF EXIST "%POPPER_BIN%" (
    SET "PATH=%POPPER_BIN%;%PATH%"
    echo Found library: poppler
) ELSE (
    echo Folder with 'LIBS\poppler\Library\bin' does not exist. PDF function is limited in app.
)

PUSHD "FRONTEND\fastparking"

setlocal enabledelayedexpansion
set "ENV=..\..\deploy\.env"
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
endlocal



rem git rev-parse --short HEAD > ..\git-version.txt
echo.
echo Starting FastAPI web server...
poetry run uvicorn main:app --port ${APP_PORT_API:-9000} --host 0.0.0.0 --reload
POPD
ENDLOCAL
POPD