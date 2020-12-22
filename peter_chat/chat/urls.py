from django.urls import path
from . import views

urlpatterns = [
	#path('chat/', views.chat)
	path('chat/<str:room_name>/', views.chat, name='room'),
]
