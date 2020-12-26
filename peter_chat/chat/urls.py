from django.urls import path
from . import views

urlpatterns = [
	path('', views.home),
	path('chat/<str:room_name>/', views.chat, name='room'),
]
