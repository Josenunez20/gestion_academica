from django.urls import path
from .views import RegistroView, CustomLoginView, CustomLogoutView

urlpatterns = [
    path('registro/', RegistroView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
]