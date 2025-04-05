FROM postgres:16-alpine

RUN apk add --no-cache dcron curl
COPY backup_and_send.sh /usr/local/bin/backup_and_send.sh
COPY mydump.sql .
RUN chmod +x /usr/local/bin/backup_and_send.sh

# Добавить cron задачу в файл /etc/crontabs/root
RUN echo "0 7 * * * /usr/local/bin/backup_and_send.sh" >> /etc/crontabs/root

# Запустить cron в фоновом режиме и затем запустить PostgreSQL
CMD ["sh", "-c", "crond && docker-entrypoint.sh postgres"]
