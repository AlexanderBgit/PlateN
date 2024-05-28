#!/bin/bash

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
cd "${script_dir}"


echo PYTHONPATH=${PYTHONPATH}
pushd "../FRONTEND/fastparking"

BACKUP_FILE=savedb.json.gz

if [[ -f "${BACKUP_FILE}" ]]; then
  echo -n "Want to rewrite file \"${BACKUP_FILE}\" by all database value ? (y/n): "
  read answer

  if [[ "$answer" =~ ^[Yy]$ ]]; then
      echo "Rewriting the file..."
      # Your code to rewrite the database goes here
  else
      echo "Operation canceled."
      popd
      exit 1
  fi
fi

echo -e "\nStarting Django dumpdata..."
USE_DS_NUMBER_DETECTION=0 poetry run python manage.py dumpdata --format=json | gzip > "${BACKUP_FILE}"
ls -lh *.json.gz
popd