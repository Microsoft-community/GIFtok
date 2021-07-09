FROM python:3.9-alpine

RUN apk add --no-cache ffmpeg build-base

RUN adduser -D user
#RUN groupadd -r user && useradd --no-log-init -r -g user user
RUN mkdir -p /usr/src/app && chown user:user /usr/src/app
WORKDIR /usr/src/app
USER user

COPY requirements.txt .
RUN  pip install -r requirements.txt

COPY . .

CMD ["./crashnt.py"]
