#!/bin/bash

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate

poetry export --without-hashes > requirements.txt
popd