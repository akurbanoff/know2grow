import smtplib
from email.message import EmailMessage

from celery import Celery
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, KNOW2GROW_SMTP_PASS

celery = Celery('tasks', broker='redis://localhost:6379')


def send_hello_email_message(username: str, email):
    email = EmailMessage()
    email['Subject'] = 'know2grow'
    email['From'] = SMTP_USER
    email['To'] = email

    email.set_content(f'''Привет {username}! Мы рады, что ты к нам присоединился. Чтобы увидеть пример использования сайта,
        перейдите по ссылке http://127.0.0.1:8000/example .
    ''')

    return email


@celery.task
def send_hello_to_new_user(username:str, email):
    email = send_hello_email_message(username=username, email=email)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, KNOW2GROW_SMTP_PASS)
        server.send_message(email)