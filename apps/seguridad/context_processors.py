from django.conf import settings
from .services import PermisosService


def menu_context(request):
    """Context processor para el menú dinámico"""
    context = {
        'menu_items': [],
        'usuario_actual': None,
        'permisos_actuales': {},
    }
    
    if hasattr(request, 'usuario_actual') and request.usuario_actual:
        context['usuario_actual'] = request.usuario_actual
        context['menu_items'] = PermisosService.obtener_menu_usuario(request.usuario_actual)
        
        # Obtener permisos para la URL actual
        current_path = request.path
        context['permisos_actuales'] = PermisosService.obtener_permisos_modulo(
            request.usuario_actual, 
            current_path
        )
    
    return context


def recaptcha_context(request):
    """Context processor para reCAPTCHA"""
    return {
        'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
    }