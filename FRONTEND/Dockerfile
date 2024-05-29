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
# OS package dependecy for pdf2impg
RUN apt update -q && apt install -y poppler-utils dos2unix

# Скопіюємо інші файли в робочу директорію контейнера
COPY $APP_BASE  ./

# Convert line endings for all shell scripts
RUN  find . -name '*.sh' -exec dos2unix {} + -exec chmod +x {} +

# Debug step to verify conversion
RUN file ./run.sh

# CMD bash ./run.sh 
CMD [ "bash" , "./run.sh" ] 
#CMD bash

# Запустимо наш застосунок всередині контейнера
# ENTRYPOINT [ "bash", "./run.sh" ]

