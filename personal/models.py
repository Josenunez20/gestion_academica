from django.db import models

class ResponsableAcademico(models.Model):
    entidad = models.CharField(max_length=100)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    nombre_apellido = models.CharField(max_length=200)
    responsabilidad = models.CharField(max_length=100, default="GESTION ACADEMICA")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_apellido} - {self.entidad}"

    class Meta:
        verbose_name = "Responsable Académico"
        verbose_name_plural = "Responsables Académicos"


class TutorRegional(models.Model):
    cedula = models.CharField(max_length=20)
    nombre_apellido = models.CharField(max_length=200)
    entidad = models.CharField(max_length=100)
    condicion_laboral = models.CharField(max_length=50, blank=True, null=True)
    area_formacion = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_apellido} - {self.entidad} ({self.area_formacion})"

    class Meta:
        verbose_name = "Tutor Regional"
        verbose_name_plural = "Tutores Regionales"


class TutorNacional(models.Model):
    nombre_apellido = models.CharField(max_length=200)
    programa_formacion = models.CharField(max_length=255, blank=True, null=True)
    cedula = models.CharField(max_length=20, blank=True, null=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre_apellido} - {self.programa_formacion}"

    class Meta:
        verbose_name = "Tutor Nacional"
        verbose_name_plural = "Tutores Nacionales"