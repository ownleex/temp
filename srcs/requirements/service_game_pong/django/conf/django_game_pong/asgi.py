"""
ASGI config for django_live_chat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Définir le module de settings avant tout import dépendant de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_game_pong.settings')

# Initialiser Django ASGI application pour charger les apps
django_asgi_app = get_asgi_application()

# Importer les modules dépendants de Django après l'initialisation
from core.middleware import CustomAuthMiddlewareStack
import core.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CustomAuthMiddlewareStack(
        URLRouter(
            core.routing.websocket_urlpatterns
        )
    ),
})
