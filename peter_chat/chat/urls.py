from django.urls import path
from . import views

urlpatterns = [
	path('', views.home),
	path('logout', views.logout),
	path('chat/<str:room_name>/', views.chat, name='room'),
	path('user/<int:user_number>/', views.inbox, name='room'),
]
