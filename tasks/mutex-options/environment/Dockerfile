FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN git clone https://github.com/pallets/click.git . \
    && git checkout 08b803cf32ceb2ae6a772c62d5da42757a897d44

RUN pip install --no-cache-dir -e . pytest==8.4.1
