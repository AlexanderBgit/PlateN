#!/bin/env sh

USE_DS_NUMBER_DETECTION=0
python ./utils/scheduler.py --loop -q --sent_hello

# while true; do
#   python ./utils/telegram_api.py
#   sleep 2
# done
