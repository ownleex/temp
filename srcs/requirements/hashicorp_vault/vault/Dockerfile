# syntax=docker/dockerfile:1
# escape=\

FROM hashicorp/vault@sha256:c51bb287709b74daefab32d1246cac767c32b8c73cb86509957634dffcd66a0e

RUN apk update \
	&& apk upgrade \
	&& apk add vim curl jq

# Create volumes for tokens services
RUN mkdir /vault/clients_tokens /vault/clients_tokens/user_handler_django /vault/clients_tokens/user_handler_postgres \
			/vault/clients_tokens/live_chat_django /vault/clients_tokens/live_chat_postgres /vault/clients_tokens/game_pong_django \
			/vault/clients_tokens/game_pong_postgres

# Copy vault config
COPY --chown=vault:vault ./conf/config/vault.hcl /vault/config/vault.hcl

# Copy vault policies
COPY --chown=vault:vault ./conf/config/vault_game_pong_django_policies.hcl /vault/config/vault_game_pong_django_policies.hcl
COPY --chown=vault:vault ./conf/config/vault_game_pong_postgres_policies.hcl /vault/config/vault_game_pong_postgres_policies.hcl
COPY --chown=vault:vault ./conf/config/vault_live_chat_django_policies.hcl /vault/config/vault_live_chat_django_policies.hcl
COPY --chown=vault:vault ./conf/config/vault_live_chat_postgres_policies.hcl /vault/config/vault_live_chat_postgres_policies.hcl
COPY --chown=vault:vault ./conf/config/vault_user_handler_django_policies.hcl /vault/config/vault_user_handler_django_policies.hcl
COPY --chown=vault:vault ./conf/config/vault_user_handler_postgres_policies.hcl /vault/config/vault_user_handler_postgres_policies.hcl

# Give rights vault config
RUN chmod 640 /vault/config/vault.hcl

# Give rights vault policies
RUN chmod 640 /vault/config/vault_game_pong_django_policies.hcl
RUN chmod 640 /vault/config/vault_game_pong_postgres_policies.hcl
RUN chmod 640 /vault/config/vault_live_chat_django_policies.hcl
RUN chmod 640 /vault/config/vault_live_chat_postgres_policies.hcl
RUN chmod 640 /vault/config/vault_user_handler_django_policies.hcl
RUN chmod 640 /vault/config/vault_user_handler_postgres_policies.hcl

CMD ["vault", "server", "-config=/vault/config/vault.hcl"]
