from django.contrib import admin
from .models import ResponsableAcademico, TutorRegional, TutorNacional

@admin.register(ResponsableAcademico)
class ResponsableAcademicoAdmin(admin.ModelAdmin):
    list_display = ('entidad', 'cedula', 'nombre_apellido', 'telefono', 'correo')
    search_fields = ('nombre_apellido', 'cedula', 'entidad', 'correo')
    list_filter = ('entidad',)


@admin.register(TutorRegional)
class TutorRegionalAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'cedula', 'entidad', 'condicion_laboral', 'area_formacion')
    search_fields = ('nombre_apellido', 'cedula', 'entidad', 'area_formacion')
    list_filter = ('entidad', 'condicion_laboral', 'area_formacion')


@admin.register(TutorNacional)
class TutorNacionalAdmin(admin.ModelAdmin):
    list_display = ('nombre_apellido', 'programa_formacion', 'cedula', 'telefono', 'correo')
    search_fields = ('nombre_apellido', 'cedula', 'programa_formacion', 'correo')
    list_filter = ('programa_formacion',)