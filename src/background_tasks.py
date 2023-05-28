import smtplib
from email.message import EmailMessage

from celery import Celery
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, KNOW2GROW_SMTP_PASS

celery = Celery('tasks', broker='redis://localhost:6379')


def send_hello_email_message(username: str):
    email = EmailMessage()
    email['Subject'] = 'know2grow'
    email['From'] = SMTP_USER
    email['To'] = 'uspeshniy.ae@yandex.ru'

    email.set_content(f'Привет {username}! Мы рады, что ты к нам присоединился. Вперед к мечте и не скучай!')

    return email


@celery.task
def send_hello_to_new_user(username:str):
    email = send_hello_email_message(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, KNOW2GROW_SMTP_PASS)
        server.send_message(email)