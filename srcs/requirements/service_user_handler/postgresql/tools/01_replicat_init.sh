#!/bin/sh
set -e

VAULT_TOKEN=$(cat /etc/postgresql/user_handler_postgres/user_handler_postgres)

# Secrets extraction
PG_NAME=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/user_handler/postgres/postgres_database_name | jq -r ".data.postgres_database_name")
PG_USER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/user_handler/postgres/postgres_user | jq -r ".data.postgres_user")
PG_PASSWORD=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/user_handler/postgres/postgres_password | jq -r ".data.postgres_password")

# Wait until data base is ready
until pg_isready -U $PG_USER -d $PG_NAME; do
	echo coucou_1
	sleep 1
done

echo coucou_2
# Wait until tables access is OK
for table in auth_user shared_models_player shared_models_block shared_models_friendship; do
    until PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -t -c "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table';" | grep -q 1; do
        sleep 1
    done
done
echo coucou_3

# Create publications
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -c "
CREATE PUBLICATION auth_user_pub FOR TABLE auth_user;
CREATE PUBLICATION shared_models_pub FOR TABLE shared_models_player, shared_models_block, shared_models_friendship;"
echo coucou_4
