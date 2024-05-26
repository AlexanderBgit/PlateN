@echo off                                                                                                                                                   
PUSHD "..\deploy"

setlocal enabledelayedexpansion
set "ENV=.env"
if exist %ENV% (
    :: Read the .env file and set environment variables
    for /f "tokens=* delims=" %%i in (%ENV%) do (
        set "line=%%i"
        echo !line! | findstr /r "^PURPOSE" >nul
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
echo %branch%%purpose%-%commit% > ..\FRONTEND\git-version.txt
:: Display the environment variables to verify
echo BRANCH=%branch%, PURPOSE=%purpose%, commit=%commit%
endlocal

docker-compose  --file docker-compose-project.yml --env-file .env build code 
rem timeout 1
rem docker attach fastparking-code-1

rem docker-compose down 

POPD