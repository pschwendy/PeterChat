from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from . import queries


# Create your views here.
from .forms import UserForm, LoginForm
def home(request):
	if request.method == 'POST':
		req = request.POST
		form = LoginForm(req)
		if len(req) == 5:
			form = UserForm(req)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				first_name = form.cleaned_data['first_name']
				last_name = form.cleaned_data['last_name']
				request.session['username'] = username
				#signup(username, password, first_name, signup)
				return HttpResponseRedirect('/chat/room')	
		elif len(req) == 3:
			form = LoginForm(req)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				request.session['username'] = username
				#login(username, password)
				return HttpResponseRedirect('/chat/room')	
	else:
		form = UserForm()
	return render(request, 'index.html', {'form': form})

def chat(request, room_name):
	username = request.session['username']
	#return render(request, "peter_chat.html", {})
	return render(request, 'peter_chat.html', {
        'room_name': room_name,
		'username': username
    })
