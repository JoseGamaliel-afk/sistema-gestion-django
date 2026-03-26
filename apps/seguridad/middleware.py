from django.shortcuts import redirect, render
from django.urls import reverse, resolve, Resolver404
from django.contrib import messages
from django.http import JsonResponse
from .services import JWTService, PermisosService

class JWTAuthenticationMiddleware:
    """Middleware para autenticación JWT"""

    # 0. Rutas EXACTAS que siempre pasan sin importar nada
    EXACT_PUBLIC_PATHS = [
        '/',
        '/favicon.ico'
    ]

    # 1. Rutas que NO requieren estar logueado (basta con que empiecen con esto)
    PUBLIC_PATHS = [
        '/seguridad/login',
        '/seguridad/api/login',
        '/seguridad/recuperar-password',
        '/seguridad/restablecer-password',
        '/seguridad/verificar-email',
        '/seguridad/reenviar-verificacion',
        '/admin/',
        '/static/',
        '/media/',
    ]

    # 2. NOMBRES INTERNOS DE VISTAS que SÍ requieren login, pero NO permisos de módulo
    EXEMPT_URL_NAMES = [
        'dashboard',
        'logout',
        'mi_perfil',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # PASO 0: Permitir rutas exactas
        if path in self.EXACT_PUBLIC_PATHS:
            return self.get_response(request)

        # PASO 1: Permitir rutas públicas sin checar nada
        for public in self.PUBLIC_PATHS:
            if path.startswith(public):
                return self.get_response(request)
                
        # ... (de aquí para abajo todo se queda igual: PASO 2, PASO 3, etc.)

        # PASO 2: Obtener token y validar usuario
        token = request.session.get('jwt_token') or request.COOKIES.get('jwt_token')

        if token:
            usuario = JWTService.obtener_usuario_desde_token(token)
            if usuario:
                # ¡Aquí pegamos el usuario para que las vistas no fallen!
                request.usuario_actual = usuario

                # PASO 3: Validación infalible por NOMBRE DE VISTA
                try:
                    # resolve() averigua cómo se llama la vista internamente en tus urls.py
                    current_url_name = resolve(path).url_name
                    if current_url_name in self.EXEMPT_URL_NAMES:
                        return self.get_response(request)
                except Resolver404:
                    pass # Si la ruta no existe, lo dejamos seguir para que tire un 404 normal

                # PASO 4: CANDADO DE SEGURIDAD ESTRICTO PARA MÓDULOS
                partes_path = path.strip('/').split('/')
                
                # Armamos la ruta base (ej: /seguridad/usuarios/)
                if len(partes_path) >= 2:
                    ruta_base = f"/{partes_path[0]}/{partes_path[1]}/"
                else:
                    ruta_base = path

                permisos = PermisosService.obtener_permisos_modulo(usuario, ruta_base)

                if not permisos or not permisos.get('puede_consultar'):
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': False, 
                            'error': 'No tienes permisos para acceder a este módulo o fue eliminado.'
                        }, status=403)
                    
                    # 🔴 CHIVATO EN CONSOLA: Esto te avisará en la terminal negra qué ruta exacta se bloqueó
                    print(f"🛑 MIDDLEWARE: Acceso denegado a la ruta -> {path}")
                    
                    # Mostrar la vista 403
                    return render(request, 'errores.html', {'error_code': 403}, status=403)
                # -----------------------------------------------------------

                return self.get_response(request)

        # PASO 5: Si no hay token o no es válido
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'No autorizado'}, status=401)

        # Redirigir a login si es navegación normal
        return redirect(reverse('seguridad:login'))