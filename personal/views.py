import pandas as pd
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView, LogoutView

from .forms import ExcelUploadForm, RegistroForm
from .models import ResponsableAcademico, TutorRegional, TutorNacional

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

def detectar_tipo_archivo(df):
    """Detecta automáticamente el tipo de archivo según sus columnas"""
    columnas = [str(c).lower().strip() for c in df.iloc[0].tolist()]
    columnas_str = ' '.join(columnas)
    
    if 'entidad' in columnas_str and 'responsabilidad' in columnas_str:
        return 'responsables'
    elif 'condicion laboral' in columnas_str or 'condición laboral' in columnas_str:
        return 'tutores_regionales'
    elif 'programa de formación' in columnas_str or 'programa de formacion' in columnas_str:
        return 'tutores_nacionales'
    return None


@login_required
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = request.FILES['archivo_excel']
            tipo_personal = form.cleaned_data.get('tipo_personal', 'auto')
            
            try:
                df = pd.read_excel(archivo, engine='openpyxl', header=None)
                
                # Si es detección automática o no se seleccionó tipo
                if tipo_personal == 'auto' or tipo_personal == '':
                    tipo_detectado = detectar_tipo_archivo(df)
                    if tipo_detectado:
                        tipo_personal = tipo_detectado
                        messages.info(request, f"🔍 Tipo detectado automáticamente: '{tipo_detectado}'")
                    else:
                        messages.error(request, "No se pudo detectar el tipo de archivo. Por favor, selecciona manualmente el tipo.")
                        return render(request, 'personal/upload.html', {'form': form})
                else:
                    # Verificar si el tipo seleccionado coincide con la detección
                    tipo_detectado = detectar_tipo_archivo(df)
                    if tipo_detectado and tipo_detectado != tipo_personal:
                        messages.warning(request, f"⚠️ El archivo parece ser de tipo '{tipo_detectado}', pero se procesará como '{tipo_personal}'.")
                
                if tipo_personal == 'responsables':
                    resultado = procesar_responsables(df)
                elif tipo_personal == 'tutores_regionales':
                    resultado = procesar_tutores_regionales(df)
                elif tipo_personal == 'tutores_nacionales':
                    resultado = procesar_tutores_nacionales(df)
                else:
                    messages.error(request, "Tipo de personal no reconocido.")
                    return render(request, 'personal/upload.html', {'form': form})
                
                messages.success(request, resultado)
                return redirect('search')
            except Exception as e:
                messages.error(request, f"Error al procesar el archivo: {e}")
    else:
        form = ExcelUploadForm(initial={'tipo_personal': 'auto'})
    
    return render(request, 'personal/upload.html', {'form': form})


