FROM python:3.10-alpine
LABEL maintainer="mamanadarin@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pip install wheel setuptools pip --upgrade
RUN pip install -r requirements.txt
RUN apk del .tmp-build-deps

RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

COPY . .

USER django-user
