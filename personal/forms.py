from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# Formulario para subir Excel
class ExcelUploadForm(forms.Form):
    TIPO_CHOICES = [
        ('', '---------- Selecciona un tipo ----------'),  # Opción vacía por defecto
        ('auto', '🤖 Detección automática (recomendado)'),
        ('responsables', '📋 Responsables Académicos'),
        ('tutores_regionales', '🏫 Tutores Regionales'),
        ('tutores_nacionales', '🎓 Tutores Nacionales'),
    ]
    
    tipo_personal = forms.ChoiceField(
        choices=TIPO_CHOICES,
        label="Tipo de personal a cargar",
        required=False,  # No obligatorio
        initial='auto',  # Por defecto: detección automática
        help_text="Selecciona 'Detección automática' o elige manualmente el tipo de documento."
    )
    archivo_excel = forms.FileField(
        label="Selecciona archivo Excel",
        help_text="Formatos aceptados: .xlsx. La detección automática identificará el tipo de documento."
    )
    
# Formulario para registro de usuarios
class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'correo@ejemplo.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nombre'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Apellido'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Nombre de usuario'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Contraseña'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Confirmar contraseña'
        })
        self.fields['password1'].help_text = "Mínimo 8 caracteres. No uses contraseñas comunes."
        self.fields['password2'].help_text = "Repite la misma contraseña."

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user