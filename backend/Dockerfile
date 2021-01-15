FROM python:3.7-alpine as build-env

ENV LANG=es_CO.UTF-8
ENV LC_ALL=es_CO.UTF-8
ENV LC_CTYPE=es_CO.UTF8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

FROM build-env
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
EXPOSE 5000
EXPOSE 27017
EXPOSE 28017
