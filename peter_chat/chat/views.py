from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def chat(request):
	return render(request, "peter_chat.html", {})
