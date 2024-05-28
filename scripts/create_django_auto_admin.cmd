@echo off
@REM echo "runed poetry shell?"
@REM poetry env info -p
@REM echo "\Scripts\activate"
PUSHD "../FRONTEND/fastparking"
set PYTHONPATH=.
poetry run python ./admin/create_groups.py
poetry run python ./admin/create_admin_user.py
POPD