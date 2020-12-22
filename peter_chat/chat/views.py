from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def chat(request, room_name):
	#return render(request, "peter_chat.html", {})
	return render(request, 'peter_chat.html', {
        'room_name': room_name
    })
