from django.urls import path
from . import views

app_name = 'principal'

urlpatterns = [
    path('principal11/', views.Principal11View.as_view(), name='principal11'),
    path('principal12/', views.Principal12View.as_view(), name='principal12'),
    path('principal21/', views.Principal21View.as_view(), name='principal21'),
    path('principal22/', views.Principal22View.as_view(), name='principal22'),
]
