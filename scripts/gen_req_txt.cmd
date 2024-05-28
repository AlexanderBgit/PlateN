@echo off
@REM echo "runed poetry shell?"
PUSHD "../FRONTEND"
@REM poetry env info -p
@REM echo "\Scripts\activate"
poetry export --without-hashes > requirements.txt
POPD