#!/bin/sh
set -e

VAULT_TOKEN=$(cat /etc/postgresql/game_pong_postgres/game_pong_postgres)

# Secrets extraction
PG_NAME=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/game_pong/postgres/postgres_database_name | jq -r ".data.postgres_database_name")
PG_USER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/game_pong/postgres/postgres_user | jq -r ".data.postgres_user")
PG_PASSWORD=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/game_pong/postgres/postgres_password | jq -r ".data.postgres_password")

sed -i "s/PG_NAME/$PG_NAME/g" /var/lib/postgresql/data/pg_hba.conf
sed -i "s/PG_USER/$PG_USER/g" /var/lib/postgresql/data/pg_hba.conf

# Starts postgres temporarily
pg_ctl -D /var/lib/postgresql/data -o "-c listen_addresses='localhost'" -w start

# Create super user, create replicator, create database, grant privilleges to super user
psql -U postgres -c "CREATE ROLE $PG_USER WITH SUPERUSER CREATEDB CREATEROLE REPLICATION BYPASSRLS LOGIN PASSWORD '$PG_PASSWORD';"
psql -U postgres -c "CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD '$PG_PASSWORD';"
psql -U postgres -c "CREATE DATABASE $PG_NAME OWNER $PG_USER;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $PG_NAME TO $PG_USER;"

# Wait until data base is ready
until pg_isready -U "$PG_USER" -d "$PG_NAME"; do
	sleep 1
done

# Grant privilleges to replicator
PGPASSWORD=$PG_PASSWORD psql -U "$PG_USER" -d "$PG_NAME" -c "GRANT USAGE ON SCHEMA public TO replicator;"
PGPASSWORD=$PG_PASSWORD psql -U "$PG_USER" -d "$PG_NAME" -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;"
PGPASSWORD=$PG_PASSWORD psql -U "$PG_USER" -d "$PG_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO replicator;"

# Stop postgres temporarily
pg_ctl -D /var/lib/postgresql/data stop
