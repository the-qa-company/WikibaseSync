FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y git
RUN apt-get install -y procps

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD "./script.sh"