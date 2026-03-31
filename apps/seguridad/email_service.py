import logging
import os
from django.conf import settings

# Configuración de logger
logger = logging.getLogger(__name__)

class EmailService:
    """Servicio para envío de emails con SendGrid (Modo Moderno Simplificado)"""
    
    def __init__(self):
        self.sg = None
        
        # Leemos las variables directamente de settings
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', '').strip()
        self.from_email_addr = getattr(settings, 'SENDGRID_FROM_EMAIL', '').strip()
        self.from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Sistema de Gestión').strip()
        
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            # Solo necesitamos Mail, como en la documentación
            self._Mail = Mail
            
            if self.api_key and self.from_email_addr:
                self.sg = SendGridAPIClient(api_key=self.api_key)
                print(f"✅ EmailService Listo: Operando con {self.from_email_addr}")
            else:
                print("❌ EmailService ERROR: Faltan credenciales en .env")
                
        except ImportError:
            print("❌ ERROR CRÍTICO: Librería 'sendgrid' no instalada. Ejecuta: pip install sendgrid")

    def enviar_email(self, to_email, subject, html_content, text_content=None):
        """Envío real usando la estructura oficial de SendGrid"""
        
        if not self.api_key or not self.from_email_addr:
            print(f"❌ ENVÍO CANCELADO A {to_email}: No hay credenciales configuradas.")
            return {'success': False, 'error': 'Credenciales no configuradas'}
        
        try:
            # Estructura exacta de la documentación de SendGrid
            message = self._Mail(
                from_email=(self.from_email_addr, self.from_name), # Tupla para incluir nombre y correo
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            
            # Si hay texto plano, se agrega como propiedad simplificada
            if text_content:
                message.plain_text_content = text_content
            
            # Petición a SendGrid
            response = self.sg.send(message)
            
            # SendGrid retorna 200, 201 o 202 para envíos exitosos
            if response.status_code in [200, 201, 202]:
                print(f"✅ CORREO REAL ENVIADO EXITOSAMENTE A {to_email}")
                return {'success': True, 'status_code': response.status_code}
            else:
                print(f"❌ ERROR DE SENDGRID: Status {response.status_code}")
                print(f"Detalle: {response.body}")
                return {'success': False, 'status_code': response.status_code}
            
        except Exception as e:
            logger.error(f"Error en SendGrid: {str(e)}")
            print(f"❌ EXCEPCIÓN CRÍTICA AL ENVIAR CORREO: {e}")
            return {'success': False, 'error': str(e)}

    def enviar_verificacion_email(self, usuario):
        token = usuario.generar_token_verificacion()
        app_url = getattr(settings, 'APP_URL', 'http://localhost:8000').rstrip('/')
        verification_url = f"{app_url}/seguridad/verificar-email/{token}/"
        expiry = getattr(settings, 'EMAIL_VERIFICATION_EXPIRY_HOURS', 24)
        
        subject = "Verifica tu correo electrónico - Sistema de Gestión"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: #fff; padding: 30px; border-radius: 8px;">
                <h2 style="color: #3b82f6;">¡Hola, {usuario.nombre}!</h2>
                <p>Gracias por registrarte. Para activar tu cuenta, haz clic en el siguiente botón:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: #3b82f6; color: white; padding: 15px 25px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verificar mi correo</a>
                </div>
                <p style="font-size: 12px; color: #666;">Si el botón no funciona, copia este link: <br>{verification_url}</p>
                <p style="font-size: 11px; color: #999;">Este enlace expira en {expiry} horas.</p>
            </div>
        </body>
        </html>
        """
        return self.enviar_email(usuario.correo, subject, html_content, f"Verifica tu cuenta aquí: {verification_url}")

    def enviar_bienvenida(self, usuario):
        app_url = getattr(settings, 'APP_URL', 'http://localhost:8000').rstrip('/')
        login_url = f"{app_url}/seguridad/login/"
        
        subject = "¡Bienvenido al Sistema de Gestión!"
        html_content = f"""
        <div style="text-align: center; padding: 20px;">
            <h1>🎉 ¡Cuenta Activada!</h1>
            <p>Hola {usuario.nombre}, tu cuenta ha sido verificada correctamente.</p>
            <a href="{login_url}" style="color: #10b981; font-weight: bold;">Ir al Login</a>
        </div>
        """
        return self.enviar_email(usuario.correo, subject, html_content)

    def enviar_recuperacion_password(self, usuario):
        token = usuario.generar_token_recuperacion()
        app_url = getattr(settings, 'APP_URL', 'http://localhost:8000').rstrip('/')
        reset_url = f"{app_url}/seguridad/restablecer-password/{token}/"
        
        subject = "Recuperación de contraseña - Sistema de Gestión"
        html_content = f"""
        <div style="padding: 20px; border: 1px solid #ddd;">
            <h3>Solicitud de cambio de contraseña</h3>
            <p>Hola {usuario.nombre}, haz clic abajo para cambiar tu clave. Si no solicitaste esto, ignora el mensaje.</p>
            <a href="{reset_url}" style="background: #f59e0b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Restablecer Contraseña</a>
            <p style="margin-top: 20px; font-size: 11px;">El link expira en 1 hora.</p>
        </div>
        """
        return self.enviar_email(usuario.correo, subject, html_content)

# Instancia global del servicio
email_service = EmailService()