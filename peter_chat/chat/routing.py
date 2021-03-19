# chat/routing.py
from django.urls import re_path
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'^ws/user/(?P<user_number>[^/]+)/$', consumers.InboxConsumer.as_asgi()),
]
