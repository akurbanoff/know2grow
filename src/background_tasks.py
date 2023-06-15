import smtplib
from email.message import EmailMessage

from celery import Celery
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, KNOW2GROW_SMTP_PASS
from src.crypto_news.routers import current_user

celery = Celery('tasks', broker='redis://localhost:6379')


def send_hello_email_message(username: str):
    email = EmailMessage()
    email['Subject'] = 'know2grow'
    email['From'] = SMTP_USER
    email['To'] = current_user.email

    email.set_content(f'''Привет {username}! Мы рады, что ты к нам присоединился. Чтобы увидеть пример использования сайта,
        перейдите по ссылке http://127.0.0.1:8000/example .
    ''')

    return email


@celery.task
def send_hello_to_new_user(username:str):
    email = send_hello_email_message(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, KNOW2GROW_SMTP_PASS)
        server.send_message(email)