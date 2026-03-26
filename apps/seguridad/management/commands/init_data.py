from django.core.management.base import BaseCommand
from apps.seguridad.models import Perfil, Modulo, Usuario, PermisosPerfil


class Command(BaseCommand):
    help = 'Inicializa los datos básicos del sistema'

    def handle(self, *args, **options):
        self.stdout.write('Inicializando datos...')

        # ========================
        # 👤 PERFILES
        # ========================
        perfiles_data = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso total al sistema'},
            {'nombre': 'Consultor', 'descripcion': 'Solo consulta de información'},
            {'nombre': 'Operador', 'descripcion': 'Operaciones básicas'},
            {'nombre': 'Usuario', 'descripcion': 'Usuario estándar'},
            {'nombre': 'Ventas Administrativas', 'descripcion': 'Gestión de ventas'},
        ]

        for data in perfiles_data:
            perfil, created = Perfil.objects.get_or_create(
                nombre=data['nombre'],
                defaults={'descripcion': data['descripcion']}
            )
            self.stdout.write(
                f"{'✔ Creado' if created else '• Existente'}: {perfil.nombre}"
            )

        # ========================
        # 📁 MÓDULOS PADRE
        # ========================
        modulos_padres = [
            {'nombre': 'Seguridad', 'icono': 'shield-alt', 'orden': 1},
            {'nombre': 'Principal 1', 'icono': 'briefcase', 'orden': 2},
            {'nombre': 'Principal 2', 'icono': 'chart-line', 'orden': 3},
        ]

        for data in modulos_padres:
            modulo, created = Modulo.objects.get_or_create(
                nombre=data['nombre'],
                padre=None,
                defaults={'icono': data['icono'], 'orden': data['orden']}
            )
            self.stdout.write(
                f"{'✔ Creado' if created else '• Existente'} módulo padre: {modulo.nombre}"
            )

        # ========================
        # 📂 SUBMÓDULOS
        # ========================
        seguridad = Modulo.objects.get(nombre='Seguridad', padre=None)
        principal1 = Modulo.objects.get(nombre='Principal 1', padre=None)
        principal2 = Modulo.objects.get(nombre='Principal 2', padre=None)

        submodulos = [
            {'nombre': 'Perfiles', 'padre': seguridad, 'url': '/seguridad/perfiles/', 'icono': 'id-badge', 'orden': 1},
            {'nombre': 'Módulos', 'padre': seguridad, 'url': '/seguridad/modulos/', 'icono': 'cubes', 'orden': 2},
            {'nombre': 'Permisos-Perfil', 'padre': seguridad, 'url': '/seguridad/permisos-perfil/', 'icono': 'key', 'orden': 3},
            {'nombre': 'Usuarios', 'padre': seguridad, 'url': '/seguridad/usuarios/', 'icono': 'users', 'orden': 4},

            {'nombre': 'Principal 1.1', 'padre': principal1, 'url': '/principal/principal11/', 'icono': 'shopping-cart', 'orden': 1},
            {'nombre': 'Principal 1.2', 'padre': principal1, 'url': '/principal/principal12/', 'icono': 'file-alt', 'orden': 2},

            {'nombre': 'Principal 2.1', 'padre': principal2, 'url': '/principal/principal21/', 'icono': 'boxes', 'orden': 1},
            {'nombre': 'Principal 2.2', 'padre': principal2, 'url': '/principal/principal22/', 'icono': 'users-cog', 'orden': 2},
        ]

        for data in submodulos:
            modulo, created = Modulo.objects.get_or_create(
                nombre=data['nombre'],
                padre=data['padre'],
                defaults={
                    'url': data['url'],
                    'icono': data['icono'],
                    'orden': data['orden']
                }
            )
            self.stdout.write(
                f"{'✔ Creado' if created else '• Existente'} submódulo: {modulo.nombre}"
            )

        # ========================
        # 👑 USUARIO ADMIN
        # ========================
        admin_perfil = Perfil.objects.get(nombre='Administrador')

        admin, created = Usuario.objects.get_or_create(
            correo='admin@sistema.com',
            defaults={
                'nombre': 'Administrador',
                'perfil': admin_perfil,
                'activo': True,
                'email_verificado': True
            }
        )

        if created:
            admin.set_password('admin123')
            admin.token_verificacion = None
            admin.token_verificacion_expira = None
            admin.save()

            self.stdout.write(self.style.SUCCESS(f'✔ Admin creado: {admin.correo}'))
        else:
            # 🔥 asegurar consistencia
            admin.activo = True
            admin.email_verificado = True
            admin.token_verificacion = None
            admin.token_verificacion_expira = None

            admin.save(update_fields=[
                'activo',
                'email_verificado',
                'token_verificacion',
                'token_verificacion_expira'
            ])

            self.stdout.write(f'• Admin actualizado: {admin.correo}')

        # ========================
        # 🔐 PERMISOS ADMIN
        # ========================
        modulos = Modulo.objects.filter(padre__isnull=False)

        for modulo in modulos:
            PermisosPerfil.objects.get_or_create(
                perfil=admin_perfil,
                modulo=modulo,
                defaults={
                    'puede_agregar': True,
                    'puede_editar': True,
                    'puede_eliminar': True,
                    'puede_consultar': True,
                    'puede_ver_detalle': True,
                }
            )

        # ========================
        # 👁️ CONSULTOR
        # ========================
        self._crear_permisos_consultor()

        # ========================
        # ⚙️ OPERADOR
        # ========================
        self._crear_permisos_operador()

        # ========================
        # ✅ FINAL
        # ========================
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('✔ ¡Datos inicializados correctamente!'))
        self.stdout.write(self.style.SUCCESS('='*50))

        self.stdout.write('\nCredenciales:')
        self.stdout.write(self.style.WARNING('Correo: admin@sistema.com'))
        self.stdout.write(self.style.WARNING('Password: admin123'))
        self.stdout.write('')

    # ========================
    # CONSULTOR
    # ========================
    def _crear_permisos_consultor(self):
        try:
            consultor = Perfil.objects.get(nombre='Consultor')
            modulos = Modulo.objects.filter(padre__isnull=False)

            for modulo in modulos:
                PermisosPerfil.objects.get_or_create(
                    perfil=consultor,
                    modulo=modulo,
                    defaults={
                        'puede_consultar': True,
                        'puede_ver_detalle': True,
                    }
                )
        except Perfil.DoesNotExist:
            pass

    # ========================
    # OPERADOR
    # ========================
    def _crear_permisos_operador(self):
        try:
            operador = Perfil.objects.get(nombre='Operador')

            modulos = Modulo.objects.filter(
                padre__nombre__in=['Principal 1', 'Principal 2']
            )

            for modulo in modulos:
                PermisosPerfil.objects.get_or_create(
                    perfil=operador,
                    modulo=modulo,
                    defaults={
                        'puede_agregar': True,
                        'puede_editar': True,
                        'puede_consultar': True,
                        'puede_ver_detalle': True,
                    }
                )
        except Perfil.DoesNotExist:
            pass