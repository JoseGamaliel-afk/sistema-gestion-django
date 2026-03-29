from django.urls import path
from . import views

app_name = 'seguridad'

urlpatterns = [

    # =========================
    # 🔥 HOME INTELIGENTE (ENTRY POINT)
    # =========================
    path('', views.SeguridadHomeView.as_view(), name='home'),

    # =========================
    # AUTH
    # =========================
    path('login/', views.LoginView.as_view(), name='login'),
    path('api/login/', views.LoginAPIView.as_view(), name='api_login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    # =========================
    # VERIFICACIÓN DE EMAIL
    # =========================
    path('verificar-email/<str:token>/', views.VerificarEmailView.as_view(), name='verificar_email'),
    path('reenviar-verificacion/', views.ReenviarVerificacionView.as_view(), name='reenviar_verificacion'),
    path('api/reenviar-verificacion/<int:pk>/', views.ReenviarVerificacionAPIView.as_view(), name='api_reenviar_verificacion'),

    # =========================
    # RECUPERACIÓN DE PASSWORD
    # =========================
    path('recuperar-password/', views.RecuperarPasswordView.as_view(), name='recuperar_password'),
    path('restablecer-password/<str:token>/', views.RestablecerPasswordView.as_view(), name='restablecer_password'),

    # =========================
    # DASHBOARD
    # =========================
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),

    # =========================
    # PERFILES
    # =========================
    path('perfiles/', views.PerfilListView.as_view(), name='perfil_list'),
    path('perfiles/crear/', views.PerfilCreateView.as_view(), name='perfil_create'),
    path('perfiles/<int:pk>/editar/', views.PerfilUpdateView.as_view(), name='perfil_update'),
    path('perfiles/<int:pk>/eliminar/', views.PerfilDeleteView.as_view(), name='perfil_delete'),
    path('perfiles/<int:pk>/detalle/', views.PerfilDetailView.as_view(), name='perfil_detail'),

    # =========================
    # MÓDULOS
    # =========================
    path('modulos/', views.ModuloListView.as_view(), name='modulo_list'),
    path('modulos/crear/', views.ModuloCreateView.as_view(), name='modulo_create'),
    path('modulos/<int:pk>/editar/', views.ModuloUpdateView.as_view(), name='modulo_update'),
    path('modulos/<int:pk>/eliminar/', views.ModuloDeleteView.as_view(), name='modulo_delete'),
    path('modulos/<int:pk>/detalle/', views.ModuloDetailView.as_view(), name='modulo_detail'),

    # =========================
    # PERMISOS PERFIL
    # =========================
    path('permisos-perfil/', views.PermisosPerfilListView.as_view(), name='permisosperfil_list'),
    path('permisos-perfil/guardar/', views.PermisosPerfilSaveView.as_view(), name='permisosperfil_save'),

    # =========================
    # USUARIOS
    # =========================
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/crear/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('usuarios/<int:pk>/detalle/', views.UsuarioDetailView.as_view(), name='usuario_detail'),

    # =========================
    # MI PERFIL
    # =========================
    path('mi-perfil/', views.MiPerfilView.as_view(), name='mi_perfil'),
]