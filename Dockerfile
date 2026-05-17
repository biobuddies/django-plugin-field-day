FROM debian:trixie-slim

# Copy PostgreSQL signing key
COPY postgresql-keyring.gpg /usr/share/keyrings/postgresql-keyring.gpg

# Install system dependencies
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    sqlite3-doc \
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

COPY entrypoint.sh /entrypoint.sh

EXPOSE 5432 3306

ENTRYPOINT ["/entrypoint.sh"]
