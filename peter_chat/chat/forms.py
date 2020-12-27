from django import forms

class UserForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=30)
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=40)