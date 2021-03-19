from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .queries import signup, login, get_user_pk


# Create your views here.
from .forms import UserForm, LoginForm, SignUpForm
def home(request):
	'''if request.session.get('username'):
		return HttpResponseRedirect('/chat/room')'''
	try:
		if request.COOKIES['username']:
			unum = get_user_pk(request.COOKIES['username'])
			response = HttpResponseRedirect(f'/user/{unum}')
			return response
	except:
		pass

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
					user_pk = get_user_pk(username)
					response = HttpResponseRedirect(f'/user/{user_pk}')
					response.set_cookie('username', username)
					return response
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
					user_pk = get_user_pk(username)
					response = HttpResponseRedirect(f'/user/{user_pk}')
					response.set_cookie('username', username)
					return response
	else:
		form = UserForm()
	return render(request, 'index.html', {'form': form})

def chat(request, room_name):
	username = request.COOKIES['username']
	
	#return render(request, "peter_chat.html", {})
	return render(request, 'peter_chat.html', {
        'room_name': room_name,
		'username': username
    })

def inbox(request, user_number):
	username = request.COOKIES['username']
	
	#return render(request, "peter_chat.html", {})
	return render(request, 'inbox.html', {
        'user_number': user_number,
		'username': username
    })

def logout(request):
	response = HttpResponseRedirect('/')
	response.delete_cookie('username')
	return response
