@echo off
@REM echo "runed poetry shell?"
PUSHD "../FRONTEND/fastparking"
@REM poetry env info -p
@REM echo "\Scripts\activate"
set PYTHONPATH=.
poetry run python ./parking/create_parking.py
POPD