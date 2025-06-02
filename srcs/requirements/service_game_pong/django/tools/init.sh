#!/bin/sh

# Lancer Redis en arrière-plan avec des options pour minimiser les risques
redis-server --daemonize yes --maxmemory 256mb --maxmemory-policy allkeys-lru --save "" || { echo "Échec du démarrage de Redis"; exit 1; }

# Attendre que Redis soit prêt
until redis-cli ping | grep -q PONG > /dev/null; do
  echo "En attente de Redis..."
  sleep 1
done

echo "Redis fonctionnel"

source /django_web_app/.env/bin/activate > /dev/null \
	&& python3 manage.py makemigrations shared_models --no-input > /dev/null \
	&& python3 manage.py migrate --no-input > /dev/null \
	&& python3 manage.py makemigrations core --no-input > /dev/null \
	&& python3 manage.py migrate --no-input > /dev/null \
	&& python3 manage.py collectstatic --no-input > /dev/null \
	&& daphne -b 0.0.0.0 -p 8000 django_game_pong.asgi:application
