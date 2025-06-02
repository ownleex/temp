from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'pong/ws/match/(?P<match_id>\d+)/$', consumers.PongConsumer.as_asgi()),
    re_path(r'^pong/ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]