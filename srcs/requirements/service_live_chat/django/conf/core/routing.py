from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'live_chat/ws/chat/general/$', consumers.GeneralChatConsumer.as_asgi()),
    re_path(r'live_chat/ws/chat/private/(?P<player_id>\d+)/$', consumers.PrivateChatConsumer.as_asgi()),
]
