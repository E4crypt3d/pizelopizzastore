from django.urls import path
from .consumers import TrackOrder

ws_urlpatterns = [
    path('order/track/<str:order_id>', TrackOrder.as_asgi()),
]