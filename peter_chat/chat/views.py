from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
	return render(request, 'index.html', {})

def chat(request, room_name):
	#return render(request, "peter_chat.html", {})
	return render(request, 'peter_chat.html', {
        'room_name': room_name
    })
