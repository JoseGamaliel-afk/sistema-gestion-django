from django.shortcuts import redirect
from django.http import JsonResponse
from .services import PermisosService

def permiso_requerido(ruta, accion):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            usuario = getattr(request, 'usuario_actual', None)

            if not usuario:
                return redirect('seguridad:login')

            permisos = PermisosService.obtener_permisos_modulo(usuario, ruta)

            if not permisos.get(accion, False):
                # Para peticiones AJAX
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'error': 'No tienes permisos para esta acción'
                    }, status=403)

                return redirect('seguridad:dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator