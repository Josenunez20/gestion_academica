from django.urls import path
from . import views

urlpatterns = [
    # Rutas de autenticación
    path('registro/', views.RegistroView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Rutas de la aplicación
    path('', views.search_personal, name='search'),
    path('upload/', views.upload_excel, name='upload'),
    path('search/', views.search_personal, name='search'),
]