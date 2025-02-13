from django.urls import path
from .consumer import EmotionDetectionConsumer

websocket_urlpatterns = [
    path("ws/emotion-detection/", EmotionDetectionConsumer.as_asgi()),
]
