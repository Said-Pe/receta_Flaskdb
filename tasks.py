from flask import current_app
from flask_mail import Message
from celery import Celery  # Importar Celery directamente

celery = Celery(__name__)  # Inicializar Celery

@celery.task  # Usar el decorador @celery.task
def send_email(subject, sender, recipients, body):
    with current_app.app_context():
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = body
        try:
            current_app.mail.send(msg)
            return 'Email sent!'
        except Exception as e:
            return f'Error sending email: {str(e)}'
