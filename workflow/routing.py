from django.urls import re_path

from .consumers import RunMessageConsumer

websocket_urlpatterns = [
    re_path(r"ws/messages/(?P<run_id>\w+)/$", RunMessageConsumer.as_asgi()),
]
