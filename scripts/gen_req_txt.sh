#!/bin/zsh

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate
popd

pushd "../FRONTEND/fastparking"
poetry export --without-hashes > requirements.txt
popd