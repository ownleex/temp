all:

	@sh ./scripts/set_dom.sh
	@sh ./scripts/django_secret_key_gen.sh

	@docker compose -f ./srcs/docker-compose.yml down > /dev/null

	@if [ $$(docker images -qa | wc -l) -ne 0 ]; then \
		docker rmi -f $(shell docker images -qa) > /dev/null; \
	fi

	@if [ $$(docker network ls -q | wc -l) -ne 0 ]; then \
		docker network prune -f > /dev/null; \
	fi

	@if [ $$(docker volume ls -q | wc -l) -ne 0 ]; then \
		docker volume rm -f $(shell docker volume ls -q) > /dev/null; \
	fi

	@if [ -e ./srcs/secrets/.vault_secrets_key.json ]; then \
		rm ./srcs/secrets/.vault_secrets_key.json > /dev/null; \
	fi

	@docker compose -f ./srcs/docker-compose.yml up -d vault > /dev/null

	@sh -c "./srcs/requirements/hashicorp_vault/vault/tools/init.sh"

	@docker compose -f ./srcs/docker-compose.yml up -d service_user_handler_postgresql > /dev/null
	@docker compose -f ./srcs/docker-compose.yml up -d service_game_pong_postgresql > /dev/null
	@docker compose -f ./srcs/docker-compose.yml up -d service_live_chat_postgresql > /dev/null

	@docker compose -f ./srcs/docker-compose.yml up -d > /dev/null
 
	@docker exec service_user_handler_postgresql sh /home/init/01_replicat_init.sh > /dev/null
	@docker exec service_game_pong_postgresql sh /home/init/01_replicat_init.sh > /dev/null
	@docker exec service_live_chat_postgresql sh /home/init/01_replicat_init.sh > /dev/null
	@docker exec service_user_handler_postgresql sh /home/init/02_replicat_init.sh > /dev/null

fclean:

	@docker compose -f ./srcs/docker-compose.yml down > /dev/null

	@if [ $$(docker images -qa | wc -l) -ne 0 ]; then \
		docker rmi -f $(shell docker images -qa) > /dev/null; \
	fi

	@if [ $$(docker network ls -q | wc -l) -ne 0 ]; then \
		docker network prune -f > /dev/null; \
	fi

	@if [ $$(docker volume ls -q | wc -l) -ne 0 ]; then \
		docker volume rm -f $(shell docker volume ls -q) > /dev/null; \
	fi

	@if [ -e ./srcs/secrets/.vault_secrets_key.json ]; then \
		rm ./srcs/secrets/.vault_secrets_key.json > /dev/null; \
	fi