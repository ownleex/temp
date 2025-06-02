from channels.middleware import BaseMiddleware
from django.conf import settings
from channels.db import database_sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import AnonymousUser
from channels.auth import AuthMiddlewareStack
from shared_models.models import Player
import asyncio
from urllib.parse import parse_qs
from django.http import JsonResponse
import json
import re

# Middleware existant pour l'authentification JWT
@database_sync_to_async
def get_user_from_token(token):
    try:
        jwt_auth = JWTAuthentication()
        validated_token = jwt_auth.get_validated_token(token)
        user = jwt_auth.get_user(validated_token)
        return user
    except (InvalidToken, TokenError):
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = parse_qs(scope['query_string'].decode())
        token_list = query_string.get('token', None)

        if token_list:
            token = token_list[0]
            scope['user'] = await get_user_from_token(token)
            if scope['user'].is_authenticated:
                try:
                    player = await database_sync_to_async(lambda: scope['user'].player_profile)()
                    scope['player_id'] = player.id
                except Player.DoesNotExist:
                    scope['player_id'] = None
            else:
                scope['player_id'] = None
        else:
            scope['user'] = AnonymousUser()
            scope['player_id'] = None

        return await self.inner(scope, receive, send)

# Middleware pour vérifier ALLOWED_HOSTS
class AllowedHostsMiddleware(BaseMiddleware):
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        # Extraire l'en-tête Host
        host = None
        for header_name, header_value in scope['headers']:
            if header_name == b'host':
                host = header_value.decode('utf-8')
                break

        # Vérifier si l'hôte est dans ALLOWED_HOSTS
        if host:
            host_name = host.split(':')[0]
            if host_name not in settings.ALLOWED_HOSTS:
                # Accepter la connexion WebSocket
                await send({
                    'type': 'websocket.accept'
                })
                # Envoyer un message de fermeture
                await send({
                    'type': 'websocket.close',
                    'code': 3016,
                    'reason': 'Invalid Host header'
                })
                await asyncio.sleep(0.1)
                return

        return await self.inner(scope, receive, send)

# Mise à jour de CustomAuthMiddlewareStack pour inclure AllowedHostsMiddleware
def CustomAuthMiddlewareStack(inner):
    return AllowedHostsMiddleware(JWTAuthMiddleware(AuthMiddlewareStack(inner)))

class XSSProtectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('POST', 'PATCH'):
            # Regex combinée pour XSS et SQL
            malicious_pattern = re.compile(
                r'[<>\'";]|--|/\*|\*/|script|on(click|load|mouseover|mouseout|submit|change|focus|blur|keypress|keydown|keyup)|(\b(union|select|insert|delete|update|drop|alter|exec|create|truncate|grant|revoke)\b\s*(all|from|into|set|table)?\s*[^\w])',
                re.IGNORECASE
            )
            if request.content_type == 'application/json':
                try:
                    data = json.loads(request.body)
                    for key, value in data.items():
                        if isinstance(value, str) and malicious_pattern.search(value):
                            return JsonResponse({"code": 1100, "message": f"Characters not allowed in {key}"}, status=400)
                except json.JSONDecodeError:
                    return JsonResponse({"code": 1015, "message": "JSON invalid"}, status=400)
            elif request.content_type.startswith('multipart/form-data'):
                for key, value in request.POST.items():
                    if malicious_pattern.search(value):
                        return JsonResponse({"code": 1100, "message": f"Characters not allowed in {key}"}, status=400)
        return self.get_response(request)
