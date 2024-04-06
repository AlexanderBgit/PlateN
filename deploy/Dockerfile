# Docker-команда FROM вказує базовий образ контейнера
# Наш базовий образ - це Linux з попередньо встановленим python-3.11
# FROM python:3.11
FROM python:3.11

# Встановимо змінну середовища
ENV APP_BASE ../FRONTEND/
ENV APP_HOME /app 

# Встановимо робочу директорію всередині контейнера
WORKDIR $APP_HOME

# Скопіюємо інші файли в робочу директорію контейнера
COPY $APP_BASE  .
# COPY .env .env
#COPY run.sh run.sh 
#COPY src/ src/
#COPY templates/ templates/
#COPY tests/ tests/
#COPY static/ static/
#COPY docs/ docs/
#COPY main.py main.py

COPY .${APP_BASE}requirements.txt requirements.txt

# Встановимо залежності всередині контейнера
# RUN pip install -r requirements.txt 
# RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt
RUN pip install -r requirements.txt 

CMD bash ./run.sh 

# CMD bash

#CMD ["python", "-u", "src/main.py"]

# Запустимо наш застосунок всередині контейнера
# ENTRYPOINT [ "python", "src/main.py" ]

