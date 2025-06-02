#!/bin/sh

source /django_web_app/.env/bin/activate > /dev/null \
	&& python3 manage.py makemigrations shared_models --no-input > /dev/null \
    && python3 manage.py migrate --no-input > /dev/null \
	&& python3 manage.py makemigrations core --no-input > /dev/null \
    && python3 manage.py migrate --no-input > /dev/null \
	&& python3 manage.py collectstatic --no-input > /dev/null \
	&& python3 /django_web_app/utils/create_superuser.py > /dev/null \
	&& gunicorn --workers=9 django_user_handler.wsgi:application --bind 0.0.0.0:8000
