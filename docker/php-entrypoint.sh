#!/bin/sh
set -eu
: "${ADMIN_PASSWORD:?Set ADMIN_PASSWORD in .env}"
data_file="${DOUTU_USERS_FILE:-/var/lib/doutu/users.json}"
mkdir -p "$(dirname "$data_file")"
if [ ! -f "$data_file" ]; then printf '[]\n' > "$data_file"; fi
chown www-data:www-data "$(dirname "$data_file")" "$data_file"
chmod 700 "$(dirname "$data_file")"
chmod 600 "$data_file"
exec docker-php-entrypoint "$@"
