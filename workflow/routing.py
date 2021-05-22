from django.urls import re_path

from .consumers import RunMessageConsumer, AsyncRunStatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/messages/(?P<run_id>\w+)/$", RunMessageConsumer.as_asgi()),
    re_path(r"ws/run-status/(?P<run_id>\w+)/$", AsyncRunStatusConsumer.as_asgi()),
]
