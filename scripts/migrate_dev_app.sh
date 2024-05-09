#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"

if command -v dos2unix &> /dev/null; then
#  echo "converting *.sh files from CRLF to LF"
  dos2unix *.sh &> /dev/null
fi

# simulate poetry shell
#pushd "../FRONTEND" > /dev/null
#pyact=$(poetry env info -p)
#source ${pyact}/bin/activate
#popd > /dev/null

#echo PYTHONPATH=${PYTHONPATH}
echo -e "\nStarting Django migrate..."
pushd "../FRONTEND/fastparking" > /dev/null
poetry run python manage.py migrate
popd > /dev/null