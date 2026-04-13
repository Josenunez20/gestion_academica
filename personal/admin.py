from django.contrib import admin
from .models import PersonalAcademico

@admin.register(PersonalAcademico)
class PersonalAcademicoAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'cedula', 'nombre_apellido', 'telefono', 'correo')
    search_fields = ('nombre_apellido', 'cedula', 'entidad', 'correo')
    list_filter = ('entidad',)