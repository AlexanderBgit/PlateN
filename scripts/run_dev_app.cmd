@echo off

@REM call gen_static.cmd
call migrate_dev_app.cmd
echo .
echo Starting to check additional libraries...
SETLOCAL
SET "POPPER_BIN=..\LIBS\poppler\Library\bin"
IF EXIST "%POPPER_BIN%" (
    SET "PATH=%POPPER_BIN%;%PATH%"
) ELSE (
    echo Folder with 'LIBS\poppler\Library\bin' does not exist. PDF function is limited in app.
)

PUSHD "..\FRONTEND\fastparking"
git rev-parse --short HEAD > ..\git-version.txt
echo .
echo Starting Django web server...
poetry run python manage.py runserver 0.0.0.0:8000 --insecure
POPD
ENDLOCAL