from django import forms

class UserForm(forms.Form):
    first_name = forms.CharField(label='first name', max_length=32)
    last_name = forms.CharField(label='last name', max_length=40)
    username = forms.CharField(label='username', max_length=20)
    password = forms.CharField(label='password', max_length=30, widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField(label='username', max_length=20)
    password = forms.CharField(label='password', max_length=30, widget=forms.PasswordInput)