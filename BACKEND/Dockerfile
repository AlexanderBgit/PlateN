# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
# FROM python:3.11
FROM python:3.11

# Встановимо змінну середовища
ENV APP_BASE ./
ENV APP_HOME /app 

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Скопіюємо інші файли в робочу директорію контейнера
COPY $APP_BASE  ./

COPY ${APP_BASE}requirements.txt requirements.txt

# Встановимо залежності всередині контейнера

RUN pip install -r requirements.txt 

CMD bash ./run.sh 

#CMD bash

#CMD ["python", "-u", "api/main.py"]

# Запустимо наш застосунок всередині контейнера
# ENTRYPOINT [ "python", "api/main.py" ]

