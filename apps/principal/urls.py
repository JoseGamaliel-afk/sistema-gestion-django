from django.urls import path
from . import views

app_name = 'principal'

urlpatterns = [
    # ✅ RUTA BASE (LA QUE TE FALTA)
    path('', views.Principal11View.as_view(), name='principal'),

    # 🔹 Tus vistas actuales
    path('principal11/', views.Principal11View.as_view(), name='principal11'),
    path('principal12/', views.Principal12View.as_view(), name='principal12'),
    path('principal21/', views.Principal21View.as_view(), name='principal21'),
    path('principal22/', views.Principal22View.as_view(), name='principal22'),
]