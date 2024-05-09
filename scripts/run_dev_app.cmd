@echo off
echo "runed poetry shell?"

echo "runing migration"

call migrate_dev_app.cmd

SETLOCAL
SET "POPPER_BIN=..\LIBS\poppler\Library\bin"
IF EXIST "%POPPER_BIN%" (
    SET "PATH=%POPPER_BIN%;%PATH%"
) ELSE (
    echo Folder with 'LIBS\poppler\Library\bin' does not exist. PDF function is limited in app.
)
PUSHD "..\FRONTEND\fastparking"
REM poetry env info -p
REM echo "\Scripts\activate"
git rev-parse --short HEAD > ..\git-version.txt
poetry shell
python manage.py runserver 0.0.0.0:8000
POPD
ENDLOCAL