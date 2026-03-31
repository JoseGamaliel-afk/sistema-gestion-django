import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails con SendGrid"""

    def __init__(self):
        self.sg = None
        self.from_email = None

        self.api_key = getattr(settings, 'SENDGRID_API_KEY', '').strip()
        self.from_email_addr = getattr(settings, 'SENDGRID_FROM_EMAIL', '').strip()
        self.from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Sistema de Gestión')

        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content

            self._Mail = Mail
            self._Email = Email
            self._To = To
            self._Content = Content

            if self.api_key and self.from_email_addr:
                self.sg = SendGridAPIClient(api_key=self.api_key)
                self.from_email = self._Email(self.from_email_addr, self.from_name)
                logger.info(f"EmailService listo con {self.from_email_addr}")
            else:
                logger.error("Faltan credenciales de SendGrid")

        except ImportError:
            logger.critical("Instala sendgrid: pip install sendgrid")

    # 🔥 URL BASE CENTRALIZADA
    def _get_app_url(self):
        url = getattr(settings, 'APP_URL', '').strip()

        if not url:
            url = "https://sistema-gestion-django.onrender.com"

        return url.rstrip('/')

    # 🔥 ENVÍO GENERAL
    def enviar_email(self, to_email, subject, html_content, text_content=None):
        if not self.sg:
            logger.error(f"No se puede enviar correo a {to_email}: SendGrid no configurado")
            return {'success': False, 'error': 'SendGrid no configurado'}

        try:
            message = self._Mail(
                from_email=self.from_email,
                to_emails=self._To(to_email),
                subject=subject,
                html_content=html_content
            )

            if text_content:
                message.add_content(self._Content("text/plain", text_content))

            response = self.sg.send(message)

            logger.info(f"SendGrid status: {response.status_code}")

            if response.status_code in [200, 201, 202]:
                logger.info(f"Correo enviado a {to_email}")
                return {'success': True}
            else:
                logger.error(f"Error SendGrid: {response.status_code}")
                logger.error(response.body)
                return {'success': False, 'status_code': response.status_code}

        except Exception as e:
            logger.exception(f"Error enviando correo: {e}")
            return {'success': False, 'error': str(e)}

    # 🔐 VERIFICACIÓN DE EMAIL
    def enviar_verificacion_email(self, usuario):
        token = usuario.generar_token_verificacion()

        app_url = self._get_app_url()
        verification_url = f"{app_url}/seguridad/verificar-email/{token}/"

        subject = "Verifica tu correo electrónico"

        html_content = f"""
        <div style="font-family:sans-serif;padding:20px;">
            <h2>Hola {usuario.nombre}</h2>
            <p>Haz clic para verificar tu cuenta:</p>

            <div style="margin:20px 0;">
                <a href="{verification_url}" 
                   style="background:#3b82f6;color:white;padding:12px 20px;border-radius:5px;text-decoration:none;">
                   Verificar cuenta
                </a>
            </div>

            <p>O copia este enlace:</p>
            <p>{verification_url}</p>
        </div>
        """

        return self.enviar_email(
            usuario.correo,
            subject,
            html_content,
            f"Verifica tu cuenta: {verification_url}"
        )

    # 🎉 BIENVENIDA
    def enviar_bienvenida(self, usuario):
        app_url = self._get_app_url()
        login_url = f"{app_url}/seguridad/login/"

        subject = "Bienvenido al sistema"

        html_content = f"""
        <div style="text-align:center;padding:20px;">
            <h1>🎉 Cuenta activada</h1>
            <p>Hola {usuario.nombre}</p>
            <a href="{login_url}">Ir al login</a>
        </div>
        """

        return self.enviar_email(usuario.correo, subject, html_content)

    # 🔑 RECUPERACIÓN DE CONTRASEÑA
    def enviar_recuperacion_password(self, usuario):
        token = usuario.generar_token_recuperacion()

        app_url = self._get_app_url()
        reset_url = f"{app_url}/seguridad/restablecer-password/{token}/"

        subject = "Recuperar contraseña"

        html_content = f"""
        <div style="padding:20px;">
            <h3>Recuperación de contraseña</h3>
            <p>Hola {usuario.nombre}</p>

            <div style="margin:20px 0;">
                <a href="{reset_url}" 
                   style="background:#f59e0b;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;">
                   Restablecer contraseña
                </a>
            </div>
        </div>
        """

        return self.enviar_email(usuario.correo, subject, html_content)


# 🔥 INSTANCIA GLOBAL
email_service = EmailService()