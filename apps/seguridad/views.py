import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.conf import settings
from django.utils import timezone
from apps.seguridad.email_service import email_service

from .models import Usuario, Perfil, Modulo, PermisosPerfil
from .forms import LoginForm, UsuarioForm, PerfilForm, ModuloForm, MiPerfilForm
from .services import AuthService, PermisosService

from .email_service import email_service
class LoginView(View):
    """Vista de login"""
    template_name = 'seguridad/login.html'

    def get(self, request):
        # Si ya está autenticado, redirigir al dashboard
        token = request.session.get('jwt_token')
        if token:
            from .services import JWTService
            if JWTService.verificar_token(token):
                return redirect('seguridad:dashboard')
        
        form = LoginForm()
        return render(request, self.template_name, {'form': form})


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(View):
    """API para login"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            correo = data.get('correo', '').strip()
            password = data.get('password', '')
            recaptcha_response = data.get('recaptcha', '')
            
            # Validar campos
            if not correo or not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Correo y contraseña son obligatorios'
                }, status=400)
            
            # Intentar login
            usuario, token, error = AuthService.login(correo, password, recaptcha_response)
            
            if error:
                return JsonResponse({
                    'success': False,
                    'error': error
                }, status=401)
            
            # Guardar token en sesión
            request.session['jwt_token'] = token
            
            return JsonResponse({
                'success': True,
                'token': token,
                'usuario': {
                    'id': usuario.id,
                    'nombre': usuario.nombre,
                    'correo': usuario.correo,
                    'avatar': usuario.avatar_url
                },
                'redirect': '/seguridad/dashboard/'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Datos inválidos'
            }, status=400)


class LogoutView(View):
    """Vista de logout"""
    
    def get(self, request):
        request.session.flush()
        response = redirect('seguridad:login')
        response.delete_cookie('jwt_token')
        return response


class DashboardView(View):
    """Vista del dashboard"""
    template_name = 'seguridad/dashboard.html'

    def get(self, request):
        usuario = request.usuario_actual
        
        # Estadísticas
        total_usuarios = Usuario.objects.filter(activo=True).count()
        total_perfiles = Perfil.objects.filter(activo=True).count()
        total_modulos = Modulo.objects.filter(activo=True).count()
        total_permisos = PermisosPerfil.objects.count()
        
        # Últimos usuarios
        ultimos_usuarios = Usuario.objects.select_related('perfil').order_by('-fecha_creacion')[:5]
        
        context = {
            'usuario': usuario,
            'fecha_actual': timezone.now(),
            'total_usuarios': total_usuarios,
            'total_perfiles': total_perfiles,
            'total_modulos': total_modulos,
            'total_permisos': total_permisos,
            'ultimos_usuarios': ultimos_usuarios,
            'breadcrumbs': [
                {'nombre': 'Dashboard', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class PerfilListView(View):
    """Vista de listado de perfiles"""
    template_name = 'seguridad/perfil_list.html'

    def get(self, request):
        search = request.GET.get('search', '')
        perfiles = Perfil.objects.all()
        
        if search:
            perfiles = perfiles.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search)
            )
        
        paginator = Paginator(perfiles, settings.ITEMS_PER_PAGE)
        page = request.GET.get('page', 1)
        perfiles_page = paginator.get_page(page)
        
        permisos = PermisosService.obtener_permisos_modulo(
            request.usuario_actual, 
            '/seguridad/perfiles/'
        )
        
        context = {
            'perfiles': perfiles_page,
            'search': search,
            'permisos': permisos,
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Perfiles', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class PerfilCreateView(View):
    """Vista para crear perfil"""
    template_name = 'seguridad/perfil_form.html'

    def get(self, request):
        form = PerfilForm()
        context = {
            'form': form,
            'titulo': 'Nuevo Perfil',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Perfiles', 'url': '/seguridad/perfiles/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = PerfilForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seguridad:perfil_list')
        
        context = {
            'form': form,
            'titulo': 'Nuevo Perfil',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Perfiles', 'url': '/seguridad/perfiles/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class PerfilUpdateView(View):
    """Vista para editar perfil"""
    template_name = 'seguridad/perfil_form.html'

    def get(self, request, pk):
        perfil = get_object_or_404(Perfil, pk=pk)
        form = PerfilForm(instance=perfil)
        context = {
            'form': form,
            'perfil': perfil,
            'titulo': 'Editar Perfil',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Perfiles', 'url': '/seguridad/perfiles/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        perfil = get_object_or_404(Perfil, pk=pk)
        form = PerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('seguridad:perfil_list')
        
        context = {
            'form': form,
            'perfil': perfil,
            'titulo': 'Editar Perfil',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Perfiles', 'url': '/seguridad/perfiles/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


from django.db.models import ProtectedError

class PerfilDeleteView(View):
    """Vista para eliminar perfil"""
    
    def post(self, request, pk):
        perfil = get_object_or_404(Perfil, pk=pk)
        
        try:
            perfil.delete()
            return JsonResponse({
                'success': True,
                'message': 'Perfil eliminado correctamente'
            })

        except ProtectedError:
            usuarios = Usuario.objects.filter(perfil=perfil).count()
            
            return JsonResponse({
                'success': False,
                'error': f'No se puede eliminar el perfil porque tiene {usuarios} usuario(s) asociado(s)'
            }, status=400)

        except Exception:
            return JsonResponse({
                'success': False,
                'error': 'Ocurrió un error al intentar eliminar el perfil'
            }, status=500)


class ModuloListView(View):
    """Vista de listado de módulos jerárquico"""
    template_name = 'seguridad/modulo_list.html'

    def get(self, request):
        search = request.GET.get('search', '')
        
        # 1. Traemos SOLO los módulos que NO tienen padre (Carpetas principales)
        # y pre-cargamos sus submódulos (hijos)
        modulos = Modulo.objects.filter(padre__isnull=True).prefetch_related('submodulos').order_by('orden', 'nombre')
        
        # 2. Si hay búsqueda, buscamos en el padre o en sus hijos
        if search:
            modulos = modulos.filter(
                Q(nombre__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(submodulos__nombre__icontains=search) |
                Q(submodulos__descripcion__icontains=search)
            ).distinct()
        
        # La paginación ahora cuenta por "Carpetas principales", no por items individuales
        paginator = Paginator(modulos, settings.ITEMS_PER_PAGE)
        page = request.GET.get('page', 1)
        modulos_page = paginator.get_page(page)
        
        permisos = PermisosService.obtener_permisos_modulo(
            request.usuario_actual, 
            '/seguridad/modulos/'
        )
        
        context = {
            'modulos': modulos_page,
            'search': search,
            'permisos': permisos,
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Módulos', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

class ModuloCreateView(View):
    """Vista para crear módulo"""
    template_name = 'seguridad/modulo_form.html'

    def get(self, request):
        form = ModuloForm()
        context = {
            'form': form,
            'titulo': 'Nuevo Módulo',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Módulos', 'url': '/seguridad/modulos/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = ModuloForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('seguridad:modulo_list')
        
        context = {
            'form': form,
            'titulo': 'Nuevo Módulo',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Módulos', 'url': '/seguridad/modulos/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class ModuloUpdateView(View):
    """Vista para editar módulo"""
    template_name = 'seguridad/modulo_form.html'

    def get(self, request, pk):
        modulo = get_object_or_404(Modulo, pk=pk)
        form = ModuloForm(instance=modulo)
        context = {
            'form': form,
            'modulo': modulo,
            'titulo': 'Editar Módulo',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Módulos', 'url': '/seguridad/modulos/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        modulo = get_object_or_404(Modulo, pk=pk)
        form = ModuloForm(request.POST, instance=modulo)
        if form.is_valid():
            form.save()
            return redirect('seguridad:modulo_list')
        
        context = {
            'form': form,
            'modulo': modulo,
            'titulo': 'Editar Módulo',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Módulos', 'url': '/seguridad/modulos/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class ModuloDeleteView(View):
    """Vista para eliminar módulo"""
    
    def post(self, request, pk):
        modulo = get_object_or_404(Modulo, pk=pk)
        try:
            modulo.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class PermisosPerfilListView(View):
    """Vista de gestión de permisos por perfil"""
    template_name = 'seguridad/permisosperfil_list.html'

    def get(self, request):
        # 1. ESTA ES LA LÍNEA QUE FALTA: Definir la variable perfiles
        perfiles = Perfil.objects.filter(activo=True)
        
        perfil_id = request.GET.get('perfil')
        perfil_seleccionado = None
        matriz_permisos = []

        # Obtener los permisos del usuario logueado para controlar la interfaz
        permisos_usuario = PermisosService.obtener_permisos_modulo(
            request.usuario_actual, 
            request.path
        )

        if perfil_id:
            perfil_seleccionado = get_object_or_404(Perfil, pk=perfil_id)

            # Lógica para armar la matriz (padres y submodulos)
            modulos_padres = Modulo.objects.filter(
                padre__isnull=True,
                activo=True
            ).order_by('orden', 'nombre')

            for padre in modulos_padres:
                submodulos = Modulo.objects.filter(
                    padre=padre,
                    activo=True
                ).order_by('orden', 'nombre')

                submodulos_permisos = []
                for submodulo in submodulos:
                    permiso, _ = PermisosPerfil.objects.get_or_create(
                        perfil=perfil_seleccionado,
                        modulo=submodulo
                    )
                    submodulos_permisos.append({
                        'modulo': submodulo,
                        'permiso': permiso
                    })

                matriz_permisos.append({
                    'padre': padre,
                    'submodulos': submodulos_permisos
                })

        # Ahora perfiles ya existe y no dará NameError
        context = {
            'perfiles': perfiles,
            'perfil_seleccionado': perfil_seleccionado,
            'matriz_permisos': matriz_permisos,
            'permisos_usuario': permisos_usuario,
        }

        return render(request, self.template_name, context)
@method_decorator(csrf_exempt, name='dispatch')
class PermisosPerfilSaveView(View):
    """API para guardar permisos"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            perfil_id = data.get('perfil_id')
            permisos = data.get('permisos', [])
            
            perfil = get_object_or_404(Perfil, pk=perfil_id)
            
            # --- CANDADO DE SEGURIDAD PARA EL ADMIN ---
            if perfil.nombre.lower() == 'administrador':
                return JsonResponse({
                    'success': False, 
                    'error': 'Acción denegada. El perfil Administrador tiene acceso total por defecto y no puede ser modificado.'
                }, status=403)
            # ------------------------------------------
            
            for permiso_data in permisos:
                modulo = get_object_or_404(Modulo, pk=permiso_data['modulo_id'])
                
                # --- REGLA ESTRICTA DE PERMISOS ---
                # Si 'consultar' es False, forzamos a que todo lo demás sea False.
                # Si 'consultar' es True, tomamos los valores que vengan del frontend.
                puede_consultar = permiso_data.get('consultar', False)
                
                puede_agregar = permiso_data.get('agregar', False) if puede_consultar else False
                puede_editar = permiso_data.get('editar', False) if puede_consultar else False
                puede_eliminar = permiso_data.get('eliminar', False) if puede_consultar else False
                puede_ver_detalle = permiso_data.get('detalle', False) if puede_consultar else False
                # ----------------------------------
                
                permiso, _ = PermisosPerfil.objects.update_or_create(
                    perfil=perfil,
                    modulo=modulo,
                    defaults={
                        'puede_agregar': puede_agregar,
                        'puede_editar': puede_editar,
                        'puede_eliminar': puede_eliminar,
                        'puede_consultar': puede_consultar,
                        'puede_ver_detalle': puede_ver_detalle,
                    }
                )
            
            return JsonResponse({'success': True, 'message': 'Permisos guardados correctamente'})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
