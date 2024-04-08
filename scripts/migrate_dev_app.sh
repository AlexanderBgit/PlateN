#!/bin/zsh

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate
popd

pushd "../FRONTEND/fastparking"
python manage.py migrate
popd