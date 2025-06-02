#!/bin/bash

set -e

SECRET_KEY="$(LC_ALL=C tr -dc 'a-zA-Z0-9!#$%^&*()_+-=[]{}|;:,.?/' < /dev/urandom | head -c 50)"

jq --arg new_key "$SECRET_KEY" \
	'.service_user_handler_django.SECRET_KEY = $new_key | .service_live_chat_django.SECRET_KEY = $new_key | .service_game_pong_django.SECRET_KEY = $new_key' \
	./srcs/secrets/.secrets.json > temp.json && mv temp.json ./srcs/secrets/.secrets.json
