import smtplib
from email.message import EmailMessage

from celery import Celery
from src.config import SMTP_HOST, SMTP_PORT, SMTP_USER, KNOW2GROW_SMTP_PASS, REDIS_PORT, REDIS_HOST

celery = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def send_hello_email_message(username: str, user_email):
    email = EmailMessage()
    email['Subject'] = 'know2grow'
    email['From'] = SMTP_USER
    email['To'] = user_email

    email.set_content(f'''Привет {username}! Мы рады, что ты к нам присоединился. Чтобы увидеть пример использования сайта,
        перейдите по ссылке http://127.0.0.1:8000/example .
    ''')

    return email


@celery.task
def send_hello_to_new_user(username:str, email):
    email = send_hello_email_message(username=username, user_email=email)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, KNOW2GROW_SMTP_PASS)
        server.send_message(email)