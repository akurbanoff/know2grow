from tests.conftest import client
from src.main import app
import json


def test_registration():
    data = {
      "name": "Artem",
      "email": "sir.re-zero@yandex.ru",
      "password": "Encode88"
    }
    response = client.post(url='/auth/register', json=data)

    assert response.status_code == 201


def test_login():
    data = {
        'grant_type': '',
        'username': 'sir.re-zero@yandex.ru',
        'password': 'Encode88',
        'scope': '',
        'client_id': '',
        'client_secret': ''
    }

    response = client.post(url='/auth/jwt/login', data=data)

    assert response.status_code == 204


def test_change_name():
    data = {
        "name": "Artem",
        "email": "sir.re-zero@yandex.ru",
        'new_name': 'Alex'
    }
    response = client.post(url='/auth/change_name', params=data)

    assert response.status_code == 200


def test_change_email():
    data = {
        "name": "Alex",
        "email": "sir.re-zero@yandex.ru",
        'new_email': 'sir.re-zero@yandex.ru'
    }
    response = client.post(url='/auth/change_email')

    assert response.status_code == 200


def test_change_password():
    data = {
        'email': 'sir.re-zero@yandex.ru',
        'new_password': 'EnCoDe88',
        'test_db': True
    }

    response = client.post(url='/auth/change_password', params=data)

    assert response.status_code == 200
