@echo off
@REM echo "runed poetry shell?"
@REM poetry env info -p
@REM echo "\Scripts\activate"
PUSHD "../FRONTEND/fastparking"
poetry run python ./admin/create_admin_user.py
poetry run python ./admin/create_groups.py
POPD