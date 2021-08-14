FROM python:3.9-alpine3.13

RUN apk add --no-cache ffmpeg build-base && \  
    pip install pipenv

RUN adduser -D user
#RUN groupadd -r user && useradd --no-log-init -r -g user user
RUN mkdir -p /usr/src/app && chown user:user /usr/src/app
WORKDIR /usr/src/app
USER user

COPY requirements.txt .
COPY Pipfile* ./
RUN  pipenv install --deploy --ignore-pipfile

COPY . .

CMD ["pipenv", "run", "bot"]