def procesar_responsables(df):
    """Procesa archivo de Responsables Académicos"""
    # Datos comienzan en fila 7 (índice 6), columnas N°(0), ENTIDAD(1), CEDULA(2), NOMBRE(3), RESP(4), TEL(5), CORREO(6)
    data_rows = df.iloc[6:, 1:7]
    data_rows.columns = ['entidad', 'cedula', 'nombre', 'responsabilidad', 'telefono', 'correo']
    
    registros_creados = 0
    registros_actualizados = 0
    
    for _, row in data_rows.iterrows():
        if pd.isna(row['entidad']) and pd.isna(row['nombre']):
            continue
        
        entidad = str(row['entidad']).strip() if not pd.isna(row['entidad']) else ''
        nombre = str(row['nombre']).strip() if not pd.isna(row['nombre']) else ''
        responsabilidad = str(row['responsabilidad']).strip() if not pd.isna(row['responsabilidad']) else 'GESTION ACADEMICA'
        correo = str(row['correo']).strip() if not pd.isna(row['correo']) else ''
        
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
        
        if entidad and nombre:
            obj, created = ResponsableAcademico.objects.update_or_create(
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
    
    return f"Responsables Académicos: {registros_creados} registros nuevos, {registros_actualizados} actualizados."


def procesar_tutores_regionales(df):
    """Procesa archivo de Tutores Regionales"""
    # Datos comienzan en fila 9 (índice 8), columnas Nº(0), CEDULA(1), NOMBRE(2), ENTIDAD(3), CONDICION(4), AREA(5)
    # Buscar la fila del encabezado
    header_row = None
    for i in range(min(15, len(df))):
        row_values = [str(v).lower().strip() for v in df.iloc[i].tolist() if not pd.isna(v)]
        if 'cedula' in row_values and ('nombre' in row_values or 'nombre y apellido' in row_values):
            header_row = i
            break
    
    if header_row is None:
        header_row = 8  # Por defecto fila 9
    
    data_rows = df.iloc[header_row + 1:, 0:6]
    data_rows.columns = ['numero', 'cedula', 'nombre', 'entidad', 'condicion_laboral', 'area_formacion']
    
    registros_creados = 0
    registros_actualizados = 0
    
    for _, row in data_rows.iterrows():
        if pd.isna(row['nombre']):
            continue
        
        nombre = str(row['nombre']).strip() if not pd.isna(row['nombre']) else ''
        entidad = str(row['entidad']).strip() if not pd.isna(row['entidad']) else ''
        condicion = str(row['condicion_laboral']).strip() if not pd.isna(row['condicion_laboral']) else ''
        area = str(row['area_formacion']).strip() if not pd.isna(row['area_formacion']) else ''
        
        if not pd.isna(row['cedula']):
            try:
                cedula = str(int(row['cedula']))
            except (ValueError, TypeError):
                cedula = str(row['cedula']).strip()
        else:
            cedula = ''
        
        if nombre:
            obj, created = TutorRegional.objects.update_or_create(
                nombre_apellido=nombre,
                cedula=cedula,
                defaults={
                    'entidad': entidad,
                    'condicion_laboral': condicion,
                    'area_formacion': area,
                }
            )
            if created:
                registros_creados += 1
            else:
                registros_actualizados += 1
    
    return f"Tutores Regionales: {registros_creados} registros nuevos, {registros_actualizados} actualizados."


def procesar_tutores_nacionales(df):
    """Procesa archivo de Tutores Nacionales"""
    # Datos en columnas N°(0), NOMBRE(1), PROGRAMA(2), CEDULA(3), TELEFONO(4), CORREO(5)
    # Buscar la fila del encabezado
    header_row = None
    for i in range(min(15, len(df))):
        row_values = [str(v).lower().strip() for v in df.iloc[i].tolist() if not pd.isna(v)]
        if 'programa' in row_values and ('nombre' in row_values or 'nombre y apellido' in row_values):
            header_row = i
            break
    
    if header_row is None:
        header_row = 8  # Por defecto fila 9
    
    data_rows = df.iloc[header_row + 1:, 0:6]
    data_rows.columns = ['numero', 'nombre', 'programa_formacion', 'cedula', 'telefono', 'correo']
    
    registros_creados = 0
    registros_actualizados = 0
    
    for _, row in data_rows.iterrows():
        if pd.isna(row['nombre']):
            continue
        
        nombre = str(row['nombre']).strip() if not pd.isna(row['nombre']) else ''
        programa = str(row['programa_formacion']).strip() if not pd.isna(row['programa_formacion']) else ''
        correo = str(row['correo']).strip() if not pd.isna(row['correo']) else ''
        telefono = str(row['telefono']).strip() if not pd.isna(row['telefono']) else ''
        
        if not pd.isna(row['cedula']):
            try:
                cedula = str(int(row['cedula']))
            except (ValueError, TypeError):
                cedula = str(row['cedula']).strip()
        else:
            cedula = ''
        
        if nombre:
            obj, created = TutorNacional.objects.update_or_create(
                nombre_apellido=nombre,
                cedula=cedula if cedula else None,
                defaults={
                    'programa_formacion': programa,
                    'telefono': telefono,
                    'correo': correo,
                }
            )
            if created:
                registros_creados += 1
            else:
                registros_actualizados += 1
    
    return f"Tutores Nacionales: {registros_creados} registros nuevos, {registros_actualizados} actualizados."


@login_required
def search_personal(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', 'todos')
    
    responsables = []
    tutores_regionales = []
    tutores_nacionales = []
    total_resultados = 0
    
    if query:
        # Búsqueda en TODOS los campos de Responsables Académicos
        if tipo == 'todos' or tipo == 'responsables':
            responsables = ResponsableAcademico.objects.filter(
                Q(nombre_apellido__icontains=query) |
                Q(cedula__icontains=query) |
                Q(entidad__icontains=query) |
                Q(correo__icontains=query) |
                Q(telefono__icontains=query) |
                Q(responsabilidad__icontains=query)
            ).order_by('entidad', 'nombre_apellido')
            total_resultados += responsables.count()
        
        # Búsqueda en TODOS los campos de Tutores Regionales
        if tipo == 'todos' or tipo == 'tutores_regionales':
            tutores_regionales = TutorRegional.objects.filter(
                Q(nombre_apellido__icontains=query) |
                Q(cedula__icontains=query) |
                Q(entidad__icontains=query) |
                Q(area_formacion__icontains=query) |
                Q(condicion_laboral__icontains=query)
            ).order_by('entidad', 'nombre_apellido')
            total_resultados += tutores_regionales.count()
        
        # Búsqueda en TODOS los campos de Tutores Nacionales
        if tipo == 'todos' or tipo == 'tutores_nacionales':
            tutores_nacionales = TutorNacional.objects.filter(
                Q(nombre_apellido__icontains=query) |
                Q(cedula__icontains=query) |
                Q(programa_formacion__icontains=query) |
                Q(correo__icontains=query) |
                Q(telefono__icontains=query)
            ).order_by('nombre_apellido')
            total_resultados += tutores_nacionales.count()
    
    return render(request, 'personal/search.html', {
        'responsables': responsables,
        'tutores_regionales': tutores_regionales,
        'tutores_nacionales': tutores_nacionales,
        'total_resultados': total_resultados,
        'query': query,
        'tipo': tipo,
    })