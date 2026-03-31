import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails con SendGrid"""

    def __init__(self):
        self.sg = None
        self.from_email = None

        self.api_key = getattr(settings, 'SENDGRID_API_KEY', '')
        self.from_email_addr = getattr(settings, 'SENDGRID_FROM_EMAIL', '')
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
                print(f"✅ EmailService listo con {self.from_email_addr}")
            else:
                print("❌ Faltan credenciales de SendGrid")

        except ImportError:
            print("❌ Instala sendgrid: pip install sendgrid")

    def _get_app_url(self):
        """URL FIJA de producción"""
        return "https://sistema-gestion-django.onrender.com"

    def enviar_email(self, to_email, subject, html_content, text_content=None):
        if not self.api_key or not self.from_email_addr:
            print(f"❌ No hay credenciales para enviar a {to_email}")
            return {'success': False, 'error': 'Credenciales no configuradas'}

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

            if response.status_code in [200, 201, 202]:
                print(f"✅ Correo enviado a {to_email}")
                return {'success': True}
            else:
                print(f"❌ Error SendGrid {response.status_code}")
                return {'success': False, 'status_code': response.status_code}

        except Exception as e:
            logger.error(f"Error enviando correo: {e}")
            return {'success': False, 'error': str(e)}

    def enviar_verificacion_email(self, usuario):
        token = usuario.generar_token_verificacion()

        app_url = self._get_app_url()
        verification_url = f"{app_url}/seguridad/verificar-email/{token}/"

        expiry = getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_HOURS', 24)

        subject = "Verifica tu correo electrónico"

        html_content = f"""
        <div style="font-family:sans-serif;padding:20px;">
            <h2>Hola {usuario.nombre}</h2>
            <p>Haz clic para verificar tu cuenta:</p>
            <a href="{verification_url}" 
               style="background:#3b82f6;color:white;padding:10px 20px;border-radius:5px;text-decoration:none;">
               Verificar
            </a>
            <p>O copia este enlace:</p>
            <p>{verification_url}</p>
            <small>Expira en {expiry} horas</small>
        </div>
        """

        return self.enviar_email(
            usuario.correo,
            subject,
            html_content,
            f"Verifica tu cuenta: {verification_url}"
        )

    def enviar_bienvenida(self, usuario):
        app_url = self._get_app_url()
        login_url = f"{app_url}/seguridad/login/"

        subject = "Bienvenido al sistema"

        html_content = f"""
        <div>
            <h1>🎉 Cuenta activada</h1>
            <p>Hola {usuario.nombre}</p>
            <a href="{login_url}">Ir al login</a>
        </div>
        """

        return self.enviar_email(usuario.correo, subject, html_content)

    def enviar_recuperacion_password(self, usuario):
        token = usuario.generar_token_recuperacion()

        app_url = self._get_app_url()
        reset_url = f"{app_url}/seguridad/restablecer-password/{token}/"

        subject = "Recuperar contraseña"

        html_content = f"""
        <div>
            <h3>Recuperación de contraseña</h3>
            <p>Hola {usuario.nombre}</p>
            <a href="{reset_url}">Restablecer contraseña</a>
        </div>
        """

        return self.enviar_email(usuario.correo, subject, html_content)


# Instancia global
email_service = EmailService()