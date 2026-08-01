#!/bin/bash
set -o errexit -o nounset -o pipefail

case "${1:-}" in
    postgres)
        if [ -z "$(ls -A "$PGDATA")" ]; then
            su -m postgres -c "initdb -D $PGDATA"
        fi
        exec su -m postgres -c \
            "postgres -D $PGDATA -c hba_file=/etc/postgresql/pg_hba.conf -c listen_addresses='*'"
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
