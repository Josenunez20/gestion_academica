from django.db import models

class PersonalAcademico(models.Model):
    entidad = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    nombre_apellido = models.CharField(max_length=200)
    responsabilidad = models.CharField(max_length=100, default="GESTION ACADEMICA")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_apellido} - {self.entidad}"

    class Meta:
        verbose_name = "Personal Académico"
        verbose_name_plural = "Personal Académico"