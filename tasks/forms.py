# tasks/forms.py

from django import forms

class LoginForm(forms.Form):
    nomusuario = forms.CharField(label='Nombre de Usuario', max_length=10)
    contrasenia = forms.CharField(label='Contraseña', widget=forms.PasswordInput())

class selCur(forms.Form):
    # como funciona esta cosa?
    idcurso = forms.HiddenInput()