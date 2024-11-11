import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import os

def send_email_with_attachment(sender_email, receiver_email, subject, body, pdf_files):
    """
    Envía un correo con uno o múltiples archivos PDF como adjuntos.

    Parameters:
        sender_email (str): Dirección del remitente.
        receiver_email (str): Dirección del destinatario.
        subject (str): Asunto del correo.
        body (str): Cuerpo del correo.
        pdf_files (list): Lista de tuplas donde cada tupla contiene (nombre del archivo, bytes del pdf).
    """
    # Crear el mensaje MIME
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = receiver_email
    message['Subject'] = subject

    # Adjuntamos el cuerpo del correo
    message.attach(MIMEText(body, 'plain'))

    # Adjuntamos cada PDF como un archivo en el correo
    for file_name, pdf_bytes in pdf_files:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(pdf_bytes)
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={file_name}',
        )
        message.attach(part)

    # Convertimos el mensaje a una string para enviar
    email_text = message.as_string()

    # Configuración del servidor SMTP
    smtp_server = os.getenv("SMTP_SERVER")
    smtp_port = os.getenv("SMTP_PORT")
    sender_password = os.getenv("SMTP_PASSWORD")

    # Enviamos el correo
    try:
        # Creación del contexto SSL seguro
        context = ssl.create_default_context()

        # Conexión al servidor SMTP y enviar el correo
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, email_text)

        print("Email sent successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")