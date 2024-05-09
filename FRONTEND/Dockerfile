# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
# FROM python:3.11
FROM python:3.11

# Встановимо змінну середовища
ENV APP_BASE ./
ENV APP_HOME /app 

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

COPY ${APP_BASE}requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt update -q; apt install -y poppler-utils

# Скопіюємо інші файли в робочу директорію контейнера
COPY $APP_BASE  ./

# CMD bash ./run.sh 
CMD [ "bash" , "./run.sh" ] 
#CMD bash

# Запустимо наш застосунок всередині контейнера
# ENTRYPOINT [ "bash", "./run.sh" ]

