@echo off

setlocal enabledelayedexpansion
set "ENV=..\deploy\.env"
if exist %ENV% (
    :: Read the .env file and set environment variables
    for /f "tokens=* delims=" %%i in (%ENV%) do (
        set "line=%%i"
        echo !line! | findstr /r "^POSTGRES_DB" >nul
        if !errorlevel! equ 0 (
            for /f "tokens=1,2 delims==" %%a in ("!line!") do set "%%a=%%b"
        )
        echo !line! | findstr /r "^POSTGRES_USER" >nul
        if !errorlevel! equ 0 (
            for /f "tokens=1,2 delims==" %%a in ("!line!") do set "%%a=%%b"
        )
    )
)
echo POSTGRES_USER=%POSTGRES_USER%
echo POSTGRES_DB=%POSTGRES_DB% 

docker exec -it fastparking-db-postgres-1 bash -c "cd /var/lib/postgresql/data;pg_dump -U %POSTGRES_USER% %POSTGRES_DB% | gzip > db_%POSTGRES_DB%_`date +%%Y%%m%%d%%H%%M`.sql.gz"

echo "database_volume/postgres-data/db_%POSTGRES_DB%_*.sql.gz"
dir "..\Database\postgres-data\db_%POSTGRES_DB%_*.sql.gz"
endlocal
