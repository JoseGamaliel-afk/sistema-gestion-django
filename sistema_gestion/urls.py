from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('seguridad:login')),
    path('seguridad/', include('apps.seguridad.urls', namespace='seguridad')),
    path('principal/', include('apps.principal.urls', namespace='principal')),
]

# --- MANEJO DE ERRORES PERSONALIZADOS ---

def custom_404(request, exception=None):
    return render(request, 'errores.html', {'error_code': 404}, status=404)

def custom_500(request):
    return render(request, 'errores.html', {'error_code': 500}, status=500)

def custom_403(request, exception=None):
    return render(request, 'errores.html', {'error_code': 403}, status=403)

def custom_400(request, exception=None):
    return render(request, 'errores.html', {'error_code': 400}, status=400)

# Le decimos a Django que use nuestras funciones cuando ocurran estos errores
handler404 = custom_404
handler500 = custom_500
handler403 = custom_403
handler400 = custom_400