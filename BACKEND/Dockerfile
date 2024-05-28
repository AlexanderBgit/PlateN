FROM python:3.11

ENV APP_BASE ./
ENV APP_HOME /app 

WORKDIR $APP_HOME

COPY ${APP_BASE}requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY $APP_BASE  ./


CMD bash ./run.sh 

#CMD bash

#CMD ["python", "-u", "api/main.py"]

# ENTRYPOINT [ "python", "api/main.py" ]

