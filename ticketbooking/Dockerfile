# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /ticketbooking

RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    wget \
    && apt-get clean

# Install a newer version of SQLite (for example, version 3.35.5)
RUN wget https://www.sqlite.org/2021/sqlite-autoconf-3350500.tar.gz \
    && tar -xvzf sqlite-autoconf-3350500.tar.gz \
    && cd sqlite-autoconf-3350500 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install \
    && cd .. \
    && rm -rf sqlite-autoconf-3350500

# Verify SQLite version
RUN sqlite3 --version

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .