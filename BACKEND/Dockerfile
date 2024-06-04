FROM python:3.11

ENV APP_BASE ./
ENV APP_HOME /app 

WORKDIR $APP_HOME

COPY ${APP_BASE}requirements.txt requirements.txt

RUN pip install -r requirements.txt


COPY $APP_BASE  ./

RUN apt update -q && apt install -y dos2unix

# Convert line endings for all shell scripts
RUN find . -name '*.sh' -exec dos2unix {} + -exec chmod +x {} +


CMD [ "bash" , "./run.sh" ] 

#CMD bash

#CMD ["python", "-u", "api/main.py"]

# ENTRYPOINT [ "python", "api/main.py" ]

