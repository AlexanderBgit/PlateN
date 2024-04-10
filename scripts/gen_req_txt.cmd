@echo off
echo "runed poetry shell?"
PUSHD "../FRONTEND"
poetry env info -p
echo "\Scripts\activate"
poetry export --without-hashes > requirements.txt
POPD