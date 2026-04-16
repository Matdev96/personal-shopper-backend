from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings

# Configuração da conexão SMTP com Gmail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Personal Shopper",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)

fastmail = FastMail(conf)


async def send_reset_email(email: str, token: str) -> None:
    """
    Envia o email de recuperação de senha com o link de reset.
    O link aponta para o frontend com o token como query param.
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    html_body = f"""
    <div style="font-family: Inter, Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 32px 24px; background: #f9fafb; border-radius: 12px;">
        <h2 style="color: #111827; margin-bottom: 8px;">Recuperação de senha</h2>
        <p style="color: #6b7280; font-size: 15px; margin-bottom: 24px;">
            Recebemos uma solicitação para redefinir a senha da sua conta no <strong>Personal Shopper</strong>.
        </p>
        <a href="{reset_link}"
           style="display: inline-block; background: #2563eb; color: #ffffff; text-decoration: none;
                  padding: 12px 28px; border-radius: 8px; font-weight: 600; font-size: 15px;">
            Redefinir minha senha
        </a>
        <p style="color: #9ca3af; font-size: 13px; margin-top: 24px;">
            Este link expira em <strong>1 hora</strong>. Se você não solicitou a recuperação, ignore este email.
        </p>
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;" />
        <p style="color: #d1d5db; font-size: 12px;">Personal Shopper — TCC ADS</p>
    </div>
    """

    message = MessageSchema(
        subject="Redefinição de senha — Personal Shopper",
        recipients=[email],
        body=html_body,
        subtype=MessageType.html,
    )

    await fastmail.send_message(message)
