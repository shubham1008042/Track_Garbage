from django.http import HttpResponse
import datetime
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomUserCreationForm

class Login(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/login.html'


class Signup(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('signup')
    template_name='signup.html'
