import jwt
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from .models import Usuario, PermisosPerfil, Modulo


class JWTService:
    """Servicio para manejo de JWT"""

    @staticmethod
    def generar_token(usuario):
        """Genera un token JWT para el usuario"""
        payload = {
            'usuario_id': usuario.id,
            'correo': usuario.correo,
            'perfil_id': usuario.perfil.id,
            'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')

        # Compatibilidad PyJWT (por si devuelve bytes)
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    @staticmethod
    def verificar_token(token):
        """Verifica y decodifica un token JWT"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def obtener_usuario_desde_token(token):
        """Obtiene el usuario desde el token"""
        payload = JWTService.verificar_token(token)

        if payload:
            try:
                return Usuario.objects.get(id=payload['usuario_id'], activo=True)
            except Usuario.DoesNotExist:
                return None

        return None


class RecaptchaService:
    """Servicio para validación de reCAPTCHA"""

    VERIFY_URL = 'https://www.google.com/recaptcha/api/siteverify'

    @staticmethod
    def verificar(recaptcha_response):
        """Verifica la respuesta del reCAPTCHA"""

        if not recaptcha_response:
            return False

        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response
        }

        try:
            response = requests.post(
                RecaptchaService.VERIFY_URL,
                data=data,
                timeout=5
            )
            result = response.json()

            return result.get('success', False)

        except requests.RequestException:
            return False


class AuthService:
    """Servicio de autenticación"""

    @staticmethod
    def autenticar(correo, password):
        """Autentica un usuario"""

        try:
            usuario = Usuario.objects.get(correo=correo)

            if not usuario.activo:
                return None, "Usuario inactivo"

            # 🔥 NUEVO: validar email verificado
            if not usuario.email_verificado:
                return None, "EMAIL_NO_VERIFICADO"

            if not usuario.check_password(password):
                return None, "Contraseña incorrecta"

            # Actualizar último acceso
            usuario.ultimo_acceso = timezone.now()
            usuario.save(update_fields=['ultimo_acceso'])

            return usuario, None

        except Usuario.DoesNotExist:
            return None, "Usuario no encontrado"

    @staticmethod
    def login(correo, password, recaptcha_response):
        """Proceso completo de login"""

        # Validar reCAPTCHA
        if not RecaptchaService.verificar(recaptcha_response):
            return None, None, "Verificación reCAPTCHA fallida"

        # Autenticación
        usuario, error = AuthService.autenticar(correo, password)

        if error:
            return None, None, error

        # Generar token
        token = JWTService.generar_token(usuario)

        return usuario, token, None


class PermisosService:
    """Servicio para manejo de permisos"""

    @staticmethod
    def obtener_menu_usuario(usuario):
        """Obtiene el menú según los permisos del usuario"""
        
        # --- NUEVO CANDADO ADMIN ---
        # Si es Administrador, le damos todos los módulos activos
        if usuario.perfil and usuario.perfil.nombre.lower() == 'administrador':
            modulos_padres = Modulo.objects.filter(
                padre__isnull=True, 
                activo=True
            ).order_by('orden')
            
            menu = []
            for padre in modulos_padres:
                hijos = Modulo.objects.filter(
                    padre=padre, 
                    activo=True
                ).order_by('orden')
                
                menu.append({
                    'modulo': padre,
                    'submodulos': list(hijos)
                })
            return menu
        # ---------------------------

        permisos = PermisosPerfil.objects.filter(
            perfil=usuario.perfil
        ).select_related('modulo', 'modulo__padre')

        modulos_permitidos = set()

        for permiso in permisos:
            if permiso.tiene_algun_permiso:
                modulos_permitidos.add(permiso.modulo.id)

                if permiso.modulo.padre:
                    modulos_permitidos.add(permiso.modulo.padre.id)

        # Obtener módulos padres
        modulos_padres = Modulo.objects.filter(
            padre__isnull=True,
            activo=True,
            id__in=modulos_permitidos
        ).order_by('orden')

        menu = []

        for padre in modulos_padres:
            hijos = Modulo.objects.filter(
                padre=padre,
                activo=True,
                id__in=modulos_permitidos
            ).order_by('orden')

            menu.append({
                'modulo': padre,
                'submodulos': list(hijos)
            })

        return menu

    @staticmethod
    def tiene_permiso(usuario, modulo_url, tipo_permiso):
        """Verifica si el usuario tiene un permiso específico"""

        # --- NUEVO CANDADO ADMIN ---
        if usuario.perfil and usuario.perfil.nombre.lower() == 'administrador':
            # Solo verificamos que el módulo exista y esté activo
            modulo_existe = Modulo.objects.filter(url=modulo_url, activo=True).exists()
            return modulo_existe
        # ---------------------------

        try:
            modulo = Modulo.objects.get(url=modulo_url, activo=True)

            permiso = PermisosPerfil.objects.get(
                perfil=usuario.perfil,
                modulo=modulo
            )

            permisos_map = {
                'agregar': permiso.puede_agregar,
                'editar': permiso.puede_editar,
                'eliminar': permiso.puede_eliminar,
                'consultar': permiso.puede_consultar,
                'detalle': permiso.puede_ver_detalle,
            }

            return permisos_map.get(tipo_permiso, False)

        except (Modulo.DoesNotExist, PermisosPerfil.DoesNotExist):
            return False

    @staticmethod
    def obtener_permisos_modulo(usuario, modulo_url):
        """Obtiene todos los permisos del usuario para un módulo"""

        # --- NUEVO CANDADO ADMIN ---
        if usuario.perfil and usuario.perfil.nombre.lower() == 'administrador':
            # Buscamos que exista el módulo y esté activo (y si tiene padre, que el padre también esté activo)
            modulo = Modulo.objects.filter(url=modulo_url, activo=True).first()
            
            if modulo and (not modulo.padre or modulo.padre.activo):
                return {
                    'puede_agregar': True,
                    'puede_editar': True,
                    'puede_eliminar': True,
                    'puede_consultar': True,
                    'puede_ver_detalle': True,
                }
            return None
        # ---------------------------

        try:
            modulo = Modulo.objects.get(url=modulo_url, activo=True)

            # Si el módulo padre está inactivo, bloqueamos los hijos
            if modulo.padre and not modulo.padre.activo:
                return None

            permiso = PermisosPerfil.objects.get(
                perfil=usuario.perfil,
                modulo=modulo
            )

            return {
                'puede_agregar': permiso.puede_agregar,
                'puede_editar': permiso.puede_editar,
                'puede_eliminar': permiso.puede_eliminar,
                'puede_consultar': permiso.puede_consultar,
                'puede_ver_detalle': permiso.puede_ver_detalle,
            }

        except (Modulo.DoesNotExist, PermisosPerfil.DoesNotExist):
            # Si no hay permisos o no existe el módulo, devolvemos todo en False en lugar de None
            # para que la interfaz de usuario (plantillas) no arroje errores.
            return {
                'puede_agregar': False,
                'puede_editar': False,
                'puede_eliminar': False,
                'puede_consultar': False,
                'puede_ver_detalle': False,
            }