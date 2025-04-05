FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y wget gnupg2 \
    && echo "deb http://apt.postgresql.org/pub/repos/apt bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && wget -qO - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && apt-get update \
    && apt-get install -y postgresql-client-16 \
    && rm -rf /var/lib/apt/lists/*
COPY req.txt /app/
RUN pip install --no-cache-dir -r req.txt
COPY . /app/