#!/bin/bash

# Récupère le nom d'hôte sans option incompatible
DOMAIN=$(hostname)

# Si l'utilisateur a un nom de domaine custom dans .env_user, on le prend
if [ -f "./srcs/env/.env_user" ]; then
    CUSTOM_DOMAIN=$(grep DOMAIN_NAME ./srcs/env/.env_user | cut -d '=' -f2)
    if [ -n "$CUSTOM_DOMAIN" ]; then
        DOMAIN="$CUSTOM_DOMAIN"
    fi
fi

# Remplace DOMAIN_NAME dans .env_nginx (compatible macOS et Linux)
if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s|^DOMAIN_NAME=.*|DOMAIN_NAME='$DOMAIN'|" ./srcs/env/.env_nginx
else
    sed -i "s|^DOMAIN_NAME=.*|DOMAIN_NAME='$DOMAIN'|" ./srcs/env/.env_nginx
fi

# Même chose dans docker-compose.yml (si nécessaire)
if grep -q "DOMAIN_NAME=" ./srcs/docker-compose.yml; then
    if [ "$(uname)" = "Darwin" ]; then
        sed -i '' "s|DOMAIN_NAME=.*|DOMAIN_NAME=$DOMAIN|" ./srcs/docker-compose.yml
    else
        sed -i "s|DOMAIN_NAME=.*|DOMAIN_NAME=$DOMAIN|" ./srcs/docker-compose.yml
    fi
fi

echo "Mise à jour réussie : DOMAIN_NAME='$DOMAIN' dans ./srcs/env/.env_nginx"
