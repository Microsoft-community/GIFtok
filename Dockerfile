FROM python:3.9-buster

RUN apt-get update
RUN apt-get -y install ffmpeg
RUN pip install --no-cache-dir discord requests

WORKDIR /usr/src/app
COPY . .

CMD ["./crashnt.py"]