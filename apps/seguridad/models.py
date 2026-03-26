from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from cloudinary.models import CloudinaryField
import secrets
from django.utils import timezone
from datetime import timedelta

class Perfil(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perfiles'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Modulo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    icono = models.CharField(max_length=50, default='folder')
    url = models.CharField(max_length=200, blank=True, null=True)
    orden = models.IntegerField(default=0)

    padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='submodulos'
    )

    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'modulos'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f"{self.padre.nombre} > {self.nombre}" if self.padre else self.nombre

    @property
    def es_padre(self):
        return self.submodulos.filter(activo=True).exists()


class Usuario(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True, db_index=True)
    celular = models.CharField(max_length=10, blank=True, null=True)
    password = models.CharField(max_length=255)
    avatar = CloudinaryField('avatar', blank=True, null=True)

    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.PROTECT,
        related_name='usuarios'
    )

    # 🔴 IMPORTANTE: usuario inicia INACTIVO
    activo = models.BooleanField(default=False)

    # ========================
    # 📧 VERIFICACIÓN EMAIL
    # ========================
    email_verificado = models.BooleanField(default=False)
    token_verificacion = models.CharField(max_length=100, unique=True, blank=True, null=True)
    token_verificacion_expira = models.DateTimeField(blank=True, null=True)

    # ========================
    # 🔑 RECUPERACIÓN PASSWORD
    # ========================
    token_recuperacion = models.CharField(max_length=100, blank=True, null=True)
    token_recuperacion_expira = models.DateTimeField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    ultimo_acceso = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'usuarios'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.nombre

    # ========================
    # 🔐 PASSWORD
    # ========================
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    # ========================
    # 🖼️ AVATAR
    # ========================
    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return 'https://ui-avatars.com/api/?name=' + '+'.join(self.nombre.split())

    # ========================
    # 📧 EMAIL VERIFICACIÓN
    # ========================
    def generar_token_verificacion(self):
        from django.conf import settings
        self.token_verificacion = secrets.token_urlsafe(32)
        self.token_verificacion_expira = timezone.now() + timedelta(
            hours=settings.EMAIL_VERIFICATION_EXPIRY_HOURS
        )
        # 🔥 CAMBIO CLAVE: Guardar en la base de datos y retornar el valor
        self.save(update_fields=['token_verificacion', 'token_verificacion_expira'])
        return self.token_verificacion

    def verificar_token(self, token):
        if not self.token_verificacion or not self.token_verificacion_expira:
            return False

        if self.token_verificacion != token:
            return False

        if timezone.now() > self.token_verificacion_expira:
            # limpiar token expirado
            self.token_verificacion = None
            self.token_verificacion_expira = None
            self.save(update_fields=['token_verificacion', 'token_verificacion_expira'])
            return False

        return True

    def marcar_email_verificado(self):
        self.email_verificado = True
        self.activo = True  # 🔥 activa usuario
        self.token_verificacion = None
        self.token_verificacion_expira = None

        self.save(update_fields=[
            'email_verificado',
            'activo',
            'token_verificacion',
            'token_verificacion_expira'
        ])

    # ========================
    # 🔑 RECUPERACIÓN PASSWORD
    # ========================
    def generar_token_recuperacion(self):
        self.token_recuperacion = secrets.token_urlsafe(32)
        self.token_recuperacion_expira = timezone.now() + timedelta(hours=1)
        # 🔥 CAMBIO CLAVE: Guardar en la base de datos y retornar el valor
        self.save(update_fields=['token_recuperacion', 'token_recuperacion_expira'])
        return self.token_recuperacion

    def verificar_token_recuperacion(self, token):
        if not self.token_recuperacion or not self.token_recuperacion_expira:
            return False

        if self.token_recuperacion != token:
            return False

        if timezone.now() > self.token_recuperacion_expira:
            return False

        return True

    def limpiar_token_recuperacion(self):
        self.token_recuperacion = None
        self.token_recuperacion_expira = None
        self.save(update_fields=['token_recuperacion', 'token_recuperacion_expira'])


class PermisosPerfil(models.Model):
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='permisos'
    )
    modulo = models.ForeignKey(
        Modulo,
        on_delete=models.CASCADE,
        related_name='permisos'
    )

    puede_agregar = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)
    puede_consultar = models.BooleanField(default=False)
    puede_ver_detalle = models.BooleanField(default=False)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'permisos_perfil'
        unique_together = ['perfil', 'modulo']
        ordering = ['perfil', 'modulo__orden']

    def __str__(self):
        return f"{self.perfil.nombre} - {self.modulo.nombre}"

    @property
    def tiene_algun_permiso(self):
        return any([
            self.puede_agregar,
            self.puede_editar,
            self.puede_eliminar,
            self.puede_consultar,
            self.puede_ver_detalle
        ])