class UsuarioListView(View):
    """Vista de listado de usuarios"""
    template_name = 'seguridad/usuario_list.html'

    def get(self, request):
        search = request.GET.get('search', '')
        usuarios = Usuario.objects.select_related('perfil').all()
        
        if search:
            usuarios = usuarios.filter(
                Q(nombre__icontains=search) |
                Q(correo__icontains=search) |
                Q(perfil__nombre__icontains=search)
            )
        
        paginator = Paginator(usuarios, settings.ITEMS_PER_PAGE)
        page = request.GET.get('page', 1)
        usuarios_page = paginator.get_page(page)
        
        permisos = PermisosService.obtener_permisos_modulo(
            request.usuario_actual, 
            '/seguridad/usuarios/'
        )
        
        context = {
            'usuarios': usuarios_page,
            'search': search,
            'permisos': permisos,
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Usuarios', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class UsuarioCreateView(View):
    """Vista para crear usuario"""
    template_name = 'seguridad/usuario_form.html'

    def get(self, request):
        form = UsuarioForm()
        context = {
            'form': form,
            'titulo': 'Nuevo Usuario',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Usuarios', 'url': '/seguridad/usuarios/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = UsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            # 1. Guardamos al usuario en la base de datos
            usuario = form.save()
            
            # 2. Leemos si el administrador marcó la casilla de "Enviar correo"
            enviar_correo = form.cleaned_data.get('enviar_verificacion', False)
            
            if enviar_correo:
                # Si marcó la casilla, enviamos el correo de verificación
                email_service.enviar_verificacion_email(usuario)
            else:
                # Si NO marcó la casilla, lo auto-verificamos para que no requiera el correo
                usuario.email_verificado = True
                usuario.save()

            return redirect('seguridad:usuario_list')
        
        context = {
            'form': form,
            'titulo': 'Nuevo Usuario',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Usuarios', 'url': '/seguridad/usuarios/'},
                {'nombre': 'Nuevo', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

class UsuarioUpdateView(View):
    """Vista para editar usuario"""
    template_name = 'seguridad/usuario_form.html'

    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        form = UsuarioForm(instance=usuario)
        context = {
            'form': form,
            'usuario_edit': usuario,
            'titulo': 'Editar Usuario',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Usuarios', 'url': '/seguridad/usuarios/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        form = UsuarioForm(request.POST, request.FILES, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('seguridad:usuario_list')
        
        context = {
            'form': form,
            'usuario_edit': usuario,
            'titulo': 'Editar Usuario',
            'breadcrumbs': [
                {'nombre': 'Seguridad', 'url': None},
                {'nombre': 'Usuarios', 'url': '/seguridad/usuarios/'},
                {'nombre': 'Editar', 'url': None}
            ]
        }
        return render(request, self.template_name, context)


class UsuarioDeleteView(View):
    """Vista para eliminar usuario"""
    
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        try:
            usuario.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class UsuarioDetailView(View):
    """Vista de detalle de usuario"""
    
    def get(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        return JsonResponse({
            'id': usuario.id,
            'nombre': usuario.nombre,
            'correo': usuario.correo,
            'celular': usuario.celular,
            'perfil': usuario.perfil.nombre,
            'activo': usuario.activo,
            'avatar': usuario.avatar_url,
            'fecha_creacion': usuario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
            'ultimo_acceso': usuario.ultimo_acceso.strftime('%d/%m/%Y %H:%M') if usuario.ultimo_acceso else 'Nunca'
        })


class MiPerfilView(View):
    """Vista del perfil del usuario actual"""
    template_name = 'seguridad/mi_perfil.html'

    def get(self, request):
        form = MiPerfilForm(instance=request.usuario_actual)
        context = {
            'form': form,
            'usuario': request.usuario_actual,
            'breadcrumbs': [
                {'nombre': 'Mi Perfil', 'url': None}
            ]
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = MiPerfilForm(request.POST, request.FILES, instance=request.usuario_actual)
        if form.is_valid():
            form.save()
            return redirect('seguridad:mi_perfil')
        
        context = {
            'form': form,
            'usuario': request.usuario_actual,
            'breadcrumbs': [
                {'nombre': 'Mi Perfil', 'url': None}
            ]
        }
        return render(request, self.template_name, context)
    

    



class VerificarEmailView(View):
    template_name = 'seguridad/verificar_email.html'

    def get(self, request, token):
        if not token:
            return render(request, self.template_name, {
                'success': False,
                'message': 'Token inválido'
            })

        try:
            usuario = Usuario.objects.get(token_verificacion=token)

            if usuario.verificar_token(token):
                usuario.marcar_email_verificado()

                # Enviar bienvenida (no bloquea flujo si falla)
                try:
                    email_service.enviar_bienvenida(usuario)
                except Exception:
                    pass

                context = {
                    'success': True,
                    'message': '¡Tu correo ha sido verificado exitosamente!',
                    'usuario': usuario
                }
            else:
                context = {
                    'success': False,
                    'message': 'El enlace ha expirado. Solicita uno nuevo.'
                }

        except Usuario.DoesNotExist:
            context = {
                'success': False,
                'message': 'El enlace no es válido.'
            }

        return render(request, self.template_name, context)


class ReenviarVerificacionView(View):
    template_name = 'seguridad/reenviar_verificacion.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        correo = request.POST.get('correo', '').strip()

        if not correo:
            return render(request, self.template_name, {
                'error': 'Ingresa tu correo electrónico'
            })

        try:
            usuario = Usuario.objects.get(correo=correo)

            if usuario.email_verificado:
                return render(request, self.template_name, {
                    'error': 'Este correo ya está verificado'
                })

            result = email_service.enviar_verificacion_email(usuario)

            if result['success']:
                return render(request, self.template_name, {
                    'success': True,
                    'message': f'Se envió un nuevo enlace a {correo}'
                })

            return render(request, self.template_name, {
                'error': 'Error al enviar el correo'
            })

        except Usuario.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'No existe una cuenta con ese correo'
            })


class RecuperarPasswordView(View):
    template_name = 'seguridad/recuperar_password.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        correo = request.POST.get('correo', '').strip()
        try:
            usuario = Usuario.objects.get(correo=correo, activo=True)
            
            # CAMBIO: Usar tu función que ya arma la URL dinámica y el HTML bonito
            email_service.enviar_recuperacion_password(usuario)
            
        except Usuario.DoesNotExist:
            pass # Por seguridad no avisamos si el correo existe o no
            
        return render(request, self.template_name, {
            'success': True, 
            'message': 'Si el correo está registrado, recibirás instrucciones pronto.'
        })

@method_decorator(csrf_exempt, name='dispatch')
class ReenviarVerificacionAPIView(View):
    def post(self, request, pk):
        usuario = get_object_or_404(Usuario, pk=pk)
        if usuario.email_verificado:
            return JsonResponse({'success': False, 'error': 'Ya verificado'}, status=400)
        
        result = email_service.enviar_verificacion_email(usuario)
        if result.get('success'):
            return JsonResponse({'success': True, 'message': 'Correo enviado'})
        return JsonResponse({'success': False, 'error': 'Error de proveedor'}, status=500)


class RestablecerPasswordView(View):
    template_name = 'seguridad/restablecer_password.html'

    def get(self, request, token):
        try:
            usuario = Usuario.objects.get(token_recuperacion=token)

            if not usuario.verificar_token_recuperacion(token):
                return render(request, self.template_name, {
                    'error': 'El enlace ha expirado',
                    'token_invalido': True
                })

            return render(request, self.template_name, {'token': token})

        except Usuario.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Enlace inválido',
                'token_invalido': True
            })

    def post(self, request, token):
        password = request.POST.get('password', '')
        confirmar = request.POST.get('confirmar_password', '')

        if not password or not confirmar:
            return render(request, self.template_name, {
                'token': token,
                'error': 'Completa todos los campos'
            })

        if password != confirmar:
            return render(request, self.template_name, {
                'token': token,
                'error': 'Las contraseñas no coinciden'
            })

        if len(password) < 8:
            return render(request, self.template_name, {
                'token': token,
                'error': 'Mínimo 8 caracteres'
            })

        try:
            usuario = Usuario.objects.get(token_recuperacion=token)

            if not usuario.verificar_token_recuperacion(token):
                return render(request, self.template_name, {
                    'error': 'El enlace expiró',
                    'token_invalido': True
                })

            usuario.set_password(password)
            usuario.limpiar_token_recuperacion()
            usuario.save()  # 🔥 IMPORTANTE

            return render(request, self.template_name, {
                'success': True,
                'message': 'Contraseña actualizada correctamente'
            })

        except Usuario.DoesNotExist:
            return render(request, self.template_name, {
                'error': 'Enlace inválido',
                'token_invalido': True
            })
# Al final de views.py, agregar esta vista:

@method_decorator(csrf_exempt, name='dispatch')
class ReenviarVerificacionAPIView(View):
    """API para reenviar verificación desde el panel de admin"""
    
    def post(self, request, pk):
        try:
            usuario = get_object_or_404(Usuario, pk=pk)
            
            if usuario.email_verificado:
                return JsonResponse({
                    'success': False,
                    'error': 'El usuario ya tiene su email verificado'
                }, status=400)
            
            # Importar aquí para evitar imports circulares
            from .email_service import email_service
            
            result = email_service.enviar_verificacion_email(usuario)
            
            if result.get('success'):
                return JsonResponse({
                    'success': True,
                    'message': 'Correo de verificación enviado'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result.get('error', 'Error al enviar el correo')
                }, status=500)
                
        except Usuario.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Usuario no encontrado'
            }, status=404)
        except Exception as e:
            import traceback
            traceback.print_exc()  # Esto mostrará el error completo en consola
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
class PerfilDetailView(View):
    def get(self, request, pk):
        perfil = get_object_or_404(Perfil, pk=pk)

        return JsonResponse({
            'id': perfil.id,
            'nombre': perfil.nombre,
            'descripcion': perfil.descripcion,
            'activo': perfil.activo,
            'fecha_creacion': perfil.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(perfil, 'fecha_creacion') else ''
        })
    
class ModuloDetailView(View):
    """Vista de detalle de módulo en JSON"""
    def get(self, request, pk):
        modulo = get_object_or_404(Modulo, pk=pk)
        return JsonResponse({
            'id': modulo.id,
            'nombre': modulo.nombre,
            'descripcion': modulo.descripcion,
            'url': getattr(modulo, 'url', ''), # Usamos getattr por si tu modelo no tiene el campo exacto 'url'
            'icono': modulo.icono,
            'orden': modulo.orden,
            'padre': modulo.padre.nombre if modulo.padre else None,
            'activo': modulo.activo,
        })
    
class SeguridadHomeView(View):
    def get(self, request):
        if hasattr(request, 'usuario_actual'):
            usuario = request.usuario_actual

            modulos = PermisosService.obtener_modulos_usuario(usuario)

            for modulo in modulos:
                if modulo['puede_consultar']:
                    return redirect(modulo['ruta'])

            return redirect('seguridad:dashboard')

        return redirect('seguridad:login')