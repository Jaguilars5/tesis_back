"""Correo saliente del sistema academico."""

import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.html import escape

logger = logging.getLogger(__name__)


def _send_email(to_email: str, subject: str, text_body: str, html_body: str = "") -> bool:
    if not to_email:
        return False
    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email],
        )
        if html_body:
            message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.warning("No se pudo enviar correo a %s", to_email, exc_info=True)
        return False


def _base_html(title: str, body_html: str, footer: str = "") -> str:
    safe_title = escape(title)
    safe_footer = escape(footer or "Este es un mensaje automatico del Sistema Academico.")
    return f"""\
<!DOCTYPE html>
<html lang="es">
  <body style="margin:0;padding:0;background:#f4f6f8;font-family:Arial,Helvetica,sans-serif;color:#1f2937;">
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:28px 0;">
      <tr>
        <td align="center">
          <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="width:560px;max-width:94%;background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
            <tr>
              <td style="background:#0f172a;color:#ffffff;padding:20px 24px;">
                <div style="font-size:18px;font-weight:700;">Sistema Academico</div>
                <div style="font-size:12px;color:#cbd5e1;margin-top:4px;">Notificaciones institucionales</div>
              </td>
            </tr>
            <tr>
              <td style="padding:28px 24px;">
                <h1 style="font-size:22px;line-height:1.3;margin:0 0 16px;color:#111827;">{safe_title}</h1>
                {body_html}
              </td>
            </tr>
            <tr>
              <td style="padding:16px 24px;background:#f9fafb;color:#6b7280;font-size:12px;line-height:1.5;">
                {safe_footer}
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
"""


def send_welcome_email(to_email: str, name: str, username: str, password: str) -> bool:
    subject = "Bienvenido/a al Sistema Academico"
    text_body = (
        f"Hola {name},\n\n"
        "Tu cuenta ha sido creada.\n\n"
        f"Usuario: {username}\n"
        f"Correo: {to_email}\n"
        f"Contrasena inicial: {password}\n\n"
        "Por seguridad, deberas cambiar tu contrasena al iniciar sesion."
    )
    html_body = _base_html(
        "Cuenta creada",
        f"""
        <p style="font-size:15px;line-height:1.6;margin:0 0 18px;">Hola {escape(name)}, tu cuenta ha sido creada correctamente.</p>
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:8px;margin:16px 0;">
          <tr><td style="padding:14px 16px;color:#6b7280;font-size:13px;width:130px;">Usuario</td><td style="padding:14px 16px;font-weight:700;">{escape(username)}</td></tr>
          <tr><td style="padding:14px 16px;color:#6b7280;font-size:13px;">Correo</td><td style="padding:14px 16px;font-weight:700;">{escape(to_email)}</td></tr>
          <tr><td style="padding:14px 16px;color:#6b7280;font-size:13px;">Contrasena</td><td style="padding:14px 16px;font-family:Consolas,monospace;font-weight:700;">{escape(password)}</td></tr>
        </table>
        <p style="font-size:13px;line-height:1.6;color:#6b7280;margin:0;">Por seguridad, deberas cambiar tu contrasena al iniciar sesion.</p>
        """,
    )
    return _send_email(to_email, subject, text_body, html_body)


def send_password_reset_email(to_email: str, reset_url: str) -> bool:
    subject = "Recuperacion de contrasena"
    text_body = (
        "Recibimos una solicitud para restablecer tu contrasena.\n\n"
        f"Ingresa al siguiente enlace para crear una nueva contrasena:\n{reset_url}\n\n"
        "Si no solicitaste este cambio, puedes ignorar este mensaje."
    )
    html_body = _base_html(
        "Recuperacion de contrasena",
        f"""
        <p style="font-size:15px;line-height:1.6;margin:0 0 22px;">Recibimos una solicitud para restablecer tu contrasena.</p>
        <p style="margin:0 0 22px;">
          <a href="{escape(reset_url)}" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;border-radius:6px;padding:12px 18px;font-weight:700;">Crear nueva contrasena</a>
        </p>
        <p style="font-size:12px;line-height:1.6;color:#6b7280;word-break:break-all;margin:0;">Si el boton no funciona, copia este enlace:<br>{escape(reset_url)}</p>
        """,
        footer="Si no solicitaste este cambio, puedes ignorar este mensaje.",
    )
    return _send_email(to_email, subject, text_body, html_body)


def send_notification_email(to_email: str, title: str, body: str) -> bool:
    text_body = body or title
    html_body = _base_html(
        title,
        f'<p style="font-size:15px;line-height:1.6;margin:0;">{escape(body or title)}</p>',
    )
    return _send_email(to_email, title, text_body, html_body)
