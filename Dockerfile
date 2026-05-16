FROM debian:trixie-slim

# Copy PostgreSQL signing key
COPY postgresql-keyring.gpg /usr/share/keyrings/postgresql-keyring.gpg

# Install system dependencies
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    mariadb-server \
    mariadb-client \
    && echo "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] http://apt.postgresql.org/pub/repos/apt trixie-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    # hadolint ignore=DL3008
    && apt-get install -y --no-install-recommends \
    postgresql-17 \
    postgresql-client-17 \
    postgresql-doc-17 \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/postgresql/17/bin:$PATH"
ENV PGDATA="/var/lib/postgresql/data"

RUN mkdir -p "$PGDATA" && chown -R postgres:postgres "$PGDATA"

COPY <<-"EOF" /entrypoint.sh
#!/bin/bash
set -o errexit -o nounset -o pipefail

case "${1:-}" in
    postgres)
        if [ -z "$(ls -A $PGDATA)" ]; then
            su -m postgres -c "initdb -D $PGDATA"
            echo "host all all 0.0.0.0/0 trust" >> "$PGDATA/pg_hba.conf"
        fi
        echo "listen_addresses='*'" >> "$PGDATA/postgresql.conf"
        exec su -m postgres -c "postgres -D $PGDATA"
        ;;
    mariadb)
        if [ ! -d /var/lib/mysql/mysql ]; then
            mysql_install_db --user=mysql --datadir=/var/lib/mysql
        fi
        exec mysqld --user=mysql --bind-address=0.0.0.0
        ;;
    *)
        echo "Usage: $0 {postgres|mariadb}" >&2
        exit 1
        ;;
esac
EOF

RUN chmod +x /entrypoint.sh

EXPOSE 5432 3306

ENTRYPOINT ["/entrypoint.sh"]
