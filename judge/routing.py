from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/judge/queue/", consumers.QueueUpdateConsumer.as_asgi()),
    re_path(r"ws/judge/scoreboard/", consumers.ScoreboardUpdateConsumer.as_asgi()),
]
