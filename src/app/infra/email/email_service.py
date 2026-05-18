import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:

    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        msg = MIMEMultipart()
        msg["From"] = "noreply@test.local"
        msg["To"] = to_email
        msg["Subject"] = subject

        html = """
            <html>
            <body>
                <h1>Hola 👋</h1>
                <p>{body}</p>
            </body>
            </html>
            """

        msg.attach(MIMEText(html.format(body=body), "html"))

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        ) as server:
            server.send_message(msg)
