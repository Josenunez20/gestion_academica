from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegistroForm

class RegistroView(CreateView):
    form_class = RegistroForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')   # Después de registrarse, va al login

    def form_valid(self, form):
        response = super().form_valid(form)
        # Opcional: auto-login después del registro
        # user = form.save()
        # login(self.request, user)
        return response

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True    # Si ya está logueado, redirige a LOGIN_REDIRECT_URL

class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'   # Plantilla de confirmación
    next_page = reverse_lazy('login')        # Redirige después del logout
    http_method_names = ['get', 'post'] 