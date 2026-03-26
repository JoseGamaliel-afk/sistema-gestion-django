from django.contrib import admin
from .models import Usuario, Perfil, Modulo, PermisosPerfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    search_fields = ['nombre']
    list_filter = ['activo']


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'padre', 'url', 'orden', 'activo']
    search_fields = ['nombre']
    list_filter = ['activo', 'padre']
    ordering = ['orden']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'correo', 'perfil', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'correo']
    list_filter = ['activo', 'perfil']


@admin.register(PermisosPerfil)
class PermisosPerfilAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'modulo', 'puede_agregar', 'puede_editar', 'puede_eliminar', 'puede_consultar']
    list_filter = ['perfil', 'modulo']