#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

# simulate poetry shell
pushd "../FRONTEND"
pyact=$(poetry env info -p)
source ${pyact}/bin/activate

poetry export --without-hashes > requirements.txt
popd