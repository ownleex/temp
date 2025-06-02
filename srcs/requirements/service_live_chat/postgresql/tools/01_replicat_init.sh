#!/bin/sh
set -e

VAULT_TOKEN=$(cat /etc/postgresql/live_chat_postgres/live_chat_postgres)
VAULT_TOKEN_USER_HANDLER=$(cat /etc/postgresql/user_handler_postgres/user_handler_postgres)
VAULT_TOKEN_GAME_PONG=$(cat /etc/postgresql/game_pong_postgres/game_pong_postgres)

# Secrets extraction
PG_NAME=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/live_chat/postgres/postgres_database_name | jq -r ".data.postgres_database_name")
PG_USER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/live_chat/postgres/postgres_user | jq -r ".data.postgres_user")
PG_PASSWORD=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN" http://vault:8200/v1/secret/live_chat/postgres/postgres_password | jq -r ".data.postgres_password")

PG_NAME_USER_HANDLER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_USER_HANDLER" http://vault:8200/v1/secret/user_handler/postgres/postgres_database_name | jq -r ".data.postgres_database_name")
PG_USER_USER_HANDLER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_USER_HANDLER" http://vault:8200/v1/secret/user_handler/postgres/postgres_user | jq -r ".data.postgres_user")
PG_PASSWORD_USER_HANDLER=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_USER_HANDLER" http://vault:8200/v1/secret/user_handler/postgres/postgres_password | jq -r ".data.postgres_password")

PG_NAME_GAME_PONG=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_GAME_PONG" http://vault:8200/v1/secret/game_pong/postgres/postgres_database_name | jq -r ".data.postgres_database_name")
PG_USER_GAME_PONG=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_GAME_PONG" http://vault:8200/v1/secret/game_pong/postgres/postgres_user | jq -r ".data.postgres_user")
PG_PASSWORD_GAME_PONG=$(curl -q --silent --header "X-Vault-Token: $VAULT_TOKEN_GAME_PONG" http://vault:8200/v1/secret/game_pong/postgres/postgres_password | jq -r ".data.postgres_password")

# Wait until data base is ready
until pg_isready -U $PG_USER -d $PG_NAME; do
	sleep 1
done

# Wait until service_user_handler_postgresql data base is ready
until pg_isready -h service_user_handler_postgresql -U $PG_USER_USER_HANDLER -d $PG_NAME_USER_HANDLER; do
	sleep 1
done

# Wait until service_game_pong_postgresql data base is ready
until pg_isready -h service_game_pong_postgresql -U $PG_USER_GAME_PONG -d $PG_NAME_GAME_PONG; do
	sleep 1
done

# Wait until tables access is OK
for table in auth_user shared_models_tournament shared_models_player shared_models_block shared_models_friendship; do
	until PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -t -c "SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '$table';" | grep -q 1; do
		sleep 1
	done
done

# Wait until auth_user_pub publication access on service_user_handler_postgresql is OK
until PGPASSWORD=$PG_PASSWORD_USER_HANDLER psql -h service_user_handler_postgresql -U $PG_USER_USER_HANDLER -d $PG_NAME_USER_HANDLER -t -c "SELECT 1 FROM pg_publication WHERE pubname = 'auth_user_pub';" | grep -q 1; do
	sleep 1
done

# Wait until shared_models_pub publication access on service_user_handler_postgresql is OK
until PGPASSWORD=$PG_PASSWORD_USER_HANDLER psql -h service_user_handler_postgresql -U $PG_USER_USER_HANDLER -d $PG_NAME_USER_HANDLER -t -c "SELECT 1 FROM pg_publication WHERE pubname = 'shared_models_pub';" | grep -q 1; do
	sleep 1
done

# Wait until publication access on service_game_pong_postgresql is OK
until PGPASSWORD=$PG_PASSWORD_GAME_PONG psql -h service_game_pong_postgresql -U $PG_USER_GAME_PONG -d $PG_NAME_GAME_PONG -t -c "SELECT 1 FROM pg_publication WHERE pubname = 'tournament_match_pub';" | grep -q 1; do
	sleep 1
done

# Create subscription and connect to service_user_handler_postgresql service_game_pong_postgresql publications
PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -c "
CREATE SUBSCRIPTION chat_sub_auth_user
CONNECTION 'host=service_user_handler_postgresql dbname=$PG_NAME_USER_HANDLER user=replicator password=$PG_PASSWORD_USER_HANDLER'
PUBLICATION auth_user_pub;"

PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -c "
CREATE SUBSCRIPTION chat_sub_tournament_data
CONNECTION 'host=service_game_pong_postgresql dbname=$PG_NAME_GAME_PONG user=replicator password=$PG_PASSWORD_GAME_PONG'
PUBLICATION tournament_match_pub;"

PGPASSWORD=$PG_PASSWORD psql -U $PG_USER -d $PG_NAME -c "
CREATE SUBSCRIPTION chat_sub_player_data
CONNECTION 'host=service_user_handler_postgresql dbname=$PG_NAME_USER_HANDLER user=replicator password=$PG_PASSWORD_USER_HANDLER'
PUBLICATION shared_models_pub;"
