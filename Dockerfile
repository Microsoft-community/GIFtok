FROM python:3.9-buster

RUN apt-get update && \
  apt-get -y install ffmpeg && \
  pip install --no-cache-dir discord requests

WORKDIR /usr/src/app
COPY . .

CMD ["./crashnt.py"]
