FROM python:3.9-alpine

RUN apk add --no-cache ffmpeg build-base && \
  pip install --no-cache-dir discord requests

RUN adduser -D user
#RUN groupadd -r user && useradd --no-log-init -r -g user user
RUN mkdir -p /usr/src/app && chown user:user /usr/src/app

USER user

WORKDIR /usr/src/app
COPY . .

CMD ["./crashnt.py"]
