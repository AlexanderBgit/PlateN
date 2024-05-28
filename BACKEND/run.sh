#!/bin/bash

cd ./api

echo -e "\nStarting FastAPI web server..."
uvicorn main:app --port ${APP_PORT_API:-9000} --host 0.0.0.0


