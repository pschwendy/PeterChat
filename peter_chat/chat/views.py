from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect

# Create your views here.
from .forms import UserForm
def home(request):
	if request.method == 'POST':
		form = UserForm(request.POST)
		return HttpResponseRedirect('/chat/room')
	else:
		form = UserForm()
	return render(request, 'index.html', {'form': form})

def chat(request, room_name):
	#return render(request, "peter_chat.html", {})
	return render(request, 'peter_chat.html', {
        'room_name': room_name
    })
