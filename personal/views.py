import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView

from .forms import ExcelUploadForm, RegistroForm
from .models import PersonalAcademico


# ============================================
# VISTAS DE AUTENTICACIÓN
# ============================================

class RegistroView(CreateView):
    """Vista para registro de nuevos usuarios"""
    form_class = RegistroForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        # Opcional: auto-login después del registro
        # user = form.save()
        # login(self.request, user)
        messages.success(self.request, "¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.")
        return super().form_valid(form)


class CustomLoginView(LoginView):
    """Vista para inicio de sesión"""
    template_name = 'auth/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        messages.success(self.request, f"¡Bienvenido {self.request.user.username}!")
        return reverse_lazy('search')


class CustomLogoutView(LogoutView):
    """Vista para cerrar sesión"""
    template_name = 'auth/logout.html'
    next_page = reverse_lazy('login')
    http_method_names = ['get', 'post', 'options']
    
    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() == 'post':
            messages.success(request, "Has cerrado sesión correctamente.")
        return super().dispatch(request, *args, **kwargs)


# ============================================
# VISTAS DE LA APLICACIÓN PRINCIPAL
# ============================================

@login_required
def upload_excel(request):
    """Vista para subir y procesar archivos Excel"""
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            try:
                # Leer el archivo Excel con pandas
                df = pd.read_excel(archivo, engine='openpyxl', header=None)

                # En el archivo de ejemplo, los datos comienzan en la fila 7 (índice 6)
                # Las columnas esperadas: N°(0), ENTIDAD(1), CEDULA(2), NOMBRE(3), RESP(4), TEL(5), CORREO(6)
                data_rows = df.iloc[6:, 1:7]  # desde fila 7, columnas B a G
                data_rows.columns = ['entidad', 'cedula', 'nombre', 'responsabilidad', 'telefono', 'correo']

                registros_creados = 0
                registros_actualizados = 0

                for _, row in data_rows.iterrows():
                    # Saltar filas completamente vacías
                    if pd.isna(row['entidad']) and pd.isna(row['nombre']):
                        continue

                    # Limpiar valores NaN
                    entidad = str(row['entidad']).strip() if not pd.isna(row['entidad']) else ''
                    nombre = str(row['nombre']).strip() if not pd.isna(row['nombre']) else ''
                    responsabilidad = str(row['responsabilidad']).strip() if not pd.isna(row['responsabilidad']) else 'GESTION ACADEMICA'
                    correo = str(row['correo']).strip() if not pd.isna(row['correo']) else ''

                    # Manejar cédula y teléfono (pueden venir como números o strings)
                    if not pd.isna(row['cedula']):
                        try:
                            cedula = str(int(row['cedula']))
                        except (ValueError, TypeError):
                            cedula = str(row['cedula']).strip()
                    else:
                        cedula = ''

                    if not pd.isna(row['telefono']):
                        try:
                            telefono = str(int(row['telefono']))
                        except (ValueError, TypeError):
                            telefono = str(row['telefono']).strip()
                    else:
                        telefono = ''

                    # Solo crear/actualizar si al menos entidad y nombre existen
                    if entidad and nombre:
                        obj, created = PersonalAcademico.objects.update_or_create(
                            entidad=entidad,
                            cedula=cedula if cedula else None,
                            defaults={
                                'nombre_apellido': nombre,
                                'responsabilidad': responsabilidad,
                                'telefono': telefono,
                                'correo': correo,
                            }
                        )
                        if created:
                            registros_creados += 1
                        else:
                            registros_actualizados += 1

                messages.success(
                    request,
                    f"✅ Archivo procesado exitosamente. "
                    f"{registros_creados} registros nuevos, {registros_actualizados} actualizados."
                )
                return redirect('search')
            except Exception as e:
                messages.error(request, f"❌ Error al procesar el archivo: {e}")
    else:
        form = ExcelUploadForm()

    return render(request, 'personal/upload.html', {'form': form})


@login_required
def search_personal(request):
    """Vista para buscar personal académico"""
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        resultados = PersonalAcademico.objects.filter(
            Q(nombre_apellido__icontains=query) |
            Q(cedula__icontains=query) |
            Q(entidad__icontains=query) |
            Q(correo__icontains=query)
        ).order_by('entidad', 'nombre_apellido')
        
        if resultados:
            messages.info(request, f"🔍 Se encontraron {resultados.count()} resultados para '{query}'")
        else:
            messages.warning(request, f"⚠️ No se encontraron resultados para '{query}'")
    
    return render(request, 'personal/search.html', {
        'resultados': resultados,
        'query': query
    })