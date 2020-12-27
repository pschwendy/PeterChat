from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .queries import signup, login


# Create your views here.
from .forms import UserForm, LoginForm, SignUpForm
def home(request):
	'''if request.session.get('username'):
		return HttpResponseRedirect('/chat/room')'''
	if request.method == 'POST':
		req = request.POST
		#form = LoginForm(req)
		if len(req) == 5:
			form = SignUpForm(req)
			if form.is_valid():
				username = form.cleaned_data['username']
				'''
				password = form.cleaned_data['password']
				first_name = form.cleaned_data['first_name']
				last_name = form.cleaned_data['last_name']'''
				try:
					signup(form)
					#signup(username, password, first_name, signup)
					request.session['username'] = username
					return HttpResponseRedirect('/chat/room')
				except:
					pass
		elif len(req) == 3:
			form = LoginForm(req)
			if form.is_valid():
				username = form.cleaned_data['username']
				password = form.cleaned_data['password']
				#
				#return HttpResponseRedirect('/chat/room')
				if login(username, password):
					request.session['username'] = username
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
