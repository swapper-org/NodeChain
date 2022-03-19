FROM postgres:12

COPY create_tables.sql /docker-entrypoint-initdb.d/create_tables.sql
COPY create_users.sh /docker-entrypoint-initdb.d/create_users.sh

CMD ["postgres"]
