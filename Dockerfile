FROM python:3.11

WORKDIR /usr/src/app
COPY ./requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt

COPY ./main.py .

ARG API_PORT="80"
ENV REDIS_ADD='redis-api-cache'
ENV MAIN_LOC='Tehran'

CMD uvicorn main:app --proxy-headers --host 0.0.0.0 --port ${API_PORT}